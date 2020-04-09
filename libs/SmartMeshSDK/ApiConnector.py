'''
Base class for ApiConnectors

The base ApiConnector class contains common methods for managing the notification queue. 
'''

import logging
from queue import Empty  
from queue import Queue

from . import ApiException
DEFAULT_Q_SIZE = 1000

# Log initialization 
class NullHandler(logging.Handler):
    def emit(self, record):
        pass
log = logging.getLogger('ApiConnector')
log.setLevel(logging.INFO)
log.addHandler(NullHandler())

def logDump(buf, msg = None, level=logging.DEBUG):
    '''
    \brief Print dump for binary object to trace file.
    '''
    
    if log.getEffectiveLevel() > level :
        return
    if msg :
        log.log(level, msg)
    addr = 0
    step = 20
    dump = " ".join(["{0:02x}".format(ord(c)) for c in buf])
    for i in range(0, len(dump), 3 * step) :
        log.log(level, "    {0:3} : {1}".format(addr, dump[i : i + 3 * step]))
        addr += step
        

class ApiConnector(object):
    '''
    \ingroup ApiConnector
    
    \brief Base class for all connector objects.
    '''
    
    def __init__(self, maxQSize = DEFAULT_Q_SIZE):
        self.maxQSize = maxQSize
        self.queue = NotifQueue(self.maxQSize)
        self.isConnected = False
        self.isExceptionRaise = False
        self.pendingNotification = None
        self.disconnectReason = ''
        self.traceFile = None
                
    def connect(self) :
        self.queue.clear()
        self.isConnected = True
        self.isExceptionRaise = False
        self.pendingNotification = None
        
    def disconnect(self, reason):
        if not self.isConnected :
            return
        self.disconnectReason = reason
        self.isConnected = False
        self.putDisconnectNotification(reason)
        
    def send(self, cmdName, params):
        raise NotImplementedError("ApiConnector.send is not implemented")

    def getNotificationInternal(self, timeoutSec=-1):
        '''
        \brief get notification from queue
        
        \param timeoutSec timeout for waiting if queue is empty.
               <0 wait infinity (blocked), >=0 wait up to 'timeout' seconds
         
        \exception ConnectionError disconnected from device
        \exception QueueError reading from empty 'offline' queue
        \returns   Notification object or None if queue is empty.
        '''
        
        if self.pendingNotification :
            res, self.pendingNotification = self.pendingNotification, None
            return res
        
        if not self.isConnected :
            self.oneTimeRaiseDisconnectException(None)
            timeoutSec = 0   # for 'offline' queue use get without timeout 
            
        res = self.queue.get(timeoutSec)
        if not self.isConnected :
            self.oneTimeRaiseDisconnectException(res)
            
        if not self.isConnected and not res :
            raise ApiException.QueueError() # Send exception: Reading from empty queue
        return res
    
    def oneTimeRaiseDisconnectException(self, notif):
        '''
        \brief raise exception only one time for one session and save current
               notification.
        '''
        
        if not self.isExceptionRaise :  # Send Disconnect Exception (only one time)
            self.isExceptionRaise = True
            self.pendingNotification = notif
            raise ApiException.ConnectionError(self.disconnectReason)

    def putNotification(self, item):
        '''
        \brief Put notification to queue
         
        Insert notification to queue. If queue is full raise ConnectionError exception
       
        \param item notification to insert
       
        \exception ConnectionError
        '''
        
        if not self.isConnected :
            raise ApiException.ConnectionError("Disconnected")
        if self.queue.qsize() < self.maxQSize :
            self.queue.put(item)
        else :
            raise ApiException.ConnectionError("Queue overflowed")

    def putDisconnectNotification(self, reason):
        '''
        \brief Put Disconnect notification to queue
       
        \param reason reason for disconnection
        '''
        # used by HartMgr where notifications are separate from control messages
        self.queue.putDisconnectNotification(reason)
        
     
class NotifQueue(Queue):
    class _DisconnectNotification:
        '''
        \brief Special internal notification - connection is broken
        '''
        def __init__(self, reason):
            self.reason = reason
        
    def __init__(self, maxSize):
        self.maxQSize = maxSize
        Queue.__init__(self)
    
    def get(self, timeout = -1):
        '''
        \brief Get notification from queue
        
        \param timeout timeout for waiting if queue is empty.
               <0 wait forever (blocked), >=0 wait up to 'timeout' seconds
        
        \returns   Notification object or None if queue is empty.
        '''
        
        try :
            if timeout < 0 :
                notif = Queue.get(self, True)
            elif timeout == 0 :
                notif = Queue.get(self, False)
            else:
                notif = Queue.get(self, True, timeout)
            if isinstance(notif, NotifQueue._DisconnectNotification) :  
                notif = Queue.get(self, False)  # disconnect notification is used for kick 'get' method  
            return notif
        except Empty:
            return None 
               
    def putDisconnectNotification(self, reason):
        '''
        \brief Put Disconnect notification to queue
       
        \param reason reason for disconnection
        '''
        self.put(NotifQueue._DisconnectNotification(reason))
        
    def clear(self) :
        while self.get(0) : pass
        
