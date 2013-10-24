import os
import threading
import socket
import ssl

from  SmartMeshSDK.ApiConnector import ApiConnector
from  SmartMeshSDK.ApiException import ConnectionError

AUTHTIMEOUT   = 10.0 # max number of seconds to wait for response during connection
TCPRXBUFSIZE  = 4096 # size of the TCP reception buffer

import logging
class NullHandler(logging.Handler):
    def emit(self, record):
        pass
log = logging.getLogger('LbrConnector')
log.setLevel(logging.ERROR)
log.addHandler(NullHandler())

class LbrProtocol(object):
    '''
    \brief Enumeration of commands sent/received to/from LBR
    '''
    # possible value of the commandId
    CMD_SECURITY             = 'S'
    CMD_USERNAME             = 'N'
    CMD_PASSWORD             = 'X'
    CMD_PREFIX               = 'P'
    
    # possible payload value for security command ID
    SECLEVEL_NONE            = 0
    SECLEVEL_PASSWORD        = 1
    SECLEVEL_SSL             = 2
  
class LbrListener(threading.Thread):
    '''
    \brief A helper class for the lbrConnector which listens to the socket.
    '''
    def __init__(self,socket,rxCb,disconnectedCb):
    
        # record variables
        self.socket          = socket
        self.rxCb            = rxCb
        self.disconnectedCb  = disconnectedCb
        
        # init the parent
        threading.Thread.__init__(self)
        self.name            = "LbrListener"
    
    #======================== public ==========================================
    
    def run(self):
        keepListening = True
        while keepListening:
            try:
                input = self.socket.recv(TCPRXBUFSIZE)
            except socket.error:
                keepListening = False
                continue
            if input:
                self.rxCb(input)
            else:
                keepListening = False
                continue
        self.disconnectedCb()
    
class LbrConnector(ApiConnector):
    
    # possible values for the lbrConnector's status
    STATUS_DISCONNECTED      = 'disconnected'
    STATUS_INIT_CONNECTION   = 'initiating connection'
    STATUS_TX_SECURITY       = 'sending security capability'
    STATUS_RX_SECURITY       = 'waiting for security capability'
    STATUS_TX_PASSWORD       = 'sending password to LBR'
    STATUS_SLL_WRAPPING      = 'wrapping TCP session with SSL'
    STATUS_TX_USERNAME       = 'sending username'
    STATUS_RX_USERNAME       = 'receiving username echo'
    STATUS_RX_PREFIX         = 'waiting for prefix information'
    STATUS_CONNECTED         = 'connected'
    STATUS_DISCONNECTING     = 'disconnecting'
    
    def __init__(self, maxQSize=100):
        log.debug("creating object")
        
        # init the parent
        ApiConnector.__init__(self,maxQSize)
        
        # variables
        self.varLock         = threading.Lock()
        self._updateStatus(self.STATUS_DISCONNECTED)
        self.prefix          = None
        
        # reset stats
        self._resetStats()
    
    #======================== public ==========================================
    
    def connect(self,connectParams):
        '''
        \brief Connect to the LBR.
        '''
        
        # filter error
        if self.getStatus() not in [self.STATUS_DISCONNECTED]:
            self._abortConnectionWithError(connectParams,'is at wrong status to connect '+str(self.getStatus()))
        
        # record variables
        try:
            self.varLock.acquire()
            self.lbrAddr              = connectParams['lbrAddr']
            self.lbrPort              = connectParams['lbrPort']
            self.username             = connectParams['username']
            self.seclevel             = connectParams['seclevel']
            if   self.seclevel==LbrProtocol.SECLEVEL_PASSWORD:
                self.password         = connectParams['password']
            elif self.seclevel==LbrProtocol.SECLEVEL_SSL:
                self.clientprivatekey = connectParams['clientprivatekey']
                self.clientpublickey  = connectParams['clientpublickey']
                self.lbrpublickey     = connectParams['lbrpublickey']
        except KeyError as err:
            raise ConnectionError('Missing connection parameter: '+str(err))
        finally:
            self.varLock.release()
        
        # connect the parent
        ApiConnector.connect(self)
        
        # update status
        self._updateStatus(self.STATUS_INIT_CONNECTION)
        
        # create TCP socket to connect to LBR
        try:
            self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.socket.connect((self.lbrAddr,self.lbrPort))
        except socket.error:
            self._abortConnectionWithError(connectParams,'could not open socket to LBR@'+self.lbrAddr+':'+str(self.lbrPort)+'.')
        
        # listen for at most AUTHTIMEOUT seconds during connection
        self.socket.settimeout(AUTHTIMEOUT)
        
        #=== Step 1. Send my security capability to LBR
        self._updateStatus(self.STATUS_TX_SECURITY)
        try:
            self.socket.send(LbrProtocol.CMD_SECURITY+chr(self.seclevel))
        except socket.error:
            self._abortConnectionWithError(connectParams,'could not send security capability.')
        
        #=== Step 2. Receive security capabilities from LBR
        self._updateStatus(self.STATUS_RX_SECURITY)
        try:
            input = self.socket.recv(TCPRXBUFSIZE)
        except socket.timeout:
            self._abortConnectionWithError(connectParams,'waited too long for security reply.')
        if (     len(input)!=2   or
                 input[0]  !=LbrProtocol.CMD_SECURITY or
             ord(input[1]) !=self.seclevel):
            self._abortConnectionWithError(connectParams,'received incorrect security reply.')
        
        #=== Step 3. Send username
        self._updateStatus(self.STATUS_TX_USERNAME)
        try:
            self.socket.send(LbrProtocol.CMD_USERNAME+self.username)
        except socket.error:
            self._abortConnectionWithError(connectParams,'could not send username.')
        
        #=== Step 4. Receive username
        self._updateStatus(self.STATUS_RX_USERNAME)
        try:
            input = self.socket.recv(TCPRXBUFSIZE)
        except socket.timeout:
            self._abortConnectionWithError(connectParams,'waited too long for username echo.')
        if (     len(input)<=1   or
                 input[0]  !=LbrProtocol.CMD_USERNAME or
                 input[1:] !=self.username):
            self._abortConnectionWithError(connectParams,'received incorrect echoed username.')
        
        #=== Step 5. Secure TCP session
        if   self.seclevel==LbrProtocol.SECLEVEL_NONE:
            log.debug('TCP session securing: none')
        elif self.seclevel==LbrProtocol.SECLEVEL_PASSWORD:
            log.debug('TCP session securing: password')
            self._updateStatus(self.STATUS_TX_PASSWORD)
            try:
                self.socket.send(LbrProtocol.CMD_PASSWORD+self.password)
            except socket.error:
                self._abortConnectionWithError(connectParams,'could not send password.')
        elif self.seclevel==LbrProtocol.SECLEVEL_SSL:
            log.debug('TCP session securing: SSL')
            self._updateStatus(self.STATUS_SLL_WRAPPING)
            try:
                clientPrivateKeyPem      = self._privatekeyToPem(self.clientprivatekey)
                clientPrivateKeyFileName = self.username+'.tempprivatekey'
                clientPrivateKeyFile     = open(clientPrivateKeyFileName,'w')
                clientPrivateKeyFile.write(clientPrivateKeyPem)
                clientPrivateKeyFile.close()
                
                clientPublicKeyPem       = self._publickeyToPem(self.clientpublickey)
                clientPublicKeyFileName  = self.username+'.temppublickey'
                clientPublicKeyFile      = open(clientPublicKeyFileName,'w')
                clientPublicKeyFile.write(clientPublicKeyPem)
                clientPublicKeyFile.close()
                
                lbrpublickeyPem       = self._publickeyToPem(self.lbrpublickey)
                lbrpublickeyFileName  = self.username+'.templbrpublickey'
                lbrpublickeyFile      = open(lbrpublickeyFileName,'w')
                lbrpublickeyFile.write(lbrpublickeyPem)
                lbrpublickeyFile.close()
                
                self.socket = ssl.wrap_socket(
                                    self.socket,
                                    keyfile=clientPrivateKeyFileName,     # client's private key
                                    certfile=clientPublicKeyFileName,     # client's public key
                                    ca_certs=lbrpublickeyFileName,     # server's public key
                                    cert_reqs=ssl.CERT_REQUIRED)
            except ssl.SSLError as err:
                self._abortConnectionWithError(connectParams,'SSL wrapping failed.')
            except Exception as err:
                print err
            else:
                output  = ''
                output += 'Peer validated:\n'
                output += '- name:        '+str(self.socket.getpeername())+'\n'
                output += '- cipher:      '+str(self.socket.cipher())+'\n'
                output += '- cartificate: '+str(self.socket.getpeercert())
                log.debug(output)
            finally:
                os.remove(clientPrivateKeyFileName)
                os.remove(clientPublicKeyFileName)
                os.remove(lbrpublickeyFileName)
        
        #=== Step 6. Receive assigned prefix from LBR
        self._updateStatus(self.STATUS_RX_PREFIX)
        try:
            input = self.socket.recv(TCPRXBUFSIZE)
        except (socket.timeout,ssl.SSLError):
            self._abortConnectionWithError(connectParams,'waited too long for prefix.')
        if (len(input)!=20 or
              input[0]!=LbrProtocol.CMD_PREFIX):
            self._abortConnectionWithError(connectParams,'received malformatted prefix.')
        
        # record the prefix
        self.prefix = input[1:]
        
        # if you get here, connection is succesfully established with LBR
        
        # update status
        self._updateStatus(self.STATUS_CONNECTED)
        
        # no socket timeout from now on
        self.socket.settimeout(None)
        
        # start an LbrListener thread
        temp = LbrListener(self.socket,self._rxCb,self._disconnectedCb)
        temp.start()
    
    def disconnect(self):
        '''
        \brief Disconnect from the LBR.
        '''
        
        # filter error
        if self.getStatus() not in [self.STATUS_CONNECTED]:
            raise EnvironmentError('Wrong status to disconnect '+str(self.getStatus()))
        
        # update status
        self._updateStatus(self.STATUS_DISCONNECTING)
        
        # close the TCP session (causes LbrListener thread to exit)
        self._closeSocket()
    
    def send(self,macAndLowpan):
        
        log.debug("send to LBR: {0}".format(
            ''.join(['%02x'%ord(b) for b in macAndLowpan]),
        ))
        
        # filter error
        if self.getStatus() not in [self.STATUS_CONNECTED]:
            raise EnvironmentError('Wrong status to send '+str(self.getStatus()))
        
        # send over socket
        self.socket.send(macAndLowpan)
        
        # update stats
        self.varLock.acquire()
        self.sentPackets += 1
        self.sentBytes   += len(macAndLowpan)
        self.varLock.release()
    
    def getUsername(self):
        self.varLock.acquire()
        returnVal = self.username
        self.varLock.release()
        return returnVal
    
    def getLbrAddr(self):
        self.varLock.acquire()
        returnVal = self.lbrAddr
        self.varLock.release()
        return returnVal
    
    def getLbrPort(self):
        self.varLock.acquire()
        returnVal = self.lbrPort
        self.varLock.release()
        return returnVal
    
    def getStatus(self):
        self.varLock.acquire()
        returnVal = self.status
        self.varLock.release()
        return returnVal
        
    def getPrefix(self):
        self.varLock.acquire()
        returnVal = self.prefix
        self.varLock.release()
        return returnVal
    
    def getStats(self):
        self.varLock.acquire()
        returnVal = (self.sentPackets,
                     self.sentBytes,
                     self.receivedPackets,
                     self.receivedBytes)
        self.varLock.release()
        return returnVal
    
    #======================== private =========================================
    
    def _rxCb(self,input):
        # the data received from the LBR should be:
        # [0:8]: mac address of the final destination
        # [8:] : 6LoWPAN packet
        
        # update stats
        self.varLock.acquire()
        self.receivedPackets += 1
        self.receivedBytes   += len(input)
        self.varLock.release()
        
        # filter error
        if len(input)<8:
            # update stats
            self.varLock.acquire()
            self.receivedPackets += 1
            self.receivedBytes   += len(input)
            self.varLock.release()
        
        # deserialize received packet
        mac    = input[0:8]
        lowpan = input[8:]
        
        log.debug("received from LBR, for MAC={0} payload={1}".format(
            '-'.join(['%02x'%ord(b) for b in mac]),
            ''.join(['%02x'%ord(b) for b in lowpan]),
        ))
            
        # put received packet in notification buffer
        self.putNotification((mac, lowpan))
    
    def _disconnectedCb(self):
        # disconnect the parent
        ApiConnector.disconnect(self,'')
        
        # update status
        self._updateStatus(self.STATUS_DISCONNECTED)
    
    def _closeSocket(self):
        self.socket.shutdown(socket.SHUT_RDWR)
        self.socket.close()
    
    def _updateStatus(self,newStatus):
        self.varLock.acquire()
        self.status  = newStatus
        self.varLock.release()
        log.debug("status: "+self.status)
    
    def _abortConnectionWithError(self,connectParams,reason):
        try:
            self._closeSocket()
        except (AttributeError,socket.error):
            pass
        raise ConnectionError(connectParams['username']+' '+reason)
    
    def _resetStats(self):
        self.varLock.acquire()
        self.sentPackets     = 0
        self.sentBytes       = 0
        self.receivedPackets = 0
        self.receivedBytes   = 0
        self.varLock.release()
        
    #======================== helpers =========================================
    
    def _publickeyToPem(self,keyString):
        return self._keyToPem(keyString,
                              '-----BEGIN CERTIFICATE-----',
                              '-----END CERTIFICATE-----')
    
    def _privatekeyToPem(self,keyString):
        return self._keyToPem(keyString,
                              '-----BEGIN RSA PRIVATE KEY-----',
                              '-----END RSA PRIVATE KEY-----')
    
    def _keyToPem(self,keyString,firstLine,lastLine):
        keypem  = ''
        keypem += firstLine+'\r\n'
        index = 0
        while index<len(keyString):
           keypem += keyString[index:index+64]+'\r\n'
           index += 64
        keypem += lastLine
        return keypem
        