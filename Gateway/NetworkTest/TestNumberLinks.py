import NetworkTest
from Gateway import NetworkState

class TestNumberLinks(NetworkTest.NetworkTest):
    
    MAX_LINKS_MOTE  = 180
    MAX_TX_LINKS_AP = 140
    
    TXLINK = 2 # TODO replace by attribute of Path object when defined
    RXLINK = 3 # TODO replace by attribute of Path object when defined
    
    @staticmethod
    def getType():
        return NetworkTest.NetworkTest.PER_MOTE
    
    #======================== tests ===========================================
    
    def test_txRxBalance(self):
    
        mote = self.networkState.motes[self.mac]
        
        if mote.info['isAP']:
            # log a notRun message
            self.setNotRunDesc(
                'This test could not run because mote {0} is an AP (isAP=={1}).'.format(
                    self._formatMac(self.mac),
                    mote.info['isAP']
                )
            )
            return
        
        (numTx,numRx) = self._countLinks(mote)
        try:
            self.assertGreater(numTx,numRx)
        except AssertionError as err:
            # log an error message
            self.setFailureDesc(
                'mote {0} has {1} TX and {2} RX links'.format(
                    self._formatMac(self.mac),
                    numTx,
                    numRx,
                )
            )
            # let the unittest framework know this test failed
            raise
        else:
            # log an success message
            self.setSuccessDesc(
                'mote {0} has {1} TX and {2} RX links'.format(
                    self._formatMac(self.mac),
                    numTx,
                    numRx,
                )
            )
    
    def test_linksMote(self):
        
        mote = self.networkState.motes[self.mac]
        
        if mote.info['isAP']:
            # log a notRun message
            self.setNotRunDesc(
                'This test could not run because mote {0} is an AP (isAP=={1}).'.format(
                    self._formatMac(self.mac),
                    mote.info['isAP']
                )
            )
            return
        
        (numTx,numRx) = self._countLinks(mote)
        try:
            self.assertLessEqual(numTx+numRx,self.MAX_LINKS_MOTE)
        except AssertionError as err:
            # log an error message
            self.setFailureDesc(
                'mote {0} has {1} links (both TX and RX), which is more than the recommended max {2}'.format(
                    self._formatMac(self.mac),
                    numTx+numRx,
                    self.MAX_LINKS_MOTE,
                )
            )
            # let the unittest framework know this test failed
            raise
        else:
            # log an success message
            self.setSuccessDesc(
                'mote {0} has {1} links (both TX and RX), which is less than the recommended max {2}'.format(
                    self._formatMac(self.mac),
                    numTx+numRx,
                    self.MAX_LINKS_MOTE,
                )
            )
    
    def test_rxLinksAp(self):
        
        mote = self.networkState.motes[self.mac]
        
        if mote.info['isAP']:
            # log a notRun message
            self.setNotRunDesc(
                'This test could not run because mote {0} is an AP (isAP=={1}).'.format(
                    self._formatMac(self.mac),
                    mote.info['isAP']
                )
            )
            return
        
        (numTx,numRx) = self._countLinks(mote)
        try:
            self.assertLessEqual(numRx,self.MAX_TX_LINKS_AP)
        except AssertionError as err:
            # log an error message
            self.setFailureDesc(
                'AP mote {0} has {1} RX links, which is more than the recommended max {2}'.format(
                    self._formatMac(self.mac),
                    numRx,
                    self.MAX_TX_LINKS_AP,
                )
            )
            # let the unittest framework know this test failed
            raise
        else:
            # log an success message
            self.setSuccessDesc(
                'AP mote {0} has {1} RX links, which is less than the recommended max {2}'.format(
                    self._formatMac(self.mac),
                    numRx,
                    self.MAX_TX_LINKS_AP,
                )
            )
    
    #======================== helpers =========================================
    
    def _countLinks(self,mote):
        numTx      = 0
        numRx      = 0
        
        for neighbor,path in mote.paths.items():
            assert(type(path)==NetworkState.Path)
            if   path.direction==self.TXLINK:
                numTx       += path.numLinks
            elif path.direction==self.RXLINK:
                numRx       += path.numLinks
        
        return (numTx,numRx)
