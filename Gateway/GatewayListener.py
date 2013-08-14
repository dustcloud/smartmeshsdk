#!/usr/bin/python

import logging
class NullHandler(logging.Handler):
    def emit(self, record):
        pass
log = logging.getLogger('GatewayListener')
log.setLevel(logging.ERROR)
log.addHandler(NullHandler())

import time
import threading
import traceback

from EventBus   import EventBusClient
from pydispatch import dispatcher

import DynNotifs
import FormatUtils
import ApiConnector
import Gateway
import ApiException
from   IpMgrConnectorMux import IpMgrSubscribe

class SnapShot(threading.Thread):
    
    SNAPSHOT_PERIOD_FIRST    = 5                 ##< in seconds
    SNAPSHOT_PERIOD_SEC      = 5*60              ##< in seconds
    
    def __init__(self,gatewaylistener,connector,connectParams):
        
        assert isinstance(gatewaylistener,GatewayListener)
        assert isinstance(connector,ApiConnector.ApiConnector)
        assert isinstance(connectParams,(str,tuple))
        
        # store params
        self.gatewaylistener           = gatewaylistener
        self.connector                 = connector
        self.connectParams             = connectParams
        
        # local variables
        self.periodicSnapshotRunning   = False
        self.snapShotPeriod            = self.SNAPSHOT_PERIOD_FIRST
        self.busySnapshotting          = threading.Lock()
        
        # initialize parent
        threading.Thread.__init__(self)
        self.name                      = '{0}_SnapShot'.format(FormatUtils.formatConnectionParams(self.connectParams))
        
        # start itself
        self.start()
    
    def run(self):
        
        # log
        log.info('thread {0} started'.format(self.name))
        
        try:
            
            self.periodicSnapshotRunning    = True
            self.delayCounter               = 0
            while self.periodicSnapshotRunning:
                time.sleep(1)
                self.delayCounter +=1
                if self.delayCounter==self.snapShotPeriod:
                    self.doSnapshot()
                    self.delayCounter       = 0
                    self.snapShotPeriod     = self.SNAPSHOT_PERIOD_SEC
            
        except (ApiException.ConnectionError,ApiException.CommandTimeoutError) as err:
            
            # log
            log.warning('connection error={0}'.format(err))
            
            # dispatch
            dispatcher.send(
                signal      =   'deviceCommunicationError',
                data        =   {
                                    'connectionParam': self.connectParams,
                                    'reason':          str(err),
                                },
            )
            
        except Exception as err:
            output  = []
            output += ['===== crash in thread {0} ====='.format(self.name)]
            output += ['\nerror:\n']
            output += [str(err)]
            output += ['\ncall stack:\n']
            output += [traceback.format_exc()]
            output  = '\n'.join(output)
            print output # critical error
            log.critical(output)
            raise
        
        # log
        log.info('thread {0} ended'.format(self.name))
    
    #======================== public ==========================================
    
    def doSnapshot(self):
        
        self.busySnapshotting.acquire()
        
        motes                = []
        
        # dispatch
        dispatcher.send(
            signal      =   'networkEvent_{0}'.format(FormatUtils.formatConnectionParams(self.connectParams)),
            data        =   {
                                'type': Gateway.Gateway.SNAPSHOT_START,
                            },
        )
        
        starttime = time.time()
        
        try:
            currentMac     = (0,0,0,0,0,0,0,0) # start getMoteConfig() iteration with the 0 MAC address
            continueAsking = True
            while continueAsking:
                try:
                    res = self._execCommand(self.connector.dn_getMoteConfig,(currentMac,True))
                except ApiException.APIError:
                    continueAsking = False
                else:
                    motes.append(res.macAddress)
                    currentMac = res.macAddress
            
            for mac in motes:
                self._execCommand(self.connector.dn_getMoteInfo,(mac,))
            
            for mac in motes:
                currentPathId  = 0
                continueAsking = True
                while continueAsking:
                    try:
                        res = self._execCommand(self.connector.dn_getNextPathInfo,(mac,0,currentPathId))
                    except ApiException.APIError:
                        continueAsking = False
                    else:
                        currentPathId  = res.pathId
            
            # Note: below are commands we don't execute since not parsed
            '''
            currentMac     = (0,0,0,0,0,0,0,0) # start getNextACLEntry() iteration with the 0 MAC address
            continueAsking = True
            while continueAsking:
                try:
                    res = self._execCommand(self.connector.dn_getNextAclEntry,(currentMac,))
                except ApiException.APIError:
                    continueAsking = False
                else:
                    currentMac = res.mac
            
            self._execCommand(self.connector.dn_getIPConfig,())
            
            self._execCommand(self.connector.dn_getLicense,())
            
            self._execCommand(self.connector.dn_getManagerInfo,())
            
            self._execCommand(self.connector.dn_getNetworkConfig,())
            
            self._execCommand(self.connector.dn_getNetworkInfo,())
            
            self._execCommand(self.connector.dn_getSysInfo,())
            
            self._execCommand(self.connector.dn_getTime,())
            '''
            
        except ApiException.APIError as err:
            log.critical("FAILED: {0}".format(str(err)))
        
        # dispatch
        dispatcher.send(
            signal      =   'networkEvent_{0}'.format(FormatUtils.formatConnectionParams(self.connectParams)),
            data        =   {
                                'type': Gateway.Gateway.SNAPSHOT_END,
                            },
        )
        
        self.busySnapshotting.release()
    
    def tearDown(self):
        self.periodicSnapshotRunning = False
    
    #======================== private =========================================
    
    def _execCommand(self,func,params):
        try:
            res = func(*params)
        except TypeError as err:
            # TODO: Avoid TypeError from communication error
            log.error(str(err))
            raise ApiException.ConnectionError(str(err))

        
        # dispatch
        dispatcher.send(
            signal      =   'networkEvent_{0}'.format(FormatUtils.formatConnectionParams(self.connectParams)),
            data        =   {
                                'type':     Gateway.Gateway.CMD,
                                'name':     func.__name__,
                                'params':   params,
                                'res':      res,
                            },
        )
        
        return res
    
    def _formatParams(self, params):
        output = []
        for p in params:
            if isinstance(p, (list,tuple)):
                if len(p)==8:
                    value = FormatUtils.formatMacString(p)
                else:
                    value = '0x'+(''.join(['%.2x'%i for i in p]))
            else:
                value = str(p)
            output += [value]
        return ','.join(output)
    
    #======================== helpers =========================================

class GatewayListener(EventBusClient.EventBusClient):
    
    def __init__(self,connector,connectParams):
        assert isinstance(connector,ApiConnector.ApiConnector)
        assert isinstance(connectParams,(str,tuple))
        
        # record parameters
        self.connector       = connector
        self.connectParams   = connectParams
        
        # log
        log.info("creating instance")
        
        # local variables
        self.statsLock       = threading.Lock()
        self.starttime       = time.time()
        self.logLineCounter  = 0
        self._clearStats()
        
        self.snapShotThread  = SnapShot(self,connector,connectParams)
        
        # subscriber
        try:
            self.subscriber      = IpMgrSubscribe.IpMgrSubscribe(self.connector)
            self.subscriber.start()
            
            self.subscriber.subscribe(
                notifTypes =    [
                                    IpMgrSubscribe.IpMgrSubscribe.NOTIFDATA,
                                    IpMgrSubscribe.IpMgrSubscribe.NOTIFIPDATA,
                                ],
                fun =           self._notifCallback,
                isRlbl =        False,
            )
            self.subscriber.subscribe(
                notifTypes =    [
                                    IpMgrSubscribe.IpMgrSubscribe.NOTIFEVENT,
                                    IpMgrSubscribe.IpMgrSubscribe.NOTIFLOG, 
                                    IpMgrSubscribe.IpMgrSubscribe.NOTIFHEALTHREPORT,
                                ],
                fun =           self._notifCallback,
                isRlbl =        True,
            )
            self.subscriber.subscribe(
                notifTypes =    [
                                    IpMgrSubscribe.IpMgrSubscribe.ERROR,
                                    IpMgrSubscribe.IpMgrSubscribe.FINISH,
                                ],
                fun =           self._disconnectedCallback,
                isRlbl =        True,
            )
        except TypeError as err:
            # TODO: Avoid TypeError from communication error
            log.error(str(err))
            raise ApiException.ConnectionError(str(err))

        self.subscriber._thread.name   = '{0}_IpMgrSubscribe'.format(FormatUtils.formatConnectionParams(self.connectParams))
        
        # initialize parent class
        EventBusClient.EventBusClient.__init__(self,
            'dataToMesh_{0}'.format(FormatUtils.formatConnectionParams(self.connectParams)),
            self._sendDataToMesh,
        )
        self.name                 = '{0}_GatewayListener'.format(
            FormatUtils.formatConnectionParams(self.connectParams)
        )
    
    #======================== public ==========================================
    
    def tearDown(self):
        
        # tear down internal threads
        self.snapShotThread.tearDown()
        
        # call parent class
        super(GatewayListener,self).tearDown()
    
    #======================== private =========================================
    
    def _sendDataToMesh(self,sender,signal,data):
        
        try:
            self.connector.dn_sendData(
                macAddress       = data['mac'],
                priority         = data['priority'],
                srcPort          = data['srcPort'],
                dstPort          = data['dstPort'],
                options          = data['options'],
                data             = data['data'],
            )
        except TypeError as err:
            # TODO: Avoid TypeError from communication error
            log.error(str(err))
            raise ApiException.ConnectionError(str(err))
        
    def _clearStats(self):
        self.statsLock.acquire()
        self.statsStarttime = time.time()
        self.stats          = {}
        self.statsLock.release()
    
    def _notifCallback(self, notifName, notifParams):
        
        if   notifName in [IpMgrSubscribe.IpMgrSubscribe.NOTIFDATA]:
            
            packet = {
                'timestamp': float(notifParams.utcSecs)+float(notifParams.utcUsecs/1000000.0),
                'mac':       tuple(notifParams.macAddress),
                'srcPort':   notifParams.srcPort,
                'destPort':  notifParams.dstPort,
                'payload':   [b for b in notifParams.data],
            }
            
            # log
            if log.isEnabledFor(logging.DEBUG):
                log.debug('dispatching rawDataToLocal from {0}:{1} to port {2} ({3} bytes)'.format(
                        packet['mac'],
                        packet['srcPort'],
                        packet['destPort'],
                        len(packet['payload'])
                    )
                )
            
            # dispatch
            self._dispatch (
                signal       = 'rawDataToLocal',
                data         = packet,
            )
            
        elif notifName in [IpMgrSubscribe.IpMgrSubscribe.NOTIFIPDATA]:
            
            print 'TODO dispatch IPdata {0}'.format(notifParams)
            pass
        
        else:
            
            # dispatch
            self._dispatch (
                signal      =   'networkEvent_{0}'.format(FormatUtils.formatConnectionParams(self.connectParams)),
                data        =   {
                                    'type':        Gateway.Gateway.NOTIF,
                                    'notifName':   notifName,
                                    'notifParams': notifParams,
                                },
            )
        
        # increment stats
        self.statsLock.acquire()
        if notifName not in self.stats:
            self.stats[notifName] = 0
        self.stats[notifName] += 1
        self.statsLock.release()
    
    def _disconnectedCallback(self,notifName=None,notifParams=None):
        
        # log
        log.warning('disconnection indication received')
        
        # dispatch
        dispatcher.send(
            signal      =   'deviceCommunicationError',
            data        =   {
                                'connectionParam': self.connectParams,
                                'reason':          'disconnection indication received',
                            },
        )
