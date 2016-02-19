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
import Queue
import datetime
import copy
import webbrowser

from   SmartMeshSDK.utils                        import AppUtils,              \
                                                        FormatUtils
from   SmartMeshSDK.ApiDefinition                import IpMgrDefinition
from   SmartMeshSDK.IpMgrConnectorMux            import IpMgrSubscribe
from   SmartMeshSDK.ApiException                 import APIError
from   SmartMeshSDK.protocols.oap                import OAPDispatcher,         \
                                                        OAPClient,             \
                                                        OAPMessage,            \
                                                        OAPNotif
from   SmartMeshSDK.protocols.xivelyConnector    import xivelyConnector
from   dustUI                                    import dustWindow,            \
                                                        dustFrameConnection,   \
                                                        dustFrameForm,         \
                                                        dustFrameMoteList,     \
                                                        dustFrameText

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

DFLT_API_KEY            = ''

GUI_UPDATEPERIOD        = 500 # ms
MAX_QUEUE_SIZE          = 10

COL_NUMDATARX           = 'data received'
COL_NUMDATAPUB          = 'published'
COL_NUMDATAPUBOK        = 'published OK'
COL_CLR                 = 'clear'
COL_URL                 = 'see data online'

#============================ body ============================================

##
# \addtogroup Xively
# \{
# 

class xivelyConnectorThread(threading.Thread):
    '''
    \brief A singleton which publishes data to Xively.
    '''
    
    #======================== singleton pattern ===============================
    
    _instance      = None
    _init          = False
    CLOSE_MESSAGE  = 'close'
    
    def __new__(cls, *args, **kwargs):
        if not cls._instance:
            cls._instance = super(xivelyConnectorThread, cls).__new__(cls, *args, **kwargs)
        return cls._instance
    
    def __init__(self):
        
        # don't re-initialize an instance (needed because singleton)
        if self._init:
            return
        self._init = True
        
        # variables
        self.queue      = Queue.Queue(maxsize=MAX_QUEUE_SIZE)
        self.publisher  = None
        
        # initialize parent class
        threading.Thread.__init__(self)
        
        # give this thread a name
        self.name       = "xivelyConnectorThread"
        
        # start myself
        self.start()
    
    #======================== public ==========================================
    
    def publish(self,mac,datastream,value):
        try:
            self.queue.put_nowait((mac,datastream,value))
        except Queue.Full:
            print "Queue is full"
    
    def getProductId(self):
        returnVal = None
        if self.publisher:
            returnVal = self.publisher.getProductId()
        return returnVal
    
    def close(self):
        self.queue.put(self.CLOSE_MESSAGE)
    
    #======================== private =========================================
    
    def run(self):
        
        while True:
            elem = self.queue.get()
            
            if elem==self.CLOSE_MESSAGE:
                if self.publisher:
                    self.publisher.close()
                return
            
            (mac,datastream,value) = elem
            
            AppData().incrementMoteCounter(mac,COL_NUMDATAPUB)
            
            if self.publisher==None:
                apiKey = AppData().getApiKey()
                if apiKey:
                    self.publisher = xivelyConnector.xivelyConnector(
                        apiKey          = apiKey,
                        productName     = 'SmartMesh IP Starter Kit',
                        productDesc     = 'Manager {0}'.format(
                            FormatUtils.formatMacString(AppData().getManager()),
                        ),
                    )
            
            if self.publisher==None:
                continue
            
            try:
                # publish
                self.publisher.publish(
                   mac            = mac,
                   datastream     = datastream,
                   value          = value,
                )
                
                # log
                output       = []
                output      += ['pushed following data to Xively:']
                output      += ['- mac:         {0}'.format(
                        FormatUtils.formatMacString(mac),
                    )
                ]
                output      += ['- datastream:  {0}'.format(datastream)]
                output      += ['- value:       {0}'.format(value)]
                output       = '\n'.join(output)
                log.debug(output)
                
            except Exception as err:
                output       = []
                output      += ['===============']
                output      += ['{0}: Exception when publishing'.format(self.name)]
                output      += ['- mac:          {0}'.format(FormatUtils.formatMacString(mac))]
                output      += ['- datastream:   {0}'.format(datastream)]
                output      += ['{0}'.format(type(err))]
                output      += ['{0}'.format(err)]
                output      += ['']
                output       = '\n'.join(output)
                log.error(output)
                print output
                
            else:
                AppData().incrementMoteCounter(mac,COL_NUMDATAPUBOK)

class AppData(object):
    '''
    \brief A singleton that holds the data about the motes.
    '''
    
    #======================== singleton pattern ===============================
    
    _instance = None
    _init     = False
    
    def __new__(cls, *args, **kwargs):
        if not cls._instance:
            cls._instance = super(AppData, cls).__new__(cls, *args, **kwargs)
        return cls._instance
    
    def __init__(self):
        
        # don't re-initialize an instance (needed because singleton)
        if self._init:
            return
        self._init = True
        
        # variables
        self.dataLock   = threading.RLock()
        self.apiKey     = ''
        self.motedata   = {}
        self.manager    = None
    
    #======================== public ==========================================
    
    def resetData(self):
        with self.dataLock:
            self.motedata   = {}
            self.manager    = None
    
    #===== apiKey
    
    def setApiKey(self,apiKey):
        assert type(apiKey)==str
        
        with self.dataLock:
            self.apiKey = apiKey
    
    def getApiKey(self):
        with self.dataLock:
            return self.apiKey
    
    #===== manager
    
    def setManager(self,mac):
        mac = self._formatMac(mac)
        
        with self.dataLock:
            assert self.manager==None
            self.manager = mac
    
    def getManager(self):
        with self.dataLock:
            return self.manager
    
    #===== mote
    
    def addMote(self,mac):
        mac = self._formatMac(mac)
        
        with self.dataLock:
            if mac not in self.motedata:
                self.motedata[mac] = {
                    COL_NUMDATARX:        0,
                    COL_NUMDATAPUB:       0,
                    COL_NUMDATAPUBOK:     0,
                }
    
    def deleteMote(self,mac):
        mac = self._formatMac(mac)
        
        with self.dataLock:
            if mac in self.motedata:
                del self.motedata[mac]
    
    def getMoteData(self):
        with self.dataLock:
            return copy.deepcopy(self.motedata)
    
    def incrementMoteCounter(self,mac,counterName):
        mac = self._formatMac(mac)
        assert counterName in [COL_NUMDATARX,COL_NUMDATAPUB,COL_NUMDATAPUBOK]
        
        with self.dataLock:
            self.addMote(mac)
            self.motedata[mac][counterName] += 1
    
    def clearMoteCounters(self,mac):
        mac = self._formatMac(mac)
        
        with self.dataLock:
            for counterName in [COL_NUMDATARX,COL_NUMDATAPUB,COL_NUMDATAPUBOK]:
                self.motedata[mac][counterName] = 0
    
    #======================== private =========================================
    
    def _formatMac(self,mac):
        assert type(mac) in [tuple,list]
        assert len(mac)==8
        
        return tuple(mac)
    
class notifClient(object):
    '''
    \brief Class which subscribes to and receives notifications from the
        manager.
    '''
    
    def __init__(self, connector, disconnectedCallback):
        
        # store params
        self.connector            = connector
        self.disconnectedCallback = disconnectedCallback
        self.oap_clients          = {}
        
        # variables
        
        # subscriber
        self.subscriber = IpMgrSubscribe.IpMgrSubscribe(self.connector)
        self.subscriber.start()
        
        self.subscriber.subscribe(
            notifTypes  = [
                IpMgrSubscribe.IpMgrSubscribe.NOTIFEVENT,
            ],
            fun         = self._eventHandler,
            isRlbl      = True,
        )
        self.subscriber.subscribe(
            notifTypes  = [
                IpMgrSubscribe.IpMgrSubscribe.ERROR,
                IpMgrSubscribe.IpMgrSubscribe.FINISH,
            ],
            fun         = self._errorHandler,
            isRlbl      = True,
        )
        self.subscriber.subscribe(
            notifTypes  = [
                IpMgrSubscribe.IpMgrSubscribe.NOTIFDATA,
            ],
            fun         = self._notifDataHandler,
            isRlbl      = False,
        )
        
        # OAP dispatcher
        self.oap_dispatch = OAPDispatcher.OAPDispatcher()
        self.oap_dispatch.register_notif_handler(self._handle_oap_notif)
    
    #======================== public ==========================================
    
    def disconnect(self):
        self.connector.disconnect()
        xivelyConnectorThread().close()
    
    #======================== private =========================================
    
    #===== notifications from manager
    
    def _eventHandler(self,notifName,notifParams):
        
        if notifName in [IpMgrSubscribe.IpMgrSubscribe.EVENTMOTEOPERATIONAL]:
            AppData().addMote(notifParams.macAddress)
        
        if notifName in [IpMgrSubscribe.IpMgrSubscribe.EVENTMOTELOST]:
            AppData().deleteMote(notifParams.macAddress)
    
    def _errorHandler(self,notifName,notifParams):
        self.disconnectedCallback()
    
    def _notifDataHandler(self,notifName,notifParams):
        
        assert notifName==IpMgrSubscribe.IpMgrSubscribe.NOTIFDATA
        
        mac = tuple(notifParams.macAddress)
        
        AppData().incrementMoteCounter(mac,COL_NUMDATARX)
        
        self.oap_dispatch.dispatch_pkt(notifName, notifParams)
    
    def _handle_oap_notif(self,mac,notif):
        
        # convert MAC to tuple
        mac = tuple(mac)
        
        if isinstance(notif,OAPNotif.OAPTempSample):
            # this is a temperature notification
            
            value            = float(notif.samples[0])/100.0 # /100 since unit in 100th of C
            
            xivelyConnectorThread().publish(
                mac          = mac,
                datastream   = 'temperature',
                value        = value,
            )
            
            if mac not in self.oap_clients:
                
                publisher = xivelyConnectorThread().publisher
                
                if publisher:
                    
                    try:
                        
                        # create datastream
                        publisher.publish(
                            mac             = mac,
                            datastream      = 'led',
                            value           = 0,
                        )
                    
                        # subscribe                    
                        publisher.subscribe(
                            mac             = mac,
                            datastream      = 'led',
                            callback        = self._led_cb,
                        )
                        
                        # create OAP client
                        self.oap_clients[mac] = OAPClient.OAPClient(
                            mac,
                            self._sendDataToConnector,
                            self.oap_dispatch,
                        )
                        
                    except Exception as err:
                        output    = []
                        output   += ['===============']
                        output   += ['{0}: Exception when creating and subscribing to datastream']
                        output   += ['- mac:          {0}'.format(FormatUtils.formatMacString(mac))]
                        output   += ['{0}'.format(type(err))]
                        output   += ['{0}'.format(err)]
                        output   += ['']
                        output    = '\n'.join(output)
                        log.error(output)
                        print output
    
    #===== notifications from Xively
    
    def _led_cb(self,mac,datastream,value):
        
        # all non-0 values turn LED on
        if value==0:
            value = 0
        else:
            value = 1
        
        # send through OAP
        self.oap_clients[mac].send(
            OAPMessage.CmdType.PUT,                        # command
            [3,2],                                         # address
            data_tags=[OAPMessage.TLVByte(t=0,v=value)],   # parameters
            cb=None,                                       # callback
        )
    
    def _sendDataToConnector(self,mac,priority,srcPort,dstPort,options,data):
        
        self.connector.dn_sendData(
            mac,
            priority,
            srcPort,
            dstPort,
            options,
            data
        )
    
class xivelyGui(object):
    
    def __init__(self):
        
        # local variables
        self.guiLock              = threading.Lock()
        self.notifClientHandler   = None
        self.macs                 = []
        self.oldData              = {}
        
        # create window
        self.window = dustWindow.dustWindow(
            'Xively Publisher',
            self._windowCb_close,
        )
        
        # add a connection frame
        self.connectionFrame = dustFrameConnection.dustFrameConnection(
            self.window,
            self.guiLock,
            self._connectionFrameCb_connected,
            frameName="manager connection",
            row=0,column=0,
        )
        self.connectionFrame.apiLoaded(IpMgrDefinition.IpMgrDefinition())
        self.connectionFrame.show()
        
        # add a form frame
        self.apiKeyFrame = dustFrameForm.dustFrameForm(
            self.window,
            self.guiLock,
            self._apiKeyButtonCb,
            "Xively API key",
            row=1,column=0
        )
        self.apiKeyFrame.show()
        self.apiKeyFrame.setVal(DFLT_API_KEY)
        
        # add a mote list frame
        columnnames =       [
            {
                'name': COL_NUMDATARX,
                'type': dustFrameMoteList.dustFrameMoteList.LABEL,
            },
            {
                'name': COL_NUMDATAPUB,
                'type': dustFrameMoteList.dustFrameMoteList.LABEL,
            },
            {
                'name': COL_NUMDATAPUBOK,
                'type': dustFrameMoteList.dustFrameMoteList.LABEL,
            },
            {
                'name': COL_CLR,
                'type': dustFrameMoteList.dustFrameMoteList.ACTION,
            },
            {
                'name': COL_URL,
                'type': dustFrameMoteList.dustFrameMoteList.ACTION,
            },
        ]
        self.moteListFrame = dustFrameMoteList.dustFrameMoteList(
            self.window,
            self.guiLock,
            columnnames,
            row=2,column=0,
        )
        self.moteListFrame.show()
        
        # add a tooltip frame
        self.toolTipFrame = dustFrameText.dustFrameText(
            self.window,
            self.guiLock,
            frameName="tooltip",
            row=5,column=0,
        )
        self.toolTipFrame.show()
        
    #======================== public ==========================================
    
    def start(self):
        
        # start update
        self.moteListFrame.after(GUI_UPDATEPERIOD,self._updateMoteList)
        
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
        
        # update MAC address of manager and operational motes
        self._updateMacAddresses()
        
        # create a notification client
        self.notifClientHandler = notifClient(
            self.connector,
            self._connectionFrameCb_disconnected,
        )
    
    def _connectionFrameCb_disconnected(self):
        '''
        \brief Called when the connectionFrame has disconnected.
        '''
        
        # update the GUI
        self.connectionFrame.updateGuiDisconnected()
        
        # reset the data
        AppData().resetData()
        
        # delete the connector
        if self.connector:
            self.connector.disconnect()
        self.connector = None
    
    def _apiKeyButtonCb(self,apiKey):
        AppData().setApiKey(str(apiKey))
        self.apiKeyFrame.disable()
    
    def _moteListFrame_clear(self,mac,button):
        AppData().clearMoteCounters(mac)
    
    def _moteListFrame_Url(self,mac,button):
        
        # get FeedId
        productId = xivelyConnectorThread().getProductId()
        
        if not productId:
            self.toolTipFrame.write('Cannot open live data. Not connected to Xively.')
            return
        
        # format URL
        url    = "https://xively.com/manage/{0}/devices/{1}".format(
            productId,
            FormatUtils.formatMacString(mac),
        )
        
        # open browser
        webbrowser.open(
            url    = url,
            new    = 2,   # 2==Open new tab if possible
        )
    
    #======================== helpers =========================================
    
    def _updateMoteList(self):
        
        # get latest data
        newData = AppData().getMoteData()
        
        # update GUI
        for (mac,moteData) in newData.items():
            
            if mac not in self.macs:
                # add the mote
                self.macs += [mac]
                moteData[COL_CLR] = {
                    'text':            'clear',
                    'callback':        self._moteListFrame_clear,
                }
                moteData[COL_URL] = {
                    'text':            'open browser',
                    'callback':        self._moteListFrame_Url,
                }
                self.moteListFrame.addMote(mac,moteData)
                self.oldData[mac] = {
                    COL_NUMDATARX:     0,
                    COL_NUMDATAPUB:    0,
                    COL_NUMDATAPUBOK:  0,
                }
            
            else:
                # update the mote
                for columnname,columnval in moteData.items():
                    if columnname in [COL_NUMDATARX,
                                      COL_NUMDATAPUB,
                                      COL_NUMDATAPUBOK]:
                        if self.oldData[mac][columnname]!=columnval:
                            self.oldData[mac][columnname] = columnval
                            self.moteListFrame.update(mac,columnname,columnval)
        
        # schedule next update
        self.moteListFrame.after(GUI_UPDATEPERIOD,self._updateMoteList)
    
    def _updateMacAddresses(self):
        
        currentMac      = (0,0,0,0,0,0,0,0) # start getMoteConfig() iteration with the 0 MAC address
        continueAsking  = True
        while continueAsking:
            try:
                res     = self.connector.dn_getMoteConfig(currentMac,True)
            except APIError:
                continueAsking = False
            else:
                
                if res.isAP:
                    # I found the managerMac
                    AppData().setManager(res.macAddress)
                
                if ((not res.isAP) and (res.state in [4,])):
                    # I found an operational mote
                    AppData().addMote(res.macAddress)
                
                currentMac = res.macAddress

#============================ main ============================================

def main():
    xivelyGuiHandler = xivelyGui()
    xivelyGuiHandler.start()

if __name__ == '__main__':
    main()

##
# end of Xively
# \}
# 
