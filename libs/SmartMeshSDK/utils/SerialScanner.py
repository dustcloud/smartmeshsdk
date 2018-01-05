import os
if os.name=='nt':       # Windows
   import _winreg as winreg
elif os.name=='posix':  # Linux
   import glob

import serial
import time
import threading

from SmartMeshSDK.IpMoteConnector      import IpMoteConnector
from SmartMeshSDK.IpMgrConnectorSerial import IpMgrConnectorSerial
from SmartMeshSDK.ApiException         import ConnectionError

class SerialScanner(object):
    
    WAITFORMGRHELLO_TOUT = 3.500
    
    def __init__(self):
        pass
    
    # ======================= public ==========================================
    
    # === raw serial port manipulation
    
    def listAllSerialPorts(self):
        returnVal = []
        
        if os.name=='nt':
            key  = winreg.OpenKey(
                winreg.HKEY_LOCAL_MACHINE,
                'HARDWARE\\DEVICEMAP\\SERIALCOMM'
            )
            for i in range(winreg.QueryInfoKey(key)[1]):
                try:
                    val = winreg.EnumValue(key,i)
                except:
                    pass
                else:
                    if val[0].find('VCP')>-1:
                        returnVal.append(str(val[1]))
        elif os.name=='posix':
            returnVal = glob.glob('/dev/ttyUSB*')
        
        returnVal.sort()
        
        return returnVal
    
    def canOpen(self,serialport):
        try:
            serialHandler = serial.Serial(serialport)
        except serial.serialutil.SerialException:
            returnVal = False
        else:
            returnVal = True
            serialHandler.close()
        return returnVal
    
    # === atomic testing of serial port
    
    def isIpManagerApi(self,serialport):
        return self._isIpApi(
            serialport       = serialport,
            apiClass         = IpMgrConnectorSerial.IpMgrConnectorSerial,
        )
    
    def isIpManagerCli(self,serialport):
        raise NotImplementedError()
    
    def isIpMoteApi(self,serialport):
        return self._isIpApi(
            serialport       = serialport,
            apiClass         = IpMoteConnector.IpMoteConnector,
            apiTestCommand   = 'dn_getParameter_moteInfo',
        )
    
    def isIpMoteCli(self,serialport):
        raise NotImplementedError()
    
    # === detecting IP manager's
    
    def listIpManagerApi(self):
        isManager  = {}
        dataLock   = threading.RLock()
        threads    = []
        for serialport in self.listAllSerialPorts():
            threads += [self._waitForMgrHello(serialport,isManager,dataLock)]
        for t in threads:
            t.join()
        return [k for (k,v) in isManager.items() if v==True]
    
    def availableManagerNotifier(self,cb,period=0):
        # start thread which continuously scans for IP Managers
        self._availableManagerNotifierThread(
            cb         = cb,
            period     = period,
        )
    
    # ======================= private =========================================
    
    def _isIpApi(self,serialport,apiClass,apiTestCommand=None):
        connector = apiClass()
        connector.MAX_NUM_RETRY = 1
        try:
            connector.connect({'port': serialport,})
            if apiTestCommand:
                getattr(connector,apiTestCommand)()
        except ConnectionError:
            returnVal = False
        else:
            returnVal = True
        finally:
            try:
                connector.disconnect()
            except:
                pass
            del connector
        return returnVal
    
    class _availableManagerNotifierThread(threading.Thread):
        def __init__(self,cb,period):
            self.cb         = cb
            self.period     = period
            threading.Thread.__init__(self)
            self.name       = "_ipManagerFinderThread"
            self.daemon     = True
            self.start()
        def run(self):
            while True:
                for m in SerialScanner().listIpManagerApi():
                    self.cb(m)
                time.sleep(self.period)

    class _waitForMgrHello(threading.Thread):
        def __init__(self,serialport,isManager,dataLock):
            self.serialport       = serialport
            self.isManager        = isManager
            self.dataLock         = dataLock
            self.goOn             = True
            with self.dataLock:
                isManager[serialport]=False
            threading.Thread.__init__(self)
            self.name             = "_waitForMgrHello@{0}".format(self.serialport)
            self.daemon           = True
            self.start()
        def run(self):
            # listen to that serial port for some time
            try:
                serialHandler = serial.Serial(self.serialport,baudrate=115200)
                serialHandler.setRTS(False)
                serialHandler.setDTR(True)
                listenThread = threading.Thread(
                    target = self._listenForMgrHello,
                    args = (
                        self.serialport,
                        serialHandler,
                        self.isManager,
                        self.dataLock,
                    ),
                )
                listenThread.name      = 'listenThread@{0}'.format(self.serialport)
                listenThread.daemon    = True
                listenThread.start()
                listenThread.join(SerialScanner.WAITFORMGRHELLO_TOUT)
                self.goOn = False
                serialHandler.close()
                while listenThread.isAlive():
                    pass # wait for listenThread to stop
            except serial.SerialException:
                pass # happens when serial port unavailable
        def _listenForMgrHello(self,serialport,serialHandler,isManager,dataLock):
            try:
                rxBuff = []
                while True:
                    c = serialHandler.read(1)
                    if c:
                        rxBuff += [ord(c)]
                        if self._contains_mrgHello(rxBuff):
                            with self.dataLock:
                                isManager[serialport]=True
                            return
            except Exception as err:
                if self.goOn:
                    print err
        def _contains_mrgHello(self,l):
            MSG_HELLO    = [126,0,3,0,2,4,0,155,56,126]
            len_mrgHello = len(MSG_HELLO)
            return any(l[i:len_mrgHello+i]==MSG_HELLO for i in xrange(len(l) - len_mrgHello+1))
