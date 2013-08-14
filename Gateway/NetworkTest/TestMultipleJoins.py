import NetworkTest

class TestMultipleJoins(NetworkTest.NetworkTest):
    
    @staticmethod
    def getType():
        return NetworkTest.NetworkTest.LAST_MOTE
    
    #======================== tests ===========================================
    
    def test_multipleJoins(self):
        
        mote = self.networkState.motes[self.mac]
        try:
            self.assertEqual(len(mote.timestamps[Mote.TS_MOTEJOIN]),1)
        except AssertionError as err:
            
            # log an error message
            self.setFailureDesc(
                'mote {0} joined {1} times.'.format(
                    self._formatMac(self.mac),
                    len(mote.timestamps[Mote.TS_MOTEJOIN])
                )
            )
            
            # let the unittest framework know this test failed
            raise
        else:
            # log an success message
            self.setSuccessDesc(
                'mote {0} joined {1} time.'.format(
                    self._formatMac(self.mac),
                    len(mote.timestamps[Mote.TS_MOTEJOIN])
                )
            )
    
    #======================== helpers =========================================
