# Utilities for handling the blink payload

import struct

BLINK_PAYLOAD_COMMAND_ID         = 0x94
BLINK_DSCV_NEIGHBORS_COMMAND_ID  = 0x95

def decode_blink(payload):
    '''Parse the blink payload
    payload - raw payload bytes as a string

    Returns: user payload as a raw string and neighbors as a list of (id, RSSI)
    '''
    data = ''
    neighbors = []
    # test whether this looks like a blink payload
    if ord(payload[0]) != BLINK_PAYLOAD_COMMAND_ID:
        raise RuntimeError('blink packet does not start with blink payload command')
    
    index = 0
    while (index < len(payload)):
        ptag, plen = struct.unpack('BB', payload[index:index+2])
        index += 2
        if ptag == BLINK_PAYLOAD_COMMAND_ID:
            # blink user payload
            data = payload[index:index+plen]
        elif ptag == BLINK_DSCV_NEIGHBORS_COMMAND_ID:
            # discovered neighbors
            dn_struct = payload[index:index+plen]            
            num_neighbors = struct.unpack('B', dn_struct[0])[0]
            dnindex = 1
            for _ in range(num_neighbors):
                # neighbor id, RSSI
                nid, rssi = struct.unpack('!Hb', dn_struct[dnindex:dnindex+3])
                dnindex += 3
                neighbors.append((nid, rssi))
        else:
            # unknown command id in blink packet
            pass
        index += plen

    return data, neighbors

