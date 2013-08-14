import unittest

class NetworkTestResult(unittest.TestResult):
    
    def __init__(self):
        
        # initialize parent class
        unittest.TestResult.__init__(self)
        
        # additional variables
        self.notRunDesc   = []
        self.successDesc  = []
        self.failureDesc  = []
    
    def addSuccess(self, test):
    
        # call function from parent class
        unittest.TestResult.addSuccess(self,test)
        
        # add in descriptions of the successes (or notRun)
        try:
            self.notRunDesc.append(  (test.timestamp,                               # timestamp
                                      test._testMethodName,                         # testName
                                      test.getNotRunDesc(test._testMethodName)))    # desc
        except KeyError:
            self.successDesc.append( (test.timestamp,                               # timestamp
                                      test._testMethodName,                         # testName
                                      test.getSuccessDesc(test._testMethodName)))   # desc
    
    def addFailure(self, test, err):
        
        # call function from parent class
        unittest.TestResult.addFailure(self,test,err)
        
        # add in descriptions of the failures
        self.failureDesc.append( (test.timestamp,                                   # timestamp
                                  test._testMethodName,                             # testName
                                  test.getFailureDesc(test._testMethodName)))       # desc
    
    def __str__(self):
        output  = []
        output += [unittest.TestResult.__str__(self)]
        if self.failures:
            output += ["failures:"]
            for fd in self.failureDesc:
                output += [" - {0}".format(fd)]
        return '\n'.join(output)
