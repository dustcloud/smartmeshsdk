#!/usr/bin/python

import sys
import threading
import traceback

import Crc


from SmartMeshSDK.ApiException import ConnectionError, \
                                      CommandError

try:
    import serial
except ImportError:
    output  = ''
    output += 'Could not load the serial module.\n'
    output += 'Please install PySerial from http://pyserial.sourceforge.net/,'
    output += 'then run this script again.\n'
    raw_input(output)
    sys.exit()

import logging
class NullHandler(logging.Handler):
    def emit(self, record):
        pass
log = logging.getLogger('Hdlc')
log.setLevel(logging.ERROR)
log.addHandler(NullHandler())

class Hdlc(threading.Thread):
    
    _BAUDRATE      = 115200 # the default baudrate used by this module
    
    _HDLC_FLAG     = 0x7e   # the HDLC flag at the beginning/end of a frame
    _HDLC_ESCAPE   = 0x7d   # escape character when the HDLC flag in payload
    _HDLC_MASK     = 0x20   # mask used to recover from escape characters
    
    _FCS_LENGTH    = 2      # number of bytes in the FCS field
    
    def __init__(self,rxcallback,connectcallback):
        
        # log
        log.info('Creating object')
        
        # store params
        self.rxcallback           = rxcallback
        self.connectcallback      = connectcallback
        
        # initialize parent class
        threading.Thread.__init__(self)
        self.name                 = 'HDLC'
        self.daemon               = True
        
        # local variables
        self.crc                  = Crc.Crc()
        self.connected            = False
        self.comPort              = ''
        self.pyserialHandler      = ''
        self.busySending          = threading.Lock()
        self.busyReceiving        = False
        self.lastRxByte           = self._HDLC_FLAG
        
        # initialize state
        self._restart()
    
    def run(self):
        
        # log
        log.info('thread started')
        
        try:
        
            while self.connected==True:
                try:
                    
                    # received a byte
                    try:
                        rxByte = self.pyserialHandler.read(1)
                    except Exception as err:
                        # work-around for bug in pyserial
                        # https://sourceforge.net/tracker/?func=detail&aid=3591432&group_id=46487&atid=446302
                        raise serial.SerialException(str(err))
                    if not len(rxByte):
                        raise serial.SerialException()
                    
                    # convert the received byte from a character to an int
                    rxByte = ord(rxByte)
                    if      (
                                (not self.busyReceiving)             and
                                self.lastRxByte==self._HDLC_FLAG     and
                                rxByte!=self._HDLC_FLAG
                            ):
                        # start of frame
                        
                        self.busyReceiving            = True
                        self.receivedFrame            = {}
                        self.receivedFrame['payload'] = [rxByte]
                    
                    elif    (
                                self.busyReceiving                   and
                                rxByte!=self._HDLC_FLAG
                            ):
                        # middle of frame
                        
                        if rxByte==self._HDLC_ESCAPE:
                            self._escape = True
                            # do not add this byte to the payload
                        else:
                            if self._escape == True:
                                self.receivedFrame['payload'].append(rxByte^self._HDLC_MASK)
                                self._escape = False
                            else:
                                self.receivedFrame['payload'].append(rxByte)
                    
                    elif    (
                                self.busyReceiving                   and
                                rxByte==self._HDLC_FLAG
                            ):
                        # end of frame
                        
                        self.busyReceiving       = False
                        
                        # split payload and fcs
                        if len(self.receivedFrame['payload'])>self._FCS_LENGTH:
                            temp_payload                   = self.receivedFrame['payload']
                            self.receivedFrame['payload']  = temp_payload[:-2]
                            self.receivedFrame['fcs']      = temp_payload[-2:]
                            
                            # check fcs, write 'valid' field
                            recalculatedCrc                = self.crc.calculate(self.receivedFrame['payload'])
                            if recalculatedCrc==self.receivedFrame['fcs']:
                                self.receivedFrame['valid'] = True
                            else:
                                self.receivedFrame['valid'] = False
                            
                            # log
                            if log.isEnabledFor(logging.DEBUG):
                                output     = []
                                output    += ['\nreceivedFrame:']
                                output    += self._formatFrame(self.receivedFrame)
                                log.debug('\n'.join(output))
                            
                            # callback
                            if self.receivedFrame['valid']==True:
                                try:
                                    self.rxcallback(self.receivedFrame['payload'])
                                except (ConnectionError,CommandError) as err:
                                    output = "@Hdlc: {0}".format(err)
                                    log.error(output)
                                    print output
                        else:
                            output = "@Hdlc: received hdlc frame too short"
                            log.error(output)
                            print output
                        self._restart()
                    
                    # remember the last byte I received
                    self.lastRxByte = rxByte
                    
                except serial.SerialException:
                    self.connected = False
        
        except Exception as err:
            output  = []
            output += ['===== crash in thread {0} ====='.format(self.name)]
            output += ['\nerror:\n']
            output += [str(err)]
            output += ['\ncall stack:\n']
            output += [traceback.format_exc()]
            output  = '\n'.join(output)
            print output # critical error
            log.critical(output)
            raise
        
        del self.crc
        del self.pyserialHandler
        self.connectcallback(self.connected)
        
        # log
        log.info('thread ended')
    
    #======================== public ==========================================
    
    def connect(self,comPort,baudrate=_BAUDRATE):
        self.comPort         = comPort
        try:
            self.pyserialHandler = serial.Serial(self.comPort,baudrate=baudrate)
            self.pyserialHandler.setRTS(False)
            self.pyserialHandler.setDTR(True)
        except serial.serialutil.SerialException as err:
            output = "could not open {0}@{1}baud, reason: {2}".format(self.comPort,baudrate,err)
            log.warning(output)
            raise ConnectionError(output)
        else:
            log.info("opened port {0}@{1}baud".format(self.comPort,baudrate))
            self._restart()
            self.connected = True
            self.connectcallback(self.connected)
            self.name      = '{0}_HDLC'.format(self.comPort)
            self.start()
        return self
    
    def send(self,message):
        
        if not self.connected:
            output = 'not connected'
            log.error(output)
            raise ConnectionError(output)
        
        # calculate fcs
        packetToSend              = {}
        packetToSend['payload']   = message
        packetToSend['fcs']       = self.crc.calculate(packetToSend['payload'])
        packetToSend['valid']     = True
        
        # assemble packet
        packetBytes               = packetToSend['payload']+packetToSend['fcs']
        
        # add HDLC escape characters
        index = 0
        while index<len(packetBytes):
            if packetBytes[index]==self._HDLC_FLAG or packetBytes[index]==self._HDLC_ESCAPE:
                packetBytes.insert(index,self._HDLC_ESCAPE)
                index += 1
                packetBytes[index] = packetBytes[index]^self._HDLC_MASK
            index += 1
        
        # add HDLC flags
        packetBytes.insert(0,self._HDLC_FLAG)
        packetBytes.insert(len(packetBytes),self._HDLC_FLAG)
        
        # log
        if log.isEnabledFor(logging.DEBUG):
            output           = []
            output          += ['\npacketToSend:']
            output          += self._formatFrame(packetToSend)
            log.debug('\n'.join(output))
        
        # reconstitute byteArray
        byteArray            = ''.join([chr(byte) for byte in packetBytes])
        
        # send over serial port
        try:        
            with self.busySending:
                numWritten   = self.pyserialHandler.write(byteArray)
        except IOError, e:
            raise ConnectionError(str(e))

        if numWritten!=len(packetBytes):
            output = 'wrote '+str(numWritten)+' bytes, expected '+str(len(packetBytes))
            log.error(output)
            raise ConnectionError(output)
    
    def disconnect(self):
        log.info("disconnect")
        if self.connected==True:
            self.pyserialHandler.close()
        self.comPort         = ''
        self.name            = 'HDLC'
    
    #======================== support methods for Python "with" statement =====
    
    def __enter__(self):
        pass
    
    def __exit__(self, type, value, tb):
        self.disconnect()

    #======================== private =========================================
    
    def _restart(self):
        self._escape         = False
        self.busyReceiving   = False
        self.lastRxByte      = self._HDLC_FLAG
    
    def _formatFrame(self,frame):
        returnVal  = []
        returnVal += [' - payload: {0}'.format(' '.join(["%.02x"%b for b in frame['payload']]))]
        returnVal += [' - fcs:     {0}'.format(' '.join(["%.02x"%b for b in frame['fcs']]))]
        returnVal += [' - valid:   {0}'.format(frame['valid'])]
        return returnVal
    