'''API Definition for HART Manager XML API'''

import ApiDefinition

import xmlutils
import re

# Add a log handler for the HART Manager

import logging
class NullHandler(logging.Handler):
    def emit(self, record):
        pass

log = logging.getLogger('HartManager')
log.setLevel(logging.INFO)
log.addHandler(NullHandler())

##
# \ingroup ApiDefinition
#

class HartMgrDefinition(ApiDefinition.ApiDefinition):
    '''
    \brief API definition for the HART manager.
   
    \note This class inherits from ApiDefinition. It redefines the attributes of
          its parent class, but inherits the methods.
    '''

    FIELDS = 'unnamed'
    
    STRING    = ApiDefinition.FieldFormats.STRING
    BOOL      = ApiDefinition.FieldFormats.BOOL
    INT       = ApiDefinition.FieldFormats.INT
    INTS      = ApiDefinition.FieldFormats.INTS
    FLOAT     = ApiDefinition.FieldFormats.FLOAT
    HEXDATA   = ApiDefinition.FieldFormats.HEXDATA
    RC        = ApiDefinition.ApiDefinition.RC
    SUBID1    = ApiDefinition.ApiDefinition.SUBID1
    LIST      = 'list'

    # Enumerations
    # fieldOptions is a list of [ value, description, ?? ]
    fieldOptions = {
        RC : [
            [0x0,                      'OK',                    ''],
            # ...
        ],
        'bool' : [
            ['true',                   'true',                  ''],
            ['false',                  'false',                 ''],
        ],
        'appDomain' : [
            ['maintenance',            'maintenance',           ''],
        ],
        'packetPriority' : [
            ['low',                    'low',                   ''],
            ['high',                   'high',                  ''],
        ],
        'pipeDirection' : [
            ['UniUp',                  'upstream',              ''],
            ['UniDown',                'downstream',            ''],
            ['Bi',                     'bidirectional',         ''],
        ],
        'moteState' : [
            ['Idle',                   'idle',                  ''],
            ['Lost',                   'lost',                  ''],
            ['Joining',                'joining',               ''],
            ['Operational',            'operational',           ''],
            ['Disconnecting',          'disconnecting',         ''],
        ],
        'pathDirection' : [
            ['all',                    'all',                   ''],
            ['upstream',               'upstream',              ''],
            ['downstream',             'downstream',            ''],
            ['unused',                 'unused',                ''],
        ],
        'bandwidthProfile' : [
            ['Manual',                 'manual profile',        ''],
            ['P1',                     'normal profile',        ''],
            ['P2',                     'low-power profile',     ''],
        ], 
        'securityMode' : [
            ['acceptACL',              'Accept ACL',             ''],
            ['acceptCommonJoinKey',    'Accept common join key', '']
        ],
        'userPrivilege' : [
            ['viewer',                 'viewer',                ''],
            ['user',                   'user',                  ''],
            ['superuser',              'superuser',             ''],
        ],
        'onOff' : [
            ['on',                     'on',                    ''],
            ['off',                    'off',                   ''],
        ],
        'resetObject' : [
            ['network',                'network',               ''],
            ['system',                 'system',                ''],
            ['stat',                   'statistics',            ''],
            ['eventLog',               'eventLog',              ''],
        ],
        'resetMote' : [
            ['mote',                   'mote',                  ''],
        ],
        'statPeriod': [
            ['current',                'current',               ''],
            ['lifetime',               'lifetime',              ''],
            ['short',                  'short',                 ''],
            ['long',                   'long',                  ''],
        ],
        'advertisingStatus': [
            ['on',                     'on',                    ''],
            ['off',                    'off',                   ''],
            ['pending',                'pending',               ''],
        ],
        'pipeStatus': [
            ['off',                    'off',                     ''],
            ['pending',                'Pipe activation pending', ''],
            ['on_bi',                  'Bidirection pipe on',     ''],
            ['on_up',                  'Upstream pipe on',        ''],
            ['on_down',                'Downstream pipe on',      ''],
        ],
        'locationTag': [
            ['supported',              'supported',               ''],
            ['not supported',          'not supported',           ''],
        ],
        'redundancyMode': [
            ['standalone',             'standalone',              ''],
            ['transToMaster',          'Transitioning to master', ''],
            ['transToSlave',           'Transitioning to slave',  ''],
            ['master',                 'master',                  ''],
            ['slave',                  'slave',                   ''],
            ['failed',                 'Manager failed',          ''],
        ],
        'redundancyPeerStatus': [
            ['unknown',                'unknown',                 ''],
            ['connected',              'connected',               ''],
            ['synchronized',           'synchronized',            ''],
        ],
        'channelType': [
            ['cli',                    'Manager CLI',             ''],
            ['config',                 'API control',             ''],
            ['notif',                  'API notifications',       ''],
        ],
        'alarmType': [
            ['moteDown',               'Mote down alarm',         ''],
            ['slaReliability',         'SLA Reliability',         ''],
            ['slaLatency',             'SLA Latency',             ''],
            ['slaStability',           'SLA Stability',           ''],
            ['maxMotesReached',        'Maximum number of motes reached',  ''],
            ['bbLatencyWarn',          'Backbone latency warning',''],
        ],
    }


    # ----------------------------------------------------------------------
    # Notifications
    
    eventNotifications = [
        {
            'id'         : 'sysConnect',
            'name'       : 'UserConnect',
            'description': '',
            'response'   : {
                'FIELDS':  [
                    ['channel',             STRING,   16,  'channelType'],
                    ['ipAddr',              STRING,   16,  None],
                    ['userName',            STRING,   32,  None],
                ],
            },
        },
        {
            'id'         : 'sysDisconnect',
            'name'       : 'UserDisconnect',
            'description': '',
            'response'   : {
                'FIELDS':  [
                    ['channel',             STRING,   16,  'channelType'],
                    ['ipAddr',              STRING,   16,  None],
                    ['userName',            STRING,   32,  None],
                ],
            },
        },
        {
            'id'         : 'sysManualMoteReset',
            'name'       : 'ManualMoteReset',
            'description': '',
            'response'   : {
                'FIELDS':  [
                    ['userName',            STRING,   32,  None],
                    ['moteId',              INT,      4,   None],
                    ['macAddr',             STRING,   32,  None],
                ],
            },
        },
        {
            'id'         : 'sysManualMoteDelete',
            'name'       : 'ManualMoteDelete',
            'description': '',
            'response'   : {
                'FIELDS':  [
                    ['userName',            STRING,   32,  None],
                    ['moteId',              INT,      4,   None],
                    ['macAddr',             STRING,   32,  None],
                ],
            },
        },
        {
            'id'         : 'sysManualMoteDecommission',
            'name'       : 'ManualMoteDecommission',
            'description': '',
            'response'   : {
                'FIELDS':  [
                    ['userName',            STRING,   32,  None],
                    ['moteId',              INT,      4,   None],
                    ['macAddr',             STRING,   32,  None],
                ],
            },
        },
        {
            'id'         : 'sysManualNetReset',
            'name'       : 'ManualNetReset',
            'description': '',
            'response'   : {
                'FIELDS':  [
                    ['userName',            STRING,   32,  None],
                ],
            },
        },
        {
            'id'         : 'sysManualDccReset',
            'name'       : 'ManualDccReset',
            'description': '',
            'response'   : {
                'FIELDS':  [
                    ['userName',            STRING,   32,  None],
                ],
            },
        },
        {
            'id'         : 'sysManualStatReset',
            'name'       : 'ManualStatReset',
            'description': '',
            'response'   : {
                'FIELDS':  [
                    ['userName',            STRING,   32,  None],
                ],
            },
        },
        {
            'id'         : 'sysConfigChange',
            'name'       : 'ConfigChange',
            'description': '',
            'response'   : {
                'FIELDS':  [
                    ['userName',            STRING,   32,  None],
                    ['objectType',          STRING,   32,  None], # TODO: enum
                    ['objectId',            STRING,   32,  None],
                ],
            },
        },

        {
            'id'         : 'sysBootUp',
            'name'       : 'BootUp',
            'description': '',
            'response'   : {
                'FIELDS':  [
                    # None
                ],
            },
        },
        {
            'id'         : 'netReset',
            'name'       : 'NetworkReset',
            'description': '',
            'response'   : {
                'FIELDS':  [
                    # None
                ],
            },
        },
        {
            'id'         : 'sysCmdFinish',
            'name'       : 'CommandFinished',
            'description': '',
            'response'   : {
                'FIELDS':  [
                    ['callbackId',          INT,      4,   None],
                    ['objectType',          STRING,   32,  None], # TODO: enum
                    ['macAddr',             STRING,   32,  None],
                    ['resultCode',          INT,      4,   None],
                ],
            },
        },
        {
            'id'         : 'netPacketSent',
            'name'       : 'PacketSent',
            'description': '',
            'response'   : {
                'FIELDS':  [
                    ['callbackId',          INT,      4,   None],
                    ['macAddr',             STRING,   32,  None],
                ],
            },
        },
        {
            'id'         : 'netMoteJoin',
            'name'       : 'MoteJoin',
            'description': '',
            'response'   : {
                'FIELDS':  [
                    ['moteId',              INT,      4,   None],
                    ['macAddr',             STRING,   32,  None],
                    ['reason',              STRING,   64,  None], # TODO: length
                    ['userData',            STRING,   64,  None], # TODO: length
                ],
            },
        },
        {
            'id'         : 'netMoteLive',
            'name'       : 'MoteLive',
            'description': '',
            'response'   : {
                'FIELDS':  [
                    ['moteId',              INT,      4,   None],
                    ['macAddr',             STRING,   32,  None],
                    ['reason',              STRING,   64,  None], # TODO: length
                ],
            },
        },
        {
            'id'         : 'netMoteQuarantine',
            'name'       : 'MoteQuarantine',
            'description': '',
            'response'   : {
                'FIELDS':  [
                    ['moteId',              INT,      4,   None],
                    ['macAddr',             STRING,   32,  None],
                    ['reason',              STRING,   64,  None], # TODO: length
                ],
            },
        },
        {
            'id'         : 'netMoteJoinQuarantine',
            'name'       : 'MoteJoinQuarantine',
            'description': '',
            'response'   : {
                'FIELDS':  [
                    ['moteId',              INT,      4,   None],
                    ['macAddr',             STRING,   32,  None],
                    ['reason',              STRING,   64,  None], # TODO: length
                    ['userData',            STRING,   64,  None], # TODO: length
                ],
            },
        },
        {
            'id'         : 'netMoteUnknown',
            'name'       : 'MoteUnknown',
            'description': '',
            'response'   : {
                'FIELDS':  [
                    ['moteId',              INT,      4,   None],
                    ['macAddr',             STRING,   32,  None],
                    ['reason',              STRING,   64,  None], # TODO: length
                ],
            },
        },
        {
            'id'         : 'netMoteDisconnect',
            'name'       : 'MoteDisconnect',
            'description': '',
            'response'   : {
                'FIELDS':  [
                    ['moteId',              INT,      4,   None],
                    ['macAddr',             STRING,   32,  None],
                    ['reason',              STRING,   64,  None], # TODO: length
                ],
            },
        },
        {
            'id'         : 'netMoteJoinFailure',
            'name'       : 'MoteJoinFailure',
            'description': '',
            'response'   : {
                'FIELDS':  [
                    ['macAddr',             STRING,   32,  None],
                    ['reason',              STRING,   64,  None], # TODO: length
                ],
            },
        },
        {
            'id'         : 'netMoteInvalidMIC',
            'name'       : 'InvalidMIC',
            'description': '',
            'response'   : {
                'FIELDS':  [
                    ['macAddr',             STRING,   32,  None],
                ],
            },
        },
        {
            'id'         : 'netPathCreate',
            'name'       : 'PathCreate',
            'description': '',
            'response'   : {
                'FIELDS':  [
                    ['pathId',              INT,      4,   None],
                    ['moteAMac',            STRING,   32,  None],
                    ['moteBMac',            STRING,   32,  None],
                ],
            },
        },
        {
            'id'         : 'netPathDelete',
            'name'       : 'PathDelete',
            'description': '',
            'response'   : {
                'FIELDS':  [
                    ['pathId',              INT,      4,   None],
                    ['moteAMac',            STRING,   32,  None],
                    ['moteBMac',            STRING,   32,  None],
                ],
            },
        },
        {
            'id'         : 'netPathActivate',
            'name'       : 'PathActivate',
            'description': '',
            'response'   : {
                'FIELDS':  [
                    ['pathId',              INT,      4,   None],
                    ['moteAMac',            STRING,   32,  None],
                    ['moteBMac',            STRING,   32,  None],
                ],
            },
        },
        {
            'id'         : 'netPathDeactivate',
            'name'       : 'PathDeactivate',
            'description': '',
            'response'   : {
                'FIELDS':  [
                    ['pathId',              INT,      4,   None],
                    ['moteAMac',            STRING,   32,  None],
                    ['moteBMac',            STRING,   32,  None],
                ],
            },
        },
        {
            'id'         : 'netPathAlert',
            'name'       : 'PathAlert',
            'description': '',
            'response'   : {
                'FIELDS':  [
                    ['pathId',              INT,      4,   None],
                    ['moteAMac',            STRING,   32,  None],
                    ['moteBMac',            STRING,   32,  None],
                ],
            },
        },
        {
            'id'         : 'netPipeOn',
            'name'       : 'PipeOn',
            'description': '',
            'response'   : {
                'FIELDS':  [
                    ['macAddr',             STRING,   32,  None],
                    ['allocatedPipePkPeriod', INT,    4,   None],
                ],
            },
        },
        {
            'id'         : 'netPipeOff',
            'name'       : 'PipeOff',
            'description': '',
            'response'   : {
                'FIELDS':  [
                    ['macAddr',             STRING,   32,  None],
                ],
            },
        },
        {
            'id'         : 'netServiceDenied',
            'name'       : 'ServiceDenied',
            'description': '',
            'response'   : {
                'FIELDS':  [
                    ['serviceId',          INT,      4,   None],
                    ['requestingMacAddr',  STRING,   32,  None],
                    ['peerMacAddr',        STRING,   32,  None],
                    ['appDomain',          STRING,   32,  'appDomain'],
                    ['isSource',           BOOL,     1,   None],
                    ['isSink',             BOOL,     1,   None],
                    ['isIntermittent',     BOOL,     1,   None],
                    ['period',             INT,      4,   None],
                ],
            },
        },
        {
            'id'         : 'netPingReply',
            'name'       : 'PingReply',
            'description': '',
            'response'   : {
                'FIELDS':  [
                    ['macAddr',             STRING,   32,  None],
                    ['callbackId',          INT,      4,   None],
                    ['latency',             INT,      4,   None],
                    ['temperature',         FLOAT,    8,   None],
                    ['voltage',             FLOAT,    8,   None],
                    ['hopCount',            INT,      4,   None],
                ],
            },
        },
        {
            'id'         : 'netTransportTimeout',
            'name'       : 'TransportTimeout',
            'description': '',
            'response'   : {
                'FIELDS':  [
                    ['srcMacAddr',          STRING,   32,  None],
                    ['destMacAddr',         STRING,   32,  None],
                    ['timeoutType',         STRING,   32,  None], # TODO: timeout type
                    ['callbackId',          INT,      4,   None],
                ],
            },
        },

        # TODO: redundancy events: sysRdntModeChange, sysRdntPeerStatusChange
        # TODO: alarm open and close have sub-events
    ]

    measurementNotifications = [
        {
            'id'         : 'location',
            'name'       : 'Location',
            'description': '',
            'response'   : {
                'FIELDS':  [
                    ['ver',                 INT,      1,   None],
                    ['asn',                 INT,      8,   None],
                    ['src',                 STRING,   32,  None],
                    ['dest',                STRING,   32,  None],
                    ['payload',             HEXDATA, None, None],
                ],
            },
        },
    ]
    
    notifications = [
        {
            'id'         : 'event',
            'name'       : 'event',
            'description': '',
            'response'   : {
                'FIELDS':  [
                    ['timeStamp',           INT,      8,   None],
                    ['eventId',             INT,      4,   None],
                    [SUBID1,                INT,      1,   None],
                ]
            },
            'subCommands': eventNotifications,
            'deserializer': 'parse_eventNotif',
        },
        {
            'id'         : 'data',
            'name'       : 'data',
            'description': '',
            'response'   : {
                'FIELDS':  [
                    ['moteId',              INT,      4,   None],
                    ['macAddr',             STRING,   32,  None],
                    ['time',                INT,      8,   None],
                    ['payload',             HEXDATA, None, None],
                    ['payloadType',         INT,      1,   None],
                    ['isReliable',          BOOL,     1,   None],
                    ['isRequest',           BOOL,     1,   None],
                    ['isBroadcast',         BOOL,     1,   None],
                    ['callbackId',          INT,      4,   None],
                    # counter field added in 4.1.0.2
                    ['counter',             INT,      4,   None],
                ]
            },
            'deserializer': 'parse_dataNotif',
        },
        {
            'id'         : 'measurement',
            'name'       : 'measurement',
            'description': '',
            'response'   : {
                'FIELDS':  [
                    [SUBID1,                INT,      1,   None],
                ]
            },
            'subCommands': measurementNotifications,
        },
        {
            'id'         : 'cli',
            'name'       : 'cli',
            'description': '',
            'response'   : {
                'FIELDS':  [
                    ['time',                INT,      8,   None],
                    ['message',             STRING,   128, None],
                ]
            },
        },
        {
            'id'         : 'log',
            'name'       : 'log',
            'description': '',
            'response'   : {
                'FIELDS':  [
                    ['time',                INT,      8,   None],
                    ['severity',            STRING,   16,  None],
                    ['message',             STRING,   128, None],
                ]
            },
        },
        {
            'id'         : 'stdMoteReport',
            'name'       : 'stdMoteReport',
            'description': '',
            'response'   : {
                'FIELDS':  [
                    ['time',     INT,      8,   None],
                    ['macAddr',  STRING,   16,  None],
                    ['payload',  HEXDATA, None, None],
                ]
            },
        },
        {
            'id'         : 'vendorMoteReport',
            'name'       : 'vendorMoteReport',
            'description': '',
            'response'   : {
                'FIELDS':  [
                    ['time',     INT,      8,   None],
                    ['macAddr',  STRING,   16,  None],
                    ['payload',  HEXDATA, None, None],
                ]
            },
        },
    ]

    # Notification parsing

    def parse_dataNotif(self, notif_str, notif_fields):
        data_dict = self._parse_xmlobj(notif_str, 'data', notif_fields)
        log.debug('DATA: %s' % str(data_dict))
        # reconvert payload type as a hex value
        data_dict['payloadType'] = int(str(data_dict['payloadType']), 16)
        # set default values for any fields that aren't present
        DEFAULTS = (('isRequest', False),
                    ('isReliable', False),
                    ('isBroadcast', False),
                    ('callbackId', 0))
        for f, v in DEFAULTS:
            if not data_dict[f]:
                data_dict[f] = v
        return (['data'], data_dict)

    def parse_eventNotif(self, notif_str, notif_fields):
        obj_dict = self._parse_xmlobj(notif_str, 'event', None)
        log.debug('EVENT: %s' % str(obj_dict))
        
        event_name = ['event']
        event_dict = {}
        for event_attr, val in obj_dict.items():
            if type(val) is dict:
                event_name += [self.subcommandIdToName(self.NOTIFICATION, event_name, event_attr)]
                subevent_fields = self.getResponseFields(self.NOTIFICATION, event_name)
                event_dict.update(self._xml_parse_fieldset(val, subevent_fields))
            else:
                # we assume that all event fields are defined
                field = [f for f in notif_fields if f.name == event_attr][0]
                event_dict[event_attr] = self._xml_parse_field(val, field)
        return (event_name, event_dict)

    def parse_notif(self, notif_name, notif_str):
        notif_metadata = self.getDefinition(self.NOTIFICATION, notif_name)
        notif_fields = self.getResponseFields(self.NOTIFICATION, notif_name)
        if notif_metadata.has_key('deserializer'):
            deserialize_func = getattr(self, notif_metadata['deserializer'])
            notif_name, notif_dict = deserialize_func(notif_str, notif_fields)
        else:
            notif_dict = self._parse_xmlobj(notif_str, notif_name[0], notif_fields)
        return (notif_name, notif_dict)
    
    # XML-RPC Serializer
    
    def _xmlrpc_format_field(self, field_value, field_metadata):
        if field_metadata[1] == self.HEXDATA:
            return ''.join(['%02X' % b for b in field_value])
        else:
            return field_value

    def default_serializer(self, commandArray, fields):
        cmd_metadata = self.getDefinition(self.COMMAND, commandArray)
        param_list = []
        # for each field in the input parameters, look up the value in cmd_params
        for p in cmd_metadata['request']:
            param_name = p[0]
            # format the parameter by type
            param_list.append(self._xmlrpc_format_field(fields[param_name], p))
        # param_list = [self.format_field(fields[f[0]], f) for f in cmd_metadata['request']]
        return param_list


    # XML-RPC Deserializer

    def _xml_parse_field(self, str_value, field_metadata):
        if field_metadata.format in [self.INT, self.INTS]:
            return int(str_value)
        elif field_metadata.format == self.FLOAT:
            return float(str_value)
        elif field_metadata.format == self.BOOL:
            if str_value.lower() == 'true':
                return True
            else:
                return False
        elif field_metadata.format == self.HEXDATA:
            returnVal = [int(str_value[i:i+2], 16) for i in range(0, len(str_value), 2)]
            return returnVal
        else: 
            return str_value

    def _xml_parse_fieldset(self, obj_dict, fields_metadata):
        'Filter and parse fields in obj_dict'
        filtered_dict = {}
        for field in fields_metadata:
            try:
                field_str = obj_dict[field.name]
                filtered_dict[field.name] = self._xml_parse_field(field_str, field)
            except KeyError:
                # some fields are not always present (especially in Statistics)
                filtered_dict[field.name] = ''
        return filtered_dict

    def _parse_xmlobj(self, xml_doc, base_element, fields_metadata, isArray = False):
        log.debug('Parsing XML: %s %s', base_element, xml_doc)
        aFull_resp = xmlutils.parse_xml_obj(xml_doc, base_element, fields_metadata)
        aRes = []
        for full_resp in aFull_resp : 
            if fields_metadata:
                # parse each field listed in the fields_metadata
                res = self._xml_parse_fieldset(full_resp, fields_metadata)
            else:
                res = full_resp
            if not isArray :
                return res
            aRes.append(res)
        return aRes
    
    def default_deserializer(self, cmd_metadata, xmlrpc_resp):
        resp = {}
        #resp = {'_raw_': xmlrpc_resp}
        resp_fields = self.getResponseFields(self.COMMAND, [cmd_metadata['name']])
        if cmd_metadata['response'].has_key(self.FIELDS):
            # unnamed fields are processed in order
            # note: special case the single return value
            if len(resp_fields) is 1:
                resp[resp_fields[0].name] = self._xml_parse_field(xmlrpc_resp, resp_fields[0])
            else:
                for i, field in enumerate(resp_fields):
                    resp[field.name] = self._xml_parse_field(xmlrpc_resp[i], field)

        elif cmd_metadata['id'] in ['getConfig', 'setConfig'] :
            # default getConfig parser
            # TODO: need an ApiDefinition method to get the response object name
            resp_obj = cmd_metadata['response'].keys()[0]
            isArray = False
            if ('isResponseArray' in cmd_metadata) :
                isArray = cmd_metadata['isResponseArray']
            resp = self._parse_xmlobj(xmlrpc_resp, resp_obj, resp_fields, isArray)
        
        return resp

    def deserialize(self, cmd_name, xmlrpc_resp):
        '''\brief Returns the XML-RPC response as a dict

        \returns A tuple of commandName and the response dictionary, 
                 which contains each of the fields of the response. 
        '''
        cmd_metadata = self.getDefinition(self.COMMAND, cmd_name)
        if cmd_metadata.has_key('deserializer'):
            deserializer = getattr(self, cmd_metadata['deserializer'])
        else:
            deserializer = self.default_deserializer
        resp = deserializer(cmd_metadata, xmlrpc_resp)
        return resp
    
    # ----------------------------------------------------------------------
    # Command-specific serialization methods
    # (must be defined ahead of commands)

    def serialize_getConfig(self, commandArray, cmd_params):
        '''\brief Returns an array of parameters for a typical getConfig query
        '''
        cmd_metadata = self.getDefinition(self.COMMAND, commandArray)
        prefix = []
        if 'serializerParam' in cmd_metadata:
            prefix = cmd_metadata['serializerParam']
        config_query = xmlutils.dict_to_xml(cmd_params, prefix)
        return ['all', config_query]

    def serialize_getNetworkStats(self, commandArray, cmd_params):
        stat_query = self._build_stat_set(cmd_params['period'], cmd_params['index'])
        return ['all', '<config><Network><Statistics>%s</Statistics></Network></config>' % stat_query]

    def serialize_getMote(self, commandArray, cmd_params):
        config_doc = '<config><Motes><Mote><macAddr>%s</macAddr></Mote></Motes></config>' % (cmd_params['macAddr'])
        return ['all', config_doc]

    def serialize_getMoteStats(self, commandArray, cmd_params):
        stat_query = self._build_stat_set(cmd_params['period'], cmd_params['index'])
        config_doc = '<config><Motes><Mote><macAddr>%s</macAddr><Statistics>%s</Statistics></Mote></Motes></config>' % (cmd_params['macAddr'], stat_query)
        return ['all', config_doc]

    def serialize_getPath(self, commandArray, cmd_params):
        config_doc = '<config><Paths><Path><moteMac>%s</moteMac></Path></Paths></config>' % (cmd_params['moteMac'])
        return ['all', config_doc]
    
    def serialize_getPathStats(self, commandArray, cmd_params):
        stat_query = self._build_stat_set(cmd_params['period'], cmd_params['index'])
        config_doc = '<config><Paths><Path><pathId>%s</pathId><Statistics>%s</Statistics></Path></Paths></config>' % (cmd_params['pathId'], stat_query)
        return ['all', config_doc]

    def serialize_getUser(self, commandArray, cmd_params):
        config_doc = '<config><Users><User><userName>%s</userName></User></Users></config>' % (cmd_params['userName'], )
        return ['all', config_doc]


    def _configDoc_format_field(self, field_value, field_metadata):
        if field_metadata[1] == self.HEXDATA:
            return ''.join(['%02X' % b for b in field_value])
        elif field_metadata[1] == self.BOOL:
            return 'true' if field_value else 'false'
        else:
            return str(field_value)

    def serialize_setConfig(self, commandArray, fields) :
        cmd_metadata = self.getDefinition(self.COMMAND, commandArray)
        prefix = []
        if 'serializerParam' in cmd_metadata : 
            prefix = cmd_metadata['serializerParam']
        param_dict = {}
        # for each field in the input parameters, look up the value in cmd_params
        for p in cmd_metadata['request']:
            param_name = p[0]
            # format the parameter by type
            param_dict[param_name] = self._configDoc_format_field(fields[param_name], p)
        config_doc = xmlutils.dict_to_xml(param_dict, prefix)
        return [config_doc]

    def serialize_setBlacklist(self, commandArray, fields):
        cmd_metadata = self.getDefinition(self.COMMAND, commandArray)
        prefix = []
        if 'serializerParam' in cmd_metadata : 
            prefix = cmd_metadata['serializerParam']
        params = fields['frequency'].split()        
        return [xmlutils.list_to_xml(params, 'frequency', prefix)]

    def _build_stat_set(self, period, index = 0):
        STAT_PERIOD_QUERY_TMPL = '<{0}Set><{0}><index>{1}</index></{0}></{0}Set>'
        if period in ['current']:
            return '<statCur/>'
        elif period in ['lifetime']:
            return '<lifetime/>'
        elif period in ['short']:
            return STAT_PERIOD_QUERY_TMPL.format('stat15Min', index)
        elif period in ['long']:
            return STAT_PERIOD_QUERY_TMPL.format('stat1Day', index)
        else:
            raise RuntimeError('invalid stat period: %s', period)
    
    # ----------------------------------------------------------------------
    # Command-specific deserialization methods
    # (must be defined ahead of commands)

    def deserialize_getStats(self, cmd_metadata, xmlrpc_resp):
        net_stats = {}
        fields = self.getResponseFields(self.COMMAND, [cmd_metadata['name']])
        # parse the Statistics element
        resp_dict = self._parse_xmlobj(xmlrpc_resp, 'Statistics', None)
        # detect the statistics period
        stat_dict = {}
        if 'statCur' in resp_dict:
            stat_dict = resp_dict['statCur']
        elif 'lifetime' in resp_dict:
            stat_dict = resp_dict['lifetime']
        elif 'stat15MinSet' in resp_dict:
            stat_dict = resp_dict['stat15MinSet']['stat15Min']
        elif 'stat1DaySet' in resp_dict:
            stat_dict = resp_dict['stat1DaySet']['stat1Day']
        # if there are no statistics for the requested period, stat_dict may be a string 
        if type(stat_dict) != dict:
            stat_dict = {}
        # fill in the statistics fields
        for field in fields:
            try:
                field_str = stat_dict[field.name]
                net_stats[field.name] = self._xml_parse_field(field_str, field)
            except KeyError:
                # some fields are not always present (especially in Statistics)
                net_stats[field.name] = ''  # default value
        return net_stats

    def deserialize_getSourceRoute(self, cmd_metadata, xmlrpc_resp):
        fields = self.getResponseFields(self.COMMAND, [cmd_metadata['name']])
        resp_dict = self._parse_xmlobj(xmlrpc_resp, 'SourceRoute', None)
        # Ug. deserialization for this case is heavily dependant on response structure
        for path in ['primaryPath', 'secondaryPath']:
            if path in resp_dict and 'macAddr' in resp_dict[path]:
                resp_dict[path] = resp_dict[path]['macAddr']
            else:
                resp_dict[path] = []            
        return resp_dict

    def _parse_alarm(self, alarm_dict, alarm_fields, alarm_types):
        '''Reformat a single Alarm object as a flat list of fields'''
        field_names = [f.name for f in alarm_fields]
        # ensure all expected fields are initialized
        result = {f: '' for f in field_names} 
        for f, v in alarm_dict.items():
            # detect the element identifying the alarm type
            if f in alarm_types:
                result['alarmType'] = f
                # this value may contain a dict of alarm-specific data
                if type(v) is dict:
                    # for any matching fields in the alarm-specific data,
                    # flatten them into the result
                    for f2, v2 in v.items():
                        if f2 in field_names:
                            result[f2] = v[f2]
            elif f in field_names:
                result[f] = v
        return result

    def deserialize_getOpenAlarms(self, cmd_metadata, xmlrpc_resp):
        fields = self.getResponseFields(self.COMMAND, [cmd_metadata['name']])
        resp_dict = self._parse_xmlobj(xmlrpc_resp, 'Alarms', None)
        # this parses the list of XML Alarms as:
        # {'Alarm': [{'eventId':...}, {'eventId':...}]}
        # but if there's only one Alarm:
        # {'Alarm': {'eventId':...}}
        # Ug. deserialization for this case is heavily dependant on Alarm types
        result = []
        if 'Alarm' in resp_dict:
            alarm_types = self.getResponseFieldOptions(self.COMMAND, [cmd_metadata['name']], 'alarmType').validOptions
            if type(resp_dict['Alarm']) is list:
                # use the list of Alarms
                alarms = resp_dict['Alarm']
            elif type(resp_dict['Alarm']) is dict:
                # put the single Alarm into a list
                alarms = [resp_dict['Alarm']]
            else:
                raise RuntimeError('invalid Alarm response: can not find Alarm element')
            result = [self._parse_alarm(alarm, fields, alarm_types)
                      for alarm in alarms]            
        return result

    def deserialize_blacklist(self, cmd_metadata, xmlrpc_resp):
        # the same deserializer is used for getConfig and setConfig operations
        resp_fields = self.getResponseFields(self.COMMAND, [cmd_metadata['name']])
        resp_obj = cmd_metadata['response'].keys()[0]
        # cmd_metadata['isResponseArray'] should be True
        resp_dict = xmlutils.parse_xml_obj(xmlrpc_resp, resp_obj, resp_fields)[0]
        # resp_dict['frequency'] contains either a single string or a list of string values
        if type(resp_dict['frequency']) is list:
            resp = [{'frequency': int(freq)} for freq in resp_dict['frequency']]
        else:
            resp = [{'frequency': int(resp_dict['frequency'])}]
        # we return a list of objects containing frequency values
        return resp

    # Commands
    commands = [
        # Get Config commands
        # TODO: use serializer_getConfig instead of command-specific serializers
        
        # activateAdvertising
        {
            'id'         : 'activateAdvertising',
            'name'       : 'activateAdvertising',
            'description': 'Activate advertisement frame',
            'request'    : [
                ['macAddr',                 STRING,   25,  None],
                ['timeout',                 INT,      4,   None]
            ],
            'response'   : {
                FIELDS : [ 
                          ['result',        STRING,   32,  None],
                ],
            },
        },
        # activateFastPipe
        {
            'id'         : 'activateFastPipe',
            'name'       : 'activateFastPipe',
            'description': 'Activate the fast network pipe to the specified mote.',
            'request'    : [
                ['macAddr',                 STRING,   25,  None],
                ['pipeDirection',           STRING,   25,  'pipeDirection'],
            ],
            'response'   : {
                FIELDS : [
                    ['result',              STRING,   32,  None],
                ],
            },
        },
        # cancelOtap
        {
            'id'         : 'cancelOtap',
            'name'       : 'cancelOtap',
            'description': 'This command cancels the OTAP (Over-The-Air-Programming) process to upgrade software on motes and the access point.',
            'request'    : [
            ],
            'response'   : { 
                FIELDS : [ 
                          ['result',        STRING,   32,  None],
                ],
            },
        },
        # cli (deprecated)
        {
            'id'         : 'cli',
            'name'       : 'cli',
            'description': 'This command tunnels a given command through to the manager\'s Command Line Interface (CLI). The CLI command can be called by only one XML API client at a time. The response to the given CLI command is tunneled back to the client via the notifications channel. To receive the CLI notification, the client must be subscribed to CLI notifications (see Notification Channel)',
            'request'    : [
                ['command',                 STRING,   128, None],
            ],
            'response'   : {
                FIELDS : [ 
                    ['result',              STRING,   32,  None],
                ],
            },
        },
        # deactivateFastPipe
        {
            'id'         : 'deactivateFastPipe',
            'name'       : 'deactivateFastPipe',
            'description': 'Deactivate the fast network pipe to the specified mote.',
            'request'    : [
                ['macAddr',                 STRING,   25,  None],
            ],
            'response'   : {
                FIELDS : [
                    ['result',              STRING,   32,  None],
                ],
            },
        },
        # deleteConfig.deleteAcl
        {
            'id'         : 'deleteConfig',
            'name'       : 'deleteAcl',
            'description': 'Remove a device from the ACL',
            'request'    : [
                ['macAddr', STRING, 25, None],
            ],
            'response'   : { 
                FIELDS:  [
                ],
            },
            'serializer' : 'serialize_setConfig',
            'serializerParam' : ['config', 'Security', 'Acl', 'Device'],
        },
        # deleteConfig.deleteMote
        {
            'id'         : 'deleteConfig',
            'name'       : 'deleteMote',
            'description': 'Remove a mote from the manager configuration',
            'request'    : [
                ['macAddr',                 STRING,   25,  None],
            ],
            'response'   : { 
                FIELDS:  [
                ],
            },
            'serializer' : 'serialize_setConfig',
            'serializerParam' : ['config', 'Motes', 'Mote'],
        },
        # deleteConfig.deleteUser
        {
            'id'         : 'deleteConfig',
            'name'       : 'deleteUser',
            'description': 'Remove a user',
            'request'    : [
                ['userName',                STRING,   16,  None],
            ],
            'response'   : { 
                FIELDS:  [
                ],
            },
            'serializer' : 'serialize_setConfig',
            'serializerParam' : ['config', 'Users', 'User'],
        },
        # exchangeJoinKey
        {
            'id'         : 'exchangeJoinKey',
            'name'       : 'exchangeJoinKey',
            'description': 'Exchange the common join key',
            'request'    : [
                ['newKey',                  HEXDATA,  16,  None],
            ],
            'response'   : {
                FIELDS : [ 
                    ['callbackId',          INT,      4,   None],
                ],
            },
        },
        # exchangeMoteJoinKey
        {
            'id'         : 'exchangeMoteJoinKey',
            'name'       : 'exchangeMoteJoinKey',
            'description': 'Exchange a mote\'s join key',
            'request'    : [
                ['macAddr',                 STRING,   25,  None],
                ['newKey',                  HEXDATA,  16,  None],
            ],
            'response'   : {
                FIELDS : [ 
                    ['callbackId',          INT,      4,   None],
                ],
            },
        },
        # exchangeMoteNetworkId
        {
            'id'         : 'exchangeMoteNetworkId',
            'name'       : 'exchangeMoteNetworkId',
            'description': 'Exchange the network ID for a mote',
            'request'    : [
                ['macAddr',                 STRING,   25,  None],
                ['newId',                   INT,      4,   None],
            ],
            'response'   : {
                FIELDS : [ 
                    ['callbackId',          INT,      4,   None],
                ],
            },
        },
        # exchangeNetworkKey
        {
            'id'         : 'exchangeNetworkKey',
            'name'       : 'exchangeNetworkKey',
            'description': 'Exchange the network key',
            'request'    : [
            ],
            'response'   : {
                FIELDS : [ 
                    ['callbackId',          INT,      4,   None],
                ],
            },
        },
        # exchangeNetworkId
        {
            'id'         : 'exchangeNetworkId',
            'name'       : 'exchangeNetworkId',
            'description': 'Exchange the network ID',
            'request'    : [
                ['newId',                   INT,      4,   None],
            ],
            'response'   : {
                FIELDS : [ 
                    ['callbackId',          INT,      4,   None],
                ],
            },
        },
        # exchangeSessionKey
        {
            'id'         : 'exchangeSessionKey',
            'name'       : 'exchangeSessionKey',
            'description': 'Exchange a mote\'s session key',
            'request'    : [
                ['macAddrA',                STRING,   25,  None],
                ['macAddrB',                STRING,   25,  None],
            ],
            'response'   : {
                FIELDS : [ 
                    ['callbackId',          INT,      4,   None],
                ],
            },
        },
        # decommissionDevice
        {
            'id'         : 'decommissionDevice',
            'name'       : 'decommissionDevice',
            'description': 'Decommission a device in the network',
            'request'    : [
                ['macAddr',                 STRING,   25,  None],
            ],
            'response'   : {
                FIELDS : [ 
                          ['result',        STRING,   32,  None],
                ],
            },
        },
        # getConfig.getAcl
        {
            'id'         : 'getConfig',
            'name'       : 'getAcl',
            'description': '''Check whether a device is part of the ACL''',
            'request'    : [
                ['macAddr',             STRING,   25,  None],
            ],
            'response'   : { 
                'Acl':  [
                    ['macAddr',             STRING,   25,  None],
                ],
            },
            'serializer' : 'serialize_getConfig',
            'serializerParam' : ['config', 'Security', 'Acl', 'Device'],
        },
        # getConfig.getAcls
        {
            'id'         : 'getConfig',
            'name'       : 'getAcls',
            'description': '''Get the list of devices on the ACL''',
            'request'    : [
            ],
            'response'   : { 
                'Acl':  [
                    ['macAddr',             STRING,   25,  None],
                ],
            },
            'serializer' : 'serialize_getConfig',
            'serializerParam' : ['config', 'Security', 'Acl'],
            'isResponseArray': True,
        },
        # getConfig.getBlacklist (returns LIST)
        {
            'id'         : 'getConfig',
            'name'       : 'getBlacklist',
            'description': 'Get the channel blacklist. The output is a list of the blacklisted frequency values.',
            'request'    : [
            ],
            'response'   : {
                'ChannelBlackList':  [
                    ['frequency',           INT,    4,   None],
                ],
            },
            'serializer' : 'serialize_getConfig',
            'serializerParam': ['config', 'Network', 'ChannelBlackList'],
            'isResponseArray': True,
            'deserializer': 'deserialize_blacklist',
        },
        # getConfig.getMote
        {
            'id'         : 'getConfig',
            'name'       : 'getMote',
            'description': '',
            'request'    : [
                ['macAddr',                 STRING,   25,  None],
            ],
            'response'   : {
                'Mote':  [
                    ['moteId',              INT,      4,   None],
                    ['macAddr',             STRING,   25,  None],
                    ['name',                STRING,   16,  None], 
                    ['state',               STRING,   16,  'moteState'],
                    ['numJoins',            INT,      4,   None],
                    ['joinTime',            INT,      8,   None], # TODO: date time
                    ['reason',              STRING,   16,  None], 
                    ['isAccessPoint',       BOOL,     1,   None],
                    ['powerSource',         STRING,   16,  None], # TODO: enum
                    ['dischargeCurrent',    INT,      4,   None],
                    ['dischargeTime',       INT,      4,   None],
                    ['recoveryTime',        INT,      4,   None],
                    ['enableRouting',       BOOL,     1,   None],
                    ['productName',         STRING,   16,  None], 
                    ['hwModel',             INT,      1,   None],
                    ['hwRev',               INT,      1,   None],
                    ['swRev',               STRING,   16,  None], 
                    ['voltage',             FLOAT,    8,   None],
                    ['numNeighbors',        INT,      4,   None],
                    ['needNeighbor',        BOOL,     1,   None],
                    ['goodNeighbors',       INT,      4,   None],
                    ['allocatedPkPeriod',   INT,      4,   None],
                    ['allocatedPipePkPeriod', INT,    4,   None],
                    ['pipeStatus',          STRING,   4,   'pipeStatus'],
                    ['advertisingStatus',   STRING,   4,   'advertisingStatus'],
                    ['locationTag',         STRING,   16,  'locationTag'],                   
                ],
            },
            'serializer' : 'serialize_getMote',
        },
        # setConfig.setMote
        {
            'id'         : 'setConfig',
            'name'       : 'setMote',
            'description': 'Set mote configuration',
            'request'    : [
                ['macAddr',                 STRING,   25,  None],
                ['name',                    STRING,   16,  None],
                ['enableRouting',           BOOL,     1,   None],
            ],
            'response'   : { 
                'Mote':  [
                    ['moteId',              INT,      4,   None],
                    ['macAddr',             STRING,   25,  None],
                    ['name',                STRING,   16,  None], 
                    ['state',               STRING,   16,  'moteState'],
                    ['numJoins',            INT,      4,   None],
                    ['joinTime',            INT,      8,   None], # TODO: date time
                    ['reason',              STRING,   16,  None], 
                    ['isAccessPoint',       BOOL,     1,   None],
                    ['powerSource',         STRING,   16,  None], # TODO: enum
                    ['dischargeCurrent',    INT,      4,   None],
                    ['dischargeTime',       INT,      4,   None],
                    ['recoveryTime',        INT,      4,   None],
                    ['enableRouting',       BOOL,     1,   None],
                    ['productName',         STRING,   16,  None], 
                    ['hwModel',             INT,      1,   None],
                    ['hwRev',               INT,      1,   None],
                    ['swRev',               STRING,   16,  None], 
                    ['voltage',             FLOAT,    8,   None],
                    ['numNeighbors',        INT,      4,   None],
                    ['needNeighbor',        BOOL,     1,   None],
                    ['goodNeighbors',       INT,      4,   None],
                    ['allocatedPkPeriod',   INT,      4,   None],
                    ['allocatedPipePkPeriod', INT,    4,   None],
                    ['pipeStatus',          STRING,   4,   'pipeStatus'],
                    ['advertisingStatus',   STRING,   4,   'advertisingStatus'],
                    ['locationTag',         STRING,   16,  'locationTag'],
                ],
            },
            'serializer' : 'serialize_setConfig',
            'serializerParam' : ['config', 'Motes', 'Mote'],
        },
        # getConfig.getMotes (return LIST)
        {
            'id'         : 'getConfig',
            'name'       : 'getMotes',
            'description': '''Get the list of Motes''',
            'request'    : [
            ],
            'response'   : {
                'Mote':  [
                    ['moteId',              INT,      4,   None],
                    ['macAddr',             STRING,   25,  None],
                    ['name',                STRING,   16,  None], 
                    ['state',               STRING,   16,  'moteState'],
                    ['numJoins',            INT,      4,   None],
                    ['joinTime',            INT,      8,   None], # TODO: date time
                    ['reason',              STRING,   16,  None], 
                    ['isAccessPoint',       BOOL,     1,   None],
                    ['powerSource',         STRING,   16,  None], # TODO: enum
                    ['dischargeCurrent',    INT,      4,   None],
                    ['dischargeTime',       INT,      4,   None],
                    ['recoveryTime',        INT,      4,   None],
                    ['enableRouting',       BOOL,     1,   None],
                    ['productName',         STRING,   16,  None], 
                    ['hwModel',             INT,      1,   None],
                    ['hwRev',               INT,      1,   None],
                    ['swRev',               STRING,   16,  None], 
                    ['voltage',             FLOAT,    8,   None],
                    ['numNeighbors',        INT,      4,   None],
                    ['needNeighbor',        BOOL,     1,   None],
                    ['goodNeighbors',       INT,      4,   None],
                    ['allocatedPkPeriod',   INT,      4,   None],
                    ['allocatedPipePkPeriod', INT,    4,   None],
                    ['pipeStatus',          STRING,   4,   'pipeStatus'],
                    ['advertisingStatus',   STRING,   4,   'advertisingStatus'],
                    ['locationTag',         STRING,   16,  'locationTag'],
                ],
            },
            'serializer' : 'serialize_getConfig',
            'serializerParam': ['config', 'Motes'],
            'isResponseArray': True,
        },
        # getConfig.getMoteStatistics
        {
            'id'         : 'getConfig',
            'name'       : 'getMoteStatistics',
            'description': 'Get the Mote Statistics',
            'request'    : [
                ['macAddr',                 STRING,   25,  None],
                ['period',                  STRING,   32,  'statPeriod'],
                ['index',                   INT,      4,   None], # TODO: optional
            ],
            'response'   : { 
                'MoteStatistics':  [
                    ['index',               INT,      4,   None],
                    ['startTime',           INT,      8,   None], # milliseconds
                    ['avgLatency',          INT,      4,   None], # milliseconds
                    ['reliability',         FLOAT,    0,   None], # percentage
                    ['numJoins',            INT,      4,   None],
                    ['voltage',             FLOAT,    4,   None], # volts
                    ['chargeConsumption',   INT,      4,   None], # mC
                    ['temperature',         FLOAT,    4,   None], # deg C
                    # added in Manager 4.1.0.2
                    ['numLostPackets',      INT,      4,   None],
                    # added in Manager 4.1.0.11
                    ['latencyToMote',       INT,      4,   None],
                ],
            },
            'serializer' : 'serialize_getMoteStats',
            'deserializer' : 'deserialize_getStats',
        },
        # getConfig.getNetwork
        {
            'id'         : 'getConfig',
            'name'       : 'getNetwork',
            'description': 'Retrieves network configuration parameters',
            'request'    : [
            ],
            'response'   : { 
                'Network':  [
                    ['netName',             STRING,   16,  None],
                    ['networkId',           INT,      4,   None],
                    ['maxMotes',            INT,      4,   None],
                    ['numMotes',            INT,      4,   None],
                    ['optimizationEnable',  BOOL,     1,   None],
                    ['accessPointPA',       BOOL,     1,   None],
                    ['ccaEnabled',          BOOL,     1,   None],
                    ['requestedBasePkPeriod', INT,    4,   None],
                    ['minServicesPkPeriod', INT,      4,   None],
                    ['minPipePkPeriod',     INT,      4,   None],
                    ['bandwidthProfile',    STRING,   16,  'bandwidthProfile'],
                    ['manualUSFrameSize',   INT,      4,   None],
                    ['manualDSFrameSize',   INT,      4,   None],
                    ['manualAdvFrameSize',  INT,      4,   None],
                    ['netQueueSize',        INT,      4,   None],
                    ['userQueueSize',       INT,      4,   None],
                    ['locationMode',        STRING,   16,  'onOff'],
                    # backbone parameters added in 4.1.0.3
                    ['backboneEnabled',     BOOL,     1,   None],
                    ['backboneSize',        INT,      4,   None],
                ],
            },
            'serializer' : 'serialize_getConfig',
            'serializerParam': ['config', 'Network'],
        },
        # getConfig.getNetworkStatistics
        {
            'id'         : 'getConfig',
            'name'       : 'getNetworkStatistics',
            'description': 'Get the Network Statistics',
            'request'    : [
                ['period',                  STRING,   32,  'statPeriod'],
                ['index',                   INT,      4,   None], # TODO: optional
            ],
            'response'   : { 
                'NetworkStatistics':  [
                    ['index',               INT,      4,   None],
                    ['startTime',           INT,      8,   None], # milliseconds
                    ['netLatency',          INT,      4,   None], # milliseconds
                    ['netReliability',      FLOAT,    0,   None], # percentage
                    ['netPathStability',    FLOAT,    0,   None], # percentage
                    ['lostUpstreamPackets', INT,      4,   None], # lifetime only ?
                ],
            },
            'serializer' : 'serialize_getNetworkStats',
            'deserializer' : 'deserialize_getStats',
        },
        # getConfig.getOpenAlarms
        {
            'id'         : 'getConfig',
            'name'       : 'getOpenAlarms',
            'description': 'Retrieves a list of the open alarms on the Manager',
            'request'    : [
            ],
            'response'   : {
                'Alarm':  [
                    ['timeStamp',               INT,      4,   None],
                    ['eventId',                 INT,      4,   None],
                    ['alarmType',               STRING,   32,  'alarmType'],
                    ['macAddr',                 STRING,   25,  None],
                ],
            },
            'serializer' : 'serialize_getConfig',
            'serializerParam': ['config', 'Alarms'],
            'deserializer' : 'deserialize_getOpenAlarms',
            'isResponseArray': True,
        },
        # getConfig.getPaths (returns LIST)
        {
            'id'         : 'getConfig',
            'name'       : 'getPaths',
            'description': '''Get the list of Paths to the mote\'s neighbors''',
            'request'    : [
                # the request parameter moteMac matches the XML query for Paths
                ['moteMac',                STRING,    25,  None],
            ],
            'response'   : {
                'Path':  [
                    ['pathId',              INT,      4,   None],
                    ['moteAMac',            STRING,   25,  None],
                    ['moteBMac',            STRING,   25,  None],
                    ['numLinks',            INT,      4,   None],
                    ['pathDirection',       STRING,   16,  'pathDirection'],
                    ['pathQuality',         FLOAT,    0,   None],
                ],
            },
            'serializer' : 'serialize_getPath',
            'isResponseArray': True,
        },
        # getConfig.getPathStatistics
        {
            'id'         : 'getConfig',
            'name'       : 'getPathStatistics',
            'description': 'Get Statistics for a specific Path',
            'request'    : [
                ['pathId',                  INT,      4,   None],
                ['period',                  STRING,   16,  'statPeriod'],
                ['index',                   INT,      4,   None],
            ],
            'response'   : {
                'PathStatistics':  [
                    ['index',               INT,      4,   None],
                    ['startTime',           INT,      8,   None], # milliseconds
                    ['baPwr',               INT,      1,   None],
                    ['abPwr',               INT,      1,   None],
                    ['stability',           FLOAT,    8,   None],
                ],
            },
            'serializer' : 'serialize_getPathStats',
            'deserializer' : 'deserialize_getStats',
        },
        # getConfig.getRedundancy
        {
            'id'         : 'getConfig',
            'name'       : 'getRedundancy',
            'description': 'Get the redundancy state',
            'request'    : [
            ],
            'response'   : {
                'Redundancy':  [
                    ['localMode',            STRING,  16,  'redundancyMode'],
                    ['peerStatus',           STRING,  16,  'redundancyPeerStatus'],
                    ['peerControllerSwRev',  STRING,  16,  None],
                ],
            },
            'serializer' : 'serialize_getConfig',
            'serializerParam': ['config', 'Redundancy'],
        },
        # getConfig.getSecurity 
        {
            'id'         : 'getConfig',
            'name'       : 'getSecurity',
            'description': '''Get the Security configuration''',
            'request'    : [
            ],
            'response'   : { 
                'Security':  [
                    ['securityMode',        STRING,   20,  'securityMode'],
                    ['acceptHARTDevicesOnly', BOOL,   1,   None],
                ],
            },
            'serializer' : 'serialize_getConfig',
            'serializerParam' : ['config', 'Security'],
        },
        # getConfig.getSla
        {
            'id'         : 'getConfig',
            'name'       : 'getSla',
            'description': 'Get the Service Level Agreement (SLA) configuration',
            'request'    : [
            ],
            'response'   : {
                'Sla':  [
                    ['minNetReliability',   FLOAT,    8,   None],
                    ['maxNetLatency',       INT,      4,   None],
                    ['minNetPathStability', FLOAT,    8,   None],
                    ['apRdntCoverageThreshold', FLOAT,8,   None],
                ],
            },
            'serializer' : 'serialize_getConfig',
            'serializerParam': ['config', 'Network', 'Sla'],
        },
        # getConfig.getSystem
        {
            'id'         : 'getConfig',
            'name'       : 'getSystem',
            'description': 'Retrieves system-level information',
            'request'    : [
            ],
            'response'   : {
                'System':  [
                    ['systemName',          STRING,   32,  None],
                    ['location',            STRING,   32,  None],
                    ['swRev',               STRING,   32,  None],
                    ['hwModel',             STRING,   32,  None],
                    ['hwRev',               STRING,   32,  None],
                    ['serialNumber',        STRING,   32,  None],
                    ['time',                INT,      8,   None],
                    ['startTime',           INT,      8,   None],
                    ['cliTimeout',          INT,      4,   None],
                    ['controllerSwRev',     STRING,   32,  None],
                ],
            },
            'serializer' : 'serialize_getConfig',
            'serializerParam': ['config', 'System'],
        },
        # getConfig.getUser 
        {
            'id'         : 'getConfig',
            'name'       : 'getUser',
            'description': 'Get the description of a user ',
            'request'    : [
                ['userName',                STRING,   16,  None],
            ],
            'response'   : {
                'User':  [
                    ['userName',            STRING,   16,  None],
                    ['privilege',           STRING,   16,  'userPrivilege'],
                ],
            },
            'serializer' : 'serialize_getUser',
        },
        # getConfig.getUsers (returns LIST)
        {
            'id'         : 'getConfig',
            'name'       : 'getUsers',
            'description': 'Get the list of users',
            'request'    : [
            ],
            'response'   : {
                'User':  [
                    ['userName',            STRING,   16,  None],
                    ['privilege',           STRING,   16,  'userPrivilege'],
                ],
            },
            'serializer' : 'serialize_getConfig',
            'serializerParam': ['config', 'Users'],
            'isResponseArray': True,
        },
        # getConfig.getSourceRoute
        {
            'id'         : 'getConfig',
            'name'       : 'getSourceRoute',
            'description': 'Get the Source Route for a specific Mote',
            'request'    : [
                ['destMacAddr',             STRING,   25,  None],
            ],
            'response'   : {
                'SourceRoute':  [
                    ['destMacAddr',         STRING,   25,  None],
                    ['primaryPath',         LIST,     16,  None], 
                    ['secondaryPath',       LIST,     16,  None], 
                ],
            },
            'serializer' : 'serialize_getConfig',
            'serializerParam': ['config', 'SourceRoutes', 'SourceRoute'],
            'deserializer' : 'deserialize_getSourceRoute',
        },
        # getLatency
        {
            'id'         : 'getLatency',
            'name'       : 'getLatency',
            'description': 'Get estimated latency for a mote.',
            'request'    : [
                ['macAddr',                 STRING,   25,  None],
            ],
            'response'   : {
                FIELDS : [ 
                    ['downstream',          INT,      4,   None],
                    ['upstream',            INT,      4,   None],
                ],
            },
        },
        # getLicense
        {
            'id'         : 'getLicense',
            'name'       : 'getLicense',
            'description': '''Get the software license key.''',
            'request'    : [
            ],
            'response'   : {
                FIELDS : [ 
                    ['license',             STRING,   40,  None],
                ],
            },
        },
        # getTime
        {
            'id'         : 'getTime',
            'name'       : 'getTime',
            'description': 'Get the current time.',
            'request'    : [
            ],
            'response'   : {
                FIELDS : [ 
                    ['utc_time',            FLOAT,    0,   None], # TODO: return as a date-time format
                    ['asn_time',            INT,      8,   None],
                ],
            },
        },
        # pingMote
        {
            'id'         : 'pingMote',
            'name'       : 'pingMote',
            'description': '''Ping the specified mote. A Net Ping Reply event notification will contain the mote's response.''',
            'request'    : [
                ['macAddr',                 STRING,   25,  None],
            ],
            'response'   : {
                FIELDS : [ 
                    ['callbackId',          INT,      4,   None],
                ],
            },
        },
        # promoteToOperational
        {
            'id'         : 'promoteToOperational',
            'name'       : 'promoteToOperational',
            'description': 'Promote a quarantined device to operational',
            'request'    : [
                ['macAddr',                 STRING,   25,  None],
            ],
            'response'   : {
                FIELDS : [ 
                          ['result',        STRING,   32,  None],
                ],
            },
        },
        # reset
        {
            'id'         : 'reset',
            'name'       : 'reset',
            'description': 'Reset the system or network',
            'request'    : [
                ['object',                  STRING,   25,  'resetObject'],
            ],
            'response'   : {
                FIELDS : [ 
                    ['result',              STRING,   32,  None],
                ],
            },
        },
        # resetWithId
        {
            'id'         : 'reset',
            'name'       : 'resetWithId',
            'description': 'Reset mote by ID',
            'request'    : [
                ['object',                  STRING,   25,  'resetMote'],
                ['moteId',                  INT,      4,   None],
            ],
            'response'   : {
                FIELDS : [ 
                    ['result',              STRING,   32,  None],
                ],
            },
        },
        # resetWithMac
        {
            'id'         : 'reset',
            'name'       : 'resetWithMac',
            'description': 'Reset mote by MAC address',
            'request'    : [
                ['object',                  STRING,   25,  'resetMote'],
                ['macAddr',                 STRING,   25,  None],
            ],
            'response'   : {
                FIELDS : [ 
                    ['result',              STRING,   32,  None],
                ],
            },
        },
        # sendRequest
        {
            'id'         : 'sendRequest',
            'name'       : 'sendRequest',
            'description': 'Send downstream (request) data',
            'request'    : [
                ['macAddr',                 STRING,   25,  None],
                ['domain',                  STRING,   16,  'appDomain'],
                ['priority',                STRING,   16,  'packetPriority'],
                ['reliable',                BOOL,     0,   None],
                ['data',                    HEXDATA,  None,None],
            ],
            'response'   : { 
                FIELDS : [
                    ['callbackId',          INT,      4,   None],
                ],
            },
        },
        # sendResponse
        {
            'id'         : 'sendResponse',
            'name'       : 'sendResponse',
            'description': 'Send downstream data as a response. sendResponse should only be used in special cases.',
            'request'    : [
                ['macAddr',                 STRING,   25,  None],
                ['domain',                  STRING,   16,  'appDomain'],
                ['priority',                STRING,   16,  'packetPriority'],
                ['reliable',                BOOL,     0,   None],
                ['callbackId',              INT,      4,   None],
                ['data',                    HEXDATA, None, None],
            ],
            'response'   : { 
                FIELDS : [
                    ['callbackId',          INT,      4,   None],
                ],
            },
        },
        # setConfig.setAcl
        {
            'id'         : 'setConfig',
            'name'       : 'setAcl',
            'description': 'Add or update a device in the ACL',
            'request'    : [
                ['macAddr',                 STRING,   25,  None],
                ['joinKey',                 HEXDATA,  16,  None],
            ],
            'response'   : { 
                'Device':  [
                    ['macAddr',             STRING,   25,  None],
                ],
            },
            'serializer' : 'serialize_setConfig',
            'serializerParam' : ['config', 'Security', 'Acl', 'Device'],
        },
        # setConfig.setBlacklist
        {
            'id'         : 'setConfig',
            'name'       : 'setBlacklist',
            'description': 'Update the channel blacklist. The input is a list of blacklisted frequency values separated by spaces.',
            'request'    : [
                ['frequency',               STRING,   64,   None],
            ],
            'response'   : { 
                'ChannelBlackList':  [
                    ['frequency',           INT,      4,   None],
                ],
            },
            'serializer' : 'serialize_setBlacklist',
            'serializerParam' : ['config', 'Network', 'ChannelBlackList'],
            'isResponseArray': True,
            'deserializer': 'deserialize_blacklist',
        },
        # setConfig.setNetwork
        {
            'id'         : 'setConfig',
            'name'       : 'setNetwork',
            'description': 'Set network configuration',
            'request'    : [
                ['netName',                 STRING,   16,  None],
                ['networkId',               INT,      4,   None],
                ['maxMotes',                INT,      4,   None],
                ['optimizationEnable',      BOOL,     1,   None],
                ['accessPointPA',           BOOL,     1,   None],
                ['ccaEnabled',              BOOL,     1,   None],
                ['requestedBasePkPeriod',   INT,      4,   None],
                ['minServicesPkPeriod',     INT,      4,   None],
                ['minPipePkPeriod',         INT,      4,   None],
                ['bandwidthProfile',        STRING,   16,  'bandwidthProfile'],
                ['manualUSFrameSize',       INT,      4,   None],
                ['manualDSFrameSize',       INT,      4,   None],
                ['manualAdvFrameSize',      INT,      4,   None],
                ['locationMode',            STRING,   8,   'onOff'],
                # backbone parameters added in 4.1.0.3
                # TODO: UG! adding these parameters prevents backward compatibility
                #['backboneEnabled',     BOOL,     1,   None],
                #['backboneSize',        INT,      4,   None],
            ],
            'response'   : { 
                'Network':  [
                    # TODO: return all elements?
                    ['netName',             STRING,   16,  None],
                    ['networkId',           INT,      4,   None],
                    ['maxMotes',            INT,      4,   None],
                    ['optimizationEnable',  BOOL,     1,   None],
                    ['accessPointPA',       BOOL,     1,   None],
                    ['ccaEnabled',          BOOL,     1,   None],
                    ['requestedBasePkPeriod', INT,    4,   None],
                    ['minServicesPkPeriod', INT,      4,   None],
                    ['minPipePkPeriod',     INT,      4,   None],
                    ['bandwidthProfile',    STRING,   16,  'bandwidthProfile'],
                    ['manualUSFrameSize',   INT,      4,   None],
                    ['manualDSFrameSize',   INT,      4,   None],
                    ['manualAdvFrameSize',  INT,      4,   None],
                    ['locationMode',        STRING,   8,   'onOff'],
                    # backbone parameters added in 4.1.0.3
                    ['backboneEnabled',     BOOL,     1,   None],
                    ['backboneSize',        INT,      4,   None],
                ],
            },
            'serializer' : 'serialize_setConfig',
            'serializerParam' : ['config', 'Network'],
        },
        # setConfig.setSecurity
        {
            'id'         : 'setConfig',
            'name'       : 'setSecurity',
            'description': 'Set security configuration',
            'request'    : [
                ['securityMode',            STRING,   20,  'securityMode'],
                ['commonJoinKey',           HEXDATA,  16,  None],
                ['acceptHARTDevicesOnly',   BOOL,     1,   None],
            ],
            'response'   : { 
                'Security':  [
                    ['securityMode',        STRING,   20,  'securityMode'],
                    ['acceptHARTDevicesOnly', BOOL,   1,   None],
                ],
            },
            'serializer' : 'serialize_setConfig',
            'serializerParam' : ['config', 'Security'],
        },
        # setConfig.setSla
        {
            'id'         : 'setConfig',
            'name'       : 'setSla',
            'description': 'Set SLA configuration',
            'request'    : [
                ['minNetReliability',       FLOAT,    8,   None],
                ['maxNetLatency',           INT,      4,   None],
                ['minNetPathStability',     FLOAT,    8,   None],
                ['apRdntCoverageThreshold', FLOAT,    8,   None],
            ],
            'response'   : { 
                'Sla':  [
                    ['minNetReliability',   FLOAT,    8,   None],
                    ['maxNetLatency',       INT,      4,   None],
                    ['minNetPathStability', FLOAT,    8,   None],
                    ['apRdntCoverageThreshold', FLOAT, 8,  None],
                ],
            },
            'serializer' : 'serialize_setConfig',
            'serializerParam' : ['config', 'Network', 'Sla'],
        },
        # setConfig.setSystem
        {
            'id'         : 'setConfig',
            'name'       : 'setSystem',
            'description': 'Set system-level configuration',
            'request'    : [
                ['systemName',              STRING,   16,  None],
                ['location',                STRING,   16,  None],
                ['cliTimeout',              INT,      4,   None],
            ],
            'response'   : { 
                'System':  [
                    # TODO: return all elements?
                    ['systemName',          STRING,   50,  None],
                    ['location',            STRING,   50,  None],
                    ['cliTimeout',          INT,      4,   None],
                ],
            },
            'serializer' : 'serialize_setConfig',
            'serializerParam' : ['config', 'System'],
        },
        # setConfig.setUser
        {
            'id'         : 'setConfig',
            'name'       : 'setUser',
            'description': 'Add or update user configuration',
            'request'    : [
                ['userName',                STRING,   16,  None],
                ['password',                STRING,   16,  None],
                ['privilege',               STRING,   16,  'userPrivilege'],
            ],
            'response'   : { 
                'User':  [
                    ['userName',            STRING,   16,  None],
                    ['privilege',           STRING,   16,  'userPrivilege'],
                ],
            },
            'serializer' : 'serialize_setConfig',
            'serializerParam' : ['config', 'Users', 'User'],
        },
        # setLicense
        {
            'id'         : 'setLicense',
            'name'       : 'setLicense',
            'description': 'Set the software license key.',
            'request'    : [
                ['license',                 STRING,   40,  None],
            ],
            'response'   : {
                FIELDS : [ 
                    ['result',              STRING,   32,  None],
                ],
            },
        },
        # startOtap
        {
            'id'         : 'startOtap',
            'name'       : 'startOtap',
            'description': 'This command initiates the OTAP (Over-The-Air-Programming) process to upgrade software on motes and the Access Point. By default, the process will retry the OTAP file transmission 100 times.',
            'request'    : [
            ],
            'response'   : { 
                FIELDS : [ 
                          ['result',        STRING,   32,  None],
                ],
            },
        },
        # startOtapWithRetries 
        {
            'id'         : 'startOtap',
            'name'       : 'startOtapWithRetries',
            'description': 'This command initiates the OTAP (Over-The-Air-Programming) process to upgrade software for motes and the Access Point, using the specified number of retries.',
            'request'    : [
                ['retries',                 INT,      1,   None]
            ],
            'response'   : { 
                FIELDS : [ 
                          ['result',        STRING,   32,  None],
                ],
            },
        },
        # subscribe
        {
            'id'         : 'subscribe',
            'name'       : 'subscribe',
            'description': '''Subscribe to notifications. This function adds or updates the subscribed notifications to match 'filter'. The filter is a space-separated list of notification types. Valid types include 'data' and 'events'.''',
            'request'    : [
                ['filter',                  STRING,   128, None],
            ],
            'response'   : {
                FIELDS : [ 
                    ['notif_token',         STRING,   32,  None],
                    # note: this is intentionally different from the subscribe API command
                    # (not returning the notification port) because the SmartMesh SDK method
                    # also handles connecting to the notification channel.
                ],
            },
            'command_override': 'subscribe_override',
        },
        # unsubscribe
        {
            'id'         : 'unsubscribe',
            'name'       : 'unsubscribe',
            'description': 'Unsubscribe from notifications. This function clears the existing notification subscription of the client and stops the notification thread. ',
            'request'    : [
                # note: this is intentionally different from the unsubscribe API
            ],
            'response'   : {
                FIELDS : [ 
                    ['result',              STRING,   32,  None],
                ],
            },
            'command_override': 'unsubscribe_override',
        },
    ]
