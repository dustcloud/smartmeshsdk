#============================ adjust path =====================================

import sys
import os
if __name__ == "__main__":
    here = sys.path[0]
    sys.path.insert(0, os.path.join(here, '..'))

#============================ imports =========================================

from   SmartMeshSDK import ApiException
from   SmartMeshSDK.ApiDefinition.IpMgrDefinition    import IpMgrDefinition
from   SmartMeshSDK.ApiDefinition.IpMoteDefinition   import IpMoteDefinition
from   SmartMeshSDK.ApiDefinition.HartMgrDefinition  import HartMgrDefinition
from   SmartMeshSDK.ApiDefinition.HartMoteDefinition import HartMoteDefinition

#============================ templates =======================================

TMPL_CLASSDEF = '''\'\'\'
This module was generated automatically. Do not edit directly.
\'\'\'

import collections
from   SmartMeshSDK import ApiException
from   {MODULE_NAME} import {BASE_CLASS_NAME}

##
# \\addtogroup {GEN_CLASS_NAME}
# \\{{
# 

class {GEN_CLASS_NAME}({BASE_CLASS_NAME}):
    \'\'\'
    \\brief {BRIEF_DESCRIPTION}
    \'\'\'
'''

TMPL_DEF = '''
    ##
    # The named tuple returned by the {CMD_NAME}() function.
    # 
{TUPLE_COMMENT}
    # 
    Tuple_{CMD_NAME} = collections.namedtuple("Tuple_{CMD_NAME}", {TUPLE_PARAMS})

    ##
    # {DESCR}
    # 
{CMD_COMMENT}
    # 
    # \\returns The response to the command, formatted as a #Tuple_{CMD_NAME} named tuple.
    # 
    def {CMD_NAME}(self, {CMD_PARMS}) :
        res = {BASE_CLASS_NAME}.send(self, {NAMES}, {{{PARAMS_DICT}}})
        return {CLASS_NAME}.Tuple_{CMD_NAME}(**res)
''' 

TMPL_DEF_LIST = '''
    ##
    # The named tuple returned by the {CMD_NAME}() function.
    # 
{TUPLE_COMMENT}
    # 
    Tuple_{CMD_NAME} = collections.namedtuple("Tuple_{CMD_NAME}", {TUPLE_PARAMS})

    ##
    # {DESCR}
    # 
{CMD_COMMENT}
    # 
    # \\returns The response to the command, formatted as a list of #Tuple_{CMD_NAME} named tuple.
    # 
    def {CMD_NAME}(self, {CMD_PARMS}) :
        res = {BASE_CLASS_NAME}.send(self, {NAMES}, {{{PARAMS_DICT}}})
        tupleList = []
        for r in res :
            tupleList.append({CLASS_NAME}.Tuple_{CMD_NAME}(**r))
        return tupleList
'''
 
TMPL_DEF_NOTUPLE = '''
    ##
    # {DESCR}
    # 
{CMD_COMMENT}
    # 
    # \\returns The response to the command.
    # 
    def {CMD_NAME}(self, {CMD_PARMS}) :
        res = {BASE_CLASS_NAME}.send(self, {NAMES}, {{{PARAMS_DICT}}})
        return res
''' 

TMPL_NOTIF = '''
    ##
    # \\brief {NOTIF_NAME_UP} notification.
    # 
    # {DESCR}
    #
{NOTIF_COMMENT}    
    # 
    {NOTIF_NAME_UP} = "{NOTIF_NAME}"
    notifTupleTable[{NOTIF_NAME_UP}] = Tuple_{NOTIF_NAME} = collections.namedtuple("Tuple_{NOTIF_NAME}", {NOTIF_PARAMS})
'''

TMPL_NOTIF_NOTUPLE = '''
    ##
    # \\brief Notification {NOTIF_NAME_UP} 
    # 
    # {DESCR}
    #        
    {NOTIF_NAME_UP} = "{NOTIF_NAME}"
    notifTupleTable[{NOTIF_NAME_UP}] = None
'''

TMPL_GETNOTIFICATION = '''
    ##
    # \\brief Get a notification from the notification queue, and returns
    #        it properly formatted.
    #
    # \\exception NotificationError if unknown notification.
    # 
    def getNotification(self, timeoutSec=-1) :
        temp = self.getNotificationInternal(timeoutSec)
        if not temp:
            return temp
        (ids, param) = temp
        try :
            if  {CLASS_NAME}.notifTupleTable[ids[-1]] :
                return (ids[-1], {CLASS_NAME}.notifTupleTable[ids[-1]](**param))
            else :
                return (ids[-1], None)
        except KeyError :
            raise ApiException.NotificationError(ids, param)
'''

START_LOCATION_COMMENT = '''
    # \param numFrames 1-byte field formatted as an integer.<br/>
    #     There is no restriction on the value of this field.
    # \param mobileMote 8-byte field formatted as hex.<br/>
    #     There is no restriction on the value of this field.
    # \param fixedMotes list of 8-byte fields formatted as hex.<br/>
    #     There is no restriction on the value of this field.
    # 
'''

START_LOCATION_PAYLOAD = '''
        payload = []
        for fm in fixedMotes :
            payload += fm
        res = {BASE_CLASS_NAME}.send(self, ['startLocation'], {{"numFrames" : numFrames, "mobileMote" : mobileMote, "fixedMotes" : payload}})
'''

TMPL_ENDCLASSDEF = '''
##
# end of {GEN_CLASS_NAME}
# \\}}
# 
'''

def printStartLocation(names, respFieldsName, reqFieldsName, 
                       CMD_NAME, CMD_PARMS, DESCR, 
                       TUPLE_PARAMS, NAMES, PARAMS_DICT, 
                       BASE_CLASS_NAME, CLASS_NAME,
                       TUPLE_COMMENT, CMD_COMMENT) :
    s = TMPL_DEF.format(CMD_NAME = CMD_NAME, CMD_PARMS = CMD_PARMS, DESCR = DESCR, 
                       TUPLE_PARAMS = TUPLE_PARAMS, NAMES = NAMES, PARAMS_DICT = PARAMS_DICT, 
                       BASE_CLASS_NAME = BASE_CLASS_NAME, CLASS_NAME = CLASS_NAME,
                       TUPLE_COMMENT = TUPLE_COMMENT, CMD_COMMENT = '***')
    lines = s.split('\n')
    res = []
    for l in lines :
        if l == '***' :
            res += [START_LOCATION_COMMENT[1:]]
        elif l.find('send(self') >= 0:
            res += [START_LOCATION_PAYLOAD[1:].format(BASE_CLASS_NAME=BASE_CLASS_NAME)]
        else :
            res += [l + '\n']
    return ''.join(res)

RADIOTEST_TX_COMMENT = '''
    # \param type 1-byte field formatted as an integer.<br/>
    #     Type of transmission test: 0=packet, 1=continuous modulation (CM), 2=continuous wave (CW)
    # \param mask 2-bytes field formatted as an integer.<br/>
    #     Mask of channels(0-15) enabled for test.
    # \param txPower 1-byte field formatted as an sign integer.<br/>
    #     Transmit power, in dB. Valid values are 0 (power amplifier off) and 8 (power amplifier on).
    # \param numRepeats 2-byte field formatted as an integer.<br/>
    #     Number of times to repeat the packet sequence (0=do not stop). Applies only to packet transmission tests.
    # \param tests list of pair of integer.<br/>
    #     Sequence definitions (up to 10) specifies the length (bytes) and after-packet delay (usec) for each packets
'''

RADIOTEST_TX_PAYLOAD = '''
        d = {{"type" : type, "mask" : mask, "numRepeats" : numRepeats, "txPower" : txPower, "numPackets" : len(tests)}}
        for i in xrange(10) :
            if i < len(tests) :
                l, g = tests[i]
            else :
                l, g = (0, 0)
            d["pkSize" + str(i+1)] = l
            d["gap" + str(i+1)]    = g
        res = {BASE_CLASS_NAME}.send(self, ['radiotestTx'], d)
'''
    
def printRsadioTestTx(names, respFieldsName, reqFieldsName, 
                       CMD_NAME, CMD_PARMS, DESCR, 
                       TUPLE_PARAMS, NAMES, PARAMS_DICT, 
                       BASE_CLASS_NAME, CLASS_NAME,
                       TUPLE_COMMENT, CMD_COMMENT) :
    s = TMPL_DEF.format(CMD_NAME = CMD_NAME, CMD_PARMS = CMD_PARMS, DESCR = DESCR, 
                       TUPLE_PARAMS = TUPLE_PARAMS, NAMES = NAMES, PARAMS_DICT = PARAMS_DICT, 
                       BASE_CLASS_NAME = BASE_CLASS_NAME, CLASS_NAME = CLASS_NAME,
                       TUPLE_COMMENT = TUPLE_COMMENT, CMD_COMMENT = '***')
    lines = s.split('\n')
    res = []
    for l in lines :
        if l == '***' :
            res += [RADIOTEST_TX_COMMENT[1:]]
        elif l.find('def dn_radioTestTx') >= 0 :
            res += '    def dn_radioTestTx(self, type, mask, txPower, numRepeats, tests) :\n'
        elif l.find('send(self') >= 0:
            res += [RADIOTEST_TX_PAYLOAD[1:].format(BASE_CLASS_NAME=BASE_CLASS_NAME)]
        else :
            res += [l + '\n']
    return ''.join(res)
    
'''
Dictionary of commands with special processing:
    {'cmdName' : [requestFields, responseFields, generator]}
    
    def generator(names, respFieldsName, reqFieldsName, 
                  CMD_NAME, CMD_PARMS, DESCR, TUPLE_PARAMS, NAMES, PARAMS_DICT, 
                  BASE_CLASS_NAME, CLASS_NAME, TUPLE_COMMENT, CMD_COMMENT) :
        return strings
'''

specialCmd = {
    'dn_startLocation' : [
        ['numFrames', 'mobileMote', 'fixedMotes'],
        ['RC', 'callbackId'],
        printStartLocation
    ],

    'dn_radioTestTx' : [
        ['type', 'mask', 'numRepeats', 'txPower', 'numPackets',
         'pkSize1', 'gap1', 'pkSize2', 'gap2', 'pkSize3', 'gap3', 'pkSize4', 'gap4', 'pkSize5', 'gap5', 
         'pkSize6', 'gap6', 'pkSize7', 'gap7', 'pkSize8', 'gap8', 'pkSize9', 'gap9', 'pkSize10', 'gap10'],
        ['RC'],
        printRsadioTestTx
    ]   
}       
        
class GenApiConnectors(object):
        
    #======================== public ==========================================
    
    def __init__(self, apiDefName, myClassName, baseClassName, baseModuleName, outputFileName = None, briefDescription = '', apiDefClass=None):
        if apiDefName:
            apiDefClass = globals()[apiDefName]
        self.apiDef           = apiDefClass() 
        self.myClassName      = myClassName
        self.baseClassName    = baseClassName 
        self.baseModuleName   = baseModuleName
        self.briefDescription = briefDescription
        if outputFileName:
            self.outFile = open(outputFileName, "wt")
        else:
            self.outFile = sys.stdout
            
    def gen(self):
        s = TMPL_CLASSDEF.format(MODULE_NAME       = self.baseModuleName,
                                 BASE_CLASS_NAME   = self.baseClassName, 
                                 GEN_CLASS_NAME    = self.myClassName,
                                 BRIEF_DESCRIPTION = self.briefDescription)
        self.outFile.write(s)
        self.outFile.write('\n    #======================== commands ========================================\n')
        self.genCmd()
        self.outFile.write('\n    #======================== notifications ===================================\n')
        self.genNotif()
        s = TMPL_ENDCLASSDEF.format(GEN_CLASS_NAME    = self.myClassName)
        self.outFile.write(s)
        self.genFinish()
        
    #======================== private =========================================
    
    #===== commands
    
    def genCmd(self):
        cmdNames = self.apiDef.getNames(self.apiDef.COMMAND)
        for name in cmdNames :
            self.genOneCmd([name], [], [])
    
    def genOneCmd(self, names, respFieldsName, reqFieldsName):
        
        # get request fields
        r = self.apiDef.getRequestFieldNames(names)
        reqFieldsName += [n for n in r if n not in self.apiDef.RESERVED]
        
        # get response fields
        try:
            r = self.apiDef.getResponseFieldNames(self.apiDef.COMMAND, names) 
            respFieldsName += [n for n in r if n not in self.apiDef.RESERVED]
        except ApiException.CommandError :
            # means that this function has no response fields, which is OK
            pass
        
        if self.apiDef.hasSubcommands(self.apiDef.COMMAND, names):
            subcmdsName = self.apiDef.getNames(self.apiDef.COMMAND, names)
            for sn in subcmdsName :
                self.genOneCmd(names+[sn], respFieldsName[:], reqFieldsName[:])
        else:
            cmdName     = 'dn_'
            cmdName    += '_'.join([n for n in names])
            cmdParams   = ', '.join([p for p in reqFieldsName])
            paramsDict  = ', '.join(['"{0}" : {1}'.format(p, p) for p in reqFieldsName])
            descr       = self.apiDef.getDescription(self.apiDef.COMMAND, names).replace('\n', '\n    # ')
            cmdComment  = ''.join([self.getCmdComments(names, p) for p in reqFieldsName])[:-1]
            if not cmdComment:
                cmdComment = '    # '
            tupleComment = ''.join([self.getCmdTupleComments(names, p) for p in respFieldsName])[:-1]
            
            if cmdName in specialCmd and specialCmd[cmdName][0] == reqFieldsName and specialCmd[cmdName][1] == respFieldsName :
                s = specialCmd[cmdName][2](names, respFieldsName, reqFieldsName, 
                                           CMD_NAME             = cmdName,
                                           CMD_PARMS            = cmdParams,
                                           DESCR                = descr, 
                                           TUPLE_PARAMS         = respFieldsName,
                                           NAMES                = names,
                                           PARAMS_DICT          = paramsDict, 
                                           BASE_CLASS_NAME      = self.baseClassName,
                                           CLASS_NAME           = self.myClassName,
                                           TUPLE_COMMENT        = tupleComment,
                                           CMD_COMMENT          = cmdComment)
            else :
                if respFieldsName :
                    cmd_metadata = self.apiDef.getDefinition(self.apiDef.COMMAND, names)
                    if ('isResponseArray' in cmd_metadata) :
                        s = TMPL_DEF_LIST.format(CMD_NAME                = cmdName,
                                            CMD_PARMS               = cmdParams,
                                            DESCR                   = descr, 
                                            TUPLE_PARAMS            = respFieldsName,
                                            NAMES                   = names,
                                            PARAMS_DICT             = paramsDict, 
                                            BASE_CLASS_NAME         = self.baseClassName,
                                            CLASS_NAME              = self.myClassName,
                                            TUPLE_COMMENT           = tupleComment,
                                            CMD_COMMENT             = cmdComment)
                    else :
                        s = TMPL_DEF.format(CMD_NAME                = cmdName,
                                            CMD_PARMS               = cmdParams,
                                            DESCR                   = descr, 
                                            TUPLE_PARAMS            = respFieldsName,
                                            NAMES                   = names,
                                            PARAMS_DICT             = paramsDict, 
                                            BASE_CLASS_NAME         = self.baseClassName,
                                            CLASS_NAME              = self.myClassName,
                                            TUPLE_COMMENT           = tupleComment,
                                            CMD_COMMENT             = cmdComment)
                else :
                    s = TMPL_DEF_NOTUPLE.format(CMD_NAME        = cmdName,
                                                CMD_PARMS       = cmdParams,
                                                DESCR           = descr, 
                                                NAMES           = names,
                                                PARAMS_DICT     = paramsDict, 
                                                BASE_CLASS_NAME = self.baseClassName,
                                                CMD_COMMENT     = cmdComment)
            self.outFile.write(s)
    
    #===== notifications
    
    def genNotif(self):
        # write header
        output  = []
        output += ['    \n']
        output += ['    ##\n']
        output += ['    # Dictionary of all notification tuples.\n']
        output += ['    #\n']
        output += ['    notifTupleTable = {}\n']
        output += ['    ']
        self.outFile.write(''.join(output))
        
        # generate all notifications
        notifIds = self.apiDef.getIds(self.apiDef.NOTIFICATION)
        for notifId in notifIds :
            notifName = self.apiDef.idToName(self.apiDef.NOTIFICATION, notifId)
            self.genOneNotif([notifName], [])
        s = TMPL_GETNOTIFICATION.format(BASE_CLASS_NAME=self.baseClassName,
                                        CLASS_NAME=self.myClassName)
        self.outFile.write(s)
        
    def genOneNotif(self, names, fieldNames) :
        try :
            f = self.apiDef.getResponseFieldNames(self.apiDef.NOTIFICATION, names)
            if not f :
                raise KeyError
            fieldNames += [n for n in f if n not in self.apiDef.RESERVED]
        except (NameError, KeyError, ApiException.CommandError) :
            pass
        
        try :
            subcmdsName = self.apiDef.getNames(self.apiDef.NOTIFICATION, names)
            for sn in subcmdsName :
                self.genOneNotif(names + [sn], fieldNames[:])
        except ApiException.CommandError :
            notifName = names[-1]
            descr = self.apiDef.getDescription(self.apiDef.NOTIFICATION, names).replace('\n', '\n    # ')
            if fieldNames:
                tupleName = "Tuple_"+notifName
                notifComment  = '    # Formatted as a {0} named tuple.'.format(tupleName)
                notifComment += ' It contains the following fields:\n'
                notifComment += ''.join([self.getNotifComments(names,tupleName,fieldName) for fieldName in fieldNames])[:-1]
                if not notifComment:
                    notifComment = '    # '
                s = TMPL_NOTIF.format(NOTIF_NAME                = notifName,
                                      NOTIF_NAME_UP             = notifName.upper(),
                                      NOTIF_PARAMS              = fieldNames,
                                      DESCR                     = descr,
                                      NOTIF_COMMENT             = notifComment)
            else :
                s = TMPL_NOTIF_NOTUPLE.format(NOTIF_NAME        = notifName,
                                              NOTIF_NAME_UP     = notifName.upper(),
                                              DESCR             = descr)
            self.outFile.write(s)
    
    #===== end
    
    def genFinish(self):
        if self.outFile != sys.stdout :
            self.outFile.close()
    
    #======================== helpers =========================================
    
    def getCmdTupleComments(self, names, param):
        format  = self.apiDef.getResponseFieldFormat(self.apiDef.COMMAND, names, param)
        length  = self.apiDef.getResponseFieldLength(self.apiDef.COMMAND, names, param)
        options = self.apiDef.getResponseFieldOptions(self.apiDef.COMMAND, names, param)
        s = '    # - <tt>{NAME}</tt>: {LEN}-byte field formatted as a {FMT}.<br/>\n'.format(NAME=param, 
                                                                                            LEN=length,
                                                                                            FMT=format)
        s +=  self.getValidationComment(options)
        return s
    
    def getCmdComments(self, names, param):
        format  = self.apiDef.getRequestFieldFormat(names, param)
        length  = self.apiDef.getRequestFieldLength(names, param)
        options = self.apiDef.getRequestFieldOptions(names, param)
        s = '    # \param {NAME} {LEN}-byte field formatted as a {FMT}.<br/>\n'.format(NAME=param, 
                                                                                       LEN=length,
                                                                                       FMT=format)
        s +=  self.getValidationComment(options)
        return s
    
    def getNotifComments(self, names, tupleName, fieldName):
        format  = self.apiDef.getResponseFieldFormat(self.apiDef.NOTIFICATION,
                                                     names,
                                                     fieldName)
        length  = self.apiDef.getResponseFieldLength(self.apiDef.NOTIFICATION,
                                                     names,
                                                     fieldName)
        options = self.apiDef.getResponseFieldOptions(self.apiDef.NOTIFICATION,
                                                      names,
                                                      fieldName)
        s = '    #   - <tt>{NAME}</tt> {LEN}-byte field formatted as a {FMT}.<br/>\n'.format(NAME=fieldName, 
                                                                                           LEN=length,
                                                                                           FMT=format)
        s +=  self.getValidationComment(options)
        return s
        
    def getValidationComment(self, options):
        if not options.validOptions:
            return '    #     There is no restriction on the value of this field.\n' 
        s = '    #     This field can only take one of the following values:\n'
        for i in range(len(options.validOptions)):
            s += '    #      - {0}: {1}\n'.format(options.validOptions[i], options.optionDescs[i])
        return s

def genFile(srcFileName, dstFileName, comment):
    if isinstance(srcFileName, str):
        apiDefClass = None
        apiDefName = os.path.splitext(os.path.basename(srcFileName))[0]
    else:
        apiDefClass = srcFileName
        apiDefName = None
    baseName   = os.path.splitext(os.path.basename(dstFileName))[0]
    gen = GenApiConnectors(apiDefName=apiDefName,
                           apiDefClass=apiDefClass,
                           myClassName=baseName,
                           baseClassName=baseName + "Internal",
                           baseModuleName=baseName + "Internal",
                           outputFileName=dstFileName,
                           briefDescription=comment)
    gen.gen()
        
def main() :
    if len(sys.argv) < 3:
        print "Usage: GenApiConnectors <apiDefinitionFile> <resultFile> [<comment>]"
        return 1
    
    comment = ''
    if len(sys.argv) > 3:
        comment = sys.argv[3]
    genFile(sys.argv[1], sys.argv[2], comment)
    
if __name__ == '__main__':
    main()

