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

from   SmartMeshSDK.utils         import AppUtils,                   \
                                         FormatUtils
from   SmartMeshSDK.ApiDefinition import ApiDefinition
from   SmartMeshSDK.ApiException  import CommandError,               \
                                         ConnectionError,            \
                                         QueueError
from   dustUI                     import dustWindow,                 \
                                         dustFrameApi,               \
                                         dustFrameConnection,        \
                                         dustFrameCommand,           \
                                         dustFrameResponse,          \
                                         dustFrameNotifications,     \
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

#============================ body ============================================

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
        self.daemon = True

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
        self.guiLock         = threading.Lock()
        self.lastNotifLock   = threading.Lock()
        self.lastNotif       = None
        self.apiDef          = None
        self.connector       = None
        
        # create window
        self.window = dustWindow.dustWindow(
            appName          = 'APIExplorer',
            closeCb          = self._windowCb_close,
        )
        
        # fill window with frames
        self.apiFrame        = dustFrameApi.dustFrameApi(
            parentElem       = self.window,
            guiLock          = self.guiLock,
            cbApiLoaded      = self._apiFrameCb_apiLoaded,
            row              = 0,
            column           = 0,
        )
        self.connectionFrame = dustFrameConnection.dustFrameConnection(
            parentElem       = self.window,
            guiLock          = self.guiLock,
            connectCb        = self._connectionFrameCb_connected,
            row              = 1,
            column           = 0,
        )
        self.commandFrame    = dustFrameCommand.dustFrameCommand(
            parentElem       = self.window,
            guiLock          = self.guiLock,
            selectedCb       = self._commandFrameCb_selected,
            responseCb       = self._commandFrameCb_response,
            responseErrorCb  = self._commandFrameCb_responseError,
            row              = 2,
            column           = 0,
        )
        self.responseFrame   = dustFrameResponse.dustFrameResponse(
            parentElem       = self.window,
            guiLock          = self.guiLock,
            row              = 3,
            column           = 0,
        )
        self.notifFrame      = dustFrameNotifications.dustFrameNotifications(
            getNotifCb       = self._getLastNotif,
            parentElem       = self.window,
            guiLock          = self.guiLock,
            row              = 4,
            column           = 0,
        )
        self.toolTipFrame    = dustFrameText.dustFrameText(
            parentElem       = self.window,
            guiLock          = self.guiLock,
            frameName        = "tooltip",
            row              = 5,
            column           = 0,
        )
        
        # choose the frames to show when app starts
        self.apiFrame.show()
    
    #======================== public ==========================================
    
    def run(self):
        '''
        This command instructs the GUI to start executing and reacting to 
        user interactions. It never returns and should therefore be the last
        command called.
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
        with self.guiLock:
            self.connectionFrame.show()
            self.commandFrame.show()
            self.responseFrame.show()
            self.notifFrame.show()
            self.toolTipFrame.show()
    
    def _connectionFrameCb_connected(self,connector):
        '''
        \brief Called when the connectionFrame has connected.
        '''
        
        # store connector in global variable
        self.connector = connector
        
        # add notification listener
        self.notifListener  = NotifListener(
            self.connector,
            self._notifRxCallback,
            self._connectorDisconnectedCallback,
        )
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
        self.responseFrame.indicateFields(
            commandArray,
            responseFields,
        )
        
    def _commandFrameCb_responseError(self,errorText):
        self.responseFrame.indicateError(
            errorText
        )
    
    #======================== helpers =========================================
    
    def _writeTooltip(self,textToWrite):
        output  = []
        output += [textToWrite]
        output += [
            '\n\nNote: to enter a value in a field of type HEXDATA, please enter two digits for each byte (zero padded).'
        ]
        self.toolTipFrame.write(''.join(output))
    
    def _notifRxCallback(self, notif):
        with self.lastNotifLock:
            self.lastNotif = notif
    
    def _getLastNotif(self):
        with self.lastNotifLock:
            returnVal      = self.lastNotif
            self.lastNotif = None
            return returnVal
    
    def _connectorDisconnectedCallback(self):
        
        # update the GUI
        self.connectionFrame.updateGuiDisconnected()
        
        # delete the connector
        self.connector.disconnect()
        self.connector = None

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
