# use distutils because it's easier to specify what's included
from distutils.core import setup
try:
    import py2exe
except ImportError:
    pass

# Grab the current version from the version file
import os
import sys

# add SmartMeshSDK, dustUI to the path because that what the binaries expect
sys.path.append('dustUI')
sys.path.append('SmartMeshSDK')
sys.path.append(os.path.join('bin', 'MuxConfig'))
sys.path.append('cryptopy')

import sdk_version

# TODO: include documentation
# TODO: include functional tests

setup(
    name           = 'SmartMeshSDK',
    version        = '.'.join([str(v) for v in sdk_version.VERSION]),
    scripts        = [
        'bin/APIExplorer/APIExplorer.py',
        'bin/DC2126A/DC2126A.py',
        'bin/HrListener/HrListener.py',
        'bin/InstallTest/InstallTest.py',
        'bin/LBRConnection/LBRConnection.py',
        'bin/LEDPing/LEDPing.py',
        'bin/MgrListener/MgrListener.py',
        'bin/MuxConfig/MuxConfig.py',
        'bin/OTAPCommunicator/OTAPCommunicator.py',
        'bin/PkGen/PkGen.py',
        'bin/SensorDataReceiver/SensorDataReceiver.py',
        'bin/Simple/SimpleHartMote.py',
        'bin/Simple/SimpleIPMgr.py',
        'bin/Simple/SimpleIPMote.py',
        'bin/TempMonitor/TempMonitor.py',
        'bin/Upstream/Upstream.py',
        'bin/Xively/Xively.py',
    ],
    # TODO: is there an easier way to include packages recursively? 
    # maybe find_packages? 
    packages       = [
        'cryptopy',
        'cryptopy.crypto',
        'cryptopy.crypto.cipher',
        'cryptopy.crypto.entropy',
        'cryptopy.crypto.hash',
        'cryptopy.crypto.keyedHash',
        'cryptopy.crypto.passwords',
        'cryptopy.fmath',
        'dustUI',
        'SmartMeshSDK',
        'SmartMeshSDK.ApiDefinition',
        'SmartMeshSDK.HartMgrConnector',
        'SmartMeshSDK.HartMoteConnector',
        'SmartMeshSDK.IpMgrConnectorMux',
        'SmartMeshSDK.IpMgrConnectorSerial',
        'SmartMeshSDK.IpMoteConnector',
        'SmartMeshSDK.LbrConnector',
        'SmartMeshSDK.protocols',
        'SmartMeshSDK.protocols.DC2126AConverters',
        'SmartMeshSDK.protocols.oap',
        'SmartMeshSDK.protocols.otap',
        'SmartMeshSDK.protocols.xivelyConnector',
        'SmartMeshSDK.SerialConnector',
        # application-specific packages
        'MuxConfig',
    ],
    package_dir    = {
        '':             '.',
        # application-specific packages
        'MuxConfig':    'bin/MuxConfig',
    },
    data_files     = [
        ('',                  ['DN_LICENSE.txt']),
        ('',                  ['requirements.txt']),
        ('bin',               ['bin/logging.conf']),
        ('bin/LBRConnection', ['bin/LBRConnection/guest.lbrauth']),
        ('dustUI',            ['dustUI/dust.ico']),
        #('cryptopy',          ['cryptopy/LICENSE.txt']),
    ],
    # url          =
    author         = 'Linear Technology',
    author_email   = "dust-support@linear.com",
    license        = 'see DN_LICENSE.txt',
    # py2exe parameters
    console        = [
        {'script': os.path.join('bin', 'InstallTest', 'InstallTest.py'),},
        {'script': os.path.join('bin', 'OTAPCommunicator', 'OTAPCommunicator.py'),},
        {'script': os.path.join('bin', 'Simple', 'SimpleHartMote.py'),},
        {'script': os.path.join('bin', 'Simple', 'SimpleIPMgr.py'),},
        {'script': os.path.join('bin', 'Simple', 'SimpleIPMote.py'),},
    ],
    windows        = [
        {'script': os.path.join('bin', 'APIExplorer', 'APIExplorer.py'),},
        {'script': os.path.join('bin', 'DC2126A', 'DC2126A.py'),},
        {'script': os.path.join('bin', 'HrListener', 'HrListener.py'),},
        {'script': os.path.join('bin', 'LBRConnection', 'LBRConnection.py'),},
        {'script': os.path.join('bin', 'LEDPing', 'LEDPing.py'),},
        {'script': os.path.join('bin', 'MgrListener', 'MgrListener.py'),},
        {'script': os.path.join('bin', 'MuxConfig', 'MuxConfig.py'),},
        {'script': os.path.join('bin', 'PkGen', 'PkGen.py'),},
        {'script': os.path.join('bin', 'SensorDataReceiver', 'SensorDataReceiver.py'),},
        {'script': os.path.join('bin', 'TempMonitor', 'TempMonitor.py'),},
        {'script': os.path.join('bin', 'Upstream', 'Upstream.py'),},
        {'script': os.path.join('bin', 'Xively', 'Xively.py'),},
    ],
    zipfile        = None,
    options        = {
        'py2exe': {
            #'bundle_files': 1,
            'dll_excludes': ['MSVCP90.dll', 'w9xpopen.exe'],
        },
    },
)
