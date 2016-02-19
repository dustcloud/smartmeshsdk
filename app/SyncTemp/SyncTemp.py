#!/usr/bin/python

#============================ adjust path =====================================

import sys
import os
if __name__ == "__main__":
    here = sys.path[0]
    sys.path.insert(0, os.path.join(here, '..', '..','libs'))
    sys.path.insert(0, os.path.join(here, '..', '..','external_libs'))

#============================ imports =========================================

import re
import time
import struct
import threading

from SmartMeshSDK                           import sdk_version
from SmartMeshSDK.utils                     import AppUtils, \
                                                   FormatUtils
from SmartMeshSDK.IpMgrConnectorSerial      import IpMgrConnectorSerial
from SmartMeshSDK.IpMgrConnectorMux         import IpMgrConnectorMux, \
                                                   IpMgrSubscribe
from SmartMeshSDK.ApiException              import ConnectionError,  \
                                                   CommandTimeoutError

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

## UDP port for all communication with this application
SYNCTEMP_UDP_PORT            = 0xf0ba

## Magic value put at the start of each packet
SYNCTEMP_MAGIC_VALUE         = [0x73,0x79,0x74,0x70]

## name of the file, in the local directory, where the configuration is stored
CONFIG_FILENAME              = 'configuration_DO_NOT_DELETE.txt'

## number of seconds before this application broadcasts the configuration to
# the motes for the first time
CONFIGURATION_PERIOD_INITIAL = 5

## number of seconds between two broadcast of the configuration to the mote,
# in seconds
CONFIGURATION_PERIOD         = 5*60

## command identifiers
CMDID_GET                    = 0x01    ##< [app->mote] get the current configuration
CMDID_SET                    = 0x02    ##< [app->mote] set a current configuration
CMDID_RESPONSE               = 0x03    ##< [app<-mote] response from the mote to a GET command
CMDID_TEMP_DATA              = 0x04    ##< [app<-mote] temperature data point from the mote
CMDID_ALL                    = [
    CMDID_GET,
    CMDID_SET,
    CMDID_RESPONSE,
    CMDID_TEMP_DATA,
]

APP_RC_OK                    = 0x00    ##< command executed correctly
APP_RC_ERROR                 = 0x01    ##< an error occured when executing the command
APP_RC_ALL                   = [
    APP_RC_OK,
    APP_RC_ERROR,
]

#============================ helpers =========================================

def getConfiguration():
    '''
    \brief Return the configuration of the application.
    
    This function will read the configuration file and create a dictionnary 
    with the configuration. Example dictonnaries are:
    
    {
        'connection_details':     'COM17',
        'reporting_period':       3600,
    }
    
    or
    
    {
        'connection_details':     ('127.0.0.1',9900),
        'reporting_period':       1800,
    }
    
    \return the configuration to use, as a dictonnary.
    '''
    
    connection_details = None
    reporting_period   = None
    
    with open(CONFIG_FILENAME,'r') as f:
        for line in f:
            
            if line.startswith('#'):
                continue
            
            # e.g. "connection_details = 127.0.0.1:9900"
            m = re.search('\s*connection_details\s*=\s*([\w.]+):(\d+)', line)
            if m:
                if connection_details!=None:
                    raise Exception('Multiple connection_details found in {0}'.format(CONFIG_FILENAME))
                connection_details     = (m.group(1),int(m.group(2)))
                continue
            
            # e.g. "connection_details = COM17"
            # e.g. "connection_details = /dev/ttyUSB3"
            # e.g. "connection_details = /dev/tty.usbserial-2644D"
            m = re.search('\s*connection_details\s*=\s*([\S]+)', line)
            if m:
                if connection_details!=None:
                    raise Exception('Multiple connection_details found in {0}'.format(CONFIG_FILENAME))
                connection_details     = m.group(1)
                continue
            
            # e.g. "reporting_period = 3600"
            m = re.search('\s*reporting_period\s*=\s*(\d+)', line)
            if m:
                if reporting_period!=None:
                    raise Exception('Multiple reporting_period found in {0}'.format(CONFIG_FILENAME))
                reporting_period       = int(m.group(1))
                continue
    
    if connection_details==None:
        raise Exception('No connection_details found in {0}'.format(CONFIG_FILENAME))
    if reporting_period==None:
        raise Exception('No reporting_period found in {0}'.format(CONFIG_FILENAME))
    
    return {
        'connection_details':     connection_details,
        'reporting_period':       reporting_period,
    }

#============================ classes =========================================

class CsvLogger(object):
    
    LOG_FILENAME        = 'temperaturelog.csv'
    
    EVENT_TEMPERATURE   = 'temperature'
    EVENT_STARTAPP      = 'start_app'
    EVENT_STOPAPP       = 'stop_app'
    EVENT_CONNECTED     = 'connected'
    EVENT_DISCONNECTED  = 'disconnected'
    EVENT_ALL           = [
        EVENT_TEMPERATURE,
        EVENT_STARTAPP,
        EVENT_STOPAPP,
        EVENT_CONNECTED,
        EVENT_DISCONNECTED
    ]
    
    def __init__(self):
        
        self.datalogfile     = open(self.LOG_FILENAME,'a',1)
        self.timeOffset      = None
        
    def managerTime(self,managerTime):
        log.info("updated manager time to {0}".format(managerTime))
        self.timeOffset      = time.time()-managerTime
    
    def log(self,event_type,mac=None,temperature='',generationTime=None):
        assert event_type in self.EVENT_ALL
        
        if mac:
            macString   = FormatUtils.formatMacString(mac)
        else:
            macString   = ''
        
        if generationTime!=None and self.timeOffset!=None:
            timestamp   = self.timeOffset+generationTime
        else:
            timestamp   = time.time()
        
        timestampString = '{0}.{1:03d}'.format(
            time.strftime("%Y-%m-%d %H:%M:%S",time.localtime(timestamp)),
            int(1000*(timestamp-int(timestamp))),
        )
        
        logline = '{TIMESTAMP},{EVENT_TYPE},{MAC},{TEMPERATURE}\n'.format(
            TIMESTAMP   = timestampString,
            EVENT_TYPE  = event_type,
            MAC         = macString,
            TEMPERATURE = temperature,
        )
        
        print logline,
        self.datalogfile.write(logline)
        self.datalogfile.flush()

class ReceiverTask(threading.Thread):
    
    def __init__(self,csvLogger,connection_details):
        
        # store params
        self.csvLogger            = csvLogger
        self.connection_details   = connection_details
        
        # log
        self.csvLogger.log(CsvLogger.EVENT_STARTAPP)
        
        # local variables
        self.reconnectSem         = threading.Semaphore()
        self.isReconnecting       = False
        self.dataLock             = threading.RLock()
        
        # initialize thread
        threading.Thread.__init__(self)
        self.name = 'receiverTask'
        
        # log
        log.info('{0} started'.format(self.name))
        
        # start myself
        self.start()
    
    def run(self):
        
        with self.dataLock:
            self.isReconnecting = True
        
        while(True):
            
            try:
            
                #==== wait for an order to (re)connect
                
                self.reconnectSem.acquire()
                
                with self.dataLock:
                    assert self.isReconnecting==True
                
                #==== connect to serial port
                
                if isinstance(self.connection_details,str):
                    # connecting to a serial port
                    
                    self.connector = IpMgrConnectorSerial.IpMgrConnectorSerial()
                    self.connector.connect({
                        'port': self.connection_details,
                    })
                else:
                    # connecting to the serialMux
                    
                    self.connector = IpMgrConnectorMux.IpMgrConnectorMux()
                    self.connector.connect({
                        'host': self.connection_details[0],
                        'port': self.connection_details[1],
                    })
                
                #==== getTime
                
                temp         = self.connector.dn_getTime()
                managerTime  = float(temp.utcSecs)+float(temp.utcUsecs/1000000.0)
                self.csvLogger.managerTime(managerTime)
                
                #==== subscribe
                
                self.subscriber       = IpMgrSubscribe.IpMgrSubscribe(self.connector)
                self.subscriber.start()
                
                self.subscriber.subscribe(
                    notifTypes =    [
                                        IpMgrSubscribe.IpMgrSubscribe.NOTIFDATA,
                                    ],
                    fun =           self._subs_notifData,
                    isRlbl =        False,
                )
                
                self.subscriber.subscribe(
                    notifTypes =    [
                                        IpMgrSubscribe.IpMgrSubscribe.FINISH,
                                        IpMgrSubscribe.IpMgrSubscribe.ERROR,
                                    ],
                    fun =           self._subs_finishOrError,
                    isRlbl =        True,
                )
                
                #==== log
                
                self.csvLogger.log(CsvLogger.EVENT_CONNECTED)
                log.info(CsvLogger.EVENT_CONNECTED)
            
            except ConnectionError as err:
                
                # log
                log.warning(err)
                
                # schedule reconnection
                self._reconnect()
                
                # wait before attempting to reconnect
                time.sleep(1)
            
            else:
                
                with self.dataLock:
                    # remember I'm not connecting anymore
                    self.isReconnecting = False
    
    def __del__(self):
        
        # log
        self.csvLogger.log(CsvLogger.EVENT_STOPAPP)
    
    #======================== subscriptions ===================================
    
    def _subs_notifData(self, notifName, notifParams):
        '''
        \brief Received data from the manager.
        '''
        
        #=== reject non-SyncTemp packets
        
        if notifParams.srcPort!=SYNCTEMP_UDP_PORT:
            return
        if notifParams.dstPort!=SYNCTEMP_UDP_PORT:
            return
        if len(notifParams.data)!=4+1+2:
            return
        if tuple(notifParams.data[0:4])!=tuple(SYNCTEMP_MAGIC_VALUE):
            return
        if notifParams.data[4]!=CMDID_TEMP_DATA:
            return
        
        #=== extract temperature
        temperature          = '{0:.2f}'.format(float(struct.unpack('>h', ''.join([chr(b) for b in notifParams.data[5:7]]))[0])/100.0)
        
        #=== log
        self.csvLogger.log(
            event_type       = CsvLogger.EVENT_TEMPERATURE,
            mac              = notifParams.macAddress,
            temperature      = temperature,
            generationTime   = float(notifParams.utcSecs)+float(notifParams.utcUsecs/1000000.0),
        )
    
    def _subs_finishOrError(self,notifName=None,notifParams=None):
        
        print notifName
        
        with self.dataLock:
            
            # reconnect only if I'm not busy
            if not self.isReconnecting:
                
                # remember I'm reconnecting
                self.isReconnecting = True
                
                # give the order to reconnect
                self._reconnect()
    
    #======================== helpers =========================================
    
    def _reconnect(self):
        
        with self.dataLock:
            assert self.isReconnecting==True
        
        # disconnect current connector
        self.connector.disconnect()
        
        # log
        self.csvLogger.log(CsvLogger.EVENT_DISCONNECTED)
        log.info(CsvLogger.EVENT_DISCONNECTED)
        
        # give order to reconnect
        self.reconnectSem.release()
    
class ConfigurationTask(threading.Thread):
    
    def __init__(self,receiverTask,reporting_period):
        
        # store params
        self.receiverTask         = receiverTask
        self.reporting_period     = reporting_period
        
        # local variables
        
        # initialize thread
        threading.Thread.__init__(self)
        self.name = 'configurationTask'
        
        # log
        log.info('{0} started'.format(self.name))
        
        # start myself
        self.start()
    
    def run(self):
        
        # wait before sending the first configuration
        time.sleep(CONFIGURATION_PERIOD_INITIAL)
        
        while(True):
            
            #===== format configuration payload
            
            payload  = []
            payload += SYNCTEMP_MAGIC_VALUE
            payload += [CMDID_SET]
            payload += [ord(b) for b in struct.pack('>I', self.reporting_period)]
            
            #===== send configuration
            
            try:
                self.receiverTask.connector.dn_sendData(
                    macAddress = [0xff]*8,
                    priority    = 0,
                    srcPort     = SYNCTEMP_UDP_PORT,
                    dstPort     = SYNCTEMP_UDP_PORT,
                    options     = 0x00,
                    data        = payload,
                )
            except Exception as err:
                msg = 'error sending configuration: {0}'.format(err)
                log.error(msg)
                print msg
                
                # cause app to reconnect
                self.receiverTask._subs_finishOrError(notifName='INTERNAL')
            else:
                msg = '   configuration broadcast'
                log.info(msg)
                print msg
            
            #===== wait
            
            time.sleep(CONFIGURATION_PERIOD)

#============================ main ============================================

def main():
    
    # print banner
    print 'SyncTemp application - SmartMeshSDK {VERSION}\n'.format(
        VERSION = '.'.join([str(i) for i in sdk_version.VERSION]),
    )
    
    # retrieve configuration
    try:
        config = getConfiguration()
    except Exception as err:
        print 'FATAL: {0}\n'.format(err)
        raw_input('Aborted. Press enter to close')
        return
    
    # print configuration
    output         = []
    output         = ['configuration used:']
    output        += [' - connection_details:    {0}'.format(config['connection_details'])]
    output        += [' - reporting_period:      {0}'.format(config['reporting_period'])]
    output        += ['']
    output         = '\n'.join(output)
    print output
    
    # create CSV logger
    csvLogger                = CsvLogger()
    
    # start receiver task
    receiverTaskHandler      = ReceiverTask(
        csvLogger            = csvLogger,
        connection_details   = config['connection_details'],
    )
    
    # start configuration task
    configurationTaskHandler = ConfigurationTask(
        receiverTask         = receiverTaskHandler,
        reporting_period     = config['reporting_period'],
    )

if __name__=='__main__':
    main()
