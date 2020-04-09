#!/usr/bin/python
'''
This script subscribes to data notifications looking for an OAP packet from
the default Dust mote application. If the packet payload is from this app,
and it is a temperature notification, the temperature is printed out
and published to the Grafana instance at http://clouddata.dustcloud.org/
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
import requests
import json
import base64
import argparse
from   array import array
import certifi

# generic SmartMeshSDK imports
from SmartMeshSDK                      import sdk_version
from SmartMeshSDK.protocols.oap        import OAPMessage, \
                                              OAPNotif 
# VManager-specific imports
from VManagerSDK.vmanager              import Configuration
from VManagerSDK.vmgrapi               import VManagerApi
from VManagerSDK.vmanager.rest         import ApiException

#============================ defines =========================================

DFLT_VMGR_HOST     = '127.0.0.1'
DFLT_VMGR_PORT     = 8888
DFLT_DB_HOST       = 'clouddata.dustcloud.org'
DFLT_DB_PORT       = 80

urllib3.disable_warnings() # disable warnings that show up about self-signed certificates

#============================ helpers =========================================

def handle_oap_notif(mac, oap_notif):
    '''
    Forward the data to the DB host.
    '''
    global db_host, db_port

    if isinstance(oap_notif, OAPNotif.OAPTempSample):
        temp = oap_notif.samples[0] / 100.0
        try:
            r = requests.post(
                "http://{0}:{1}/api/v1/oap".format(db_host, db_port),
                data = json.dumps({
                    'mac':          mac,
                    'temperature':  temp,
                }),
                headers = {
                    'Content-type': 'application/json',
                }
            )
        except Exception as err:
            print (err)
        else:
            print ('sent mac={0} temperature={1:.2f}C'.format(mac, temp))

def process_data(data_notif):
    '''
    Parse data notifications containing OAP sensor data.
    '''
    # TODO: use the OAPDispatcher for parsing notifications
    time = data_notif.gen_net_time.strftime("%m-%d %H:%M:%S")
    payload = array('B', base64.b64decode(data_notif.payload))
    # OAP message starts at byte 2
    if len(payload) > 3 and payload[2] == OAPMessage.CmdType.NOTIF:
        oap_notif = OAPNotif.parse_oap_notif(payload, 3) # start at byte 3
        handle_oap_notif(data_notif.mac_address, oap_notif)

#============================ main ============================================

try:
    # print banner
    print ('\nVMgr_PublishToWeb (c) Dust Networks')
    print ('SmartMesh SDK {0}'.format('.'.join([str(b) for b in sdk_version.VERSION])))

    parser = argparse.ArgumentParser()
    parser.add_argument(
        '--vmgr_host',
        default    = DFLT_VMGR_HOST,
        help       = "VManager host to connect to for mote data",
    )
    parser.add_argument(
        '--vmgr_port',
        default    = DFLT_VMGR_PORT,
        help       = "VManager API port to connect to for mote data",
    )
    parser.add_argument(
        '--db_host',
        default    = DFLT_DB_HOST,
        help       = "Database server to forward data to",
    )
    parser.add_argument(
        '--db_port',
        default    = DFLT_DB_PORT,
        help       = "Port to forward data to on the DB host",
    )
    options = parser.parse_args()

    db_host = options.db_host
    db_port = options.db_port

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
    voyager = VManagerApi(host=options.vmgr_host, port=options.vmgr_port)

    # start listening for data notifications
    voyager.get_notifications('data', notif_callback=process_data)

    print ('\n==== Subscribing to data notifications and publish to clouddata.dustcloud.org')
    reply = input('Forwarding notifications. Press any key to stop\n\n')

    voyager.stop_notifications()
    print ('Script ended normally')

except:
    traceback.print_exc()
    print ('Script ended with an error.')
    voyager.stop_notifications()
    sys.exit()
