import sys
import os
sys.path.insert(0, os.path.join(sys.path[0], '..'))

import time
import threading

from SmartMeshSDK                 import ApiException
from SmartMeshSDK.ApiDefinition   import IpMgrDefinition, \
                                         HartMgrDefinition

import logging
class NullHandler(logging.Handler):
    def emit(self, record):
        pass
log = logging.getLogger('LatencyCalculator')
log.setLevel(logging.ERROR)
log.addHandler(NullHandler())

class LatencyCalculator(threading.Thread) :
    '''
    \brief Packet latency calculator for the SmartMesh IP network.
    '''
    QUERY_PERIOD_S     = 10
    
    def __init__(self,apiDef,connector):
        
        # log
        log.debug('Creating object')
        
        # store params
        self.apiDef                         = apiDef
        self.connector                      = connector
        
        # variables
        self.datalock                       = threading.Lock()
        self.lockPcTime                     = None
        self.lockNetworkTime                = None
        self.numNetworkTimeAcquisitions     = 0
        self.keepRunning                    = True
        self.delay                          = 0
        
        # initialize the parent class
        threading.Thread.__init__(self)
        self.name            = "LatencyCalculator"
        
    def run(self):
        # log
        log.debug('Thread started')
        
        self.delay           = 0
        while self.keepRunning:
            
            # sleep for a second
            time.sleep(1)
            
            if not self.keepRunning:
                log.debug('thread quitting')
                return
            
            # update time match
            if self.delay==0:
                
                # match PC time to manager time
                self.datalock.acquire()
                self.lockPcTime = time.time()
                try:
                    res = self.connector.dn_getTime()
                except ApiException.ConnectionError:
                    self.keepRunning = False
                    output = 'Connector appears disconnected, quitting thread'
                    log.error(output)
                    print (output)
                except Exception as err:
                    output = "unexpected {0}: {1}".format(type(err),err)
                    log.critical(output)
                    print (output)
                else:
                    if   isinstance(self.apiDef,IpMgrDefinition.IpMgrDefinition):
                        self.lockNetworkTime = float(res.utcSecs)+(float(res.utcUsecs)/1000000.0)
                    elif isinstance(self.apiDef,HartMgrDefinition.HartMgrDefinition):
                        self.lockNetworkTime = res.utc_time
                    else:
                        output = "apiDef of type {0} unexpected".format(type(self.apiDef))
                        log.critical(output)
                        print (output)
                        raise SystemError(output)
                    
                    self.numNetworkTimeAcquisitions += 1
                    
                    # log
                    log.info('Acquired time: lockNetworkTime={0} lockPcTime={1}'.format(
                                    self.lockNetworkTime,
                                    self.lockPcTime))
                finally:
                    self.datalock.release()
            
            # increment delay
            self.delay      += 1
            if self.delay==self.QUERY_PERIOD_S:
                # reset delay
                self.delay   = 0
    
    #======================== public ==========================================
    
    def getLatency(self,tsTxNetwork,tsRxPc):
        '''
        \brief Calculate the latency of a given packet
        
        \param tsTxNetwork [in] The timestamp (in s) as read from the data
                                notification. This is the time, expressed in
                                network time, when the packet was generated.
        \param tsRxPc     [in]  The timestamp (in epoch) of reception of this
                                packet at the PC.
        \exception RuntimeError if lock not acquired enough times yet.
        \returns The latency of the packet, in seconds.
        '''
        
        # log
        log.debug('Calculating latency for tsTxNetwork={0} tsRxPc={1}'.format(
                        tsTxNetwork,
                        tsRxPc))
        
        if self.numNetworkTimeAcquisitions<2:
            raise RuntimeError("lock hasn't been acquired enough times")
        
        # convert tsTxNetwork to tsTxPc
        self.datalock.acquire()
        tsTxPc     = self.lockPcTime + (tsTxNetwork - self.lockNetworkTime)
        self.datalock.release()
        
        log.debug('tsTxPc={0}'.format(tsTxPc))
        
        # calculate the latency
        latency    = tsRxPc - tsTxPc
        
        log.debug('latency={0}'.format(latency))
        
        return latency
    
    def disconnect(self):
        '''
        \brief Disconnect from the mamager.
        
        Causes the thread to terminate.
        '''
        
        # log
        log.warning('disconnect function called')
        
        # cause the thread to disconnect
        self.keepRunning = False

    #======================== private ==========================================    
    