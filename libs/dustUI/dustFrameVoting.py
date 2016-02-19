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

PRESENTERMOTE_FILE      = 'presenterMote.txt'

#============================ body ============================================

class dustFrameVoting(dustFrame.dustFrame):
    
    MAX_BAR_VAL         = 100
    PERCENTAGE          = True
    
    WIDTH               = 800
    HEIGHT              = 600
    BAR_PADDING_TOP     = 100
    BAR_PADDING_BOTTOM  = 50
    QUESTIONBOX_OFFS    = 10
    QUESTIONBOX_SIDE    = 60
    
    BAR_WIDTH           = 100
    
    BAR_A               = 'A'
    BAR_B               = 'B'
    BAR_C               = 'C'
    BAR_D               = 'D'
    BAR_ALL             = [
        BAR_A,
        BAR_B,
        BAR_C,
        BAR_D,
    ]
    
    COLOR_BAR_A         = '#FFCC00'
    COLOR_BAR_B         = '#66FF66'
    COLOR_BAR_C         = '#FF0000'
    COLOR_BAR_D         = '#66CCFF'
    COLOR_QUESTIONBOX   = '#00FFFF'
    
    PRESENTERMOTE_DFLT  = 'none selected'
    
    votingFont          = ("Times", "24", "bold")
    
    def __init__(self,parentElem,guiLock,nextQuestionCb=None,presenterChangedCb=None,scanCb=None,frameName="voting",row=0,column=0):
        
        # record variables
        self.nextQuestionCb       = nextQuestionCb
        self.presenterChangedCb   = presenterChangedCb
        self.scanCb               = scanCb
        
        # init parent
        dustFrame.dustFrame.__init__(self,parentElem,guiLock,frameName,row,column)
        
        #===== header row
        self.headerRow      = Tkinter.Frame(self.container)
        self._add(self.headerRow,0,0,sticky=Tkinter.E)
        
        self.buttonNextQuestion   = Tkinter.Button(
            self.headerRow,
            text             = 'next question',
            command          = self._nextQuestion,
        )
        self.buttonNextQuestion.grid(
            row              = 0,
            column           = 0,
        )
        
        temp = Tkinter.Label(self.headerRow,text='presenter mote:')
        temp.grid(
            row              = 0,
            column           = 2,
        )
        
        self.networkMotes    = (self._getInitPresenterMote(),)
        self.presenterMote   = Tkinter.StringVar(self.container)
        self.presenterMote.trace('w',self._presenterChanged)
        self.presenterMote.set(self.networkMotes[0])
        self.moteDropDown    = Tkinter.OptionMenu(
            self.headerRow,
            self.presenterMote,
            *self.networkMotes
        )
        self.moteDropDown.grid(
            row              = 0,
            column           = 3,
        )
        
        self.buttonScan = Tkinter.Button(
            self.headerRow,
            text             = 'scan',
            command          = self._scan,
        )
        self.buttonScan.grid(
            row              = 0,
            column           = 4,
        )
        
        #===== canvas
        self.canvas = Tkinter.Canvas(
            self.container,
            width            = self.WIDTH,
            height           = self.HEIGHT,
        )
        self._add(self.canvas,1,0)
        
        # questionNum
        self.questionNumBox  = self.canvas.create_oval(*self._questionNumBoxCoords(),fill=self.COLOR_QUESTIONBOX)
        self.questionNum     = self.canvas.create_text(*self._questionNumCoords(),font=self.votingFont)
        
        # bars
        self.bar = {}
        for (name,color) in [
                (self.BAR_A,self.COLOR_BAR_A),
                (self.BAR_B,self.COLOR_BAR_B),
                (self.BAR_C,self.COLOR_BAR_C),
                (self.BAR_D,self.COLOR_BAR_D),
            ]:
            self.bar[name]   = self.canvas.create_rectangle(*self._barCoords(name,0), fill=color)
        
        # barNames
        self.barName = {}
        for name in self.BAR_ALL:
            (x,y) = self._barNamePosition(name)
            self.barName[name] = self.canvas.create_text(x,y,text=name,font=self.votingFont)
        
        # barVal
        self.barVal = {}
        for name in self.BAR_ALL:
            val   = 0
            (x,y) = self._barValPosition(name,val)
            self.barVal[name] = self.canvas.create_text(x,y,text=str(val),font=self.votingFont)
        
        # firstMAC
        self.firstMAC = {}
        for name in self.BAR_ALL:
            (x,y) = self._firstMacPosition(name)
            self.firstMAC[name] = self.canvas.create_text(x,y,font=self.votingFont)
    
    #======================== public ==========================================
    
    def loadData(self,newData):
        
        # update questionNum
        self.canvas.itemconfig(self.questionNum,text=str(newData['questionNum']))
        
        # update bar (heights)
        for b in self.BAR_ALL:
            self.canvas.coords(self.bar[b],*self._barCoords(b,newData['numVotes'][b]))
        
        # update barVal
        for b in self.BAR_ALL:
            val    = newData['numVotes'][b]
            (x,y)  = self._barValPosition(b,val)
            self.canvas.coords(self.barVal[b],x,y)
            if self.PERCENTAGE:
                valSum       = sum([v for (k,v) in newData['numVotes'].items()])
                if valSum>0:
                    val      = int(round(100*float(val)/float(valSum)))
                else:
                    val      = 0
                valString    = '{0}%'.format(val)
            else:
                valString    = str(val)
            self.canvas.itemconfig(self.barVal[b],text=valString)
        
        # update firstMAC
        for b in self.BAR_ALL:
            mac              = newData['firstMACs'][b]
            if mac==None:
                macString    = ''
            else:
                macString    = self._formatMac(mac)
            self.canvas.itemconfig(self.firstMAC[b],text=macString)
            thisFont = self.votingFont
            if mac==newData['firstMAC']:
                thisFont = tuple(list(thisFont)+['underline'])
            self.canvas.itemconfig(self.firstMAC[b],font=thisFont)
    
    def loadNetworkMotes(self,networkMotes):
        
        # abort if not motes reported
        if not networkMotes:
            return
        
        # convert to tuple of strings
        newMotes = [FormatUtils.formatMacString(m) for m in networkMotes]
        
        # sort
        newMotes = sorted(newMotes)
        
        # turn into tuple
        newMotes = tuple(newMotes)
        
        if newMotes!=self.networkMotes:
            
            # remember last selection
            lastSelection     = self.presenterMote.get()
            
            # record new options
            self.networkMotes = newMotes
            
            # delete old options
            self.moteDropDown['menu'].delete(0, 'end')
            
            # load new options
            for mote in self.networkMotes :
                self.moteDropDown['menu'].add_command(
                    label=mote, 
                    command=Tkinter._setit(
                        self.presenterMote,
                        mote,
                    )
                )
            
            # load option to select none
            self.moteDropDown['menu'].add_command(
                label=self.PRESENTERMOTE_DFLT, 
                command=Tkinter._setit(
                    self.presenterMote,
                    self.PRESENTERMOTE_DFLT,
                )
            )
            
            # change selection, if needed
            if not self.networkMotes or (lastSelection not in self.networkMotes):
                if lastSelection!=self.PRESENTERMOTE_DFLT:
                    self.presenterMote.set(self.PRESENTERMOTE_DFLT)
    
    #======================== private =========================================
    
    def _getInitPresenterMote(self):
        returnVal = self.PRESENTERMOTE_DFLT
        try:
            with open(PRESENTERMOTE_FILE,'r') as f:
                returnVal = f.readline()
        except IOError:
            pass
        return returnVal
    
    def _nextQuestion(self):
        if self.nextQuestionCb:
            self.nextQuestionCb()
    
    def _presenterChanged(self,*args):
        if self.presenterChangedCb:
            newPresenterMote = self.presenterMote.get()
            
            self.presenterChangedCb(newPresenterMote) 
            
            with open(PRESENTERMOTE_FILE,'w') as f:
                f.write(newPresenterMote)
    
    def _scan(self):
        if self.scanCb:
            self.scanCb()
    
    def _questionNumCoords(self):
        (x_ul,y_ul,x_lr,y_lr) = self._questionNumBoxCoords()
        x = (x_ul+x_lr)/2
        y = (y_ul+y_lr)/2
        return (x,y)
    
    def _questionNumBoxCoords(self):
        x_ul = self.QUESTIONBOX_OFFS
        y_ul = self.QUESTIONBOX_OFFS
        x_lr = self.QUESTIONBOX_OFFS+self.QUESTIONBOX_SIDE
        y_lr = self.QUESTIONBOX_OFFS+self.QUESTIONBOX_SIDE
        return (x_ul,y_ul,x_lr,y_lr)
    
    def _barX(self,bar):
        return self.WIDTH/5*(self.BAR_ALL.index(bar)+1)
    
    def _barCoords(self,bar,val):
        
        x_bar      = self._barX(bar)
        
        height     = self.HEIGHT-self.BAR_PADDING_TOP-self.BAR_PADDING_BOTTOM
        height    *= float(val)/float(self.MAX_BAR_VAL)
        
        x_ul       = x_bar-self.BAR_WIDTH/2
        y_ul       = self.HEIGHT-self.BAR_PADDING_BOTTOM-height
        x_lr       = x_bar+self.BAR_WIDTH/2
        y_lr       = self.HEIGHT-self.BAR_PADDING_BOTTOM
        
        return (x_ul, y_ul, x_lr, y_lr)
    
    def _barNamePosition(self,bar):
        x = self._barX(bar)
        y = self.HEIGHT-self.BAR_PADDING_BOTTOM/2
        return (x,y)
    
    def _barValPosition(self,bar,val):
        (x_ul, y_ul, x_lr, y_lr) = self._barCoords(bar,val)
        x = self._barX(bar)
        y = y_ul-self.BAR_PADDING_TOP/4
        return (x,y)
    
    def _firstMacPosition(self,bar):
        x = self._barX(bar)
        y = 0.25*self.BAR_PADDING_TOP
        return (x,y)
    
    def _formatMac(self,mac):
        return ''.join(["%.2X"%i for i in mac[5:]])

#============================ sample app ======================================
# The following gets called only if you run this module as a standalone app, by
# double-clicking on this source file. This code is NOT executed when importing
# this module is a larger application
#

class exampleApp(object):
    
    GUIUPDATEPERIOD = 1000 # ms
    ALLMOTES        = [tuple([i]*8) for i in range(100)]
    
    def __init__(self):
        self.loadCycle            = 0
        self.window               = dustWindow("voting",self._closeCb)
        self.guiLock              = threading.Lock()
        self.frameVoting          = dustFrameVoting(
            self.window,
            self.guiLock,
            nextQuestionCb        = self._nextQuestionCb,
            presenterChangedCb    = self._presenterChangedCb,
            scanCb                = self._scanCb,
            row                   = 0,
            column                = 0,
        )
        self.frameVoting.show()
        
        self.frameVoting.after(self.GUIUPDATEPERIOD,self._updateData)
        
        self.window.mainloop()
    
    def _nextQuestionCb(self):
        print 'next question clicked!'
    
    def _presenterChangedCb(self,newPresenter):
        print 'changed presenter to {0}!'.format(newPresenter)
    
    def _scanCb(self):
        print 'scan clicked!'
    
    def _updateData(self):
        
        self.loadCycle = (self.loadCycle+1)%10
        
        # load data
        motes = self._randomMotes()
        newData = {
            'questionNum':        random.choice(range(0,500,49)),
            'numVotes': {
                'A':              random.randint(0,100),
                'B':              random.randint(0,100),
                'C':              random.randint(0,100),
                'D':              random.randint(0,100),
            },
            'firstMACs': {
                'A':              motes[0],
                'B':              motes[1],
                'C':              motes[2],
                'D':              motes[3],
            },
        }
        newData['firstMAC'] =     random.choice([v for (k,v) in newData['firstMACs'].items()])
        self.frameVoting.loadData(newData)
        
        # load motes
        self.frameVoting.loadNetworkMotes(self.ALLMOTES[:self.loadCycle+1])
        
        # trigger next update
        self.frameVoting.after(self.GUIUPDATEPERIOD,self._updateData)
    
    def _randomMotes(self):
        return random.sample(
            self.ALLMOTES,
            4,
        )
    
    def _closeCb(self):
        pass

if __name__ == '__main__':
    import random
    from dustWindow import dustWindow
    exampleApp()
