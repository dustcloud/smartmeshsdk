#!/usr/bin/python

from . import ApiDefinition
from . import ByteArraySerializer

class HartMoteDefinition(ApiDefinition.ApiDefinition):
    '''
    \ingroup ApiDefinition
    
    \brief  API definition for the IP mote.
   
    \note   This class inherits from ApiDefinition. It redefines the attributes of
            its parents class, but inherits the methods.
    '''
    
    STRING    = ApiDefinition.FieldFormats.STRING
    BOOL      = ApiDefinition.FieldFormats.BOOL
    INT       = ApiDefinition.FieldFormats.INT
    INTS      = ApiDefinition.FieldFormats.INTS
    HEXDATA   = ApiDefinition.FieldFormats.HEXDATA
    ARRAY     = ApiDefinition.FieldFormats.ARRAY
    RC        = ApiDefinition.ApiDefinition.RC
    SUBID1    = ApiDefinition.ApiDefinition.SUBID1
    SUBID2    = ApiDefinition.ApiDefinition.SUBID2
    RC_OK     = ApiDefinition.ApiDefinition.RC_OK
    
    FLAG_SETNV_RAM      = 7
    FLAG_TRAN_ACKED     = 6
    FLAG_TRAN_DIR_RESP  = 7
    
    def __init__(self, array2scalar = True):
        ApiDefinition.ApiDefinition.__init__(self, array2scalar)
        self.serializer = ByteArraySerializer.ByteArraySerializer(self)
    
    def default_serializer(self,commandArray,fieldsToFill):
        '''
        \brief IpMgrDefinition-specific implementation of default serializer
        '''
        return self.serializer.serialize(commandArray,fieldsToFill)
        
    def deserialize(self,type,cmdId,byteArray):
        '''
        \brief IpMgrDefinition-specific implementation of deserializer
        '''
        return self.serializer.deserialize(type,cmdId,byteArray)
    
    def serializeSend(self,commandArray,fieldsToFill):
        '''
        \brief Serializer specific for the send command
        
        This serializer:
        - toggles the 'tranType' and 'tranDir' flags
        '''
        
        # serialize the command using the default serializer
        cmdId,byteArray = self.serializer.serialize(commandArray,fieldsToFill)
        
        # byteArray now contains the following bytes:
        # [0]  is the paramId
        # [1]  is the tranType value
        # [2]  is the tranDir value
        # [3:] are the parameters
        
        # remove the tranType and tranDir from the packet
        tranType = byteArray.pop(0)
        tranDir  = byteArray.pop(0) # still index 0 since popped before
        
        # prepend the flagList, the list of flags to be set in the header
        flaglist = []
        if tranType:
            flaglist.append(self.FLAG_TRAN_ACKED)
        if tranDir:
            flaglist.append(self.FLAG_TRAN_DIR_RESP)
        
        # add the flagList as the first element of the byteArray
        byteArray = [flaglist]+byteArray
        
        return cmdId,byteArray
    
    def serializeSetNv(self,commandArray,fieldsToFill):
        '''
        \brief Serializer specific for the setNVParameter commands
        
        This serializer:
        - toggles the 'memory' flag
        - adds the 4B 'reserved' field to the serialized bytes
        '''
        
        # serialize the command using the default serializer
        cmdId,byteArray = self.serializer.serialize(commandArray,fieldsToFill)
        
        # byteArray now contains the following bytes:
        # [0]  is the paramId
        # [1:] are the parameters
        
        # prepend the flagList, the list of flags to be set in the header
        flaglist = []
        
        # add the 4B reserved field
        byteArray = [0,0,0,0]+byteArray
        
        # add the flagList as the first element of the byteArray
        byteArray = [flaglist]+byteArray
        
        return cmdId,byteArray
    
    def serializeGetNv(self,commandArray,fieldsToFill):
        '''
        \brief Serializer specific for the getNVParameter commands
        
        This serializer adds the 4B 'reserved' field to the serialized bytes
        '''
        
        # serialize the command using the default serializer
        cmdId,byteArray = self.serializer.serialize(commandArray,fieldsToFill)
        
        # add the 4B reserved field
        byteArray = [0,0,0,0]+byteArray
        
        return cmdId,byteArray
    
    # We redefine this attribute inherited from ApiDefinition. See
    # ApiDefinition for a full description of the structure of this field.
    fieldOptions = {
        RC: [
            [0,    'RC_OK',                      'Operation was successfullycompleted.'],
            [3,    'RC_BUSY',                    'Resource unavailable'],
            [4,    'RC_INVALID_LEN',             'Invalid length'],
            [5,    'RC_INVALID_STATE',           'Invalid state'],
            [6,    'RC_UNSUPPORTED',             'Command or operation not supported'],
            [7,    'RC_UNKNOWN_PARAM',           'Unknown parameter'],
            [8,    'RC_UNKNOWN_CMD',             'Unknown command'],
            [9,    'RC_WRITE_FAIL',              'Write did not complete'],
            [10,   'RC_READ_FAIL',               'Read did not complete'],
            [11,   'RC_LOW_VOLTAGE',             'Voltage check failed'],
            [12,   'RC_NO_RESOURCES',            'No resources are available to complete command'],
            [13,   'RC_INCOMPLETE_JOIN_INFO',    'Incomplete join info'],
            [14,   'RC_NOT_FOUND',               'Resource not found'],
            [15,   'RC_INVALID_VALUE',           'Invalid value'],
            [16,   'RC_ACCESS_DENIED',           'Access to this command/variable denied'],
            [18,   'RC_OPEN_FAIL',               'Open operation failed'],
            [19,   'RC_ERASE_FAIL',              'Erase operation failed'],
            [21,   'RC_ERROR',                   'Generic error'], 			
        ],
        'ApplicationDomain' : [
            [0x00, 'Publish',               ''],
            [0x01, 'Event',                 ''],
            [0x02, 'Maintenance',           ''],
            [0x03, 'Block transfer',        ''],
        ],
        'PowerStatus' : [
            [0x00, 'Nominal',               ''],
            [0x01, 'Low',                   ''],
            [0x02, 'Critically low',        ''],
            [0x03, 'Recharging low',        ''],
            [0x04, 'Recharging high',       ''],
        ],
        'WriteProtectMode' : [
            [0x00, 'Write allowed',         ''],
            [0x01, 'Write not allowed',     ''],
        ],
        'moteState' : [
            [0x00, 'Init',                  'The mote is in the process of booting'],
            [0x01, 'Idle',                  'The mote is accepting configuration commands. Upon receiving a join command, the mote moves into the Searching state. The Idle state is equivalent to the HART "Low Power" state.'],
            [0x02, 'Searching',             'The mote\'s receiver is on with a configurable duty cycle while the mote is actively searching for a network. The Searching state is equivalent to the HART "Active Search" state or "Passive Search," depending on the duty cycle setting.'],
            [0x03, 'Negotiating',           'The mote has detected a network and has sent a join request to the manager'],
            [0x04, 'Connected',             'The mote has joined the network and established communication with the network manager. The Connected state is equivalent to the HART "Quarantine" state.'],
            [0x05, 'Operational',           'The mote has links to both the network manager and gateway, and is ready to send data'],
            [0x06, 'Disconnected',          'The mote has disconnected from the network'],
            [0x07, 'Radio test',            'The mote is in radio test mode'],
            [0x08, 'Promiscuous Listen',    'The mote received a search command and is in promiscuous listen mode'],
            [0x09, 'Suspended',             'The mote entered suspended state after having processed command 972'],
        ],
        'ServiceState' : [
            [0x00, 'Inactive',              ''],
            [0x01, 'Active',                ''],
            [0x02, 'Requested',             ''],
        ],
        'PowerSource' : [
            [0x00, 'Line',                  ''],
            [0x01, 'Battery',               ''],
            [0x02, 'Rechargeable/Scavenging',    ''],
        ],
        'OTAPLockout' : [
            [0x00, 'OTAP allowed (default)',     ''],
            [0x01, 'OTAP disabled',              ''],
        ],
        'Priority' : [
            [0x00, 'Low',                   ''],
            [0x01, 'Medium',                ''],
            [0x02, 'High',                  ''],
        ],
        'TestType' : [
            [0x00, 'packet', 'Packet transmission'],
            [0x01, 'cm',     'Continuous modulation'],
            [0x02, 'cw',     'Continuous wave'],
            [0x03, 'pkcca',  'Packet test with clear channel assessment'],
        ],
        'hrCounterMode' : [
            [0,    'Rollover',              ''],
            [1,    'Saturating',            ''],
        ],
        'HartComplianceMode' : [
            [0,    'Some timers and counters deviate from HART specification', ''],
            [1,    'Strict HART compliance',                                   ''],
        ],
        'FileOpenOptions' : [
            [0x01, 'Create the file if it does not exist', ''],
        ],
        'FileOpenMode' : [
            [0x01, 'Others have read permission',                                        ''],
            [0x02, 'Others have write permission',                                       ''],
            [0x03, 'Others have read/write permission',                                  ''],
            [0x04, 'This is a temporary file (it is deleted upon reset or power cycle)', ''],
            [0x08, 'This file is created in shadow mode (for wear leveling)',            ''],
        ],
        'seqSize': [
            [0,    '0',                     ''],
            [1,    '1',                     ''],
            [2,    '2',                     ''],
            [3,    '3',                     ''],
            [4,    '4',                     ''],
            [5,    '5',                     ''],
            [6,    '6',                     ''],
            [7,    '7',                     ''],
            [8,    '8',                     ''],
            [9,    '9',                     ''],
            [10,   '10',                    ''],
        ],
        
        #----------------------------------------------------------------------
        
        'tranType' : [
            [False,'bestEffort',            ''],
            [True, 'Acked',                 ''],
        ],
        'tranDir' : [
            [False,'request',               ''],
            [True, 'response',              ''],
        ],
    }
    
    subCommandsSet = [
        {
            'id'         : 0x04,
            'name'       : 'txPower',
            'description': 'The setParameter<txPower> command sets the mote conducted RF output power. Refer to product datasheets for supported RF output power values. For example, if the mote has a typical RF output power of +8 dBm when the Power Amplifier (PA) is enabled, set the txPower parameter to 8 to enable the PA. Similarly, if the mote has a typical RF output power of -2 dBm when the PA is disabled, then set the txPower parameter to -2 to turn off the PA. Note that this value is the RF output power coming out of the mote and not the radiated power coming out of the antenna. This command may be issued at any time and takes effect upon the next transmission.',
            'request'    : [
                ['txPower',                 INTS,     1,   None],
            ],
            'response'   : {
                'FIELDS':  [
                ],
            },
            'responseCodes': {
               'RC_OK'                      : 'Operation was successfully completed',
               'RC_INVALID_LEN'             : 'Invalid packet length',
               'RC_UNKNOWN_PARAM'           : 'Unknown parameter value',
               'RC_INVALID_VALUE'           : 'Invalid value',
            },
        },
        {
            'id'         : 0x06,
            'name'       : 'joinDutyCycle',
            'description': 'The setParameter<joinDutyCycle> command allows the microprocessor to control the join duty cycle the ratio of active listen time to doze time (a low-power radio state) during the period when the mote is searching for the network. The default duty cycle enables the mote to join the network at a reasonable rate without using excessive battery power. If you desire a faster join time at the cost of higher power consumption, use the setParameter<joinDutyCycle> command to increase the join duty cycle up to 100%. Note that the setParameter<joinDutyCycle> command is not persistent and stays in effect only until reset. For power consumption information, refer to the mote product datasheet.\n\nThis command may be issued multiple times during the joining process. This command is only effective when the mote is in the Idle and Searching states.',
            'request'    : [
                ['dutyCycle',               INT,      1,   None],
            ],
            'response'   : {
                'FIELDS':  [
                ],
            },
            'responseCodes': {
               'RC_OK'                      : 'Operation was successfully completed',
               'RC_INVALID_LEN'             : 'Invalid packet length',
               'RC_UNKNOWN_PARAM'           : 'Unknown parameter value',
            },
        },
        {
            'id'         : 0x07,
            'name'       : 'batteryLife',
            'description': 'The setParameter<batteryLife> command allows the microprocessor to update the remaining battery life information that the mote reports to WirelessHART Gateway in Command 778. This parameter must be set during the Idle state prior to joining, and should be updated periodically throughout operation. This parameter is only used in WirelessHART-compliant devices.\n\nCommand 778 is deprecated in version 7.4 of the HART specification as most existing gateways do not use battery life information.',
            'request'    : [
                ['batteryLife',             INT,      2,   None],
                ['powerStatus',             INT,      1,   'PowerStatus'],
            ],
            'response'   : {
                'FIELDS':  [
                ],
            },
            'responseCodes': {
               'RC_OK'                      : 'Operation was successfully completed',
               'RC_INVALID_LEN'             : 'Invalid packet length',
               'RC_UNKNOWN_PARAM'           : 'Unknown parameter value',
            },
        },
        {
            'id'         : 0x08,
            'name'       : 'service',
            'description': 'The setParameter<service> command is used to request new device-originated bandwidth services and modify existing device-initiated services (now called "Timetables" in WirelessHART 7.4). Calling this command updates the motes internal service table, which later initiates a request to the network manager for bandwidth allocation. A subsequent serviceIndication notification will be sent indicating the response from the network manager. The getParameter<service> command may be used to read the service table, including the state of the service request.\n\nThe setParameter<service> command may be sent at any time. If the network manager rejects a service request, the microprocessor can try again by re-issuing the setParameter<service> command.\n\nTo delete a service, set the time field of the desired service to zero. Service request flags, application domain, and destination address are ignored by the mote when time equals zero.\n\nNormally all service requests are compared against the power limits set with the setNVParameter<powerInfo> command. Services that would cause the device to exceed its power budget are denied. In Manager 4.1.1, a service request of 1 ms will result in the manager respecting the power limit for publish services, but will allow a block-transfer service requests (see the SmartMesh WirelessHART User\'s Guide section on Services) that would result in a fast pipe being activated.',
            'request'    : [
                ['serviceId',               INT,      1,   None],
                ['serviceReqFlags',         INT,      1,   None],
                ['appDomain',               INT,      1,   'ApplicationDomain'],
                ['destAddr',                HEXDATA,  2,   None],
                ['time',                    INT,      4,   None],
            ],
            'response'   : {
                'FIELDS':  [
                    ['numServices',         INT,      1,   None],
                ],
            },
            'responseCodes': {
               'RC_OK'                      : 'Operation was successfully completed',
               'RC_INVALID_LEN'             : 'Invalid packet length',
               'RC_UNKNOWN_PARAM'           : 'Unknown parameter value',
            },
        },
        {
            'id'         : 0x09,
            'name'       : 'hartDeviceStatus',
            'description': 'The setParameter<hartDeviceStatus> command sets the current status of a WirelessHART device. The value passed in this parameter is used in all subsequent WirelessHART communications between the mote and the manager. This command is only required for WirelessHART-compliant devices. Refer to the HART Command Specifications for the appropriate value to use.',
            'request'    : [
                ['hartDevStatus',           INT,      1,   None],
                ['hartExtDevStatus',        INT,      1,   None],
            ],
            'response'   : {
                'FIELDS':  [
                ],
            },
            'responseCodes': {
               'RC_OK'                      : 'Operation was successfully completed',
               'RC_INVALID_LEN'             : 'Invalid packet length',
               'RC_UNKNOWN_PARAM'           : 'Unknown parameter value',
            },
        },
        {
            'id'         : 0x0A,
            'name'       : 'hartDeviceInfo',
            'description': 'The setParameter<hartDeviceInfo> command is used to set HART device information that the mote passes to gateway during join. This command must be issued prior to join. This command is only required for WirelessHART-compliant devices. Note that the contents of this command are not validated by mote.',
            'request'    : [
                ['hartCmd0',                HEXDATA,  22,  None],
                ['hartCmd20',               HEXDATA,  32,  None],
            ],
            'response'   : {
                'FIELDS':  [
                  
                ],
            },
            'responseCodes': {
               'RC_OK'                      : 'Operation was successfully completed',
               'RC_INVALID_LEN'             : 'Invalid packet length',
               'RC_UNKNOWN_PARAM'           : 'Unknown parameter value',
            },
        },
        {
            'id'         : 0x0B,
            'name'       : 'eventMask',
            'description': 'The setParameter<eventMask> command allows the microprocessor to subscribe to the types of events that may be sent in the motes events notification message. This command may be called at any time and takes effect at the next event notification. The mote includes an event in the notification message if the corresponding bit in <eventMask> is set to 1, and excludes the event if the bit is set to 0. At mote reset, the default value of <eventMask> is 1 for all events.\n\nNew event type may be added in future revisions of mote software. It is recommended that the client code only subscribe to known events and gracefully ignore all unknown events.',
            'request'    : [
                ['eventMask',               INT,      4,   None],
            ],
            'response'   : {
                'FIELDS':  [
                  
                ],
            },
            'responseCodes': {
               'RC_OK'                      : 'Operation was successfully completed',
               'RC_UNKNOWN_PARAM'           : 'Unknown parameter value',
               'RC_INVALID_LEN'             : 'Invalid packet length',
            },
        },
        {
            'id'         : 0x12,
            'name'       : 'writeProtect',
            'description': "The setParameter<writeProtect> command allows the microprocessor to enable or disable access to selected WirelessHART commands via wireless or the hartPayload command. Refer to the SmartMesh WirelessHART User's Guide for the list of affected commands. If writeProtect is enabled and the mote receives any of these commands (either via wireless connection or via the hartPayload command), the command will have no effect, and the mote will return RC_7 (In Write Protect Mode). At mote boot, writeProtect is set to 0 (writes allowed). The current status of writeProtect may be read via the getParameter<moteStatus> command. This command is for WirelessHART-compliant devices only.",
            'request'    : [
                ['writeProtect',            INT,      1,   'WriteProtectMode'],
            ],
            'response'   : {
                'FIELDS':  [
                  
                ],
            },
            'responseCodes': {
               'RC_OK'                      : 'Operation was successfully completed',
               'RC_UNKNOWN_PARAM'           : 'Unknown parameter value',
               'RC_INVALID_LEN'             : 'Invalid packet length',
            },
        },
        {
            'id'         : 0x1a,
            'name'       : 'lock',
            'description': 'The setParameter<lock> command locks/unlocks select HART commands (ones that affect the configuration changed flag) to a specific master (GW or serial maintenance port) to prevent the other master from changing it. This command is intended for use when the lock is temporary, i.e. it does not persist through power cycle or reset. For nonvolatile locking, use the setNVParameter<lock> command. Note: This parameter is available in devices running mote software >= 1.1.0',
            'request'    : [
                ['code',                    INT,      1,   None],
                ['master',                  INT,      2,   None],
            ],
            'response'   : {
                'FIELDS':  [
                  
                ],
            },
            'responseCodes': {
               'RC_OK'                      : 'Operation was successfully completed',
               'RC_INVALID_LEN'             : 'Invalid packet length',
               'RC_UNKNOWN_PARAM'           : 'Unknown parameter value',
               'RC_INVALID_VALUE'           : 'Invalid value',
            },
        },
    ]
    
    subCommandsGet = [
        {
            'id'         : 0x06,
            'name'       : 'joinDutyCycle',
            'description': 'The getParameter<joinDutyCycle> command return mote\'s join duty cycle, which determines the percentage of time the mote spends in radio receive mode while searching for network. The value of join duty cycle is expressed in increments of 1/255th of 100%, where 0 corresponds to 0% and 255 corresponds to 100%.',
            'request'    : [
            ],
            'response'   : {
                'FIELDS':  [
                    ['joinDutyCycle',       INT,      1,   None],
                ],
            },
            'responseCodes': {
               'RC_OK'                      : 'Operation was successfully completed',
            },
        },
        {
            'id'         : 0x08,
            'name'       : 'service',
            'description': 'The getParameter<service> command retrieves information about the service allocation that is currently available to the field device. Services (now called "Timetables" in WirelessHART 7.4) in the range 0x00-7F are those requested by the device, and those in the range 0x80-FF are assigned independently by the network manager.',
            'request'    : [
                ['serviceId',               INT,      1,   None],
            ],
            'response'   : {
                'FIELDS':  [
                    ['serviceId',           INT,      1,   None],
                    ['serviceState',        INT,      1,   'ServiceState'],
                    ['serviceFlags',        INT,      1,   None],
                    ['appDomain',           INT,      1,   'ApplicationDomain'],
                    ['destAddr',            HEXDATA,  2,   None],
                    ['time',                INT,      4,   None],
                ],
            },
            'responseCodes': {
               'RC_OK'                      : 'Operation was successfully completed',
               'RC_INVALID_LEN'             : 'Invalid packet length',
               'RC_UNKNOWN_PARAM'           : 'Unknown parameter value',
               'RC_NOT_FOUND'               : 'Service not found',
            },
        },
        {
            'id'         : 0x0C,
            'name'       : 'moteInfo',
            'description': 'The getParameter<moteInfo> command returns static information about the motes hardware and software. Note that network state-related information about the mote may be retrieved using getParameter<networkInfo>.',
            'request'    : [
            ],
            'response'   : {
                'FIELDS':  [
                    ['apiVersion',          INT,      1,   None],
                    ['serialNum',           HEXDATA,  8,   None],
                    ['hwModel',             INT,      1,   None],
                    ['hwRev',               INT,      1,   None],
                    ['swMajorRev',          INT,      1,   None],
                    ['swMinorRev',          INT,      1,   None],
                    ['swPatch',             INT,      1,   None],
                    ['swBuild',             INT,      2,   None],
                ],
            },
            'responseCodes': {
               'RC_OK'                      : 'Operation was successfully completed',
               'RC_INVALID_LEN'             : 'Invalid packet length',
               'RC_UNKNOWN_PARAM'           : 'Unknown parameter value',
            },
        },
        {
            'id'         : 0x0D,
            'name'       : 'networkInfo',
            'description': 'The getParameter<networkInfo> command may be used to retrieve the mote\'s network-related parameters. Note that static information about the motes hardware and software may be retrieved using getParameter<moteInfo>.',
            'request'    : [
            ],
            'response'   : {
                'FIELDS':  [
                    ['macAddress',          HEXDATA,  8,   None],
                    ['moteId',              INT,      2,   None],
                    ['networkId',           INT,      2,   None],
                ],
            },
            'responseCodes': {
               'RC_OK'                      : 'Operation was successfully completed',
               'RC_INVALID_LEN'             : 'Invalid packet length',
               'RC_UNKNOWN_PARAM'           : 'Unknown parameter value',
            },
        },
        {
            'id'         : 0x0E,
            'name'       : 'moteStatus',
            'description': 'The getParameter<moteStatus> command is used to retrieve the mote\'s state and frequently changing information. Note that static information about the state of the mote hardware and software may be retrieved using getParameter<moteInfo>.',
            'request'    : [
            ],
            'response'   : {
                'FIELDS':  [
                    ['state',               INT,      1,   'moteState'],
                    ['moteStateReason',     INT,      1,   None],
                    ['changeCounter',       INT,      2,   None],
                    ['numParents',          INT,      1,   None],
                    ['moteAlarms',          INT,      4,   None],
                    ['statusFlags',         INT,      1,   None],
                ],
            },
            'responseCodes': {
               'RC_OK'                      : 'Operation was successfully completed',
               'RC_INVALID_LEN'             : 'Invalid packet length',
               'RC_UNKNOWN_PARAM'           : 'Unknown parameter value',
            },
        },
        {
            'id'         : 0x0F,
            'name'       : 'time',
            'description': 'The getParameter<time> command is used to request the current time on the mote.',
            'request'    : [
            ],
            'response'   : {
                'FIELDS':  [
                    ['utcTime',             HEXDATA,  8,   None],
                    ['asn',                 HEXDATA,  5,   None],
                    ['asnOffset',           INT,      2,   None],
                ],
            },
            'responseCodes': {
               'RC_OK'                      : 'Operation was successfully completed',
               'RC_INVALID_LEN'             : 'Invalid packet length',
               'RC_UNKNOWN_PARAM'           : 'Unknown parameter value',
            },
        },
        {
            'id'         : 0x10,
            'name'       : 'charge',
            'description': 'The getParameter<charge> command retrieves estimated charge consumption of the mote since the last reset, as well as the mote uptime and last measured temperature.',
            'request'    : [
            ],
            'response'   : {
                'FIELDS':  [
                    ['charge',              INT,      4,   None],
                    ['uptime',              INT,      4,   None],
                    ['temperature',         INTS,     1,   None],
                    ['fractionalTemp',      INT,      1,   None],
                ],
            },
            'responseCodes': {
               'RC_OK'                      : 'Operation was successfully completed',
               'RC_INVALID_LEN'             : 'Invalid packet length',
               'RC_UNKNOWN_PARAM'           : 'Unknown parameter value',
            },
        },
        {
            'id'         : 0x11,
            'name'       : 'testRadioRxStats',
            'description': 'The getParameter<testRadioRxStats> command retrieves statistics for the latest radio reception test performed using the testRadioRx command. The radio test statistics contain the number of good packets received, the number of bad packets (CRC failures) received, the average RSSI (in dBm) of successfully received packets, and the average link quality indicator (LQI) of successfully received packets during the test.',
            'request'    : [
            ],
            'response'   : {
                'FIELDS':  [
                    ['rxOk',                INT,      2,   None],
                    ['rxFailed',            INT,      2,   None],
                    ['aveRSSI',             INTS,     1,   None],
                    ['aveLQI',              INT,      1,   None],
                ],
            },
            'responseCodes': {
               'RC_OK'                      : 'Operation was successfully completed',
               'RC_INVALID_LEN'             : 'Invalid packet length',
               'RC_UNKNOWN_PARAM'           : 'Unknown parameter value.',
            },
        },
        {
            'id'         : 0x1a,
            'name'       : 'lock',
            'description': 'The getParameter<lock> command returns the current (RAM resident) lock code and locking master. To determine what the lock status will be after reset, use the getNVParameter<lock> command. Note: This parameter is available in devices running mote software >= 1.1.0',
            'request'    : [
            ],
            'response'   : {
                'FIELDS':  [
                    ['code',                INT,      1,   None],
                    ['master',              INT,      2,   None],
                ],
            },
            'responseCodes': {
               'RC_OK'                      : 'Operation was successfully completed',
               'RC_INVALID_LEN'             : 'Invalid packet length',
               'RC_UNKNOWN_PARAM'           : 'Unknown parameter value',
            },
        },
    ]

    subCommandsSetNv = [
        {
            'id'         : 0x01,
            'name'       : 'macAddress',
            'description': 'The setNVParameter<macAddress> command may be used to supersede the factory-configured MAC address of the mote.',
            'request'    : [
                ['macAddr',                 HEXDATA,  8,   None],
            ],
            'response'   : {
                'FIELDS':  [
                ],
            },
            'responseCodes': {
               'RC_OK'                      : 'Operation was successfully completed',
               'RC_INVALID_LEN'             : 'Invalid packet length',
               'RC_WRITE_FAIL'              : 'Write did not complete',
               'RC_LOW_VOLTAGE'             : 'Voltage check failed',
               'RC_UNKNOWN_PARAM'           : 'Unknown parameter value',
            },
            'serializer' : 'serializeSetNv',
        },
        {
            'id'         : 0x02,
            'name'       : 'joinKey',
            'description': 'The setNVParameter<joinKey> command may be used to set the join key. Upon receiving this request, the mote stores the new join key in its persistent storage. Using the write RAM option will only have an effect if the command is called while the mote is in Idle state. Otherwise, the new value will be used after the next mote boot.',
            'request'    : [
                ['joinKey',                 HEXDATA,  16,  None],
            ],
            'response'   : {
                'FIELDS':  [
                ],
            },
            'responseCodes': {
               'RC_OK'                      : 'Operation was successfully completed',
               'RC_INVALID_LEN'             : 'Invalid packet length',
               'RC_WRITE_FAIL'              : 'Write did not complete',
               'RC_LOW_VOLTAGE'             : 'Voltage check failed',
               'RC_UNKNOWN_PARAM'           : 'Unknown parameter value',
            },
            'serializer' : 'serializeSetNv',
        },
        {
            'id'         : 0x03,
            'name'       : 'networkId',
            'description': "The setNVParameter<networkId> command may be used to set the persistent Network ID of the mote. The networkId is used to separate networks, and can be set during manufacturing or in the field. The mote reads this value from persistent storage at boot time. Note: while the mote is in Idle state, it is possible to update the value of mote's in-RAM Network ID by using the RAM flag in the header of this command. This avoids the extra reset that is needed to start using the Network ID. Network ID can also be set over the air using HART command 773 in a WirelessHART-compliant network.\n\nAs of version 1.1.1, a network ID of 0xFFFF can be used to indicate that the mote should join the first network heard.\n\n0xFFFF is never used over the air as a valid HART network ID - do not set the Manager's network ID to 0xFFFF.",
            'request'    : [
                ['networkId',               INT,      2,   None],
            ],
            'response'   : {
                'FIELDS':  [
                ],
            },
            'responseCodes': {
               'RC_OK'                      : 'Operation was successfully completed',
               'RC_INVALID_LEN'             : 'Invalid packet length',
               'RC_WRITE_FAIL'              : 'Write did not complete',
               'RC_LOW_VOLTAGE'             : 'Voltage check failed',
               'RC_UNKNOWN_PARAM'           : 'Unknown parameter value',
            },
            'serializer' : 'serializeSetNv',
        },
        {
            'id'         : 0x04,
            'name'       : 'txPower',
            'description': 'The setNVParameter<txPower> command sets the mote output power. Refer to product datasheets for supported RF output power values. For example, if the mote has a typical RF output power of +8 dBm when the Power Amplifier (PA) is enabled, then set the txPower parameter to 8 to enable the PA. Similarly, if the mote has a typical RF output power of -2 dBm when the PA is disabled, then set the txPower parameter to -2 to turn off the PA. This command may be issued at any time and takes effect at the next mote boot. To change the transmit power immediately, use the write RAM option of this command, which can also be used at any time.',
            'request'    : [
                ['txPower',                 INTS,     1,   None],
            ],
            'response'   : {
                'FIELDS':  [
                ],
            },
            'responseCodes': {
               'RC_OK'                      : 'Operation was successfully completed',
               'RC_INVALID_LEN'             : 'Invalid packet length',
               'RC_WRITE_FAIL'              : 'Write did not complete',
               'RC_LOW_VOLTAGE'             : 'Read did not complete',
               'RC_UNKNOWN_PARAM'           : 'Unknown parameter value',
            },
            'serializer' : 'serializeSetNv',
        },
        {
            'id'         : 0x05,
            'name'       : 'powerInfo',
            'description': 'The setNVParameter<powerInfo> command specifies the average current that is available to the mote. Using the write RAM option will only have an effect if the command is called while the mote is in Idle state. Otherwise, the new value will be used after the next mote boot.',
            'request'    : [
                ['powerSource',             INT,      1,   'PowerSource'],
                ['dischargeCur',            INT,      2,   None],
                ['dischargeTime',           INT,      4,   None],
                ['recoverTime',             INT,      4,   None],
            ],
            'response'   : {
                'FIELDS':  [
                ],
            },
            'responseCodes': {
               'RC_OK'                      : 'Operation was successfully completed',
               'RC_INVALID_LEN'             : 'Invalid packet length',
               'RC_WRITE_FAIL'              : 'Write did not complete',
               'RC_LOW_VOLTAGE'             : 'Voltage check failed',
               'RC_UNKNOWN_PARAM'           : 'Unknown parameter value',
               'RC_INVALID_VALUE'           : 'Parameter value failed validation',
            },
            'serializer' : 'serializeSetNv',
        },
        {
            'id'         : 0x13,
            'name'       : 'ttl',
            'description': "The setNVParameter<ttl> command sets the mote's persistent packet Time To Live (TTL) value. TTL specifies the maximum number of hops a packet may traverse before it is discarded from the network. A mote sets the initial value of the TTL field in the packets it generates to this value. The mote reads the value from persistent storage at boot time. To change the TTL used currently, this command may be issued with the RAM option.\n\nThe mote defaults TTL to 127. For compliant devices, the HART specification currently defaults to 32, but this will change to 249 in spec version 7.4, as will the mote default. We suggest not changing the mote default unless HART specifically raises it as a compliance issue when you submit your device for testing.",
            'request'    : [
                ['timeToLive',              INT,      1,   None],
            ],
            'response'   : {
                'FIELDS':  [
                ],
            },
            'responseCodes': {
               'RC_OK'                      : 'Operation was successfully completed',
               'RC_INVALID_LEN'             : 'Invalid packet length',
               'RC_WRITE_FAIL'              : 'Write did not complete',
               'RC_LOW_VOLTAGE'             : 'Voltage check failed',
               'RC_UNKNOWN_PARAM'           : 'Unknown parameter value',
               'RC_INVALID_VALUE'           : 'Parameter value failed validation',
            },
            'serializer' : 'serializeSetNv',
        },
        {
            'id'         : 0x14,
            'name'       : 'hartAntennaGain',
            'description': "The setNVParameter<hartAntennaGain> command stores value of the antenna gain in the mote's persistent storage. This value is added to the conducted output power of the mote when replying to HART command 797 (Write Radio Power Output) and to HART command 798 (Read Radio Output Power). The antenna gain should take into account both the gain of the antenna and any loss (for example, attenuation from a long coax cable) between the mote and the antenna. By default, this value is 2, assuming a +2 dBi antenna gain. To change the transmit power immediately, use the write RAM option of this command.",
            'request'    : [
                ['antennaGain',             INTS,     1,   None],
            ],
            'response'   : {
                'FIELDS':  [
                ],
            },
            'responseCodes': {
               'RC_OK'                      : 'Operation was successfully completed',
               'RC_INVALID_LEN'             : 'Invalid packet length',
               'RC_WRITE_FAIL'              : 'Write did not complete',
               'RC_LOW_VOLTAGE'             : 'Voltage check failed',
               'RC_UNKNOWN_PARAM'           : 'Unknown parameter value',
            },
            'serializer' : 'serializeSetNv',
        },
        {
            'id'         : 0x15,
            'name'       : 'OTAPlockout',
            'description': 'The setNVParameter<OTAPlockout> command specifies whether the mote\'s firmware can be updated over the air. Over-The-Air-Programming (OTAP) is allowed by default. The mote reads the OTAPlockout value from persistent storage at boot time. To change the value used currently, this command may be issued with RAM option.\n\nDust Networks recommends that OEMs allow their devices to receive firmware updates, either by leaving the OTAPlockout parameter at its default value, or by making OTAPlockout settable using a WirelessHART command that is available both over the air and through its wired maintenance port. OEMs have the option of making such a command password protected.',
            'request'    : [
                ['otapLockout',             INT,      1,   'OTAPLockout'],
            ],
            'response'   : {
                'FIELDS':  [
                ],
            },
            'responseCodes': {
               'RC_OK'                      : 'Operation was successfully completed.',
               'RC_INVALID_LEN'             : 'Invalid packet length',
               'RC_WRITE_FAIL'              : 'Write did not complete',
               'RC_LOW_VOLTAGE'             : 'Voltage check failed',
               'RC_UNKNOWN_PARAM'           : 'Unknown parameter value',
               'RC_INVALID_VALUE'           : 'Parameter value failed validation',
            },
            'serializer' : 'serializeSetNv',
        },
        {
            'id'         : 0x17,
            'name'       : 'hrCounterMode',
            'description': 'The setNVParameter<hrCounterMode> command may be used to control how the mote increments statistics counters reported via HART health reports. The two options are "saturating" (i.e. stop counting at maximum value) and "rollover" (i.e. continue counting through rollover). The default value of "saturating" is required for compatibility with Dust Wireless HART managers. This parameter takes effect upon mote reset.\n\nNote: This parameter is available in devices running mote software >=1.1.0',
            'request'    : [
                ['hrCounterMode',           INT,      1,   True],
            ],
            'response'   : {
                'FIELDS':  [
                ],
            },
            'responseCodes': {
               'RC_OK'                      : 'Operation was successfully completed',
               'RC_INVALID_LEN'             : 'Invalid packet length',
               'RC_WRITE_FAIL'              : 'Write did not complete',
               'RC_LOW_VOLTAGE'             : 'Voltage check failed',
               'RC_UNKNOWN_PARAM'           : 'Unknown parameter value',
            },
            'serializer' : 'serializeSetNv',
        },
        {
            'id'         : 0x18,
            'name'       : 'autojoin',
            'description': "The setNVParameter<autojoin> command allows the microprocessor to change between automatic and manual joining by the mote's networking stack. In manual mode, an explicit join command from the application is required to initiate joining. This setting is persistent and takes effect after mote reset. (Available Mote >= 1.1) Note that auto join mode must not be set if the application is also configured to join (e.g combining 'auto join' with 'master' mode will result in mote not joining).",
            'request'    : [
                ['autojoin',                INT,      1,   None],
            ],
            'response'   : {
                'FIELDS':  [
                    ['nvParamId',           INT,      1,   None],
                ],
            },
            'responseCodes': {
               'RC_OK'                      : 'Operation was successfully completed',
               'RC_INVALID_LEN'             : 'Invalid packet length',
               'RC_WRITE_FAIL'              : 'Write did not complete',
               'RC_LOW_VOLTAGE'             : 'Voltage check failed',
               'RC_UNKNOWN_PARAM'           : 'Unknown parameter value',
            },
            'serializer' : 'serializeSetNv',
        },
        {
            'id'         : 0x19,
            'name'       : 'hartCompliantMode',
            'description': 'The setNVParameter<hartCompliantMode> command may be used to force strict compliance to HART specification requirements, specifically:\n\n- join timeouts (faster in non-compliant mode)\n- Keepalive interval (adapts to synch quality in non-compliant mode)\n- Health report format (uses saturating counters in non-compliant mode)\n\nNote: This parameter is referred to as compliantMode in documentation for versions 1.1.x, and hartCompliantMode in >=1.2.x, but the parameter ID is the same in both versions. The corresponding CLI command is called mset compliantMode in 1.1.x, and mset hartCompliantMode in >=1.2.x',
            'request'    : [
                ['hartCompliantMode',       INT,      1,   None],
            ],
            'response'   : {
                'FIELDS':  [
                ],
            },
            'responseCodes': {
               'RC_OK'                      : 'Operation was successfully completed',
               'RC_INVALID_LEN'             : 'Invalid packet length',
               'RC_WRITE_FAIL'              : 'Write did not complete',
               'RC_LOW_VOLTAGE'             : 'Voltage check failed',
               'RC_UNKNOWN_PARAM'           : 'Unknown parameter value',
            },
            'serializer' : 'serializeSetNv',
        },
        {
            'id'         : 0x1a,
            'name'       : 'lock',
            'description': 'The setNVParameter<lock> command persistently locks/unlocks select HART commands (ones that affect the configuration changed flag) to a specific master (GW or serial maintenance port) to prevent the other master from changing it. This command is intended for use when the lock persists through power cycle or reset. For temporary locking, use the setParameter<lock> command. Bit 7 in the flags field of the API header (see Packet Format) should be set (store in NV & RAM) when calling this command. Note: This parameter is available in devices running mote software >= 1.1.0',
            'request'    : [
                ['code',                    INT,      1,   None],
                ['master',                  INT,      2,   None],
            ],
            'response'   : {
                'FIELDS':  [
                ],
            },
            'responseCodes': {
               'RC_OK'                      : 'Operation was successfully completed',
               'RC_INVALID_LEN'             : 'Invalid packet length',
               'RC_WRITE_FAIL'              : 'Write did not complete',
               'RC_LOW_VOLTAGE'             : 'Voltage check failed',
               'RC_UNKNOWN_PARAM'           : 'Unknown parameter value',
            },
            'serializer' : 'serializeSetNv',
        },
        {
            'id'         : 0x1b,
            'name'       : 'euCompliantMode',
            'description': 'The setNVParameter<euCompliantMode> command may be used to enforce EN 300 328 duty cycle limits based on output power. This may cause the mote to skip some transmit opportunities to remain within average power limits. Motes below +10 dBm radiated power do not need to duty cycle to meet EN 300 328 requirements.\n\nNote: This parameter is available in version >=1.2.x',
            'request'    : [
                ['euCompliantMode',         INT,      1,   None],
            ],
            'response'   : {
                'FIELDS':  [
                ],
            },
            'responseCodes': {
               'RC_OK'                      : 'Operation was successfully completed',
               'RC_INVALID_LEN'             : 'Invalid packet length',
               'RC_WRITE_FAIL'              : 'Write did not complete',
               'RC_LOW_VOLTAGE'             : 'Voltage check failed',
               'RC_UNKNOWN_PARAM'           : 'Unknown parameter value',
            },
            'serializer' : 'serializeSetNv',
        },
        {
            'id'         : 0x1c,
            'name'       : 'joinShedTime',
            'description': 'The setNVParameter<joinShedTime> command sets the join shed time u sed with HART command 771/772 to determine when the mote should transition between active and passive search. This command may be issued at any time and takes effect at the next mote boot.',
            'request'    : [
                ['joinShedTime',            INT,      4,   None],
            ],
            'response'   : {
                'FIELDS':  [
                ],
            },
            'responseCodes': {
               'RC_OK'                      : 'Operation was successfully completed',
               'RC_INVALID_LEN'             : 'Invalid packet length',
               'RC_WRITE_FAIL'              : 'Write did not complete',
               'RC_LOW_VOLTAGE'             : 'Voltage check failed',
               'RC_UNKNOWN_PARAM'           : 'Unknown parameter value',
            },
            'serializer' : 'serializeSetNv',
        },
    ]
    
    subCommandsGetNv = [
        {
            'id'         : 0x01,
            'name'       : 'macAddress',
            'description': 'The getNVParameter<macAddress> command returns the MAC address stored in mote\'s persistent storage (i.e. set with setNVParameter<macAddress>).\n\nThis command returns 0000000000000000 if the macAddress has not been set previously - the mote will use its hardware MAC in this case, but it is not displayed with this command.',
            'request'    : [
            ],
            'response'   : {
                'FIELDS':  [
                    ['macAddr',             HEXDATA,  8,   None],
                ],
            },
            'responseCodes': {
               'RC_OK'                      : 'Operation was successfully completed',
               'RC_UNKNOWN_PARAM'           : 'Unknown parameter value',
               'RC_READ_FAIL'               : 'Read did not complete',
               'RC_LOW_VOLTAGE'             : 'Voltage check failed',
            },
            'serializer' : 'serializeGetNv',
        },
        {
            'id'         : 0x03,
            'name'       : 'networkId',
            'description': "The getNVParameter<networkId> command returns the Network ID stored in mote's persistent storage.",
            'request'    : [
            ],
            'response'   : {
                'FIELDS':  [
                    ['networkId',           INT,      2,   None],
                ],
            },
            'responseCodes': {
               'RC_OK'                      : 'Operation was successfully completed',
               'RC_UNKNOWN_PARAM'           : 'Unknown parameter value',
               'RC_READ_FAIL'               : 'Read did not complete',
               'RC_LOW_VOLTAGE'             : 'Voltage check failed',
            },
            'serializer' : 'serializeGetNv',
        },
        {
            'id'         : 0x04,
            'name'       : 'txPower',
            'description': 'The getNVParameter<txPower> command returns the transmit power value stored in mote\'s persistent storage.',
            'request'    : [
            ],
            'response'   : {
                'FIELDS':  [
                    ['txPower',             INTS,     1,   None],
                ],
            },
            'responseCodes': {
               'RC_OK'                      : 'Operation was successfully completed',
               'RC_UNKNOWN_PARAM'           : 'Unknown parameter value',
               'RC_READ_FAIL'               : 'Read did not complete',
               'RC_LOW_VOLTAGE'             : 'Voltage check failed',
            },
            'serializer' : 'serializeGetNv',
        },
        {
            'id'         : 0x05,
            'name'       : 'powerInfo',
            'description': 'The getNVParameter<powerInfo> command returns the power supply information stored in mote\'s persistent storage.',
            'request'    : [
            ],
            'response'   : {
                'FIELDS':  [
                    ['powerSource',         INT,      1,   'PowerSource'],
                    ['dischargeCur',        INT,      2,   None],
                    ['dischargeTime',       INT,      4,   None],
                    ['recoverTime',         INT,      4,   None],
                ],
            },
            'responseCodes': {
               'RC_OK'                      : 'Operation was successfully completed',
               'RC_UNKNOWN_PARAM'           : 'Unknown parameter value',
               'RC_READ_FAIL'               : 'Read did not complete',
               'RC_LOW_VOLTAGE'             : 'Voltage check failed',
            },
            'serializer' : 'serializeGetNv',
        },
        {
            'id'         : 0x13,
            'name'       : 'ttl',
            'description': 'The getNVParameter<ttl> command reads the Time To Live parameter from the mote\'s persistent storage. Time To Live is used when the mote sends a packet into the network, and specifies the maximum number of hops the packet may traverse before it is discarded from the network.',
            'request'    : [
            ],
            'response'   : {
                'FIELDS':  [
                     ['timeToLive',         INT,      1,   None],
                ],
            },
            'responseCodes': {
               'RC_OK'                      : 'Operation was successfully completed',
               'RC_UNKNOWN_PARAM'           : 'Unknown parameter value',
               'RC_READ_FAIL'               : 'Write did not complete',
               'RC_LOW_VOLTAGE'             : 'Voltage check failed',
            },
            'serializer' : 'serializeGetNv',
        },
        {
            'id'         : 0x14,
            'name'       : 'HARTantennaGain',
            'description': 'The getNVParameter<HARTantennaGain> command reads the antenna gain value from the mote\'s persistent storage. This value is added to conducted output power of the Dust mote when replying to HART command 797 (Write Radio Power Output) and to HART command 798 (Read Radio Output Power).',
            'request'    : [
            ],
            'response'   : {
                'FIELDS':  [
                     ['antennaGain',        INTS,     1,   None],
                ],
            },
            'responseCodes': {
               'RC_OK'                      : 'Operation was successfully completed',
               'RC_UNKNOWN_PARAM'           : 'Unknown parameter value',
               'RC_READ_FAIL'               : 'Read did not complete',
               'RC_LOW_VOLTAGE'             : 'Voltage check failed',
            },
            'serializer' : 'serializeGetNv',
        },
        {
            'id'         : 0x15,
            'name'       : 'OTAPlockout',
            'description': 'The getNVParameter<OTAPlockout> command reads the OTAP lockout setting from the motes persistent storage. OTAP lockout specifies whether the mote can be Over-The-Air-Programmed (OTAP).',
            'request'    : [
            ],
            'response'   : {
                'FIELDS':  [
                    ['otapLockout',         INT,      1,   'OTAPLockout'],
                ],
            },
            'responseCodes': {
               'RC_OK'                      : 'Operation was successfully completed',
               'RC_UNKNOWN_PARAM'           : 'Unknown parameter value',
               'RC_READ_FAIL'               : 'Read did not complete',
               'RC_LOW_VOLTAGE'             : 'Voltage check failed',
            },
            'serializer' : 'serializeGetNv',
        },
        {
            'id'         : 0x17,
            'name'       : 'hrCounterMode',
            'description': 'The getNVParameter<hrCounterMode> command may be used to retrieve the health report counter mode that is used by devices. This mode controls how the mote deals with statistics counters when they reach their maximum value.\n\nNote: This parameter is available in devices running mote software >=1.1.0',
            'request'    : [
            ],
            'response'   : {
                'FIELDS':  [
                    ['hrCounterMode',       INT,      1,   True],
                ],
            },
            'responseCodes': {
               'RC_OK'                      : 'Operation was successfully completed',
               'RC_UNKNOWN_PARAM'           : 'Unknown parameter value',
               'RC_READ_FAIL'               : 'Read did not complete',
            },
            'serializer' : 'serializeGetNv',
        },
        {
            'id'         : 0x18,
            'name'       : 'autojoin',
            'description': "The getNVParameter<autojoin> command returns the autojoin status stored in mote's persistent storage (i.e. set with setNVParameter<autojoin>). Autojoin can be used to cause a mote in slave mode to join on its own when booted.",
            'request'    : [
            ],
            'response'   : {
                'FIELDS':  [
                    ['autojoin',            INT,      1,   None],
                ],
            },
            'responseCodes': {
               'RC_OK'                      : 'Operation was successfully completed',
               'RC_UNKNOWN_PARAM'           : 'Unknown parameter value',
               'RC_READ_FAIL'               : 'Read did not complete',
               'RC_LOW_VOLTAGE'             : 'Voltage check failed',
            },
            'serializer' : 'serializeGetNv',
        },
        {
            'id'         : 0x19,
            'name'       : 'hartCompliantMode',
            'description': 'The getNVParameter<hartCompliantMode> command may be used to retrieve the HART compliance mode that is used by devices. This mode controls strict compliance to HART specification requirements, specifically:\n\n- join timeouts (faster in non-compliant mode)\n- Keepalive interval (adapts to synch quality in non-compliant mode)\n- Health report format (uses saturating counters in non-compliant mode)\n\nNote: This parameter is available in devices running mote software >= 1.1.0',
            'request'    : [
            ],
            'response'   : {
                'FIELDS':  [
                    ['hartCompliantMode',   INT,      1,   'HartComplianceMode'],
                ],
            },
            'responseCodes': {
               'RC_OK'                      : 'Operation was successfully completed',
               'RC_UNKNOWN_PARAM'           : 'Unknown parameter value',
               'RC_READ_FAIL'               : 'Read did not complete',
            },
            'serializer' : 'serializeGetNv',
        },
        {
            'id'         : 0x1a,
            'name'       : 'lock',
            'description': 'The getNVParameter < lock > command returns the persisted lock code and locking master (those to be used after reset). To determine the current lock status, use the getParameter<lock> command. Note: This parameter is available in devices running mote software >= 1.1.0',
            'request'    : [
            ],
            'response'   : {
                'FIELDS':  [
                    ['code',                INT,      1,   None],
                    ['master',              INT,      2,   None],
                ],
            },
            'responseCodes': {
               'RC_OK'                      : 'Operation was successfully completed',
               'RC_INVALID_LEN'             : 'Invalid packet length',
               'RC_UNKNOWN_PARAM'           : 'Unknown parameter value',
            },
            'serializer' : 'serializeGetNv',
        },
        {
            'id'         : 0x1b,
            'name'       : 'euCompliantMode',
            'description': 'The getNVParameter<euCompliantMode> command may be used to retrieve the EN 300 328 compliance mode that is used by devices. When enabled, the mote may skip some transmit opportunities to remain within average power limits. Motes below +10 dBm radiated power do not need to duty cycle to meet EN 300 328 requirements.\n\nNote: This parameter is available in devices running mote software >=1.2.x',
            'request'    : [
            ],
            'response'   : {
                'FIELDS':  [
                    ['euCompliantMode',     INT,      1,   None],
                ],
            },
            'responseCodes': {
               'RC_OK'                      : 'Operation was successfully completed',
               'RC_UNKNOWN_PARAM'           : 'Unknown parameter value',
               'RC_READ_FAIL'               : 'Read did not complete',
            },
            'serializer' : 'serializeGetNv',
        },
        {
            'id'         : 0x1c,
            'name'       : 'joinShedTime',
            'description': 'The getNVParameter<joinShedTime> command returns the join shed time used with HART command 771/772 to determine when the mote should transition between active and passive search.',
            'request'    : [
            ],
            'response'   : {
                'FIELDS':  [
                    ['joinShedTime',        INT,      4,   None],
                ],
            },
            'responseCodes': {
               'RC_OK'                      : 'Operation was successfully completed',
               'RC_UNKNOWN_PARAM'           : 'Unknown parameter value',
               'RC_READ_FAIL'               : 'Read did not complete',
               'RC_LOW_VOLTAGE'             : 'Voltage check failed',
            },
            'serializer' : 'serializeGetNv',
        },
    ]
        
    # We redefine this attribute inherited from ApiDefinition. See
    # ApiDefinition for a full description of the structure of this field.
    commands = [
        {
            'id'         : 0x01,
            'name'       : 'setParameter',
            'description': 'The setParameter command may be used to change parameters on the mote. The payload of each setParameter command begins with a parameter ID field that specifies the parameter being modified. All parameters modified with this command are volatile do not persist across multiple resets.',
            'request'    : [
                [SUBID1,                    INT,      1,   None],
            ],
            'response'   : {
                'FIELDS':  [
                    [RC,                    INT,      1,   True],
                    [SUBID1,                INT,      1,   None],
                ]
            },
            'subCommands': subCommandsSet,
        },
        {
            'id'         : 0x02,
            'name'       : 'getParameter',
            'description': 'The getParameter command may be used to retrieve current settings on the mote. The payload of each getParameter commands begins with a parameter Id field that specifies the parameter being accessed.',
            'request'    : [
                [SUBID1,                    INT,      1,   None],
            ],
            'response'   : {
                'FIELDS':  [
                    [RC,                    INT,      1,   True],
                    [SUBID1,                INT,      1,   None],
                ]
            },
            'subCommands': subCommandsGet,
        },
        {
            'id'         : 0x03,
            'name'       : 'setNVParameter',
            'description': 'setNVParameter command modifies persistent (non-nolatile) parameters on the mote. Generally speaking, the settings changed with this command take effect after mote reset. Note: The flags field in the command header contains a "RAM" option that may be used with some commands to update the settings immediately.',
            'request'    : [
                # the 4B reserved field is added automatically
                [SUBID1,                    INT,      1,   None],
            ],
            'response'   : {
                'FIELDS':  [
                    [RC,                    INT,      1,   True],
                    [SUBID1,                INT,      1,   None],
                ]
            },
            'subCommands': subCommandsSetNv,
        },
        {
            'id'         : 0x04,
            'name'       : 'getNVParameter',
            'description': 'The getNVParameter command can be used to retrieve the value of persistent parameters on the mote.',
            'request'    : [
                # the 4B reserved field is added automatically
                [SUBID1,                    INT,      1,   None],
            ],
            'response'   : {
                'FIELDS':  [
                    [RC,                    INT,      1,   True],
                    [SUBID1,                INT,      1,   None],
                ]
            },
            'subCommands': subCommandsGetNv,
        },
        {
            'id'         : 0x05,
            'name'       : 'send',
            'description': "The send command allows a serial device to send a packet into the network through the mote's serial port. The mote forwards the packet to the network upon receiving it. The microprocessor must not attempt to send data at a rate that exceeds its allocated bandwidth. For a WirelessHART device, the payload of the packet must include the status byte and the extended status byte, followed by one or more sets of HART commands up to the maximum send payload size, as follows:\n\nRequest: Status|Extended Status|Cmd1|Length1|Data1|Cmd2|Length2|Data2... Response: Status|Extended Status|Cmd1|Length1(includes response code)|RC1|Data1|Cmd2|Length2|RC2|Data2...\n\nPrior to sending the payload into the network, the mote caches the value of Status and Extended Status to use in packets it originates locally. The send command is only valid when the mote is in the Operational state. If the mote receives this command when it is not in the Operational state, it returns the error RC_INV_STATE. Note: The serial device can receive a request while the mote is in the process of transition from the Connected state to the Operational state.",
            'request'    : [
                ['tranType',                BOOL,     1,   True],
                ['tranDir',                 BOOL,     1,   True],
                ['destAddr',                HEXDATA,  2,   None],
                ['serviceId',               INT,      1,   None],
                ['appDomain',               INT,      1,   'ApplicationDomain'],
                ['priority',                INT,      1,   'Priority'],
                ['reserved',                INT,      2,   None],
                ['seqNum',                  INT,      1,   None],
                ['payloadLen',              INT,      1,   None],
                ['payload',                 HEXDATA,  None,None],
            ],
            'response'   : {
                'FIELDS':  [
                    [RC,                    INT,      1,   True],
                ],
            },
            'responseCodes': {
               'RC_OK'                      : 'Operation was successfully completed',
               'RC_INVALID_LEN'             : 'Invalid packet length',
               'RC_UNKNOWN_CMD'             : 'Unknown command',
               'RC_INVALID_VALUE'           : 'Invalid application domain or priority',
               'RC_NOT_FOUND'               : 'Service or route to destination not found',
               'RC_NO_RESOURCES'            : 'Mote buffers are full',
               'RC_INVALID_STATE'           : 'Mote is not in Operational state',
            },
            'serializer' : 'serializeSend',
        },
        {
            'id'         : 0x6,
            'name'       : 'join',
            'description': 'The join command requests that a mote start searching for the network and attempt to join. The mote must be in the Idle state or the Promiscuous Listen state (see search) for this command to be valid. The join time is partly determined by the join duty cycle. For guidance on setting the join duty cycle, see setParameter<joinDutyCycle>.',
            'request'    : [
            ],
            'response'   : {
                'FIELDS':  [
                    [RC,                    INT,      1,   True],
                ],
            },
            'responseCodes': {
               'RC_OK'                      : 'Operation was successfully completed',
               'RC_INVALID_STATE'           : 'Invalid state for join',
               'RC_INCOMPLETE_JOIN_INFO'    : 'Incomplete join information',
            },
        },
        {
            'id'         : 0x07,
            'name'       : 'disconnect',
            'description': 'The disconnect command requests that the mote disconnect from the network. The mote will send an indication to its network neighbors that it is about to become unavailable. Just after the mote disconnects, it sends the microprocessor an events packet with the disconnected bit set, indicating it will reset. This command is only valid in when the mote is in the Connected or Operational state (see Mote State).\n\nThe OEM microprocessor should disconnect from the network if the device is going to power down, reset, or otherwise be unavailable for a long period.\n\nA mote will reset itself after having sent the disconnect notification to the OEM microprocessor. The microprocessor should wait to acknowledge the boot event before shutting down.',
            'request'    : [
            ],
            'response'   : {
                'FIELDS':  [
                    [RC,                    INT,      1,   True],
                ],
            },
            'responseCodes': {
               'RC_OK'                      : 'Command was accepted',
            },
        },
        {
            'id'         : 0x08,
            'name'       : 'reset',
            'description': 'Upon receiving this command, the mote resets itself after a short delay. The mote will always send a response packet before initiating the reset. To force the mote to gracefully leave the network, use the disconnect command.',
            'request'    : [
            ],
            'response'   : {
                'FIELDS':  [
                    [RC,                    INT,      1,   True],
                ],
            },
            'responseCodes': {
               'RC_OK'                      : 'Command was accepted',
            },
        },
        {
            'id'         : 0x09,
            'name'       : 'lowPowerSleep',
            'description': 'The lowPowerSleep command shuts down all peripherals and places the mote in deep sleep mode. The lowPowerSleep command may be issued at any time and will cause the mote to interrupt all in-progress network operation. The command executes after the mote sends its response. The mote enters deep sleep within two seconds after the command executes.\n\nThe OEM microprocessor should put the mote into low power sleep when the mote needs to be offline for an extended period of time. In most cases, this will result in a lower current state of the mote than simply asserting /RST without putting the mote in low power sleep. To achieve a graceful disconnect, use the disconnect command before using the lowPowerSleep command. The mote can only be awakened from low power sleep by asserting a non-maskable interrupt, such as the /RST control line. For power consumption information, refer to the mote product datasheet.',
            'request'    : [
            ],
            'response'   : {
                'FIELDS':  [
                    [RC,                    INT,      1,   True],
                ],
            },
            'responseCodes': {
               'RC_OK'                      : 'Command was accepted',
            },
        },
        {
            'id'         : 0x0A,
            'name'       : 'hartPayload',
            'description': 'The hartPayload command allows the microprocessor to forward a HART payload to the mote. The format of the command must be as follows:\n\n16-bit command number | data length | data\n\nThe reply (if any) will be in the form of a HART response and sent in the payload of the acknowledgement. This command always returns RC_OK - any HART errors are returned within the response payload, e.g. if a command is not implemented, the response payload field will contain the 16-bit command number, a length = 1, and data = 0x40 (HART RC 64).',
            'request'    : [
                ['payloadLen',              INT,      1,   None],
                ['payload',                 HEXDATA,  None,None],
            ],
            'response'   : {
                'FIELDS':  [
                    [RC,                    INT,      1,   True],
                    ['payloadLen',          INT,      1,   None],
                    ['payload',             HEXDATA,  None,None],
                ],
            },
            'responseCodes': {
               'RC_OK'                      : 'Operation was successfully completed',
               'RC_INVALID_LEN'             : 'Invalid packet length',
            },
        },
        {
            'id'         : 0x0B,
            'name'       : 'testRadioTx',
            'description': 'The testRadioTx command initiates transmission over the radio. This command may only be issued prior to the mote joining the network. While executing this command the mote sends numPackets packets. Each packet consists of a payload of up to 125 bytes, and a 2-byte 802.15.4 CRC at the end. Bytes 0 and 1 contain the packet number (in big-endian format) that increments with every packet transmitted. Bytes 2..N contain a counter (from 0..N-2) that increments with every byte inside payload. Transmissions occur on the specified channel.\n\nIf number of packets parameter is set to 0x00, the mote will generate an unmodulated test tone on the selected channel. The test tone can only be stopped by resetting the mote.\n\n\n\nChannel numbering is 0-15, corresponding to IEEE 2.4 GHz channels 11-26.\n\n\n\nNote: this command is deprecated and should not be used in new designs. The replacement command is testRadioTxExt.',
            'request'    : [
                ['channel',                 INT,      1,   None],
                ['numPackets',              INT,      2,   None],
            ],
            'response'   : {
                'FIELDS':  [
                    [RC,                    INT,      1,   True],
                ],
            },
            'responseCodes': {
               'RC_OK'                      : 'Operation was successfully completed',
               'RC_INVALID_VALUE'           : 'A parameter value is not valid',
               'RC_INVALID_STATE'           : 'The mote is not in Idle state',
               'RC_BUSY'                    : 'Another test operation is in progress',
               'RC_INVALID_LEN'             : 'Invalid packet size',
            },
        },
        {
            'id'         : 0x0C,
            'name'       : 'testRadioRx',
            'description': 'The testRadioRx command clears all previously collected statistics and initiates a test of radio reception for the specified channel and duration. During the test, the mote keeps statistics about the number of packets received (with and without error). The test results may be retrieved using the getParameter<testRadioRxStats> command. The mote must be reset (either hardware or software reset) after radio tests are complete and prior to joining.\n\n\n\nChannel numbering is 0-15, corresponding to IEEE 2.4 GHz channels 11-26.\n\n\n\nNote: this command is deprecated and should not be used in new designs. The replacement command is testRadioRxExt.',
            'request'    : [
                ['channel',                 INT,      1,   None],
                ['time',                    INT,      2,   None],
            ],
            'response'   : {
                'FIELDS':  [
                    [RC,                    INT,      1,   True],
                ],
            },
            'responseCodes': {
               'RC_OK'                      : 'Operation was successfully completed',
               'RC_INVALID_VALUE'           : 'A parameter value is not valid',
               'RC_INVALID_STATE'           : 'The mote is not in Idle state',
               'RC_BUSY'                    : 'Another test operation is in progress',
            },
        },
        {
            'id'         : 0x10,
            'name'       : 'clearNV',
            'description': "The clearNV command resets the motes Non-Volatile (NV) memory to its factory-default state. Refer to the WirelessHART User Guide for table of default values. Note that since this command clears the mote's security join counter, the corresponding manager's Access Control List (ACL) entry may need to be cleared as well to allow joining.",
            'request'    : [
            ],
            'response'   : {
                'FIELDS':  [
                    [RC,                    INT,      1,   True],
                ],
            },
            'responseCodes': {
               'RC_OK'                      : 'Operation was successfully completed',
               'RC_INVALID_LEN'             : 'Invalid packet length',
               'RC_WRITE_FAIL'              : 'Flash operation failed',
               'RC_LOW_VOLTAGE'             : 'Low voltage',
            },
        },
        {
            'id'         : 0x11,
            'name'       : 'search',
            'description': 'The search command causes the mote to listen for network advertisements and notify the microprocessor about each advertisement it hears. This is referred to as the Promiscuous Listen state. Notifications are sent using the advReceived notification. The search command may only be issued prior to join. The mote stays in listen mode until the join command is received or the mote is reset.',
            'request'    : [
            ],
            'response'   : {
                'FIELDS':  [
                    [RC,                    INT,      1,   True],
                ],
            },
            'responseCodes': {
               'RC_OK'                      : 'Operation was successfully completed',
               'RC_INVALID_STATE'           : 'Mote is in invalid state for this operation',
            },
        },
        {
            'id'         : 0x13,
            'name'       : 'testRadioTxExt',
            'description': 'The testRadioTxExt command allows the microprocessor to initiate a radio transmission test. This command may only be issued prior to the mote joining the network. Three types of transmission tests are supported:\n\n- Packet transmission\n- Continuous modulation\n- Continuous wave (unmodulated signal)\n\nIn a packet transmission test, the mote generates a repeatCnt number of packet sequences. Each sequence consists of up to 10 packets with configurable size and delays. Each packet starts with a PHY preamble (5 bytes), followed by a PHY length field (1 byte), followed by data payload of up to 125 bytes, and finally a 2-byte 802.15.4 CRC at the end. Byte 0 of the payload contains stationId of the sender. Bytes 1 and 2 contain the packet number (in big-endian format) that increments with every packet transmitted. Bytes 3..N contain a counter (from 0..N-3) that increments with every byte inside payload. Transmissions occur on the set of channels defined by chanMask , selected inpseudo-randomorder.\n\nIn a continuous modulation test, the mote generates continuous pseudo-random modulated signal, centered at the specified channel. The test is stopped by resetting the mote.\n\nIn a continuous wave test, the mote generates an unmodulated tone, centered at the specified channel. The test tone is stopped by resetting the mote.\n\nThe testRadioTxExt command may only be issued when the mote is in Idle mode, prior to its joining the network. The mote must be reset (either hardware or software reset) after radio tests are complete and prior to joining.\n\nThe station ID is a user selectable value. It is used in packet tests so that a receiver can identify packets from this device in cases where there may be multiple tests running in the same radio space. This field is not used for CM or CW tests. See testRadioRX (SmartMesh IP) or testRadioRxExt (SmartMesh WirelessHART).\n\n\n\nChannel numbering is 0-15, corresponding to IEEE 2.4 GHz channels 11-26.',
            'request'    : [
                ['testType',                INT,      1,   'TestType'],
                ['chanMask',                HEXDATA,  2,   None],
                ['repeatCnt',               INT,      2,   None],
                ['txPower',                 INTS,     1,   None],
                ['seqSize',                 INT,      1,   'seqSize'],
                ['pkLen_1',                 INT,      1,   None],
                ['delay_1',                 INT,      2,   None],
                ['pkLen_2',                 INT,      1,   None],
                ['delay_2',                 INT,      2,   None],
                ['pkLen_3',                 INT,      1,   None],
                ['delay_3',                 INT,      2,   None],
                ['pkLen_4',                 INT,      1,   None],
                ['delay_4',                 INT,      2,   None],
                ['pkLen_5',                 INT,      1,   None],
                ['delay_5',                 INT,      2,   None],
                ['pkLen_6',                 INT,      1,   None],
                ['delay_6',                 INT,      2,   None],
                ['pkLen_7',                 INT,      1,   None],
                ['delay_7',                 INT,      2,   None],
                ['pkLen_8',                 INT,      1,   None],
                ['delay_8',                 INT,      2,   None],
                ['pkLen_9',                 INT,      1,   None],
                ['delay_9',                 INT,      2,   None],
                ['pkLen_10',                INT,      1,   None],
                ['delay_10',                INT,      2,   None],
                ['stationId',               INT,      1,   None],
            ],
            'response'   : {
                'FIELDS':  [
                    [RC,                    INT,      1,   True],
                ],
            },
            'responseCodes': {
               'RC_OK'                      : 'Operation was successfully completed',
               'RC_INVALID_VALUE'           : 'A parameter value is not valid',
               'RC_INVALID_STATE'           : 'The mote is not in Idle state',
               'RC_BUSY'                    : 'Another test operation is in progress',
               'RC_INVALID_LEN'             : 'Invalid packet size',
            },
            'serializer' : 'serialize_testRadioTxExt',
        },
        {
            'id'         : 0x14,
            'name'       : 'testRadioRxExt',
            'description': 'The testRadioRxExt command clears all previously collected statistics and initiates a test of radio reception for the specified channel and duration. During the test, the mote keeps statistics about the number of packets received (with and without error). The test results may be retrieved using the getParameter<testRadioRxStats> command. The mote must be reset (either hardware or software reset) after radio tests are complete and prior to joining.\n\nStation ID is available in IP Mote 1.4.0 or later, and WirelessHART Mote 1.1.2 or later. The station ID is a user selectable value used to isolate traffic if multiple tests are running in the same radio space. It must be set to match the station ID used by the transmitter.\n\n\n\nChannel numbering is 0-15, corresponding to IEEE 2.4 GHz channels 11-26.',
            'request'    : [
                ['channelMask',             HEXDATA,  2,   None],
                ['time',                    INT,      2,   None],
                ['stationId',               INT,      1,   None],
            ],
            'response'   : {
                'FIELDS':  [
                    [RC,                    INT,      1,   True],
                ],
            },
            'responseCodes': {
               'RC_OK'                      : 'Operation was successfully completed',
               'RC_INVALID_VALUE'           : 'A parameter value is not valid',
               'RC_INVALID_STATE'           : 'The mote is not in Idle state',
               'RC_BUSY'                    : 'Another test operation is in progress',
               'RC_INVALID_LEN'             : 'Invalid packet size',
            },
        },
        {
            'id'         : 0x15,
            'name'       : 'zeroize',
            'description': 'The zeroize (zeroise) command erases flash area that is used to store configuration parameters, such as join keys. This command is intended to satisfy the zeroization requirement of the FIPS-140 standard. After the command executes, the mote should be reset. Available in mote >= 1.1.x\n\nThe zeroize command will render the mote inoperable. It must be re-programmed via SPI or JTAG in order to be useable.',
            'request'    : [
                ['password',                INT,      4,   None],
            ],
            'response'   : {
                'FIELDS':  [
                    [RC,                    INT,      1,   True],
                ],
            },
            'responseCodes': {
               'RC_OK'                      : 'Command completed successfully',
               'RC_ERASE_FAIL'              : 'Flash could not be erased due to unexpected internal error',
            },
        },
        {
            'id'         : 0x17,
            'name'       : 'fileWrite',
            'description': 'The fileWrite command may be used to read data stored in the scratchpad file in the mote filesystem. The size of the data read is limited by the size of a serial API transaction.',
            'request'    : [
                ['descriptor',              INTS,     4,   None],
                ['offset',                  INT,      2,   None],
                ['length',                  INT,      1,   None],
                ['data',                    HEXDATA,  None,None],
            ],
            'response'   : {
                'FIELDS':  [
                    [RC,                    INT,      1,   True],
                    ['length',              INTS,     4,   None],
                ],
            },
            'responseCodes': {
               'RC_OK'                      : 'Operation was successfully completed',
               'RC_WRITE_FAIL'              : 'File could not be written',
               'RC_INVALID_VALUE'           : 'Invalid value for a parameter',
               'RC_NOT_FOUND'               : 'File descriptor was not found',
            },
        },
        {
            'id'         : 0x18,
            'name'       : 'fileRead',
            'description': 'The fileRead command may be used to read data stored in the scratchpad file in the mote filesystem. The size of the data read is limited by the size of a serial API transaction.',
            'request'    : [
                ['descriptor',              INTS,     4,   None],
                ['offset',                  INT,      2,   None],
                ['length',                  INT,      1,   None],
            ],
            'response'   : {
                'FIELDS':  [
                    [RC,                    INT,      1,   True],
                    ['descriptor',          INTS,     4,   None],
                    ['offset',              INT,      2,   None],
                    ['length',              INT,      1,   None],
                    ['data',                HEXDATA,  None,None],
                ],
            },
            'responseCodes': {
               'RC_OK'                      : 'Operation was successfully completed',
               'RC_READ_FAIL'               : 'File could not be read',
               'RC_INVALID_VALUE'           : 'Invalid value for a parameter',
               'RC_NOT_FOUND'               : 'File descriptor was not found',
            },
        },
        {
            'id'         : 0x19,
            'name'       : 'fileOpen',
            'description': 'The fileOpen command may be used to open the scratchpad file in the mote filesystem.',
            'request'    : [
                ['name',                    HEXDATA,  12,  None],
                ['options',                 INT,      1,   'FileOpenOptions'],
                ['size',                    INT,      2,   None],
                ['mode',                    INT,      1,   'FileOpenMode'],
            ],
            'response'   : {
                'FIELDS':  [
                    [RC,                    INT,      1,   True],
                    ['descriptor',          INTS,     4,   None],
                ],
            },
            'responseCodes': {
               'RC_OK'                      : 'Command was accepted',
               'RC_OPEN_FAIL'               : 'File could not be opened',
               'RC_INVALID_VALUE'           : 'Invalid value for a parameter',
            },
        },
        {
            'id'         : 0x1a,
            'name'       : 'testRadioRxPER',
            'description': 'The testRadioRxPER command initiates Packet Error Rate (PER) test in rx mode. This command may be issued only when mote is in Idle state.\n\nThis command is available in WiHART Mote version 1.2.4.1 or later',
            'request'    : [
            ],
            'response'   : {
                'FIELDS':  [
                    [RC,                    INT,      1,   True],
                ],
            },
            'responseCodes': {
               'RC_OK'                      : 'Command was accepted',
               'RC_INVALID_STATE'           : 'The mote is in invalid state to start PER test',
            },
        },
        {
            'id'         : 0x1b,
            'name'       : 'testRadioTxPER',
            'description': 'The testRadioTxPER command initiates Packet Error Rate (PER) test in tx mode. This command may be issued only when mote is in Idle state.\n\nThis command is available in WiHART Mote version 1.2.4.1 or later',
            'request'    : [
                ['txPower',        INTS,      1,   None],
                ['numPackets',     INT,       2,   None],
                ['chanMask',       HEXDATA,   2,   None],
                ['numRepeat',     INT,       2,   None],
            ],
            'response'   : {
                'FIELDS':  [
                    [RC,                    INT,      1,   True],
                ],
            },
            'responseCodes': {
               'RC_OK'                      : 'Command was accepted',
               'RC_INVALID_STATE'           : 'The mote is in invalid state to start PER test',
            },
        },
        {
            'id'         : 0x1d,
            'name'       : 'testXtalComp',
            'description': 'The testXtalComp command initiates 32kHz crystal test to check frequency accuracy. This command may be issues only when mote is in the Idle state.\n\nThis command is available in Hart Mote version 1.3.0 or later.',
            'request'    : [
                ['bias',            INT,      1,   None],
                ['spinDownMs',      INT,      2,   None],
                ['spinUpMs',        INT,      2,   None],
                ['iterations',      INT,      1,   None],
            ],
            'response'   : {
                'FIELDS':  [
                    [RC,            INT,      1,   True],
                    ['avgFreqMeas', INT,      4,   None],	
                    ['ppFreqMeas',  INT,      2,   None],					
                ],
            },
            'responseCodes': {
               'RC_OK'                      : 'Command was accepted',
               'RC_ERROR'                   : 'The device is marginal',
            },
        },
        {
            'id'         : 0x1f,
            'name'       : 'testXtal',
            'description': "The testXtal command is is used to determine the optimal trim value to center the 20MHz crystal oscillator frequency given a particular PCB layout and crystal combination. It is used to measure the 20MHz crystal, after which the user must enter trim values into the device's fuse table for access by software.\n\nThe command is available in HART Mote version 1.3.0 or later.\n\nThis command may only be used when the mote's radio is not active, i.e in the slave mode and prior to joining the network. This function requires the mote be connected to the DC9010 programming board. It could take up to 30 seconds for the command to execute. After using this command, reboot the mote to continue normal operation.",
            'request'    : [
                ['trimOpt',        INT,     1,   None],
                ['tempGrade',      INT,     1,   None],
            ],
            'response'   : {
                'FIELDS':  [
                    [RC,           INT,     1,   True],
                    ['pullVal',    INT,     1,   None],	
                    ['ppmErr',     INTS,    4,   None],					
                ],
            },
            'responseCodes': {
               'RC_OK'                      : 'Command was accepted',
               'RC_INVALID_STATE'           : 'The mote is in invalid state to start Xtal test',
            },
        },
    ]
    
    # We redefine this attribute inherited from ApiDefinition. See
    # ApiDefinition for a full description of the structure of this field.
    notifications = [
        {
            'id'         : 0xd,
            'name'       : 'timeIndication',
            'description': 'The timeIndication notification applies to mote products that support a time interrupt into the mote. The time packet includes the network time and the current UTC time relative to the manager.\n\nFor LTC5800-WHM based products, driving the TIMEn pin low (assert) wakes the processor. The pin must asserted for a minimum of t strobe s. De-asserting the pin latches the time, and a timeIndication will be generated within t response ms. Refer to the LTC5800-WHM Datasheet for additional information about TIME pin usage.\n\nThe processor will remain awake and drawing current while the TIMEn pin is asserted. To avoid drawing excess current, take care to minimize the duration of the TIMEn pin being asserted past t strobe minimum.',
            'response'   : {
                'FIELDS':  [
                    ['utcSec',              INT,      4,   None],
                    ['utcMicroSec',         INT,      4,   None],
                    ['asn',                 HEXDATA,  5,   None],
                    ['asnOffset',           INT,      2,   None],
                ],
            },
        },
        {
            'id'         : 0xe,
            'name'       : 'serviceIndication',
            'description': 'The serviceIndication notification describes new manager-originated services (ID = 0x80-FF), or changes in existing services (ID = 0x00-7F). For more info on when the serviceIndication notification is sent and details about the individual parameters, see Bandwidth Services. If the time field contains the value 0x07FFFFFF , the manager is unable to sustain the service due to network conditions and has effectively disabled the service. The service is not removed, however, and the microprocessor can elect to either delete the service or submit a request to update the service at a future time.',
            'response'   : {
                'FIELDS':  [
                    ['eventCode',           INT,      1,   None],
                    ['netMgrCode',          INT,      1,   None],
                    ['serviceId',           INT,      1,   None],
                    ['serviceState',        INT,      1,   'ServiceState'],
                    ['serviceFlags',        INT,      1,   None],
                    ['appDomain',           INT,      1,   'ApplicationDomain'],
                    ['destAddr',            HEXDATA,  2,   None],
                    ['time',                INT,      4,   None],
                ],
            },
        },
        {
            'id'         : 0xf,
            'name'       : 'events',
            'description': 'The events notification sends an event notification packet to the microprocessor informing it of new events that have occurred. The reported event is cleared from the mote when the mote receives an acknowledgement in the form of a response packet from the microprocessor.',
            'response'   : {
                'FIELDS':  [
                    ['events',              INT,      4,   None],
                    ['state',               INT,      1,   'moteState'],
                    ['moteAlarms',          INT,      4,   None],
                ],
            },
        },
        {
            'id'         : 0x81,
            'name'       : 'dataReceived',
            'description': 'The dataReceived notification notifies the microprocessor that a packet was received. When the microprocessor receives a reliable dataReceived request, in addition to acknowledging the request with a dataReceived response it must also respond using the send command.',
            'response'   : {
                'FIELDS':  [
                    ['srcAddr',             HEXDATA,  2,   None],
                    ['seqNum',              INT,      1,   None],
                    ['pktLength',           INT,      1,   None],
                    ['data',                HEXDATA,  None,None],
                ],
            },
        },
        {
            'id'         : 0x12,
            'name'       : 'advReceived',
            'description': 'The advReceived notification notifies the microprocessor each time the mote receives an advertisement packet while in promiscuous listen mode. The command contains information about the advertisement, including the Network ID, Mote ID, RSSI, and join priority (hop depth). Note that advReceived notifications are sent only if the mote has been placed in listen mode using the search command (see search).',
            'response'   : {
                'FIELDS':  [
                    ['netId',               INT,      2,   None],
                    ['moteId',              HEXDATA,  2,   None],
                    ['rssi',                INTS,     1,   None],
                    ['joinPri',             INT,      1,   None],
                ],
            },
        },
        {
            'id'         : 0x16,
            'name'       : 'suspendStarted',
            'description': 'The mote generates a suspendStarted notification when it enters the Suspended state as a result of processing Wireless HART command 972. When the suspend interval begins, the mote discontinues its radio operation and generates this notification. After the interval specified in command 972 ends, mote proceeds to reset. It is the responsibility of the attached microprocessor to re-join the network.',
            'response'   : {
                'FIELDS':  [
                    ['duration',            INT,      4,   None],
                ],
            },
        },
        {
            'id'         : 0x1c,
            'name'       : 'testRadioStatsPER',
            'description': 'The testRadioStatsPER notification is generated by the mote when PER test in RX mode is completed.\n\nThis command is available in WiHART Mote version 1.2.4 or later.',
            'response'   : {
                'FIELDS':  [
                    ['numRxOK',           INT,      2,   None],
                    ['numRxErr',          INT,      2,   None],
                    ['numRxInv',          INT,      2,   None],
                    ['numRxMiss',         INT,      2,   None],
                    ['perInt',            INT,      2,   None],
                    ['perFrac',           INT,      2,   None],
                ],
            },
        },
    ]
    
    def serialize_testRadioTxExt(self, commandArray, cmd_params):
        
        # start by serializing with complete API definition
        returnVal = self.default_serializer(commandArray, cmd_params)
        
        # remove the unused sequence definitions
        startIndex = 7+cmd_params['seqSize']*3
        numVals    = 10-cmd_params['seqSize']
        returnVal[1][startIndex:startIndex+numVals*3] = []
        
        return returnVal
