#!/usr/bin/python

#============================ adjust path =====================================

import sys
import os
if __name__ == "__main__":
    here = sys.path[0]
    sys.path.insert(0, os.path.join(here, '..', '..','libs'))
    sys.path.insert(0, os.path.join(here, '..', '..','external_libs'))

#============================ imports =========================================

import traceback

from SmartMeshSDK                       import sdk_version
from SmartMeshSDK.IpMgrConnectorSerial  import IpMgrConnectorSerial
from SmartMeshSDK.IpMgrConnectorMux     import IpMgrSubscribe

#============================ helper functions ================================

def handle_data(notifName, notifParams):
    print '   Received from mote {0}: "{1}"'.format(
        '-'.join(['%02x'%b for b in notifParams.macAddress]),
        ''.join([chr(i) for i in notifParams.data])
    )

#============================ main ============================================

try:
    print 'SimpleIPUpstreamMgr (c) Dust Networks'
    print 'SmartMesh SDK {0}\n'.format('.'.join([str(b) for b in sdk_version.VERSION]))
    print 'Note: Use with SimpleIPUpstreamMote\n'
    
    #=====
    print "- create the variable 'mgrconnector'"
    
    mgrconnector  = IpMgrConnectorSerial.IpMgrConnectorSerial()
    
    #===== 
    print "- connect to the manager's serial port"
    
    serialport     = raw_input("Enter the serial API port of SmartMesh IP Manager (e.g. COM7): ")
    mgrconnector.connect({'port': serialport})
    
    #=====
    print "- subscribe to data notifications "
    
    subscriber = IpMgrSubscribe.IpMgrSubscribe(mgrconnector)
    subscriber.start()
    subscriber.subscribe(
        notifTypes =    [
                            IpMgrSubscribe.IpMgrSubscribe.NOTIFDATA,
                        ],
        fun =           handle_data,
        isRlbl =        False,
    )

    #===
    raw_input("Press any key to stop.")
    
    mgrconnector.disconnect()
    
    print 'Script ended normally.'

except:
    traceback.print_exc()
    print 'Script ended with an error.'
    
raw_input('Press Enter to close.')

