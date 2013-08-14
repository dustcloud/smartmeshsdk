#!/usr/bin/python

import logging
class NullHandler(logging.Handler):
    def emit(self, record):
        pass
log = logging.getLogger('Gateway')
log.setLevel(logging.ERROR)
log.addHandler(NullHandler())

import time
import threading
import traceback

from pydispatch import dispatcher

from DustLinkData import DustLinkData

from   EventBus import EventBusClient

from   IpMgrConnectorSerial  import IpMgrConnectorSerial
from   IpMgrConnectorMux     import IpMgrConnectorMux
import ApiException

import GatewayListener
import NetworkStateAnalyzer

from   NetworkTestPublisher  import PublishDustLinkData
from   NetworkTestPublisher  import PublishLogFile

import FormatUtils

class Gateway(threading.Thread):
    
    REFRESH_PERIOD = 10.0 # in seconds
    
    SNAPSHOT_START = 'SNAPSHOT_START'
    CMD            = 'CMD'
    SNAPSHOT_END   = 'SNAPSHOT_END'
    NOTIF          = 'NOTIF'
    
    def __init__(self,refresh_period=REFRESH_PERIOD):
        
        # log
        log.info('creating instance')
    
        # store params
        self.refresh_period  = refresh_period
        
        # initialize parent class
        threading.Thread.__init__(self)
        
        # give this thread a name
        self.name                 = 'Gateway'
        
        # local variables
        self.goOn                 = True
        self.dataLock             = threading.Lock()
        self.apiconnectors        = {}
        self.listeners            = {}
        self.analyzers            = {}
        
        # connect to dispatcher
        dispatcher.connect(
            self.tearDown,
            signal = 'tearDown',
            weak   = False,
        )
        dispatcher.connect(
            self.deviceCommunicationError,
            signal = 'deviceCommunicationError',
            weak   = False,
        )
        
        # start itself
        self.start()
    
    def run(self):
        
        try:
            
            # log
            log.info('thread started')
            
            while self.goOn:
                
                # update modules
                with self.dataLock:
                    self._updateModules()
                
                # sleep a bit
                time.sleep(self.refresh_period)
            
            #===== kill associated threads
            
            with self.dataLock:
                for connectParam in self.apiconnectors.keys():
                    self._deleteConnection(connectParam)
            
            # disconnect from dispatcher
            dispatcher.disconnect(
                self.tearDown,
                signal = 'tearDown',
                weak   = False,
            )
            dispatcher.disconnect(
                self.deviceCommunicationError,
                signal = 'deviceCommunicationError',
                weak   = False,
            )
            
            # log
            log.info('thread ended')
            
        except Exception as err:
            output  = []
            output += ['===== crash in thread {0} ====='.format(self.name)]
            output += ['\nerror:\n']
            output += [str(err)]
            output += ['\ncall stack:\n']
            output += [traceback.format_exc()]
            output  = '\n'.join(output)
            print output
            log.critical(output)
            raise
    
    #======================== public ==========================================
    
    def tearDown(self):
        
        # log
        log.info('tearDown() called')
        
        # kill main thread (will kill associated threads)
        self.goOn = False
    
    def deviceCommunicationError(self,sender,signal,data):
        assert isinstance(data,dict)
        dictKeys = data.keys()
        dictKeys.sort()
        assert dictKeys==['connectionParam','reason']
        
        log.warning('received device communication error for connection {0}'.format(
                data['connectionParam']
            )
        )
        
        with self.dataLock:
            # update state
            try:
                DustLinkData.DustLinkData().updateManagerConnectionState(
                    data['connectionParam'],
                    DustLinkData.DustLinkData.MANAGERCONNECTION_STATE_FAIL,
                    reason = data['reason'],
                )
            except ValueError:
                pass # happens when connection has already been deleted
            
            self._deleteConnection(data['connectionParam'])
    
    #======================== private =========================================
    
    def _updateModules(self):
        
        # get the connections
        storedConnections = DustLinkData.DustLinkData().getManagerConnections()
        
        connectionKeys = self.apiconnectors.keys()
        
        # stop some
        for activeConnection in connectionKeys:
            if (not storedConnections) or (activeConnection not in storedConnections):
                self._deleteConnection(activeConnection)
        
        # start some
        if storedConnections:
            for storedConnection in storedConnections:
                if storedConnection not in connectionKeys:
                    self._addConnection(storedConnection)
                elif storedConnections[storedConnection]['state'] == DustLinkData.DustLinkData.MANAGERCONNECTION_STATE_INACTIVE:
                    self._deleteConnection(storedConnection)
                    self._addConnection(storedConnection)
    
    def _addConnection(self,connectParam):
        
        #===== apiconnectors
        
        assert(connectParam not in self.apiconnectors)
        
        if isinstance(connectParam,str):
            newConnector = IpMgrConnectorSerial.IpMgrConnectorSerial()
            try:
                newConnector.connect({
                                'port': connectParam,
                             })
            except ApiException.ConnectionError as err:
                
                # log
                log.warning('could not add apiconnectors {0}: {1}'.format(connectParam, err))
                
                # update state
                DustLinkData.DustLinkData().updateManagerConnectionState(
                    connectParam,
                    DustLinkData.DustLinkData.MANAGERCONNECTION_STATE_FAIL,
                    reason = str(err),
                )
                
                # give the aborted connector a chance to disconnect
                try:
                    newConnector.disconnect()
                except:
                    pass
                
                return
        else:
            try:
                newConnector = IpMgrConnectorMux.IpMgrConnectorMux()
                newConnector.connect({
                                'host': connectParam[0],
                                'port': connectParam[1],
                             })
            except ApiException.ConnectionError as err:
            
                # log
                log.warning('could not add apiconnectors {0}: {1}'.format(connectParam, err))
                
                # update state
                DustLinkData.DustLinkData().updateManagerConnectionState(
                    connectParam,
                    DustLinkData.DustLinkData.MANAGERCONNECTION_STATE_FAIL,
                    reason = str(err),
                )
                
                # give the aborted connector a chance to disconnect
                try:
                    newConnector.disconnect()
                except:
                    pass
                
                return
        
        # log
        log.info('added apiconnectors {0}'.format(connectParam))
        
        self.apiconnectors[connectParam] = newConnector
        
        DustLinkData.DustLinkData().updateManagerConnectionState(
                    connectParam,
                    DustLinkData.DustLinkData.MANAGERCONNECTION_STATE_ACTIVE
        )
        
        #===== add network
        try:
            DustLinkData.DustLinkData().deleteNetwork(FormatUtils.formatConnectionParams(connectParam))
        except ValueError:
            pass # happens if network doesn't exist
        
        #===== add network
        try:
            DustLinkData.DustLinkData().addNetwork(FormatUtils.formatConnectionParams(connectParam))
        except ValueError:
            pass # happens if network already exists from previous connection
        
        #===== add listener
        assert(connectParam not in self.listeners)
        self.listeners[connectParam]   = GatewayListener.GatewayListener(
                                                self.apiconnectors[connectParam],
                                                connectParam,
                                            )
        log.info('added listener {0}'.format(connectParam))
        
        #===== add analyzer
        assert(connectParam not in self.analyzers)
        self.analyzers[connectParam]   = NetworkStateAnalyzer.NetworkStateAnalyzer(connectParam)
        log.info('added analyzer {0}'.format(connectParam))
    
    def _deleteConnection(self, connectParam):
        
        #===== analyzers
        if connectParam in self.analyzers:
            self.analyzers[connectParam].tearDown()
            del self.analyzers[connectParam]
            log.info('deleted analyzer {0}'.format(connectParam))
        
        #===== listener
        if connectParam in self.listeners:
            self.listeners[connectParam].tearDown()
            del self.listeners[connectParam]
            log.info('deleted listener {0}'.format(connectParam))
        
        #===== apiconnectors
        if connectParam in self.apiconnectors:
            self.apiconnectors[connectParam].disconnect()
            del self.apiconnectors[connectParam]
            log.info('deleted apiconnector {0}'.format(connectParam))
        
        #===== delete network
        try:
            DustLinkData.DustLinkData().deleteNetwork(FormatUtils.formatConnectionParams(connectParam))
        except ValueError:
            pass # happens if network was already deleted, e.g. by an earlier call to this function
