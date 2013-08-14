'''
Serial Mux Message classes
'''
import struct

# Magic token for the Serial Mux
MAGIC = struct.pack('BBBB', 0xa7, 0x40, 0xa0, 0xf5)

# Magic token for the Location Engine API
LOCATION_MAGIC = struct.pack('BBBB', 0x73, 0x03, 0xc6, 0x5d)

AUTH    = [ 48, 49, 50, 51, 52, 53, 54, 55 ]  # TODO: randomize me!
VERSION = 4

# Message Parser

class MuxMsg(object):
    def __init__(self, cb, ver = VERSION, magic = MAGIC, auth = AUTH):
        self.callback = cb
        self.ver = ver
        self.auth = auth
        self.magic = magic
        self.input_buffer = ''
    
    def getVer(self) :
        return self.ver
    
    def getAuth(self):
        return self.auth
    
    def build_message(self, cmd_type, data, cmd_id=0):
        '''Build a Serial Mux message'''
        cmd = self.magic
        cmd += struct.pack('!HHB', len(data)+3, cmd_id, cmd_type)
        cmd += data
        return cmd
    
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
            
