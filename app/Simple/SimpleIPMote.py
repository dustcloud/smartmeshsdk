#!/usr/bin/python

#============================ adjust path =====================================

import sys
import os
if __name__ == "__main__":
    here = sys.path[0]
    sys.path.insert(0, os.path.join(here, '..', '..','libs'))
    sys.path.insert(0, os.path.join(here, '..', '..','external_libs'))

#============================ imports =========================================

from SmartMeshSDK.ApiDefinition   import ApiDefinition,    \
                                         IpMoteDefinition
from SmartMeshSDK.IpMoteConnector import IpMoteConnector
from SmartMeshSDK.ApiException    import CommandError,     \
                                         ConnectionError

#============================ main ============================================

print 'Simple Application which interacts with the IP mote - (c) Dust Networks'

print '\n\n================== Step 1. API exploration ========================'

print '\n=====\nLoad the API definition of the IP mote'
apidef       = IpMoteDefinition.IpMoteDefinition()
print 'done.'

print '\n=====\nList all the defined command IDs:'
print apidef.getIds(ApiDefinition.ApiDefinition.COMMAND)

print '\n=====\nList all the defined command names:'
print apidef.getNames(ApiDefinition.ApiDefinition.COMMAND)

print '\n=====\nGet the command name of command ID 2:'
print apidef.idToName(ApiDefinition.ApiDefinition.COMMAND,
                      2)

print '\n=====\nGet the command ID of command name \'getParameter\':'
print apidef.nameToId(ApiDefinition.ApiDefinition.COMMAND,
                      ['getParameter'])

print '\n=====\nList the subcommand of command \'getParameter\':'
print apidef.getNames(ApiDefinition.ApiDefinition.COMMAND,
                      ['getParameter'])

print '\n=====\nGet a description of the getParameter.moteStatus command:'
print apidef.getDescription(ApiDefinition.ApiDefinition.COMMAND,
                            ['getParameter','moteStatus'])
                      
print '\n=====\nList the name of the fields in the getParameter.moteStatus request:'
print apidef.getRequestFieldNames(['getParameter','moteStatus'])

print '\n=====\nList the name of the fields in the getParameter.moteStatus response:'
print apidef.getResponseFieldNames(ApiDefinition.ApiDefinition.COMMAND,
                                   ['getParameter','moteStatus'])
                                   
print '\n=====\nPrint the format of the getParameter.moteStatus \'state\' response field:'
print apidef.getResponseFieldFormat(ApiDefinition.ApiDefinition.COMMAND,
                                    ['getParameter','moteStatus'],
                                    'state')

print '\n=====\nPrint the length of the getParameter.moteStatus \'state\' response field:'
print apidef.getResponseFieldLength(ApiDefinition.ApiDefinition.COMMAND,
                                    ['getParameter','moteStatus'],
                                    'state')

print '\n=====\nPrint the valid options of the getParameter.moteStatus \'state\' response field:'
print apidef.getResponseFieldOptions(ApiDefinition.ApiDefinition.COMMAND,
                                    ['getParameter','moteStatus'],
                                    'state').validOptions

print '\n=====\nPrint the description of each valid options of the getParameter.moteStatus \'state\' response field:'
print apidef.getResponseFieldOptions(ApiDefinition.ApiDefinition.COMMAND,
                                    ['getParameter','moteStatus'],
                                    'state').optionDescs

print '\n\n================== Step 2. Connecting to a device ================='

connect = raw_input('\nDo you want to connect to a device? [y/n] ')

if connect.strip()!='y':
    raw_input('\nScript ended. Press Enter to exit.')
    sys.exit()

serialPort = raw_input('\nEnter the serial port of the IP mote\'s API (e.g. COM30) ')

print '\n=====\nCreating connector'
connector = IpMoteConnector.IpMoteConnector()
print 'done.'

print '\n=====\nConnecting to IP mote'
try:
    connector.connect({
                        'port': serialPort,
                     })
except ConnectionError as err:
    print err
    raw_input('\nScript ended. Press Enter to exit.')
print 'done.'


print '\n\n================== Step 3. Getting information from the device ===='

try:
    print '\n=====\nRetrieve the moteStatus, through \'raw\' API access:'
    print connector.send(['getParameter','moteStatus'],{})
    
    print '\n=====\nRetrieve the moteStatus, through function-based API access:'
    print connector.dn_getParameter_moteStatus()
except ConnectionError as err:
    print "Could not send data, err={0}".format(err)

print '\n\n================== Step 4. Disconnecting from the device =========='

print '\n=====\nDisconnecting from IP mote'
try:
    connector.disconnect()
except ConnectionError as err:
    print err
    raw_input('\nScript ended. Press Enter to exit.')
print 'done.'

raw_input('\nScript ended. Press Enter to exit.')