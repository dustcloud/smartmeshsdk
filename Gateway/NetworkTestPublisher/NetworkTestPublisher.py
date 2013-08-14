import logging
class NullHandler(logging.Handler):
    def emit(self, record):
        pass
log = logging.getLogger('NetworkTestPublisher')
log.setLevel(logging.ERROR)
log.addHandler(NullHandler())

class NetworkTestPublisher(object):
    
    def __init__(self,filename=None):
    
        # store params
        
        # log
        log.info("creating instance")
        
        # local variables
    
    #======================== public ==========================================
    
    def publish(self, testResult):
        raise NotImplementedError()
        
    #======================== private =========================================
