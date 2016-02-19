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
                                              FormatUtils
from   SmartMeshSDK.ApiDefinition      import IpMgrDefinition
from   SmartMeshSDK.IpMgrConnectorMux  import IpMgrConnectorMux,          \
                                              IpMgrSubscribe
from   SmartMeshSDK.LbrConnector       import LbrConnector
from   SmartMeshSDK.ApiException       import ConnectionError,            \
                                              QueueError
from   dustUI                          import dustWindow,                 \
                                              dustFrameLBRConnection,     \
                                              dustFrameConnection

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

#============================ body ============================================

##
# \addtogroup LBRConnection
# \{
# 

class lbrsubscriber(threading.Thread):
    
    def __init__(self,lbrconnector,rxCb,disconnectedCb):
    
        # record variables
        self.lbrconnector    = lbrconnector
        self.rxCb            = rxCb
        self.disconnectedCb  = disconnectedCb
        
        # init the parent
        threading.Thread.__init__(self)
        self.name            = "lbrsubscriber"
        
    #======================== public ==========================================
    
    def run(self):
        keepListening = True
        while keepListening:
            try:
                input = self.lbrconnector.getNotificationInternal(-1)
            except (ConnectionError,QueueError) as err:
                keepListening = False
            else:
                if input:
                    self.rxCb(input)
                else:
                    keepListening = False
        self.disconnectedCb()

class LBRConnectionGui(object):
    
    def __init__(self):
        
        # local variables
        self.guiLock            = threading.Lock()
        self.apiDef             = IpMgrDefinition.IpMgrDefinition()
        self.mgrconnector       = None
        self.lbrconnector       = None
        
        # create window
        self.window = dustWindow.dustWindow('LBRConnection',
                                 self._windowCb_close)
        
        # add an LBR connection frame
        self.LBRConnectionFrame = dustFrameLBRConnection.dustFrameLBRConnection(
                                    self.window,
                                    self.guiLock,
                                    self._LBRConnectionFrameCb_connected,
                                    frameName="LBR connection",
                                    row=0,column=0)
        self.LBRConnectionFrame.show()
        
        # add a manager connection frame
        self.mgrconnectionFrame = dustFrameConnection.dustFrameConnection(
                                    self.window,
                                    self.guiLock,
                                    self._mgrconnectionFrameCb_connected,
                                    frameName="manager connection",
                                    row=1,column=0)
        self.mgrconnectionFrame.apiLoaded(self.apiDef)
        self.mgrconnectionFrame.show()
    
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
    
    def _windowCb_close(self):
        
        # disconnect the manager connector
        if self.mgrconnector:
            self.mgrconnector.disconnect()
            
        # disconnect the lbr connector
        if self.lbrconnector:
            self.lbrconnector.disconnect()
    
    def _mgrconnectionFrameCb_connected(self,mgrconnector):
        '''
        \brief Called when the application has connected to the manager.
        '''
        
        # store the connector
        self.mgrconnector = mgrconnector
        
        # add subscriber for the manager
        self.mgrsubscriber = IpMgrSubscribe.IpMgrSubscribe(self.mgrconnector)
        self.mgrsubscriber.start()
        self.mgrsubscriber.subscribe(
            notifTypes =    [
                                IpMgrSubscribe.IpMgrSubscribe.NOTIFIPDATA,
                            ],
            fun =           self._mgrRxCallback,
            isRlbl =        False,
        )
        self.mgrsubscriber.subscribe(
            notifTypes =    [
                                IpMgrSubscribe.IpMgrSubscribe.ERROR,
                                IpMgrSubscribe.IpMgrSubscribe.FINISH,
                            ],
            fun =           self._mgrconnectionFrameCb_disconnected,
            isRlbl =        True,
        )
        
    def _mgrRxCallback(self, notifName, notifParams):
        
        # make sure this is IPdata
        if notifName not in ['notifIpData']:
            raise AttributeError("Should only receive notifIpData notifications, not "+notifName)
        
        # build the string to send to the LBR
        stringToSend = ''
        
        for c in notifParams.macAddress:
            stringToSend += chr(c)
        for c in notifParams.data:
            stringToSend += chr(c)
        
        # send to the LBR
        self.lbrconnector.send(stringToSend)
    
    def _mgrconnectionFrameCb_disconnected(self, notifName, notifParams):
        
        # update the GUI
        self.mgrconnectionFrame.updateGuiDisconnected()
        
        # delete the connector
        if self.mgrconnector:
            self.mgrconnector.disconnect()
        self.mgrconnector = None
    
    def _LBRConnectionFrameCb_connected(self,lbrconnector):
        '''
        \brief Called when the application has connected to the LBR.
        '''
        
        # store the connector
        self.lbrconnector = lbrconnector
        
        # add subscriber for the lbr
        self.lbrsubscriber  = lbrsubscriber(self.lbrconnector,
                                            self._lbrRxCallback,
                                            self._lbrDisconnectedCallback)
        self.lbrsubscriber.start()
    
    def _lbrRxCallback(self, input):
        
        mac  = []
        for c in input[0]:
            mac.append(ord(c))
        data = []
        for c in input[1]:
            data.append(ord(c))
        
        res = self.mgrconnector.dn_sendIP(mac,0,0,0xff,data)
    
    def _lbrDisconnectedCallback(self):
        
        self.lbrconnector = None
        
        self.LBRConnectionFrame.updateGuiDisconnected()

#============================ main ============================================

def main():
    LBRConnectionGuiHandler = LBRConnectionGui()
    LBRConnectionGuiHandler.start()

if __name__ == '__main__':
    main()

##
# end of LBRConnection
# \}
# 
