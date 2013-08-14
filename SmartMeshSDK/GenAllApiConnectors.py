'''
Created on Mar 26, 2012

@author: alushin
'''

import sys
import os
sys.path.insert(0, os.path.join(sys.path[0], '..'))

import GenApiConnectors
import GenIpMgrSubscribe

#===== SmartMesh IP

GenApiConnectors.genFile ("IpMgrDefinition", 
                          "IpMgrConnectorMux/IpMgrConnectorMux.py", 
                          "Public class for IP manager connector, over SerialMux.")

GenApiConnectors.genFile ("IpMgrDefinition",
                          "IpMgrConnectorSerial/IpMgrConnectorSerial.py",
                          "Public class for IP manager connector, over Serial.")

GenApiConnectors.genFile ("IpMoteDefinition",
                          "IpMoteConnector/IpMoteConnector.py",
                          "Public class for IP mote connector, over Serial.")

GenIpMgrSubscribe.genFile("IpMgrDefinition",
                          "IpMgrConnectorMux/IpMgrSubscribe.py",
                          "Notification subscribe for IpMgrConnectorMux object")

#===== SmartMesh WirelessHART

GenApiConnectors.genFile ("HartMoteDefinition",
                          "HartMoteConnector/HartMoteConnector.py",
                          "Public class for HART mote connector, over Serial.")

GenApiConnectors.genFile ("HartMgrDefinition", 
                          "HartMgrConnector/HartMgrConnector.py", 
                          "Public class for HART manager connector, over XML-RPC.")
