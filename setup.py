'''Setup for SmartMesh SDK python distribution
'''

# Grab the current version from the version file
import os
import sys
import platform

sys.path.append(os.path.join('libs',         'dustUI'))
sys.path.append(os.path.join('libs',         'SmartMeshSDK'))
sys.path.append(os.path.join('app',          'MuxConfig'))
sys.path.append(os.path.join('external_libs','cryptopy'))

import sdk_version

# TODO: include documentation
# TODO: include functional tests

# Platform-specific initialization

NAME = 'SmartMeshSDK'

if platform.system() in ['Darwin']:
    # use setuptools on OS X
    from setuptools import setup
    import py2app

    # use a different name because we're only building one application
    NAME = 'ApiExplorer'

    platform_setup_options = {
        'app': [os.path.join('app', 'APIExplorer', 'APIExplorer.py')],
        'options': { 
            'py2app': {'argv_emulation': True}
        },
        'setup_requires': ['py2app'],
    }

elif platform.system() in ['Windows']:
    # imports for Windows
    # use distutils because it's easier to specify what's included
    from distutils.core import setup
    import py2exe

    platform_setup_options = {
        # py2exe parameters
        'console': [
            {'script': os.path.join('app', 'AclCommissioning', 'AclCommissioning.py'),},
            {'script': os.path.join('app', 'BroadcastLeds', 'BroadcastLeds.py'),},
            {'script': os.path.join('app', 'InstallTest', 'InstallTest.py'),},
            {'script': os.path.join('app', 'JsonServer', 'JsonServer.py'),},
            {'script': os.path.join('app', 'NetworkHealth', 'NetworkHealth.py'),},
            {'script': os.path.join('app', 'OapClient', 'OapClient.py'),},
            {'script': os.path.join('app', 'OTAPCommunicator', 'OTAPCommunicator.py'),},
            {'script': os.path.join('app', 'PublishToWeb', 'PublishToWeb.py'),},
            {'script': os.path.join('app', 'RangeTest', 'RangeTest.py'),},
            {'script': os.path.join('app', 'RawSerial', 'RawSerial.py'),},
            {'script': os.path.join('app', 'Simple', 'SimpleHartMote.py'),},
            {'script': os.path.join('app', 'Simple', 'SimpleIPMgr.py'),},
            {'script': os.path.join('app', 'Simple', 'SimpleIPMote.py'),},
            {'script': os.path.join('app', 'Simple', 'SimpleIPDownstreamMgr.py'),},
            {'script': os.path.join('app', 'Simple', 'SimpleIPDownstreamMote.py'),},
            {'script': os.path.join('app', 'Simple', 'SimpleIPPing.py'),},
            {'script': os.path.join('app', 'Simple', 'SimpleIPUpstreamMgr.py'),},
            {'script': os.path.join('app', 'Simple', 'SimpleIPUpstreamMote.py'),},
            {'script': os.path.join('app', 'SyncTemp', 'SyncTemp.py'),},
            {'script': os.path.join('app', 'SyncTemp', 'logAnalysis.py'),},
            {'script': os.path.join('app', 'TempLogger', 'TempLogger.py'),},
            {'script': os.path.join('app', 'Timelapse', 'Timelapse1Collect.py'),},
        ],
        'windows': [
            {'script': os.path.join('app', 'APIExplorer', 'APIExplorer.py'),},
            {'script': os.path.join('app', 'Chaser', 'Chaser.py'),},
            {'script': os.path.join('app', 'DC2126A', 'DC2126A.py'),},
            {'script': os.path.join('app', 'HdlcTool', 'HdlcTool.py'),},
            {'script': os.path.join('app', 'HrListener', 'HrListener.py'),},
            {'script': os.path.join('app', 'LBRConnection', 'LBRConnection.py'),},
            {'script': os.path.join('app', 'LEDPing', 'LEDPing.py'),},
            {'script': os.path.join('app', 'MeshOfMeshes', 'MeshOfMeshes.py'),},
            {'script': os.path.join('app', 'MgrListener', 'MgrListener.py'),},
            {'script': os.path.join('app', 'MuxConfig', 'MuxConfig.py'),},
            {'script': os.path.join('app', 'PkGen', 'PkGen.py'),},
            {'script': os.path.join('app', 'SensorDataReceiver', 'SensorDataReceiver.py'),},
            {'script': os.path.join('app', 'TempMonitor', 'TempMonitor.py'),},\
            {'script': os.path.join('app', 'Timelapse', 'Timelapse2Analyze.py'),},
            {'script': os.path.join('app', 'Upstream', 'Upstream.py'),},
            {'script': os.path.join('app', 'Voting', 'Voting.py'),},
            {'script': os.path.join('app', 'Xively', 'Xively.py'),},
        ],
        'options': {
            'py2exe': {
                #'bundle_files': 1,
                'dll_excludes': ['MSVCP90.dll', 'w9xpopen.exe'],
            },
        },
        'zipfile': None,
    }

else:
    # use distutils because it's easier to specify what's included
    from distutils.core import setup
    platform_setup_options = {}


setup(
    name           = NAME,
    version        = '.'.join([str(v) for v in sdk_version.VERSION]),
    scripts        = [
        'app/AclCommissioning/AclCommissioning.py',
        'app/APIExplorer/APIExplorer.py',
        'app/BroadcastLeds/BroadcastLeds.py',
        'app/Chaser/Chaser.py',
        'app/DC2126A/DC2126A.py',
        'app/HdlcTool/HdlcTool.py',
        'app/HrListener/HrListener.py',
        'app/InstallTest/InstallTest.py',
        'app/JsonServer/JsonServer.py',
        'app/LBRConnection/LBRConnection.py',
        'app/LEDPing/LEDPing.py',
        'app/MeshOfMeshes/MeshOfMeshes.py',
        'app/MgrListener/MgrListener.py',
        'app/MuxConfig/MuxConfig.py',
        'app/NetworkHealth/NetworkHealth.py',
        'app/OapClient/OapClient.py',
        'app/OTAPCommunicator/OTAPCommunicator.py',
        'app/PkGen/PkGen.py',
        'app/PublishToWeb/PublishToWeb.py',
        'app/PublishToWeb/PublishToWebRandom.py',
        'app/RangeTest/RangeTest.py',
        'app/RawSerial/RawSerial.py',
        'app/SensorDataReceiver/SensorDataReceiver.py',
        'app/Simple/SimpleHartMote.py',
        'app/Simple/SimpleIPMgr.py',
        'app/Simple/SimpleIPMote.py',
        'app/Simple/SimpleIPDownstreamMgr.py',
        'app/Simple/SimpleIPDownstreamMote.py',
        'app/Simple/SimpleIPPing.py',
        'app/Simple/SimpleIPUpstreamMgr.py',
        'app/Simple/SimpleIPUpstreamMote.py',
        'app/SyncTemp/SyncTemp.py',
        'app/SyncTemp/logAnalysis.py',
        'app/TempLogger/TempLogger.py',
        'app/TempMonitor/TempMonitor.py',
        'app/Timelapse/Timelapse1Collect.py',
        'app/Timelapse/Timelapse2Analyze.py',
        'app/Upstream/Upstream.py',
        'app/Voting/Voting.py',
        'app/Xively/Xively.py',
    ],
    # TODO: is there an easier way to include packages recursively? 
    # maybe find_packages? 
    packages       = [
        # from external_libs/
        'bottle',
        'cryptopy',
        'cryptopy.crypto',
        'cryptopy.crypto.cipher',
        'cryptopy.crypto.entropy',
        'cryptopy.crypto.hash',
        'cryptopy.crypto.keyedHash',
        'cryptopy.crypto.passwords',
        'cryptopy.fmath',
        # from libs/
        'dustUI',
        'dustCli',
        'SmartMeshSDK',
        'SmartMeshSDK.ApiDefinition',
        'SmartMeshSDK.HartMgrConnector',
        'SmartMeshSDK.HartMoteConnector',
        'SmartMeshSDK.IpMgrConnectorMux',
        'SmartMeshSDK.IpMgrConnectorSerial',
        'SmartMeshSDK.IpMoteConnector',
        'SmartMeshSDK.LbrConnector',
        'SmartMeshSDK.utils',
        'SmartMeshSDK.protocols',
        'SmartMeshSDK.protocols.DC2126AConverters',
        'SmartMeshSDK.protocols.Hr',
        'SmartMeshSDK.protocols.NetworkHealthAnalyzer',
        'SmartMeshSDK.protocols.oap',
        'SmartMeshSDK.protocols.otap',
        'SmartMeshSDK.protocols.xivelyConnector',
        'SmartMeshSDK.SerialConnector',
        # application-specific packages
        'MuxConfig',
    ],
    package_dir    = {
        'bottle':       'external_libs/bottle',
        'cryptopy':     'external_libs/cryptopy',
        'dustUI':       'libs/dustUI',
        'dustCli':      'libs/dustCli',
        'SmartMeshSDK': 'libs/SmartMeshSDK',
        # application-specific packages
        'MuxConfig':    'app/MuxConfig',
    },
    data_files     = [
        # destination              source
        ('',                       ['DN_LICENSE.txt']),
        ('',                       ['requirements.txt']),
        ('app',                    ['app/logging.conf']),
        
        ('app/AclCommissioning',   ['app/AclCommissioning/README.md']),
        ('app/APIExplorer',        ['app/APIExplorer/README.md']),
        ('app/BroadcastLeds',      ['app/BroadcastLeds/README.md']),
        ('app/Chaser',             ['app/Chaser/README.md']),
        ('app/DC2126A',            ['app/DC2126A/README.md']),
        ('app/HdlcTool',           ['app/HdlcTool/README.md']),
        ('app/HrListener',         ['app/HrListener/README.md']),
        ('app/InstallTest',        ['app/InstallTest/README.md']),
        ('app/LBRConnection',      ['app/LBRConnection/README.md']),
        ('app/LEDPing',            ['app/LEDPing/README.md']),
        ('app/MeshOfMeshes',       ['app/MeshOfMeshes/README.md']),
        ('app/MgrListener',        ['app/MgrListener/README.md']),
        ('app/MuxConfig',          ['app/MuxConfig/README.md']),
        ('app/NetworkHealth',      ['app/NetworkHealth/README.md']),
        ('app/OapClient',          ['app/OapClient/README.md']),
        ('app/OTAPCommunicator',   ['app/OTAPCommunicator/README.md']),
        ('app/PkGen',              ['app/PkGen/README.md']),
        ('app/PublishToWeb',       ['app/PublishToWeb/clouddata_server.py']),
        ('app/PublishToWeb',       ['app/PublishToWeb/README.md']),
        ('app/RangeTest',          ['app/RangeTest/README.md']),
        ('app/RawSerial',          ['app/RawSerial/README.md']),
        ('app/SensorDataReceiver', ['app/SensorDataReceiver/README.md']),
        ('app/Simple',             ['app/Simple/README.md']),
        ('app/SyncTemp',           ['app/SyncTemp/README.md']),
        ('app/TempLogger',         ['app/TempLogger/README.md']),
        ('app/TempMonitor',        ['app/TempMonitor/README.md']),
        ('app/Timelapse',          ['app/Timelapse/README.md']),
        ('app/Upstream',           ['app/Upstream/README.md']),
        ('app/Voting',             ['app/Voting/README.md']),
        ('app/Xively',             ['app/Xively/README.md']),
        
        ('app/LBRConnection',      ['app/LBRConnection/guest.lbrauth']),
        ('app/JsonServer',         ['app/JsonServer/index.html']),
        ('app/JsonServer',         ['app/JsonServer/README.md']),
        ('app/JsonServer/static',  ['app/JsonServer/static/jquery-1.8.0.min.js']),
        ('app/JsonServer/static',  ['app/JsonServer/static/jquery-1.8.0.min.license']),
        ('',                       ['app/SyncTemp/configuration_DO_NOT_DELETE.txt']),
        ('libs/dustUI',            ['libs/dustUI/dust.ico']),
        #('external_libs/cryptopy',['external_libs/cryptopy/LICENSE.txt']),
    ],
    # url          =
    author         = 'Linear Technology',
    author_email   = "dustsupport@linear.com",
    license        = 'see DN_LICENSE.txt',

    # platform-specific options
    **platform_setup_options
)
