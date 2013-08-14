import NetworkTest

class TestStabilityVsRssi(NetworkTest.NetworkTest):
    
    MIN_NUM_PACKETS =  30
    THRES_HIGH_RSSI = -70
    THRES_HIGH_STAB =   0.7
    THRES_LOW_RSSI  = -80
    THRES_LOW_STAB  =   0.5
    
    @staticmethod
    def getType():
        return NetworkTest.NetworkTest.PER_MOTE
    
    #======================== tests ===========================================
    
    def test_stabilityVsRssi(self):
        
        mote = self.networkState.motes[self.mac]
        
        goOn = False
        for neighbor in mote.neighbors:
            if neighbor.numTxPk>self.MIN_NUM_PACKETS and neighbor.rsl<0:
                goOn = True
                break
        
        if not goOn:
            # log a notRun message
            self.setNotRunDesc(
                'This test could not run because mote {0} does not have any neighbor to which it has sent more than {1} packet, and which reports a negative RSSI.'.format(
                    self._formatMac(self.mac),
                    self.MIN_NUM_PACKETS
                )
            )
            return
        
        for neighbor in mote.neighbors:
            if neighbor.numTxPk>self.MIN_NUM_PACKETS and neighbor.rsl<0:
                linkStability = 1-float(neighbor.numTxFail)/float(neighbor.numTxPk)
                linkRssi      = neighbor.rsl
                
                try:
                    self.assertFalse(linkRssi>self.THRES_HIGH_RSSI and linkStability<self.THRES_HIGH_STAB)
                except AssertionError as err:
                    # log an error message
                    self.setFailureDesc(
                        'the link\'s RSSI is above {0}dBm (at {1}dBm), while the link stability is below {2} (at {3})'.format(
                            self.THRES_HIGH_RSSI,
                            linkRssi,
                            self.THRES_HIGH_STAB,
                            linkStability,
                        )
                    )
                    # let the unittest framework know this test failed
                    raise
                else:
                    # log an success message
                    self.setSuccessDesc(
                        'this link appears normal: RSSI={0}, stability={1}'.format(
                            linkRssi,
                            linkStability,
                        )
                    )
                
                try:
                    self.assertFalse(linkRssi>self.THRES_LOW_RSSI  and linkStability<self.THRES_LOW_STAB)
                except AssertionError as err:
                    # log an error message
                    self.setFailureDesc(
                        'the link\'s RSSI is above {0}dBm (at {1}dBm), while the link stability is below {2} (at {3})'.format(
                            self.THRES_LOW_RSSI,
                            linkRssi,
                            self.THRES_LOW_STAB,
                            linkStability,
                        )
                    )
                    # let the unittest framework know this test failed
                    raise
                else:
                    # log an success message
                    self.setSuccessDesc(
                        'this link appears normal: RSSI={0}, stability={1}'.format(
                            linkRssi,
                            linkStability,
                        )
                    )
    
    #======================== helpers =========================================
