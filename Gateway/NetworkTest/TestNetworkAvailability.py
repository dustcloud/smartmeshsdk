import NetworkTest

class TestNetworkAvailability(NetworkTest.NetworkTest):
    
    MIN_NETWORKAVAILABILITY = 0.99
    
    @staticmethod
    def getType():
        return NetworkTest.NetworkTest.NETWORK_WIDE
    
    #======================== tests ===========================================
    
    def test_networkAvailability(self):
        
        # counter network-wide number of packets generated/failed
        numTxOk    = 0
        numTxFail  = 0
        for mac,mote in self.networkState.motes.items():
            if ('numTxOk' in mote.info):
                numTxOk     += mote.info['numTxOk']
            if ('numTxFail' in mote.info):
                numTxFail   += mote.info['numTxFail']
        
        # stop here if both counters are 0
        if not numTxOk:
            # log a notRun message
            self.setNotRunDesc(
                'This test could not run because no packets were sent in the network (yet?) (numTxOk=={0} for the network) and so its\'s impossible to calculate a ratio.'.format(
                    numTxOk
                )
            )
            return
        
        # calculate resulting network availbility
        networkAvailability = (1-float(numTxFail)/float(numTxOk))
        
        # make sure about threshold
        try:
            self.assertGreaterEqual(networkAvailability,self.MIN_NETWORKAVAILABILITY)
        except AssertionError as err:
            # log an error message
            self.setFailureDesc(
                'networkAvailability={0} is below the expected {1}'.format(
                    networkAvailability,
                    self.MIN_NETWORKAVAILABILITY,
                )
            )
            # let the unittest framework know this test failed
            raise
        else:
            # log an success message
            self.setSuccessDesc(
                'networkAvailability={0} is better than the expected {1}'.format(
                    networkAvailability,
                    self.MIN_NETWORKAVAILABILITY,
                )
            )
    
    #======================== helpers =========================================
