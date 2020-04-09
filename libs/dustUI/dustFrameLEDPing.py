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
from   .dustStyle                  import dustStyle

from   SmartMeshSDK.ApiDefinition import ApiDefinition

#============================ body ============================================

class dustFrameLEDPing(dustFrame.dustFrame):
    
    def __init__(self,parentElem,guiLock,startPressedCb,stopPressedCb,frameName="LED ping",row=0,column=0):
        
        # record params
        self.startPressedCb = startPressedCb
        self.stopPressedCb  = stopPressedCb
        
        # init parent
        dustFrame.dustFrame.__init__(self,parentElem,guiLock,frameName,row,column)   
        
        # row 0: mac
        self.macText = dustGuiLib.Text(
            self.container,
            font=dustStyle.FONT_BODY,
            width=25,
            height=1
        )
        self.macText.insert(1.0,"00170d000038")
        self._add(self.macText,0,0)
        
        self.startStopButton = dustGuiLib.Button(
            self.container,
            text='start',
            command=self._startStopButtonPressed
        )
        self.disableButton()
        self._add(self.startStopButton,0,1)
        
        # row 1: canvas
        self.ledCanvas = tkinter.Canvas(
            self.container,
            width=200,
            height=200
        )
        self._add(self.ledCanvas,1,0,columnspan=2)
        
        # row 2: rtt label
        self.rttLabel = tkinter.Label(self.container)
        self._add(self.rttLabel,2,0,columnspan=2)
        
    #======================== public ==========================================
    
    def enableButton(self):
        '''
        \brief Enable start button.
        '''
        with self.guiLock:
            self.startStopButton.configure(state=tkinter.NORMAL)
    
    def disableButton(self):
        '''
        \brief Disable start button.
        '''
        with self.guiLock:
            self.startStopButton.configure(state=tkinter.DISABLED)
            self.startStopButton.configure(text='start')
    
    def enableMacText(self):
        '''
        \brief Enable MAC text field.
        '''
        with self.guiLock:
            self.macText.configure(state=tkinter.NORMAL)
    
    def disableMacText(self):
        '''
        \brief Disable MAC text field.
        '''
        with self.guiLock:
            self.macText.configure(state=tkinter.DISABLED)
    
    def updateLed(self,ledState):
        with self.guiLock:
            if ledState:
                self.ledCanvas.config(bg="blue")
            else:
                self.ledCanvas.config(bg="white")
    
    def updateRttLabel(self,newRtt):
        if newRtt:
            self.rttLabel.config(text='round-trip time: {0:.3f}s'.format(newRtt))
        else:
            self.rttLabel.config(text='')
    
    #======================== private =========================================

    def _startStopButtonPressed(self):
        
        with self.guiLock:
            buttonText = self.startStopButton.cget('text')
        
        if buttonText=='start':
            
            # get the MAC address
            with self.guiLock:
                macString = self.macText.get(1.0,tkinter.END).strip()
            
            # format MAC
            mac = []
            macString = ''.join( macString.split(" ") )
            if len(macString)!=16:
                with self.guiLock:
                    self.macText.configure(bg=dustStyle.COLOR_ERROR)
                return
            try:
                for i in range(0, len(macString), 2):
                    mac.append( int(macString[i:i+2],16) )
            except ValueError:
                with self.guiLock:
                    self.macText.configure(bg=dustStyle.COLOR_ERROR)
                return
            
            with self.guiLock:
                self.macText.configure(bg=dustStyle.COLOR_NOERROR)
                self.startStopButton.configure(text='stop')
            
            self.startPressedCb(mac)
        
        else:
            with self.guiLock:
                self.startStopButton.configure(text='start')
            
            self.stopPressedCb()
    
#============================ sample app ======================================
# The following gets called only if you run this module as a standalone app, by
# double-clicking on this source file. This code is NOT executed when importing
# this module is a larger application
#
class exampleApp(object):
    
    def __init__(self):
        self.window  = dustWindow(
            "dustFrameLEDPing",
            self._closeCb
        )
        self.guiLock            = threading.Lock()
        self.frame = dustFrameLEDPing(
            self.window,
            self.guiLock,
            self._startPressedCb,
            self._stopPressedCb,
            row=0,column=0
        )
        self.frame.show()
        self.frame.enableButton()
        self.window.mainloop()
    
    def _startPressedCb(self,mac):
        print (" _startPressedCb called mac={0}".format(mac))
    
    def _stopPressedCb(self):
        print (" _stopPressedCb called")
    
    def _closeCb(self):
        print (" _closeCb called")

if __name__ == '__main__':
    import threading
    from .dustWindow import dustWindow
    exampleApp()