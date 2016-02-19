#!/usr/bin/python

#============================ adjust path =====================================

import sys
import os
if __name__ == '__main__':
    here = sys.path[0]
    sys.path.insert(0, os.path.join(here, '..'))

#============================ imports =========================================

import Tkinter

import dustGuiLib
import dustFrame
from   dustStyle import dustStyle

#============================ body ============================================

class SetOneValFrame(Tkinter.Frame):
    
    def __init__(self,container,lambda_factory,content,mac,handle_update_set,defaultVal):
        
        Tkinter.Frame.__init__(self,container)
        
        # text
        self.textElem = dustGuiLib.Text(self,width=15,height=1)
        self.textElem.insert(1.0, defaultVal)
        self.textElem.grid(row=0,column=0)
        
        # set button
        self.setButton = dustGuiLib.Button(
            self,
            command=lambda_factory(
                    handle_update_set,
                    (
                        mac,
                        self.textElem,
                        content['cb_set']
                    )
                ),
                text="set",
            )
        self.setButton.grid(row=0,column=1)
    
    def enable(self):
        self.textElem.configure(state=Tkinter.NORMAL)
        self.setButton.configure(state=Tkinter.NORMAL)
    
    def update(self,val):
        self.textElem.delete(1.0, Tkinter.END)
        self.textElem.insert(1.0, str(val))
        self.textElem.configure(bg=dustStyle.COLOR_BG)
    
    def disable(self):
        self.textElem.configure(state=Tkinter.DISABLED)
        self.setButton.configure(state=Tkinter.DISABLED)

class GetSetOneValFrame(Tkinter.Frame):
    
    def __init__(self,container,lambda_factory,content,mac,handle_update_set):
        
        Tkinter.Frame.__init__(self,container)
        
        # text
        self.textElem = dustGuiLib.Text(self,width=6,height=1)
        self.textElem.insert(1.0, '')
        self.textElem.grid(row=0,column=0)
        
        # get button
        self.getButton = dustGuiLib.Button(self,
                                           command=lambda_factory(
                                                content['cb_get'],
                                                (
                                                    mac,
                                                )
                                           ),
                                           text="get",)
        self.getButton.grid(row=0,column=1)
        
        # set button
        self.setButton = dustGuiLib.Button(self,
                                    command=lambda_factory(
                                            handle_update_set,
                                            (
                                                mac,
                                                self.textElem,
                                                content['min'],
                                                content['max'],
                                                content['cb_set']
                                            )
                                        ),
                                    text="set",)
        self.setButton.grid(row=0,column=2)
    
    def enable(self):
        self.textElem.configure(state=Tkinter.NORMAL)
        self.getButton.configure(state=Tkinter.NORMAL)
        self.setButton.configure(state=Tkinter.NORMAL)
    
    def update(self,val):
        self.textElem.delete(1.0, Tkinter.END)
        self.textElem.insert(1.0, str(val))
        self.textElem.configure(bg=dustStyle.COLOR_BG)
    
    def disable(self):
        self.textElem.configure(state=Tkinter.DISABLED)
        self.getButton.configure(state=Tkinter.DISABLED)
        self.setButton.configure(state=Tkinter.DISABLED)

class SetThreeValFrame(Tkinter.Frame):
    
    def __init__(self,container,lambda_factory,content,mac,handle_setThreeVal_set):
        
        # initialize parent class
        Tkinter.Frame.__init__(self,container)
        
        # text 1
        self.textElem1 = dustGuiLib.Text(self,width=6,height=1)
        self.textElem1.insert(1.0, '')
        self.textElem1.grid(row=0,column=0)
        
        # text 2
        self.textElem2 = dustGuiLib.Text(self,width=6,height=1)
        self.textElem2.insert(1.0, '')
        self.textElem2.grid(row=0,column=1)
        
        # text 3
        self.textElem3 = dustGuiLib.Text(self,width=6,height=1)
        self.textElem3.insert(1.0, '')
        self.textElem3.grid(row=0,column=2)
        
        # set button
        self.setButton = dustGuiLib.Button(self,
                                    command=lambda_factory(
                                            handle_setThreeVal_set,
                                            (
                                                mac,
                                                self.textElem1,
                                                self.textElem2,
                                                self.textElem3,
                                                content['min2'],
                                                content['max2'],
                                                content['min3'],
                                                content['max3'],
                                                content['cb_set']
                                            )
                                        ),
                                    text="set",)
        self.setButton.grid(row=0,column=3)
    
    def enable(self):
        self.textElem1.configure(state=Tkinter.NORMAL)
        self.textElem2.configure(state=Tkinter.NORMAL)
        self.textElem3.configure(state=Tkinter.NORMAL)
        self.setButton.configure(state=Tkinter.NORMAL)
    
    def update(self,(val1,val2,val3)):
        self.textElem1.delete(1.0, Tkinter.END)
        self.textElem1.insert(1.0, str(val1))
        self.textElem2.delete(1.0, Tkinter.END)
        self.textElem2.insert(1.0, str(val2))
        self.textElem3.delete(1.0, Tkinter.END)
        self.textElem3.insert(1.0, str(val3))
    
    def disable(self):
        self.textElem1.configure(state=Tkinter.DISABLED)
        self.textElem2.configure(state=Tkinter.DISABLED)
        self.textElem3.configure(state=Tkinter.DISABLED)
        self.setButton.configure(state=Tkinter.DISABLED)

class dustFrameMoteList(dustFrame.dustFrame):
    
    LABEL        = 'LABEL'
    ACTION       = 'ACTION'
    SETONEVAL    = 'SETONEVAL'
    GETSETONEVAL = 'GETSETONEVAL'
    SETTHREEVAL  = 'SETTHREEVAL'
    
    def __init__(self,parentElem,guiLock,columnDesc,frameName="mote list",row=0,column=0):
        
        # store params
        self.columnNames = [c['name'] for c in columnDesc]
        self.columntypes = [c['type'] for c in columnDesc]
        self.moteMacs    = []
        
        # local variables
        self.guiElems = []
        
        # init parent
        dustFrame.dustFrame.__init__(self,parentElem,guiLock,frameName,row,column,
                                          scrollable=True)
        
        # create the header row
        self._addHeaderRow(self.columnNames)
    
    #======================== public ==========================================
    
    def addMote(self,mac,columnvals):
        
        assert(len(columnvals.keys())==len(self.columnNames))
        for k in columnvals.keys():
            assert(k in self.columnNames)
        
        # mote might already be in moteMacs when reconnecting
        if mac not in self.moteMacs:
            self.moteMacs.append(mac)
        
        values = [columnvals[colname] for colname in self.columnNames]
        self._addDataRow(mac,values)
    
    def enableMote(self,mac):
        self._changeActiveMode(mac,True)
    
    def disableMote(self,mac):
        self._changeActiveMode(mac,False)
    
    def update(self,mac,columnname,columnval):
        
        row    = self._macToRowIndex(mac)
        column = self._columnNameToColumnIndex(columnname)
        
        if   type(columnval) is float:
            valString = "%.1f"%columnval
        elif type(columnval) in [tuple,list]:
            valString = '-'.join(["%.2x"%i for i in columnval])
        else:
            valString = str(columnval)
        
        try:
            self.guiElems[row][column].configure(text=valString)
            if self.guiElems[row][column].cget('bg')==dustStyle.COLOR_PRIMARY2:
                self.guiElems[row][column].configure(bg=dustStyle.COLOR_PRIMARY2_LIGHT)
            else:
                self.guiElems[row][column].configure(bg=dustStyle.COLOR_PRIMARY2)
        except Tkinter.TclError:
            self.guiElems[row][column].update(valString)
    
    def clearColors(self):
        for row in self.guiElems:
            for cell in row:
                cell.configure(bg=dustStyle.COLOR_BG)
    
    #======================== private =========================================
    
    def _changeActiveMode(self,mac,isActive):
        assert isActive in [True,False]
        
        try:
            row    = self._macToRowIndex(mac)
        except KeyError:
            # happens when MAC not in data
            return
        else:
            for column in range(len(self.guiElems[row])):
                try:
                    if isActive:
                        self.guiElems[row][column].configure(state=Tkinter.NORMAL)
                    else:
                        self.guiElems[row][column].configure(state=Tkinter.DISABLED)
                except Tkinter.TclError:
                    # happens when not a widget
                    if isActive:
                        self.guiElems[row][column].enable()
                    else:
                        self.guiElems[row][column].disable()
    
    def _addDataRow(self,mac,contents):
        self._addRowInternal(['-'.join(['%.2x'%b for b in mac])]+contents,
                             [self.LABEL]+self.columntypes,
                             mac)
    
    def _addHeaderRow(self,contents):
        self._addRowInternal(['mac']+contents,
                             [self.LABEL]+[self.LABEL for i in self.columntypes])
    
    def _addRowInternal(self,contents,coltypes,mac=None):
        
        assert(len(contents)==len(coltypes))
        
        self.guiElems.append([])
        for (content,type) in zip(contents,coltypes):
        
            if   type==self.LABEL:
                temp = dustGuiLib.Label(self.container,
                                     text=str(content),
                                     border=1,
                                     bg=dustStyle.COLOR_BG,
                                     relief=Tkinter.RIDGE,
                                     borderwidth=1,
                                     padx=3,
                                     pady=3)
            
            elif type==self.ACTION:
                temp = dustGuiLib.Button(self.container)
                temp.configure(text=content['text'])
                temp.configure(command=self._lambda_factory(content['callback'],(mac,temp)))
            
            elif type==self.SETONEVAL:
                if 'defaultVal' in content:
                    defaultVal = content['defaultVal']
                else:
                    defaultVal = ''
                temp = SetOneValFrame(self.container,
                                   self._lambda_factory,
                                   content,
                                   mac,
                                   self._handle_setOneVal_set,
                                   defaultVal)
            
            elif type==self.GETSETONEVAL:
                temp = GetSetOneValFrame(self.container,
                                   self._lambda_factory,
                                   content,
                                   mac,
                                   self._handle_getSetOneVal_set)
            
            elif type==self.SETTHREEVAL:
                temp = SetThreeValFrame(self.container,
                                   self._lambda_factory,
                                   content,
                                   mac,
                                   self._handle_setThreeVal_set)
            
            else:
                raise SystemError("column type {0} unsupported".format(type))
            
            self._add(temp,len(self.guiElems)-1,
                           len(self.guiElems[-1]),
                           sticky=Tkinter.W+Tkinter.E)
            self.guiElems[-1].append(temp)
    
    def _handle_setOneVal_set(self,mac,textField,cb):
        
        # retrieve value from text field
        with self.guiLock:
            val = textField.get(1.0,Tkinter.END)
        
        # if you get here, value is accepted
        with self.guiLock:
            textField.configure(bg=dustStyle.COLOR_NOERROR)
        
        # call the callback
        cb(mac,val)
    
    def _handle_getSetOneVal_set(self,mac,textField,min,max,cb):
        
        # retrieve value from text field
        self.guiLock.acquire()
        valString = textField.get(1.0,Tkinter.END)
        self.guiLock.release()
        
        # convert to int
        try:
           val = int(valString)
        except ValueError:
            self.guiLock.acquire()
            textField.configure(bg=dustStyle.COLOR_ERROR)
            self.guiLock.release()
            return
        
        # check boundaries
        if val<min or val>max:
            self.guiLock.acquire()
            textField.configure(bg=dustStyle.COLOR_WARNING_FORMATTING)
            self.guiLock.release()
            return
        
        # if you get here, value is accepted
        self.guiLock.acquire()
        textField.configure(bg=dustStyle.COLOR_NOERROR)
        self.guiLock.release()
        
        # call callback
        cb(mac,val)
    
    def _handle_setThreeVal_set(self,mac,textField1,textField2,textField3,min2,max2,min3,max3,cb):
        
        # retrieve value from text fields
        self.guiLock.acquire()
        valString1 = textField1.get(1.0,Tkinter.END)
        self.guiLock.release()

        self.guiLock.acquire()
        valString2 = textField2.get(1.0,Tkinter.END)
        self.guiLock.release()

        self.guiLock.acquire()
        valString3 = textField3.get(1.0,Tkinter.END)
        self.guiLock.release()
        
        # convert to ints
        try:
            val1 = int(valString1)
        except ValueError:
            self.guiLock.acquire()
            textField1.configure(bg=dustStyle.COLOR_ERROR)
            self.guiLock.release()
            return

        try:
            val2 = int(valString2)
        except ValueError:
            self.guiLock.acquire()
            textField2.configure(bg=dustStyle.COLOR_ERROR)
            self.guiLock.release()
            return

        try:
            val3 = int(valString3)
        except ValueError:
            self.guiLock.acquire()
            textField3.configure(bg=dustStyle.COLOR_ERROR)
            self.guiLock.release()
            return
        
        # check boundaries
        if val2<min2 or val2>max2:
            self.guiLock.acquire()
            textField2.configure(bg=dustStyle.COLOR_WARNING_FORMATTING)
            self.guiLock.release()
            return
            
        if val3<min3 or val3>max3:
            self.guiLock.acquire()
            textField3.configure(bg=dustStyle.COLOR_WARNING_FORMATTING)
            self.guiLock.release()
            return
        
        # if you get here, values are accepted
        
        self.guiLock.acquire()
        textField1.configure(bg=dustStyle.COLOR_NOERROR)
        self.guiLock.release()
        
        self.guiLock.acquire()
        textField2.configure(bg=dustStyle.COLOR_NOERROR)
        self.guiLock.release()
        
        self.guiLock.acquire()
        textField3.configure(bg=dustStyle.COLOR_NOERROR)
        self.guiLock.release()
        
        # call callback
        cb(mac,(val1,val2,val3))
    
    def _lambda_factory(self,fun,param):
        return lambda:fun(*param)
    
    def _macToRowIndex(self,mac):
        i     = 0
        for i in range(len(self.moteMacs)):
            if self.moteMacs[i]==tuple(mac):
                return i+1 # row 0 is used for the heading
        raise KeyError('mac {0} not present in table'.format(mac))
    
    def _columnNameToColumnIndex(self,columnname):
        i     = 0
        for i in range(len(self.columnNames)):
            if self.columnNames[i]==columnname:
                return i+1 # column 0 is used for the MAC address
        raise KeyError('no columnname {0} in table'.format(columnname))
    
    #======================== helpers =========================================

#============================ sample app ======================================
# The following gets called only if you run this module as a standalone app, by
# double-clicking on this source file. This code is NOT executed when importing
# this module is a larger application
#
class exampleApp(object):
    
    def __init__(self):
        columnnames = [
            {
                'name'  : 'state',
                'type'  : dustFrameMoteList.LABEL,
            },
            {
                'name'  : 'numDataRx',
                'type'  : dustFrameMoteList.LABEL,
            },
            {
                'name'  : 'numIpRx',
                'type'  : dustFrameMoteList.LABEL,
            },
            {
                'name'  : 'toggle led',
                'type'  : dustFrameMoteList.ACTION,
            },
            {
                'name'  : 'rate',
                'type'  : dustFrameMoteList.GETSETONEVAL,
            },
            {
                'name'  : 'pkgen (num/rate/size)',
                'type'  : dustFrameMoteList.SETTHREEVAL,
            },
            {
                'name'  : 'key',
                'type'  : dustFrameMoteList.SETONEVAL,
            },
        ]
        macMote1    = (0x00,0x17,0x0d,0x00,0x00,0x38,0x11,0x11)
        macMote2    = (0x00,0x17,0x0d,0x00,0x00,0x38,0x22,0x22)
    
        self.window  = dustWindow(
            "dustFrameMoteList",
            self._closeCb,
        )
        self.guiLock    = threading.Lock()
        self.frame      = dustFrameMoteList(
            self.window,
            self.guiLock,
            columnnames,
            row=0,column=0,
        )
        self.frame.show()
        
        self.frame.addMote(
            macMote1,
            { 
                'state':          'operational',
                'numDataRx':      100,
                'numIpRx':        70,
                'toggle led': {
                    'text':       'ON',
                    'callback':   self._toggleLedCb,
                },
                'rate': {
                    'min':        1000,
                    'max':        60000,
                    'cb_get':     self._rateCbGet,
                    'cb_set':     self._rateCbSet,
                },
                'pkgen (num/rate/size)': {
                    'min2':       1000,
                    'max2':       60000,
                    'min3':       0,
                    'max3':       90,
                    'cb_set':     self._pkgenCbSet,
                },
                'key': {
                    'cb_set':     self._keyCbSet,
                }
            }
      )
        
        self.frame.addMote(
            macMote2,
            { 
                'state':          'searching',
                'numDataRx':      0,
                'numIpRx':        0,
                'toggle led': {
                    'text':       'ON',
                    'callback':   self._toggleLedCb,
                },
                'rate': {
                    'min':        1000,
                    'max':        60000,
                    'cb_get':     self._rateCbGet,
                    'cb_set':     self._rateCbSet,
                },
                'pkgen (num/rate/size)': {
                    'min2':       16,
                    'max2':       60000,
                    'min3':       0,
                    'max3':       90,
                    'cb_set':     self._pkgenCbSet,
                },
                'key': {
                    'cb_set':     self._keyCbSet,
                }
            }
        )
        
        for i in range(3,40):
            self.frame.addMote(
                tuple([random.randint(0,255) for i in range(8)]),
                { 
                    'state':      'searching',
                    'numDataRx':  0,
                    'numIpRx':    0,
                    'toggle led': {
                        'text':        'ON',
                        'callback':    self._toggleLedCb,
                    },
                    'rate': {
                        'min':         1000,
                        'max':         60000,
                        'cb_get':      self._rateCbGet,
                        'cb_set':      self._rateCbSet,
                    },
                    'pkgen (num/rate/size)': {
                        'min2':        16,
                        'max2':        60000,
                        'min3':        0,
                        'max3':        90,
                        'cb_set':      self._pkgenCbSet,
                    },
                    'key': {
                        'cb_set':     self._keyCbSet,
                    }
                }
            )
        
        self.frame.update(macMote1,'numDataRx',            200)
        self.frame.update(macMote1,'numIpRx',              600)
        self.frame.update(macMote1,'rate',                 3000)
        
        self.frame.disableMote(macMote1)
        self.frame.disableMote(macMote2)
        self.frame.enableMote(macMote1)
        
        self.window.mainloop()
    
    def _toggleLedCb(self,mac,button):
        print " _buttonCb for mac {0}".format('-'.join(['%.2x'%c for c in mac]))
        
        if button.cget('text')=='ON':
           button.configure(text="OFF")
        else:
           button.configure(text="ON")
    
    def _rateCbGet(self,mac):
        print " _rateCbGet for mac {0}".format(
                                    '-'.join(['%.2x'%c for c in mac])
                                )
    
    def _rateCbSet(self,mac,val):
        print " _rateCbSet for mac {0}, value={1}".format(
                                    '-'.join(['%.2x'%c for c in mac]),
                                    val
                                )
    def _pkgenCbSet(self,mac,val1,val2,val3):
        print " _pkgenCbSet for mac {0}, value1={1} value2={2} value3={3}".format(
                                    '-'.join(['%.2x'%c for c in mac]),
                                    val1,
                                    val2,
                                    val3
                                )
    
    def _keyCbSet(self,mac,value):
        print " _keyCbSet for mac={0} value={1}".format(
            '-'.join(['%.2x'%c for c in mac]),
            value
        )
    
    def _closeCb(self):
        print " _closeCb called"

if __name__ == '__main__':
    import threading
    import random
    from dustWindow import dustWindow
    exampleApp()
