'''
This module was generated automatically. Do not edit directly.
'''

import collections
from   SmartMeshSDK import ApiException
from   IpMoteConnectorInternal import IpMoteConnectorInternal

##
# \addtogroup IpMoteConnector
# \{
# 

class IpMoteConnector(IpMoteConnectorInternal):
    '''
    \brief Public class for IP mote connector, over Serial.
    '''

    #======================== commands ========================================

    ##
    # The named tuple returned by the dn_setParameter_macAddress() function.
    # 
    # - <tt>RC</tt>: 1-byte field formatted as a int.<br/>
    #     This field can only take one of the following values:
    #      - 0: RC_OK
    #      - 1: RC_ERROR
    #      - 3: RC_BUSY
    #      - 4: RC_INVALID_LEN
    #      - 5: RC_INVALID_STATE
    #      - 6: RC_UNSUPPORTED
    #      - 7: RC_UNKNOWN_PARAM
    #      - 8: RC_UNKNOWN_CMD
    #      - 9: RC_WRITE_FAIL
    #      - 10: RC_READ_FAIL
    #      - 11: RC_LOW_VOLTAGE
    #      - 12: RC_NO_RESOURCES
    #      - 13: RC_INCOMPLETE_JOIN_INFO
    #      - 14: RC_NOT_FOUND
    #      - 15: RC_INVALID_VALUE
    #      - 16: RC_ACCESS_DENIED
    #      - 18: RC_ERASE_FAIL
    # 
    Tuple_dn_setParameter_macAddress = collections.namedtuple("Tuple_dn_setParameter_macAddress", ['RC'])

    ##
    # This command allows user to overwrite the manufacturer-assigned MAC address of the mote. The new value takes effect after the mote resets.
    # 
    # \param macAddress 8-byte field formatted as a hex.<br/>
    #     There is no restriction on the value of this field.
    # 
    # \returns The response to the command, formatted as a #Tuple_dn_setParameter_macAddress named tuple.
    # 
    def dn_setParameter_macAddress(self, macAddress) :
        res = IpMoteConnectorInternal.send(self, ['setParameter', 'macAddress'], {"macAddress" : macAddress})
        return IpMoteConnector.Tuple_dn_setParameter_macAddress(**res)

    ##
    # The named tuple returned by the dn_setParameter_joinKey() function.
    # 
    # - <tt>RC</tt>: 1-byte field formatted as a int.<br/>
    #     This field can only take one of the following values:
    #      - 0: RC_OK
    #      - 1: RC_ERROR
    #      - 3: RC_BUSY
    #      - 4: RC_INVALID_LEN
    #      - 5: RC_INVALID_STATE
    #      - 6: RC_UNSUPPORTED
    #      - 7: RC_UNKNOWN_PARAM
    #      - 8: RC_UNKNOWN_CMD
    #      - 9: RC_WRITE_FAIL
    #      - 10: RC_READ_FAIL
    #      - 11: RC_LOW_VOLTAGE
    #      - 12: RC_NO_RESOURCES
    #      - 13: RC_INCOMPLETE_JOIN_INFO
    #      - 14: RC_NOT_FOUND
    #      - 15: RC_INVALID_VALUE
    #      - 16: RC_ACCESS_DENIED
    #      - 18: RC_ERASE_FAIL
    # 
    Tuple_dn_setParameter_joinKey = collections.namedtuple("Tuple_dn_setParameter_joinKey", ['RC'])

    ##
    # The setParameter<joinKey> command may be used to set the join key in mote's persistent storage. Join keys are used by motes to establish secure connection with the network. The join key is used at next join.
    # 
    # Reading the joinKey parameter is prohibited for security reasons.
    # 
    # \param joinKey 16-byte field formatted as a hex.<br/>
    #     There is no restriction on the value of this field.
    # 
    # \returns The response to the command, formatted as a #Tuple_dn_setParameter_joinKey named tuple.
    # 
    def dn_setParameter_joinKey(self, joinKey) :
        res = IpMoteConnectorInternal.send(self, ['setParameter', 'joinKey'], {"joinKey" : joinKey})
        return IpMoteConnector.Tuple_dn_setParameter_joinKey(**res)

    ##
    # The named tuple returned by the dn_setParameter_networkId() function.
    # 
    # - <tt>RC</tt>: 1-byte field formatted as a int.<br/>
    #     This field can only take one of the following values:
    #      - 0: RC_OK
    #      - 1: RC_ERROR
    #      - 3: RC_BUSY
    #      - 4: RC_INVALID_LEN
    #      - 5: RC_INVALID_STATE
    #      - 6: RC_UNSUPPORTED
    #      - 7: RC_UNKNOWN_PARAM
    #      - 8: RC_UNKNOWN_CMD
    #      - 9: RC_WRITE_FAIL
    #      - 10: RC_READ_FAIL
    #      - 11: RC_LOW_VOLTAGE
    #      - 12: RC_NO_RESOURCES
    #      - 13: RC_INCOMPLETE_JOIN_INFO
    #      - 14: RC_NOT_FOUND
    #      - 15: RC_INVALID_VALUE
    #      - 16: RC_ACCESS_DENIED
    #      - 18: RC_ERASE_FAIL
    # 
    Tuple_dn_setParameter_networkId = collections.namedtuple("Tuple_dn_setParameter_networkId", ['RC'])

    ##
    # This command may be used to set the Network ID of the mote. This setting is persistent and is used on next join attempt.
    # 
    # As of version 1.4.x, a network ID of 0xFFFF can be used to indicate that the mote should join the first network heard.
    # 
    # 0xFFFF is never used over the air as a valid network ID - you should not set the Manager's network ID to 0xFFFF.
    # 
    # \param networkId 2-byte field formatted as a int.<br/>
    #     There is no restriction on the value of this field.
    # 
    # \returns The response to the command, formatted as a #Tuple_dn_setParameter_networkId named tuple.
    # 
    def dn_setParameter_networkId(self, networkId) :
        res = IpMoteConnectorInternal.send(self, ['setParameter', 'networkId'], {"networkId" : networkId})
        return IpMoteConnector.Tuple_dn_setParameter_networkId(**res)

    ##
    # The named tuple returned by the dn_setParameter_txPower() function.
    # 
    # - <tt>RC</tt>: 1-byte field formatted as a int.<br/>
    #     This field can only take one of the following values:
    #      - 0: RC_OK
    #      - 1: RC_ERROR
    #      - 3: RC_BUSY
    #      - 4: RC_INVALID_LEN
    #      - 5: RC_INVALID_STATE
    #      - 6: RC_UNSUPPORTED
    #      - 7: RC_UNKNOWN_PARAM
    #      - 8: RC_UNKNOWN_CMD
    #      - 9: RC_WRITE_FAIL
    #      - 10: RC_READ_FAIL
    #      - 11: RC_LOW_VOLTAGE
    #      - 12: RC_NO_RESOURCES
    #      - 13: RC_INCOMPLETE_JOIN_INFO
    #      - 14: RC_NOT_FOUND
    #      - 15: RC_INVALID_VALUE
    #      - 16: RC_ACCESS_DENIED
    #      - 18: RC_ERASE_FAIL
    # 
    Tuple_dn_setParameter_txPower = collections.namedtuple("Tuple_dn_setParameter_txPower", ['RC'])

    ##
    # This command sets the radio output power. This setting is persistent. The command may be issued at any time and takes effect on next transmission. Refer to product datasheets for supported RF output power values. If the provided txPower does not match an appropriate value for the hardware, the radio driver will select the nearest appropriate value. The nearest appropriate value varies depending on the hardware and calibration. The getParameter<txPower> command will return the value selected by the radio driver.
    # 
    # 
    # 
    # For example, if the part has a typical RF output power of +8 dBm when the power amplifier (PA) is enabled, then set the txPower parameter to 8 to enable the PA. Similarly, if the part has a typical RF output power of 0 dBm when the PA is disabled, then set the txPower parameter to 0 to turn off the PA. Similarly, calling this function with a value of 10 on a part, such as the LTC-5800, that supports a maximum of +8 dBm will result in a setting of +8.
    # 
    # \param txPower 1-byte field formatted as a ints.<br/>
    #     There is no restriction on the value of this field.
    # 
    # \returns The response to the command, formatted as a #Tuple_dn_setParameter_txPower named tuple.
    # 
    def dn_setParameter_txPower(self, txPower) :
        res = IpMoteConnectorInternal.send(self, ['setParameter', 'txPower'], {"txPower" : txPower})
        return IpMoteConnector.Tuple_dn_setParameter_txPower(**res)

    ##
    # The named tuple returned by the dn_setParameter_joinDutyCycle() function.
    # 
    # - <tt>RC</tt>: 1-byte field formatted as a int.<br/>
    #     This field can only take one of the following values:
    #      - 0: RC_OK
    #      - 1: RC_ERROR
    #      - 3: RC_BUSY
    #      - 4: RC_INVALID_LEN
    #      - 5: RC_INVALID_STATE
    #      - 6: RC_UNSUPPORTED
    #      - 7: RC_UNKNOWN_PARAM
    #      - 8: RC_UNKNOWN_CMD
    #      - 9: RC_WRITE_FAIL
    #      - 10: RC_READ_FAIL
    #      - 11: RC_LOW_VOLTAGE
    #      - 12: RC_NO_RESOURCES
    #      - 13: RC_INCOMPLETE_JOIN_INFO
    #      - 14: RC_NOT_FOUND
    #      - 15: RC_INVALID_VALUE
    #      - 16: RC_ACCESS_DENIED
    #      - 18: RC_ERASE_FAIL
    # 
    Tuple_dn_setParameter_joinDutyCycle = collections.namedtuple("Tuple_dn_setParameter_joinDutyCycle", ['RC'])

    ##
    # The setParameter<joinDutyCycle> command allows the microprocessor to control the ratio of active listen time to doze time (a low-power radio state) during the period when the mote is searching for the network. If you desire a faster join time at the risk of higher power consumption, use the setParameter<joinDutyCycle> command to increase the join duty cycle up to 100%. This setting is persistent and takes effect immediately if the device is searching for network.
    # 
    # \param dutyCycle 1-byte field formatted as a int.<br/>
    #     There is no restriction on the value of this field.
    # 
    # \returns The response to the command, formatted as a #Tuple_dn_setParameter_joinDutyCycle named tuple.
    # 
    def dn_setParameter_joinDutyCycle(self, dutyCycle) :
        res = IpMoteConnectorInternal.send(self, ['setParameter', 'joinDutyCycle'], {"dutyCycle" : dutyCycle})
        return IpMoteConnector.Tuple_dn_setParameter_joinDutyCycle(**res)

    ##
    # The named tuple returned by the dn_setParameter_eventMask() function.
    # 
    # - <tt>RC</tt>: 1-byte field formatted as a int.<br/>
    #     This field can only take one of the following values:
    #      - 0: RC_OK
    #      - 1: RC_ERROR
    #      - 3: RC_BUSY
    #      - 4: RC_INVALID_LEN
    #      - 5: RC_INVALID_STATE
    #      - 6: RC_UNSUPPORTED
    #      - 7: RC_UNKNOWN_PARAM
    #      - 8: RC_UNKNOWN_CMD
    #      - 9: RC_WRITE_FAIL
    #      - 10: RC_READ_FAIL
    #      - 11: RC_LOW_VOLTAGE
    #      - 12: RC_NO_RESOURCES
    #      - 13: RC_INCOMPLETE_JOIN_INFO
    #      - 14: RC_NOT_FOUND
    #      - 15: RC_INVALID_VALUE
    #      - 16: RC_ACCESS_DENIED
    #      - 18: RC_ERASE_FAIL
    # 
    Tuple_dn_setParameter_eventMask = collections.namedtuple("Tuple_dn_setParameter_eventMask", ['RC'])

    ##
    # The setParameter<eventMask> command allows the microprocessor to selectively subscribe to event notifications. The default value of eventMask at mote reset is all 1s - all events are enabled. This setting is not persistent.
    # 
    # New event types may be added in future revisions of mote software. It is recommended that the client code only subscribe to known events and gracefully ignore all unknown events.
    # 
    # \param eventMask 4-byte field formatted as a hex.<br/>
    #     There is no restriction on the value of this field.
    # 
    # \returns The response to the command, formatted as a #Tuple_dn_setParameter_eventMask named tuple.
    # 
    def dn_setParameter_eventMask(self, eventMask) :
        res = IpMoteConnectorInternal.send(self, ['setParameter', 'eventMask'], {"eventMask" : eventMask})
        return IpMoteConnector.Tuple_dn_setParameter_eventMask(**res)

    ##
    # The named tuple returned by the dn_setParameter_OTAPLockout() function.
    # 
    # - <tt>RC</tt>: 1-byte field formatted as a int.<br/>
    #     This field can only take one of the following values:
    #      - 0: RC_OK
    #      - 1: RC_ERROR
    #      - 3: RC_BUSY
    #      - 4: RC_INVALID_LEN
    #      - 5: RC_INVALID_STATE
    #      - 6: RC_UNSUPPORTED
    #      - 7: RC_UNKNOWN_PARAM
    #      - 8: RC_UNKNOWN_CMD
    #      - 9: RC_WRITE_FAIL
    #      - 10: RC_READ_FAIL
    #      - 11: RC_LOW_VOLTAGE
    #      - 12: RC_NO_RESOURCES
    #      - 13: RC_INCOMPLETE_JOIN_INFO
    #      - 14: RC_NOT_FOUND
    #      - 15: RC_INVALID_VALUE
    #      - 16: RC_ACCESS_DENIED
    #      - 18: RC_ERASE_FAIL
    # 
    Tuple_dn_setParameter_OTAPLockout = collections.namedtuple("Tuple_dn_setParameter_OTAPLockout", ['RC'])

    ##
    # This command allows the microprocessor to control whether Over-The-Air Programming (OTAP) of motes is allowed. This setting is persistent and takes effect immediately.
    # 
    # \param mode 1-byte field formatted as a bool.<br/>
    #     There is no restriction on the value of this field.
    # 
    # \returns The response to the command, formatted as a #Tuple_dn_setParameter_OTAPLockout named tuple.
    # 
    def dn_setParameter_OTAPLockout(self, mode) :
        res = IpMoteConnectorInternal.send(self, ['setParameter', 'OTAPLockout'], {"mode" : mode})
        return IpMoteConnector.Tuple_dn_setParameter_OTAPLockout(**res)

    ##
    # The named tuple returned by the dn_setParameter_routingMode() function.
    # 
    # - <tt>RC</tt>: 1-byte field formatted as a int.<br/>
    #     This field can only take one of the following values:
    #      - 0: RC_OK
    #      - 1: RC_ERROR
    #      - 3: RC_BUSY
    #      - 4: RC_INVALID_LEN
    #      - 5: RC_INVALID_STATE
    #      - 6: RC_UNSUPPORTED
    #      - 7: RC_UNKNOWN_PARAM
    #      - 8: RC_UNKNOWN_CMD
    #      - 9: RC_WRITE_FAIL
    #      - 10: RC_READ_FAIL
    #      - 11: RC_LOW_VOLTAGE
    #      - 12: RC_NO_RESOURCES
    #      - 13: RC_INCOMPLETE_JOIN_INFO
    #      - 14: RC_NOT_FOUND
    #      - 15: RC_INVALID_VALUE
    #      - 16: RC_ACCESS_DENIED
    #      - 18: RC_ERASE_FAIL
    # 
    Tuple_dn_setParameter_routingMode = collections.namedtuple("Tuple_dn_setParameter_routingMode", ['RC'])

    ##
    # This command allows the microprocessor to control whether the mote will become a router once joined the network. If disabled, the manager will keep the mote a leaf node.
    # 
    # \param mode 1-byte field formatted as a bool.<br/>
    #     There is no restriction on the value of this field.
    # 
    # \returns The response to the command, formatted as a #Tuple_dn_setParameter_routingMode named tuple.
    # 
    def dn_setParameter_routingMode(self, mode) :
        res = IpMoteConnectorInternal.send(self, ['setParameter', 'routingMode'], {"mode" : mode})
        return IpMoteConnector.Tuple_dn_setParameter_routingMode(**res)

    ##
    # The named tuple returned by the dn_setParameter_powerSrcInfo() function.
    # 
    # - <tt>RC</tt>: 1-byte field formatted as a int.<br/>
    #     This field can only take one of the following values:
    #      - 0: RC_OK
    #      - 1: RC_ERROR
    #      - 3: RC_BUSY
    #      - 4: RC_INVALID_LEN
    #      - 5: RC_INVALID_STATE
    #      - 6: RC_UNSUPPORTED
    #      - 7: RC_UNKNOWN_PARAM
    #      - 8: RC_UNKNOWN_CMD
    #      - 9: RC_WRITE_FAIL
    #      - 10: RC_READ_FAIL
    #      - 11: RC_LOW_VOLTAGE
    #      - 12: RC_NO_RESOURCES
    #      - 13: RC_INCOMPLETE_JOIN_INFO
    #      - 14: RC_NOT_FOUND
    #      - 15: RC_INVALID_VALUE
    #      - 16: RC_ACCESS_DENIED
    #      - 18: RC_ERASE_FAIL
    # 
    Tuple_dn_setParameter_powerSrcInfo = collections.namedtuple("Tuple_dn_setParameter_powerSrcInfo", ['RC'])

    ##
    # This command allows the microprocessor to configure power source information on the device. This setting is persistent and is used at network join time.
    # 
    # \param maxStCurrent 2-byte field formatted as a int.<br/>
    #     There is no restriction on the value of this field.
    # \param minLifetime 1-byte field formatted as a int.<br/>
    #     There is no restriction on the value of this field.
    # \param currentLimit_0 2-byte field formatted as a int.<br/>
    #     There is no restriction on the value of this field.
    # \param dischargePeriod_0 2-byte field formatted as a int.<br/>
    #     There is no restriction on the value of this field.
    # \param rechargePeriod_0 2-byte field formatted as a int.<br/>
    #     There is no restriction on the value of this field.
    # \param currentLimit_1 2-byte field formatted as a int.<br/>
    #     There is no restriction on the value of this field.
    # \param dischargePeriod_1 2-byte field formatted as a int.<br/>
    #     There is no restriction on the value of this field.
    # \param rechargePeriod_1 2-byte field formatted as a int.<br/>
    #     There is no restriction on the value of this field.
    # \param currentLimit_2 2-byte field formatted as a int.<br/>
    #     There is no restriction on the value of this field.
    # \param dischargePeriod_2 2-byte field formatted as a int.<br/>
    #     There is no restriction on the value of this field.
    # \param rechargePeriod_2 2-byte field formatted as a int.<br/>
    #     There is no restriction on the value of this field.
    # 
    # \returns The response to the command, formatted as a #Tuple_dn_setParameter_powerSrcInfo named tuple.
    # 
    def dn_setParameter_powerSrcInfo(self, maxStCurrent, minLifetime, currentLimit_0, dischargePeriod_0, rechargePeriod_0, currentLimit_1, dischargePeriod_1, rechargePeriod_1, currentLimit_2, dischargePeriod_2, rechargePeriod_2) :
        res = IpMoteConnectorInternal.send(self, ['setParameter', 'powerSrcInfo'], {"maxStCurrent" : maxStCurrent, "minLifetime" : minLifetime, "currentLimit_0" : currentLimit_0, "dischargePeriod_0" : dischargePeriod_0, "rechargePeriod_0" : rechargePeriod_0, "currentLimit_1" : currentLimit_1, "dischargePeriod_1" : dischargePeriod_1, "rechargePeriod_1" : rechargePeriod_1, "currentLimit_2" : currentLimit_2, "dischargePeriod_2" : dischargePeriod_2, "rechargePeriod_2" : rechargePeriod_2})
        return IpMoteConnector.Tuple_dn_setParameter_powerSrcInfo(**res)

    ##
    # The named tuple returned by the dn_setParameter_advKey() function.
    # 
    # - <tt>RC</tt>: 1-byte field formatted as a int.<br/>
    #     This field can only take one of the following values:
    #      - 0: RC_OK
    #      - 1: RC_ERROR
    #      - 3: RC_BUSY
    #      - 4: RC_INVALID_LEN
    #      - 5: RC_INVALID_STATE
    #      - 6: RC_UNSUPPORTED
    #      - 7: RC_UNKNOWN_PARAM
    #      - 8: RC_UNKNOWN_CMD
    #      - 9: RC_WRITE_FAIL
    #      - 10: RC_READ_FAIL
    #      - 11: RC_LOW_VOLTAGE
    #      - 12: RC_NO_RESOURCES
    #      - 13: RC_INCOMPLETE_JOIN_INFO
    #      - 14: RC_NOT_FOUND
    #      - 15: RC_INVALID_VALUE
    #      - 16: RC_ACCESS_DENIED
    #      - 18: RC_ERASE_FAIL
    # 
    Tuple_dn_setParameter_advKey = collections.namedtuple("Tuple_dn_setParameter_advKey", ['RC'])

    ##
    # Sets the Advertisement MIC key - this key is used to authenticate advertisements, and can be set per vendor/installation to prevent unauthorized devices from being able to respond to advertisements. If changed, it must match that set on the corresponding AP (using mset on the manager CLI) in order for the mote to join. It can be reset to default via the clearNV command.
    # 
    # \param advKey 16-byte field formatted as a hex.<br/>
    #     There is no restriction on the value of this field.
    # 
    # \returns The response to the command, formatted as a #Tuple_dn_setParameter_advKey named tuple.
    # 
    def dn_setParameter_advKey(self, advKey) :
        res = IpMoteConnectorInternal.send(self, ['setParameter', 'advKey'], {"advKey" : advKey})
        return IpMoteConnector.Tuple_dn_setParameter_advKey(**res)

    ##
    # The named tuple returned by the dn_setParameter_autoJoin() function.
    # 
    # - <tt>RC</tt>: 1-byte field formatted as a int.<br/>
    #     This field can only take one of the following values:
    #      - 0: RC_OK
    #      - 1: RC_ERROR
    #      - 3: RC_BUSY
    #      - 4: RC_INVALID_LEN
    #      - 5: RC_INVALID_STATE
    #      - 6: RC_UNSUPPORTED
    #      - 7: RC_UNKNOWN_PARAM
    #      - 8: RC_UNKNOWN_CMD
    #      - 9: RC_WRITE_FAIL
    #      - 10: RC_READ_FAIL
    #      - 11: RC_LOW_VOLTAGE
    #      - 12: RC_NO_RESOURCES
    #      - 13: RC_INCOMPLETE_JOIN_INFO
    #      - 14: RC_NOT_FOUND
    #      - 15: RC_INVALID_VALUE
    #      - 16: RC_ACCESS_DENIED
    #      - 18: RC_ERASE_FAIL
    # 
    Tuple_dn_setParameter_autoJoin = collections.namedtuple("Tuple_dn_setParameter_autoJoin", ['RC'])

    ##
    # This command allows the microprocessor to change between automatic and manual joining by the mote's networking stack. In manual mode, an explicit join command from the application is required to initiate joining. This setting is persistent and takes effect after mote reset.
    # 
    # Note that auto join mode must not be set if the application is also configured to join (e.g combining 'auto join' with 'master' mode will result in mote not joining).
    # 
    # \param mode 1-byte field formatted as a bool.<br/>
    #     There is no restriction on the value of this field.
    # 
    # \returns The response to the command, formatted as a #Tuple_dn_setParameter_autoJoin named tuple.
    # 
    def dn_setParameter_autoJoin(self, mode) :
        res = IpMoteConnectorInternal.send(self, ['setParameter', 'autoJoin'], {"mode" : mode})
        return IpMoteConnector.Tuple_dn_setParameter_autoJoin(**res)

    ##
    # The named tuple returned by the dn_setParameter_antGain() function.
    # 
    # - <tt>RC</tt>: 1-byte field formatted as a int.<br/>
    #     This field can only take one of the following values:
    #      - 0: RC_OK
    #      - 1: RC_ERROR
    #      - 3: RC_BUSY
    #      - 4: RC_INVALID_LEN
    #      - 5: RC_INVALID_STATE
    #      - 6: RC_UNSUPPORTED
    #      - 7: RC_UNKNOWN_PARAM
    #      - 8: RC_UNKNOWN_CMD
    #      - 9: RC_WRITE_FAIL
    #      - 10: RC_READ_FAIL
    #      - 11: RC_LOW_VOLTAGE
    #      - 12: RC_NO_RESOURCES
    #      - 13: RC_INCOMPLETE_JOIN_INFO
    #      - 14: RC_NOT_FOUND
    #      - 15: RC_INVALID_VALUE
    #      - 16: RC_ACCESS_DENIED
    #      - 18: RC_ERASE_FAIL
    # 
    Tuple_dn_setParameter_antGain = collections.namedtuple("Tuple_dn_setParameter_antGain", ['RC'])

    ##
    # The setParameter<antGain> command sets the antenna gain of the system (to properly calculate radiated power). Defaults to 2 dBi if not set.
    # 
    # Note: This parameter is available in devices running mote software >=1.4.x
    # 
    # \param antGain 1-byte field formatted as a ints.<br/>
    #     There is no restriction on the value of this field.
    # 
    # \returns The response to the command, formatted as a #Tuple_dn_setParameter_antGain named tuple.
    # 
    def dn_setParameter_antGain(self, antGain) :
        res = IpMoteConnectorInternal.send(self, ['setParameter', 'antGain'], {"antGain" : antGain})
        return IpMoteConnector.Tuple_dn_setParameter_antGain(**res)

    ##
    # The named tuple returned by the dn_setParameter_euCompliantMode() function.
    # 
    # - <tt>RC</tt>: 1-byte field formatted as a int.<br/>
    #     This field can only take one of the following values:
    #      - 0: RC_OK
    #      - 1: RC_ERROR
    #      - 3: RC_BUSY
    #      - 4: RC_INVALID_LEN
    #      - 5: RC_INVALID_STATE
    #      - 6: RC_UNSUPPORTED
    #      - 7: RC_UNKNOWN_PARAM
    #      - 8: RC_UNKNOWN_CMD
    #      - 9: RC_WRITE_FAIL
    #      - 10: RC_READ_FAIL
    #      - 11: RC_LOW_VOLTAGE
    #      - 12: RC_NO_RESOURCES
    #      - 13: RC_INCOMPLETE_JOIN_INFO
    #      - 14: RC_NOT_FOUND
    #      - 15: RC_INVALID_VALUE
    #      - 16: RC_ACCESS_DENIED
    #      - 18: RC_ERASE_FAIL
    # 
    Tuple_dn_setParameter_euCompliantMode = collections.namedtuple("Tuple_dn_setParameter_euCompliantMode", ['RC'])

    ##
    # The setParameter<euCompliantMode> command may be used to set the EN 300 328 compliance mode that is used by the device. When enabled, the mote may skip some transmit opportunities to remain within average power limits. Motes below +10 dBm radiated power do not need to duty cycle to meet EN 300 328 requirements.
    # 
    # Note: This parameter is available in devices running mote software >=1.4.x
    # 
    # \param euCompliantMode 1-byte field formatted as a int.<br/>
    #     There is no restriction on the value of this field.
    # 
    # \returns The response to the command, formatted as a #Tuple_dn_setParameter_euCompliantMode named tuple.
    # 
    def dn_setParameter_euCompliantMode(self, euCompliantMode) :
        res = IpMoteConnectorInternal.send(self, ['setParameter', 'euCompliantMode'], {"euCompliantMode" : euCompliantMode})
        return IpMoteConnector.Tuple_dn_setParameter_euCompliantMode(**res)

    ##
    # The named tuple returned by the dn_getParameter_macAddress() function.
    # 
    # - <tt>RC</tt>: 1-byte field formatted as a int.<br/>
    #     This field can only take one of the following values:
    #      - 0: RC_OK
    #      - 1: RC_ERROR
    #      - 3: RC_BUSY
    #      - 4: RC_INVALID_LEN
    #      - 5: RC_INVALID_STATE
    #      - 6: RC_UNSUPPORTED
    #      - 7: RC_UNKNOWN_PARAM
    #      - 8: RC_UNKNOWN_CMD
    #      - 9: RC_WRITE_FAIL
    #      - 10: RC_READ_FAIL
    #      - 11: RC_LOW_VOLTAGE
    #      - 12: RC_NO_RESOURCES
    #      - 13: RC_INCOMPLETE_JOIN_INFO
    #      - 14: RC_NOT_FOUND
    #      - 15: RC_INVALID_VALUE
    #      - 16: RC_ACCESS_DENIED
    #      - 18: RC_ERASE_FAIL
    # - <tt>macAddress</tt>: 8-byte field formatted as a hex.<br/>
    #     There is no restriction on the value of this field.
    # 
    Tuple_dn_getParameter_macAddress = collections.namedtuple("Tuple_dn_getParameter_macAddress", ['RC', 'macAddress'])

    ##
    # This command returns the user defined MAC address of the device. By default, the MAC address returned is 00's if not overwritten using the setParameter<macAddress> command. In mote versions prior to 1.4.1, it returned the factory MAC address.
    # 
    # 
    # 
    # \returns The response to the command, formatted as a #Tuple_dn_getParameter_macAddress named tuple.
    # 
    def dn_getParameter_macAddress(self, ) :
        res = IpMoteConnectorInternal.send(self, ['getParameter', 'macAddress'], {})
        return IpMoteConnector.Tuple_dn_getParameter_macAddress(**res)

    ##
    # The named tuple returned by the dn_getParameter_networkId() function.
    # 
    # - <tt>RC</tt>: 1-byte field formatted as a int.<br/>
    #     This field can only take one of the following values:
    #      - 0: RC_OK
    #      - 1: RC_ERROR
    #      - 3: RC_BUSY
    #      - 4: RC_INVALID_LEN
    #      - 5: RC_INVALID_STATE
    #      - 6: RC_UNSUPPORTED
    #      - 7: RC_UNKNOWN_PARAM
    #      - 8: RC_UNKNOWN_CMD
    #      - 9: RC_WRITE_FAIL
    #      - 10: RC_READ_FAIL
    #      - 11: RC_LOW_VOLTAGE
    #      - 12: RC_NO_RESOURCES
    #      - 13: RC_INCOMPLETE_JOIN_INFO
    #      - 14: RC_NOT_FOUND
    #      - 15: RC_INVALID_VALUE
    #      - 16: RC_ACCESS_DENIED
    #      - 18: RC_ERASE_FAIL
    # - <tt>networkId</tt>: 2-byte field formatted as a int.<br/>
    #     There is no restriction on the value of this field.
    # 
    Tuple_dn_getParameter_networkId = collections.namedtuple("Tuple_dn_getParameter_networkId", ['RC', 'networkId'])

    ##
    # This command returns the network id stored in mote's persistent storage.
    # 
    # 
    # 
    # \returns The response to the command, formatted as a #Tuple_dn_getParameter_networkId named tuple.
    # 
    def dn_getParameter_networkId(self, ) :
        res = IpMoteConnectorInternal.send(self, ['getParameter', 'networkId'], {})
        return IpMoteConnector.Tuple_dn_getParameter_networkId(**res)

    ##
    # The named tuple returned by the dn_getParameter_txPower() function.
    # 
    # - <tt>RC</tt>: 1-byte field formatted as a int.<br/>
    #     This field can only take one of the following values:
    #      - 0: RC_OK
    #      - 1: RC_ERROR
    #      - 3: RC_BUSY
    #      - 4: RC_INVALID_LEN
    #      - 5: RC_INVALID_STATE
    #      - 6: RC_UNSUPPORTED
    #      - 7: RC_UNKNOWN_PARAM
    #      - 8: RC_UNKNOWN_CMD
    #      - 9: RC_WRITE_FAIL
    #      - 10: RC_READ_FAIL
    #      - 11: RC_LOW_VOLTAGE
    #      - 12: RC_NO_RESOURCES
    #      - 13: RC_INCOMPLETE_JOIN_INFO
    #      - 14: RC_NOT_FOUND
    #      - 15: RC_INVALID_VALUE
    #      - 16: RC_ACCESS_DENIED
    #      - 18: RC_ERASE_FAIL
    # - <tt>txPower</tt>: 1-byte field formatted as a ints.<br/>
    #     There is no restriction on the value of this field.
    # 
    Tuple_dn_getParameter_txPower = collections.namedtuple("Tuple_dn_getParameter_txPower", ['RC', 'txPower'])

    ##
    # This command gets the radio output power in dBm, excluding any antenna gain. This value corresponds to the actual output power used by the radio driver and may not be the same as the input value entered with the setParameter<txPower>, which will set to nearest if the value entered is not supported by the hardware.
    # 
    # 
    # 
    # \returns The response to the command, formatted as a #Tuple_dn_getParameter_txPower named tuple.
    # 
    def dn_getParameter_txPower(self, ) :
        res = IpMoteConnectorInternal.send(self, ['getParameter', 'txPower'], {})
        return IpMoteConnector.Tuple_dn_getParameter_txPower(**res)

    ##
    # The named tuple returned by the dn_getParameter_joinDutyCycle() function.
    # 
    # - <tt>RC</tt>: 1-byte field formatted as a int.<br/>
    #     This field can only take one of the following values:
    #      - 0: RC_OK
    #      - 1: RC_ERROR
    #      - 3: RC_BUSY
    #      - 4: RC_INVALID_LEN
    #      - 5: RC_INVALID_STATE
    #      - 6: RC_UNSUPPORTED
    #      - 7: RC_UNKNOWN_PARAM
    #      - 8: RC_UNKNOWN_CMD
    #      - 9: RC_WRITE_FAIL
    #      - 10: RC_READ_FAIL
    #      - 11: RC_LOW_VOLTAGE
    #      - 12: RC_NO_RESOURCES
    #      - 13: RC_INCOMPLETE_JOIN_INFO
    #      - 14: RC_NOT_FOUND
    #      - 15: RC_INVALID_VALUE
    #      - 16: RC_ACCESS_DENIED
    #      - 18: RC_ERASE_FAIL
    # - <tt>joinDutyCycle</tt>: 1-byte field formatted as a int.<br/>
    #     There is no restriction on the value of this field.
    # 
    Tuple_dn_getParameter_joinDutyCycle = collections.namedtuple("Tuple_dn_getParameter_joinDutyCycle", ['RC', 'joinDutyCycle'])

    ##
    # This command allows user to retrieve current value of joinDutyCycle parameter.
    # 
    # 
    # 
    # \returns The response to the command, formatted as a #Tuple_dn_getParameter_joinDutyCycle named tuple.
    # 
    def dn_getParameter_joinDutyCycle(self, ) :
        res = IpMoteConnectorInternal.send(self, ['getParameter', 'joinDutyCycle'], {})
        return IpMoteConnector.Tuple_dn_getParameter_joinDutyCycle(**res)

    ##
    # The named tuple returned by the dn_getParameter_eventMask() function.
    # 
    # - <tt>RC</tt>: 1-byte field formatted as a int.<br/>
    #     This field can only take one of the following values:
    #      - 0: RC_OK
    #      - 1: RC_ERROR
    #      - 3: RC_BUSY
    #      - 4: RC_INVALID_LEN
    #      - 5: RC_INVALID_STATE
    #      - 6: RC_UNSUPPORTED
    #      - 7: RC_UNKNOWN_PARAM
    #      - 8: RC_UNKNOWN_CMD
    #      - 9: RC_WRITE_FAIL
    #      - 10: RC_READ_FAIL
    #      - 11: RC_LOW_VOLTAGE
    #      - 12: RC_NO_RESOURCES
    #      - 13: RC_INCOMPLETE_JOIN_INFO
    #      - 14: RC_NOT_FOUND
    #      - 15: RC_INVALID_VALUE
    #      - 16: RC_ACCESS_DENIED
    #      - 18: RC_ERASE_FAIL
    # - <tt>eventMask</tt>: 4-byte field formatted as a hex.<br/>
    #     There is no restriction on the value of this field.
    # 
    Tuple_dn_getParameter_eventMask = collections.namedtuple("Tuple_dn_getParameter_eventMask", ['RC', 'eventMask'])

    ##
    # getParameter<eventMask> allows the microprocessor to read the currently subscribed-to event types.
    # 
    # 
    # 
    # \returns The response to the command, formatted as a #Tuple_dn_getParameter_eventMask named tuple.
    # 
    def dn_getParameter_eventMask(self, ) :
        res = IpMoteConnectorInternal.send(self, ['getParameter', 'eventMask'], {})
        return IpMoteConnector.Tuple_dn_getParameter_eventMask(**res)

    ##
    # The named tuple returned by the dn_getParameter_moteInfo() function.
    # 
    # - <tt>RC</tt>: 1-byte field formatted as a int.<br/>
    #     This field can only take one of the following values:
    #      - 0: RC_OK
    #      - 1: RC_ERROR
    #      - 3: RC_BUSY
    #      - 4: RC_INVALID_LEN
    #      - 5: RC_INVALID_STATE
    #      - 6: RC_UNSUPPORTED
    #      - 7: RC_UNKNOWN_PARAM
    #      - 8: RC_UNKNOWN_CMD
    #      - 9: RC_WRITE_FAIL
    #      - 10: RC_READ_FAIL
    #      - 11: RC_LOW_VOLTAGE
    #      - 12: RC_NO_RESOURCES
    #      - 13: RC_INCOMPLETE_JOIN_INFO
    #      - 14: RC_NOT_FOUND
    #      - 15: RC_INVALID_VALUE
    #      - 16: RC_ACCESS_DENIED
    #      - 18: RC_ERASE_FAIL
    # - <tt>apiVersion</tt>: 1-byte field formatted as a int.<br/>
    #     There is no restriction on the value of this field.
    # - <tt>serialNumber</tt>: 8-byte field formatted as a hex.<br/>
    #     There is no restriction on the value of this field.
    # - <tt>hwModel</tt>: 1-byte field formatted as a int.<br/>
    #     There is no restriction on the value of this field.
    # - <tt>hwRev</tt>: 1-byte field formatted as a int.<br/>
    #     There is no restriction on the value of this field.
    # - <tt>swVerMajor</tt>: 1-byte field formatted as a int.<br/>
    #     There is no restriction on the value of this field.
    # - <tt>swVerMinor</tt>: 1-byte field formatted as a int.<br/>
    #     There is no restriction on the value of this field.
    # - <tt>swVerPatch</tt>: 1-byte field formatted as a int.<br/>
    #     There is no restriction on the value of this field.
    # - <tt>swVerBuild</tt>: 2-byte field formatted as a int.<br/>
    #     There is no restriction on the value of this field.
    # - <tt>bootSwVer</tt>: 1-byte field formatted as a int.<br/>
    #     There is no restriction on the value of this field.
    # 
    Tuple_dn_getParameter_moteInfo = collections.namedtuple("Tuple_dn_getParameter_moteInfo", ['RC', 'apiVersion', 'serialNumber', 'hwModel', 'hwRev', 'swVerMajor', 'swVerMinor', 'swVerPatch', 'swVerBuild', 'bootSwVer'])

    ##
    # The getParameter<moteInfo> command returns static information about the motes hardware and network stack software.
    # 
    # 
    # 
    # \returns The response to the command, formatted as a #Tuple_dn_getParameter_moteInfo named tuple.
    # 
    def dn_getParameter_moteInfo(self, ) :
        res = IpMoteConnectorInternal.send(self, ['getParameter', 'moteInfo'], {})
        return IpMoteConnector.Tuple_dn_getParameter_moteInfo(**res)

    ##
    # The named tuple returned by the dn_getParameter_netInfo() function.
    # 
    # - <tt>RC</tt>: 1-byte field formatted as a int.<br/>
    #     This field can only take one of the following values:
    #      - 0: RC_OK
    #      - 1: RC_ERROR
    #      - 3: RC_BUSY
    #      - 4: RC_INVALID_LEN
    #      - 5: RC_INVALID_STATE
    #      - 6: RC_UNSUPPORTED
    #      - 7: RC_UNKNOWN_PARAM
    #      - 8: RC_UNKNOWN_CMD
    #      - 9: RC_WRITE_FAIL
    #      - 10: RC_READ_FAIL
    #      - 11: RC_LOW_VOLTAGE
    #      - 12: RC_NO_RESOURCES
    #      - 13: RC_INCOMPLETE_JOIN_INFO
    #      - 14: RC_NOT_FOUND
    #      - 15: RC_INVALID_VALUE
    #      - 16: RC_ACCESS_DENIED
    #      - 18: RC_ERASE_FAIL
    # - <tt>macAddress</tt>: 8-byte field formatted as a hex.<br/>
    #     There is no restriction on the value of this field.
    # - <tt>moteId</tt>: 2-byte field formatted as a int.<br/>
    #     There is no restriction on the value of this field.
    # - <tt>networkId</tt>: 2-byte field formatted as a int.<br/>
    #     There is no restriction on the value of this field.
    # - <tt>slotSize</tt>: 2-byte field formatted as a int.<br/>
    #     There is no restriction on the value of this field.
    # 
    Tuple_dn_getParameter_netInfo = collections.namedtuple("Tuple_dn_getParameter_netInfo", ['RC', 'macAddress', 'moteId', 'networkId', 'slotSize'])

    ##
    # The getParameter<networkInfo> command may be used to retrieve the mote's network-related parameters.
    # 
    # 
    # 
    # \returns The response to the command, formatted as a #Tuple_dn_getParameter_netInfo named tuple.
    # 
    def dn_getParameter_netInfo(self, ) :
        res = IpMoteConnectorInternal.send(self, ['getParameter', 'netInfo'], {})
        return IpMoteConnector.Tuple_dn_getParameter_netInfo(**res)

    ##
    # The named tuple returned by the dn_getParameter_moteStatus() function.
    # 
    # - <tt>RC</tt>: 1-byte field formatted as a int.<br/>
    #     This field can only take one of the following values:
    #      - 0: RC_OK
    #      - 1: RC_ERROR
    #      - 3: RC_BUSY
    #      - 4: RC_INVALID_LEN
    #      - 5: RC_INVALID_STATE
    #      - 6: RC_UNSUPPORTED
    #      - 7: RC_UNKNOWN_PARAM
    #      - 8: RC_UNKNOWN_CMD
    #      - 9: RC_WRITE_FAIL
    #      - 10: RC_READ_FAIL
    #      - 11: RC_LOW_VOLTAGE
    #      - 12: RC_NO_RESOURCES
    #      - 13: RC_INCOMPLETE_JOIN_INFO
    #      - 14: RC_NOT_FOUND
    #      - 15: RC_INVALID_VALUE
    #      - 16: RC_ACCESS_DENIED
    #      - 18: RC_ERASE_FAIL
    # - <tt>state</tt>: 1-byte field formatted as a int.<br/>
    #     This field can only take one of the following values:
    #      - 0: init
    #      - 1: idle
    #      - 2: searching
    #      - 3: negotiating
    #      - 4: connected
    #      - 5: operational
    #      - 6: disconnected
    #      - 7: radiotest
    #      - 8: promiscuous listen
    #      - 9: blink
    # - <tt>reserved_0</tt>: 1-byte field formatted as a int.<br/>
    #     There is no restriction on the value of this field.
    # - <tt>reserved_1</tt>: 2-byte field formatted as a int.<br/>
    #     There is no restriction on the value of this field.
    # - <tt>numParents</tt>: 1-byte field formatted as a int.<br/>
    #     There is no restriction on the value of this field.
    # - <tt>alarms</tt>: 4-byte field formatted as a int.<br/>
    #     There is no restriction on the value of this field.
    # - <tt>reserved_2</tt>: 1-byte field formatted as a int.<br/>
    #     There is no restriction on the value of this field.
    # 
    Tuple_dn_getParameter_moteStatus = collections.namedtuple("Tuple_dn_getParameter_moteStatus", ['RC', 'state', 'reserved_0', 'reserved_1', 'numParents', 'alarms', 'reserved_2'])

    ##
    # The getParameter<moteStatus> command is used to retrieve current mote state and other dynamic information.
    # 
    # 
    # 
    # \returns The response to the command, formatted as a #Tuple_dn_getParameter_moteStatus named tuple.
    # 
    def dn_getParameter_moteStatus(self, ) :
        res = IpMoteConnectorInternal.send(self, ['getParameter', 'moteStatus'], {})
        return IpMoteConnector.Tuple_dn_getParameter_moteStatus(**res)

    ##
    # The named tuple returned by the dn_getParameter_time() function.
    # 
    # - <tt>RC</tt>: 1-byte field formatted as a int.<br/>
    #     This field can only take one of the following values:
    #      - 0: RC_OK
    #      - 1: RC_ERROR
    #      - 3: RC_BUSY
    #      - 4: RC_INVALID_LEN
    #      - 5: RC_INVALID_STATE
    #      - 6: RC_UNSUPPORTED
    #      - 7: RC_UNKNOWN_PARAM
    #      - 8: RC_UNKNOWN_CMD
    #      - 9: RC_WRITE_FAIL
    #      - 10: RC_READ_FAIL
    #      - 11: RC_LOW_VOLTAGE
    #      - 12: RC_NO_RESOURCES
    #      - 13: RC_INCOMPLETE_JOIN_INFO
    #      - 14: RC_NOT_FOUND
    #      - 15: RC_INVALID_VALUE
    #      - 16: RC_ACCESS_DENIED
    #      - 18: RC_ERASE_FAIL
    # - <tt>upTime</tt>: 4-byte field formatted as a int.<br/>
    #     There is no restriction on the value of this field.
    # - <tt>utcSecs</tt>: 8-byte field formatted as a int.<br/>
    #     There is no restriction on the value of this field.
    # - <tt>utcUsecs</tt>: 4-byte field formatted as a int.<br/>
    #     There is no restriction on the value of this field.
    # - <tt>asn</tt>: 5-byte field formatted as a hex.<br/>
    #     There is no restriction on the value of this field.
    # - <tt>asnOffset</tt>: 2-byte field formatted as a int.<br/>
    #     There is no restriction on the value of this field.
    # 
    Tuple_dn_getParameter_time = collections.namedtuple("Tuple_dn_getParameter_time", ['RC', 'upTime', 'utcSecs', 'utcUsecs', 'asn', 'asnOffset'])

    ##
    # The getParameter<time> command may be used to request the current time on the mote. The mote reports time at the moment it is processing the command, so the information includes variable delay. For more precise time information consider using TIMEn pin (see timeIndication).
    # 
    # 
    # 
    # \returns The response to the command, formatted as a #Tuple_dn_getParameter_time named tuple.
    # 
    def dn_getParameter_time(self, ) :
        res = IpMoteConnectorInternal.send(self, ['getParameter', 'time'], {})
        return IpMoteConnector.Tuple_dn_getParameter_time(**res)

    ##
    # The named tuple returned by the dn_getParameter_charge() function.
    # 
    # - <tt>RC</tt>: 1-byte field formatted as a int.<br/>
    #     This field can only take one of the following values:
    #      - 0: RC_OK
    #      - 1: RC_ERROR
    #      - 3: RC_BUSY
    #      - 4: RC_INVALID_LEN
    #      - 5: RC_INVALID_STATE
    #      - 6: RC_UNSUPPORTED
    #      - 7: RC_UNKNOWN_PARAM
    #      - 8: RC_UNKNOWN_CMD
    #      - 9: RC_WRITE_FAIL
    #      - 10: RC_READ_FAIL
    #      - 11: RC_LOW_VOLTAGE
    #      - 12: RC_NO_RESOURCES
    #      - 13: RC_INCOMPLETE_JOIN_INFO
    #      - 14: RC_NOT_FOUND
    #      - 15: RC_INVALID_VALUE
    #      - 16: RC_ACCESS_DENIED
    #      - 18: RC_ERASE_FAIL
    # - <tt>qTotal</tt>: 4-byte field formatted as a int.<br/>
    #     There is no restriction on the value of this field.
    # - <tt>upTime</tt>: 4-byte field formatted as a int.<br/>
    #     There is no restriction on the value of this field.
    # - <tt>tempInt</tt>: 1-byte field formatted as a ints.<br/>
    #     There is no restriction on the value of this field.
    # - <tt>tempFrac</tt>: 1-byte field formatted as a int.<br/>
    #     There is no restriction on the value of this field.
    # 
    Tuple_dn_getParameter_charge = collections.namedtuple("Tuple_dn_getParameter_charge", ['RC', 'qTotal', 'upTime', 'tempInt', 'tempFrac'])

    ##
    # The getParameter<charge> command retrieves the charge consumption of the mote since the last reset.
    # 
    # 
    # 
    # \returns The response to the command, formatted as a #Tuple_dn_getParameter_charge named tuple.
    # 
    def dn_getParameter_charge(self, ) :
        res = IpMoteConnectorInternal.send(self, ['getParameter', 'charge'], {})
        return IpMoteConnector.Tuple_dn_getParameter_charge(**res)

    ##
    # The named tuple returned by the dn_getParameter_testRadioRxStats() function.
    # 
    # - <tt>RC</tt>: 1-byte field formatted as a int.<br/>
    #     This field can only take one of the following values:
    #      - 0: RC_OK
    #      - 1: RC_ERROR
    #      - 3: RC_BUSY
    #      - 4: RC_INVALID_LEN
    #      - 5: RC_INVALID_STATE
    #      - 6: RC_UNSUPPORTED
    #      - 7: RC_UNKNOWN_PARAM
    #      - 8: RC_UNKNOWN_CMD
    #      - 9: RC_WRITE_FAIL
    #      - 10: RC_READ_FAIL
    #      - 11: RC_LOW_VOLTAGE
    #      - 12: RC_NO_RESOURCES
    #      - 13: RC_INCOMPLETE_JOIN_INFO
    #      - 14: RC_NOT_FOUND
    #      - 15: RC_INVALID_VALUE
    #      - 16: RC_ACCESS_DENIED
    #      - 18: RC_ERASE_FAIL
    # - <tt>rxOk</tt>: 2-byte field formatted as a int.<br/>
    #     There is no restriction on the value of this field.
    # - <tt>rxFailed</tt>: 2-byte field formatted as a int.<br/>
    #     There is no restriction on the value of this field.
    # 
    Tuple_dn_getParameter_testRadioRxStats = collections.namedtuple("Tuple_dn_getParameter_testRadioRxStats", ['RC', 'rxOk', 'rxFailed'])

    ##
    # The getParameter<testRadioRxStats> command retrieves statistics for the latest radio test performed using the testRadioRx command. The statistics show the number of good and bad packets (CRC failures) received during the test
    # 
    # 
    # 
    # \returns The response to the command, formatted as a #Tuple_dn_getParameter_testRadioRxStats named tuple.
    # 
    def dn_getParameter_testRadioRxStats(self, ) :
        res = IpMoteConnectorInternal.send(self, ['getParameter', 'testRadioRxStats'], {})
        return IpMoteConnector.Tuple_dn_getParameter_testRadioRxStats(**res)

    ##
    # The named tuple returned by the dn_getParameter_OTAPLockout() function.
    # 
    # - <tt>RC</tt>: 1-byte field formatted as a int.<br/>
    #     This field can only take one of the following values:
    #      - 0: RC_OK
    #      - 1: RC_ERROR
    #      - 3: RC_BUSY
    #      - 4: RC_INVALID_LEN
    #      - 5: RC_INVALID_STATE
    #      - 6: RC_UNSUPPORTED
    #      - 7: RC_UNKNOWN_PARAM
    #      - 8: RC_UNKNOWN_CMD
    #      - 9: RC_WRITE_FAIL
    #      - 10: RC_READ_FAIL
    #      - 11: RC_LOW_VOLTAGE
    #      - 12: RC_NO_RESOURCES
    #      - 13: RC_INCOMPLETE_JOIN_INFO
    #      - 14: RC_NOT_FOUND
    #      - 15: RC_INVALID_VALUE
    #      - 16: RC_ACCESS_DENIED
    #      - 18: RC_ERASE_FAIL
    # - <tt>mode</tt>: 1-byte field formatted as a bool.<br/>
    #     There is no restriction on the value of this field.
    # 
    Tuple_dn_getParameter_OTAPLockout = collections.namedtuple("Tuple_dn_getParameter_OTAPLockout", ['RC', 'mode'])

    ##
    # This command reads the current state of OTAP lockout, i.e. whether over-the-air upgrades of software are permitted on this mote.
    # 
    # 
    # 
    # \returns The response to the command, formatted as a #Tuple_dn_getParameter_OTAPLockout named tuple.
    # 
    def dn_getParameter_OTAPLockout(self, ) :
        res = IpMoteConnectorInternal.send(self, ['getParameter', 'OTAPLockout'], {})
        return IpMoteConnector.Tuple_dn_getParameter_OTAPLockout(**res)

    ##
    # The named tuple returned by the dn_getParameter_moteId() function.
    # 
    # - <tt>RC</tt>: 1-byte field formatted as a int.<br/>
    #     This field can only take one of the following values:
    #      - 0: RC_OK
    #      - 1: RC_ERROR
    #      - 3: RC_BUSY
    #      - 4: RC_INVALID_LEN
    #      - 5: RC_INVALID_STATE
    #      - 6: RC_UNSUPPORTED
    #      - 7: RC_UNKNOWN_PARAM
    #      - 8: RC_UNKNOWN_CMD
    #      - 9: RC_WRITE_FAIL
    #      - 10: RC_READ_FAIL
    #      - 11: RC_LOW_VOLTAGE
    #      - 12: RC_NO_RESOURCES
    #      - 13: RC_INCOMPLETE_JOIN_INFO
    #      - 14: RC_NOT_FOUND
    #      - 15: RC_INVALID_VALUE
    #      - 16: RC_ACCESS_DENIED
    #      - 18: RC_ERASE_FAIL
    # - <tt>moteId</tt>: 2-byte field formatted as a int.<br/>
    #     There is no restriction on the value of this field.
    # 
    Tuple_dn_getParameter_moteId = collections.namedtuple("Tuple_dn_getParameter_moteId", ['RC', 'moteId'])

    ##
    # This command retrieves the mote's Mote ID. If the mote is not in the network, value of 0 is returned.
    # 
    # 
    # 
    # \returns The response to the command, formatted as a #Tuple_dn_getParameter_moteId named tuple.
    # 
    def dn_getParameter_moteId(self, ) :
        res = IpMoteConnectorInternal.send(self, ['getParameter', 'moteId'], {})
        return IpMoteConnector.Tuple_dn_getParameter_moteId(**res)

    ##
    # The named tuple returned by the dn_getParameter_ipv6Address() function.
    # 
    # - <tt>RC</tt>: 1-byte field formatted as a int.<br/>
    #     This field can only take one of the following values:
    #      - 0: RC_OK
    #      - 1: RC_ERROR
    #      - 3: RC_BUSY
    #      - 4: RC_INVALID_LEN
    #      - 5: RC_INVALID_STATE
    #      - 6: RC_UNSUPPORTED
    #      - 7: RC_UNKNOWN_PARAM
    #      - 8: RC_UNKNOWN_CMD
    #      - 9: RC_WRITE_FAIL
    #      - 10: RC_READ_FAIL
    #      - 11: RC_LOW_VOLTAGE
    #      - 12: RC_NO_RESOURCES
    #      - 13: RC_INCOMPLETE_JOIN_INFO
    #      - 14: RC_NOT_FOUND
    #      - 15: RC_INVALID_VALUE
    #      - 16: RC_ACCESS_DENIED
    #      - 18: RC_ERASE_FAIL
    # - <tt>ipv6Address</tt>: 16-byte field formatted as a hex.<br/>
    #     There is no restriction on the value of this field.
    # 
    Tuple_dn_getParameter_ipv6Address = collections.namedtuple("Tuple_dn_getParameter_ipv6Address", ['RC', 'ipv6Address'])

    ##
    # This command allows the microprocessor to read IPV6 address assigned to the mote. Before the mote has an assigned address it will return all 0s.
    # 
    # 
    # 
    # \returns The response to the command, formatted as a #Tuple_dn_getParameter_ipv6Address named tuple.
    # 
    def dn_getParameter_ipv6Address(self, ) :
        res = IpMoteConnectorInternal.send(self, ['getParameter', 'ipv6Address'], {})
        return IpMoteConnector.Tuple_dn_getParameter_ipv6Address(**res)

    ##
    # The named tuple returned by the dn_getParameter_routingMode() function.
    # 
    # - <tt>RC</tt>: 1-byte field formatted as a int.<br/>
    #     This field can only take one of the following values:
    #      - 0: RC_OK
    #      - 1: RC_ERROR
    #      - 3: RC_BUSY
    #      - 4: RC_INVALID_LEN
    #      - 5: RC_INVALID_STATE
    #      - 6: RC_UNSUPPORTED
    #      - 7: RC_UNKNOWN_PARAM
    #      - 8: RC_UNKNOWN_CMD
    #      - 9: RC_WRITE_FAIL
    #      - 10: RC_READ_FAIL
    #      - 11: RC_LOW_VOLTAGE
    #      - 12: RC_NO_RESOURCES
    #      - 13: RC_INCOMPLETE_JOIN_INFO
    #      - 14: RC_NOT_FOUND
    #      - 15: RC_INVALID_VALUE
    #      - 16: RC_ACCESS_DENIED
    #      - 18: RC_ERASE_FAIL
    # - <tt>routingMode</tt>: 1-byte field formatted as a bool.<br/>
    #     There is no restriction on the value of this field.
    # 
    Tuple_dn_getParameter_routingMode = collections.namedtuple("Tuple_dn_getParameter_routingMode", ['RC', 'routingMode'])

    ##
    # This command allows the microprocessor to retrieve the current routing mode of the mote.
    # 
    # 
    # 
    # \returns The response to the command, formatted as a #Tuple_dn_getParameter_routingMode named tuple.
    # 
    def dn_getParameter_routingMode(self, ) :
        res = IpMoteConnectorInternal.send(self, ['getParameter', 'routingMode'], {})
        return IpMoteConnector.Tuple_dn_getParameter_routingMode(**res)

    ##
    # The named tuple returned by the dn_getParameter_appInfo() function.
    # 
    # - <tt>RC</tt>: 1-byte field formatted as a int.<br/>
    #     This field can only take one of the following values:
    #      - 0: RC_OK
    #      - 1: RC_ERROR
    #      - 3: RC_BUSY
    #      - 4: RC_INVALID_LEN
    #      - 5: RC_INVALID_STATE
    #      - 6: RC_UNSUPPORTED
    #      - 7: RC_UNKNOWN_PARAM
    #      - 8: RC_UNKNOWN_CMD
    #      - 9: RC_WRITE_FAIL
    #      - 10: RC_READ_FAIL
    #      - 11: RC_LOW_VOLTAGE
    #      - 12: RC_NO_RESOURCES
    #      - 13: RC_INCOMPLETE_JOIN_INFO
    #      - 14: RC_NOT_FOUND
    #      - 15: RC_INVALID_VALUE
    #      - 16: RC_ACCESS_DENIED
    #      - 18: RC_ERASE_FAIL
    # - <tt>vendorId</tt>: 2-byte field formatted as a int.<br/>
    #     There is no restriction on the value of this field.
    # - <tt>appId</tt>: 1-byte field formatted as a int.<br/>
    #     There is no restriction on the value of this field.
    # - <tt>appVer</tt>: 5-byte field formatted as a hex.<br/>
    #     There is no restriction on the value of this field.
    # 
    Tuple_dn_getParameter_appInfo = collections.namedtuple("Tuple_dn_getParameter_appInfo", ['RC', 'vendorId', 'appId', 'appVer'])

    ##
    # Get the application (as opposed to the network stack) version information.
    # 
    # 
    # 
    # \returns The response to the command, formatted as a #Tuple_dn_getParameter_appInfo named tuple.
    # 
    def dn_getParameter_appInfo(self, ) :
        res = IpMoteConnectorInternal.send(self, ['getParameter', 'appInfo'], {})
        return IpMoteConnector.Tuple_dn_getParameter_appInfo(**res)

    ##
    # The named tuple returned by the dn_getParameter_powerSrcInfo() function.
    # 
    # - <tt>RC</tt>: 1-byte field formatted as a int.<br/>
    #     This field can only take one of the following values:
    #      - 0: RC_OK
    #      - 1: RC_ERROR
    #      - 3: RC_BUSY
    #      - 4: RC_INVALID_LEN
    #      - 5: RC_INVALID_STATE
    #      - 6: RC_UNSUPPORTED
    #      - 7: RC_UNKNOWN_PARAM
    #      - 8: RC_UNKNOWN_CMD
    #      - 9: RC_WRITE_FAIL
    #      - 10: RC_READ_FAIL
    #      - 11: RC_LOW_VOLTAGE
    #      - 12: RC_NO_RESOURCES
    #      - 13: RC_INCOMPLETE_JOIN_INFO
    #      - 14: RC_NOT_FOUND
    #      - 15: RC_INVALID_VALUE
    #      - 16: RC_ACCESS_DENIED
    #      - 18: RC_ERASE_FAIL
    # - <tt>maxStCurrent</tt>: 2-byte field formatted as a int.<br/>
    #     There is no restriction on the value of this field.
    # - <tt>minLifetime</tt>: 1-byte field formatted as a int.<br/>
    #     There is no restriction on the value of this field.
    # - <tt>currentLimit_0</tt>: 2-byte field formatted as a int.<br/>
    #     There is no restriction on the value of this field.
    # - <tt>dischargePeriod_0</tt>: 2-byte field formatted as a int.<br/>
    #     There is no restriction on the value of this field.
    # - <tt>rechargePeriod_0</tt>: 2-byte field formatted as a int.<br/>
    #     There is no restriction on the value of this field.
    # - <tt>currentLimit_1</tt>: 2-byte field formatted as a int.<br/>
    #     There is no restriction on the value of this field.
    # - <tt>dischargePeriod_1</tt>: 2-byte field formatted as a int.<br/>
    #     There is no restriction on the value of this field.
    # - <tt>rechargePeriod_1</tt>: 2-byte field formatted as a int.<br/>
    #     There is no restriction on the value of this field.
    # - <tt>currentLimit_2</tt>: 2-byte field formatted as a int.<br/>
    #     There is no restriction on the value of this field.
    # - <tt>dischargePeriod_2</tt>: 2-byte field formatted as a int.<br/>
    #     There is no restriction on the value of this field.
    # - <tt>rechargePeriod_2</tt>: 2-byte field formatted as a int.<br/>
    #     There is no restriction on the value of this field.
    # 
    Tuple_dn_getParameter_powerSrcInfo = collections.namedtuple("Tuple_dn_getParameter_powerSrcInfo", ['RC', 'maxStCurrent', 'minLifetime', 'currentLimit_0', 'dischargePeriod_0', 'rechargePeriod_0', 'currentLimit_1', 'dischargePeriod_1', 'rechargePeriod_1', 'currentLimit_2', 'dischargePeriod_2', 'rechargePeriod_2'])

    ##
    # This command allows the microprocessor to read a mote's power source settings.
    # 
    # 
    # 
    # \returns The response to the command, formatted as a #Tuple_dn_getParameter_powerSrcInfo named tuple.
    # 
    def dn_getParameter_powerSrcInfo(self, ) :
        res = IpMoteConnectorInternal.send(self, ['getParameter', 'powerSrcInfo'], {})
        return IpMoteConnector.Tuple_dn_getParameter_powerSrcInfo(**res)

    ##
    # The named tuple returned by the dn_getParameter_autoJoin() function.
    # 
    # - <tt>RC</tt>: 1-byte field formatted as a int.<br/>
    #     This field can only take one of the following values:
    #      - 0: RC_OK
    #      - 1: RC_ERROR
    #      - 3: RC_BUSY
    #      - 4: RC_INVALID_LEN
    #      - 5: RC_INVALID_STATE
    #      - 6: RC_UNSUPPORTED
    #      - 7: RC_UNKNOWN_PARAM
    #      - 8: RC_UNKNOWN_CMD
    #      - 9: RC_WRITE_FAIL
    #      - 10: RC_READ_FAIL
    #      - 11: RC_LOW_VOLTAGE
    #      - 12: RC_NO_RESOURCES
    #      - 13: RC_INCOMPLETE_JOIN_INFO
    #      - 14: RC_NOT_FOUND
    #      - 15: RC_INVALID_VALUE
    #      - 16: RC_ACCESS_DENIED
    #      - 18: RC_ERASE_FAIL
    # - <tt>autoJoin</tt>: 1-byte field formatted as a bool.<br/>
    #     There is no restriction on the value of this field.
    # 
    Tuple_dn_getParameter_autoJoin = collections.namedtuple("Tuple_dn_getParameter_autoJoin", ['RC', 'autoJoin'])

    ##
    # This command allows the microprocessor to retrieve the current autoJoin setting.
    # 
    # 
    # 
    # \returns The response to the command, formatted as a #Tuple_dn_getParameter_autoJoin named tuple.
    # 
    def dn_getParameter_autoJoin(self, ) :
        res = IpMoteConnectorInternal.send(self, ['getParameter', 'autoJoin'], {})
        return IpMoteConnector.Tuple_dn_getParameter_autoJoin(**res)

    ##
    # The named tuple returned by the dn_getParameter_antGain() function.
    # 
    # - <tt>RC</tt>: 1-byte field formatted as a int.<br/>
    #     This field can only take one of the following values:
    #      - 0: RC_OK
    #      - 1: RC_ERROR
    #      - 3: RC_BUSY
    #      - 4: RC_INVALID_LEN
    #      - 5: RC_INVALID_STATE
    #      - 6: RC_UNSUPPORTED
    #      - 7: RC_UNKNOWN_PARAM
    #      - 8: RC_UNKNOWN_CMD
    #      - 9: RC_WRITE_FAIL
    #      - 10: RC_READ_FAIL
    #      - 11: RC_LOW_VOLTAGE
    #      - 12: RC_NO_RESOURCES
    #      - 13: RC_INCOMPLETE_JOIN_INFO
    #      - 14: RC_NOT_FOUND
    #      - 15: RC_INVALID_VALUE
    #      - 16: RC_ACCESS_DENIED
    #      - 18: RC_ERASE_FAIL
    # - <tt>antGain</tt>: 1-byte field formatted as a ints.<br/>
    #     There is no restriction on the value of this field.
    # 
    Tuple_dn_getParameter_antGain = collections.namedtuple("Tuple_dn_getParameter_antGain", ['RC', 'antGain'])

    ##
    # The getParameter<antGain> command retrieves the antenna gain used by the system (to properly calculate radiated power). Defaults to 2 dBi.
    # 
    # Note: This parameter is available in devices running mote software >=1.4.x
    # 
    # 
    # 
    # \returns The response to the command, formatted as a #Tuple_dn_getParameter_antGain named tuple.
    # 
    def dn_getParameter_antGain(self, ) :
        res = IpMoteConnectorInternal.send(self, ['getParameter', 'antGain'], {})
        return IpMoteConnector.Tuple_dn_getParameter_antGain(**res)

    ##
    # The named tuple returned by the dn_getParameter_euCompliantMode() function.
    # 
    # - <tt>RC</tt>: 1-byte field formatted as a int.<br/>
    #     This field can only take one of the following values:
    #      - 0: RC_OK
    #      - 1: RC_ERROR
    #      - 3: RC_BUSY
    #      - 4: RC_INVALID_LEN
    #      - 5: RC_INVALID_STATE
    #      - 6: RC_UNSUPPORTED
    #      - 7: RC_UNKNOWN_PARAM
    #      - 8: RC_UNKNOWN_CMD
    #      - 9: RC_WRITE_FAIL
    #      - 10: RC_READ_FAIL
    #      - 11: RC_LOW_VOLTAGE
    #      - 12: RC_NO_RESOURCES
    #      - 13: RC_INCOMPLETE_JOIN_INFO
    #      - 14: RC_NOT_FOUND
    #      - 15: RC_INVALID_VALUE
    #      - 16: RC_ACCESS_DENIED
    #      - 18: RC_ERASE_FAIL
    # - <tt>compMode</tt>: 1-byte field formatted as a int.<br/>
    #     There is no restriction on the value of this field.
    # 
    Tuple_dn_getParameter_euCompliantMode = collections.namedtuple("Tuple_dn_getParameter_euCompliantMode", ['RC', 'compMode'])

    ##
    # The getParameter<euCompliantMode> command may be used to retrieve the EN 300 328 compliance mode that is used by the device. When enabled, the mote may skip some transmit opportunities to remain within average power limits. Motes below +10 dBm radiated power do not need to duty cycle to meet EN 300 328 requirements.
    # 
    # Note: This parameter is available in devices running mote software >=1.4.x
    # 
    # 
    # 
    # \returns The response to the command, formatted as a #Tuple_dn_getParameter_euCompliantMode named tuple.
    # 
    def dn_getParameter_euCompliantMode(self, ) :
        res = IpMoteConnectorInternal.send(self, ['getParameter', 'euCompliantMode'], {})
        return IpMoteConnector.Tuple_dn_getParameter_euCompliantMode(**res)

    ##
    # The named tuple returned by the dn_getParameter_entropy() function.
    # 
    # - <tt>RC</tt>: 1-byte field formatted as a int.<br/>
    #     This field can only take one of the following values:
    #      - 0: RC_OK
    #      - 1: RC_ERROR
    #      - 3: RC_BUSY
    #      - 4: RC_INVALID_LEN
    #      - 5: RC_INVALID_STATE
    #      - 6: RC_UNSUPPORTED
    #      - 7: RC_UNKNOWN_PARAM
    #      - 8: RC_UNKNOWN_CMD
    #      - 9: RC_WRITE_FAIL
    #      - 10: RC_READ_FAIL
    #      - 11: RC_LOW_VOLTAGE
    #      - 12: RC_NO_RESOURCES
    #      - 13: RC_INCOMPLETE_JOIN_INFO
    #      - 14: RC_NOT_FOUND
    #      - 15: RC_INVALID_VALUE
    #      - 16: RC_ACCESS_DENIED
    #      - 18: RC_ERASE_FAIL
    # - <tt>entropy</tt>: 16-byte field formatted as a hex.<br/>
    #     There is no restriction on the value of this field.
    # 
    Tuple_dn_getParameter_entropy = collections.namedtuple("Tuple_dn_getParameter_entropy", ['RC', 'entropy'])

    ##
    # The getParameter<entropy> command may be used to retrieve a 16-byte block of random data. The data is obtained from thermal noise in the LTC5800 receive signal chain with the radio front-end disabled - as such, it can only be called when the mote is in the idle state. Thus while it is suitable for cryptographic operations, it is recommended to be used as a seed for a DRBG because of this limitation.
    # 
    # This parameter is available in devices running mote software 1.4.0 or later.
    # 
    # 
    # 
    # \returns The response to the command, formatted as a #Tuple_dn_getParameter_entropy named tuple.
    # 
    def dn_getParameter_entropy(self, ) :
        res = IpMoteConnectorInternal.send(self, ['getParameter', 'entropy'], {})
        return IpMoteConnector.Tuple_dn_getParameter_entropy(**res)

    ##
    # The named tuple returned by the dn_join() function.
    # 
    # - <tt>RC</tt>: 1-byte field formatted as a int.<br/>
    #     This field can only take one of the following values:
    #      - 0: RC_OK
    #      - 1: RC_ERROR
    #      - 3: RC_BUSY
    #      - 4: RC_INVALID_LEN
    #      - 5: RC_INVALID_STATE
    #      - 6: RC_UNSUPPORTED
    #      - 7: RC_UNKNOWN_PARAM
    #      - 8: RC_UNKNOWN_CMD
    #      - 9: RC_WRITE_FAIL
    #      - 10: RC_READ_FAIL
    #      - 11: RC_LOW_VOLTAGE
    #      - 12: RC_NO_RESOURCES
    #      - 13: RC_INCOMPLETE_JOIN_INFO
    #      - 14: RC_NOT_FOUND
    #      - 15: RC_INVALID_VALUE
    #      - 16: RC_ACCESS_DENIED
    #      - 18: RC_ERASE_FAIL
    # 
    Tuple_dn_join = collections.namedtuple("Tuple_dn_join", ['RC'])

    ##
    # The join command requests that mote start searching for the network and attempt to join.The mote must be in the Idle state or the Promiscuous Listen state (see search) for this command to be valid. Note that the join time will be affected by the maximum current setting.
    # 
    # 
    # 
    # \returns The response to the command, formatted as a #Tuple_dn_join named tuple.
    # 
    def dn_join(self, ) :
        res = IpMoteConnectorInternal.send(self, ['join'], {})
        return IpMoteConnector.Tuple_dn_join(**res)

    ##
    # The named tuple returned by the dn_disconnect() function.
    # 
    # - <tt>RC</tt>: 1-byte field formatted as a int.<br/>
    #     This field can only take one of the following values:
    #      - 0: RC_OK
    #      - 1: RC_ERROR
    #      - 3: RC_BUSY
    #      - 4: RC_INVALID_LEN
    #      - 5: RC_INVALID_STATE
    #      - 6: RC_UNSUPPORTED
    #      - 7: RC_UNKNOWN_PARAM
    #      - 8: RC_UNKNOWN_CMD
    #      - 9: RC_WRITE_FAIL
    #      - 10: RC_READ_FAIL
    #      - 11: RC_LOW_VOLTAGE
    #      - 12: RC_NO_RESOURCES
    #      - 13: RC_INCOMPLETE_JOIN_INFO
    #      - 14: RC_NOT_FOUND
    #      - 15: RC_INVALID_VALUE
    #      - 16: RC_ACCESS_DENIED
    #      - 18: RC_ERASE_FAIL
    # 
    Tuple_dn_disconnect = collections.namedtuple("Tuple_dn_disconnect", ['RC'])

    ##
    # The disconnect command requests that the mote initiate disconnection from the network. After disconnection completes, the mote will generate a disconnected event, and proceed to reset. If the mote is not in the network, the disconnected event will be generated immediately. This command will return an error if the mote is not presently joining or joined to a network.
    # 
    # 
    # 
    # \returns The response to the command, formatted as a #Tuple_dn_disconnect named tuple.
    # 
    def dn_disconnect(self, ) :
        res = IpMoteConnectorInternal.send(self, ['disconnect'], {})
        return IpMoteConnector.Tuple_dn_disconnect(**res)

    ##
    # The named tuple returned by the dn_reset() function.
    # 
    # - <tt>RC</tt>: 1-byte field formatted as a int.<br/>
    #     This field can only take one of the following values:
    #      - 0: RC_OK
    #      - 1: RC_ERROR
    #      - 3: RC_BUSY
    #      - 4: RC_INVALID_LEN
    #      - 5: RC_INVALID_STATE
    #      - 6: RC_UNSUPPORTED
    #      - 7: RC_UNKNOWN_PARAM
    #      - 8: RC_UNKNOWN_CMD
    #      - 9: RC_WRITE_FAIL
    #      - 10: RC_READ_FAIL
    #      - 11: RC_LOW_VOLTAGE
    #      - 12: RC_NO_RESOURCES
    #      - 13: RC_INCOMPLETE_JOIN_INFO
    #      - 14: RC_NOT_FOUND
    #      - 15: RC_INVALID_VALUE
    #      - 16: RC_ACCESS_DENIED
    #      - 18: RC_ERASE_FAIL
    # 
    Tuple_dn_reset = collections.namedtuple("Tuple_dn_reset", ['RC'])

    ##
    # The reset command initiates a soft-reset of the device. The device will initiate the reset sequence shortly after sending out the response to this command. Resetting a mote directly can adversely impact its descendants; to disconnect gracefully from the network, use the disconnect command
    # 
    # 
    # 
    # \returns The response to the command, formatted as a #Tuple_dn_reset named tuple.
    # 
    def dn_reset(self, ) :
        res = IpMoteConnectorInternal.send(self, ['reset'], {})
        return IpMoteConnector.Tuple_dn_reset(**res)

    ##
    # The named tuple returned by the dn_lowPowerSleep() function.
    # 
    # - <tt>RC</tt>: 1-byte field formatted as a int.<br/>
    #     This field can only take one of the following values:
    #      - 0: RC_OK
    #      - 1: RC_ERROR
    #      - 3: RC_BUSY
    #      - 4: RC_INVALID_LEN
    #      - 5: RC_INVALID_STATE
    #      - 6: RC_UNSUPPORTED
    #      - 7: RC_UNKNOWN_PARAM
    #      - 8: RC_UNKNOWN_CMD
    #      - 9: RC_WRITE_FAIL
    #      - 10: RC_READ_FAIL
    #      - 11: RC_LOW_VOLTAGE
    #      - 12: RC_NO_RESOURCES
    #      - 13: RC_INCOMPLETE_JOIN_INFO
    #      - 14: RC_NOT_FOUND
    #      - 15: RC_INVALID_VALUE
    #      - 16: RC_ACCESS_DENIED
    #      - 18: RC_ERASE_FAIL
    # 
    Tuple_dn_lowPowerSleep = collections.namedtuple("Tuple_dn_lowPowerSleep", ['RC'])

    ##
    # The lowPowerSleep command shuts down all peripherals and places the mote into deep sleep mode. The command executes after the mote sends its response. The mote enters deep sleep within two seconds after the command executes. The command may be issued at any time and will cause the mote to interrupt all in-progress network operation. To achieve a graceful disconnect, use the disconnect command before using the lowPowerSleep command. A hardware reset is required to bring a mote out of deep sleep mode.
    # 
    # 
    # 
    # \returns The response to the command, formatted as a #Tuple_dn_lowPowerSleep named tuple.
    # 
    def dn_lowPowerSleep(self, ) :
        res = IpMoteConnectorInternal.send(self, ['lowPowerSleep'], {})
        return IpMoteConnector.Tuple_dn_lowPowerSleep(**res)

    ##
    # The named tuple returned by the dn_testRadioRx() function.
    # 
    # - <tt>RC</tt>: 1-byte field formatted as a int.<br/>
    #     This field can only take one of the following values:
    #      - 0: RC_OK
    #      - 1: RC_ERROR
    #      - 3: RC_BUSY
    #      - 4: RC_INVALID_LEN
    #      - 5: RC_INVALID_STATE
    #      - 6: RC_UNSUPPORTED
    #      - 7: RC_UNKNOWN_PARAM
    #      - 8: RC_UNKNOWN_CMD
    #      - 9: RC_WRITE_FAIL
    #      - 10: RC_READ_FAIL
    #      - 11: RC_LOW_VOLTAGE
    #      - 12: RC_NO_RESOURCES
    #      - 13: RC_INCOMPLETE_JOIN_INFO
    #      - 14: RC_NOT_FOUND
    #      - 15: RC_INVALID_VALUE
    #      - 16: RC_ACCESS_DENIED
    #      - 18: RC_ERASE_FAIL
    # 
    Tuple_dn_testRadioRx = collections.namedtuple("Tuple_dn_testRadioRx", ['RC'])

    ##
    # The testRadioRx command clears all previously collected statistics and initiates a test of radio reception for the specified channel and duration. During the test, the mote keeps statistics about the number of packets received (with and without error). The test results may be retrieved using the getParameter<testRadioRxStats> command. The testRadioRx command may only be issued in Idle mode. The mote must be reset (either hardware or software reset) after radio tests are complete and prior to joining.
    # 
    # Station ID is available in IP Mote 1.4.0 or later, and WirelessHART Mote 1.1.2 or later. The station ID is a user selectable value used to isolate traffic if multiple tests are running in the same radio space. It must be set to match the station ID used by the transmitter.
    # 
    # 
    # 
    # Channel numbering is 0-15, corresponding to IEEE 2.4 GHz channels 11-26.
    # 
    # \param channelMask 2-byte field formatted as a hex.<br/>
    #     There is no restriction on the value of this field.
    # \param time 2-byte field formatted as a int.<br/>
    #     There is no restriction on the value of this field.
    # \param stationId 1-byte field formatted as a int.<br/>
    #     There is no restriction on the value of this field.
    # 
    # \returns The response to the command, formatted as a #Tuple_dn_testRadioRx named tuple.
    # 
    def dn_testRadioRx(self, channelMask, time, stationId) :
        res = IpMoteConnectorInternal.send(self, ['testRadioRx'], {"channelMask" : channelMask, "time" : time, "stationId" : stationId})
        return IpMoteConnector.Tuple_dn_testRadioRx(**res)

    ##
    # The named tuple returned by the dn_clearNV() function.
    # 
    # - <tt>RC</tt>: 1-byte field formatted as a int.<br/>
    #     This field can only take one of the following values:
    #      - 0: RC_OK
    #      - 1: RC_ERROR
    #      - 3: RC_BUSY
    #      - 4: RC_INVALID_LEN
    #      - 5: RC_INVALID_STATE
    #      - 6: RC_UNSUPPORTED
    #      - 7: RC_UNKNOWN_PARAM
    #      - 8: RC_UNKNOWN_CMD
    #      - 9: RC_WRITE_FAIL
    #      - 10: RC_READ_FAIL
    #      - 11: RC_LOW_VOLTAGE
    #      - 12: RC_NO_RESOURCES
    #      - 13: RC_INCOMPLETE_JOIN_INFO
    #      - 14: RC_NOT_FOUND
    #      - 15: RC_INVALID_VALUE
    #      - 16: RC_ACCESS_DENIED
    #      - 18: RC_ERASE_FAIL
    # 
    Tuple_dn_clearNV = collections.namedtuple("Tuple_dn_clearNV", ['RC'])

    ##
    # The clearNV command resets the motes non-volatile memory (NV) to its factory-default state. See User Guide for detailed information about the default values. Since many parameters are read by the mote only at power-up, this command should be followed up by mote reset.
    # 
    # 
    # 
    # \returns The response to the command, formatted as a #Tuple_dn_clearNV named tuple.
    # 
    def dn_clearNV(self, ) :
        res = IpMoteConnectorInternal.send(self, ['clearNV'], {})
        return IpMoteConnector.Tuple_dn_clearNV(**res)

    ##
    # The named tuple returned by the dn_requestService() function.
    # 
    # - <tt>RC</tt>: 1-byte field formatted as a int.<br/>
    #     This field can only take one of the following values:
    #      - 0: RC_OK
    #      - 1: RC_ERROR
    #      - 3: RC_BUSY
    #      - 4: RC_INVALID_LEN
    #      - 5: RC_INVALID_STATE
    #      - 6: RC_UNSUPPORTED
    #      - 7: RC_UNKNOWN_PARAM
    #      - 8: RC_UNKNOWN_CMD
    #      - 9: RC_WRITE_FAIL
    #      - 10: RC_READ_FAIL
    #      - 11: RC_LOW_VOLTAGE
    #      - 12: RC_NO_RESOURCES
    #      - 13: RC_INCOMPLETE_JOIN_INFO
    #      - 14: RC_NOT_FOUND
    #      - 15: RC_INVALID_VALUE
    #      - 16: RC_ACCESS_DENIED
    #      - 18: RC_ERASE_FAIL
    # 
    Tuple_dn_requestService = collections.namedtuple("Tuple_dn_requestService", ['RC'])

    ##
    # The requestService command may be used to request a new or changed service level to a destination device in the mesh. This command may only be used to update the service to a device with an existing connection (session).
    # 
    # Whenever a change in bandwidth assignment occurs, the application receives a serviceChanged event that it can use as a trigger to read the new service allocation.
    # 
    # \param destAddr 2-byte field formatted as a int.<br/>
    #     There is no restriction on the value of this field.
    # \param serviceType 1-byte field formatted as a int.<br/>
    #     This field can only take one of the following values:
    #      - 0: bandwidth
    # \param value 4-byte field formatted as a int.<br/>
    #     There is no restriction on the value of this field.
    # 
    # \returns The response to the command, formatted as a #Tuple_dn_requestService named tuple.
    # 
    def dn_requestService(self, destAddr, serviceType, value) :
        res = IpMoteConnectorInternal.send(self, ['requestService'], {"destAddr" : destAddr, "serviceType" : serviceType, "value" : value})
        return IpMoteConnector.Tuple_dn_requestService(**res)

    ##
    # The named tuple returned by the dn_getServiceInfo() function.
    # 
    # - <tt>RC</tt>: 1-byte field formatted as a int.<br/>
    #     This field can only take one of the following values:
    #      - 0: RC_OK
    #      - 1: RC_ERROR
    #      - 3: RC_BUSY
    #      - 4: RC_INVALID_LEN
    #      - 5: RC_INVALID_STATE
    #      - 6: RC_UNSUPPORTED
    #      - 7: RC_UNKNOWN_PARAM
    #      - 8: RC_UNKNOWN_CMD
    #      - 9: RC_WRITE_FAIL
    #      - 10: RC_READ_FAIL
    #      - 11: RC_LOW_VOLTAGE
    #      - 12: RC_NO_RESOURCES
    #      - 13: RC_INCOMPLETE_JOIN_INFO
    #      - 14: RC_NOT_FOUND
    #      - 15: RC_INVALID_VALUE
    #      - 16: RC_ACCESS_DENIED
    #      - 18: RC_ERASE_FAIL
    # - <tt>destAddr</tt>: 2-byte field formatted as a hex.<br/>
    #     There is no restriction on the value of this field.
    # - <tt>type</tt>: 1-byte field formatted as a int.<br/>
    #     This field can only take one of the following values:
    #      - 0: bandwidth
    # - <tt>state</tt>: 1-byte field formatted as a int.<br/>
    #     This field can only take one of the following values:
    #      - 0: completed
    #      - 1: pending
    # - <tt>value</tt>: 4-byte field formatted as a int.<br/>
    #     There is no restriction on the value of this field.
    # 
    Tuple_dn_getServiceInfo = collections.namedtuple("Tuple_dn_getServiceInfo", ['RC', 'destAddr', 'type', 'state', 'value'])

    ##
    # The getServiceInfo command returns information about the service currently allocated to the mote.
    # 
    # \param destAddr 2-byte field formatted as a int.<br/>
    #     There is no restriction on the value of this field.
    # \param type 1-byte field formatted as a int.<br/>
    #     This field can only take one of the following values:
    #      - 0: bandwidth
    # 
    # \returns The response to the command, formatted as a #Tuple_dn_getServiceInfo named tuple.
    # 
    def dn_getServiceInfo(self, destAddr, type) :
        res = IpMoteConnectorInternal.send(self, ['getServiceInfo'], {"destAddr" : destAddr, "type" : type})
        return IpMoteConnector.Tuple_dn_getServiceInfo(**res)

    ##
    # The named tuple returned by the dn_openSocket() function.
    # 
    # - <tt>RC</tt>: 1-byte field formatted as a int.<br/>
    #     This field can only take one of the following values:
    #      - 0: RC_OK
    #      - 1: RC_ERROR
    #      - 3: RC_BUSY
    #      - 4: RC_INVALID_LEN
    #      - 5: RC_INVALID_STATE
    #      - 6: RC_UNSUPPORTED
    #      - 7: RC_UNKNOWN_PARAM
    #      - 8: RC_UNKNOWN_CMD
    #      - 9: RC_WRITE_FAIL
    #      - 10: RC_READ_FAIL
    #      - 11: RC_LOW_VOLTAGE
    #      - 12: RC_NO_RESOURCES
    #      - 13: RC_INCOMPLETE_JOIN_INFO
    #      - 14: RC_NOT_FOUND
    #      - 15: RC_INVALID_VALUE
    #      - 16: RC_ACCESS_DENIED
    #      - 18: RC_ERASE_FAIL
    # - <tt>socketId</tt>: 1-byte field formatted as a int.<br/>
    #     There is no restriction on the value of this field.
    # 
    Tuple_dn_openSocket = collections.namedtuple("Tuple_dn_openSocket", ['RC', 'socketId'])

    ##
    # The openSocket command creates an endpoint for IP communication and returns an ID for the socket.
    # 
    # \param protocol 1-byte field formatted as a int.<br/>
    #     This field can only take one of the following values:
    #      - 0: udp
    # 
    # \returns The response to the command, formatted as a #Tuple_dn_openSocket named tuple.
    # 
    def dn_openSocket(self, protocol) :
        res = IpMoteConnectorInternal.send(self, ['openSocket'], {"protocol" : protocol})
        return IpMoteConnector.Tuple_dn_openSocket(**res)

    ##
    # The named tuple returned by the dn_closeSocket() function.
    # 
    # - <tt>RC</tt>: 1-byte field formatted as a int.<br/>
    #     This field can only take one of the following values:
    #      - 0: RC_OK
    #      - 1: RC_ERROR
    #      - 3: RC_BUSY
    #      - 4: RC_INVALID_LEN
    #      - 5: RC_INVALID_STATE
    #      - 6: RC_UNSUPPORTED
    #      - 7: RC_UNKNOWN_PARAM
    #      - 8: RC_UNKNOWN_CMD
    #      - 9: RC_WRITE_FAIL
    #      - 10: RC_READ_FAIL
    #      - 11: RC_LOW_VOLTAGE
    #      - 12: RC_NO_RESOURCES
    #      - 13: RC_INCOMPLETE_JOIN_INFO
    #      - 14: RC_NOT_FOUND
    #      - 15: RC_INVALID_VALUE
    #      - 16: RC_ACCESS_DENIED
    #      - 18: RC_ERASE_FAIL
    # 
    Tuple_dn_closeSocket = collections.namedtuple("Tuple_dn_closeSocket", ['RC'])

    ##
    # Close the previously open socket.
    # 
    # \param socketId 1-byte field formatted as a int.<br/>
    #     There is no restriction on the value of this field.
    # 
    # \returns The response to the command, formatted as a #Tuple_dn_closeSocket named tuple.
    # 
    def dn_closeSocket(self, socketId) :
        res = IpMoteConnectorInternal.send(self, ['closeSocket'], {"socketId" : socketId})
        return IpMoteConnector.Tuple_dn_closeSocket(**res)

    ##
    # The named tuple returned by the dn_bindSocket() function.
    # 
    # - <tt>RC</tt>: 1-byte field formatted as a int.<br/>
    #     This field can only take one of the following values:
    #      - 0: RC_OK
    #      - 1: RC_ERROR
    #      - 3: RC_BUSY
    #      - 4: RC_INVALID_LEN
    #      - 5: RC_INVALID_STATE
    #      - 6: RC_UNSUPPORTED
    #      - 7: RC_UNKNOWN_PARAM
    #      - 8: RC_UNKNOWN_CMD
    #      - 9: RC_WRITE_FAIL
    #      - 10: RC_READ_FAIL
    #      - 11: RC_LOW_VOLTAGE
    #      - 12: RC_NO_RESOURCES
    #      - 13: RC_INCOMPLETE_JOIN_INFO
    #      - 14: RC_NOT_FOUND
    #      - 15: RC_INVALID_VALUE
    #      - 16: RC_ACCESS_DENIED
    #      - 18: RC_ERASE_FAIL
    # 
    Tuple_dn_bindSocket = collections.namedtuple("Tuple_dn_bindSocket", ['RC'])

    ##
    # Bind a previously opened socket to a port. When a socket is created, it is only given a protocol family, but not assigned a port. This association must be performed before the socket can accept connections from other hosts.
    # 
    # \param socketId 1-byte field formatted as a int.<br/>
    #     There is no restriction on the value of this field.
    # \param port 2-byte field formatted as a int.<br/>
    #     There is no restriction on the value of this field.
    # 
    # \returns The response to the command, formatted as a #Tuple_dn_bindSocket named tuple.
    # 
    def dn_bindSocket(self, socketId, port) :
        res = IpMoteConnectorInternal.send(self, ['bindSocket'], {"socketId" : socketId, "port" : port})
        return IpMoteConnector.Tuple_dn_bindSocket(**res)

    ##
    # The named tuple returned by the dn_sendTo() function.
    # 
    # - <tt>RC</tt>: 1-byte field formatted as a int.<br/>
    #     This field can only take one of the following values:
    #      - 0: RC_OK
    #      - 1: RC_ERROR
    #      - 3: RC_BUSY
    #      - 4: RC_INVALID_LEN
    #      - 5: RC_INVALID_STATE
    #      - 6: RC_UNSUPPORTED
    #      - 7: RC_UNKNOWN_PARAM
    #      - 8: RC_UNKNOWN_CMD
    #      - 9: RC_WRITE_FAIL
    #      - 10: RC_READ_FAIL
    #      - 11: RC_LOW_VOLTAGE
    #      - 12: RC_NO_RESOURCES
    #      - 13: RC_INCOMPLETE_JOIN_INFO
    #      - 14: RC_NOT_FOUND
    #      - 15: RC_INVALID_VALUE
    #      - 16: RC_ACCESS_DENIED
    #      - 18: RC_ERASE_FAIL
    # 
    Tuple_dn_sendTo = collections.namedtuple("Tuple_dn_sendTo", ['RC'])

    ##
    # Send a packet into the network. If the command returns RC_OK, the mote has accepted the packet and has queued it up for transmission. A txDone notification will be issued when the packet has been sent, if and only if the packet ID passed in this command is different from 0xffff. You can set the packet ID to any value. The notification will contain the packet ID of the packet just sent, allowing association of the notification with a particular packet. The destination port should be in the range 0xF0B8-F0BF (61624-61631) to maximize payload.
    # 
    # \param socketId 1-byte field formatted as a int.<br/>
    #     There is no restriction on the value of this field.
    # \param destIP 16-byte field formatted as a hex.<br/>
    #     There is no restriction on the value of this field.
    # \param destPort 2-byte field formatted as a int.<br/>
    #     There is no restriction on the value of this field.
    # \param serviceType 1-byte field formatted as a int.<br/>
    #     This field can only take one of the following values:
    #      - 0: bandwidth
    # \param priority 1-byte field formatted as a int.<br/>
    #     This field can only take one of the following values:
    #      - 0: low
    #      - 1: medium
    #      - 2: high
    # \param packetId 2-byte field formatted as a int.<br/>
    #     There is no restriction on the value of this field.
    # \param payload None-byte field formatted as a hex.<br/>
    #     There is no restriction on the value of this field.
    # 
    # \returns The response to the command, formatted as a #Tuple_dn_sendTo named tuple.
    # 
    def dn_sendTo(self, socketId, destIP, destPort, serviceType, priority, packetId, payload) :
        res = IpMoteConnectorInternal.send(self, ['sendTo'], {"socketId" : socketId, "destIP" : destIP, "destPort" : destPort, "serviceType" : serviceType, "priority" : priority, "packetId" : packetId, "payload" : payload})
        return IpMoteConnector.Tuple_dn_sendTo(**res)

    ##
    # The named tuple returned by the dn_search() function.
    # 
    # - <tt>RC</tt>: 1-byte field formatted as a int.<br/>
    #     This field can only take one of the following values:
    #      - 0: RC_OK
    #      - 1: RC_ERROR
    #      - 3: RC_BUSY
    #      - 4: RC_INVALID_LEN
    #      - 5: RC_INVALID_STATE
    #      - 6: RC_UNSUPPORTED
    #      - 7: RC_UNKNOWN_PARAM
    #      - 8: RC_UNKNOWN_CMD
    #      - 9: RC_WRITE_FAIL
    #      - 10: RC_READ_FAIL
    #      - 11: RC_LOW_VOLTAGE
    #      - 12: RC_NO_RESOURCES
    #      - 13: RC_INCOMPLETE_JOIN_INFO
    #      - 14: RC_NOT_FOUND
    #      - 15: RC_INVALID_VALUE
    #      - 16: RC_ACCESS_DENIED
    #      - 18: RC_ERASE_FAIL
    # 
    Tuple_dn_search = collections.namedtuple("Tuple_dn_search", ['RC'])

    ##
    # The search command requests that mote start listening for advertisements and report those heard from any network without attempting to join. This is called the Promiscuous Listen state. The mote must be in the Idle state for this command to be valid. The search state can be exited by issuing the join command or the reset command.
    # 
    # 
    # 
    # \returns The response to the command, formatted as a #Tuple_dn_search named tuple.
    # 
    def dn_search(self, ) :
        res = IpMoteConnectorInternal.send(self, ['search'], {})
        return IpMoteConnector.Tuple_dn_search(**res)

    ##
    # The named tuple returned by the dn_testRadioTxExt() function.
    # 
    # - <tt>RC</tt>: 1-byte field formatted as a int.<br/>
    #     This field can only take one of the following values:
    #      - 0: RC_OK
    #      - 1: RC_ERROR
    #      - 3: RC_BUSY
    #      - 4: RC_INVALID_LEN
    #      - 5: RC_INVALID_STATE
    #      - 6: RC_UNSUPPORTED
    #      - 7: RC_UNKNOWN_PARAM
    #      - 8: RC_UNKNOWN_CMD
    #      - 9: RC_WRITE_FAIL
    #      - 10: RC_READ_FAIL
    #      - 11: RC_LOW_VOLTAGE
    #      - 12: RC_NO_RESOURCES
    #      - 13: RC_INCOMPLETE_JOIN_INFO
    #      - 14: RC_NOT_FOUND
    #      - 15: RC_INVALID_VALUE
    #      - 16: RC_ACCESS_DENIED
    #      - 18: RC_ERASE_FAIL
    # 
    Tuple_dn_testRadioTxExt = collections.namedtuple("Tuple_dn_testRadioTxExt", ['RC'])

    ##
    # The testRadioTxExt command allows the microprocessor to initiate a radio transmission test. This command may only be issued prior to the mote joining the network. Three types of transmission tests are supported:
    # 
    # - Packet transmission
    # - Continuous modulation
    # - Continuous wave (unmodulated signal)
    # 
    # In a packet transmission test, the mote generates a repeatCnt number of packet sequences. Each sequence consists of up to 10 packets with configurable size and delays. Each packet starts with a PHY preamble (5 bytes), followed by a PHY length field (1 byte), followed by data payload of up to 125 bytes, and finally a 2-byte 802.15.4 CRC at the end. Byte 0 of the payload contains stationId of the sender. Bytes 1 and 2 contain the packet number (in big-endian format) that increments with every packet transmitted. Bytes 3..N contain a counter (from 0..N-3) that increments with every byte inside payload. Transmissions occur on the set of channels defined by chanMask , selected inpseudo-randomorder.
    # 
    # In a continuous modulation test, the mote generates continuous pseudo-random modulated signal, centered at the specified channel. The test is stopped by resetting the mote.
    # 
    # In a continuous wave test, the mote generates an unmodulated tone, centered at the specified channel. The test tone is stopped by resetting the mote.
    # 
    # The testRadioTxExt command may only be issued when the mote is in Idle mode, prior to its joining the network. The mote must be reset (either hardware or software reset) after radio tests are complete and prior to joining.
    # 
    # The station ID is a user selectable value. It is used in packet tests so that a receiver can identify packets from this device in cases where there may be multiple tests running in the same radio space. This field is not used for CM or CW tests. See testRadioRX (SmartMesh IP) or testRadioRxExt (SmartMesh WirelessHART).
    # 
    # 
    # 
    # Channel numbering is 0-15, corresponding to IEEE 2.4 GHz channels 11-26.
    # 
    # \param testType 1-byte field formatted as a int.<br/>
    #     This field can only take one of the following values:
    #      - 0: packet
    #      - 1: cm
    #      - 2: cw
    #      - 3: pkcca
    # \param chanMask 2-byte field formatted as a hex.<br/>
    #     There is no restriction on the value of this field.
    # \param repeatCnt 2-byte field formatted as a int.<br/>
    #     There is no restriction on the value of this field.
    # \param txPower 1-byte field formatted as a ints.<br/>
    #     There is no restriction on the value of this field.
    # \param seqSize 1-byte field formatted as a int.<br/>
    #     This field can only take one of the following values:
    #      - 0: 0
    #      - 1: 1
    #      - 2: 2
    #      - 3: 3
    #      - 4: 4
    #      - 5: 5
    #      - 6: 6
    #      - 7: 7
    #      - 8: 8
    #      - 9: 9
    #      - 10: 10
    # \param pkLen_1 1-byte field formatted as a int.<br/>
    #     There is no restriction on the value of this field.
    # \param delay_1 2-byte field formatted as a int.<br/>
    #     There is no restriction on the value of this field.
    # \param pkLen_2 1-byte field formatted as a int.<br/>
    #     There is no restriction on the value of this field.
    # \param delay_2 2-byte field formatted as a int.<br/>
    #     There is no restriction on the value of this field.
    # \param pkLen_3 1-byte field formatted as a int.<br/>
    #     There is no restriction on the value of this field.
    # \param delay_3 2-byte field formatted as a int.<br/>
    #     There is no restriction on the value of this field.
    # \param pkLen_4 1-byte field formatted as a int.<br/>
    #     There is no restriction on the value of this field.
    # \param delay_4 2-byte field formatted as a int.<br/>
    #     There is no restriction on the value of this field.
    # \param pkLen_5 1-byte field formatted as a int.<br/>
    #     There is no restriction on the value of this field.
    # \param delay_5 2-byte field formatted as a int.<br/>
    #     There is no restriction on the value of this field.
    # \param pkLen_6 1-byte field formatted as a int.<br/>
    #     There is no restriction on the value of this field.
    # \param delay_6 2-byte field formatted as a int.<br/>
    #     There is no restriction on the value of this field.
    # \param pkLen_7 1-byte field formatted as a int.<br/>
    #     There is no restriction on the value of this field.
    # \param delay_7 2-byte field formatted as a int.<br/>
    #     There is no restriction on the value of this field.
    # \param pkLen_8 1-byte field formatted as a int.<br/>
    #     There is no restriction on the value of this field.
    # \param delay_8 2-byte field formatted as a int.<br/>
    #     There is no restriction on the value of this field.
    # \param pkLen_9 1-byte field formatted as a int.<br/>
    #     There is no restriction on the value of this field.
    # \param delay_9 2-byte field formatted as a int.<br/>
    #     There is no restriction on the value of this field.
    # \param pkLen_10 1-byte field formatted as a int.<br/>
    #     There is no restriction on the value of this field.
    # \param delay_10 2-byte field formatted as a int.<br/>
    #     There is no restriction on the value of this field.
    # \param stationId 1-byte field formatted as a int.<br/>
    #     There is no restriction on the value of this field.
    # 
    # \returns The response to the command, formatted as a #Tuple_dn_testRadioTxExt named tuple.
    # 
    def dn_testRadioTxExt(self, testType, chanMask, repeatCnt, txPower, seqSize, pkLen_1, delay_1, pkLen_2, delay_2, pkLen_3, delay_3, pkLen_4, delay_4, pkLen_5, delay_5, pkLen_6, delay_6, pkLen_7, delay_7, pkLen_8, delay_8, pkLen_9, delay_9, pkLen_10, delay_10, stationId) :
        res = IpMoteConnectorInternal.send(self, ['testRadioTxExt'], {"testType" : testType, "chanMask" : chanMask, "repeatCnt" : repeatCnt, "txPower" : txPower, "seqSize" : seqSize, "pkLen_1" : pkLen_1, "delay_1" : delay_1, "pkLen_2" : pkLen_2, "delay_2" : delay_2, "pkLen_3" : pkLen_3, "delay_3" : delay_3, "pkLen_4" : pkLen_4, "delay_4" : delay_4, "pkLen_5" : pkLen_5, "delay_5" : delay_5, "pkLen_6" : pkLen_6, "delay_6" : delay_6, "pkLen_7" : pkLen_7, "delay_7" : delay_7, "pkLen_8" : pkLen_8, "delay_8" : delay_8, "pkLen_9" : pkLen_9, "delay_9" : delay_9, "pkLen_10" : pkLen_10, "delay_10" : delay_10, "stationId" : stationId})
        return IpMoteConnector.Tuple_dn_testRadioTxExt(**res)

    ##
    # The named tuple returned by the dn_zeroize() function.
    # 
    # - <tt>RC</tt>: 1-byte field formatted as a int.<br/>
    #     This field can only take one of the following values:
    #      - 0: RC_OK
    #      - 1: RC_ERROR
    #      - 3: RC_BUSY
    #      - 4: RC_INVALID_LEN
    #      - 5: RC_INVALID_STATE
    #      - 6: RC_UNSUPPORTED
    #      - 7: RC_UNKNOWN_PARAM
    #      - 8: RC_UNKNOWN_CMD
    #      - 9: RC_WRITE_FAIL
    #      - 10: RC_READ_FAIL
    #      - 11: RC_LOW_VOLTAGE
    #      - 12: RC_NO_RESOURCES
    #      - 13: RC_INCOMPLETE_JOIN_INFO
    #      - 14: RC_NOT_FOUND
    #      - 15: RC_INVALID_VALUE
    #      - 16: RC_ACCESS_DENIED
    #      - 18: RC_ERASE_FAIL
    # 
    Tuple_dn_zeroize = collections.namedtuple("Tuple_dn_zeroize", ['RC'])

    ##
    # Zeroize (zeroise) command erases flash area that is used to store configuration parameters, such as join keys. This command is intended to satisfy zeroization requirement of FIPS-140 standard. After the command executes, the mote should be reset. Available in mote >= 1.4.x
    # 
    # The zeroize command will render the mote inoperable. It must be re-programmed via SPI or JTAG in order to be useable.
    # 
    # \param password 4-byte field formatted as a int.<br/>
    #     There is no restriction on the value of this field.
    # 
    # \returns The response to the command, formatted as a #Tuple_dn_zeroize named tuple.
    # 
    def dn_zeroize(self, password) :
        res = IpMoteConnectorInternal.send(self, ['zeroize'], {"password" : password})
        return IpMoteConnector.Tuple_dn_zeroize(**res)

    ##
    # The named tuple returned by the dn_socketInfo() function.
    # 
    # - <tt>RC</tt>: 1-byte field formatted as a int.<br/>
    #     This field can only take one of the following values:
    #      - 0: RC_OK
    #      - 1: RC_ERROR
    #      - 3: RC_BUSY
    #      - 4: RC_INVALID_LEN
    #      - 5: RC_INVALID_STATE
    #      - 6: RC_UNSUPPORTED
    #      - 7: RC_UNKNOWN_PARAM
    #      - 8: RC_UNKNOWN_CMD
    #      - 9: RC_WRITE_FAIL
    #      - 10: RC_READ_FAIL
    #      - 11: RC_LOW_VOLTAGE
    #      - 12: RC_NO_RESOURCES
    #      - 13: RC_INCOMPLETE_JOIN_INFO
    #      - 14: RC_NOT_FOUND
    #      - 15: RC_INVALID_VALUE
    #      - 16: RC_ACCESS_DENIED
    #      - 18: RC_ERASE_FAIL
    # - <tt>index</tt>: 1-byte field formatted as a int.<br/>
    #     There is no restriction on the value of this field.
    # - <tt>socketId</tt>: 1-byte field formatted as a int.<br/>
    #     There is no restriction on the value of this field.
    # - <tt>protocol</tt>: 1-byte field formatted as a int.<br/>
    #     There is no restriction on the value of this field.
    # - <tt>bindState</tt>: 1-byte field formatted as a int.<br/>
    #     There is no restriction on the value of this field.
    # - <tt>port</tt>: 2-byte field formatted as a int.<br/>
    #     There is no restriction on the value of this field.
    # 
    Tuple_dn_socketInfo = collections.namedtuple("Tuple_dn_socketInfo", ['RC', 'index', 'socketId', 'protocol', 'bindState', 'port'])

    ##
    # Retrieve information about a socket. Available in IP Mote 1.4.0 or later.
    # 
    # \param index 1-byte field formatted as a int.<br/>
    #     There is no restriction on the value of this field.
    # 
    # \returns The response to the command, formatted as a #Tuple_dn_socketInfo named tuple.
    # 
    def dn_socketInfo(self, index) :
        res = IpMoteConnectorInternal.send(self, ['socketInfo'], {"index" : index})
        return IpMoteConnector.Tuple_dn_socketInfo(**res)

    ##
    # The named tuple returned by the dn_blink() function.
    # 
    # - <tt>RC</tt>: 1-byte field formatted as a int.<br/>
    #     This field can only take one of the following values:
    #      - 0: RC_OK
    #      - 1: RC_ERROR
    #      - 3: RC_BUSY
    #      - 4: RC_INVALID_LEN
    #      - 5: RC_INVALID_STATE
    #      - 6: RC_UNSUPPORTED
    #      - 7: RC_UNKNOWN_PARAM
    #      - 8: RC_UNKNOWN_CMD
    #      - 9: RC_WRITE_FAIL
    #      - 10: RC_READ_FAIL
    #      - 11: RC_LOW_VOLTAGE
    #      - 12: RC_NO_RESOURCES
    #      - 13: RC_INCOMPLETE_JOIN_INFO
    #      - 14: RC_NOT_FOUND
    #      - 15: RC_INVALID_VALUE
    #      - 16: RC_ACCESS_DENIED
    #      - 18: RC_ERASE_FAIL
    # 
    Tuple_dn_blink = collections.namedtuple("Tuple_dn_blink", ['RC'])

    ##
    # Send a packet into the network without joining. The mote searches for a network and sends the packet. Optionally, the list of neighbors discovered during the search process is also sent, up to a maximum of four neighbors. If the discovered neighbor list is not included, the payload maximum size is 73B, and if the discovered neighbors are included, the maximum size is 58B.
    # 
    # Upon receiving a blink command, the mote will transition to the blink state and start searching for advertisements. When it hears an advertisement, it synchronizes and continues listening briefly in efforts to discover more neighbors. After this short timeout, the mote immediately sends the data packet to one of the discovered neighbors. If the blink command is called repeatedly to send consecutive packets, the mote does not search again unless the discovered neighbor list is requested.
    # 
    # When the mote successfully sends the packet, a txDone notification will be sent with status set to 0. If the mote cannot send the packet, e.g. if 60 seconds elapse without receiving a MAC-layer acknowledgement, a txDone notification is sent with status set to 1.
    # 
    # For Blink packets, the mote can only accept a single packet at a time. To send multiple packets, the application must wait for the txDone notification. The mote will return to low-power sleep when 60 seconds elapse without any MAC-layer acknowledgements, so to prevent the mote from sleeping, the application should send the packets much faster than this 60 second timeout. See the SmartMesh Embedded IP Manager API Guide for details on the manager-side blink notification.
    # 
    # The mote will stay in the blink state unless it is reset, OR a join command is issued. This was done so that the getTime command can be called at any time after at least one blink packet has been sent. Note that the clock is free-running since its last packet sent and will drift, however can be used as a relatively accurate clock source for many applications, if sending packets once a day for example.
    # 
    # \param fIncludeDscvNbrs 1-byte field formatted as a int.<br/>
    #     There is no restriction on the value of this field.
    # \param payload None-byte field formatted as a hex.<br/>
    #     There is no restriction on the value of this field.
    # 
    # \returns The response to the command, formatted as a #Tuple_dn_blink named tuple.
    # 
    def dn_blink(self, fIncludeDscvNbrs, payload) :
        res = IpMoteConnectorInternal.send(self, ['blink'], {"fIncludeDscvNbrs" : fIncludeDscvNbrs, "payload" : payload})
        return IpMoteConnector.Tuple_dn_blink(**res)

    ##
    # The named tuple returned by the dn_stopSearch() function.
    # 
    # - <tt>RC</tt>: 1-byte field formatted as a int.<br/>
    #     This field can only take one of the following values:
    #      - 0: RC_OK
    #      - 1: RC_ERROR
    #      - 3: RC_BUSY
    #      - 4: RC_INVALID_LEN
    #      - 5: RC_INVALID_STATE
    #      - 6: RC_UNSUPPORTED
    #      - 7: RC_UNKNOWN_PARAM
    #      - 8: RC_UNKNOWN_CMD
    #      - 9: RC_WRITE_FAIL
    #      - 10: RC_READ_FAIL
    #      - 11: RC_LOW_VOLTAGE
    #      - 12: RC_NO_RESOURCES
    #      - 13: RC_INCOMPLETE_JOIN_INFO
    #      - 14: RC_NOT_FOUND
    #      - 15: RC_INVALID_VALUE
    #      - 16: RC_ACCESS_DENIED
    #      - 18: RC_ERASE_FAIL
    # 
    Tuple_dn_stopSearch = collections.namedtuple("Tuple_dn_stopSearch", ['RC'])

    ##
    # The stopSearch command stops the search that was started either by the join or the search command. The mote must be in either Promiscuous Listen or Search state for this command to be valid. The mote goes back to Idle state when this command is received in a valid state. Available in Mote 1.4.0 or later.
    # 
    # 
    # 
    # \returns The response to the command, formatted as a #Tuple_dn_stopSearch named tuple.
    # 
    def dn_stopSearch(self, ) :
        res = IpMoteConnectorInternal.send(self, ['stopSearch'], {})
        return IpMoteConnector.Tuple_dn_stopSearch(**res)

    ##
    # The named tuple returned by the dn_testRadioRxPER() function.
    # 
    # - <tt>RC</tt>: 1-byte field formatted as a int.<br/>
    #     This field can only take one of the following values:
    #      - 0: RC_OK
    #      - 1: RC_ERROR
    #      - 3: RC_BUSY
    #      - 4: RC_INVALID_LEN
    #      - 5: RC_INVALID_STATE
    #      - 6: RC_UNSUPPORTED
    #      - 7: RC_UNKNOWN_PARAM
    #      - 8: RC_UNKNOWN_CMD
    #      - 9: RC_WRITE_FAIL
    #      - 10: RC_READ_FAIL
    #      - 11: RC_LOW_VOLTAGE
    #      - 12: RC_NO_RESOURCES
    #      - 13: RC_INCOMPLETE_JOIN_INFO
    #      - 14: RC_NOT_FOUND
    #      - 15: RC_INVALID_VALUE
    #      - 16: RC_ACCESS_DENIED
    #      - 18: RC_ERASE_FAIL
    # 
    Tuple_dn_testRadioRxPER = collections.namedtuple("Tuple_dn_testRadioRxPER", ['RC'])

    ##
    # The testRadioRxPER command initiates Packet Error Rate (PER) test in rx mode. This command may be issued only when mote is in Idle state.
    # 
    # This command is available in SmartMesh IP Stack version 1.4.2.5 or later
    # 
    # 
    # 
    # \returns The response to the command, formatted as a #Tuple_dn_testRadioRxPER named tuple.
    # 
    def dn_testRadioRxPER(self, ) :
        res = IpMoteConnectorInternal.send(self, ['testRadioRxPER'], {})
        return IpMoteConnector.Tuple_dn_testRadioRxPER(**res)

    ##
    # The named tuple returned by the dn_testRadioTxPER() function.
    # 
    # - <tt>RC</tt>: 1-byte field formatted as a int.<br/>
    #     This field can only take one of the following values:
    #      - 0: RC_OK
    #      - 1: RC_ERROR
    #      - 3: RC_BUSY
    #      - 4: RC_INVALID_LEN
    #      - 5: RC_INVALID_STATE
    #      - 6: RC_UNSUPPORTED
    #      - 7: RC_UNKNOWN_PARAM
    #      - 8: RC_UNKNOWN_CMD
    #      - 9: RC_WRITE_FAIL
    #      - 10: RC_READ_FAIL
    #      - 11: RC_LOW_VOLTAGE
    #      - 12: RC_NO_RESOURCES
    #      - 13: RC_INCOMPLETE_JOIN_INFO
    #      - 14: RC_NOT_FOUND
    #      - 15: RC_INVALID_VALUE
    #      - 16: RC_ACCESS_DENIED
    #      - 18: RC_ERASE_FAIL
    # 
    Tuple_dn_testRadioTxPER = collections.namedtuple("Tuple_dn_testRadioTxPER", ['RC'])

    ##
    # The testRadioTxPER command initiates Packet Error Rate (PER) test in tx mode. This command may be issued only when mote is in Idle state.
    # 
    # This command is available in SmartMesh IP Stack version 1.4.2.5 or later
    # 
    # \param txPower 1-byte field formatted as a ints.<br/>
    #     There is no restriction on the value of this field.
    # \param numPackets 2-byte field formatted as a int.<br/>
    #     There is no restriction on the value of this field.
    # \param chanMask 2-byte field formatted as a hex.<br/>
    #     There is no restriction on the value of this field.
    # \param numRepeat 2-byte field formatted as a int.<br/>
    #     There is no restriction on the value of this field.
    # 
    # \returns The response to the command, formatted as a #Tuple_dn_testRadioTxPER named tuple.
    # 
    def dn_testRadioTxPER(self, txPower, numPackets, chanMask, numRepeat) :
        res = IpMoteConnectorInternal.send(self, ['testRadioTxPER'], {"txPower" : txPower, "numPackets" : numPackets, "chanMask" : chanMask, "numRepeat" : numRepeat})
        return IpMoteConnector.Tuple_dn_testRadioTxPER(**res)

    #======================== notifications ===================================
    
    ##
    # Dictionary of all notification tuples.
    #
    notifTupleTable = {}
    
    ##
    # \brief TIMEINDICATION notification.
    # 
    # The timeIndication notification applies to mote products that support a time interrupt into the mote. The time packet includes the network time and the current UTC time relative to the manager.
    # 
    # For LTC5800-IPM based products, driving the TIMEn pin low (assert) wakes the processor. The pin must asserted for a minimum of t strobe s. De-asserting the pin latches the time, and a timeIndication will be generated within t response ms. Refer to the LTC5800-IPM Datasheet for additional information about TIME pin usage. The processor will remain awake and drawing current while the TIMEn pin is asserted. To avoid drawing excess current, take care to minimize the duration of the TIMEn pin being asserted past t strobe minimum.
    #
    # Formatted as a Tuple_timeIndication named tuple. It contains the following fields:
    #   - <tt>uptime</tt> 4-byte field formatted as a int.<br/>
    #     There is no restriction on the value of this field.
    #   - <tt>utcSecs</tt> 8-byte field formatted as a int.<br/>
    #     There is no restriction on the value of this field.
    #   - <tt>utcUsecs</tt> 4-byte field formatted as a int.<br/>
    #     There is no restriction on the value of this field.
    #   - <tt>asn</tt> 5-byte field formatted as a hex.<br/>
    #     There is no restriction on the value of this field.
    #   - <tt>asnOffset</tt> 2-byte field formatted as a int.<br/>
    #     There is no restriction on the value of this field.
    #   - <tt>asnSubOffset</tt> 2-byte field formatted as a int.<br/>
    #     There is no restriction on the value of this field.    
    # 
    TIMEINDICATION = "timeIndication"
    notifTupleTable[TIMEINDICATION] = Tuple_timeIndication = collections.namedtuple("Tuple_timeIndication", ['uptime', 'utcSecs', 'utcUsecs', 'asn', 'asnOffset', 'asnSubOffset'])

    ##
    # \brief EVENTS notification.
    # 
    # The mote sends an events notification to inform the application of new events that occurred since the previous events notification. The notification also contains up-to-date information about current mote state and any pending alarms.
    #
    # Formatted as a Tuple_events named tuple. It contains the following fields:
    #   - <tt>events</tt> 4-byte field formatted as a int.<br/>
    #     This field can only take one of the following values:
    #      - 1: boot
    #      - 2: alarmChange
    #      - 4: timeChange
    #      - 8: joinFail
    #      - 16: disconnected
    #      - 32: operational
    #      - 128: svcChange
    #      - 256: joinStarted
    #   - <tt>state</tt> 1-byte field formatted as a int.<br/>
    #     This field can only take one of the following values:
    #      - 0: init
    #      - 1: idle
    #      - 2: searching
    #      - 3: negotiating
    #      - 4: connected
    #      - 5: operational
    #      - 6: disconnected
    #      - 7: radiotest
    #      - 8: promiscuous listen
    #      - 9: blink
    #   - <tt>alarmsList</tt> 4-byte field formatted as a int.<br/>
    #     There is no restriction on the value of this field.    
    # 
    EVENTS = "events"
    notifTupleTable[EVENTS] = Tuple_events = collections.namedtuple("Tuple_events", ['events', 'state', 'alarmsList'])

    ##
    # \brief RECEIVE notification.
    # 
    # Informs the application that a packet was received.
    #
    # Formatted as a Tuple_receive named tuple. It contains the following fields:
    #   - <tt>socketId</tt> 1-byte field formatted as a int.<br/>
    #     There is no restriction on the value of this field.
    #   - <tt>srcAddr</tt> 16-byte field formatted as a hex.<br/>
    #     There is no restriction on the value of this field.
    #   - <tt>srcPort</tt> 2-byte field formatted as a int.<br/>
    #     There is no restriction on the value of this field.
    #   - <tt>payload</tt> None-byte field formatted as a hex.<br/>
    #     There is no restriction on the value of this field.    
    # 
    RECEIVE = "receive"
    notifTupleTable[RECEIVE] = Tuple_receive = collections.namedtuple("Tuple_receive", ['socketId', 'srcAddr', 'srcPort', 'payload'])

    ##
    # \brief MACRX notification.
    # 
    # 
    #
    # Formatted as a Tuple_macRx named tuple. It contains the following fields:
    #   - <tt>payload</tt> None-byte field formatted as a hex.<br/>
    #     There is no restriction on the value of this field.    
    # 
    MACRX = "macRx"
    notifTupleTable[MACRX] = Tuple_macRx = collections.namedtuple("Tuple_macRx", ['payload'])

    ##
    # \brief TXDONE notification.
    # 
    # The txDone notification informs the application that the mote has finished sending a packet. This notification will only be generated if the user has provided a valid (0x0000-0xFFFE) packet ID when calling the sendTo command.
    #
    # Formatted as a Tuple_txDone named tuple. It contains the following fields:
    #   - <tt>packetId</tt> 2-byte field formatted as a int.<br/>
    #     There is no restriction on the value of this field.
    #   - <tt>status</tt> 1-byte field formatted as a int.<br/>
    #     This field can only take one of the following values:
    #      - 0: ok
    #      - 1: fail    
    # 
    TXDONE = "txDone"
    notifTupleTable[TXDONE] = Tuple_txDone = collections.namedtuple("Tuple_txDone", ['packetId', 'status'])

    ##
    # \brief ADVRECEIVED notification.
    # 
    # The advReceived notification is generated by the mote w hen it is in Promiscuous Listen state (see the Mote States table) and it receives an advertisement.
    #
    # Formatted as a Tuple_advReceived named tuple. It contains the following fields:
    #   - <tt>netId</tt> 2-byte field formatted as a int.<br/>
    #     There is no restriction on the value of this field.
    #   - <tt>moteId</tt> 2-byte field formatted as a int.<br/>
    #     There is no restriction on the value of this field.
    #   - <tt>rssi</tt> 1-byte field formatted as a ints.<br/>
    #     There is no restriction on the value of this field.
    #   - <tt>joinPri</tt> 1-byte field formatted as a int.<br/>
    #     There is no restriction on the value of this field.    
    # 
    ADVRECEIVED = "advReceived"
    notifTupleTable[ADVRECEIVED] = Tuple_advReceived = collections.namedtuple("Tuple_advReceived", ['netId', 'moteId', 'rssi', 'joinPri'])

    ##
    # \brief TESTRADIOSTATSPER notification.
    # 
    # The testRadioStatsPER notification is generated by the mote when PER test in RX mode is completed.
    # 
    # This command is available in SmartMesh IP Stack version 1.4.2 or later.
    #
    # Formatted as a Tuple_testRadioStatsPER named tuple. It contains the following fields:
    #   - <tt>numRxOK</tt> 2-byte field formatted as a int.<br/>
    #     There is no restriction on the value of this field.
    #   - <tt>numRxErr</tt> 2-byte field formatted as a int.<br/>
    #     There is no restriction on the value of this field.
    #   - <tt>numRxInv</tt> 2-byte field formatted as a int.<br/>
    #     There is no restriction on the value of this field.
    #   - <tt>numRxMiss</tt> 2-byte field formatted as a int.<br/>
    #     There is no restriction on the value of this field.
    #   - <tt>perInt</tt> 2-byte field formatted as a int.<br/>
    #     There is no restriction on the value of this field.
    #   - <tt>perFrac</tt> 2-byte field formatted as a int.<br/>
    #     There is no restriction on the value of this field.    
    # 
    TESTRADIOSTATSPER = "testRadioStatsPER"
    notifTupleTable[TESTRADIOSTATSPER] = Tuple_testRadioStatsPER = collections.namedtuple("Tuple_testRadioStatsPER", ['numRxOK', 'numRxErr', 'numRxInv', 'numRxMiss', 'perInt', 'perFrac'])

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
            if  IpMoteConnector.notifTupleTable[ids[-1]] :
                return (ids[-1], IpMoteConnector.notifTupleTable[ids[-1]](**param))
            else :
                return (ids[-1], None)
        except KeyError :
            raise ApiException.NotificationError(ids, param)

##
# end of IpMoteConnector
# \}
# 
