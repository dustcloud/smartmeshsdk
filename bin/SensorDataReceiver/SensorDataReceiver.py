#!/usr/bin/python

# add the SmartMeshSDK/ folder to the path
import sys
import os

temp_path = sys.path[0]
if temp_path:
    sys.path.insert(0, os.path.join(temp_path, '..', '..', 'dustUI'))
    sys.path.insert(0, os.path.join(temp_path, '..', '..', 'SmartMeshSDK'))

# verify installation
import SmsdkInstallVerifier
(goodToGo,reason) = SmsdkInstallVerifier.verifyComponents(
                            [
                                SmsdkInstallVerifier.PYTHON,
                                SmsdkInstallVerifier.PYSERIAL,
                            ]
                        )
if not goodToGo:
    print "Your installation does not allow this application to run:\n"
    print reason
    raw_input("Press any button to exit")
    sys.exit(1)

import Tkinter
import threading

from dustWindow           import dustWindow
from dustFrameConnection  import dustFrameConnection
from dustFrameSensorData  import dustFrameSensorData

from ApiDefinition  import IpMgrDefinition

from IpMgrConnectorMux  import IpMgrConnectorMux
from IpMgrConnectorMux  import IpMgrSubscribe

from optparse import OptionParser

UPDATEPERIOD = 500 # in ms
DEFAULT_HOST = '127.0.0.1'
DEFAULT_PORT = 9900

class notifClient(object):
    '''
    \ingroup MgrListener
    '''
    
    def __init__(self, connector, disconnectedCallback):
        
        # store params
        self.connector = connector
        self.disconnectedCallback = disconnectedCallback
        
        # variables
        self.data      = None
        self.dataLock  = threading.Lock()
        
        # subscriber
        self.subscriber = IpMgrSubscribe.IpMgrSubscribe(self.connector)
        self.subscriber.start()
        self.subscriber.subscribe(
            notifTypes =    [
                                IpMgrSubscribe.IpMgrSubscribe.NOTIFDATA,
                            ],
            fun =           self._notifDataCallback,
            isRlbl =        False,
        )
        self.subscriber.subscribe(
            notifTypes =    [
                                IpMgrSubscribe.IpMgrSubscribe.ERROR,
                                IpMgrSubscribe.IpMgrSubscribe.FINISH,
                            ],
            fun =           self.disconnectedCallback,
            isRlbl =        True,
        )
    
    #======================== public ==========================================
    
    def getSensorData(self):
        self.dataLock.acquire()
        if self.data:
            returnVal = self.data.copy()
            self.data = None
        else:
            returnVal = None
        self.dataLock.release()
        return returnVal
        
    def disconnect(self):
        self.connector.disconnect()
    
    #======================== private =========================================
    
    def _notifDataCallback(self,notifName,notifParams):
        
        self.dataLock.acquire()
        self.data              = {}
        self.data['srcMac']    = notifParams.macAddress
        self.data['srcPort']   = notifParams.srcPort
        self.data['destPort']  = notifParams.dstPort
        self.data['payload']   = notifParams.data
        self.data['ts_sec']    = notifParams.utcSecs
        self.data['ts_usec']   = notifParams.utcUsecs
        self.dataLock.release()

class dataGui(object):
    '''
    \ingroup MgrListener
    '''
   
    def __init__(self):
        
        # local variables
        self.guiLock            = threading.Lock()
        self.apiDef             = IpMgrDefinition.IpMgrDefinition()
        self.notifClientHandler = None
        
        # create window
        self.window = dustWindow('SensorDataReceiver',
                                 self._windowCb_close)
                                 
        # add a connection frame
        self.connectionFrame = dustFrameConnection(
                                    self.window,
                                    self.guiLock,
                                    self._connectionFrameCb_connected,
                                    frameName="manager connection",
                                    row=0,column=0)
        self.connectionFrame.apiLoaded(self.apiDef)
        self.connectionFrame.show()
        
        # add a sensor data frame
        self.sensorDataFrame = dustFrameSensorData(self.window,
                                         self.guiLock,
                                         frameName="received sensor data",
                                         row=1,column=0)
        self.sensorDataFrame.show()
    
    #======================== public ==========================================
    
    def start(self, connect_params):
        
        # start Tkinter's main thead
        try:
            self.window.mainloop()
        except SystemExit:
            sys.exit()

    #======================== private =========================================
    
    def _windowCb_close(self):
        if self.notifClientHandler:
            self.notifClientHandler.disconnect()
    
    def _connectionFrameCb_connected(self,connector):
        '''
        \brief Called when the connectionFrame has connected.
        '''
        
        # store the connector
        self.connector = connector
        
        # schedule the GUI to update itself in UPDATEPERIOD ms
        self.sensorDataFrame.after(UPDATEPERIOD,self._updateSensorData)
        
        # start a notification client
        self.notifClientHandler = notifClient(
                    self.connector,
                    self._connectionFrameCb_disconnected
                )
        
    def _connectionFrameCb_disconnected(self,notifName,notifParams):
        '''
        \brief Called when the connectionFrame has disconnected.
        '''
        
        # update the GUI
        self.connectionFrame.updateGuiDisconnected()
        
        # delete the connector
        self.connector = None
    
    def _updateSensorData(self):
        
        # get the data
        sensorDataToDisplay = self.notifClientHandler.getSensorData()
        
        # update the frame
        if sensorDataToDisplay:
            self.sensorDataFrame.update(sensorDataToDisplay)
        
        # schedule the next update
        self.sensorDataFrame.after(UPDATEPERIOD,self._updateSensorData)
        
    
def main(connect_params):
    dataGuiHandler = dataGui()
    dataGuiHandler.start(connect_params)

if __name__ == '__main__':
    # Parse the command line
    parser = OptionParser("usage: %prog [options]", version="%prog 1.0")
    parser.add_option("--host", dest="host", 
                      default=DEFAULT_HOST,
                      help="Mux host to connect to")
    parser.add_option("-p", "--port", dest="port", 
                      default=DEFAULT_PORT,
                      help="Mux port to connect to")
    (options, args) = parser.parse_args()
    
    connect_params = {'host': options.host,
                      'port': int(options.port)}
    main(connect_params)
