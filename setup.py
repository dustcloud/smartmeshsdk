'''Setup for SmartMesh SDK python distribution
'''

# Grab the current version from the version file
import os
import sys
import platform

sys.path.append(os.path.join('libs',         'dustUI'))
sys.path.append(os.path.join('libs',         'SmartMeshSDK'))
sys.path.append(os.path.join('libs',         'VManagerSDK'))
sys.path.append(os.path.join('app',          'MuxConfig'))
sys.path.append(os.path.join('external_libs','cryptopy'))

import sdk_version

# TODO: include documentation
# TODO: include functional tests

# Platform-specific initialization

NAME = 'SmartMeshSDK'

VMANAGER_REQUIRES = ["urllib3 >= 1.10", "six >= 1.9", "certifi", "python-dateutil"]

ssl_ca_cert = []

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
    from setuptools import setup, find_packages

    #import py2exe
    import certifi
    
    ssl_ca_cert.append(certifi.where())

    platform_setup_options = {
        # py2exe parameters
        'console': [
            # embedded manager apps
            {'script': os.path.join('app', 'AclCommissioning', 'AclCommissioning.py'),},
            {'script': os.path.join('app', 'BlinkPacketSend', 'BlinkPacketSend.py'),},
            {'script': os.path.join('app', 'BroadcastLeds', 'BroadcastLeds.py'),},
            {'script': os.path.join('app', 'FindManagers', 'FindManagers.py'),},
            {'script': os.path.join('app', 'InstallTest', 'InstallTest.py'),},
            {'script': os.path.join('app', 'JsonServer', 'JsonServer.py'),},
            {'script': os.path.join('app', 'MgrBlinkData', 'MgrBlinkData.py'),},
            {'script': os.path.join('app', 'NetworkHealth', 'NetworkHealth.py'),},
            {'script': os.path.join('app', 'OapClient', 'OapClient.py'),},
            {'script': os.path.join('app', 'OTAPCommunicator', 'OTAPCommunicator.py'),},
            {'script': os.path.join('app', 'PublishToWeb', 'PublishToWeb.py'),},
            {'script': os.path.join('app', 'RangeTest', 'RangeTest.py'),},
            {'script': os.path.join('app', 'RawSerial', 'RawSerial.py'),},
            {'script': os.path.join('app', 'SeeTheMesh', 'SeeTheMesh.py'),},
            {'script': os.path.join('app', 'SerialScanner', 'SerialScanner.py'),},
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
            # VManager apps
            {'script': os.path.join('vmanager_apps', 'VMgr_OTAPCommunicator.py'),},
            {'script': os.path.join('vmanager_apps', 'VMgr_PublishToWeb.py'),},
            {'script': os.path.join('vmanager_apps', 'VMgr_SendPing.py'),},
            {'script': os.path.join('vmanager_apps', 'VMgr_TemperatureData.py'),},
            {'script': os.path.join('vmanager_apps', 'VMgr_BasicExample.py'),},
            {'script': os.path.join('vmanager_apps', 'VMgr_BlinkData.py'),},
            {'script': os.path.join('vmanager_apps', 'VMgr_LatencyMote.py'),},
            {'script': os.path.join('vmanager_apps', 'VMgr_LatencyNotifs.py'),},
            {'script': os.path.join('vmanager_apps', 'VMgr_LEDOnOff.py'),},
            {'script': os.path.join('vmanager_apps', 'VMgr_OAPsend.py'),},
            {'script': os.path.join('vmanager_apps', 'VMgr_PktPerSec.py'),},
            {'script': os.path.join('vmanager_apps', 'VMgr_UserCreate-Delete.py'),},
            {'script': os.path.join('vmanager_apps', 'VMgr_AllNotifications.py'),},
        ],
        'windows': [
            {'script': os.path.join('app', 'APIExplorer', 'APIExplorer.py'),},
            {'script': os.path.join('app', 'Chaser', 'Chaser.py'),},
            {'script': os.path.join('app', 'HdlcTool', 'HdlcTool.py'),},
            {'script': os.path.join('app', 'HrListener', 'HrListener.py'),},
            {'script': os.path.join('app', 'LBRConnection', 'LBRConnection.py'),},
            {'script': os.path.join('app', 'LEDPing', 'LEDPing.py'),},
            {'script': os.path.join('app', 'MgrListener', 'MgrListener.py'),},
            {'script': os.path.join('app', 'PkGen', 'PkGen.py'),},
            {'script': os.path.join('app', 'SensorDataReceiver', 'SensorDataReceiver.py'),},
            {'script': os.path.join('app', 'TempMonitor', 'TempMonitor.py'),},\
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
        # embedded manager scripts
        'app/AclCommissioning/AclCommissioning.py',
        'app/APIExplorer/APIExplorer.py',
        'app/BlinkPacketSend/BlinkPacketSend.py',
        'app/BroadcastLeds/BroadcastLeds.py',
        'app/Chaser/Chaser.py',
        'app/FindManagers/FindManagers.py',
        'app/HdlcTool/HdlcTool.py',
        'app/HrListener/HrListener.py',
        'app/InstallTest/InstallTest.py',
        'app/JsonServer/JsonServer.py',
        'app/LBRConnection/LBRConnection.py',
        'app/LEDPing/LEDPing.py',
        'app/MgrBlinkData/MgrBlinkData.py',
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
        'app/SeeTheMesh/SeeTheMesh.py',
        'app/SensorDataReceiver/SensorDataReceiver.py',
        'app/SerialScanner/SerialScanner.py',
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
        # VManager scripts
        'vmanager_apps/VMgr_OTAPCommunicator.py',
        'vmanager_apps/VMgr_PublishToWeb.py',
        'vmanager_apps/VMgr_SendPing.py',
        'vmanager_apps/VMgr_TemperatureData.py',
        'vmanager_apps/VMgr_BasicExample.py',
        'vmanager_apps/VMgr_BlinkData.py',
        'vmanager_apps/VMgr_LatencyMote.py',
        'vmanager_apps/VMgr_LatencyNotifs.py',
        'vmanager_apps/VMgr_LEDOnOff.py',
        'vmanager_apps/VMgr_OAPsend.py',
        'vmanager_apps/VMgr_PktPerSec.py',
        'vmanager_apps/VMgr_UserCreate-Delete.py',
        'vmanager_apps/VMgr_AllNotifications.py',
    ],
    # TODO: is there an easier way to include packages recursively? 
    # maybe find_packages? 
    packages       = [
        # from external_libs/
        'cryptopy',
        'cryptopy.crypto',
        'cryptopy.crypto.cipher',
        'cryptopy.crypto.entropy',
        'cryptopy.crypto.hash',
        'cryptopy.crypto.keyedHash',
        'cryptopy.crypto.passwords',
        'cryptopy.fmath',
        # from libs/
        # 'dustUI',
        # 'dustCli',
        # 'SmartMeshSDK',
        # 'SmartMeshSDK.ApiDefinition',
        # 'SmartMeshSDK.HartMgrConnector',
        # 'SmartMeshSDK.HartMoteConnector',
        # 'SmartMeshSDK.IpMgrConnectorMux',
        # 'SmartMeshSDK.IpMgrConnectorSerial',
        # 'SmartMeshSDK.IpMoteConnector',
        # 'SmartMeshSDK.LbrConnector',
        # 'SmartMeshSDK.utils',
        # 'SmartMeshSDK.protocols',
        # 'SmartMeshSDK.protocols.blink',
        # 'SmartMeshSDK.protocols.Hr',
        # 'SmartMeshSDK.protocols.NetworkHealthAnalyzer',
        # 'SmartMeshSDK.protocols.oap',
        # 'SmartMeshSDK.protocols.otap',
        # 'SmartMeshSDK.protocols.xivelyConnector',
        # 'SmartMeshSDK.SerialConnector',
        # packages for VManager
        'VManagerSDK',
        'VManagerSDK.vmanager',
        'VManagerSDK.vmanager.apis',
        'VManagerSDK.vmanager.models',
        # application-specific packages
        'MuxConfig',
    ] + find_packages('libs'),
    package_dir    = {
        'cryptopy':     'external_libs/cryptopy',
        '': 'libs',
        #'dustUI':       'libs/dustUI',
        #'dustCli':      'libs/dustCli',
        #'SmartMeshSDK': 'libs/SmartMeshSDK',
        #'VManagerSDK':  'libs/VManagerSDK',
        # application-specific packages
        'MuxConfig':    'app/MuxConfig',
    },
    data_files     = [
        # destination              source
        ('',                       ssl_ca_cert),
        ('',                       ['DN_LICENSE.txt']),
        ('',                       ['requirements.txt']),
        ('app',                    ['app/logging.conf']),
        ('app/AclCommissioning',   ['app/AclCommissioning/README.md']),
        ('app/APIExplorer',        ['app/APIExplorer/README.md']),
        ('app/BlinkPacketSend',    ['app/BlinkPacketSend/README.md']),
        ('app/BroadcastLeds',      ['app/BroadcastLeds/README.md']),
        ('app/Chaser',             ['app/Chaser/README.md']),
        ('app/HdlcTool',           ['app/HdlcTool/README.md']),
        ('app/HrListener',         ['app/HrListener/README.md']),
        ('app/InstallTest',        ['app/InstallTest/README.md']),
        ('app/JsonServer',         ['app/JsonServer/index.html']),
        ('app/JsonServer',         ['app/JsonServer/README.md']),
        ('app/JsonServer',         ['app/JsonServer/postman_collection.json']),
        ('app/JsonServer',         ['app/JsonServer/postman_environment.json']),
        ('app/JsonServer',         ['app/JsonServer/NotifReceiver.py']),
        ('app/JsonServer/static',  ['app/JsonServer/static/jquery-1.8.0.min.js']),
        ('app/JsonServer/static',  ['app/JsonServer/static/jquery-1.8.0.min.license']),
        ('app/LBRConnection',      ['app/LBRConnection/guest.lbrauth']),
        ('app/LBRConnection',      ['app/LBRConnection/README.md']),
        ('app/LEDPing',            ['app/LEDPing/README.md']),
        ('app/MgrBlinkData',       ['app/MgrBlinkData/README.md']),
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
        ('app/SeeTheMesh/static',  ['app/SeeTheMesh/static/background.jpg']),
        ('app/SeeTheMesh/static',  ['app/SeeTheMesh/static/d3.v3.min.js']),
        ('app/SeeTheMesh/static',  ['app/SeeTheMesh/static/dagre-d3.js']),
        ('app/SeeTheMesh/static',  ['app/SeeTheMesh/static/icon_box.png']),
        ('app/SeeTheMesh/static',  ['app/SeeTheMesh/static/icon_hub.png']),
        ('app/SeeTheMesh/static',  ['app/SeeTheMesh/static/jquery-3.1.1.min.js']),
        ('app/SeeTheMesh/static',  ['app/SeeTheMesh/static/logo_dust.png']),
        ('app/SeeTheMesh/static',  ['app/SeeTheMesh/static/logo_map.png']),
        ('app/SeeTheMesh/static',  ['app/SeeTheMesh/static/logo_topology.png']),
        ('app/SeeTheMesh/static',  ['app/SeeTheMesh/static/map.js']),
        ('app/SeeTheMesh/static',  ['app/SeeTheMesh/static/style.css']),
        ('app/SeeTheMesh/views',   ['app/SeeTheMesh/views/map.tpl']),
        ('app/SeeTheMesh/views',   ['app/SeeTheMesh/views/topology.tpl']),
        ('app/SensorDataReceiver', ['app/SensorDataReceiver/README.md']),
        ('app/Simple',             ['app/Simple/README.md']),
        ('app/SyncTemp',           ['app/SyncTemp/README.md']),
        ('app/TempLogger',         ['app/TempLogger/README.md']),
        ('app/TempMonitor',        ['app/TempMonitor/README.md']),
        ('app/Timelapse',          ['app/Timelapse/README.md']),
        ('app/Upstream',           ['app/Upstream/README.md']),
        ('app/Voting',             ['app/Voting/README.md']),
        ('app/Xively',             ['app/Xively/README.md']),
        ('',                       ['app/SyncTemp/configuration_DO_NOT_DELETE.txt']),
        ('libs/dustUI',            ['libs/dustUI/dust.ico']),
        #('external_libs/cryptopy',['external_libs/cryptopy/LICENSE.txt']),
    ],
    # url          =
    author         = 'Analog Devices',
    author_email   = "dustsupport@analog.com",
    license        = 'see DN_LICENSE.txt',

    # TODO: install_requires

    # platform-specific options
    **platform_setup_options
)
