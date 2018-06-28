import OAPMessage
import OAPDefines
import struct
import datetime
from   array import array

DIGITAL_IN_ADDRESS = 2
ANALOG_ADDRESS     = 4
TEMP_ADDRESS       = array('B', [5])

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
        (secs, usecs)                       = struct.unpack_from('!ql', data, index)
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
        
        #===== create result structure
        
        if len(channel)==2 and channel[0]==DIGITAL_IN_ADDRESS:
            result                          = OAPDigitalInSample()
        elif channel == TEMP_ADDRESS:
            result                          = OAPTempSample()
        elif len(channel)==2 and channel[0]==ANALOG_ADDRESS:
            result                          = OAPAnalogSample()
        else:
            raise SystemError("unknown OAP sample with channel={0}").format(channel)
        
        #===== populate result structure
		
        if channel[0]==ANALOG_ADDRESS or channel[0]==DIGITAL_IN_ADDRESS:
            result.input                    = channel[1] 
        result.packet_timestamp             = (secs, usecs)
        result.rate                         = rate
        result.num_samples                  = num_samples
        result.sample_size                  = sample_size
        for i in range(num_samples):
            if   sample_size==8:
                temp                            = struct.unpack('!B', data[index:index+1])[0]
                index                          += 1
            elif sample_size==16:
                temp                            = struct.unpack('!h', data[index:index+2])[0]
                index                          += 2
            else:
                raise SystemError("unexpected sample_size of {0}".format(sample_size))
            result.samples.append(temp)
        
    elif notif_type==NOTIFTYPE_STATS:
        
        #===== parse
        
        # channel (TLV)
        (tag, l, channel)                   = OAPMessage.parse_tlv(data[index:])
        if tag!=TAG_ADDRESS:
            raise ValueError('invalid notification data: expected address tag')
        index                              += 2 + l
        
        # timestamp
        (secs, usecs)                       = struct.unpack_from('!ql', data, index)
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

        # channel (TLV)
        (tag, l, channel)                   = OAPMessage.parse_tlv(data[index:])
        if tag!=TAG_ADDRESS:
            raise ValueError('invalid notification data: expected address tag')
        index                              += 2 + l
        
        # timestamp
        (secs, usecs)                       = struct.unpack_from('!ql', data, index)
        index                              += 12
        
        # new value
        new_val                             = int(data[index])
        index                              += 1
        
        #===== create and populate result structure
        
        result                          = OAPDigitalIn()
        result.channel                  = channel
        result.packet_timestamp         = (secs, usecs)
        result.new_val                  = new_val
   
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

#===== OAP notification base class

class OAPNotif(object):
    '''
    \brief Parent class for all OAP notification structures.
    '''
    
    def __init__(self):
        self.channel                        = ''
        self.packet_timestamp               = None
        self.received_timestamp             = None
    
    def channel_str(self):
        returnVal = 'UNKNOWN'
        for (k,v) in OAPDefines.ADDRESS.items():
            if list(v)==self.channel.tolist():
                returnVal = k
                break
        return returnVal
    
    def _asdict(self):
        returnVal = {
            'channel':                      self.channel.tolist(),
            'channel_str':                  self.channel_str(),
            'packet_timestamp':             self.packet_timestamp,
            'received_timestamp':           str(self.received_timestamp),
        }
        return returnVal

#===== OAP Sample/Report notification

class OAPSample(OAPNotif):
    '''
    \brief representation of a (e.g. sensor) sample notification.
    '''
    def __str__(self):
        return 'C=[{0}] samples: {1}'.format(
            self.channel_str(),
            ', '.join([str(i) for i in self.samples]),
        )

class OAPDigitalInSample(OAPSample):
    '''
    \brief representation of an digital_in sample notification.
    '''
    def __init__(self):
        self.rate                           = 0
        self.input                          = 0
        self.num_samples                    = 0
        self.sample_size                    = 0
        self.samples                        = []
    
    def __str__(self):
        return 'DIGITAL_IN input={0} state={1} V'.format(
            self.input,
            self.samples[0],
        )
    
    def _asdict(self):
        returnVal = super(OAPDigitalInSample, self)._asdict()
        returnVal['rate']                   = self.rate
        returnVal['input']                  = self.input
        returnVal['num_samples']            = self.num_samples
        returnVal['sample_size']            = self.sample_size
        returnVal['samples']                = self.samples
        return returnVal

class OAPTempSample(OAPSample):
    '''
    \brief representation of a temperature sample notification.
    '''
    def __init__(self):
        self.rate                           = 0
        self.num_samples                    = 0
        self.sample_size                    = 0
        self.samples                        = []

    def __str__(self):
        return 'TEMPERATURE {0:.2f} C'.format(
            float(self.samples[0])/100,
        )
    
    def _asdict(self):
        returnVal = super(OAPTempSample, self)._asdict()
        returnVal['rate']                   = self.rate
        returnVal['num_samples']            = self.num_samples
        returnVal['sample_size']            = self.sample_size
        returnVal['samples']                = self.samples
        return returnVal

class OAPAnalogSample(OAPSample):
    '''
    \brief representation of an analog sample notification.
    '''
    def __init__(self):
        self.rate                           = 0
        self.input                          = 0
        self.num_samples                    = 0
        self.sample_size                    = 0
        self.samples                        = []
    
    def __str__(self):
        return 'ANALOG input={0} voltage={1:.3f} V'.format(
            self.input,
            float(self.samples[0])/1000,
        )
    
    def _asdict(self):
        returnVal = super(OAPAnalogSample, self)._asdict()
        returnVal['rate']                   = self.rate
        returnVal['input']                  = self.input
        returnVal['num_samples']            = self.num_samples
        returnVal['sample_size']            = self.sample_size
        returnVal['samples']                = self.samples
        return returnVal

#===== OAP Stats report (min/max/ave)

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
        return 'C=[{0}] min_value={1} max_value={2} ave_value={3}'.format(
            self.channel_str(),
            self.min_value,
            self.max_value,
            self.ave_value,
        )
    
    def _asdict(self):
        returnVal = super(OAPAnalogStats, self)._asdict()
        returnVal['rate']                   = self.rate
        returnVal['num_samples']            = self.num_samples
        returnVal['sample_size']            = self.sample_size
        returnVal['min_value']              = self.min_value
        returnVal['max_value']              = self.max_value
        returnVal['ave_value']              = self.ave_value
        return returnVal

#===== OAP Digital change notification

class OAPDigitalIn(OAPNotif):
    '''
    \brief representation of a digital input notification.
    '''
    def __init__(self):
        self.new_val                        = 0
        
    def __str__(self):
        return 'DIGITAL value={0}'.format(
            self.new_val,
        )
    
    def _asdict(self):
        returnVal = super(OAPDigitalIn, self)._asdict()
        returnVal['new_val']                = self.new_val
        return returnVal

#===== OAP PkGen notification

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
    
    def _asdict(self):
        returnVal = super(OAPpkGenPacket, self)._asdict()
        returnVal['pid']                    = self.pid
        returnVal['startPid']               = self.startPid
        returnVal['numPackets']             = self.numPackets
        returnVal['payload']                = self.payload
        return returnVal
