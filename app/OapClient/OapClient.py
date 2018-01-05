#!/usr/bin/python

#============================ adjust path =====================================

import sys
import os
if __name__ == "__main__":
    here = sys.path[0]
    sys.path.insert(0, os.path.join(here, '..', '..','libs'))
    sys.path.insert(0, os.path.join(here, '..', '..','external_libs'))

#============================ imports =========================================

# built-in
import time
import threading
import traceback

# SmartMeshSDK
from SmartMeshSDK                                 import sdk_version
from SmartMeshSDK.utils                           import FormatUtils
from SmartMeshSDK.IpMgrConnectorSerial            import IpMgrConnectorSerial
from SmartMeshSDK.IpMgrConnectorMux               import IpMgrSubscribe
from SmartMeshSDK.ApiException                    import APIError, \
                                                         ConnectionError,  \
                                                         CommandTimeoutError
from SmartMeshSDK.protocols.oap                   import OAPDispatcher, \
                                                         OAPClient,     \
                                                         OAPMessage,    \
                                                         OAPNotif

# DustCli
from dustCli      import DustCli

#============================ defines =========================================

NUM_BCAST_TO_SEND  = 2
LOGFILE            = "OapClient_log.txt"

#============================ globals =========================================

#============================ helpers =========================================

def printExcAndQuit(err):
    output  = []
    output += ["="*30]
    output += ["error"]
    output += [str(err)]
    output += ["="*30]
    output += ["traceback"]
    output += [traceback.format_exc()]
    output += ["="*30]
    output += ["Script ended because of an error. Press Enter to exit."]
    output  = '\n'.join(output)
    
    raw_input(output)
    sys.exit(1)

def getOperationalMotes():

    operationalmotes = [] 
    # get list of operational motes
    currentMac     = (0,0,0,0,0,0,0,0) # start getMoteConfig() iteration with the 0 MAC address
    continueAsking = True
    while continueAsking:
        try:
            res = AppData().get('connector').dn_getMoteConfig(currentMac,True)
        except APIError:
            continueAsking = False
        else:
            if ((not res.isAP) and (res.state in [4,])):
                operationalmotes += [tuple(res.macAddress)]
            currentMac = res.macAddress
    AppData().set('operationalmotes',operationalmotes)
    
    # create an oap_client for each operational mote
    oap_clients = AppData().get('oap_clients')
    for mac in operationalmotes:
        if mac not in oap_clients:
            oap_clients[mac] = OAPClient.OAPClient(
                mac,
                AppData().get('connector').dn_sendData,
                AppData().get('oap_dispatch'),
            )
    
    return len(operationalmotes)
    
def printOperationalMotes():
    
    output  = []
    output += ["{0} operational motes:".format(len(AppData().get('operationalmotes')))]
    for (i,m) in enumerate(AppData().get('operationalmotes')):
        output += ['{0}: {1}'.format(i,FormatUtils.formatMacString(m))]
    output  = '\n'.join(output)
    
    print output

def selectOperationalMote(moteNum):
    
    if moteNum>len(AppData().get('operationalmotes')):
        print 'Cannot select mote {0}, there are only {1} motes'.format(
            moteNum,
            len(AppData().get('operationalmotes')),
        )
        return
    
    AppData().set('currentmote',moteNum)
    
    print '\nCurrently using mote {0} ({1}).'.format(
        AppData().get('currentmote'),
        FormatUtils.formatMacString(AppData().get('operationalmotes')[AppData().get('currentmote')])
    )

def togglePrintNotifs():
    
    if AppData().get('printNotifs')==False:
        AppData().set('printNotifs',True)
        print "notifications are ON."
    else:
        AppData().set('printNotifs',False)
        print "notifications are OFF."

def toggleLogNotifs():
    
    if AppData().get('logNotifs')==False:
        AppData().set('logNotifs',True)
        print "logging to logfile is ON."
    else:
        AppData().set('logNotifs',False)
        print "logging to logfile is OFF."

#============================ classes =========================================

class AppData(object):
    #======================== singleton pattern ===============================
    _instance = None
    _init     = False
    def __new__(cls, *args, **kwargs):
        if not cls._instance:
            cls._instance = super(AppData, cls).__new__(cls, *args, **kwargs)
        return cls._instance
    def __init__(self):
        # singleton
        if self._init:
            return
        self._init = True
        # variables
        self.dataLock   = threading.RLock()
        self.data       = {}
    #======================== public ==========================================
    def set(self,k,v):
        with self.dataLock:
            self.data[k] = v
    def get(self,k):
        with self.dataLock:
            return self.data[k]
    def delete(self,k):
        with self.dataLock:
            del self.data[k]

class Manager(object):
    
    def __init__(self):
        
        # OAP dispatcher
        AppData().set('oap_dispatch',OAPDispatcher.OAPDispatcher())
        AppData().get('oap_dispatch').register_notif_handler(self._handle_oap_notif)
        
        # subscriber
        self.subscriber = IpMgrSubscribe.IpMgrSubscribe(AppData().get('connector'))
        self.subscriber.start()
        self.subscriber.subscribe(
            notifTypes =    [
                                IpMgrSubscribe.IpMgrSubscribe.NOTIFDATA,
                            ],
            fun =           self._cb_NOTIFDATA,
            isRlbl =        False,
        )
        
        # list operational motes
        AppData().set('oap_clients',{})
        numMotes = getOperationalMotes()
        if numMotes:
            printOperationalMotes()
            selectOperationalMote(0)
        AppData().set('printNotifs',False)
        togglePrintNotifs()

        self.log_file = open(LOGFILE, 'w')
        AppData().set('logNotifs',True)
        toggleLogNotifs()

        # Added to calculate Mgr vs system time offset in the log prints
        self.mapmgrtime = MgrTime(0, 20)
        self.mapmgrtime.start()
        
    #======================== public ==========================================
    
    def disconnect(self):
        AppData().get('connector').disconnect()
        self.log_file.close()
    
    #======================== private =========================================
    
    def _cb_NOTIFDATA(self,notifName,notifParams):
        
        AppData().get('oap_dispatch').dispatch_pkt(notifName, notifParams)
        if AppData().get('logNotifs'):
            if notifParams.data[0] == 0:
                self.log_file.write (' Pkt queued Time  ---> {0}.{1:0>6}\n'.format(notifParams.utcSecs, notifParams.utcUsecs))

    def _handle_oap_notif(self,mac,notif):

        receive_time = float(time.time()) - self.mapmgrtime.pctomgr_time_offset
        output  = "OAP notification from {0} (receive time {1}):\n{2}".format(
            FormatUtils.formatMacString(mac),
            receive_time,
            notif
        )
        
        if AppData().get('printNotifs'):
            print output
        if AppData().get('logNotifs'):
            self.log_file.write('{0}\n'.format(output))

class MgrTime(threading.Thread):
    '''
    This class periodically sends a getTime() API command to the manager to map
    network time to UTC time. The offset is used to calculate the pkt arrival
    time for the same time base as the mote.
    '''

    def __init__(self, pctomgr_time_offset, sleepperiod):
        # init the parent
        threading.Thread.__init__(self)
        self.event                  = threading.Event()
        self.sleepperiod            = sleepperiod
        self.daemon                 = True
        self.pctomgr_time_offset    = pctomgr_time_offset
        # give this thread a name
        self.name                   = 'MgrTime'               

    def run(self):
        while True:
            # Get PC time and send the getTime command to the Manager
            pc_time = float(time.time())
            mgr_timepinres = AppData().get('connector').dn_getTime()
            mgr_time = mgr_timepinres.utcSecs + mgr_timepinres.utcUsecs / 1000000.0
            mgr_asn = int(''.join(["%02x"%i for i in mgr_timepinres.asn]),16)
            self.pctomgr_time_offset = pc_time - mgr_time
            
            self.event.wait(self.sleepperiod)

#============================ CLI handlers ====================================

def connect_clicb(params):
    
    # filter params
    port = params[0]
    
    try:
        AppData().get('connector')
    except KeyError:
        pass
    else:
        print 'already connected.'
        return
    
    # create a connector
    AppData().set('connector',IpMgrConnectorSerial.IpMgrConnectorSerial())
    
    # connect to the manager
    try:
        AppData().get('connector').connect({
            'port': port,
        })
    except ConnectionError as err:
        print 'Could not connect to {0}: {1}'.format(
            port,
            err,
        )
        AppData().delete('connector')
        return
    
    # start threads
    AppData().set('manager',Manager())

def list_clicb(params):
    getOperationalMotes()
    printOperationalMotes()

def select_clicb(params):
    selectOperationalMote(int(params[0]))

def notifs_clicb(params):
    togglePrintNotifs()

def writelogfile_clicb(params):
    toggleLogNotifs()

def oapinfo_response(mac, oap_resp):
    output  = []
    output += ["GET /info response from {0}:".format(FormatUtils.formatMacString(mac))]
    output  = '\n'.join(output)
    
    print output
    print (mac, oap_resp)

def info_clicb(params):
    
    # filter params
    moteId    = int(params[0])
    
    if moteId>len(AppData().get('operationalmotes')):
        print 'moteId {0} impossible, there are only {1} motes'.format(
            moteId,
            len(AppData().get('operationalmotes')),
        )
        return
    
    AppData().get('oap_clients')[AppData().get('operationalmotes')[moteId]].send(
        cmd_type   = OAPMessage.CmdType.GET,
        addr       = [0],
        data_tags  = [],
        cb         = oapinfo_response,
    )

def led_clicb(params):
    
    # filter params
    try:
        moteId    = int(params[0])
        isBcast   = False
    except:
        isBcast   = True
    ledState  = params[1]
    
    if moteId>len(AppData().get('operationalmotes')):
        print 'moteId {0} impossible, there are only {1} motes'.format(
            moteId,
            len(AppData().get('operationalmotes')),
        )
        return
    
    if ledState=="0":
        ledVal = 0
    else:
        ledVal = 1
    
    # send OAP command ... single or all broadcast
    if not isBcast:
        AppData().get('oap_clients')[AppData().get('operationalmotes')[moteId]].send(
            cmd_type   = OAPMessage.CmdType.PUT,
            addr       = [3,2],
            data_tags  = [OAPMessage.TLVByte(t=0,v=ledVal)],
        )
    else:
        # build OAP message
        oap_msg = OAPMessage.build_oap(
            seq          = 0,
            sid          = 0,
            cmd          = OAPMessage.CmdType.PUT,
            addr         = [3,2],
            tags         = [OAPMessage.TLVByte(t=0,v=ledVal)],
            sync         = True,
        )
        oap_msg = [ord(b) for b in oap_msg]
        
        # send OAP message broadcast NUM_BCAST_TO_SEND times
        for i in range (NUM_BCAST_TO_SEND):
            AppData().get('connector').dn_sendData(
                macAddress   = [0xff]*8,
                priority     = 0,
                srcPort      = OAPMessage.OAP_PORT,
                dstPort      = OAPMessage.OAP_PORT,
                options      = 0x00,
                data         = oap_msg,
            )

def temp_clicb(params):
    
    # filter params
    try:
        moteId    = int(params[0])
        isBcast   = False
    except:
        isBcast   = True 
    tempOn      = int(params[1])
    pktPeriod   = int(params[2])
    
    if moteId>len(AppData().get('operationalmotes')):
        print 'moteId {0} impossible, there are only {1} motes'.format(
            moteId,
            len(AppData().get('operationalmotes')),
        )
        return
    
    # send OAP command ... single or all broadcast
    if not isBcast:
        AppData().get('oap_clients')[AppData().get('operationalmotes')[moteId]].send(
            cmd_type   = OAPMessage.CmdType.PUT,
            addr       = [5],
            data_tags  = [
                OAPMessage.TLVByte(t=0,v=tempOn),
                OAPMessage.TLVLong(t=1,v=pktPeriod),
            ],
        )
    else:
        # build OAP message
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
        oap_msg = [ord(b) for b in oap_msg]
        
        # send OAP message broadcast NUM_BCAST_TO_SEND times
        for i in range (NUM_BCAST_TO_SEND):
            AppData().get('connector').dn_sendData(
                macAddress   = [0xff]*8,
                priority     = 0,
                srcPort      = OAPMessage.OAP_PORT,
                dstPort      = OAPMessage.OAP_PORT,
                options      = 0x00,
                data         = oap_msg,
            )

def pkgen_clicb(params):
    
    # filter params
    try:
        moteId    = int(params[0])
        isBcast   = False
    except:
        isBcast   = True 
    numPkt      = int(params[1])
    pktPeriod   = int(params[2])
    pktSize     = int(params[3])
    pktstartPID = 0
    
    if moteId>len(AppData().get('operationalmotes')):
        print 'moteId {0} impossible, there are only {1} motes'.format(
            moteId,
            len(AppData().get('operationalmotes')),
        )
        return
    
    # send OAP command ... single mote, or all unicast, or all broadcast
    if isBcast == False:
        AppData().get('oap_clients')[AppData().get('operationalmotes')[moteId]].send(
            cmd_type   = OAPMessage.CmdType.PUT,
            addr       = [254],
            data_tags  = [
                OAPMessage.TLVLong(t=0,v=1),
                OAPMessage.TLVLong(t=1,v=numPkt),
                OAPMessage.TLVLong(t=2,v=pktPeriod),
                OAPMessage.TLVByte(t=3,v=pktSize),
                OAPMessage.TLVByte(t=4,v=pktstartPID),
            ],
        )
    elif params[0] == "allu":
        print " Sending Unicast command to all motes\n"
        for mote_mac in AppData().get('operationalmotes'):
            AppData().get('oap_clients')[mote_mac].send(
                cmd_type   = OAPMessage.CmdType.PUT,
                addr       = [254],
                data_tags  = [
                    OAPMessage.TLVLong(t=0,v=1),
                    OAPMessage.TLVLong(t=1,v=numPkt),
                    OAPMessage.TLVLong(t=2,v=pktPeriod),
                    OAPMessage.TLVByte(t=3,v=pktSize),
                    OAPMessage.TLVByte(t=4,v=pktstartPID),
                ],
            )
            time.sleep(.25)
    elif params[0] == "allb":
        print " Sending Broadcast command to all motes\n"
        # build OAP message
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
        oap_msg = [ord(b) for b in oap_msg]
                
        # send OAP message broadcast NUM_BCAST_TO_SEND times
        for i in range (NUM_BCAST_TO_SEND):
            AppData().get('connector').dn_sendData(
                macAddress   = [0xff]*8,
                priority     = 0,
                srcPort      = OAPMessage.OAP_PORT,
                dstPort      = OAPMessage.OAP_PORT,
                options      = 0x00,
                data         = oap_msg,
            )
    else:
        print (' unknown paramater ... {0}'.format(params[0]))

def analog_clicb(params):
    
    # filter params
    moteId         = int(params[0])
    channel        = int(params[1])
    enable         = int(params[2])
    rate           = int(params[3])
    
    if moteId>len(AppData().get('operationalmotes')):
        print 'moteId {0} impossible, there are only {1} motes'.format(
            moteId,
            len(AppData().get('operationalmotes')),
        )
        return
    
    AppData().get('oap_clients')[AppData().get('operationalmotes')[moteId]].send(
        cmd_type   = OAPMessage.CmdType.PUT,
        addr       = [4,channel],
        data_tags  = [
            OAPMessage.TLVByte(t=0,v=enable),  # enable
            OAPMessage.TLVLong(t=1,v=rate),    # rate
        ],
    )

def quit_clicb():
    
    if AppData().get('connector'):
        AppData().get('connector').disconnect()
    if AppData().get('manager'):
        AppData().get('manager').disconnect()
    
    time.sleep(.3)
    print "bye bye."

#============================ main ============================================

def main():
    
    # create CLI interface
    cli = DustCli.DustCli(
        quit_cb  = quit_clicb,
        versions = {
            'SmartMesh SDK': sdk_version.VERSION,
        },
    )
    cli.registerCommand(
        name                      = 'connect',
        alias                     = 'c',
        description               = 'connect to a serial port',
        params                    = ['portname'],
        callback                  = connect_clicb,
        dontCheckParamsLength     = False,
    )
    cli.registerCommand(
        name                      = 'motes',
        alias                     = 'm',
        description               = 'list all the nodes in the network',
        params                    = [],
        callback                  = list_clicb,
        dontCheckParamsLength     = False,
    )
    cli.registerCommand(
        name                      = 'select',
        alias                     = 's',
        description               = 'select the mote to use',
        params                    = ['motenum'],
        callback                  = select_clicb,
        dontCheckParamsLength     = False,
    )
    cli.registerCommand(
        name                      = 'notifs',
        alias                     = 'n',
        description               = 'toggle whether to print OAP notifications',
        params                    = [],
        callback                  = notifs_clicb,
        dontCheckParamsLength     = False,
    )
    cli.registerCommand(
        name                      = 'writelogfile',
        alias                     = 'w',
        description               = 'toggle whether to write OAP notifications to a LOGFILE',
        params                    = [],
        callback                  = writelogfile_clicb,
        dontCheckParamsLength     = False,
    )
    cli.registerCommand(
        name                      = 'oapinfo',
        alias                     = 'oi',
        description               = 'read the info resource',
        params                    = ['moteId'],
        callback                  = info_clicb,
        dontCheckParamsLength     = False,
    )
    cli.registerCommand(
        name                      = 'led',
        alias                     = 'l',
        description               = 'set/clear blue led',
        params                    = ['moteId/all','ledState (0 or 1)'],
        callback                  = led_clicb,
        dontCheckParamsLength     = False,
    )
    cli.registerCommand(
        name                      = 'temp',
        alias                     = 't',
        description               = 'interact with the OAP "temp" resource',
        params                    = ['moteId/all','active(0 or 1)','rate'],
        callback                  = temp_clicb,
        dontCheckParamsLength     = False,
    )
    cli.registerCommand(
        name                      = 'pkgen',
        alias                     = 'p',
        description               = 'set the pkgen application on the mote',
        params                    = ['moteId/allu/allb','numPkt','pktPeriod','pktSize'],
        callback                  = pkgen_clicb,
        dontCheckParamsLength     = False,
    )
    cli.registerCommand(
        name                      = 'analog',
        alias                     = 'a',
        description               = 'set the analog application on the mote',
        params                    = ['moteId','channel','enable','rate'],
        callback                  = analog_clicb,
        dontCheckParamsLength     = False,
    )

if __name__=='__main__':
    main()
