import threading
import socket
import select
import struct

import MuxMsg

from   SmartMeshSDK import ApiException,                   \
                           ApiConnector
from   SmartMeshSDK.ApiDefinition import IpMgrDefinition

class IpMgrConnectorMuxInternal(ApiConnector.ApiConnector ) :
    '''
    \ingroup ApiConnector
    
    \brief Internal class for IP manager connector, through Serial Mux.
    
    Members of class
        acknowledgeBuf - binary payload of acknowledge
        ackCmdId       - command ID from acknowledge
        sendSemaphor   - semaphore to wait for acknowledgement of command (threading.Semaphore)
        inputThread    - thread for processing input packets (threading.Thread) 
        socket         - TCP socket for connection with Serial Mux   
    '''
    PARAM_HOST         = 'host'
    PARAM_PORT         = 'port'
    PARAM_ISSENDHELLO  = 'isSendHello'

    DEFAULT_PARAM_HOST = '127.0.0.1'
    DEFAULT_PARAM_PORT = 9900
    
    _RC_OK         = 0  
    _RC_TIMEOUT    = 5
    
    def __init__(self, maxQSize = 100) :
        ApiConnector.ApiConnector.__init__(self, maxQSize)
        self.acknowledgeBuf = None
        self.ackCmdId = -1
        self.sendSemaphor = threading.BoundedSemaphore(1)
        self.sendLock = threading.Lock()
        self.socket = None
        self.inputThread = None
        self.muxMsg = MuxMsg.MuxMsg(self.processCmd)
        self.apiDef = IpMgrDefinition.IpMgrDefinition()
        self.notifIds = self.apiDef.getIds(self.apiDef.NOTIFICATION) 
        
    def connect(self, params = {}) :
        '''
        \brief Connect to device
        
        \param params Dictionary of connection parameters:
            - 'host' - IP address of Mux (default: '127.0.0.1')
            - 'port' - port of Mux (default: 9900)
            - 'isSendHello' - send Hello message after connection (default True)
        '''
        
        host = self.DEFAULT_PARAM_HOST 
        port = self.DEFAULT_PARAM_PORT
        isSendHello = True
        if self.PARAM_HOST in params and params[self.PARAM_HOST] :
            host = params[self.PARAM_HOST]
        if self.PARAM_PORT in params and params[self.PARAM_PORT] :
            port = int(params[self.PARAM_PORT])
        if self.PARAM_ISSENDHELLO in params :
            isSendHello = params[self.PARAM_ISSENDHELLO]
        
        if self.inputThread :   # Wait finish disconnect process
            try :
                self.inputThread.join(1.0)
                if  self.inputThread.isAlive() :
                    raise ApiException.ConnectionError("Already connected")
            except RuntimeError :
                pass    # Ignore join error
            self.inputThread = None 
        
        try:
            self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.socket.connect( (host, port) )
            self.socket.setblocking(1)
        except socket.error as ex:
            raise ApiException.ConnectionError(str(ex))
        
        self.sendSemaphor.acquire(False)    # Clear semaphore
        # Start thread for processing input stream
        self.inputThread = threading.Thread(target = self.inputProcess)
        self.inputThread.name = "IpMgrConnectorMuxInternal"
        self.inputThread.start()
        ApiConnector.ApiConnector.connect(self)
        if isSendHello :
            self.sendHelloCmd()
        
    def disconnect(self, reason="") :
        if not self.isConnected :
            return
        try :
            self.socket.send("stop")
            self.socket.shutdown(socket.SHUT_RD)    # start disconnection
            self.socket.close()
        except socket.error :
            pass    # Ignore socket error 
        ApiConnector.ApiConnector.disconnect(self, reason)
        
    def send(self, cmdNames, params) :
        self.sendLock.acquire()
        try :
            if not self.isConnected :
                raise ApiException.ConnectionError("Disconnected")
    
            # Send data
            ApiConnector.log.debug("IO OUT.    {0} : {1}".format(cmdNames, params))
            (cmdId, paramsBinList) = self.apiDef.serialize(cmdNames, params)
            paramsBin = struct.pack('!'+str(len(paramsBinList))+'B', *paramsBinList) 
            ApiConnector.logDump(paramsBin, "RawIO OUT. Command ID: {0}".format(cmdId))
            packet = self.muxMsg.build_message(cmdId, paramsBin)
            self.acknowledgeBuf = None
            self.ackCmdId = -1
            try :
                self.socket.sendall(packet)
            except socket.error, way:
                # Socket error. Disconnect from device. Stop command processing
                reason = "IO output error [{0}] {1}".format(way.args[0], way.args[1])
                self.disconnect(reason)
                raise ApiException.ConnectionError(reason)
            
            # Waiting acknowledge
            self.sendSemaphor.acquire()
            if not self.isConnected :         # Disconnect happened during waiting ack.  
                raise ApiException.ConnectionError(self.disconnectReason)
                                                        
            # Process acknowledge
            cmdId = self.apiDef.nameToId(self.apiDef.COMMAND, (cmdNames[0],))
            if self.ackCmdId != cmdId :
                reason = "Unexpected acknowledge {0} for command {1} ({2})".format(self.ackCmdId, cmdId, cmdNames)
                self.disconnect(reason)
                raise ApiException.ConnectionError(reason)
    
            # Parse acknowledge
            ackList = struct.unpack('!'+str(len(self.acknowledgeBuf))+'B', self.acknowledgeBuf)
            (resCmdName, resParams) = self.apiDef.deserialize(self.apiDef.COMMAND, self.ackCmdId, ackList) 
            ApiConnector.log.debug("IO INP.    {0} : {1}".format(resCmdName, resParams))
            
            if self.apiDef.RC in resParams and resParams[self.apiDef.RC] != self._RC_OK : 
                if resParams[self.apiDef.RC] == self._RC_TIMEOUT :
                    raise ApiException.CommandTimeoutError(resCmdName)
                try:
                    desc = '({0})\n{1}'.format(
                        self.apiDef.responseFieldValueToDesc(
                            resCmdName,
                            self.apiDef.RC,
                            resParams[self.apiDef.RC],
                        ),
                        self.apiDef.rcToDescription(
                            resParams[self.apiDef.RC],
                            resCmdName,
                        ),
                    )
                except:
                    desc = None
                raise   ApiException.APIError(
                            cmd=resCmdName,
                            rc=resParams[self.apiDef.RC],
                            desc=desc
                        )
            
            self.ackCmdId = -1
            self.acknowledgeBuf = None
        finally:
            self.sendLock.release()
        return resParams
            
    def ackSignal(self):
        '''
        \brief Send signal 'Acknowledge received'
        '''
        try    : 
            self.sendSemaphor.release()
        except ValueError : 
            pass

    def inputProcess(self):
        '''
        \brief Processing device input 
        '''
        try :
            while True :
                select.select([self.socket], [], [self.socket])
                buf = self.socket.recv(4096)
                if not buf :
                    raise socket.error(0, "Connection close")
                self.muxMsg.parse(buf)
        except socket.error, way:
            # Disconnect process -------------------------------------------------
            if way.args[0] == 9 :   # 
                way = socket.error(0, "Connection close")
            ApiConnector.ApiConnector.disconnect(self, "Disconnect. Reason: {0} [{1}]".format(way.args[1], way.args[0]))
            self.acknowledgeBuf = None
            self.ackCmdId = -1
            self.ackSignal()
            try :
                self.socket.close()
            except socket.error :
                pass    # Ignore socket error 
    
    def processCmd(self, reserved, cmdId, payload):
        '''
        \brief deserialize and process command
        '''
        ApiConnector.logDump(payload, "RawIO INP. Command ID: {0}".format(cmdId))
        if cmdId in self.notifIds :
            try :
                payloadList = struct.unpack('!'+str(len(payload))+'B', payload)
                (notifNames, params) = self.apiDef.deserialize(self.apiDef.NOTIFICATION, cmdId, payloadList)
                ApiConnector.log.debug("IO INP.    {0} : {1}".format(notifNames, params))
                self.putNotification((notifNames, params))
            except ApiException.ConnectionError as ex:
                raise socket.error(0, ex.value)    # Initiate disconnection
            except Exception as ex :
                ApiConnector.log.error("Deserialization command {0}. Error {1}".format(cmdId, ex))
        else :
            self.ackCmdId = cmdId
            self.acknowledgeBuf = payload
            self.ackSignal()
    
    def sendHelloCmd(self):
        '''
        \brief Send Hello command
        '''
        res = self.send(["mux_hello"], {"version" : self.muxMsg.getVer(), "secret" :  self.muxMsg.getAuth()})
        return res
