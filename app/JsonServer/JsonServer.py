#!/usr/bin/python

#============================ adjust path =====================================

import sys
import os
if __name__ == "__main__":
    here = sys.path[0]
    sys.path.insert(0, os.path.join(here, '..', '..','libs'))
    sys.path.insert(0, os.path.join(here, '..', '..','external_libs'))

#============================ define ==========================================

DEFAULT_SERIALPORT = 'COM15'

#============================ imports =========================================

from bottle.bottle import get,post,run,static_file,request

from SmartMeshSDK import sdk_version
from SmartMeshSDK.IpMgrConnectorSerial import IpMgrConnectorSerial

#===== print banner

print 'JsonServer - SmartMesh SDK {0} (c) Dust Networks\n'.format('.'.join([str(b) for b in sdk_version.VERSION]))

#===== connect to manager

serialport = raw_input("serial port of SmartMesh IP Manager (e.g. {0}): ".format(DEFAULT_SERIALPORT))
serialport = serialport.strip()
if not serialport:
    serialport = DEFAULT_SERIALPORT

manager = IpMgrConnectorSerial.IpMgrConnectorSerial()
try:
    manager.connect({'port': serialport})
except Exception as err:
    print 'failed to connect to manager at {0}'.format(serialport)
    raw_input('Aborting. Press Enter to close.')
    sys.exit(1)
else:
    print 'ok. connected to manager at {0}'.format(serialport)

#===== start JSON server

@get('/static/<filename>')
def server_static(filename):
    return static_file(filename, root='static/')

@get('/')
def root_get():
    return static_file('index.html', root='.')

@post('/')
def root_post():
    mac    = request.json['mac']
    state  = request.json['state']
    
    mac    = [int(b,16) for b in mac.split('-')]
    
    manager.dn_sendData(
        macAddress      = mac,
        priority        = 1,
        srcPort         = 0xf0b9,
        dstPort         = 0xf0b9,
        options         = 0,
        data            = [
            0x05,            # un-ACK'ed transport, resync connection
            0x00,            # seqnum and session
            0x02,            # "PUT" command
            0xff,            # ==TLV== address (0xff)
            0x02,            #         length (2)
            0x03,            #         digital_out (3)
            0x02,            #         Actuate LED (2)
            0x00,            # ==TLV== Value (0x00)
            0x01,            #         length (1)
            state,           # set pin high or low
        ]
    )
    
    sys.stdout.write('.')

print 'ok. JSON server started on port 8080'
run(host='localhost', port=8080, quiet=True)
