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
from   dustUI                          import dustWindow,                 \
                                              dustFrameConnection,        \
                                              dustFrameDirection

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

UDP_PORT           = 0xf0b9
BYTE_FORWARD       = 0xf0
BYTE_REVERSE       = 0xf1

#============================ body ============================================

##
# \addtogroup Chaser
# \{
# 

class ChaserApp(object):
   
    def __init__(self):
        
        # local variables
        self.guiLock            = threading.Lock()
        self.apiDef             = IpMgrDefinition.IpMgrDefinition()
        self.connector          = None
        
        # create window
        self.window = dustWindow.dustWindow(
            'Chaser',
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
        
        # add a directionFrame
        self.directionFrame = dustFrameDirection.dustFrameDirection(
            self.window,
            self.guiLock,
            self._directionFrameCb,
            row=1,column=0
        )
    
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
    
    #===== GUI interaction
    
    def _connectionFrameCb_connected(self,connector):
        '''
        \brief Called when the connectionFrame has connected.
        '''
        
        # store the connector
        self.connector = connector
        
        # show the directionFrame
        self.directionFrame.show()
    
    def _directionFrameCb(self,forward):
        assert forward in [True,False]
        
        if forward:
            byteToSend       = BYTE_FORWARD
        else:
            byteToSend       = BYTE_REVERSE
        
        if self.connector:
            self.connector.dn_sendData(
                macAddress   = [0xff]*8,
                priority     = 0,
                srcPort      = UDP_PORT,
                dstPort      = UDP_PORT,
                options      = 0x00,
                data         = [byteToSend]
            )
    
    def _windowCb_close(self):
        '''
        \brief Called when the window is closed.
        '''
        
        if self.connector:
            self.connector.disconnect()
    
    #===== helpers
    

#============================ main ============================================

def main():
    app = ChaserApp()
    app.start()

if __name__ == '__main__':
    main()

##
# end of Chaser
# \}
# 
