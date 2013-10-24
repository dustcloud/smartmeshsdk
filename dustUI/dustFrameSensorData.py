#!/usr/bin/python

#============================ adjust path =====================================

import sys
import os
if __name__ == '__main__':
    here = sys.path[0]
    sys.path.insert(0, os.path.join(here, '..'))

#============================ imports =========================================

import Tkinter
import time

import dustGuiLib
import dustFrame
from   dustStyle import dustStyle

#============================ body ============================================

class dustFrameSensorData(dustFrame.dustFrame):
    
    def __init__(self,parentElem,guiLock,frameName="sensor data",row=0,column=0):
        
        # record variables
        
        # init parent
        dustFrame.dustFrame.__init__(self,parentElem,guiLock,frameName,row,column)
        
        #row 0: slide
        self.slide = Tkinter.Scale(self.container,
                                   from_=0,
                                   to=0xffff,
                                   state=Tkinter.DISABLED,
                                   orient=Tkinter.HORIZONTAL)
        self._add(self.slide,0,0,columnspan=2)
        
        #row 1: sourceMac
        temp = dustGuiLib.Label(self.container,
                             text='source MAC:')
        self._add(temp,1,0)
        self.sourceMac = dustGuiLib.Label(self.container)
        self._add(self.sourceMac,1,1)
        
        #row 2: sourcePort
        temp = dustGuiLib.Label(self.container,
                             text='source port:')
        self._add(temp,2,0)
        self.sourcePort = dustGuiLib.Label(self.container)
        self._add(self.sourcePort,2,1)
        
        #row 3: destPort
        temp = dustGuiLib.Label(self.container,
                             text='destination port:')
        self._add(temp,3,0)
        self.destPort = dustGuiLib.Label(self.container)
        self._add(self.destPort,3,1)
    
    #======================== public ==========================================
    
    def update(self,sensorData):
        
        # display/hide connection forms
        self.guiLock.acquire()
        
        # slide
        if len(sensorData['payload'])==2:
            temp = sensorData['payload'][0]*256+sensorData['payload'][1]
            self.slide.config(state=Tkinter.NORMAL)
            self.slide.set(temp)
            self.slide.config(state=Tkinter.DISABLED)
        
        # sourceMac
        if len(sensorData['payload'])==2:
            temp = ''
            for i in sensorData['srcMac']:
                j = hex(i)[2:]
                while len(j)<2:
                   j = '0'+j
                temp += j
            self.sourceMac.configure(text=temp)
        
        # sourcePort
        if len(sensorData['payload'])==2:
            self.sourcePort.configure(text=str(sensorData['srcPort']))
        
        # destPort
        if len(sensorData['payload'])==2:
            self.destPort.configure(text=str(sensorData['destPort']))
        
        self.guiLock.release()
    
    #======================== private =========================================

#============================ sample app ======================================
# The following gets called only if you run this module as a standalone app, by
# double-clicking on this source file. This code is NOT executed when importing
# this module is a larger application
#
class exampleApp(object):
    
    def __init__(self):
        self.window  = dustWindow("dustFrameSensorData",
                                  self._closeCb)
        self.guiLock            = threading.Lock()
        self.frame = dustFrameSensorData(
                                self.window,
                                self.guiLock,
                                row=0,column=0)
        self.frame.show()
        self.window.mainloop()
    
    def _closeCb(self):
        print " _closeCb called"

if __name__ == '__main__':
    import threading
    from dustWindow import dustWindow
    exampleApp()