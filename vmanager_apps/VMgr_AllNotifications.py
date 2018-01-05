#!/usr/bin/env python
'''
This script subscribes to all notifications and prints out the type of
notification which was received
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

urllib3.disable_warnings() # disable warnings that show up about self-signed certificates

#============================ helpers =========================================

def process_notif(notif):
    '''
    Dispatch notifications to specific processing functions.
    '''
    if   notif.type in (
            'dataPacketReceived',
            'ipPacketReceived'
        ):
        # handle data notifications
        print ' Data notification --> Type={0}'.format(notif.type)

    elif notif.type in (
            'deviceHealthReport', 
            'discoveryHealthReport',
            'neighborHealthReport',
            'rawMoteNotification',
        ):
        # handle health reports
        print '   HR notification --> Type={0}'.format(notif.type)
        
    elif notif.type in (
            'configChanged', 
            'configDeleted', 
            'configLoaded', 
            'configRestored',
        ):
        # handle config notifications
        print '     Config notification --> Type={0}'.format(notif.type)
        
    else:
        # handle all other event notifications
        print '       Event notification --> Type={0}'.format(notif.type)

#============================ main ============================================

try:
    # print banner
    print '\nVMgr_AllNotifications (c) Dust Networks'
    print 'SmartMesh SDK {0}\n'.format('.'.join([str(i) for i in sdk_version.VERSION]))

    # ask the user which Manager IP to connect to, and which mote to monitor
    mgrhost = raw_input('Enter the IP address of the manager (e.g. {0} ): '.format(DFLT_VMGR_HOST))
    if mgrhost == "":
        mgrhost = DFLT_VMGR_HOST

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

    # start listening for hr notifications
    voyager.get_notifications(notif_callback=process_notif)

    print '\n==== Subscribing to all notifications'
    reply = raw_input ('\n Waiting for notifications from mote, Press any key to stop\n')

    voyager.stop_notifications()
    print 'Script ended normally'

except:
    traceback.print_exc()
    print ('Script ended with an error.')
    sys.exit()
