#!/usr/bin/env python
'''
This example subscribes to the data notifications and prints out the total
number of packets received from all motes, and calculates average packets
per second arriving at the manager.
'''

#============================ adjust path =====================================

import sys
import os
from builtins import input
if __name__ == "__main__":
    here = sys.path[0]
    sys.path.insert(0, os.path.join(here, '..', 'libs'))
    sys.path.insert(0, os.path.join(here, '..', 'external_libs'))

#============================ imports =========================================

import urllib3
import traceback
import time
import base64
import certifi

# generic SmartMeshSDK imports
from SmartMeshSDK                      import sdk_version
# VManager-specific imports
from VManagerSDK.vmanager              import Configuration
from VManagerSDK.vmgrapi               import VManagerApi
from VManagerSDK.vmanager.rest         import ApiException

#============================ defines =========================================

DFLT_VMGR_HOST     = "127.0.0.1"

urllib3.disable_warnings() # disable warnings that show up about self-signed certificates

#============================ variables =======================================

notif_count        = 0

#============================ helpers =========================================

def process_data(mydata):
    '''
    Process data notifications
    Checks whether the notification came from the desired MAC address, 
    then prints latency data and calculates average and max latencies.
    '''
    global notif_count
    #global latency_total, latency_max

    notif_count += 1
    # TODO: calculate overall latency

def process_notif(notif):
    '''Dispatch notifications to specific processing functions'''
    if notif.type in ('dataPacketReceived', 'ipPacketReceived'):
        # handle data notifications
        process_data(notif)
    else:
        # handle other event notifications
        pass


#============================ main ============================================

try:
    # print script name and SmartMesh SDK version
    print ('\nVMgr_PktPerSec (c) Dust Networks')
    print ('SmartMesh SDK {0}\n'.format('.'.join([str(i) for i in sdk_version.VERSION])))
    
    mgrhost = input('Enter the IP address of the manager (e.g. {0} ): '.format(DFLT_VMGR_HOST))
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
    print ('\n==== Display current network Configuration')
    print (netConfig)

    # start listening for data notifications
    print ('\n==== Subscribe to data notifications and display Average pkt/sec')
    print ('         Ctrl C to stop')
    voyager.get_notifications('data', notif_callback=process_notif)

    # report the number of notifications received
    previous_count = 0
    while True:
        avg_per_second = (notif_count - previous_count)/30.0
        previous_count = notif_count
        print(' Total so far = {0} --> Average pkt/sec = {1}'.format(notif_count, avg_per_second))
        time.sleep(30)

    voyager.stop_notifications()

except:
    traceback.print_exc()
    print ('Script ended with an error.')
    sys.exit()
