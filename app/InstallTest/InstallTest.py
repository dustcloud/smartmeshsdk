#!/usr/bin/python

#============================ adjust path =====================================

import sys
import os
if __name__ == "__main__":
    here = sys.path[0]
    sys.path.insert(0, os.path.join(here, '..', '..','libs'))
    sys.path.insert(0, os.path.join(here, '..', '..','external_libs'))

#============================ imports =========================================

from SmartMeshSDK       import sdk_version
from SmartMeshSDK.utils import SmsdkInstallVerifier

#============================ main ============================================

def verifyOneComponent(name):
    print "\nTesting installation of "+name+"..."
    (goodToGo,reason) = SmsdkInstallVerifier.verifyComponents([name])
    if goodToGo:
        print 'PASS!'
        print reason
    else:
        print 'FAIL!'
        if name==SmsdkInstallVerifier.PYWIN32:
            print "Note: {0} is only required to run the MuxConfig application.".format(SmsdkInstallVerifier.PYWIN32)
        print reason
    return goodToGo

def main():
    version_str = '.'.join([str(v) for v in sdk_version.VERSION])
    print "Installation test script - Dust Networks SmartMeshSDK v{0}".format(version_str)

    wait_for_user = True
    components = [SmsdkInstallVerifier.PYTHON,
                  SmsdkInstallVerifier.PYSERIAL, ]
    # expect pywin32 on Windows
    if os.name in ['nt']:
        components += [SmsdkInstallVerifier.PYWIN32,]

    # LATER: do we need to allow list of tests to be input on the command line?
    for arg in sys.argv:
        if arg == '-q' or arg == '--no-wait':
            wait_for_user = False

    results = [verifyOneComponent(c) for c in components]
    exit_code = 0
    if False in results:
        exit_code = 1

    if wait_for_user:
        raw_input("\nPress Enter to exit.")
        
    sys.exit(exit_code)


if __name__ == "__main__":
    main()
