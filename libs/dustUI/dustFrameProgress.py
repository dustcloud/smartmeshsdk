#!/usr/bin/python

#============================ adjust path =====================================

import sys
import os
if __name__ == '__main__':
    here = sys.path[0]
    sys.path.insert(0, os.path.join(here, '..'))

#============================ imports =========================================

import Tkinter
import threading

import dustGuiLib
import dustFrame
from   dustStyle import dustStyle

#============================ body ============================================

class dustFrameProgress(dustFrame.dustFrame):
    
    SEVERITY_NOERROR    = 'no error'
    SEVERITY_WARNING    = 'warning'
    SEVERITY_ERROR      = 'error'
    SEVERITY_ALL        = [
        SEVERITY_NOERROR,
        SEVERITY_WARNING,
        SEVERITY_ERROR,
    ]
    
    def __init__(self,parentElem,guiLock,frameName="progress",row=0,column=0):
        
        # record variables
        
        # init parent
        dustFrame.dustFrame.__init__(self,parentElem,guiLock,frameName,row,column)
        
        # text field with yscrollbar 
        
        yscrollbar  = Tkinter.Scrollbar(self.container)
        yscrollbar.grid(row=0, column=1, sticky=Tkinter.N+Tkinter.S)
        
        self.textField = Tkinter.Text(
            self.container,
            font             = dustStyle.FONT_BODY,
            bg               = dustStyle.COLOR_BG,
            width            = 120,
            height           = 20,
            state            = 'disabled',
            yscrollcommand   = yscrollbar.set,
        )
        yscrollbar.config(command=self.textField.yview)
        
        self.textField.tag_config(self.SEVERITY_NOERROR,   background=dustStyle.COLOR_NOERROR)
        self.textField.tag_config(self.SEVERITY_WARNING,   background=dustStyle.COLOR_WARNING)
        self.textField.tag_config(self.SEVERITY_ERROR,     background=dustStyle.COLOR_ERROR)
        
        self._add(self.textField,0,0)
        
        # clear button
        temp = dustGuiLib.Button(
            self.container,
            text    = 'Clear',
            command = self.clear,
        )
        self._add(
            elem   = temp,
            row    = 1,
            column = 0,
            sticky = Tkinter.E,
        )
        
    #======================== public ==========================================
    
    def addStep(self,textToAdd,severity=None):
        
        assert type(textToAdd)==str
        if severity:
         assert severity in self.SEVERITY_ALL
        
        # enable
        self.textField.configure(state='normal')
        
        # write
        if severity:
           self.textField.insert(
               Tkinter.END,
               '{0}\n'.format(textToAdd.strip()),
               (severity,)
           )
        else:
           self.textField.insert(
               Tkinter.END,
               '{0}\n'.format(textToAdd.strip()),
           )
        
        # disable
        self.textField.configure(state='disabled')
    
    def clear(self):
        # enable
        self.textField.configure(state='normal')
        # delete
        self.textField.delete(1.0,Tkinter.END)
        # disable
        self.textField.configure(state='disabled')
    
    #======================== private =========================================

#============================ sample app ======================================
# The following gets called only if you run this module as a standalone app, by
# double-clicking on this source file. This code is NOT executed when importing
# this module is a larger application
#

class exampleApp(object):
    
    goOn = True
    
    class PublisherThread(threading.Thread):
        def __init__(self,cbGoOn,frameProgress):
            self.cbGoOn           = cbGoOn
            self.frameProgress    = frameProgress
            threading.Thread.__init__(self)
        def run(self):
            while self.cbGoOn():
                # wait
                time.sleep(0.5)
                # public
                self.frameProgress.addStep(
                    textToAdd = random.choice(['un','dos','tres','un pasito palante maria']),
                    severity  = random.choice(dustFrameProgress.SEVERITY_ALL),
                )
    
    def __init__(self):
        self.window  = dustWindow("dustFrameProgress",
                                  self._closeCb)
        self.guiLock            = threading.Lock()
        self.frameProgress = dustFrameProgress(
            self.window,
            self.guiLock,
            row=0,
            column=0,
        )
        self.frameProgress.show()
        
        publisher = self.PublisherThread(self._getGoOn,self.frameProgress)
        publisher.start()
        
        self.window.mainloop()
    
    def _closeCb(self):
        self.goOn = False
    
    def _getGoOn(self):
        return self.goOn

if __name__ == '__main__':
    import time
    import random
    from dustWindow import dustWindow
    exampleApp()
