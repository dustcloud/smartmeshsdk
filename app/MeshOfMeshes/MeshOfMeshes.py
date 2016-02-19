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
import traceback

from   SmartMeshSDK.utils              import AppUtils,                   \
                                              FormatUtils
from   SmartMeshSDK.ApiDefinition      import IpMgrDefinition
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

GUI_UPDATEPERIOD                  = 250   # in ms

MOM_UDP_PORT                      = 0xf0bf
MAX_PAYLOAD_LENGTH                = 79

# columns names
COL_ROLE                          = 'role'
COL_BRIDGE                        = 'bridge'
COL_TEMPERATURE                   = 'temperature'
COL_LED                           = 'toggle led'
COL_NOTIF_DATA                    = IpMgrSubscribe.IpMgrSubscribe.NOTIFDATA
COL_NOTIF_HEALTHREPORT            = IpMgrSubscribe.IpMgrSubscribe.NOTIFHEALTHREPORT

NOTIFDATA                         = IpMgrSubscribe.IpMgrSubscribe.NOTIFDATA
NOTIFEVENT                        = IpMgrSubscribe.IpMgrSubscribe.NOTIFEVENT
NOTIFHEALTHREPORT                 = IpMgrSubscribe.IpMgrSubscribe.NOTIFHEALTHREPORT

MOM_REQ_DISPATCH_SERIALREQ        = 0x00
MOM_REQ_DISPATCH_RPC              = 0x01

MOM_RPC_getOperationalMotes       = 0x00

MOM_RESP_DISPATCH_SERIALRESP      = 0x00
MOM_RESP_DISPATCH_RPC             = 0x01
MOM_RESP_DISPATCH_SERIALNOTIF     = 0x02

ROLE_UNKNOWN                      = '?'
ROLE_BRIDGE                       = 'bridge'
ROLE_DATA                         = 'data'
ROLE_ALL                          = [
    ROLE_UNKNOWN,
    ROLE_BRIDGE,
    ROLE_DATA,
]

#============================ body ============================================

##
# \addtogroup MeshOfMeshes
# \{
# 

class notifClient(object):
    
    def __init__(self, apiDef, connector, disconnectedCallback):
        
        # store params
        self.apiDef               = apiDef
        self.connector            = connector
        self.disconnectedCallback = disconnectedCallback
        
        # log
        log.debug("Initialize notifClient")
        
        # variables
        self.dataLock             = threading.RLock()
        self.isMoteActive         = {}
        self.tabledata            = {}
        self.tableupdates         = {}
        
        # subscriber
        self.subscriber           = IpMgrSubscribe.IpMgrSubscribe(self.connector)
        self.subscriber.start()
        self.subscriber.subscribe(
            notifTypes            = [
                                       NOTIFDATA,
                                    ],
            fun                   = self._notifDataCallbackTunneled,
            isRlbl                = False,
        )
        self.subscriber.subscribe(
            notifTypes            = [
                                       NOTIFEVENT,
                                    ],
            fun                   = self._notifEventCallback,
            isRlbl                = True,
        )
        self.subscriber.subscribe(
            notifTypes            = [
                                       NOTIFHEALTHREPORT,
                                    ],
            fun                   = self._notifHrCallback,
            isRlbl                = True,
        )
        self.subscriber.subscribe(
            notifTypes            = [
                                       IpMgrSubscribe.IpMgrSubscribe.ERROR,
                                       IpMgrSubscribe.IpMgrSubscribe.FINISH,
                                    ],
            fun                   = self.disconnectedCallback,
            isRlbl                = True,
        )
        
        # OAP dispatcher
        self.oap_dispatch = OAPDispatcher.OAPDispatcher()
        self.oap_dispatch.register_notif_handler(self._handle_oap_notif)
    
    #======================== public ==========================================
    
    def getData(self):
        
        with self.dataLock:
            returnIsMoteActive    = copy.deepcopy(self.isMoteActive)
            returnData            = copy.deepcopy(self.tabledata)
            returnUpdates         = copy.deepcopy(self.tableupdates)
            self.tableupdates     = {}
        
        return (returnIsMoteActive,returnData,returnUpdates)
    
    def getOapDispatcher(self):
        return self.oap_dispatch
    
    def disconnect(self):
        self.connector.disconnect()
    
    #======================== private =========================================
    
    def _notifDataCallbackTunneled(self, notifName, notifParams):
        
        assert notifName==NOTIFDATA
        
        try:
            # log
            log.debug(
                "notifClient._notifDataCallbackTunneled {0}:\n{1}".format(
                    NOTIFDATA,
                    FormatUtils.formatNamedTuple(notifParams)
                )
            )
            
            # modify notification to unwrap mesh-of-meshes tunneling protocol
            if notifParams.srcPort==MOM_UDP_PORT:
                
                bridgeMac         = tuple(notifParams.macAddress)
                
                # update role
                self._changeDeviceRole(bridgeMac,ROLE_BRIDGE)
                
                if notifParams.dstPort==MOM_UDP_PORT:
                    # tunneled response
                    
                    payload  = list(notifParams.data)
                    
                    # unwrap tunneling protocol
                    assert(len(payload)>1)
                    dispatch = payload[0]
                    payload  = payload[1:]
                    
                    if   dispatch==MOM_RESP_DISPATCH_SERIALRESP:
                        raise NotImplementedError
                    elif dispatch==MOM_RESP_DISPATCH_RPC:
                        assert(len(payload)>1)
                        procId    = payload[0]
                        payload   = payload[1:]
                        if procId==MOM_RPC_getOperationalMotes:
                            self._handle_resp_getOperationalMotes(bridgeMac,payload)
                        else:
                            raise SystemError("unexpected procId {0}".format(procId))
                    elif dispatch==MOM_RESP_DISPATCH_SERIALNOTIF:
                        # parse unwrapped Serial API Notification
                        (notifName,notifDict) = self.apiDef.deserialize(
                            self.apiDef.NOTIFICATION,
                            self.apiDef.nameToId(
                                self.apiDef.NOTIFICATION,
                                ['notification',]
                            ),
                            payload,
                        )
                        
                        # convert to tuple
                        notifTuple     = IpMgrConnectorMux.IpMgrConnectorMux.notifTupleTable[notifName[-1]](**notifDict)
                        
                        # update bridge, if possible
                        try:
                            dataMoteMac     = notifTuple.macAddress
                        except:
                            pass
                        else:
                            self._updateDataColumn(
                                mac         = dataMoteMac,
                                colname     = COL_BRIDGE,
                                colvalue    = bridgeMac,
                            )
                        
                        # dispatch
                        if   notifName[1]==NOTIFEVENT:
                            self._notifEventCallback(notifName[2],notifTuple)
                        elif notifName[1]==NOTIFHEALTHREPORT:
                            self._notifHrCallback(NOTIFHEALTHREPORT, notifTuple)
                        else:
                            SystemError("Unexpected notifName {0}".format(notifName))
                        
                    else:
                        raise SystemError("Unexpected dispatch byte {0}".format(dispatch))
                    
                else:
                    # tunneled upstream data
                    
                    dataMoteMac        = notifParams.data[:8]
                    data               = notifParams.data[8:]
                    
                    # update bridge
                    self._updateDataColumn(
                        mac            = dataMoteMac,
                        colname        = COL_BRIDGE,
                        colvalue       = bridgeMac,
                    )
                    
                    # unwrap tunneling protocol
                    notifParams = IpMgrConnectorMux.IpMgrConnectorMux.Tuple_notifData(
                        utcSecs        = notifParams.utcSecs,
                        utcUsecs       = notifParams.utcUsecs,
                        macAddress     = dataMoteMac,
                        srcPort        = notifParams.dstPort,
                        dstPort        = notifParams.dstPort,
                        data           = data,
                    )
                    
                    # dispatch unwrapped data again
                    self._notifDataCallback(notifName,notifParams)
            else:
                self._notifDataCallback(notifName,notifParams)
        
        except Exception as err:
            output  = []
            output += [type(err)]
            output += [err]
            output += [traceback.format_exc()]
            output  = '\n'.join([str(o) for o in output])
            log.error(output)
            print output
    
    def _notifDataCallback(self, notifName, notifParams):
        
        assert notifName==NOTIFDATA
        
        try:
            # log
            log.debug(
                "notifClient._notifDataCallback {0}:\n{1}".format(
                    NOTIFDATA,
                    FormatUtils.formatNamedTuple(notifParams)
                )
            )
            
            # read MAC address from notification
            mac              = tuple(notifParams.macAddress)
            
            # update role
            self._changeDeviceRole(mac,ROLE_DATA)
            
            # update counters
            self._incrementCounter(mac,COL_NOTIF_DATA)
            
            # parse packet
            if notifParams.srcPort==0xf0b9:
                self.oap_dispatch.dispatch_pkt(NOTIFDATA, notifParams)
            else:
                raise SystemError("expected srcPort {0}".format(notifParams.srcPort))
        
        except Exception as err:
            output  = []
            output += [type(err)]
            output += [err]
            output += [traceback.format_exc()]
            output  = '\n'.join([str(o) for o in output])
            log.error(output)
            print output
    
    def _notifEventCallback(self, notifName, notifParams):
        
        try:
            
            # log
            log.debug("notifClient._notifEventCallback {0} {1}".format(notifName, notifParams))
            
            # read MAC address from notification
            try:
                mac = notifParams.macAddress
            except Exception as err:
                mac = None
            else:
                try:
                    mac = tuple(mac)
                except:
                    pass
            
            with self.dataLock: 
                if notifName in [IpMgrSubscribe.IpMgrSubscribe.EVENTMOTEOPERATIONAL]:
                    assert mac
                    self.isMoteActive[mac] = True
                    
                if notifName in [IpMgrSubscribe.IpMgrSubscribe.EVENTMOTELOST]:
                    assert mac
                    self.isMoteActive[mac] = False
        
        except Exception as err:
            output  = []
            output += [type(err)]
            output += [err]
            output += [traceback.format_exc()]
            output  = '\n'.join([str(o) for o in output])
            log.error(output)
            print output
    
    def _notifHrCallback(self, notifName, notifParams):
        
        assert notifName==NOTIFHEALTHREPORT
        
        try:
            
            # log
            log.debug("notifClient._notifHrCallback {0} {1}".format(notifName, notifParams))
            
            # read MAC address from notification
            mac = tuple(notifParams.macAddress)
            
            # update counters
            self._incrementCounter(mac,COL_NOTIF_HEALTHREPORT)
            
        except Exception as err:
            output  = []
            output += [type(err)]
            output += [err]
            output += [traceback.format_exc()]
            output  = '\n'.join([str(o) for o in output])
            log.error(output)
            print output
    
    def _handle_oap_notif(self,mac,notif):
        
        # convert MAC to tuple
        mac = tuple(mac)
        
        if isinstance(notif,OAPNotif.OAPTempSample):
            # this is a temperature notification
            
            self._updateDataColumn(
                mac          = mac,
                colname      = COL_TEMPERATURE,
                colvalue     = notif.samples[0],
            )
    
    def _handle_resp_getOperationalMotes(self,bridgeMac,payload):
        
        macs            = []
        lastMAC         = []
        
        # parse header
        assert len(payload)>2
        number          = payload[0]
        index           = payload[1]
        payload         = payload[2:]
        
        # parse payload
        while payload:
            
            # parse lenMAC
            assert len(payload)>1
            lenMAC      = payload[0]
            payload     = payload[1:]
            
            # parse thisMAC (delta encoded)
            assert len(payload)>=lenMAC
            thisMAC     = payload[:lenMAC]
            payload     = payload[lenMAC:]
            
            # complement thisMAC
            thisMAC     = lastMAC[:8-len(thisMAC)]+thisMAC
            assert len(thisMAC)==8
            
            # store in discovered list
            macs       += [thisMAC]
            
            # remember lastMAC
            lastMAC     = thisMAC
        
        for mac in macs:
            self._updateDataColumn(
                mac          = mac,
                colname      = COL_BRIDGE,
                colvalue     = bridgeMac,
            )
    
    #======================== helpers =========================================
    
    def _updateDataColumn(self,mac,colname,colvalue):
        
        try:
            mac = tuple(mac)
        except:
            pass
        
        with self.dataLock:
            if mac not in self.tabledata:
                self.tabledata[mac] = {}
            if  (
                    (colname not in self.tabledata[mac])
                    or
                    (self.tabledata[mac][colname]!=colvalue)
                ):
                if mac not in self.tableupdates:
                    self.tableupdates[mac] = []
                self.tableupdates[mac].append(colname)
            self.tabledata[mac][colname] = colvalue
    
    def _incrementCounter(self,mac,counterName):
        
        try:
            mac = tuple(mac)
        except:
            pass
        
        with self.dataLock:
        
            # add mac/type to tabledata, if necessary
            if mac not in self.tabledata:
                self.tabledata[mac] = {}
            if counterName not in self.tabledata[mac]:
                self.tabledata[mac][counterName] = 0
                
            # add mac/type to tableupdates, if necessary
            if mac not in self.tableupdates:
                self.tableupdates[mac] = []
            if counterName not in self.tableupdates[mac]:
                self.tableupdates[mac].append(counterName)
            
            # increment counter
            self.tabledata[mac][counterName] += 1
    
    def _changeDeviceRole(self,mac,newRole):
        
        try:
            mac = tuple(mac)
        except:
            pass
        
        assert newRole in ROLE_ALL
        
        # get current role
        try:
            previousRole     = self.tabledata[mac][COL_ROLE]
        except:
            previousRole     = None
        
        # update role
        self._updateDataColumn(
            mac              = mac,
            colname          = COL_ROLE,
            colvalue         = newRole,
        )
        
        # kick of discovery process, if application
        if (newRole==ROLE_BRIDGE and newRole!=previousRole):
            self._startDiscovery(mac)
    
    def _startDiscovery(self,macBridge):
        
        self.connector.dn_sendData(
            macAddress  = macBridge,
            priority    = 0,
            srcPort     = MOM_UDP_PORT,
            dstPort     = MOM_UDP_PORT,
            options     = 0x00,
            data        = [
                MOM_REQ_DISPATCH_RPC,
                MOM_RPC_getOperationalMotes,
            ],
        )
    
class MeshOfMeshesGui(object):
    
    def __init__(self):
        
        # local variables
        self.guiLock            = threading.Lock()
        self.apiDef             = IpMgrDefinition.IpMgrDefinition()
        self.notifClientHandler = None
        self.guiUpdaters        = 0
        self.oap_clients        = {}
        
        # create window
        self.window = dustWindow.dustWindow(
            'MeshOfMeshes',
            self._windowCb_close
        )
        
        # add a connection frame
        self.connectionFrame = dustFrameConnection.dustFrameConnection(
            self.window,
            self.guiLock,
            self._connectionFrameCb_connected,
            frameName="manager connection",
            row=1,column=0
        )
        self.connectionFrame.apiLoaded(self.apiDef)
        self.connectionFrame.show()
        
        # add a mote list frame
        columnnames =       [
            # role
            {
                'name': COL_ROLE,
                'type': dustFrameMoteList.dustFrameMoteList.LABEL,
            },
            # bridge
            {
                'name': COL_BRIDGE,
                'type': dustFrameMoteList.dustFrameMoteList.LABEL,
            },
            # temperature
            {
                'name': COL_TEMPERATURE,
                'type': dustFrameMoteList.dustFrameMoteList.LABEL,
            },
            # led
            {
                'name': COL_LED,
                'type': dustFrameMoteList.dustFrameMoteList.ACTION,
            },
            # counters
            {
                'name': COL_NOTIF_DATA,
                'type': dustFrameMoteList.dustFrameMoteList.LABEL,
            },
            {
                'name': COL_NOTIF_HEALTHREPORT,
                'type': dustFrameMoteList.dustFrameMoteList.LABEL,
            },
        ]
        self.moteListFrame = dustFrameMoteList.dustFrameMoteList(
            self.window,
            self.guiLock,
            columnnames,
            row=2,column=0
        )
        self.moteListFrame.show()
        
        # add a status (text) frame
        self.statusFrame   = dustFrameText.dustFrameText(
            self.window,
            self.guiLock,
            frameName="status",
            row=3,column=0
        )
        self.statusFrame.show()
    
    #======================== public ==========================================
    
    def start(self):
        
        # log
        log.debug("Starting MeshOfMeshesGui")
        
        # start Tkinter's main thead
        try:
            self.window.mainloop()
        except SystemExit:
            sys.exit()

    #======================== private =========================================
    
    #===== user interaction
    
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
                self.oap_clients[mac].send(
                    OAPMessage.CmdType.PUT,                    # command
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
    
    def _connectionFrameCb_disconnected(self,notifName=None,notifParams=None):
        '''
        \brief Called when the connectionFrame has disconnected.
        '''
        
        # update the GUI
        self.connectionFrame.updateGuiDisconnected()
        
        # delete the connector
        self.connector = None
    
    def _windowCb_close(self):
        if self.notifClientHandler:
            self.notifClientHandler.disconnect()
    
    #===== helpers
    
    def _getOperationalMotesMacAddresses(self):
        returnVal = []
        
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
        
        return sorted(returnVal)
    
    def _addNewMote(self,mac):
    
        # add mote to GUI
        # Note: if you're reconnecting, mote already exists
        
        columnvals = {
            # role
            COL_ROLE:                  ROLE_UNKNOWN,
            # bridge
            COL_BRIDGE:                '-',
            # temperature
            COL_TEMPERATURE:           '-',
            # led
            COL_LED: {
                'text':     'ON',
                'callback': self._moteListFrameCb_toggleLed,
            },
            # counters
            COL_NOTIF_DATA:            0,
            COL_NOTIF_HEALTHREPORT:    0,
        }
        
        if mac not in self.oap_clients:
            self.moteListFrame.addMote(
                    mac,
                    columnvals,
                )
        
        # create OAPClient
        # Note: if you're reconnecting, this recreates the OAP client
        self.oap_clients[mac] = OAPClient.OAPClient(
            mac,
            self._sendDataToConnector,
            self.notifClientHandler.getOapDispatcher()
        )
    
    def _updateMoteList(self):
        
        updatable_columns = [
            COL_ROLE,
            COL_BRIDGE,
            COL_TEMPERATURE,
            COL_NOTIF_DATA,
            COL_NOTIF_HEALTHREPORT,
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
    
    def _sendDataToConnector(self,finalMac,priority,srcPort,dstPort,options,data):
        
        # get the data
        (_,datadb,_) = self.notifClientHandler.getData()
        
        if (finalMac in datadb) and (COL_BRIDGE in datadb[finalMac]) and (datadb[finalMac][COL_BRIDGE]):
            # tunneling protocol
            
            if len(data)+8<=MAX_PAYLOAD_LENGTH:
                self.connector.dn_sendData(
                    datadb[finalMac][COL_BRIDGE],
                    priority,
                    srcPort,
                    MOM_UDP_PORT,
                    options,
                    [b for b in finalMac]+data
                )
            else:
                log.warning("downstream data is too long ({0} bytes)".format(len(data)))
        
        else:
            # non-tunneling protocol
            
            self.connector.dn_sendData(
                finalMac,
                priority,
                srcPort,
                dstPort,
                options,
                data
            )

#============================ main ============================================

def main():
    MeshOfMeshesGuiHandler = MeshOfMeshesGui()
    MeshOfMeshesGuiHandler.start()

if __name__ == '__main__':
    main()

##
# end of MeshOfMeshes
# \}
# 
