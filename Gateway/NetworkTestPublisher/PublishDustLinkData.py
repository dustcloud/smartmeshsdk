import logging
class NullHandler(logging.Handler):
    def emit(self, record):
        pass
log = logging.getLogger('PublishDustLinkData')
log.setLevel(logging.ERROR)
log.addHandler(NullHandler())

import NetworkTestPublisher

from DustLinkData import DustLinkData
        
class PublishDustLinkData(NetworkTestPublisher.NetworkTestPublisher):
    
    def __init__(self,filename=None):
        
        # log
        log.info("creating instance")
        
        # initialize parent class
        NetworkTestPublisher.NetworkTestPublisher.__init__(self)
    
    #======================== public ==========================================
    
    def publish(self, testResult):
        
        # log
        log.debug("writing testResult {0} into dataConnector".format(testResult))
        
        for (timestamp,testName,desc) in testResult.notRunDesc:
            DustLinkData.DustLinkData().addResult('testNet',
                                                  testName,
                                                  DustLinkData.DustLinkData.TEST_OUTCOME_NOTRUN,
                                                  timestamp,
                                                  desc)
        for (timestamp,testName,desc) in testResult.successDesc:
            DustLinkData.DustLinkData().addResult('testNet',
                                                  testName,
                                                  DustLinkData.DustLinkData.TEST_OUTCOME_PASS,
                                                  timestamp,
                                                  desc)
        for (timestamp,testName,desc) in testResult.failureDesc:
            DustLinkData.DustLinkData().addResult('testNet',
                                                  testName,
                                                  DustLinkData.DustLinkData.TEST_OUTCOME_FAIL,
                                                  timestamp,
                                                  desc)
        
    #======================== private =========================================