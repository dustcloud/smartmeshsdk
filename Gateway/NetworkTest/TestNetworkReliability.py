import NetworkTest

class TestNetworkReliability(NetworkTest.NetworkTest):
    
    MIN_NETWORKRELIABILITY = 0.999
    
    @staticmethod
    def getType():
        return NetworkTest.NetworkTest.NETWORK_WIDE
    
    #======================== tests ===========================================
    
    def test_networkReliability(self):
        
        # counter network-wide number of packets generated/lost
        numPktsGenerated = 0
        numPktsLost      = 0
        for mac,mote in self.networkState.motes.items():
            if ('packetsReceived' in mote.info):
                numPktsGenerated += mote.info['packetsReceived']
            if ('packetsLost' in mote.info):
                numPktsGenerated += mote.info['packetsLost']
        
        # stop here if both counters are 0
        if (not numPktsGenerated) and (not numPktsLost):
            # log a notRun message
            self.setNotRunDesc(
                'This test could not run because numPktsGenerated=={0} and numPktsLost=={1} and so its\'s impossible to calculate a ratio.'.format(
                    numPktsGenerated,numPktsLost
                )
            )
            return
        
        # calculate resulting network reliability
        networkReliability = (1-float(numPktsLost)/float(numPktsLost + numPktsGenerated))
        
        # make sure about threshold
        try:
            self.assertGreaterEqual(networkReliability,self.MIN_NETWORKRELIABILITY)
        except AssertionError as err:
            # log an error message
            self.setFailureDesc(
                'networkReliability={0} is below the expected {1}'.format(
                    networkReliability,
                    self.MIN_NETWORKRELIABILITY,
                )
            )
            # let the unittest framework know this test failed
            raise
        else:
            # log an success message
            self.setSuccessDesc(
                'networkReliability={0} is better than the expected {1}'.format(
                    networkReliability,
                    self.MIN_NETWORKRELIABILITY,
                )
            )
    
    #======================== helpers =========================================
