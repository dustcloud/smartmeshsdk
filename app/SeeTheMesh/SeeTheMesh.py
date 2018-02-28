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
import os
import copy
import time
import string
import random
import threading
import traceback
import argparse
import json
import pprint
import socket

# requirements
import requests
import bottle

# SmartMeshSDK
from SmartMeshSDK            import sdk_version
from SmartMeshSDK.utils      import JsonManager

# DustCli
from dustCli                 import DustCli

#============================ define ==========================================

# default TCP port to listen to
DFLT_TCPPORT = 8081

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

pp = pprint.PrettyPrinter(indent=4)

#============================ classes =========================================

class AppData(object):
    '''
    {
        "motes": [
            {
                # added by this app
                "manager":        "COM3",
                # fields from "getMoteConfig" section of snapshot
                "RC":             0,
                "macAddress":     "00-17-0d-00-00-30-5d-39",
                "moteId":         1,
                "state":          4,
                "isAP":           true,
                "isRouting":      true,
                "reserved":       1,
            },
        ]
        "paths": [
            {
                # added by this app
                "manager":        "COM3",
                # fields from "getPathInfo" section of snapshot
                "RC":             0,
                "pathId":         2,
                "source":         "00-17-0d-00-00-30-5d-39",
                "dest":           "00-17-0d-00-00-38-03-ca",
                "direction":      3,
                "rssiSrcDest":    0,
                "rssiDestSrc":    0,
                "numLinks":       2,
                "quality":        74,
            },
            ...
        ],
        "map": {
            'centerlat':          123,
            'centerlng':          123,
            'zoom':               123,
        },
    }
    '''
    
    # singleton pattern
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
    
    #=== generation
    
    def getDataGeneration(self):
        with self.dataLock:
            return self.dataGeneration
    
    def bumpDataGeneration(self):
        with self.dataLock:
            self.dataGeneration += 1
    
    def append(self,k,v):
        with self.dataLock:
            self.data[k] += v
            self.dataGeneration  += 1
    
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

class LatLngFile(object):
    '''
    {
        "map":                     {
            'centerlat': 0,
            'centerlng': 0,
            'zoom':      0,
        },
        "box":                     [0,0],
        "hub":                     [0,0],
        "11-11-11-11-11-11-11-11": [0,0],
        "22-22-22-22-22-22-22-22": [0,0],
        ...
    }
    '''
    BACKUP_FILE         = 'latlng.json'
    DFLT_MAP_CENTERLAT  =             0
    DFLT_MAP_CENTERLNG  =             0
    DFLT_MAP_ZOOM       =             3
    DFLT_BOX_LAT        =     37.594206 # Union City
    DFLT_BOX_LNG        =   -122.044215
    DFLT_HUB_LAT        =     51.501181 # London
    DFLT_HUB_LNG        =     -0.142427
    
    # singleton pattern
    _instance      = None
    _init          = False
    def __new__(cls, *args, **kwargs):
        if not cls._instance:
            cls._instance = super(LatLngFile, cls).__new__(cls, *args, **kwargs)
        return cls._instance
    
    def __init__(self):
        
        # singleton pattern
        if self._init:
            return
        self._init = True
        
        # local variables
        self.dataLock             = threading.RLock()
        self.data                 = {}
        try:
            self.loadBackup()
        except IOError:
            self._set('hub',self.DFLT_HUB_LAT,self.DFLT_HUB_LNG)
            self._set('box',self.DFLT_BOX_LAT,self.DFLT_BOX_LNG)
    
    # ======================= public ==========================================
    
    # === map lat/lng/zoom
    
    def getMap(self):
        with self.dataLock:
            if 'map' not in self.data:
                self.setMap(
                    self.DFLT_MAP_CENTERLAT,
                    self.DFLT_MAP_CENTERLNG,
                    self.DFLT_MAP_ZOOM,
                )
            return copy.deepcopy(self.data['map'])
    def setMap(self,centerlat,centerlng,zoom):
        with self.dataLock:
            self.data['map'] = {
                'centerlat': centerlat,
                'centerlng': centerlng,
                'zoom':      zoom,
            }
    
    # === box/hub/mote lat/lng
    
    def getBox(self):
        return self._get('box')
    def setBox(self,lat,lng):
        self._set('box',lat,lng)
    
    def getHub(self):
        return self._get('hub')
    def setHub(self,lat,lng):
        self._set('hub',lat,lng)
    
    def getMote(self,mac):
        return self._get(mac)
    def setMote(self,mac,lat,lng):
        self._set(mac,lat,lng)
    
    # === backup
    
    def loadBackup(self):
        with open(self.BACKUP_FILE,'r') as f:
            with self.dataLock:
                self.data              = json.loads(f.read())
    
    def dumpBackup(self):
        with open(self.BACKUP_FILE,'w') as f:
            with self.dataLock:
                f.write(json.dumps(self.data))
    
    # ======================= private =========================================
    
    def _get(self,k):
        with self.dataLock:
            if k not in self.data:
                self._set(
                    k,
                    self.getBox()[0],
                    self.getBox()[1],
                )
            return copy.deepcopy(self.data[k])
    
    def _set(self,k,lat,lng):
        with self.dataLock:
            if k not in self.data:
                self.data[k] = {}
            self.data[k] = [lat,lng]
        self.dumpBackup()

class DataGatherer(threading.Thread):
    
    SNAPSHOT_PERIOD_S             = 10
    
    def __init__(self):
        
        # local variables
        self.delaySnapshot        = 1 # wait for banners before first snapshot
        self.goOn                 = True
        
        # initialize AppData
        AppData().set('motes',[])
        AppData().set('paths',[])
        
        # start thread
        threading.Thread.__init__(self)
        self.name = 'DataGatherer'
        self.start()
    
    def run(self):
        while self.goOn:
            try:
                if self.delaySnapshot==0:
                    self._triggerSnapshots()
                    self.delaySnapshot = self.SNAPSHOT_PERIOD_S
                self.delaySnapshot -= 1
                time.sleep(1)
            except Exception as err:
                logError(err)
    
    #======================== public ==========================================
    
    def snapshotNow(self):
        self.delaySnapshot = 0
    
    def close(self):
        self.goOn = False
    
    #======================== private =========================================
    
    # === abstract methods
    
    def getStatus(self):
        raise NotImplementedError() # to be defined by subclass
    
    def _triggerSnapshots(self):
        raise NotImplementedError() # to be defined by subclass
    
    # === private
    
    # notifications from networks
    
    def _snapshot_cb(self,snapshot):
        '''
        contained in the snapshot:
        {
            // metadata
            
            u'manager':         'COM11',
            u'valid':           True,
            
            'snapshot': {
            
                u'timestamp_start': u'Wed, 28 Jun 2017 10:07:00 UTC',
                u'timestamp_stop':  u'Wed, 28 Jun 2017 10:07:00 UTC'},
                'epoch_stop':       1498644420.962,
                
                // general
                
                u'getSystemInfo': {
                    u'RC': 0,
                    u'hwModel': 16,
                    u'hwRev': 1,
                    u'macAddress': u'00-17-0d-00-00-30-5d-39',
                    u'swBuild': 9,
                    u'swMajor': 1,
                    u'swMinor': 4,
                    u'swPatch': 1
                },
                'getNetworkInfo': {
                    u'RC': 0,
                    u'advertisementState': 0,
                    u'asnSize': 7250,
                    u'downFrameState': 1,
                    u'ipv6Address': u'fe80:0000:0000:0000:0017:0d00:0030:5d39',
                    u'maxNumbHops': 3,
                    u'netLatency': 700,
                    u'netPathStability': 99,
                    u'netReliability': 100,
                    u'netState': 0,
                    u'numArrivedPackets': 995,
                    u'numLostPackets': 0,
                    u'numMotes': 3
                },
                'getNetworkConfig': {
                    u'RC': 0,
                    u'apTxPower': 8,
                    u'autoStartNetwork': True,
                    u'baseBandwidth': 9000,
                    u'bbMode': 0,
                    u'bbSize': 1,
                    u'bwMult': 300,
                    u'ccaMode': 0,
                    u'channelList': 32767,
                    u'downFrameMultVal': 1,
                    u'frameProfile': 1,
                    u'isRadioTest': 0,
                    u'locMode': 0,
                    u'maxMotes': 101,
                    u'networkId': 430,
                    u'numParents': 2,
                    u'oneChannel': 255
                },
                
                // motes
                
                'getMoteInfo': {
                    '00-17-0d-00-00-30-5d-39': {
                        u'RC': 0,
                        u'assignedBw': 0,
                        u'avgLatency': 0,
                        u'hopDepth': 0,
                        u'macAddress': u'00-17-0d-00-00-30-5d-39',
                        u'numGoodNbrs': 3,
                        u'numJoins': 1,
                        u'numNbrs': 3,
                        u'packetsLost': 0,
                        u'packetsReceived': 12,
                        u'requestedBw': 61770,
                        u'state': 4,
                        u'stateTime': 11226,
                        u'totalNeededBw': 2472
                    },
                    ...
                },
                'getMoteConfig': {
                    '00-17-0d-00-00-30-5d-39': {
                        'RC': 0,
                        u'isAP': True,
                        u'isRouting': True,
                        u'macAddress': u'00-17-0d-00-00-30-5d-39',
                        u'moteId': 1,
                        u'reserved': 1,
                        u'state': 4,
                    },
                    ...
                },
                
                // links
                
                'getMoteLinks': {
                    '00-17-0d-00-00-30-5d-39': {
                        'RC': 0,
                        u'utilization': 1
                        u'links': [
                            {
                                'channelOffset': 1,
                                u'flags': 2,
                                u'frameId': 1,
                                u'moteId': 2,
                                u'slot': 241
                            },
                            ...
                        ],
                    },
                    ...
                },
                
                // paths
                
                u'getPathInfo': {
                    u'00-17-0d-00-00-30-5d-39': {
                        u'0': {
                            u'RC': 0,
                            u'dest': u'00-17-0d-00-00-38-06-f0',
                            u'direction': 3,
                            u'numLinks': 2,
                            u'pathId': 2,
                            u'quality': 97,
                            u'rssiDestSrc': -46,
                            u'rssiSrcDest': 0,
                            u'source': u'00-17-0d-00-00-30-5d-39'
                        },
                        ...
                    },
                    ...
                }
            }
        }
        '''
        
        # update stats
        AppData().incrStats("numRxSnapshot")
        
        # abort if snapshot invalid
        if snapshot['valid']==False:
            # update stats
            AppData().incrStats("numRxSnapshotInvalid")
            return
        
        AppData().incrStats("numRxSnapshotValid")
        
        #=== motes
        # getMoteConfig from snapshot
        motes = [v for (k,v) in snapshot['snapshot']['getMoteConfig'].items()]
        # metadata
        for m in motes:
            m['manager'] = snapshot['manager']
        
        #=== paths
        paths = []
        # getPathInfo from snapshot
        for (mac,pi) in snapshot['snapshot']['getPathInfo'].items():
            paths += pi.values()
        # metadata
        for p in paths:
            p['manager'] = snapshot['manager']
        
        # store in AppData
        self._deleteMotes(manager=snapshot['manager'])
        AppData().append('motes',motes)
        self._deletePaths(manager=snapshot['manager'])
        AppData().append('paths',paths)
    
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
                        # added by this app
                        'manager':        event['manager'],
                        # simplified entry, mimicking the snapshot data
                        'macAddress':     event['fields']['macAddress'],
                        'reserved':       1,
                        'state':          moteState,
                        'isRouting':      None,
                        'moteId':         None,
                        'isAP':           False,
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
                # added by this app
                'manager':        event['manager'],
                # simplified entry, mimicking the snapshot data
                'direction':      2, # hardcoding the path direction to upstream
                'dest':           event['fields']['dest'],
                'rssiDestSrc':    None,
                'source':         event['fields']['source'],
                'pathId':         None,
                'numLinks':       None,
                'quality':        None,
                'rssiSrcDest':    None,
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
                manager = event['manager'],
                moteA   = event['fields']['source'],
                moteB   = event['fields']['dest'],
            )
        
        else:
            raise SystemError('unexpected event')
    
    # deleters
    
    def _deleteMotes(self,manager):
        motes = AppData().get('motes')
        numberOfMotesDeleted = 0
        
        # loop through motes
        while True:
            found = False
            for idx in range(len(motes)):
                if  motes[idx]['manager']== manager:
                    found = True
                    motes.pop(idx)
                    numberOfMotesDeleted += 1
                    break
            if not found:
                break
        
        AppData().set('motes',motes)
    
    def _deletePaths(self,moteA=None,moteB=None,manager=None,exceptManager=None):
    
        paths = AppData().get('paths')
        numberOfPathsDeleted = 0
        
        # loop through paths
        while True:
            found = False
            for idx in range(len(paths)):
                
                if   (moteA==None and moteB==None and manager!=None and exceptManager==None):
                    '''
                    delete all paths from for manager 'manager'
                    '''
                    condition = (
                        paths[idx]['manager']         == manager
                    )
                elif (moteA!=None and moteB==None and manager!=None and exceptManager==None):
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
                elif (moteA!=None and moteB==None and manager==None and exceptManager!=None):
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
                elif (moteA!=None and moteB!=None and manager!=None and exceptManager==None):
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

class DataGatherer_JsonServer(DataGatherer):
    def __init__(self):
        # initialize parent class
        super(DataGatherer_JsonServer,self).__init__()
        # local variables
        self.status = {
            'mode': 'JsonServer',
        }
    def getStatus(self):
        return self.status
    def _triggerSnapshots(self):
        try:
            # step 1. get list of managers
            r = requests.get(
                'http://127.0.0.1:8080/api/v1/status',
            )
            managers = [k for (k,v) in r.json()['managers'].items() if v=='connected']
            # step 2. trigger snapshots for each
            for m in managers:
                r = requests.post(
                    'http://127.0.0.1:8080/api/v1/helpers/snapshot',
                    json = {
                        "manager": m,
                    },
                )
        except requests.exceptions.ConnectionError:
            self.status['connectionToJsonServer'] = 'down'
        else:
            self.status['connectionToJsonServer'] = 'up'

class DataGatherer_serial(DataGatherer):
    def __init__(self):
        
        # initialize parent class
        super(DataGatherer_serial,self).__init__()
        
        # instantiate a JsonManager
        self.jsonManager          = JsonManager.JsonManager(
            autoaddmgr            = True,
            autodeletemgr         = True,
            serialport            = None,
            configfilename        = None,
            notifCb               = self._notif_cb,
        )
    def getStatus(self):
        returnVal = self.jsonManager.status_GET()
        assert 'mode' not in returnVal
        returnVal['mode'] = 'serial'
        return returnVal
    def _triggerSnapshots(self):
        # step 1. get list of managers
        r = self.jsonManager.status_GET()
        managers = [k for (k,v) in r['managers'].items() if v=='connected']
        # step 2. trigger snapshots for each
        for m in managers:
            self.jsonManager.snapshot_POST(
                manager = m,
            )
    def _notif_cb(self,notifName,notifJson):
        if   notifName=='snapshot':
            self._snapshot_cb(notifJson)
        elif notifName=='event':
            self._deviceevent_cb(notifJson)
        else:
            pass # silently drop notification I don't need

class WebServer(object):
    
    HUB_LABEL = 'hub'
    
    def __init__(self,dataGatherer,tcpport,showhub,BOTTLE_STATIC_PATH,BOTTLE_TEMPLATE_PATH,LatLngClass):
        
        # store params
        self.dataGatherer         = dataGatherer
        self.tcpport              = tcpport
        self.showhub              = showhub
        self.BOTTLE_STATIC_PATH   = BOTTLE_STATIC_PATH
        self.BOTTLE_TEMPLATE_PATH = BOTTLE_TEMPLATE_PATH
        
        # local variables
        self.dataGeneration       = None
        self.topology             = ''
        self.LatLng               = LatLngClass
        
        # web server
        if self.BOTTLE_TEMPLATE_PATH:
            bottle.TEMPLATE_PATH.insert(0,self.BOTTLE_TEMPLATE_PATH)
        self.websrv   = bottle.Bottle()
        #=== interact with JsonServer
        self.websrv.route('/snapshot',                'POST',   self._webhandle_snapshot_POST)
        self.websrv.route('/event',                   'POST',   self._webhandle_event_POST)
        #=== interact with user
        self.websrv.route('/',                        'GET',    self._webhandle_root_GET)
        self.websrv.route('/static/<path:path>',      'GET',    self._webhandle_static_GET)
        # hidden API
        self.websrv.route('/stats',                   'GET',    self._webhandle_stats_GET)
        self.websrv.route('/triggersnapshot',         'POST',   self._webhandle_triggersnapshot_POST)
        # topology
        self.websrv.route('/topology',                'GET',    self._webhandle_topology_GET)
        self.websrv.route('/topology.json',           'GET',    self._webhandle_topologyjson_GET)
        # map
        self.websrv.route('/map',                     'GET',    self._webhandle_map_GET)
        self.websrv.route('/map.json',                'GET',    self._webhandle_mapjson_GET)
        self.websrv.route('/map.json',                'POST',   self._webhandle_mapjson_POST)
        
        # start web interface
        webthread = threading.Thread(
            target = self._bottle_try_running_forever,
            args   = (self.websrv.run,),
            kwargs = {
                'host'          : '0.0.0.0',
                'port'          : int(os.getenv('PORT', self.tcpport)),
                'quiet'         : True,
                'debug'         : False,
            }
        )
        webthread.name   = 'WebServer'
        webthread.daemon = True
        webthread.start()
    
    #======================== public ==========================================
    
    def close(self):
        pass # nothing to do, thread is daemonic
    
    #======================== admin ===========================================
    
    def _bottle_try_running_forever(self,*args,**kwargs):
        RETRY_PERIOD = 3
        while True:
            try:
                args[0](**kwargs) # blocking
            except socket.error as err:
                if err[0]==10013:
                    print 'FATAL: cannot open TCP port {0}.'.format(kwargs['port'])
                    print '    Is another application running on that port?'
                else:
                    print logError(err)
            except Exception as err:
                print logError(err)
            print '    Trying again in {0} seconds'.format(RETRY_PERIOD),
            for _ in range(RETRY_PERIOD):
                time.sleep(1)
                print '.',
            print ''
    
    #======================== webhandlers =====================================
    
    #=== interact with JsonServer
    
    def _webhandle_snapshot_POST(self):
        self.dataGatherer._snapshot_cb(bottle.request.json)
    
    def _webhandle_event_POST(self):
        self.dataGatherer._deviceevent_cb(bottle.request.json)
    
    #=== interact with user
    
    def _webhandle_root_GET(self):
        bottle.redirect("/topology")
    
    def _webhandle_static_GET(self,path):
        return bottle.static_file(
            path,
            root=self.BOTTLE_STATIC_PATH,
        )
    
    # hidden API
    
    def _webhandle_stats_GET(self):
        return AppData().getStats()
    
    def _webhandle_triggersnapshot_POST(self):
        self.dataGatherer.snapshotNow()
        return 'triggered snapshot'
    
    # topology
    
    def _webhandle_topology_GET(self):
        return bottle.template(
            'topology',
            pagetitle   = '',
            version     = formatVersion(),
        )
    
    def _webhandle_topologyjson_GET(self):
        return self._getTopology()
    
    # map
    
    def _webhandle_map_GET(self):
        return bottle.template(
            "map",
            pagetitle   = 'SeeTheMesh',
        )
    
    def _webhandle_mapjson_GET(self):
        return self._getTopology()
    
    def _webhandle_mapjson_POST(self):
        rxjson = bottle.request.json
        
        if   (sorted(rxjson.keys())==sorted(['title','lat','lng'])):
            # update position of mote/manager
            
            title  = rxjson['title']
            lat    = rxjson['lat']
            lng    = rxjson['lng']
            if '-' in title:
                title = '00-17-0d-00-00-{0}'.format(title)
            self.LatLng().setMote(title,lat,lng)
            
            AppData().bumpDataGeneration()
        elif (sorted(rxjson.keys())==sorted(['centerlat','centerlng','zoom'])):
            # update position/zoom of map
            
            self.LatLng().setMap(
                rxjson['centerlat'],
                rxjson['centerlng'],
                rxjson['zoom'],
            )
            
            AppData().bumpDataGeneration()
        else:
            raise ValueError('unexpected JSON {0}'.format(rxjson))
    
    #======================== private =========================================
    
    def _getTopology(self):
        # avoid redrawing the topology is AppData hasn't changed
        dataGeneration = AppData().getDataGeneration()
        if dataGeneration!=self.dataGeneration:
            self.topology = self._formatTopology()
            self.dataGeneration = dataGeneration
        return self.topology
    
    def _formatTopology(self):
        '''
        This function needs to create
        
        {
            'generation': 123,
            'hub': {
                'latitude':                 0,
                'longitude':                0,
            },
            'box': {
                'latitude':                 0,
                'longitude':                0,
            },
            'nodes': [
                {
                    'title':                '11-11-11',
                    'hovertext':            '',
                    'latitude':             0,
                    'longitude':            0,
                },
                ...
            ],
            'links': [
                {
                    'sourceidx':            0,
                    'destidx':              1,
                    'source_latitude':      0,
                    'source_longitude':     0,
                    'dest_latitude':        0,
                    'dest_longitude':       0,
                }
            ]
        }
        '''
        
        returnVal = {}
        
        #=== generation
        returnVal['generation'] = AppData().getDataGeneration()
        
        #=== map
        returnVal['map'] = self.LatLng().getMap()
        
        #=== nodes
        returnVal['nodes'] = []
        # box
        returnVal['nodes'] += [
            {
                'latitude':  self.LatLng().getBox()[0],
                'longitude': self.LatLng().getBox()[1],
                'title':     'box',
                'infotext':  'box',
                'icon':      '/static/icon_box.png',
            }
        ]
        # hub
        if self.showhub:
            returnVal['nodes'] += [
                {
                    'latitude':  self.LatLng().getHub()[0],
                    'longitude': self.LatLng().getHub()[1],
                    'title':     self.HUB_LABEL,
                    'infotext':  'hub',
                    'icon':      'http://maps.google.com/mapfiles/ms/micons/sunny.png',
                }
            ]
        # motes (which are operational)
        motes = AppData().get('motes')
        for mote in motes:
            if mote['state']==0: # 0==lost
                continue
            
            # compute infotext
            infotext  = []
            for k in ['macAddress','moteId']:
                if k not in mote:
                    continue
                infotext += [' - {0}: {1}'.format(k,mote[k])]
            infotext = '\n'.join(infotext)
            
            # compute icon/style
            if   mote['isAP']:
                style = "fill: #9cd9ec"
                icon  = "http://maps.google.com/mapfiles/ms/icons/blue-dot.png"
            elif mote['state']!=4:
                style = "fill: #dddddd"
                icon  = "http://maps.gstatic.com/mapfiles/ms2/micons/red.png"
            else:
                style = ""
                icon  = "http://maps.google.com/mapfiles/ms/icons/red-dot.png"
            
            returnVal['nodes'] += [
                {
                    'latitude':  self.LatLng().getMote(mote['macAddress'])[0],
                    'longitude': self.LatLng().getMote(mote['macAddress'])[1],
                    'title':     mote['macAddress'][-8:],
                    'infotext':  infotext,
                    'style':     style,
                    'icon':      icon,
                }
            ]
        
        #=== add links
        returnVal['links'] = []
        paths      = AppData().get('paths')
        nodelabels = [n['title'] for n in returnVal['nodes']]
        # upstream paths
        for path in paths:
            if path['direction']!=2: # 2==upstream
                continue
            try:
                # compute infotext
                infotext  = []
                for k in ['numLinks','rssiSrcDest','rssiDestSrc','quality']:
                    if k not in path:
                        continue
                    infotext += [' - {0}: {1}'.format(k,path[k])]
                infotext = '\n'.join(infotext)
                
                # compute linkcolor
                if   path['quality'] < 50:
                    linkcolor = '#ff0000'
                elif path['quality'] < 80:
                    linkcolor = 'yellow'
                else:
                    linkcolor = '#00ff00'
                
                returnVal['links'] += [
                    {
                        'sourceidx':             nodelabels.index(path['source'][-8:]),
                        'destidx':               nodelabels.index(path['dest'][-8:]),
                        'source_latitude':       self.LatLng().getMote(path['source'])[0],
                        'source_longitude':      self.LatLng().getMote(path['source'])[1],
                        'dest_latitude':         self.LatLng().getMote(path['dest'])[0],
                        'dest_longitude':        self.LatLng().getMote(path['dest'])[1],
                        'infotext':              infotext,
                        'color':                 linkcolor,
                        'opacity':               1.0,
                        'weight':                3,
                    }
                ]
            except ValueError:
                # happens when an eventMoteLost is received before the
                # eventPathDelete events for all the paths it's involved
                # in
                pass
        # links between managers and the hub
        if self.showhub:
            for mote in motes:
                if mote['isAP']:
                    returnVal['links'] += [
                        {
                            'sourceidx':             nodelabels.index(mote['macAddress'][-8:]),
                            'destidx':               nodelabels.index(self.HUB_LABEL),
                            'source_latitude':       self.LatLng().getMote(mote['macAddress'])[0],
                            'source_longitude':      self.LatLng().getMote(mote['macAddress'])[1],
                            'dest_latitude':         self.LatLng().getMote(self.HUB_LABEL)[0],
                            'dest_longitude':        self.LatLng().getMote(self.HUB_LABEL)[1],
                            'infotext':              '',
                            'color':                 'blue',
                            'opacity':               0.7,
                            'weight':                2,
                        }
                    ]
        
        return returnVal

class SeeTheMesh(object):
    
    def __init__(self,managerconnection,tcpport,showhub,BOTTLE_STATIC_PATH,BOTTLE_TEMPLATE_PATH,LatLngClass):
        
        # store params
        self.managerconnection    = managerconnection
        self.tcpport              = tcpport
        self.showhub              = showhub
        self.BOTTLE_STATIC_PATH   = BOTTLE_STATIC_PATH
        self.BOTTLE_TEMPLATE_PATH = BOTTLE_TEMPLATE_PATH
        self.LatLngClass          = LatLngClass
        
        # start the appropriate dataGatherer subclass
        found = False
        for sc in DataGatherer.__subclasses__():
            if sc.__name__[len('DataGatherer_'):].lower()==self.managerconnection.lower():
                self.dataGatherer = sc()
                found = True
                break
        if not found:
            print 'ERROR: unexpected "managerconnection" parameter'
            return

        # interfaces
        self.webServer            = WebServer(
            dataGatherer          = self.dataGatherer,
            tcpport               = self.tcpport,
            showhub               = self.showhub,
            BOTTLE_STATIC_PATH    = self.BOTTLE_STATIC_PATH,
            BOTTLE_TEMPLATE_PATH  = self.BOTTLE_TEMPLATE_PATH,
            LatLngClass           = self.LatLngClass,
        )
        self.cli                  = DustCli.DustCli(
            quit_cb  = self._clihandle_quit,
            versions = {
                'SmartMesh SDK': sdk_version.VERSION,
            },
        )
        self.cli.registerCommand(
            name                  = 'stats',
            alias                 = 's',
            description           = 'get the current stats',
            params                = [],
            callback              = self._clihandle_stats,
        )
        self.cli.registerCommand(
            name                  = 'status',
            alias                 = 'u',
            description           = 'get the current status',
            params                = [],
            callback              = self._clihandle_status,
        )
        
        print 'Web interface started at http://127.0.0.1:{0}'.format(self.tcpport)
    
    #========================  CLI handlers ===================================
    
    def _clihandle_quit(self):
        
        self.dataGatherer.close()
        self.webServer.close()
        
        time.sleep(.3)
        print "bye bye."
    
    def _clihandle_stats(self,params):
        
        stats = AppData().getStats()
        if stats:
            maxlen = max([len(k) for k in stats.keys()])
            formatstring = ' - {0:<'+str(maxlen+1)+'}: {1}'
            for k in sorted(stats.keys()):
                print formatstring.format(k,stats[k])
    
    def _clihandle_status(self,params):
        pp.pprint(self.dataGatherer.getStatus())

#============================ main =======================================

def main(args):
    SeeTheMesh(**args)

if __name__=="__main__":
    # command line arguments
    parser = argparse.ArgumentParser()
    parser.add_argument('--managerconnection', default='serial')
    parser.add_argument('--tcpport',           default=DFLT_TCPPORT)
    parser.add_argument('--showhub',           default=False)
    args = vars(parser.parse_args())
    
    # where Bottle folders are
    # static/ folder
    if os.path.exists('static'):
        args['BOTTLE_STATIC_PATH'] = 'static'
    else:
        args['BOTTLE_STATIC_PATH'] = os.path.join('app','SeeTheMesh','static')
    assert os.path.exists(args['BOTTLE_STATIC_PATH'])
    # views/  folder
    if os.path.exists('views'):
        args['BOTTLE_TEMPLATE_PATH'] = None
    else:
        args['BOTTLE_TEMPLATE_PATH'] = os.path.join('app','SeeTheMesh','views')
        assert os.path.exists(args['BOTTLE_TEMPLATE_PATH'])
    
    # which LatLng class to use
    args['LatLngClass'] = LatLngFile
    
    main(args)
