import sys
import tkinter
import threading
from .dustStyle import dustStyle
from builtins import input

class GuiFactory(object):
    
    #======================== singleton pattern ===============================
    
    _instance = None
    _init     = False
    
    def __new__(cls, *args, **kwargs):
        if not cls._instance:
            cls._instance = super(GuiFactory,cls).__new__(cls, *args, **kwargs)
        return cls._instance
    
    def __init__(self):
        # don't re-initialize an instance (needed because singleton)
        if self._init:
            return
        self._init = True
        
        self.dataLock   = threading.Lock()
        self.recycleBin = []
    
    #======================== return pattern ==================================
    
    def recycle(self,elem):
        
        with self.dataLock:
            self.recycleBin += [elem]
    
    def getRecycled(self,typeWanted):
        
        # try to find a recycles element
        with self.dataLock:
            for i in range(len(self.recycleBin)):
                if type(self.recycleBin[i])==typeWanted:
                    returnVal = self.recycleBin.pop(i)
                    return returnVal
    
class FactoryElem(object):
    
    def removeGui(self):
        self.grid_forget()
        GuiFactory().recycle(self)

class Button(FactoryElem,tkinter.Button):
    
    def __init__(self,*args,**kwargs):
        
        # initialize the parent classes
        FactoryElem.__init__(self)
        tkinter.Button.__init__(self,*args,**kwargs)
    
class OptionMenu(FactoryElem,tkinter.OptionMenu):
    
    def __init__(self,*args,**kwargs):
        
        # initialize the parent classes
        FactoryElem.__init__(self)
        tkinter.OptionMenu.__init__(self,*args,**kwargs)

class Text(FactoryElem,tkinter.Text):
    
    BLINK_ITERATIONS = 2
    BLINK_PERIOD_MS  = 50
    RESIZE_PERIOD    = 100
    
    def __init__(self,*args,**kwargs):
        
        # store the class' parameters
        try:
            self.returnAction = kwargs['returnAction']
        except KeyError:
            self.returnAction = None
        else:
            del kwargs['returnAction']
        try:
            self.autoResize = kwargs['autoResize']
        except KeyError:
            self.autoResize = False
        else:
            del kwargs['autoResize']
        
        # initialize the parent classes
        FactoryElem.__init__(self)
        tkinter.Text.__init__(self,*args,**kwargs)
        
        # local variables
        self.blinkIterationsRemaining = 0
        self.blinkActive              = False
        self.blinkDefaultColor        = self.cget("bg")
        
        # have pressing Tab move focus on the next field, not write \t
        self.bind('<Tab>',        self._focusNext)
        self.bind('<Shift-Tab>',  self._focusPrevious)
        
        # have a return (pressing the Enter key) call a function, not write \n
        self.bind('<Return>',     self._returnPressed)
        
        # have right-clicking paste the contents to the clipboard
        self.bind('<Button-3>',   self._pasteClipboard)
        
        # resize the field to it content
        if self.autoResize:
            self.after(self.RESIZE_PERIOD,self._autoResize)
    
    #======================== public ==========================================
    
    #======================== private =========================================
    
    def _returnPressed(self,event):
        if self.returnAction:
            self.returnAction()
        return 'break'
    
    def _focusNext(self,event):
        self.tk_focusNext().focus_set()
        return 'break'
    
    def _focusPrevious(self,event):
        self.tk_focusPrev().focus_set()
        return 'break'
    
    def _pasteClipboard(self,event):
        try:
            self.insert(tkinter.CURRENT,self.clipboard_get().replace('-',''))
            self._blink()
        except tkinter.TclError:
            # can happen if not pasting a text
            pass
    
    def _autoResize(self):
    
        # determine the new width
        newwidth = len(self.get(1.0,tkinter.END))+2
        if   newwidth>dustStyle.TEXTFIELD_ENTRY_LENGTH_MAX:
            newwidth=dustStyle.TEXTFIELD_ENTRY_LENGTH_MAX
        elif newwidth<dustStyle.TEXTFIELD_ENTRY_LENGTH_DEFAULT:
            newwidth=dustStyle.TEXTFIELD_ENTRY_LENGTH_DEFAULT
        
        # apply new width
        self.configure(width=newwidth)
        
        # schedule next resize event
        if self.autoResize:
            self.after(self.RESIZE_PERIOD,self._autoResize)
    
    def _blink(self):
        if not self.blinkIterationsRemaining:
            self.blinkDefaultColor        = self.cget("bg")
            self.blinkIterationsRemaining = self.BLINK_ITERATIONS
            self._blinkIteration()
    
    def _blinkIteration(self):
        
        # change the state of the label
        if self.blinkIterationsRemaining:
            if self.blinkActive:
                self.configure(bg=self.blinkDefaultColor)
                self.blinkActive = False
                self.blinkIterationsRemaining -= 1
            else:
                self.configure(bg=dustStyle.COLOR_PRIMARY2_LIGHT)
                self.blinkActive = True
        
        # arm next iteration
        if self.blinkIterationsRemaining:
            self.after(self.BLINK_PERIOD_MS,self._blinkIteration)
    
class Label(FactoryElem,tkinter.Label):
    
    BLINK_ITERATIONS    = 2
    BLINK_PERIOD_MS     = 50
    
    def __new__(cls, *args, **kwargs):
        returnVal = GuiFactory().getRecycled(cls)
        if not returnVal:
            returnVal = super(Label,cls).__new__(cls)
        return returnVal
    
    def __init__(self,*args,**kwargs):
        
        # initialize the parent classes
        FactoryElem.__init__(self)
        tkinter.Label.__init__(self,*args,**kwargs)
        
        # have right-clicking copy the contents to the clipboard
        self.unbind('<Button-3>')
        self.bind(  '<Button-3>', self._copyClipboard)
        
        # local variables
        self.blinkIterationsRemaining = 0
        self.blinkActive              = False
        self.blinkDefaultColor        = self.cget("bg")
        
    #======================== public ==========================================
    
    #======================== private =========================================
    
    def _copyClipboard(self,event):
        self.clipboard_clear()
        self.clipboard_append(self.cget("text"))
        self._blink()
    
    def _blink(self):
        if not self.blinkIterationsRemaining:
            self.blinkDefaultColor        = self.cget("bg")
            self.blinkIterationsRemaining = self.BLINK_ITERATIONS
            self._blinkIteration()
    
    def _blinkIteration(self):
        
        # change the state of the label
        if self.blinkIterationsRemaining:
            if self.blinkActive:
                self.configure(bg=self.blinkDefaultColor)
                self.blinkActive = False
                self.blinkIterationsRemaining -= 1
            else:
                self.configure(bg=dustStyle.COLOR_PRIMARY2_LIGHT)
                self.blinkActive = True
        
        # arm next iteration
        if self.blinkIterationsRemaining:
            self.after(self.BLINK_PERIOD_MS,self._blinkIteration)

#============================ sample app ======================================
# The following gets called only if you run this module as a standalone app, by
# double-clicking on this source file. This code is NOT executed when importing
# this module is a larger application
#
class exampleApp(object):
    
    def __init__(self):
        input("No sample app. Press enter to close.")

if __name__ == '__main__':
    exampleApp()