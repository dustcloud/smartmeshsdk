#!/usr/bin/python
'''
This script sends an OAP command to the standard SmartMesh IP mote to
enable or disable publishing of temperature or pkgen data, or control the
blue LED of eval kit motes. This will only work with motes running the
default SmartMesh IP mote SW running in "master" mode.
'''

#============================ adjust path =====================================

import sys
import os
if __name__ == "__main__":
    here = sys.path[0]
    sys.path.insert(0, os.path.join(here, '..', 'libs'))
    sys.path.insert(0, os.path.join(here, '..', 'external_libs'))

#============================ imports =========================================

import urllib3
import traceback
import time
import base64
import certifi

# generic SmartMeshSDK imports
from SmartMeshSDK                      import sdk_version
from SmartMeshSDK.protocols.oap        import OAPDispatcher, \
                                              OAPClient,     \
                                              OAPMessage,    \
                                              OAPNotif
# VManager-specific imports
from VManagerSDK.vmanager              import Configuration
from VManagerSDK.vmgrapi               import VManagerApi
from VManagerSDK.vmanager.rest         import ApiException
from VManagerSDK.vmanager              import DataPacketSendInfo

#============================ defines =========================================

DFLT_VMGR_HOST          = "127.0.0.1"
DFLT_MOTE_MAC           = "FF-FF-FF-FF-FF-FF-FF-FF"
DFLT_RATE               = 30000
DFLT_SIZE               = 60
PRIORITY                = "low"

urllib3.disable_warnings() # disable warnings that show up about self-signed certificates

#============================ helpers =========================================

def sendapacket(mymac, mydata):
    '''
    Send data to all motes via broadcast.
    '''
    try:
        myPayload = DataPacketSendInfo()
        myPayload.src_port   = OAPMessage.OAP_PORT
        myPayload.dest_port  = OAPMessage.OAP_PORT
        myPayload.priority   = PRIORITY
        myPayload.payload    = mydata
        # send the data packet
        voyager.motesApi.send_data_packet(mymac, myPayload)
    except:
        print ('\n   ERROR -- Could not send data.\n')
    else:
        print '\n   Sending string "{0}" to {1} \n'.format(mydata, mymac)

#============================ main ============================================

try:
    # print Script name and SmartMesh SDK version
    print '\nVMgr_OAPsend (c) Dust Networks'
    print 'SmartMesh SDK {0}\n'.format('.'.join([str(i) for i in sdk_version.VERSION]))

    # ask the user for VManager hostname/IP address
    mgrhost = raw_input('Enter the IP address of the manager (e.g. {0} ):'.format(DFLT_VMGR_HOST))
    if mgrhost == "":
        mgrhost = DFLT_VMGR_HOST
    
    # ask the user for mote's MAC address
    macaddr = raw_input('Enter MAC address of mote to send to (e.g. {0} ):'.format(DFLT_MOTE_MAC))
    if macaddr == "":
        macaddr = DFLT_MOTE_MAC
    macaddr = macaddr.upper()       # Make sure all letters are upper case
    if len(macaddr) <> 23:          # Basic error checking
        sys.exit('\n\nMote Mac address entered is invalid\n')

    # ask the user for command
    userinput = raw_input(
        '\nEnter the desired command;\n'
        '1=Temperature ON/OFF\n'
        '2=PKGen ON/OFF or service only\n'
        '3=LED ON/OFF')
    if userinput == "1":
        # 1=Temperature ON/OFF
        userinput = raw_input('\nTurn Temperature publish ON or OFF?')
        if userinput.upper() == "ON" or userinput == "":
            tempOn = 1
            userinput = raw_input('\nEnter the desired publish rate in ms (e.g. {0} ):'.format(DFLT_RATE))
            if userinput == "":
                pktPeriod = DFLT_RATE
            else:
                pktPeriod = int(userinput)
        else:
            tempOn = 0
            pktPeriod = DFLT_RATE

        oap_msg = OAPMessage.build_oap(
            seq          = 0,
            sid          = 0,
            cmd          = OAPMessage.CmdType.PUT,
            addr         = [5],
            tags         = [
                OAPMessage.TLVByte(t=0,v=tempOn),
                OAPMessage.TLVLong(t=1,v=pktPeriod),
            ],
            sync         = True,
        )
    elif userinput == "2":
        # '2=PKGen ON/OFF or service only
        
        userinput = raw_input(
            '\nEnter the desired PKGen mode;\n'
            '1=Turn PKGen ON\n'
            '2=Turn PKGen OFF\n'
            '3=PKGen service Bandwidth request only - no publishing\n'
        )

        numPkt          = 30000
        pktSize         = DFLT_SIZE
        pktPeriod       = DFLT_RATE
        pktstartPID     = 0

        if userinput == "1":
            # 1=Turn PKGen ON
            userinput = raw_input('Enter the desired publish rate in ms (e.g. {0} ):'.format(DFLT_RATE))
            if userinput != "":
                pktPeriod = int(userinput)

        elif userinput == "2":
            # 2=Turn PKGen OFF
            numPkt = 1

        elif userinput == "3":
            # 3=PKGen service Bandwidth request only - no publishing
            numPkt = 1
            userinput = raw_input('Enter the desired bandwidth in ms (e.g. {0} ):'.format(DFLT_RATE))
            if userinput != "":
                pktPeriod = int(userinput)

        else:
            print 'Just use defaults to turn PKGen on'

        oap_msg = OAPMessage.build_oap(
            seq          = 0,
            sid          = 0,
            cmd          = OAPMessage.CmdType.PUT,
            addr         = [254],
            tags         = [
                OAPMessage.TLVLong(t=0,v=1),
                OAPMessage.TLVLong(t=1,v=numPkt),
                OAPMessage.TLVLong(t=2,v=pktPeriod),
                OAPMessage.TLVByte(t=3,v=pktSize),
                OAPMessage.TLVByte(t=4,v=pktstartPID),
            ],
            sync         = True,
        )

    elif userinput == "3":
        # 3=LED ON/OFF
        userinput = raw_input('Turn Blue LED ON or OFF?')
        
        if userinput.upper() == "ON" or userinput == "":
            ledVal = 1
        else:
            ledVal = 0

        oap_msg = OAPMessage.build_oap(
            seq          = 0,
            sid          = 0,
            cmd          = OAPMessage.CmdType.PUT,
            addr         = [3,2],
            tags         = [OAPMessage.TLVByte(t=0,v=ledVal)],
            sync         = True,
        )
    else:
        sys.exit('\n\nInvalid menu option selected\n')

    # log in as user "dust"
    config = Configuration()
    config.username     = 'dust'
    config.password     = 'dust'
    config.verify_ssl   = False
    
    if os.path.isfile(certifi.where()):
        config.ssl_ca_cert  = certifi.where()
    else:
        config.ssl_ca_cert = os.path.join(os.path.dirname(sys.executable), "cacert.pem")

    # initialize the VManager Python library
    voyager = VManagerApi(host=mgrhost)
    
    oap_msg_b64 = base64.b64encode(oap_msg)   # Convert from bin to base64

    # send the packet, once if to one mote, 3 times if Broadcast
    if macaddr == "FF-FF-FF-FF-FF-FF-FF-FF":
        loop = 3
    else:
        loop = 1
    for x in xrange(loop):
        sendapacket(macaddr, oap_msg_b64)
        time.sleep(2)

    print 'Script ended normally'

except:
    traceback.print_exc()
    print ('Script ended with an error.\n')
    sys.exit()
