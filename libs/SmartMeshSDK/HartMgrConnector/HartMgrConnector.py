'''
This module was generated automatically. Do not edit directly.
'''

import collections
from   SmartMeshSDK import ApiException
from   HartMgrConnectorInternal import HartMgrConnectorInternal

##
# \addtogroup HartMgrConnector
# \{
# 

class HartMgrConnector(HartMgrConnectorInternal):
    '''
    \brief Public class for the HART Manager connector using the XML API.
    '''

    #======================== commands ========================================

    ##
    # The named tuple returned by the dn_activateAdvertising() function.
    # 
    # - <tt>result</tt>: 32-byte field formatted as a string.<br/>
    #     There is no restriction on the value of this field.
    # 
    Tuple_dn_activateAdvertising = collections.namedtuple("Tuple_dn_activateAdvertising", ['result'])

    ##
    # Activate advertisement frame
    # 
    # \param macAddr 25-byte field formatted as a string.<br/>
    #     There is no restriction on the value of this field.
    # \param timeout 4-byte field formatted as a int.<br/>
    #     There is no restriction on the value of this field.
    # 
    # \returns The response to the command, formatted as a #Tuple_dn_activateAdvertising named tuple.
    # 
    def dn_activateAdvertising(self, macAddr, timeout) :
        res = HartMgrConnectorInternal.send(self, ['activateAdvertising'], {"macAddr" : macAddr, "timeout" : timeout})
        return HartMgrConnector.Tuple_dn_activateAdvertising(**res)

    ##
    # The named tuple returned by the dn_activateFastPipe() function.
    # 
    # - <tt>result</tt>: 32-byte field formatted as a string.<br/>
    #     There is no restriction on the value of this field.
    # 
    Tuple_dn_activateFastPipe = collections.namedtuple("Tuple_dn_activateFastPipe", ['result'])

    ##
    # Activate the fast network pipe to the specified mote.
    # 
    # \param macAddr 25-byte field formatted as a string.<br/>
    #     There is no restriction on the value of this field.
    # \param pipeDirection 25-byte field formatted as a string.<br/>
    #     This field can only take one of the following values:
    #      - UniUp: upstream
    #      - UniDown: downstream
    #      - Bi: bidirectional
    # 
    # \returns The response to the command, formatted as a #Tuple_dn_activateFastPipe named tuple.
    # 
    def dn_activateFastPipe(self, macAddr, pipeDirection) :
        res = HartMgrConnectorInternal.send(self, ['activateFastPipe'], {"macAddr" : macAddr, "pipeDirection" : pipeDirection})
        return HartMgrConnector.Tuple_dn_activateFastPipe(**res)

    ##
    # The named tuple returned by the dn_cancelOtap() function.
    # 
    # - <tt>result</tt>: 32-byte field formatted as a string.<br/>
    #     There is no restriction on the value of this field.
    # 
    Tuple_dn_cancelOtap = collections.namedtuple("Tuple_dn_cancelOtap", ['result'])

    ##
    # This command cancels the OTAP (Over-The-Air-Programming) process to upgrade software on motes and the access point.
    # 
    # 
    # 
    # \returns The response to the command, formatted as a #Tuple_dn_cancelOtap named tuple.
    # 
    def dn_cancelOtap(self, ) :
        res = HartMgrConnectorInternal.send(self, ['cancelOtap'], {})
        return HartMgrConnector.Tuple_dn_cancelOtap(**res)

    ##
    # The named tuple returned by the dn_cli() function.
    # 
    # - <tt>result</tt>: 32-byte field formatted as a string.<br/>
    #     There is no restriction on the value of this field.
    # 
    Tuple_dn_cli = collections.namedtuple("Tuple_dn_cli", ['result'])

    ##
    # This command tunnels a given command through to the manager's Command Line Interface (CLI). The CLI command can be called by only one XML API client at a time. The response to the given CLI command is tunneled back to the client via the notifications channel. To receive the CLI notification, the client must be subscribed to CLI notifications (see Notification Channel)
    # 
    # \param command 128-byte field formatted as a string.<br/>
    #     There is no restriction on the value of this field.
    # 
    # \returns The response to the command, formatted as a #Tuple_dn_cli named tuple.
    # 
    def dn_cli(self, command) :
        res = HartMgrConnectorInternal.send(self, ['cli'], {"command" : command})
        return HartMgrConnector.Tuple_dn_cli(**res)

    ##
    # The named tuple returned by the dn_deactivateFastPipe() function.
    # 
    # - <tt>result</tt>: 32-byte field formatted as a string.<br/>
    #     There is no restriction on the value of this field.
    # 
    Tuple_dn_deactivateFastPipe = collections.namedtuple("Tuple_dn_deactivateFastPipe", ['result'])

    ##
    # Deactivate the fast network pipe to the specified mote.
    # 
    # \param macAddr 25-byte field formatted as a string.<br/>
    #     There is no restriction on the value of this field.
    # 
    # \returns The response to the command, formatted as a #Tuple_dn_deactivateFastPipe named tuple.
    # 
    def dn_deactivateFastPipe(self, macAddr) :
        res = HartMgrConnectorInternal.send(self, ['deactivateFastPipe'], {"macAddr" : macAddr})
        return HartMgrConnector.Tuple_dn_deactivateFastPipe(**res)

    ##
    # Remove a device from the ACL
    # 
    # \param macAddr 25-byte field formatted as a string.<br/>
    #     There is no restriction on the value of this field.
    # 
    # \returns The response to the command.
    # 
    def dn_deleteAcl(self, macAddr) :
        res = HartMgrConnectorInternal.send(self, ['deleteAcl'], {"macAddr" : macAddr})
        return res

    ##
    # Remove a mote from the manager configuration
    # 
    # \param macAddr 25-byte field formatted as a string.<br/>
    #     There is no restriction on the value of this field.
    # 
    # \returns The response to the command.
    # 
    def dn_deleteMote(self, macAddr) :
        res = HartMgrConnectorInternal.send(self, ['deleteMote'], {"macAddr" : macAddr})
        return res

    ##
    # Remove a user
    # 
    # \param userName 16-byte field formatted as a string.<br/>
    #     There is no restriction on the value of this field.
    # 
    # \returns The response to the command.
    # 
    def dn_deleteUser(self, userName) :
        res = HartMgrConnectorInternal.send(self, ['deleteUser'], {"userName" : userName})
        return res

    ##
    # The named tuple returned by the dn_exchangeJoinKey() function.
    # 
    # - <tt>callbackId</tt>: 4-byte field formatted as a int.<br/>
    #     There is no restriction on the value of this field.
    # 
    Tuple_dn_exchangeJoinKey = collections.namedtuple("Tuple_dn_exchangeJoinKey", ['callbackId'])

    ##
    # Exchange the common join key
    # 
    # \param newKey 16-byte field formatted as a hex.<br/>
    #     There is no restriction on the value of this field.
    # 
    # \returns The response to the command, formatted as a #Tuple_dn_exchangeJoinKey named tuple.
    # 
    def dn_exchangeJoinKey(self, newKey) :
        res = HartMgrConnectorInternal.send(self, ['exchangeJoinKey'], {"newKey" : newKey})
        return HartMgrConnector.Tuple_dn_exchangeJoinKey(**res)

    ##
    # The named tuple returned by the dn_exchangeMoteJoinKey() function.
    # 
    # - <tt>callbackId</tt>: 4-byte field formatted as a int.<br/>
    #     There is no restriction on the value of this field.
    # 
    Tuple_dn_exchangeMoteJoinKey = collections.namedtuple("Tuple_dn_exchangeMoteJoinKey", ['callbackId'])

    ##
    # Exchange a mote's join key
    # 
    # \param macAddr 25-byte field formatted as a string.<br/>
    #     There is no restriction on the value of this field.
    # \param newKey 16-byte field formatted as a hex.<br/>
    #     There is no restriction on the value of this field.
    # 
    # \returns The response to the command, formatted as a #Tuple_dn_exchangeMoteJoinKey named tuple.
    # 
    def dn_exchangeMoteJoinKey(self, macAddr, newKey) :
        res = HartMgrConnectorInternal.send(self, ['exchangeMoteJoinKey'], {"macAddr" : macAddr, "newKey" : newKey})
        return HartMgrConnector.Tuple_dn_exchangeMoteJoinKey(**res)

    ##
    # The named tuple returned by the dn_exchangeMoteNetworkId() function.
    # 
    # - <tt>callbackId</tt>: 4-byte field formatted as a int.<br/>
    #     There is no restriction on the value of this field.
    # 
    Tuple_dn_exchangeMoteNetworkId = collections.namedtuple("Tuple_dn_exchangeMoteNetworkId", ['callbackId'])

    ##
    # Exchange the network ID for a mote
    # 
    # \param macAddr 25-byte field formatted as a string.<br/>
    #     There is no restriction on the value of this field.
    # \param newId 4-byte field formatted as a int.<br/>
    #     There is no restriction on the value of this field.
    # 
    # \returns The response to the command, formatted as a #Tuple_dn_exchangeMoteNetworkId named tuple.
    # 
    def dn_exchangeMoteNetworkId(self, macAddr, newId) :
        res = HartMgrConnectorInternal.send(self, ['exchangeMoteNetworkId'], {"macAddr" : macAddr, "newId" : newId})
        return HartMgrConnector.Tuple_dn_exchangeMoteNetworkId(**res)

    ##
    # The named tuple returned by the dn_exchangeNetworkKey() function.
    # 
    # - <tt>callbackId</tt>: 4-byte field formatted as a int.<br/>
    #     There is no restriction on the value of this field.
    # 
    Tuple_dn_exchangeNetworkKey = collections.namedtuple("Tuple_dn_exchangeNetworkKey", ['callbackId'])

    ##
    # Exchange the network key
    # 
    # 
    # 
    # \returns The response to the command, formatted as a #Tuple_dn_exchangeNetworkKey named tuple.
    # 
    def dn_exchangeNetworkKey(self, ) :
        res = HartMgrConnectorInternal.send(self, ['exchangeNetworkKey'], {})
        return HartMgrConnector.Tuple_dn_exchangeNetworkKey(**res)

    ##
    # The named tuple returned by the dn_exchangeNetworkId() function.
    # 
    # - <tt>callbackId</tt>: 4-byte field formatted as a int.<br/>
    #     There is no restriction on the value of this field.
    # 
    Tuple_dn_exchangeNetworkId = collections.namedtuple("Tuple_dn_exchangeNetworkId", ['callbackId'])

    ##
    # Exchange the network ID
    # 
    # \param newId 4-byte field formatted as a int.<br/>
    #     There is no restriction on the value of this field.
    # 
    # \returns The response to the command, formatted as a #Tuple_dn_exchangeNetworkId named tuple.
    # 
    def dn_exchangeNetworkId(self, newId) :
        res = HartMgrConnectorInternal.send(self, ['exchangeNetworkId'], {"newId" : newId})
        return HartMgrConnector.Tuple_dn_exchangeNetworkId(**res)

    ##
    # The named tuple returned by the dn_exchangeSessionKey() function.
    # 
    # - <tt>callbackId</tt>: 4-byte field formatted as a int.<br/>
    #     There is no restriction on the value of this field.
    # 
    Tuple_dn_exchangeSessionKey = collections.namedtuple("Tuple_dn_exchangeSessionKey", ['callbackId'])

    ##
    # Exchange a mote's session key
    # 
    # \param macAddrA 25-byte field formatted as a string.<br/>
    #     There is no restriction on the value of this field.
    # \param macAddrB 25-byte field formatted as a string.<br/>
    #     There is no restriction on the value of this field.
    # 
    # \returns The response to the command, formatted as a #Tuple_dn_exchangeSessionKey named tuple.
    # 
    def dn_exchangeSessionKey(self, macAddrA, macAddrB) :
        res = HartMgrConnectorInternal.send(self, ['exchangeSessionKey'], {"macAddrA" : macAddrA, "macAddrB" : macAddrB})
        return HartMgrConnector.Tuple_dn_exchangeSessionKey(**res)

    ##
    # The named tuple returned by the dn_decommissionDevice() function.
    # 
    # - <tt>result</tt>: 32-byte field formatted as a string.<br/>
    #     There is no restriction on the value of this field.
    # 
    Tuple_dn_decommissionDevice = collections.namedtuple("Tuple_dn_decommissionDevice", ['result'])

    ##
    # Decommission a device in the network
    # 
    # \param macAddr 25-byte field formatted as a string.<br/>
    #     There is no restriction on the value of this field.
    # 
    # \returns The response to the command, formatted as a #Tuple_dn_decommissionDevice named tuple.
    # 
    def dn_decommissionDevice(self, macAddr) :
        res = HartMgrConnectorInternal.send(self, ['decommissionDevice'], {"macAddr" : macAddr})
        return HartMgrConnector.Tuple_dn_decommissionDevice(**res)

    ##
    # The named tuple returned by the dn_getAcl() function.
    # 
    # - <tt>macAddr</tt>: 25-byte field formatted as a string.<br/>
    #     There is no restriction on the value of this field.
    # 
    Tuple_dn_getAcl = collections.namedtuple("Tuple_dn_getAcl", ['macAddr'])

    ##
    # Check whether a device is part of the ACL
    # 
    # \param macAddr 25-byte field formatted as a string.<br/>
    #     There is no restriction on the value of this field.
    # 
    # \returns The response to the command, formatted as a #Tuple_dn_getAcl named tuple.
    # 
    def dn_getAcl(self, macAddr) :
        res = HartMgrConnectorInternal.send(self, ['getAcl'], {"macAddr" : macAddr})
        return HartMgrConnector.Tuple_dn_getAcl(**res)

    ##
    # The named tuple returned by the dn_getAcls() function.
    # 
    # - <tt>macAddr</tt>: 25-byte field formatted as a string.<br/>
    #     There is no restriction on the value of this field.
    # 
    Tuple_dn_getAcls = collections.namedtuple("Tuple_dn_getAcls", ['macAddr'])

    ##
    # Get the list of devices on the ACL
    # 
    # 
    # 
    # \returns The response to the command, formatted as a list of #Tuple_dn_getAcls named tuple.
    # 
    def dn_getAcls(self, ) :
        res = HartMgrConnectorInternal.send(self, ['getAcls'], {})
        tupleList = []
        for r in res :
            tupleList.append(HartMgrConnector.Tuple_dn_getAcls(**r))
        return tupleList

    ##
    # The named tuple returned by the dn_getBlacklist() function.
    # 
    # - <tt>frequency</tt>: 4-byte field formatted as a int.<br/>
    #     There is no restriction on the value of this field.
    # 
    Tuple_dn_getBlacklist = collections.namedtuple("Tuple_dn_getBlacklist", ['frequency'])

    ##
    # Get the channel blacklist. The output is a list of the blacklisted frequency values.
    # 
    # 
    # 
    # \returns The response to the command, formatted as a list of #Tuple_dn_getBlacklist named tuple.
    # 
    def dn_getBlacklist(self, ) :
        res = HartMgrConnectorInternal.send(self, ['getBlacklist'], {})
        tupleList = []
        for r in res :
            tupleList.append(HartMgrConnector.Tuple_dn_getBlacklist(**r))
        return tupleList

    ##
    # The named tuple returned by the dn_getMote() function.
    # 
    # - <tt>moteId</tt>: 4-byte field formatted as a int.<br/>
    #     There is no restriction on the value of this field.
    # - <tt>macAddr</tt>: 25-byte field formatted as a string.<br/>
    #     There is no restriction on the value of this field.
    # - <tt>name</tt>: 16-byte field formatted as a string.<br/>
    #     There is no restriction on the value of this field.
    # - <tt>state</tt>: 16-byte field formatted as a string.<br/>
    #     This field can only take one of the following values:
    #      - Idle: idle
    #      - Lost: lost
    #      - Joining: joining
    #      - Operational: operational
    #      - Disconnecting: disconnecting
    # - <tt>numJoins</tt>: 4-byte field formatted as a int.<br/>
    #     There is no restriction on the value of this field.
    # - <tt>joinTime</tt>: 8-byte field formatted as a int.<br/>
    #     There is no restriction on the value of this field.
    # - <tt>reason</tt>: 16-byte field formatted as a string.<br/>
    #     There is no restriction on the value of this field.
    # - <tt>isAccessPoint</tt>: 1-byte field formatted as a bool.<br/>
    #     There is no restriction on the value of this field.
    # - <tt>powerSource</tt>: 16-byte field formatted as a string.<br/>
    #     There is no restriction on the value of this field.
    # - <tt>dischargeCurrent</tt>: 4-byte field formatted as a int.<br/>
    #     There is no restriction on the value of this field.
    # - <tt>dischargeTime</tt>: 4-byte field formatted as a int.<br/>
    #     There is no restriction on the value of this field.
    # - <tt>recoveryTime</tt>: 4-byte field formatted as a int.<br/>
    #     There is no restriction on the value of this field.
    # - <tt>enableRouting</tt>: 1-byte field formatted as a bool.<br/>
    #     There is no restriction on the value of this field.
    # - <tt>productName</tt>: 16-byte field formatted as a string.<br/>
    #     There is no restriction on the value of this field.
    # - <tt>hwModel</tt>: 1-byte field formatted as a int.<br/>
    #     There is no restriction on the value of this field.
    # - <tt>hwRev</tt>: 1-byte field formatted as a int.<br/>
    #     There is no restriction on the value of this field.
    # - <tt>swRev</tt>: 16-byte field formatted as a string.<br/>
    #     There is no restriction on the value of this field.
    # - <tt>voltage</tt>: 8-byte field formatted as a float.<br/>
    #     There is no restriction on the value of this field.
    # - <tt>numNeighbors</tt>: 4-byte field formatted as a int.<br/>
    #     There is no restriction on the value of this field.
    # - <tt>needNeighbor</tt>: 1-byte field formatted as a bool.<br/>
    #     There is no restriction on the value of this field.
    # - <tt>goodNeighbors</tt>: 4-byte field formatted as a int.<br/>
    #     There is no restriction on the value of this field.
    # - <tt>allocatedPkPeriod</tt>: 4-byte field formatted as a int.<br/>
    #     There is no restriction on the value of this field.
    # - <tt>allocatedPipePkPeriod</tt>: 4-byte field formatted as a int.<br/>
    #     There is no restriction on the value of this field.
    # - <tt>pipeStatus</tt>: 4-byte field formatted as a string.<br/>
    #     This field can only take one of the following values:
    #      - off: off
    #      - pending: Pipe activation pending
    #      - on_bi: Bidirection pipe on
    #      - on_up: Upstream pipe on
    #      - on_down: Downstream pipe on
    # - <tt>advertisingStatus</tt>: 4-byte field formatted as a string.<br/>
    #     This field can only take one of the following values:
    #      - on: on
    #      - off: off
    #      - pending: pending
    # - <tt>locationTag</tt>: 16-byte field formatted as a string.<br/>
    #     This field can only take one of the following values:
    #      - supported: supported
    #      - not supported: not supported
    # 
    Tuple_dn_getMote = collections.namedtuple("Tuple_dn_getMote", ['moteId', 'macAddr', 'name', 'state', 'numJoins', 'joinTime', 'reason', 'isAccessPoint', 'powerSource', 'dischargeCurrent', 'dischargeTime', 'recoveryTime', 'enableRouting', 'productName', 'hwModel', 'hwRev', 'swRev', 'voltage', 'numNeighbors', 'needNeighbor', 'goodNeighbors', 'allocatedPkPeriod', 'allocatedPipePkPeriod', 'pipeStatus', 'advertisingStatus', 'locationTag'])

    ##
    # 
    # 
    # \param macAddr 25-byte field formatted as a string.<br/>
    #     There is no restriction on the value of this field.
    # 
    # \returns The response to the command, formatted as a #Tuple_dn_getMote named tuple.
    # 
    def dn_getMote(self, macAddr) :
        res = HartMgrConnectorInternal.send(self, ['getMote'], {"macAddr" : macAddr})
        return HartMgrConnector.Tuple_dn_getMote(**res)

    ##
    # The named tuple returned by the dn_setMote() function.
    # 
    # - <tt>moteId</tt>: 4-byte field formatted as a int.<br/>
    #     There is no restriction on the value of this field.
    # - <tt>macAddr</tt>: 25-byte field formatted as a string.<br/>
    #     There is no restriction on the value of this field.
    # - <tt>name</tt>: 16-byte field formatted as a string.<br/>
    #     There is no restriction on the value of this field.
    # - <tt>state</tt>: 16-byte field formatted as a string.<br/>
    #     This field can only take one of the following values:
    #      - Idle: idle
    #      - Lost: lost
    #      - Joining: joining
    #      - Operational: operational
    #      - Disconnecting: disconnecting
    # - <tt>numJoins</tt>: 4-byte field formatted as a int.<br/>
    #     There is no restriction on the value of this field.
    # - <tt>joinTime</tt>: 8-byte field formatted as a int.<br/>
    #     There is no restriction on the value of this field.
    # - <tt>reason</tt>: 16-byte field formatted as a string.<br/>
    #     There is no restriction on the value of this field.
    # - <tt>isAccessPoint</tt>: 1-byte field formatted as a bool.<br/>
    #     There is no restriction on the value of this field.
    # - <tt>powerSource</tt>: 16-byte field formatted as a string.<br/>
    #     There is no restriction on the value of this field.
    # - <tt>dischargeCurrent</tt>: 4-byte field formatted as a int.<br/>
    #     There is no restriction on the value of this field.
    # - <tt>dischargeTime</tt>: 4-byte field formatted as a int.<br/>
    #     There is no restriction on the value of this field.
    # - <tt>recoveryTime</tt>: 4-byte field formatted as a int.<br/>
    #     There is no restriction on the value of this field.
    # - <tt>enableRouting</tt>: 1-byte field formatted as a bool.<br/>
    #     There is no restriction on the value of this field.
    # - <tt>productName</tt>: 16-byte field formatted as a string.<br/>
    #     There is no restriction on the value of this field.
    # - <tt>hwModel</tt>: 1-byte field formatted as a int.<br/>
    #     There is no restriction on the value of this field.
    # - <tt>hwRev</tt>: 1-byte field formatted as a int.<br/>
    #     There is no restriction on the value of this field.
    # - <tt>swRev</tt>: 16-byte field formatted as a string.<br/>
    #     There is no restriction on the value of this field.
    # - <tt>voltage</tt>: 8-byte field formatted as a float.<br/>
    #     There is no restriction on the value of this field.
    # - <tt>numNeighbors</tt>: 4-byte field formatted as a int.<br/>
    #     There is no restriction on the value of this field.
    # - <tt>needNeighbor</tt>: 1-byte field formatted as a bool.<br/>
    #     There is no restriction on the value of this field.
    # - <tt>goodNeighbors</tt>: 4-byte field formatted as a int.<br/>
    #     There is no restriction on the value of this field.
    # - <tt>allocatedPkPeriod</tt>: 4-byte field formatted as a int.<br/>
    #     There is no restriction on the value of this field.
    # - <tt>allocatedPipePkPeriod</tt>: 4-byte field formatted as a int.<br/>
    #     There is no restriction on the value of this field.
    # - <tt>pipeStatus</tt>: 4-byte field formatted as a string.<br/>
    #     This field can only take one of the following values:
    #      - off: off
    #      - pending: Pipe activation pending
    #      - on_bi: Bidirection pipe on
    #      - on_up: Upstream pipe on
    #      - on_down: Downstream pipe on
    # - <tt>advertisingStatus</tt>: 4-byte field formatted as a string.<br/>
    #     This field can only take one of the following values:
    #      - on: on
    #      - off: off
    #      - pending: pending
    # - <tt>locationTag</tt>: 16-byte field formatted as a string.<br/>
    #     This field can only take one of the following values:
    #      - supported: supported
    #      - not supported: not supported
    # 
    Tuple_dn_setMote = collections.namedtuple("Tuple_dn_setMote", ['moteId', 'macAddr', 'name', 'state', 'numJoins', 'joinTime', 'reason', 'isAccessPoint', 'powerSource', 'dischargeCurrent', 'dischargeTime', 'recoveryTime', 'enableRouting', 'productName', 'hwModel', 'hwRev', 'swRev', 'voltage', 'numNeighbors', 'needNeighbor', 'goodNeighbors', 'allocatedPkPeriod', 'allocatedPipePkPeriod', 'pipeStatus', 'advertisingStatus', 'locationTag'])

    ##
    # Set mote configuration
    # 
    # \param macAddr 25-byte field formatted as a string.<br/>
    #     There is no restriction on the value of this field.
    # \param name 16-byte field formatted as a string.<br/>
    #     There is no restriction on the value of this field.
    # \param enableRouting 1-byte field formatted as a bool.<br/>
    #     There is no restriction on the value of this field.
    # 
    # \returns The response to the command, formatted as a #Tuple_dn_setMote named tuple.
    # 
    def dn_setMote(self, macAddr, name, enableRouting) :
        res = HartMgrConnectorInternal.send(self, ['setMote'], {"macAddr" : macAddr, "name" : name, "enableRouting" : enableRouting})
        return HartMgrConnector.Tuple_dn_setMote(**res)

    ##
    # The named tuple returned by the dn_getMotes() function.
    # 
    # - <tt>moteId</tt>: 4-byte field formatted as a int.<br/>
    #     There is no restriction on the value of this field.
    # - <tt>macAddr</tt>: 25-byte field formatted as a string.<br/>
    #     There is no restriction on the value of this field.
    # - <tt>name</tt>: 16-byte field formatted as a string.<br/>
    #     There is no restriction on the value of this field.
    # - <tt>state</tt>: 16-byte field formatted as a string.<br/>
    #     This field can only take one of the following values:
    #      - Idle: idle
    #      - Lost: lost
    #      - Joining: joining
    #      - Operational: operational
    #      - Disconnecting: disconnecting
    # - <tt>numJoins</tt>: 4-byte field formatted as a int.<br/>
    #     There is no restriction on the value of this field.
    # - <tt>joinTime</tt>: 8-byte field formatted as a int.<br/>
    #     There is no restriction on the value of this field.
    # - <tt>reason</tt>: 16-byte field formatted as a string.<br/>
    #     There is no restriction on the value of this field.
    # - <tt>isAccessPoint</tt>: 1-byte field formatted as a bool.<br/>
    #     There is no restriction on the value of this field.
    # - <tt>powerSource</tt>: 16-byte field formatted as a string.<br/>
    #     There is no restriction on the value of this field.
    # - <tt>dischargeCurrent</tt>: 4-byte field formatted as a int.<br/>
    #     There is no restriction on the value of this field.
    # - <tt>dischargeTime</tt>: 4-byte field formatted as a int.<br/>
    #     There is no restriction on the value of this field.
    # - <tt>recoveryTime</tt>: 4-byte field formatted as a int.<br/>
    #     There is no restriction on the value of this field.
    # - <tt>enableRouting</tt>: 1-byte field formatted as a bool.<br/>
    #     There is no restriction on the value of this field.
    # - <tt>productName</tt>: 16-byte field formatted as a string.<br/>
    #     There is no restriction on the value of this field.
    # - <tt>hwModel</tt>: 1-byte field formatted as a int.<br/>
    #     There is no restriction on the value of this field.
    # - <tt>hwRev</tt>: 1-byte field formatted as a int.<br/>
    #     There is no restriction on the value of this field.
    # - <tt>swRev</tt>: 16-byte field formatted as a string.<br/>
    #     There is no restriction on the value of this field.
    # - <tt>voltage</tt>: 8-byte field formatted as a float.<br/>
    #     There is no restriction on the value of this field.
    # - <tt>numNeighbors</tt>: 4-byte field formatted as a int.<br/>
    #     There is no restriction on the value of this field.
    # - <tt>needNeighbor</tt>: 1-byte field formatted as a bool.<br/>
    #     There is no restriction on the value of this field.
    # - <tt>goodNeighbors</tt>: 4-byte field formatted as a int.<br/>
    #     There is no restriction on the value of this field.
    # - <tt>allocatedPkPeriod</tt>: 4-byte field formatted as a int.<br/>
    #     There is no restriction on the value of this field.
    # - <tt>allocatedPipePkPeriod</tt>: 4-byte field formatted as a int.<br/>
    #     There is no restriction on the value of this field.
    # - <tt>pipeStatus</tt>: 4-byte field formatted as a string.<br/>
    #     This field can only take one of the following values:
    #      - off: off
    #      - pending: Pipe activation pending
    #      - on_bi: Bidirection pipe on
    #      - on_up: Upstream pipe on
    #      - on_down: Downstream pipe on
    # - <tt>advertisingStatus</tt>: 4-byte field formatted as a string.<br/>
    #     This field can only take one of the following values:
    #      - on: on
    #      - off: off
    #      - pending: pending
    # - <tt>locationTag</tt>: 16-byte field formatted as a string.<br/>
    #     This field can only take one of the following values:
    #      - supported: supported
    #      - not supported: not supported
    # 
    Tuple_dn_getMotes = collections.namedtuple("Tuple_dn_getMotes", ['moteId', 'macAddr', 'name', 'state', 'numJoins', 'joinTime', 'reason', 'isAccessPoint', 'powerSource', 'dischargeCurrent', 'dischargeTime', 'recoveryTime', 'enableRouting', 'productName', 'hwModel', 'hwRev', 'swRev', 'voltage', 'numNeighbors', 'needNeighbor', 'goodNeighbors', 'allocatedPkPeriod', 'allocatedPipePkPeriod', 'pipeStatus', 'advertisingStatus', 'locationTag'])

    ##
    # Get the list of Motes
    # 
    # 
    # 
    # \returns The response to the command, formatted as a list of #Tuple_dn_getMotes named tuple.
    # 
    def dn_getMotes(self, ) :
        res = HartMgrConnectorInternal.send(self, ['getMotes'], {})
        tupleList = []
        for r in res :
            tupleList.append(HartMgrConnector.Tuple_dn_getMotes(**r))
        return tupleList

    ##
    # The named tuple returned by the dn_getMoteStatistics() function.
    # 
    # - <tt>index</tt>: 4-byte field formatted as a int.<br/>
    #     There is no restriction on the value of this field.
    # - <tt>startTime</tt>: 8-byte field formatted as a int.<br/>
    #     There is no restriction on the value of this field.
    # - <tt>avgLatency</tt>: 4-byte field formatted as a int.<br/>
    #     There is no restriction on the value of this field.
    # - <tt>reliability</tt>: 0-byte field formatted as a float.<br/>
    #     There is no restriction on the value of this field.
    # - <tt>numJoins</tt>: 4-byte field formatted as a int.<br/>
    #     There is no restriction on the value of this field.
    # - <tt>voltage</tt>: 4-byte field formatted as a float.<br/>
    #     There is no restriction on the value of this field.
    # - <tt>chargeConsumption</tt>: 4-byte field formatted as a int.<br/>
    #     There is no restriction on the value of this field.
    # - <tt>temperature</tt>: 4-byte field formatted as a float.<br/>
    #     There is no restriction on the value of this field.
    # - <tt>numLostPackets</tt>: 4-byte field formatted as a int.<br/>
    #     There is no restriction on the value of this field.
    # - <tt>latencyToMote</tt>: 4-byte field formatted as a int.<br/>
    #     There is no restriction on the value of this field.
    # 
    Tuple_dn_getMoteStatistics = collections.namedtuple("Tuple_dn_getMoteStatistics", ['index', 'startTime', 'avgLatency', 'reliability', 'numJoins', 'voltage', 'chargeConsumption', 'temperature', 'numLostPackets', 'latencyToMote'])

    ##
    # Get the Mote Statistics
    # 
    # \param macAddr 25-byte field formatted as a string.<br/>
    #     There is no restriction on the value of this field.
    # \param period 32-byte field formatted as a string.<br/>
    #     This field can only take one of the following values:
    #      - current: current
    #      - lifetime: lifetime
    #      - short: short
    #      - long: long
    # \param index 4-byte field formatted as a int.<br/>
    #     There is no restriction on the value of this field.
    # 
    # \returns The response to the command, formatted as a #Tuple_dn_getMoteStatistics named tuple.
    # 
    def dn_getMoteStatistics(self, macAddr, period, index) :
        res = HartMgrConnectorInternal.send(self, ['getMoteStatistics'], {"macAddr" : macAddr, "period" : period, "index" : index})
        return HartMgrConnector.Tuple_dn_getMoteStatistics(**res)

    ##
    # The named tuple returned by the dn_getNetwork() function.
    # 
    # - <tt>netName</tt>: 16-byte field formatted as a string.<br/>
    #     There is no restriction on the value of this field.
    # - <tt>networkId</tt>: 4-byte field formatted as a int.<br/>
    #     There is no restriction on the value of this field.
    # - <tt>maxMotes</tt>: 4-byte field formatted as a int.<br/>
    #     There is no restriction on the value of this field.
    # - <tt>numMotes</tt>: 4-byte field formatted as a int.<br/>
    #     There is no restriction on the value of this field.
    # - <tt>optimizationEnable</tt>: 1-byte field formatted as a bool.<br/>
    #     There is no restriction on the value of this field.
    # - <tt>accessPointPA</tt>: 1-byte field formatted as a bool.<br/>
    #     There is no restriction on the value of this field.
    # - <tt>ccaEnabled</tt>: 1-byte field formatted as a bool.<br/>
    #     There is no restriction on the value of this field.
    # - <tt>requestedBasePkPeriod</tt>: 4-byte field formatted as a int.<br/>
    #     There is no restriction on the value of this field.
    # - <tt>minServicesPkPeriod</tt>: 4-byte field formatted as a int.<br/>
    #     There is no restriction on the value of this field.
    # - <tt>minPipePkPeriod</tt>: 4-byte field formatted as a int.<br/>
    #     There is no restriction on the value of this field.
    # - <tt>bandwidthProfile</tt>: 16-byte field formatted as a string.<br/>
    #     This field can only take one of the following values:
    #      - Manual: manual profile
    #      - P1: normal profile
    #      - P2: low-power profile
    # - <tt>manualUSFrameSize</tt>: 4-byte field formatted as a int.<br/>
    #     There is no restriction on the value of this field.
    # - <tt>manualDSFrameSize</tt>: 4-byte field formatted as a int.<br/>
    #     There is no restriction on the value of this field.
    # - <tt>manualAdvFrameSize</tt>: 4-byte field formatted as a int.<br/>
    #     There is no restriction on the value of this field.
    # - <tt>netQueueSize</tt>: 4-byte field formatted as a int.<br/>
    #     There is no restriction on the value of this field.
    # - <tt>userQueueSize</tt>: 4-byte field formatted as a int.<br/>
    #     There is no restriction on the value of this field.
    # - <tt>locationMode</tt>: 16-byte field formatted as a string.<br/>
    #     This field can only take one of the following values:
    #      - on: on
    #      - off: off
    # - <tt>backboneEnabled</tt>: 1-byte field formatted as a bool.<br/>
    #     There is no restriction on the value of this field.
    # - <tt>backboneSize</tt>: 4-byte field formatted as a int.<br/>
    #     There is no restriction on the value of this field.
    # 
    Tuple_dn_getNetwork = collections.namedtuple("Tuple_dn_getNetwork", ['netName', 'networkId', 'maxMotes', 'numMotes', 'optimizationEnable', 'accessPointPA', 'ccaEnabled', 'requestedBasePkPeriod', 'minServicesPkPeriod', 'minPipePkPeriod', 'bandwidthProfile', 'manualUSFrameSize', 'manualDSFrameSize', 'manualAdvFrameSize', 'netQueueSize', 'userQueueSize', 'locationMode', 'backboneEnabled', 'backboneSize'])

    ##
    # Retrieves network configuration parameters
    # 
    # 
    # 
    # \returns The response to the command, formatted as a #Tuple_dn_getNetwork named tuple.
    # 
    def dn_getNetwork(self, ) :
        res = HartMgrConnectorInternal.send(self, ['getNetwork'], {})
        return HartMgrConnector.Tuple_dn_getNetwork(**res)

    ##
    # The named tuple returned by the dn_getNetworkStatistics() function.
    # 
    # - <tt>index</tt>: 4-byte field formatted as a int.<br/>
    #     There is no restriction on the value of this field.
    # - <tt>startTime</tt>: 8-byte field formatted as a int.<br/>
    #     There is no restriction on the value of this field.
    # - <tt>netLatency</tt>: 4-byte field formatted as a int.<br/>
    #     There is no restriction on the value of this field.
    # - <tt>netReliability</tt>: 0-byte field formatted as a float.<br/>
    #     There is no restriction on the value of this field.
    # - <tt>netPathStability</tt>: 0-byte field formatted as a float.<br/>
    #     There is no restriction on the value of this field.
    # - <tt>lostUpstreamPackets</tt>: 4-byte field formatted as a int.<br/>
    #     There is no restriction on the value of this field.
    # 
    Tuple_dn_getNetworkStatistics = collections.namedtuple("Tuple_dn_getNetworkStatistics", ['index', 'startTime', 'netLatency', 'netReliability', 'netPathStability', 'lostUpstreamPackets'])

    ##
    # Get the Network Statistics
    # 
    # \param period 32-byte field formatted as a string.<br/>
    #     This field can only take one of the following values:
    #      - current: current
    #      - lifetime: lifetime
    #      - short: short
    #      - long: long
    # \param index 4-byte field formatted as a int.<br/>
    #     There is no restriction on the value of this field.
    # 
    # \returns The response to the command, formatted as a #Tuple_dn_getNetworkStatistics named tuple.
    # 
    def dn_getNetworkStatistics(self, period, index) :
        res = HartMgrConnectorInternal.send(self, ['getNetworkStatistics'], {"period" : period, "index" : index})
        return HartMgrConnector.Tuple_dn_getNetworkStatistics(**res)

    ##
    # The named tuple returned by the dn_getOpenAlarms() function.
    # 
    # - <tt>timeStamp</tt>: 4-byte field formatted as a int.<br/>
    #     There is no restriction on the value of this field.
    # - <tt>eventId</tt>: 4-byte field formatted as a int.<br/>
    #     There is no restriction on the value of this field.
    # - <tt>alarmType</tt>: 32-byte field formatted as a string.<br/>
    #     This field can only take one of the following values:
    #      - moteDown: Mote down alarm
    #      - slaReliability: SLA Reliability
    #      - slaLatency: SLA Latency
    #      - slaStability: SLA Stability
    #      - maxMotesReached: Maximum number of motes reached
    #      - bbLatencyWarn: Backbone latency warning
    # - <tt>macAddr</tt>: 25-byte field formatted as a string.<br/>
    #     There is no restriction on the value of this field.
    # 
    Tuple_dn_getOpenAlarms = collections.namedtuple("Tuple_dn_getOpenAlarms", ['timeStamp', 'eventId', 'alarmType', 'macAddr'])

    ##
    # Retrieves a list of the open alarms on the Manager
    # 
    # 
    # 
    # \returns The response to the command, formatted as a list of #Tuple_dn_getOpenAlarms named tuple.
    # 
    def dn_getOpenAlarms(self, ) :
        res = HartMgrConnectorInternal.send(self, ['getOpenAlarms'], {})
        tupleList = []
        for r in res :
            tupleList.append(HartMgrConnector.Tuple_dn_getOpenAlarms(**r))
        return tupleList

    ##
    # The named tuple returned by the dn_getPaths() function.
    # 
    # - <tt>pathId</tt>: 4-byte field formatted as a int.<br/>
    #     There is no restriction on the value of this field.
    # - <tt>moteAMac</tt>: 25-byte field formatted as a string.<br/>
    #     There is no restriction on the value of this field.
    # - <tt>moteBMac</tt>: 25-byte field formatted as a string.<br/>
    #     There is no restriction on the value of this field.
    # - <tt>numLinks</tt>: 4-byte field formatted as a int.<br/>
    #     There is no restriction on the value of this field.
    # - <tt>pathDirection</tt>: 16-byte field formatted as a string.<br/>
    #     This field can only take one of the following values:
    #      - all: all
    #      - upstream: upstream
    #      - downstream: downstream
    #      - unused: unused
    # - <tt>pathQuality</tt>: 0-byte field formatted as a float.<br/>
    #     There is no restriction on the value of this field.
    # 
    Tuple_dn_getPaths = collections.namedtuple("Tuple_dn_getPaths", ['pathId', 'moteAMac', 'moteBMac', 'numLinks', 'pathDirection', 'pathQuality'])

    ##
    # Get the list of Paths to the mote's neighbors
    # 
    # \param moteMac 25-byte field formatted as a string.<br/>
    #     There is no restriction on the value of this field.
    # 
    # \returns The response to the command, formatted as a list of #Tuple_dn_getPaths named tuple.
    # 
    def dn_getPaths(self, moteMac) :
        res = HartMgrConnectorInternal.send(self, ['getPaths'], {"moteMac" : moteMac})
        tupleList = []
        for r in res :
            tupleList.append(HartMgrConnector.Tuple_dn_getPaths(**r))
        return tupleList

    ##
    # The named tuple returned by the dn_getPathStatistics() function.
    # 
    # - <tt>index</tt>: 4-byte field formatted as a int.<br/>
    #     There is no restriction on the value of this field.
    # - <tt>startTime</tt>: 8-byte field formatted as a int.<br/>
    #     There is no restriction on the value of this field.
    # - <tt>baPwr</tt>: 1-byte field formatted as a int.<br/>
    #     There is no restriction on the value of this field.
    # - <tt>abPwr</tt>: 1-byte field formatted as a int.<br/>
    #     There is no restriction on the value of this field.
    # - <tt>stability</tt>: 8-byte field formatted as a float.<br/>
    #     There is no restriction on the value of this field.
    # 
    Tuple_dn_getPathStatistics = collections.namedtuple("Tuple_dn_getPathStatistics", ['index', 'startTime', 'baPwr', 'abPwr', 'stability'])

    ##
    # Get Statistics for a specific Path
    # 
    # \param pathId 4-byte field formatted as a int.<br/>
    #     There is no restriction on the value of this field.
    # \param period 16-byte field formatted as a string.<br/>
    #     This field can only take one of the following values:
    #      - current: current
    #      - lifetime: lifetime
    #      - short: short
    #      - long: long
    # \param index 4-byte field formatted as a int.<br/>
    #     There is no restriction on the value of this field.
    # 
    # \returns The response to the command, formatted as a #Tuple_dn_getPathStatistics named tuple.
    # 
    def dn_getPathStatistics(self, pathId, period, index) :
        res = HartMgrConnectorInternal.send(self, ['getPathStatistics'], {"pathId" : pathId, "period" : period, "index" : index})
        return HartMgrConnector.Tuple_dn_getPathStatistics(**res)

    ##
    # The named tuple returned by the dn_getRedundancy() function.
    # 
    # - <tt>localMode</tt>: 16-byte field formatted as a string.<br/>
    #     This field can only take one of the following values:
    #      - standalone: standalone
    #      - transToMaster: Transitioning to master
    #      - transToSlave: Transitioning to slave
    #      - master: master
    #      - slave: slave
    #      - failed: Manager failed
    # - <tt>peerStatus</tt>: 16-byte field formatted as a string.<br/>
    #     This field can only take one of the following values:
    #      - unknown: unknown
    #      - connected: connected
    #      - synchronized: synchronized
    # - <tt>peerControllerSwRev</tt>: 16-byte field formatted as a string.<br/>
    #     There is no restriction on the value of this field.
    # 
    Tuple_dn_getRedundancy = collections.namedtuple("Tuple_dn_getRedundancy", ['localMode', 'peerStatus', 'peerControllerSwRev'])

    ##
    # Get the redundancy state
    # 
    # 
    # 
    # \returns The response to the command, formatted as a #Tuple_dn_getRedundancy named tuple.
    # 
    def dn_getRedundancy(self, ) :
        res = HartMgrConnectorInternal.send(self, ['getRedundancy'], {})
        return HartMgrConnector.Tuple_dn_getRedundancy(**res)

    ##
    # The named tuple returned by the dn_getSecurity() function.
    # 
    # - <tt>securityMode</tt>: 20-byte field formatted as a string.<br/>
    #     This field can only take one of the following values:
    #      - acceptACL: Accept ACL
    #      - acceptCommonJoinKey: Accept common join key
    # - <tt>acceptHARTDevicesOnly</tt>: 1-byte field formatted as a bool.<br/>
    #     There is no restriction on the value of this field.
    # 
    Tuple_dn_getSecurity = collections.namedtuple("Tuple_dn_getSecurity", ['securityMode', 'acceptHARTDevicesOnly'])

    ##
    # Get the Security configuration
    # 
    # 
    # 
    # \returns The response to the command, formatted as a #Tuple_dn_getSecurity named tuple.
    # 
    def dn_getSecurity(self, ) :
        res = HartMgrConnectorInternal.send(self, ['getSecurity'], {})
        return HartMgrConnector.Tuple_dn_getSecurity(**res)

    ##
    # The named tuple returned by the dn_getSla() function.
    # 
    # - <tt>minNetReliability</tt>: 8-byte field formatted as a float.<br/>
    #     There is no restriction on the value of this field.
    # - <tt>maxNetLatency</tt>: 4-byte field formatted as a int.<br/>
    #     There is no restriction on the value of this field.
    # - <tt>minNetPathStability</tt>: 8-byte field formatted as a float.<br/>
    #     There is no restriction on the value of this field.
    # - <tt>apRdntCoverageThreshold</tt>: 8-byte field formatted as a float.<br/>
    #     There is no restriction on the value of this field.
    # 
    Tuple_dn_getSla = collections.namedtuple("Tuple_dn_getSla", ['minNetReliability', 'maxNetLatency', 'minNetPathStability', 'apRdntCoverageThreshold'])

    ##
    # Get the Service Level Agreement (SLA) configuration
    # 
    # 
    # 
    # \returns The response to the command, formatted as a #Tuple_dn_getSla named tuple.
    # 
    def dn_getSla(self, ) :
        res = HartMgrConnectorInternal.send(self, ['getSla'], {})
        return HartMgrConnector.Tuple_dn_getSla(**res)

    ##
    # The named tuple returned by the dn_getSystem() function.
    # 
    # - <tt>systemName</tt>: 32-byte field formatted as a string.<br/>
    #     There is no restriction on the value of this field.
    # - <tt>location</tt>: 32-byte field formatted as a string.<br/>
    #     There is no restriction on the value of this field.
    # - <tt>swRev</tt>: 32-byte field formatted as a string.<br/>
    #     There is no restriction on the value of this field.
    # - <tt>hwModel</tt>: 32-byte field formatted as a string.<br/>
    #     There is no restriction on the value of this field.
    # - <tt>hwRev</tt>: 32-byte field formatted as a string.<br/>
    #     There is no restriction on the value of this field.
    # - <tt>serialNumber</tt>: 32-byte field formatted as a string.<br/>
    #     There is no restriction on the value of this field.
    # - <tt>time</tt>: 8-byte field formatted as a int.<br/>
    #     There is no restriction on the value of this field.
    # - <tt>startTime</tt>: 8-byte field formatted as a int.<br/>
    #     There is no restriction on the value of this field.
    # - <tt>cliTimeout</tt>: 4-byte field formatted as a int.<br/>
    #     There is no restriction on the value of this field.
    # - <tt>controllerSwRev</tt>: 32-byte field formatted as a string.<br/>
    #     There is no restriction on the value of this field.
    # 
    Tuple_dn_getSystem = collections.namedtuple("Tuple_dn_getSystem", ['systemName', 'location', 'swRev', 'hwModel', 'hwRev', 'serialNumber', 'time', 'startTime', 'cliTimeout', 'controllerSwRev'])

    ##
    # Retrieves system-level information
    # 
    # 
    # 
    # \returns The response to the command, formatted as a #Tuple_dn_getSystem named tuple.
    # 
    def dn_getSystem(self, ) :
        res = HartMgrConnectorInternal.send(self, ['getSystem'], {})
        return HartMgrConnector.Tuple_dn_getSystem(**res)

    ##
    # The named tuple returned by the dn_getUser() function.
    # 
    # - <tt>userName</tt>: 16-byte field formatted as a string.<br/>
    #     There is no restriction on the value of this field.
    # - <tt>privilege</tt>: 16-byte field formatted as a string.<br/>
    #     This field can only take one of the following values:
    #      - viewer: viewer
    #      - user: user
    #      - superuser: superuser
    # 
    Tuple_dn_getUser = collections.namedtuple("Tuple_dn_getUser", ['userName', 'privilege'])

    ##
    # Get the description of a user 
    # 
    # \param userName 16-byte field formatted as a string.<br/>
    #     There is no restriction on the value of this field.
    # 
    # \returns The response to the command, formatted as a #Tuple_dn_getUser named tuple.
    # 
    def dn_getUser(self, userName) :
        res = HartMgrConnectorInternal.send(self, ['getUser'], {"userName" : userName})
        return HartMgrConnector.Tuple_dn_getUser(**res)

    ##
    # The named tuple returned by the dn_getUsers() function.
    # 
    # - <tt>userName</tt>: 16-byte field formatted as a string.<br/>
    #     There is no restriction on the value of this field.
    # - <tt>privilege</tt>: 16-byte field formatted as a string.<br/>
    #     This field can only take one of the following values:
    #      - viewer: viewer
    #      - user: user
    #      - superuser: superuser
    # 
    Tuple_dn_getUsers = collections.namedtuple("Tuple_dn_getUsers", ['userName', 'privilege'])

    ##
    # Get the list of users
    # 
    # 
    # 
    # \returns The response to the command, formatted as a list of #Tuple_dn_getUsers named tuple.
    # 
    def dn_getUsers(self, ) :
        res = HartMgrConnectorInternal.send(self, ['getUsers'], {})
        tupleList = []
        for r in res :
            tupleList.append(HartMgrConnector.Tuple_dn_getUsers(**r))
        return tupleList

    ##
    # The named tuple returned by the dn_getSourceRoute() function.
    # 
    # - <tt>destMacAddr</tt>: 25-byte field formatted as a string.<br/>
    #     There is no restriction on the value of this field.
    # - <tt>primaryPath</tt>: 16-byte field formatted as a list.<br/>
    #     There is no restriction on the value of this field.
    # - <tt>secondaryPath</tt>: 16-byte field formatted as a list.<br/>
    #     There is no restriction on the value of this field.
    # 
    Tuple_dn_getSourceRoute = collections.namedtuple("Tuple_dn_getSourceRoute", ['destMacAddr', 'primaryPath', 'secondaryPath'])

    ##
    # Get the Source Route for a specific Mote
    # 
    # \param destMacAddr 25-byte field formatted as a string.<br/>
    #     There is no restriction on the value of this field.
    # 
    # \returns The response to the command, formatted as a #Tuple_dn_getSourceRoute named tuple.
    # 
    def dn_getSourceRoute(self, destMacAddr) :
        res = HartMgrConnectorInternal.send(self, ['getSourceRoute'], {"destMacAddr" : destMacAddr})
        return HartMgrConnector.Tuple_dn_getSourceRoute(**res)

    ##
    # The named tuple returned by the dn_getLatency() function.
    # 
    # - <tt>downstream</tt>: 4-byte field formatted as a int.<br/>
    #     There is no restriction on the value of this field.
    # - <tt>upstream</tt>: 4-byte field formatted as a int.<br/>
    #     There is no restriction on the value of this field.
    # 
    Tuple_dn_getLatency = collections.namedtuple("Tuple_dn_getLatency", ['downstream', 'upstream'])

    ##
    # Get estimated latency for a mote.
    # 
    # \param macAddr 25-byte field formatted as a string.<br/>
    #     There is no restriction on the value of this field.
    # 
    # \returns The response to the command, formatted as a #Tuple_dn_getLatency named tuple.
    # 
    def dn_getLatency(self, macAddr) :
        res = HartMgrConnectorInternal.send(self, ['getLatency'], {"macAddr" : macAddr})
        return HartMgrConnector.Tuple_dn_getLatency(**res)

    ##
    # The named tuple returned by the dn_getLicense() function.
    # 
    # - <tt>license</tt>: 40-byte field formatted as a string.<br/>
    #     There is no restriction on the value of this field.
    # 
    Tuple_dn_getLicense = collections.namedtuple("Tuple_dn_getLicense", ['license'])

    ##
    # Get the software license key.
    # 
    # 
    # 
    # \returns The response to the command, formatted as a #Tuple_dn_getLicense named tuple.
    # 
    def dn_getLicense(self, ) :
        res = HartMgrConnectorInternal.send(self, ['getLicense'], {})
        return HartMgrConnector.Tuple_dn_getLicense(**res)

    ##
    # The named tuple returned by the dn_getTime() function.
    # 
    # - <tt>utc_time</tt>: 0-byte field formatted as a float.<br/>
    #     There is no restriction on the value of this field.
    # - <tt>asn_time</tt>: 8-byte field formatted as a int.<br/>
    #     There is no restriction on the value of this field.
    # 
    Tuple_dn_getTime = collections.namedtuple("Tuple_dn_getTime", ['utc_time', 'asn_time'])

    ##
    # Get the current time.
    # 
    # 
    # 
    # \returns The response to the command, formatted as a #Tuple_dn_getTime named tuple.
    # 
    def dn_getTime(self, ) :
        res = HartMgrConnectorInternal.send(self, ['getTime'], {})
        return HartMgrConnector.Tuple_dn_getTime(**res)

    ##
    # The named tuple returned by the dn_pingMote() function.
    # 
    # - <tt>callbackId</tt>: 4-byte field formatted as a int.<br/>
    #     There is no restriction on the value of this field.
    # 
    Tuple_dn_pingMote = collections.namedtuple("Tuple_dn_pingMote", ['callbackId'])

    ##
    # Ping the specified mote. A Net Ping Reply event notification will contain the mote's response.
    # 
    # \param macAddr 25-byte field formatted as a string.<br/>
    #     There is no restriction on the value of this field.
    # 
    # \returns The response to the command, formatted as a #Tuple_dn_pingMote named tuple.
    # 
    def dn_pingMote(self, macAddr) :
        res = HartMgrConnectorInternal.send(self, ['pingMote'], {"macAddr" : macAddr})
        return HartMgrConnector.Tuple_dn_pingMote(**res)

    ##
    # The named tuple returned by the dn_promoteToOperational() function.
    # 
    # - <tt>result</tt>: 32-byte field formatted as a string.<br/>
    #     There is no restriction on the value of this field.
    # 
    Tuple_dn_promoteToOperational = collections.namedtuple("Tuple_dn_promoteToOperational", ['result'])

    ##
    # Promote a quarantined device to operational
    # 
    # \param macAddr 25-byte field formatted as a string.<br/>
    #     There is no restriction on the value of this field.
    # 
    # \returns The response to the command, formatted as a #Tuple_dn_promoteToOperational named tuple.
    # 
    def dn_promoteToOperational(self, macAddr) :
        res = HartMgrConnectorInternal.send(self, ['promoteToOperational'], {"macAddr" : macAddr})
        return HartMgrConnector.Tuple_dn_promoteToOperational(**res)

    ##
    # The named tuple returned by the dn_reset() function.
    # 
    # - <tt>result</tt>: 32-byte field formatted as a string.<br/>
    #     There is no restriction on the value of this field.
    # 
    Tuple_dn_reset = collections.namedtuple("Tuple_dn_reset", ['result'])

    ##
    # Reset the system or network
    # 
    # \param object 25-byte field formatted as a string.<br/>
    #     This field can only take one of the following values:
    #      - network: network
    #      - system: system
    #      - stat: statistics
    #      - eventLog: eventLog
    # 
    # \returns The response to the command, formatted as a #Tuple_dn_reset named tuple.
    # 
    def dn_reset(self, object) :
        res = HartMgrConnectorInternal.send(self, ['reset'], {"object" : object})
        return HartMgrConnector.Tuple_dn_reset(**res)

    ##
    # The named tuple returned by the dn_resetWithId() function.
    # 
    # - <tt>result</tt>: 32-byte field formatted as a string.<br/>
    #     There is no restriction on the value of this field.
    # 
    Tuple_dn_resetWithId = collections.namedtuple("Tuple_dn_resetWithId", ['result'])

    ##
    # Reset mote by ID
    # 
    # \param object 25-byte field formatted as a string.<br/>
    #     This field can only take one of the following values:
    #      - mote: mote
    # \param moteId 4-byte field formatted as a int.<br/>
    #     There is no restriction on the value of this field.
    # 
    # \returns The response to the command, formatted as a #Tuple_dn_resetWithId named tuple.
    # 
    def dn_resetWithId(self, object, moteId) :
        res = HartMgrConnectorInternal.send(self, ['resetWithId'], {"object" : object, "moteId" : moteId})
        return HartMgrConnector.Tuple_dn_resetWithId(**res)

    ##
    # The named tuple returned by the dn_resetWithMac() function.
    # 
    # - <tt>result</tt>: 32-byte field formatted as a string.<br/>
    #     There is no restriction on the value of this field.
    # 
    Tuple_dn_resetWithMac = collections.namedtuple("Tuple_dn_resetWithMac", ['result'])

    ##
    # Reset mote by MAC address
    # 
    # \param object 25-byte field formatted as a string.<br/>
    #     This field can only take one of the following values:
    #      - mote: mote
    # \param macAddr 25-byte field formatted as a string.<br/>
    #     There is no restriction on the value of this field.
    # 
    # \returns The response to the command, formatted as a #Tuple_dn_resetWithMac named tuple.
    # 
    def dn_resetWithMac(self, object, macAddr) :
        res = HartMgrConnectorInternal.send(self, ['resetWithMac'], {"object" : object, "macAddr" : macAddr})
        return HartMgrConnector.Tuple_dn_resetWithMac(**res)

    ##
    # The named tuple returned by the dn_sendRequest() function.
    # 
    # - <tt>callbackId</tt>: 4-byte field formatted as a int.<br/>
    #     There is no restriction on the value of this field.
    # 
    Tuple_dn_sendRequest = collections.namedtuple("Tuple_dn_sendRequest", ['callbackId'])

    ##
    # Send downstream (request) data
    # 
    # \param macAddr 25-byte field formatted as a string.<br/>
    #     There is no restriction on the value of this field.
    # \param domain 16-byte field formatted as a string.<br/>
    #     This field can only take one of the following values:
    #      - maintenance: maintenance
    # \param priority 16-byte field formatted as a string.<br/>
    #     This field can only take one of the following values:
    #      - low: low
    #      - high: high
    # \param reliable 0-byte field formatted as a bool.<br/>
    #     There is no restriction on the value of this field.
    # \param data None-byte field formatted as a hex.<br/>
    #     There is no restriction on the value of this field.
    # 
    # \returns The response to the command, formatted as a #Tuple_dn_sendRequest named tuple.
    # 
    def dn_sendRequest(self, macAddr, domain, priority, reliable, data) :
        res = HartMgrConnectorInternal.send(self, ['sendRequest'], {"macAddr" : macAddr, "domain" : domain, "priority" : priority, "reliable" : reliable, "data" : data})
        return HartMgrConnector.Tuple_dn_sendRequest(**res)

    ##
    # The named tuple returned by the dn_sendResponse() function.
    # 
    # - <tt>callbackId</tt>: 4-byte field formatted as a int.<br/>
    #     There is no restriction on the value of this field.
    # 
    Tuple_dn_sendResponse = collections.namedtuple("Tuple_dn_sendResponse", ['callbackId'])

    ##
    # Send downstream data as a response. sendResponse should only be used in special cases.
    # 
    # \param macAddr 25-byte field formatted as a string.<br/>
    #     There is no restriction on the value of this field.
    # \param domain 16-byte field formatted as a string.<br/>
    #     This field can only take one of the following values:
    #      - maintenance: maintenance
    # \param priority 16-byte field formatted as a string.<br/>
    #     This field can only take one of the following values:
    #      - low: low
    #      - high: high
    # \param reliable 0-byte field formatted as a bool.<br/>
    #     There is no restriction on the value of this field.
    # \param callbackId 4-byte field formatted as a int.<br/>
    #     There is no restriction on the value of this field.
    # \param data None-byte field formatted as a hex.<br/>
    #     There is no restriction on the value of this field.
    # 
    # \returns The response to the command, formatted as a #Tuple_dn_sendResponse named tuple.
    # 
    def dn_sendResponse(self, macAddr, domain, priority, reliable, callbackId, data) :
        res = HartMgrConnectorInternal.send(self, ['sendResponse'], {"macAddr" : macAddr, "domain" : domain, "priority" : priority, "reliable" : reliable, "callbackId" : callbackId, "data" : data})
        return HartMgrConnector.Tuple_dn_sendResponse(**res)

    ##
    # The named tuple returned by the dn_setAcl() function.
    # 
    # - <tt>macAddr</tt>: 25-byte field formatted as a string.<br/>
    #     There is no restriction on the value of this field.
    # 
    Tuple_dn_setAcl = collections.namedtuple("Tuple_dn_setAcl", ['macAddr'])

    ##
    # Add or update a device in the ACL
    # 
    # \param macAddr 25-byte field formatted as a string.<br/>
    #     There is no restriction on the value of this field.
    # \param joinKey 16-byte field formatted as a hex.<br/>
    #     There is no restriction on the value of this field.
    # 
    # \returns The response to the command, formatted as a #Tuple_dn_setAcl named tuple.
    # 
    def dn_setAcl(self, macAddr, joinKey) :
        res = HartMgrConnectorInternal.send(self, ['setAcl'], {"macAddr" : macAddr, "joinKey" : joinKey})
        return HartMgrConnector.Tuple_dn_setAcl(**res)

    ##
    # The named tuple returned by the dn_setBlacklist() function.
    # 
    # - <tt>frequency</tt>: 4-byte field formatted as a int.<br/>
    #     There is no restriction on the value of this field.
    # 
    Tuple_dn_setBlacklist = collections.namedtuple("Tuple_dn_setBlacklist", ['frequency'])

    ##
    # Update the channel blacklist. The input is a list of blacklisted frequency values separated by spaces.
    # 
    # \param frequency 64-byte field formatted as a string.<br/>
    #     There is no restriction on the value of this field.
    # 
    # \returns The response to the command, formatted as a list of #Tuple_dn_setBlacklist named tuple.
    # 
    def dn_setBlacklist(self, frequency) :
        res = HartMgrConnectorInternal.send(self, ['setBlacklist'], {"frequency" : frequency})
        tupleList = []
        for r in res :
            tupleList.append(HartMgrConnector.Tuple_dn_setBlacklist(**r))
        return tupleList

    ##
    # The named tuple returned by the dn_setNetwork() function.
    # 
    # - <tt>netName</tt>: 16-byte field formatted as a string.<br/>
    #     There is no restriction on the value of this field.
    # - <tt>networkId</tt>: 4-byte field formatted as a int.<br/>
    #     There is no restriction on the value of this field.
    # - <tt>maxMotes</tt>: 4-byte field formatted as a int.<br/>
    #     There is no restriction on the value of this field.
    # - <tt>optimizationEnable</tt>: 1-byte field formatted as a bool.<br/>
    #     There is no restriction on the value of this field.
    # - <tt>accessPointPA</tt>: 1-byte field formatted as a bool.<br/>
    #     There is no restriction on the value of this field.
    # - <tt>ccaEnabled</tt>: 1-byte field formatted as a bool.<br/>
    #     There is no restriction on the value of this field.
    # - <tt>requestedBasePkPeriod</tt>: 4-byte field formatted as a int.<br/>
    #     There is no restriction on the value of this field.
    # - <tt>minServicesPkPeriod</tt>: 4-byte field formatted as a int.<br/>
    #     There is no restriction on the value of this field.
    # - <tt>minPipePkPeriod</tt>: 4-byte field formatted as a int.<br/>
    #     There is no restriction on the value of this field.
    # - <tt>bandwidthProfile</tt>: 16-byte field formatted as a string.<br/>
    #     This field can only take one of the following values:
    #      - Manual: manual profile
    #      - P1: normal profile
    #      - P2: low-power profile
    # - <tt>manualUSFrameSize</tt>: 4-byte field formatted as a int.<br/>
    #     There is no restriction on the value of this field.
    # - <tt>manualDSFrameSize</tt>: 4-byte field formatted as a int.<br/>
    #     There is no restriction on the value of this field.
    # - <tt>manualAdvFrameSize</tt>: 4-byte field formatted as a int.<br/>
    #     There is no restriction on the value of this field.
    # - <tt>locationMode</tt>: 8-byte field formatted as a string.<br/>
    #     This field can only take one of the following values:
    #      - on: on
    #      - off: off
    # - <tt>backboneEnabled</tt>: 1-byte field formatted as a bool.<br/>
    #     There is no restriction on the value of this field.
    # - <tt>backboneSize</tt>: 4-byte field formatted as a int.<br/>
    #     There is no restriction on the value of this field.
    # 
    Tuple_dn_setNetwork = collections.namedtuple("Tuple_dn_setNetwork", ['netName', 'networkId', 'maxMotes', 'optimizationEnable', 'accessPointPA', 'ccaEnabled', 'requestedBasePkPeriod', 'minServicesPkPeriod', 'minPipePkPeriod', 'bandwidthProfile', 'manualUSFrameSize', 'manualDSFrameSize', 'manualAdvFrameSize', 'locationMode', 'backboneEnabled', 'backboneSize'])

    ##
    # Set network configuration
    # 
    # \param netName 16-byte field formatted as a string.<br/>
    #     There is no restriction on the value of this field.
    # \param networkId 4-byte field formatted as a int.<br/>
    #     There is no restriction on the value of this field.
    # \param maxMotes 4-byte field formatted as a int.<br/>
    #     There is no restriction on the value of this field.
    # \param optimizationEnable 1-byte field formatted as a bool.<br/>
    #     There is no restriction on the value of this field.
    # \param accessPointPA 1-byte field formatted as a bool.<br/>
    #     There is no restriction on the value of this field.
    # \param ccaEnabled 1-byte field formatted as a bool.<br/>
    #     There is no restriction on the value of this field.
    # \param requestedBasePkPeriod 4-byte field formatted as a int.<br/>
    #     There is no restriction on the value of this field.
    # \param minServicesPkPeriod 4-byte field formatted as a int.<br/>
    #     There is no restriction on the value of this field.
    # \param minPipePkPeriod 4-byte field formatted as a int.<br/>
    #     There is no restriction on the value of this field.
    # \param bandwidthProfile 16-byte field formatted as a string.<br/>
    #     This field can only take one of the following values:
    #      - Manual: manual profile
    #      - P1: normal profile
    #      - P2: low-power profile
    # \param manualUSFrameSize 4-byte field formatted as a int.<br/>
    #     There is no restriction on the value of this field.
    # \param manualDSFrameSize 4-byte field formatted as a int.<br/>
    #     There is no restriction on the value of this field.
    # \param manualAdvFrameSize 4-byte field formatted as a int.<br/>
    #     There is no restriction on the value of this field.
    # \param locationMode 8-byte field formatted as a string.<br/>
    #     This field can only take one of the following values:
    #      - on: on
    #      - off: off
    # 
    # \returns The response to the command, formatted as a #Tuple_dn_setNetwork named tuple.
    # 
    def dn_setNetwork(self, netName, networkId, maxMotes, optimizationEnable, accessPointPA, ccaEnabled, requestedBasePkPeriod, minServicesPkPeriod, minPipePkPeriod, bandwidthProfile, manualUSFrameSize, manualDSFrameSize, manualAdvFrameSize, locationMode) :
        res = HartMgrConnectorInternal.send(self, ['setNetwork'], {"netName" : netName, "networkId" : networkId, "maxMotes" : maxMotes, "optimizationEnable" : optimizationEnable, "accessPointPA" : accessPointPA, "ccaEnabled" : ccaEnabled, "requestedBasePkPeriod" : requestedBasePkPeriod, "minServicesPkPeriod" : minServicesPkPeriod, "minPipePkPeriod" : minPipePkPeriod, "bandwidthProfile" : bandwidthProfile, "manualUSFrameSize" : manualUSFrameSize, "manualDSFrameSize" : manualDSFrameSize, "manualAdvFrameSize" : manualAdvFrameSize, "locationMode" : locationMode})
        return HartMgrConnector.Tuple_dn_setNetwork(**res)

    ##
    # The named tuple returned by the dn_setSecurity() function.
    # 
    # - <tt>securityMode</tt>: 20-byte field formatted as a string.<br/>
    #     This field can only take one of the following values:
    #      - acceptACL: Accept ACL
    #      - acceptCommonJoinKey: Accept common join key
    # - <tt>acceptHARTDevicesOnly</tt>: 1-byte field formatted as a bool.<br/>
    #     There is no restriction on the value of this field.
    # 
    Tuple_dn_setSecurity = collections.namedtuple("Tuple_dn_setSecurity", ['securityMode', 'acceptHARTDevicesOnly'])

    ##
    # Set security configuration
    # 
    # \param securityMode 20-byte field formatted as a string.<br/>
    #     This field can only take one of the following values:
    #      - acceptACL: Accept ACL
    #      - acceptCommonJoinKey: Accept common join key
    # \param commonJoinKey 16-byte field formatted as a hex.<br/>
    #     There is no restriction on the value of this field.
    # \param acceptHARTDevicesOnly 1-byte field formatted as a bool.<br/>
    #     There is no restriction on the value of this field.
    # 
    # \returns The response to the command, formatted as a #Tuple_dn_setSecurity named tuple.
    # 
    def dn_setSecurity(self, securityMode, commonJoinKey, acceptHARTDevicesOnly) :
        res = HartMgrConnectorInternal.send(self, ['setSecurity'], {"securityMode" : securityMode, "commonJoinKey" : commonJoinKey, "acceptHARTDevicesOnly" : acceptHARTDevicesOnly})
        return HartMgrConnector.Tuple_dn_setSecurity(**res)

    ##
    # The named tuple returned by the dn_setSla() function.
    # 
    # - <tt>minNetReliability</tt>: 8-byte field formatted as a float.<br/>
    #     There is no restriction on the value of this field.
    # - <tt>maxNetLatency</tt>: 4-byte field formatted as a int.<br/>
    #     There is no restriction on the value of this field.
    # - <tt>minNetPathStability</tt>: 8-byte field formatted as a float.<br/>
    #     There is no restriction on the value of this field.
    # - <tt>apRdntCoverageThreshold</tt>: 8-byte field formatted as a float.<br/>
    #     There is no restriction on the value of this field.
    # 
    Tuple_dn_setSla = collections.namedtuple("Tuple_dn_setSla", ['minNetReliability', 'maxNetLatency', 'minNetPathStability', 'apRdntCoverageThreshold'])

    ##
    # Set SLA configuration
    # 
    # \param minNetReliability 8-byte field formatted as a float.<br/>
    #     There is no restriction on the value of this field.
    # \param maxNetLatency 4-byte field formatted as a int.<br/>
    #     There is no restriction on the value of this field.
    # \param minNetPathStability 8-byte field formatted as a float.<br/>
    #     There is no restriction on the value of this field.
    # \param apRdntCoverageThreshold 8-byte field formatted as a float.<br/>
    #     There is no restriction on the value of this field.
    # 
    # \returns The response to the command, formatted as a #Tuple_dn_setSla named tuple.
    # 
    def dn_setSla(self, minNetReliability, maxNetLatency, minNetPathStability, apRdntCoverageThreshold) :
        res = HartMgrConnectorInternal.send(self, ['setSla'], {"minNetReliability" : minNetReliability, "maxNetLatency" : maxNetLatency, "minNetPathStability" : minNetPathStability, "apRdntCoverageThreshold" : apRdntCoverageThreshold})
        return HartMgrConnector.Tuple_dn_setSla(**res)

    ##
    # The named tuple returned by the dn_setSystem() function.
    # 
    # - <tt>systemName</tt>: 50-byte field formatted as a string.<br/>
    #     There is no restriction on the value of this field.
    # - <tt>location</tt>: 50-byte field formatted as a string.<br/>
    #     There is no restriction on the value of this field.
    # - <tt>cliTimeout</tt>: 4-byte field formatted as a int.<br/>
    #     There is no restriction on the value of this field.
    # 
    Tuple_dn_setSystem = collections.namedtuple("Tuple_dn_setSystem", ['systemName', 'location', 'cliTimeout'])

    ##
    # Set system-level configuration
    # 
    # \param systemName 16-byte field formatted as a string.<br/>
    #     There is no restriction on the value of this field.
    # \param location 16-byte field formatted as a string.<br/>
    #     There is no restriction on the value of this field.
    # \param cliTimeout 4-byte field formatted as a int.<br/>
    #     There is no restriction on the value of this field.
    # 
    # \returns The response to the command, formatted as a #Tuple_dn_setSystem named tuple.
    # 
    def dn_setSystem(self, systemName, location, cliTimeout) :
        res = HartMgrConnectorInternal.send(self, ['setSystem'], {"systemName" : systemName, "location" : location, "cliTimeout" : cliTimeout})
        return HartMgrConnector.Tuple_dn_setSystem(**res)

    ##
    # The named tuple returned by the dn_setUser() function.
    # 
    # - <tt>userName</tt>: 16-byte field formatted as a string.<br/>
    #     There is no restriction on the value of this field.
    # - <tt>privilege</tt>: 16-byte field formatted as a string.<br/>
    #     This field can only take one of the following values:
    #      - viewer: viewer
    #      - user: user
    #      - superuser: superuser
    # 
    Tuple_dn_setUser = collections.namedtuple("Tuple_dn_setUser", ['userName', 'privilege'])

    ##
    # Add or update user configuration
    # 
    # \param userName 16-byte field formatted as a string.<br/>
    #     There is no restriction on the value of this field.
    # \param password 16-byte field formatted as a string.<br/>
    #     There is no restriction on the value of this field.
    # \param privilege 16-byte field formatted as a string.<br/>
    #     This field can only take one of the following values:
    #      - viewer: viewer
    #      - user: user
    #      - superuser: superuser
    # 
    # \returns The response to the command, formatted as a #Tuple_dn_setUser named tuple.
    # 
    def dn_setUser(self, userName, password, privilege) :
        res = HartMgrConnectorInternal.send(self, ['setUser'], {"userName" : userName, "password" : password, "privilege" : privilege})
        return HartMgrConnector.Tuple_dn_setUser(**res)

    ##
    # The named tuple returned by the dn_setLicense() function.
    # 
    # - <tt>result</tt>: 32-byte field formatted as a string.<br/>
    #     There is no restriction on the value of this field.
    # 
    Tuple_dn_setLicense = collections.namedtuple("Tuple_dn_setLicense", ['result'])

    ##
    # Set the software license key.
    # 
    # \param license 40-byte field formatted as a string.<br/>
    #     There is no restriction on the value of this field.
    # 
    # \returns The response to the command, formatted as a #Tuple_dn_setLicense named tuple.
    # 
    def dn_setLicense(self, license) :
        res = HartMgrConnectorInternal.send(self, ['setLicense'], {"license" : license})
        return HartMgrConnector.Tuple_dn_setLicense(**res)

    ##
    # The named tuple returned by the dn_startOtap() function.
    # 
    # - <tt>result</tt>: 32-byte field formatted as a string.<br/>
    #     There is no restriction on the value of this field.
    # 
    Tuple_dn_startOtap = collections.namedtuple("Tuple_dn_startOtap", ['result'])

    ##
    # This command initiates the OTAP (Over-The-Air-Programming) process to upgrade software on motes and the Access Point. By default, the process will retry the OTAP file transmission 100 times.
    # 
    # 
    # 
    # \returns The response to the command, formatted as a #Tuple_dn_startOtap named tuple.
    # 
    def dn_startOtap(self, ) :
        res = HartMgrConnectorInternal.send(self, ['startOtap'], {})
        return HartMgrConnector.Tuple_dn_startOtap(**res)

    ##
    # The named tuple returned by the dn_startOtapWithRetries() function.
    # 
    # - <tt>result</tt>: 32-byte field formatted as a string.<br/>
    #     There is no restriction on the value of this field.
    # 
    Tuple_dn_startOtapWithRetries = collections.namedtuple("Tuple_dn_startOtapWithRetries", ['result'])

    ##
    # This command initiates the OTAP (Over-The-Air-Programming) process to upgrade software for motes and the Access Point, using the specified number of retries.
    # 
    # \param retries 1-byte field formatted as a int.<br/>
    #     There is no restriction on the value of this field.
    # 
    # \returns The response to the command, formatted as a #Tuple_dn_startOtapWithRetries named tuple.
    # 
    def dn_startOtapWithRetries(self, retries) :
        res = HartMgrConnectorInternal.send(self, ['startOtapWithRetries'], {"retries" : retries})
        return HartMgrConnector.Tuple_dn_startOtapWithRetries(**res)

    ##
    # The named tuple returned by the dn_subscribe() function.
    # 
    # - <tt>notif_token</tt>: 32-byte field formatted as a string.<br/>
    #     There is no restriction on the value of this field.
    # 
    Tuple_dn_subscribe = collections.namedtuple("Tuple_dn_subscribe", ['notif_token'])

    ##
    # Subscribe to notifications. This function adds or updates the subscribed notifications to match 'filter'. The filter is a space-separated list of notification types. Valid types include 'data' and 'events'.
    # 
    # \param filter 128-byte field formatted as a string.<br/>
    #     There is no restriction on the value of this field.
    # 
    # \returns The response to the command, formatted as a #Tuple_dn_subscribe named tuple.
    # 
    def dn_subscribe(self, filter) :
        res = HartMgrConnectorInternal.send(self, ['subscribe'], {"filter" : filter})
        return HartMgrConnector.Tuple_dn_subscribe(**res)

    ##
    # The named tuple returned by the dn_unsubscribe() function.
    # 
    # - <tt>result</tt>: 32-byte field formatted as a string.<br/>
    #     There is no restriction on the value of this field.
    # 
    Tuple_dn_unsubscribe = collections.namedtuple("Tuple_dn_unsubscribe", ['result'])

    ##
    # Unsubscribe from notifications. This function clears the existing notification subscription of the client and stops the notification thread. 
    # 
    # 
    # 
    # \returns The response to the command, formatted as a #Tuple_dn_unsubscribe named tuple.
    # 
    def dn_unsubscribe(self, ) :
        res = HartMgrConnectorInternal.send(self, ['unsubscribe'], {})
        return HartMgrConnector.Tuple_dn_unsubscribe(**res)

    #======================== notifications ===================================
    
    ##
    # Dictionary of all notification tuples.
    #
    notifTupleTable = {}
    
    ##
    # \brief USERCONNECT notification.
    # 
    # 
    #
    # Formatted as a Tuple_UserConnect named tuple. It contains the following fields:
    #   - <tt>timeStamp</tt> 8-byte field formatted as a int.<br/>
    #     There is no restriction on the value of this field.
    #   - <tt>eventId</tt> 4-byte field formatted as a int.<br/>
    #     There is no restriction on the value of this field.
    #   - <tt>channel</tt> 16-byte field formatted as a string.<br/>
    #     This field can only take one of the following values:
    #      - cli: Manager CLI
    #      - config: API control
    #      - notif: API notifications
    #   - <tt>ipAddr</tt> 16-byte field formatted as a string.<br/>
    #     There is no restriction on the value of this field.
    #   - <tt>userName</tt> 32-byte field formatted as a string.<br/>
    #     There is no restriction on the value of this field.    
    # 
    USERCONNECT = "UserConnect"
    notifTupleTable[USERCONNECT] = Tuple_UserConnect = collections.namedtuple("Tuple_UserConnect", ['timeStamp', 'eventId', 'channel', 'ipAddr', 'userName'])

    ##
    # \brief USERDISCONNECT notification.
    # 
    # 
    #
    # Formatted as a Tuple_UserDisconnect named tuple. It contains the following fields:
    #   - <tt>timeStamp</tt> 8-byte field formatted as a int.<br/>
    #     There is no restriction on the value of this field.
    #   - <tt>eventId</tt> 4-byte field formatted as a int.<br/>
    #     There is no restriction on the value of this field.
    #   - <tt>channel</tt> 16-byte field formatted as a string.<br/>
    #     This field can only take one of the following values:
    #      - cli: Manager CLI
    #      - config: API control
    #      - notif: API notifications
    #   - <tt>ipAddr</tt> 16-byte field formatted as a string.<br/>
    #     There is no restriction on the value of this field.
    #   - <tt>userName</tt> 32-byte field formatted as a string.<br/>
    #     There is no restriction on the value of this field.    
    # 
    USERDISCONNECT = "UserDisconnect"
    notifTupleTable[USERDISCONNECT] = Tuple_UserDisconnect = collections.namedtuple("Tuple_UserDisconnect", ['timeStamp', 'eventId', 'channel', 'ipAddr', 'userName'])

    ##
    # \brief MANUALMOTERESET notification.
    # 
    # 
    #
    # Formatted as a Tuple_ManualMoteReset named tuple. It contains the following fields:
    #   - <tt>timeStamp</tt> 8-byte field formatted as a int.<br/>
    #     There is no restriction on the value of this field.
    #   - <tt>eventId</tt> 4-byte field formatted as a int.<br/>
    #     There is no restriction on the value of this field.
    #   - <tt>userName</tt> 32-byte field formatted as a string.<br/>
    #     There is no restriction on the value of this field.
    #   - <tt>moteId</tt> 4-byte field formatted as a int.<br/>
    #     There is no restriction on the value of this field.
    #   - <tt>macAddr</tt> 32-byte field formatted as a string.<br/>
    #     There is no restriction on the value of this field.    
    # 
    MANUALMOTERESET = "ManualMoteReset"
    notifTupleTable[MANUALMOTERESET] = Tuple_ManualMoteReset = collections.namedtuple("Tuple_ManualMoteReset", ['timeStamp', 'eventId', 'userName', 'moteId', 'macAddr'])

    ##
    # \brief MANUALMOTEDELETE notification.
    # 
    # 
    #
    # Formatted as a Tuple_ManualMoteDelete named tuple. It contains the following fields:
    #   - <tt>timeStamp</tt> 8-byte field formatted as a int.<br/>
    #     There is no restriction on the value of this field.
    #   - <tt>eventId</tt> 4-byte field formatted as a int.<br/>
    #     There is no restriction on the value of this field.
    #   - <tt>userName</tt> 32-byte field formatted as a string.<br/>
    #     There is no restriction on the value of this field.
    #   - <tt>moteId</tt> 4-byte field formatted as a int.<br/>
    #     There is no restriction on the value of this field.
    #   - <tt>macAddr</tt> 32-byte field formatted as a string.<br/>
    #     There is no restriction on the value of this field.    
    # 
    MANUALMOTEDELETE = "ManualMoteDelete"
    notifTupleTable[MANUALMOTEDELETE] = Tuple_ManualMoteDelete = collections.namedtuple("Tuple_ManualMoteDelete", ['timeStamp', 'eventId', 'userName', 'moteId', 'macAddr'])

    ##
    # \brief MANUALMOTEDECOMMISSION notification.
    # 
    # 
    #
    # Formatted as a Tuple_ManualMoteDecommission named tuple. It contains the following fields:
    #   - <tt>timeStamp</tt> 8-byte field formatted as a int.<br/>
    #     There is no restriction on the value of this field.
    #   - <tt>eventId</tt> 4-byte field formatted as a int.<br/>
    #     There is no restriction on the value of this field.
    #   - <tt>userName</tt> 32-byte field formatted as a string.<br/>
    #     There is no restriction on the value of this field.
    #   - <tt>moteId</tt> 4-byte field formatted as a int.<br/>
    #     There is no restriction on the value of this field.
    #   - <tt>macAddr</tt> 32-byte field formatted as a string.<br/>
    #     There is no restriction on the value of this field.    
    # 
    MANUALMOTEDECOMMISSION = "ManualMoteDecommission"
    notifTupleTable[MANUALMOTEDECOMMISSION] = Tuple_ManualMoteDecommission = collections.namedtuple("Tuple_ManualMoteDecommission", ['timeStamp', 'eventId', 'userName', 'moteId', 'macAddr'])

    ##
    # \brief MANUALNETRESET notification.
    # 
    # 
    #
    # Formatted as a Tuple_ManualNetReset named tuple. It contains the following fields:
    #   - <tt>timeStamp</tt> 8-byte field formatted as a int.<br/>
    #     There is no restriction on the value of this field.
    #   - <tt>eventId</tt> 4-byte field formatted as a int.<br/>
    #     There is no restriction on the value of this field.
    #   - <tt>userName</tt> 32-byte field formatted as a string.<br/>
    #     There is no restriction on the value of this field.    
    # 
    MANUALNETRESET = "ManualNetReset"
    notifTupleTable[MANUALNETRESET] = Tuple_ManualNetReset = collections.namedtuple("Tuple_ManualNetReset", ['timeStamp', 'eventId', 'userName'])

    ##
    # \brief MANUALDCCRESET notification.
    # 
    # 
    #
    # Formatted as a Tuple_ManualDccReset named tuple. It contains the following fields:
    #   - <tt>timeStamp</tt> 8-byte field formatted as a int.<br/>
    #     There is no restriction on the value of this field.
    #   - <tt>eventId</tt> 4-byte field formatted as a int.<br/>
    #     There is no restriction on the value of this field.
    #   - <tt>userName</tt> 32-byte field formatted as a string.<br/>
    #     There is no restriction on the value of this field.    
    # 
    MANUALDCCRESET = "ManualDccReset"
    notifTupleTable[MANUALDCCRESET] = Tuple_ManualDccReset = collections.namedtuple("Tuple_ManualDccReset", ['timeStamp', 'eventId', 'userName'])

    ##
    # \brief MANUALSTATRESET notification.
    # 
    # 
    #
    # Formatted as a Tuple_ManualStatReset named tuple. It contains the following fields:
    #   - <tt>timeStamp</tt> 8-byte field formatted as a int.<br/>
    #     There is no restriction on the value of this field.
    #   - <tt>eventId</tt> 4-byte field formatted as a int.<br/>
    #     There is no restriction on the value of this field.
    #   - <tt>userName</tt> 32-byte field formatted as a string.<br/>
    #     There is no restriction on the value of this field.    
    # 
    MANUALSTATRESET = "ManualStatReset"
    notifTupleTable[MANUALSTATRESET] = Tuple_ManualStatReset = collections.namedtuple("Tuple_ManualStatReset", ['timeStamp', 'eventId', 'userName'])

    ##
    # \brief CONFIGCHANGE notification.
    # 
    # 
    #
    # Formatted as a Tuple_ConfigChange named tuple. It contains the following fields:
    #   - <tt>timeStamp</tt> 8-byte field formatted as a int.<br/>
    #     There is no restriction on the value of this field.
    #   - <tt>eventId</tt> 4-byte field formatted as a int.<br/>
    #     There is no restriction on the value of this field.
    #   - <tt>userName</tt> 32-byte field formatted as a string.<br/>
    #     There is no restriction on the value of this field.
    #   - <tt>objectType</tt> 32-byte field formatted as a string.<br/>
    #     There is no restriction on the value of this field.
    #   - <tt>objectId</tt> 32-byte field formatted as a string.<br/>
    #     There is no restriction on the value of this field.    
    # 
    CONFIGCHANGE = "ConfigChange"
    notifTupleTable[CONFIGCHANGE] = Tuple_ConfigChange = collections.namedtuple("Tuple_ConfigChange", ['timeStamp', 'eventId', 'userName', 'objectType', 'objectId'])

    ##
    # \brief BOOTUP notification.
    # 
    # 
    #
    # Formatted as a Tuple_BootUp named tuple. It contains the following fields:
    #   - <tt>timeStamp</tt> 8-byte field formatted as a int.<br/>
    #     There is no restriction on the value of this field.
    #   - <tt>eventId</tt> 4-byte field formatted as a int.<br/>
    #     There is no restriction on the value of this field.    
    # 
    BOOTUP = "BootUp"
    notifTupleTable[BOOTUP] = Tuple_BootUp = collections.namedtuple("Tuple_BootUp", ['timeStamp', 'eventId'])

    ##
    # \brief NETWORKRESET notification.
    # 
    # 
    #
    # Formatted as a Tuple_NetworkReset named tuple. It contains the following fields:
    #   - <tt>timeStamp</tt> 8-byte field formatted as a int.<br/>
    #     There is no restriction on the value of this field.
    #   - <tt>eventId</tt> 4-byte field formatted as a int.<br/>
    #     There is no restriction on the value of this field.    
    # 
    NETWORKRESET = "NetworkReset"
    notifTupleTable[NETWORKRESET] = Tuple_NetworkReset = collections.namedtuple("Tuple_NetworkReset", ['timeStamp', 'eventId'])

    ##
    # \brief COMMANDFINISHED notification.
    # 
    # 
    #
    # Formatted as a Tuple_CommandFinished named tuple. It contains the following fields:
    #   - <tt>timeStamp</tt> 8-byte field formatted as a int.<br/>
    #     There is no restriction on the value of this field.
    #   - <tt>eventId</tt> 4-byte field formatted as a int.<br/>
    #     There is no restriction on the value of this field.
    #   - <tt>callbackId</tt> 4-byte field formatted as a int.<br/>
    #     There is no restriction on the value of this field.
    #   - <tt>objectType</tt> 32-byte field formatted as a string.<br/>
    #     There is no restriction on the value of this field.
    #   - <tt>macAddr</tt> 32-byte field formatted as a string.<br/>
    #     There is no restriction on the value of this field.
    #   - <tt>resultCode</tt> 4-byte field formatted as a int.<br/>
    #     There is no restriction on the value of this field.    
    # 
    COMMANDFINISHED = "CommandFinished"
    notifTupleTable[COMMANDFINISHED] = Tuple_CommandFinished = collections.namedtuple("Tuple_CommandFinished", ['timeStamp', 'eventId', 'callbackId', 'objectType', 'macAddr', 'resultCode'])

    ##
    # \brief PACKETSENT notification.
    # 
    # 
    #
    # Formatted as a Tuple_PacketSent named tuple. It contains the following fields:
    #   - <tt>timeStamp</tt> 8-byte field formatted as a int.<br/>
    #     There is no restriction on the value of this field.
    #   - <tt>eventId</tt> 4-byte field formatted as a int.<br/>
    #     There is no restriction on the value of this field.
    #   - <tt>callbackId</tt> 4-byte field formatted as a int.<br/>
    #     There is no restriction on the value of this field.
    #   - <tt>macAddr</tt> 32-byte field formatted as a string.<br/>
    #     There is no restriction on the value of this field.    
    # 
    PACKETSENT = "PacketSent"
    notifTupleTable[PACKETSENT] = Tuple_PacketSent = collections.namedtuple("Tuple_PacketSent", ['timeStamp', 'eventId', 'callbackId', 'macAddr'])

    ##
    # \brief MOTEJOIN notification.
    # 
    # 
    #
    # Formatted as a Tuple_MoteJoin named tuple. It contains the following fields:
    #   - <tt>timeStamp</tt> 8-byte field formatted as a int.<br/>
    #     There is no restriction on the value of this field.
    #   - <tt>eventId</tt> 4-byte field formatted as a int.<br/>
    #     There is no restriction on the value of this field.
    #   - <tt>moteId</tt> 4-byte field formatted as a int.<br/>
    #     There is no restriction on the value of this field.
    #   - <tt>macAddr</tt> 32-byte field formatted as a string.<br/>
    #     There is no restriction on the value of this field.
    #   - <tt>reason</tt> 64-byte field formatted as a string.<br/>
    #     There is no restriction on the value of this field.
    #   - <tt>userData</tt> 64-byte field formatted as a string.<br/>
    #     There is no restriction on the value of this field.    
    # 
    MOTEJOIN = "MoteJoin"
    notifTupleTable[MOTEJOIN] = Tuple_MoteJoin = collections.namedtuple("Tuple_MoteJoin", ['timeStamp', 'eventId', 'moteId', 'macAddr', 'reason', 'userData'])

    ##
    # \brief MOTELIVE notification.
    # 
    # 
    #
    # Formatted as a Tuple_MoteLive named tuple. It contains the following fields:
    #   - <tt>timeStamp</tt> 8-byte field formatted as a int.<br/>
    #     There is no restriction on the value of this field.
    #   - <tt>eventId</tt> 4-byte field formatted as a int.<br/>
    #     There is no restriction on the value of this field.
    #   - <tt>moteId</tt> 4-byte field formatted as a int.<br/>
    #     There is no restriction on the value of this field.
    #   - <tt>macAddr</tt> 32-byte field formatted as a string.<br/>
    #     There is no restriction on the value of this field.
    #   - <tt>reason</tt> 64-byte field formatted as a string.<br/>
    #     There is no restriction on the value of this field.    
    # 
    MOTELIVE = "MoteLive"
    notifTupleTable[MOTELIVE] = Tuple_MoteLive = collections.namedtuple("Tuple_MoteLive", ['timeStamp', 'eventId', 'moteId', 'macAddr', 'reason'])

    ##
    # \brief MOTEQUARANTINE notification.
    # 
    # 
    #
    # Formatted as a Tuple_MoteQuarantine named tuple. It contains the following fields:
    #   - <tt>timeStamp</tt> 8-byte field formatted as a int.<br/>
    #     There is no restriction on the value of this field.
    #   - <tt>eventId</tt> 4-byte field formatted as a int.<br/>
    #     There is no restriction on the value of this field.
    #   - <tt>moteId</tt> 4-byte field formatted as a int.<br/>
    #     There is no restriction on the value of this field.
    #   - <tt>macAddr</tt> 32-byte field formatted as a string.<br/>
    #     There is no restriction on the value of this field.
    #   - <tt>reason</tt> 64-byte field formatted as a string.<br/>
    #     There is no restriction on the value of this field.    
    # 
    MOTEQUARANTINE = "MoteQuarantine"
    notifTupleTable[MOTEQUARANTINE] = Tuple_MoteQuarantine = collections.namedtuple("Tuple_MoteQuarantine", ['timeStamp', 'eventId', 'moteId', 'macAddr', 'reason'])

    ##
    # \brief MOTEJOINQUARANTINE notification.
    # 
    # 
    #
    # Formatted as a Tuple_MoteJoinQuarantine named tuple. It contains the following fields:
    #   - <tt>timeStamp</tt> 8-byte field formatted as a int.<br/>
    #     There is no restriction on the value of this field.
    #   - <tt>eventId</tt> 4-byte field formatted as a int.<br/>
    #     There is no restriction on the value of this field.
    #   - <tt>moteId</tt> 4-byte field formatted as a int.<br/>
    #     There is no restriction on the value of this field.
    #   - <tt>macAddr</tt> 32-byte field formatted as a string.<br/>
    #     There is no restriction on the value of this field.
    #   - <tt>reason</tt> 64-byte field formatted as a string.<br/>
    #     There is no restriction on the value of this field.
    #   - <tt>userData</tt> 64-byte field formatted as a string.<br/>
    #     There is no restriction on the value of this field.    
    # 
    MOTEJOINQUARANTINE = "MoteJoinQuarantine"
    notifTupleTable[MOTEJOINQUARANTINE] = Tuple_MoteJoinQuarantine = collections.namedtuple("Tuple_MoteJoinQuarantine", ['timeStamp', 'eventId', 'moteId', 'macAddr', 'reason', 'userData'])

    ##
    # \brief MOTEUNKNOWN notification.
    # 
    # 
    #
    # Formatted as a Tuple_MoteUnknown named tuple. It contains the following fields:
    #   - <tt>timeStamp</tt> 8-byte field formatted as a int.<br/>
    #     There is no restriction on the value of this field.
    #   - <tt>eventId</tt> 4-byte field formatted as a int.<br/>
    #     There is no restriction on the value of this field.
    #   - <tt>moteId</tt> 4-byte field formatted as a int.<br/>
    #     There is no restriction on the value of this field.
    #   - <tt>macAddr</tt> 32-byte field formatted as a string.<br/>
    #     There is no restriction on the value of this field.
    #   - <tt>reason</tt> 64-byte field formatted as a string.<br/>
    #     There is no restriction on the value of this field.    
    # 
    MOTEUNKNOWN = "MoteUnknown"
    notifTupleTable[MOTEUNKNOWN] = Tuple_MoteUnknown = collections.namedtuple("Tuple_MoteUnknown", ['timeStamp', 'eventId', 'moteId', 'macAddr', 'reason'])

    ##
    # \brief MOTEDISCONNECT notification.
    # 
    # 
    #
    # Formatted as a Tuple_MoteDisconnect named tuple. It contains the following fields:
    #   - <tt>timeStamp</tt> 8-byte field formatted as a int.<br/>
    #     There is no restriction on the value of this field.
    #   - <tt>eventId</tt> 4-byte field formatted as a int.<br/>
    #     There is no restriction on the value of this field.
    #   - <tt>moteId</tt> 4-byte field formatted as a int.<br/>
    #     There is no restriction on the value of this field.
    #   - <tt>macAddr</tt> 32-byte field formatted as a string.<br/>
    #     There is no restriction on the value of this field.
    #   - <tt>reason</tt> 64-byte field formatted as a string.<br/>
    #     There is no restriction on the value of this field.    
    # 
    MOTEDISCONNECT = "MoteDisconnect"
    notifTupleTable[MOTEDISCONNECT] = Tuple_MoteDisconnect = collections.namedtuple("Tuple_MoteDisconnect", ['timeStamp', 'eventId', 'moteId', 'macAddr', 'reason'])

    ##
    # \brief MOTEJOINFAILURE notification.
    # 
    # 
    #
    # Formatted as a Tuple_MoteJoinFailure named tuple. It contains the following fields:
    #   - <tt>timeStamp</tt> 8-byte field formatted as a int.<br/>
    #     There is no restriction on the value of this field.
    #   - <tt>eventId</tt> 4-byte field formatted as a int.<br/>
    #     There is no restriction on the value of this field.
    #   - <tt>macAddr</tt> 32-byte field formatted as a string.<br/>
    #     There is no restriction on the value of this field.
    #   - <tt>reason</tt> 64-byte field formatted as a string.<br/>
    #     There is no restriction on the value of this field.    
    # 
    MOTEJOINFAILURE = "MoteJoinFailure"
    notifTupleTable[MOTEJOINFAILURE] = Tuple_MoteJoinFailure = collections.namedtuple("Tuple_MoteJoinFailure", ['timeStamp', 'eventId', 'macAddr', 'reason'])

    ##
    # \brief INVALIDMIC notification.
    # 
    # 
    #
    # Formatted as a Tuple_InvalidMIC named tuple. It contains the following fields:
    #   - <tt>timeStamp</tt> 8-byte field formatted as a int.<br/>
    #     There is no restriction on the value of this field.
    #   - <tt>eventId</tt> 4-byte field formatted as a int.<br/>
    #     There is no restriction on the value of this field.
    #   - <tt>macAddr</tt> 32-byte field formatted as a string.<br/>
    #     There is no restriction on the value of this field.    
    # 
    INVALIDMIC = "InvalidMIC"
    notifTupleTable[INVALIDMIC] = Tuple_InvalidMIC = collections.namedtuple("Tuple_InvalidMIC", ['timeStamp', 'eventId', 'macAddr'])

    ##
    # \brief PATHCREATE notification.
    # 
    # 
    #
    # Formatted as a Tuple_PathCreate named tuple. It contains the following fields:
    #   - <tt>timeStamp</tt> 8-byte field formatted as a int.<br/>
    #     There is no restriction on the value of this field.
    #   - <tt>eventId</tt> 4-byte field formatted as a int.<br/>
    #     There is no restriction on the value of this field.
    #   - <tt>pathId</tt> 4-byte field formatted as a int.<br/>
    #     There is no restriction on the value of this field.
    #   - <tt>moteAMac</tt> 32-byte field formatted as a string.<br/>
    #     There is no restriction on the value of this field.
    #   - <tt>moteBMac</tt> 32-byte field formatted as a string.<br/>
    #     There is no restriction on the value of this field.    
    # 
    PATHCREATE = "PathCreate"
    notifTupleTable[PATHCREATE] = Tuple_PathCreate = collections.namedtuple("Tuple_PathCreate", ['timeStamp', 'eventId', 'pathId', 'moteAMac', 'moteBMac'])

    ##
    # \brief PATHDELETE notification.
    # 
    # 
    #
    # Formatted as a Tuple_PathDelete named tuple. It contains the following fields:
    #   - <tt>timeStamp</tt> 8-byte field formatted as a int.<br/>
    #     There is no restriction on the value of this field.
    #   - <tt>eventId</tt> 4-byte field formatted as a int.<br/>
    #     There is no restriction on the value of this field.
    #   - <tt>pathId</tt> 4-byte field formatted as a int.<br/>
    #     There is no restriction on the value of this field.
    #   - <tt>moteAMac</tt> 32-byte field formatted as a string.<br/>
    #     There is no restriction on the value of this field.
    #   - <tt>moteBMac</tt> 32-byte field formatted as a string.<br/>
    #     There is no restriction on the value of this field.    
    # 
    PATHDELETE = "PathDelete"
    notifTupleTable[PATHDELETE] = Tuple_PathDelete = collections.namedtuple("Tuple_PathDelete", ['timeStamp', 'eventId', 'pathId', 'moteAMac', 'moteBMac'])

    ##
    # \brief PATHACTIVATE notification.
    # 
    # 
    #
    # Formatted as a Tuple_PathActivate named tuple. It contains the following fields:
    #   - <tt>timeStamp</tt> 8-byte field formatted as a int.<br/>
    #     There is no restriction on the value of this field.
    #   - <tt>eventId</tt> 4-byte field formatted as a int.<br/>
    #     There is no restriction on the value of this field.
    #   - <tt>pathId</tt> 4-byte field formatted as a int.<br/>
    #     There is no restriction on the value of this field.
    #   - <tt>moteAMac</tt> 32-byte field formatted as a string.<br/>
    #     There is no restriction on the value of this field.
    #   - <tt>moteBMac</tt> 32-byte field formatted as a string.<br/>
    #     There is no restriction on the value of this field.    
    # 
    PATHACTIVATE = "PathActivate"
    notifTupleTable[PATHACTIVATE] = Tuple_PathActivate = collections.namedtuple("Tuple_PathActivate", ['timeStamp', 'eventId', 'pathId', 'moteAMac', 'moteBMac'])

    ##
    # \brief PATHDEACTIVATE notification.
    # 
    # 
    #
    # Formatted as a Tuple_PathDeactivate named tuple. It contains the following fields:
    #   - <tt>timeStamp</tt> 8-byte field formatted as a int.<br/>
    #     There is no restriction on the value of this field.
    #   - <tt>eventId</tt> 4-byte field formatted as a int.<br/>
    #     There is no restriction on the value of this field.
    #   - <tt>pathId</tt> 4-byte field formatted as a int.<br/>
    #     There is no restriction on the value of this field.
    #   - <tt>moteAMac</tt> 32-byte field formatted as a string.<br/>
    #     There is no restriction on the value of this field.
    #   - <tt>moteBMac</tt> 32-byte field formatted as a string.<br/>
    #     There is no restriction on the value of this field.    
    # 
    PATHDEACTIVATE = "PathDeactivate"
    notifTupleTable[PATHDEACTIVATE] = Tuple_PathDeactivate = collections.namedtuple("Tuple_PathDeactivate", ['timeStamp', 'eventId', 'pathId', 'moteAMac', 'moteBMac'])

    ##
    # \brief PATHALERT notification.
    # 
    # 
    #
    # Formatted as a Tuple_PathAlert named tuple. It contains the following fields:
    #   - <tt>timeStamp</tt> 8-byte field formatted as a int.<br/>
    #     There is no restriction on the value of this field.
    #   - <tt>eventId</tt> 4-byte field formatted as a int.<br/>
    #     There is no restriction on the value of this field.
    #   - <tt>pathId</tt> 4-byte field formatted as a int.<br/>
    #     There is no restriction on the value of this field.
    #   - <tt>moteAMac</tt> 32-byte field formatted as a string.<br/>
    #     There is no restriction on the value of this field.
    #   - <tt>moteBMac</tt> 32-byte field formatted as a string.<br/>
    #     There is no restriction on the value of this field.    
    # 
    PATHALERT = "PathAlert"
    notifTupleTable[PATHALERT] = Tuple_PathAlert = collections.namedtuple("Tuple_PathAlert", ['timeStamp', 'eventId', 'pathId', 'moteAMac', 'moteBMac'])

    ##
    # \brief PIPEON notification.
    # 
    # 
    #
    # Formatted as a Tuple_PipeOn named tuple. It contains the following fields:
    #   - <tt>timeStamp</tt> 8-byte field formatted as a int.<br/>
    #     There is no restriction on the value of this field.
    #   - <tt>eventId</tt> 4-byte field formatted as a int.<br/>
    #     There is no restriction on the value of this field.
    #   - <tt>macAddr</tt> 32-byte field formatted as a string.<br/>
    #     There is no restriction on the value of this field.
    #   - <tt>allocatedPipePkPeriod</tt> 4-byte field formatted as a int.<br/>
    #     There is no restriction on the value of this field.    
    # 
    PIPEON = "PipeOn"
    notifTupleTable[PIPEON] = Tuple_PipeOn = collections.namedtuple("Tuple_PipeOn", ['timeStamp', 'eventId', 'macAddr', 'allocatedPipePkPeriod'])

    ##
    # \brief PIPEOFF notification.
    # 
    # 
    #
    # Formatted as a Tuple_PipeOff named tuple. It contains the following fields:
    #   - <tt>timeStamp</tt> 8-byte field formatted as a int.<br/>
    #     There is no restriction on the value of this field.
    #   - <tt>eventId</tt> 4-byte field formatted as a int.<br/>
    #     There is no restriction on the value of this field.
    #   - <tt>macAddr</tt> 32-byte field formatted as a string.<br/>
    #     There is no restriction on the value of this field.    
    # 
    PIPEOFF = "PipeOff"
    notifTupleTable[PIPEOFF] = Tuple_PipeOff = collections.namedtuple("Tuple_PipeOff", ['timeStamp', 'eventId', 'macAddr'])

    ##
    # \brief SERVICEDENIED notification.
    # 
    # 
    #
    # Formatted as a Tuple_ServiceDenied named tuple. It contains the following fields:
    #   - <tt>timeStamp</tt> 8-byte field formatted as a int.<br/>
    #     There is no restriction on the value of this field.
    #   - <tt>eventId</tt> 4-byte field formatted as a int.<br/>
    #     There is no restriction on the value of this field.
    #   - <tt>serviceId</tt> 4-byte field formatted as a int.<br/>
    #     There is no restriction on the value of this field.
    #   - <tt>requestingMacAddr</tt> 32-byte field formatted as a string.<br/>
    #     There is no restriction on the value of this field.
    #   - <tt>peerMacAddr</tt> 32-byte field formatted as a string.<br/>
    #     There is no restriction on the value of this field.
    #   - <tt>appDomain</tt> 32-byte field formatted as a string.<br/>
    #     This field can only take one of the following values:
    #      - maintenance: maintenance
    #   - <tt>isSource</tt> 1-byte field formatted as a bool.<br/>
    #     There is no restriction on the value of this field.
    #   - <tt>isSink</tt> 1-byte field formatted as a bool.<br/>
    #     There is no restriction on the value of this field.
    #   - <tt>isIntermittent</tt> 1-byte field formatted as a bool.<br/>
    #     There is no restriction on the value of this field.
    #   - <tt>period</tt> 4-byte field formatted as a int.<br/>
    #     There is no restriction on the value of this field.    
    # 
    SERVICEDENIED = "ServiceDenied"
    notifTupleTable[SERVICEDENIED] = Tuple_ServiceDenied = collections.namedtuple("Tuple_ServiceDenied", ['timeStamp', 'eventId', 'serviceId', 'requestingMacAddr', 'peerMacAddr', 'appDomain', 'isSource', 'isSink', 'isIntermittent', 'period'])

    ##
    # \brief PINGREPLY notification.
    # 
    # 
    #
    # Formatted as a Tuple_PingReply named tuple. It contains the following fields:
    #   - <tt>timeStamp</tt> 8-byte field formatted as a int.<br/>
    #     There is no restriction on the value of this field.
    #   - <tt>eventId</tt> 4-byte field formatted as a int.<br/>
    #     There is no restriction on the value of this field.
    #   - <tt>macAddr</tt> 32-byte field formatted as a string.<br/>
    #     There is no restriction on the value of this field.
    #   - <tt>callbackId</tt> 4-byte field formatted as a int.<br/>
    #     There is no restriction on the value of this field.
    #   - <tt>latency</tt> 4-byte field formatted as a int.<br/>
    #     There is no restriction on the value of this field.
    #   - <tt>temperature</tt> 8-byte field formatted as a float.<br/>
    #     There is no restriction on the value of this field.
    #   - <tt>voltage</tt> 8-byte field formatted as a float.<br/>
    #     There is no restriction on the value of this field.
    #   - <tt>hopCount</tt> 4-byte field formatted as a int.<br/>
    #     There is no restriction on the value of this field.    
    # 
    PINGREPLY = "PingReply"
    notifTupleTable[PINGREPLY] = Tuple_PingReply = collections.namedtuple("Tuple_PingReply", ['timeStamp', 'eventId', 'macAddr', 'callbackId', 'latency', 'temperature', 'voltage', 'hopCount'])

    ##
    # \brief TRANSPORTTIMEOUT notification.
    # 
    # 
    #
    # Formatted as a Tuple_TransportTimeout named tuple. It contains the following fields:
    #   - <tt>timeStamp</tt> 8-byte field formatted as a int.<br/>
    #     There is no restriction on the value of this field.
    #   - <tt>eventId</tt> 4-byte field formatted as a int.<br/>
    #     There is no restriction on the value of this field.
    #   - <tt>srcMacAddr</tt> 32-byte field formatted as a string.<br/>
    #     There is no restriction on the value of this field.
    #   - <tt>destMacAddr</tt> 32-byte field formatted as a string.<br/>
    #     There is no restriction on the value of this field.
    #   - <tt>timeoutType</tt> 32-byte field formatted as a string.<br/>
    #     There is no restriction on the value of this field.
    #   - <tt>callbackId</tt> 4-byte field formatted as a int.<br/>
    #     There is no restriction on the value of this field.    
    # 
    TRANSPORTTIMEOUT = "TransportTimeout"
    notifTupleTable[TRANSPORTTIMEOUT] = Tuple_TransportTimeout = collections.namedtuple("Tuple_TransportTimeout", ['timeStamp', 'eventId', 'srcMacAddr', 'destMacAddr', 'timeoutType', 'callbackId'])

    ##
    # \brief DATA notification.
    # 
    # 
    #
    # Formatted as a Tuple_data named tuple. It contains the following fields:
    #   - <tt>moteId</tt> 4-byte field formatted as a int.<br/>
    #     There is no restriction on the value of this field.
    #   - <tt>macAddr</tt> 32-byte field formatted as a string.<br/>
    #     There is no restriction on the value of this field.
    #   - <tt>time</tt> 8-byte field formatted as a int.<br/>
    #     There is no restriction on the value of this field.
    #   - <tt>payload</tt> None-byte field formatted as a hex.<br/>
    #     There is no restriction on the value of this field.
    #   - <tt>payloadType</tt> 1-byte field formatted as a int.<br/>
    #     There is no restriction on the value of this field.
    #   - <tt>isReliable</tt> 1-byte field formatted as a bool.<br/>
    #     There is no restriction on the value of this field.
    #   - <tt>isRequest</tt> 1-byte field formatted as a bool.<br/>
    #     There is no restriction on the value of this field.
    #   - <tt>isBroadcast</tt> 1-byte field formatted as a bool.<br/>
    #     There is no restriction on the value of this field.
    #   - <tt>callbackId</tt> 4-byte field formatted as a int.<br/>
    #     There is no restriction on the value of this field.
    #   - <tt>counter</tt> 4-byte field formatted as a int.<br/>
    #     There is no restriction on the value of this field.    
    # 
    DATA = "data"
    notifTupleTable[DATA] = Tuple_data = collections.namedtuple("Tuple_data", ['moteId', 'macAddr', 'time', 'payload', 'payloadType', 'isReliable', 'isRequest', 'isBroadcast', 'callbackId', 'counter'])

    ##
    # \brief LOCATION notification.
    # 
    # 
    #
    # Formatted as a Tuple_Location named tuple. It contains the following fields:
    #   - <tt>ver</tt> 1-byte field formatted as a int.<br/>
    #     There is no restriction on the value of this field.
    #   - <tt>asn</tt> 8-byte field formatted as a int.<br/>
    #     There is no restriction on the value of this field.
    #   - <tt>src</tt> 32-byte field formatted as a string.<br/>
    #     There is no restriction on the value of this field.
    #   - <tt>dest</tt> 32-byte field formatted as a string.<br/>
    #     There is no restriction on the value of this field.
    #   - <tt>payload</tt> None-byte field formatted as a hex.<br/>
    #     There is no restriction on the value of this field.    
    # 
    LOCATION = "Location"
    notifTupleTable[LOCATION] = Tuple_Location = collections.namedtuple("Tuple_Location", ['ver', 'asn', 'src', 'dest', 'payload'])

    ##
    # \brief CLI notification.
    # 
    # 
    #
    # Formatted as a Tuple_cli named tuple. It contains the following fields:
    #   - <tt>time</tt> 8-byte field formatted as a int.<br/>
    #     There is no restriction on the value of this field.
    #   - <tt>message</tt> 128-byte field formatted as a string.<br/>
    #     There is no restriction on the value of this field.    
    # 
    CLI = "cli"
    notifTupleTable[CLI] = Tuple_cli = collections.namedtuple("Tuple_cli", ['time', 'message'])

    ##
    # \brief LOG notification.
    # 
    # 
    #
    # Formatted as a Tuple_log named tuple. It contains the following fields:
    #   - <tt>time</tt> 8-byte field formatted as a int.<br/>
    #     There is no restriction on the value of this field.
    #   - <tt>severity</tt> 16-byte field formatted as a string.<br/>
    #     There is no restriction on the value of this field.
    #   - <tt>message</tt> 128-byte field formatted as a string.<br/>
    #     There is no restriction on the value of this field.    
    # 
    LOG = "log"
    notifTupleTable[LOG] = Tuple_log = collections.namedtuple("Tuple_log", ['time', 'severity', 'message'])

    ##
    # \brief STDMOTEREPORT notification.
    # 
    # 
    #
    # Formatted as a Tuple_stdMoteReport named tuple. It contains the following fields:
    #   - <tt>time</tt> 8-byte field formatted as a int.<br/>
    #     There is no restriction on the value of this field.
    #   - <tt>macAddr</tt> 16-byte field formatted as a string.<br/>
    #     There is no restriction on the value of this field.
    #   - <tt>payload</tt> None-byte field formatted as a hex.<br/>
    #     There is no restriction on the value of this field.    
    # 
    STDMOTEREPORT = "stdMoteReport"
    notifTupleTable[STDMOTEREPORT] = Tuple_stdMoteReport = collections.namedtuple("Tuple_stdMoteReport", ['time', 'macAddr', 'payload'])

    ##
    # \brief VENDORMOTEREPORT notification.
    # 
    # 
    #
    # Formatted as a Tuple_vendorMoteReport named tuple. It contains the following fields:
    #   - <tt>time</tt> 8-byte field formatted as a int.<br/>
    #     There is no restriction on the value of this field.
    #   - <tt>macAddr</tt> 16-byte field formatted as a string.<br/>
    #     There is no restriction on the value of this field.
    #   - <tt>payload</tt> None-byte field formatted as a hex.<br/>
    #     There is no restriction on the value of this field.    
    # 
    VENDORMOTEREPORT = "vendorMoteReport"
    notifTupleTable[VENDORMOTEREPORT] = Tuple_vendorMoteReport = collections.namedtuple("Tuple_vendorMoteReport", ['time', 'macAddr', 'payload'])

    ##
    # \brief Get a notification from the notification queue, and returns
    #        it properly formatted.
    #
    # \exception NotificationError if unknown notification.
    # 
    def getNotification(self, timeoutSec=-1) :
        temp = self.getNotificationInternal(timeoutSec)
        if not temp:
            return temp
        (ids, param) = temp
        try :
            if  HartMgrConnector.notifTupleTable[ids[-1]] :
                return (ids[-1], HartMgrConnector.notifTupleTable[ids[-1]](**param))
            else :
                return (ids[-1], None)
        except KeyError :
            raise ApiException.NotificationError(ids, param)

##
# end of HartMgrConnector
# \}
# 
