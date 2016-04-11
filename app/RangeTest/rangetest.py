#!/usr/bin/python

#============================ adjust path =====================================

import sys
import os
if __name__ == "__main__":
    here = sys.path[0]
    sys.path.insert(0, os.path.join(here, '..', '..','libs'))
    sys.path.insert(0, os.path.join(here, '..', '..','external_libs'))

#============================ imports =========================================

import time
import threading
import traceback
import pdb

from SmartMeshSDK.IpMoteConnector      import IpMoteConnector
from SmartMeshSDK.IpMgrConnectorSerial import IpMgrConnectorSerial
from SmartMeshSDK.IpMgrConnectorMux    import IpMgrSubscribe
from SmartMeshSDK.ApiException         import APIError, \
                                              ConnectionError
from SmartMeshSDK.protocols.oap        import OAPMessage

from dustCli                           import DustCli
from SmartMeshSDK                      import sdk_version
from SmartMeshSDK.utils                import FormatUtils as u

#============================ defines =========================================

#============================ globals =========================================

connector     = None
range_tester  = None

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

#============================ objects =========================================

class RangeTester(object):

    ## timeout (in seconds) for a broadcast commmand. The timeout will expire
    # if not all OAP responses have been received. Note that up to MAX_NUM_BCAST
    # will be sent.
    TOUT_OAP_RESPONSE_BCAST       = 10.0

    ## maximum number of broadcasts sent. A new broadcast is sent when BOTH
    # conditions are met: the timeout (of value TOUT_OAP_RESPONSE_BCAST)
    # expired AND we are still expecting more than THRES_BCAST_UNICAST OAP
    # responses.
    MAX_NUM_BCAST                 =    3
    
    ## if we are expected less than THRES_BCAST_UNICAST OAP responses when the 
    # timeout expires, we send unicast messages, otherwise broadcast
    THRES_BCAST_UNICAST           =    3
    
    ## maximum time (in seconds) we wait for a unicast OAP response
    TOUT_OAP_RESPONSE_UNICAST     =  6.0
    
    ## maximum number of unicasts sent to a single node. A new unicast is when
    # the timeout (of value TOUT_OAP_RESPONSE_UNICAST) expires
    MAX_NUM_UNICASTS              =    3
    
    ## state of the state machine
    ST_IDLE                       = 'ST_IDLE'              # idle, no active communication
    ST_SENDING_BCASTS             = 'ST_SENDING_BCASTS'    # I'm busy sending (possibly more than 1) broadcast
    ST_SENDING_UNICASTS           = 'ST_SENDING_UNICASTS'  # I'm busy sending (possibly more than 1) unicast
    ST_ALL                        = [
        ST_IDLE,
        ST_SENDING_BCASTS,
        ST_SENDING_UNICASTS,
    ]
    
    def __init__(self,connector):

        # store params
        self.connector              = connector
        self.stationId              = 26
        self.goOn                   = True

        # local variables
        self.stats                  = [""]*17              # a list of statistic per channel

        self.dataLock             = threading.RLock()      # lock access to the object variables
        self.expectedOAPResp      = []                     # MAC addresses of all operational motes
        self.tsStart              = None                   # timestamp when the OAP commands was sent
        self.state                = self.ST_IDLE           # state of the fsm we are currently in
        self.numBcastAttempts     = 0                      # number of broadcast attempts
        self.numUnicastAttempts   = 0                      # number of unicast attempts (reset for each node)
        self.lastUnicastDest      = None                   # destination MAC address of the last unicast
        self.toutTimer            = None                   # timer to measure timeout
        self.rtts                 = []                     # round-trip-times of all OAP responses
        self.failedNodes          = []                     # nodes that never answered

    
    #======================== public ==========================================

    def start(self):

        # set the current channel to default
        cc = 0

        # loop to the infinite and beyond
        while(self.goOn):
            # current channel
            cc = cc % 15 + 1

            # channel mask
            cm = 0x1<<cc

            # listen for packets
            resp = self._readPackets(cm)
            radioRxDone = False

            while not radioRxDone:
                time.sleep(1)

                # try to get last statistics
                try:
                    last_stats = self._getStats()
                except APIError:
                    continue

                radioRxDone = True

            # save stats
            self._saveStats(cc, last_stats)

            # print stats
            self._printStats(cc)

    def setAllLeds(self,ledVal): 
        '''
        \brief Set all the LEDs of all nodes in the mesh on/off
        
        \pre You can only call this functions if no active transmission is going
            on
        
        \param[in] ledVal The state of the LED to set: 0 for off, 1 for on
        
        \post The object is actively sending packets to the motes in then network.
            This function returning does NOT mean the operation is over.
        '''
        
        assert ledVal in [0,1]
        
        with self.dataLock:
            
            # abort if already busy
            if self.state!=self.ST_IDLE:
                print "aborting, still busy with previous command (state={0})".format(self.state)
                return
            
            # remember whether we're setting the LED "on" or "off"
            self.ledVal           = ledVal
            
            print '\n===== set LED {0}\n'.format(self.ledVal)
            
            # retrieve the MAC addresses of all operational nodes
            self.expectedOAPResp  = []
            currentMac      = (0,0,0,0,0,0,0,0) 
            continueAsking  = True
            while continueAsking:
                try:
                    res = self.connector.dn_getMoteConfig(currentMac,True)
                except APIError:
                    continueAsking = False
                else:
                    if ((not res.isAP) and (res.state in [4,])):
                        self.expectedOAPResp += [res.macAddress]
                    currentMac = res.macAddress
            self._printExpectedOAPResp()
            
            # abort if no nodes in network
            if not self.expectedOAPResp:
                print "aborting, no nodes in network"
                return
            
            # reset stats
            self.rtts                  = []
            self.failedNodes           = []
            self.numBcastAttempts      = 0
            self.numUnicastAttempts    = 0
            self.lastUnicastDest       = None
            self.state                 = self.ST_SENDING_BCASTS
            
            # start measuring time
            self.tsStart  = time.time()
            
            # send the first broadcast
            self.numBcastAttempts = 1
            self._sendBroadcast()
    
    def disconnect(self):
        try:
            self.connector.disconnect()
        except:
            # can happen if connector not connected
            pass
    
    #======================== private =========================================

    #=== actions

    def _readPackets(self, channel, duration=10):
        """
        Call the API to start listen for incomming packets
        """

        channel_hex = self._num_to_list(channel,2)
        connector.dn_testRadioRx(
                channelMask     = channel_hex,      # channel
                time            = duration,         # reading time
                stationId       = self.stationId    # stationId
            )

    def _getStats(self):
        """
        Get the latest radiotest statistics
        """
        return connector.dn_getParameter_testRadioRxStats()

    def _saveStats(self, channel, last_stats):
        """
        Populate the statistics list
        """
        self.stats[channel] = str(last_stats[1])

    def _printStats(self, channel):
        """
        Refresh page and print the statistics
        """
        print "Channel\tRxOK"
        for i in range(1,16):
            print "%s\t%s\n" % (i, self.stats[i])

    def _num_to_list(self,num,length):
        output = []
        for l in range(length):
            output = [(num>>8*l)&0xff]+output
        return output


    def _sendBroadcast(self):
        '''
        \brief Send a single broadcast into the mesh.
        '''
        
        with self.dataLock:
            
            print ' --> sending broadcast (attempt {0}/{1})'.format(
                self.numBcastAttempts,
                self.MAX_NUM_BCAST
            )
            
            # send OAP packet
            self._sendOap([0xff]*8)
            
            # arm timeout
            self.toutTimer   = threading.Timer(
                self.TOUT_OAP_RESPONSE_BCAST,
                self._timeout
            )
            self.toutTimer.start()
    
    def _sendUnicast(self,macToSendTo):
        
        with self.dataLock:
            
            print ' --> sending unicast to {0} (attempt {1}/{2})'.format(
                u.formatMacString(macToSendTo),
                self.numUnicastAttempts,
                self.MAX_NUM_UNICASTS,
            )
            
            # send OAP packet
            self._sendOap(macToSendTo)
            
            # arm timeout
            self.toutTimer   = threading.Timer(
                self.TOUT_OAP_RESPONSE_UNICAST,
                self._timeout
            )
            self.toutTimer.start()
    
    def _sendOap(self,macToSendTo):
        
        with self.dataLock:
            
            # build OAP message
            oap_msg = OAPMessage.build_oap(
                seq          = 0,
                sid          = 0,
                cmd          = OAPMessage.CmdType.PUT,
                addr         = [3,2],
                tags         = [OAPMessage.TLVByte(t=0,v=self.ledVal)],
                sync         = True,
            )
            oap_msg = [ord(b) for b in oap_msg]
            
            # send OAP message
            connector.dn_sendData(
                macAddress   = macToSendTo,
                priority     = 0,
                srcPort      = OAPMessage.OAP_PORT,
                dstPort      = OAPMessage.OAP_PORT,
                options      = 0x00,
                data         = oap_msg,
            )
    
    #=== notifications
    
    def _notifDataReceived(self, notifName, notifParams):
        
        assert notifName=='notifData'
        
        try:
            
            with self.dataLock:
                
                # remember what time it is
                now = time.time()
                
                # disregard data packets which are NOT notifications from the LED
                if  (
                        notifParams.srcPort!=OAPMessage.OAP_PORT or
                        notifParams.dstPort!=OAPMessage.OAP_PORT or
                        notifParams.data[-6:]!=[2, 0, 255, 2, 3, 2]
                    ):
                    return
                
                # stop if I'm NOT busy sending
                if self.state not in [
                        self.ST_SENDING_BCASTS,
                        self.ST_SENDING_UNICASTS
                    ]:
                    print "ERROR: receiving unexpected OAP response (state={0},mac={1})".format(
                        self.state,
                        u.formatMacString(notifParams.macAddress),
                    )
                    return
                
                # verify that MAC address is indeed in the list
                if notifParams.macAddress not in self.expectedOAPResp:
                    if notifParams.macAddress in [mac for (_,mac,_,_) in self.rtts]:
                        print "INFO: additional OAP response from {0}".format(
                            u.formatMacString(notifParams.macAddress),
                        )
                    else:
                        print "WARNING: receiving OAP response from unexpected mote {0} (response to multiple broadcasts?)".format(
                            u.formatMacString(notifParams.macAddress),
                        )
                    return
                
                # remove that mote from list of expected ACKs
                print " <-- first response from {0}".format(u.formatMacString(notifParams.macAddress))
                self.expectedOAPResp.remove(notifParams.macAddress)
                self._printExpectedOAPResp()
                
                # remember RTT
                self.rtts += [(now-self.tsStart,notifParams.macAddress,self.numBcastAttempts,self.numUnicastAttempts)]
                
                # decide what's next
                if self.expectedOAPResp:
                    # I'm still expecting OAP responses
                    
                    if   self.state==self.ST_SENDING_BCASTS:
                        # Just did a broadcast. I'm passively waiting for other OAP responses
                        
                        # do not cancel timeout here, as we haven't received all responses
                        
                        # nothing to do
                        pass
                    elif self.state==self.ST_SENDING_UNICASTS:
                        # I'm actively sending unicasts to all missing motes, one-by-one
                        
                        # stop the timeout
                        self.toutTimer.cancel()
                        
                        # send the next unicast
                        while self.expectedOAPResp:
                            
                            # select the next MAC address to send to
                            self.lastUnicastDest     = self.expectedOAPResp[0]
                            
                            self.numUnicastAttempts  = 1
                            try:
                                self._sendUnicast(self.lastUnicastDest)
                            except APIError:
                                # can happen if not is declared "lost" by manager
                                print "WARNING: APIError when sending unicast (mote lost?)"
                                
                                # remove from list of expected responses
                                self.expectedOAPResp.remove(self.lastUnicastDest)
                                
                                # add to list of failed nodes
                                self.failedNodes        += [
                                    (
                                        self.lastUnicastDest,
                                        self.numBcastAttempts,
                                        self.numUnicastAttempts,
                                        1,
                                    )
                                ]
                            else:
                                # I successfully sent out the OAP request
                                break
                        
                        if not self.expectedOAPResp:
                            # this can happen if all last nodes are lost
                            
                            # wrap up
                            self._wrapUp()
                        
                    else:
                        raise SystemError()
                
                else:
                    # I received all OAP responses, I'm DONE!
                    
                    # stop the timeout
                    self.toutTimer.cancel()
                    
                    # wrap up
                    self._wrapUp()
        
        except Exception as err:
            printExcAndQuit(err)
    
    def _wrapUp(self):
        with self.dataLock:
            
            # update state
            self.state = self.ST_IDLE
            
            # prepare print
            output  = []
            output += ['=====']
            output += ['']
            output += ['transmission done after {0:.03f}s'.format(time.time()-self.tsStart)]
            output += ['']
            
            # print response times
            output += ['response times:']
            for (dur,macAddress,numBcastAttempts,numUnicastAttempts) in self.rtts:
                line  = []
                line += [
                    ' - {0:.03f}s, {1} after {2:>2} broadcast(s)'.format(
                        dur,
                        u.formatMacString(macAddress),
                        numBcastAttempts,
                    )
                ]
                if numUnicastAttempts:
                    line += [
                    ' and {0:>2} unicast(s)'.format(
                        numUnicastAttempts,
                    )
                ]
                line  = ''.join(line)
                output += [line]
            
            # print failed nodes
            if self.failedNodes:
                output += ['failed nodes:']
                for (macAddress,numBcastAttempts,numUnicastAttempts,numApiErr) in self.failedNodes:
                    line  = []
                    line += [
                        ' - {0} after {1:>2} broadcast(s)'.format(
                            u.formatMacString(macAddress),
                            numBcastAttempts,
                        )
                    ]
                    if numUnicastAttempts:
                        line += [
                            ', {0:>2} unicast(s)'.format(
                                numUnicastAttempts,
                            )
                        ]
                    if numApiErr:
                        line += [
                            ', {0:>2} API error(s)'.format(
                                numApiErr,
                            )
                        ]
                    line = ''.join(line)
                    
                    output += [line]
            
            output += ['']
            output  = '\n'.join(output)
            
            # print
            print output
    
    def _printExpectedOAPResp(self):
        with self.dataLock:
            print '   expectedOAPResp ({0} items):'.format(len(self.expectedOAPResp))
            if self.expectedOAPResp:
                for mac in self.expectedOAPResp:
                    print '     - {0}'.format(u.formatMacString(mac))
            else:
                print '     (empty)'

#============================ CLI handlers ====================================

def quit_clicb():
    global connector

    try:
        connector.disconnect()
    except:
        # can happen if connector not created
        pass

    print "bye bye."
    time.sleep(0.3)

def connect_clicb(params):
    global connector
    global range_tester

    # filter params
    port = params[0]

    # create a coonnector
    connector = IpMoteConnector.IpMoteConnector()
    #connector = IpMgrConnectorSerial.IpMgrConnectorSerial()

    # connect to the manager
    try:
        connector.connect({
            'port': port,
        })
    except ConnectionError as err:
        printExcAndQuit(err)

    # create main object
    range_tester = RangeTester(connector)

def start_clicb(params):
    global range_tester
    range_tester.start()

#============================ main ============================================

def main():

    # create CLI interface
    cli = DustCli.DustCli("BroadcastLeds Application",quit_clicb)
    cli.registerCommand(
        name                      = 'connect',
        alias                     = 'c',
        description               = 'connect to a serial port',
        params                    = ['portname'],
        callback                  = connect_clicb,
        dontCheckParamsLength     = False,
    )
    cli.registerCommand(
        name                      = 'start',
        alias                     = 's',
        description               = 'start the range test',
        params                    = [],
        callback                  = start_clicb,
        dontCheckParamsLength     = False,
    )

    # print SmartMesh SDK version
    print 'SmartMesh SDK {0}'.format('.'.join([str(i) for i in sdk_version.VERSION]))
    cli.start()

if __name__=='__main__':
    main()
