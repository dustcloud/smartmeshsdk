
from SmartMeshSDK.ApiDefinition   import HartMoteDefinition
from SmartMeshSDK.SerialConnector import SerialConnector

class HartMoteConnectorInternal(SerialConnector.SerialConnector):
    '''
    \ingroup ApiConnector
    
    \brief Internal class for HART mote connector, over Serial.
    '''
    
    def __init__(self, maxQSize=100):
        api_def = HartMoteDefinition.HartMoteDefinition()
        SerialConnector.SerialConnector.__init__(self,api_def, maxQSize)
    
    #======================== TX ==============================================
    
    def _buildTxHeader(self,cmdId,isResponse,serializedFields):
        txHeader = []
        
        if len(serializedFields)>0 and isinstance(serializedFields[0],list):
            flagList = serializedFields.pop(0)
        else:
            flagList = []
            
        txHeader.append(cmdId)                     # command ID
        txHeader.append(len(serializedFields))     # length
        txHeader.append(self._setFlags(isResponse,flagList))# flags
        if isResponse:
            txHeader.append(0)                     # RC (always 0)
        
        return txHeader
    
    def _setFlags(self,isResponse,flagList):
        self.paramLock.acquire()
        flags      = 0
        if isResponse:
            flags  |= 0x01
            flags  |= self.RxPacketId<<1
        else:
            self._incrementTxPacketId()
            flags  |= self.TxPacketId<<1
        self.paramLock.release()
        
        for flagPosition in flagList:
            flags  |= 1<<flagPosition
        
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
        isResponse           = ((flags&0x01)>>0==1)
        packetId             =  (flags&0x02)>>1
        self.ignorePktId     = ((flags&0x04)>>2==1)
        
        return cmdId,length,isResponse,packetId,payload
    
    def isValidPacketId(self,cmdId,isResponse,packetId):
        result = True
        isRepeatId = False
        updateRxPacketId  = True
        
        if self.RxPacketId==None:
            result = True
        else:
            result = not  (
                                isResponse==False         and
                          self.ignorePktId==False         and
                                  packetId==self.RxPacketId
                        )
        return (result, isRepeatId, updateRxPacketId)
    
    #======================== packetId ========================================
    
    def _incrementTxPacketId(self):
        if self.TxPacketId==0:
            self.TxPacketId=1
        else:
            self.TxPacketId=0