'''
Dynamic API structures

Build notifications from a description of their fields
'''

import struct
import datetime
from array import array
from collections import namedtuple

import DynStructs
from MuxMessage import API

NOTIF_TYPES = ['ULPM Data', 'Event', 'Log', 'NotImpl', 'Data', 'IP', 'Health']
EVENT_TYPES_STR = {API.EV_MOTE_RESET    : 'Mote Reset' ,
                   API.EV_NET_RESET     : 'Net Reset' ,
                   API.EV_CMD_FINISH    : 'Cmd Finish' ,
                   API.EV_MOTE_JOIN     : 'Mote Join' ,
                   API.EV_MOTE_OPER     : 'Mote Oper' ,
                   API.EV_MOTE_LOST     : 'Mote Lost' ,
                   API.EV_NET_TIME      : 'Net Time' ,
                   API.EV_PING_RESP     : 'Ping',
                   API.EV_RSV1          : 'NotImpl' ,
                   API.EV_MOTE_BANDWIDTH: 'Mote BW',
                   API.EV_PATH_CREATE   : 'Path Create',
                   API.EV_PATH_DELETE   : 'Path Delete',
                   API.EV_PACKET_SENT   : 'Packet Sent',
                   API.EV_MOTE_CREATE   : 'Mote Create',
                   API.EV_MOTE_DELETE   : 'Mote Delete'}

#[ Define    Health Report Mote Commands -------------------------------------------
MOTECMD_DEVHR_FIELDS = [
   DynStructs.ApiStructField('charge',          'int',  4),       
   DynStructs.ApiStructField('QOcc',            'int',  1),    
   DynStructs.ApiStructField('temperature',     'sint', 1),  
   DynStructs.ApiStructField('batteryVolt',     'int',  2),  
   DynStructs.ApiStructField('numTxOk',         'int',  2),      
   DynStructs.ApiStructField('numTxFail',       'int',  2),    
   DynStructs.ApiStructField('numRxOk',         'int',  2),    
   DynStructs.ApiStructField('numRxLost',       'int',  2),  
   DynStructs.ApiStructField('numMacDrop',      'int',  1), 
   DynStructs.ApiStructField('numTxBad',        'int',  1),   
   DynStructs.ApiStructField('badLink_frameId', 'int',  1),
   DynStructs.ApiStructField('badLink_slot',    'int',  4),
   DynStructs.ApiStructField('badLink_offset',  'int',  1),
]
MoteCmdDevHR = DynStructs.synthesize('MoteCmdDevHR', MOTECMD_DEVHR_FIELDS)

MOTECMD_DSCVR_FILEDS = [
   DynStructs.ApiStructField('nbrId',           'int',  2),
   DynStructs.ApiStructField('rsl',             'sint', 1),
   DynStructs.ApiStructField('numRx',           'int',  1),
]
MoteCmdDscvr = DynStructs.synthesize('MoteCmdDscvr', MOTECMD_DSCVR_FILEDS)

MOTECMD_NBRHR_FIELDS = [
   DynStructs.ApiStructField('nbrId',           'int',  2),
   DynStructs.ApiStructField('nbrFlag',         'int',  1),
   DynStructs.ApiStructField('rsl',             'sint', 1),
   DynStructs.ApiStructField('numTxPk',         'int',  2),
   DynStructs.ApiStructField('numTxFail',       'int',  2),
   DynStructs.ApiStructField('numRxPk',         'int',  2),
]
MoteCmdNbrHR = DynStructs.synthesize('MoteCmdNbrHR', MOTECMD_NBRHR_FIELDS)
#] ---------------------------------------------------------------------------------

QOcc = namedtuple('QOcc', 'avrg max')

#[ Event structure -----------------------------------------------------------------
# EV_CMD_FINISH, EV_PACKET_SENT
EVENT_CMD_FIELDS = [
   DynStructs.ApiStructField('callbackId',      'int',    4),
   DynStructs.ApiStructField('result',          'int',    1),
]
EventCmd = DynStructs.synthesize('EventCmd', EVENT_CMD_FIELDS)

# EV_PATH_CREATE, EV_PATH_DELETE
EVENT_PATH_FIELDS = [
   DynStructs.ApiStructField('source',          'array',  8),
   DynStructs.ApiStructField('dest',            'array',  8),
   DynStructs.ApiStructField('direction',       'int',    1),
]
EventPath = DynStructs.synthesize('EventPath', EVENT_PATH_FIELDS)

# EV_PING_RESP
EVENT_PING_FIELDS = [
   DynStructs.ApiStructField('callbackId',      'int',    4),
   DynStructs.ApiStructField('mac',             'array',  8),
   DynStructs.ApiStructField('delay',           'sint',   4),
   DynStructs.ApiStructField('voltage',         'int',    2),
   DynStructs.ApiStructField('temperature',     'sint',   1),
]   
EventPing = DynStructs.synthesize('EventPing', EVENT_PING_FIELDS)

# EV_MOTE_RESET, EV_MOTE_JOIN, EV_MOTE_OPER, EV_MOTE_LOST, EV_MOTE_BANDWIDTH
EVENT_MOTE_FIELDS = [
   DynStructs.ApiStructField('mac',             'array',  8),
]   
EventMote = DynStructs.synthesize('EventMote', EVENT_MOTE_FIELDS)

# EV_MOTE_CREATE, EV_MOTE_DELETE
EVENT_MOTEID_FIELDS = [
   DynStructs.ApiStructField('mac',             'array',  8),
   DynStructs.ApiStructField('moteId',          'int',    2),
]   
EventMoteId = DynStructs.synthesize('EventMoteId', EVENT_MOTEID_FIELDS)

# EV_NET_TIME
EVENT_TIME_FIELDS = [
   DynStructs.ApiStructField('uptime',          'int',    4),
   DynStructs.ApiStructField('asn',             'array',  5),
   DynStructs.ApiStructField('encoding',        'int',    1),
   DynStructs.ApiStructField('utcSecs',         'int',    4),
   DynStructs.ApiStructField('utcUsecs',        'int',    4),
]   
EventTime = DynStructs.synthesize('EventTime', EVENT_TIME_FIELDS)

#] ---------------------------------------------------------------------------------

class Event(object):
    '''Event notification class

    Attributes:
    raw_data    : original notification data as a string
    event_id    : event ID as integer
    event_type  : event type as integer
    time        : arrival timestamp as datetime
    event_data  : event data as an array of integer bytes
    mac         : (if appropriate)
    parsed_data : event specific data
    '''

    def __init__(self, data):
        self.raw_data = data
        (self.event_id, self.event_type) = struct.unpack('!ib', data[0:5])
        # (most) events don't have a timestamp in the data
        self.time = datetime.datetime.now()
        # turn event_data into a list of byte values rather than a string
        self.event_data = [ord(c) for c in data[5:]]
        # shortcut, lots of events have a mac as the first dynamic element
        self.parsed_data = None
        self.mac = None
        
        if self.event_type in (API.EV_MOTE_RESET, API.EV_MOTE_JOIN, API.EV_MOTE_OPER, 
                               API.EV_MOTE_LOST, API.EV_MOTE_BANDWIDTH):
            self.parsed_data = DynStructs.parse(EventMote, data[5:])
            self.mac = self.parsed_data.mac

        elif self.event_type in (API.EV_MOTE_CREATE, API.EV_MOTE_DELETE):
            self.parsed_data = DynStructs.parse(EventMoteId, data[5:])
            self.mac = self.parsed_data.mac

        elif self.event_type in (API.EV_PATH_CREATE, API.EV_PATH_DELETE):
            self.parsed_data = DynStructs.parse(EventPath, data[5:])
            self.mac = self.parsed_data.source

        elif self.event_type in (API.EV_CMD_FINISH, API.EV_PACKET_SENT):
            self.parsed_data = DynStructs.parse(EventCmd, data[5:])

        elif self.event_type == API.EV_PING_RESP:
            self.parsed_data = DynStructs.parse(EventPing, data[5:])
    
        elif self.event_type == API.EV_NET_TIME:
            self.parsed_data = DynStructs.parse(EventTime, data[5:])
    
    def __str__(self):
        if self.parsed_data:
           data_str = str(self.parsed_data)
        else:
           data_str = ' '.join(['%02X' % b for b in self.event_data]) + '\n'
        if self.event_type in EVENT_TYPES_STR:
           evntType = EVENT_TYPES_STR[self.event_type]
        else:
           evntType = str(self.event_type)
        return "EVENT: id=%d '%s'\n%s" % (self.event_id, evntType, data_str)

class Data(object):
    '''Data notification class (API protocol v4)

    Attributes:
    raw_data    : original notification data as a string
    secs, usecs : packet timestamp (generated time)
    mac         : mac address as an array of integer bytes
    src_port, dest_port : source and destination ports as integers
    payload_str : payload in the raw string representation
    payload     : payload as an array of integer bytes
    '''

    def __init__(self, data):
        self.raw_data = data
        (self.secs, self.usecs) = struct.unpack('!ql', data[0:12])
        self.mac = [ord(c) for c in data[12:20]]
        (self.src_port, self.dest_port) = struct.unpack('!HH', data[20:24])
        # 
        self.payload_str = data[24:]
        # turn payload into an array of byte values rather than a string
        self.payload = array('B', self.payload_str)

    def __str__(self):
        mac_str = '-'.join(['%02X' % c for c in self.mac])
        payload_str = ' '.join(['%02X' % b for b in self.payload])
        return 'DATA: [%d.%d] src=%s:%x dest=%x: %s' % (self.secs, self.usecs, mac_str, self.src_port, self.dest_port, payload_str)

class Data_v3(object):
    '''Data notification class (API protocol v3)

    Attributes:
    raw_data    : original notification data as a string
    secs, usecs : packet timestamp (generated time)
    mac         : mac address as an array of integer bytes
    src_port, dest_port : source and destination ports as integers
    payload_str : payload in the raw string representation
    payload     : payload as an array of integer bytes
    '''

    def __init__(self, data):
        self.raw_data = data
        (self.secs, self.usecs) = struct.unpack('!ll', data[1:9])
        self.mac = [ord(c) for c in data[9:17]]
        (self.src_port, self.dest_port) = struct.unpack('!HH', data[17:21])
        # 
        self.payload_str = data[21:]
        # turn payload into an array of byte values rather than a string
        self.payload = array('B', self.payload_str)

    def __str__(self):
        mac_str = '-'.join(['%02X' % c for c in self.mac])
        payload_str = ' '.join(['%02X' % b for b in self.payload])
        return 'DATA: [%d.%d] src=%s:%x dest=%x: %s' % (self.secs, self.usecs, mac_str, self.src_port, self.dest_port, payload_str)


# Health Report Class =================================================================
class HealthReport(object): 
   '''Health Report notification class

      Attributes:
      raw_data    : original notification data as a string
      mac         : mac address as an array of integer bytes
      devHR       : device health report as named tuple
                    (charge, QOcc, temperature, batteryVolt, numTxOk, 
                     numTxFail, numRxOk, numRxLost, numMacDrop, numTxBad, 
                     badLink_frameId, badLink_offset)
      QOcc        : size ofmote queue as named tuple
                    (avrg, max)
      nbrDscv[]   : neighbors health reports as list of named tuples
                    (nbrId, nbrFlag, rsl, numTxPk, numTxFail, numRxPk)
      dscvrDef[]  : discovered neighbors as list of named tuples
                    (moteId, rsl, numRx)
   '''
   
   def __init__(self, data):
      
      self.raw_data = data
      self.nbrDscv = []
      self.nbrHR = []
      self.devHR = ()
      self.QOcc = ()
      
      if data:
          self.mac = [ord(c) for c in data[0:8]]
          i = 8 # Skip MAC
          
          # Parse Mote Commands
          while (i+2 <= len(data)) :
             (cmdId, cmdLen) = struct.unpack('!BB', data[i:i+2])
             if (i + 2 + cmdLen > len(data)) :
                break;
                
             curPos = i + 2 # Skip CmdID:Length

             if (cmdId == 0x80) : 
                # Device HR
                if (cmdLen >= MoteCmdDevHR.size) :
                   self.devHR  = DynStructs.parse(MoteCmdDevHR, data[curPos : curPos+cmdLen])
                   self.QOcc = QOcc(self.devHR.QOcc & 0xF, (self.devHR.QOcc >> 4) & 0xF)
                
             elif (cmdId == 0x82) : 
                # Discovery.  curPos + 2 for skip two 1-byte field Number of neigbours, Number of Join neigbours
                if (cmdLen >= 2) :
                   self.nbrDscv = DynStructs.parse_array(MoteCmdDscvr, data[curPos+2 : curPos + cmdLen])
                
             elif (cmdId == 0x81) : 
                # Neighbors HR.  curPos + 1 for skip one 1-byte field Number of neigbours
                if (cmdLen >= 1) :
                   self.nbrHR = DynStructs.parse_array(MoteCmdNbrHR, data[curPos+1 : curPos + cmdLen])
             
             i += cmdLen + 2;

   def __str__(self):
      res = DynStructs.pair_to_string('mac', self.mac)
      divider = '- - - - - - - - - - - -'
      if (self.devHR) :
         res += DynStructs.pair_to_string('Device HR', divider) + str(self.devHR)
         res += DynStructs.pair_to_string('Qavrg', self.QOcc.avrg)
         res += DynStructs.pair_to_string('Qmax',  self.QOcc.max)
      for f in self.nbrDscv :
         res += DynStructs.pair_to_string('Neighbors Discovery', divider) + str(f)
      for f in self.nbrHR :
         res += DynStructs.pair_to_string('Neighbors HR', divider) + str(f)
      return res
        

