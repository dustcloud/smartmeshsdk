#!/usr/bin/python

import types
from SmartMeshSDK.ApiException import CommandError

import logging
class NullHandler(logging.Handler):
    def emit(self, record):
        pass
log = logging.getLogger('ApiDefinition')
log.setLevel(logging.ERROR)
log.addHandler(NullHandler())

class FieldFormats(object):
    '''
    \brief Enumeration of possible field formats.
    '''
    STRING              = 'string'
    BOOL                = 'bool'
    INT                 = 'int'
    INTS                = 'ints'
    HEXDATA             = 'hex'
    HEXDATA_VL          = 'hex_vl'      # variable length
    FLOAT               = 'float'
    ARRAY               = 'array'

class FieldOptions(object):
    '''
    \brief Possible options for a command field
    '''
    
    optionName     = None
    validOptions   = None
    optionDescs    = None
    
    def __init__(self,optionsDef,fieldOptions,fieldName):
        self.optionDescs = []
        if   not optionsDef:
            self.validOptions = None
        else:
            if optionsDef==True:
                self.optionName = fieldName
            else:
                self.optionName = optionsDef
            self.validOptions = []
            for i in fieldOptions[self.optionName]:
                self.validOptions.append(i[0])
                self.optionDescs.append(i[1])
    
    def isValidValue(self,val):
        if (
            (not self.validOptions)   or
            (val in self.validOptions)
           ):
            return True
        return False
    
    def valueToDesc(self,val):
        if self.validOptions:
            for i in range(len(self.validOptions)):
                if self.validOptions[i]==val:
                    return self.optionDescs[i]
        raise CommandError(CommandError.VALUE_NOT_IN_OPTIONS,
                           'option='+str(self.optionName)+' val='+str(val))

class Field(object):
    '''
    \brief Object representing one field of a command.
    '''
    
    def __init__(self,fieldDef,fieldOptions):
        self.name       = fieldDef[0]
        self.format     = fieldDef[1]
        self.length     = fieldDef[2]
        self.options    = FieldOptions(fieldDef[3],fieldOptions,self.name)
    
    def isValidValue(self,val):
        # check format and length
        if   self.format==FieldFormats.STRING:
            if ( (type(val) not in [bytes,str]) or
                 len(val)>self.length
               ):
                return False
        elif self.format==FieldFormats.BOOL:
            if type(val)!=bool:
                return False
        elif self.format==FieldFormats.INT:
            if ( (type(val)!=int and  type(val)!=int)  or
                 val>pow(2,8*self.length)
               ):
                return False
        elif self.format==FieldFormats.INTS:
            if ( (type(val)!=int and  type(val)!=int)  or
                 val>(pow(2,8*self.length)/2) or
                 val<(-pow(2,8*self.length)/2)
               ):
                return False
        elif self.format==FieldFormats.HEXDATA:
            if type(val)!=list and type(val)!=tuple:
                return False
            if self.length and len(val)>self.length:
                return False
            for i in val:
                if type(i)!=int:
                    return False
                if i>=pow(2,8):
                    return False
        elif self.format==FieldFormats.FLOAT:
            if ( (type(val)!=int and type(val)!=float) ):
                return False
        else:
            raise SystemError('unknown field format='+self.format)
        
        # check options
        if self.options.isValidValue(val)==False:
            return False
        
        return True

class ApiDefinition(object):
    '''
    \ingroup ApiDefinition
    
    \brief Base class for all API definitions objects.
    '''
    
    RC           = 'RC'
    SUBID1       = '_subId1'
    SUBID2       = '_subId2'
    RESERVED     = [SUBID1,SUBID2,'magic']
    OPTIONAL     = []
    COMMAND      = 'command'
    NOTIFICATION = 'notification'
    RC_OK        = 0
    
    #======================== id and name =====================================
    def __init__(self, array2scalar = True) :
        if array2scalar :
            self._array2scalar(self.commands)
            self._array2scalar(self.notifications)
    
    def _array2scalar(self, defs) :
        '''
        \brief Convert ARRAY to list of scalars
        '''
        for fields in defs:
            if 'subCommands' in fields :
                self._array2scalar(fields['subCommands'])
            if 'response' in fields and 'FIELDS' in fields['response'] :
                arrays = [f for f in fields['response']['FIELDS'] if f[1] == FieldFormats.ARRAY]
                for array in arrays :
                    scalars = []
                    for n in range(array[2]) :
                        for item in array[3] :
                            name = '{}_{}'.format(item[0], n+1)
                            scalars.append([name] + item[1:])
                    fields['response']['FIELDS'].remove(array)
                    fields['response']['FIELDS'] += scalars
    
    def idToName(self,type,id):
        '''
        \brief Translate a command or notification ID into a command name.
       
        \exception CommandError.INVALID_COMMAND Command does
                   not exist
        \returns The command name.
        '''
        list = self._getList(type)
        for item in list:
            if item['id']==id:
                return item['name']
        raise CommandError(CommandError.INVALID_COMMAND,
                           'id=%s' % str(id))
    
    def nameToId(self,type,nameArray):
        '''
        \brief Translate a command or notification name into a command ID.
       
        \exception CommandError.INVALID_COMMAND Command does
                   not exist
        \returns The command ID.
        '''
        list = self._getList(type)
        for item in list:
            if item['name']==nameArray[0]:
                return item['id']
        raise CommandError(CommandError.INVALID_COMMAND,
                                        nameArray[0])
    
    def rcToLabel(self,rc):
        '''
        \brief Translate a return code (RC) into its label, i.e. 'RC_OK' for 0x00.
        
        \param rc A return code, an int.
        
        \exception CommandError If RC does not exist.
        
        \returns The label for this RC, a string.
        '''
        
        # get the RC description
        rcLabel       = None
        for r in self.fieldOptions[self.RC]:
            if r[0]==rc:
                rcLabel           = r[1]
                break
        if not rcLabel:
            raise CommandError(CommandError.VALUE_NOT_IN_OPTIONS,
                               'rc={0} does not exist'.format(rc))
        
        return rcLabel
    
    def rcToDescription(self,rc,nameArray):
        '''
        \brief Translate a return code (RC) into a description.
       
        If this RC is described in the API definition for thise nameArray, then
        that description is returned. If not, the generic description of that
        RC is returned, preceeded by the string "[generic]".
        
        \param rc A return code, an int.
        
        \exception CommandError.VALUE_NOT_IN_OPTIONS if rc not in generic RC's.
        \returns The description for this RC, a string.
        '''
        
        returnVal = ''
        
        # get the RC description
        rcLabel       = None
        rcGenericDesc = None
        for r in self.fieldOptions[self.RC]:
            if r[0]==rc:
                rcLabel           = r[1]
                rcGenericDesc     = r[2]
                break
        if not rcLabel:
            raise CommandError(CommandError.VALUE_NOT_IN_OPTIONS,
                               'rc={0} does not exist'.format(rc))
        
        # retrieve rcDescription
        definition = self.getDefinition(self.COMMAND,nameArray)
        try:
            returnVal = definition['responseCodes'][rcLabel]
        except KeyError:
            returnVal = '[generic] {0}'.format(rcGenericDesc)
        
        return returnVal
    
    def getIds(self,type):
        '''
        \brief Get the list of command IDs this API defines
       
        \returns A array of numbers, each numbers representing a command ID
        '''
        list = self._getList(type)
        return [item['id'] for item in list]
    
    def getNames(self,type,nameArray=None):
        '''
        \brief Get the list of (sub)command names this API defines
       
        \param type         Type of definition to be looked up 
                            Supported values are: COMMAND or NOTIFICATION
        
        \param nameArray    Optional, used only when accessing names of
                            subcommands. Specifies the name of the command we
                            want the subcommand names for.
       
        \returns A array of strings, each string representing the name of a
                 command
        '''
        list = self._getList(type)
        definition  = None
        if nameArray:
            definition,list = self._commandIterator(nameArray,list)
        if not list:
            raise CommandError(CommandError.INVALID_COMMAND,
                                            '.'.join(nameArray)) 
        return [command['name'] for command in list]
    
    def getDefinition(self,type,nameArray):
        '''
        \brief Get the complete definition of a (sub)command, from its name.
        
        \param type           Type of definition to be looked up 
                              Supported values are: COMMAND or NOTIFICATION
        
        \param nameArray   An array of the form [commandName, subCommandname]
                              The array can be of any length, and is of length 1
                              if no subcommands are used.
       
        \exception CommandError(INVALID_COMMAND) The (sub)command
                   does not exist.
        \returns The definition of a (sub)command, represented as a dictionary.
        '''
        list = self._getList(type)
        definition  = None
        definition,list = self._commandIterator(nameArray,list)
        return definition
        
    def getDescription(self,type,nameArray):
        '''
        \brief Get the description of a command.
       
        \param type           Type of definition to be looked up 
                              Supported values are: COMMAND or NOTIFICATION
        
        \param nameArray      An array of the form [commandName, subCommandname]
                              The array can be of any length, and is of length 1
                              if no subcommands are used.
       
        \exception CommandError(INVALID_COMMAND) The (sub)command
                   does not exist.
        \returns The description of a (sub)command, represented as a dictionary.
                 '' if no description
        '''
        definition = self.getDefinition(type,nameArray)
        return definition['description']
    
    def hasSubcommands(self,type,nameArray):
        return 'subCommands' in self.getDefinition(type,nameArray)
    
    def subcommandIdToName(self,type,nameArray,id):
        subcommands = self.getSubcommands(type,nameArray)
        for subcommand in subcommands:
            if subcommand['id']==id:
                return subcommand['name']
        raise CommandError(CommandError.UNKNOWN_SUBCOMMAND,
                                            str(id))
    
    def subcommandNameToId(self,type,nameArray,name):
        subcommands = self.getSubcommands(type,nameArray)
        for subcommand in subcommands:
            if subcommand['name']==name:
                return subcommand['id']
        raise CommandError(CommandError.UNKNOWN_SUBCOMMAND,
                                            str(name))
    
    def getSubcommands(self,type,nameArray):
        definition = self.getDefinition(type,nameArray)
        if not 'subCommands' in definition:
            raise CommandError(CommandError.NO_SUBCOMMANDS,
                                            '.'.join(nameArray))
        return definition['subCommands']
    
    def _getList(self,type):
        if   type==self.COMMAND:
            list = self.commands
        elif type==self.NOTIFICATION:
            list = self.notifications
        else:
            raise ValueError("type="+str(type)+" unsupported")
        return list
    
    def _commandIterator(self,nameArray,list):
        for commandName in nameArray:
            if not list:
                raise CommandError(CommandError.INVALID_COMMAND,
                                            '.'.join(nameArray))
            found = False
            for elem in list:
                if elem['name']==commandName:
                    found       = True
                    definition  = elem
                    if 'subCommands' in elem:
                        list = definition['subCommands']
                    else:
                        list = None
                    break
            if found==False:
                raise CommandError(CommandError.INVALID_COMMAND,
                                            '.'.join(nameArray))
        return definition,list
    
    def getRequestFieldNames(self,commandArray):
        '''
        \brief Get the request fields of a (sub)command, from its name.
        
        \param commandArray   An array of the form [commandName, subCommandname]
                              The array can be of any length, and is of length 1
                              if no subcommands are used.
       
        \exception CommandError(NO_REQUEST) The (sub)command has
                   no request fields.
        \returns The list of request fields.
        '''
        fields = self.getRequestFields(commandArray)
        return [field.name for field in fields]
    
    def getRequestFieldFormat(self,commandArray,fieldName):
        return self.getRequestField(commandArray,fieldName).format
        
    def getRequestFieldLength(self,commandArray,fieldName):
        return self.getRequestField(commandArray,fieldName).length
        
    def getRequestFieldOptions(self,commandArray,fieldName):
        return self.getRequestField(commandArray,fieldName).options
    
    def getRequestField(self,commandArray,fieldName):
        fields = self.getRequestFields(commandArray)
        for field in fields:
            if field.name==fieldName:
                return field
        raise CommandError(CommandError.UNKNOWN_FIELD,
                                        '%s in %s' % (fieldName, '.'.join(commandArray))) 
    
    def getRequestFields(self,commandArray):
        commandDef = self.getDefinition(self.COMMAND,commandArray)
        if 'request' not in commandDef:
            raise CommandError(CommandError.NO_REQUEST,
                                            '.'.join(commandArray)) 
        fields = [Field(fieldRaw,self.fieldOptions)
                             for fieldRaw in commandDef['request']]
        return fields
    
    def getResponseFieldNames(self,type,nameArray):
        '''
        \brief Get the response fields of a (sub)command, from its name.
        
        \param type        Command or notification?
        \param nameArray   An array of the form [commandName, subCommandname]
                           The array can be of any length, and is of length 1
                           if no subcommands are used.
        
        \exception CommandError(NO_RESPONSE) The (sub)command has
                   no request fields.
        \returns The list of request fields.
        '''
        fields = self.getResponseFields(type,nameArray)
        return [field.name for field in fields]
    
    def getResponseFieldFormat(self,type,nameArray,fieldName):
        return self.getResponseField(type,nameArray,fieldName).format
        
    def getResponseFieldLength(self,type,nameArray,fieldName):
        return self.getResponseField(type,nameArray,fieldName).length
        
    def getResponseFieldOptions(self,type,nameArray,fieldName):
        return self.getResponseField(type,nameArray,fieldName).options
    
    def getResponseField(self,type,nameArray,fieldName):
        for i in range(len(nameArray)):
            fields = self.getResponseFields(type,nameArray[:i+1])
            for field in fields:
                if field.name==fieldName:
                    return field
        raise CommandError(CommandError.UNKNOWN_FIELD,
                                        '%s in %s' % (fieldName, '.'.join(nameArray))) 
    
    def getResponseFields(self,type,nameArray):
        
        commandDef = self.getDefinition(type,nameArray)
        
        if 'response' not in commandDef:
            raise CommandError(CommandError.NO_RESPONSE,
                                            '.'.join(nameArray))
        
        keys          = list(commandDef['response'].keys())
        responseName  = keys[0]
        
        fields = [Field(fieldRaw,self.fieldOptions)
                             for fieldRaw in commandDef['response'][responseName]]
        return fields
        
    def responseFieldValueToDesc(self,nameArray,fieldName,fieldValue):
        return self.fieldValueToDesc(
                    self.COMMAND,
                    nameArray,
                    fieldName,
                    fieldValue)
            
    def notifFieldValueToDesc(self,nameArray,fieldName,fieldValue):
        return self.fieldValueToDesc(
                    self.NOTIFICATION,
                    nameArray,
                    fieldName,
                    fieldValue)
    
    def fieldValueToDesc(self,type,nameArray,fieldName,fieldValue):
        responseField = self.getResponseField(type,nameArray,fieldName)
        return responseField.options.valueToDesc(fieldValue)
    
    @classmethod
    def fieldOptionToShortDesc(self,name,value):
        for option in self.fieldOptions[name]:
            if option[0]==value:
                return option[1]
    
    @classmethod
    def fieldFormatToString(self,fieldLength,fieldFormat):
        '''
        \brief Turns the field format into a human-readable string.
        
        \param fieldLength The number of bytes (an int) of the field
        \param fieldFormat The format of a field, expressed as a string
        
        \return A human-readable string.
        '''
        returnVal = ''
        
        if   fieldFormat==FieldFormats.INT  and fieldLength==1:
            returnVal       += 'INT8U'
        elif fieldFormat==FieldFormats.INT  and fieldLength==2:
            returnVal       += 'INT16U'
        elif fieldFormat==FieldFormats.INT  and fieldLength==4:
            returnVal       += 'INT32U'
        elif fieldFormat==FieldFormats.INTS and fieldLength==1:
            returnVal       += 'INT8S'
        elif fieldFormat==FieldFormats.INTS and fieldLength==2:
            returnVal       += 'INT16'
        elif fieldFormat==FieldFormats.INTS and fieldLength==4:
            returnVal       += 'INT32'
        elif fieldFormat==FieldFormats.BOOL:
            returnVal       += 'BOOL'
        else:
            if fieldLength:
                returnVal   += "{0}B ({1})".format(fieldLength,fieldFormat)
            else:
                returnVal   += "{0}".format(fieldFormat)
        
        return returnVal
    
    #======================== validation ======================================
    
    def areSameFieldNames(self,fieldsCommand,fieldsPassed):
        '''
        \brief Determine whether the fields passed contains the same field names
               as defined in the commands.
       
        \exception CommandError.TOO_FEW_FIELDS  Too few fields are 
                   present in the fields passed.
        \exception CommandError.TOO_MANY_FIELDS Too many fields are 
                   present in the fields passed.
        \exception CommandError.UNKNOWN_FIELD At least one unknown 
                   fields in the fields passed.
        '''
        
        # list of field names expected in the command
        namesCommand    = [field[0] for field in fieldsCommand]
        namesCommand.sort()
        
        # list of field names in the passed fields
        namesPassed     = list(fieldsPassed.keys())
        namesPassed.sort()
        
        if   len(namesPassed)<len(namesCommand):
            raise CommandError(CommandError.TOO_FEW_FIELDS) 
        elif len(namesPassed)>len(namesCommand):
            raise CommandError(CommandError.TOO_MANY_FIELDS)
        else:
            for i in range(len(namesPassed)):
                if namesPassed[i]!=namesCommand[i]:
                    raise CommandError(CommandError.UNKNOWN_FIELD,namesPassed[i])
    
    def isValidFieldFormatting(self,commandArray,
                                    fieldName,
                                    fieldValue):
        '''
        \brief Determine whether the field passed contains a correct format
               according to the command definition passed.
       
        \exception CommandError.UNKNOWN_FIELD   The field is not in
                   the definition.
        \exception CommandError.MALFORMED_FIELD The field is malformed.
        '''
        thisField = self.getRequestField(commandArray,fieldName)
        
        # check whether this value is valid
        if thisField.isValidValue(fieldValue)==False:
            raise CommandError(
                CommandError.MALFORMED_FIELD,
                'commandArray={0} fieldName={1} fieldValue={2}'.format(commandArray,fieldName,fieldValue)
            )
    
    def validateRequest(self,commandArray,fields):
        '''
        \brief Validate that the fields passed form a valid request for the
               specified command or subcommand. Raises a CommandError exception
               if the request fields are invalid. 
       
        \param commandArray   An array of the form [commandName, subCommandname]
                              The array can be of any length, and is of length 1
                              if no subcommands are used.
        \param fields         A dictionary indicating the value of every field
                              in that (sub)command, of the form
                              <tt>
                              {
                                 \<fieldName1\>: \<fieldValue1\>,
                                 \<fieldName2\>: \<fieldValue2\>,
                                  ...,
                              }
                              </tt>
       
        \exception CommandError Describes the validation error
        '''
       
        definition = self.getDefinition(self.COMMAND,commandArray)
        
        if 'request' not in definition:
            raise CommandError(CommandError.NO_REQUEST,
                                            '.'.join(commandArray))
        
        # step 1. make sure the command definition and the fields passed have
        #         the same fields (raises errors if not)
        self.areSameFieldNames(definition['request'],fields)
        
        # step 2. for each field, make sure formatting is correct
        #         (raises errors if not)
        for fieldName,fieldValue in list(fields.items()):
            self.isValidFieldFormatting(commandArray,
                                        fieldName,
                                        fieldValue)
    
    #======================== serialization ===================================
    
    def _getSerializer(self,commandArray):
        '''
        \brief Get the serializer associated with a command or subcommand.
        
        \param commandArray   An array of the form [commandName, subCommandname]
                              The array can be of any length, and is of length 1
                              if no subcommands are used.
        
        \returns The definition of a subcommand, represented as a dictionary.
        '''
        return self.getDefinition(self.COMMAND,commandArray)['serializer']
    
    def serialize(self,commandArray,fields):
        '''
        \brief Serialize a command.
       
        This function applies the serializer function specified in this
        (sub)command\'s entry in the API definition.
       
        \param commandArray   An array of the form [commandName, subCommandname]
                              The array can be of any length, and is of length 1
                              if no subcommands are used.
        \param fields         A dictionary indicating the value of every field
                              in that (sub)command, of the form
                              <tt>
                              {
                                 \<fieldName1\>: \<fieldValue1\>,
                                 \<fieldName2\>: \<fieldValue2\>,
                                  ...,
                              }
                              </tt>
       
        \returns The serialized command, in the format specified by this field\'s
                 serializer.
        '''
        
        # verify that this is a valid request (raises exception if not)
        self.validateRequest(commandArray,fields)
        
        # get the serializer associated with this (sub)command
        try:
            serialize_func = getattr(self, self._getSerializer(commandArray))
        except KeyError:
            serialize_func = self.default_serializer
            
        # apply the serializer and return the result
        return serialize_func(commandArray,fields)
    
    #======================== abstract methods ================================

    def default_serializer(self,commandArray,fields):
        '''
        \brief Default serializer for the API if no 'serializer' is specified
               in the command description
       
        The API-specific child class is expected to implement this method
        '''
        
        raise NotImplementedError('No default serializer')
    
    #======================== abstract attributes =============================
    
    ##
    # \brief Enumeration of valid options for certain fields.
    #
    # This structure is a Python dictionary. The key of each entry is an 
    # arbitrary but unique string. The value of each entry is a array of
    # options. Each option is an array of three elements:
    # - a valid value for the field
    # - a short description of that value
    # - a long description of that value
    #
    # An example redefinition is:
    # <tt>
    # fieldOptions = {
    #    'packetPriority' : [
    #       [0,     'low',                   'low'],
    #       [1,     'high',                  'high'],
    #    ],
    # }
    # </tt>
    #
    # \note While the commands variable is defined in this parent ApiDefinition
    #       class, it is meant to be redefined by inheriting classes.
    # 
    fieldOptions = {
    }
    
    ##
    # \brief Commands in this API.
    #
    # Each command is a dictionary with the following mandatory keys:
    # - 'id'           : The ID of this command (a number)
    # - 'name'         : The name of the command (a string)
    # - 'description'  : A plain-English description of the command
    #
    # The following keys are optional:
    # - 'serializer'   : a function to call to serialize this command. If this
    #                    field is absent, the default serializer will be
    #                    called.
    #
    # The remaining fields define the format of the request and response.
    #
    # In the general case, the following fields are present:
    # - 'request'      : array of fields in the request
    # - 'response'     : array of fields in the response
    #
    # A 'request' (resp. response) contains the fields contained in the request
    # (resp. response).
    #
    # \note Commands can define only a request (resp. response), in which case
    #       the response (resp. request) field is not present.
    #
    # In some cases, a command does not defines request/response directly, but 
    # rather subcommands. In that case, the following fields are present:
    # - 'subcommands'  : The name of the dictionary subcomands for this
    #                    function
    #
    # \note While the commands variable is defined in the parent API class,
    #       it is meant to be redefined by classes inheriting from this one.
    #
    commands = [
    ]
    
    ##
    # \brief Notifications in this API.
    #
    # \note While the notifications variable is defined in the parent API class,
    #       it is meant to be redefined by classes inheriting from this one.
    #
    notifications = [
    ]
