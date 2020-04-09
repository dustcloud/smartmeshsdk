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
from   .dustStyle import dustStyle

#============================ body ============================================

class dustFrameConversion(dustFrame.dustFrame):
    
    FONT_MONOSPACE = ("Courier", 10)
    
    def __init__(self,parentElem,guiLock,frameName="Conversion",topName='top',toBottomCb=None,bottomName='bottom',toTopCb=None,row=0,column=0):
        
        if toBottomCb:
            assert callable(toBottomCb)
        if toTopCb:
            assert callable(toTopCb)
        
        # record variables
        self.topName         = topName
        self.toBottomCb      = toBottomCb
        self.bottomName      = bottomName
        self.toTopCb         = toTopCb
        
        # init parent
        dustFrame.dustFrame.__init__(self,parentElem,guiLock,frameName,row,column)
        
        #===== row 0: topName
        temp = dustGuiLib.Label(
            self.container,
            text=self.topName,
        )
        self._add(temp,0,0,columnspan=2)
        temp.configure(font=dustStyle.FONT_HEADER)
        
        #===== row 1: topField
        
        topscrollbar  = tkinter.Scrollbar(self.container)
        topscrollbar.grid(row=1, column=2, sticky=tkinter.N+tkinter.S)
        self.topField = tkinter.Text(
            self.container,
            bg               = dustStyle.COLOR_BG,
            width            = 100,
            height           = 10,
            yscrollcommand   = topscrollbar.set,
        )
        topscrollbar.config(command=self.topField.yview)
        self._add(self.topField,1,0,columnspan=2)
        self.topField.configure(font=self.FONT_MONOSPACE)
        
        #===== row 2: buttons
        
        temp = dustGuiLib.Button(
            self.container,
            text        = 'to {0}'.format(self.bottomName),
            command     = self._toBottomButtonPressed
        )
        self._add(temp,2,0)
        
        temp = dustGuiLib.Button(
            self.container,
            text        = 'to {0}'.format(self.topName),
            command     = self._toTopButtonPressed
        )
        self._add(temp,2,1)
        
        #===== row 3: bottomName
        temp = dustGuiLib.Label(
            self.container,
            text=self.bottomName,
        )
        self._add(temp,3,0,columnspan=2)
        temp.configure(font=dustStyle.FONT_HEADER)
        
        #===== row 4: bottomField
        
        bottomscrollbar  = tkinter.Scrollbar(self.container)
        bottomscrollbar.grid(row=4, column=2, sticky=tkinter.N+tkinter.S)
        self.bottomField = tkinter.Text(
            self.container,
            bg               = dustStyle.COLOR_BG,
            width            = 100,
            height           = 10,
            yscrollcommand   = bottomscrollbar.set,
        )
        bottomscrollbar.config(command=self.bottomField.yview)
        self._add(self.bottomField,4,0,columnspan=2)
        self.bottomField.configure(font=self.FONT_MONOSPACE)
                  
    #======================== public ==========================================
    
    def writeTop(self,textToWrite):
        self.topField.delete(1.0,tkinter.END)
        self.topField.insert(tkinter.END,textToWrite)
    
    def writeBottom(self,textToWrite):
        self.bottomField.delete(1.0,tkinter.END)
        self.bottomField.insert(tkinter.END,textToWrite)
    
    #======================== private =========================================
    
    def _toBottomButtonPressed(self):
        if self.toBottomCb:
            # get value
            val = self.topField.get(1.0,tkinter.END).strip()
            
            # call the callback
            self.toBottomCb(val)
    
    def _toTopButtonPressed(self):
        if self.toTopCb:
            # get value
            val = self.bottomField.get(1.0,tkinter.END).strip()
            
            # call the callback
            self.toTopCb(val)
    
#============================ sample app ======================================
# The following gets called only if you run this module as a standalone app, by
# double-clicking on this source file. This code is NOT executed when importing
# this module is a larger application
#
class exampleApp(object):
    
    def __init__(self):
        self.window  = dustWindow(
            "dustFrameConversion",
            self._closeCb
        )
        self.guiLock         = threading.Lock()
        self.frame = dustFrameConversion(
            self.window,
            self.guiLock,
            toBottomCb     = self._topEnteredCb,
            toTopCb  = self._bottomEnteredCb,
            row=0,column=0
        )
        self.frame.show()
        self.window.mainloop()
    
    def _topEnteredCb(self,textEntered):
        output  = []
        output += ['entered on top:']
        output += [textEntered]
        output  = '\n'.join(output)
        print (output)
    
    def _bottomEnteredCb(self,textEntered):
        output  = []
        output += ['entered on bottom:']
        output += [textEntered]
        output  = '\n'.join(output)
        print (output)
    
    def _closeCb(self):
        print (" _closeCb called")

if __name__ == '__main__':
    import threading
    from .dustWindow import dustWindow
    exampleApp()