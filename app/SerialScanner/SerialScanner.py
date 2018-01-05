#!/usr/bin/python

#============================ adjust path =====================================

import sys
import os
if __name__ == "__main__":
    here = sys.path[0]
    sys.path.insert(0, os.path.join(here, '..', '..','libs'))
    sys.path.insert(0, os.path.join(here, '..', '..','external_libs'))

#============================ imports =========================================

# SmartMeshSDK
from SmartMeshSDK       import sdk_version
from SmartMeshSDK.utils import SerialScanner

# DustCli
from dustCli            import DustCli

#============================ defines =========================================

#============================ CLI handlers ====================================

def quit_clicb():
    print "bye, bye!"
    sys.exit(0)

def listmanagers_clicb(params):
    serialScanner = SerialScanner.SerialScanner()
    print serialScanner.listIpManagerApi()

def availablemanagers_clicb_cb(serialport):
    print "manager available on port {0}".format(serialport)

def availablemanagers_clicb(params):
    serialScanner = SerialScanner.SerialScanner()
    serialScanner.availableManagerNotifier(
       cb = availablemanagers_clicb_cb,
    )

def full_clicb(params):
    serialScanner = SerialScanner.SerialScanner()
    allSerialPorts = serialScanner.listAllSerialPorts()
    print 'all serial ports: {0}'.format(allSerialPorts)
    for sp in allSerialPorts:
        print 'testing serial port {0}'.format(sp)
        print '- canOpen?        {0}'.format(serialScanner.canOpen(sp))
        print '- isIpMoteApi?    {0}'.format(serialScanner.isIpMoteApi(sp))
        print '- isIpManagerApi? {0}'.format(serialScanner.isIpManagerApi(sp))

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
        name                      = 'listmanagers',
        alias                     = 'lm',
        description               = 'list SmartMesh IP Managers',
        params                    = [],
        callback                  = listmanagers_clicb,
    )
    cli.registerCommand(
        name                      = 'availablemanagers',
        alias                     = 'am',
        description               = 'notify about available Managers',
        params                    = [],
        callback                  = availablemanagers_clicb,
    )
    cli.registerCommand(
        name                      = 'full',
        alias                     = 'f',
        description               = 'full scan WARNING: resets all DC2274 boards!',
        params                    = [],
        callback                  = full_clicb,
    )

if __name__=='__main__':
    main()
