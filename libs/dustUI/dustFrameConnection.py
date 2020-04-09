#!/usr/bin/python

#============================ adjust path =====================================

import sys
import os
if __name__ == '__main__':
    here = sys.path[0]
    sys.path.insert(0, os.path.join(here, '..'))

#============================ imports =========================================

import tkinter
import traceback

from . import dustGuiLib
from . import dustFrame
from   .dustStyle                            import dustStyle

from SmartMeshSDK.ApiDefinition             import IpMgrDefinition,       \
                                                   IpMoteDefinition,      \
                                                   HartMgrDefinition,     \
                                                   HartMoteDefinition

from SmartMeshSDK.IpMgrConnectorMux         import IpMgrConnectorMux
from SmartMeshSDK.IpMgrConnectorSerial      import IpMgrConnectorSerial
from SmartMeshSDK.IpMoteConnector           import IpMoteConnector
from SmartMeshSDK.HartMgrConnector          import HartMgrConnector
from SmartMeshSDK.HartMoteConnector         import HartMoteConnector

from SmartMeshSDK.ApiException              import ConnectionError,       \
                                                   CommandError

#============================ body ============================================

class dustFrameConnection(dustFrame.dustFrame):
    
    def __init__(self,parentElem,guiLock,connectCb,frameName="connection",row=0,column=0):
        
        # record variables
        self.connectCb    = connectCb
        
        # init parent
        dustFrame.dustFrame.__init__(self,parentElem,guiLock,frameName,row,column)
        
        # row 0: serial port
        self.serialFrame = tkinter.Frame(self.container,
                                borderwidth=0,
                                bg=dustStyle.COLOR_BG)
        
        temp = dustGuiLib.Label(self.serialFrame,
                             font=dustStyle.FONT_BODY,
                             bg=dustStyle.COLOR_BG,
                             text="through serial port:")
        self._add(temp,0,0,columnspan=3)
        
        temp = dustGuiLib.Label(self.serialFrame,
                             font=dustStyle.FONT_BODY,
                             bg=dustStyle.COLOR_BG,
                             text="port name:")
        self._add(temp,1,0)
        
        self.serialPortText = dustGuiLib.Text(self.serialFrame,
                                              font=dustStyle.FONT_BODY,
                                              width=25,
                                              height=1,
                                              returnAction=self._connectSerial)
        self.serialPortText.insert(1.0,"")
        self._add(self.serialPortText,1,1)
        
        self.serialButton = dustGuiLib.Button(self.serialFrame,
                                              text='connect',
                                              command=self._connectSerial)
        self._add(self.serialButton,1,2)

        # row 2: serialMux
        self.serialMuxFrame = tkinter.Frame(self.container,
                                borderwidth=0,
                                bg=dustStyle.COLOR_BG)
        
        temp = dustGuiLib.Label(self.serialMuxFrame,
                             font=dustStyle.FONT_BODY,
                             text="through serialMux:",
                             bg=dustStyle.COLOR_BG)
        self._add(temp,0,0,columnspan=5)
        
        temp = dustGuiLib.Label(self.serialMuxFrame,
                             font=dustStyle.FONT_BODY,
                             bg=dustStyle.COLOR_BG,
                             text="host:")
        self._add(temp,1,0)
        
        self.serialMuxHostText = dustGuiLib.Text(self.serialMuxFrame,
                                        font=dustStyle.FONT_BODY,
                                        width=15,
                                        height=1,
                                        returnAction=self._connectSerialMux)
        self.serialMuxHostText.insert(1.0,"127.0.0.1")
        self._add(self.serialMuxHostText,1,1)
        
        temp = dustGuiLib.Label(self.serialMuxFrame,
                             font=dustStyle.FONT_BODY,
                             bg=dustStyle.COLOR_BG,
                             text="port:")
        self._add(temp,1,2)
        
        self.serialMuxPortText = dustGuiLib.Text(self.serialMuxFrame,
                                        font=dustStyle.FONT_BODY,
                                        width=5,
                                        height=1,
                                        returnAction=self._connectSerialMux)
        self.serialMuxPortText.insert(1.0,"9900")
        self._add(self.serialMuxPortText,1,3)
        
        self.serialMuxButton = dustGuiLib.Button(self.serialMuxFrame,
                                                 text='connect',
                                                 command=self._connectSerialMux)
        self._add(self.serialMuxButton,1,4)

        # row 3: xml
        self.xmlFrame = tkinter.Frame(self.container,borderwidth=0,bg=dustStyle.COLOR_BG)
        temp = dustGuiLib.Label(self.xmlFrame,
                             font=dustStyle.FONT_BODY,
                             bg=dustStyle.COLOR_BG,
                             text="through XML-RPC:")
        self._add(temp,0,0,columnspan=5)
        
        temp = dustGuiLib.Label(self.xmlFrame,
                             font=dustStyle.FONT_BODY,
                             bg=dustStyle.COLOR_BG,
                             text="host:")
        self._add(temp,1,0)
        
        self.xmlHostText = dustGuiLib.Text(self.xmlFrame,
                            font=dustStyle.FONT_BODY,
                            width=15,
                            height=1,
                            returnAction=self._connectXml)
        self.xmlHostText.insert(1.0,"")
        self._add(self.xmlHostText,1,1)
        
        temp = dustGuiLib.Label(self.xmlFrame,
                            font=dustStyle.FONT_BODY,
                            bg=dustStyle.COLOR_BG,
                            text="port:")
        self._add(temp,1,2)
        
        self.xmlPortText = dustGuiLib.Text(self.xmlFrame,
                                        font=dustStyle.FONT_BODY,
                                        width=5,
                                        height=1,
                                        returnAction=self._connectXml)
        self.xmlPortText.insert(1.0,"4445")
        self._add(self.xmlPortText,1,3)
        
        self.xmlButton = dustGuiLib.Button(self.xmlFrame,
                                           text='connect',
                                           command=self._connectXml)
        self._add(self.xmlButton,1,4)
        
        # row 4: text
        self.tipLabel = dustGuiLib.Label(self.container,borderwidth=0,bg=dustStyle.COLOR_BG)
        self.guiLock.acquire()
        self.tipLabel.grid(row=4,column=0,sticky=tkinter.W)
        self.guiLock.release()
                  
    #======================== public ==========================================
    
    def apiLoaded(self,apiDef):
        # call the parent's apiLoaded function
        dustFrame.dustFrame.apiLoaded(self,apiDef)
        
        # display/hide connection forms
        self._showHideConnectionForms()
    
    def updateGuiDisconnected(self):
        
        # update the connection fields
        self.guiLock.acquire()
        self.serialPortText.configure(bg=dustStyle.COLOR_BG)
        self.serialMuxHostText.configure(bg=dustStyle.COLOR_BG)
        self.serialMuxPortText.configure(bg=dustStyle.COLOR_BG) 
        self.xmlHostText.configure(bg=dustStyle.COLOR_BG)
        self.xmlPortText.configure(bg=dustStyle.COLOR_BG)
        self.tipLabel.configure(text="")
        self.guiLock.release()
        
        # update the buttons
        self.guiLock.acquire()
        self.serialButton.configure(text='connect',command=self._connectSerial)
        self.serialMuxButton.configure(text='connect', command=self._connectSerialMux)
        self.xmlButton.configure(text='connect', command=self._connectXml)
        self.guiLock.release()
        
        # display/hide connection forms
        self._showHideConnectionForms()
    
    #======================== private =========================================

    def _showHideConnectionForms(self):
        self.guiLock.acquire()
        if (
             isinstance(self.apiDef,IpMoteDefinition.IpMoteDefinition) or
             isinstance(self.apiDef,IpMgrDefinition.IpMgrDefinition)   or
             isinstance(self.apiDef,HartMoteDefinition.HartMoteDefinition)
           ):
            self.serialFrame.grid(row=2,column=0,sticky=tkinter.W)
        if (
             isinstance(self.apiDef,IpMgrDefinition.IpMgrDefinition)
           ):
            self.serialMuxFrame.grid(row=1,column=0,sticky=tkinter.W)
        if (
             isinstance(self.apiDef,HartMgrDefinition.HartMgrDefinition)
           ):
            self.xmlFrame.grid(row=3,column=0,sticky=tkinter.W)
        self.guiLock.release()
    
    def _connectSerial(self):
        '''
        \brief Connect through the serial port.
        '''
       
        # initialize the connector
        try:
            if   isinstance(self.apiDef,IpMgrDefinition.IpMgrDefinition):
                self.connector = IpMgrConnectorSerial.IpMgrConnectorSerial()
            elif isinstance(self.apiDef,IpMoteDefinition.IpMoteDefinition):
                self.connector = IpMoteConnector.IpMoteConnector()
            elif isinstance(self.apiDef,HartMoteDefinition.HartMoteDefinition):
                self.connector = HartMoteConnector.HartMoteConnector()
            else:
                raise SystemError
        except NotImplementedError as err:
            self.guiLock.acquire()
            self.tipLabel.configure(text=str(err))
            self.guiLock.release()
            return
        
        # read connection params from GUI
        self.guiLock.acquire()
        connectParams = {
            'port': self.serialPortText.get(1.0,tkinter.END).strip(),
        }
        self.guiLock.release()
        
        # connect to the serial port
        try:
            self.connector.connect(connectParams)
        except ConnectionError as err:
            self.guiLock.acquire()
            self.serialPortText.configure(bg=dustStyle.COLOR_ERROR)
            self.tipLabel.configure(text=str(err))
            self.guiLock.release()
            return
            
        # if you get here, the connector could connect, i.e. the COM port is available
        
        # make sure that the device attached to the serial port is really the mote we expect
        if   isinstance(self.apiDef,IpMgrDefinition.IpMgrDefinition):
            # nothing to do, since connecting to a manager includes a handshake
            pass
        
        elif isinstance(self.apiDef,IpMoteDefinition.IpMoteDefinition):
            try:
                res = self.connector.dn_getParameter_moteInfo()
            except (ConnectionError,CommandError) as err:
                
                # disconnect the connector
                self.connector.disconnect()
                
                # print error text
                output  = []
                output += ["Could open the COM port, but issuing dn_getParameter_moteInfo() failed."]
                output += ["Exact error received: {0}".format(err)]
                output += ["Please verify that the device connected to {0} is a SmartMesh IP mote.".format(connectParams['port'])]
                output += ["Please verify that the SmartMesh IP mote is configured in slave mode."]
                output  = '\n'.join(output)
                self.guiLock.acquire()
                self.serialPortText.configure(bg=dustStyle.COLOR_WARNING_NOTWORKING)
                self.tipLabel.configure(text=output)
                self.guiLock.release()
                return
            
        elif isinstance(self.apiDef,HartMoteDefinition.HartMoteDefinition):
            
            try:
                res = self.connector.dn_getParameter_moteInfo()
            except (ConnectionError,CommandError) as err:
                
                # disconnect the connector
                self.connector.disconnect()
                
                # print error text
                output  = []
                output += ["Could open the COM port, but issuing dn_getParameter_moteInfo() failed."]
                output += ["Exact error received: {0}".format(err)]
                output += ["Please verify that the device connected to {0} is a SmartMesh WirelessHART mote.".format(connectParams['port'])]
                output += ["Please verify that the SmartMesh WirelessHART mote is configured in slave mode."]
                output  = '\n'.join(output)
                self.guiLock.acquire()
                self.serialPortText.configure(bg=dustStyle.COLOR_WARNING_NOTWORKING)
                self.tipLabel.configure(text=output)
                self.guiLock.release()
                return
        else:
            raise SystemError
        
        # if you get here, the connection has succeeded
        self.guiLock.acquire()
        self.serialPortText.configure(bg=dustStyle.COLOR_NOERROR)
        self.tipLabel.configure(text="Connection successful.")
        self.guiLock.release()
        
        # hide other connectFrames
        self.guiLock.acquire()
        self.serialMuxFrame.grid_forget()
        self.xmlFrame.grid_forget()
        self.guiLock.release()
        
        # update the button
        self.guiLock.acquire()
        self.serialButton.configure(text='disconnect', command=self._disconnect)
        self.guiLock.release()
        
        # common connect routing
        self._connect()

    def _connectSerialMux(self):
        '''
        \brief Connect through the serial Mux.
        '''
        
        # initialize the connector
        try:
            if isinstance(self.apiDef,IpMgrDefinition.IpMgrDefinition):
                self.connector = IpMgrConnectorMux.IpMgrConnectorMux()
            else:
                raise SystemError
        except NotImplementedError as err:
            self.guiLock.acquire()
            self.tipLabel.configure(text=str(err))
            self.guiLock.release()
            return
           
        # read connection params from GUI
        self.guiLock.acquire()
        connectParams = {
            'host':     self.serialMuxHostText.get(1.0,tkinter.END).strip(),
            'port': int(self.serialMuxPortText.get(1.0,tkinter.END).strip()),
        }
        self.guiLock.release()
        
        # connect
        try:
            self.connector.connect(connectParams)
        except ConnectionError as err:
            self.guiLock.acquire()
            self.serialMuxHostText.configure(bg=dustStyle.COLOR_ERROR)
            self.serialMuxPortText.configure(bg=dustStyle.COLOR_ERROR)
            self.tipLabel.configure(text=str(err))
            self.guiLock.release()
            return
        else:
            self.guiLock.acquire()
            self.serialMuxHostText.configure(bg=dustStyle.COLOR_NOERROR)
            self.serialMuxPortText.configure(bg=dustStyle.COLOR_NOERROR)
            self.tipLabel.configure(text="Connection successful.")
            self.guiLock.release()
        
        # hide other connectFrames
        self.guiLock.acquire()
        self.serialFrame.grid_forget()
        self.xmlFrame.grid_forget()
        self.guiLock.release()
        
        # update the button
        self.guiLock.acquire()
        self.serialMuxButton.configure(text='disconnect', command=self._disconnect)
        self.guiLock.release()
        
        # common connect routing
        self._connect()

    def _connectXml(self):
        '''
        \brief Connect over XML-RPC.
        '''
        
        # initialize the connector
        try:
            if isinstance(self.apiDef,HartMgrDefinition.HartMgrDefinition):
                self.connector = HartMgrConnector.HartMgrConnector()
            else:
                raise SystemError
        except NotImplementedError as err:
            self.guiLock.acquire()
            self.tipLabel.configure(text=str(err))
            self.guiLock.release()
            return
           
        # read connection params from GUI
        self.guiLock.acquire()
        connectParams = {
            'host':     self.xmlHostText.get(1.0,tkinter.END).strip(),
            'port': int(self.xmlPortText.get(1.0,tkinter.END).strip()),
        }
        self.guiLock.release()

        # connect
        try:
            self.connector.connect(connectParams)
        except ConnectionError as err:
            self.guiLock.acquire()
            self.xmlHostText.configure(bg=dustStyle.COLOR_ERROR)
            self.xmlPortText.configure(bg=dustStyle.COLOR_ERROR)
            self.tipLabel.configure(text=str(err))
            self.guiLock.release()
            return
        else:
            self.guiLock.acquire()
            self.xmlHostText.configure(bg=dustStyle.COLOR_NOERROR)
            self.xmlPortText.configure(bg=dustStyle.COLOR_NOERROR)
            self.tipLabel.configure(text="Connection successful.")
            self.guiLock.release()
        
        # hide other connectFrames
        self.guiLock.acquire()
        self.serialFrame.grid_forget()
        self.serialMuxFrame.grid_forget()
        self.guiLock.release()
        
        # update the button
        self.guiLock.acquire()
        self.xmlButton.configure(text='disconnect', command=self._disconnect)
        self.guiLock.release()
        
        # common connect routine
        self._connect()

    #======================== helpers =========================================
    
    def _connect(self):
        '''
        \brief Connect routine common to all connectors.
        '''
        
        # call the callback
        self.connectCb(self.connector)
    
    def _disconnect(self):
        '''
        \brief Disconnect routine common to all connectors.
        '''
        
        # disconnect the connector from  the device
        self.connector.disconnect()

#============================ sample app ======================================
# The following gets called only if you run this module as a standalone app, by
# double-clicking on this source file. This code is NOT executed when importing
# this module is a larger application
#
class exampleApp(object):
    
    def __init__(self):
        self.window  = dustWindow("dustFrameConnection",
                                  self._closeCb)
        self.guiLock            = threading.Lock()
        self.frame = dustFrameConnection(
                                self.window,
                                self.guiLock,
                                self._connectCb,
                                row=0,column=0)
        self.apidef = IpMoteDefinition.IpMoteDefinition()
        self.frame.apiLoaded(self.apidef)
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