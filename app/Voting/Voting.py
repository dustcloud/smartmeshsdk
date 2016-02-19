#!/usr/bin/python

#============================ adjust path =====================================

import sys
import os
if __name__ == "__main__":
    here = sys.path[0]
    sys.path.insert(0, os.path.join(here, '..', '..','libs'))
    sys.path.insert(0, os.path.join(here, '..', '..','external_libs'))

#============================ verify installation =============================

import re
import time
import copy
import random

from SmartMeshSDK.utils import SmsdkInstallVerifier
(goodToGo,reason) = SmsdkInstallVerifier.verifyComponents(
    [
        SmsdkInstallVerifier.PYTHON,
        SmsdkInstallVerifier.PYSERIAL,
    ]
)
if not goodToGo:
    print "Your installation does not allow this application to run:\n"
    print reason
    raw_input("Press any button to exit")
    sys.exit(1)

#============================ imports =========================================

import threading

from   SmartMeshSDK.utils              import AppUtils,                   \
                                              FormatUtils
from   SmartMeshSDK.ApiDefinition      import IpMgrDefinition
from   SmartMeshSDK.ApiException       import APIError
from   SmartMeshSDK.IpMgrConnectorMux  import IpMgrSubscribe
from   dustUI                          import dustWindow,                 \
                                              dustFrameConnection,        \
                                              dustFrameVoting

#============================ logging =========================================

import logging

# local
class NullHandler(logging.Handler):
    def emit(self, record):
        pass
log = logging.getLogger('App')
log.setLevel(logging.ERROR)
log.addHandler(NullHandler())

#============================ defines =========================================

#============================ globals =========================================

#============================ setup/teardown ==================================

AppUtils.configureLogging()

#============================ defines =========================================

GUIUPDATEPERIOD         = 500 # in ms
WKP_VOTING              = 0xf0b8
VOTES_FILE              = 'votes.csv'
QUESTIONNUM_DLFT        = 1

#============================ body ============================================

##
# \addtogroup Voting
# \{
# 

class notifClient(object):
    
    VAL_A               = 0x01
    VAL_B               = 0x02
    VAL_C               = 0x04
    VAL_D               = 0x08
    VAL_ALL             = [
        VAL_A,
        VAL_B,
        VAL_C,
        VAL_D,
    ]
    VAL_TESTMOTE        = 0x00
    
    BUTTON_A            = 'A'
    BUTTON_B            = 'B'
    BUTTON_C            = 'C'
    BUTTON_D            = 'D'
    BUTTON_ALL          = [
        BUTTON_A,
        BUTTON_B,
        BUTTON_C,
        BUTTON_D,
    ]
    
    def __init__(self, connector, disconnectedCallback, presenterMote=None):
        
        # store params
        self.connector = connector
        self.disconnectedCallback = disconnectedCallback
        
        # variables
        self.dataLock        = threading.RLock()
        self.networkMotes    = []
        self.presenterMote   = presenterMote
        self.questionNum     = self._getInitQuestionNum()
        self._resetData()
        
        # subscriber
        if (self.connector!=None and self.disconnectedCallback!=None):
            self.subscriber = IpMgrSubscribe.IpMgrSubscribe(self.connector)
            self.subscriber.start()
            self.subscriber.subscribe(
                notifTypes =    [
                                    IpMgrSubscribe.IpMgrSubscribe.NOTIFDATA,
                                ],
                fun =           self._notifDataCallback,
                isRlbl =        False,
            )
            self.subscriber.subscribe(
                notifTypes =    [
                    IpMgrSubscribe.IpMgrSubscribe.ERROR,
                    IpMgrSubscribe.IpMgrSubscribe.FINISH,
                ],
                fun =           self.disconnectedCallback,
                isRlbl =        False,
            )
    
    #======================== public ==========================================
    
    def setPresenterMote(self,presenterMote):
        with self.dataLock:
            self.presenterMote    = presenterMote
    
    def nextQuestion(self):
        with self.dataLock:
            
            # save the current data
            self._saveData()
            
            # reset the data
            self._resetData()
            
            # increment the question number
            self.questionNum += 1
    
    def scan(self):
        
        networkMotes = []
        
        currentMac     = (0,0,0,0,0,0,0,0) # start getMoteConfig() iteration with the 0 MAC address
        continueAsking = True
        while continueAsking:
            try:
                res = self.connector.dn_getMoteConfig(currentMac,True)
            except APIError:
                continueAsking = False
            else:
                if ((not res.isAP) and (res.state in [4,])):
                    networkMotes.append(tuple(res.macAddress))
                currentMac = res.macAddress
        
        with self.dataLock:
            self.networkMotes          = networkMotes
    
    def getNetworkMotes(self):
        with self.dataLock:
            returnVal                  = copy.deepcopy(self.networkMotes)
        return returnVal 
    
    def getData(self):
        with self.dataLock:
            returnVal = {}
            returnVal['questionNum']   = self.questionNum
            returnVal['numVotes']      = copy.deepcopy(self.numVotes)
            returnVal['firstMACs']     = copy.deepcopy(self.firstMACs)
            returnVal['firstMAC']      = self.firstMAC
        
        return returnVal
    
    def disconnect(self):
        self.connector.disconnect()
    
    def close(self):
        self._saveData()
    
    #======================== private =========================================
    
    def _resetData(self):
        with self.dataLock:
            self.numVotes         = {
                self.BUTTON_A:    0,
                self.BUTTON_B:    0,
                self.BUTTON_C:    0,
                self.BUTTON_D:    0,
            }
            self.firstTs          = {
                self.BUTTON_A:    None,
                self.BUTTON_B:    None,
                self.BUTTON_C:    None,
                self.BUTTON_D:    None,
            }
            self.firstMACs        = {
                self.BUTTON_A:    None,
                self.BUTTON_B:    None,
                self.BUTTON_C:    None,
                self.BUTTON_D:    None,
            }
            self.firstMAC         = None
            self.motesWhichVoted  = []
    
    def _saveData(self):
        
        #===== format lines
        
        # header line (if needed)
        headerline  = None
        if not os.path.isfile(VOTES_FILE):
            headerline  = []
            headerline += ['time']
            headerline += ['question_number']
            headerline += ['first_mote']
            headerline += ['num_votes_A']
            headerline += ['first_mote_A']
            headerline += ['num_votes_B']
            headerline += ['first_mote_B']
            headerline += ['num_votes_C']
            headerline += ['first_mote_C']
            headerline += ['num_votes_D']
            headerline += ['first_mote_D']
            headerline  = '{0}\n'.format(','.join(headerline))
        
        # data line
        dataline = None
        with self.dataLock:
            dataline    = []
            dataline   += [time.strftime("%d/%m/%y %H:%M:%S")]                 # time
            dataline   += [self.questionNum]                                   # question_number
            dataline   += [self._formatSaveMAC(self.firstMAC)]                 # first_mote
            dataline   += [self.numVotes[self.BUTTON_A]]                       # num_votes_A
            dataline   += [self._formatSaveMAC(self.firstMACs[self.BUTTON_A])] # first_mote_A
            dataline   += [self.numVotes[self.BUTTON_B]]                       # num_votes_B
            dataline   += [self._formatSaveMAC(self.firstMACs[self.BUTTON_B])] # first_mote_B
            dataline   += [self.numVotes[self.BUTTON_C]]                       # num_votes_C
            dataline   += [self._formatSaveMAC(self.firstMACs[self.BUTTON_C])] # first_mote_C
            dataline   += [self.numVotes[self.BUTTON_D]]                       # num_votes_D
            dataline   += [self._formatSaveMAC(self.firstMACs[self.BUTTON_D])] # first_mote_D
            dataline    = '{0}\n'.format(','.join([str(d) for d in dataline]))
        
        #===== write to file
        
        f = open(VOTES_FILE,'a')
        if headerline:
            f.write(headerline)
        if dataline:
            f.write(dataline)
        f.close()
    
    def _formatSaveMAC(self,mac):
        if mac:
            returnVal   = FormatUtils.formatMacString(mac)
        else:
            returnVal   = mac
        return returnVal
    
    def _notifDataCallback(self, notifName, notifParams):
        
        try:
            
            assert notifName==IpMgrSubscribe.IpMgrSubscribe.NOTIFDATA
            
            if  (
                    notifParams.srcPort==WKP_VOTING   and
                    notifParams.dstPort==WKP_VOTING   and
                    len(notifParams.data)==1          and
                    (notifParams.data[0] in self.VAL_ALL+[self.VAL_TESTMOTE])
                ):
                
                # parse packet
                mac          = notifParams.macAddress
                ts_us        = notifParams.utcSecs*1000000+notifParams.utcUsecs
                if   notifParams.data[0]==self.VAL_A:
                    vote     = self.BUTTON_A
                elif notifParams.data[0]==self.VAL_B:
                    vote     = self.BUTTON_B
                elif notifParams.data[0]==self.VAL_C:
                    vote     = self.BUTTON_C
                elif notifParams.data[0]==self.VAL_D:
                    vote     = self.BUTTON_D
                elif notifParams.data[0]==self.VAL_TESTMOTE:
                    print 'WARNING: received test mote data'
                    vote     = self.BUTTON_D
                
                # indicate vote
                with self.dataLock:
                    if FormatUtils.formatMacString(mac)==self.presenterMote:
                        self.nextQuestion()
                    else:
                        self._indicateVote(mac,ts_us,vote)
            
        except Exception as err:
            print type(err)
            print err
            raise
    
    def _getInitQuestionNum(self):
        returnVal = QUESTIONNUM_DLFT
        
        try:
            maxNum = 0
            for line in open(VOTES_FILE,'r'):
                m = re.match(".+,(\d+),.+,.+,.+,.+,.+,.+,.+,.+,.+", line)
                if m:
                    num = int(m.group(1))
                    if num>maxNum:
                        maxNum = num
            if maxNum>0:
                returnVal = maxNum+1
        except IOError:
            # problem reading file, maybe not there
            pass
        
        return returnVal
    
    def _indicateVote(self,mac,ts_us,vote):
        assert vote in self.BUTTON_ALL
        
        with self.dataLock:
            
            # abort if already voted
            if mac in self.motesWhichVoted:
                return
            self.motesWhichVoted      += [mac]
            
            # increment number of votes
            self.numVotes[vote]       += 1
            
            # decide whether update firstMAC
            minTs = None
            for b in self.BUTTON_ALL:
                thisTs = self.firstTs[b]
                if thisTs!=None and (minTs==None or thisTs<minTs):
                    minTs = thisTs
            if minTs==None:
                self.firstMAC = mac
            else:
                if (self.firstMAC==None or ts_us<minTs):
                    self.firstMAC = mac
            
            # decide whether update firstMACs
            if (self.firstTs[vote]==None or ts_us<self.firstTs[vote]):
                self.firstTs[vote]     = ts_us
                self.firstMACs[vote]   = mac

class votingGui(object):
    
    def __init__(self):
        
        # variables
        self.guiLock            = threading.Lock()
        self.apiDef             = IpMgrDefinition.IpMgrDefinition()
        self.notifClientHandler = None
        self.presenterMote      = None
        
        # create window
        self.window = dustWindow.dustWindow(
            'Voting',
            self._windowCb_close,
        )
        
        # add a connection frame
        self.connectionFrame = dustFrameConnection.dustFrameConnection(
            self.window,
            self.guiLock,
            self._connectionFrameCb_connected,
            frameName="manager connection",
            row=0,column=0
        )
        self.connectionFrame.apiLoaded(self.apiDef)
        self.connectionFrame.show()
        
        # add a voting frame
        self.votingFrame         = dustFrameVoting.dustFrameVoting(
            self.window,
            self.guiLock,
            nextQuestionCb        = self._nextQuestionCb,
            presenterChangedCb    = self._presenterChangedCb,
            scanCb                = self._scanCb,
            frameName             = "voting",
            row=1,column=0,
        )
    
    #======================== public ==========================================
    
    def start(self):
        '''
        This command instructs the GUI to start executing and reacting to 
        user interactions. It never returns and should therefore be the last
        command called.
        '''
        try:
            self.window.mainloop()
        except SystemExit:
            sys.exit()
    
    #======================== private =========================================
    
    def _windowCb_close(self):
        if self.notifClientHandler:
            self.notifClientHandler.disconnect()
            self.notifClientHandler.close()
    
    def _connectionFrameCb_connected(self,connector):
        '''
        \brief Called when the connectionFrame has connected.
        '''
        
        # store the connector
        self.connector = connector
        
        # start a notification client
        self.notifClientHandler = notifClient(
            self.connector,
            self._connectionFrameCb_disconnected,
            presenterMote = self.presenterMote,
        )
        
        # show the votingFrame
        self.votingFrame.show()
        
        # schedule the GUI to update itself in GUIUPDATEPERIOD ms
        self.votingFrame.after(GUIUPDATEPERIOD,self._updateVoting)
    
    def _connectionFrameCb_disconnected(self,notifName,notifParams):
        '''
        \brief Called when the connectionFrame has disconnected.
        '''
        
        # update the GUI
        self.connectionFrame.updateGuiDisconnected()
        
        # disconnect the notifClient
        self.notifClientHandler.disconnect()
        
        # delete the connector
        self.connector = None
    
    def _nextQuestionCb(self):
        if self.notifClientHandler:
            self.notifClientHandler.nextQuestion()
    
    def _presenterChangedCb(self,newPresenter):
        self.presenterMote = newPresenter
        if self.notifClientHandler:
            self.notifClientHandler.setPresenterMote(newPresenter)
    
    def _scanCb(self):
        if self.notifClientHandler:
            self.notifClientHandler.scan()
    
    def _updateVoting(self):
        
        # get the data
        rawData = self.notifClientHandler.getData()
        
        # load data in frame
        self.votingFrame.loadData(rawData)
        
        # get the network motes
        networkMotes = self.notifClientHandler.getNetworkMotes()
        
        # load network motes in frame
        self.votingFrame.loadNetworkMotes(networkMotes)
        
        # schedule the next update
        self.votingFrame.after(GUIUPDATEPERIOD,self._updateVoting)

#============================ main ============================================

def main():
    votingGuiHandler = votingGui()
    votingGuiHandler.start()

if __name__ == '__main__':
    main()

##
# end of Voting
# \}
# 
