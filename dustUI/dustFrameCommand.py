#!/usr/bin/python

#============================ adjust path =====================================

import sys
import os
if __name__ == '__main__':
    here = sys.path[0]
    sys.path.insert(0, os.path.join(here, '..'))

#============================ imports =========================================

import Tkinter
import traceback

import dustGuiLib
import dustFrame
from   dustStyle import dustStyle

from   SmartMeshSDK.ApiDefinition import ApiDefinition
from   SmartMeshSDK.ApiException  import CommandError, \
                                         ConnectionError, \
                                         APIError

#============================ body ============================================

class dustFrameCommand(dustFrame.dustFrame):
    
    def __init__(self,parentElem,guiLock,
                                 selectedCb,responseCb,responseErrorCb,
                                 frameName="command",
                                 row=0,column=0):
        
        # record variables
        self.selectedCb      = selectedCb
        self.responseCb      = responseCb
        self.responseErrorCb = responseErrorCb
        self.fieldsFrame     = None
        
        # init parent
        dustFrame.dustFrame.__init__(self,parentElem,guiLock,frameName,row,column,scrollable=True)
    
    #======================== public ==========================================
    
    def apiLoaded(self,apiDef):
        # call the parent's apiLoaded function
        dustFrame.dustFrame.apiLoaded(self,apiDef)
        
        self.guiLock.acquire()
        self.commandToSend = Tkinter.StringVar()
        self.commandToSend.trace_variable('w',self._handleCommandSelected)
        self.guiLock.release()
        
        self.guiLock.acquire()
        self.subcommandToSend = Tkinter.StringVar()
        self.subcommandToSend.trace_variable('w',self._handleSubCommandSelected)
        self.guiLock.release()
        
        self.commandDropDownOptions = self.apiDef.getNames(ApiDefinition.ApiDefinition.COMMAND)
        self.commandDropDownOptions.sort()
        
        # remove command we don't want to appear in drop-down menu
        for itemToRemove in ['hello', 'hello_response','mux_hello']:
            try:
                self.commandDropDownOptions.remove(itemToRemove)
            except ValueError:
                # happens when item does not appear in list
                pass
        
        self.guiLock.acquire()
        self.commandDropDown = dustGuiLib.OptionMenu(self.container,
                                                     self.commandToSend,
                                                     *self.commandDropDownOptions)
        self._add(self.commandDropDown,0,0)
        self.guiLock.release()
    
    #======================== private =========================================
    
    def _handleCommandSelected(self,name,index,mode):
        '''
        \brief Called when an item is selected from the drop-down list of
               commands.
        
        \param name  Unused.
        \param index Unused.
        \param mode  Unused.
        '''
        self._handleCommand(0)

    def _handleSubCommandSelected(self,name,index,mode):
        '''
        \brief Called when an item is selected from the drop-down list of
               subcommands.
        
        \param name  Unused.
        \param index Unused.
        \param mode  Unused.
        '''
        self._handleCommand(1)
        
    def _handleCommand(self,level):
        '''
        \brief Generic handler when item is selected from drop-down list of (sub)commands.
        
        \param level 0 indicates a command was selected. 1 indicates a subcommand was selected.
        '''
        
        # clear the old guiElems
        self._clearGuiElems(level)
        if self.fieldsFrame:
            self.fieldsFrame.grid_forget()
            self.fieldsFrame = None
        
        c = {
                'commandName'         : None,
                'fieldNames'          : [],
                'fieldNamesGui'       : [],
                'fieldFormats'        : [],
                'fieldFormatsGui'     : [],
                'fieldLengths'        : [],
                'fieldOptions'        : [],
                'fieldValuesGui'      : [],
                'fieldValuesString'   : [],
                'fieldValuesRaw'      : [],
                'fieldValues'         : [],
                'commandORbuttonGui'  : None,
            }
        
        # read the command name just selected
        self.guiLock.acquire()
        if   level==0: 
            c['commandName'] = self.commandToSend.get()
        elif level==1:
            c['commandName'] = self.subcommandToSend.get()
        self.guiLock.release()
        
        fullCmd = [elem['commandName'] for elem in self.guiElems]
        fullCmd.append(c['commandName'])
        
        # call the selected callback
        self.selectedCb(fullCmd)
        
        # add elements for fields
        try:
            c['fieldNames']   =  self.apiDef.getRequestFieldNames(fullCmd)
            c['fieldFormats'] = [self.apiDef.getRequestFieldFormat(fullCmd,fieldName)
                                    for fieldName in c['fieldNames']]
            c['fieldLengths'] = [self.apiDef.getRequestFieldLength(fullCmd,fieldName)
                                    for fieldName in c['fieldNames']]
            c['fieldOptions'] = [self.apiDef.getRequestFieldOptions(fullCmd,fieldName)
                                    for fieldName in c['fieldNames']]
        except CommandError as err:
            traceback.print_exc()
            return
            
        # create a frame for all fields and add GUI elements
        self.guiLock.acquire()
        self.fieldsFrame = Tkinter.Frame(self.container,
                                  borderwidth=10,
                                  bg=dustStyle.COLOR_BG)
        self._add(self.fieldsFrame,level*2+2,column=0)
        self.guiLock.release()
        
        headerColor = self._getHeaderColor()
        
        self.guiLock.acquire()
        for i in range(len(c['fieldNames'])):
            if c['fieldNames'][i] in ApiDefinition.ApiDefinition.RESERVED:
                continue
                
            # calculate width of text entry
            
            if c['fieldLengths'][i]:
                if   c['fieldFormats'][i] in [ApiDefinition.FieldFormats.STRING]:
                    textEntryWidth = c['fieldLengths'][i]+2
                elif c['fieldFormats'][i] in [ApiDefinition.FieldFormats.HEXDATA]:
                    textEntryWidth = c['fieldLengths'][i]*2+2
                else:
                    textEntryWidth = dustStyle.TEXTFIELD_ENTRY_LENGTH_DEFAULT
                autoResize = False
            else:
                textEntryWidth = dustStyle.TEXTFIELD_ENTRY_LENGTH_DEFAULT
                autoResize = True
            
            if textEntryWidth>dustStyle.TEXTFIELD_ENTRY_LENGTH_MAX:
                textEntryWidth = dustStyle.TEXTFIELD_ENTRY_LENGTH_MAX
                
            # display row 0: name
            c['fieldNamesGui'].append(dustGuiLib.Label(
                self.fieldsFrame,
                text=c['fieldNames'][i],
                bg=dustStyle.COLOR_BG,
                relief=Tkinter.RIDGE,
                borderwidth=1,
                background=headerColor,
                padx=3,
                pady=3))
            c['fieldNamesGui'][-1].grid(row=0,column=i,
                sticky=Tkinter.W+Tkinter.E)
            
            # display row 1: value
            if c['fieldOptions'][i].optionDescs or c['fieldFormats'][i]=='bool':
                if c['fieldOptions'][i].optionDescs:
                    optionValues = c['fieldOptions'][i].optionDescs
                else:
                    optionValues = ['True','False']
                c['fieldValuesString'].append(Tkinter.StringVar())
                c['fieldValuesGui'].append(dustGuiLib.OptionMenu(self.fieldsFrame, c['fieldValuesString'][-1],*optionValues))
            else:
                c['fieldValuesString'].append(None)
                c['fieldValuesGui'].append(dustGuiLib.Text(
                    self.fieldsFrame,
                    font=dustStyle.FONT_BODY,
                    width=textEntryWidth,
                    height=1,
                    padx=3,
                    pady=3,
                    autoResize=autoResize))
            c['fieldValuesGui'][-1].grid(row=1,column=i,
                sticky=Tkinter.W+Tkinter.E)
            
            # display row 2: format and length
            fieldFormatsString = ApiDefinition.ApiDefinition.fieldFormatToString(
                c['fieldLengths'][i],
                c['fieldFormats'][i]
            )
            c['fieldFormatsGui'].append(dustGuiLib.Label(
                self.fieldsFrame,
                text=fieldFormatsString,
                bg=dustStyle.COLOR_BG,
                relief=Tkinter.RIDGE,
                borderwidth=1,
                padx=3,
                pady=3))
            c['fieldFormatsGui'][-1].grid(row=2,column=i,
                sticky=Tkinter.W+Tkinter.E)
        self.guiLock.release()
        
        # subcommands
        self.guiLock.acquire()
        tempOptions = None
        if self.apiDef.hasSubcommands(ApiDefinition.ApiDefinition.COMMAND,
                                 fullCmd)==True:
            tempOptions = self.apiDef.getNames(ApiDefinition.ApiDefinition.COMMAND,
                                          fullCmd)
            tempOptions.sort()
            c['commandORbuttonGui'] = dustGuiLib.OptionMenu(self.container,
                                                            self.subcommandToSend,
                                                            *tempOptions)
        else:
            c['commandORbuttonGui'] = dustGuiLib.Button(self.container,
                                                        command=self._handleSend,
                                                        text="send",)
        self._add(c['commandORbuttonGui'],level*2+2+1,0)
        self.guiLock.release()
        
        # add to guiElems
        self.guiElems.append(c)
        
        # display the first alphabetical subcommand in subcommand option menu
        if tempOptions:
            self.subcommandToSend.set(tempOptions[0])
    
    def _handleSend(self):
        '''
        \brief Called when 'send' button is clicked.
        '''
        
        # collect data from fields, put in c['fieldValuesRaw']
        self.guiLock.acquire()
        for c in self.guiElems:
            c['fieldValuesRaw'] = []
            for i in range(len(c['fieldNames'])):
                if c['fieldNames'][i] in ApiDefinition.ApiDefinition.RESERVED:
                    continue
                if c['fieldValuesString'][i]:
                    c['fieldValuesRaw'].append(c['fieldValuesString'][i].get())
                else:
                    c['fieldValuesRaw'].append(c['fieldValuesGui'][i].get(1.0,Tkinter.END).rstrip('\n'))
        self.guiLock.release()
        
        # turn c['fieldValuesRaw'] into c['fieldValues'] (also check for length)
        self.guiLock.acquire()
        for c in self.guiElems:
            c['fieldValues'] = []
            for i in range(len(c['fieldNames'])):
                if c['fieldNames'][i] in ApiDefinition.ApiDefinition.RESERVED:
                    continue
                try:
                    c['fieldValues'].append(self._rawToValue(
                                                c['fieldValuesRaw'][i],
                                                c['fieldFormats'][i],
                                                c['fieldLengths'][i],
                                                c['fieldOptions'][i]))
                except (ValueError,OverflowError):
                    c['fieldValuesGui'][i].configure(bg=dustStyle.COLOR_WARNING_FORMATTING)
                    self.guiLock.release()
                    return
                else:
                    c['fieldValuesGui'][i].configure(bg=dustStyle.COLOR_NOERROR)
        self.guiLock.release()
        
        # assemble data into variables for send() command
        commandArray = []
        fields       = {}
        for c in self.guiElems:
            commandArray.append(c['commandName'])
            for i in range(len(c['fieldNames'])):
                if c['fieldNames'][i] in ApiDefinition.ApiDefinition.RESERVED:
                    continue
                fields[c['fieldNames'][i]] = c['fieldValues'][i]

        #print 'Ready to send', commandArray, fields
        
        # call send command
        try:
            responseFields = self.connector.send(commandArray,fields)
        except CommandError as err:
            self.responseErrorCb(str(err))
            errorField = err.details
            for c in self.guiElems:
                for i in range(len(c['fieldNames'])): 
                    if c['fieldNames'][i] == errorField:
                        self.guiLock.acquire()
                        c['fieldValuesGui'][i].configure(bg=dustStyle.COLOR_ERROR)
                        self.guiLock.release()
        except AttributeError as err:
            self.responseErrorCb('Not connected')
        except (ConnectionError,APIError) as err:
            self.responseErrorCb(str(err))
        else:
            self.responseCb(commandArray,responseFields)
    
    #======================== helpers =========================================
    
    def _rawToValue(self,raw,format,length,options):
        '''
        \brief convert a raw value entered by the user into a value useable by the 
               connector.
        
        This function converts the data according to the format passed, and checks
        the resulting length.
        
        \param raw     The raw value, as read from the TkInter GUI element.
        \param format  The format of the resulting field.
        \param length  The length of the resulting field.
        \param options The options of the resulting field.
        
        \exception ValueError    The raw value can not be converted into that format.
        \exception OverflowError The raw value is not the expected size.
        \returns The converted value, in the format specified by format.
        '''
        returnVal = None

        if options.validOptions:
            # raw is one of options.optionDescs
            
            # return validOptions
            for i in range(len(options.optionDescs)):
                if options.optionDescs[i]==raw:
                    returnVal = options.validOptions[i]
                    break
            
            if returnVal==None:
                raise ValueError
        
        else:
        
            if   format=='string':
                
                # convert from unicode to string
                returnVal = str(raw)
                
                # check for length
                if length!=None:
                    if len(raw)>length:
                        raise OverflowError
                
            elif format=='bool':
                
                # convert
                if   raw=='True':
                    returnVal = True
                elif raw=='False':
                    returnVal = False
                else:
                    raise ValueError
                
            elif (format=='int' or format=='ints'):
                
                if not raw:
                    raise ValueError
                
                # convert
                try:
                    returnVal = int(raw)
                except:
                    raise ValueError
                    
                # check for length
                if length!=None:
                    if returnVal>=pow(2,8*length):
                        raise OverflowError
                
            elif format=='hex':
                
                # convert
                returnVal = []
                raw = ''.join( raw.split(" ") )
                if len(raw)%2!=0:
                    raise ValueError
                try:
                    for i in range(0, len(raw), 2):
                        returnVal.append( int(raw[i:i+2],16) )
                except ValueError:
                    raise ValueError
                
                # check for length
                if length!=None:  
                    if len(returnVal)!=length:
                        raise OverflowError
                
            else:
                raise SystemError('unknown field format='+format)

        return returnVal

#============================ sample app ======================================
# The following gets called only if you run this module as a standalone app, by
# double-clicking on this source file. This code is NOT executed when importing
# this module is a larger application
#
class exampleApp(object):
    
    def __init__(self):
        self.window  = dustWindow("dustFrameCommand",
                                  self._closeCb)
        self.guiLock            = threading.Lock()
        self.frame = dustFrameCommand(
                                self.window,
                                self.guiLock,
                                self._selectedCb,
                                self._responseCb,
                                self._responseErrorCb,
                                row=0,column=0)
        self.apidef = IpMoteDefinition.IpMoteDefinition()
        self.frame.apiLoaded(self.apidef)
        self.frame.show()
        self.window.mainloop()
    
    def _closeCb(self):
        print " _closeCb called"
    def _selectedCb(self,param):
        print " _selectedCb called with param="+str(param)
    def _responseCb(self):
        print " _responseCb called"
    def _responseErrorCb(self,param):
        print " _responseErrorCb called with param="+str(param)

if __name__ == '__main__':
    import threading
    from dustWindow import dustWindow
    from SmartMeshSDK.ApiDefinition import IpMoteDefinition
    exampleApp()
