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
from SmartMeshSDK.IpMoteConnector       import IpMoteConnector

#============================ defines =========================================

UDP_PORT_NUMBER         = 60000
STRING_TO_PUBLISH       = "Hello, World!"
PUBLISH_RATE_SEC        = 5

#============================ main ============================================

try:
    print 'SimpleIPUpstreamMote (c) Dust Networks'
    print 'SmartMesh SDK {0}\n'.format('.'.join([str(b) for b in sdk_version.VERSION]))
    print 'Note: Use with SimpleIPUpstreamMgr\n'
    
    #=====
    print "- create the variable 'moteconnector'"
    
    moteconnector  = IpMoteConnector.IpMoteConnector()
    
    #===== 
    print "- connect to the mote's serial port"
    
    serialport     = raw_input("Enter the serial API port of SmartMesh IP Mote (e.g. COM15): ")
    moteconnector.connect({'port': serialport})

    #=====
    print "- have the mote join and wait until it reaches operational state"
    
    while True:
        res = moteconnector.dn_getParameter_moteStatus()
        print "   current mote state: {0}".format(res.state)
        if   res.state==1:
            res    = moteconnector.dn_join()
        elif res.state==5:
            break
        time.sleep(1)

    #=====
    print "- setup a socket"
        
    # open a socket
    res = moteconnector.dn_openSocket(0)
    socketId = res.socketId
    
    # bind socket to a UDP port
    moteconnector.dn_bindSocket(socketId,UDP_PORT_NUMBER)
    
    #=====
    print "- request a service"
    
    res = moteconnector.dn_requestService(
        destAddr             = 0xfffe,                # destination mote (0xfffe=manager)
        serviceType          = 0,                     # type (0=bandwidth)
        value                = 1000*PUBLISH_RATE_SEC  # expected Tx period (in ms)
    )
    
    #===== 
    print "- publish {0} every {1}s".format(STRING_TO_PUBLISH,PUBLISH_RATE_SEC)
    
    try:
        while True:
            
            # send data
            moteconnector.dn_sendTo(
                socketId    = socketId,
                destIP      = [
                    0xff, 0x02, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00,
                    0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x02,
                ],
                destPort    = UDP_PORT_NUMBER,
                serviceType = 0,
                priority    = 1,
                packetId    = 0xffff,
                payload     = [ord(i) for i in STRING_TO_PUBLISH],
            )
            
            # print
            print '   Just sent "{0}", next transmission in {1}s'.format(STRING_TO_PUBLISH,PUBLISH_RATE_SEC)
            
            # wait a bit before sending again
            time.sleep(PUBLISH_RATE_SEC)
        
    except KeyboardInterrupt:
        pass
     
    #=====
    print '-  close everything'
    res = moteconnector.dn_closeSocket(socketId)
    
    moteconnector.disconnect()
    
    print 'Script ended normally.'

except:
    traceback.print_exc()
    print 'Script ended with an error.'

raw_input('Press Enter to close.')
