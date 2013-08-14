import logging
class NullHandler(logging.Handler):
    def emit(self, record):
        pass
log = logging.getLogger('PublishLogFile')
log.setLevel(logging.ERROR)
log.addHandler(NullHandler())

import NetworkTestPublisher
from Gateway import FormatUtils

class PublishLogFile(NetworkTestPublisher.NetworkTestPublisher):
    
    TESTLOG_FORMAT  = "%(levelname)s %(message)s"
    
    PASS = logging.DEBUG+5
    FAIL = logging.DEBUG+6
    
    def __init__(self,filename=None):
        # initialize parent class
        NetworkTestPublisher.NetworkTestPublisher.__init__(self)
        
        # setup logging
        self.testLogger = logging.getLogger('testResults-{0}'.format(filename))
        # set up logging for that manager
        logFilename       = '{0}.testresults'.format(filename)
        logHandler        = logging.handlers.RotatingFileHandler(
                                logFilename,
                                maxBytes=20000000,
                                backupCount=5)
        logHandler.setFormatter(logging.Formatter(self.TESTLOG_FORMAT))
        logging.addLevelName(self.PASS, 'PASS')
        logging.addLevelName(self.FAIL, 'FAIL')
        self.testLogger.setLevel(self.PASS)
        self.testLogger.addHandler(logHandler)
    
    #======================== public ==========================================
    
    def publish(self, testResult):
    
        # log for debug
        log.debug("publishing {0}".format(testResult))
        
        # log in logFile
        for (timestamp,testName,desc) in testResult.notRunDesc:
            self.testLogger.log(self.PASS,"{0} {1:>30}: NOTRUN: {2}".format(FormatUtils.formatTimestamp(timestamp),
                                                                    testName,
                                                                    desc))
        for (timestamp,testName,desc) in testResult.successDesc:
            self.testLogger.log(self.PASS,"{0} {1:>30}: {2}".format(FormatUtils.formatTimestamp(timestamp),
                                                                    testName,
                                                                    desc))
        for (timestamp,testName,desc) in testResult.failureDesc:
            self.testLogger.log(self.FAIL,"{0} {1:>30}: {2}".format(FormatUtils.formatTimestamp(timestamp),
                                                                    testName,
                                                                    desc))
    
    #======================== private =========================================