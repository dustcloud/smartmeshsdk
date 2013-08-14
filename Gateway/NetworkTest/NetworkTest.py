import sys
import unittest

from Gateway import FormatUtils

class NetworkTest(unittest.TestCase):
    
    NETWORK_WIDE   = 'network wide'
    LAST_MOTE      = 'last mote'
    PER_MOTE       = 'per mote'
    
    def __init__(self, timestamp, methodName='runTest', networkState=None, mac=None):
        
        # initialize parent class
        unittest.TestCase.__init__(self,methodName)
        
        # record params
        self.timestamp       = timestamp
        self.networkState    = networkState
        self.mac             = mac
    
    def setUp(self):
        self.notRunDesc      = {}
        self.successDesc     = {}
        self.failureDesc     = {}
    
    #======================== setup ===========================================
    
    @staticmethod
    def getType():
        raise NotImplementedError()
    
    @staticmethod
    def parametrize(timestamp, testcase_class,networkState,mac=None):
        testloader = unittest.TestLoader()
        testnames  = testloader.getTestCaseNames(testcase_class)
        suite      = unittest.TestSuite()
        for name in testnames:
            suite.addTest(testcase_class(timestamp,name,networkState=networkState,mac=mac))
        return suite
    
    #======================== public ==========================================
    
    #==== set desc
    
    def setNotRunDesc(self,desc):
        self.notRunDesc[self._callerName()]  = desc
    
    def setSuccessDesc(self,desc):
        self.successDesc[self._callerName()] = desc
    
    def setFailureDesc(self,desc):
        self.failureDesc[self._callerName()] = desc
    
    #==== get desc
    
    # raises KeyError when no notRunDesc
    def getNotRunDesc(self,methodName):
        return self.notRunDesc[methodName]
    
    def getSuccessDesc(self,methodName):
        try:
            return self.successDesc[methodName]
        except KeyError:
            return "No decription provided."
    
    def getFailureDesc(self,methodName):
        try:
            return self.failureDesc[methodName]
        except KeyError:
            return "No decription provided."
    
    #======================== private =========================================
    
    def _callerName(self):
        return sys._getframe(2).f_code.co_name
    
    def _formatMac(self,mac):
        assert(len(mac)==8)
        
        return FormatUtils.formatMacString(mac)