#!/usr/bin/python

#============================ adjust path =====================================

import sys
import os
if __name__ == "__main__":
    here = sys.path[0]
    sys.path.insert(0, os.path.join(here, '..', '..','libs'))
    sys.path.insert(0, os.path.join(here, '..', '..','external_libs'))

#============================ verify installation =============================

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
import time
import traceback

from   SmartMeshSDK.utils              import AppUtils,                   \
                                              FormatUtils
from   SmartMeshSDK.ApiDefinition      import IpMoteDefinition
from   SmartMeshSDK.IpMoteConnector    import IpMoteConnector
from   SmartMeshSDK.ApiException       import APIError,                   \
                                              ConnectionError,            \
                                              QueueError
from   dustUI                          import dustWindow,                 \
                                              dustFrameSensorTx,          \
                                              dustFrameTable,             \
                                              dustFrameConnection,        \
                                              dustFrameText,              \
                                              dustStyle

#============================ logging =========================================

# local

import logging
class NullHandler(logging.Handler):
    def emit(self, record):
        pass
log = logging.getLogger('App')
log.setLevel(logging.ERROR)
log.addHandler(NullHandler())

# global

AppUtils.configureLogging()

#============================ defines =========================================

GUIUPDATEPERIOD    = 500
SOURCE_PORT        = 60000
BW_REQUESTED       = 5000

#============================ body ============================================

##
# \addtogroup Upstream
# \{
# 

class FsmState(object):
    
    def __init__(self):
        self.states  = []
        self.varLock = threading.Lock()
    
    #==================== public ==========================================
    
    def addState(self,name,desc):
        self.varLock.acquire()
        self.states.append(
            {
                'name':   name,
                'active': 'todo',
                'desc':   desc,
            }
        )
        self.varLock.release()
    
    def resetStates(self):
        self.varLock.acquire()
        for state in self.states:
            state['active']='todo'
            if 'startTime' in state:
                del state['startTime']
            if 'stopTime' in state:
                del state['stopTime']
        self.varLock.release()
    
    def addLog(self,name,log):
        self.varLock.acquire()
        self._getStateByName(name)['log'] = log
        self.varLock.release()
    
    def switchActiveState(self,name):
        self.varLock.acquire()
        activeState = self._getActiveState()
        if activeState:
           activeState['stopTime'] = time.time()
           activeState['active']   = 'done'
        self._getStateByName(name)['active']    = 'active'
        self._getStateByName(name)['startTime'] = time.time()
        self.varLock.release()
        log.debug("state="+str(name))
        
    def isActiveState(self,name):
        self.varLock.acquire()
        returnVal = (self._getStateByName(name)['active']=='active')
        self.varLock.release()
        return returnVal
    
    def getAllData(self):
        self.varLock.acquire()
        returnVal = self.states[:] # creates a copy
        self.varLock.release()
        return returnVal
        
    def getNameActiveState(self):
        self.varLock.acquire()
        returnVal = self._getActiveState()['name']
        self.varLock.release()
        return returnVal

    #==================== private =========================================
    
    def _getActiveState(self):
        for state in self.states:
            if state['active']=='active':
                return state
        return None
        
    def _getStateByName(self,name):
        for state in self.states:
            if state['name']==name:
                return state
        raise KeyError('state '+name+' does not exist')

class NotifListener(threading.Thread):
    
    def __init__(self,connector,notifCb,disconnectedCb):
    
        # record variables
        self.connector       = connector
        self.notifCb         = notifCb
        self.disconnectedCb  = disconnectedCb
        
        # init the parent
        threading.Thread.__init__(self)
        
        # give this thread a name
        self.name            = 'NotifListener'
        
    #======================== public ==========================================
    
    def run(self):
        keepListening = True
        while keepListening:
            try:
                input = self.connector.getNotification(-1)
            except (ConnectionError,QueueError) as err:
                keepListening = False
            else:
                if input:
                    self.notifCb(input)
                else:
                    keepListening = False
        self.disconnectedCb()

class MoteClient(threading.Thread):
    
    def __init__(self,readyToSendCb,disconnectedCb,textFrame):
    
        # store params
        self.readyToSendCb   = readyToSendCb
        self.disconnectedCb  = disconnectedCb
        self.textFrame       = textFrame
        
        # variables
        self.payloadCounter  = 0
        self.stop            = False
        
        # fsm states
        self.states          = FsmState()
        self.states.addState('WAITFORINITIALNOTIF',
                             'wait for initial notifications')
        self.states.addState('ASSESSMOTESTATE',
                             'evaluate what the current mote state is')
        self.states.addState('CONFIGURE',
                             'start configuring the mote')
        '''
        self.states.addState('CONFIGURING_NETID',
                             'configuring the netid')
        '''
        self.states.addState('CONFIGURING_DC',
                             'configuring the join duty cycle')
        self.states.addState('CONFIGURED',
                             'configured')
        self.states.addState('SEARCHING',
                             'searching for a network')
        self.states.addState('JOINREQUESTSENT',
                             'join request sent')
        self.states.addState('OPERATIONAL',
                             'mote is operational')
        self.states.addState('JOINED',
                             'joined')
        self.states.addState('REQUESTINGSERVICE',
                             'requesting service')
        self.states.addState('SERVICEGRANTED',
                             'service granted')
        self.states.addState('OPENSOCKET',
                             'open a socket')
        self.states.addState('BINDSOCKET',
                             'bind the socket')
        self.states.addState('READYTOSEND',
                             'ready to send')
        
        # FSM semaphore
        self.sem             = threading.BoundedSemaphore()
        
        # reset the FSM
        self._resetFsm()
        
        # if the socket already exists, assume it's socket 22
        self.socketId        = 22
        
        # intialize the thread parent class
        threading.Thread.__init__(self)
        
        # give this thread a name
        self.name            = 'MoteClient'
    
    #======================== public ==========================================
    
    def apiLoaded(self,apiDef):
        self.apiDef     = apiDef
        
    def connectorLoaded(self,connector):
        self.connector = connector
    
    def run(self):
    
        log.debug("fsm started")
    
        # start a NotifListener
        self.notifListener   = NotifListener (
                                self.connector,
                                self._notifIndication,
                                self._disconnectedIndication,
                                )
        self.notifListener.start()
        
        while True:
        
            log.debug(    "============================== FSM STOP")
            # wait for the FSM to be kicked
            self.sem.acquire()
            log.debug("\n\n============================== FSM START")
            log.debug("state="+self.states.getNameActiveState())
            
            # stop if needed
            if self.stop:
                break
            
            # execute an action based on state
            try:
                if   self.states.isActiveState('WAITFORINITIALNOTIF'):
                    self._actionWaitForInitialNotification()
                elif self.states.isActiveState('ASSESSMOTESTATE'):
                    self._assessMoteState()
                elif self.states.isActiveState('CONFIGURE'):
                    self._actionConfigure()
                elif self.states.isActiveState('CONFIGURED'):
                    self._actionJoin()
                elif self.states.isActiveState('JOINED'):
                    self._actionRequestService()
                elif self.states.isActiveState('SERVICEGRANTED'):
                    self._actionSetupSocket()
                elif self.states.isActiveState('READYTOSEND'):
                    self.readyToSendCb(self.socketId)
                else:
                    raise RuntimeError("unexpected FSM state="+self.states.getNameActiveState())
            except ConnectionError as err:
                print err
                self.textFrame.write(str(err))
                log.error(err)
                self.disconnect()
            except:
                self._publishErrorText("Unexpected error: {0}".format(sys.exc_info()[0]))
                raise
        
        self.disconnectedCb()
    
    def disconnect(self):
        self.connector.disconnect()
    
    #======================== private =========================================
    
    #===== actions
    
    def _resetFsm(self):
    
        # reset states
        self.states.resetStates()
    
        # change state
        self.states.switchActiveState('WAITFORINITIALNOTIF')
    
    def _actionWaitForInitialNotification(self):
        # wait for possible pending notifications (sent by mote every 500ms)
        time.sleep(2)
        
        # change state
        self.states.switchActiveState('ASSESSMOTESTATE')
        
        # kick the FSM
        self._kickFsm()
        
    def _assessMoteState(self):
    
        # read mote status
        try:
            res = self.connector.dn_getParameter_moteStatus()
        except Exception as err:
            self._publishErrorText("Could not execute dn_getParameter_moteStatus: {0}".format(err))
        
        if res.state!=5:
            # not operational, next step is CONFIGURE
            
            # change state
            self.states.switchActiveState('CONFIGURE')
            
            # kick the FSM
            self._kickFsm()
            return
        
        # read service
        try:
            res = self.connector.dn_getServiceInfo(0xfffe, # destination mote (0xfffe=manager)
                                                   0,      # type (0=bandwidth)
                                                   )
        except APIError as err:
            # happens when no service is active to manager; will return RC=14 (NOT_FOUND)
            res = None
            self._publishErrorText("APIError when executing dn_getServiceInfo: {0}".format(err))
        except Exception as err:
            res = None
            self._publishErrorText("Could not execute dn_getServiceInfo: {0}".format(err))
            
        if (not res) or (res.type!=0) or (res.value>BW_REQUESTED):
            # not the right service, next step is JOINED
            
            # change state
            self.states.switchActiveState('CONFIGURE')
            
            # kick the FSM
            self._kickFsm()
            return
            
        # if you get here all is good, next state is READYTOSEND
        
        # change state
        self.states.switchActiveState('READYTOSEND')
        
        # kick the FSM
        self._kickFsm()
    
    def _actionConfigure(self):
        '''
        NETWORKID  = <enter your networkid>
        # change state
        self.states.switchActiveState('CONFIGURING_NETID')
        
        # get the mote's networkId
        res = self.connector.dn_getParameter_networkId()
        
        # set the mote's neworkId, if needed
        if res.netId!=NETWORKID:
            self.connector.dn_setParameter_networkId(NETWORKID)
        '''
        
        self.states.switchActiveState('CONFIGURING_DC')
        
        # set the join duty cycle to 100%
        try:
            self.connector.dn_setParameter_joinDutyCycle(0xff)
        except Exception as err:
            self._publishErrorText("Could not execute dn_setParameter_joinDutyCycle: {0}".format(err))
        
        # change state
        self.states.switchActiveState('CONFIGURED')
        
        # kick the FSM
        self._kickFsm()
    
    def _actionJoin(self):
        # change state
        self.states.switchActiveState('SEARCHING')
        
        # have the mote join
        try:
            res = self.connector.dn_join()
        except Exception as err:
            self._publishErrorText("Could not execute dn_join: {0}".format(err))
        else:
            log.debug(res)
    
    def _actionRequestService(self):
        # change state
        self.states.switchActiveState('REQUESTINGSERVICE')
        
        # request service
        try:
            res = self.connector.dn_requestService(0xfffe,      # destination mote (0xfffe=manager)
                                                   0,           # type (0=bandwidth)
                                                   BW_REQUESTED # expected Tx period (in ms)
                                                   )
        except Exception as err:
            self._publishErrorText("Could not execute dn_requestService: {0}".format(err))
        
        log.debug(res)
    
    def _actionSetupSocket(self):
        # change state
        self.states.switchActiveState('OPENSOCKET')
        
        # open a socket
        try:
            res = self.connector.dn_openSocket(0)
        except Exception as err:
            self._publishErrorText("Could not execute dn_openSocket: {0}".format(err))
            
        # record socket Id
        self.socketId = res.socketId
        
        # change state
        self.states.switchActiveState('BINDSOCKET')
        
        # bind socket
        try:
            res = self.connector.dn_bindSocket(self.socketId,SOURCE_PORT)
        except Exception as err:
            self._publishErrorText("Could not execute dn_bindSocket: {0}".format(err))
        
        # change state
        self.states.switchActiveState('READYTOSEND')
        
        # kick the FSM
        self._kickFsm()
    
    #===== callbacks
    
    def _notifIndication(self,notif):
    
        log.debug("received notif="+str(notif))
        
        (notifType,params) = notif
        
        if notifType=='events':
            
            moteEventsString = self.apiDef.notifFieldValueToDesc(
                ['events'],
                'events',
                params.events)
            
            log.debug("moteEventsString="+str(moteEventsString))
                
            if  (
                    self.states.isActiveState('SEARCHING')          and
                    moteEventsString=='joinStarted'
                ):
                    # change state
                    self.states.switchActiveState('JOINREQUESTSENT')
            elif(
                    self.states.isActiveState('JOINREQUESTSENT')    and
                    moteEventsString=='operational'
                ):
                    # change state
                    self.states.switchActiveState('OPERATIONAL')
            elif(
                    self.states.isActiveState('OPERATIONAL')        and
                    moteEventsString=='svcChange'
                ):
                    # change state
                    self.states.switchActiveState('JOINED')
                    
                    # kick the FSM
                    self._kickFsm()
            elif(
                    self.states.isActiveState('REQUESTINGSERVICE')  and
                    moteEventsString=='svcChange'
                ):
                    # change state
                    self.states.switchActiveState('SERVICEGRANTED')
                    
                    # kick the FSM
                    self._kickFsm()
            elif(
                    moteEventsString=='boot'
                ):
                    # change state
                    self._resetFsm()
                    
                    # kick the FSM
                    self._kickFsm()
            else:
                self._publishErrorText('unexpected mote event {0}'.format(moteEventsString))
                
                # change state
                self._resetFsm()
                
                # kick the FSM
                self._kickFsm()
                    
        log.debug("return from _notifIndication")
    
    def _disconnectedIndication(self):
    
        log.debug("disconnected")
        
        self.stop = True
        
        # change state
        self._resetFsm()
        
        # kick the FSM
        self._kickFsm()
    
    #===== helpers
        
    def _kickFsm(self):
        log.debug("kick fsm try")
        try:
            self.sem.release()
        except ValueError:
            log.debug("kick fsm canceled")
        else:
            log.debug("kick fsm ok")
    
    def _publishErrorText(self,errorText):
        
        # print error text to console
        print errorText
        
        # print exception stack
        traceback.print_exc()
        
        # display in GUI text Frame
        self.textFrame.write(errorText)
        
        # write in logfile
        log.error(errorText)

class UpstreamGui(object):
    
    def __init__(self):
        
        # variables
        self.guiLock            = threading.Lock()
        self.apiDef             = IpMoteDefinition.IpMoteDefinition()
        
        # initialize GUI window
        self.window = dustWindow.dustWindow('Upstream',self._windowCb_close)
        
        # create a sensor frame (don't show yet)
        self.sensorFrame = dustFrameSensorTx.dustFrameSensorTx(
                                    self.window,
                                    self.guiLock,
                                    frameName="sensor data to send",
                                    row=0,column=0)
        self.sensorFrame.show()
        
        # create a table frame
        self.tableFrame = dustFrameTable.dustFrameTable(
                                    self.window,
                                    self.guiLock,
                                    frameName="join state machine",
                                    row=1,column=0)
        
        # add a connection frame
        self.connectionFrame = dustFrameConnection.dustFrameConnection(
                                    self.window,
                                    self.guiLock,
                                    self._connectionFrameCb_connected,
                                    frameName="mote connection",
                                    row=2,column=0)
        self.connectionFrame.apiLoaded(self.apiDef)
        self.connectionFrame.show()
        
        # create a table frame
        self.textFrame = dustFrameText.dustFrameText(
                                    self.window,
                                    self.guiLock,
                                    frameName="tip",
                                    row=3,column=0)
        self.textFrame.setWrapLength(400)
        self.textFrame.show()
        output  = []
        output += ['Remember to reset your mote before starting this application.']
        output += ['The fields in the "sensor data to send" frame are preset with IPv6 address of the motedata.dustnetworks.com server, and the UDP port it is listening on. You can change this IPv6 address and UDP port to if you wish to send to a different server. Per the 6LoWPAN standard, a UDP port chosen between 61616 (0xF0B0) and 61631 (0xF0BF) results in the best compression, thus largest payload. See the mote API guide for further information.']
        output += ['Note: The "send to manager" and "send to host" button become active only once the mote has reached the READYTOSEND state.']
        self.textFrame.write('\n\n'.join(output))
        
        # update in GUI elements
        self._updateGui()
    
    #======================== public ==========================================
    
    def start(self):
        
        # schedule the GUI to update itself in GUIUPDATEPERIOD ms
        self.window.after(GUIUPDATEPERIOD,self._updateGui)
        
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
        try:
            self.moteClientHandler.disconnect()
        except AttributeError:
            pass
        
    def _connectionFrameCb_connected(self,connector):
        '''
        \brief Called when the connectionFrame has connected.
        '''
        
        # store the connector
        self.connector = connector
        
        # initialize mote client
        self.moteClientHandler = MoteClient(self._readyToSendIndication,
                                            self._disconnectedIndication,
                                            self.textFrame)
        
        # start the MoteClient
        self.moteClientHandler.apiLoaded(self.apiDef)
        self.moteClientHandler.connectorLoaded(self.connector)
        self.moteClientHandler.start()
        
        # show the table frame
        self.tableFrame.show()
        
    def _readyToSendIndication(self,socketId):
        # activate the sensor frame
        self.sensorFrame.activate(self.connector,socketId)
        
    def _disconnectedIndication(self):
        
        # update the GUI
        self.connectionFrame.updateGuiDisconnected()
        
        # delete the moteClientHandler
        self.moteClientHandler    = None
        
        # delete the connector
        self.connector            = None
        
    def _updateGui(self):
        
        try:
            rawData = self.moteClientHandler.states.getAllData()
            # get the data so can be plotted
            dataToPlot = [[i['name'],i['active'],i['desc'],self._timeRunning(i)] for i in rawData]
            
            displayOptions = {}
            displayOptions['rowColors'] = []
            for i in rawData:
                if   i['active']=='active':
                    displayOptions['rowColors'].append(dustStyle.dustStyle.COLOR_PRIMARY2)
                elif i['active']=='done':
                    displayOptions['rowColors'].append(dustStyle.dustStyle.COLOR_PRIMARY2_LIGHT)
                else:
                    displayOptions['rowColors'].append(dustStyle.dustStyle.COLOR_BG)
            
        except AttributeError:
            # happens when not connected
            pass
        else:
            # reverse the table to the first state is on the bottom
            dataToPlot.reverse()
            displayOptions['rowColors'].reverse()
            # have the data plotted
            self.tableFrame.update(dataToPlot,displayOptions)
        
        # schedule next update
        self.window.after(GUIUPDATEPERIOD,self._updateGui)
        
    #======================== helpers =========================================
    
    def _timeRunning(self,data):
        returnVal = ''
        
        if 'startTime' in data:
            if 'stopTime' in data:
                totalTime = data['stopTime']-data['startTime']
            else:
                totalTime = time.time()-data['startTime']
            returnVal ='%.3fs'%totalTime
        
        return returnVal

#============================ main ============================================

def main():
    UpstreamGuiHandler = UpstreamGui()
    UpstreamGuiHandler.start()

if __name__ == '__main__':
    main()

##
# end of Upstream
# \}
# 
