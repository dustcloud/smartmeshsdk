import sys
import os
sys.path.insert(0, os.path.join(sys.path[0], '..'))

from   ApiDefinition.IpMgrDefinition    import IpMgrDefinition
from   ApiDefinition.IpMoteDefinition   import IpMoteDefinition
#from   ApiDefinition.HartMgrDefinition  import HartMgrDefinition
#from   ApiDefinition.HartMoteDefinition import HartMoteDefinition

import ApiException

#============================ templates =======================================

#===== doc

TMPL_DOC_HEADER = '''<?xml version="1.0" encoding="UTF-8"?>
<book xmlns="http://docbook.org/ns/docbook" xmlns:xlink="http://www.w3.org/1999/xlink" xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance" xsi:schemaLocation="http://docbook.org/ns/docbook http://docbook.org/xml/5.0/xsd/docbook.xsd" version="5.0" >
<info>
<title>{DEVICE_NAME} API Guide</title>
</info>
'''

TMPL_DOC_FOOTER = '''</book>
'''

#===== commands

TMPL_COMMANDS_HEADER = '''
<chapter>
<title>Commands</title>
'''

TMPL_COMMANDS_FOOTER = '''</chapter>
'''

TMPL_ONE_COMMAND = '''<section>
<title>{CMD_NAME}</title>
<para><emphasis role="strong">Description</emphasis></para>
<para>
{CMD_DESCRIPTION}
</para>
<para><emphasis role="strong">Request</emphasis></para>
<para>
{CMD_REQUEST}
</para>
<para><emphasis role="strong">Response</emphasis></para>
<para>
{CMD_RESPONSE}
</para>
</section>
'''

TMPL_FIELDS = '''<informaltable>
<colgroup>
</colgroup>
<thead>
<tr>
<td rowspan="1" colspan="1">
<para>Parameter</para>
</td>
<td rowspan="1" colspan="1">
<para>Length</para>
</td>
<td rowspan="1" colspan="1">
<para>Format</para>
</td>
</tr>
</thead>
<tbody>
{FIELDS}</tbody>
</informaltable>
'''

TMPL_ONE_FIELD = '''<tr>
<td rowspan="1" colspan="1">
<para>{FIELD_NAME}</para>
</td>
<td rowspan="1" colspan="1">
<para>{FIELD_LENGTH}</para>
</td>
<td rowspan="1" colspan="1">
<para>{FIELD_FORMAT}</para>
</td>
</tr>
<tr>
<td rowspan="1" colspan="3">
{FIELD_OPTIONS}
</td>
</tr>
'''

TMPL_OPTIONS_YES = '''<para>This field can only take one of the following values:</para>
<informaltable>
<colgroup>
</colgroup>
<thead>
<tr>
<td rowspan="1" colspan="1">
<para>Value</para>
</td>
<td rowspan="1" colspan="1">
<para>Description</para>
</td>
</tr>
</thead>
<tbody>
{OPTIONS}</tbody>
</informaltable>
'''

TMPL_OPTIONS_NO = '''<para>There is no restriction on the value of this field.</para>
'''

TMPL_ONE_OPTION = '''<tr>
<td rowspan="1" colspan="1">
<para>{OPTION_VALUE}</para>
</td>
<td rowspan="1" colspan="1">
<para>{OPTION_DESCRIPTION}</para>
</td>
</tr>
'''

#===== notifications

TMPL_NOTIFICATIONS_HEADER = '''
<chapter>
<title>Notifications</title>
'''

TMPL_NOTIFICATIONS_FOOTER = '''</chapter>
'''

class GenApiDocbook(object):
   
    #======================== public ==========================================
    
    def __init__(self,apiDef,deviceName,outputFileName=None):
        self.apiDef          = apiDef
        self.deviceName      = deviceName
        if outputFileName :
            self.outFile     = open(outputFileName, "wt")
        else :
            self.outFile     = sys.stdout
            
    def gen(self):
        self.genStartOutput()
        self.genCommands()
        self.genNotifications()
        self.genEndOutput()
        
    #======================== private =========================================
    
    STRING_NONE = '<emphasis role="italics">none</emphasis>'
    REQUEST     = 'request'
    RESPONSE    = 'response'
    
    #===== start
    
    def genStartOutput(self):
        s = TMPL_DOC_HEADER.format(DEVICE_NAME = self.deviceName)
        self.outFile.write(s)
    
    #===== commands
    
    def genCommands(self):
        
        # header
        s = TMPL_COMMANDS_HEADER.format()
        self.outFile.write(s)
        
        # body
        cmdNames = self.apiDef.getNames(self.apiDef.COMMAND)
        for name in cmdNames :
            self.genOneCommand([name], [], [])
        
        # footer
        s = TMPL_COMMANDS_FOOTER.format()
        self.outFile.write(s)
    
    def genOneCommand(self, nameArray, responseFieldsName, requestFieldsName):
        
        # get request fields
        r = self.apiDef.getRequestFieldNames(nameArray)
        requestFieldsName += [n for n in r if n not in self.apiDef.RESERVED]
        
        # get response fields
        try:
            r = self.apiDef.getResponseFieldNames(self.apiDef.COMMAND, nameArray) 
            responseFieldsName += [n for n in r if n not in self.apiDef.RESERVED]
        except (ApiException.CommandError) as err:
            # means that this function has no response fields, which is OK
            pass
        
        if self.apiDef.hasSubcommands(self.apiDef.COMMAND, nameArray):
            subcmdsName = self.apiDef.getNames(self.apiDef.COMMAND, nameArray)
            for sn in subcmdsName :
                self.genOneCommand(nameArray+[sn],
                                   responseFieldsName[:],
                                   requestFieldsName[:])
        else:
            nameString     = '.'.join(nameArray)
            descString     = self.apiDef.getDescription(self.apiDef.COMMAND, nameArray)
            if not descString:
                descString = self.STRING_NONE
            requestString  = self.genFields(self.apiDef.COMMAND,
                                            self.REQUEST,
                                            nameArray,
                                            requestFieldsName)
            responseString = self.genFields(self.apiDef.COMMAND,
                                            self.RESPONSE,
                                            nameArray,
                                            responseFieldsName)
            s = TMPL_ONE_COMMAND.format(CMD_NAME        = nameString,
                                        CMD_DESCRIPTION = descString,
                                        CMD_REQUEST     = requestString,
                                        CMD_RESPONSE    = responseString)
            self.outFile.write(s)
    
    #===== notifications
    
    def genNotifications(self):
        
        # header
        s = TMPL_NOTIFICATIONS_HEADER.format()
        self.outFile.write(s)
        
        # body
        notifNames = self.apiDef.getNames(self.apiDef.NOTIFICATION)
        for notifName in notifNames:
            self.genOneNotification([notifName], [])
        # footer
        s = TMPL_NOTIFICATIONS_FOOTER.format()
        self.outFile.write(s)
    
    def genOneNotification(self, nameArray, responseFieldsName):
        
        # get response fields
        try:
            r = self.apiDef.getResponseFieldNames(self.apiDef.NOTIFICATION,nameArray) 
            responseFieldsName += [n for n in r if n not in self.apiDef.RESERVED]
        except (ApiException.CommandError) as err:
            # means that this function has no response fields, which is NOT OK
            raise
            pass
        
        if self.apiDef.hasSubcommands(self.apiDef.NOTIFICATION, nameArray):
            subcmdsName = self.apiDef.getNames(self.apiDef.NOTIFICATION, nameArray)
            for sn in subcmdsName :
                self.genOneNotification(nameArray+[sn],
                                        responseFieldsName[:])
        else:
            nameString     = '.'.join(nameArray)
            descString     = self.apiDef.getDescription(self.apiDef.NOTIFICATION, nameArray)
            if not descString:
                descString = self.STRING_NONE
            responseString = self.genFields(self.apiDef.NOTIFICATION,
                                            self.RESPONSE,
                                            nameArray,
                                            responseFieldsName)
            s = TMPL_ONE_COMMAND.format(CMD_NAME        = nameString,
                                        CMD_DESCRIPTION = descString,
                                        CMD_REQUEST     = "N.A.",
                                        CMD_RESPONSE    = responseString)
            self.outFile.write(s)
    
    #===== end
    
    def genEndOutput(self):
        s = TMPL_DOC_FOOTER.format()
        self.outFile.write(s)
        if self.outFile != sys.stdout :
            self.outFile.close()
    
    #======================== helpers =========================================
    
    #===== fields
    
    def genFields(self,listType,fieldType,nameArray,fieldNames):
        fieldsString = ''
        if fieldNames:
            for fieldName in fieldNames:
                fieldsString += self.genOneField(listType,fieldType,nameArray,fieldName)
            s = TMPL_FIELDS.format(FIELDS = fieldsString)
        else:
            s = self.STRING_NONE
        return s
        
    def genOneField(self,listType,fieldType,nameArray,fieldName):
        if fieldType==self.REQUEST:
            length  = self.apiDef.getRequestFieldLength(nameArray,fieldName)
            format  = self.apiDef.getRequestFieldFormat(nameArray,fieldName)
            options = self.apiDef.getRequestFieldOptions(nameArray,fieldName)
        else:
            length  = self.apiDef.getResponseFieldLength(listType,nameArray,fieldName)
            format  = self.apiDef.getResponseFieldFormat(listType,nameArray,fieldName)
            options = self.apiDef.getResponseFieldOptions(listType,nameArray,fieldName)
        optionsString = self.genOptions(options)
        s = TMPL_ONE_FIELD.format(FIELD_NAME    = fieldName,
                                  FIELD_LENGTH  = length,
                                  FIELD_FORMAT  = format,
                                  FIELD_OPTIONS = optionsString)
        return s
    
    #===== options
    
    def genOptions(self,options):
        optionValues       = options.validOptions
        optionDescriptions = options.optionDescs
        if optionValues:
            optionsString = ''
            for i in range(len(optionValues)):
                optionsString += self.genOneOption(optionValues[i],
                                                   optionDescriptions[i])
            s = TMPL_OPTIONS_YES.format(OPTIONS = optionsString)
        else:
            s = TMPL_OPTIONS_NO.format()
        return s
        
    def genOneOption(self,optionValue,optionDescription):
        s = TMPL_ONE_OPTION.format(OPTION_VALUE       = optionValue,
                                   OPTION_DESCRIPTION = optionDescription)
        return s
        
def main() :
    # generate IP manager API gude
    apiDef  = IpMgrDefinition()
    gen     = GenApiDocbook(apiDef,  "SmartMesh IP manager",
                                     "../doc/docbook/IpMgrApi.xml")
    gen.gen()
    
    # generate IP mote API guide
    apiDef  = IpMoteDefinition()
    gen     = GenApiDocbook(apiDef,  "SmartMesh IP mote",
                                     "../doc/docbook/IpMoteApi.xml")
    gen.gen()
    
    '''
    # generate HART manager API guide
    apiDef  = HartMgrDefinition()
    gen     = GenApiDocbook(apiDef,  "SmartMesh WirelessHART manager",
                                     "../doc/docbook/HartMgrApi.xml")
    gen.gen()
    
    # generate HART mote API guide
    apiDef  = HartMoteDefinition()
    gen     = GenApiDocbook(apiDef,  "SmartMesh WirelessHART mpte",
                                     "../doc/docbook/HartMoteApi.xml")
    gen.gen()
    '''
    
if __name__ == '__main__':
    main()

