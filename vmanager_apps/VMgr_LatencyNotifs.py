#!/usr/bin/python
'''
This script subscribes to Data notifications and prints out the latency for
every packet that is received by the manager.
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
# VManager-specific imports
from VManagerSDK.vmanager              import Configuration
from VManagerSDK.vmgrapi               import VManagerApi
from VManagerSDK.vmanager.rest         import ApiException

#============================ defines =========================================

DFLT_MGR_HOST      = "127.0.0.1"

urllib3.disable_warnings() # disable warnings that show up about self-signed certificates

#============================ helpers =========================================

def process_data(mydata):
    '''
    Processes latency data, prints MAC address and latency of the packet
    '''
    print(' Latency for mote {0} --> {1}'.format(mydata.mac_address,mydata.latency))
    
#============================ main ============================================

try:
    # print banner
    print '\nVMgr_LatencyNotifs (c) Dust Networks'
    print 'SmartMesh SDK {0}\n'.format('.'.join([str(i) for i in sdk_version.VERSION]))

    mgrhost = raw_input('Enter the IP address of the manager (e.g. {0}): '.format(DFLT_MGR_HOST))
    if mgrhost == "":
        mgrhost = DFLT_MGR_HOST

    # log-in as user "dust"
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

    # read and display network configuration
    netConfig = voyager.networkApi.get_network_config()
    print ('Current network configuration is ...\n {0}'.format(netConfig))

    # start listening for data notifications
    voyager.get_notifications('data', notif_callback=process_data)

    print '\n==== Subscribing to data notifications'
    reply = raw_input ('\n Waiting for notifications , Press any key to stop\n')

    voyager.stop_notifications()
    print 'Script ended normally'

except:
    traceback.print_exc()
    print ('Script ended with an error.')
    voyager.stop_notifications()
    sys.exit()
