#!/usr/bin/python

#============================ adjust path =====================================

import sys
import os
if __name__ == '__main__':
    here = sys.path[0]
    sys.path.insert(0, os.path.join(here, '..'))

#============================ imports =========================================

import Tkinter

import dustGuiLib
import dustFrame
from   dustStyle import dustStyle

#============================ body ============================================

class dustFrameForm(dustFrame.dustFrame):
    
    def __init__(self,parentElem,guiLock,setCb,frameName="Form",row=0,column=0):
        
        # validate params
        assert callable(setCb)
        
        # store params
        self.setCb      = setCb
        
        # init parent
        dustFrame.dustFrame.__init__(self,parentElem,guiLock,frameName,row,column)
        
        # row 0: form
        self.formFrame = Tkinter.Frame(
            self.container,
            borderwidth=0,
            bg=dustStyle.COLOR_BG,
        )
        self.formFrame.grid(row=0,column=0,sticky=Tkinter.W)
        
        self.formText = dustGuiLib.Text(
            self.formFrame,
            font=dustStyle.FONT_BODY,
            width=50,
            height=1,
            returnAction=self._buttonCb,
        )
        self.formText.insert(1.0,"")
        self._add(self.formText,0,0)
        
        self.formButton = dustGuiLib.Button(
            self.formFrame,
            text='set',
            command=self._buttonCb,
        )
        self._add(self.formButton,0,1)
        
    #======================== public ==========================================
    
    def setVal(self,value):
        self.formText.delete(1.0, Tkinter.END)
        self.formText.insert(1.0, str(value))
    
    def setColor(self,color):
        self.formText.configure(bg=color)
    
    def disable(self):
        self.formText.configure(state=Tkinter.DISABLED)
        self.formButton.configure(state=Tkinter.DISABLED)
    
    #======================== private =========================================
    
    def _buttonCb(self):
        enteredText = str(self.formText.get(1.0,Tkinter.END).strip())
        self.setCb(enteredText)
    
    #======================== helpers =========================================

#============================ sample app ======================================
# The following gets called only if you run this module as a standalone app, by
# double-clicking on this source file. This code is NOT executed when importing
# this module is a larger application
#
class exampleApp(object):
    
    def __init__(self):
        
        self.window  = dustWindow(
            "dustFrameForm",
            self._closeCb,
        )
        self.guiLock            = threading.Lock()
        self.frame = dustFrameForm(
            self.window,
            self.guiLock,
            self._buttonCb,
            "example Frame",
            row=0,column=0
        )
        self.frame.show()
        
        self.frame.setVal("testVal")
        self.frame.setColor(dustStyle.COLOR_NOERROR)
        
        self.window.mainloop()
    
    def _buttonCb(self,enteredText):
        print 'button pressed. enteredText="{0}"'.format(enteredText)
        self.frame.disable()
    
    def _closeCb(self):
        print " _closeCb called"

if __name__ == '__main__':
    import threading
    from dustWindow import dustWindow
    exampleApp()
