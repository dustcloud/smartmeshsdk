#!/usr/bin/python
'''OTAP Communicator for VManager

The OTAP Communicator connects to the VManager. The default address
is local host (127.0.0.1), however any desired IP address can be entered with
the --host option.

To program a file (Linux, Cygwin):

$ python otap_communicator.py my-file.otap2

Or on Windows:

> \Python27\python bin\OTAPCommunicator\OTAPCommunicator.py my-file.otap2

For interactive mode (debugging), run:
$ python -i bin/OTAPCommunicator/OTAPCommunicator.py --nostart

'''

#============================ adjust path =====================================
from __future__ import print_function
import sys
import os
import json
if __name__ == "__main__":
    here = sys.path[0]
    sys.path.insert(0, os.path.join(here, '..', 'libs'))
    sys.path.insert(0, os.path.join(here, '..', 'external_libs'))

#============================ imports =========================================

# cryptopy.crypto wants to import parts of the crypto module without the
# cryptopy prefix
import cryptopy
sys.path.append(os.path.dirname(cryptopy.__file__)) 

import traceback
import base64
import binascii
import certifi

# generic SmartMeshSDK imports
from SmartMeshSDK.protocols.otap       import OTAPStructs
from SmartMeshSDK.protocols.otap       import OTAPCommunicator
from SmartMeshSDK                      import sdk_version
# VManager-specific imports
from VManagerSDK.vmanager              import Configuration
from VManagerSDK.vmgrapi               import VManagerApi
from VManagerSDK.vmanager.rest         import ApiException
from VManagerSDK.vmanager              import DataPacketSendInfo

# disable warnings that show up about self-signed certificates
import urllib3
urllib3.disable_warnings()

#============================ defines =========================================

def version_string():
    return '.'.join([str(v) for v in sdk_version.VERSION])

DFLT_VMGR_HOST     = '127.0.0.1'
PRIORITY           = "low"

OTAP_EXTENSIONS    = ['.otap', '.otap2']

#============================ logging =========================================

import logging
import logging.handlers

LOG_FILENAME = 'otap_communicator.log'
LOG_FORMAT   = "%(asctime)s [%(name)s:%(levelname)s] %(message)s"

# set up a specific logger with our desired output level
log = logging.getLogger('otap_communicator')
log.setLevel(logging.INFO)

# add the log message handler to the logger
handler = logging.handlers.RotatingFileHandler(
    LOG_FILENAME,
    maxBytes=2000000,
    backupCount=5,
)
handler.doRollover()

handler.setFormatter(logging.Formatter(LOG_FORMAT))
log.addHandler(handler)

# add our logger to the various libraries we use as well
LOGGERS = ['OTAPCommunicator', 'ReliableCmd', 'ApiConnector']
for l in LOGGERS:
    logging.getLogger(l).addHandler(handler)
    logging.getLogger(l).setLevel(logging.INFO)

#============================ command line options ============================

from optparse import OptionParser

otap_options = OTAPCommunicator.DEFAULT_OPTIONS

# Parse the command line
parser = OptionParser(
    "usage: %prog [options] <file(s)>...",
    version="OTAP Communicator " + version_string(),
)
parser.add_option("-v", "--verbose", dest="verbose", action="store_true",
                  default=False, 
                  help="Print verbose messages")
parser.add_option("--host", dest="host", 
                  default=DFLT_VMGR_HOST,
                  help="Host address of the VManager")
parser.add_option("-m", "--mote", dest="motes", default=[],
                  action="append",
                  help="List of mote(s) to send files")
parser.add_option("--delay", dest="delay", default=otap_options.inter_command_delay,
                  help="Length of delay between sending OTAP commands (seconds)")
parser.add_option("--nostart", dest="autorun", default=True,
                  action="store_false",
                  help="Don't start running the OTAP process automatically (use interactive mode)")
(options, args) = parser.parse_args()

if options.verbose:
    h = logging.StreamHandler(sys.stdout)
    h.setFormatter(logging.Formatter("[%(name)s:%(levelname)s] %(message)s"))
    for l in LOGGERS:
        logging.getLogger(l).addHandler(h)

# update values in OTAP options
otap_options = otap_options._replace(inter_command_delay=int(options.delay))

#============================ body ============================================

# create the client
config = Configuration()
config.username    = 'dust'
config.password    = 'dust'
config.verify_ssl  = False

if os.path.isfile(certifi.where()):
    config.ssl_ca_cert  = certifi.where()
else:
    config.ssl_ca_cert = os.path.join(os.path.dirname(sys.executable), "cacert.pem")

voyager = VManagerApi(host=options.host)

# Wrap a simple adapter around the manager's sendData method

def send_data(mac, msg, port):
    'Returns: the sendData response'
    msg_encoded = base64.b64encode(msg)
    # TODO: priority as enum
    rc = -1
    cbid = -1
    dataPacket = DataPacketSendInfo()
    dataPacket.src_port = port
    dataPacket.dest_port = port
    dataPacket.priority = PRIORITY
    dataPacket.payload = msg_encoded
    mac_str = '-'.join(["%02X" % b for b in mac])
    try:
        resp = voyager.motesApi.send_data_packet(mac_str,dataPacket)
        rc = OTAPCommunicator.OK
    except ApiException as exc:
        resp = exc.body
        resp = json.loads(resp)
        if 'errors' in resp:
            error = resp['errors'][0]
            if error['code'] == 1001:
                rc = OTAPCommunicator.END_OF_LIST
            elif error['code'] == 1011:
                if error['message'] == 'RPC timeout':
                    rc = OTAPCommunicator.DISCONNECTED
                else:
                    raise IOError(error.message)
            elif error['code'] == 1008:
                rc = OTAPCommunicator.NACK
            else:
                raise IOError(error['message'])
        else:
            raise exc
    # always return RC, callbackId
    return (rc, cbid)

from collections import namedtuple

Data = namedtuple('Data', 'mac src_port payload payload_str')

class NotifListener:
    def register(self, cb):
        self.otap_callback = cb
        voyager.get_notifications('data', notif_callback=self.process_notif)
        
    def process_notif(self,notif):
        if notif.type == 'dataPacketReceived':
            self.handle_data(notif)
        else:
            pass
        
    def handle_data(self, notif):
        try:
            # convert notif data into the OTAP Communicator data structure
            ps = base64.b64decode(notif.payload)
            dataPayload = [ord(b) for b in ps]
            mac_str = notif.mac_address.lower()
            mac = tuple([int(c, 16) for c in mac_str.split('-')])
            data = Data(mac, notif.src_port, dataPayload, ps)
            self.otap_callback(data)
        except Exception as ex:
            log.error('Exception in handle_data: %s', str(ex))
            #log.error(traceback.format_exc())

notif_listener = NotifListener()

# create the OTAP Communicator
comm = OTAPCommunicator.OTAPCommunicator(send_data, notif_listener, options=otap_options)

def get_motes():
    motes = []
    total_motes = 0
    while True:
        moteList = voyager.motesApi.get_motes(start_index=total_motes)
        total_motes = total_motes + len(moteList.motes)
        if len(moteList.motes) == 0:
            break
        for m in moteList.motes:
            if m.state == 'operational':
                motes.append(m)
    return motes

def match_mote(motes, mote_abbrev):
    macs = [(m.mac_address).lower() for m in motes]
    mote_abbrev = mote_abbrev.lower()
    if mote_abbrev in macs:
        input_mac = tuple([int(c, 16) for c in mote_abbrev.split('-')])
        return input_mac
    else:
        return False

#============================ main ============================================

def main(opts, files):
    global comm
    log.info("--- OTAP Communicator v%s", version_string())
    log.info("Started with command line arguments: %s", sys.argv)
    
    print ("Welcome to the OTAP communicator console")
    if len(files):
        for f in files:
            print ('Loading', f)
            comm.load_file(f, os.path.splitext(f)[1] in OTAP_EXTENSIONS)

    # Handle user-specified list of motes
    motes = get_motes()
    if len(opts.motes):
        for m in opts.motes:
            full_mac = match_mote(motes, m)
            if full_mac:
                comm.all_motes.append(full_mac)
    else:
        # if no motes are listed, send to all Operational motes
        for m in motes:
            full_mac = tuple([int(c, 16) for c in ((m.mac_address).lower()).split('-')])
            comm.all_motes.append(full_mac)

    if opts.autorun and len(comm.all_motes):
        for f in files:
            print ('Starting OTAP for', f)
            comm.start_handshake(f)
            comm.wait_for_commit_complete()

        voyager.stop_notifications()
        
    else:
        # Useful imports for debug mode
        import time
        import struct
        # Welcome!
        print ("You can use the 'mgr' variable to call Manager API functions.")
        print (">>> help(mgr)")
        print ("You can use the 'comm' variable to interact with the OTAP Communicator.")
        print (">>> help(comm)")
        print ("Run mgr.disconnect() before exiting the interactive shell.")


if __name__=='__main__':
    try:
        main(options, args)
    except KeyboardInterrupt:
        voyager.stop_notifications()
