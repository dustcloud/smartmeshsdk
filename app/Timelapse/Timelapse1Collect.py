#!/usr/bin/python

#============================ adjust path =====================================

import sys
import os
if __name__ == "__main__":
    here = sys.path[0]
    sys.path.insert(0, os.path.join(here, '..', '..','libs'))
    sys.path.insert(0, os.path.join(here, '..', '..','external_libs'))

#============================ verify installation =============================

from SmartMeshSDK.utils import SmsdkInstallVerifier
(goodToGo,reason) = SmsdkInstallVerifier.verifyComponents(
    [
        SmsdkInstallVerifier.PYTHON,
        SmsdkInstallVerifier.PYSERIAL,
    ]
)
if not goodToGo:
    print "Your installation does not allow this application to run:\n"
    print reason
    raw_input("Press any button to exit")
    sys.exit(1)

#============================ imports =========================================

import threading
import json
import traceback
import time
import copy

from   SmartMeshSDK.protocols.Hr       import HrParser
from   SmartMeshSDK.utils              import AppUtils
from   SmartMeshSDK.ApiException       import APIError
from   SmartMeshSDK.ApiDefinition      import IpMgrDefinition
from   SmartMeshSDK.IpMgrConnectorMux  import IpMgrSubscribe
from   dustUI                          import dustWindow,                 \
                                              dustFrameConnection,        \
                                              dustFrameTable

#============================ logging =========================================

import logging

# local
'''
class NullHandler(logging.Handler):
    def emit(self, record):
        pass
log = logging.getLogger('App')
log.setLevel(logging.ERROR)
log.addHandler(NullHandler())
'''

#============================ defines =========================================

#============================ globals =========================================

#============================ setup/teardown ==================================

'''
def setup_module(function):
    
    # setup logging
    for loggerName in LOG_MODULES:
        temp = logging.getLogger(loggerName)
        temp.setLevel(logging.DEBUG)
        temp.addHandler(logHandler)

# global

AppUtils.configureLogging()
'''

# activity logs (do last)
activitylog = logging.getLogger('activitylog')
activitylog.setLevel(logging.INFO)
activitylogHandler = logging.handlers.RotatingFileHandler(
    'NetworkActivity.txt',
    maxBytes       = 200000000,
    backupCount    = 5,
    mode           = 'a',
)
activitylogHandler.setFormatter(logging.Formatter("%(message)s"))
activitylog.addHandler(activitylogHandler)

#============================ defines =========================================

GUIUPDATEPERIOD    = 500 # in ms
DEFAULT_CRASHLOG   = 'Timelapse.crashlog'

#============================ helpers =========================================

def currentUtcTime():
    return time.strftime("%a, %d %b %Y %H:%M:%S UTC", time.gmtime())

def logCrash(err):
    output  = []
    output += ["==============================================================="]
    output += [currentUtcTime()]
    output += [""]
    output += ["CRASH!!"]
    output += [""]
    output += ["=== exception type ==="]
    output += [str(type(err))]
    output += [""]
    output += ["=== traceback ==="]
    output += [traceback.format_exc()]
    output  = '\n'.join(output)
    print output
    with open(DEFAULT_CRASHLOG,'a') as f:
        f.write(output)

#============================ body ============================================

class AppData(object):
    '''
    Singleton that holds the data local to this application.
    '''
    _instance = None
    _init     = False
    def __new__(cls, *args, **kwargs):
        if not cls._instance:
            cls._instance = super(AppData,cls).__new__(cls, *args, **kwargs)
        return cls._instance
    def __init__(self):
        if self._init:
            return
        self._init      = True
        self.dataLock   = threading.RLock()
        self.data       = []
        self.data.append(['activity type' , 'number', 'last']) # header
    def update(self,notifName):
        with self.dataLock:
            # format of data:
            # [
            #     ['activity type', 'number',                          'last'],
            #     [         'data',      111, 'Thu, 28 Jan 2016 14:47:16 UTC'],
            #     [       'ipdata',      222, 'Thu, 28 Jan 2016 14:47:16 UTC'],
            # ]
            
            # find notifName row
            found=False
            for row in self.data:
                if row[0]==notifName:
                   found=True
                   break
            # create row if needed
            if not found:
                self.data.append([notifName,0,0])
                row = self.data[-1]
            # update columns
            row[1] += 1
            row[2]  = currentUtcTime()
    def get(self):
        with self.dataLock:
            return copy.deepcopy(self.data)

class SnapshotThread(threading.Thread):
    
    SNAPSHOT_DELAY_S    = 5       # delay, in seconds, before the FIRST snaphot
    SNAPSHOT_PERIOD_S   = 5*60    # number of seconds BETWEEN snapshots
    
    def __init__(self,connector):
        
        # store params
        self.connector                 = connector
        
        # local variables
        self.goOn                      = True
        self.dataLock                  = threading.RLock()
        self.delayCounter              = self.SNAPSHOT_DELAY_S
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
                        self.delayCounter   = self.SNAPSHOT_PERIOD_S
                    else:
                        doSnapshot          = False
                
                # snapshot
                if doSnapshot:
                    self._doSnapshot()
        
        except Exception as err:
            logCrash(err)
    
    #======================== public ==========================================
    
    def close(self):
        
        with self.dataLock:
            self.goOn = False
    
    #======================== private =========================================
    
    def _doSnapshot(self):
        
        try:
            with self.dataLock:
                
                motes                 = []
                moteConfig            = []
                moteInfo              = []
                links                 = []
                
                # getMoteConfig on all motes
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
                        moteConfig   += [dict(res._asdict())]
                
                # getMoteInfo on all motes
                for mac in motes:
                    res               = self.connector.dn_getMoteInfo(mac)
                    moteInfo         += [dict(res._asdict())]
                
                # get path info on all paths of all motes
                for mac in motes:
                    currentPathId  = 0
                    continueAsking = True
                    while continueAsking:
                        try:
                            res        = self.connector.dn_getNextPathInfo(mac,0,currentPathId)
                            fromMAC    = tuple(res.source)
                            toMAC      = tuple(res.dest)
                            quality    = res.quality
                            links += [{
                                'fromMAC': fromMAC,
                                'toMAC': toMAC,
                                'quality': quality,
                            }]
                        except APIError:
                            continueAsking = False
                        else:
                            currentPathId  = res.pathId
                
                # activitylog
                now = currentUtcTime()
                activitylog.info('[{0}] [moteConfig] {1}'.format(
                        now,
                        json.dumps(moteConfig),
                    ),
                )
                activitylog.info('[{0}] [moteInfo] {1}'.format(
                        now,
                        json.dumps(moteInfo),
                    ),
                )
                activitylog.info('[{0}] [topology] {1}'.format(
                        now,
                        json.dumps(links),
                    ),
                )
                
                # update data
                AppData().update('snaphot')
        
        except Exception as err:
            logCrash(err)

class NotifThread(object):
    
    def __init__(self, connector, disconnectedCallback):
        
        # store params
        self.connector = connector
        self.disconnectedCallback = disconnectedCallback
        
        # variables
        self.hrParser  = HrParser.HrParser()
        
        # activitylog
        activitylog.info("[{0}] [startLogging]".format(currentUtcTime()))
        
        # subscriber
        self.subscriber = IpMgrSubscribe.IpMgrSubscribe(self.connector)
        self.subscriber.start()
        self.subscriber.subscribe(
            notifTypes =    [
                IpMgrSubscribe.IpMgrSubscribe.ERROR,
                IpMgrSubscribe.IpMgrSubscribe.FINISH,
            ],
            fun =           self.disconnectedCallback,
            isRlbl =        False,
        )
        self.subscriber.subscribe(
            notifTypes  =   [
                IpMgrSubscribe.IpMgrSubscribe.NOTIFEVENT,
                IpMgrSubscribe.IpMgrSubscribe.NOTIFDATA,
                IpMgrSubscribe.IpMgrSubscribe.NOTIFIPDATA,
                IpMgrSubscribe.IpMgrSubscribe.NOTIFHEALTHREPORT,
            ],
            fun =           self._notifCallback,
            isRlbl =        False,
        )
    
    #======================== public ==========================================
    
    def close(self):
        
        # activitylog
        activitylog.info("[{0}] [stopLogging]".format(currentUtcTime()))
        
        self.connector.disconnect()
    
    #======================== private =========================================
    
    def _notifCallback(self, notifName, notifParams):
        
        try:
            
            # activitylog
            activitylog.info('[{0}] [{1}] {2}'.format(
                    currentUtcTime(),
                    notifName,
                    json.dumps(notifParams._asdict()),
                ),
            )
            
            # update data
            AppData().update(notifName)
            
        except Exception as err:
            logCrash(err)

class HrListenerGui(object):
    
    def __init__(self):
        
        # variables
        self.guiLock         = threading.Lock()
        self.apiDef          = IpMgrDefinition.IpMgrDefinition()
        self.notifThread     = None
        self.snapshotThread  = None
        
        # create window
        self.window = dustWindow.dustWindow(
            'Timelapse',
            self._windowCb_close,
        )
        
        # add a connection frame
        self.connectionFrame = dustFrameConnection.dustFrameConnection(
            self.window,
            self.guiLock,
            self._connectionFrameCb_connected,
            frameName="manager connection",
            row=0,column=0
        )
        self.connectionFrame.apiLoaded(self.apiDef)
        self.connectionFrame.show()
        
        # add a table frame
        self.tableFrame = dustFrameTable.dustFrameTable(
            self.window,
            self.guiLock,
            frameName="network activity",
            row=1,column=0,
        )
        self.tableFrame.show()
    
    #======================== public ==========================================
    
    def start(self):
        '''
        This command instructs the GUI to start executing and reacting to 
        user interactions. It never returns and should therefore be the last
        command called.
        '''
        try:
            self.window.mainloop()
        except SystemExit:
            sys.exit()
    
    #======================== private =========================================
    
    def _windowCb_close(self):
        if self.notifThread:
            self.notifThread.close()
        if self.snapshotThread:
            self.snapshotThread.close()
    
    def _connectionFrameCb_connected(self,connector):
        '''
        \brief Called when the connectionFrame has connected.
        '''
        
        # store the connector
        self.connector = connector
        
        # schedule the GUI to update itself in GUIUPDATEPERIOD ms
        self.tableFrame.after(GUIUPDATEPERIOD,self._updateTable)
        
        # start threads
        self.notifThread     = NotifThread(
            self.connector,
            self._connectionFrameCb_disconnected
        )
        self.snapshotThread  = SnapshotThread(
            self.connector,
        )
    
    def _connectionFrameCb_disconnected(self,notifName,notifParams):
        '''
        \brief Called when the connectionFrame has disconnected.
        '''
        
        # update the GUI
        self.connectionFrame.updateGuiDisconnected()
        
        # end threads
        self.notifThread.close()
        
        # delete the connector
        self.connector = None
    
    def _updateTable(self):
        
        # get the data
        dataToPlot = AppData().get()
        
        # update the frame
        self.tableFrame.update(dataToPlot)
        
        # schedule the next update
        self.tableFrame.after(GUIUPDATEPERIOD,self._updateTable)

#============================ main ============================================

def main():
    hrListenerGui = HrListenerGui()
    hrListenerGui.start()

if __name__ == '__main__':
    main()
