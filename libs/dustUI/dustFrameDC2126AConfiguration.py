#!/usr/bin/python

#============================ adjust path =====================================

import sys
import os
if __name__ == "__main__":
    here = sys.path[0]
    sys.path.insert(0, os.path.join(here, '..'))

#============================ imports =========================================

import Tkinter

from   SmartMeshSDK.utils    import  FormatUtils
from   dustStyle             import dustStyle
import dustGuiLib
import dustFrame

#============================ body ============================================

class dustFrameDC2126AConfiguration(dustFrame.dustFrame):
    
    def __init__(self,parentElem,guiLock,
            selectedMoteChangedCB,
            refreshButtonCB,
            getConfigurationCB,
            setConfigurationCB,
            frameName="Configuration",row=0,column=1):
        
        # record params
        self.selectedMoteChangedCB     = selectedMoteChangedCB
        self.refreshButtonCB           = refreshButtonCB
        self.getConfigurationCB        = getConfigurationCB
        self.setConfigurationCB        = setConfigurationCB
        
        # local variables
        self.selectedMote         = Tkinter.StringVar()
        self.selectedMote.trace("w",self._selectedMoteChangedCB_internal)
        
        # initialize parent
        dustFrame.dustFrame.__init__(self,
            parentElem,
            guiLock,
            frameName,
            row,column
        )
        
        # report period
        temp                      = dustGuiLib.Label(self.container,
            anchor                = Tkinter.NW,
            justify               = Tkinter.LEFT,
            text                  = 'Report Period (ms):',
        )
        self._add(temp,0,0)
        self.reportPeriod         = dustGuiLib.Text(self.container,
            font                  = dustStyle.FONT_BODY,
            width                 = 25,
            height                = 1,
        )
        self._add(self.reportPeriod,0,1)
        
        # bridge settling time
        temp                      = dustGuiLib.Label(self.container,
            anchor                = Tkinter.NW,
            justify               = Tkinter.LEFT,
            text                  = 'Bridge Settling Time (ms):',
        )
        self._add(temp,1,0)
        self.bridgeSettlingTime   = dustGuiLib.Text(self.container,
            font                  = dustStyle.FONT_BODY,
            width                 = 25,
            height                = 1,
        )
        self._add(self.bridgeSettlingTime,1,1)
        
        # LDO on time
        temp                      = dustGuiLib.Label(self.container,
            anchor                = Tkinter.NW,
            justify               = Tkinter.LEFT,
            text                  = 'LDO on time (ms):',
        )
        self._add(temp,2,0)
        self.ldoOnTime            = dustGuiLib.Text(
            self.container,
            font                  = dustStyle.FONT_BODY,
            width                 = 25,
            height                = 1,
        )
        self._add(self.ldoOnTime,2,1)
        
        # motes
        temp                      = dustGuiLib.Label(self.container,
            anchor                = Tkinter.NW,
            justify               = Tkinter.LEFT,
            text                  = 'Select mote:')
        self._add(temp,3,0)
        self.motes                = dustGuiLib.OptionMenu(
            self.container,
            self.selectedMote,
            *['']
        )
        self._add(self.motes,3,1)
        
        # refresh button
        self.refreshButton        = dustGuiLib.Button(self.container,
            text                  = 'refresh',
            command               = self.refreshButtonCB
        )
        self._add(self.refreshButton,3,2)
        
        # action label
        self.actionLabel          = dustGuiLib.Label(self.container,
            anchor                = Tkinter.CENTER,
            justify               = Tkinter.LEFT,
            text                  = '',
        )
        self._add(self.actionLabel,4,1)
        
        # get configuration button
        self.getConfigurationButton = dustGuiLib.Button(self.container,
            text                  = 'get configuration',
            command               = self.getConfigurationCB,
        )
        self._add(self.getConfigurationButton,4,2)
        
        # set configuration button
        self.setConfigurationButton = dustGuiLib.Button(self.container,
            text                  = 'set configuration',
            command               = self._setConfigurationCB_internal,
        )
        self._add(self.setConfigurationButton,5,2)
    
    #============================ public ======================================
    
    def displayConfiguration(self,reportPeriod,bridgeSettlingTime,ldoOnTime):
        
        with self.guiLock:
            # delete previous content
            self.reportPeriod.delete(1.0,Tkinter.END)
            self.bridgeSettlingTime.delete(1.0,Tkinter.END)
            self.ldoOnTime.delete(1.0,Tkinter.END)
            
            # clear color
            self.reportPeriod.configure(bg=dustStyle.COLOR_BG)
            self.bridgeSettlingTime.configure(bg=dustStyle.COLOR_BG)
            self.ldoOnTime.configure(bg=dustStyle.COLOR_BG)
            
            # insert new content
            self.reportPeriod.insert(1.0,str(reportPeriod))
            self.bridgeSettlingTime.insert(1.0,str(bridgeSettlingTime))
            self.ldoOnTime.insert(1.0,str(ldoOnTime))
    
    def disableButtons(self):
        
        with self.guiLock:
            self.refreshButton.configure(state=Tkinter.DISABLED)
            self.setConfigurationButton.configure(state=Tkinter.DISABLED)
            self.getConfigurationButton.configure(state=Tkinter.DISABLED)
            self.motes.configure(state=Tkinter.DISABLED)
    
    def enableButtons(self):
        
        with self.guiLock:
            self.refreshButton.configure(state=Tkinter.NORMAL)
            self.setConfigurationButton.configure(state=Tkinter.NORMAL)
            self.getConfigurationButton.configure(state=Tkinter.NORMAL)
            self.motes.configure(state=Tkinter.NORMAL)
    
    def refresh(self,macs):
        
        with self.guiLock:
            self.motes['menu'].delete(0, 'end')
            
            # format the MAC addresses into strings
            formattedMacs = [FormatUtils.formatMacString(mac) for mac in macs]
            
            # update the optionmenu
            for mac in formattedMacs:
                self.motes['menu'].add_command(
                    label   = mac,
                    command = Tkinter._setit(self.selectedMote,mac)
                )
            
            # update the selected mote, if pre
            previousSelectedMote = self.selectedMote.get()
            if (formattedMacs) and (previousSelectedMote not in formattedMacs):
                self.selectedMote.set(formattedMacs[0])
    
    def writeActionMsg(self,text):
        
        with self.guiLock:
            self.actionLabel.configure(text=text)
    
    #============================ private =====================================
    
    def _selectedMoteChangedCB_internal(self,*args):
        
        # get selected mote
        bytes = self.selectedMote.get().split('-')
        
        if len(bytes)==8:
            # convert
            selectedMote = [int(b,16) for b in self.selectedMote.get().split('-')]
            
            # indicate
            self.selectedMoteChangedCB(selectedMote)
    
    def _setConfigurationCB_internal(self):
        
        configuration = {}
        
        validConfiguration = True
        
        # read configuration from GUI
        for (var,guiElem) in [
            ('reportPeriod',      self.reportPeriod),
            ('bridgeSettlingTime',self.bridgeSettlingTime),
            ('ldoOnTime',         self.ldoOnTime),
        ]:
            try:
                configuration[var]          = int(guiElem.get(1.0,Tkinter.END).strip())
            except ValueError:
                guiElem.configure(bg=dustStyle.COLOR_ERROR)
                validConfiguration = False
            else:
                guiElem.configure(bg=dustStyle.COLOR_NOERROR)
        
        # call the callback
        if validConfiguration:
            self.setConfigurationCB(
                reportPeriod          = configuration['reportPeriod'],
                bridgeSettlingTime    = configuration['bridgeSettlingTime'],
                ldoOnTime             = configuration['ldoOnTime'],
            )
    
#============================ sample app =============================
# The following gets called only if you run this module as a 
# standalone app, by double-clicking on this source file. This code is 
# NOT executed when importing this module is a larger application
#
class exampleApp(object):
    
    ACTION_DELAY = 1.0 # in seconds
    
    def __init__(self):
        self.window  = dustWindow.dustWindow("dustFrameDC2126AConfiguration",
                                  self._closeCb)
        self.guiLock              = threading.Lock()
        self.frame = dustFrameDC2126AConfiguration(self.window,self.guiLock,
            selectedMoteChangedCB = self._selectedMoteChangedCB,
            refreshButtonCB       = self._refreshButtonCB,
            getConfigurationCB    = self._getConfigurationCB,
            setConfigurationCB    = self._setConfigurationCB,
            row=0,column=0
        )
        self.frame.show()
        self.window.mainloop()
    
    #===== GUI action callbacks
    
    def _selectedMoteChangedCB(self,mote):
        print "selected mote changed to {0}".format(mote)
    
    def _refreshButtonCB(self):
        print "refresh button pressed, scheduling action in {0}s".format(self.ACTION_DELAY)
        t = threading.Timer(self.ACTION_DELAY,self._refresh)
        t.start()
    
    def _setConfigurationCB(self,reportPeriod,bridgeSettlingTime,ldoOnTime):
        output  = []
        output += ["_setConfigurationCB called with "]
        output += ["- reportPeriod:       {0}".format(reportPeriod)]
        output += ["- bridgeSettlingTime: {0}".format(bridgeSettlingTime)]
        output += ["- ldoOnTime:          {0}".format(ldoOnTime)]
        output  = '\n'.join(output)
        
        print output
    
    def _getConfigurationCB(self):
        print "get configuration button pressed, scheduling action in {0}s".format(self.ACTION_DELAY)
        t = threading.Timer(self.ACTION_DELAY,self._displayConfiguration)
        t.start()
    
    def _closeCb(self):
        print " _closeCb called"
    
    #===== private
    
    def _refresh(self):
        print "Refreshing"
        self.frame.refresh(
            macs = [
                [0x11]*8,
                [0x22]*8,
                [0x33]*8,
            ]
        )
    
    def _displayConfiguration(self):
        print "Setting new configuration"
        self.frame.displayConfiguration(
            reportPeriod        = 10000,
            bridgeSettlingTime  = 20,
            ldoOnTime           = 100,
        )
    
if __name__ == '__main__':
    import threading
    import dustWindow
    exampleApp()
