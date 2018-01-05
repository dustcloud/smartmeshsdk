#!/usr/bin/python
'''
This script subscribes to data notifications and waits for Blink packets.
'''

#============================ adjust path =====================================

import sys
import os
if __name__ == "__main__":
    here = sys.path[0]
    sys.path.insert(0, os.path.join(here, '..', 'libs'))
    sys.path.insert(0, os.path.join(here, '..', 'external_libs'))

#============================ imports =========================================

import urllib3
import traceback
import base64
import certifi

# generic SmartMeshSDK imports
from SmartMeshSDK                      import sdk_version
from SmartMeshSDK.protocols.blink      import blink
# VManager-specific imports
from VManagerSDK.vmanager              import Configuration
from VManagerSDK.vmgrapi               import VManagerApi
from VManagerSDK.vmanager.rest         import ApiException

#============================ defines =========================================

DFLT_VMGR_HOST     = "127.0.0.1"

urllib3.disable_warnings() # disable warnings that show up about self-signed certificates

#============================ helpers =========================================

def process_data(data_notif):
    payload = base64.b64decode(data_notif.payload)
    try:
        (data,neighbors) = blink.decode_blink(payload)
        if data:
            print 'Blink packet received from {0}'.format(data_notif.mac_address)
            for neighbor_id, rssi in neighbors:
                print '    --> Neighbor ID = {0},  RSSI = {1}'.format(neighbor_id, rssi)
            if not neighbors:
                print '    --> Neighbors = n/a'            
            print '    --> Data Sent = {0}\n\n'.format(data.encode("hex"))
    except: 
        # handle non-blink data
        pass

#============================ main ============================================

try:
    # print banner
    print '\nVMgr_BlinkData (c) Dust Networks'
    print 'SmartMesh SDK {0}\n'.format('.'.join([str(i) for i in sdk_version.VERSION]))

    mgrhost = raw_input('Enter the IP address of the manager (e.g. {0} ): '.format(DFLT_VMGR_HOST))
    if mgrhost == "":
        mgrhost = DFLT_VMGR_HOST

    # log in as user "dust"
    config = Configuration()
    config.username     = 'dust'
    config.password     = 'dust'
    config.verify_ssl   = False
    
    if os.path.isfile(certifi.where()):
        config.ssl_ca_cert  = certifi.where()
    else:
        config.ssl_ca_cert = os.path.join(os.path.dirname(sys.executable), "cacert.pem")

    # initialize the VManager Python library
    voyager = VManagerApi(host=mgrhost)

    # start listening for data notifications
    voyager.get_notifications('data', notif_callback=process_data)

    print '\n==== Subscribing to all Blink data notifications'
    reply = raw_input ('Waiting for notifications , Press any key to stop\n\n')

    voyager.stop_notifications()
    print 'Script ended normally'

except:
    traceback.print_exc()
    print ('Script ended with an error.')
    sys.exit()
