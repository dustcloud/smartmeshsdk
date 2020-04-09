
from SmartMeshSDK.SerialConnector import SerialConnector
from SmartMeshSDK.ApiDefinition   import ApiDefinition,    \
                                         IpMgrDefinition
from SmartMeshSDK.ApiException    import ConnectionError

class IpMgrConnectorSerialInternal(SerialConnector.SerialConnector):
    '''
    \ingroup ApiConnector
    
    \brief Internal class for IP manager connector, over Serial.
    '''

    HELLO_CMD      = (ApiDefinition.ApiDefinition.COMMAND, ['hello'])
    HELLO_RESP_CMD = (ApiDefinition.ApiDefinition.COMMAND, ['hello_response'])
    MGR_HELLO_CMD  = (ApiDefinition.ApiDefinition.NOTIFICATION, ['manager_hello'])

    def __init__(self, maxQSize=100):
        api_def = IpMgrDefinition.IpMgrDefinition()
        SerialConnector.SerialConnector.__init__(self, api_def, maxQSize)

        self.HELLO_IDS = {'hello':          self.api_def.nameToId(*self.HELLO_CMD),
                          'hello_response': self.api_def.nameToId(*self.HELLO_RESP_CMD),
                          'manager_hello':  self.api_def.nameToId(*self.MGR_HELLO_CMD),
                          }
        self.helloCmdIds = list(self.HELLO_IDS.values())
        self.isConnect = False
        self.TxPacketId = 0
        
    def connect(self, params):
        SerialConnector.SerialConnector.connect(self, params)
        try:
            self._sendHello()
        except:
            SerialConnector.SerialConnector.disconnect(self)
            raise

    def isHelloResponse(self, cmdId):
        return cmdId == self.HELLO_IDS['hello_response']
    
    #======================== TX ==============================================

    def _sendHello(self):
        'Send the client Hello to the manager'
        self.paramLock.acquire()
        self.isConnect = False
        cmdId,byteArray = self.api_def.serialize(['hello'],
                                                 {'version':  self.api_def.fieldOptions['protocolVersion'],
                                                  'cliSeqNo': (self.TxPacketId - 1) % 256,
                                                  'mode':     0,
                                                  })
        self.paramLock.release()
        resp = self._sendInternal(cmdId, False, byteArray)
        if resp['successCode'] == ApiDefinition.ApiDefinition.RC_OK:
            self.paramLock.acquire()
            self.RxPacketId = resp['mgrSeqNo']
            self.isConnect = True
            self.paramLock.release()
        else:
            self.disconnect()
    
    def _buildTxHeader(self,cmdId,isResponse,serializedFields):
        txHeader = []
        controlByte = 0
        if cmdId not in [self.HELLO_IDS['hello']]:
            controlByte |= 0x02
            if isResponse:
                controlByte |= 0x01
        
        txHeader.append(controlByte)
        txHeader.append(cmdId)
        self.paramLock.acquire()
        if isResponse:
            txHeader.append(self.RxPacketId)
        else:
            txHeader.append(self.TxPacketId)
        self.paramLock.release()
        txHeader.append(len(serializedFields))
        
        return txHeader
        
    def _ackIfNeeded(self,cmdId,isResponse):
        if  (
                (not isResponse) and
                (self.shouldAck)
            ):
            # send normal ACK (with RC=0)
            self._sendInternal(cmdId,True,[0])
            return True
        elif cmdId == self.HELLO_IDS['manager_hello'] and self.isConnect :
            raise ConnectionError("Unexpected manager_hello")
        return False
    
    def _iShouldAck(self,isResponse):
        return 
    
    #======================== RX ==============================================
    
    def _parseRxHeader(self,frameRx):
        
        controlByte     = frameRx[0]
        cmdId           = frameRx[1]
        packetId        = frameRx[2]
        length          = frameRx[3]
        payload         = frameRx[4:]
        
        # parse controlByte
        isResponse      = ((controlByte&0x01)>>0==1)
        self.shouldAck  = ((controlByte&0x02)>>1==1)
        
        return cmdId,length,isResponse,packetId,payload
    
    def isValidPacketId(self,cmdId,isResponse,packetId):
        self.paramLock.acquire()
        isValidId            = True
        isDuplicate          = False
        updateRxPacketId  = True
        if ((self.RxPacketId==None) or
            (cmdId in self.helloCmdIds)):
            isValidId             = True
            isDuplicate           = False
            updateRxPacketId   = True
        else:
            if isResponse:
                isValidId              = packetId==self.TxPacketId
                if isValidId :
                    self._incrementTxPacketId()
                isDuplicate            = False
                updateRxPacketId    = True
            else:
                if self.shouldAck:
                    # reliable transport
                    isValidId               = packetId==self.RxPacketId or packetId==(self.RxPacketId+1)%256
                    isDuplicate             = packetId==self.RxPacketId 
                    updateRxPacketId     = True
                else:
                    # unreliable transport
                    isValidId               = True
                    isDuplicate             = False
                    updateRxPacketId     = False
        self.paramLock.release()
        return (isValidId, isDuplicate, updateRxPacketId)
    
    #======================== packetId ========================================
    
    def _incrementTxPacketId(self):
        self.TxPacketId += 1
        if self.TxPacketId>0xff:
            self.TxPacketId=0
