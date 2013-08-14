'''
Serial Mux Message classes
'''
import string
import struct
import time

# Magic token for the Serial Mux
MAGIC = struct.pack('BBBB', 0xa7, 0x40, 0xa0, 0xf5)
# Magic token for the Location Engine API
LOCATION_MAGIC = struct.pack('BBBB', 0x73, 0x03, 0xc6, 0x5d)

# Global event id
event_id = 1


class API:
    AUTH  = [ 48, 49, 50, 51, 52, 53, 54, 55 ]  # TODO: randomize me!
    VERSIONS = (4, 3)

    # Notification constants
    NOTIF_EVENT = 1
    NOTIF_DATA = 4
    NOTIF_IP = 5
    NOTIF_HEALTH = 6

    # Command types
    HELLO_CMD = 1
    HELLO_RESP = 2
    
    NOTIFICATION = 20
    RESET_CMD = 21
    SUBSCRIBE_CMD = 22
    GET_TIME_CMD = 23
    SET_NETWORK_CFG_CMD = 26
    CLEAR_STATS_CMD = 31
    EXCH_JOINKEY_CMD = 33
    EXCH_NETWORKID_CMD = 34
    SET_ACL_CMD = 39
    GET_NEXT_ACL_CMD = 40
    DELETE_ACL_CMD = 41
    PING_MOTE_CMD = 42
    GET_LOG_CMD = 43
    
    SEND_DATA_CMD = 44
    START_NETWORK_CMD = 45
    GET_SYS_INFO_CMD = 46 
    GET_MOTE_CFG_CMD = 47
    GET_PATH_INFO_CMD = 48
    GET_NEXT_PATH_CMD = 49
    SET_ADVERTISING_CMD = 50
    SET_DFRAME_MULT_CMD = 51
    MEASURE_RSSI_CMD = 52
    GET_MANAGER_INFO_CMD = 53    
    SET_TIME_CMD = 54
    GET_LICENSE_CMD = 55
    SET_LICENSE_CMD = 56
    ENABLE_TRACE_CMD = 57
    SET_CLI_USER_CMD = 58
    SEND_IP_CMD = 59
    START_LOCATION_CMD = 60
    RESTORE_FACTORY_DEFAULTS_CMD = 61
    GET_MOTE_INFO_CMD = 62
    GET_NETWORK_CFG_CMD = 63
    GET_NETWORK_INFO_CMD = 64
    GET_MOTE_CFG_BY_ID_CMD = 65
    SET_COMMONJOINKEY_CMD = 66
    GET_IP_CFG_CMD = 67
    SET_IP_CFG_CMD = 68
    DEL_MOTE       = 69

    # Path direction
    PATH_DIR_NOTUSE = 1
    PATH_DIR_UP    = 2
    PATH_DIR_DOWN  = 3

    # Notification ID
    NOTIF_EVENT      = 1
    NOTIF_LOG        = 2
    NOTIF_DATA       = 4
    NOTIF_IP_DATA    = 5
    NOTIF_HR         = 6

    # Event type
    EV_MOTE_RESET    = 0
    EV_NET_RESET     = 1
    EV_CMD_FINISH    = 2
    EV_MOTE_JOIN     = 3
    EV_MOTE_OPER     = 4
    EV_MOTE_LOST     = 5
    EV_NET_TIME      = 6
    EV_PING_RESP     = 7
    EV_RSV1          = 8
    EV_MOTE_BANDWIDTH= 9
    EV_PATH_CREATE   = 10
    EV_PATH_DELETE   = 11
    EV_PACKET_SENT   = 12
    EV_MOTE_CREATE   = 13
    EV_MOTE_DELETE   = 14

    # Mote state
    MOTE_STATE_LOST  = 0 
    MOTE_STATE_NEGOT = 1      
    MOTE_STATE_OPER  = 4
        
    
# Mux messages

def build_message(cmd_type, data, cmd_id=0):
    '''Build a Serial Mux message'''
    cmd = MAGIC
    cmd += struct.pack('!HHB', len(data)+3, cmd_id, cmd_type)
    cmd += data
    return cmd

def build_response(cmd_type, response_code, data, cmd_id=0):
    '''Build a Serial Mux response'''
    resp = struct.pack('B', response_code) + data
    return build_message(cmd_type, resp, cmd_id)

def build_data_notif(src_mac, src_port, dest_port, data):
    '''
    Build a data notification
    src, dest: mac address, port of source and destination
    '''
    t = time.time()
    secs = int(t)
    msecs = int((t - secs) * 1000000)
    notif = struct.pack('!BBLL8B', API.NOTIF_DATA, 0, secs, msecs, *src_mac)
    notif += struct.pack('HH', src_port, dest_port) + data
    return build_message(API.NOTIFICATION, notif) 

def build_event(event_type, data):
    '''Build an event from the provided data and insert the current event id'''
    global event_id
    notif = struct.pack('!BLB', API.NOTIF_EVENT, event_id, event_type) + data
    event_id += 1
    return build_message(API.NOTIFICATION, notif)

def build_mote_event(event_type, mac):
    '''
    Build a mote event notification (Lost, Joining, Operational, Reset)
    '''
    return build_event(event_type, struct.pack('8B', *mac))


# Message Parser

class Parser(object):
    '''
    Simple parser class for Serial Mux messages
    '''
    def __init__(self, magic = MAGIC):
        self.magic = magic
        self.input_buffer = ''
        self.callback = None
    
    def setCallback(self, cb):
        '''
        Set the callback for a complete message
        '''
        self.callback = cb

    def parse(self, data):
        '''
        Parse input data
        Calls the registered callback when complete message is received
        '''
        if not data:
            return
        self.input_buffer += data
        while self.parse_one():
            pass

    def parse_one(self):
        '''Parse a single command from input_data
        Returns: whether a command was found
        '''
        msg_start = self.input_buffer.find(self.magic)
        if msg_start >= 0:
            # strip the ignored input
            self.input_buffer = self.input_buffer[msg_start:]
            # verify input is long enough
            if len(self.input_buffer) < 6:
                return False
            # parse message header
            bin_len = self.input_buffer[4:6]
            msg_len = struct.unpack('!H', bin_len)[0]
            # TODO: limit the length of valid messages
            index_end = 6 + msg_len
            # verify the message is complete
            if len(self.input_buffer) < index_end:
                return False
            
            msg = self.input_buffer[6:index_end]
            (cmd_id, cmd_type) = struct.unpack('!HB', msg[0:3])
            data = msg[3:]
            if self.callback:
                self.callback(cmd_id, cmd_type, data)
            self.input_buffer = self.input_buffer[index_end:]
            return True
        else:
            # if the token doesn't appear, ignore all but the last 3 characters
            self.input_buffer = self.input_buffer[-3:]
            return False
            
