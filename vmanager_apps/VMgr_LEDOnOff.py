#!/usr/bin/python
'''
This script sends an OAP command to the standard SmartMesh IP mote
to turn the Blue LED on/off. This will only work with the DC reference
motes that have the LED, and when running in "master" mode.
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
import time
import traceback
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
DFLT_MOTE_MAC           = "00-17-0D-00-00-38-0F-CC"
PRIORITY                = "low"

urllib3.disable_warnings() # disable warnings that show up about self-signed certificates

#============================ helpers =========================================

def sendapacket(mymac, mydata):
    '''
    Send a data packet to a mote.
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
        print '\n   Sending packet to {0} \n'.format(mymac)

#============================ main ============================================

try:
    # print banner
    print '\nVMgr_LEDOnOff (c) Dust Networks'
    print 'SmartMesh SDK {0}\n'.format('.'.join([str(i) for i in sdk_version.VERSION]))

    # ask the user which Manager IP to connect to, to which mote, and LED ON or OFF
    mgrhost = raw_input(' Enter the IP address of the manager (e.g. {0} ):'.format(DFLT_VMGR_HOST))
    if mgrhost == "":
        mgrhost = DFLT_VMGR_HOST
    
    # ask the user for mote's MAC address
    macaddr = raw_input(' Enter MAC address of mote to send to (e.g. {0})\n    or FF-FF-FF-FF-FF-FF-FF-FF for broadast:'.format(DFLT_MOTE_MAC))
    if macaddr == "":
        macaddr = DFLT_MOTE_MAC
    macaddr = macaddr.upper()       # Make sure all letters are upper case
    if len(macaddr) <> 23:          # Basic error checking
        sys.exit('\n\n Mote Mac address entered is invalid\n')

    userinput = raw_input(' Turn the LED ON or OFF? Default = ON:')
    if userinput == "":
        ledVal = 1
    else:
        ledVal = 0
                      
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
    
    # build OAP message
    oap_msg = OAPMessage.build_oap(
        seq             = 0,
        sid             = 0,
        cmd             = OAPMessage.CmdType.PUT,
        addr            = [3,2],
        tags            = [OAPMessage.TLVByte(t=0,v=ledVal)],
        sync           = True,
    )
    oap_msg_b64 = base64.b64encode(oap_msg)   # Convert from bin to base64

    # send the packet, once if to one mote, 4 times if Broadcast
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
    print ('Script ended with an error.')
    sys.exit()
