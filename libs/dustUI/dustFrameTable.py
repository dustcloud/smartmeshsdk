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

class dustFrameTable(dustFrame.dustFrame):
    
    def __init__(self,parentElem,guiLock,frameName="data table",row=0,column=0):
        
        # record variables
        self.guiElems = []
        
        # init parent
        dustFrame.dustFrame.__init__(
            self,
            parentElem  = parentElem,
            guiLock     = guiLock,
            frameName   = frameName,
            row         = row,
            column      = column,
            scrollable  = True,
        )
                  
    #======================== public ==========================================
    
    def update(self,data,displayOptions={}):
    
        if not self._isSameSize(data):
            self._createAndFillLabels(data,displayOptions)
        else:
            self._justFillLabels(data,displayOptions)
    
    #======================== private =========================================
    
    def _isSameSize(self,data):
        
        if len(data)!=len(self.guiElems):
            return False
        
        for i in range(len(data)):
            if len(data[i])!=len(self.guiElems[i]):
                return False
                
        return True
        
    def _createAndFillLabels(self,data,displayOptions):
        
        # clear old elems
        for line in self.guiElems:
            for elem in line:
                elem.removeGui()
        self.guiElems = []
        
        # create and fill labels
        for row in range(len(data)):
            self.guiElems.append([])
            for column in range(len(data[row])):
                temp = dustGuiLib.Label(self.container,
                                 text=str(data[row][column]),
                                 border=1,
                                 bg=dustStyle.COLOR_BG,
                                 relief=Tkinter.RIDGE,
                                 borderwidth=1,
                                 padx=3,
                                 pady=3)
                self._add(temp,row,
                               column,
                               sticky=Tkinter.W+Tkinter.E)
                self.guiElems[-1].append(temp)
        
        # apply display options
        self._applyDisplayOptions(displayOptions)
    
    def _justFillLabels(self,data,displayOptions):
        
        # fill labels
        for row in range(len(data)):
            for column in range(len(data[row])):
                self.guiElems[row][column].configure(text=str(data[row][column]))
        
        # apply display options
        self._applyDisplayOptions(displayOptions)
        
    #======================== helpers =========================================
    
    def _applyDisplayOptions(self,displayOptions):
        for k,v in displayOptions.items():
            if k=='rowColors':
                self._applyRowColors(v)
    
    def _applyRowColors(self,rowColorOptions):
        if len(rowColorOptions)!=len(self.guiElems):
            return
        
        for row in range(len(self.guiElems)):
            for col in range(len(self.guiElems[row])):
                self.guiElems[row][col].configure(bg=rowColorOptions[row])

#============================ sample app ======================================
# The following gets called only if you run this module as a standalone app, by
# double-clicking on this source file. This code is NOT executed when importing
# this module is a larger application
#
class exampleApp(object):
    
    def __init__(self):
        self.window  = dustWindow("dustFrameTable",
                                  self._closeCb)
        self.guiLock            = threading.Lock()
        self.frame = dustFrameTable(
                                self.window,
                                self.guiLock,
                                row=0,column=0)
        self.frame.show()
        self.frame.update(
                [
                    ['a','b','c'],
                    ['d','e','f'],
                ]
            )
        
        self.window.mainloop()
    
    def _closeCb(self):
        print " _closeCb called"

if __name__ == '__main__':
    import threading
    from dustWindow import dustWindow
    exampleApp()