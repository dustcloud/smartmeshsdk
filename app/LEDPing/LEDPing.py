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

from   SmartMeshSDK.utils              import AppUtils,                   \
                                              FormatUtils,                \
                                              RateCalculator
from   SmartMeshSDK.ApiDefinition      import IpMgrDefinition
from   SmartMeshSDK.IpMgrConnectorMux  import IpMgrSubscribe
from   SmartMeshSDK.protocols.oap      import OAPDispatcher,              \
                                              OAPClient,                  \
                                              OAPMessage
from   dustUI                          import dustWindow,                 \
                                              dustFrameConnection,        \
                                              dustFrameLEDPing,           \
                                              dustFrameText

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

LEDUPDATEPERIOD    = 100     # in ms
RATEUPDATEPERIOD   = 500     # in ms
OAP_PORT           = 0xf0b9

#============================ body ============================================

##
# \addtogroup LEDPing
# \{
# 

class LEDPingApp(object):
   
    def __init__(self):
        
        # local variables
        self.guiLock            = threading.Lock()
        self.apiDef             = IpMgrDefinition.IpMgrDefinition()
        self.ledOn              = False
        self.pingOngoing        = False
        self.oap_client         = None
        self.ratecalculator     = RateCalculator.RateCalculator()
        self.connector          = None
        
        # create window
        self.window = dustWindow.dustWindow(
            'LEDPing',
            self._windowCb_close
        )
                                 
        # add a connection frame
        self.connectionFrame = dustFrameConnection.dustFrameConnection(
            self.window,
            self.guiLock,
            self._connectionFrameCb_connected,
            frameName="manager connection",
            row=0,column=0
        )
        self.connectionFrame.apiLoaded(self.apiDef)
        self.connectionFrame.show()
        
        # add a LEDPing frame
        self.LEDPingFrame = dustFrameLEDPing.dustFrameLEDPing(
            self.window,
            self.guiLock,
            self._LEDPingFrameCb_startPressed,
            self._LEDPingFrameCb_stopPressed,
            frameName="LED ping",
            row=1,column=0
        )
        self.LEDPingFrame.show()
        
        # add a text frame
        self.textFrame = dustFrameText.dustFrameText(
            self.window,
            self.guiLock,
            frameName="Notes",
            row=2,column=0
        )
        self.textFrame.show()
        
        # put information in text frame
        output  = []
        output += ['The mote this application drives needs to run the']
        output += ['default firmware, and operate in master mode.']
        output += ['']
        output += ['']
        output += ['The start button is only active when the']
        output += ['application is connected to a SmartMesh IP manager.']
        output  = '\n'.join(output)
        self.textFrame.write(output)
    
    #======================== public ==========================================
    
    def start(self):
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
    
    #===== GUI refresh
    
    def _gui_refresh_led(self):
        
        # ask LED frame to update
        self.LEDPingFrame.updateLed(self.ledOn)
        
        # schedule the next update
        self.LEDPingFrame.after(LEDUPDATEPERIOD,self._gui_refresh_led)
    
    def _gui_refresh_rate(self):
        
        # ask rate calculator for rate
        try:
            self.LEDPingFrame.updateRttLabel(1.0/float(self.ratecalculator.getRate()))
        except RateCalculator.RateCalculatorError:
            self.LEDPingFrame.updateRttLabel(None)
        
        # schedule the next update
        self.LEDPingFrame.after(RATEUPDATEPERIOD,self._gui_refresh_rate)
    
    #===== GUI interaction
    
    def _connectionFrameCb_connected(self,connector):
        '''
        \brief Called when the connectionFrame has connected.
        '''
        
        # store the connector
        self.connector = connector
        
        # schedule the GUI to update
        self.LEDPingFrame.after(LEDUPDATEPERIOD,self._gui_refresh_led)
        self.LEDPingFrame.after(RATEUPDATEPERIOD,self._gui_refresh_rate)
        
        # have LEDPingFrame enable button
        self.LEDPingFrame.enableButton()
        
        # OAP dispatcher
        self.oap_dispatch = OAPDispatcher.OAPDispatcher()
        
        # create a subscriber
        self.subscriber           = IpMgrSubscribe.IpMgrSubscribe(self.connector)
        self.subscriber.start()
        self.subscriber.subscribe(
            notifTypes =    [
                               IpMgrSubscribe.IpMgrSubscribe.NOTIFDATA,
                            ],
            fun =           self.oap_dispatch.dispatch_pkt,
            isRlbl =        False,
        )
        self.subscriber.subscribe(
            notifTypes =    [
                                IpMgrSubscribe.IpMgrSubscribe.ERROR,
                                IpMgrSubscribe.IpMgrSubscribe.FINISH,
                            ],
            fun =           self._notifClientCb_disconnected,
            isRlbl =        True,
        )
    
    def _LEDPingFrameCb_startPressed(self,mac):
        
        # remember that the app is started
        self.pingOngoing = True
        
        # disable further editing of MAC address
        self.LEDPingFrame.disableMacText()
        
        # create OAPClient
        if not self.oap_client:
            self.oap_client = OAPClient.OAPClient(
                mac,
                self.connector.dn_sendData,
                self.oap_dispatch
            )
        
        # initiate first LED toggle
        self._toggleLed()
    
    def _LEDPingFrameCb_stopPressed(self):
        
        # remember that the app is stopped
        self.pingOngoing = False
        
        # stop measuring rate
        self.ratecalculator.clearBuf()
    
    def _windowCb_close(self):
        '''
        \brief Called when the window is closed.
        '''
        
        if self.connector:
            self.connector.disconnect()
    
    #===== notifications
    
    def _oap_response(self,mac,oap_resp):
        
        # initiate next LED toggle
        if self.pingOngoing:
            self._toggleLed()
    
    def _notifClientCb_disconnected(self,notifName,notifParams):
        '''
        \brief Called when the connectionFrame has disconnected.
        '''
        
        # update the GUI
        self.connectionFrame.updateGuiDisconnected()
        self.LEDPingFrame.disableButton()
        
        # delete the connector
        if self.connector:
            self.connector.disconnect()
        self.connector = None
        
        # the app is stopped
        self.pingOngoing = False
    
    #===== helpers
    
    def _toggleLed(self):
        
        # indicate event
        self.ratecalculator.signalEvent()
        
        # pick the command to send
        if self.ledOn:
            ledVal = 0x00                                  # turn LED off
        else:
            ledVal = 0x01                                  # turn LED on
        
        # send packet
        self.oap_client.send(
            OAPMessage.CmdType.PUT,                        # command
            [3,2],                                         # address (digital_out=3,Actuate LED (2))
            data_tags=[OAPMessage.TLVByte(t=0,v=ledVal)],  # parameters
            cb=self._oap_response                          # callback
        )
        
        # update my local view of the LED
        self.ledOn = not self.ledOn

#============================ main ============================================

def main():
    app = LEDPingApp()
    app.start()

if __name__ == '__main__':
    main()

##
# end of LEDPing
# \}
# 
