'OTAP command and file structures'

import struct
from .GenStructs import ApiStructField, GenObjectFactory, parse_obj

OTAP_PORT = 0xF0B1

class OTAP:
    HANDSHAKE_CMD = 0x16
    DATA_CMD      = 0x17
    STATUS_CMD    = 0x18
    COMMIT_CMD    = 0x19

# TODO: DN API response codes
RC_UNSUPPORTED = 6

class OTAPError:
    # OTAP return codes
    OTAP_RC_LOWBATT            = 1  # low battery voltage
    OTAP_RC_FILE               = 2  # invalid file metadata
                                    # size, block size, start address, execute size is wrong
    OTAP_RC_INVALID_PARTITION  = 3  # Invalid partition information (ID, file size)
    OTAP_RC_INVALID_APP_ID     = 4  # AppId is not correct
    OTAP_RC_INVALID_VER        = 5  # SW versions are not compatible for OTAP
    OTAP_RC_INVALID_VENDOR_ID  = 6  # invalid vendor ID
    OTAP_RC_RCV_ERROR          = 7 
    OTAP_RC_FLASH              = 8
    OTAP_RC_MIC                = 9  # MIC failed on uploaded data
    OTAP_RC_NOT_IN_OTAP        = 10 # No OTAP handshake is initiated
    OTAP_RC_IOERR              = 11 # IO error
    OTAP_RC_CREATE             = 12 # Can not create OTAP file
    OTAP_RC_INVALID_EXEPAR_HDR = 13 # Wrong value for exe-partition header fields 'signature' or 'upgrade'
    OTAP_RC_RAM                = 14 # Can not allocate memory
    OTAP_RC_UNCOMPRESS         = 15 # Decompression error
    OTAP_IN_PROGRESS           = 16 # OTAP in progress
    OTAP_LOCK                  = 17 # OTAP lockout

    OTAP_RC_STRINGS = [ "OK",
                        "Low battery",
                        "Invalid file data",
                        "Invalid partition",
                        "Invalid App ID",
                        "Invalid version",
                        "Invalid Vendor",
                        "Receive error",
                        "Flash error",
                        "MIC error",
                        "No OTAP session",
                        "IO error",
                        "Can not create file",
                        "Invalid exe header",
                        "Out of memory",
                        "Decompression error",
                        "OTAP in progress",
                        "OTAP lockout"
                        ]

def otap_error_string(rc):
    try:
        return OTAPError.OTAP_RC_STRINGS[rc]
    except IndexError:
        return "Unknown error (%d)" % rc


factory = GenObjectFactory()

VER_FIELDS = [ ApiStructField('major', 'int', 1),
               ApiStructField('minor', 'int', 1),
               ApiStructField('release', 'int', 1),
               ApiStructField('build', 'int', 2), 
               ]

Version = factory.synthesize('Version', VER_FIELDS)

# OTAP File structs

FI_FIELDS = [ ApiStructField('partitionId', 'int', 1), 
              ApiStructField('flags', 'int', 1),
              ApiStructField('uncompressedSize', 'int', 4),
              ApiStructField('startAddr', 'int', 4),
              ApiStructField('exeVersion', Version, Version.serialized_length),
              ApiStructField('exeDependsVersion', Version, Version.serialized_length),
              ApiStructField('exeAppId', 'int', 1),
              ApiStructField('exeVendorId', 'int', 2),
              ApiStructField('exeHwId', 'int', 1),
              ]

FileInfo = factory.synthesize('FileInfo', FI_FIELDS)

FH_FIELDS = [ ApiStructField('MIC', 'int', 4),
              ApiStructField('size', 'int', 4),
              ApiStructField('fileInfo', FileInfo, FileInfo.serialized_length),
              ]

FileHeader = factory.synthesize('FileHeader', FH_FIELDS)

def parse_otap_file(filename):
    header_data = ''
    with open(filename, 'rb') as f:
        header_data = f.read(FileHeader.serialized_length)
    return parse_obj(FileHeader, header_data)


# OTAP command structs

# Handshake

OH_FIELDS = [ ApiStructField('flags', 'int', 1),
              ApiStructField('file_mic', 'int', 4),
              ApiStructField('size', 'int', 4),
              ApiStructField('blockSize', 'int', 1),
              ]

OtapHandshakeHeader = factory.synthesize('OtapHandshakeHeader', OH_FIELDS)

class OldOtapHandshakeCmd(object):
    def __init__(self):
        pass
    
    def serialize(self):
        # file header
        result = struct.pack('!LL3BH3BHBHLL3B',
                             17, # MIC
                             128, # size
                             1, 0, 0, 10, # version
                             1, 0, 0, 1, # depends version
                             1, # app id
                             1, # vendor id
                             1, # addr
                             128, # compressed size
                             0, 0, 0) # padding
        result += struct.pack('!LBB', 1, 1, 0x40)
        return result


class OtapHandshake(object):
    pass
# TODO: append filename or fileInfo header


OH_RESP_FIELDS = [ ApiStructField('result', 'int', 1),
                   ApiStructField('otapResult', 'int', 1),
                   ApiStructField('file_mic', 'int', 4),
                   ApiStructField('delay', 'int', 4),
                   ]

OtapHandshakeResp = factory.synthesize('OtapHandshakeResp', OH_RESP_FIELDS,
                                       OTAP.HANDSHAKE_CMD)

# Data

class OtapData(object):
    def __init__(self, mic, block_num, data, index = 0, data_len = 0):
        self.file_mic = mic
        self.block_num = block_num
        if data_len:
            self.data = data[index:index+data_len]
        else:
            self.data = data[index:]
        
    def serialize(self):
        return struct.pack('!LH', self.file_mic, self.block_num) + self.data


# Status -- command is trivial, file MIC only

OS_RESP_FIELDS = [ ApiStructField('result', 'int', 1),
                   ApiStructField('otapResult', 'int', 1),
                   ApiStructField('file_mic', 'int', 4),
                   ]

OtapStatusRespHeader = factory.synthesize('OtapStatusRespHeader', OS_RESP_FIELDS)

class OtapStatusResp(object):
    def __init__(self):
        self.header = OtapStatusRespHeader(0, 0, 0)
        self.missing_blocks = []

    def parse(self, data, index = 0):
        self.header = parse_obj(OtapStatusRespHeader, data, index)
        index = OtapStatusRespHeader.serialized_length
        while index < len(data):
            (lost_block,) = struct.unpack('!H', data[index:index+2])
            self.missing_blocks.append(lost_block)
            index = index + 2

    def __str__(self):
        return str(self.header) + ' Missing=' + str(self.missing_blocks)

# Commit -- command is trivial, file MIC only
# response has same header as OTAP Status

OtapCommitResp = factory.synthesize('OtapCommitResp', OS_RESP_FIELDS,
                                    OTAP.COMMIT_CMD)

