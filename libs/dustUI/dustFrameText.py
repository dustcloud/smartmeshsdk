#!/usr/bin/python

#============================ adjust path =====================================

import sys
import os
if __name__ == '__main__':
    here = sys.path[0]
    sys.path.insert(0, os.path.join(here, '..'))

#============================ imports =========================================

import tkinter

from . import dustGuiLib
from . import dustFrame
from  .dustStyle import dustStyle

#============================ body ============================================

class dustFrameText(dustFrame.dustFrame):
    
    def __init__(self,parentElem,guiLock,frameName="text",row=0,column=0):
        
        # record variables
        
        # init parent
        dustFrame.dustFrame.__init__(self,parentElem,guiLock,frameName,row,column)
        
        #row 0: text field
        self.toolTipLabel = dustGuiLib.Label(self.container,
                                          font=dustStyle.FONT_BODY,
                                          bg=dustStyle.COLOR_BG,
                                          wraplength=600,
                                          justify=tkinter.LEFT,
                                          text="")
        self._add(self.toolTipLabel,0,0)
                  
    #======================== public ==========================================
    
    def setWrapLength(self,newWrapLength):
        # display/hide connection forms
        self.guiLock.acquire()
        self.toolTipLabel.configure(wraplength=newWrapLength)
        self.guiLock.release()
    
    def write(self,textToWrite):
        
        # display/hide connection forms
        self.guiLock.acquire()
        self.toolTipLabel.configure(text=textToWrite)
        self.guiLock.release()
    
    #======================== private =========================================

#============================ sample app ======================================
# The following gets called only if you run this module as a standalone app, by
# double-clicking on this source file. This code is NOT executed when importing
# this module is a larger application
#
class exampleApp(object):
    
    def __init__(self):
        self.window  = dustWindow("dustFrameText",
                                  self._closeCb)
        self.guiLock            = threading.Lock()
        self.frame = dustFrameText(
                                self.window,
                                self.guiLock,
                                row=0,column=0)
        self.frame.show()
        self.frame.write("Hello, World!")
        self.window.mainloop()
    
    def _closeCb(self):
        print (" _closeCb called")

if __name__ == '__main__':
    import threading
    from .dustWindow import dustWindow
    exampleApp()