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

from SmartMeshSDK.ApiDefinition import ApiDefinition
from SmartMeshSDK.ApiException  import CommandError

#============================ body ============================================

class dustFrameFields(dustFrame.dustFrame):
    
    def __init__(self,parentElem,guiLock,type,frameName="fields",row=0,column=0):
        
        # record variables
        self.type = type
        
        # init parent
        dustFrame.dustFrame.__init__(
            self,
            parentElem  = parentElem,
            guiLock     = guiLock,
            frameName   = frameName,
            row         = row,
            column      = column,
            scrollable  = True,
        )
        
        # row 0: headerLabel
        self.headerLabel = dustGuiLib.Label(
            self.container,
            text='',
        )
        self._add(self.headerLabel,0,0)
        
        # row 1: fieldsFrame
        self.fieldsFrame = Tkinter.Frame(self.container)
        self._add(self.fieldsFrame,1,0)
    
    #======================== public ==========================================
    
    def indicateFields(self,commandArray,fields):
        
        # write commandArray in the header label
        with self.guiLock:
            self.headerLabel.configure(text='.'.join(commandArray))
            self.headerLabel.configure(bg=dustStyle.COLOR_BG)
        
        # display the fields in the fieldsFrame
        self._displayFields(
            self.type,
            commandArray,
            fields,
        )
    
    def indicateError(self,errorText):
        
        # write APIError in the header label
        with self.guiLock:
            self.headerLabel.configure(text=str(errorText))
            self.headerLabel.configure(bg=dustStyle.COLOR_ERROR)
        
        # clear the GUI elems
        self._clearGuiElems()
    
    #======================== private =========================================
    
    def _displayFields(self,type,nameArray,fields):
        '''
        \brief Display a response or notification as GUI elements. If the fields
               contain a list of elements, each one is displayed as a separate
               line in the resulting table.
        
        \param type      Set to ApiDefinition.COMMAND when displaying a response, 
                         ApiDefinition.NOTIFICATION when displaying a notification.
        \param nameArray The name array of the response or notification received from
                         the connector.
        \param fields    The fields received from the connector.
        '''
        
        # clear the old elems
        self._clearGuiElems()
        
        # display information row by row
        if   isinstance(fields,dict):
            self._displayFieldsRow(
                rowNumber         = 0,
                isFirstRow        = True,
                isLastRow         = True,
                type              = type,
                nameArray         = nameArray,
                fields            = fields,
            )
        elif isinstance(fields,list):
            for rowNumber in range(len(fields)):
                self._displayFieldsRow(
                    rowNumber     = rowNumber,
                    isFirstRow    = (rowNumber==0),
                    isLastRow     = (rowNumber==len(fields)-1),
                    type          = type,
                    nameArray     = nameArray,
                    fields        = fields[rowNumber],
                )
        else:
            raise SystemError("fields expected to be a list of dictionary, {0} is not".format(fields))
    
    def _displayFieldsRow(self,rowNumber,isFirstRow,isLastRow,type,nameArray,fields):
        
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
        
        # add elements for fields
        for i in range(len(nameArray)):
            tempName = nameArray[:i+1]
            
            try:
                temp_fieldNames        =  self.apiDef.getResponseFieldNames(
                    type,
                    tempName
                )
                temp_fieldFormats      = [
                    self.apiDef.getResponseFieldFormat(
                        type,
                        tempName,
                        fieldName,
                    ) for fieldName in temp_fieldNames
                ]
                temp_fieldLengths      = [
                    self.apiDef.getResponseFieldLength(
                        type,
                        tempName,
                        fieldName,
                    ) for fieldName in temp_fieldNames
                ]
                temp_fieldOptions      = [
                    self.apiDef.getResponseFieldOptions(
                        type,
                        tempName,
                        fieldName,
                    ) for fieldName in temp_fieldNames
                ]
                
                c['fieldNames']       += temp_fieldNames
                c['fieldFormats']     += temp_fieldFormats
                c['fieldLengths']     += temp_fieldLengths
                c['fieldOptions']     += temp_fieldOptions
            
            except CommandError as err:
                print str(err)
                return
        
        # add values
        for i in range(len(c['fieldNames'])):
            fieldName = c['fieldNames'][i]
            try:
                fieldValue   = fields[fieldName]
            except KeyError:
                fieldValue   = "N.A."
                
            if c['fieldFormats'][i]=='hex':
                fieldString  = self._hexdata2string(fieldValue,0,len(fieldValue))
            elif fieldValue==None:
                fieldString  = 'missing'
            else:
                fieldString  = str(fieldValue)
            try:
                description  = self.apiDef.fieldValueToDesc(
                    type,
                    nameArray,
                    fieldName,
                    fieldValue,
                )
                fieldString  = fieldString+" ("+description+")"
            except CommandError as err:
                if err.errorCode!=CommandError.VALUE_NOT_IN_OPTIONS:
                    raise
            c['fieldValues'].append(fieldString)
        
        # display fields
        headercolor = self._getHeaderColor()
        with self.guiLock:
            for i in range(len(c['fieldNames'])):
                if c['fieldNames'][i] in ApiDefinition.ApiDefinition.RESERVED:
                    continue
                
                # row: name (add iff first row)
                if isFirstRow:
                    c['fieldNamesGui']     += [
                        dustGuiLib.Label(
                            self.fieldsFrame,
                            text            = c['fieldNames'][i],
                            bg              = dustStyle.COLOR_BG,
                            relief          = Tkinter.RIDGE,
                            borderwidth     = 1,
                            background      = headercolor,
                            padx            = 3,
                            pady            = 3,
                        )
                    ]
                    c['fieldNamesGui'][-1].grid(
                        row                 = 0,
                        column              = i,
                        sticky              = Tkinter.W+Tkinter.E,
                    )
                
                # row: value
                c['fieldValuesString'].append(None)
                c['fieldValuesGui']        += [
                    dustGuiLib.Label(
                        self.fieldsFrame,
                        text                = c['fieldValues'][i],
                        bg                  = dustStyle.COLOR_BG,
                        relief              = Tkinter.RIDGE,
                        borderwidth         = 1,
                        padx                = 3,
                        pady                = 3,
                    )
                ]
                c['fieldValuesGui'][-1].grid(
                    row                     = rowNumber+1,
                    column                  = i,
                    sticky                  = Tkinter.W+Tkinter.E
                )
                
                # row: add format and length (iff last row)
                if isLastRow:
                    fieldFormatsString      = ApiDefinition.ApiDefinition.fieldFormatToString(
                        c['fieldLengths'][i],
                        c['fieldFormats'][i]
                    )
                    c['fieldFormatsGui']   += [
                        dustGuiLib.Label(
                            self.fieldsFrame,
                            text            = fieldFormatsString,
                            bg              = dustStyle.COLOR_BG,
                            relief          = Tkinter.RIDGE,
                            borderwidth     = 1,
                            padx            = 3,
                            pady            = 3,
                        )
                    ]
                    c['fieldFormatsGui'][-1].grid(
                        row                 = rowNumber+2,
                        column              = i,
                        sticky              = Tkinter.W+Tkinter.E,
                    )
        
        # add to the guiElems
        self.guiElems.append(c)
    
    #======================== helpers =========================================

#============================ sample app ======================================
# The following gets called only if you run this module as a standalone app, by
# double-clicking on this source file. This code is NOT executed when importing
# this module is a larger application
#
class exampleApp(object):
    
    def __init__(self):
        raw_input("No sample app. Press enter to close.")

if __name__ == '__main__':
    exampleApp()