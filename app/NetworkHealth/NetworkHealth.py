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
from SmartMeshSDK.IpMgrConnectorSerial            import IpMgrConnectorSerial
from SmartMeshSDK.IpMgrConnectorMux               import IpMgrSubscribe
from SmartMeshSDK.ApiException                    import APIError, \
                                                         ConnectionError,  \
                                                         CommandTimeoutError
from SmartMeshSDK.protocols.NetworkHealthAnalyzer import NetworkHealthAnalyzer

# DustCli
from dustCli      import DustCli

#============================ defines =========================================

#============================ globals =========================================

connector          = None
notifThread        = None
snapshotThread     = None

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

#============================ threads =========================================

class NotifThread(object):
    
    def __init__(self,connector):
        
        # store params
        self.connector = connector
        
        # subscriber
        self.subscriber = IpMgrSubscribe.IpMgrSubscribe(self.connector)
        self.subscriber.start()
        self.subscriber.subscribe(
            notifTypes =    [
                                IpMgrSubscribe.IpMgrSubscribe.NOTIFHEALTHREPORT,
                            ],
            fun =           self._notifHealthReportCb,
            isRlbl =        True,
        )
        '''
        self.subscriber.subscribe(
            notifTypes =    [
                                IpMgrSubscribe.IpMgrSubscribe.ERROR,
                                IpMgrSubscribe.IpMgrSubscribe.FINISH,
                            ],
            fun =           self.disconnectedCallback,
            isRlbl =        True,
        )
        '''
    
    #======================== public ==========================================
    
    def disconnect(self):
        self.connector.disconnect()
    
    #======================== private =========================================
    
    def _notifHealthReportCb(self, notifName, notifParams):
        print notifName
        print notifParams
        print "TODO _notifHealthReportCb"

class SnapshotThread(threading.Thread):
    
    SNAPSHOTDELAY_INITIAL_S = 5
    DFLT_SNAPSHOTPERIOD     = 3600
    
    def __init__(self,connector):
        
        # store params
        self.connector                 = connector
        
        # local variables
        self.goOn                      = True
        self.dataLock                  = threading.RLock()
        self.delayCounter              = self.SNAPSHOTDELAY_INITIAL_S
        self.snapshotPeriod            = self.DFLT_SNAPSHOTPERIOD
        self.networkHealthAnalyzer     = NetworkHealthAnalyzer.NetworkHealthAnalyzer()
        self.lastResults               = ""
        
        # initialize parent
        threading.Thread.__init__(self)
        self.name                      = 'SnapshotThread'
        
        # start itself
        self.start()
    
    #======================== thread ==========================================
    
    def run(self):
        
        try:
            while self.goOn:
                
                # delay
                time.sleep(1)
                
                # decide whether to snapshot
                with self.dataLock:
                    self.delayCounter      -=1
                    if self.delayCounter<=0:
                        doSnapshot          = True
                        self.delayCounter   = self.snapshotPeriod
                    else:
                        doSnapshot          = False
                
                # snapshot
                if doSnapshot:
                    self._doSnapshot()
        
        except Exception as err:
            printExcAndQuit(err)
    
    #======================== public ==========================================
    
    def setSnapshotPeriod(self,period):
        
        with self.dataLock:
            
            # store new value
            self.snapshotPeriod = period
            
            # do a snapshot right now
            self.snapshotNow()
    
    def snapshotNow(self):
        
        with self.dataLock:
            
            # do a snapshot right now
            self.delayCounter   = 0
    
    def printLastResults(self):
        with self.dataLock:
            print self.lastResults
    
    def close(self):
        
        with self.dataLock:
            self.goOn = False
    
    #======================== private =========================================
    
    def _doSnapshot(self):
        
        try:
            with self.dataLock:
                
                dataForAnalyzer       = {}
                motes                 = []
                
                # getMoteConfig on all motes
                dataForAnalyzer['moteinfo']     = {}
                currentMac            = (0,0,0,0,0,0,0,0) # start getMoteConfig() iteration with the 0 MAC address
                continueAsking        = True
                while continueAsking:
                    try:
                        res           = self.connector.dn_getMoteConfig(currentMac,True)
                    except APIError:
                        continueAsking = False
                    else:
                        currentMac    = res.macAddress
                        motes        += [currentMac]
                        dataForAnalyzer['moteinfo'][tuple(currentMac)] = self._namedTupleToDict(res)
                
                # getMoteInfo on all motes
                for mac in motes:
                    res = self.connector.dn_getMoteInfo(mac)
                    for (k,v) in self._namedTupleToDict(res).items():
                        dataForAnalyzer['moteinfo'][tuple(mac)][k] = v
                
                # get path info on all paths of all motes
                dataForAnalyzer['networkpaths'] = {}
                for mac in motes:
                    currentPathId  = 0
                    continueAsking = True
                    while continueAsking:
                        try:
                            res = self.connector.dn_getNextPathInfo(mac,0,currentPathId)
                            fromMAC = tuple(res.source)
                            toMAC   = tuple(res.dest)
                            dataForAnalyzer['networkpaths'][(fromMAC,toMAC)] = self._namedTupleToDict(res)
                        except APIError:
                            continueAsking = False
                        else:
                            currentPathId  = res.pathId
                
                print "running test at {0}".format(self._now())
                
                # run NetworkHealthAnalyzer
                results = self.networkHealthAnalyzer.analyze(dataForAnalyzer)
                
                # format the results
                self.lastResults = self._formatResults(results)
                
                # log the formatted results
                self._logResults(self.lastResults)
        
        except Exception as err:
            printExcAndQuit(err)
    
    def _formatResults(self,results):
        output     = []
        output    += ['']
        output    += [
            '============================= {0} ============================='.format(
                self._now()
            )
        ]
        output    += ['']
        
        for result in results:
            testName    = result['testName']
            outcome     = result['outcome']
            description = self._removeHtml(result['description'])
            testDesc    = self._removeHtml(result['testDesc'])
            output    += ['']
            output    += ['=== name ==============']
            output    += ['']
            output    += [testName]
            output    += ['']
            output    += ['=== outcome ===========']
            output    += ['']
            output    += [outcome]
            output    += ['']
            output    += ['=== description =======']
            output    += ['']
            output    += [description]
            output    += ['']
            output    += ['=== about this test ===']
            output    += ['']
            output    += [testDesc]
        
        output     = '\n'.join(output)
        
        return output
    
    def _removeHtml(self,input):
        for tag in ['<b>','</b>','<p>','</p>','<li>','</li>','<ul>','</ul>']:
            input = input.replace(tag,"")
        input = input.replace("<br/>","\n")
        return input
    
    def _logResults(self,results):
        
        with open('testresults.txt','a') as f:
            f.write(results)
    
    def _namedTupleToDict(self,nt):
        return dict(nt._asdict())
    
    def _now(self):
        return time.strftime("%Y-%m-%d %H:%M:%S",time.localtime())

#============================ CLI handlers ====================================

def connect_clicb(params):
    global connector
    global notifThread
    global snapshotThread
    
    # filter params
    port = params[0]
    
    # create a coonnector
    connector = IpMgrConnectorSerial.IpMgrConnectorSerial()
    
    # connect to the manager
    try:
        connector.connect({
            'port': port,
        })
    except ConnectionError as err:
        printExcAndQuit(err)
    
    # start threads
    notifThread         = NotifThread(connector)
    snapshotThread      = SnapshotThread(connector)

def now_clicb(params):
    global snapshotThread
    
    snapshotThread.snapshotNow()

def last_clicb(params):
    global snapshotThread
    
    snapshotThread.printLastResults()

def period_clicb(params):
    global snapshotThread
    
    try:
        period = int(params[0])
    except ValueError:
        print 'you should pass an integer, "{0}" is not'.format(params[0])
        return
    
    if not snapshotThread:
        print "connect first before setting the period"
    else:
        snapshotThread.setSnapshotPeriod(period)

def quit_clicb():
    global connector
    global notifThread
    global snapshotThread
    
    if connector:
        connector.disconnect()
    if notifThread:
        notifThread.disconnect()
    if snapshotThread:
        snapshotThread.close()
    
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
        name                      = 'now',
        alias                     = 'n',
        description               = 'assess the health of the network now',
        params                    = [],
        callback                  = now_clicb,
        dontCheckParamsLength     = False,
    )
    cli.registerCommand(
        name                      = 'last',
        alias                     = 'l',
        description               = 'print the last results',
        params                    = [],
        callback                  = last_clicb,
        dontCheckParamsLength     = False,
    )
    cli.registerCommand(
        name                      = 'period',
        alias                     = 'p',
        description               = 'set the period of the health assessment',
        params                    = ['period'],
        callback                  = period_clicb,
        dontCheckParamsLength     = False,
    )

if __name__=='__main__':
    main()
