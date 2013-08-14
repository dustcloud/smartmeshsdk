#!/usr/bin/python

import logging
class NullHandler(logging.Handler):
    def emit(self, record):
        pass
log = logging.getLogger('NetworkStateAnalyzer')
log.setLevel(logging.ERROR)
log.addHandler(NullHandler())

import threading

from   DustLinkData import DustLinkData
import FormatUtils
import Gateway

import DynNotifs
from   EventBus import EventBusClient
from   IpMgrConnectorSerial.IpMgrConnectorSerial import IpMgrConnectorSerial
from   IpMgrConnectorMux.IpMgrConnectorMux       import IpMgrConnectorMux

class NetworkStateAnalyzer(EventBusClient.EventBusClient):
    
    QUEUESIZE = 100
    
    def __init__(self,connectParams):
        
        # log
        log.info("creating instance")
        
        # store params
        self.connectParams         = connectParams
        
        # initialize parent class
        EventBusClient.EventBusClient.__init__(self,
            'networkEvent_{0}'.format(FormatUtils.formatConnectionParams(self.connectParams)),
            self._logIndication,
            queuesize=self.QUEUESIZE,
        )
        self.name                  = '{0}_NetworkStateAnalyzer'.format(
            FormatUtils.formatConnectionParams(self.connectParams)
        )
        
        # local variables
        self.netname               = FormatUtils.formatConnectionParams(self.connectParams)
        self.dataLock              = threading.Lock()
        self.snapPaths             = []
        self.snapshotOngoing       = False
    
    #======================== public ==========================================
    
    def _logIndication(self,sender,signal,data):
        
        # log
        if log.isEnabledFor(logging.DEBUG):
            log.debug("got data {0}".format(data))
        
        #===== store event data in DustLinkData
        found = True
        
        if   data['type']==Gateway.Gateway.SNAPSHOT_START:
            self._handle_SNAPSHOT_START()
        
        elif data['type']==Gateway.Gateway.CMD:
            if   (isinstance(data['res'],IpMgrConnectorSerial.Tuple_dn_getMoteConfig)              or isinstance(data['res'],IpMgrConnectorMux.Tuple_dn_getMoteConfig)):
                self._handle_CMD_getMoteConfig(data['res'])
            elif (isinstance(data['res'],IpMgrConnectorSerial.Tuple_dn_getMoteInfo)                or isinstance(data['res'],IpMgrConnectorMux.Tuple_dn_getMoteInfo)):
                self._handle_CMD_getMoteInfo(data['res'])
            elif (isinstance(data['res'],IpMgrConnectorSerial.Tuple_dn_getNextPathInfo)            or isinstance(data['res'],IpMgrConnectorMux.Tuple_dn_getNextPathInfo)):
                self._handle_CMD_getNextPathInfo(data['res'])
            else:
                found = False
        
        elif data['type']==Gateway.Gateway.SNAPSHOT_END:
            self._handle_SNAPSHOT_END()
        
        elif data['type']==Gateway.Gateway.NOTIF:
            if   (isinstance(data['notifParams'],IpMgrConnectorSerial.Tuple_notifHealthReport)     or isinstance(data['notifParams'],IpMgrConnectorMux.Tuple_notifHealthReport)):
                self._handle_NOTIF_notifHealthReport(data['notifParams'])
            elif (isinstance(data['notifParams'],IpMgrConnectorSerial.Tuple_eventMoteCreate)       or isinstance(data['notifParams'],IpMgrConnectorMux.Tuple_eventMoteCreate)):
                self._handle_NOTIF_eventMoteCreate(data['notifParams'])
            elif (isinstance(data['notifParams'],IpMgrConnectorSerial.Tuple_eventMoteJoin)         or isinstance(data['notifParams'],IpMgrConnectorMux.Tuple_eventMoteJoin)):
                self._handle_NOTIF_eventMoteJoin(data['notifParams'])
            elif (isinstance(data['notifParams'],IpMgrConnectorSerial.Tuple_eventMoteOperational)  or isinstance(data['notifParams'],IpMgrConnectorMux.Tuple_eventMoteOperational)):
                self._handle_NOTIF_eventMoteOperational(data['notifParams'])
            elif (isinstance(data['notifParams'],IpMgrConnectorSerial.Tuple_eventPathCreate)       or isinstance(data['notifParams'],IpMgrConnectorMux.Tuple_eventPathCreate)):
                self._handle_NOTIF_eventPathCreate(data['notifParams'])
            elif (isinstance(data['notifParams'],IpMgrConnectorSerial.Tuple_eventPathDelete)       or isinstance(data['notifParams'],IpMgrConnectorMux.Tuple_eventPathDelete)):
                self._handle_NOTIF_eventPathDelete(data['notifParams'])
            elif (isinstance(data['notifParams'],IpMgrConnectorSerial.Tuple_eventMoteLost)         or isinstance(data['notifParams'],IpMgrConnectorMux.Tuple_eventMoteLost)):
                self._handle_NOTIF_eventMoteLost(data['notifParams'])
            elif (isinstance(data['notifParams'],IpMgrConnectorSerial.Tuple_eventPacketSent)       or isinstance(data['notifParams'],IpMgrConnectorMux.Tuple_eventPacketSent)):
                pass # nothing to do
            else:
                found = False
        
        else:
            raise SystemError('unexpected data type={0}'.format(data['type']))
        
        if not found:
            log.warning('unhandled indication {0}'.format(data))
        
        #===== execute tests
        pass # TODO
    
    #======================== handlers ========================================
    
    #===== SNAPSHOT_START
    
    def _handle_SNAPSHOT_START(self):
        try:
            self.dataLock.acquire()
            self.snapshotOngoing  = True
            self.snapPaths        = []
        finally:
            self.dataLock.release()
    
    #===== CMD
    
    def _handle_CMD_getMoteConfig(self,res):
        
        mac      = tuple(res.macAddress)
        
        self._addNewMoteIfNeeded(mac)
        
        for k,v in {'moteId':          res.moteId,
                    'isAP':            res.isAP,
                    'state':           res.state,
                    'isRouting':       res.isRouting,}.items():
            DustLinkData.DustLinkData().setMoteInfo(mac,k,v)
    
    def _handle_CMD_getMoteInfo(self,res):
        
        mac      = tuple(res.macAddress)
        
        self._addNewMoteIfNeeded(mac)
        
        for k,v in {'state':           res.state,
                    'numNbrs':         res.numNbrs,
                    'numGoodNbrs':     res.numGoodNbrs,
                    'requestedBw':     res.requestedBw,
                    'totalNeededBw':   res.totalNeededBw,
                    'assignedBw':      res.assignedBw,
                    'packetsReceived': res.packetsReceived,
                    'packetsLost':     res.packetsLost,
                    'avgLatency':      res.avgLatency,}.items():
            DustLinkData.DustLinkData().setMoteInfo(mac,k,v)
    
    def _handle_CMD_getNextPathInfo(self,res):
        try:
            self.dataLock.acquire()
            self.snapPaths.append(res)
        finally:
            self.dataLock.release()
    
    #===== SNAPSHOT_END
    
    def _handle_SNAPSHOT_END(self):
        try:
            self.dataLock.acquire()
            
            currentPaths  = DustLinkData.DustLinkData().getNetworkPaths(self.netname)
            receivedPaths = [(tuple(p.source),tuple(p.dest)) for p in self.snapPaths]
            
            # delete paths that have disappeared
            for path in currentPaths:
                if path not in receivedPaths:
                    DustLinkData.DustLinkData().deletePath(self.netname,path[0],path[1])
            
            # add new paths
            for path in receivedPaths:
                if path not in currentPaths:
                    DustLinkData.DustLinkData().addPath(self.netname,path[0],path[1])
            
            # update paths
            for path in self.snapPaths:
                mac      = tuple(path.source)
                neighbor = tuple(path.dest)
                
                self._addNewMoteIfNeeded(mac)
                self._addNewMoteIfNeeded(neighbor)
                
                for k,v in {'pathId':          path.pathId,
                            'direction':       path.direction,
                            'numLinks':        path.numLinks,
                            'quality':         path.quality,
                            'rssiSrcDest':     path.rssiSrcDest,
                            'rssiDestSrc':     path.rssiDestSrc,}.items():
                    DustLinkData.DustLinkData().setPathInfo(
                        FormatUtils.formatConnectionParams(self.connectParams),
                        mac,neighbor,
                        k,
                        v
                    )
            
            self.snapshotOngoing  = False
            
        finally:
            self.dataLock.release()
    
    #===== NOTIF
    
    def _handle_NOTIF_notifHealthReport(self,notifParams):
        
        mac = tuple(notifParams.macAddress)
        self._addNewMoteIfNeeded(mac)
        
        # create the HR object
        data_as_string  = ''
        data_as_string += ''.join([chr(b) for b in notifParams.macAddress])
        data_as_string += ''.join([chr(b) for b in notifParams.payload])
        hr = DynNotifs.HealthReport(data_as_string)
        
        if hr.nbrDscv:
            self._handle_NOTIF_notifHealthReport_nbrDscv(mac,hr.nbrDscv)
        if hr.nbrHR:
           self._handle_NOTIF_notifHealthReport_nbrHR(mac,hr.nbrHR)
        if hr.devHR:
            self._handle_NOTIF_notifHealthReport_devHR(mac,hr.devHR)
        if hr.QOcc:
           self._handle_NOTIF_notifHealthReport_QOcc(mac,hr.QOcc)
    
    # helper for _handle_NOTIF_notifHealthReport
    def _handle_NOTIF_notifHealthReport_nbrDscv(self,mac,nbrDscv):
        
        return # poipoi
        
        '''
        def updateFromTuple(self,tuple):
            assert type(tuple)==DynNotifs.MoteCmdDscvr
            self.nbrId           = tuple.nbrId
            self.rsl             = tuple.rsl
            self.numRx           = tuple.numRx
        
        self.motes[mac].discoveredNeighbors = []
        for nbr in nbrDscv:
            newDiscoveredNeighbor = DiscoveredNeigbor()
            newDiscoveredNeighbor.updateFromTuple(nbr)
            self.motes[mac].discoveredNeighbors.append(newDiscoveredNeighbor)
        '''
    
    # helper for _handle_NOTIF_notifHealthReport
    def _handle_NOTIF_notifHealthReport_nbrHR(self,mac,nbrHR):
        
        return # poipoi
        
        '''
        class Neighbor(StateAttribute):
    
        def updateFromTuple(self,tuple):
            assert type(tuple)==DynNotifs.MoteCmdNbrHR
            
            self.nbrId           = tuple.nbrId
            self.nbrFlag         = tuple.nbrFlag
            self.rsl             = tuple.rsl
            self.numTxPk         = tuple.numTxPk
            self.numTxFail       = tuple.numTxFail
            self.numRxPk         = tuple.numRxPk
        
        # update motes
        self.motes[mac].neighbors = []
        for nbr in nbrHR:
            newNeighbor = Neighbor()
            newNeighbor.updateFromTuple(nbr)
            self.motes[mac].neighbors.append(newNeighbor)
        
        # update waterfall
        for nbr in nbrHR:
            if nbr.numTxPk>0:
                self.waterfall.append({
                    "from" : self._formatShortMac(mac),
                    "to"   : nbr.nbrId,
                    "rssi" : nbr.rsl,
                    "pdr"  : float(nbr.numTxPk-nbr.numTxFail)/float(nbr.numTxPk),
                })
                while len(self.waterfall)>self.NUM_WATERFALL_POINTS:
                    # log
                    log.debug("{0} waterfalls entries (max is {1}): popping".format(
                                    len(self.waterfall),
                                    self.NUM_WATERFALL_POINTS,
                                )
                             )
                    self.waterfall.pop(0)
        '''
    
    # helper for _handle_NOTIF_notifHealthReport
    def _handle_NOTIF_notifHealthReport_devHR(self,mac,devHR):
        
        for k,v in {'charge':          devHR.charge,
                    'temperature':     devHR.temperature,
                    'batteryVolt':     devHR.batteryVolt,
                    'numTxOk':         devHR.numTxOk,
                    'numTxFail':       devHR.numTxFail,
                    'numRxOk':         devHR.numRxOk,
                    'numRxLost':       devHR.numRxLost,
                    'numMacDrop':      devHR.numMacDrop,
                    'numTxBad':        devHR.numTxBad,
                    'badLink_frameId': devHR.badLink_frameId,
                    'badLink_slot':    devHR.badLink_slot,
                    'badLink_offset':  devHR.badLink_offset,}.items():
            DustLinkData.DustLinkData().setMoteInfo(mac,k,v)
    
    # helper for _handle_NOTIF_notifHealthReport
    def _handle_NOTIF_notifHealthReport_QOcc(self,mac,QOcc_param):
        
        for k,v in {'QOccAvrg':        QOcc_param.avrg,
                    'QOccMax':         QOcc_param.max,}.items():
            DustLinkData.DustLinkData().setMoteInfo(mac,k,v)
    
    def _handle_NOTIF_eventMoteCreate(self,notifParams):
        
        mac      = tuple(notifParams.macAddress)
    
        # add mote if needed
        self._addNewMoteIfNeeded(mac)
        
        # configure the mote's id
        DustLinkData.DustLinkData().setMoteInfo(mac,'moteId',notifParams.moteId)
    
    def _handle_NOTIF_eventMoteJoin(self,notifParams):
        
        mac      = tuple(notifParams.macAddress)
    
        # add mote if needed
        self._addNewMoteIfNeeded(mac)
        
        # configure the mote's state
        DustLinkData.DustLinkData().setMoteInfo(mac,'moteState',1) # state 1=negotiating
    
    def _handle_NOTIF_eventMoteOperational(self,notifParams):
        
        mac      = tuple(notifParams.macAddress)
        
        # add mote if needed
        self._addNewMoteIfNeeded(mac)
        
        # configure the mote's state
        DustLinkData.DustLinkData().setMoteInfo(mac,'moteState',4) # state 1=operational
    
    def _handle_NOTIF_eventPathCreate(self,notifParams):
        try:
            self.dataLock.acquire()
            
            if not self.snapshotOngoing:
                
                source        = tuple(notifParams.source)
                destination   = tuple(notifParams.dest)
                
                # add motes if needed
                self._addNewMoteIfNeeded(source)
                self._addNewMoteIfNeeded(destination)
                
                thisPath      = (source,destination)
                currentPaths  = DustLinkData.DustLinkData().getNetworkPaths(self.netname)
                
                # add path
                if thisPath not in currentPaths:
                    DustLinkData.DustLinkData().addPath(self.netname,thisPath[0],thisPath[1])
                
                # update path info
                DustLinkData.DustLinkData().setPathInfo(
                            self.netname,
                            thisPath[0],thisPath[1],
                            'direction',
                            notifParams.direction
                        )
            
        finally:
            self.dataLock.release()
    
    def _handle_NOTIF_eventPathDelete(self,notifParams):
        try:
            self.dataLock.acquire()
            
            if not self.snapshotOngoing:
                
                source        = tuple(notifParams.source)
                destination   = tuple(notifParams.dest)
                
                # add motes if needed
                self._addNewMoteIfNeeded(source)
                self._addNewMoteIfNeeded(destination)
                
                thisPath      = (source,destination)
                reversePath   = (destination, source)
                currentPaths  = DustLinkData.DustLinkData().getNetworkPaths(self.netname)
                
                # delete path
                if thisPath in currentPaths:
                    DustLinkData.DustLinkData().deletePath(self.netname,thisPath[0],thisPath[1])
                if reversePath in currentPaths:
                    DustLinkData.DustLinkData().deletePath(self.netname,reversePath[0],reversePath[1])
            
        finally:
            self.dataLock.release()
    
    def _handle_NOTIF_eventMoteLost(self,notifParams):
        try:
            self.dataLock.acquire()
            
            if not self.snapshotOngoing:
                
                source        = tuple(notifParams.macAddress)
                
                # add motes if needed
                self._addNewMoteIfNeeded(source)
                
                currentPaths  = DustLinkData.DustLinkData().getNetworkPaths(self.netname)
                
                # delete path
                for path in currentPaths:
                    if source == path[0]:
                        DustLinkData.DustLinkData().deletePath(self.netname,*path)
            
        finally:
            self.dataLock.release()
    
    #======================== helpers =========================================
    
    def _addNewMoteIfNeeded(self,mac):
        dld = DustLinkData.DustLinkData()
        
        # add mote
        try:
            dld.addMote(mac)
        except ValueError:
            pass # happens when mote already exists
        
        # in demo mode, add OAP apps to mote
        if dld.getDemoMode():
            moteInfo = dld.getMoteInfo(mac)
            if moteInfo and ('isAP' in moteInfo) and moteInfo['isAP']==0:
                for appname in dld.DEMO_MODE_APPS.keys():
                    try:
                        dld.attachAppToMote(mac,appname)
                    except ValueError:
                        pass # happens when app does not exist, or already attached
        
        # add mote to network
        try:
            dld.addNetworkMote(
                self.netname,
                mac
            )
        except ValueError:
            pass # happens when mote already in network
    
    #======================== unused ==========================================
    
    # running tests
    '''
    from NetworkTest   import NetworkTest
    from NetworkTest   import TestNumGoodNeighbors
    from NetworkTest   import TestNetworkReliability
    from NetworkTest   import TestMultipleJoins
    from NetworkTest   import TestStabilityVsRssi
    from NetworkTest   import TestPerMoteAvailability
    from NetworkTest   import TestNetworkAvailability
    from NetworkTest   import TestNumberLinks
    from NetworkTest   import TestSingleParent
    '''
    
    '''
    # add stats
    self.stats['testCounters'] = {}
    self.stats['numRun']       = 0
    self.stats['numNOTRUN']    = 0
    self.stats['numPASS']      = 0
    self.stats['numFAIL']      = 0
    
    # local variable
    self.dataLock              = threading.Lock()
    self.networkState          = NetworkState.NetworkState(connectParams)
    
    self.tests = {
        GatewayLogParser.AnalysisEventCmd:   {
            'param':     'returnTuple',
            'tests': {
                IpMgrConnectorSerial.Tuple_dn_getMoteInfo: [
                    TestNumGoodNeighbors.TestNumGoodNeighbors,             # check for number of good neighbors
                    TestNetworkReliability.TestNetworkReliability,         # check network reliability
                ]
            },
        },
        GatewayLogParser.AnalysisEventStats: [
        ],
        GatewayLogParser.AnalysisEventNotif: {
            'param':     'notifTuple',
            'tests': {
                IpMgrConnectorSerial.Tuple_eventMoteJoin: [
                    TestMultipleJoins.TestMultipleJoins,                   # check for multiple joins
                ],
                GatewayListener.SnapHr: [
                    TestPerMoteAvailability.TestPerMoteAvailability,       # check per-mote availability
                    TestNetworkAvailability.TestNetworkAvailability,       # check network availability
                ]
            },
        },
        GatewayLogParser.AnalysisEventFyi: {
            'param':     'type',
            'tests': {
                GatewayLogParser.AnalysisEventFyi.SNAPSHOT_END: [
                    TestStabilityVsRssi.TestStabilityVsRssi,               # check stability vs. RSSI
                    TestNumberLinks.TestNumberLinks,                       # analyze number of links
                    TestSingleParent.TestSingleParent,                     # count single-parent motes
                ]
            },
        },
    '''
    
    '''
    def _findTestsToRun(self,data):
        testDesc = self.tests[type(data)]
        if isinstance(testDesc,(list)):
            return testDesc
        else:
            key = getattr(data,testDesc['param'])
            if not isinstance(key,str):
                key = type(key)
            try:
                return testDesc['tests'][key]
            except KeyError:
                pass # happend when no test exists for this case
        return None
    '''
    
    '''
        # run tests associated with data
        testToRun = self._findTestsToRun(data)
        if testToRun:
            
            # lock the networkState
            self.networkState.dataLock.acquire()
            
            # build test suite
            testSuite = unittest.TestSuite()
            for testToRun in testToRun:
                
                # update stats
                self.dataLock.acquire()
                testName = testToRun.__name__
                if testName not in self.stats['testCounters']:
                    self.stats['testCounters'][testName] = 0
                self.stats['testCounters'][testName] += 1
                self.dataLock.release()
            
                # parametrize test
                if   testToRun.getType()==NetworkTest.NetworkTest.NETWORK_WIDE:
                    testSuite.addTest(NetworkTest.NetworkTest.parametrize(data.timestamp,testToRun,self.networkState))
                elif testToRun.getType()==NetworkTest.NetworkTest.LAST_MOTE:
                    assert(lastmac)
                    testSuite.addTest(NetworkTest.NetworkTest.parametrize(data.timestamp,testToRun,self.networkState,tuple(lastmac)))
                elif testToRun.getType()==NetworkTest.NetworkTest.PER_MOTE:
                    for mac in self.networkState.motes.keys():
                        testSuite.addTest(NetworkTest.NetworkTest.parametrize(data.timestamp,testToRun,self.networkState,mac))
                else:
                    raise SystemError("unsupported test type {0}".format(testToRun.getType()))
            
            # log
            if log.isEnabledFor(logging.DEBUG):
                log.debug("Testing {0} by calling {1}".format(type(data),testSuite))
            
            # run tests
            testResult = NetworkTestResult.NetworkTestResult()
            testSuite.run(testResult)
            if testResult.errors:
                print testResult.errors
            assert(not testResult.errors)
            assert(testResult.testsRun==(len(testResult.notRunDesc)+len(testResult.successDesc)+len(testResult.failureDesc)))
            assert(len(testResult.failures)==len(testResult.failureDesc))
            
            # unlock the networkState
            self.networkState.dataLock.release()
            
            # update stats
            self.dataLock.acquire()
            self.stats['numRun']      += testResult.testsRun
            self.stats['numNOTRUN']   += len(testResult.notRunDesc)
            self.stats['numPASS']     += len(testResult.successDesc)
            self.stats['numFAIL']     += len(testResult.failureDesc)
            self.dataLock.release()
            
            # publish testResult
            for pub in self.networkTestPublishers:
               pub.publish(testResult)
        '''