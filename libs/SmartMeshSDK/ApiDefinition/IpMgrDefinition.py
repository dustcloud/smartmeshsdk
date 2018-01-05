#!/usr/bin/python

import ApiDefinition
import ByteArraySerializer

class IpMgrDefinition(ApiDefinition.ApiDefinition):
    '''
    \ingroup ApiDefinition
    
    \brief API definition for the IP manager.
   
    \note This class inherits from ApiDefinition. It redefines the attributes of
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
    
    OPTIONAL  = [
        'pkLen_1',
        'delay_1',
        'pkLen_2',
        'delay_2',
        'pkLen_3',
        'delay_3',
        'pkLen_4',
        'delay_4',
        'pkLen_5',
        'delay_5',
        'pkLen_6',
        'delay_6',
        'pkLen_7',
        'delay_7',
        'pkLen_8',
        'delay_8',
        'pkLen_9',
        'delay_9',
        'pkLen_10',
        'delay_10',
        'stationId',
    ]
    
    def __init__(self, array2scalar = True):
        ApiDefinition.ApiDefinition.__init__(self, array2scalar)
        self.serializer = ByteArraySerializer.ByteArraySerializer(self)
    
    def default_serializer(self,commandArray,fieldsToFill):
        '''
        \brief IpMgrDefinition-specific implementation of default serializer
       
        \param commandArray   An array of the form [commandName, subCommandname]
                              The array can be of any length, and is of length 1
                              if no subcommands are used.
        \param fieldsToFill   The list of fields to send, organized as a
                              dictionary of the form
                              <tt>fieldname:fieldvalue</tt>.
       
        \returns id,byteString where id is the command ID and byteArray an array
                               of bytes
        '''
        return self.serializer.serialize(commandArray,fieldsToFill)
    
    def deserialize(self,type,cmdId,byteArray):
        '''
        \brief IpMgrDefinition-specific implementation of deserializer
        '''
        return self.serializer.deserialize(type,cmdId,byteArray)
    
    # We redefine this attribute inherited from ApiDefinition. See
    # ApiDefinition for a full description of the structure of this field.
    fieldOptions = {
        # 'notificationTypes' : [
        #     [ 1,   'event',                 'Event notification'],
        #     [ 2,   'log',                   'Log notification'],
        #     [ 4,   'data',                  'Data payload notification'],
        #     [ 5,   'ipData',                '6LoWPAN packet notification'],
        #     [ 6,   'healthReport',          'Health report notification'],
        # ],
        # 'eventTypes' : [
        #     [ 0,   'moteReset',             'A mote reset'],
        #     [ 1,   'networkReset',          'The network was reset'],
        #     [ 2,   'commandFinish ',        'A command has completed execution'],
        #     [ 3,   'moteJoin',              'A mote joined the network'],
        #     [ 4,   'moteOperational',       'A new mote was configured and is now operational'],
        #     [ 5,   'moteLost',              'A mote is no longer communicating in the network'],
        #     [ 6,   'netTime',               'Contains the network uptime (in response to a getTime command)'],
        #     [ 7,   'pingResponse',          'A reply was received from a mote ping'],
        #     [10,   'pathCreate',            'A path was created'],
        #     [11,   'pathDelete',            'A path was deleted'],
        #     [12,   'packetSent',            'A packet was sent'],
        #     [13,   'moteCreate',            'A mote was created'],
        #     [14,   'moteDelete',            'A mote was deleted'],
        # ],
        RC : [
            [ 0,   'RC_OK',                 'The application layer has processed the command correctly'],
            [ 1,   'RC_INVALID_COMMAND',    'Invalid command'],
            [ 2,   'RC_INVALID_ARGUMENT',   'Invalid argument'],
            [11,   'RC_END_OF_LIST',        'End of list is returned when an iteration reaches the end of the list of objects'],
            [12,   'RC_NO_RESOURCES',       'Reached maximum number of items'],
            [13,   'RC_IN_PROGRESS',        'Operation is in progress'],
            [14,   'RC_NACK',               'Negative acknowledgment'],
            [15,   'RC_WRITE_FAIL',         'Flash write failed'],
            [16,   'RC_VALIDATION_ERROR',   'Parameter validation error'],
            [17,   'RC_INV_STATE',          'Object has inappropriate state'],
            [18,   'RC_NOT_FOUND',          'Object is not found'],
            [19,   'RC_UNSUPPORTED',        'The operation is not supported'],
        ],
        'frameProfile' : [
            [ 1,   'Profile_01',            'Fast network build, medium speed network operation'],
        ],
        'advertisementState' : [
            [ 0,   'on',                    'Advertisement is on'],
            [ 1,   'off',                   'Advertisement is off or slow*'],
        ],
        'downstreamFrameMode' : [
            [ 0,   'normal',                'Normal downstream bandwidth'],
            [ 1,   'fast',                  'Fast downstream bandwidth'],
        ],
        'networkState' : [
            [ 0,   'operational',           'Network is operating normally'],
            [ 1,   'radiotest',             'Manager is in radiotest mode'],
            [ 2,   'notStarted',            'Waiting for startNetwork API command'],
            [ 3,   'errorStartup',          'Unexpected error occurred at startup'],
            [ 4,   'errorConfig',           'Invalid or not licensed configuration found at startup'],
            [ 5,   'errorLicense',          'Invalid license file found at startup'],
        ],
        'moteState' : [
            [ 0,   'lost',                  'Mote is not currently part of the network'],
            [ 1,   'negotiating',           'Mote is in the process of joining the network'],
            [ 4,   'operational',           'Mote is operational'],
        ],
        'resetType' : [
            [ 0,   'resetSystem',           'Reset the system'],
            [ 2,   'resetMote',             'Reset the mote'],
        ],
        'backboneFrameMode' : [
            [ 0,   'off',                   'Backbone frame is off'],
            [ 1,   'upstream',              'Backbone frame is activated for upstream frames'],
            [ 2,   'bidirectional',         'Backbone frame is activated for both upstream and downstream frames'],
        ],
        'pathFilter' : [
            [ 0,   'all',                   'All paths'],
            [ 1,   'upstream',              'Upstream paths'],
        ],
        'pathDirection' : [
            [ 0,   'none',                  'No path'],
            [ 1,   'unused',                'Path is not used'],
            [ 2,   'upstream',              'Upstream path'],
            [ 3,   'downstream',            'Downstream path'],
        ],
        'packetPriority': [
            [0,    'Low',                   'Default packet priority'],
            [1,    'Medium',                'Higher packet priority'],
            [2,    'High',                  'Highest packet priority'],
        ],
        'commandFinishedResult': [
            [0,    'OK',                    'Command completed successfully'],
            [1,    'nack',                  'Command not acknowledged'],
            [2,    'commandTimeout',        'Command timed out'],
        ],
        'ccaMode': [
            [0,    'off',                   'CCA disabled'],
            [1,    'energy',                'Energy detect'],
            [2,    'carrier',               'Carrier detect'],
            [3,    'both',                  'Energy detect and Carrier detect'],
        ],
        'radiotestType': [
            [0,    'packet',                'Transmit packets'],
            [1,    'cm',                    'Continuous modulation'],
            [2,    'cw',                    'Continuous wave'],
            [3,    'pkcca',                 'Packet test with clear channel assessment (CCA) enabled'],
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
        'joinFailedReason': [
            [0,    'counter',               'The join packet reused an already used join counter'],
            [1,    'notOnACL',               'The mote is not listed on the ACL'],
            [2,    'authentication',        'The join request could not be decrypted. Generally, this means the request was encrypted with a join key that did not match the key in the ACL.'],
            [3,    'unexpected',            'An unexpected error occurred while processing the join request'],
        ],
        
        
        #==================== misc ============================================
        'successCode' : [
            [ 0,   'success',               ''],
            [ 1,   'unsupported_version',   ''],
            [ 2,   'invalid_mode',          ''],
        ],
        'mode' : [
            [ 0,   'legacy',                ''],
        ],
        'userRole' : [
            [ 0,   'viewer',                'Viewer-role user has read-only access to non-sensitive network information'],
            [ 1,   'user',                  'User-role user has read-write privileges'],
        ],
        'protocolVersion' : 4,
    }
    
    # We redefine this attribute inherited from ApiDefinition. See
    # ApiDefinition for a full description of the structure of this field.
    commands = [
        # command 'hello' (commandID 1) is handled by the Hdlc module
        # command 'hello_response' (commandID 2) is handled by the Hdlc module
        {
            'id'         :  1,
            'name'       :  'mux_hello',
            'description':  'Sent by the manager to initiate a new session with a client.',
            'request'    : [
                ['version',                 INT,      1,   None],
                ['secret',                  HEXDATA,  8,   None],
            ],
            'response'   : {
                'FIELDS':  [
                    [RC,                    INT,      1,   True],
                    ['version',             INT,      1,   None],
                ],
            },
        },
        {
            'id'         :  1,
            'name'       :  'hello',
            'description':  '',
            'request'    : [
                ['version',                 INT,      1,   None],
                ['cliSeqNo',                INT,      1,   None],
                ['mode',                    INT,      1,   True],
            ],
        },
        {
            'id'         : 2,
            'name'       : 'hello_response',
            'description': '',
            'request'    : [], # there is no request
            'response'   : {
                'FIELDS':  [
                    ['successCode',         INT,      1,   True],
                    ['version',             INT,      1,   None],
                    ['mgrSeqNo',            INT,      1,   None],
                    ['cliSeqNo',            INT,      1,   None],
                    ['mode',                INT,      1,   True],
                ],
            },
        },
        {
            'id'         : 21,
            'name'       : 'reset',
            'description': 'The reset command is used to reset various objects. The command argument is an object type, and if the object is a mote the MAC address must be specified (otherwise that argument is ignored).',
            'request'    : [
                ['type',                    INT,      1,   'resetType'],
                ['macAddress',              HEXDATA,  8,   None],
            ],
            'response'   : {
                'FIELDS':  [
                    [RC,                    INT,      1,   True],
                    ['macAddress',          HEXDATA,  8,   None],
                ],
            },
            'responseCodes': {
               'RC_OK'                 : 'Command successfully completed',
               'RC_NOT_FOUND'          : 'Mote with specified MAC address is not found',
               'RC_INV_STATE'          : 'Mote is not in operational state',
               'RC_NACK'               : 'User commands queue is full (applies to mote reset)',
               'RC_INVALID_ARGUMENT'   : 'Invalid reset type value',
            },
        },
        {
            'id'         : 22,
            'name'       : 'subscribe',
            'description': "The subscribe command indicates that the manager should send the external application the specified notifications. It contains two filter fields:\n\n- filter is a bitmask of flags indicating the types of notifications that the client wants to receive\n- unackFilter allows the client to select which of the notifications selected in filter should be sent acknowledged. If a notification is sent as 'acknowledged', the subsequent notification packets will be queued while waiting for response.\n\nEach subscription request overwrites the previous one. If an application is subscribed to data and then decides he also wants events he should send a subscribe command with both the data and event flags set. To clear all subscriptions, the client should send a subscribe command with the filter set to zero. When a session is initiated between the manager and a client, the subscription filter is initialized to zero.\n\nThe subscribe bitmap uses the values of the notification type enumeration. Some values are unused to provide backwards compatibility with earlier APIs.",
            'request' : [
                ['filter',                  HEXDATA,  4,   None],
                ['unackFilter',             HEXDATA,  4,   None],
            ],
            'response'   : {
                'FIELDS':  [
                    [RC,                    INT,      1,   True],
                ],
            },
            'responseCodes': {
               'RC_OK'                 : 'Command successfully completed',
               'RC_INVALID_ARGUMENT'   : 'Invalid subscription filter value',
            },
        },
        {
            'id'         : 23,
            'name'       : 'getTime',
            'description': 'The getTime command returns the current manager UTC time and current absolute slot number (ASN). The time values returned by this command are delayed by queuing and transfer time over the serial connection. For additional precision, an external application should trigger the networkTime notification using the Time Pin.',
            'request'    : [
            ],
            'response'   : {
                'FIELDS':  [
                    [RC,                    INT,      1,   True],
                    ['uptime',              INT,      4,   None],
                    ['utcSecs',             INT,      8,   None],
                    ['utcUsecs',            INT,      4,   None],
                    ['asn',                 HEXDATA,  5,   None],
                    ['asnOffset',           INT,      2,   None],
                ],
            },
            'responseCodes': {
               'RC_OK'                 : 'Command successfully completed',
            },
        },
        {
            'id'         : 26,
            'name'       : 'setNetworkConfig',
            'description': 'The setNetworkConfig command changes network configuration parameters. The response code indicates whether the changes were successfully applied. This change is persistent.\n\nGenerally, changes to network configuration will take effect when the manager reboots. Exceptions are detailed below:\n\n- Max Motes: The new maxMotes value is used as soon as new motes try to join the network, but motes are not removed from the network if the value is set to a number lower than numMotes.\n- Base Bandwidth: Changing baseBandwidth while the network is running does not reallocate bandwidth to Operational motes.',
            'request'    :  [
                ['networkId',               INT,      2,   None],
                ['apTxPower',               INTS,     1,   None],
                ['frameProfile',            INT,      1,   True],
                ['maxMotes',                INT,      2,   None],
                ['baseBandwidth',           INT,      2,   None],
                ['downFrameMultVal',        INT,      1,   None],
                ['numParents',              INT,      1,   None],
                ['ccaMode',                 INT,      1,   True],
                ['channelList',             INT,      2,   None],
                ['autoStartNetwork',        BOOL,     1,   None],
                ['locMode',                 INT,      1,   None],
                ['bbMode',                  INT,      1,   'backboneFrameMode'],
                ['bbSize',                  INT,      1,   None],
                ['isRadioTest',             INT,      1,   None],
                ['bwMult',                  INT,      2,   None],
                ['oneChannel',              INT,      1,   None],
            ],
            'response'   : {
                'FIELDS':  [
                    [RC,                    INT,      1,   True],
                ],
            },
            'responseCodes': {
               'RC_OK'                 : 'Command successfully completed',
               'RC_INVALID_ARGUMENT'   : 'Validation of the network parameters failed',
               'RC_WRITE_FAIL'         : 'Flash write error, cannot save new settings',
            },
        },
        {
            'id'         : 31,
            'name'       : 'clearStatistics',
            'description': 'The clearStatistics command clears the accumulated network statistics. The command does not clear path quality or mote statistics.',
            'request'    : [
            ],
            'response'   : {
                'FIELDS':  [
                    [RC,                    INT,      1,   True],
                ],
            },
            'responseCodes': {
               'RC_OK'                 : 'Command successfully completed',
            },
        },
        {
            'id'         : 33,
            'name'       : 'exchangeMoteJoinKey',
            'description': 'The exchangeMoteJoinKey command triggers the manager to send a new join key to the specified mote and update the manager\'s ACL entry for the mote. The response contains a callbackId. A commandFinished event notification with this callbackId will be sent when the operation is complete. This change is persistent.',
            'request'    : [
                ['macAddress',              HEXDATA,  8,   None],
                ['key',                     HEXDATA,  16,  None],
            ],
            'response'   : {
                'FIELDS':  [
                    [RC,                    INT,      1,   True],
                    ['callbackId',          INT,      4,   None],
                ],
            },
            'responseCodes': {
               'RC_OK'                 : 'Command successfully completed',
               'RC_NOT_FOUND'          : 'Mote with specified MAC address is not found',
               'RC_INV_STATE'          : 'Mote is not in operational state',
               'RC_NACK'               : 'User commands queue is full',
               'RC_WRITE_FAIL'         : 'Flash write error, can\'t save new settings',
            },
        },
        {
            'id'         : 34,
            'name'       : 'exchangeNetworkId',
            'description': 'The exchangeNetworkId command triggers the manager to distribute a new network ID to all the motes in the network. A callbackId is returned in the response. A commandFinished notification with this callbackId will be sent when the operation is complete. This change is persistent.',
            'request'    : [
                ['id',                      INT,      2,   None],
            ],
            'response'   : {
                'FIELDS':  [
                    [RC,                    INT,      1,   True],
                    ['callbackId',          INT,      4,   None],
                ],
            },
            'responseCodes': {
                'RC_OK'                : 'Command received',
                'RC_IN_PROGRESS'       : 'A command is still pending. Wait until a commandFinished notification is received for the previous command before retrying.',
                'RC_NACK'              : 'User commands queue is full',
                'RC_WRITE_FAIL'        : 'Flash write error; cannot save new settings',
            },
        },
        {
            'id'         : 35,
            'name'       : 'radiotestTx',
            'description': 'The radiotestTx command allows the user to initiate a radio transmission test. It may only be executed if the manager has been booted up in radiotest mode (see setNetworkConfig command). Four types of transmission tests are supported:\n\n- Packet transmission\n- Continuous modulation (CM)\n- Continuous wave, i.e unmodulated signal (CW)\n- Packet transmission with clear channel assessment (CCA) enabled (Available in Manager > 1.3.x)\n\nIn a packet transmission test, the device generates a repeatCnt number of packet sequences. Each sequence consists of up to 10 packets with configurable size and delays. Each packet starts with a PHY preamble (5 bytes), followed by a PHY length field (1 byte), followed by data payload of up to 125 bytes, and finally a 2-byte 802.15.4 CRC at the end. Byte 0 of the payload contains stationId of the sender. Bytes 1 and 2 contain the packet number (in big-endian format) that increments with every packet transmitted. Bytes 3..N contain a counter (from 0..N-2) that increments with every byte inside payload. Transmissions occur on the set of channels defined by chanMask , selected in pseudo-random order.\n\nIn a continuous modulation test, the device generates continuous pseudo-random modulated signal, centered at the specified channel. The test is stopped by resetting the device.\n\nIn a continuous wave test, the device generates an unmodulated tone, centered at the specified channel. The test tone is stopped by resetting the device.\n\nIn a packet transmission with CCA test, the device is configured identically to that in the packet transmission test, however the device does a clear channel assessment before each transmission and aborts that packet if the channel is busy.\n\nThe station ID is a user selectable value. It is used in packet tests so that a receiver (see radiotestRx) can identify packets from this device in cases where there may be multiple tests running in the same radio space. This field is not used for CM or CW tests. (Available in Manager >= 1.3.0) Channel numbering is 0-15, corresponding to IEEE 2.4 GHz channels 11-26.',
            'request'    : [
                ['testType',                INT,      1,   'radiotestType'],
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
               'RC_OK'                 : 'Command successfully completed',
               'RC_IN_PROGRESS'        : 'Radiotest is in progress',
               'RC_INVALID_ARGUMENT'   : 'Invalid "channel" or "txPower" value',
            },
            'serializer' : 'serialize_radiotestTx',
        },
        {
            'id'         : 37,
            'name'       : 'radiotestRx',
            'description': 'The radiotestRx command clears all previously collected statistics and initiates radio reception on the specified channel. It may only be executed if the manager has been booted up in radiotest mode (see setNetworkConfig command). During the test, the device keeps statistics about the number of packets received (with and without error). The test results may be retrieved using the getRadiotestStatistics command.\n\nThe station ID is a user selectable value. It must be set to match the station ID used by the transmitter. Station ID is used to isolate traffic if multiple tests are running in the same radio space.\n\n\n\nChannel numbering is 0-15, corresponding to IEEE 2.4 GHz channels 11-26.',
            'request'    : [
                ['mask',                    HEXDATA,  2,   None],
                ['duration',                INT,      2,   None],
                ['stationId',               INT,      1,   None],
            ],
            'response'   : {
                'FIELDS':  [
                    [RC,                    INT,      1,   True],
                ],
            },
            'responseCodes': {
               'RC_OK'                 : 'Command successfully completed',
               'RC_IN_PROGRESS'        : 'Radiotest is in progress',
               'RC_INVALID_ARGUMENT'   : 'Invalid mask value',
            },
        },
        {
            'id'         : 38,
            'name'       : 'getRadiotestStatistics',
            'description': 'This command retrieves statistics from a previously run radiotestRx command. It may only be executed if the manager has been booted up in radiotest mode (see setNetworkConfig command).',
            'request'    : [
            ],
            'response'   : {
                'FIELDS':  [
                    [RC,                    INT,      1,   True],
                    ['rxOk',                INT,      2,   None],
                    ['rxFail',              INT,      2,   None],
                ],
            },
            'responseCodes': {
               'RC_OK'                 : 'Command successfully completed',
               'RC_IN_PROGRESS'        : 'Radiotest is in progress',
               'RC_INVALID_COMMAND'    : 'No radiotest was started',
            },
        },
        {
            'id'         : 39,
            'name'       : 'setACLEntry',
            'description': 'The setACLEntry command adds a new entry or updates an existing entry in the Access Control List (ACL). This change is persistent. The maximum number of entries is 1,200.',
            'request'    : [
                ['macAddress',              HEXDATA,  8,   None],
                ['joinKey',                 HEXDATA,  16,  None],
            ],
            'response'   : {
                'FIELDS':  [
                    [RC,                    INT,      1,   True],
                ],
            },
            'responseCodes': {
               'RC_OK'                 : 'Command successfully completed',
               'RC_NO_RESOURCES'       : 'ACL is full (when adding a new entry)',
               'RC_WRITE_FAIL'         : 'Flash write error, can\'t save new settings',
            },
        },
        {
            'id'         : 40,
            'name'       : 'getNextACLEntry',
            'description': 'The getNextACLEntry command returns information about next mote entry in the access control list (ACL). To begin a search (find the first mote in ACL), a zero MAC address (0000000000000000) should be sent. There is no mechanism for reading the ACL entry of a specific mote. This call is an iterator. If you call getNextACLEntry with mote A as the argument, your response is the ACL entry for mote B, where B is the next mote in the ACL.',
            'request'    : [
                ['macAddress',              HEXDATA,  8,   None],
            ],
            'response'   : {
                'FIELDS':  [
                    [RC,                    INT,      1,   True],
                    ['macAddress',          HEXDATA,  8,   None],
                    ['joinKey',             HEXDATA,  16,  None],
                ],
            },
            'responseCodes': {
               'RC_OK'                 : 'Command successfully completed',
               'RC_END_OF_LIST'        : 'End of ACL is reached',
               'RC_NOT_FOUND'          : 'No such mote in the ACL',
            },
        },
        {
            'id'         : 41,
            'name'       : 'deleteACLEntry',
            'description': 'The deleteACLEntry command deletes the specified mote from the access control list (ACL). If the macAddress parameter is set to all 0xFFs or all 0x00s, the entire ACL is cleared. This change is persistent.',
            'request'    : [
                ['macAddress',              HEXDATA,  8,   None],
            ],
            'response'   : {
                'FIELDS':  [
                    [RC,                    INT,      1,   True],
                ],
            },
            'responseCodes': {
               'RC_OK'                 : 'Command successfully completed',
               'RC_NOT_FOUND'          : 'Specified mote is not found in ACL',
               'RC_WRITE_FAIL'         : 'Flash write error, can\'t save new settings',
            },
        },
        {
            'id'         : 42,
            'name'       : 'pingMote',
            'description': 'The pingMote command sends a ping (echo request) to the mote specified by MAC address. A unique callbackId is generated and returned with the response. When the response is received from the mote, the manager generates a pingResponse notification with the measured round trip delay and several other parameters. The request is sent using unacknowledged transport, so the mote is not guaranteed to receive the request.',
            'request'    : [
                ['macAddress',              HEXDATA,  8,   None],
            ],
            'response'   : {
                'FIELDS':  [
                    [RC,                    INT,      1,   True],
                    ['callbackId',          INT,      4,   None],
                ],
            },
            'responseCodes': {
               'RC_OK'                 : 'Command successfully completed',
               'RC_NOT_FOUND'          : 'Specified mote not found',
               'RC_INV_STATE'          : 'Mote is not in operational state',
               'RC_NO_RESOURCES'       : 'User commands queue is full',
               'RC_IN_PROGRESS'        : 'Previous echo request command is still pending for specified mote',
            },
        },
        {
            'id'         : 43,
            'name'       : 'getLog',
            'description': 'The getLog command retrieves diagnostic logs from the manager or a mote specified by MAC address.',
            'request'    : [
                ['macAddress',              HEXDATA,  8,   None],
            ],
            'response'   : {
                'FIELDS':  [
                    [RC,                    INT,      1,   True],
                ],
            },
            'responseCodes': {
               'RC_OK'                 : 'Command successfully completed',
               'RC_NOT_FOUND'          : 'Specified mote not found',
               'RC_INV_STATE'          : 'Mote is not in operational state',
            },
        },
        {
            'id'         : 44,
            'name'       : 'sendData',
            'description': "The sendData command sends a packet to a mote in the network. The response contains a callbackId. When the manager injects the packet into the network, it will generate a packetSent notification. It is the responsibility of the customer's application layer at the mote to send a response. It is also the responsibility of the customer's application layer to timeout if no response is received at the manager if one is expected.\n\nThe sendData command should be used by applications that communicate directly with the manager. If end-to-end (application to mote) IP connectivity is required, the application should use the sendIP command. For a more comprehensive discussion of the distinction, see the SmartMesh IP Network User Guide.",
            'request'    : [
                ['macAddress',              HEXDATA,  8,   None],
                ['priority',                INT,      1,   'packetPriority'],
                ['srcPort',                 INT,      2,   None],
                ['dstPort',                 INT,      2,   None],
                ['options',                 INT,      1,   None],
                ['data',                    HEXDATA,  None,None],
            ],
            'response'   : {
                'FIELDS':  [
                    [RC,                    INT,      1,   True],
                    ['callbackId',          INT,      4,   None],
                ],
            },
            'responseCodes': {
               'RC_OK'                 : 'Command successfully completed',
               'RC_NOT_FOUND'          : 'Specified mote is not found',
               'RC_INV_STATE'          : 'Mote is not in operational state',
               'RC_NACK'               : 'User commands queue is full or couldn\'t allocate memory buffer for payload',
               'RC_INVALID_ARGUMENT'   : 'Payload size exceeds maximum allowed value',
            },
        },
        {
            'id'         : 45,
            'name'       : 'startNetwork',
            'description': 'The startNetwork command tells the manager to allow the network to start forming (begin accepting join requests from devices). The external application must issue the startNetwork command if the autoStartNetwork flag is not set (see setNetworkConfig).\n\nThis command has been deprecated and should not be used in new designs.',
            'request'    : [
            ],
            'response'   : {
                'FIELDS':  [
                    [RC,                    INT,      1,   True],
                ],
            },
            'responseCodes': {
               'RC_OK'                 : 'Command successfully completed',
               'RC_IN_PROGRESS'        : 'The network is already started',
            },
        },
        {
            'id'         : 46,
            'name'       : 'getSystemInfo',
            'description': 'The getSystemInfo command returns system-level information about the hardware and software versions.',
            'request'    : [
            ],
            'response'   : {
                'FIELDS':  [
                    [RC,                    INT,      1,   True],
                    ['macAddress',          HEXDATA,  8,   None],
                    ['hwModel',             INT,      1,   None],
                    ['hwRev',               INT,      1,   None],
                    ['swMajor',             INT,      1,   None],
                    ['swMinor',             INT,      1,   None],
                    ['swPatch',             INT,      1,   None],
                    ['swBuild',             INT,      2,   None],
                ],
            },
            'responseCodes': {
               'RC_OK'                 : 'Command successfully completed',
            },
        },
        {
            'id'         : 47,
            'name'       : 'getMoteConfig',
            'description': 'The getMoteConfig command returns a single mote description as the response. The command takes two arguments, a MAC Address and a flag indicating whether the MAC Address refers to the requested mote or to the next mote in managers memory. This command may be used to iterate through all motes known by the manager by starting with the macAddress parameter set to 0 and next set to true, and then using the MAC Address of that response as the input to the next call.\n\nThe mote MAC address is used in all query commands, but space constraints require the neighbor health reports to use the Mote ID for identification. Therefore, both identifiers are present in the mote structure.',
            'request'    : [
                ['macAddress',              HEXDATA,  8,   None],
                ['next',                    BOOL,     1,   None],
            ],
            'response'   : {
                'FIELDS':  [
                    [RC,                    INT,      1,   True],
                    ['macAddress',          HEXDATA,  8,   None],
                    ['moteId',              INT,      2,   None],
                    ['isAP',                BOOL,     1,   None],
                    ['state',               INT,      1,   'moteState'],
                    ['reserved',            INT,      1,   None],
                    ['isRouting',           BOOL,     1,   None],
                ],
            },
            'responseCodes': {
               'RC_OK'                 : 'Command successfully completed',
               'RC_NOT_FOUND'          : 'The specified mote doesn\'t exist',
               'RC_END_OF_LIST'        : 'Last mote in the list has been reached (next = true)',
            },
        },
        {
            'id'         : 48,
            'name'       : 'getPathInfo',
            'description': 'The getPathInfo command returns parameters of requested path.',
            'request'    : [
                ['source',                  HEXDATA,  8,   None],
                ['dest',                    HEXDATA,  8,   None],
            ],
            'response'   : {
                'FIELDS':  [
                    [RC,                    INT,      1,   True],
                    ['source',              HEXDATA,  8,   None],
                    ['dest',                HEXDATA,  8,   None],
                    ['direction',           INT,      1,   'pathDirection'],
                    ['numLinks',            INT,      1,   None],
                    ['quality',             INT,      1,   None],
                    ['rssiSrcDest',         INTS,     1,   None],
                    ['rssiDestSrc',         INTS,     1,   None],
                ],
            },
            'responseCodes': {
               'RC_OK'                 : 'Command successfully completed',
               'RC_NOT_FOUND'          : 'A path between the specified motes doesn\'t exist',
            },
        },
        {
            'id'         : 49,
            'name'       : 'getNextPathInfo',
            'description': 'The getNextPathInfo command allows iteration across paths connected to a particular mote. The pathId parameter indicates the previous value in the iteration. Setting pathId to 0 returns the first path. A pathId can not be used as a unique identifier for a path. It is only valid when associated with a particular mote.',
            'request'    : [
                ['macAddress',              HEXDATA,  8,   None],
                ['filter',                  INT,      1,   'pathFilter'],
                ['pathId',                  INT,      2,   None],
            ],
            'response'   : {
                'FIELDS':  [
                    [RC,                    INT,      1,   True],
                    ['pathId',              INT,      2,   None],
                    ['source',              HEXDATA,  8,   None],
                    ['dest',                HEXDATA,  8,   None],
                    ['direction',           INT,      1,   'pathDirection'],
                    ['numLinks',            INT,      1,   None],
                    ['quality',             INT,      1,   None],
                    ['rssiSrcDest',         INTS,     1,   None],
                    ['rssiDestSrc',         INTS,     1,   None],
                ],
            },
            'responseCodes': {
               'RC_OK'                 : 'Command successfully completed',
               'RC_NOT_FOUND'          : 'The specified path ID does not exist',
               'RC_END_OF_LIST'        : 'The specified pathId in the request is the end of the list',
            },
        },
        {
            'id'         : 50,
            'name'       : 'setAdvertising',
            'description': '''The setAdvertising command tells the manager to activate, deactivate, or use slow advertising. The response is a callbackId. A commandFinished notification with the callbackId is generated when the command propagation is complete.

With motes prior to version 1.4.1, it is only possible to turn advertising ON or OFF. If building networks consisting primarily of motes 1.4.1 or later, power can be saved by setting advertising to "slow". Set the INI parameter advtimeout to a value (in ms) and set this command to 0.

For example, the default full advertising frequency is approximately once per 2 seconds. It is recommended to set advtimeout = 20000, which will result in an advertising every 20 seconds which will result in a 90% power savings in the cost of advertising.

It is dangerous to turn off advertising in the network. When advertising is off, new motes can not join and existing motes can not rejoin the network after a reset. Turning off advertising is primarily used to save power, or may be useful in for specific use cases where it is desirable to prevent motes from joining the network. In most cases, it is best to allow advertising to remain under the control of the manager.''',
            'request'    : [
                ['activate',                INT,      1,   'advertisementState'],
            ],
            'response'   : {
                'FIELDS':  [
                    [RC,                    INT,      1,   True],
                    ['callbackId',          INT,      4,   None],
                ],
            },
            'responseCodes': {
                'RC_OK'                : 'Command successfully completed',
                'RC_IN_PROGRESS'       : 'A command is still pending. Wait until a commandFinished notification is received for the previous command before retrying.',
            },
        },
        {
            'id'         : 51,
            'name'       : 'setDownstreamFrameMode',
            'description': 'The setDownstreamFrameMode command tells the manager to shorten or extend the downstream slotframe. The base slotframe length will be multiplied by the downFrameMultVal for "normal" speed. For "fast" speed the downstream slotframe is the base length. Once this command is executed, the manager switches to manual mode and no longer changes slotframe size automatically. The response is a callbackId. A commandFinished notification with the callbackId is generated when the command propagation is complete.',
            'request'    : [
                ['frameMode',               INT,      1,   'downstreamFrameMode'],
            ],
            'response'   : {
                'FIELDS':  [
                    [RC,                    INT,      1,   True],
                    ['callbackId',          INT,      4,   None],
                ],
            },
            'responseCodes': {
               'RC_OK'                 : 'Command successfully completed',
               'RC_IN_PROGRESS'        : 'A command is still pending. Wait until a commandFinished notification is received for the previous command before retrying.',
               'RC_INVALID_ARGUMENT'   : 'The downFrameMultVal (as set by setNetworkConfig) is equal to 1, so changing the downstream frame mode would have no effect.',
            },
        },
        {
            'id'         : 53,
            'name'       : 'getManagerStatistics',
            'description': 'The getManagerStatistics command returns dynamic information and statistics about the manager API. The statistics counts are cleared together with all current statistics using clearStatistics.',
            'request'    : [
            ],
            'response'   : {
                'FIELDS':  [
                    [RC,                    INT,      1,   True],
                    ['serTxCnt',            INT,      2,   None],
                    ['serRxCnt',            INT,      2,   None],
                    ['serRxCRCErr',         INT,      2,   None],
                    ['serRxOverruns',       INT,      2,   None],
                    ['apiEstabConn',        INT,      2,   None],
                    ['apiDroppedConn',      INT,      2,   None],
                    ['apiTxOk',             INT,      2,   None],
                    ['apiTxErr',            INT,      2,   None],
                    ['apiTxFail',           INT,      2,   None],
                    ['apiRxOk',             INT,      2,   None],
                    ['apiRxProtErr',        INT,      2,   None],
                ],
            },
            'responseCodes': {
               'RC_OK'                 : 'Command successfully completed',
            },
        },
        {
            'id'         : 54,
            'name'       : 'setTime',
            'description': 'This command has been deprecated, and should not be used in new designs. When the Manager restarts, it will start counting from 20:00:00 UTC July 2, 2002.\n\nThe setTime command sets the UTC time on the manager. This command may only be executed when the network is not running. If the trigger flag is false, the manager sets the specified time as soon as it receives the setTime command. When the manager receives a Time Pin trigger, it temporarily stores the current time. If a setTime request is received within a short period of time following the trigger, the manager calculates the delay since the trigger and adjust the time such that the trigger was received at the specified time value.',
            'request'    : [
                ['trigger',                 INT,      1,   None],
                ['utcSecs',                 INT,      8,   None],
                ['utcUsecs',                INT,      4,   None],
            ],
            'response'   : {
                'FIELDS':  [
                    [RC,                    INT,      1,   True],
                ],
            },
            'responseCodes': {
               'RC_OK'                 : 'Command successfully completed. The manager is ready to set the time.',
               'RC_INVALID_ARGUMENT'   : 'One of the parameters was invalid',
               'RC_VALIDATION_ERROR'   : 'Network is running, setTime command is disabled.',
            },
        },
        {
            'id'         : 55,
            'name'       : 'getLicense',
            'description': 'The getLicense command has been deprecated in Manager >= 1.3.0.There is no need to use a license to enable > 32 mote networks.\n\nThe getLicense command returns the current license key.',
            'request'    : [
            ],
            'response'   : {
                'FIELDS':  [
                    [RC,                    INT,      1,   True],
                    ['license',             HEXDATA,  13,  None],
                ],
            },
            'responseCodes': {
               'RC_OK'                 : 'Command successfully completed',
            },
        },
        {
            'id'         : 56,
            'name'       : 'setLicense',
            'description': 'The setLicense command has been deprecated in Manager >= 1.3.0. There is no longer a need to use a license to enable > 32 mote networks.\n\nThe setLicense command validates and updates the software license key stored in flash. Features enabled or disabled by the license key change will take effect after the device is restarted. If the license parameter is set to all 0x0s, the manager restores the default license. This change is persistent.',
            'request'    : [
                ['license',                 HEXDATA,  13,  None],
            ],
            'response'   : {
                'FIELDS':  [
                    [RC,                    INT,      1,   True],
                ],
            },
            'responseCodes': {
               'RC_OK'                 : 'Command successfully completed',
               'RC_VALIDATION_ERROR'   : 'The license key is not valid',
               'RC_WRITE_FAIL'         : 'Flash write error, cannot save new settings',
            },
        },
        {
            'id'         : 58,
            'name'       : 'setCLIUser',
            'description': 'The setCLIUser command sets the password that must be used to log into the command line for a particular user role. The user roles are:\n\n- Viewer - read-only access to non-sensitive information\n- User - read-write access This change is persistent.',
            'request'    : [
                ['role',                    INT,      1,   'userRole'],
                ['password',                HEXDATA,  16,  None],
            ],
            'response'   : {
                'FIELDS':  [
                    [RC,                    INT,      1,   True],
                ],
            },
            'responseCodes': {
               'RC_OK'                 : 'Command successfully completed',
               'RC_WRITE_FAIL'         : 'Flash write error, can\'t save new settings',
            },
        },
        {
            'id'         : 59,
            'name'       : 'sendIP',
            'description': 'The sendIP command sends a 6LoWPAN packet to a mote in the network. The response contains a callback Id. When the manager injects the packet into the network, it will generate a packetSent notification with the calllbackId. The application is responsible for constructing a valid 6LoWPAN packet. The packet is sent to the mote best-effort, so the application should deal with responses and timeouts, if any.\n\nThe sendIP command should be used by applications that require end-to-end IP connectivity. For applications that do not require end-to-end IP connectivity, the sendData command provides a simpler interface without requiring the application to understand 6LoWPAN encapsulation. For a more comprehensive discussion of the distinction, see the SmartMesh IP Network User Guide.',
            'request'    : [
                ['macAddress',              HEXDATA,  8,   None],
                ['priority',                INT,      1,   'packetPriority'],
                ['options',                 INT,      1,   None],
                ['encryptedOffset',         INT,      1,   None],
                ['data',                    HEXDATA,  None,None],
            ],
            'response'   : {
                'FIELDS':  [
                    [RC,                    INT,      1,   True],
                    ['callbackId',          INT,      4,   None],
                ],
            },
            'responseCodes': {
               'RC_OK'                 : 'Command successfully completed',
               'RC_NOT_FOUND'          : 'Specified mote is not found',
               'RC_INV_STATE'          : 'Mote is not in operational state',
               'RC_NACK'               : 'User commands queue is full or could not allocate memory buffer for payload',
               'RC_INVALID_ARGUMENT'   : 'Payload size exceeds maximum allowed value or the 6LoWPAN packet is invalid',
            },
        },
        {
            'id'         : 61,
            'name'       : 'restoreFactoryDefaults',
            'description': 'The restoreFactoryDefaults command restores the default configuration and clears the ACL. This change is persistent.\n\nFor Manager versions <1.3.0 that required a license, the license used to enable optional features is preserved during a restore.',
            'request'    : [
            ],
            'response'   : {
                'FIELDS':  [
                    [RC,                    INT,      1,   True],
                ],
            },
            'responseCodes': {
               'RC_OK'                 : 'Command successfully completed',
               'RC_WRITE_FAIL'         : 'Flash write error; cannot save new settings',
            },
        },
        {
            'id'         : 62,
            'name'       : 'getMoteInfo',
            'description': 'The getMoteInfo command returns dynamic information for the specified mote.',
            'request'    : [
                ['macAddress',              HEXDATA,  8,   None],
            ],
            'response'   : {
                'FIELDS':  [
                    [RC,                    INT,      1,   True],
                    ['macAddress',          HEXDATA,  8,   None],
                    ['state',               INT,      1,   'moteState'],
                    ['numNbrs',             INT,      1,   None],
                    ['numGoodNbrs',         INT,      1,   None],
                    ['requestedBw',         INT,      4,   None],
                    ['totalNeededBw',       INT,      4,   None],
                    ['assignedBw',          INT,      4,   None],
                    ['packetsReceived',     INT,      4,   None],
                    ['packetsLost',         INT,      4,   None],
                    ['avgLatency',          INT,      4,   None],
                    ['stateTime',           INT,      4,   None],
                    ['numJoins',            INT,      1,   None],
                    ['hopDepth',            INT,      1,   None],
                ],
            },
            'responseCodes': {
               'RC_OK'                 : 'Command successfully completed',
               'RC_NOT_FOUND'          : 'No such mote',
            },
        },
        {
            'id'         : 63,
            'name'       : 'getNetworkConfig',
            'description': 'The getNetworkConfig command returns general network configuration parameters, including the Network ID, bandwidth parameters and number of motes.',
            'request'    : [
            ],
            'response'   : {
                'FIELDS':  [
                    [RC,                    INT,      1,   True],
                    ['networkId',           INT,      2,   None],
                    ['apTxPower',           INTS,     1,   None],
                    ['frameProfile',        INT,      1,   True],
                    ['maxMotes',            INT,      2,   None],
                    ['baseBandwidth',       INT,      2,   None],
                    ['downFrameMultVal',    INT,      1,   None],
                    ['numParents',          INT,      1,   None],
                    ['ccaMode',             INT,      1,   True],
                    ['channelList',         INT,      2,   None],
                    ['autoStartNetwork',    BOOL,     1,   None],
                    ['locMode',             INT,      1,   None],
                    ['bbMode',              INT,      1,   'backboneFrameMode'],
                    ['bbSize',              INT,      1,   None],
                    ['isRadioTest',         INT,      1,   None],
                    ['bwMult',              INT,      2,   None],
                    ['oneChannel',          INT,      1,   None],
                ],
            },
            'responseCodes': {
               'RC_OK'                 : 'Command successfully completed',
            },
        },
        {
            'id'         : 64,
            'name'       : 'getNetworkInfo',
            'description': 'The getNetworkInfo command returns dynamic network information and statistics.',
            'request'    : [
            ],
            'response'   : {
                'FIELDS':  [
                    [RC,                    INT,      1,   True],
                    ['numMotes',            INT,      2,   None],
                    ['asnSize',             INT,      2,   None],
                    ['advertisementState',  INT,      1,   True],
                    ['downFrameState',      INT,      1,   'downstreamFrameMode'],
                    ['netReliability',      INT,      1,   None],
                    ['netPathStability',    INT,      1,   None],
                    ['netLatency',          INT,      4,   None],
                    ['netState',            INT,      1,   'networkState'],
                    ['ipv6Address',         HEXDATA,  16,  None],
                    ['numLostPackets',      INT,      4,   None],
                    ['numArrivedPackets',   INT,      8,   None],
                    ['maxNumbHops',         INT,      1,   None],
                ],
            },
            'responseCodes': {
               'RC_OK'                 : 'Command successfully completed',
            },
        },
        {
            'id'         : 65,
            'name'       : 'getMoteConfigById',
            'description': 'The getMoteConfigById command returns a single mote description as the response. The command takes one argument, the short address of a mote (Mote ID). The command returns the same response structure as the getMoteConfig command.',
            'request'    : [
                    ['moteId',              INT,      2,   None],
            ],
            'response'   : {
                'FIELDS':  [
                    [RC,                    INT,      1,   True],
                    ['macAddress',          HEXDATA,  8,   None],
                    ['moteId',              INT,      2,   None],
                    ['isAP',                BOOL,     1,   None],
                    ['state',               INT,      1,   'moteState'],
                    ['reserved',            INT,      1,   None],
                    ['isRouting',           BOOL,     1,   None],
                ],
            },
            'responseCodes': {
               'RC_OK'                 : 'Command successfully completed',
               'RC_NOT_FOUND'          : 'No such mote',
            },
        },
        {
            'id'         : 66,
            'name'       : 'setCommonJoinKey',
            'description': 'The setCommonJoinKey command will set a new value for the common join key. The common join key is used to decrypt join messages only if the ACL is empty.',
            'request'    : [
                ['key',                     HEXDATA,  16,  None],
            ],
            'response'   : {
                'FIELDS':  [
                    [RC,                    INT,      1,   True],
                ],
            },
            'responseCodes': {
               'RC_OK'                 : 'Command successfully completed',
            },
        },
        {
            'id'         : 67,
            'name'       : 'getIPConfig',
            'description': 'The getIPConfig command returns the manager\'s IP configuration parameters, including the IPv6 address and mask.',
            'request'    : [
            ],
            'response'   : {
                'FIELDS':  [
                    [RC,                    INT,      1,   True],
                    ['ipv6Address',         HEXDATA,  16,  None],
                    ['mask',                HEXDATA,  16,  None],
                ],
            },
            'responseCodes': {
               'RC_OK'                 : 'Command successfully completed',
            },
        },
        {
            'id'         : 68,
            'name'       : 'setIPConfig',
            'description': 'The setIPConfig command sets the IPv6 prefix of the mesh network. Only the upper 8 bytes of the IPv6 address are relevant: the lower 8 bytes of the IPv6 address are ignored, and lower 8 bytes of the mask field are reserved and should be set to 0. This change is persistent.',
            'request'    : [
                ['ipv6Address',             HEXDATA,  16,  None],
                ['mask',                    HEXDATA,  16,  None],
            ],
            'response'   : {
                'FIELDS':  [
                    [RC,                    INT,      1,   True],
                ],
            },
            'responseCodes': {
               'RC_OK'                 : 'Command successfully completed',
               'RC_WRITE_FAIL'         : 'Flash write error, can\'t save new settings',
            },
        },
        {
            'id'         : 69,
            'name'       : 'deleteMote',
            'description': 'The deleteMote command deletes a mote from the manager\'s list. A mote can only be deleted if it is in the Lost state.',
            'request'    : [
                ['macAddress',              HEXDATA,  8,   None],
            ],
            'response'   : {
                'FIELDS':  [
                    [RC,                    INT,      1,   True],
                ],
            },
            'responseCodes': {
               'RC_OK'                 : 'Command successfully completed',
               'RC_NOT_FOUND'          : 'Specified mote is not found',
               'RC_INV_STATE'          : 'Mote state is not Lost or mote is access point',
               'RC_WRITE_FAIL'         : 'Flash write error, can\'t save new settings',
            },
        },
        {
            'id'         : 70,
            'name'       : 'getMoteLinks',
            'description': 'The getMoteLinks command returns information about links assigned to the mote. The response contains a list of links starting with Nth link on the mote, where N is supplied as the idx parameter in the request. To retrieve all links on the device the user can call this command with idx that increments by number of links returned with prior response, until the command returns RC_END_OF_LIST response code. Note that links assigned to a mote may change between API calls.',
            'request'    : [
                ['macAddress',              HEXDATA,  8,   None],
                ['idx',                     INT,      2,   None],
            ],
            'response'   : {
                'FIELDS':  [
                    [RC,                    INT,      1,   True],
                    ['idx',                 INT,      2,   None],
                    ['utilization',         INT,      1,   None],
                    ['numLinks',            INT,      1,   None],
                    ['links',               ARRAY,    10,
                        [
                            ['frameId',         INT,      1,   None],
                            ['slot',            INT,      4,   None],
                            ['channelOffset',   INT,      1,   None],
                            ['moteId',          INT,      2,   None],
                            ['flags',           INT,      1,   None],
                        ]
                    ],
                ],
            },
            'responseCodes': {
               'RC_NOT_FOUND'          : 'No such mote.',
               'RC_INV_STATE'          : 'Mote is not in operational state',
               'RC_END_OF_LIST'        : 'The index requested is greater than number of links.',
            },
        },
        {
            'id'         : 74,
            'name'       : 'radiotestRxPER',
            'description': 'The radiotestRxPER command initiates the Packet Error Rate (PER) test in RX mode. This command may be issued only if the manager has been booted up in radiotest mode (see setNetworkConfig command).\n\nThis command is available in the SmartMesh IP Manager version 1.4.2 or later.',
            'request'    : [
            ],
            'response'   : {
                'FIELDS':  [
                    [RC,                    INT,      1,   True],
                ],
            },
            'responseCodes': {
               'RC_OK'             : 'Command was accepted',
               'RC_IN_PROGRESS'  : 'The mote is in invalid state to start PER test',
            },
        },
        {
            'id'         : 75,
            'name'       : 'radiotestTxPER',
            'description': 'The radiotestTxPER command initiates the Packet Error Rate (PER) test in TX mode. This command may be issued only if the manager has been booted up in radiotest mode (see setNetworkConfig command).\nChannel numbering is 0-15, corresponding to IEEE 2.4 GHz channels 11-26.\n\nThis command is available in the SmartMesh IP Manager version 1.4.2 or later.',
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
               'RC_OK'             : 'Command was accepted',
               'RC_IN_PROGRESS'  : 'The mote is in invalid state to start PER test',
            },
        },
    ]
    
    subCommandsEvents = [
        {
            'id'         : 0,
            'name'       : 'eventMoteReset',
            'description': 'This notification is sent when a user-initiated reset is executed by the manager.',
            'response'   : {
                'FIELDS':  [
                    ['macAddress',         HEXDATA,  8,   None],
                ],
            },
        },
        {
            'id'         : 1,
            'name'       : 'eventNetworkReset',
            'description': 'This notification is sent when the manager starts the network. This event has no eventData fields.',
            'response'   : {
                'FIELDS':  [
                ],
            },
        },
        {
            'id'         : 2,
            'name'       : 'eventCommandFinished',
            'description': 'The commandFinished notification is sent when a command associated with the provided callback id finishes executing.',
            'response'   : {
                'FIELDS':  [
                    ['callbackId',          HEXDATA,  4,   None],
                    ['rc',                  INT,      1,   'commandFinishedResult'],
                ],
            },
        },
        {
            'id'         : 3,
            'name'       : 'eventMoteJoin',
            'description': 'This notification is sent when a mote joins the network.',
            'response'   : {
                'FIELDS':  [
                    ['macAddress',         HEXDATA,  8,   None],
                ],
            },
        },
        {
            'id'         : 4,
            'name'       : 'eventMoteOperational',
            'description': 'This notification is sent when a mote that joins the network becomes operational.',
            'response'   : {
                'FIELDS':  [
                    ['macAddress',         HEXDATA,  8,   None],
                ],
            },
        },
        {
            'id'         : 5,
            'name'       : 'eventMoteLost',
            'description': "This notification is sent when a mote's state changes to Lost , which indicates that the mote is not responding to downstream messages.",
            'response'   : {
                'FIELDS':  [
                    ['macAddress',         HEXDATA,  8,   None],
                ],
            },
        },
        {
            'id'         : 6,
            'name'       : 'eventNetworkTime',
            'description': 'The time notification is triggered by the client asserting the TIME pin or by calling the getTime command. This notification contains the time when the TIME pin was asserted (or the getTime command was processed) expressed as:\n\n- ASN The absolute slot number (the number of timeslots since " 7/2/2002 8:00:00 PM PST" if UTC is set on manager, otherwise since Jan 1, 1970)\n\n\n- Uptime The number of seconds since the device was booted\n- Unix time The number of seconds and microseconds since Jan 1, 1970 in UTC',
            'response'   : {
                'FIELDS':  [
                    ['uptime',             INT,      4,   None],
                    ['utcSecs',            INT,      8,   None],
                    ['utcUsecs',           INT,      4,   None],
                    ['asn',                HEXDATA,  5,   None],
                    ['asnOffset',          INT,      2,   None],
                ],
            },
        },
        {
            'id'         : 7,
            'name'       : 'eventPingResponse',
            'description': 'This notification is sent when a reply is received from a mote ping.',
            'response'   : {
                'FIELDS':  [
                    ['callbackId',         INT,      4,   None],
                    ['macAddress',         HEXDATA,  8,   None],
                    ['delay',              INT,      4,   None],
                    ['voltage',            INT,      2,   None],
                    ['temperature',        INTS,     1,   None],
                ],
            },
        },
        {
            'id'         : 10,
            'name'       : 'eventPathCreate',
            'description': 'This notification is sent when the manager creates a connection (path) between two motes.',
            'response'   : {
                'FIELDS':  [
                    ['source',             HEXDATA,  8,   None],
                    ['dest',               HEXDATA,  8,   None],
                    ['direction',          INT,      1,   'pathDirection'],
                ],
            },
        },
        {
            'id'         : 11,
            'name'       : 'eventPathDelete',
            'description': 'This notification is sent when the manager removes a connection (path) between two motes.',
            'response'   : {
                'FIELDS':  [
                    ['source',             HEXDATA,  8,   None],
                    ['dest',               HEXDATA,  8,   None],
                    ['direction',          INT,      1,   'pathDirection'],
                ],
            },
        },
        {
            'id'         : 12,
            'name'       : 'eventPacketSent',
            'description': 'The packetSent notification is generated when client\'s packet is removed from manager\'s queue and sent into the wireless network.',
            'response'   : {
                'FIELDS':  [
                    ['callbackId',         INT,      4,   None],
                    ['rc',                 INT,      1,   None],
                ],
            },
        },
        {
            'id'         : 13,
            'name'       : 'eventMoteCreate',
            'description': 'This event is sent when a mote joins the manager for the first time.',
            'response'   : {
                'FIELDS':  [
                    ['macAddress',        HEXDATA,  8,   None],
                    ['moteId',             INT,      2,   None],
                ],
            },
        },
        {
            'id'         : 14,
            'name'       : 'eventMoteDelete',
            'description': 'This notification is sent when a mote is deleted as a result of moteDelete command.',
            'response'   : {
                'FIELDS':  [
                    ['macAddress',        HEXDATA,  8,   None],
                    ['moteId',             INT,      2,   None],
                ],
            },
        },
        {
            'id'         : 15,
            'name'       : 'eventJoinFailed',
            'description': 'The joinFailed event is generated when a mote sends a join request to the manager but the request can not be validated. This notification is available in Manager 1.4.1 or later.',
            'response'   : {
                'FIELDS':  [
                    ['macAddress',        HEXDATA,  8,   None],
                    ['reason',            INT,      1,   'joinFailedReason'],
                ],
            },
        },
        {
            'id'         : 16,
            'name'       : 'eventInvalidMIC',
            'description': 'The invalidMIC event is generated when a packet that the manager receives from a mote in the network fails decryption. This notification is available in Manager 1.4.1 or later.',
            'response'   : {
                'FIELDS':  [
                    ['macAddress',        HEXDATA,  8,   None],
                ],
            },
        },
    ]
    
    subCommandsNotification = [
        {
            'id'         : 1,
            'name'       : 'notifEvent',
            'description': 'Event notification',
            'response'   : {
                'FIELDS':  [
                    ['eventId',            INT,      4,   None],
                    [SUBID2,               INT,      1,   None],
                ],
            },
            'subCommands': subCommandsEvents,
        },
        {
            'id'         : 2,
            'name'       : 'notifLog',
            'description': 'A log notifications is generated in response to the getLog command. Each log notification contains a message from the mote\'s log.',
            'response'   : {
                'FIELDS':  [
                    ['macAddress',         HEXDATA,  8,   None],
                    ['logMsg',             HEXDATA,  None,None],
                ],
            },
        },
        {
            'id'         : 4,
            'name'       : 'notifData',
            'description': 'The data notification contains a header and a variable length array of binary data. The length of the data is determined based on the length of the notification.\n\nThe manager forwards all packets received on its IP address and non-manager ports as data notifications.',
            'response'   : {
                'FIELDS':  [
                    ['utcSecs',            INT,      8,   None],
                    ['utcUsecs',           INT,      4,   None],
                    ['macAddress',         HEXDATA,  8,   None],
                    ['srcPort',            INT,      2,   None],
                    ['dstPort',            INT,      2,   None],
                    ['data',               HEXDATA,  None,None],
                ],
            },
        },
        {
            'id'         : 5,
            'name'       : 'notifIpData',
            'description': "The ipData notification contains full IP packet sent by the mote, including 6LoWPAN header, UDP header, and the UDP payload. Manager generates this notification when it receives packet from a mote with destination other than manager's own IP address. The size of the data field can be calculated by subtracting the fixed header size (up to macAddress) from the size of overall notification packet.",
            'response'   : {
                'FIELDS':  [
                    ['utcSecs',            INT,      8,   None],
                    ['utcUsecs',           INT,      4,   None],
                    ['macAddress',         HEXDATA,  8,   None],
                    ['data',               HEXDATA,  None,None],
                ],
            },
        },
        {
            'id'         : 6,
            'name'       : 'notifHealthReport',
            'description': 'The healthReport notifications include the raw payload of health reports received from devices. The payload contains one or more specific health report messages. Each message contains an identifier, length and variable-sized data. The individual healthReport message structures are defined below.',
            'response'   : {
                'FIELDS':  [
                    ['macAddress',         HEXDATA,  8,   None],
                    ['payload',            HEXDATA,  None,None],
                ],
            },
        },
        {
            'id'         : 7,
            'name'       : 'notifRadiotestStatsPER',
            'description': 'The testRadioStatsPER notification is generated by the manager when PER test in RX mode is completed.\n\nThis command is available in the SmartMesh IP Manager version 1.4.2 or later.',
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
    
    # We redefine this attribute inherited from ApiDefinition. See
    # ApiDefinition for a full description of the structure of this field.
    notifications = [
        {
            'id'         : 3,
            'name'       : 'manager_hello',
            'description': 'Sent by the manager to a initiate new session with a client.',
            'response'   : {
                'FIELDS':  [
                    ['version',             INT,      1,   None],
                    ['mode',                INT,      1,   None],
                ],
            },
        },
        {
            'id'         : 20,
            'name'       : 'notification',
            'description': '',
            'response'   : {
                'FIELDS':  [
                    [SUBID1,                INT,      1,   None],
                ]
            },
            'subCommands': subCommandsNotification,
        },
    ]
    
    def serialize_radiotestTx(self, commandArray, cmd_params):
        
        # start by serializing with complete API definition
        returnVal = self.default_serializer(commandArray, cmd_params)
        
        # remove the unused sequence definitions
        startIndex = 7+cmd_params['seqSize']*3
        numVals    = 10-cmd_params['seqSize']
        returnVal[1][startIndex:startIndex+numVals*3] = []
        
        return returnVal
