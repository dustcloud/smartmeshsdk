import OAPMessage
import struct
import datetime
from   array import array

INFO_ADDRESS       = array('B', [0])
TEMP_ADDRESS       = array('B', [5])
PKGEN_ADDRESS      = array('B', [254])

NOTIFTYPE_SAMPLE   = 0
NOTIFTYPE_STATS    = 1
NOTIFTYPE_DIG      = 2
NOTIFTYPE_LOCATEME = 3
NOTIFTYPE_PKGEN    = 4

TAG_ADDRESS        = 0xff

# TODO: turn parse_oap_notif into an OAP Notification Factory?

def parse_oap_notif(data, index = 0):
    '''
    Parse the OAP notification data and return a OAPNotif object.
    
    data: array of bytes from the OAP notification payload.
        OAP transport header and OAP command type should be stripped
    '''
    
    # TODO: validate length
    result = None
    
    # notif type
    notif_type                              = data[index]
    index                                  += 1
    
    # payload
    if   notif_type==NOTIFTYPE_SAMPLE:
        
        #===== parse
        
        # channel (TLV)
        (tag, l, channel)                   = OAPMessage.parse_tlv(data[index:])
        if tag!=TAG_ADDRESS:
            raise ValueError('invalid notification data: expected address tag')
        index                              += 2 + l
        
        # timestamp
        (secs, usecs)                       = struct.unpack_from('!ql', data, index + 1)
        index                              += 12
        
        # rate
        rate                                = struct.unpack_from('!l', data, index)[0]
        index                              += 4
        
        # numSamples
        num_samples                         = int(data[index])
        index                              += 1
        
        # sampleSize
        sample_size                         = int(data[index])
        index                              += 1
        
        #===== create and populate result structure
        
        if channel == TEMP_ADDRESS:
            result                          = OAPTempSample()
            result.packet_timestamp         = (secs, usecs)
            result.rate                     = rate
            result.num_samples              = num_samples
            result.sample_size              = sample_size
            for i in range(num_samples):
                temp                        = struct.unpack('!h', data[index:index+2])[0]
                index                      += 2
                result.samples.append(temp)
        else:
            result                          = OAPSample()
            result.packet_timestamp         = (secs, usecs)
            result.rate                     = rate
            result.num_samples              = num_samples
            result.sample_size              = sample_size
            result.samples                  = []
            bit_index                       = 0
            for i in range(num_samples):
                sample_data                 = OAPMessage.read_bits(data[index:], bit_index, sample_size)
                result.samples.append(sample_data)
           
    elif notif_type==NOTIFTYPE_STATS:
        
        #===== parse
        
        # channel (TLV)
        (tag, l, channel)                   = OAPMessage.parse_tlv(data[index:])
        if tag!=TAG_ADDRESS:
            raise ValueError('invalid notification data: expected address tag')
        index                              += 2 + l
        
        # timestamp
        (secs, usecs)                       = struct.unpack_from('!ql', data, index + 1)
        index                              += 12
        
        # rate
        rate                                = struct.unpack_from('!l', data, index)[0]
        index                              += 4
        
        # numSamples
        num_samples                         = int(data[index])
        index                              += 1
        
        # sampleSize
        sample_size                         = int(data[index])
        index                              += 1
        
        #===== create and populate result structure
        
        # TODO populate
        result                              = OAPAnalogStats()
        result.packet_timestamp             = (secs, usecs)
    
    elif notif_type==NOTIFTYPE_DIG:
    
        #===== parse
        
        raise NotImplementedError("parsing digital OAP notification")
        
        #===== create and populate result structure
        
        raise NotImplementedError("filling digital OAP result structure")
        
    elif notif_type==NOTIFTYPE_LOCATEME:
        
        #===== parse
        
        raise NotImplementedError("parsing locateMe OAP notification")
        
        #===== create and populate result structure
        
        raise NotImplementedError("filling locateMe OAP result structure")
    
    elif notif_type == 4:  # pkgen
        
        #===== parse
        
        # channel (TLV)
        (tag, l, channel)                   = OAPMessage.parse_tlv(data[index:])
        if tag != 0xFF:
            raise ValueError('invalid notification data: expected address tag')
        index                              += 2 + l
        
        # pid
        pid                                 = struct.unpack_from('!l', data, index)[0]
        index                              += 4
        
        # startPid
        startPid                            = struct.unpack_from('!l', data, index)[0]
        index                              += 4
        
        # numPackets
        numPackets                          = struct.unpack_from('!l', data, index)[0]
        index                              += 4
        
        # payload
        payload                             = data[index:]
        
        #===== create and populate result structure
        
        result                              = OAPpkGenPacket()
        result.pid                          = pid
        result.startPid                     = startPid
        result.numPackets                   = numPackets
        result.payload                      = payload
        
    # set common notification attributes
    if result:
        result.raw_data                     = data
        result.channel                      = channel
        result.received_timestamp           = datetime.datetime.now()
        
    return result

class OAPNotif(object):
    '''
    \brief Parent class for all OAP notification structures.
    '''
    
    def __init__(self):
        self.channel                        = ''
        self.packet_timestamp               = None
        self.received_timestamp             = None
        
    def channel_str(self):
        return ':'.join([str(c) for c in self.channel])

class OAPSample(OAPNotif):
    '''
    \brief representation of a (sensor) sample notification.
    '''
    def __str__(self):
        return 'C=[%s] samples: %s' % (self.channel_str(),
                                       ', '.join([str(i) for i in self.samples]))

class OAPTempSample(OAPSample):
    '''
    \brief representation of a temperatire sample notification.
    '''
    def __init__(self):
        self.rate                           = 0
        self.num_samples                    = 0
        self.sample_size                    = 0
        self.samples                        = []

    def __str__(self):
        return 'TEMP=%d' % (self.samples[0])

class OAPAnalogStats(OAPNotif):
    '''
    \brief representation of a stats notification.
    '''
    def __init__(self):
        self.rate                           = 0
        self.num_samples                    = 0
        self.sample_size                    = 0
        self.min_value                      = 0
        self.max_value                      = 0
        self.ave_value                      = 0

    def __str__(self):    
        return 'C=[%s] min=%d max=%d ave=%d' % (self.channel_str(),
                                                self.min_value,
                                                self.max_value,
                                                self.ave_value)

class OAPpkGenPacket(OAPNotif):
    def __init__(self):
        self.pid                            = 0
        self.startPid                       = 0
        self.numPackets                     = 0
        self.payload                        = []

    def __str__(self):
        template = "{0}={1}"
        output   = ['PKGEN']
        output  += [template.format("pid",       self.pid)]
        output  += [template.format("startPid",  self.startPid)]
        output  += [template.format("numPackets",self.numPackets)]
        return ' '.join(output)
