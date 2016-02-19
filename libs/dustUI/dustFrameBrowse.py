#!/usr/bin/python

#============================ adjust path =====================================

import sys
import os
if __name__ == '__main__':
    here = sys.path[0]
    sys.path.insert(0, os.path.join(here, '..'))

#============================ logging =========================================

import logging
class NullHandler(logging.Handler):
    def emit(self, record):
        pass
log = logging.getLogger('dustFrameBrowse')
log.setLevel(logging.INFO)
log.addHandler(NullHandler())

#============================ imports =========================================

import Tkinter
import tkFileDialog

import dustGuiLib
import dustFrame
from dustStyle     import dustStyle

#============================ body ============================================

class dustFrameBrowse(dustFrame.dustFrame):
    
    def __init__(self,parentElem,guiLock,selected_cb,allowMultipleFiles=True,frameName="browse",row=0,column=0):
        
        # record variables
        self.selected_cb           = selected_cb
        self.allowMultipleFiles    = allowMultipleFiles
        
        # init parent
        dustFrame.dustFrame.__init__(self,parentElem,guiLock,frameName,row,column)
        
        #====
        
        # browse button
        self.browseButton = dustGuiLib.Button(self.container,
                                              text='browse',
                                              command=self._browse)
        self._add(self.browseButton,0,0)
    
    #======================== public ==========================================
    
    #======================== private =========================================
    
    def _browse(self):
        '''
        \brief Browse button clicked; have the user select a number of files.
        '''
        
        if self.allowMultipleFiles:
            title = 'Select multiple files'
        else:
            title = 'Select a single file'
        
        # open authentication file
        selectedFiles = tkFileDialog.askopenfilenames(
                            title       = 'Select a file',
                            multiple    = self.allowMultipleFiles,
                            filetypes = [
                                            ("All types", "*.*"),
                                        ]
                        )
        
        # workaround for http://bugs.python.org/issue5712
        if isinstance(selectedFiles, (str, unicode)):
            selectedFiles = self.tk.splitlist(selectedFiles)
        
        # log
        log.debug("user selected {0}".format([f.split('/')[-1] for f in selectedFiles]))
        
        # call the callback
        self.selected_cb(selectedFiles)

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
        self.frame = dustFrameBrowse(
                                self.window,
                                self.guiLock,
                                self._dustFrameBrowse_selected_cb,
                                row=0,column=0)
        self.frame.show()
        self.window.mainloop()
    
    def _closeCb(self):
        print " _closeCb called"
        
    def _dustFrameBrowse_selected_cb(self,filenames):
        print "user selected the following files: {0}".format(filenames)
    
if __name__ == '__main__':
    import threading
    from dustWindow import dustWindow
    exampleApp()