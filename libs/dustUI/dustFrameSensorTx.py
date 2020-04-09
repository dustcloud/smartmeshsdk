#!/usr/bin/python

#============================ adjust path =====================================

import sys
import os
if __name__ == '__main__':
    here = sys.path[0]
    sys.path.insert(0, os.path.join(here, '..'))

#============================ imports =========================================

import tkinter

from. import dustGuiLib
from . import dustFrame
from  .dustStyle import dustStyle

from   SmartMeshSDK import ApiException

#============================ defines =========================================

WELL_KNOWN_ADDR_MANAGER      = 'ff020000000000000000000000000002'
DEFAULT_DEST_PORT            = '61000'
DEFAULT_HOST_ADDR            = '20010470006600170000000000000002'

#============================ body ============================================

class dustFrameSensorTx(dustFrame.dustFrame):
    
    ERROR   = 'error'
    NOERROR = 'noerror'
    
    def __init__(self,parentElem,guiLock,frameName="sensor",row=0,column=0):
        
        # record params
        
        # local variables
        self.connector      = None
        self.payloadCounter = 0
        
        # init parent
        dustFrame.dustFrame.__init__(self,parentElem,guiLock,frameName,row,column)
        
        #row 0: slide
        self.slide = tkinter.Scale(self.container,
                                   from_=0,
                                   to=0xffff,
                                   orient=tkinter.HORIZONTAL)
        self._add(self.slide,0,0,columnspan=3)
        
        #row 1: label
        temp = dustGuiLib.Label(self.container,
                             text='destination IPv6 address')
        self._add(temp,1,0)
        temp.configure(font=dustStyle.FONT_HEADER)
        
        temp = dustGuiLib.Label(self.container,
                             text='dest. UDP port')
        self._add(temp,1,1)
        temp.configure(font=dustStyle.FONT_HEADER)
        
        #row 2: send to manager
        temp = dustGuiLib.Label(self.container,
                             text=WELL_KNOWN_ADDR_MANAGER)
        self._add(temp,2,0)
        
        self.mgrPortText = dustGuiLib.Text(self.container,
                                           width=6,
                                           height=1)
        self.mgrPortText.insert(1.0,DEFAULT_DEST_PORT)
        self._add(self.mgrPortText,2,1)
        
        self.mgrButton = dustGuiLib.Button(self.container,
                                        text='send to manager',
                                        state=tkinter.DISABLED,
                                        command=self._sendMgr)
        self._add(self.mgrButton,2,2)
        
        #row 3: send to host
        self.hostAddrText = dustGuiLib.Text(self.container,
                                       width=35,
                                       height=1)
        self.hostAddrText.insert(1.0,DEFAULT_HOST_ADDR)
        self._add(self.hostAddrText,3,0)
        
        self.hostPortText = dustGuiLib.Text(self.container,
                                         width=6,
                                         height=1)
        self.hostPortText.insert(1.0,DEFAULT_DEST_PORT)
        self._add(self.hostPortText,3,1)
        
        self.hostButton = dustGuiLib.Button(self.container,
                                            text='send to host',
                                            state=tkinter.DISABLED,
                                            command=self._sendHost)
        self._add(self.hostButton,3,2)
        
        #row 4: status
        self.statusLabel = dustGuiLib.Label(self.container)
        self._add(self.statusLabel,4,0,columnspan=3)
                  
    #======================== public ==========================================
    
    def activate(self,connector,socketId):
        # store params
        self.connector = connector
        self.socketId  = socketId
        
        # enable send buttons
        self.mgrButton.config(state=tkinter.NORMAL)
        self.hostButton.config(state=tkinter.NORMAL)
    
    def disactivate(self):
        # forget about the connector
        self.connector = None
        
        # disable send buttons
        self.mgrButton.config(state=tkinter.DISABLED)
        self.hostButton.config(state=tkinter.DISABLED)
    
    #======================== private =========================================
    
    def _sendMgr(self):
        destAddr = WELL_KNOWN_ADDR_MANAGER
        destPort = int(self.mgrPortText.get(1.0,tkinter.END).strip())
        
        self._sendInternal(destAddr,destPort)
    
    def _sendHost(self):
        destAddr =     self.hostAddrText.get(1.0,tkinter.END).strip()
        try:
            destPort = int(self.hostPortText.get(1.0,tkinter.END).strip())
        except ValueError:
            self._printStatus(self.ERROR,"invalid port number")
        
        self._sendInternal(destAddr,destPort)
    
    #======================== helpers =========================================
    
    def _sendInternal(self,destAddrString,destPort):
        
        # format destAddr
        destAddr = []
        destAddrString = ''.join( destAddrString.split(" ") )
        if len(destAddrString)%2!=0:
            self._printStatus(self.ERROR,"destination address is not a even number of characters")
            return
        try:
            for i in range(0, len(destAddrString), 2):
                destAddr.append( int(destAddrString[i:i+2],16) )
        except ValueError:
            self._printStatus(self.ERROR,"destination address not hexadecimal numbers")
            return
        
        # prepare sensor data
        sensorValRaw = self.slide.get()
        sensorVal    = [(sensorValRaw>>8)%256,(sensorValRaw>>0)%256]
        
        try:
            res = self.connector.dn_sendTo(
                        self.socketId,
                        destAddr,
                        destPort,
                        0,
                        1,
                        self.payloadCounter,
                        sensorVal
                    )
            self.payloadCounter += 1
        except ApiException.APIError as err:
            self._printStatus(self.ERROR,str(err))
        else:
            assert(res.RC==0)
            self._printStatus(self.NOERROR,"Sent succesfully")
    
    def _printStatus(self,errorLevel,statusText):
        self.statusLabel.config(text=statusText)
        if   errorLevel in [self.NOERROR]:
            self.statusLabel.config(bg=dustStyle.COLOR_NOERROR)
        elif errorLevel in [self.ERROR]:
            self.statusLabel.config(bg=dustStyle.COLOR_ERROR)
        else:
            raise ValueError("unknown errorLevel {0}".format(errorLevel))

#============================ sample app ======================================
# The following gets called only if you run this module as a standalone app, by
# double-clicking on this source file. This code is NOT executed when importing
# this module is a larger application
#
class exampleApp(object):
    
    def __init__(self):
        self.window  = dustWindow("dustFrameSensorTx",
                                  self._closeCb)
        self.guiLock            = threading.Lock()
        self.frame = dustFrameSensorTx(
                                self.window,
                                self.guiLock,
                                row=0,column=0)
        self.frame.show()
        self.window.mainloop()
    
    def _closeCb(self):
        print (" _closeCb called")

if __name__ == '__main__':
    import threading
    from .dustWindow import dustWindow
    exampleApp()