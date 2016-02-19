#!/usr/bin/python
'''OTAP Communicator for IP Manager

The OTAP Communicator connects to the IP Manager through the Serial Mux. The Serial Mux
must be up and running for the OTAP Communicator to function.

To program a file (linux, cygwin):

$ python otap_communicator.py my-file.otap2

Or on Windows:

> \Python27\python bin\OTAPCommunicator\OTAPCommunicator.py my-file.otap2

For interactive mode (debugging), run:
$ python -i bin/OTAPCommunicator/OTAPCommunicator.py --nostart

'''

#============================ adjust path =====================================

import sys
import os
if __name__ == "__main__":
    here = sys.path[0]
    sys.path.insert(0, os.path.join(here, '..', '..','libs'))
    sys.path.insert(0, os.path.join(here, '..', '..','external_libs'))

#============================ imports =========================================

# cryptopy.crypto wants to import parts of the crypto module without the
# cryptopy prefix
import cryptopy
sys.path.append(os.path.dirname(cryptopy.__file__)) 

import traceback

from SmartMeshSDK.protocols.otap       import OTAPStructs
from SmartMeshSDK.protocols.otap       import OTAPCommunicator
from SmartMeshSDK                      import sdk_version

# Manager-specific imports
from SmartMeshSDK                      import ApiException
from SmartMeshSDK.IpMgrConnectorMux    import IpMgrConnectorMux
from SmartMeshSDK.IpMgrConnectorMux    import IpMgrSubscribe

#============================ defines =========================================

def version_string():
    return '.'.join([str(v) for v in sdk_version.VERSION])

DEFAULT_HOST       = '127.0.0.1'
DEFAULT_PORT       = 9900

OTAP_EXTENSIONS    = ['.otap', '.otap2']

#============================ logging =========================================

import logging
import logging.handlers

LOG_FILENAME = 'otap_communicator.log'
LOG_FORMAT   = "%(asctime)s [%(name)s:%(levelname)s] %(message)s"

# Set up a specific logger with our desired output level
log = logging.getLogger('otap_communicator')
log.setLevel(logging.INFO)

# Add the log message handler to the logger
handler = logging.handlers.RotatingFileHandler(LOG_FILENAME,
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
parser = OptionParser("usage: %prog [options] <file(s)>...",
                      version="OTAP Communicator " + version_string())
parser.add_option("-v", "--verbose", dest="verbose", action="store_true",
                  default=False, 
                  help="Print verbose messages")
parser.add_option("--host", dest="host", 
                  default=DEFAULT_HOST,
                  help="Host of Serial Mux")
parser.add_option("-p", "--port", dest="port", 
                  default=DEFAULT_PORT,
                  help="TCP port of Serial Mux")
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
mgr = IpMgrConnectorMux.IpMgrConnectorMux()
mgr.connect({'host': options.host, 'port': int(options.port)})

# Wrap a simple adapter around the manager's sendData method

def send_data(mac, msg, port):
    'Returns: the sendData response'
    global mgr
    msg_hex = [int(ord(b)) for b in msg]
    # TODO: priority as enum
    rc = -1
    cbid = -1
    try:
        resp = mgr.dn_sendData(mac, 2, port, port, 0, msg_hex)
        rc = resp.RC
        cbid = resp.callbackId
    except ApiException.APIError as ex:
        rc = ex.rc
    # always return RC, callbackId
    return (rc, cbid)

# Wrap a simple adapter around the IpMgrSubscribe class

from collections import namedtuple

Data = namedtuple('Data', 'mac src_port payload payload_str')

class NotifListener(IpMgrSubscribe.IpMgrSubscribe):
    def __init__(self, mgr):
        IpMgrSubscribe.IpMgrSubscribe.__init__(self, mgr)
        self.start()

    def register(self, cb):
        self.otap_callback = cb
        self.subscribe(IpMgrConnectorMux.IpMgrConnectorMux.NOTIFDATA,
                       self.handle_data, False)

    def handle_data(self, notif_type, data_tuple):
        try:
            # convert notif data into the OTAP Communicator data structure
            payload = data_tuple.data
            ps = ''.join([chr(b) for b in payload])
            data = Data(data_tuple.macAddress, data_tuple.srcPort, payload, ps)
            self.otap_callback(data)
        except Exception as ex:
            log.error('Exception in handle_data: %s', str(ex))
            #log.error(traceback.format_exc())

notif_listener = NotifListener(mgr)

# create the OTAP Communicator
comm = OTAPCommunicator.OTAPCommunicator(send_data, notif_listener, options=otap_options)

def get_motes(mgr):
    motes = []
    try:
        curr_mac = [0]*8
        while True:
            m = mgr.dn_getMoteConfig(curr_mac, True)
            motes.append(m)
            curr_mac = m.macAddress
    except ApiException.APIError:
        pass
    return motes

def match_mote(motes, mote_abbrev):
    macs = [m.macAddress for m in motes]
    input_mac = tuple([int(c, 16) for c in mote_abbrev.split('-')])
    if input_mac in macs:
        return input_mac
    else:
        return False

#============================ main ============================================

def main(opts, files):
    global mgr, comm
    log.info("--- OTAP Communicator v%s", version_string())
    log.info("Started with command line arguments: %s", sys.argv)
    
    print "Welcome to the OTAP communicator console"
    if len(files):
        for f in files:
            print 'Loading', f
            comm.load_file(f, os.path.splitext(f)[1] in OTAP_EXTENSIONS)

    # Handle user-specified list of motes
    motes = get_motes(mgr)
    if len(opts.motes):
        for m in opts.motes:
            full_mac = match_mote(motes, m)
            if full_mac:
                comm.all_motes.append(full_mac)
    else:
        # if no motes are listed, send to all Operational motes
        comm.all_motes = [m.macAddress for m in motes if m.state == 4 and not m.isAP]

    if opts.autorun and len(comm.all_motes):
        for f in files:
            print 'Starting OTAP for', f
            comm.start_handshake(f)
            comm.wait_for_commit_complete()

        mgr.disconnect()
        
    else:
        # Useful imports for debug mode
        import time
        import struct
        # Welcome!
        print "You can use the 'mgr' variable to call Manager API functions."
        print ">>> help(mgr)"
        print "You can use the 'comm' variable to interact with the OTAP Communicator."
        print ">>> help(comm)"
        print "Run mgr.disconnect() before exiting the interactive shell."


if __name__=='__main__':
    try:
        main(options, args)
    except KeyboardInterrupt:
        mgr.disconnect()
        
