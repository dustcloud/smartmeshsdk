#!/usr/bin/python

import sys
import os
if __name__ == '__main__':
    temp_path = sys.path[0]
    sys.path.insert(0, os.path.join(temp_path, '..', 'SmartMeshSDK'))

import Tkinter
try:
    import ttk
except ImportError:
    ttk = Tkinter
from dustStyle import dustStyle
import sdk_version

class dustWindow(Tkinter.Tk):
    '''
    \ingroup guiLib
    
    \brief A Tkinter window with a Dust look-and-feel.
    '''
    
    DUSTICON = '../../dustUI/dust.ico'
    
    def __init__(self,appName,closeCb):
        
        # record variables
        self.closeCb = closeCb
        
        # init parent
        Tkinter.Tk.__init__(self)
        
        # icon displayed in the upper-left
        try:
            self.iconbitmap(default=self.DUSTICON)
        except:
            pass # works on Windows only
        
        # name of the window. unichr(169) is the copyright sign
        self.title(appName+' '+unichr(169)+' Dust Networks')
        
        # background color
        self.configure(bg=dustStyle.COLOR_BG)
        
        # call releaseAndQuit when the close button is pressed
        self.protocol('WM_DELETE_WINDOW',self._releaseAndQuit)
        
        # the window cannot be resized
        self.resizable(0,0)
        
        # status bar with version
        versionString = '.'.join([str(i) for i in sdk_version.VERSION])
        self.version = ttk.Label(self,
                                 font=dustStyle.FONT_BODY,
                                 text="SmartMeshSDK "+versionString,
                                 anchor=Tkinter.E)
        self.version.grid(row=100,column=0,sticky=Tkinter.W+Tkinter.E)
        self.version.columnconfigure(0, weight=1)        
        
    #======================== public ==========================================
    
    #======================== private =========================================
    
    def _releaseAndQuit(self):
        '''
        \brief Close the main application.
        
        Called when the user closes the main application window.
        It closes both the GUI and the command line windows.
        '''
        
        global root
        
        # call the callback
        self.closeCb()
        
        # close the GUI
        self.quit()
        
        # exit
        sys.exit()

#============================ sample app ======================================
# The following gets called only if you run this module as a standalone app, by
# double-clicking on this source file. This code is NOT executed when importing
# this module is a larger application
#
class exampleApp(object):
    
    def __init__(self):
        self.window = dustWindow("dustWindow",
                                self._closeCb)
        temp = Tkinter.Frame(self.window,width=300,
                                         height=300,
                                         bg=dustStyle.COLOR_BG)
        temp.grid(row=0,column=0)
        self.window.mainloop()
    
    def _closeCb(self):
        print " _closeCb called"

if __name__ == '__main__':
    exampleApp()
