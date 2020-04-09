'''
OTAP message classes
'''

import struct

from muxclient.DynStructs import API
from muxclient.DynNotifs import Data

from . import OTAPStructs
from .GenStructs import parse_obj
#from GenStructs import factory


OTAP_PORT = 0xF0B1

class OTAP:
    HANDSHAKE_CMD = 0x16
    DATA_CMD      = 0x17
    STATUS_CMD    = 0x18
    COMMIT_CMD    = 0x19



    
def build_cmd(cmdid, datastr):
    msg = struct.pack('!BB', cmdid, len(datastr))
    msg += datastr
    return msg


def build_otap_handshake(filename):
    pass


def build_otap_data(data):
    pass



def build_otap_status(mic = '\x00\x00\x00\x00'):
    return build_cmd(OTAP.STATUS_CMD, mic)


class OTAPMonitor:
    'Monitoring class for OTAP messages'
    
    def __init__(self, client, mac):
        self.client = client
        self.mac = mac
        self.register()
        
    def register(self):
        # TODO: keep existing subscriptions
        self.client.subscribe(['data'])
        self.client.addNotifHook(API.NOTIF_DATA, self.data_callback)

    # callback id is not in the mote's response
    #def send_callback(self, resp):
    #    (self.expected_cbid,) = struct.unpack('!L', resp[0:4])
        
    def send_status(self, mic):
        # TODO: validate we're not already waiting for another command
        msg = build_otap_status(mic)
        self.client.sendData(self.mac, OTAP_PORT, OTAP_PORT, msg)

    def status_callback(self, cmd_data):
        (rc, otap_rc, mic) = struct.unpack('!BBL', cmd_data[0:6])
        missing_blocks = []
        index = 6
        while index < len(cmd_data):
            (lost_block,) = struct.unpack('!H', cmd_data[index:index+2])
            missing_blocks.append(lost_block)
            index = index + 2

        print (('Err:', rc, 'OTAP:', otap_rc, 'MIC:', mic, 'Missing:'))
        print ((' '.join([str(b) for b in missing_blocks])))
        # TODO: filter out multiple responses

    def data_callback(self, data):
        if data.mac == self.mac and data.src_port == OTAP_PORT:
            index = 0
            # parse the payload for ALL responses in the packet
            while index < len(data.payload):
                # handle OTAP command responses
                cmd_type = data.payload[index]
                cmd_len = data.payload[index+1]
                
                if cmd_type == OTAP.STATUS_CMD:
                    self.status_callback(data.payload[index+2:index+2+cmd_len])

                index += 2 + cmd_len
