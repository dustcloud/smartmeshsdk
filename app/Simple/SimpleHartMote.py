#!/usr/bin/python

#============================ adjust path =====================================

import sys
import os
if __name__ == "__main__":
    here = sys.path[0]
    sys.path.insert(0, os.path.join(here, '..', '..','libs'))
    sys.path.insert(0, os.path.join(here, '..', '..','external_libs'))

#============================ imports =========================================

from SmartMeshSDK.ApiDefinition   import ApiDefinition,         \
                                         HartMoteDefinition
from SmartMeshSDK.ApiException    import CommandError,          \
                                         ConnectionError

#============================ main ============================================

print 'Simple Application which interacts with the HART mote - (c) Dust Networks'

print '\n\n================== Step 1. API exploration ========================'

print '\n=====\nLoad the API definition of the HART mote'
apidef = HartMoteDefinition.HartMoteDefinition()
print 'done.'

print '\n=====\nList all the defined command IDs:'
print apidef.getIds(ApiDefinition.ApiDefinition.COMMAND)

print '\n=====\nList all the defined command names:'
print apidef.getNames(ApiDefinition.ApiDefinition.COMMAND)

print '\n=====\nGet the command name of command ID 4:'
print apidef.idToName(ApiDefinition.ApiDefinition.COMMAND,
                      4)

print '\n=====\nGet the command ID of command name \'getNVParameter\':'
print apidef.nameToId(ApiDefinition.ApiDefinition.COMMAND,
                      ['getNVParameter'])

print '\n=====\nList the subcommand of command \'getNVParameter\':'
print apidef.getNames(ApiDefinition.ApiDefinition.COMMAND,
                      ['getNVParameter'])

print '\n=====\nGet a description of the getNVParameter.powerInfo command:'
print apidef.getDescription(ApiDefinition.ApiDefinition.COMMAND,
                            ['getNVParameter','powerInfo'])
                      
print '\n=====\nList the name of the fields in the getNVParameter.powerInfo request:'
print apidef.getRequestFieldNames(['getNVParameter','powerInfo'])

print '\n=====\nList the name of the fields in the getNVParameter.powerInfo response:'
print apidef.getResponseFieldNames(ApiDefinition.ApiDefinition.COMMAND,
                                   ['getNVParameter','powerInfo'])

print '\n=====\nList the name of the fields in the testRadioTx response:'
print apidef.getResponseFieldNames(ApiDefinition.ApiDefinition.COMMAND,
                                   ['testRadioTx'])

print '\n=====\nPrint the format of the testRadioTx \'RC\' response field:'
print apidef.getResponseFieldFormat(ApiDefinition.ApiDefinition.COMMAND,
                                    ['testRadioTx'],
                                    'RC')

print '\n=====\nPrint the valid options of the testRadioTx \'RC\' response field:'
print apidef.getResponseFieldOptions(ApiDefinition.ApiDefinition.COMMAND,
                                    ['testRadioTx'],
                                    'RC').validOptions

print '\n=====\nPrint the format of the getNVParameter.powerInfo \'powerSource\' response field:'
print apidef.getResponseFieldFormat(ApiDefinition.ApiDefinition.COMMAND,
                                    ['getNVParameter','powerInfo'],
                                    'powerSource')

print '\n=====\nPrint the length of the getNVParameter.powerInfo \'powerSource\' response field:'
print apidef.getResponseFieldLength(ApiDefinition.ApiDefinition.COMMAND,
                                    ['getNVParameter','powerInfo'],
                                    'powerSource')

print '\n=====\nPrint the valid options of the getNVParameter.powerInfo \'powerSource\' response field:'
print apidef.getResponseFieldOptions(ApiDefinition.ApiDefinition.COMMAND,
                                    ['getNVParameter','powerInfo'],
                                    'powerSource').validOptions

print '\n=====\nPrint the description of each valid options of the getNVParameter.powerInfo \'powerSource\' response field:'
print apidef.getResponseFieldOptions(ApiDefinition.ApiDefinition.COMMAND,
                                    ['getNVParameter','powerInfo'],
                                    'powerSource').optionDescs

raw_input('\nScript ended. Press Enter to exit.')