#!/usr/bin/python

#============================ adjust path =====================================

import sys
import os
if __name__ == '__main__':
    here = sys.path[0]
    sys.path.insert(0, os.path.join(here, '..'))

#============================ imports =========================================

import re
import tkinter.filedialog

from . import dustGuiLib
from . import dustFrame
from  .dustStyle                       import dustStyle

from   SmartMeshSDK.LbrConnector       import LbrConnector
from   SmartMeshSDK.ApiException       import ConnectionError

#============================ body ============================================

UPDATEPERIOD = 500 # in ms

class dustFrameLBRConnection(dustFrame.dustFrame):
    
    def __init__(self,parentElem,guiLock,connectedCb,frameName="br connection",row=0,column=0):
        
        # record variables
        self.connectedCb    = connectedCb
        
        # init parent
        dustFrame.dustFrame.__init__(self,parentElem,guiLock,frameName,row,column)
        
        #====
        
        # connect button
        self.connectButton = dustGuiLib.Button(self.container,
                                               text='connect',
                                               command=self._connect)
        self._add(self.connectButton,0,0)
        
        #====
        
        self.connectionErrorLabel = dustGuiLib.Label(self.container,text='')
        self._add(self.connectionErrorLabel,1,0,columnspan=2)
        
        #====
        
        # connection
        temp = dustGuiLib.Label(self.container,
                             text="connection:")
        self._add(temp,2,0)
        self.connectionLabel = dustGuiLib.Label(self.container,
                             text='')
        self._add(self.connectionLabel,2,1)
        
        # status
        temp = dustGuiLib.Label(self.container,
                             text="status:")
        self._add(temp,3,0)
        self.statusLabel = dustGuiLib.Label(self.container,
                             text='')
        self._add(self.statusLabel,3,1)
        
        # prefix
        temp = dustGuiLib.Label(self.container,
                             text="prefix:")
        self._add(temp,4,0)
        self.prefixLabel = dustGuiLib.Label(self.container,
                             text='')
        self._add(self.prefixLabel,4,1)
        
        # statsTx
        temp = dustGuiLib.Label(self.container,
                             text="transmitted to LBR:")
        self._add(temp,5,0)
        self.statsTxLabel = dustGuiLib.Label(self.container,
                                          text='')
        self._add(self.statsTxLabel,5,1)
        
        # statsRx
        temp = dustGuiLib.Label(self.container,
                             text="received from LBR:")
        self._add(temp,6,0)
        self.statsRxLabel = dustGuiLib.Label(self.container,
                                          text='')
        self._add(self.statsRxLabel,6,1)
        
        # have GUI update
        self.after(UPDATEPERIOD,self._updateGui)
                  
    #======================== public ==========================================
    
    #======================== private =========================================
    
    def _connect(self):
        '''
        \brief Connect to the LBR.
        '''
        
        # retrieve information from lbr authentication file
        try:
            connectParams = self._getReadAuthenticationFile()
        except TypeError:
            return
        
        # initialize the LBR connector
        self.connector = LbrConnector.LbrConnector()
        
        # connect
        try:
            self.connector.connect(connectParams)
        except ConnectionError as err:
            self.connectButton.configure(bg=dustStyle.COLOR_ERROR)
            self.connectionErrorLabel.configure(text=str(err),bg=dustStyle.COLOR_ERROR)
            return
        else:
            self.connectButton.configure(bg=dustStyle.COLOR_NOERROR)
            self.connectionErrorLabel.configure(text='',bg=dustStyle.COLOR_BG)
        
        # update the button
        self.guiLock.acquire()
        self.connectButton.configure(text='disconnect', command=self._disconnect)
        self.guiLock.release()
        
        # call the callback
        self.connectedCb(self.connector)

    def _disconnect(self):
        '''
        \brief Disconnect from the LBR.
        '''
        
        # disconnect from the LBR
        self.connector.disconnect()
    
    def updateGuiDisconnected(self):
        
        self.connector = None
        
        # update the button
        self.guiLock.acquire()
        self.connectButton.configure(text='connect',command=self._connect)
        self.connectButton.configure(bg=dustStyle.COLOR_BG)
        self.guiLock.release()
        
    def _updateGui(self):
        
        # get information
        if self.connector:
            username              = self.connector.getUsername()
            lbrAddr               = self.connector.getLbrAddr()
            lbrPort               = self.connector.getLbrPort()
            status                = self.connector.getStatus()
            prefix                = self.connector.getPrefix()
            (sentPackets,     \
             sentBytes,       \
             receivedPackets, \
             receivedBytes)       = self.connector.getStats()
        else:
            username              = ''
            lbrAddr               = ''
            lbrPort               = ''
            status                = 'disconnected'
            prefix                = ''
            sentPackets           = 0
            sentBytes             = 0
            receivedPackets       = 0
            receivedBytes         = 0
            
        # update GUI
        self.guiLock.acquire()
        if username:
            self.connectionLabel.configure(text=str(username)+'@'+str(lbrAddr)+':'+str(lbrPort))
        else:
            self.connectionLabel.configure(text='')
        self.statusLabel.configure(text=str(status))
        self.prefixLabel.configure(text=str(prefix))
        self.statsTxLabel.configure(text=str(sentPackets)+     ' pkts ('+str(sentBytes)+'B)')
        self.statsRxLabel.configure(text=str(receivedPackets)+ ' pkts ('+str(receivedBytes)+'B)')
        self.guiLock.release()
        
        # schedule next update
        self.after(UPDATEPERIOD,self._updateGui)
    
    #======================== helpers =========================================
    
    def _getReadAuthenticationFile(self):
        # open authentication file
        authFile = tkinter.filedialog.askopenfile(
                        mode        ='r',
                        title       = 'Select an LBR authentication file',
                        multiple    = False,
                        initialfile = 'guest.lbrauth',
                        filetypes = [
                                        ("LBR authentication file", "*.lbrauth"),
                                        ("All types", "*.*"),
                                    ]
                    )
        # parse authentication file
        connectParams = {}
        for line in authFile:
            match = re.search('(.*) = (.*)',line)
            if match!=None:
                key = match.group(1).strip()
                val = match.group(2).strip()
                try:
                    connectParams[key] = int(val)
                except ValueError:
                    connectParams[key] =     val
        
        # return the parameters I've found in the file
        return connectParams

#============================ sample app ======================================
# The following gets called only if you run this module as a standalone app, by
# double-clicking on this source file. This code is NOT executed when importing
# this module is a larger application
#
class exampleApp(object):
    
    def __init__(self):
        self.window  = dustWindow("dustFrameLBRConnection",
                                  self._closeCb)
        self.guiLock            = threading.Lock()
        self.frame = dustFrameLBRConnection(
                                self.window,
                                self.guiLock,
                                self._connectCb,
                                row=0,column=0)
        self.frame.show()
        self.window.mainloop()
    
    def _closeCb(self):
        print (" _closeCb called")
    def _connectCb(self,param):
        print (" _connectCb called with param="+str(param))

if __name__ == '__main__':
    import threading
    from .dustWindow import dustWindow
    exampleApp()