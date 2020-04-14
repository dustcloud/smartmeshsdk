import os
import time

try:
    import urllib.parse as url_parser
except ImportError:
    import urllib as url_parser

LOG_FORMAT_TIMESTAMP = '%Y/%m/%d %H:%M:%S'

def formatBuffer(buf):
    '''
    example: [0x11,0x22,0x33,0x44,0x55,0x66,0x77,0x88] -> "11-22-33-44-55-66-77-88"
    '''
    return '-'.join(["%.2x"%i for i in buf])
    
def formatMacString(mac,upper=False):
    '''
    example: 0x1122334455667788 -> "11-22-33-44-55-66-77-88"
    '''
    
    if upper:
        res = '-'.join(["%.2X"%i for i in mac])
    else:
        res = '-'.join(["%.2x"%i for i in mac])
    
    return res

def formatIpString(ip):
    '''
    example: [254,128,0,0,0,0,0,0,0,23,13,0,0,48,93,57] -> "fe80:0000:0000:0000:0017:0d00:0030:5d39"
    '''
    ipString       = []
    for i in range(8):
        ipString  += [''.join(["%.2x"%i for i in ip[i*2:i*2+2]])]
    ipString       = ':'.join(ipString)
    
    return ipString

def formatShortMac(mac):
    '''
    example: 0x1122334455667788 -> "77-88"
    '''
    return '-'.join(["%.2x"%i for i in mac[6:]])

def formatNamedTuple(tup):
    output         = []
    output        += ['{0}:'.format(tup.__class__.__name__)]
    for k in tup._fields:
        v          = getattr(tup, k)
        try:
            v      = formatBuffer(v)
        except TypeError:
            pass
        output    += ['{0:>20}: {1}'.format(k,v)]
    output         = '\n'.join(output)
    return output

def formatDictionary(data):
    output         = []
    for (k,v) in list(data.items()):
        output    += ['{0:>20}: {1}'.format(k,v)]
    output         = '\n'.join(output)
    return output

def quote(string):
    return url_parser.quote(string, '')

def unquote(string):
    return url_parser.unquote(string)

def formatConnectionParams(connectionParams):
    if   isinstance(connectionParams,str):
        return connectionParams
    elif isinstance(connectionParams,tuple):
        return '{0}_{1}'.format(*connectionParams)
    else:
        raise SystemError("unexpected connectionParams format {0}".format(connectionParams))

def formatTimestamp(timestamp=None):
    if timestamp==None:
        timestamp = time.time()
    return '{0}.{1:03}'.format(
        time.strftime(LOG_FORMAT_TIMESTAMP, time.localtime(timestamp)),
        int((timestamp*1000)%1000)
    )

def format_mac_string_to_bytes(mac_string):
    '''
    "00-11-22-33-44-55-66-77" -> [0x00,0x11,0x22,0x33,0x44,0x55,0x66,0x77]
    '''
    return [int(b,16) for b in mac_string.split('-')]
