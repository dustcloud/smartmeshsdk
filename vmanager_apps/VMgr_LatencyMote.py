#!/usr/bin/env python
'''
This script subscribes to data notifications from a desired mote and
reports the latency statistics.
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
import certifi

# generic SmartMeshSDK imports
from SmartMeshSDK                      import sdk_version
# VManager-specific imports
from VManagerSDK.vmanager              import Configuration
from VManagerSDK.vmgrapi               import VManagerApi
from VManagerSDK.vmanager.rest         import ApiException

#============================ defines =========================================

DFLT_VMGR_HOST     = "127.0.0.1"
DFLT_MOTE_MAC      = "00-17-0D-00-00-60-08-DC"

urllib3.disable_warnings() # disable warnings that show up about self-signed certificates

#============================ variables =======================================

notif_count        = 0
latency_total      = 0
latency_max        = 0

#============================ helpers =========================================

def process_data(mydata):
    '''Process data notifications
    Checks whether the notification came from the desired MAC address, 
    then prints latency data and calculates average and max latencies.
    '''
    global notif_count, latency_total, latency_max

    if macaddr == mydata.mac_address:
        mylatency = mydata.latency
        notif_count += 1
        latency_total += mylatency
        average = latency_total / notif_count
        if mylatency > latency_max:
            latency_max = mylatency
        print(' Mote {0} --> Latency {1} -- Average {2} -- Max {3}\n'.format(mydata.mac_address, mylatency, average, latency_max))

def process_notif(notif):
    '''
    Dispatch notifications to specific processing functions
    '''
    if   notif.type in (
            'dataPacketReceived',
            'ipPacketReceived',
        ):
        # handle data notifications
        process_data(notif)

    elif notif.type in (
            'deviceHealthReport', 
            'discoveryHealthReport',
            'neighborHealthReport',
        ):
        # handle health reports
        pass

    elif notif.type in (
            'configChanged', 
            'configDeleted', 
            'configLoaded', 
            'configRestored',
        ):
        # handle config notifications
        pass

    else:
        # handle other event notifications
        pass

#============================ main ============================================

try:
    # print banner
    print '\nVMgr_LatencyMote (c) Dust Networks'
    print 'SmartMesh SDK {0}\n'.format('.'.join([str(i) for i in sdk_version.VERSION]))

    # ask the user for VManager host
    mgrhost = raw_input('Enter the IP address of the manager (e.g. {0} ): '.format(DFLT_VMGR_HOST))
    if mgrhost == "":
        mgrhost = DFLT_VMGR_HOST

    # ask the user for mote's MAC address
    macaddr = raw_input('Enter MAC address of mote to Ping (e.g. {0}): '.format(DFLT_MOTE_MAC))
    if macaddr == "":
        macaddr = DFLT_MOTE_MAC
    macaddr = macaddr.upper() # make sure all letters are upper case

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

    # Start listening for data notifications
    voyager.get_notifications('data', notif_callback=process_notif)

    print '\n==== Subscribing to data notifications'
    reply = raw_input ('\n Waiting for notifications from mote, Press any key to stop\n')

    voyager.stop_notifications()
    print 'Script ended normally'

except:
    traceback.print_exc()
    print ('Script ended with an error.')
    sys.exit()
