#!/usr/bin/python

#============================ adjust path =====================================

import sys
import os
if __name__ == "__main__":
    here = sys.path[0]
    sys.path.insert(0, os.path.join(here, '..', '..'))

#============================ verify installation =============================

from SmartMeshSDK import SmsdkInstallVerifier
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

# add the SmartMeshSDK folder to the path
import time
import struct
from   operator import eq
import Tkinter
import threading
import tkMessageBox
import copy

from   SmartMeshSDK                              import AppUtils,                        \
                                                        FormatUtils
from   SmartMeshSDK.ApiDefinition                import IpMgrDefinition
from   SmartMeshSDK.ApiException                 import APIError
from   SmartMeshSDK.protocols.DC2126AConverters  import DC2126AConverters
from   dustUI                                    import dustWindow,                      \
                                                        dustFrameConnection,             \
                                                        dustFrameText,                   \
                                                        dustFrameDC2126AConfiguration,   \
                                                        dustFrameDC2126AReport
from   SmartMeshSDK.IpMgrConnectorMux            import IpMgrConnectorMux,               \
                                                        IpMgrSubscribe

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

#===== udp port

WKP_DC2126A             = 60102

#===== command IDs

CMDID_BASE              =  0x2484

# host->mote
CMDID_GET_CONFIG        = CMDID_BASE   # GET current configuration
CMDID_SET_CONFIG        = CMDID_BASE+1 # SET configuration

# mote->host
CMDID_CONFIGURATION     = CMDID_BASE   # current configuration
CMDID_REPORT            = CMDID_BASE+1 # report

#===== error codes

ERR_BASE                = 0x0BAD
ERR_NO_SERVICE          = ERR_BASE
ERR_NOT_ENOUGH_BW       = ERR_BASE+1

#============================ body ============================================

##
# \addtogroup DC2126A
# \{
# 

class dc2126aData(object):
    '''
    \brief A singleton that holds the data for this application.
    '''
    
    #======================== singleton pattern ===============================
    
    _instance = None
    _init     = False
    
    def __new__(cls, *args, **kwargs):
        if not cls._instance:
            cls._instance = super(dc2126aData, cls).__new__(cls, *args, **kwargs)
        return cls._instance
    
    def __init__(self):
        
        # don't re-initialize an instance (needed because singleton)
        if self._init:
            return
        self._init = True
        
        # variables
        self.dataLock   = threading.RLock()
        self.data       = {}
    
    #======================== public ==========================================
    
    def set(self,k,v):
        with self.dataLock:
            self.data[k] = v
    
    def get(self,k):
        with self.dataLock:
            return copy.deepcopy(self.data[k])

class dc2126a(object):
    
    def __init__(
            self,
            connector,
            disconnectedCB, 
            displayConfigurationCB,
            displayErrorCB
        ):
        
        # store params
        self.connector                 = connector
        self.disconnectedCB            = disconnectedCB
        self.displayConfigurationCB    = displayConfigurationCB
        self.displayErrorCB            = displayErrorCB
        
        # local variables
        self.converters = DC2126AConverters.DC2126AConverters()
        
        # subscriber
        self.subscriber = IpMgrSubscribe.IpMgrSubscribe(self.connector)
        self.subscriber.start()
        self.subscriber.subscribe(
            notifTypes  =    [
                IpMgrSubscribe.IpMgrSubscribe.NOTIFDATA,
            ],
            fun =            self._notifDataCallback,
            isRlbl =         False,
        )
        self.subscriber.subscribe(
            notifTypes =     [
                IpMgrSubscribe.IpMgrSubscribe.ERROR,
                IpMgrSubscribe.IpMgrSubscribe.FINISH,
            ],
            fun =            self.disconnectedCB,
            isRlbl =         True,
        )
    
    #======================== public ==========================================
    
    def refreshMotes(self):
        '''
        \brief Get the MAC addresses of all operational motes in the network.
        '''
        motes = []
        
        # start getMoteConfig() iteration with the 0 MAC address
        currentMac      = (0,0,0,0,0,0,0,0) 
        continueAsking  = True
        while continueAsking:
            try:
                res = self.connector.dn_getMoteConfig(currentMac,True)
            except APIError:
                continueAsking = False
            else:
                if ((not res.isAP) and (res.state in [4,])):
                    motes.append(tuple(res.macAddress))
                currentMac = res.macAddress
        
        # order by increasing MAC address
        motes.sort()
        
        # store in data singleton
        dc2126aData().set('motes',motes)
    
    def getConfiguration(self):
        
        # format payload
        payload         = struct.pack(
           '>H',
           CMDID_GET_CONFIG,
        )
        
        # send
        self._sendPayload(payload)
    
    def setConfiguration(self,reportPeriod,bridgeSettlingTime,ldoOnTime):
        
        # format payload
        payload         = struct.pack(
           '>HIII',
           CMDID_SET_CONFIG,
           reportPeriod,
           bridgeSettlingTime,
           ldoOnTime,
        )
        
        # send
        self._sendPayload(payload)
    
    def disconnect(self):
        self.connector.disconnect()
    
    #======================== private =========================================
    
    #===== sending
    
    def _sendPayload(self,payload):
        
        if type(payload)==str:
            payload          = [ord(b) for b in payload]
        
        try:
            self.connector.dn_sendData(
                macAddress   = dc2126aData().get('selectedMote'),
                priority     = 2,
                srcPort      = WKP_DC2126A,
                dstPort      = WKP_DC2126A,
                options      = 0,
                data         = payload,
            )
        except Exception as err:
            log.error(err)
    
    #===== parsing
    
    def _notifDataCallback(self,notifName,notifParams):
        
        # only accept data from mote selected in the optionbox
        selectedMote = dc2126aData().get('selectedMote')
        
        if not selectedMote:
            return

        if tuple(notifParams.macAddress) != tuple(selectedMote):
            return
        
        if notifParams.dstPort!=WKP_DC2126A:
            return
        
        # parse data
        try:
            parsedData = self._parseData(notifParams.data)
        except ValueError as err:
            output  = "Could not parse received data {0}".format(
                FormatUtils.formatBuffer(notifParams.data)
            )
            print output
            log.error(output)
            return
        
        # log
        output  = []
        output += ["Received data:"]
        for (k,v) in parsedData.items():
            output += ["- {0:<15}: 0x{1:x} ({1})".format(k,v)]
        output  = '\n'.join(output)
        log.debug(output)
        
        # handle data
        if   parsedData['cmdId']==CMDID_REPORT:
            
            # record temperature
            temperature = self.converters.convertTemperature(parsedData['temperature'])
            dc2126aData().set('temperature',temperature)
            
            # record adcValue
            adcValue = self.converters.convertAdcValue(parsedData['adcValue'])
            dc2126aData().set('adcValue',adcValue)
            
            # record energysource
            energysource = self.converters.convertEnergySource(notifParams.macAddress,adcValue)
            dc2126aData().set('energysource',energysource)
        
        elif parsedData['cmdId']==CMDID_CONFIGURATION:
            
            # show new CFG values 
            self.displayConfigurationCB(parsedData)
            
        elif parsedData['cmdId']==ERR_NO_SERVICE:
            
            # display error
            self.displayErrorCB('Cannot change configuration, no service information.')
        
        elif parsedData['cmdId']==ERR_NOT_ENOUGH_BW:
            
            # display error
            self.displayErrorCB("Not enough bandwidth (current setting: {}ms)".format(parsedData['bw']))
        
        else:
            
            # display error
            self.displayErrorCB("received unexpected cmdId {0}".format(parsedData['cmdId']))
    
    def _parseData(self,byteArray):
        
        returnVal = {}
        
        # log
        log.debug("_parseData with byteArray {0}".format(FormatUtils.formatBuffer(byteArray)))
        
        # command ID
        try:
            (returnVal['cmdId'],) = struct.unpack('>H', self._toString(byteArray[:2]))
        except struct.error as err:
            raise ValueError(err)
        
        if   returnVal['cmdId']==CMDID_CONFIGURATION:
            
            try:
                (
                    returnVal['reportPeriod'],
                    returnVal['bridgeSettlingTime'],
                    returnVal['ldoOnTime'],
                ) = struct.unpack('>III', self._toString(byteArray[2:]))
            except struct.error as err:
                raise ValueError(err)
        
        elif returnVal['cmdId']==CMDID_REPORT:
            
            try:
                (
                    returnVal['temperature'],
                    returnVal['adcValue'],
                ) = struct.unpack('>IH', self._toString(byteArray[2:]))
            except struct.error as err:
                raise ValueError(err)
        
        elif returnVal['cmdId']==ERR_NO_SERVICE:
            pass
        
        elif returnVal['cmdId']==ERR_NOT_ENOUGH_BW:
            try:
                (
                    returnVal['bw'],
                ) = struct.unpack('>I', self._toString(byteArray[2:]))
            except struct.error as err:
                raise ValueError(err)
        
        else:
            raise ValueError("unexpected command ID {0}".format(returnVal['cmdId']))
        
        return returnVal
    
    #===== formatting
    
    def _toString(self,byteArray):
        return ''.join([chr(b) for b in byteArray])
    
class dc2126aGui(object):
    
    def __init__(self):
        
        # local variables
        self.guiLock              = threading.Lock()
        self.apiDef               = IpMgrDefinition.IpMgrDefinition()
        self.dc2126aHandler   = None
        
        # initialize data singleton
        dc2126aData().set('selectedMote',   None)
        dc2126aData().set('temperature',    None)
        dc2126aData().set('adcValue',       None)
        dc2126aData().set('energysource',   None)
        
        # create window
        self.window               = dustWindow.dustWindow(
            'DC2126A',
            self._windowCb_close,
        )
        
        # add connection Frame
        self.connectionFrame      = dustFrameConnection.dustFrameConnection(
            self.window,
            self.guiLock,
            self._connectionFrameCb_connected,
            frameName="Serial connection",
            row=0,column=0,
        )
        self.connectionFrame.apiLoaded(self.apiDef)
        self.connectionFrame.serialPortText.delete("1.0",Tkinter.END)
        self.connectionFrame.show()
        
        # add configuration frame
        self.configurationFrame   = dustFrameDC2126AConfiguration.dustFrameDC2126AConfiguration(
            self.window,
            self.guiLock,
            selectedMoteChangedCB = self._selectedMoteChangedCB,
            refreshButtonCB       = self._refreshButtonCB,
            getConfigurationCB    = self._getConfigurationCB,
            setConfigurationCB    = self._setConfigurationCB,
            row=1,column=0,
        )
        self.configurationFrame.disableButtons()
        self.configurationFrame.show()
        
        # add report Frame
        self.reportFrame = dustFrameDC2126AReport.dustFrameDC2126AReport(
            self.window,
            self.guiLock,
            getTemperatureCb      = self._getTemperature,
            getEnergySourceCb     = self._getEnergySource,
            getAdcValueCb         = self._getAdcValue,
            row=0,column=1,
        )
        self.reportFrame.show()
        
        # local variables
        self.userMsg         = ''      # error message printed to user
    
    #======================== public ==========================================
    
    def start(self):
        # start Tkinter's main thread
        try:
            self.window.bind('<<Err>>', self._sigHandlerErr)
            self.window.mainloop()
        except SystemExit:
            sys.exit()
    
    #======================== private =========================================
    
    #===== window
    
    def _windowCb_close(self):
        self.reportFrame.close()
        if self.dc2126aHandler:
            self.dc2126aHandler.disconnect()
    
    #===== connectionFrame
    
    def _connectionFrameCb_connected(self,connector):
        '''
        \brief Called when the connectionFrame has connected.
        '''
        
        # store the connector
        self.connector = connector
        
        # start a notification client
        self.dc2126aHandler = dc2126a(
            connector                  = self.connector,
            disconnectedCB             = self._connectionFrameCb_disconnected,
            displayConfigurationCB     = self._displayConfiguration,
            displayErrorCB             = self._displayError
        )
        
        # enable cfg buttons
        self.configurationFrame.enableButtons()
        
        # load operational motes
        self._refreshButtonCB()
    
    def _connectionFrameCb_disconnected(self,notifName,notifParams):
        '''
        \brief Called when the connectionFrame has disconnected.
        '''
        
        # update the GUI
        self.connectionFrame.updateGuiDisconnected()
        
        # delete the connector
        if self.connector:
            self.connector.disconnect()
        self.connector = None
        
        # disable cfg buttons
        self.configurationFrame.disableButtons()
    
    #===== configurationFrame
    
    def _selectedMoteChangedCB(self,mote):
        dc2126aData().set('selectedMote',mote)
    
    def _refreshButtonCB(self): 
        
        self.dc2126aHandler.refreshMotes()
        
        self.configurationFrame.refresh(dc2126aData().get('motes'))
    
    def _getConfigurationCB(self):
        
        # make sure mote selected
        if not dc2126aData().get('selectedMote'):
            self._displayError("No mote selected.")
            return
        
        # take action
        self.dc2126aHandler.getConfiguration()
        
        # update action
        self.configurationFrame.writeActionMsg('getting configuration...')
    
    def _setConfigurationCB(self,reportPeriod,bridgeSettlingTime,ldoOnTime):
        
        # make sure mote selected
        if not dc2126aData().get('selectedMote'):
            self._displayError("No mote selected.")
            return
        
        # take action
        self.dc2126aHandler.setConfiguration(
            reportPeriod          = reportPeriod,
            bridgeSettlingTime    = bridgeSettlingTime,
            ldoOnTime             = ldoOnTime,
        )
        
        # update action
        self.configurationFrame.writeActionMsg('setting configuration...')
    
    def _displayConfiguration(self,configuration):
        
        self.configurationFrame.displayConfiguration(
            reportPeriod          = configuration['reportPeriod'],
            bridgeSettlingTime    = configuration['bridgeSettlingTime'],
            ldoOnTime             = configuration['ldoOnTime'],
        ) 
        
        # update action
        self.configurationFrame.writeActionMsg('configuration received')
    
    #===== reportFrame
    
    def _getTemperature(self):
        returnVal = dc2126aData().get('temperature')
        dc2126aData().set('temperature',None)
        return returnVal
    
    def _getEnergySource(self):
        returnVal = dc2126aData().get('energysource')
        dc2126aData().set('energysource',None)
        return returnVal
    
    def _getAdcValue(self):
        returnVal = dc2126aData().get('adcValue')
        dc2126aData().set('adcValue',None)
        return returnVal
    
    def _displayError(self,msg):
        self.userMsg = msg
        self.window.event_generate('<<Err>>', when='tail')
    
    #===== internal signal handlers
    
    def _sigHandlerErr(self,args):
        tkMessageBox.showerror(title="Error",message=self.userMsg)

#============================ main ============================================

def main():
    dc2126aGuiHandler = dc2126aGui()
    dc2126aGuiHandler.start()

if __name__ == '__main__':
    main()

##
# end of DC2126A
# \}
# 
