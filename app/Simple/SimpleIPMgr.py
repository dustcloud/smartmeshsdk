#!/usr/bin/python

#============================ adjust path =====================================

import sys
import os
if __name__ == "__main__":
    here = sys.path[0]
    sys.path.insert(0, os.path.join(here, '..', '..','libs'))
    sys.path.insert(0, os.path.join(here, '..', '..','external_libs'))

#============================ imports =========================================

from SmartMeshSDK.IpMgrConnectorMux import IpMgrConnectorMux
from SmartMeshSDK.ApiException      import ConnectionError,  \
                                           CommandTimeoutError

#============================ defines =========================================

DEFAULT_MUXHOST = '127.0.0.1'
DEFAULT_MUXPORT = 9900

#============================ main ============================================

print 'Simple Application which interacts with the IP manager - (c) Dust Networks'

print '\n\n================== Step 1. Connecting to the manager =============='

connect = raw_input('\nDo you want to connect to a manager over SerialMux? [y/n] ')

if connect.strip()!='y':
    raw_input('\nScript ended. Press Enter to exit.')
    sys.exit()

muxHost = raw_input('\nEnter the SerialMux\'s host (leave blank for '+DEFAULT_MUXHOST+') ')
if not muxHost:
    muxHost = DEFAULT_MUXHOST
   
muxPort = raw_input('\nEnter the SerialMux\'s port (leave blank for '+str(DEFAULT_MUXPORT)+') ')
if muxPort:
    muxPort = int(muxPort)
else:
    muxPort = DEFAULT_MUXPORT

print '\n=====\nCreating connector'
connector = IpMgrConnectorMux.IpMgrConnectorMux()
print 'done.'

print '\n=====\nConnecting to IP manager'
try:
    connector.connect({
                        'host': muxHost,
                        'port': muxPort,
                     })
except ConnectionError as err:
    print err
    raw_input('\nScript ended. Press Enter to exit.')
    sys.exit(1)
print 'done.'

print '\n\n================== Step 2. Getting information from the network ===='

print '\n=====\nRetrieve the network info'
try:
    print connector.dn_getNetworkInfo()
except (ConnectionError,CommandTimeoutError) as err:
    print "Could not send data, err={0}".format(err)

print '\n\n================== Step 3. Disconnecting from the device =========='

print '\n=====\nDisconnecting from IP manager'
try:
    connector.disconnect()
except (ConnectionError,CommandTimeoutError) as err:
    print err
print 'done.'

raw_input('\nScript ended. Press Enter to exit.')
