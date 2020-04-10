import logging
class NullHandler(logging.Handler):
    def emit(self, record):
        pass
log = logging.getLogger('IpMoteConnectorInternal')
log.setLevel(logging.ERROR)
log.addHandler(NullHandler())

from   SmartMeshSDK.SerialConnector import SerialConnector
from   SmartMeshSDK.ApiDefinition   import IpMoteDefinition

class IpMoteConnectorInternal(SerialConnector.SerialConnector):
    '''
    \ingroup ApiConnector
    
    \brief Internal class for HART mote connector, over Serial.
    '''
    
    def __init__(self, maxQSize=100):
        api_def = IpMoteDefinition.IpMoteDefinition()
        SerialConnector.SerialConnector.__init__(self,api_def, maxQSize)
    
    #======================== TX ==============================================
    
    def _buildTxHeader(self,cmdId,isResponse,serializedFields):
        txHeader = []
        
        txHeader.append(cmdId)                     # command ID
        txHeader.append(len(serializedFields))     # length
        txHeader.append(self._setFlags(isResponse))# flags
        if isResponse:
            txHeader.append(0)                     # RC (always 0)
        
        return txHeader
    
    def _setFlags(self,isResponse):
        self.paramLock.acquire()
        flags      = 0
        if isResponse:
            flags  |= 0x01
            flags  |= self.RxPacketId<<1
        else:
            self._incrementTxPacketId()
            flags  |= self.TxPacketId<<1
            if self.syncNeeded :
                self.syncNeeded = False
                flags  |= 1 << 3
        self.paramLock.release()
        
        return flags
    
    def _ackIfNeeded(self,cmdId,isResponse):
        if isResponse:
            # I received a response
            
            return False
        else:
            # I received a request
            
            self._sendInternal(cmdId,True,[])
            return True
            
    
    #======================== RX ==============================================
    
    def _parseRxHeader(self,frameRx):
        
        cmdId           = frameRx[0]
        length          = frameRx[1]
        flags           = frameRx[2]
        payload         = frameRx[3:]
        
        # parse flag byte
        isResponse      = ((flags&0x01)>>0==1)
        packetId        =  (flags&0x02)>>1
        self.dontUseId  = ((flags&0x04)>>2==1)
        self.sync       = ((flags&0x08)>>3==1)
        
        return cmdId,length,isResponse,packetId,payload
    
    def isValidPacketId(self,cmdId,isResponse,packetId):
        self.paramLock.acquire()
        result = True
        isRepeatId = False
        updateRxPacketId  = True
        if self.RxPacketId==None:
            result = True
        else:
            result = not  (
                                isResponse==False         and
                            self.dontUseId==False         and
                                 self.sync==False         and
                                  packetId==self.RxPacketId
                        )
        self.paramLock.release()
        return (result, isRepeatId, updateRxPacketId)

    
    #======================== packetId ========================================
    
    def _incrementTxPacketId(self):
        if self.TxPacketId==0:
            self.TxPacketId=1
        else:
            self.TxPacketId=0
        
        if log.isEnabledFor(logging.DEBUG):
            log.debug("TxPacketId={0}".format(self.TxPacketId))