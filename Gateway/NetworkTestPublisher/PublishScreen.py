import logging
class NullHandler(logging.Handler):
    def emit(self, record):
        pass
log = logging.getLogger('PublishScreen')
log.setLevel(logging.ERROR)
log.addHandler(NullHandler())

import NetworkTestPublisher

class PublishScreen(NetworkTestPublisher.NetworkTestPublisher):
    
    #======================== public ==========================================
    
    def publish(self, testResult):
    
        # log
        log.debug("publishing {0}".format(testResult))
    
        output  = []
        output += ["NOTRUN {0} {1}: {2}".format(timestamp,testName,desc) for (timestamp,testName,desc) in testResult.notRunDesc]
        output += ["PASS   {0} {1}: {2}".format(timestamp,testName,desc) for (timestamp,testName,desc) in testResult.successDesc]
        output += ["FAIL   {0} {1}: {2}".format(timestamp,testName,desc) for (timestamp,testName,desc) in testResult.failureDesc]
        print '\n'.join(output)
    
    #======================== private =========================================