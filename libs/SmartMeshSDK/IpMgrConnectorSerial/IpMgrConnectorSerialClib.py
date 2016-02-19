import threading
import pprint
import serial
import traceback
import os

#============================ decide whether can run ==========================

CLIB_PATHS = [
    os.path.join('libdn_ipmg'),
    os.path.join('..','..','..','sm_clib','sm_clib','libdn_ipmg'),
]
if os.name!='nt':
    for P in CLIB_PATHS:
        P += '.so'

CLIB_PATH = None
for P in CLIB_PATHS:
    if os.name=='nt':
        P = P + '.dll'
    if os.path.exists(P):
        CLIB_PATH = P
        break

if not CLIB_PATH:
    raise ImportError('Could not find C library')

#============================ logging =========================================

import logging
class NullHandler(logging.Handler):
    def emit(self, record):
        pass
log = logging.getLogger('IpMgrConnectorSerial')
log.setLevel(logging.ERROR)
log.addHandler(NullHandler())

#============================ imports =========================================

from ctypes import *

from SmartMeshSDK.utils         import FormatUtils
from SmartMeshSDK.ApiException  import ConnectionError
from SmartMeshSDK.ApiConnector  import ApiConnector
from SmartMeshSDK.ApiDefinition import ApiDefinition, \
                                       IpMgrDefinition

#============================ globals =========================================

DN_SERIAL_ST_DISCONNECTED         = 0x00
DN_SERIAL_ST_HELLO_SENT           = 0x01
DN_SERIAL_ST_CONNECTED            = 0x02

DN_ERR_NONE                       = 0

NUM_SERIAL_TRIES                  = 6

uart_txByte_cbt                   = CFUNCTYPE(c_int, c_uint8)
uart_txByte                       = None

ipmg_notif_cbt                    = CFUNCTYPE(c_void_p, c_uint8, c_uint8)
ipmg_notif                        = None

ipmg_reply_cbt                    = CFUNCTYPE(c_void_p, c_uint8)
ipmg_reply                        = None

ipmg_status_cbt                   = CFUNCTYPE(c_int, c_uint8)
ipmg_status                       = None

INT                               = IpMgrDefinition.IpMgrDefinition.INT
INTS                              = IpMgrDefinition.IpMgrDefinition.INTS
BOOL                              = IpMgrDefinition.IpMgrDefinition.BOOL
HEXDATA                           = IpMgrDefinition.IpMgrDefinition.HEXDATA

SUBID1                            = ApiDefinition.ApiDefinition.SUBID1
SUBID2                            = ApiDefinition.ApiDefinition.SUBID2

#============================ helpers =========================================

pp = pprint.PrettyPrinter(indent=4)

def buf2int(valBuf):
    valInt  = 0
    for i in range(0,len(valBuf)):
        valInt += valBuf[              i]<<(8*(len(valBuf)-1-i))
    return valInt

def _generateCParam(type,length,value):
    
    returnVal = None
    
    if   type==INT:
        returnVal       = value
    elif type==INTS:
        returnVal       = value
    elif type==BOOL:
        if   value==True:
            returnVal   = 0x01
        elif value==False:
            returnVal   = 0x00
        else:
            raise SystemError()
    elif type==HEXDATA:
        if len(value)<=4 and length!=None:
            returnVal   = buf2int(value)
        else:
            buf         = create_string_buffer(len(value))
            for (i,c) in enumerate(value):
                buf[i]  = chr(c)
            returnVal   = byref(buf)
    else:
        raise NotImplementedError('type={0}'.format(type))
    
    assert returnVal!=None
    
    return returnVal

def _getResponseType(type,length):
    assert length!=None
    if   type==INT:
        if   length==1:
            return c_uint8
        elif length==2:
            return c_uint16
        elif length==4:
            return c_uint32
        elif length==8:
            return c_uint8*8
        else:
            raise NotImplementedError
    elif type==INTS:
        if   length==1:
            return c_int8
        else:
            raise NotImplementedError
    elif type==BOOL:
        assert length==1
        return c_bool
    elif type==HEXDATA:
        return c_uint8*length

#============================ body ============================================

class IpMgrConnectorSerial(ApiConnector,threading.Thread):
    
    CONNECT_TIMEOUT               = 2
    RESPONSE_TIMEOUT              = 2
    MAX_FRAME_LENGTH              = 128
    _BAUDRATE                     = 115200
    
    def __init__(self):
        
        # local variables
        self.waitForConnected     = threading.Event()
        self.waitForResponse      = threading.Event()
        
        # initialize parent classes
        ApiConnector.__init__(self)
        threading.Thread.__init__(self)
        self.name                 = 'IpMgrConnectorSerial'
    
    def connect(self,connectParams):
        log.debug("connect connectParams={0}".format(connectParams))
        
        if 'port' not in connectParams:
            output = "'port' entry required in connection parameters"
            log.error(output)
            raise ValueError(output)
        
        #==== connect to serial port
        
        self.comPort         = connectParams['port']
        try:
            self.pyserialHandler = serial.Serial(self.comPort,baudrate=self._BAUDRATE)
            self.pyserialHandler.setRTS(False)
            self.pyserialHandler.setDTR(True)
        except serial.serialutil.SerialException as err:
            output = "could not open " + self.comPort + ", reason: " + str(err)
            log.warning(output)
            raise ConnectionError(output)
        else:
            log.info("opened port "+self.comPort)
        
        #==== import and initialize the C library
        
        global uart_txByte
        global ipmg_notif
        global ipmg_reply
        global ipmg_status
        
        # local variables
        uart_txByte               = uart_txByte_cbt(self._uart_txByte)
        ipmg_notif                = ipmg_notif_cbt(self._ipmg_notif)
        ipmg_reply                = ipmg_reply_cbt(self._ipmg_reply)
        ipmg_status               = ipmg_status_cbt(self._ipmg_status)
        
        # configure the callback function
        self.notifBuf             = create_string_buffer(self.MAX_FRAME_LENGTH)
        
        # open the library under test
        self.smipmg               = CDLL(CLIB_PATH)
        self.smipmg.dn_ipmg_init(
            ipmg_notif,           # notifCb
            self.notifBuf,        # notifBuf
            len(self.notifBuf),   # notifBufLen
            ipmg_reply,           # replyCb
            ipmg_status,          # statusCb
        )
        
        # install callbacks
        self.smipmg.dn_uart_register_txByte(uart_txByte)
        
        # initial thread
        threading.Thread.__init__(self)
        self.name = 'IpMgrConnectorSerial'
        
        # start myself
        self.start()
        
        #==== connect to manager
        
        rcApi = self.smipmg.dn_ipmg_initiateConnect()
        assert rcApi == DN_ERR_NONE
        
        # wait for C library to connect
        if self.waitForConnected.wait(self.CONNECT_TIMEOUT):
            self.waitForConnected.clear()
            # connect the parent class
            ApiConnector.connect(self)
        else:
            raise ConnectionError("timeout connecting")
    
    def run(self):
        while True:
            b = self.pyserialHandler.read(1)
            if not b:
                break
            b = ord(b)
            log.debug('RX serial byte 0x{0:02x}'.format(b))
            self.smipmg.dn_uart_rxByte(b)
        
        log.info("stopping thread")
    
    #======================== public ==========================================
    
    def send(self,commandArray,fields):
        log.debug('send commandArray={0} fields={1}'.format(commandArray,fields))
        
        assert len(commandArray)==1
        commandName = commandArray[0]
        
        apiCommand = None
        for c in IpMgrDefinition.IpMgrDefinition.commands:
            if c['name']==commandName:
                apiCommand = c
                break
        assert apiCommand
        
        #===== send command to manager
        
        # create params on the fly
        params                    = []
        varSizeParamLen           = None
        
        for [paramname,type,length,_] in apiCommand['request']:
            thisparam = {}
            thisparam['name']     = paramname
            thisparam['C']        = _generateCParam(type,length,fields[paramname])
            
            params               += [thisparam]
            
            if length==None:
                varSizeParamLen   = len(fields[paramname])
        
        # create (dummy) buffer to hold reply
        reply                     = create_string_buffer(self.MAX_FRAME_LENGTH)
        
        # format params
        cparams                   = []
        cparams                  += [p['C'] for p in params]
        if varSizeParamLen!=None:
            cparams              += [varSizeParamLen]
        cparams                  += [byref(reply)]
        
        # log
        log.debug('C parameters: {0}'.format(pp.pformat(params)))
        
        # issue request
        rcApi     = getattr(self.smipmg,'dn_ipmg_{0}'.format(apiCommand['name']))(*cparams)
        assert rcApi == DN_ERR_NONE
        
        #===== wait for response
        
        if self.waitForResponse.wait(self.RESPONSE_TIMEOUT):
            self.waitForResponse.clear()
        else:
            self.smipmg.dn_ipmg_cancelTx()
            raise ConnectionError("timeout response")
        
        #===== convert C response to Python dictionnary
        
        # create returned fields on the fly
        theseFields = []
        for [name,type,length,validName] in apiCommand['response']['FIELDS']:
            theseFields += [(name, _getResponseType(type,length))]
        
        # Structure to hold the response
        class reply_t(Structure):
            _fields_    = theseFields
        
        # cast response to that structute
        notif           = cast(reply, POINTER(reply_t))
        
        # convert structure to dictionnary
        returnVal = {}
        for (f,_) in theseFields:
            rawVal = getattr(notif.contents,f)
            if  isinstance(rawVal,int):
                returnVal[f] = rawVal
            elif isinstance(rawVal,long):
                returnVal[f] = int(rawVal)
            else:
                returnVal[f] = [int(b) for b in rawVal]
        
        return returnVal
    
    def disconnect(self):
        
        # close serial port
        self.pyserialHandler.close()
        
        # disconnect the parent class
        ApiConnector.disconnect(self, reason="")
    
    #======================== private =========================================
    
    #========== C library interaction
    
    # UART interaction
    
    def _uart_txByte(self,b):
        '''
        \brief Called by C library when wants to send a byte over the serial
            port.
        '''
        log.debug('TX serial byte 0x{0:02x}'.format(b))
        
        self.pyserialHandler.write(chr(b))
        
        return 0
    
    # status notification
    
    def _ipmg_status(self,newStatus):
        '''
        \brief Called by C library when connection status is changed.
        '''
        log.debug('_ipmg_status newStatus={0}'.format(newStatus))
        
        if newStatus==DN_SERIAL_ST_CONNECTED:
            self.waitForConnected.set()
        
        return 0
    
    # data notifications
    
    def _ipmg_reply(self,cmdId):
        '''
        \brief Called by C library when a reply is received.
        '''
        log.debug('_ipmg_reply cmdId={0} (0x{0:02x})'.format(cmdId))
        
        self.waitForResponse.set()
        
        return 0
    
    def _ipmg_notif(self,cmdId,subcmdId):
        '''
        \brief Called by C library when a notification is received.
        '''
        log.debug(
            '_ipmg_notif cmdId={0} subcmdId={1} notifBuf={2}'.format(
                cmdId,
                subcmdId,
                FormatUtils.formatBuffer([ord(b) for b in self.notifBuf]),
            )
        )
        
        #===== cast notification buffer to correct type
        
        # find apiNotif
        apiNotifFields  = []
        nameArray       = ['notification']
        for notif in IpMgrDefinition.IpMgrDefinition.subCommandsNotification:
            if notif['id']==cmdId:
                nameArray += [notif['name']]
                for f in notif['response']['FIELDS']:
                    if f[0] not in [SUBID1,SUBID2]:
                        apiNotifFields += [f]
                if 'subCommands' in notif:
                    for subnotif in notif['subCommands']:
                        if subnotif['id']==subcmdId:
                            nameArray += [subnotif['name']]
                            for f in subnotif['response']['FIELDS']:
                                apiNotifFields += [f]
        
        # create returned fields on the fly
        theseFields = []
        lengthField = None
        for [name,type,length,_] in apiNotifFields:
            if length==None:
                theseFields += [('{0}Len'.format(name), c_uint8)]
                theseFields += [(name,                  c_uint8*self.MAX_FRAME_LENGTH)]
                lengthField  = name
            else:
                theseFields += [(name, _getResponseType(type,length))]
        
        # Structure to hold the response
        class reply_t(Structure):
            _fields_    = theseFields
        
        # cast response to that structute
        c_notif         = cast(self.notifBuf, POINTER(reply_t))
        
        #===== convert C notification to Python dictionnary
        
        # convert structure to dictionnary
        py_notif = {}
        for (f,_) in theseFields:
            rawVal = getattr(c_notif.contents,f)
            if  isinstance(rawVal,int):
                py_notif[f] = rawVal
            elif isinstance(rawVal,long):
                py_notif[f] = int(rawVal)
            else:
                py_notif[f] = [int(b) for b in rawVal]
        
        # trim lengthField
        if lengthField!=None:
            py_notif[lengthField] = py_notif[lengthField][:py_notif['{0}Len'.format(lengthField)]]
            del py_notif['{0}Len'.format(lengthField)]
        
        #===== put received packet in notification buffer
        
        self.putNotification((nameArray, py_notif))
