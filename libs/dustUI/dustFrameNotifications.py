#!/usr/bin/python

#============================ adjust path =====================================

import sys
import os
if __name__ == '__main__':
    here = sys.path[0]
    sys.path.insert(0, os.path.join(here, '..'))

#============================ imports =========================================
    
import tkinter

from . import dustFrameFields

from   SmartMeshSDK.ApiDefinition import ApiDefinition

#============================ body ============================================

class dustFrameNotifications(dustFrameFields.dustFrameFields):
    
    ## refresh period, in ms
    REFRESHPERIOD = 200
    
    def __init__(self,getNotifCb,parentElem,guiLock,frameName="notifications",row=0,column=0):
        
        # record params
        self.getNotifCb = getNotifCb
        
        # init parent
        dustFrameFields.dustFrameFields.__init__(
            self,
            parentElem  = parentElem,
            guiLock     = guiLock,
            type        = ApiDefinition.ApiDefinition.NOTIFICATION,
            frameName   = frameName,
            row         = row,
            column      = column,
        )
        
        # schedule the next update of the notifFrame
        with guiLock:
            self.after(self.REFRESHPERIOD,self._checkNotif)
    
    #======================== public ==========================================
    
    #======================== private =========================================
    
    def _checkNotif(self):
        
        # check if notification and update GUI
        notif = self.getNotifCb()
        if notif:
            self.indicateFields(notif[0],notif[1])
        
        # schedule the next update of the notifFrame
        with self.guiLock:
            self.after(self.REFRESHPERIOD,self._checkNotif)

#============================ sample app ======================================
# The following gets called only if you run this module as a standalone app, by
# double-clicking on this source file. This code is NOT executed when importing
# this module is a larger application
#
class exampleApp(object):
    
    ts_last_update      = None
    DATA_UPDATE_PERIOD  = 0
    
    def __init__(self):
        self.window  = dustWindow("dustFrameNotifications",
                                  self._closeCb)
        self.guiLock            = threading.Lock()
        self.frame = dustFrameNotifications(
            self._getNotifCb,
            self.window,
            self.guiLock,
            row=0,
            column=0,
        )
        self.frame.show()
        self.frame.apiLoaded(IpMgrDefinition.IpMgrDefinition())
        self.window.mainloop()
    
    def _getNotifCb(self):
        
        now = time.time()
        
        if self.ts_last_update==None or now>self.ts_last_update+self.DATA_UPDATE_PERIOD:
            self.ts_last_update = now
            return random.choice(
                [
                    (
                        ['notification', 'notifData'],
                        [
                            {
                                'macAddress': tuple([random.randint(0x00,0xff) for _ in range(8)]),
                                'srcPort':    random.randint(0x0000,0xffff),
                                'utcUsecs':   int((now*1000000)%1000000),
                                'utcSecs':    int(now),
                                'dstPort':    random.randint(0x0000,0xffff),
                                'data':       tuple([random.randint(0x00,0xff) for _ in range(random.randint(10,10))])
                            } for _ in range(5)
                        ]
                    ),
                ]
            )
            return random.choice(
                [
                    (
                        ['notification', 'notifData'],
                        {
                            'macAddress': tuple([random.randint(0x00,0xff) for _ in range(8)]),
                            'srcPort':    random.randint(0x0000,0xffff),
                            'utcUsecs':   int((now*1000000)%1000000),
                            'utcSecs':    int(now),
                            'dstPort':    random.randint(0x0000,0xffff),
                            'data':       tuple([random.randint(0x00,0xff) for _ in range(random.randint(2,15))])
                        },
                    ),
                    (
                        ['notification', 'notifHealthReport'],
                        {
                            'macAddress': tuple([random.randint(0x00,0xff) for _ in range(8)]),
                            'payload':    tuple([random.randint(0x00,0xff) for _ in range(random.randint(2,15))])
                        },
                    ),
                    (
                        ['notification', 'notifData'],
                        [
                            {
                                'macAddress': tuple([random.randint(0x00,0xff) for _ in range(8)]),
                                'srcPort':    random.randint(0x0000,0xffff),
                                'utcUsecs':   int((now*1000000)%1000000),
                                'utcSecs':    int(now),
                                'dstPort':    random.randint(0x0000,0xffff),
                                'data':       tuple([random.randint(0x00,0xff) for _ in range(random.randint(2,15))])
                            } for _ in range(random.randint(2,15))
                        ]
                    ),
                ]
            )
    
    def _closeCb(self):
        print (" _closeCb called")

if __name__ == '__main__':
    import threading
    import random
    import time
    from SmartMeshSDK.ApiDefinition  import IpMgrDefinition
    from .dustWindow import dustWindow
    exampleApp()