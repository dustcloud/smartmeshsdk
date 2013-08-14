#!/usr/bin/python

import imp
import sys
import os

def main_is_frozen():
    return (hasattr(sys, "frozen") or # new py2exe
            hasattr(sys, "importers") # old py2exe
            or imp.is_frozen("__main__")) # tools/freeze

# in dev mode, add the SmartMeshSDK/ folder to the path
dev_path = sys.path[0]
if dev_path:
    sys.path.insert(0, os.path.join(dev_path, '..', '..', 'dustUI'))
    sys.path.insert(0, os.path.join(dev_path, '..', '..', 'SmartMeshSDK'))

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
        
# we use the lock from the threading module to arbitrate access to the GUI
import threading
import logging
import logging.handlers

# API definitions
from ApiDefinition           import  ApiDefinition
# exceptions
from ApiException            import  CommandError,ConnectionError,QueueError
# GUI elements from the lib/
from dustWindow              import dustWindow
from dustFrameApi            import dustFrameApi
from dustFrameConnection     import dustFrameConnection
from dustFrameCommand        import dustFrameCommand
from dustFrameResponse       import dustFrameResponse
from dustFrameNotifications  import dustFrameNotifications
from dustFrameText           import dustFrameText

##
# \addtogroup APIExplorer
# \{
# 

class NotifListener(threading.Thread):
    
    def __init__(self,connector,notifCb,disconnectedCb):
    
        # record variables
        self.connector       = connector
        self.notifCb         = notifCb
        self.disconnectedCb  = disconnectedCb
        
        # init the parent
        threading.Thread.__init__(self)
        self.name            = "NotifListener"
        
    #======================== public ==========================================
    
    def run(self):
        keepListening = True
        while keepListening:
            try:
                input = self.connector.getNotificationInternal(-1)
            except (ConnectionError,QueueError) as err:
                keepListening = False
            else:
                if input:
                    self.notifCb(input)
                else:
                    keepListening = False
        self.disconnectedCb()

class APIExplorer(object):
    
    def __init__(self):
    
        # create local variables
        self.guiLock            = threading.Lock()
        self.lastNotifLock      = threading.Lock()
        self.lastNotif          = None
        self.apiDef             = None
        self.connector          = None
        
        # create window
        self.window = dustWindow(
                                    'APIExplorer',
                                    self._windowCb_close)
        
        # fill window with frames
        self.apiFrame = dustFrameApi(
                                    self.window,
                                    self.guiLock,
                                    self._apiFrameCb_apiLoaded,
                                    row=0,column=0)
        self.connectionFrame = dustFrameConnection(
                                    self.window,
                                    self.guiLock,
                                    self._connectionFrameCb_connected,
                                    row=1,column=0)
        self.commandFrame = dustFrameCommand(
                                    self.window,
                                    self.guiLock,
                                    self._commandFrameCb_selected,
                                    self._commandFrameCb_response,
                                    self._commandFrameCb_responseError,
                                    row=2,column=0)
        self.responseFrame = dustFrameResponse(
                                    self.window,
                                    self.guiLock,
                                    row=3,column=0)
        self.notifFrame = dustFrameNotifications(
                                    self._getLastNotif,
                                    self.window,
                                    self.guiLock,
                                    row=4,column=0)
        self.toolTipFrame = dustFrameText(
                                    self.window,
                                    self.guiLock,
                                    frameName="tooltip",
                                    row=5,column=0)
        
        # choose the frames to show when app starts
        self.apiFrame.show()
    
    #======================== public ==========================================
    
    def run(self):
        '''
        This command instructs Tkinter to start executing and reacting to 
        user interactions with the GUI. It never returns and should therefore
        be the last command called.
        '''
        self.window.mainloop()
    
    #======================== private =========================================
    
    def _windowCb_close(self):
        if self.connector:
            self.connector.disconnect()
    
    def _apiFrameCb_apiLoaded(self,apiDefLoaded):
        '''
        \brief Called when the API has been loaded by the apiFrame.
        '''
        
        # record the loaded API
        self.apiDef = apiDefLoaded
        
        # tell other frames about it
        self.connectionFrame.apiLoaded(self.apiDef)
        self.commandFrame.apiLoaded(self.apiDef)
        self.responseFrame.apiLoaded(self.apiDef)
        self.notifFrame.apiLoaded(self.apiDef)
        
        # display frames
        self.guiLock.acquire()
        self.connectionFrame.show()
        self.commandFrame.show()
        self.responseFrame.show()
        self.notifFrame.show()
        self.toolTipFrame.show()
        self.guiLock.release()
    
    def _connectionFrameCb_connected(self,connector):
        '''
        \brief Called when the connectionFrame has connected.
        '''
        
        # store connector in global variable
        self.connector = connector
        
        # add notification listener
        self.notifListener  = NotifListener(self.connector,
                                            self._notifRxCallback,
                                            self._connectorDisconnectedCallback)
        self.notifListener.start()
        
        # tell commandFrame about it
        self.commandFrame.connectorLoaded(self.connector)
        self.notifFrame.connectorLoaded(self.connector)
    
    def _commandFrameCb_selected(self,nameArray):
        try:
            output  =   []
            output +=   [
                            self.apiDef.getDescription(
                                ApiDefinition.ApiDefinition.COMMAND,
                                nameArray
                            )
                        ]
            containsUtc = False
            for field in self.apiDef.getRequestFieldNames(nameArray):
                if field.count('utc'):
                    containsUtc = True
                    break
            if containsUtc:
                output  += ['\n\nNote: UTC fields are shown as a single struct in the API documentation.']
            self._writeTooltip(''.join(output))
        except CommandError as err:
            self._writeTooltip(str(err))
    
    def _commandFrameCb_response(self,commandArray,responseFields):
        self.responseFrame.indicateFields(commandArray,
                                          responseFields)
        
    def _commandFrameCb_responseError(self,errorText):
        self.responseFrame.indicateError(errorText)
    
    #======================== helpers =========================================
    
    def _writeTooltip(self,textToWrite):
        output  = []
        output += [textToWrite]
        output += ['\n\nNote: to enter a value in a field of type HEXDATA, please enter two digits for each byte (zero padded).']
        
        self.toolTipFrame.write(''.join(output))
    
    def _notifRxCallback(self, notif):
        self.lastNotifLock.acquire()
        self.lastNotif = notif
        self.lastNotifLock.release()
    
    def _getLastNotif(self):
        self.lastNotifLock.acquire()
        returnVal      = self.lastNotif
        self.lastNotif = None
        self.lastNotifLock.release()
        return returnVal
    
    def _connectorDisconnectedCallback(self):
        
        # update the GUI
        self.connectionFrame.updateGuiDisconnected()
        
        # delete the connector
        self.connector = None
    
#============================ logging =========================================

## Name of the log file
LOG_FILENAME       = 'APIExplorer.log'
## Format of the lines printed into the log file.
LOG_FORMAT         = "%(asctime)s [%(name)s:%(levelname)s] %(message)s"
## Handler called when a module logs some activity.
logHandler = logging.handlers.RotatingFileHandler(LOG_FILENAME,
                                               maxBytes=2000000,
                                               backupCount=5,
                                               mode='w'
                                               )
logHandler.setFormatter(logging.Formatter(LOG_FORMAT))
for loggerName in ['HartManager', 'SerialConnector','ByteArraySerializer','Hdlc','Crc']:
    temp = logging.getLogger(loggerName)
    temp.setLevel(logging.DEBUG)
    temp.addHandler(logHandler)

#============================ main ============================================

def main():
    app = APIExplorer()
    app.run()

if __name__ == "__main__":
    main()

##
# end of APIExplorer
# \}
# 
