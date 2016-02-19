#!/usr/bin/python

import logging
class NullHandler(logging.Handler):
    def emit(self, record):
        pass
log = logging.getLogger('xivelyConnector')
log.setLevel(logging.ERROR)
log.addHandler(NullHandler())

import json
import threading
import socket
import traceback
import re
import time
import copy

import httplib

from   SmartMeshSDK.utils    import FormatUtils

#============================ exceptions ======================================

class xivelyError(Exception):
    pass
class xivelyRateError(xivelyError):
    pass
class xivelyTimeoutError(xivelyError):
    pass

#============================ helpers =========================================

class xivelyStats(object):
    
    RATE_WINDOW_MIN     = 3
    
    SOCKET_TX           = 'SOCKET_TX'
    SOCKET_TX_OK        = 'SOCKET_TX_OK'
    SOCKET_TX_TIMEOUT   = 'SOCKET_TX_TIMEOUT'
    
    SOCKET_RX           = 'SOCKET_RX'
    
    HTTP_TX             = 'HTTP_TX'
    HTTP_TX_OK          = 'HTTP_TX_OK'
    HTTP_TX_RATELIMIT   = 'HTTP_TX_RATELIMIT'
    HTTP_TX_ERROR       = 'HTTP_TX_ERROR'
    
    #======================== singleton pattern ===============================
    
    _instance = None
    _init     = False
    
    def __new__(cls, *args, **kwargs):
        if not cls._instance:
            log.info("Creating xivelyStats instance")
            cls._instance = super(xivelyStats, cls).__new__(cls, *args, **kwargs)
        return cls._instance
    
    #======================== init ============================================
    
    def __init__(self):
        
        # don't re-initialize an instance (needed because singleton)
        if self._init:
            return
        self._init = True
        
        # store params
        
        # local variables
        self.dataLock        = threading.RLock()
        self.reset()
    
    #======================== public ==========================================
    
    def increment(self,statName):
        with self.dataLock:
            
            if statName not in self.stats:
                self.stats[statName]   = 0
            self.stats[statName]      += 1
            
            if statName in [self.SOCKET_TX,self.SOCKET_RX,self.HTTP_TX]:
                self.numTransactions  += 1
                self.rateBuf          += [time.time()]
                self._cleanupRateBuf()
            
            if statName in [self.HTTP_TX_RATELIMIT]:
                try:
                    self.rateBuf.pop()
                except IndexError:
                    pass
    
    def getNumTransactions(self):
        with self.dataLock:
            return self.numTransactions
    
    def getRate(self):
        with self.dataLock:
            self._cleanupRateBuf()
            return len(self.rateBuf)/float(self.RATE_WINDOW_MIN)
    
    def getStats(self):
        with self.dataLock:
            return copy.deepcopy(self.stats)
    
    def reset(self):
        with self.dataLock:
            self.numTransactions       = 0
            self.rateBuf               = []
            self.stats                 = {}
    
    #======================== private =========================================
    
    def _cleanupRateBuf(self):
        now = time.time()
        with self.dataLock:
            while self.rateBuf and (self.rateBuf[0]<(now-self.RATE_WINDOW_MIN*60)):
                self.rateBuf.pop(0)

class xivelySubscriber(threading.Thread):
    
    XIVELY_SOCKETSERVER_HOST      = 'api.xively.com'
    XIVELY_SOCKETSERVER_PORT      = 8081
    XIVELY_SUBSCRIPTION_TIMEOUT   = 10
    XIVELY_KEEPALIVE_TIMEOUT      = (30*60) # in s
    
    #======================== thread ==========================================
    
    def __init__(self):
        
        # store params
        
        # local variables
        self.dataLock             = threading.Lock()
        self.stats                = xivelyStats()
        self.keepaliveTimer       = None
        self.subscriptions        = {}
        self.socket               = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.socket.setsockopt(socket.SOL_SOCKET, socket.SO_KEEPALIVE, 1)
        self.socket.connect(
            (
                self.XIVELY_SOCKETSERVER_HOST,
                self.XIVELY_SOCKETSERVER_PORT,
            )
        )
        
        # reset keepalive timer
        self._resetKeepaliveTimer()
        
        # initialize parent
        threading.Thread.__init__(self)
        self.name                 = 'xivelySubscriber'
        
        # log
        log.info("creating {0} instance".format(self.name))
        
        # start myself
        self.start()
    
    def run(self):
        
        # log
        log.info("{0} thread starts".format(self.name))
        
        try:
            while True:
            
                # read from socket
                try:
                    dataRaw = self.socket.recv(1024)
                except socket.error:
                
                    # log
                    log.info('Stopping thread {0}, error when reading socket'.format(self.name))
                    
                    # stop thread
                    return
                    
                if not dataRaw:
                    
                    # log
                    log.info('Stopping thread {0}, error no data received'.format(self.name))
                    
                    # stop thread
                    return
                
                # update stats
                self.stats.increment(xivelyStats.SOCKET_RX)
                
                # reset keepalive timer
                self._resetKeepaliveTimer()
                
                # convert to JSON
                data         = json.loads(dataRaw)
                
                # log
                if log.isEnabledFor(logging.DEBUG):
                    output   = []
                    output  += ['xivelySubscriber received data: {0}'.format(data)]
                    output   = '\n'.join(output)
                    log.debug(output)
                
                # no 'resource' field in data when sending keepalive
                if not 'resource' in data:
                    continue
                
                # retrieve feedId and datastream
                m = re.search('/feeds/(\S+)/datastreams/(\S+)', data['resource'])
                feedId       = int(m.group(1))
                datastream   = str(m.group(2))
                
                if sorted(data.keys())==sorted(['status','resource']):
                    # this is a reply to a subscribe/unsubscribe command
                    
                    # release subscriptionEvent
                    if data['status']==200:
                        with self.dataLock:
                            self.subscriptions[(feedId,datastream)]['subscriptionEvent'].set()
                    else:
                        log.warning("received response code {0} for subscription/unsubscription".format(
                                data['status']
                            )
                        )
                
                elif sorted(data.keys())==sorted(['body','resource']):
                    # this is a new data notification
                    
                    # get the mac and callback
                    with self.dataLock:
                        mac            = self.subscriptions[(feedId,datastream)]['mac']
                        callback       = self.subscriptions[(feedId,datastream)]['callback']
                    
                    # retrieve value
                    if 'current_value' in data['body']:
                    
                        value = str(data['body']['current_value'])
                        try:
                            value = int(value)
                        except Exception as err:
                            try:
                                value = float(value)
                            except Exception:
                                pass
                        
                        # call the callback
                        try:
                            callback(
                                mac            = mac,
                                datastream     = datastream,
                                value          = value,
                            )
                        except:
                            output  = []
                            output += ['exception when calling callback for mac={0} datastream={1}'.format(mac,datastream)]
                            output += ['\nerror:\n']
                            output += [type(err)]
                            output += [str(err)]
                            output += ['\ncall stack:\n']
                            output += [traceback.format_exc()]
                            output  = '\n'.join(output)
                            log.error(output)
        
        except Exception as err:
            output  = []
            output += ['===== crash in thread {0} ====='.format(self.name)]
            output += ['\nerror:\n']
            output += [str(type(err))]
            output += [str(err)]
            output += ['\ncall stack:\n']
            output += [traceback.format_exc()]
            output  = '\n'.join(output)
            print output # critical error
            log.critical(output)
            raise
    
    #======================== public ==========================================
    
    def subscribe(self,apiKey,mac,feedId,datastream,callback):
        
        # log
        log.info(
            "            subscribing to {0}/{1}".format(
                FormatUtils.formatMacString(mac),
                datastream,
            )
        )
        
        # validate params
        with self.dataLock:
            if (feedId,datastream) in self.subscriptions:
                raise ValueError("Subscription to {0}:{1} already exists".format(feedId,datastream))
        
        # add to subscriptions
        event = threading.Event()
        with self.dataLock:
            self.subscriptions[(feedId,datastream)] = {
                'mac':                 mac,
                'subscriptionEvent':   threading.Event(),
                'callback':            callback,
            }
        
        # prepare
        method     = 'subscribe'
        resource   = '/feeds/{0}/datastreams/{1}'.format(feedId,datastream)
        headers    = {  
            'X-ApiKey' : apiKey,
        }
        
        # log
        if log.isEnabledFor(logging.DEBUG):
            output      = []
            output     += ['{0} send:'.format(self.name)]
            output     += ['- method              : {0}'.format(method)]
            output     += ['- resource            : {0}'.format(resource)]
            output     += ['- headers             : {0}'.format(headers)]
            output      = '\n'.join(output)
            log.debug(output)
        
        # send 
        self.socket.send(
            json.dumps(
                {
                    'method' :     method,
                    'resource' :   resource,
                    'headers' :    headers,
                }
            )
        )
        
        # update stats
        self.stats.increment(xivelyStats.SOCKET_TX)
        
        # reset keepalive timer
        self._resetKeepaliveTimer()
        
        # wait for reply
        if not  self.subscriptions[(feedId,datastream)]['subscriptionEvent'].wait(
                    self.XIVELY_SUBSCRIPTION_TIMEOUT
                ):
            # timeout
            
            # update stats
            self.stats.increment(xivelyStats.SOCKET_TX_TIMEOUT)
            
            # subscription failed, delete from subscriptions
            del self.subscriptions[(feedId,datastream)]
            
            # raise error
            raise xivelyTimeoutError("timeout to subscribe to {0}:{1}".format(feedId,datastream))
        else:
            
            # update stats
            self.stats.increment(xivelyStats.SOCKET_TX_OK)
            
            # log
            log.info(
                "successfully subscribed to {0}/{1}".format(
                    FormatUtils.formatMacString(mac),
                    datastream,
                )
            )
            
            # remove subscriptionEvent
            with self.dataLock:
                self.subscriptions[(feedId,datastream)]['subscriptionEvent'] = None
    
    def unsubscribe(self,apiKey,mac,feedId,datastream):
        
        # log
        log.info("unsubscribing from {0}/{1}".format(
                FormatUtils.formatMacString(mac),
                datastream,
            )
        )
        
        # validate params
        with self.dataLock:
            if (feedId,datastream) not in self.subscriptions:
                raise ValueError("No active subscription to {0}:{1}".format(feedId,datastream))
            if self.subscriptions[(feedId,datastream)]['subscriptionEvent']:
                raise SystemError("Ongoing subscription/unsubscription process to {0}:{1}".format(feedId,datastream))
        
        # add to event subscriptions
        with self.dataLock:
            self.subscriptions[(feedId,datastream)]['subscriptionEvent'] = threading.Event()
        
        # send 
        self.socket.send(
            json.dumps(
                {
                    'method' :     'unsubscribe',
                    'resource' :   '/feeds/{0}/datastreams/{1}'.format(feedId,datastream),
                    'headers' :
                    {  
                        'X-ApiKey' : apiKey,
                    },
                }
            )
        )
        
        # update stats
        self.stats.increment(xivelyStats.SOCKET_TX)
        
        # reset keepalive timer
        self._resetKeepaliveTimer()
        
        # wait for reply
        if not  self.subscriptions[(feedId,datastream)]['subscriptionEvent'].wait(
                    self.XIVELY_SUBSCRIPTION_TIMEOUT
                ):
            # timeout
            
            # remove subscriptionEvent
            with self.dataLock:
                self.subscriptions[(feedId,datastream)]['subscriptionEvent'] = None
            
            # update stats
            self.stats.increment(xivelyStats.SOCKET_TX_TIMEOUT)
            
            # raise error
            raise xivelyTimeoutError("timeout to unsubscribe from {0}:{1}".format(feedId,datastream))
        else:
            # successful reply received
            
            # update stats
            self.stats.increment(xivelyStats.SOCKET_TX_OK)
            
            # unsubscription succeeded, delele from subscriptions
            del self.subscriptions[(feedId,datastream)]
    
    def close(self):
        
        # log
        log.info("closing {0}".format(self.name))
        
        # cancel the keepalive timer
        if self.keepaliveTimer:
            self.keepaliveTimer.cancel()
        
        # shut down the socket. Will cause self.socket.recv() to return ''.
        self.socket.shutdown(socket.SHUT_RDWR)
    
    #======================== private =========================================
    
    def _resetKeepaliveTimer(self):
        if self.keepaliveTimer:
            self.keepaliveTimer.cancel()
        self.keepaliveTimer  = threading.Timer(self.XIVELY_KEEPALIVE_TIMEOUT, self._keepalive)
        self.keepaliveTimer.start()
    
    def _keepalive(self):
        
        # log
        if log.isEnabledFor(logging.DEBUG):
            log.debug("sending TCP keepalive to Xively")
        
        # send dummy data over TCP socket to force TCP to stay open
        try:
            self.socket.send('keepalive')
        except Exception as err:
            
            # log
            log.error(
                "Error while sending keepalive to Xively: [{0}] {1}".format(
                    type(err),
                    err,
                )
            )
            
            # close
            self.close()
            
        else:
            
            # reset keepalive timer
            self._resetKeepaliveTimer()
    
class xivelyClient(object):
    
    XIVELY_HOST              = 'api.xively.com'
    XIVELY_BASE_URL          = '/v2/'
    XIVELY_HTTP_TIMEOUT_S    = 10.0
    
    def __init__(self,apiKey):
        
        # store params
        self.apiKey          = apiKey
        self.stats           = xivelyStats()
        
    #======================== public ==========================================
     
    def get(self,url,body=''):
        
        return self._request(
            method           = 'GET',
            url              = url,
            body             = body,
        )
    
    def post(self,url,body=''):
        
        return self._request(
            method           = 'POST',
            url              = url,
            body             = body,
        )
    
    def put(self,url,body=''):
        
        return self._request(
            method           = 'PUT',
            url              = url,
            body             = body,
        )
    
    def delete(self,url,body=''):
        
        return self._request(
            method           = 'DELETE',
            url              = url,
            body             = body,
        )
    
    #======================== private =========================================
    
    def _request(self,method,url,body):
        
        # create connection to Xively server
        connection = httplib.HTTPSConnection(
            host             = self.XIVELY_HOST,
            timeout          = self.XIVELY_HTTP_TIMEOUT_S,
        )
        
        # send the request
        try:
            args = {
                'method':        method,
                'url':           self.XIVELY_BASE_URL+url,
                'headers': {
                    'X-ApiKey':       self.apiKey,
                    'Content-Type':   'application/json',
                },
            }
            if body:
                args['body']      = json.dumps(body)
            
            # log
            if log.isEnabledFor(logging.DEBUG):
                output            = []
                output           += ['_request() called with:']
                for (k,v) in args.items():
                    output       += ['- {0:<20}: {1}'.format(k,v)]
                output            = '\n'.join(output)
                log.debug(output)
            
            # send the request
            connection.request(**args)
            
            # update stats
            self.stats.increment(xivelyStats.HTTP_TX)
            
            # parse response
            response              = connection.getresponse()
            responseBody          = response.read().strip()
            if responseBody:
                responseBody      = json.loads(responseBody)
            else:
                responseBody      = None
            
            # log
            if log.isEnabledFor(logging.DEBUG):
                output            = []
                output      += ['response:']
                output      += ['- status              : {0}'.format(response.status)]
                output      += ['- reason              : {0}'.format(response.reason)]
                output      += ['- body                : {0}'.format(responseBody)]
                output       = '\n'.join(output)
                log.debug(output)
            
            # raise returned error code
            if response.status not in [httplib.OK,httplib.CREATED]:
                output = '{0} {1} response.status={2}'.format(
                    method,
                    url,
                    response.status,
                )
                log.error(output)
                if response.status ==httplib.FORBIDDEN and responseBody['title']=='Rate too fast':
                    
                    # update stats
                    self.stats.increment(xivelyStats.HTTP_TX_RATELIMIT)
                    
                    # raise
                    raise xivelyRateError(output)
                else:
                    
                    # update stats
                    self.stats.increment(xivelyStats.HTTP_TX_ERROR)
                    
                    # raise
                    raise SystemError(output)
            
            # update stats
            self.stats.increment(xivelyStats.HTTP_TX_OK)
            
            return responseBody
        
        finally:
            # close the connection
            connection.close()

class xivelyConnector(object):
    
    def __init__(self,apiKey,productName,productDesc):
        
        assert type(apiKey)==str
        assert type(productName)==str
        assert type(productDesc)==str
        
        # log
        log.info("Creating xivelyConnector instance")
        
        # store params
        self.apiKey          = apiKey
        self.productName     = productName
        self.productDesc     = productDesc
        self.datastreams     = {} # a cache on the datastreams currently on each device
        self.dataLock        = threading.RLock()
        self.subscriber      = None
        
        # local variables
        self.client          = None
        self.product_id      = None
        self.stats           = xivelyStats()
        self.xivelyDevices   = []
        
        # connect
        self._connect()
        self.product_id      = self.getProductId()
        self._retrieveXivelyDevices()
    
    #======================== public ==========================================
    
    def createDatastream(self,mac,datastream):
        '''
        \brief Create a particular datastream on a device, or the one that
            already exists on Xively.
        
        \return The feed_id.
        '''
        
        # log
        if log.isEnabledFor(logging.DEBUG):
            output      = []
            output     += ['createDatastream() called with:']
            output     += ['- mac          {0}'.format(mac)]
            output     += ['- datastream   {0}'.format(datastream)]
            output      = '\n'.join(output)
            log.debug(output)
        
        if type(mac) in [tuple,list]:
            mac = FormatUtils.formatMacString(mac)
        
        assert self.product_id
        
        # retrieve device's information (create if needed)
        dev = None
        while dev is None:
            
            # get device, if exists
            with self.dataLock:
                for d in self.xivelyDevices:
                    if d['serial']==mac:
                        dev = d
                        break
            
            # create mote
            if dev is None:
                
                # log
                log.info("Creating mote {0}".format(mac))
                
                # create
                response = self.client.post(
                    url             = 'products/{0}/devices'.format(
                        self.product_id,
                    ),
                    body            = {
                        'devices': [
                            {"serial": mac}
                        ]
                    },
                )
                
                # update list of devices
                self._retrieveXivelyDevices()
        
        isActive                  = (dev['activated_at'] is not None)
        activation_code           = dev['activation_code']
        
        # activate mote if needed
        if not isActive:
            
            # log
            log.info("Activating mote {0}".format(mac))
            
            # activate
            self.client.get(
                url             = 'devices/{0}/activate'.format(
                    activation_code,
                ),
            )
            
            # update list of devices
            self._retrieveXivelyDevices()
        
        # get datastreams
        if mac not in self.datastreams:
            
            # log
            log.info(" retrieving datastreams of {0}".format(mac))
            
            # retrieve
            response = self.client.get(
                url         = 'feeds/{0}.json'.format(
                    dev['feed_id'],
                ),
            )
            if 'datastreams' in response:
                self.datastreams[mac] = [ds['id'] for ds in response['datastreams']]
            else:
                self.datastreams[mac] = []
        
        # create datastream
        if datastream not in self.datastreams[mac]:
            
            # log
            log.info("Create datastream {0} on mote {1}".format(
                    datastream,
                    mac,
                )
            )
            
            # create
            self.client.put(
                url         = 'feeds/{0}.json'.format(
                    dev['feed_id'],
                ),
                body        = {
                    'version':         '1.0.0',
                    'datastreams': [
                        {
                            'id' :     datastream,
                        },
                    ]
                },
            )
            
            # cache
            self.datastreams[mac] +=   [datastream]
        
        return dev['feed_id']
    
    def publish(self,mac,datastream,value):
        
        # log
        if log.isEnabledFor(logging.DEBUG):
            output      = []
            output     += ['publish() called with:']
            output     += ['- mac          {0}'.format(FormatUtils.formatMacString(mac))]
            output     += ['- datastream   {0}'.format(datastream)]
            output     += ['- value        {0}'.format(value)]
            output      = '\n'.join(output)
            log.debug(output)
        
        # verify subscriber alive, if exists
        if self.subscriber:
            if not self.subscriber.isAlive():
                self.subscriber = None
                raise SystemError("subscriber is not alive during publish()")
        
        # create the datastream (or retrieve feed_id if exists)
        feed_id = self.createDatastream(mac,datastream)
        
        # publish to datastream
        self.client.put(
            url         = 'feeds/{0}.json'.format(
                feed_id,
            ),
            body        = {
            'version':         '1.0.0',
                'datastreams': [
                    {
                        'id' :              datastream,
                        'current_value':    value,
                    },
                ]
            },
        )
        
        # log
        if log.isEnabledFor(logging.DEBUG):
            output      = []
            output     += ['published to Xively:']
            output     += ['- mac          {0}'.format(FormatUtils.formatMacString(mac))]
            output     += ['- datastream   {0}'.format(datastream)]
            output     += ['- value        {0}'.format(value)]
            output      = '\n'.join(output)
            log.debug(output)
    
    def subscribe(self,mac,datastream,callback):
        
        feedId = self.mac2feedId(mac)
        
        if not feedId:
            raise ValueError("unknown MAC {0}".format(mac))
        
        # create subscriber if needed
        if not self.subscriber:
            self.subscriber = xivelySubscriber()
        
        # verify subscriber alive
        if not self.subscriber.isAlive():
            self.subscriber = None
            raise SystemError("subscriber is not alive during subscribe()")
        
        # subscribe
        self.subscriber.subscribe(self.apiKey,mac,feedId,datastream,callback)
    
    def unsubscribe(self,mac,datastream):
        
        feedId = self.mac2feedId(mac)
        
        if not feedId:
            raise ValueError("unknown MAC {0}".format(mac))
        if not self.subscriber:
            raise SystemError("no subscriber")
        
        # verify subscriber alive
        if not self.subscriber.isAlive():
            self.subscriber = None
            raise SystemError("subscriber is not alive during subscribe()")
        
        # unsubscribe
        self.subscriber.unsubscribe(self.apiKey,mac,feedId,datastream)
    
    def mac2feedId(self,mac):
        if type(mac) in [tuple,list]:
            mac = FormatUtils.formatMacString(mac)
        
        returnVal = None
        
        with self.dataLock:
            for d in self.xivelyDevices:
                if d['serial']==mac:
                    returnVal = d['feed_id']
                    break
        
        return returnVal
    
    def feedId2mac(self,feedId):
        
        returnVal = None
        
        with self.dataLock:
            for d in self.xivelyDevices:
                if d['feed_id']==feedId:
                    returnVal = d['serial']
                    break
        
        return returnVal
    
    def getProductId(self):
        '''
        \brief Retrieve the product ID. Creates product if necessary.
        '''
        with self.dataLock:
            if self.product_id:
                return self.product_id
        
        # log
        if log.isEnabledFor(logging.DEBUG):
            output      = []
            output     += ['Get productID for:']
            output     += ['- name:        \"{0}\"'.format(self.productName)]
            output     += ['- description: \"{0}\"'.format(self.productDesc)]
            output      = '\n'.join(output)
            log.debug(output)
        
        product_id = None
        while product_id is None:
            
            # retrieve list of current products
            response    = self.client.get(
                url             = 'products.json',
            )
            
            # retrieve product ID if exists
            for product in response['products']:
                if (product['name']==self.productName and product['description']==self.productDesc):
                    if product_id:
                        raise SystemError(
                            "More than one product with name \"{0}\" and description \"{1}\"".format(
                                self.productName,
                                self.productDesc,
                            )
                        )
                    product_id = product['product_id']
            
            # create product if needed
            if product_id is None:
                
                # log
                log.info("Creating product")
                
                # create
                self.client.post(
                    url             = 'products',
                    body            = {
                        'product': {
                            'name':           self.productName,
                            'description':    self.productDesc,
                        }
                    }
                )
        
        # log
        if log.isEnabledFor(logging.DEBUG):
            log.debug("product_id: \"{0}\"".format(product_id))
        
        return product_id
    
    def deleteProduct(self):
        '''
        \brief Deletes the product from Xively.
        
        \warning Calling this function will delete all the devices and
            associated data.
        '''
        assert self.product_id
        
        # log
        log.info("Deleting product \"{0}\"".format(self.product_id))
        
        # delete
        self.client.delete(
            url             = 'products/{0}'.format(
                self.product_id,
            ),
        )
        
        # record
        with self.dataLock:
            self.product_id       = None
            self.xivelyDevices    = []
    
    def close(self):
        try:
            self.subscriber.close()
        except AttributeError:
            pass # happens when no subscriber
        
        self.subscriber = None
    
    #======================== private =========================================
    
    def _connect(self):
        '''
        \brief Connect to Xively.
        '''
        
        # log
        log.info("Connecting to Xively service")
        
        # record
        with self.dataLock:
            self.client = xivelyClient(self.apiKey)
    
    def _retrieveXivelyDevices(self):
        '''
        \brief Retrieve the list of devices currently on Xively.
        '''
        
        assert self.product_id
        
        PER_PAGE             = 10
        
        # log
        if log.isEnabledFor(logging.DEBUG):
            log.debug("Retrieving devices")
        
        duplicates = True
        while duplicates:
            
            # gather all devices
            xivelyDevices    = []
            doneListing      = False
            page             = 1
            while not doneListing:
                
                # get next devices
                response = self.client.get(
                    url             = 'products/{0}/devices?per_page={1}&page={2}'.format(
                        self.product_id,
                        PER_PAGE,
                        page,
                    )
                )
                
                # add to local devices
                xivelyDevices += response['devices']
                
                # decide whether next
                if len(response['devices'])<PER_PAGE:
                    doneListing=True
                else:
                    page += 1
                
            # make sure no duplicates
            serials              = [d['serial'] for d in xivelyDevices]
            duplicateSerials     = [s for s in serials if serials.count(s)>1]
            if duplicateSerials:
                duplicates       = True
            else:
                duplicates       = False
        
        # log
        if log.isEnabledFor(logging.DEBUG):
            output      = []
            output     += ['Found {0} devices:'.format(len(xivelyDevices))]
            for d in xivelyDevices:
                output += ['- {0}'.format(d['serial'])]
            output      = '\n'.join(output)
            log.debug(output)
        
        # record
        with self.dataLock:
            self.xivelyDevices = xivelyDevices
