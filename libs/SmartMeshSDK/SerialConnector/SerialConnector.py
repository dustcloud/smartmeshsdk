import sys
import os

sys.path.insert(0, os.path.join(sys.path[0], '..'))

import threading
import socket
import select
import time

import Hdlc

from   SmartMeshSDK.ApiException  import ConnectionError, \
                                         APIError,        \
                                         CommandError
from   SmartMeshSDK.ApiConnector  import ApiConnector
from   SmartMeshSDK.ApiDefinition import ApiDefinition

import logging
class NullHandler(logging.Handler):
    def emit(self, record):
        pass
log = logging.getLogger('SerialConnector')
log.setLevel(logging.ERROR)
log.addHandler(NullHandler())

class SerialConnector(ApiConnector):
    '''
    \ingroup ApiConnector
    
    \brief The generic serial connector.
    This class is meant to be inherited by connector using a serial link.
    '''
    
    MAX_NUM_RETRY = 5
    RX_TIMEOUT    = 0.500 # in seconds
    
    def __init__(self, api_def, maxQSize=100) :
        
        # log
        log.info("creating object")
        
        # store params
        self.api_def         = api_def
        
        # initialize parent class
        ApiConnector.__init__(self, maxQSize)
        
        # local variables
        self.waitForResp     = False                  ##< flag to indicate whether we are waiting for an ACK
        self.waitForRespEvent  = threading.Event()    ##< semaphore used when waiting for a command to be acknowledged
        self.paramLock       = threading.Lock()       ##< lock to ensure atomic access to parameters
        self.RxPacketId      = None                   ##< running id for packets received from device
        self.TxPacketId      = 0                      ##< running id for packets sent to device
        self.hdlcLock        = threading.Lock()       ##< lock for the HDLC module
        self.hdlc            = None                   ##< HDLC module (includes CRC)
        self.syncNeeded      = True                   ##< True iff we need to sync to the device
        self.requestSendLock = threading.Lock()       ##< lock to prevent concurrent requests to be sent
        self.tsDataSent      = 0                      ##< timestamp when sent data
        self.tsDataReceived  = 0                      ##< timestamp when received data
        
    #======================== public ==========================================
    
    def connect(self, connectParams):
        if 'port' not in connectParams:
            output = "'port' entry required in connection parameters"
            log.error(output)
            raise ValueError(output)
        
        with self.hdlcLock:
            # create and start HDLC module (includes CRC)
            self.hdlc            = Hdlc.Hdlc(self._hdlcRxCb,
                                             self._hdlcConnectCb)
            # connect HDLC module to serial Port
            if 'baudrate' in connectParams:
                self.hdlc.connect(connectParams['port'],baudrate=connectParams['baudrate'])
            else:
                self.hdlc.connect(connectParams['port'])
            # connect the parent class
            ApiConnector.connect(self)
    
    def disconnect(self, reason=""):
        with self.hdlcLock:
            # disconnect the parent class
            ApiConnector.disconnect(self, reason)
            # disconnect hdlc module
            if self.hdlc:
                self.hdlc.disconnect()
            # delete the hdlc module
            self.hdlc = None
    
    def send(self,commandArray,fields):
        if not self.isConnected:
            output = "not connected"
            log.error(output)
            raise ConnectionError(output)
        
        # serialize the fields
        cmdId, serializedFields = self.api_def.serialize(commandArray,fields)
        
        return self._sendInternal(cmdId,False,serializedFields)

    #======================== virtual methods =================================

    def isValidPacketId(self, cmdId, isResponse, packetId):
        '''
        \brief Return whether a received packet is in sequence
        '''
        raise NotImplementedError() # to be implemented by child class

    def _buildTxHeader(self, cmdId, isResponse, serializedFields):
        '''
        \brief Build the header for a TX packet.
        '''
        raise NotImplementedError() # to be implemented by child class

    def _ackIfNeeded(self,cmdId,isResponse):
        '''
        \brief Send an ACK if needed.
        '''
        raise NotImplementedError() # to be implemented by child class

    def isHelloResponse(self, cmdId):
        return False
    
    #======================== private =========================================
    
    def _parseRxHeader(self,frameRx):
        raise NotImplementedError("virtual method")
    
    def _sendInternal(self,cmdId,isResponse,serializedFields):
        
        try:
            if not isResponse:
                self.requestSendLock.acquire()
        
            # build packet to send
            packet  = []
            packet += self._buildTxHeader(cmdId,isResponse,serializedFields)
            packet += serializedFields

            retry = 0
            
            # Prepare for reliable send
            if not isResponse:
                self.waitForResp = True
                self.waitForRespEvent.clear()
                
            while True :
                if log.isEnabledFor(logging.DEBUG):
                    log.debug("_sendInternal cmdId={0} retry={1} isResponse={2} serializedFields={3}".format(
                            cmdId,
                            retry,
                            isResponse,
                            serializedFields
                        )
                    )
                
                if not isResponse:
                    if log.isEnabledFor(logging.DEBUG):
                        log.debug("---------- pcToMote DATA ({0}) ---------->".format(self.TxPacketId))
                        self.tsDataSent = time.time()
                
                # send packet through HDLC module
                with self.hdlcLock:
                    if not self.hdlc:
                        output = "no HDLC module, did I just disconnect?"
                        log.error(output)
                        raise ConnectionError(output)
                    self.hdlc.send(packet)
                
                if isResponse:
                    return None
                
                # wait for response. semaphore released by _hdlcRxCb()
                if self.waitForRespEvent.wait(self.RX_TIMEOUT) :
                    break
                
                log.info("retry {0}".format(retry))
                
                # Timeout error
                if retry >= self.MAX_NUM_RETRY :
                    output = "retried {0} times, max allowed is {1}".format(retry,self.MAX_NUM_RETRY)
                    log.error(output)
                    raise ConnectionError(output)
                retry = retry + 1
                    
            if isinstance(self.responseBuf,Exception):
                log.error("responseBuf contains exception {0}".format(self.responseBuf))
                raise self.responseBuf
            
            if  (
                    (ApiDefinition.ApiDefinition.RC in self.responseBuf) and
                    (
                        self.responseBuf[ApiDefinition.ApiDefinition.RC]!= \
                            ApiDefinition.ApiDefinition.RC_OK
                    )
                ):
                temp_name = self.api_def.idToName(
                                    ApiDefinition.ApiDefinition.COMMAND,
                                    cmdId
                                )
                temp_rc   = self.responseBuf[ApiDefinition.ApiDefinition.RC]
                temp_desc = '({0})\n{1}'.format(
                    self.api_def.fieldValueToDesc(
                        ApiDefinition.ApiDefinition.COMMAND,
                        [temp_name],
                        ApiDefinition.ApiDefinition.RC,
                        temp_rc
                    ),
                    self.api_def.rcToDescription(
                        temp_rc,
                        [temp_name],
                    ),
                )
                if temp_rc not in [11,18]: # rc==11:RC_NOT_FOUND, rc==18:RC_END_OF_LIST
                    log.warning("received RC={0} for command {1}:\n{2}".format(temp_rc,
                                                                               temp_name,
                                                                               temp_desc))
                raise APIError(temp_name,temp_rc,temp_desc)
            
            # return packet received
            return self.responseBuf
        
        finally:
            if not isResponse:
                self.requestSendLock.release()
    
    def _resetPacketIds(self):
        self.TxPacketId=0
        self.RxPacketId=0
        self.syncNeeded=True
    
    #======================== HDLC callbacks ==================================
    
    def _hdlcConnectCb(self,state):
        '''
        \brief called by HDLC when the connected state has changed.
       
        \param state True when the HDLC module is connected to a device,
                     False otherwise
        '''
        log.info("hdlc notification: connection state="+str(state))
        if state==False:
            # we got disconnected
            self.disconnect("HDLC disconnected")
    
    def _hdlcRxCb(self,frameRx):
        '''
        \brief called by HDLC when it's done receiving a complete frame.
        
        \note The frame received does not contain any of the HDLC-specific
              flags and espace characters
       
        \param frameRx The received frame, represented as a byteArray
        '''
        
        if len(frameRx)<3:
            output = "received packet too short"
            log.error(output)
            raise ConnectionError(output)
        
        cmdId,length,isResponse,packetId,payload = self._parseRxHeader(frameRx)
        
        # log
        if log.isEnabledFor(logging.DEBUG):
            log.debug("cmdId={0} length={1} isResponse={2} packetId={3} payload={4}".format(
                    cmdId,
                    length,
                    isResponse,
                    packetId,
                    payload
                )
            )
        
            if isResponse:
                log.debug("<--------- pcToMote ACK ({0}) after {1:.3f} --------".format(
                                packetId,
                                time.time()-self.tsDataSent)
                         )
            else:
                log.debug("<--------- moteToPc DATA ({0}) ----------".format(packetId))
                self.tsDataReceived = time.time()
        
        # check packetId
        (wasValidPacketId, isRepeatId, updateRxPacketId) = self.isValidPacketId(cmdId,isResponse,packetId)

        # raise error if packet id is wrong
        if not wasValidPacketId:
            output = "wrong packetId"
            log.error(output)
            raise ConnectionError(output)
        
        # update RxPacketId
        self.paramLock.acquire()
        if isResponse==False and (not isRepeatId) and updateRxPacketId:
            self.RxPacketId = packetId
        self.paramLock.release()
        
        # send ACK if necessary
        try :
            ackSent = self._ackIfNeeded(cmdId,isResponse)
        except ConnectionError as ex:
            log.error("putting disconnect notification {0}".format(ex))
            self.putDisconnectNotification(str(ex))
            raise ex
        
        # log
        if log.isEnabledFor(logging.DEBUG):
            if ackSent:
                log.debug("---------- moteToPc ACK ({0}) after {1:.3f} ------->".format(
                                self.RxPacketId,
                                time.time()-self.tsDataReceived)
                          )
                log.debug("ack sent")
            else:
                log.debug("no ack needed")
        
        if isResponse or self.isHelloResponse(cmdId):
            
            # deserialize received packet
            try:
                nameArray, fields = self.api_def.deserialize(
                                        ApiDefinition.ApiDefinition.COMMAND,
                                        cmdId,
                                        payload)
            except Exception as err:
                self.responseBuf = err
            else:
                # put received packet in local response buffer
                self.responseBuf = fields
            
            # release semaphore
            if self.waitForResp:
                self.waitForResp = False
                self.waitForRespEvent.set()
            else:
                output = "unexpected response"
                log.error(output)
                raise ConnectionError(output)
            
        else:
            if not isRepeatId :
                
                # deserialize received packet
                nameArray, fields = self.api_def.deserialize(
                                        ApiDefinition.ApiDefinition.NOTIFICATION,
                                        cmdId,
                                        payload)
                
                # put received packet in notification buffer
                self.putNotification((nameArray, fields))
        
