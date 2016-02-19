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
                                              RateCalculator

from   SmartMeshSDK.ApiDefinition      import IpMgrDefinition,            \
                                              HartMgrDefinition
from   SmartMeshSDK.ApiException       import APIError
from   SmartMeshSDK.IpMgrConnectorMux  import IpMgrSubscribe,             \
                                              IpMgrConnectorMux
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

GUI_UPDATEPERIOD        = 250   # in ms
DEPTH_RATE_CALCULATOR   = 30

# columns names
COL_PKGEN_NUM           = 'num. pkgen'
COL_PKGEN_PPS           = 'pk./sec'
COL_PKGEN_CLR           = 'clear pkgen'
COL_PKGEN_RATE          = 'pkgen (num/rate/size)'

#============================ body ============================================

##
# \addtogroup PkGen
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
    
    def __init__(self, apiDef, connector, disconnectedCallback):
        
        # store params
        self.apiDef               = apiDef
        self.connector            = connector
        self.disconnectedCallback = disconnectedCallback
        
        # log
        log.debug("Initialize notifClient")
        
        # variables
        self.dataLock             = threading.Lock()
        self.isMoteActive         = {}
        self.data                 = {}
        self.updates              = {}
        self.rateCalc             = {}
        
        # OAP dispatcher
        self.oap_dispatch = OAPDispatcher.OAPDispatcher()
        self.oap_dispatch.register_notif_handler(self._handle_oap_notif)
        
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
    
    #======================== public ==========================================
    
    def getData(self):
        self.dataLock.acquire()
        for mac in self.data:
            if mac in self.rateCalc:
                try:
                    self.data[mac][COL_PKGEN_PPS] = self.rateCalc[mac].getRate()
                except RateCalculator.RateCalculatorError:
                    pass
                else:
                    if mac not in self.updates:
                        self.updates[mac] = []
                    self.updates[mac].append(COL_PKGEN_PPS)
        returnIsMoteActive   = copy.deepcopy(self.isMoteActive)
        returnData           = copy.deepcopy(self.data)
        returnUpdates        = copy.deepcopy(self.updates)
        self.updates         = {}
        self.dataLock.release()
        return (returnIsMoteActive,returnData,returnUpdates)
    
    def getOapDispatcher(self):
        return self.oap_dispatch
    
    def clearPkGenCounters(self,mac):
        self.dataLock.acquire()
        self.updates = {}
        if mac in self.rateCalc:
            self.rateCalc[mac].clearBuf()
        if mac in self.data:
            self.updates[mac] = []
            for k,v in self.data[mac].items():
                if   k in [COL_PKGEN_NUM,]:
                    self.updates[mac].append(k)
                    self.data[mac][k] = 0
                elif k in [COL_PKGEN_PPS,]:
                    self.updates[mac].append(k)
                    self.data[mac][k] = '-'
        self.dataLock.release()
        
    def disconnect(self):
        # log
        log.debug("notifClient.disconnect called")
        
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
        
        # unlock the data structure
        self.dataLock.release()
        
        # transform HART OAP notification into equivalent IP version
        if isinstance(self.apiDef,HartMgrDefinition.HartMgrDefinition):
            # we are connected to a HART manager
            
            if (notifName in ['data']) and (len(notifParams['payload'])>2):
                notifName = IpMgrSubscribe.IpMgrSubscribe.NOTIFDATA
                
                notifParams  = IpMgrConnectorMux.IpMgrConnectorMux.Tuple_notifData(
                    utcSecs       = int(notifParams['time']/1000),
                    utcUsecs      = (notifParams['time']%1000)*1000,
                    macAddress    = mac,
                    srcPort       = OAPMessage.OAP_PORT,
                    dstPort       = OAPMessage.OAP_PORT,
                    data          = tuple(notifParams['payload'][2:]),
                )
        
        # parse OAP packet
        if notifName in [IpMgrSubscribe.IpMgrSubscribe.NOTIFDATA]:
            try:
                self.oap_dispatch.dispatch_pkt(notifName, notifParams)
            except Exception as ex:
                traceback.print_exc()
    
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
        
        # log
        log.debug("notifClient._handle_oap_notif {0} {1}".format(mac,notif))
        
        if   isinstance(notif,OAPNotif.OAPpkGenPacket):
            # this is a PkGen notification
            
            # lock the data structure
            self.dataLock.acquire()
            
            if mac not in self.rateCalc:
                self.rateCalc[mac] = RateCalculator.RateCalculator(tsBufSize=DEPTH_RATE_CALCULATOR)
            self.rateCalc[mac].signalEvent()
            
            # add mac/type to updates, if necessary
            if mac not in self.data:
                self.data[mac] = {}
            if COL_PKGEN_NUM not in self.data[mac]:
                self.data[mac][COL_PKGEN_NUM]   = 0
            
            # add mac/type to updates, if necessary
            if mac not in self.updates:
                self.updates[mac] = []
            if COL_PKGEN_NUM not in self.updates[mac]:
                self.updates[mac].append(COL_PKGEN_NUM)
            
            self.data[mac][COL_PKGEN_NUM]   += 1
            
            # unlock the data structure
            self.dataLock.release()

class PkGenGui(object):
   
    def __init__(self):
        
        # log
        log.debug("Creating PkGenGui")
        
        # local variables
        self.guiLock            = threading.Lock()
        self.apiDef             = IpMgrDefinition.IpMgrDefinition()
        self.notifClientHandler = None
        self.guiUpdaters        = 0
        self.oap_clients        = {}
        
        # create window
        self.window = dustWindow.dustWindow('PkGen',
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
                                    row=1,column=0
                                )
        
        # add a mote list frame
        columnnames =       [
                                # PkGen
                                {
                                    'name': COL_PKGEN_NUM,
                                    'type': dustFrameMoteList.dustFrameMoteList.LABEL,
                                },
                                {
                                    'name': COL_PKGEN_PPS,
                                    'type': dustFrameMoteList.dustFrameMoteList.LABEL,
                                },
                                {
                                    'name': COL_PKGEN_CLR,
                                    'type': dustFrameMoteList.dustFrameMoteList.ACTION,
                                },
                                {
                                    'name': COL_PKGEN_RATE,
                                    'type': dustFrameMoteList.dustFrameMoteList.SETTHREEVAL,
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
        log.debug("Starting PkGenGui")
        
        '''
        This command instructs the GUI to start executing and reacting to 
        user interactions. It never returns and should therefore be the last
        command called.
        '''
        try:
            self.window.mainloop()
        except SystemExit:
            sys.exit()

    #======================== private =========================================
    
    #==== user interactions
    
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
        
        # start a notification client
        self.notifClientHandler = notifClient(
                    self.apiDef,
                    self.connector,
                    self._connectionFrameCb_disconnected,
                )
        
        # retrieve list of motes from manager
        macs = self._getOperationalMotesMacAddresses()
        for mac in macs:
            self._addNewMote(mac)
        
        # schedule the GUI to update itself in GUI_UPDATEPERIOD ms
        if self.guiUpdaters==0:
            self.moteListFrame.after(GUI_UPDATEPERIOD,self._updateMoteList)
            self.guiUpdaters += 1
        
        # update status
        self.statusFrame.write("Connection to manager successful.")
    
    def _moteListFrameCb_clearPkGen(self,mac,button):
        
        # log
        log.debug("_moteListFrameCb_clearPkGen")
        
        # clear the PkGen counters
        self.notifClientHandler.clearPkGenCounters(mac)
        
        # update status
        self.statusFrame.write(
                "pkGen counters for mote {0} cleared successfully.".format(
                    FormatUtils.formatMacString(mac),
                )
            )
    
    def _moteListFrameCb_PkGenSet(self,mac,(val1,val2,val3)):
        
        # log
        log.debug("_moteListFrameCb_PkGenSet")
        
        # send the OAP message
        try:
            self.oap_clients[mac].send( OAPMessage.CmdType.PUT,                     # command
                                        [254],                                      # address
                                        data_tags=[OAPMessage.TLVLong(t=0,v=1),
                                                   OAPMessage.TLVLong(t=1,v=val1),
                                                   OAPMessage.TLVLong(t=2,v=val2),
                                                   OAPMessage.TLVByte(t=3,v=val3),],# parameters
                                        cb=None,                                    # callback
                                      )
        except APIError as err:
            print "[WARNING] {0}".format(err)
        else:
            # update status
            self.statusFrame.write(
                "PkGen request ({0} packets, to be sent each {1}ms, with a {2} byte payload) sent successfully to mote {3}.".format(
                    val1,val2,val3,
                    FormatUtils.formatMacString(mac),
                )
            )
    
    def _connectionFrameCb_disconnected(self,notifName=None,notifParams=None):
        '''
        \brief Called when the connectionFrame has disconnected.
        '''
        
        # log
        log.debug("_connectionFrameCb_disconnected({0},{1})".format(notifName,notifParams))
        
        # update the GUI
        self.connectionFrame.updateGuiDisconnected()
        
        # delete the connector
        if self.connector:
            self.connector.disconnect()
        self.connector = None
    
    def _windowCb_close(self):
        
        # log
        log.debug("_windowCb_close")
    
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
        
        return returnVal
    
    def _addNewMote(self,mac):
    
        # add mote to GUI
        # Note: if you're reconnecting, mote already exists
        
        columnvals = {
            COL_PKGEN_NUM:  0,
            COL_PKGEN_PPS:  '-',
            COL_PKGEN_CLR:  {
                                'text':     'clear',
                                'callback': self._moteListFrameCb_clearPkGen,
                            },
            COL_PKGEN_RATE: {
                                'min2':     100,
                                'max2':     60000,
                                'min3':     0,
                                'max3':     60,
                                'cb_set':   self._moteListFrameCb_PkGenSet,
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
    
    def _updateMoteList(self):
        
        updatable_columns = [
                                  COL_PKGEN_NUM,
                                  COL_PKGEN_PPS,
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
    PkGenGuiHandler = PkGenGui()
    PkGenGuiHandler.start()

if __name__ == '__main__':
    main()

##
# end of PkGen
# \}
# 
