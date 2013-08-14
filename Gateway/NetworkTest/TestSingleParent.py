import NetworkTest
from Gateway import NetworkState

class TestSingleParent(NetworkTest.NetworkTest):
    
    TXLINK = 2 # TODO replace by attribute of Path object when defined
    RXLINK = 3 # TODO replace by attribute of Path object when defined
    
    @staticmethod
    def getType():
        return NetworkTest.NetworkTest.NETWORK_WIDE
    
    #======================== tests ===========================================
    
    def test_SingleSingleParentMote(self):
        
        numSingleParentMotes = 0
        for mac,mote in self.networkState.motes.items():
            (numTx,numRx) = self._countLinks(mote)
            if numTx==1:
                numSingleParentMotes += 1
        try:
            self.assertEqual(numSingleParentMotes,1)
        except AssertionError as err:
            
            # log an error message
            self.setFailureDesc(
                'there are {0} single parent motes in the network; we expected only 1.'.format(
                    numSingleParentMotes,
                )
            )
            
            # let the unittest framework know this test failed
            raise
        else:
            # log an success message
            self.setSuccessDesc(
                'there are {0} single parent motes in the network; which is expected and normal.'.format(
                    numSingleParentMotes,
                )
            )
    
    #======================== helpers =========================================
    
    def _countLinks(self,mote):
        numTx      = 0
        numRx      = 0
        
        for neighbor,path in mote.paths.items():
            assert(type(path)==NetworkState.Path)
            if   path.direction==self.TXLINK:
                numTx       += 1
            elif path.direction==self.RXLINK:
                numRx       += 1
        
        return (numTx,numRx)
