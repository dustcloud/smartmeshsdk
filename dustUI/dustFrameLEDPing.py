#!/usr/bin/python

import sys
import os
if __name__ == '__main__':
    temp_path = sys.path[0]
    sys.path.insert(0, os.path.join(temp_path, '..', 'SmartMeshSDK'))

import Tkinter
import dustGuiLib
import dustFrame
from dustStyle import dustStyle
from ApiDefinition import ApiDefinition

class dustFrameLEDPing(dustFrame.dustFrame):
    
    def __init__(self,parentElem,guiLock,startPressedCb,stopPressedCb,frameName="LED ping",row=0,column=0):
        
        # record params
        self.startPressedCb = startPressedCb
        self.stopPressedCb  = stopPressedCb
        
        # init parent
        dustFrame.dustFrame.__init__(self,parentElem,guiLock,frameName,row,column)   
        
        # row 0: mac
        self.macText = dustGuiLib.Text(self.container,
                                    font=dustStyle.FONT_BODY,
                                    width=25,
                                    height=1)
        self.macText.insert(1.0,"00170d000038")
        self._add(self.macText,0,0)
        
        self.startStopButton = dustGuiLib.Button(self.container,
                                             text='start',
                                             command=self._startStopButtonPressed)
        self.disableButton()
        self._add(self.startStopButton,0,1)
        
        # row 1: canvas
        self.ledCanvas = Tkinter.Canvas(self.container,
                                    width=200,
                                    height=200)
        self._add(self.ledCanvas,1,0,columnspan=2)
        
    #======================== public ==========================================
    
    def enableButton(self):
        '''
        \brief Enable start button and MAC text field.
        '''
        self.startStopButton.configure(state=Tkinter.NORMAL)
    
    def disableButton(self):
        '''
        \brief Disable start button and MAC text field.
        '''
        self.startStopButton.configure(state=Tkinter.DISABLED)
        self.startStopButton.configure(text='start')
    
    def updateLed(self,ledState):
        self.guiLock.acquire()
        if ledState:
            self.ledCanvas.config(bg="blue")
        else:
            self.ledCanvas.config(bg="white")
        self.guiLock.release()
    
    #======================== private =========================================

    def _startStopButtonPressed(self):
        
        self.guiLock.acquire()
        buttonText = self.startStopButton.cget('text')
        self.guiLock.release()
        
        if buttonText=='start':
            
            # get the MAC address
            self.guiLock.acquire()
            macString = self.macText.get(1.0,Tkinter.END).strip()
            self.guiLock.release()
            
            # format MAC
            mac = []
            macString = ''.join( macString.split(" ") )
            if len(macString)!=16:
                self.guiLock.acquire()
                self.macText.configure(bg=dustStyle.COLOR_ERROR)
                self.guiLock.release()
                return
            try:
                for i in range(0, len(macString), 2):
                    mac.append( int(macString[i:i+2],16) )
            except ValueError:
                self.guiLock.acquire()
                self.macText.configure(bg=dustStyle.COLOR_ERROR)
                self.guiLock.release()
                return
            
            self.guiLock.acquire()
            self.macText.configure(bg=dustStyle.COLOR_NOERROR)
            self.startStopButton.configure(text='stop')
            self.guiLock.release()
            
            self.startPressedCb(mac)
        
        else:
            self.guiLock.acquire()
            self.startStopButton.configure(text='start')
            self.guiLock.release()
            
            self.stopPressedCb()
    
#============================ sample app ======================================
# The following gets called only if you run this module as a standalone app, by
# double-clicking on this source file. This code is NOT executed when importing
# this module is a larger application
#
class exampleApp(object):
    
    def __init__(self):
        self.window  = dustWindow("dustFrameLEDPing",
                                  self._closeCb)
        self.guiLock            = threading.Lock()
        self.frame = dustFrameLEDPing(
                                self.window,
                                self.guiLock,
                                self._startPressedCb,
                                row=0,column=0)
        self.frame.show()
        self.window.mainloop()
    
    def _startPressedCb(self):
        print " _startPressedCb called"
    
    def _closeCb(self):
        print " _closeCb called"

if __name__ == '__main__':
    import threading
    from dustWindow import dustWindow
    exampleApp()