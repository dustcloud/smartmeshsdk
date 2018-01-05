#!/usr/bin/python
'''
Basic example script talking to a VManager using the Python library.
Prints out network settings, changes and updates a config value, and
subscribes to data notifications and prints packets that are received.
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
from VManagerSDK.vmanager              import SystemWriteConfig

#============================ defines =========================================

DFLT_VMGR_HOST           = "127.0.0.1"

urllib3.disable_warnings() # disable warnings that show up about self-signed certificates

#============================ helpers =========================================

def process_data(mydata):
    '''
    Processes received data. Prints MAC address of source and packet content.
    '''
    macaddr = mydata.mac_address
    datapayload = int((base64.b64decode(mydata.payload)).encode('hex'),16)
    print ' Data from mote {0} --> {1}'.format(macaddr, datapayload)
    
#============================ main ============================================

try:
    # print banner
    print '\nVMgr_BasicExample (c) Dust Networks'
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

    # read and display network configuration
    netConfig = voyager.networkApi.get_network_config()
    print '\n==== Display current network Configuration'
    print netConfig

    # update system configuration
    sysConfig = SystemWriteConfig()
    sysConfig.location = "California"
    voyager.systemApi.update_system_config(sysConfig)

    # read a configuration setting
    mysetting = voyager.systemApi.get_system_config()
    print '\n==== Set and display current location'
    print mysetting.location

    # start listening for data notifications
    voyager.get_notifications('data', notif_callback=process_data)

    print '\n==== Subscribe to data notifications and display'
    reply = raw_input ('Waiting for notifications , Press any key to stop\n\n')

    voyager.stop_notifications()
    print 'Script ended normally'

except:
    traceback.print_exc()
    print ('Script ended with an error.')
    voyager.stop_notifications()
    sys.exit()
