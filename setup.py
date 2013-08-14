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

import sdk_version

# Create the SmartMesh SDK package

SCRIPTS    = [
                #'Analysis/Analysis.py',
                'APIExplorer/APIExplorer.py',
                'InstallTest/InstallTest.py',
                'LBRConnection/LBRConnection.py',
                'LEDPing/LEDPing.py',
                'MgrListener/MgrListener.py',
                'MuxConfig/MuxConfig.py',
                'OTAPCommunicator/OTAPCommunicator.py',
                #'NetworkSnapshot/NetworkSnapshot.py',
                'PkGen/PkGen.py',
                'SensorDataReceiver/SensorDataReceiver.py',
                'Simple/SimpleHartMote.py',
                'Simple/SimpleIPMgr.py',
                'Simple/SimpleIPMote.py',
                'TempMonitor/TempMonitor.py',
                'Upstream/Upstream.py',
             ]

FILES      = [ ('bin/LBRConnection', ['bin/LBRConnection/guest.lbrauth']),
               ('',                  ['DN_LICENSE.txt']),
             ]

FUNC_TESTS = []

# TODO: include documentation
# TODO: include functional tests

setup(name='SmartMeshSDK',
      version='.'.join([str(v) for v in sdk_version.VERSION]),
      scripts=[os.path.join('bin', s) for s in SCRIPTS] + [os.path.join('func_tests', s) for s in FUNC_TESTS],
      # TODO: is there an easier way to include packages recursively? 
      # maybe find_packages? 
      packages=['Gateway',
                'Gateway.NetworkTest',
                'Gateway.NetworkTestPublisher',
                'dustUI',
                'SmartMeshSDK',
                'SmartMeshSDK.ApiDefinition',
                'SmartMeshSDK.HartMgrConnector',
                'SmartMeshSDK.HartMoteConnector',
                'SmartMeshSDK.IpMgrConnectorMux',
                'SmartMeshSDK.IpMgrConnectorSerial',
                'SmartMeshSDK.IpMoteConnector',
                'SmartMeshSDK.LbrConnector',
                'SmartMeshSDK.SerialConnector',
                'SmartMeshSDK.OTAP',
                'crypto',
                'crypto.cipher',
                'crypto.entropy',
                'crypto.hash',
                'crypto.keyedHash',
                'crypto.passwords',
                'oap',
                'fmath',
                # application-specific packages
                'MuxConfig',
                ],
                
      package_dir={'': '.',
                   'crypto': 'cryptopy/crypto',
                   'fmath': 'cryptopy/fmath',
                   'oap': 'protocols/oap',
                   # application-specific packages
                   'MuxConfig': 'bin/MuxConfig'
                   },
      
      data_files = FILES,

      # url=
      author='Linear Technology',
      author_email="dust-support@linear.com",
      license='see DN_LICENSE.txt',

      # py2exe parameters
      console=  [
                    {'script': os.path.join('bin', 'InstallTest', 'InstallTest.py'),},
                    #{'script': os.path.join('bin', 'NetworkSnapshot', 'NetworkSnapshot.py'),},
                    {'script': os.path.join('bin', 'Simple', 'SimpleIPMgr.py'),},
                    {'script': os.path.join('bin', 'Simple', 'SimpleIPMote.py'),},
                    {'script': os.path.join('bin', 'Simple', 'SimpleHartMote.py'),},
                    {'script': os.path.join('bin', 'OTAPCommunicator', 'OTAPCommunicator.py'),},
                ],
      windows=  [
                    #{'script': os.path.join('bin', 'Analysis', 'Analysis.py'),},
                    {'script': os.path.join('bin', 'APIExplorer', 'APIExplorer.py'),},
                    {'script': os.path.join('bin', 'LBRConnection', 'LBRConnection.py'),},
                    {'script': os.path.join('bin', 'LEDPing', 'LEDPing.py'),},
                    {'script': os.path.join('bin', 'MgrListener', 'MgrListener.py'),},
                    {'script': os.path.join('bin', 'MuxConfig', 'MuxConfig.py'),},
                    {'script': os.path.join('bin', 'PkGen', 'PkGen.py'),},
                    {'script': os.path.join('bin', 'SensorDataReceiver', 'SensorDataReceiver.py'),},
                    {'script': os.path.join('bin', 'TempMonitor', 'TempMonitor.py'),},
                    {'script': os.path.join('bin', 'Upstream', 'Upstream.py'),},
                ],
      zipfile=None,
      options={ 'py2exe': { #'bundle_files': 1,
                            'dll_excludes': ['MSVCP90.dll', 'w9xpopen.exe'], },
                },

      )
