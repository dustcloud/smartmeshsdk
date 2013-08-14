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
import logging
import logging.handlers

from dustWindow           import dustWindow
from dustFrameConnection  import dustFrameConnection
from dustFrameTable       import dustFrameTable

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
        self.data      = []
        self.dataLock  = threading.Lock()
        
        # subscriber
        self.subscriber = IpMgrSubscribe.IpMgrSubscribe(self.connector)
        self.subscriber.start()
        self.subscriber.subscribe(
            notifTypes =    [
                                IpMgrSubscribe.IpMgrSubscribe.NOTIFDATA,
                                IpMgrSubscribe.IpMgrSubscribe.NOTIFIPDATA,
                            ],
            fun =           self._notifCallback,
            isRlbl =        False,
        )
        self.subscriber.subscribe(
            notifTypes =    [
                                IpMgrSubscribe.IpMgrSubscribe.NOTIFEVENT,
                                IpMgrSubscribe.IpMgrSubscribe.NOTIFLOG, 
                                IpMgrSubscribe.IpMgrSubscribe.NOTIFHEALTHREPORT,
                            ],
            fun =           self._notifCallback,
            isRlbl =        True,
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
    
    def getData(self):
        self.dataLock.acquire()
        returnVal = self.data[:]
        self.dataLock.release()
        return returnVal
        
    def disconnect(self):
        self.connector.disconnect()
    
    #======================== private =========================================
    
    def _notifCallback(self, notifName, notifParams):
        self.dataLock.acquire()
        
        # find notifName row
        found=False
        for row in self.data:
            if row[0]==notifName:
               found=True
               break
        
        # create row if needed
        if not found:
            self.data.append([notifName,0])
            row = self.data[-1]
        
        # increment counter
        row[1] += 1
        
        self.dataLock.release()
        

class notifGui(object):
    '''
    \ingroup MgrListener
    '''
   
    def __init__(self):
        
        # variables
        self.guiLock            = threading.Lock()
        self.apiDef             = IpMgrDefinition.IpMgrDefinition()
        self.notifClientHandler = None
        
        # create window
        self.window = dustWindow('MgrListener',
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
        
        # add a table frame
        self.tableFrame = dustFrameTable(self.window,
                                         self.guiLock,
                                         frameName="received notifications",
                                         row=1,column=0)
        self.tableFrame.show()
    
    #======================== public ==========================================
    
    def start(self, connect_params):
        
        # TODO: how to use connect_params?
        
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
        self.tableFrame.after(UPDATEPERIOD,self._updateTable)
        
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
    
    def _updateTable(self):
        
        # get the data
        dataToPlot = self.notifClientHandler.getData()
        
        # update the frame
        self.tableFrame.update(dataToPlot)
        
        # schedule the next update
        self.tableFrame.after(UPDATEPERIOD,self._updateTable)
        
    
def main(connect_params):
    notifGuiHandler = notifGui()
    notifGuiHandler.start(connect_params)

if __name__ == '__main__':
    # logging
    LOG_FILENAME       = 'MgrListener.log'
    LOG_FORMAT         = "%(asctime)s [%(name)s:%(levelname)s] %(message)s"
    logHandler = logging.handlers.RotatingFileHandler(LOG_FILENAME,
                                                   maxBytes=2000000,
                                                   backupCount=5,
                                                   mode='w'
                                                   )
    logHandler.setFormatter(logging.Formatter(LOG_FORMAT))
    for loggerName in ['ByteArraySerializer',
                       'SerialConnector',
                       'IpMoteConnectorInternal',
                       'Hdlc',
                       ]:
        temp = logging.getLogger(loggerName)
        temp.setLevel(logging.DEBUG)
        temp.addHandler(logHandler)

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
