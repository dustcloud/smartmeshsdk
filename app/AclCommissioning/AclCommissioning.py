#!/usr/bin/python

#============================ adjust path =====================================

import sys
import os
if __name__ == "__main__":
    here = sys.path[0]
    sys.path.insert(0, os.path.join(here, '..', '..','libs'))
    sys.path.insert(0, os.path.join(here, '..', '..','external_libs'))

#============================ verify installation =============================

from SmartMeshSDK.utils import SmsdkInstallVerifier
(goodToGo,reason) = SmsdkInstallVerifier.verifyComponents(
    [
        SmsdkInstallVerifier.PYTHON,
        SmsdkInstallVerifier.PYSERIAL,
    ]
)
if not goodToGo:
    print "Your installation does not allow this application to run:\n"
    print reason
    raw_input("Press any button to exit")
    sys.exit(1)

#============================ imports =========================================

import random
import traceback
from SmartMeshSDK                       import sdk_version
from SmartMeshSDK.IpMgrConnectorSerial  import IpMgrConnectorSerial
from SmartMeshSDK.IpMoteConnector       import IpMoteConnector
from SmartMeshSDK.utils                 import AppUtils, \
                                               FormatUtils

#============================ logging =========================================

# local
import logging
class NullHandler(logging.Handler):
    def emit(self, record):
        pass
log = logging.getLogger('App')
log.setLevel(logging.ERROR)
log.addHandler(NullHandler())

# global
AppUtils.configureLogging()

#============================ defines =========================================

DEFAULT_MGRSERIALPORT   = 'COM15'
DEFAULT_MOTESERIALPORT  = 'COM19'

#============================ helper functions ================================

#============================ main ============================================

try:
    manager        = IpMgrConnectorSerial.IpMgrConnectorSerial()
    mote           = IpMoteConnector.IpMoteConnector()
    
    print 'ACL Commissioning (c) Dust Networks'
    print 'SmartMesh SDK {0}\n'.format('.'.join([str(b) for b in sdk_version.VERSION]))
    
    print '==== Connect to manager'
    serialport     = raw_input("Serial port of SmartMesh IP Manager (e.g. {0}): ".format(DEFAULT_MGRSERIALPORT))
    serialport     = serialport.strip()
    if not serialport:
        serialport = DEFAULT_MGRSERIALPORT
    manager.connect({'port': serialport})
    print 'Connected to manager at {0}.\n'.format(serialport)
    
    #===== Connect to the mote, get MAC, create a join key, and configure it
    # Then keep going in a loop until the last mote is done
    
    motecount      = 1
    try:
        while True:
            print '==== Connect mote {0} to your computer (or Ctrl+C to quit)'.format(motecount)
            
            serialport = raw_input("    Serial port of SmartMesh IP Mote (e.g. {0}): ".format(DEFAULT_MOTESERIALPORT))
            serialport = serialport.strip()
            if not serialport:
                serialport = DEFAULT_MOTESERIALPORT
            mote.connect({'port': serialport})
            print '    Connected to mote at {0}.'.format(serialport)        
            
            joinKey = [random.randint(0x00,0xff) for _ in range(16)]
            print '    Random join key: {0}'.format(FormatUtils.formatBuffer(joinKey))
            
            macAddress = mote.dn_getParameter_macAddress().macAddress
            print '    mote\'s MAC address: {0}'.format(FormatUtils.formatBuffer(macAddress))
            
            print '    Writing joinKey in mote...',
            mote.dn_setParameter_joinKey(
                joinKey      = joinKey
            )
            print 'done.'
            
            print '    Configuring joinKey in manager...',
            manager.dn_setACLEntry(
                macAddress   = macAddress,
                joinKey      = joinKey,
            )
            print 'done.'
            
            print '    Disconnecting from mote...',
            mote.disconnect()
            print 'done.'
            print ''
            
            motecount += 1
    except KeyboardInterrupt:
        pass
    
    print '\n\n==== disconnect from manager'
    manager.disconnect()
    print 'done.\n'

except Exception as err:
    output  = []
    output += ['=============']
    output += ['CRASH']
    output += [str(err)]
    output += [traceback.format_exc()]
    print '\n'.join(output)
else:
    print 'Script ended normally'
finally:
    raw_input("Press Enter to close.")
