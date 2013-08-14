import NetworkTest

class TestNumGoodNeighbors(NetworkTest.NetworkTest):
    
    MIN_NUMGOODNEIGHBORS = 3
    
    @staticmethod
    def getType():
        return NetworkTest.NetworkTest.LAST_MOTE
    
    #======================== tests ===========================================
    
    def test_numGoodNeighbors(self):
        
        mote = self.networkState.motes[self.mac]
        if ('numGoodNbrs' not in mote.info):
            # log a notRun message
            self.setNotRunDesc(
                'This test could not run because mote {0} did not report any numGoodNbrs counter (the counters it did report are {1}).'.format(
                    self._formatMac(self.mac),
                    mote.info.keys()
                )
            )
            return
        
        try:
            self.assertGreaterEqual(mote.info['numGoodNbrs'],self.MIN_NUMGOODNEIGHBORS)
        except AssertionError as err:
        
            # log an error message
            self.setFailureDesc(
                'mote {0} has {1} good neighbors, expected at least {2}.'.format(
                    self._formatMac(self.mac),
                    mote.info['numGoodNbrs'],
                    self.MIN_NUMGOODNEIGHBORS
                )
            )
            
            # let the unittest framework know this test failed
            raise
        else:
            # log an success message
            self.setSuccessDesc(
                'mote {0} has {1} good neighbors, which is more than {2}.'.format(
                    self._formatMac(self.mac),
                    mote.info['numGoodNbrs'],
                    self.MIN_NUMGOODNEIGHBORS
                )
            )
    
    #======================== helpers =========================================
