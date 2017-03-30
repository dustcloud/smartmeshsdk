#!/usr/bin/python

#============================ adjust path =====================================

import sys
import os
if __name__ == "__main__":
    here = sys.path[0]
    sys.path.insert(0, os.path.join(here, '..', '..','libs'))
    sys.path.insert(0, os.path.join(here, '..', '..','external_libs'))

#============================ imports =========================================

import os
import copy
import time
import string
import random
import threading
import traceback
import json

import requests
import bottle

from SmartMeshSDK                      import sdk_version

#============================ define ==========================================

#============================ helpers =========================================

def formatVersion():
    return 'SmartMesh SDK {0}'.format('.'.join([str(v) for v in sdk_version.VERSION]))

def currentUtcTime():
    return time.strftime("%a, %d %b %Y %H:%M:%S UTC", time.gmtime())

def logError(err):
    output  = []
    output += ["============================================================="]
    output += [currentUtcTime()]
    output += [""]
    output += ["ERROR!"]
    output += [""]
    output += ["=== exception type ==="]
    output += [str(type(err))]
    output += [""]
    output += ["=== traceback ==="]
    output += [traceback.format_exc()]
    output  = '\n'.join(output)
    
    print output

#============================ classes =========================================

class AppData(object):
    
    BACKUP_FILE = 'backup.json'
    
    _instance   = None
    _init       = False
    
    def __new__(cls, *args, **kwargs):
        if not cls._instance:
            cls._instance = super(AppData, cls).__new__(cls, *args, **kwargs)
        return cls._instance
    
    def __init__(self):
        
        # singleton patterm
        if self._init:
            return
        self._init = True
        
        # local variables
        self.dataGeneration       = 0
        self.dataLock             = threading.RLock()
        self.data                 = {}
        self.statsLock            = threading.RLock()
        self.stats                = {}
    
    # ======================= public ==========================================
    
    # === data
    
    def getDataGeneration(self):
        with self.dataLock:
            return self.dataGeneration
    
    def set(self,k,v):
        with self.dataLock:
            self.data[k]          = v
            self.dataGeneration  += 1
    
    def get(self,k):
        with self.dataLock:
            return copy.deepcopy(self.data[k])
    
    # === stats
    
    def setStats(self,k,v):
        with self.statsLock:
            self.stats[k]         = v
    
    def incrStats(self,k):
        with self.statsLock:
            try:
                self.stats[k]    += 1
            except KeyError:
                self.stats[k]     = 1
    
    def getStats(self):
        with self.dataLock:
            return copy.deepcopy(self.stats)
    
    # === backup
    
    def dumpBackup(self):
        with open(self.BACKUP_FILE,'w') as f:
            with self.dataLock:
                f.write(json.dumps(self.data))
    
    def loadBackup(self):
        with open(self.BACKUP_FILE,'r') as f:
            with self.dataLock:
                self.data              = json.loads(f.read())
                self.dataGeneration   += 1

class DataGatherer(threading.Thread):
    
    SNAPSHOT_PERIOD_S                  = 5*60
    
    def __init__(self,testMode=False):
        
        # store params
        self.testMode                  = testMode
        
        # local variables
        self.token                     = 0
        self.dataLock                  = threading.RLock()
        self.delaySnapshot             = 0
        
        # initialize AppData
        if self.testMode:
            AppData().loadBackup()
        else:
            AppData().set('motes',[])
            AppData().set('paths',[])
            AppData().setStats("starttime",currentUtcTime())
        
        # start thread
        threading.Thread.__init__(self)
        self.name = 'DataGatherer'
        self.start()
    
    def run(self):
        while True:
            try:
                if self.delaySnapshot==0:
                    if not self.testMode:
                        self._doSnapshot()
                    self.delaySnapshot = self.SNAPSHOT_PERIOD_S
                self.delaySnapshot -= 1
                time.sleep(1)
            except Exception as err:
                logError(err)
    
    def snapshotNow(self):
        self.delaySnapshot = 0
    
    def _doSnapshot(self):
        
        motes = []
        paths = []
        
        # update stats
        AppData().setStats("snapshotOngoing",True)
        AppData().incrStats("numSnapshots")
        
        # print
        print 'start snapshot'
        
        # record start time
        snapShotStartTime = time.time()
        
        # retrieve list of managers
        # TODO: retrieve list of managers from JsonServer
        managers = ['TODO']
        
        # loop through managers
        for manager in managers:
            
            thismanagermotes = []
            thismanagerpaths = []
            
            try:
                
                # loop through motes
                currentMacAddress = "00-00-00-00-00-00-00-00"
                while True:
                    print '   getMoteConfig {0}'.format(currentMacAddress)
                    temp = requests.post(
                        'http://127.0.0.1:8080/api/v1/raw',
                        json = {
                            "manager": 0,
                            "command": "getMoteConfig",
                            "fields": {
                                "macAddress": currentMacAddress,
                                "next":       True,
                            }
                        },
                    ).json()
                    if temp['RC']!=0:
                        break
                    temp['manager']    = manager
                    thismanagermotes  += [temp]
                    currentMacAddress  = temp["macAddress"]
                
                # loop through paths
                for macAddress in [m["macAddress"] for m in thismanagermotes]:
                    pathId = 0
                    while True:
                        print '   getNextPathInfo {0} {1}'.format(macAddress,pathId)
                        temp = requests.post(
                            'http://127.0.0.1:8080/api/v1/raw',
                            json = {
                                "manager": 0,
                                "command": "getNextPathInfo",
                                "fields": {
                                    "macAddress": macAddress,
                                    "filter":     0,
                                    "pathId":     pathId
                                }
                            },
                        ).json()
                        if temp['RC']!=0:
                            break
                        temp['manager']     = manager
                        thismanagerpaths   += [temp]
                        pathId             += 1
            
            except IOError as err:
                print str(err)
            else:
                motes  += thismanagermotes
                paths  += thismanagerpaths
        
        # store in AppData
        AppData().set('motes',motes)
        AppData().set('paths',paths)
        
        # back up the data
        AppData().dumpBackup()
        
        # compute snapshot duration
        snapShotDuration = time.time()-snapShotStartTime
        
        # print
        print 'end snapshot (took {0} s)'.format(int(snapShotDuration))
        
        # update stats
        AppData().setStats("snapshotOngoing",False)
        AppData().setStats("durationLastSnapshot",snapShotDuration)
    
    def _deviceevent_cb(self,event):
        '''
        {
            'manager':       'COM17',
            'name':          'eventMoteOperational',
            'fields': {
                'eventId':   51,
                'macAddress':'00-17-0d-00-00-38-06-c9',
            },
        }
        
        events when mote joins for the first time:
            . eventMoteCreate
            . eventMoteJoin
            . eventPathCreate
            . eventMoteOperational
        events when mote is switch off (after a couple of minutes)
            . eventPathDelete
            . eventMoteLost
        events when mote is power cycled
            . eventPathDelete
            . eventMoteJoin
            . eventPathCreate
            . eventMoteOperational
        '''
        
        # update stats
        AppData().incrStats("num{0}".format(event['name']))
        
        print '{0} {1}'.format(event['manager'],event['name'])
        
        if event['name'] in [
                "eventMoteCreate",
                "eventMoteJoin",
                "eventMoteOperational",
                "eventMoteLost",
            ]:
            '''
            eventMoteCreate:
                {
                    'd': {
                        'eventId': 10,
                        'macAddress': u'00-17-0d-00-00-38-03-ca',
                        'moteId': 4,
                    }
                }
            eventMoteJoin:
            eventMoteOperational:
            eventMoteLost:
                {
                    'd': {
                        'eventId': 8,
                        'macAddress': '00-17-0d-00-00-38-07-18',
                    },
                }
            '''
            
            # infer new state of the motes
            if   event['name']=="eventMoteCreate":
                moteState = 0
            elif event['name']=="eventMoteJoin":
                moteState = 1
            elif event['name']=="eventMoteOperational":
                moteState = 4
            elif event['name']=="eventMoteLost":
                moteState = 0
            else:
                raise SystemError()
            
            # update motes
            motes       = AppData().get('motes')
            simpleMotes = [(m['manager'],m['macAddress']) for m in motes]
            try:
                idx = simpleMotes.index((event['manager'],event['fields']['macAddress']))
            except ValueError:
                # Not in there! All good, add.
                motes += [
                    {
                        'macAddress':     event['fields']['macAddress'],
                        'reserved':       1,
                        'state':          moteState,
                        'isRouting':      None,
                        'moteId':         None,
                        'isAP':           False,
                        'manager':        event['manager'],
                    }
                ]
            else:
                # Already in there! All good, update.
                motes[idx]['state'] = moteState
            AppData().set('motes',motes)
            
            # delete all paths involving that mote on other managers
            if event['name'] in ["eventMoteCreate","eventMoteJoin","eventMoteOperational"]:
                self._deletePaths(
                    moteA         = event['fields']['macAddress'],
                    exceptManager = event['manager'],
                )
            
            # delete all paths involving that (manager,mote) if eventMoteLost
            if event['name']=="eventMoteLost":
                self._deletePaths(
                    moteA         = event['fields']['macAddress'],
                    manager       = event['manager'],
                )
        
        elif event['name']=="eventPathCreate":
            '''
            {
                'd': {
                    'eventId': 17,
                    'source': u'00-17-0d-00-00-38-03-69',
                    'direction': 2,
                    'dest': u'00-17-0d-00-00-58-2f-e4',
                },
            }
            '''
            newPath = {
                'direction':      event['fields']['direction'],
                'dest':           event['fields']['dest'],
                'rssiDestSrc':    None,
                'source':         event['fields']['source'],
                'pathId':         None,
                'numLinks':       None,
                'quality':        None,
                'rssiSrcDest':    None,
                'manager':        event['manager'],
            }
            paths = AppData().get('paths')
            simplePaths = [(p['source'],p['dest'],p['direction']) for p in paths]
            try:
                idx = simplePaths.index((newPath['source'],newPath['dest'],newPath['direction']))
            except ValueError:
                # not in there yet, all good
                paths += [newPath]
            else:
                # already in there! replace
                print 'WARNING: eventPathCreate for a path that already exists!'
                paths[idx] = newPath
            AppData().set('paths',paths)
        
        elif event['name']=="eventPathDelete":
            '''
            {
                'd': {
                    'eventId': 14,
                    'source': '00-17-0d-00-00-58-2f-e4',
                    'direction': 2,
                    'dest': u'00-17-0d-00-00-38-03-69',
                },
            }
            Note: a path delete event means that there are no more resources
                  scheduled between the two nodes. Regardless of which node
                  is "source" and which node in "dest", the right behavior
                  when this event is received is to delete both A->B and B->A
                  paths.
            '''
            self._deletePaths(
                moteA   = event['fields']['source'],
                moteB   = event['fields']['dest'],
                manager = event['manager'],
            )
        
        else:
            raise SystemError('unexpected event')
    
    def _deletePaths(self,moteA,moteB=None,manager=None,exceptManager=None):
    
        paths = AppData().get('paths')
        numberOfPathsDeleted = 0
        
        # loop through paths
        while True:
            found = False
            for idx in range(len(paths)):
                
                if   (moteB==None and manager!=None and exceptManager==None):
                    '''
                    delete all paths which have moteA as either 'source' or 'dest'
                    for manager 'manager'
                    '''
                    condition = (
                        paths[idx]['manager']         == manager
                        and
                        (
                            paths[idx]['source']      == moteA
                            or
                            paths[idx]['dest']        == moteA
                        )
                    )
                elif (moteB==None and manager==None and exceptManager!=None):
                    '''
                    delete all paths which have moteA as either 'source' or 'dest'
                    except for manager 'exceptManager'
                    '''
                    condition = (
                        paths[idx]['manager']         != exceptManager
                        and
                        (
                            paths[idx]['source']      == moteA
                            or
                            paths[idx]['dest']        == moteA
                        )
                    )
                elif (moteB!=None and manager!=None and exceptManager==None):
                    '''
                    delete all moteA->moteB or moteB->moteA paths
                    for manager 'manager'
                    '''
                    condition = (
                        paths[idx]['manager']         == manager
                        and
                        (
                            (
                                paths[idx]['source']  == moteA
                                and
                                paths[idx]['dest']    == moteB
                            )
                            or
                            (
                                paths[idx]['source']  == moteB
                                and
                                paths[idx]['dest']    == moteA
                            )
                        )
                    )
                else:
                    raise SystemError()
                
                if condition:
                    found = True
                    paths.pop(idx)
                    numberOfPathsDeleted += 1
                    break
            if not found:
                break
        
        AppData().set('paths',paths)

class WebServer(object):
    
    HUB_LABEL = 'JsonServer'
    
    def __init__(self,dataGatherer):
        
        # store params
        self.dataGatherer    = dataGatherer
        
        # local variables
        self.dataGeneration  = None
        self.topology        = ''
        
        # start web server
        self.websrv   = bottle.Bottle()
        self.websrv.route('/',                   'GET',    self._webhandle_root_GET)
        self.websrv.route('/static/<path:path>', 'GET',    self._webhandle_static_GET)
        self.websrv.route('/event',              'POST',   self._webhandle_event_POST)
        self.websrv.route('/topology.json',      'GET',    self._webhandle_topology_GET)
        self.websrv.route('/snapshot',           'GET',    self._webhandle_snapshot_GET)
        self.websrv.route('/stats',              'GET',    self._webhandle_stats_GET)
        webthread = threading.Thread(
            target = self.websrv.run,
            kwargs = {
                'host'          : '0.0.0.0',
                'port'          : int(os.getenv('PORT', '8081')),
                'quiet'         : True,
                'debug'         : False,
            }
        )
        webthread.start()
    
    def _webhandle_root_GET(self):
        return bottle.template(
            'index',
            pagetitle   = 'SeeTheMesh',
            version     = formatVersion(),
        )
    
    def _webhandle_static_GET(self,path):
        return bottle.static_file(path,root='./static')
    
    def _webhandle_event_POST(self):
        self.dataGatherer._deviceevent_cb(bottle.request.json)
    
    def _webhandle_topology_GET(self):
        
        # avoid redrawing the topology is AppData hasn't changed
        dataGeneration = AppData().getDataGeneration()
        if dataGeneration!=self.dataGeneration:
            self.dataGeneration = dataGeneration
            self.topology = self._formatTopology()
        return self.topology
    
    def _webhandle_snapshot_GET(self):
        self.dataGatherer.snapshotNow()
        return 'Snapshot starting now'
    
    def _webhandle_stats_GET(self):
        return AppData().getStats()
    
    def _formatTopology(self):
        '''
        motes: [
            {
                'macAddress':     '00-17-0d-00-00-58-2f-e4',
                'reserved':       1,
                'state':          4,
                'isRouting':      True,
                'moteId':         1,
                'isAP':           True,
                'manager':        '00-17-0d-00-00-58-2f-e4',
            },
        ]
        paths: [
            {
                'direction':      3,
                'dest':           '00-17-0d-00-00-38-07-18',
                'rssiDestSrc':    0,
                'source':         '00-17-0d-00-00-58-2f-e4',
                'pathId':         3,
                'numLinks':       2,
                'quality':        74,
                'rssiSrcDest':    0,
                'manager':        '00-17-0d-00-00-58-2f-e4',
            },
        ]
        '''
        
        returnVal = {}
        
        #=== add nodes
        returnVal['nodes'] = []
        motes = AppData().get('motes')
        # operational motes
        for mote in motes:
            if mote['state']==0: # 0==lost
                continue
            if mote['macAddress'][-8:] in [n['label'] for n in returnVal['nodes']]:
                continue
            if   mote['isAP']:
                style = "fill: #9cd9ec"
            elif mote['state']==1:
                style = "fill: #dddddd"
            else:
                style = ""
            returnVal['nodes'] += [
                {
                    'label':     mote['macAddress'][-8:],
                    'hovertext': '',
                    'style':     style,
                }
            ]
        # hub
        returnVal['nodes'] += [
            {
                'label':     self.HUB_LABEL,
                'hovertext': '',
                'style':     "fill: #00b198",
            }
        ]
        
        #=== add links
        returnVal['links'] = []
        paths      = AppData().get('paths')
        nodelabels = [n['label'] for n in returnVal['nodes']]
        # upstream paths
        for path in paths:
            if path['direction']!=2: # 2==upstream
                continue
            try:
                returnVal['links'] += [
                    {
                        'sourceidx': nodelabels.index(path['source'][-8:]),
                        'destidx':   nodelabels.index(path['dest'][-8:]),
                        'style':     "",
                    }
                ]
            except ValueError:
                # happens when an eventMoteLost is received before the
                # eventPathDelete events for all the paths it's involved
                # in
                pass
        # links between managers and the hub
        for mote in motes:
            if mote['isAP']:
                returnVal['links'] += [
                    {
                        'sourceidx': nodelabels.index(mote['macAddress'][-8:]),
                        'destidx':   nodelabels.index(self.HUB_LABEL),
                        'style':     "",
                    }
                ]
        
        return returnVal

#============================ main =======================================

def main():
    print 'SeeTheMesh - {0}'.format(formatVersion())
    testMode       = False
    dataGatherer   = DataGatherer(testMode)
    webServer      = WebServer(dataGatherer)

if __name__=="__main__":
    main()
