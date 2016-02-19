#!/usr/bin/python

#============================ adjust path =====================================

import sys
import os
if __name__ == "__main__":
    here = sys.path[0]
    sys.path.insert(0, os.path.join(here, '..', '..','libs'))
    sys.path.insert(0, os.path.join(here, '..', '..','external_libs'))

#============================ verify installation =============================

from SmartMeshSDK.utils import SmsdkInstallVerifier
(goodToGo,reason) = SmsdkInstallVerifier.verifyComponents(
    [
        SmsdkInstallVerifier.PYTHON,
        SmsdkInstallVerifier.PYSERIAL,
    ]
)
if not goodToGo:
    print "Your installation does not allow this application to run:\n"
    print reason
    raw_input("Press any button to exit")
    sys.exit(1)

#============================ imports =========================================

import threading
import copy
import time
import traceback

from   SmartMeshSDK.utils              import AppUtils,                   \
                                              FormatUtils,                \
                                              LatencyCalculator
from   SmartMeshSDK.ApiDefinition      import IpMgrDefinition,            \
                                              HartMgrDefinition
from   SmartMeshSDK.IpMgrConnectorMux  import IpMgrSubscribe,             \
                                              IpMgrConnectorMux
from   SmartMeshSDK.ApiException       import APIError
from   SmartMeshSDK.protocols.oap      import OAPDispatcher,              \
                                              OAPClient,                  \
                                              OAPMessage,                 \
                                              OAPNotif
from   dustUI                          import dustWindow,                 \
                                              dustFrameApi,               \
                                              dustFrameConnection,        \
                                              dustFrameMoteList,          \
                                              dustFrameText,              \
                                              dustStyle

#============================ logging =========================================

# local

import logging
class NullHandler(logging.Handler):
    def emit(self, record):
        pass
log = logging.getLogger('App')
log.setLevel(logging.ERROR)
log.addHandler(NullHandler())

# global

AppUtils.configureLogging()

#============================ defines =========================================

GUI_UPDATEPERIOD = 250   # in ms

# columns names
COL_LED          = 'toggle led'
COL_NOTIF_DATA   = IpMgrSubscribe.IpMgrSubscribe.NOTIFDATA
COL_NOTIF_IPDATA = IpMgrSubscribe.IpMgrSubscribe.NOTIFIPDATA
COL_NOTIF_HR     = IpMgrSubscribe.IpMgrSubscribe.NOTIFHEALTHREPORT
COL_LAT_MIN      = 'lat. min'
COL_LAT_CUR      = 'lat. current'
COL_LAT_MAX      = 'lat. max'
COL_NOTIF_CLR    = 'clear counters'
COL_TEMPERATURE  = 'temperature'
COL_TEMP_NUM     = 'num. temp'
COL_TEMP_CLR     = 'clear temp'
COL_TEMP_RATE    = 'publish rate (ms)'

#============================ body ============================================

##
# \addtogroup TempMonitor
# \{
# 

class HartMgrSubscriber(threading.Thread):
    
    def __init__(self,connector,dataCb,eventCb,disconnectedCb):
        
        # log
        log.debug("Initialize HartMgrSubscriber")
        
        # record variables
        self.connector       = connector
        self.dataCb          = dataCb
        self.eventCb         = eventCb
        self.disconnectedCb  = disconnectedCb
        
        # initialize parent class
        threading.Thread.__init__(self)
        
        # give this thread a name
        self.name            = "HartMgrSubscriber"
        
        # subscribe to data
        self.connector.dn_subscribe('data event-network')
    
    def run(self):
        log.debug("HartMgrSubscriber starts running")
        keepListening = True
        while keepListening:
            try:
                input = self.connector.getNotificationInternal(-1)
            except (ConnectionError,QueueError) as err:
                keepListening = False
            else:
                if input:
                    log.debug("HartMgrSubscriber received {0}".format(input))
                    if   input[0][0] in ['data']:
                        self.dataCb('.'.join(input[0]),input[1])
                    elif input[0][0] in ['event']:
                        self.eventCb(input[0][1],input[1])
                    else:
                        raise SystemError("No callback for {0}".format(input[0]))
                else:
                    keepListening = False
        self.disconnectedCb()

class notifClient(object):
    
    def __init__(self, apiDef, connector, disconnectedCallback, latencyCalculator):
        
        # store params
        self.apiDef               = apiDef
        self.connector            = connector
        self.disconnectedCallback = disconnectedCallback
        self.latencyCalculator    = latencyCalculator
        
        # log
        log.debug("Initialize notifClient")
        
        # variables
        self.dataLock             = threading.Lock()
        self.isMoteActive         = {}
        self.data                 = {}
        self.updates              = {}
        
        # subscriber
        if   isinstance(self.apiDef,IpMgrDefinition.IpMgrDefinition):
            # we are connected to an IP manager
            
            self.subscriber = IpMgrSubscribe.IpMgrSubscribe(self.connector)
            self.subscriber.start()
            self.subscriber.subscribe(
                notifTypes =    [
                                    IpMgrSubscribe.IpMgrSubscribe.NOTIFDATA,
                                ],
                fun =           self._dataCallback,
                isRlbl =        False,
            )
            self.subscriber.subscribe(
                notifTypes =    [
                                    IpMgrSubscribe.IpMgrSubscribe.NOTIFEVENT,
                                ],
                fun =           self._eventCallback,
                isRlbl =        True,
            )
            self.subscriber.subscribe(
                notifTypes =    [
                                    IpMgrSubscribe.IpMgrSubscribe.ERROR,
                                    IpMgrSubscribe.IpMgrSubscribe.FINISH,
                                ],
                fun =           self.disconnectedCallback,
                isRlbl =        True,
            )
        
        elif isinstance(self.apiDef,HartMgrDefinition.HartMgrDefinition):
            # we are connected to a HART manager
            
            self.subscriber = HartMgrSubscriber(self.connector,
                                                self._dataCallback,
                                                self._eventCallback,
                                                self.disconnectedCallback)
            self.subscriber.start()
        
        else:
            output = "apiDef of type {0} unexpected".format(type(self.apiDef))
            log.critical(output)
            print output
            raise SystemError(output)
        
        # OAP dispatcher
        self.oap_dispatch = OAPDispatcher.OAPDispatcher()
        self.oap_dispatch.register_notif_handler(self._handle_oap_notif)
    
    #======================== public ==========================================
    
    def getData(self):
        self.dataLock.acquire()
        returnIsMoteActive   = copy.deepcopy(self.isMoteActive)
        returnData           = copy.deepcopy(self.data)
        returnUpdates        = copy.deepcopy(self.updates)
        self.updates         = {}
        self.dataLock.release()
        return (returnIsMoteActive,returnData,returnUpdates)
    
    def getOapDispatcher(self):
        return self.oap_dispatch
    
    def clearNotifCounters(self,mac):
        self.dataLock.acquire()
        self.updates = {}
        if mac in self.data:
            self.updates[mac] = []
            for k,v in self.data[mac].items():
                if   k in [COL_NOTIF_DATA,
                           COL_NOTIF_IPDATA,
                           COL_NOTIF_HR]:
                    self.updates[mac].append(k)
                    self.data[mac][k] = 0
                elif k in [COL_LAT_MIN,
                           COL_LAT_CUR,
                           COL_LAT_MAX,]:
                    self.updates[mac].append(k)
                    self.data[mac][k] = '-'
        self.dataLock.release()
    
    def clearTemp(self,mac):
        self.dataLock.acquire()
        self.updates = {}
        if mac in self.data:
            self.updates[mac] = []
            for k,v in self.data[mac].items():
                if   k in [COL_TEMP_NUM,]:
                    self.updates[mac].append(k)
                    self.data[mac][k] = 0
                if   k in [COL_TEMPERATURE,]:
                    self.updates[mac].append(k)
                    self.data[mac][k] = '-'
        self.dataLock.release()
        
    def disconnect(self):
        self.connector.disconnect()
    
    #======================== private =========================================
    
    def _dataCallback(self, notifName, notifParams):
        
        # log
        if   isinstance(self.apiDef,IpMgrDefinition.IpMgrDefinition):
            # IpMgrSubscribe generates a named tuple
            log.debug(
                "notifClient._dataCallback {0}:\n{1}".format(
                    notifName,
                    FormatUtils.formatNamedTuple(notifParams)
                )
            )
        elif isinstance(self.apiDef,HartMgrDefinition.HartMgrDefinition):
            # HartMgrSubscriber generates a dictionary
            log.debug(
                "notifClient._dataCallback {0}:\n{1}".format(
                    notifName,
                    FormatUtils.formatDictionnary(notifParams)
                )
            )
        else:
            output = "apiDef of type {0} unexpected".format(type(self.apiDef))
            log.critical(output)
            print output
            raise SystemError(output)
        
        # record current time
        timeNow = time.time()
        
        # read MAC address from notification
        mac = self._getMacFromNotifParams(notifParams)
        
        # lock the data structure
        self.dataLock.acquire()
        
        # add mac/type to data, if necessary
        if mac not in self.data:
            self.data[mac] = {}
        if notifName not in self.data[mac]:
            self.data[mac][notifName] = 0
            
        # add mac/type to updates, if necessary
        if mac not in self.updates:
            self.updates[mac] = []
        if notifName not in self.updates[mac]:
            self.updates[mac].append(notifName)
        
        # increment counter
        self.data[mac][notifName] += 1
        
        # transform HART OAP notification into equivalent IP version
        if isinstance(self.apiDef,HartMgrDefinition.HartMgrDefinition):
            # we are connected to a HART manager
            
            if (notifName in ['data']) and (len(notifParams['payload'])>2):
                notifName = IpMgrSubscribe.IpMgrSubscribe.NOTIFDATA
                
                notifParams = IpMgrConnectorMux.IpMgrConnectorMux.Tuple_notifData(
                    utcSecs       = int(notifParams['time']/1000),
                    utcUsecs      = (notifParams['time']%1000)*1000,
                    macAddress    = mac,
                    srcPort       = OAPMessage.OAP_PORT,
                    dstPort       = OAPMessage.OAP_PORT,
                    data          = tuple(notifParams['payload'][2:]),
                )
        
        # calculate latency
        try:
            if notifName in [IpMgrSubscribe.IpMgrSubscribe.NOTIFDATA,
                             IpMgrSubscribe.IpMgrSubscribe.NOTIFIPDATA,]:
                try:
                    latency = self.latencyCalculator.getLatency(
                            float(notifParams.utcSecs)+(float(notifParams.utcUsecs)/1000000.0),
                            timeNow)
                    # lat. current
                    if COL_LAT_CUR not in self.data[mac]:
                        self.data[mac][COL_LAT_CUR] = '-'
                    if COL_LAT_CUR not in self.updates[mac]:
                        self.updates[mac].append(COL_LAT_CUR)
                    self.data[mac][COL_LAT_CUR] = latency
                    # lat. min
                    if (
                        (
                           (COL_LAT_MIN in self.data[mac])
                           and
                           (latency<self.data[mac][COL_LAT_MIN])
                        )
                        or
                        (
                           (COL_LAT_MIN not in self.data[mac])
                        )
                        or
                        (
                           (COL_LAT_MIN in self.data[mac])
                           and
                           (self.data[mac][COL_LAT_MIN]=='-')
                        )
                       ):
                        if COL_LAT_MIN not in self.data[mac]:
                            self.data[mac][COL_LAT_MIN] = '-'
                        if COL_LAT_MIN not in self.updates[mac]:
                            self.updates[mac].append(COL_LAT_MIN)
                        self.data[mac][COL_LAT_MIN] = latency
                    # max
                    if (
                        (
                           (COL_LAT_MAX in self.data[mac])
                           and
                           (latency>self.data[mac][COL_LAT_MAX])
                        )
                        or
                        (
                           (COL_LAT_MAX not in self.data[mac])
                        )
                        or
                        (
                           (COL_LAT_MAX in self.data[mac])
                           and
                           (self.data[mac][COL_LAT_MAX]=='-')
                        )
                       ):
                        if COL_LAT_MAX not in self.data[mac]:
                            self.data[mac][COL_LAT_MAX] = '-'
                        if COL_LAT_MAX not in self.updates[mac]:
                            self.updates[mac].append(COL_LAT_MAX)
                        self.data[mac][COL_LAT_MAX] = latency
                except RuntimeError:
                    # can happen if latency calculator hasn't acquired lock yet
                    pass
        except Exception as err:
            print err
        
        # unlock the data structure
        self.dataLock.release()
        
        # parse OAP packet
        if notifName in [IpMgrSubscribe.IpMgrSubscribe.NOTIFDATA]:
            self.oap_dispatch.dispatch_pkt(notifName, notifParams)
    
    def _eventCallback(self, notifName, notifParams):
        
        try:
        
            # log
            log.debug("notifClient._eventCallback {0} {1}".format(notifName, notifParams))
            
            # lock the data structure
            self.dataLock.acquire()
            
            if   isinstance(self.apiDef,IpMgrDefinition.IpMgrDefinition):
                
                if notifName in [IpMgrSubscribe.IpMgrSubscribe.EVENTMOTEOPERATIONAL]:
                    mac = self._getMacFromNotifParams(notifParams)
                    self.isMoteActive[mac] = True
                    
                if notifName in [IpMgrSubscribe.IpMgrSubscribe.EVENTMOTELOST]:
                    mac = self._getMacFromNotifParams(notifParams)
                    self.isMoteActive[mac] = False
                
            elif isinstance(self.apiDef,HartMgrDefinition.HartMgrDefinition):
                
                if notifName in ['MoteLive']:
                    mac = self._getMacFromNotifParams(notifParams)
                    self.isMoteActive[mac] = True
                
                if notifName in ['MoteUnknown','MoteDisconnect','MoteJoin']:
                    mac = self._getMacFromNotifParams(notifParams)
                    self.isMoteActive[mac] = False
                
            else:
                output = "apiDef of type {0} unexpected".format(type(self.apiDef))
                log.critical(output)
                print output
                raise SystemError(output)
        
        except Exception as err:
            output = traceback.format_exc()
            print output
            log.critical(output)
        
        finally:
            
            # unlock the data structure
            self.dataLock.release()
    
    def _getMacFromNotifParams(self,notifParams):
        
        if   isinstance(self.apiDef,IpMgrDefinition.IpMgrDefinition):
            # we are connected to an IP manager
            
            return tuple(notifParams.macAddress)
        elif isinstance(self.apiDef,HartMgrDefinition.HartMgrDefinition):
            # we are connected to a HART manager
            
            return tuple([int(i,16) for i in notifParams['macAddr'].split('-')])
        else:
            output = "apiDef of type {0} unexpected".format(type(self.apiDef))
            log.critical(output)
            print output
            raise SystemError(output)
    
    def _handle_oap_notif(self,mac,notif):
        
        # convert MAC to tuple
        mac = tuple(mac)
        
        if isinstance(notif,OAPNotif.OAPTempSample):
            # this is a temperature notification
            
            # lock the data structure
            self.dataLock.acquire()
            
            # add mac/type to updates, if necessary
            if mac not in self.data:
                self.data[mac] = {}
            if COL_TEMPERATURE not in self.data[mac]:
                self.data[mac][COL_TEMPERATURE] = None
            if COL_TEMP_NUM not in self.data[mac]:
                self.data[mac][COL_TEMP_NUM]   = 0
            
            # add mac/type to updates, if necessary
            if mac not in self.updates:
                self.updates[mac] = []
            if COL_TEMPERATURE not in self.updates[mac]:
                self.updates[mac].append(COL_TEMPERATURE)
            if COL_TEMP_NUM not in self.updates[mac]:
                self.updates[mac].append(COL_TEMP_NUM)
            
            self.data[mac][COL_TEMPERATURE]  = notif.samples[0]
            self.data[mac][COL_TEMP_NUM]   += 1
            
            # unlock the data structure
            self.dataLock.release()

class TempMonitorGui(object):
    
    def __init__(self):
        
        # local variables
        self.guiLock            = threading.Lock()
        self.apiDef             = IpMgrDefinition.IpMgrDefinition()
        self.notifClientHandler = None
        self.latencyCalculator  = None
        self.guiUpdaters        = 0
        self.oap_clients        = {}
        
        # create window
        self.window = dustWindow.dustWindow('TempMonitor',
                                 self._windowCb_close)
        
        # add a API selection frame
        self.apiFrame = dustFrameApi.dustFrameApi(
                                    self.window,
                                    self.guiLock,
                                    self._apiFrameCb_apiLoaded,
                                    row=0,column=0,
                                    deviceType=dustFrameApi.dustFrameApi.MANAGER)
        self.apiFrame.show()
        
        # add a connection frame
        self.connectionFrame = dustFrameConnection.dustFrameConnection(
                                    self.window,
                                    self.guiLock,
                                    self._connectionFrameCb_connected,
                                    frameName="manager connection",
                                    row=1,column=0)
        
        # add a mote list frame
        columnnames =       [
                                # led
                                {
                                    'name': COL_LED,
                                    'type': dustFrameMoteList.dustFrameMoteList.ACTION,
                                },
                                # counters and latency
                                {
                                    'name': COL_NOTIF_DATA,
                                    'type': dustFrameMoteList.dustFrameMoteList.LABEL,
                                },
                                {
                                    'name': COL_NOTIF_IPDATA,
                                    'type': dustFrameMoteList.dustFrameMoteList.LABEL,
                                },
                                {
                                    'name': COL_NOTIF_HR,
                                    'type': dustFrameMoteList.dustFrameMoteList.LABEL,
                                },
                                {
                                    'name': COL_LAT_MIN,
                                    'type': dustFrameMoteList.dustFrameMoteList.LABEL,
                                },
                                {
                                    'name': COL_LAT_CUR,
                                    'type': dustFrameMoteList.dustFrameMoteList.LABEL,
                                },
                                {
                                    'name': COL_LAT_MAX,
                                    'type': dustFrameMoteList.dustFrameMoteList.LABEL,
                                },
                                {
                                    'name': COL_NOTIF_CLR,
                                    'type': dustFrameMoteList.dustFrameMoteList.ACTION,
                                },
                                # temperature
                                {
                                    'name': COL_TEMPERATURE,
                                    'type': dustFrameMoteList.dustFrameMoteList.LABEL,
                                },
                                {
                                    'name': COL_TEMP_NUM,
                                    'type': dustFrameMoteList.dustFrameMoteList.LABEL,
                                },
                                {
                                    'name': COL_TEMP_CLR,
                                    'type': dustFrameMoteList.dustFrameMoteList.ACTION,
                                },
                                {
                                    'name': COL_TEMP_RATE,
                                    'type': dustFrameMoteList.dustFrameMoteList.GETSETONEVAL,
                                },
                            ]
        self.moteListFrame = dustFrameMoteList.dustFrameMoteList(self.window,
                                               self.guiLock,
                                               columnnames,
                                               row=2,column=0)
        self.moteListFrame.show()
        
        # add a status (text) frame
        self.statusFrame   = dustFrameText.dustFrameText(
                                    self.window,
                                    self.guiLock,
                                    frameName="status",
                                    row=3,column=0)
        self.statusFrame.show()
    
    #======================== public ==========================================
    
    def start(self):
        
        # log
        log.debug("Starting TempMonitorGui")
        
        # start Tkinter's main thead
        try:
            self.window.mainloop()
        except SystemExit:
            sys.exit()

    #======================== private =========================================
    
    #===== user interaction
    
    def _apiFrameCb_apiLoaded(self,apiDefLoaded):
        '''
        \brief Called when an API is selected.
        '''
        
        # log
        log.debug("_apiFrameCb_apiLoaded")
        
        # record the loaded API
        self.apiDef = apiDefLoaded
        
        # tell other frames about it
        self.connectionFrame.apiLoaded(self.apiDef)
        
        # display frames
        self.connectionFrame.show()
        
        # update status
        self.statusFrame.write("API {0} loaded successfully.".format(type(apiDefLoaded)))
    
    def _connectionFrameCb_connected(self,connector):
        '''
        \brief Called when the connectionFrame has connected.
        '''
        
        # log
        log.debug("_connectionFrameCb_connected")
        
        # store the connector
        self.connector = connector
        
        # start a latency calculator
        self.latencyCalculator = LatencyCalculator.LatencyCalculator(self.apiDef,self.connector)
        self.latencyCalculator.start()
        
        # start a notification client
        self.notifClientHandler = notifClient(
                    self.apiDef,
                    self.connector,
                    self._connectionFrameCb_disconnected,
                    self.latencyCalculator,
                )
        
        # retrieve list of motes from manager
        macs = self._getOperationalMotesMacAddresses()
        for mac in macs:
            self._addNewMote(mac)
        
        # clear the colors on the GUI
        self.moteListFrame.clearColors()
        
        # schedule the GUI to update itself in GUI_UPDATEPERIOD ms
        if self.guiUpdaters==0:
            self.moteListFrame.after(GUI_UPDATEPERIOD,self._updateMoteList)
            self.guiUpdaters += 1
        
        # update status
        self.statusFrame.write("Connection to manager successful.")
    
    def _moteListFrameCb_toggleLed(self,mac,button):
        
        if isinstance(self.apiDef,IpMgrDefinition.IpMgrDefinition):
            # find out whether to switch LED on of off
            if button.cget("text")=='ON':
                val = 1
                button.configure(text="OFF")
            else:
                val = 0
                button.configure(text="ON")
            
            # send the OAP message
            try:
                self.oap_clients[mac].send( OAPMessage.CmdType.PUT,                    # command
                                            [3,2],                                     # address
                                            data_tags=[OAPMessage.TLVByte(t=0,v=val)], # parameters
                                            cb=None,                                   # callback
                                          )
            except APIError as err:
                self.statusFrame.write("[WARNING] {0}".format(err))
            else:
                # update status
                self.statusFrame.write(
                    "Toggle LED command sent successfully to mote {0}.".format(
                        FormatUtils.formatMacString(mac),
                    )
                )
        else:
            button.configure(text="N.A.")
            # update status
            self.statusFrame.write("This feature is only present in SmartMesh IP")
    
    def _moteListFrameCb_clearCtrs(self,mac,button):
        # clear the counters
        self.notifClientHandler.clearNotifCounters(mac)
        
        # update status
        self.statusFrame.write(
                "Counters for mote {0} cleared successfully.".format(
                    FormatUtils.formatMacString(mac),
                )
            )
    
    def _moteListFrameCb_clearTemp(self,mac,button):
        # clear the temperature data
        self.notifClientHandler.clearTemp(mac)
        
        # update status
        self.statusFrame.write(
                "Temperature data for mote {0} cleared successfully.".format(
                    FormatUtils.formatMacString(mac),
                )
            )
    
    def _moteListFrameCb_rateGet(self,mac):
        
        # send the OAP message
        try:
            self.oap_clients[mac].send( OAPMessage.CmdType.GET,                    # command
                                        [5],                                       # address
                                        data_tags=None,                            # parameters
                                        cb=self._oap_rateGet_resp,                 # callback
                                      )
        except APIError as err:
            self.statusFrame.write("[WARNING] {0}".format(err))
        else:
            # update status
            self.statusFrame.write(
                "Publish rate get request sent successfully to mote {0}.".format(
                    FormatUtils.formatMacString(mac),
                )
            )
    
    def _moteListFrameCb_rateSet(self,mac,val):
    
        # send the OAP message
        try:
            self.oap_clients[mac].send( OAPMessage.CmdType.PUT,                    # command
                                        [5],                                       # address
                                        data_tags=[OAPMessage.TLVByte(t=0,v=1),
                                                   OAPMessage.TLVLong(t=1,v=val),],# parameters
                                        cb=None,                                   # callback
                                      )
        except APIError as err:
            self.statusFrame.write("[WARNING] {0}".format(err))
        else:
            # update status
            self.statusFrame.write(
                "Publish rate set({0}) request sent successfully to mote {1}.".format(
                    val,
                    FormatUtils.formatMacString(mac),
                )
            )
    
    def _connectionFrameCb_disconnected(self,notifName=None,notifParams=None):
        '''
        \brief Called when the connectionFrame has disconnected.
        '''
        
        # kill the latency calculator thread
        if self.latencyCalculator:
            self.latencyCalculator.disconnect()
            self.latencyCalculator = None
        
        # update the GUI
        self.connectionFrame.updateGuiDisconnected()
        
        # delete the connector
        self.connector = None
    
    def _windowCb_close(self):
        if self.latencyCalculator:
            self.latencyCalculator.disconnect()
        if self.notifClientHandler:
            self.notifClientHandler.disconnect()
    
    #===== helpers
    
    def _getOperationalMotesMacAddresses(self):
        returnVal = []
        
        if   isinstance(self.apiDef,IpMgrDefinition.IpMgrDefinition):
            # we are connected to an IP manager
            
            currentMac     = (0,0,0,0,0,0,0,0) # start getMoteConfig() iteration with the 0 MAC address
            continueAsking = True
            while continueAsking:
                try:
                    res = self.connector.dn_getMoteConfig(currentMac,True)
                except APIError:
                    continueAsking = False
                else:
                    if ((not res.isAP) and (res.state in [4,])):
                        returnVal.append(tuple(res.macAddress))
                    currentMac = res.macAddress
        
        elif isinstance(self.apiDef,HartMgrDefinition.HartMgrDefinition):
            # we are connected to a HART manager
            
            for m in self.connector.dn_getMotes():
                if ((not m.isAccessPoint) and (m.state in ['Operational',])):
                    returnVal.append(tuple([int(i,16) for i in m.macAddr.split('-')]))
        
        else:
            output = "apiDef of type {0} unexpected".format(type(self.apiDef))
            log.critical(output)
            print output
            raise SystemError(output)
        
        # order by increasing MAC address
        returnVal.sort()
        
        return returnVal
    
    def _addNewMote(self,mac):
    
        # add mote to GUI
        # Note: if you're reconnecting, mote already exists
        
        columnvals = {
            # led
            COL_LED:                {
                                        'text':     'ON',
                                        'callback': self._moteListFrameCb_toggleLed,
                                    },
            # counters and latency
            COL_NOTIF_DATA:            0,
            COL_NOTIF_IPDATA:          0,
            COL_NOTIF_HR:              0,
            COL_LAT_MIN:             '-',
            COL_LAT_CUR:             '-',
            COL_LAT_MAX:             '-',
            COL_NOTIF_CLR:          {
                                        'text':     'clear',
                                        'callback': self._moteListFrameCb_clearCtrs,
                                    },
            # temperature
            COL_TEMPERATURE:          '-',
            COL_TEMP_NUM:            0,
            COL_TEMP_CLR:           {
                                        'text':     'clear',
                                        'callback': self._moteListFrameCb_clearTemp,
                                    },
            COL_TEMP_RATE:          {
                                        'min':      1000,
                                        'max':      60000,
                                        'cb_get':   self._moteListFrameCb_rateGet,
                                        'cb_set':   self._moteListFrameCb_rateSet,
                                    },
        }
        
        if mac not in self.oap_clients:
            self.moteListFrame.addMote(
                    mac,
                    columnvals,
                )
        
        # create OAPClient
        # Note: if you're reconnecting, this recreates the OAP client
        self.oap_clients[mac] = OAPClient.OAPClient(mac,
                                                    self._sendDataToConnector,
                                                    self.notifClientHandler.getOapDispatcher())
    
    def _oap_rateGet_resp(self,mac,oap_resp):
        
        temp = OAPMessage.Temperature()
        temp.parse_response(oap_resp)
        
        self.moteListFrame.update(mac,COL_TEMP_RATE,       temp.rate.value)
    
    def _updateMoteList(self):
        
        updatable_columns = [
                                COL_NOTIF_DATA,
                                COL_NOTIF_IPDATA,
                                COL_NOTIF_HR,
                                COL_LAT_MIN,
                                COL_LAT_CUR,
                                COL_LAT_MAX,
                                COL_TEMPERATURE,
                                COL_TEMP_NUM,
                            ]
        
        # get the data
        (isMoteActive,data,updates) = self.notifClientHandler.getData()
        
        # update the frame
        for mac,data in data.items():
            
            # detect new motes
            if mac not in self.oap_clients:
                self._addNewMote(mac)
            
            # update
            for columnname,columnval in data.items():
                if columnname in updatable_columns:
                    if ((mac in updates) and (columnname in updates[mac])):
                        self.moteListFrame.update(mac,columnname,columnval)
        
        # enable/disable motes
        for mac in isMoteActive:
            if isMoteActive[mac]:
                self.moteListFrame.enableMote(mac)
            else:
                self.moteListFrame.disableMote(mac)
        
        # schedule the next update
        self.moteListFrame.after(GUI_UPDATEPERIOD,self._updateMoteList)
    
    def _sendDataToConnector(self,mac,priority,srcPort,dstPort,options,data):
        
        if   isinstance(self.apiDef,IpMgrDefinition.IpMgrDefinition):
            # we are connected to an IP manager
            
            self.connector.dn_sendData(
                mac,
                priority,
                srcPort,
                dstPort,
                options,
                data
            )
        elif isinstance(self.apiDef,HartMgrDefinition.HartMgrDefinition):
            # we are connected to a HART manager
            
            self.connector.dn_sendRequest(
                '-'.join(["%.2x"%b for b in mac]),    # macAddr  (string)
                'maintenance',                        # domain   (string)
                'low',                                # priority (string)
                True,                                 # reliable (string)
                [0x00,0x00,0xfc,0x12]+data,           # data     (hex)
            )
        else:
            output = "apiDef of type {0} unexpected".format(type(self.apiDef))
            log.critical(output)
            print output
            raise SystemError(output)

#============================ main ============================================

def main():
    TempMonitorGuiHandler = TempMonitorGui()
    TempMonitorGuiHandler.start()

if __name__ == '__main__':
    main()

##
# end of TempMonitor
# \}
# 
