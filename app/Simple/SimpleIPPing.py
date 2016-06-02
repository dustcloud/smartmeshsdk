#!/usr/bin/python

#============================ adjust path =====================================

import sys
import os
if __name__ == "__main__":
    here = sys.path[0]
    sys.path.insert(0, os.path.join(here, '..', '..','libs'))
    sys.path.insert(0, os.path.join(here, '..', '..','external_libs'))

#============================ imports =========================================

import threading
import traceback

from SmartMeshSDK                      import sdk_version
from SmartMeshSDK.ApiException         import APIError
from SmartMeshSDK.IpMgrConnectorSerial import IpMgrConnectorSerial
from SmartMeshSDK.IpMgrConnectorMux    import IpMgrSubscribe
from SmartMeshSDK.utils                import FormatUtils

#============================ defines =========================================

DEFAULT_SERIALPORT = 'COM7'
DEFAULT_MOTEID     = 2

#============================ main ============================================

responseEvent = threading.Event()

def notifCallback(notifName, notifParams):
    global responseEvent
    
    if notifName!=IpMgrSubscribe.IpMgrSubscribe.EVENTPINGRESPONSE:
        return
    print 'response from {0} delay={1}ms voltage={2}mV temp={3}C'.format(
        FormatUtils.formatMacString(notifParams.macAddress),
        notifParams.delay,
        notifParams.voltage,
        notifParams.temperature,
    )
    
    responseEvent.set()

try:
    print 'Simple Application to ping a mote - (c) Dust Networks'
    print 'SmartMesh SDK {0}\n'.format('.'.join([str(b) for b in sdk_version.VERSION]))

    print '================== Step 1. Connect to the manager'
    
    # ask user for serial port of manager
    serialPort = raw_input('\nEnter the SmartMesh IP Manager\'s serial port (leave blank for {0}): '.format(DEFAULT_SERIALPORT))
    if not serialPort:
        serialPort = DEFAULT_SERIALPORT
    
    # connect to manager
    connector = IpMgrConnectorSerial.IpMgrConnectorSerial()
    connector.connect({
        'port': serialPort,
    })
    
    # subscribe to notifications
    subscriber = IpMgrSubscribe.IpMgrSubscribe(connector)
    subscriber.start()
    subscriber.subscribe(
        notifTypes =    [
                            IpMgrSubscribe.IpMgrSubscribe.NOTIFEVENT,
                        ],
        fun =           notifCallback,
        isRlbl =        True,
    )
    
    # get list of operational motes
    macs           = {}
    currentMac     = (0,0,0,0,0,0,0,0) # start getMoteConfig() iteration with the 0 MAC address
    continueAsking = True
    while continueAsking:
        try:
            res = connector.dn_getMoteConfig(currentMac,True)
        except APIError:
            continueAsking = False
        else:
            if ((not res.isAP) and (res.state in [4,])):
                macs[res.moteId] = res.macAddress
            currentMac = res.macAddress
    
    # print list of operational motes
    print '\nmoteId MAC'
    for (id,mac) in macs.items():
        print '{0:<6} {1}'.format(id,FormatUtils.formatMacString(mac))
    
    print '\n================ Step 2. Ping a mote'
    
    goOn = True
    while goOn:
        moteId = raw_input('\nEnter a moteId to ping of \'q\' to exit (leave blank for {0}): '.format(DEFAULT_MOTEID))
        if moteId=='q':
            goOn = False
            continue
        if moteId:
            moteId = int(moteId)
        else:
            moteId = DEFAULT_MOTEID
        
        connector.dn_pingMote(macs[moteId])
        
        print 'ping sent to {0}'.format(FormatUtils.formatMacString(macs[moteId]))
        
        responseEvent.wait()
        responseEvent.clear()
    
    print '\n\n============== Step 3. Disconnect from the device'
    
    connector.disconnect()

except Exception as err:
    output  = []
    output += ['=============']
    output += ['CRASH']
    output += [str(err)]
    output += [traceback.format_exc()]
    print '\n'.join(output)
else:
    print 'Script ended normally'
finally:
    try:
        connector.disconnect()
    except:
        pass
    raw_input("\nPress Enter to close.")
