import NetworkTest

class TestPerMoteAvailability(NetworkTest.NetworkTest):
    
    MIN_MOTEAVAILABILITY = 0.99
    
    @staticmethod
    def getType():
        return NetworkTest.NetworkTest.LAST_MOTE
    
    #======================== tests ===========================================
    
    def test_perMoteAvailability(self):
        
        mote = self.networkState.motes[self.mac]
        
        #==== filter edge cases where the test can not be run
        
        if 'numTxOk' not in mote.info:
            # log a notRun message
            self.setNotRunDesc(
                'This test could not run because mote {0} did not report any numTxOk counter (the counters it did report are {1}).'.format(
                    self._formatMac(self.mac),
                    mote.info.keys()
                )
            )
            return
            
        if 'numTxFail' not in mote.info:
            # log a notRun message
            self.setNotRunDesc(
                'This test could not run because mote {0} did not report any numTxFail counter (the counters it did report are {1}).'.format(
                    self._formatMac(self.mac),
                    mote.info.keys()
                )
            )
            return
        
        if not mote.info['numTxOk']:
            # log a notRun message
            self.setNotRunDesc(
                'This test could not run because mote {0} did not send any packets succesfully (yet?) (numTxOk=={1}) and so its\'s impossible to calculate a ratio.'.format(
                    self._formatMac(self.mac),
                    mote.info['numTxOk']
                )
            )
            return
        
        #==== run the test
        
        availability = (1-float(mote.info['numTxFail'])/float(mote.info['numTxOk']))
        try:
            self.assertGreaterEqual(availability,self.MIN_MOTEAVAILABILITY)
        except AssertionError as err:
    
            # log an error message
            self.setFailureDesc(
                'availability for mote {0} is {1}, expected at least {2}.'.format(
                    self._formatMac(self.mac),
                    availability,
                    self.MIN_MOTEAVAILABILITY
                )
            )
            
            # let the unittest framework know this test failed
            raise
        else:
            # log an success message
            self.setSuccessDesc(
                'availability for mote {0} is {1}, which is better than {2}.'.format(
                    self._formatMac(self.mac),
                    availability,
                    self.MIN_MOTEAVAILABILITY
                )
            )
    
    #======================== helpers =========================================
