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
    ]
)
if not goodToGo:
    print "Your installation does not allow this application to run:\n"
    print reason
    raw_input("Press any button to exit")
    sys.exit(1)

#============================ imports =========================================

import threading
import binascii

from   SmartMeshSDK.utils              import AppUtils,                   \
                                              FormatUtils
from   SmartMeshSDK.SerialConnector    import Hdlc
from   dustUI                          import dustWindow,                 \
                                              dustFrameConversion

#============================ logging =========================================

import logging

# local
class NullHandler(logging.Handler):
    def emit(self, record):
        pass
log = logging.getLogger('App')
log.setLevel(logging.ERROR)
log.addHandler(NullHandler())

#============================ defines =========================================

#============================ globals =========================================

#============================ setup/teardown ==================================

AppUtils.configureLogging()

#============================ defines =========================================

#============================ body ============================================

##
# \addtogroup HdlcTool
# \{
# 

class HdlcConverter(Hdlc.Hdlc):
    
    #======================== overloading Hdlc ================================
    
    def __init__(self):
        self.doneSem         = threading.Lock()
        self.doneSem.acquire()
        self.rawBytes        = []
        self.hdlcBytes       = []
        self.rxBytes         = []
        self.rxDoneLock      = threading.Lock()
        self.rxDoneLock.acquire()
        
        Hdlc.Hdlc.__init__(
            self,
            rxcallback       = self._rxcallback,
            connectcallback  = self._connectcallback,
        )
    
    def connect(self):
        self.pyserialHandler = self
        
        self._restart()
        self.connected       = True
        self.name            = '{0}_HDLC'.format(self.comPort)
        self.start()
    
    #======================== overloading pyserial functions ==================
    
    def read(self,numBytes):
        if len(self.rxBytes):
            byteRead = self.rxBytes.pop(0)
            print 'HdlcConverter.read {0:x}'.format(byteRead)
            return chr(byteRead)
        else:
            print 'HdlcConverter.read blocked'
            if self.toHdlcMode:
                self.rxDoneLock.acquire() # block
            else:
                self.doneSem.release()
            return ''
    
    def write(self,stringToWrite):
        self.hdlcBytes = [ord(b) for b in stringToWrite]
        print 'HdlcConverter.write {0}'.format(FormatUtils.formatBuffer(self.hdlcBytes))
        self.doneSem.release()
        return len(stringToWrite)
    
    #======================== public ==========================================
    
    def toHdlc(self,rawBytes):
        self.toHdlcMode      = True
        self.connect()
        self.send(rawBytes)
        self.doneSem.acquire()
        self.rxDoneLock.release()
        return self.hdlcBytes
    
    def fromHdlc(self,hdlcBytes):
        self.toHdlcMode      = False
        self.rxBytes         = hdlcBytes
        self.connect()
        self.doneSem.acquire()
        self.rxDoneLock.release()
        return self.rawBytes
    
    #======================== private =========================================
    
    def _rxcallback(self,payload):
        self.rawBytes = payload
        self.doneSem.release()
    
    def _connectcallback(self,state):
        print 'HdlcConverter._connectcallback state={0}'.format(state)

class hdlcToolGui(object):
    
    def __init__(self):
        
        # variables
        self.guiLock            = threading.Lock()
        
        # create window
        self.window = dustWindow.dustWindow(
            'HdlcTool',
            self._windowCb_close,
        )
        
        # add a connection frame
        self.conversionFrame = dustFrameConversion.dustFrameConversion(
            self.window,
            self.guiLock,
            topName          = 'raw',
            toBottomCb       = self._conversionFrameCb_toHdlc,
            bottomName       = 'HDLC',
            toTopCb          = self._conversionFrameCb_toRaw,
            frameName        = "HDLC Conversion",
            row=0,column=0
        )
        self.conversionFrame.show()
    
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
        pass
    
    def _conversionFrameCb_toHdlc(self,textEntered):
        
        # convert to byte list
        try:
            input = self._toByteList(textEntered)
        except Exception as err:
            print err # TODO poipoi print in status bar
            return
        
        # convert to HDLC
        output = HdlcConverter().toHdlc(input)
        
        # write bottom
        self.conversionFrame.writeBottom(self._formatBuffer(output))
    
    def _conversionFrameCb_toRaw(self,textEntered):
        
        # convert to byte list
        try:
            input = self._toByteList(textEntered)
        except Exception as err:
            print err # TODO poipoi print in status bar
            return
        
        # convert from HDLC
        output = HdlcConverter().fromHdlc(input)
        
        # write top
        self.conversionFrame.writeTop(self._formatBuffer(output))
    
    def _toByteList(self,input):
        output = input.strip()
        output = output.replace(' ','')
        output = output.replace('-','')
        output = binascii.unhexlify(output)
        output = [ord(b) for b in output]
        
        return output
    
    def _formatBuffer(self,buf):
        return ' '.join(["%.2x"%i for i in buf])

#============================ main ============================================

def main():
    hdlcToolHandler = hdlcToolGui()
    hdlcToolHandler.start()

if __name__ == '__main__':
    main()

##
# end of HdlcTool
# \}
# 
