import time
import logging
import threading

class NullHandler(logging.Handler):
    def emit(self, record):
        pass
log = logging.getLogger('RateCalculator')
log.setLevel(logging.INFO)
log.addHandler(NullHandler())

DEFAULT_TSBUF_SIZE = 10

class RateCalculatorError(Exception):
    '''
    \brief Exception class associated with the rate calculator.
    '''
    
    NOT_ENOUGH_DATA          = 1
    
    descriptions = { 
        NOT_ENOUGH_DATA:     'not enough data to calculate rate', 
    }
    
    def __init__(self,errorCode,details=None):
        self.errorCode  = errorCode
        self.details    = details
    
    def __str__(self):
        try:
            output = self.descriptions[self.errorCode]
            if self.details:
                output += ': ' + str(self.details)
            return output
        except KeyError:
            return "Unknown error: #" + str(self.errorCode)

class RateCalculator(object):
    '''
    \brief Rate calculator class.
    '''
    
    def __init__(self, tsBufSize=DEFAULT_TSBUF_SIZE):
        
        # log
        log.info("creating instance")
        
        # store params
        self.tsBufSize = tsBufSize
        
        # local variables
        self.tsBufLock = threading.Lock()
        self.tsBuf     = []
    
    def signalEvent(self,ts=None):
        
        if not ts:
            ts = time.time()
        
        # log
        log.debug("adding event at {0}".format(ts))
        
        self.tsBufLock.acquire()
        self.tsBuf.append(ts)
        while len(self.tsBuf)>self.tsBufSize:
            self.tsBuf.pop(0)
        self.tsBufLock.release()
    
    def clearBuf(self) :
        self.tsBufLock.acquire()
        self.tsBuf = []
        self.tsBufLock.release()
        
    def getRate(self):
        
        returnVal = None
        
        self.tsBufLock.acquire()
        if  len(self.tsBuf)>self.tsBufSize:
            ouput = "rate buffer has {0} elements, expected at most {1}".format(len(self.tsBuf),self.tsBufSize)
            self.tsBufLock.release()
            raise SystemError(ouput)
        if len(self.tsBuf)==self.tsBufSize:
            returnVal = float(self.tsBufSize-1)/(self.tsBuf[-1]-self.tsBuf[0])
        self.tsBufLock.release()
        
        if not returnVal:
            raise RateCalculatorError(RateCalculatorError.NOT_ENOUGH_DATA)
        else:
            return returnVal