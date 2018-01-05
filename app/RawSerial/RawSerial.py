#!/usr/bin/python

#============================ adjust path =====================================

import sys
import os
if __name__ == "__main__":
    here = sys.path[0]
    sys.path.insert(0, os.path.join(here, '..', '..','libs'))
    sys.path.insert(0, os.path.join(here, '..', '..','external_libs'))

#============================ imports =========================================

# built-in
import threading
import serial
import binascii

# SmartMeshSDK
from SmartMeshSDK       import sdk_version

# DustCli
from dustCli            import DustCli

#============================ defines =========================================

BAUDRATE      = 115200

#============================ globals =========================================

serialHandler = None

#============================ serial receiver =================================

class SerialReceiver(threading.Thread):
    
    def __init__(self,serialHandler):
        # store params
        self.serialHandler = serialHandler
        
        # initialize thread
        threading.Thread.__init__(self)
        self.name = 'SerialReceiver'
        
        # start myself
        self.start()
    
    def run(self):
        while True:
            try:
                rxByte = self.serialHandler.read(1)
            except Exception as err:
                output  = []
                output += ['ERROR while reading from serial port']
                output += ['error type: {0}'.format(type(err))]
                output += ['{0}'.format(err)]
                output  = '\n'.join(output)
                print output
                return
            else:
                print 'rxByte: {0:02x}'.format(ord(rxByte))

#============================ CLI handlers ====================================

def quit_clicb():
    global serialHandler
    
    print "quitting!"
    
    serialHandler.close()

def connect_clicb(params):
    global serialHandler
    
    portname = params[0]
    try:
        baudrate = int(params[1])
    except:
        baudrate = BAUDRATE
    
    print 'opening {0}@{1}baud'.format(portname,baudrate)
    
    if serialHandler!=None:
        print 'ERROR: already connected. Restart the application to connect to a different port.'
        return
    
    try:
        # open serial port
        serialHandler = serial.Serial(portname,baudrate=baudrate)
        
        # set flow handling pins
        serialHandler.setRTS(False)
        serialHandler.setDTR(True)
        
        # start the receiving thread
        SerialReceiver(serialHandler)
        
    except Exception as err:
        output  = []
        output += ['ERROR: could not connect to {0}'.format(portname)]
        output += ['error type: {0}'.format(type(err))]
        output += ['{0}'.format(err)]
        output  = '\n'.join(output)
        print output
        return
    else:
        print 'connected successfully'

def baudrate_clicb(params):
    global serialHandler
    
    baudrate = params[0]
    
    if serialHandler==None:
        print 'ERROR: not connected.'
        return
    
    serialHandler.baudrate = baudrate

def tx_clicb(params):
    global serialHandler
    
    bytesToTx = params[0]
    
    if serialHandler==None:
        print 'ERROR: not connected.'
        return
    
    # convert from hex string to binary
    try:
        bytesToTx = binascii.unhexlify(bytesToTx)
    except Exception as err:
        output  = []
        output += ['ERROR: invalid hexadecimal string "{0}"'.format(bytesToTx)]
        output  = '\n'.join(output)
        print output
        return
    
    # transmit over serial port
    try:
        serialHandler.write(bytesToTx)
    except Exception as err:
        output  = []
        output += ['ERROR: could not write to serial port']
        output += ['error type: {0}'.format(type(err))]
        output += ['{0}'.format(err)]
        print output
        return

#============================ main ============================================

def main():
    
    # create CLI interface
    cli = DustCli.DustCli(
        quit_cb  = quit_clicb,
        versions = {
            'SmartMesh SDK': sdk_version.VERSION,
        },
    )
    cli.registerCommand(
        name                      = 'connect',
        alias                     = 'c',
        description               = 'connnect to a serial port',
        params                    = ['portname'],
        callback                  = connect_clicb,
        dontCheckParamsLength     = True,
    )
    cli.registerCommand(
        name                      = 'baudrate',
        alias                     = 'b',
        description               = 'set the baudrate',
        params                    = ['baurate'],
        callback                  = baudrate_clicb,
    )
    cli.registerCommand(
        name                      = 'tx',
        alias                     = 'tx',
        description               = 'transmit a number of bytes, represented in hexadecimal (e.g. "ab12eb44")',
        params                    = ['bytesToTx'],
        callback                  = tx_clicb,
    )

if __name__=='__main__':
    main()

