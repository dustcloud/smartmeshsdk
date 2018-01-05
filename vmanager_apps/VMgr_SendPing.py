#!/usr/bin/python
'''
This script sends a ping to a specific mote and waits for the pingResponse
notification. If any other pingResponses are received, the program
continues listening and waits until the correct one is received.
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
import threading
import traceback
import time
import certifi

# generic SmartMeshSDK imports
from SmartMeshSDK                      import sdk_version
# VManager-specific imports
from VManagerSDK.vmanager              import Configuration
from VManagerSDK.vmgrapi               import VManagerApi
from VManagerSDK.vmanager.rest         import ApiException

#============================ defines =========================================

DFLT_MGR_HOST      = "127.0.0.1"
DFLT_MOTE_MAC      = "00-17-0D-00-00-60-08-DC"

urllib3.disable_warnings() # disable warnings that show up about self-signed certificates

#============================ variables =======================================

mote_exists        = False
stop_event         = threading.Event()

#============================ helpers =========================================

def process_event(mydata):
    global macaddr, myresponse, stop_event

    if macaddr == mydata.mac_address and myresponse.callback_id == mydata.callback_id: 
        print '\nPing response from mote {0} with callbackID = {1}'.format(mydata.mac_address, mydata.callback_id)
        print '  returned with result --> {0}'.format(mydata.result)
        print '  date and time --> {0}'.format(mydata.sys_time)
        print '  latency of response --> {0} mSec'.format(mydata.latency)
        print '  mote at hop --> {0}'.format(mydata.hop_count)
        print '  mote voltage reading = {0} v, and temperature = {1} C'.format(mydata.voltage, mydata.temperature)
        stop_event.set()
    else:
        print ('\nReceived a ping response, but either different mote or wrong callbackID... still waiting --> {0} , {1}\n'.format(mydata.mac_address, mydata.callback_id))
    
def process_notif(notif):
    '''
    Dispatch notifications to specific processing functions.
    '''
    if notif.type in ('pingResponse'):
        # handle ping response notifications
        process_event(notif)
    else:
        # handle other event notifications
        pass

#============================ main ============================================

try:
    # print banner
    print '\nVMgr_SendPing (c) Dust Networks'
    print 'SmartMesh SDK {0}\n'.format('.'.join([str(i) for i in sdk_version.VERSION]))

    mgrhost = raw_input('Enter the IP address of the manager (e.g. {0}): '.format(DFLT_MGR_HOST))
    if mgrhost == "":
        mgrhost = DFLT_MGR_HOST

    macaddr = raw_input('Enter MAC address of mote to Ping (e.g. {0}): '.format(DFLT_MOTE_MAC))
    if macaddr == "":
        macaddr = DFLT_MOTE_MAC
    macaddr = macaddr.upper() # make sure all letters are upper case

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

    # first test that the mote does exist and is operational
    print '\n==== Verifying that the mote requested is in network and Operational'
    mote_list = voyager.motesApi.get_motes()
    for mote in mote_list.motes:
        if mote.mac_address == macaddr and mote.state == "operational":
            mote_exists = True

    if mote_exists:
        print '\n==== Sending Ping to the mote and wait for the response'
        # start listening for data notifications
        voyager.get_notifications('events', notif_callback=process_notif)

        # send a ping to the mote
        myresponse = voyager.motesApi.ping_mote(macaddr)
        print '  Ping sent to mote {0}, callback = {1}'.format(macaddr, myresponse.callback_id)
    
        # wait for the pingNotification response and then exit the program
        print '\n  Waiting for the pingResponse notification'
        stop_event.wait()
        voyager.stop_notifications()
        print '\nScript ended normally'
    else:
        print '\n  This MAC address is not joined to this network'

except:
    traceback.print_exc()
    print ('Script ended with an error.')
    sys.exit()
