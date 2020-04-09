#!/usr/bin/python

#============================ adjust path =====================================

import sys
import os
if __name__ == "__main__":
    here = sys.path[0]
    sys.path.insert(0, os.path.join(here, '..'))

#============================ imports =========================================

import time
import threading
import tkinter

from . import dustGuiLib
from . import dustFrame
from . import dustFrameText
from .dustStyle import dustStyle

#============================ defines =========================================

SYMBOL_DEGREE = u"\u2103"

#============================ body ============================================

class dustFrameDC2126AReportBlinker(threading.Thread):
    
    NUM_BLINKS    = 3*2
    BLINKS_PERIOD = 0.500 # s
    
    def __init__(self,guiElem):
        
        # store params
        self.guiElem    = guiElem
        
        # local variables
        self.goOn       = True
        self.semaphore  = threading.Semaphore()
        self.semaphore.acquire()
        self.blinksLeft = 0
        self.color      = False
        
        # initialize parent
        threading.Thread.__init__(self)
        self.name = 'dustFrameDC2126AReportBlinker'
        
        # start thread
        self.start()
    
    def run(self):
        while True:
            
            # wait to be asked to blink
            self.semaphore.acquire()
            
            # kill thread if needed
            if not self.goOn:
                return
            
            for _ in range(self.NUM_BLINKS):
                if self.color=='black':
                    self.color='green'
                else:
                    self.color='black'
                self.guiElem.configure(fg=self.color)
                time.sleep(self.BLINKS_PERIOD)
    
    #======================== public ==========================================
    
    def blink(self):
        self.semaphore.release()
    
    def close(self):
        self.goOn = False
        self.semaphore.release()

class dustFrameDC2126AReport(dustFrame.dustFrame):
    
    GUI_UPDATE_PERIOD = 500
    
    def __init__(self,parentElem,guiLock,
            getTemperatureCb,
            getEnergySourceCb,
            getAdcValueCb,
            frameName='Last Report',row=0,column=1):
        
        # record params
        self.getTemperatureCb     = getTemperatureCb
        self.getEnergySourceCb    = getEnergySourceCb
        self.getAdcValueCb        = getAdcValueCb
        
        # local variables
        self.blinker         = None
        
        # initialize parent
        dustFrame.dustFrame.__init__(self,
            parentElem,
            guiLock,
            frameName,
            row,column
        )
        
        # temperature
        self.temperature = dustGuiLib.Label(
            self.container,
            fg               = 'green',
            relief           = tkinter.GROOVE, 
            borderwidth      = 2,
            text             = '--.--'+SYMBOL_DEGREE
        )
        self._add(self.temperature,0,0)
        self.temperature.configure(
            font             = ('System', 40,'bold'),
            bg               = 'black',
        )
        self.blinker         = dustFrameDC2126AReportBlinker(self.temperature)
        
        # energysource
        temp                 = dustGuiLib.Label(
            self.container,
            text             = 'Mote powered by'
        )
        self._add(temp,1,0)
        temp.configure(
            font             = ("Helvetica",12,"bold"),
            anchor           = tkinter.CENTER
        )
        self.energysource     = dustGuiLib.Label(
            self.container,
            text             = '-',
        )
        self._add(self.energysource,2,0)
        self.energysource.configure(
            font             = ("Helvetica",16,"bold"),
            anchor           = tkinter.CENTER,
        )
        
        # adcValue
        self.adcValue       = dustGuiLib.Label(
            self.container,
            text             = '',
        )
        self._add(self.adcValue,3,0)
        self.adcValue.configure(
            anchor           = tkinter.CENTER,
        )
        
        # schedule first GUI update
        self.after(self.GUI_UPDATE_PERIOD,self.updateGui)
    
    #======================== public ==========================================
    
    def close(self):
        self.blinker.close()
    
    #======================== privater ========================================
    
    def updateGui(self):
        
        # temperature
        newTemperature = self.getTemperatureCb()
        if newTemperature!=None:
            self.temperature.configure(
                text = '{0:.2f}'.format(newTemperature)+SYMBOL_DEGREE,
            )
            self.blinker.blink()
        
        # energysource
        newEnergySource = self.getEnergySourceCb()
        if newEnergySource!=None:
            if newEnergySource=='solar':
                self.energysource.configure(fg='green')
            else:
                self.energysource.configure(fg='orange')
            self.energysource.configure(
                text = newEnergySource,
            )
        
        # adcValue
        newAdcValue = self.getAdcValueCb()
        if newAdcValue!=None:
            self.adcValue.configure(
                text = "({0:.1f}mV)".format(newAdcValue),
            )
        
        # schedule next GUI update
        self.after(self.GUI_UPDATE_PERIOD,self.updateGui)

#============================ sample app =============================
# The following gets called only if you run this module as a 
# standalone app, by double-clicking on this source file. This code is 
# NOT executed when importing this module is a larger application
#
class exampleApp(object):
    
    UPDATE_PERIOD_TEMPERATURE     = 5 # seconds
    UPDATE_PERIOD_ENERGYSOURCE    = 5 # seconds
    UPDATE_PERIOD_ADCVALUE        = 5 # seconds
    
    def __init__(self):
        
        now = time.time()
        self.lastUpdateTemperature     = now
        self.lastUpdateEnergySource    = now
        self.lastUpdateAdcValue        = now
        
        self.window  = dustWindow('dustFrameDC2126AReport',
            self._closeCb)
        self.guiLock    = threading.Lock()
        self.frame      = dustFrameDC2126AReport(
            self.window,
            self.guiLock,
            getTemperatureCb      = self._getTemperatureCb,
            getEnergySourceCb     = self._getEnergySourceCb,
            getAdcValueCb         = self._getAdcValueCb,
            row=0,column=0
        )
        self.frame.show()
        self.window.mainloop()
    
    def _getTemperatureCb(self):
        
        returnVal = None
        
        now = time.time()
        
        if now-self.lastUpdateTemperature>self.UPDATE_PERIOD_TEMPERATURE:
            returnVal = random.uniform(-40,85)
            self.lastUpdateTemperature = now
        
        print ("_getTemperatureCb() returns  {0}".format(returnVal))
        
        return returnVal
    
    def _getEnergySourceCb(self):
        
        returnVal = None
        
        now = time.time()
        
        if now-self.lastUpdateEnergySource>self.UPDATE_PERIOD_ENERGYSOURCE:
            returnVal =  random.choice(['solar','battery'])
            self.lastUpdateEnergySource = now
        
        print ("_getEnergySourceCb() returns  {0}".format(returnVal))
        
        return returnVal
    
    def _getAdcValueCb(self):
        
        returnVal = None
        
        now = time.time()
        
        if now-self.lastUpdateAdcValue>self.UPDATE_PERIOD_ADCVALUE:
            returnVal =  random.uniform(0,1800)
            self.lastUpdateAdcValue = now
        
        print ("_getAdcValueCb() returns     {0}".format(returnVal))
        
        return returnVal
        
    def _closeCb(self):
        print (' _closeCb called')
        self.frame.close()

if __name__ == '__main__':
    import random
    from .dustWindow import dustWindow
    exampleApp()
