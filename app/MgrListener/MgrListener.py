#!/usr/bin/python

#============================ adjust path =====================================

import sys
import os
if __name__ == "__main__":
    here = sys.path[0]
    sys.path.insert(0, os.path.join(here, '..', '..','libs'))
    sys.path.insert(0, os.path.join(here, '..', '..','external_libs'))

#============================ verify installation =============================

from SmartMeshSDK.utils import SmsdkInstallVerifier
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

#============================ imports =========================================

import threading
from   optparse                        import OptionParser

from   SmartMeshSDK.utils              import AppUtils,                   \
                                              FormatUtils
from   SmartMeshSDK.ApiDefinition      import IpMgrDefinition
from   SmartMeshSDK.IpMgrConnectorMux  import IpMgrConnectorMux,          \
                                              IpMgrSubscribe
from   dustUI                          import dustWindow,                 \
                                              dustFrameConnection,        \
                                              dustFrameTable

#============================ logging =========================================

# local

import logging
class NullHandler(logging.Handler):
    def emit(self, record):
        pass
log = logging.getLogger('App')
log.setLevel(logging.ERROR)
log.addHandler(NullHandler())

# global

AppUtils.configureLogging()

#============================ defines =========================================

UPDATEPERIOD = 500 # in ms
DEFAULT_HOST = '127.0.0.1'
DEFAULT_PORT = 9900

#============================ body ============================================

##
# \addtogroup MgrListener
# \{
# 

class notifClient(object):
    
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
    
    def __init__(self):
        
        # variables
        self.guiLock            = threading.Lock()
        self.apiDef             = IpMgrDefinition.IpMgrDefinition()
        self.notifClientHandler = None
        
        # create window
        self.window = dustWindow.dustWindow('MgrListener',
                                 self._windowCb_close)
                                 
        # add a connection frame
        self.connectionFrame = dustFrameConnection.dustFrameConnection(
                                    self.window,
                                    self.guiLock,
                                    self._connectionFrameCb_connected,
                                    frameName="manager connection",
                                    row=0,column=0)
        self.connectionFrame.apiLoaded(self.apiDef)
        self.connectionFrame.show()
        
        # add a table frame
        self.tableFrame = dustFrameTable.dustFrameTable(self.window,
                                         self.guiLock,
                                         frameName="received notifications",
                                         row=1,column=0)
        self.tableFrame.show()
    
    #======================== public ==========================================
    
    def start(self, connect_params):
        
        # TODO: how to use connect_params?
        
        '''
        This command instructs the GUI to start executing and reacting to 
        user interactions. It never returns and should therefore be the last
        command called.
        '''
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
        if self.connector:
            self.connector.disconnect()
        self.connector = None
    
    def _updateTable(self):
        
        # get the data
        dataToPlot = self.notifClientHandler.getData()
        
        # update the frame
        self.tableFrame.update(dataToPlot)
        
        # schedule the next update
        self.tableFrame.after(UPDATEPERIOD,self._updateTable)

#============================ main ============================================

def main(connect_params):
    notifGuiHandler = notifGui()
    notifGuiHandler.start(connect_params)

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
    
    connect_params = {
        'host': options.host,
        'port': int(options.port),
    }
    main(connect_params)

##
# end of MgrListener
# \}
# 
