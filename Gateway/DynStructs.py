'''
Mux API structures

Build classes from a description of their fields
'''

from collections import namedtuple
import struct

from StructUtils import ApiStructField, parse, synthesize
# TODO: other code imports the functions below from DynStructs
from StructUtils import parse_array, pair_to_string, to_string
from MuxMessage import API


# List of functions that return a callback ID
callbackIdFun = [ API.START_LOCATION_CMD,
                  API.EXCH_NETWORKID_CMD,
                  API.SET_ADVERTISING_CMD,
                  API.SET_DFRAME_MULT_CMD ] 


# TODO: the command type could be built into the struct class, then
# this dispatch could be a loop over all the struct classes
def parse_object(cmd_type, data):
    if cmd_type is API.GET_SYS_INFO_CMD:
        si = parse(SysInfo, data)
        return si

    elif cmd_type is API.GET_NETWORK_INFO_CMD:
        ni = parse(NetworkInfo, data)
        return ni

    elif cmd_type is API.GET_NETWORK_CFG_CMD:
        nc = parse(NetworkCfg, data)
        return nc

    elif cmd_type is API.GET_MANAGER_INFO_CMD:
        nc = parse(ManagerInfo, data)
        return nc

    elif cmd_type is API.GET_MOTE_CFG_CMD:
        mc = parse(MoteCfg, data)
        return mc

    elif cmd_type is API.GET_MOTE_CFG_BY_ID_CMD:
        mc = parse(MoteCfg, data)
        return mc
        
    elif cmd_type is API.GET_MOTE_INFO_CMD:
        mi = parse(MoteInfo, data)
        return mi

    elif cmd_type is API.GET_NEXT_PATH_CMD:
        pi = parse(Path, data)
        return pi
    elif cmd_type is API.GET_PATH_INFO_CMD:
        # add a dummy path id prefix 
        pi = parse(Path, '\0\0' + data)
        return pi

    elif cmd_type is API.GET_TIME_CMD:
        mt = parse(MeshTime, data)
        return mt

    elif cmd_type is API.GET_LICENSE_CMD:
        lic = parse(LicenseInfo, data)
        return lic

    elif cmd_type is API.GET_IP_CFG_CMD:
        ipinfi = parse(IPInfo, data)
        return ipinfi
        
    elif cmd_type is API.RESET_CMD:
        resetcmd = parse(ResetCmd, data)
        return resetcmd
        
    elif cmd_type in callbackIdFun:
        cb = parse(CallbackId, data)
        return cb
    
    else:
        return data



# struct  spl_getSysInfoRsp {
#     uint8_t   mac[8];           // Dust IEEE address
#     uint8_t   hwModel;          // Hardware model
#     uint8_t   hwRev;            // otp.ic_version:4 | otp:sip_version:4
#     uint8_t   swMajor;          // Software version, major
#     uint8_t   swMinor;          // Software version, minor
#     uint8_t   swPatch;          // Software version, patch
#     uint16_t  swBuild;          // Software version, build
# }

SYSINFO_FIELDS = [ ApiStructField('mac', 'array', 8),
                   ApiStructField('hwModel', 'int', 1),
                   ApiStructField('hwRev', 'int', 1),
                   ApiStructField('swMajor', 'int', 1),
                   ApiStructField('swMinor', 'int', 1),
                   ApiStructField('swPatch', 'int', 1),
                   ApiStructField('swBuild', 'int', 2),
                  ] 

SysInfo = synthesize('SysInfo', SYSINFO_FIELDS)


# enum  spl_frameProfile {
#     PICARD_PROFILE_01  = 1,   // fast  build / medium operation
#     ULPM_PROFILE_02    = 2,   // deprecated, maps to PICARD_PROFILE_01
#     ULPM_PROFILE_03    = 3,   // deprecated, maps to PICARD_PROFILE_01
#     ULPM_PROFILE_98    = 98,  // deprecated, maps to PICARD_PROFILE_01
#     ULPM_PROFILE_99    = 99,  // deprecated, maps to PICARD_PROFILE_01
# }
# enum  spl_loc_mode_t {
#     SPL_LOC_OFF,
#     SPL_LOC_ONDEMAND,
#     SPL_LOC_RTLS
# }
# struct  spl_getNetworkConfigRsp {
#     uint16_t       networkId;
#     uint8_t        accessPointPA;       // boolean
#     uint8_t        frameProfile;        // spl_frameProfile
#     uint16_t       maxMotes;
#     uint16_t       baseBandwidth;
#     uint8_t        downFrameMultVal;    // power of 2
#     uint8_t        numParents;
#     uint8_t        enableCCA;           // boolean
#     uint16_t       channelBlacklist;    // bitmap of available channels
#     uint8_t        autoStartNetwork;    // boolean
#     uint8_t        locMode;             // location mode (spl_loc_mode_t)
#     uint8_t        bbMode;              // backbone frame mode (spl_bb_mode_t)
#     uint8_t        bbSize;              // backbone frame size
#     uint16_t       bwMult;              // backbone frame size
# }

NETWORK_CFG_FIELDS = [ ApiStructField('networkId', 'int', 2),
                       ApiStructField('accessPointPA', 'boolean', 1),
                       ApiStructField('frameProfile', 'int', 1),
                       ApiStructField('maxMotes', 'int', 2),
                       ApiStructField('baseBandwidth', 'int', 2),
                       ApiStructField('downFrameMultValue', 'int', 1),
                       ApiStructField('numParents', 'int', 1),
                       ApiStructField('enableCCA', 'int', 1),
                       ApiStructField('channelBlacklist', 'int', 2),
                       ApiStructField('autoStartNetwork', 'boolean', 1),
                       ApiStructField('locMode', 'int', 1),
                       ApiStructField('bbMode', 'int', 1),
                       ApiStructField('bbSize', 'int', 1),
                       ApiStructField('radioTest', 'int', 1),
                       ApiStructField('bwMult', 'int', 2),
                       ]

NetworkCfg = synthesize('NetworkCfg', NETWORK_CFG_FIELDS)

# enum  spl_advState {
#     SPL_ADV_ON,
#     SPL_ADV_OFF,
# }
# enum  spl_multState {
#     SPL_MULT_ON,
#     SPL_MULT_OFF
# }
# struct  spl_getNetworkInfoRsp {
#     int16_t   numMotes;
#     uint16_t  asnSize;             // microseconds
#     uint8_t   advertisementState;  // spl_advState
#     uint8_t   downFrameMultState;  // spl_multState
#     uint8_t   netReliability;      
#     uint8_t   netPathStability;
#     uint32_t  netLatency;          // avg latency, ms
#     int8_t    netState;            // current networ state (see spl_netState)
# }

NETWORK_INFO_FIELDS = [ ApiStructField('numMotes', 'int', 2),
                        ApiStructField('asnSize', 'int', 2),
                        ApiStructField('advertisementState', 'int', 1),
                        ApiStructField('downFrameMultState', 'int', 1),
                        ApiStructField('netReliability', 'int', 1),
                        ApiStructField('netPathStability', 'int', 1),
                        ApiStructField('netLatency', 'int', 4),
                        ApiStructField('netState', 'int', 1),
                        ]

NetworkInfo = synthesize('NetworkInfo', NETWORK_INFO_FIELDS)


# struct  spl_getManagerStatsRsp {
#    // Low level stats:
#    uint16_t serTxCnt;        // # of packets sent out on serial port - TODO: 16 bits seems small
#    uint16_t serRxCnt;        // # of packets received on serial port - TODO: 16 bits  seems small
#    uint16_t serRxCRCErr;     // # of CRC errors
#    uint16_t serRxOverruns;   // # of overruns detected
#    // Protocol-level stats:
#    uint16_t apiEstabConn;    // # of established Serial API connections
#    uint16_t apiDropppedConn; // # of dropped Serial API connections
#    uint16_t apiTxOk;         // # of request packets sent on serial api for which ack or nack was received
#    uint16_t apiTxFail;       // # of packets for which there was no ack/nack
#    uint16_t apiRxOk;         // # of request packets that were received and acked/nacked
#    uint16_t apiRxProtErr;    // # of packets that were received and dropped due to invalid packet format
# }

MANAGER_INFO_FIELDS = [ ApiStructField('serTxCnt', 'int', 2),
                        ApiStructField('serRxCnt', 'int', 2),
                        ApiStructField('serRxCRCErr', 'int', 2),
                        ApiStructField('serRxOverruns', 'int', 2),
                        ApiStructField('apiEstabConn', 'int', 2),
                        ApiStructField('apiDroppedConn', 'int', 2),
                        ApiStructField('apiTxOk', 'int', 2),
                        ApiStructField('apiTxFail', 'int', 2),
                        ApiStructField('apiRxOk', 'int', 2),
                        ApiStructField('apiRxProtErr', 'int', 2)
                        ]

ManagerInfo = synthesize('ManagerInfo', MANAGER_INFO_FIELDS)


# enum spl_moteState {
#     SPL_MOTE_STATE_LOST,
#     SPL_MOTE_STATE_NEGOT,
#     SPL_MOTE_STATE_RSV1,
#     SPL_MOTE_STATE_RSV2,
#     SPL_MOTE_STATE_OPERATIONAL,
# }
# enum spl_mobilityType {
#     SPL_LOCATION_UNUSED,         // mote is not used for location measurements
#     SPL_LOCATION_FIXED,          // mote has a known fixed location
#     SPL_LOCATION_MOVABLE,        // mote has an unknown location
#     SPL_LOCATION_MOBILE,         // mote is mobile mote, not participating in the network
# }
# struct  spl_getMoteInfoRsp {
#     byte_t     mac[8];
#     uint16_t   moteId;           // id is used in neighbor health reports
#     boolean    isAP;             // boolean
#     uint8_t    state;            // spl_moteState 
#     uint8_t    mobilityType;     // spl_mobilityType
#     boolean    isRouting;        // boolean 
# }

MOTECFG_FIELDS = [ ApiStructField('mac', 'array', 8),
                   ApiStructField('moteId', 'int', 2),
                   ApiStructField('isAP', 'boolean', 1),
                   ApiStructField('state', 'int', 1),
                   ApiStructField('mobilityType', 'int', 1),
                   ApiStructField('isRouting', 'boolean', 1),
                   ]

MoteCfg = synthesize('MoteCfg', MOTECFG_FIELDS)

# struct spl_getMoteInfoRsp {
#     byte_t     mac[8];
#     uint8_t    state;
#     uint8_t    numNbrs;
#     uint8_t    numGoodNbrs;
#     uint32_t   requestedBw;
#     uint32_t   totalNeededBw;
#     uint32_t   assignedBw;
#     uint32_t   packetsReceived;
#     uint32_t   packetLost;
#     uint32_t   avgLatency;       // average latency in ms
# }

MOTEINFO_FIELDS = [ ApiStructField('mac', 'array', 8), 
                    ApiStructField('state', 'int', 1),
                    ApiStructField('numNbrs', 'int', 1),
                    ApiStructField('numGoodNbrs', 'int', 1),
                    ApiStructField('requestedBw', 'int', 4),
                    ApiStructField('totalNeededBw', 'int', 4),
                    ApiStructField('assignedBw', 'int', 4),
                    ApiStructField('packetsReceived', 'int', 4),
                    ApiStructField('packetsLost', 'int', 4),
                    ApiStructField('avgLatency', 'int', 4),
                   ]

MoteInfo = synthesize('MoteInfo', MOTEINFO_FIELDS)


# enum  spl_pathDirection {
#     SPL_PATH_DIR_UNCONNECTED,
#     SPL_PATH_DIR_UNI,
#     SPL_PATH_DIR_BI,
# }
# struct  spl_getNextPathInfoRsp {
#     uint16_t  pathId;
#     byte_t    source[8];
#     byte_t    dest[8];
#     uint8_t   direction;  // spl_pathDirection
#     uint8_t   numLinks;
#     uint8_t   quality;
#     int8_t    rssiSrcDest; // last rssi, source->dest
#     int8_t    rssiDestSrc; // last rssi, dest->src
# }

PATH_FIELDS = [ ApiStructField('pathId', 'int', 2),
                ApiStructField('source', 'array', 8),
                ApiStructField('dest', 'array', 8),
                ApiStructField('direction', 'int', 1),
                ApiStructField('numLinks', 'int', 1),
                ApiStructField('quality', 'int', 1),
                ApiStructField('rssiSrcDest', 'sint', 1),
                ApiStructField('rssiDestSrc', 'sint', 1),
                ]

Path = synthesize('Path', PATH_FIELDS)    


MESHTIME_FIELDS = [ ApiStructField('uptime', 'int', 4),
                    ApiStructField('asn',    'asn', 5),
                    ApiStructField('encoding', 'int', 1),
                    ApiStructField('utcSecs', 'int', 4),
                    ApiStructField('utcUsecs', 'int', 4),
                  ]

MeshTime = synthesize('MeshTime', MESHTIME_FIELDS)    


MANAGERINFO_FIELDS = [ApiStructField('serTxCnt', 'int', 2),
                      ApiStructField('serRxCnt', 'int', 2),
                      ApiStructField('serRxCRCErr', 'int', 2),
                      ApiStructField('serRxOverruns', 'int', 2),
                      ApiStructField('apiEstabConn', 'int', 2),
                      ApiStructField('apiDropppedConn', 'int', 2),
                      ApiStructField('apiTxOk', 'int', 2),
                      ApiStructField('apiTxErr', 'int', 2),
                      ApiStructField('apiTxFail', 'int', 2),
                      ApiStructField('apiRxOk', 'int', 2),
                      ApiStructField('apiRxProtErr', 'int', 2),
                      ]
ManagerInfo = synthesize('ManagerInfo', MANAGERINFO_FIELDS)


IPINFO_FIELDS = [ ApiStructField('ip6addr', 'array', 16),
                  ApiStructField('ip6mask', 'array', 16),
                  ]
IPInfo = synthesize('IPInfo', IPINFO_FIELDS)


RESETCMD_FIELDS = [ ApiStructField('mac', 'array', 8),
                    ]
ResetCmd = synthesize('ResetCmd', RESETCMD_FIELDS)


LICENSE_FIELD = [ ApiStructField('license', 'array', 13),
                  ]
LicenseInfo = synthesize('LicenseInfo', LICENSE_FIELD)


CALLBACKID_FIELDS = [ ApiStructField('callbackId', 'int', 4),
                      ]
CallbackId = synthesize('CallbackId', CALLBACKID_FIELDS)   
 

   
# TODO: getIPConfig
