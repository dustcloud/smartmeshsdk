#!/usr/bin/python

#============================ adjust path =====================================

import sys
import os
if __name__ == '__main__':
    here = sys.path[0]
    sys.path.insert(0, os.path.join(here, '..'))

#============================ imports =========================================

import tkinter

from . import dustFrameFields

from   SmartMeshSDK.ApiDefinition import ApiDefinition

#============================ body ============================================

class dustFrameResponse(dustFrameFields.dustFrameFields):
    
    def __init__(self,parentElem,guiLock,frameName="response",row=0,column=0):
        
        # init parent
        dustFrameFields.dustFrameFields.__init__(
            self,
            parentElem  = parentElem,
            guiLock     = guiLock,
            type        = ApiDefinition.ApiDefinition.COMMAND,
            frameName   = frameName,
            row         = row,
            column      = column,
        )
    
    #======================== public ==========================================
    
    #======================== private =========================================

#============================ sample app ======================================
# The following gets called only if you run this module as a standalone app, by
# double-clicking on this source file. This code is NOT executed when importing
# this module is a larger application
#
class exampleApp(object):
    
    def __init__(self):
        self.window     = dustWindow(
            "dustFrameResponse",
            self._closeCb,
        )
        self.guiLock    = threading.Lock()
        self.frame      = dustFrameResponse(
            self.window,
            self.guiLock,
            row         = 0,
            column      = 0,
        )
        self.frame.show()
        self.window.mainloop()
    
    def _closeCb(self):
        print (" _closeCb called")

if __name__ == '__main__':
    import threading
    from .dustWindow import dustWindow
    exampleApp()