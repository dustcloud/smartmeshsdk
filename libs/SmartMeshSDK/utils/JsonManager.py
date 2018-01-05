#!/usr/bin/python

#============================ define ==========================================

#============================ imports =========================================

import os
import collections
import time
import datetime
import threading
import copy
import pickle
import traceback

if os.name=='nt':       # Windows
   import _winreg as winreg
elif os.name=='posix':  # Linux
   import glob

import json

from SmartMeshSDK                      import sdk_version
from SmartMeshSDK.utils                import FormatUtils as u, \
                                              SerialScanner
from SmartMeshSDK.IpMgrConnectorSerial import IpMgrConnectorSerial
from SmartMeshSDK.IpMgrConnectorMux    import IpMgrSubscribe
from SmartMeshSDK.ApiException         import APIError,      \
                                              ConnectionError
from SmartMeshSDK.protocols.Hr         import HrParser
from SmartMeshSDK.protocols.oap        import OAPDispatcher, \
                                              OAPClient,     \
                                              OAPMessage,    \
                                              OAPDefines as oapdefs

#============================ helpers =========================================

def currentUtcTime():
    return time.strftime("%a, %d %b %Y %H:%M:%S UTC", time.gmtime())

def logCrash(threadName,err):
    output  = []
    output += ["============================================================="]
    output += [currentUtcTime()]
    output += [""]
    output += ["CRASH in Thread {0}!".format(threadName)]
    output += [""]
    output += ["=== exception type ==="]
    output += [str(type(err))]
    output += [""]
    output += ["=== traceback ==="]
    output += [traceback.format_exc()]
    output  = '\n'.join(output)
    
    print output

def reversedict(d):
    return dict((v,k) for (k,v) in d.iteritems())

def stringifyMacIpAddresses(indict):
    '''
    in: {
        'field1':     123,
        'macAddress': [0,1,2,3,4,5,6,7],
    }
    out: {
        'field1':     123,
        'macAddress': '00-01-02-03-04-05-06-07',
    }
    '''
    outdict = indict
    for name in ['macAddress','source','dest']:
        try:
            assert len(outdict[name])==8
            outdict[name] = u.formatMacString(outdict[name])
        except KeyError:
            pass
    for name in ['ipv6Address']:
        try:
            assert len(outdict[name])==16
            outdict[name] = u.formatIpString(outdict[name])
        except KeyError:
            pass
    return outdict

def destringifyMacAddresses(d):
    '''
    in: {
        'field1':     123,
        'macAddress': '00-01-02-03-04-05-06-07',
    }
    out: {
        'field1':     123,
        'macAddress': [0,1,2,3,4,5,6,7],
    }
    returns whether was destringified
    '''
    wasDestringified = False
    for name in ['macAddress','source','dest']:
        try:
            if type(d[name]) in [str,unicode]:
                d[name] = [int(b,16) for b in d[name].split('-')]
                wasDestringified = True
        except KeyError:
            pass
    return wasDestringified

#============================ classes =========================================

class ManagerHandler(threading.Thread):
    '''
    \brief Connects to the manager, re-connects automatically
    '''
    
    def __init__(self,serialport,notifHandler):

        # store params
        self.serialport      = serialport
        self.notifHandler    = notifHandler
        
        # local variables
        self.reconnectEvent  = threading.Event()
        self.dataLock        = threading.RLock()
        self.connector       = None
        self.goOn            = True

        # start the thread
        threading.Thread.__init__(self)
        self.name            = 'ManagerHandler@{0}'.format(self.serialport)
        self.start()
    
    def run(self):
        try:
            while self.goOn:
                try:
                    
                    # connect to the manager
                    self.connector = IpMgrConnectorSerial.IpMgrConnectorSerial()
                    self.connector.connect({
                        'port': self.serialport,
                    })

                    # subscribe to notifications
                    self.subscriber = IpMgrSubscribe.IpMgrSubscribe(self.connector)
                    self.subscriber.start()
                    self.subscriber.subscribe(
                        notifTypes =    [
                                            IpMgrSubscribe.IpMgrSubscribe.NOTIFDATA,
                                        ],
                        fun =           self._notifAll,
                        isRlbl =        False,
                    )
                    self.subscriber.subscribe(
                        notifTypes =    [
                                            IpMgrSubscribe.IpMgrSubscribe.NOTIFEVENT,
                                            IpMgrSubscribe.IpMgrSubscribe.NOTIFHEALTHREPORT,
                                            IpMgrSubscribe.IpMgrSubscribe.NOTIFIPDATA,
                                            IpMgrSubscribe.IpMgrSubscribe.NOTIFLOG,
                                        ],
                        fun =           self._notifAll,
                        isRlbl =        True,
                    )
                    self.subscriber.subscribe(
                        notifTypes =    [
                                            IpMgrSubscribe.IpMgrSubscribe.ERROR,
                                            IpMgrSubscribe.IpMgrSubscribe.FINISH,
                                        ],
                        fun =           self._notifErrorFinish,
                        isRlbl =        True,
                    )

                except Exception as err:
                    
                    try:
                        self.connector.disconnect()
                    except Exception:
                        pass

                    # wait to reconnect
                    time.sleep(1)

                else:
                    self.reconnectEvent.clear()
                    self.reconnectEvent.wait()
                    
                    try:
                        self.connector.disconnect()
                    except Exception:
                        pass

        except Exception as err:
            logCrash(self.name,err)
    
    #======================== public ==========================================
    
    def close(self):

        try:
            self.connector.disconnect()
        except Exception:
            pass

        self.goOn = False
    
    def isConnected(self):
        try:
            return self.connector.isConnected
        except AttributeError:
            return False
    
    #======================== private =========================================

    #=== Dust API notifications
    
    def _notifAll(self, notif_name, dust_notif):
        
        try:
            self.notifHandler(
                self.serialport,
                notif_name,
                dust_notif,
            )
        except Exception as err:
            logCrash(self.name,err)

    def _notifErrorFinish(self,notifName,dust_notif):

        try:
            assert notifName in [
                IpMgrSubscribe.IpMgrSubscribe.ERROR,
                IpMgrSubscribe.IpMgrSubscribe.FINISH,
            ]

            if not self.reconnectEvent.isSet():
                self.reconnectEvent.set()
        except Exception as err:
            logCrash(self.name,err)

class SnapshotThread(threading.Thread):
    '''
    \brief one instance per JsonManager, waits to be triggered, does snapshot on one manager
    '''
    
    def __init__(self,raw_POST,notifCb):
        
        # store params
        self.raw_POST             = raw_POST
        self.notifCb              = notifCb
        
        # local variable
        self.dataLock             = threading.RLock()
        self.snapshotsTodo        = []
        self.snapshotnowSem       = threading.Semaphore(0)
        self.lastsnapshots        = {}
        
        # start the thread
        threading.Thread.__init__(self)
        self.name                 = 'SnapshotThread'
        self.daemon               = True
        self.start()
    
    def run(self):
        try:
            while True:
                
                # wait for trigger
                self.snapshotnowSem.acquire()
                
                # get the manager and correlationID
                with self.dataLock:
                    (manager,correlationID) = self.snapshotsTodo.pop(0)
                
                # do the snapshot
                try:
                    snapshot = {}
                    
                    # timestamp_start
                    snapshot['timestamp_start'] = currentUtcTime()
                    
                    # getSystemInfo()
                    resp = self.raw_POST(
                        commandArray   = ["getSystemInfo"],
                        fields         = {},
                        manager        = manager,
                    )
                    snapshot['getSystemInfo'] = stringifyMacIpAddresses(resp)
                    
                    # getNetworkConfig()
                    resp = self.raw_POST(
                        commandArray   = ["getNetworkConfig"],
                        fields         = {},
                        manager        = manager,
                    )
                    snapshot['getNetworkConfig'] = stringifyMacIpAddresses(resp)
                    
                    # getNetworkInfo()
                    resp = self.raw_POST(
                        commandArray   = ["getNetworkInfo"],
                        fields         = {},
                        manager        = manager,
                    )
                    snapshot['getNetworkInfo'] = stringifyMacIpAddresses(resp)
                    
                    # getMoteConfig() on all motes
                    snapshot['getMoteConfig'] = {}
                    macs       = []
                    currentMac = [0]*8
                    while True:
                        resp = self.raw_POST(
                            commandArray   = ["getMoteConfig"],
                            fields         = {
                                "macAddress": currentMac,
                                "next": True
                            },
                            manager        = manager,
                        )
                        if resp['RC'] != 0:
                            break
                        mac           = resp['macAddress']
                        macString     = u.formatMacString(mac)
                        snapshot['getMoteConfig'][macString] = stringifyMacIpAddresses(resp)
                        macs         += [mac]
                        currentMac    = mac
                    
                    # getMoteInfo() on all motes
                    snapshot['getMoteInfo'] = {}
                    for mac in macs:
                        resp = self.raw_POST(
                            commandArray   = ["getMoteInfo"],
                            fields         = {
                                "macAddress": mac,
                            },
                            manager        = manager,
                        )
                        macString     = u.formatMacString(mac)
                        snapshot['getMoteInfo'][macString] = stringifyMacIpAddresses(resp)
                    
                    # getPathInfo() on all paths on all motes
                    snapshot['getPathInfo'] = {}
                    for mac in macs:
                        macString     = u.formatMacString(mac)
                        snapshot['getPathInfo'][macString] = {}
                        currentPathId  = 0
                        while True:
                            resp = self.raw_POST(
                                commandArray   = ["getNextPathInfo"],
                                fields         = {
                                    "macAddress": mac,
                                    "filter":     0,
                                    "pathId":     currentPathId
                                },
                                manager        = manager,
                            )
                            if resp["RC"] != 0:
                                break
                            snapshot['getPathInfo'][macString][currentPathId] = stringifyMacIpAddresses(resp)
                            currentPathId  = resp["pathId"]
                    
                    # getMoteLinks() on all paths on all motes
                    snapshot['getMoteLinks'] = {}
                    for mac in macs:
                        macString     = u.formatMacString(mac)
                        snapshot['getMoteLinks'][macString] = {}
                        snapshot['getMoteLinks'][macString]['links'] = []
                        currentidx  = 0
                        while True:
                            resp = self.raw_POST(
                                commandArray   = ["getMoteLinks"],
                                fields         = {
                                    "macAddress": mac,
                                    "idx":        currentidx,
                                },
                                manager        = manager,
                            )
                            if resp["RC"] != 0:
                                break
                            # add all "metadata" fields, i.e. every before the list of links
                            for (k,v) in resp.items():
                                if ("_" not in k) and (k not in ['numLinks','idx']):
                                    snapshot['getMoteLinks'][macString][k] = v
                            # populate list of links
                            for i in range(resp['numLinks']):
                                thisLink = {}
                                suffix = '_{0}'.format(i+1)
                                for (k,v) in resp.items():
                                    if k.endswith(suffix):
                                        name = k[:-len(suffix)]
                                        thisLink[name]   = v
                                snapshot['getMoteLinks'][macString]['links'] += [thisLink]
                            currentidx += resp['numLinks']
                    
                    # timestamp_stop
                    snapshot['timestamp_stop'] = currentUtcTime()
                    
                    # epoch_stop
                    snapshot['epoch_stop']     = time.time()
                    
                    # remember the last snapshot for each manager
                    with self.dataLock:
                        self.lastsnapshots[manager] = snapshot
                    
                except Exception as err:
                    notifJson    = {
                        'valid':    False,
                        'err':      str(err),
                    }
                else:
                    notifJson    = {
                        'valid':    True,
                        'snapshot': snapshot,
                    }
                finally:
                    notifJson['manager']              = manager
                    if correlationID:
                        notifJson['correlationID']    = correlationID
                    self.notifCb(
                        notifName    = 'snapshot',
                        notifJson    = notifJson,
                    )
        
        except Exception as err:
            logCrash(self.name,err)

    #======================== public ==========================================
    
    def doSnapshot(self,manager,correlationID):
        with self.dataLock:
            self.snapshotsTodo += [(manager,correlationID)]
        self.snapshotnowSem.release()
    
    def getLastsnapshots(self):
        with self.dataLock:
            returnVal = copy.deepcopy(self.lastsnapshots)
        now = time.time()
        for m in returnVal.keys():
            returnVal[m]['age_seconds'] = int(now-returnVal[m]['epoch_stop'])
        return returnVal

class DeleMgrThread(threading.Thread):
    
    HOUSEKEEPING_PERIOD = 10
    
    def __init__(self,jsonManager):
        # store params
        self.jsonManager = jsonManager
        
        # start thread
        threading.Thread.__init__(self)
        self.name                 = 'DeleMgrThread'
        self.daemon               = True
        self.start()
    
    def run(self):
        while True:
            for (m,c) in self.jsonManager.status_GET()['managers'].items():
                if c=='disconnected':
                    self.jsonManager.managers_DELETE([m])
            time.sleep(self.HOUSEKEEPING_PERIOD)

class JsonManager(object):
    
    OAP_TIMEOUT = 30.000
    
    def __init__(self, autoaddmgr, autodeletemgr, serialport, notifCb, configfilename=None):
        
        # store params
        self.autoaddmgr           = autoaddmgr
        self.autodeletemgr        = autodeletemgr
        self.serialport           = serialport
        self.notifCb              = notifCb
        self.configfilename       = configfilename
        
        # local variables
        self.startTime            = time.time()
        self.dataLock             = threading.RLock()
        self._loadConfig()   # populates self.config dictionnary
        self.managerHandlers      = {}
        self.oapDispatch          = OAPDispatcher.OAPDispatcher()
        self.oapDispatch.register_notif_handler(self._manager_oap_notif_handler)
        self.oapClients           = {}
        self.snapshotThread       = SnapshotThread(
            self.raw_POST,
            self.notifCb,
        )
        self.outstandingEvents    = {}
        self.responses            = {}
        self.hrParser             = HrParser.HrParser()
        
        # connect to managers (if any)
        self._syncManagers()
        
        # if autoaddmgr, have SerialScanner looks for manager
        if self.autoaddmgr:
            self.serialScanner = SerialScanner.SerialScanner()
            self.serialScanner.availableManagerNotifier(
               cb     = self._availablemanagers_cb,
               period = 60,
            )
        
        # if autodeletemgr, start DeleMgrThread
        if self.autodeletemgr:
            DeleMgrThread(self)
    
    #======================== public ==========================================
    
    #=== status
    
    def status_GET(self):
        return {
            'SmartMesh SDK version': '.'.join([str(b) for b in sdk_version.VERSION]),
            'current time':          self._formatTime(),
            'running since':         '{0} ({1} ago)'.format(
                self._formatTime(self.startTime),
                datetime.timedelta(seconds=time.time()-self.startTime)
            ),
            'threads running':       [t.getName() for t in threading.enumerate()],
            'managers':              self._formatManagersStatus(),
        }
    
    #=== raw
    
    def raw_POST(self, commandArray, fields, manager):
        if type(manager)==int:
            manager = sorted(self.managerHandlers.keys())[manager]
        
        # mac addresses: '00-01-02-03-04-05-06-07' -> [0,1,2,3,4,5,6,7]
        wasDestringified = destringifyMacAddresses(fields)
        
        with self.dataLock:
            try:
                returnVal = self.managerHandlers[manager].connector.send(
                    commandArray = commandArray,
                    fields       = fields,
                )
            except APIError as err:
                returnVal = {
                    'RC': err.rc,
                }
        
        if wasDestringified:
            # mac addresses: [0,1,2,3,4,5,6,7] -> '00-01-02-03-04-05-06-07'
            stringifyMacIpAddresses(returnVal)
        
        return returnVal
    
    #=== oap
    
    # /info
    
    def oap_info_GET(self,mac):
        return self._oap_send_and_wait_for_reply(
            mac         = mac,
            method      = OAPMessage.CmdType.GET,
            resource    = 'info',
        )
    
    # /main
    
    def oap_main_GET(self,mac):
        return self._oap_send_and_wait_for_reply(
            mac         = mac,
            method      = OAPMessage.CmdType.GET,
            resource    = 'main',
        )
    
    def oap_main_PUT(self,mac,body):
        return self._oap_send_and_wait_for_reply(
            mac         = mac,
            method      = OAPMessage.CmdType.PUT,
            resource    = 'main',
            body        = body,
        )
    
    # /digital_in
    
    def oap_digital_in_GET(self,mac,pin):
        return self._oap_send_and_wait_for_reply(
            mac         = mac,
            method      = OAPMessage.CmdType.GET,
            resource    = 'digital_in',
            subresource = pin,
        )
    
    def oap_digital_in_PUT(self,mac,pin,body):
        return self._oap_send_and_wait_for_reply(
            mac         = mac,
            method      = OAPMessage.CmdType.PUT,
            resource    = 'digital_in',
            subresource = pin,
            body        = body,
        )
    
    # /digital_out
    
    def oap_digital_out_PUT(self,mac,pin,body):
        return self._oap_send_and_wait_for_reply(
            mac         = mac,
            method      = OAPMessage.CmdType.PUT,
            resource    = 'digital_out',
            subresource = pin,
            body        = body,
        )
    
    # /analog
    
    def oap_analog_GET(self,mac,pin):
        return self._oap_send_and_wait_for_reply(
            mac         = mac,
            method      = OAPMessage.CmdType.GET,
            resource    = 'analog',
            subresource = pin,
        )
    
    def oap_analog_PUT(self,mac,pin,body):
        return self._oap_send_and_wait_for_reply(
            mac         = mac,
            method      = OAPMessage.CmdType.PUT,
            resource    = 'analog',
            subresource = pin,
            body        = body,
        )
    
    # /temperature
    
    def oap_temperature_GET(self,mac):
        return self._oap_send_and_wait_for_reply(
            mac         = mac,
            method      = OAPMessage.CmdType.GET,
            resource    = 'temperature',
        )
    
    def oap_temperature_PUT(self,mac,body):
        return self._oap_send_and_wait_for_reply(
            mac         = mac,
            method      = OAPMessage.CmdType.PUT,
            resource    = 'temperature',
            body        = body,
        )
    
    # /pkgen
    
    def oap_pkgen_echo_GET(self,mac):
        return self._oap_send_and_wait_for_reply(
            mac         = mac,
            method      = OAPMessage.CmdType.GET,
            resource    = 'pkgen',
            subresource = 0,
        )
    
    def oap_pkgen_PUT(self,mac,body):
        return self._oap_send_and_wait_for_reply(
            mac         = mac,
            method      = OAPMessage.CmdType.PUT,
            resource    = 'pkgen',
            body        = body,
        )
    
    #=== helpers
    
    def serialports_GET(self):
        try:
            serialports = []
            
            if os.name=='nt':
                key  = winreg.OpenKey(winreg.HKEY_LOCAL_MACHINE, 'HARDWARE\\DEVICEMAP\\SERIALCOMM')
                for i in range(winreg.QueryInfoKey(key)[1]):
                    try:
                        val = winreg.EnumValue(key,i)
                    except:
                        pass
                    else:
                        if val[0].find('VCP')>-1:
                            serialports.append(str(val[1]))
            elif os.name=='posix':
                serialports = glob.glob('/dev/ttyUSB*')
            
            serialports.sort()
            
            return {
                'serialports': serialports
            }
        except Exception as err:
            return ['Could not scan for serial port. Error={0}'.format(err)]
    
    def motes_GET(self):
        with self.dataLock:
            returnVal = {m:self._list_motes_per_manager(m) for m in self.managerHandlers.keys()}
        return returnVal
    
    def oapmotes_GET(self):
        with self.dataLock:
            return {'oapmotes': self.oapClients.keys(),}
    
    def snapshot_POST(self,manager,correlationID=None):
        self.snapshotThread.doSnapshot(manager,correlationID)
    
    def snapshot_GET(self):
        return self.snapshotThread.getLastsnapshots()
    
    def managers_PUT(self,newmanagers):
        with self.dataLock:
            for m in newmanagers:
                if m not in self.config['managers']:
                    self.config['managers'] += [m]
        self._saveConfig()
        self._syncManagers()
    
    def managers_DELETE(self,oldmanagers):
        with self.dataLock:
            for m in oldmanagers:
                try:
                    self.config['managers'].remove(m)
                except ValueError:
                    pass # happens when manager doesn't exist
        self._saveConfig()
        self._syncManagers()
    
    #=== config
    
    def config_GET(self):
        with self.dataLock:
           return copy.deepcopy(self.config)
    
    def config_POST(self,newconfig):
        with self.dataLock:
            self.config = self._recursive_dict_update(
                self.config,
                newconfig
            )
        self._saveConfig()
        self._syncManagers()
        with self.dataLock:
           return copy.deepcopy(self.config)
    
    #=== close
    
    def close(self):
        for (k,v) in self.managerHandlers.items():
            try:
                v.close()
            except:
                pass
    
    #======================== private =========================================
    
    #=== api
    
    # status
    
    def _formatManagersStatus(self):
        returnVal = {}
        
        with self.dataLock:
            for (k,v) in self.managerHandlers.items():
                if v.isConnected():
                    returnVal[k] = 'connected'
                else:
                    returnVal[k] = 'disconnected'
        
        return returnVal
    
    # oap
    
    def _oap_send_and_wait_for_reply(self, mac, method, resource, subresource=None, body={}):
        
        # use only lowercase
        mac = mac.lower()
        
        # add an oapClient, if needed
        self._oap_add_client_if_needed(mac)
        
        # create data_tags
        data_tags = []
        if method==OAPMessage.CmdType.PUT:
            for (i,(n,t,d)) in enumerate(oapdefs.FIELDS[resource]):
                if d.count('w'):
                    if   t=='INT8U':
                        data_tags += [OAPMessage.TLVByte(   t=i,v=body[n])]
                    elif t=='INT16U':
                        data_tags += [OAPMessage.TLVShort(  t=i,v=body[n])]
                    elif t=='INT32U':
                        data_tags += [OAPMessage.TLVLong(   t=i,v=body[n])]
                    elif t=='INT8U[16]':
                        temp = body[n]
                        temp = ''.join([chr(int(b,16)) for b in [temp[2*j:2*j+2] for j in range(len(temp)/2)]])
                        data_tags += [OAPMessage.TLVString( t=i,v=temp)]
        
        # send OAP request
        addr           = [b for b in oapdefs.ADDRESS[resource]]
        if subresource!=None:
            addr      += [subresource]
        self.oapClients[mac].send(
            cmd_type   = method,
            addr       = addr,
            data_tags  = data_tags,
            cb         = self._oap_handle_response,
        )
        
        # wait for and handle OAP response
        with self.dataLock:
            if mac in self.outstandingEvents:
                raise SystemError('busy waiting for response')
            event = threading.Event()
            self.outstandingEvents[mac] = event
        if event.wait(self.OAP_TIMEOUT):
            # received response
            with self.dataLock:
                response = self.responses[mac]
                del self.responses[mac]
            return self._oap_format_response(resource,response)
        else:
            # timeout
            with self.dataLock:
                del self.outstandingEvents[mac]
            bottle.response.status = 504 # Gateway Timeout
            bottle.response.content_type = 'application/json'
            return json.dumps({
                'body': 'timeout!',
            })
    
    def _oap_handle_response(self, mac, oap_resp):
        macString = u.formatMacString(mac)
        
        with self.dataLock:
            if macString in self.responses:
                raise SystemError('response unread')
            
            if macString in self.outstandingEvents:
                self.responses[macString] = oap_resp
                self.outstandingEvents[macString].set()
                del self.outstandingEvents[macString]
            else:
                # received a response I'm not waiting for anymore (increase timeout?)'
                pass
    
    def _oap_format_response(self,resource,response):
        '''
        {
            'command': 1,
            'result': 0,
            'tags': [
                (255, 1, array('B', [0])),
                (0, 1, array('B', [1])),
                (1, 1, array('B', [3])),
                (2, 1, array('B', [0])),
                (3, 2, array('B', [0, 24])),
                (4, 2, array('B', [0, 1])),
                (5, 4, array('B', [0, 0, 0, 0])),
                (6, 4, array('B', [0, 0, 0, 0]))
            ]
        }
        {
            'resource': [0],
            'method':   1,
            'status':   0,
            'fields': {
                0: [1],
                1: [3],
                2: [0],
                3: [0, 24],
                4: [0, 1],
                5: [0, 0, 0, 0],
                6: [0, 0, 0, 0]
            }
        }
        '''
        tags = {k:v.tolist() for (k,_,v) in response['tags']}
        returnVal = {}
        # status
        returnVal['status']       = reversedict(oapdefs.RC)[response['result']]
        # resource
        returnVal['resource']     = reversedict(oapdefs.ADDRESS)[tuple(tags[255])]
        del tags[255]
        # method
        returnVal['method']       = reversedict(oapdefs.COMMAND)[response['command']]
        # fields
        desc = oapdefs.FIELDS[resource]
        fields = {}
        for (k,v) in tags.items():
            (n,t,d)               = desc[k]
            if t=='INT8U[16]':
                fields[n]         = ''.join(["%.2x"%i for i in v])
            elif v==[]:
                fields[n]         = v
            else:
                fields[n]         = int(''.join([chr(b) for b in v]).encode('hex'), 16)
        returnVal['fields']       = fields
        return returnVal
    
    def _oap_add_client_if_needed(self,mac):
        if type(mac)==str:
            macString = mac
            mac       = [int(b,16) for b in mac.split('-')]
        else:
            macString = u.formatMacString(mac)
        
        with self.dataLock:
            if macString not in self.oapClients:
                # get MACs per manager
                for (manager,motes) in self.motes_GET().items():
                    if macString in manager:
                       break
                # create OAPClient
                self.oapClients[macString] = OAPClient.OAPClient(
                    mac,
                    self.managerHandlers[manager].connector.dn_sendData,
                    self.oapDispatch,
                )
    
    # helpers
    
    def _list_motes_per_manager(self,manager):
        returnVal = []
        
        try:
            currentMac     = (0,0,0,0,0,0,0,0) # start getMoteConfig() iteration with the 0 MAC address
            continueAsking = True
            while continueAsking:
                try:
                    with self.dataLock:
                        res = self.managerHandlers[manager].connector.dn_getMoteConfig(currentMac,True)
                except APIError:
                    continueAsking = False
                else:
                    if ((not res.isAP) and (res.state in [4,])):
                        returnVal.append(u.formatMacString(res.macAddress))
                    currentMac = res.macAddress
        except ConnectionError as err:
            pass # happens when manager is disconnected
        
        return returnVal
    
    # manager management
    
    def _syncManagers(self):
        with self.dataLock:
            # add
            for m in self.config['managers']:
                if m not in self.managerHandlers:
                    self.managerHandlers[m] = ManagerHandler(m,self._manager_raw_notif_handler)
            # remove
            for m in self.managerHandlers.keys():
                if m not in self.config['managers']:
                    self.managerHandlers[m].close()
                    del self.managerHandlers[m]
    
    def _availablemanagers_cb(self,serialport):
        self.managers_PUT([serialport])
    
    # config
    
    def _loadConfig(self):
        with self.dataLock:
            try:
                if self.configfilename:
                    self.config = pickle.load(open(self.configfilename,"rb"))
                else:
                   raise IOError
            except IOError as err:
                if self.serialport:
                    managers = [self.serialport]
                else:
                    managers = []
                self.config     = {
                    'managers':         managers,
                    'notification_urls': {
                        'event':            [
                            'http://127.0.0.1:1880/event',
                            'http://127.0.0.1:8081/event',
                        ],
                        'notifLog':         [
                            'http://127.0.0.1:1880/notifLog',
                        ],
                        'notifData':        [
                            'http://127.0.0.1:1880/notifData',
                        ],
                        'notifIpData':      [
                            'http://127.0.0.1:1880/notifIpData',
                        ],
                        'notifHealthReport':[
                            'http://127.0.0.1:1880/notifHealthReport',
                        ],
                        'oap':              [
                            'http://127.0.0.1:1880/oap',
                        ],
                        'hr':               [
                            'http://127.0.0.1:1880/hr',
                        ],
                        'snapshot':         [
                            'http://127.0.0.1:1880/snapshot',
                            'http://127.0.0.1:8081/snapshot',
                        ],
                    }
                }
                self._saveConfig()
    
    def _saveConfig(self):
        if self.configfilename:
            with self.dataLock:
                pickle.dump(self.config, open(self.configfilename,"wb"))
    
    #=== notifications
    
    def _manager_raw_notif_handler(self,manager,notifName,notif):
        
        # parse further
        if   notifName==IpMgrSubscribe.IpMgrSubscribe.NOTIFDATA:
            # try to parse data notifications as OAP (fails if not OAP payload, no problem)
            self.oapDispatch.dispatch_pkt(notifName,notif)
        elif notifName==IpMgrSubscribe.IpMgrSubscribe.NOTIFHEALTHREPORT:
            hr  = self.hrParser.parseHr(notif.payload)
            # POST HR to some URL
            self.notifCb(
                notifName    = 'hr',
                notifJson    = {
                    'name':    'hr',
                    'mac':     u.formatMacString(notif.macAddress),
                    'hr':      hr,
                },
            )
        
        # POST raw notification to some URL
        if notifName.startswith('event'):
            nm           = 'event'
        else:
            nm           = notifName
        fields = stringifyMacIpAddresses(notif._asdict())
        self.notifCb(
            notifName    = nm,
            notifJson    = {
                'manager': manager,
                'name':    notifName,
                'fields':  fields,
            },
        )
    
    def _manager_oap_notif_handler(self,mac,notif):
        
        macString = u.formatMacString(mac)
        
        # add an oapClient, if needed
        self._oap_add_client_if_needed(mac)
        
        # POST OAP notification to some URLs
        fields = stringifyMacIpAddresses(notif._asdict())
        self.notifCb(
            notifName    = 'oap',
            notifJson    = {
                'name':    'oap',
                'mac':     macString,
                'fields':  fields,
            },
        )
    
    #=== formatting
    
    def _formatTime(self,ts=None):
        return time.strftime("%m/%d/%Y %H:%M:%S",time.localtime(ts))
    
    #=== helpers
    
    def _recursive_dict_update(self,d,u):
        for k, v in u.items():
            if isinstance(v, collections.Mapping):
                r = self._recursive_dict_update(d.get(k, {}), v)
                d[k] = r
            else:
                d[k] = u[k]
        return d
