'OTAP file parsing and handshake generation'

import os
import struct

from GenStructs import parse_obj
from OTAPStructs import FileHeader, FileInfo, OtapHandshakeHeader, parse_otap_file
import OTAPMic

# DN_API_OTAP_DATA_SIZE = 82
# maximum word-aligned block size to fit OTAP data command in 82 bytes of payload
BLOCK_SIZE = 72


class FileParser(object):
    """Parse and create the Handshake command for a file to be transferred
    with the OTAP protocol.
    
    """
    def __init__(self, filename, is_otap = True, overwrite = True):
        self.filename = filename
        self.is_otap = is_otap
        self.overwrite = overwrite
        self.use_temp = is_otap  # always use a temporary file for partitions
        if is_otap:
            otap_hdr = parse_otap_file(filename)
            self.header = otap_hdr.fileInfo.serialize()
        else:
            # strip any directories and use the first 13 chars of the filename
            self.header = struct.pack('13s', os.path.split(filename)[1][0:12])
        
        f = open(filename, 'rb')  
        # executable images and non-otap files are sent in their entirety
        # non-executable partition images are sent without the OTAP file header
        if is_otap and not (otap_hdr.fileInfo.flags & 1):
            f.seek(otap_hdr.serialized_length)
        file_data = f.read()                  
        f.close() 
        
        self.data = file_data
        # TODO: handle minimum file size by adding padding
        # make sure we pad before calculating mic
        self.blockify_data()
        self.mic = OTAPMic.generate_mic(self.data)
        # the FCS16 is used to output some user information so that file
        # contents can be verified on the mote with 'mfs fcs'
        self.fcs = OTAPMic.calcFCS(self.data)

    # blockify_data is separate from load_file in case we need to resize the blocks
    def blockify_data(self, block_size = BLOCK_SIZE):
        self.blocks = []
        for idx in xrange(0, len(self.data), block_size):
            self.blocks.append(self.data[idx:idx+block_size])

    def get_handshake_data(self):
        file_len = len(self.data)
        # set the flags
        flags = 0
        # Bit 0: normal (0) vs OTAP (1)
        if self.is_otap:
            flags |= 1
        # Bit 1: overwrite?
        if self.overwrite:
            flags |= 2
        # Bit 2: create temp?
        if self.use_temp:
            flags |= 4
        oh = OtapHandshakeHeader(flags=flags, file_mic=self.mic, size=file_len,
                                 blockSize=BLOCK_SIZE)
        
        # TODO: load file if not already loaded
        hs_data = oh.serialize()
        hs_data += self.header
        return hs_data


