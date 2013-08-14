#!/usr/bin/python

import struct
import operator
import ApiDefinition
from   ApiException import CommandError
import types

import logging
class NullHandler(logging.Handler):
    def emit(self, record):
        pass
log = logging.getLogger('ByteArraySerializer')
log.setLevel(logging.ERROR)
log.addHandler(NullHandler())

class ByteArraySerializer(object):
    '''
    \ingroup ApiDefinition
    \brief Serializer/deserializer for byte arrays.
    '''

    def __init__(self,ApiDef):
        self.ApiDef = ApiDef
    
    def serialize(self,commandArray,fieldsToFill):
        
        log.debug(  "serialize ...\n" + \
                    " - commandArray="+str(commandArray)+"\n" \
                    " - fieldsToFill="+str(fieldsToFill))
        
        if type(commandArray)!=types.ListType and type(commandArray)!=types.TupleType:
            raise TypeError("First parameter should be a list or tuple, not "+str(type(commandArray)))
        
        byteArray  = []
        
        for cmdCounter in range(len(commandArray)):
        
            # packet payload
            definition = self.ApiDef.getDefinition(ApiDefinition.ApiDefinition.COMMAND,
                                                   commandArray[:cmdCounter+1])
            
            fields = [ApiDefinition.Field(fieldRaw,self.ApiDef.fieldOptions)
                         for fieldRaw in definition['request']]
            for field in fields:
                thisFieldByteArray = []
                if field.name in ApiDefinition.ApiDefinition.RESERVED:
                    thisFieldByteArray.append(
                        self.ApiDef.subcommandNameToId(
                            ApiDefinition.ApiDefinition.COMMAND,
                            commandArray[:cmdCounter+1],
                            commandArray[cmdCounter+1]
                        )
                    )
                else:
                    val                = fieldsToFill[field.name]
                    
                    if   field.format==ApiDefinition.FieldFormats.STRING:
                        for car in val:
                           thisFieldByteArray += [ord(car) for car in val]
                    
                    elif field.format==ApiDefinition.FieldFormats.BOOL:
                        thisFieldByteArray.append(val)
                    
                    elif field.format==ApiDefinition.FieldFormats.INT:
                        thisFieldByteArray    += [operator.mod(int(val>>(8*i)), 0x100) for i in xrange(field.length-1, -1, -1)]
                    
                    elif field.format==ApiDefinition.FieldFormats.INTS:
                        if   field.length==1:
                            temp = struct.pack('>b',int(val))
                        elif field.length==2:
                            temp = struct.pack('>h',int(val))
                        elif field.length==4:
                            temp = struct.pack('>i',int(val))
                        else:
                            raise SystemError('field with format='+field.format+' and length='+str(field.length)+' unsupported.')
                        for i in range(len(temp)):
                            thisFieldByteArray.append(ord(temp[i]))
                    
                    elif field.format==ApiDefinition.FieldFormats.HEXDATA:
                        thisFieldByteArray    += val
                    
                    else:
                        raise SystemError('unknown field format='+field.format)
                        
                    while len(thisFieldByteArray)<field.length:
                        thisFieldByteArray  = [0x00]+thisFieldByteArray
                
                byteArray = byteArray+thisFieldByteArray
        
        cmdId = self.ApiDef.nameToId(ApiDefinition.ApiDefinition.COMMAND,commandArray)
        
        log.debug(  "... serialize into\n"+ \
                    " - cmdId="+str(cmdId)+"\n" \
                    " - byteArray="+str(byteArray) )
        
        return cmdId,byteArray

    def deserialize(self,type,id,byteArray):
        notRcOk         = False
        returnFields    = {}
        nameArray       = [self.ApiDef.idToName(type,id)]
        index           = 0
        
        log.debug(  "deserialize ...\n" +\
                    " - type="+str(type)+"\n" \
                    " - id="+str(id)+"\n" \
                    " - byteArray="+str(byteArray))
        
        continueParsing  = True
        while continueParsing:
            
            fieldDefs   = self.ApiDef.getResponseFields(type,nameArray)
            
            for fieldDef in fieldDefs:
            
                # isolate the piece of the byteArray corresponding to this field
                if fieldDef.length:
                    thisFieldArray = byteArray[index:index+fieldDef.length]
                    if len(thisFieldArray)!=fieldDef.length:
                        raise CommandError(CommandError.TOO_FEW_BYTES,
                                            "fieldName="+str(fieldDef.name)
                                          )
                    index         += fieldDef.length
                else:
                    thisFieldArray = byteArray[index:]
                    if len(thisFieldArray)<1:
                        raise CommandError(CommandError.TOO_FEW_BYTES,
                                            "fieldName="+str(fieldDef.name)
                                          )
                    index          = len(byteArray)
                
                # turn thisFieldArray into thisFieldValue
                if   fieldDef.format==ApiDefinition.FieldFormats.STRING:
                    thisFieldValue = ''
                    for byte in thisFieldArray:
                        thisFieldValue += chr(byte)
                elif fieldDef.format==ApiDefinition.FieldFormats.BOOL:
                    if    len(thisFieldArray)==1 and thisFieldArray[0]==0x00:
                        thisFieldValue = False
                    elif  len(thisFieldArray)==1 and thisFieldArray[0]==0x01:
                        thisFieldValue = True
                    else:
                        raise CommandError(CommandError.VALUE_NOT_IN_OPTIONS,
                                           "field="+fieldDef.name+" value="+str(thisFieldValue))
                elif fieldDef.format==ApiDefinition.FieldFormats.INT:
                    thisFieldValue = 0
                    for i in range(len(thisFieldArray)):
                        thisFieldValue += thisFieldArray[i]*pow(2,8*(len(thisFieldArray)-i-1))
                elif fieldDef.format==ApiDefinition.FieldFormats.INTS:
                    tempList = [chr(i) for i in thisFieldArray]
                    tempString = ''.join(tempList)
                    if   len(thisFieldArray)==1:
                        (thisFieldValue,) = struct.unpack_from('>b',tempString)
                    elif len(thisFieldArray)==2:
                        (thisFieldValue,) = struct.unpack_from('>h',tempString)
                    elif len(thisFieldArray)==4:
                        (thisFieldValue,) = struct.unpack_from('>i',tempString)
                    else:
                        raise SystemError('field with format='+fieldDef.format+' and length='+str(fieldDef.length)+' unsupported.')
                    
                elif fieldDef.format==ApiDefinition.FieldFormats.HEXDATA:
                    thisFieldValue = thisFieldArray
                else:
                    raise SystemError('unknown field format='+fieldDef.format)
                
                # make sure thisFieldValue in fieldDef.options
                if fieldDef.options.validOptions:
                    if thisFieldValue not in fieldDef.options.validOptions:
                        raise CommandError(CommandError.VALUE_NOT_IN_OPTIONS,
                                           "field="+fieldDef.name+" value="+str(thisFieldValue))
                
                if fieldDef.name in ApiDefinition.ApiDefinition.RESERVED:
                    idNextCommand = thisFieldValue
                else:
                    returnFields[fieldDef.name] = thisFieldValue
                    
                # stop if not RC_OK
                if  (
                        (ApiDefinition.ApiDefinition.RC in returnFields) and
                        (
                            returnFields[ApiDefinition.ApiDefinition.RC]!= \
                                ApiDefinition.ApiDefinition.RC_OK
                        )
                   ):
                   notRcOk = True
                   break
            
            # continue if subCommand
            if  (
                    (not notRcOk)           and
                    continueParsing         and
                    self.ApiDef.hasSubcommands(type,nameArray)
                ):
                # find name of subCommand
                nameArray.append(self.ApiDef.subcommandIdToName(type,
                                                                nameArray,
                                                                idNextCommand))
                continueParsing = True
            
            # stop if not RC_OK
            if  (
                    continueParsing         and
                    notRcOk
                ):
                continueParsing = False
            
            # stop if end of packet reached
            if  (
                    continueParsing         and
                    index>=len(byteArray)
                ):
                continueParsing = False
            
        
        if  (
                (not notRcOk)               and
                (index!=len(byteArray))
            ):
            raise CommandError(CommandError.TOO_MANY_BYTES,index)
        
        log.debug(  "... deserialized into\n"+ \
                    " - nameArray="   +str(nameArray)+"\n" \
                    " - returnFields="+str(returnFields) )
        
        return nameArray,returnFields
    
