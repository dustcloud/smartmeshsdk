#!/usr/bin/python
'''
This script subscribes to data notifications looking for an OAP packet
from the Default Dust mote Temperature application. If the packet payload
is from this app, the temperature will be printed out.
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
from array import array
import certifi

# generic SmartMeshSDK imports
from SmartMeshSDK                      import sdk_version
from SmartMeshSDK.protocols.oap        import OAPDispatcher, \
                                              OAPClient,     \
                                              OAPMessage,    \
                                              OAPNotif
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
    Parse OAP notification with sensor data
    '''
    time      = mydata.gen_net_time.strftime("%m-%d %H:%M:%S")
    payload   = array('B', base64.b64decode(mydata.payload))
    # OAP message starts at byte 2
    if len(payload)>3 and payload[2]==OAPMessage.CmdType.NOTIF:
        oap_notif = OAPNotif.parse_oap_notif(payload, 3) # start at byte 3
        if oap_notif and oap_notif.channel==OAPNotif.TEMP_ADDRESS:
            temp = oap_notif.samples[0] / 100.0
            print '{0}: Temperature from mote {1}: {2} Deg Celsius'.format(time, mydata.mac_address, temp)

def show_disconnect():
    print 'Notification connection closed'

#============================ main ============================================

try:
    # print banner
    print '\nVMgr_TemperatureData (c) Dust Networks'
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

    # Start listening for data notifications
    voyager.get_notifications(
        'data',
        notif_callback       = process_data, 
        disconnect_callback  = show_disconnect,
    )

    print '\n==== Subscribing to data notifications'
    reply = raw_input ('Waiting for notifications. Press any key to stop\n\n')

    voyager.stop_notifications()
    print 'Script ended normally'

except:
    traceback.print_exc()
    print ('Script ended with an error.')
    sys.exit()
