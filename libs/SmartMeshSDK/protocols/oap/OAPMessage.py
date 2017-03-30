'''
OAP message parser and generator
'''

# TODO: OAP message stolen from Ben (PUT echo):
# '\x01\x00\x02\xff\x01\xfe\x00\x04\x00\x00\x00\x01'
# DATA: [1025673457.536000] src=00-1B-1E-00-00-00-00-02:f0bb dest=b9f0:
# 03 00 02 00 FF 01 FE
# Tr=Rel+Resp Id=0 Cmd=2 (Put) RC=0 Tags: Addr=0xFE

# GET pkgen (note: not recursive):
# '\x01\x00\x01\xff\x01\xfe'
# DATA: [1025673457.536000] src=00-1B-1E-00-00-00-00-02:f0bb dest=b9f0:
# 03 00 01 00 FF 01 FE

# GET echo
# '\x01\x00\x01\xff\x02\xfe\x00'
# DATA: [1025673850.752000] src=00-1B-1E-00-00-00-00-02:f0bb dest=b9f0:
# 03 00 01 00 FF 01 FE 00 04 00 00 00 02
# ...send GET again...
# DATA: [1025673850.752000] src=00-1B-1E-00-00-00-00-02:f0bb dest=b9f0:
# 03 00 01 00 FF 01 FE 00 04 00 00 00 03

import struct

OAP_PORT = 0xF0B9

class CmdType:
    GET       = 1
    PUT       = 2
    POST      = 3
    DELETE    = 4
    NOTIF     = 5

# client.sendData(mac, src_port, dest_port, data)

class TLV(object):
    def __init__(self, t, v = None):
        self.tag = t
        self.value = v
        self.val_len = 1
        self.format_str = 'B'
    def __str__(self):
        return '%d: %s' % (self.tag, str(self.value))
    def serialize(self):
        return struct.pack('!BB' + self.format_str, self.tag, self.val_len, self.value)
    def parse_value(self, val_str, val_len=None):
        if val_len==0:
            self.value = None
        else:
            self.value = struct.unpack('!'+self.format_str, val_str[0:self.val_len])[0]
    
class TLVByte(TLV):
    def __init__(self, t, v = None):
        TLV.__init__(self, t, v)
        self.val_len = 1
        self.format_str = 'B'

class TLVShort(TLV):
    def __init__(self, t, v = None):
        TLV.__init__(self, t, v)
        self.val_len = 2
        self.format_str = 'H'

class TLVShortS(TLV):
    def __init__(self, t, v = None):
        TLV.__init__(self, t, v)
        self.val_len = 2
        self.format_str = 'h'

class TLVLong(TLV):
    def __init__(self, t, v = None):
        TLV.__init__(self, t, v)
        self.val_len = 4
        self.format_str = 'L'
    
class TLVString(TLV):
    def __init__(self, t, v = None):
        TLV.__init__(self, t, v)
        self.val_len = len(v)
        self.format_str = '%dB' % self.val_len
        
    def serialize(self):
        tag_len = 2 + self.val_len
        return struct.pack('!%dB' % tag_len, self.tag, self.val_len,
                           *[ord(c) for c in self.value])

    def parse_value(self, val_str):
        self.value = val_str

def find_tag(tags, tag_id):
    'Find the specified tag tuple in a list of tag objects'
    for t in tags:
        if t.tag == tag_id:
            return t
    return None

class Info(object):
    '''
    Stardard OAP /info element
    '''
    
    ADDR = 0
    
    def __init__(self):
        self.ver_major       = TLVByte(0)
        self.ver_minor       = TLVByte(1)
        self.ver_patch       = TLVByte(2)
        self.ver_build       = TLVByte(3)
        self.app_type        = TLVShort(4)
        self.reset_counter   = TLVLong(5)
        self.change_counter  = TLVLong(6)
        
        self.tags            = [ self.ver_major,
                                 self.ver_minor,
                                 self.ver_patch,
                                 self.ver_build,
                                 self.app_type,
                                 self.reset_counter,
                                 self.change_counter ]
    
    def parse_response(self, resp):
        for t in resp['tags']:
            my_tag = find_tag(self.tags, t[0])
            # the response can contain tags we don't care about
            if my_tag:
                my_tag.parse_value(t[2])
    
    def __str__(self):
        template = "{0}=({1})"
        output  = []
        output += [template.format("ver_major",       self.ver_major)]
        output += [template.format("ver_minor",       self.ver_minor)]
        output += [template.format("ver_patch",       self.ver_patch)]
        output += [template.format("ver_build",       self.ver_build)]
        output += [template.format("app_type",        self.app_type)]
        output += [template.format("reset_counter",   self.reset_counter)]
        output += [template.format("change_counter",  self.change_counter)]
        return ' '.join(output)

class Sensor(object):
    '''
    Common sensor element
    '''
    
    def __init__(self, addr):
        self.addr            = addr
        self.enable          = TLVByte(0)
        self.rate            = TLVLong(1)
        self.sample_count    = TLVByte(2)
        self.data_format     = TLVByte(3)
        self.value           = TLVShort(4)
        self.tags            = [ self.enable,
                                 self.rate,
                                 self.sample_count,
                                 self.data_format,
                                 self.value ]
    
    def parse_response(self, resp):
        for t in resp['tags']:
            # (t[0],t[1],t[2]) is (tag,length,value)
            my_tag = find_tag(self.tags, t[0])
            # the response can contain tags we don't care about
            if my_tag:
                my_tag.parse_value(val_len=t[1],val_str=t[2])
    
    def __str__(self):
        template = "{0}=({1})"
        output  = []
        output += [template.format("addr",            self.addr)]
        output += [template.format("enable",          self.enable)]
        output += [template.format("rate",            self.rate)]
        output += [template.format("sample_count",    self.sample_count)]
        output += [template.format("data_format",     self.data_format)]
        output += [template.format("value",           self.value)]
        return ' '.join(output)

class Temperature(Sensor):
    
    def __init__(self):
        Sensor.__init__(self,5)
        self.value           = TLVShortS(4)
        self.tags            = [ self.enable,
                                 self.rate,
                                 self.sample_count,
                                 self.data_format,
                                 self.value ]

# the builders are bare-bones for now
# we'll build up better classes as we get more experience with the platform

def build_tlv_addr(addr):
    tag_len = 2 + len(addr)
    return struct.pack('!%dB' % tag_len, 0xFF, len(addr), *addr)
    
def build_oap(seq, sid, cmd, addr, tags=None, sync=False):
    'usage: build_oap <cmd> <address> [tag objects]...'
    ctrl = 1  # rel/unrel transport=0, req/resp=1, sync=2
    if sync:
        ctrl += 4
    pkt_id = seq + sid * 16  # seq=0-3, session id=4-7
    msg = struct.pack('!BBB', ctrl, pkt_id, cmd)
    msg += build_tlv_addr(addr)
    # TODO
    if tags:
        for t in tags:
            msg += t.serialize()
    return msg

# the parser is bare bones for now
# we'll build up better classes as we get more experience with the platform

def make_tlv(klass, t, val_str):
    t = klass(t, '')
    t.parse_value(val_str)
    return t

def parse_tlv(msg):
    (tag, val_len) = struct.unpack('BB', msg[0:2])
    return (tag, val_len, msg[2:2+val_len])

def extract_oap_header(pkt, index = 0):
    """Extract the OAP transport header from an OAP packet"""
    (ctrl, sid) = struct.unpack('2B', pkt[index:index+2])
    return {'reliable': bool(ctrl & 1),
            'response': bool(ctrl & 2),
            'sync': bool(ctrl & 4),
            'session': int(sid) >> 4,
            'sequence': int(sid & 0x0F)}

def parse_oap_response(pkt, index = 0):
    """Parse an OAP response from a byte array (starting with the command type)

    Returns: { 'command': \<command type\>,
               'result' : \<result code\>,
               'tags'   : [ (tag, len, array('B', <value bytes>)),... ]
               }

    """
    (cmd, rc) = struct.unpack('2B', pkt[index:index+2])
    index += 2
    tags = []
    while index < len(pkt):
        tag_tuple = parse_tlv(pkt[index:])
        index += tag_tuple[1] + 2
        tags.append(tag_tuple)
    return { 'command': cmd, 'result': rc, 'tags': tags }


# we need a way to read N bits from a data string

def read_bits(data, bit_index, bit_length):
    """Read 'bit_length' bits starting at 'bit_index' from byte array 'data'"""
    byte_offset = bit_index / 8;
    bit_remainder = bit_index % 8;
    result = 0;

    # handle bit_length < bit_remainder 
    
    len_remainder = bit_length;
    # get the first bits
    if (bit_remainder > 0):
        result = data[byte_offset] & _getLowerBitmask(8 - bit_remainder)
        byte_offset += 1
        len_remainder -= 8 - bit_remainder

    # get the middle bytes
    while (len_remainder >= 8):
        result <<= 8
        result += data[byte_offset]
        byte_offset += 1
        len_remainder -= 8
        
    if (len_remainder > 0):
        # get the last bits
        result <<= len_remainder
        bottom = ((data[byte_offset] & _getHigherBitmask(len_remainder)) >> (8 - len_remainder))
        result += bottom

    return result

def _getLowerBitmask(n):
    return ((1 << n) - 1)

def _getHigherBitmask(n):
    return (_getLowerBitmask(8 - n) ^ 0xFF)
