#!/usr/bin/python

# add the SmartMeshSDK/ folder to the path
import sys
import os

temp_path = sys.path[0]
if temp_path:
    sys.path.insert(0, os.path.join(temp_path, '..', '..', 'dustUI'))
    sys.path.insert(0, os.path.join(temp_path, '..', '..', 'SmartMeshSDK'))

import random

# verify installation
import SmsdkInstallVerifier
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

import Tkinter
import threading

from dustWindow           import dustWindow
from dustFrameConnection  import dustFrameConnection
from dustFrameLEDPing     import dustFrameLEDPing
from dustFrameText        import dustFrameText

from ApiDefinition        import IpMgrDefinition
from ApiException         import APIError

from IpMgrConnectorMux    import IpMgrConnectorMux
from IpMgrConnectorMux    import IpMgrSubscribe

from optparse import OptionParser

UPDATEPERIOD = 100 # in ms
OAP_PORT     = 0xf0b9

class notifClient(object):
    '''
    \ingroup MgrListener
    '''
    
    def __init__(self, connector, notifDataCallback, disconnectedCallback):
        
        # store params
        self.connector            = connector
        self.notifDataCallback    = notifDataCallback
        self.disconnectedCallback = disconnectedCallback
        
        # variables
        self.data      = None
        self.dataLock  = threading.Lock()
        
        # subscriber
        self.subscriber = IpMgrSubscribe.IpMgrSubscribe(self.connector)
        self.subscriber.start()
        self.subscriber.subscribe(
            notifTypes =    [
                               IpMgrSubscribe.IpMgrSubscribe.NOTIFDATA,
                            ],
            fun =           self.notifDataCallback,
            isRlbl =        False,
        )
        self.subscriber.subscribe(
            notifTypes =    [
                                IpMgrSubscribe.IpMgrSubscribe.ERROR,
                                IpMgrSubscribe.IpMgrSubscribe.FINISH,
                            ],
            fun =           self.disconnectedCallback,
            isRlbl =        True,
        )
    
    #======================== public ==========================================
    
    def disconnect(self):
        self.connector.disconnect()
    
    #======================== private =========================================

class LEDPingGui(object):
   
    def __init__(self):
        
        # local variables
        self.guiLock            = threading.Lock()
        self.apiDef             = IpMgrDefinition.IpMgrDefinition()
        self.ledOn              = False
        self.handshakeDone      = False
        self.mac                = None
        self.notifClientHandler = None
        self.ledPingStarted     = False
        
        # create window
        self.window = dustWindow('LEDPing',
                                 self._windowCb_close)
                                 
        # add a connection frame
        self.connectionFrame = dustFrameConnection(
                                    self.window,
                                    self.guiLock,
                                    self._connectionFrameCb_connected,
                                    frameName="manager connection",
                                    row=0,column=0)
        self.connectionFrame.apiLoaded(self.apiDef)
        self.connectionFrame.show()
        
        # add a LEDPing frame
        self.LEDPingFrame = dustFrameLEDPing(self.window,
                                         self.guiLock,
                                         self._LEDPingFrameCb_startPressed,
                                         self._LEDPingFrameCb_stopPressed,
                                         frameName="LED ping",
                                         row=1,column=0)
        self.LEDPingFrame.show()
        
        # add a text frame
        self.textFrame = dustFrameText(self.window,
                                         self.guiLock,
                                         frameName="Notes",
                                         row=2,column=0)
        self.textFrame.show()
        self.textFrame.write("The mote this application drives needs to run the\ndefault firmware, and operate in master mode.\n\nThe start button is only active when the\napplication is connected to a SmartMesh IP manager.")
    
    #======================== public ==========================================
    
    def start(self):
        
        # start Tkinter's main thread
        try:
            self.window.mainloop()
        except SystemExit:
            sys.exit()

    #======================== private =========================================
    
    def _windowCb_close(self):
        if self.notifClientHandler:
            self.notifClientHandler.disconnect()
    
    def _connectionFrameCb_connected(self,connector):
        '''
        \brief Called when the connectionFrame has connected.
        '''
        
        # store the connector
        self.connector = connector
        
        # schedule the GUI to update itself in UPDATEPERIOD ms
        self.LEDPingFrame.after(UPDATEPERIOD,self._updateLedState)
        
        # have LEDPingFrame enable button
        self.LEDPingFrame.enableButton()
        
        # start a notification client
        self.notifClientHandler = notifClient(
                    self.connector,
                    self._notifClientCb_notifdata,
                    self._notifClientCb_disconnected
                )
    
    def _LEDPingFrameCb_startPressed(self,mac):
    
        # store params
        self.mac = mac
        
        # remember that the app is started
        self.ledPingStarted = True
        
        # initiate first LED toggle
        self._toggleLed()
    
    def _LEDPingFrameCb_stopPressed(self):
    
        # remember that the app is stopped
        self.ledPingStarted = False
    
    def _toggleLed(self):
        
        payload = []
        
        #=== header
        
        # control byte
        if self.handshakeDone:
            payload.append(1)                              # ACK'ed transport
            self.seqnum  +=1
        else:
            payload.append(5)                              # ACK'ed transport, resync connection
            self.seqnum   = random.randint(0x0,0xf)
            self.session  = 0
        # id byte
        payload.append(self.seqnum+(self.session<<4))
        
        #=== payload
        
        payload.append(0x02)                               # "PUT" command
        payload.append(0xff)                               # ==TLV== address (0xff)
        payload.append(0x02)                               #         length (2)
        payload.append(0x03)                               #         digital_out (3)
        payload.append(0x02)                               #         Actuate LED (2)
        payload.append(0x00)                               # ==TLV== Value (0x00)
        payload.append(0x01)                               #         length (1)
        if self.ledOn:
            payload.append(0x00)                           # set pin to 0
        else:
            payload.append(0x01)                           # set pin to 1
        
        try:
            self.connector.dn_sendData(
                macAddress   = self.mac,
                priority     = 1,
                srcPort      = OAP_PORT,
                dstPort      = OAP_PORT,
                options      = 0,
                data         = payload,
            )
        
        except APIError as err:
            # print error on GUI
            self.textFrame.write(str(err))
        
        else:
            # update my local view of the LED
            self.ledOn = not self.ledOn
        
    def _notifClientCb_notifdata(self,notifName,notifParams):
        '''
        \brief This function is called when we receive a notification from the
               manager.
        
        This notification will be an OAP-level ACK for the "setLED" command if
        if has the following characteristics:
         - notification type: data
         - macAddress: MAC address of the mote we specified
         - srcPort: 0xf0b9 (OAP)
         - dstPort: 0xf0b9 (OAP)
         - data (8 bytes):
            - 0x07: OAP control byte (ACK'ed transport, response, sync)
            - 0x--: OAP id
            - 0x02: "PUT" command
            - 0x00: RC=0 (success)
            - 0xff: ==TLV== address (0xff)
            - 0x02:         length (2)
            - 0x03:         digital_out (3)
            - 0x02:         Actuate LED (2)
        
        '''
        
        mac = [b for b in notifParams.macAddress]
        
        if (self.mac!=None                                                and
            notifName==IpMgrSubscribe.IpMgrSubscribe.NOTIFDATA            and
            mac==self.mac                                                 and
            notifParams.srcPort==OAP_PORT                                 and 
            notifParams.dstPort==OAP_PORT                                 and
            len(notifParams.data)==8                                      and
            tuple(notifParams.data[-6:])==(0x02,0x00,0xff,0x02,0x03,0x02) and
            self.ledPingStarted
            ):
            
            # initiate next LED toggle
            self._toggleLed()
    
    def _notifClientCb_disconnected(self,notifName,notifParams):
        '''
        \brief Called when the connectionFrame has disconnected.
        '''
        
        # update the GUI
        self.connectionFrame.updateGuiDisconnected()
        self.LEDPingFrame.disableButton()
        
        # delete the connector
        self.connector = None
        
        # the app is stopped
        self.ledPingStarted = False
    
    def _updateLedState(self):
        
        # ask LED frame to update
        self.LEDPingFrame.updateLed(self.ledOn)
        
        # schedule the next update
        self.LEDPingFrame.after(UPDATEPERIOD,self._updateLedState)
    
def main():
    LEDPingGuiHandler = LEDPingGui()
    LEDPingGuiHandler.start()

if __name__ == '__main__':
    main()
