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

from SmartMeshSDK.ApiDefinition   import IpMgrDefinition,       \
                                         IpMoteDefinition,      \
                                         HartMgrDefinition,     \
                                         HartMoteDefinition

#============================ body ============================================

class dustFrameApi(dustFrame.dustFrame):
    
    # acceptable network types
    IP        = 'SmartMesh IP'
    WHART     = 'SmartMesh WirelessHART'

    # acceptable device types
    MANAGER   = 'manager'
    MOTE      = 'mote'
    
    def __init__(self,parentElem,guiLock,cbApiLoaded,frameName="api",row=0,column=0,deviceType=None):
        
        # store params
        self.cbApiLoaded = cbApiLoaded
        self.deviceType  = deviceType
        
        # init parent
        dustFrame.dustFrame.__init__(self,parentElem,guiLock,frameName,row,column)
        
        temp = dustGuiLib.Label(self.container,
                             text="network type:")
        self._add(temp,0,0)

        self.networkTypeString = tkinter.StringVar(self.container)
        self.networkTypeString.set(self.IP)
        self.networkTypeMenu   = dustGuiLib.OptionMenu(self.container,
                                                       self.networkTypeString,
                                                       self.IP,
                                                       self.WHART)
        self._add(self.networkTypeMenu,0,1)

        temp = dustGuiLib.Label(self.container,
                             text="device type:")
        self._add(temp,0,2)

        self.deviceTypeString = tkinter.StringVar(self)
        if deviceType:
            self.deviceTypeString.set(deviceType)
        else:
            self.deviceTypeString.set(self.MOTE)
        self.deviceTypeMenu   = dustGuiLib.OptionMenu(self.container,
                                                      self.deviceTypeString,
                                                      self.MANAGER,
                                                      self.MOTE)
        self._add(self.deviceTypeMenu,0,3)
        if self.deviceType:
            self.deviceTypeMenu.config (state=tkinter.DISABLED)

        self.loadButton = dustGuiLib.Button(self.container,
                                            text="load",
                                            command=self._loadApi)
        self._add(self.loadButton,0,4)
                  
    #======================== public ==========================================
    
    #======================== private =========================================
    
    def _loadApi(self):
        '''
        \brief Called when pressing the 'load' button.
        '''
        
        # read the configuration entered in the GUI
        self.guiLock.acquire()
        temp_networkType = self.networkTypeString.get()
        if not self.deviceType:
            self.deviceType  = self.deviceTypeString.get()
        self.guiLock.release()
        
        # load the API definition
        try:
            if   temp_networkType==self.IP    and self.deviceType==self.MANAGER:
                self.apiDef    = IpMgrDefinition.IpMgrDefinition()
            elif temp_networkType==self.IP    and self.deviceType==self.MOTE:
                self.apiDef    = IpMoteDefinition.IpMoteDefinition()
            elif temp_networkType==self.WHART and self.deviceType==self.MANAGER:
                self.apiDef    = HartMgrDefinition.HartMgrDefinition()
            elif temp_networkType==self.WHART and self.deviceType==self.MOTE:
                self.apiDef    = HartMoteDefinition.HartMoteDefinition()
            else:
                raise SystemError("wrong combination "+\
                                  " temp_networkType="+str(temp_networkType)+\
                                  " self.deviceType="+str(self.deviceType))
        except NotImplementedError as err:
           print(str(err))
           return
        
        # freeze the form frame
        self.guiLock.acquire()
        self.networkTypeMenu.config(state=tkinter.DISABLED)
        self.deviceTypeMenu.config (state=tkinter.DISABLED)
        self.loadButton.config     (state=tkinter.DISABLED)
        self.guiLock.release()
        
        # call the callback
        self.cbApiLoaded(self.apiDef)

#============================ sample app ======================================
# The following gets called only if you run this module as a standalone app, by
# double-clicking on this source file. This code is NOT executed when importing
# this module is a larger application
#
class exampleApp(object):
    
    def __init__(self):
        self.window  = dustWindow("dustFrameApi",
                                  self._closeCb)
        self.guiLock            = threading.Lock()
        self.frame = dustFrameApi(
                                self.window,
                                self.guiLock,
                                self._apiFrameCb_apiLoaded,
                                row=0,column=0)
        self.frame.show()
        self.window.mainloop()
    
    def _closeCb(self):
        print(" _closeCb called")
    def _apiFrameCb_apiLoaded(self,param):
        print(" _apiFrameCb_apiLoaded called with param="+str(param))

if __name__ == '__main__':
    import threading
    from .dustWindow import dustWindow
    exampleApp()
