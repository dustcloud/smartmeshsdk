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
from   SmartMeshSDK.protocols.Hr       import HrParser
from   SmartMeshSDK.utils              import AppUtils,                   \
                                              FormatUtils
from   SmartMeshSDK.ApiDefinition      import IpMgrDefinition
from   SmartMeshSDK.IpMgrConnectorMux  import IpMgrConnectorMux,          \
                                              IpMgrSubscribe
from   dustUI                          import dustWindow,                 \
                                              dustFrameConnection,        \
                                              dustFrameTable

#============================ logging =========================================

import logging

# local
class NullHandler(logging.Handler):
    def emit(self, record):
        pass
log = logging.getLogger('App')
log.setLevel(logging.ERROR)
log.addHandler(NullHandler())

#============================ defines =========================================

#============================ globals =========================================

#============================ setup/teardown ==================================

# logging
def setup_module(function):
    for loggerName in LOG_MODULES:
        temp = logging.getLogger(loggerName)
        temp.setLevel(logging.DEBUG)
        temp.addHandler(logHandler)

# global
AppUtils.configureLogging()

# HR logs (do last)
hrlog = logging.getLogger('ParsedHr')
hrlog.setLevel(logging.INFO)
hrlogHandler = logging.handlers.RotatingFileHandler(
    'receivedHRs.log',
    maxBytes       = 2000000,
    backupCount    = 5,
    mode           = 'a',
)
hrlogHandler.setFormatter(logging.Formatter("%(asctime)s [%(levelname)s] %(message)s"))
hrlog.addHandler(hrlogHandler)

#============================ defines =========================================

UPDATEPERIOD = 500 # in ms

#============================ body ============================================

##
# \addtogroup HrListener
# \{
# 

class notifClient(object):
    
    def __init__(self, connector, disconnectedCallback):
        
        # store params
        self.connector = connector
        self.disconnectedCallback = disconnectedCallback
        
        # variables
        self.data      = []
        self.data.append(['mac' , '# Device HRs', '# Neighbors HRs', '# Discovered HRs', '# RSSI HRs']) # header
        self.dataLock  = threading.Lock()
        self.hrParser  = HrParser.HrParser()
        
        # log
        hrlog.info("========= START LOGGING HEALTH REPORTS =========")
        
        # subscriber
        self.subscriber = IpMgrSubscribe.IpMgrSubscribe(self.connector)
        self.subscriber.start()
        self.subscriber.subscribe(
            notifTypes  =   [
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
        with self.dataLock:
            returnVal = self.data[:]
        return returnVal
    
    def disconnect(self):
        
        # log
        hrlog.info("========= STOP LOGGING HEALTH REPORTS ==========")
        
        self.connector.disconnect()
    
    #======================== private =========================================
    
    def _notifCallback(self, notifName, notifParams):
        
        try:
        
            assert notifName==IpMgrSubscribe.IpMgrSubscribe.NOTIFHEALTHREPORT
            
            mac        = FormatUtils.formatMacString(notifParams.macAddress)
            hr         = self.hrParser.parseHr(notifParams.payload)
            
            # log
            hrlog.info('from {0}:\n{1}'.format(
                    mac,
                    self.hrParser.formatHr(hr),
                ),
            )
            
            with self.dataLock:
                # format of data:
                # [
                #     [''                        , 'Device', 'Neighbors', 'Discovered', 'RSSI'],
                #     ['11-11-11-11-11-11-11-11' ,        0,           3,            2,      4],
                #     ['22-22-22-22-22-22-22-22' ,        0,           3,            2,      5],
                # ]
                
                # find notifName row
                found=False
                for row in self.data:
                    if row[0]==mac:
                       found=True
                       break
                
                # create row if needed
                if not found:
                    self.data.append([mac,0,0,0,0])
                    row = self.data[-1]
                
                # increment counters
                if 'Device' in hr:
                    row[1] += 1
                if 'Neighbors' in hr:
                    row[2] += 1
                if 'Discovered' in hr:
                    row[3] += 1
                if 'Extended' in hr:
                    row[4] += 1
        
        except Exception as err:
            print type(err)
            print err
            raise

class hrListenerGui(object):
    
    def __init__(self):
        
        # variables
        self.guiLock            = threading.Lock()
        self.apiDef             = IpMgrDefinition.IpMgrDefinition()
        self.notifClientHandler = None
        
        # create window
        self.window = dustWindow.dustWindow(
            'HrListener',
            self._windowCb_close,
        )
        
        # add a connection frame
        self.connectionFrame = dustFrameConnection.dustFrameConnection(
            self.window,
            self.guiLock,
            self._connectionFrameCb_connected,
            frameName="manager connection",
            row=0,column=0
        )
        self.connectionFrame.apiLoaded(self.apiDef)
        self.connectionFrame.show()
        
        # add a table frame
        self.tableFrame = dustFrameTable.dustFrameTable(
            self.window,
            self.guiLock,
            frameName="received health reports",
            row=1,column=0,
        )
        self.tableFrame.show()
    
    #======================== public ==========================================
    
    def start(self):
        
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
        
        # disconnect the notifClient
        self.notifClientHandler.disconnect()
        
        # delete the connector
        self.connector = None
    
    def _updateTable(self):
        
        # get the data
        dataToPlot = self.notifClientHandler.getData()
        
        # update the frame
        self.tableFrame.update(dataToPlot)
        
        # schedule the next update
        self.tableFrame.after(UPDATEPERIOD,self._updateTable)

#============================ main ============================================

def main():
    hrListenerGuiHandler = hrListenerGui()
    hrListenerGuiHandler.start()

if __name__ == '__main__':
    main()

##
# end of HrListener
# \}
# 