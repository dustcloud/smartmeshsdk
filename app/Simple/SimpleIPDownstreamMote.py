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

#============================ main ============================================

try:
    print 'SimpleIPDownstreamMote (c) Dust Networks'
    print 'SmartMesh SDK {0}\n'.format('.'.join([str(b) for b in sdk_version.VERSION]))
    print 'Note: Use with SimpleIPDownstreamMgr\n'
    
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
    
    try:
        while True:
            input = moteconnector.getNotificationInternal(-1)
            if input[0]==['receive']:
                print 'received "{0}" from {1}'.format(
                    ''.join([chr(i) for i in input[1]["payload"]]),
                    '-'.join(['%02x'%b for b in input[1]["srcAddr"]]),
                )
    except KeyboardInterrupt:
        pass
    
    #=====
    print '-  close everything'
    
    moteconnector.disconnect()
    
    print 'Script ended normally.'

except:
    traceback.print_exc()
    print 'Script ended with an error.'

raw_input('Press Enter to close.')
