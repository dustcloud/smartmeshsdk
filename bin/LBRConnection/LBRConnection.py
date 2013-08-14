#!/usr/bin/python

# add the SmartMeshSDK/ folder to the path
import sys
import os

temp_path = sys.path[0]
if temp_path:
    sys.path.insert(0, os.path.join(temp_path, '..', '..', 'dustUI'))
    sys.path.insert(0, os.path.join(temp_path, '..', '..', 'SmartMeshSDK'))

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

import threading
import logging
import logging.handlers

from dustWindow              import dustWindow
from dustFrameLBRConnection  import dustFrameLBRConnection
from dustFrameConnection     import dustFrameConnection
from dustFrameTable          import dustFrameTable

from ApiDefinition      import IpMgrDefinition

from IpMgrConnectorMux  import IpMgrConnectorMux
from IpMgrConnectorMux  import IpMgrSubscribe

from LbrConnector       import LbrConnector

from ApiException       import ConnectionError, QueueError

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
    '''
    \ingroup LBRConnection
    '''
   
    def __init__(self):
        
        # local variables
        self.guiLock            = threading.Lock()
        self.apiDef             = IpMgrDefinition.IpMgrDefinition()
        self.mgrconnector       = None
        self.lbrconnector       = None
        
        # create window
        self.window = dustWindow('LBRConnection',
                                 self._windowCb_close)
        
        # add an LBR connection frame
        self.LBRConnectionFrame = dustFrameLBRConnection(
                                    self.window,
                                    self.guiLock,
                                    self._LBRConnectionFrameCb_connected,
                                    frameName="LBR connection",
                                    row=0,column=0)
        self.LBRConnectionFrame.show()
        
        # add a manager connection frame
        self.mgrconnectionFrame = dustFrameConnection(
                                    self.window,
                                    self.guiLock,
                                    self._mgrconnectionFrameCb_connected,
                                    frameName="manager connection",
                                    row=1,column=0)
        self.mgrconnectionFrame.apiLoaded(self.apiDef)
        self.mgrconnectionFrame.show()
    
    #======================== public ==========================================
    
    def start(self):
        # start Tkinter's main thead
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

#============================ logging =========================================

## Name of the log file
LOG_FILENAME       = 'LBRConnection.log'
## Format of the lines printed into the log file.
LOG_FORMAT         = "%(asctime)s [%(name)s:%(levelname)s] %(message)s"
## Handler called when a module logs some activity.
logHandler = logging.handlers.RotatingFileHandler(LOG_FILENAME,
                                               maxBytes=2000000,
                                               backupCount=5,
                                               mode='w'
                                               )
logHandler.setFormatter(logging.Formatter(LOG_FORMAT))
for loggerName in ['LbrConnector']:
    temp = logging.getLogger(loggerName)
    temp.setLevel(logging.DEBUG)
    temp.addHandler(logHandler)

#============================ main ============================================

def main():
    LBRConnectionGuiHandler = LBRConnectionGui()
    LBRConnectionGuiHandler.start()

if __name__ == '__main__':
    main()
