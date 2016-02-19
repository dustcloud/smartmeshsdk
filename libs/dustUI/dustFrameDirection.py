#!/usr/bin/python

#============================ adjust path =====================================

import sys
import os
if __name__ == '__main__':
    here = sys.path[0]
    sys.path.insert(0, os.path.join(here, '..'))

#============================ imports =========================================

import Tkinter
import tkFont
import threading

import dustGuiLib
import dustFrame
from   dustStyle             import dustStyle
from   SmartMeshSDK.utils    import FormatUtils

#============================ defines =========================================

#============================ body ============================================

class dustFrameDirection(dustFrame.dustFrame):
    
    WIDTH               = 400
    HEIGHT              = 120
    
    def __init__(self,parentElem,guiLock,directionCb=None,frameName="direction",row=0,column=0):
        
        # record variables
        self.directionCb     = directionCb
        
        # init parent
        dustFrame.dustFrame.__init__(self,parentElem,guiLock,frameName,row,column)
        
        
        self.canvas = Tkinter.Canvas(
            self.container,
            width            = self.WIDTH,
            height           = self.HEIGHT,
        )
        self._add(self.canvas,1,0)
        
        self.arrowForward = self.canvas.create_polygon(
            [
                380,60,
                350,30,
                350,40,
                220,40,
                220,80,
                350,80,
                350,90,
            ],
            outline     = 'black',
            width       = 2,
            fill        = 'white',
        )
        self.canvas.tag_bind(self.arrowForward, '<ButtonPress-1>', self._arrowClicked)
        
        self.arrowReverse = self.canvas.create_polygon(
            [
                 20,60,
                 50,30,
                 50,40,
                180,40,
                180,80,
                 50,80,
                 50,90,
            ],
            outline     = 'black',
            width       = 2,
            fill        = 'white',
        )
        self.canvas.tag_bind(self.arrowReverse, '<ButtonPress-1>', self._arrowClicked)
    
    #======================== public ==========================================
    
    #======================== private =========================================
    
    def _arrowClicked(self,event):
        widgetClicked = event.widget.find_closest(event.x, event.y)[0]
        
        assert widgetClicked in [self.arrowReverse,self.arrowForward]
        
        self.canvas.itemconfig(widgetClicked,fill='red')
        self.canvas.after(500,self._clearFillArrows)
        
        if widgetClicked==self.arrowForward:
            forward = True
        else:
            forward = False
        
        if self.directionCb:
            self.directionCb(forward)
    
    def _clearFillArrows(self):
        self.canvas.itemconfig(self.arrowForward,fill='white')
        self.canvas.itemconfig(self.arrowReverse,fill='white')

#============================ sample app ======================================
# The following gets called only if you run this module as a standalone app, by
# double-clicking on this source file. This code is NOT executed when importing
# this module is a larger application
#

class exampleApp(object):
    
    def __init__(self):
        self.window               = dustWindow("Direction",self._closeCb)
        self.guiLock              = threading.Lock()
        self.frameDirection       = dustFrameDirection(
            self.window,
            self.guiLock,
            directionCb           = self._directionCb,
            row                   = 0,
            column                = 0,
        )
        self.frameDirection.show()
        
        self.window.mainloop()
    
    def _directionCb(self,forward):
        print '_directionCb clicked, forward={0}'.format(forward)
    
    def _closeCb(self):
        pass

if __name__ == '__main__':
    import random
    from dustWindow import dustWindow
    exampleApp()
