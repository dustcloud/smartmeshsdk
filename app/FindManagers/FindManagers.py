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

#============================ classes =========================================

class FindManager(object):
    def __init__(self):
        self.serialScanner = SerialScanner.SerialScanner()
        self.serialScanner.availableManagerNotifier(
           cb = self._availablemanagers_cb,
        )
    def _availablemanagers_cb(self,serialport):
        print "manager available on port {0}".format(serialport)

#============================ CLI handlers ====================================

def quit_clicb():
    print "bye, bye!"
    sys.exit(0)

#============================ main ============================================

def main():
    
    # main app
    findManager = FindManager()
    
    # CLI interface
    cli = DustCli.DustCli(
        quit_cb  = quit_clicb,
        versions = {
            'SmartMesh SDK': sdk_version.VERSION,
        },
    )

if __name__=='__main__':
    main()
