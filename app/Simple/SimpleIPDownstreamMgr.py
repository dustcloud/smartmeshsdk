#!/usr/bin/python

#============================ adjust path =====================================

import sys
import os
if __name__ == "__main__":
    here = sys.path[0]
    sys.path.insert(0, os.path.join(here, '..', '..','libs'))
    sys.path.insert(0, os.path.join(here, '..', '..','external_libs'))

#============================ imports =========================================

import time
import traceback

from SmartMeshSDK                       import sdk_version
from SmartMeshSDK.IpMgrConnectorSerial  import IpMgrConnectorSerial
from SmartMeshSDK.IpMgrConnectorMux     import IpMgrSubscribe
from SmartMeshSDK.ApiException          import APIError

#============================ defines =========================================

UDP_PORT_NUMBER         = 60000
STRING_TO_PUBLISH       = "Hello, World!"
PUBLISH_RATE_SEC        = 5

#============================ main ============================================

try:
    print 'SimpleIPDownstreamMgr (c) Dust Networks'
    print 'SmartMesh SDK {0}\n'.format('.'.join([str(b) for b in sdk_version.VERSION]))
    print 'Note: Use with SimpleIPDownstreamMote\n'
    
    #=====
    print "- create the variable 'mgrconnector'"
    
    mgrconnector  = IpMgrConnectorSerial.IpMgrConnectorSerial()
    
    #===== 
    print "- connect to the manager's serial port"
    
    serialport     = raw_input("Enter the serial API port of SmartMesh IP Manager (e.g. COM7): ")
    mgrconnector.connect({'port': serialport})
    
    #=====
    print "- retrieve the list of all connected motes"
    
    operationalMacs     = []
    currentMac          = (0,0,0,0,0,0,0,0) # start getMoteConfig() iteration with the 0 MAC address
    continueAsking      = True
    while continueAsking:
        try:
            res = mgrconnector.dn_getMoteConfig(currentMac,True)
        except APIError:
            continueAsking = False
        else:
            if ((not res.isAP) and (res.state in [4,])):
                operationalMacs += [res.macAddress]
            currentMac = res.macAddress
    
    print "Found the following operational motes:"
    for mac in operationalMacs:
        print ' - '+'-'.join(['%02x'%b for b in mac])
    
    #=====
    print "- start sending data"
    print "Note: this is an infinite loop, close the window to end the script"
    
    while True:
        for mac in operationalMacs:
            
            # send
            mgrconnector.dn_sendData(
                macAddress   = mac,
                priority     = 0,
                srcPort      = UDP_PORT_NUMBER,
                dstPort      = UDP_PORT_NUMBER,
                options      = 0,
                data         = [ord(i) for i in STRING_TO_PUBLISH],
            )
            
            # print
            print '   Just sent "{0}" to {1}, next in {2}s'.format(
                STRING_TO_PUBLISH,
                '-'.join(['%02x'%b for b in mac]),
                PUBLISH_RATE_SEC,
            )
            
            # wait a bit before sending again
            time.sleep(PUBLISH_RATE_SEC)

except:
    traceback.print_exc()
    print 'Script ended with an error.'
    
raw_input('Press Enter to close.')

