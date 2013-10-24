#!/usr/bin/python

#============================ adjust path =====================================

import sys
import os
if __name__ == '__main__':
    here = sys.path[0]
    sys.path.insert(0, os.path.join(here, '..'))

#============================ imports =========================================
    
import Tkinter

import dustFrameFields

from   SmartMeshSDK.ApiDefinition import ApiDefinition

#============================ body ============================================

class dustFrameNotifications(dustFrameFields.dustFrameFields):
    
    ## refresh period, in ms
    REFRESHPERIOD = 200
    
    def __init__(self,getNotifCb,parentElem,guiLock,frameName="notifications",row=0,column=0):
        
        # record params
        self.getNotifCb = getNotifCb
        
        # init parent
        dustFrameFields.dustFrameFields.__init__(self,parentElem,
                                                      guiLock,
                                                      ApiDefinition.ApiDefinition.NOTIFICATION,
                                                      frameName,
                                                      row,column)
        
        # schedule the next update of the notifFrame
        guiLock.acquire()
        self.after(self.REFRESHPERIOD,self._checkNotif)
        guiLock.release()
                  
    #======================== public ==========================================
    
    #======================== private =========================================
    
    def _checkNotif(self):
        
        # check if notification and update GUI
        notif = self.getNotifCb()
        if notif:
            self.indicateFields(notif[0],notif[1])
        
        # schedule the next update of the notifFrame
        self.guiLock.acquire()
        self.after(self.REFRESHPERIOD,self._checkNotif)
        self.guiLock.release()

#============================ sample app ======================================
# The following gets called only if you run this module as a standalone app, by
# double-clicking on this source file. This code is NOT executed when importing
# this module is a larger application
#
class exampleApp(object):

    def __init__(self):
        self.window  = dustWindow("dustFrameNotifications",
                                  self._closeCb)
        self.guiLock            = threading.Lock()
        self.frame = dustFrameNotifications(
                                self._getNotifCb,
                                self.window,
                                self.guiLock,
                                row=0,column=0)
        self.frame.show()
        self.window.mainloop()
    
    def _closeCb(self):
        print " _closeCb called"
    def _getNotifCb(self):
        print " _getNotifCb called"

if __name__ == '__main__':
    import threading
    from dustWindow import dustWindow
    exampleApp()