'''
This module was generated automatically. Do not edit directly.
'''

import collections
from   SmartMeshSDK import ApiException
from   HartMoteConnectorInternal import HartMoteConnectorInternal

##
# \addtogroup HartMoteConnector
# \{
# 

class HartMoteConnector(HartMoteConnectorInternal):
    '''
    \brief Public class for the HART Mote connector, over Serial.
    '''

    #======================== commands ========================================

    ##
    # The named tuple returned by the dn_setParameter_txPower() function.
    # 
    # - <tt>RC</tt>: 1-byte field formatted as a int.<br/>
    #     This field can only take one of the following values:
    #      - 0: RC_OK
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
    #      - 18: RC_OPEN_FAIL
    #      - 19: RC_ERASE_FAIL
    # 
    Tuple_dn_setParameter_txPower = collections.namedtuple("Tuple_dn_setParameter_txPower", ['RC'])

    ##
    # The setParameter<txPower> command sets the mote conducted RF output power. Refer to product datasheets for supported RF output power values. For example, if the mote has a typical RF output power of +8 dBm when the Power Amplifier (PA) is enabled, set the txPower parameter to 8 to enable the PA. Similarly, if the mote has a typical RF output power of -2 dBm when the PA is disabled, then set the txPower parameter to -2 to turn off the PA. Note that this value is the RF output power coming out of the mote and not the radiated power coming out of the antenna. This command may be issued at any time and takes effect upon the next transmission.
    # 
    # \param txPower 1-byte field formatted as a ints.<br/>
    #     There is no restriction on the value of this field.
    # 
    # \returns The response to the command, formatted as a #Tuple_dn_setParameter_txPower named tuple.
    # 
    def dn_setParameter_txPower(self, txPower) :
        res = HartMoteConnectorInternal.send(self, ['setParameter', 'txPower'], {"txPower" : txPower})
        return HartMoteConnector.Tuple_dn_setParameter_txPower(**res)

    ##
    # The named tuple returned by the dn_setParameter_joinDutyCycle() function.
    # 
    # - <tt>RC</tt>: 1-byte field formatted as a int.<br/>
    #     This field can only take one of the following values:
    #      - 0: RC_OK
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
    #      - 18: RC_OPEN_FAIL
    #      - 19: RC_ERASE_FAIL
    # 
    Tuple_dn_setParameter_joinDutyCycle = collections.namedtuple("Tuple_dn_setParameter_joinDutyCycle", ['RC'])

    ##
    # The setParameter<joinDutyCycle> command allows the microprocessor to control the join duty cycle the ratio of active listen time to doze time (a low-power radio state) during the period when the mote is searching for the network. The default duty cycle enables the mote to join the network at a reasonable rate without using excessive battery power. If you desire a faster join time at the cost of higher power consumption, use the setParameter<joinDutyCycle> command to increase the join duty cycle up to 100%. Note that the setParameter<joinDutyCycle> command is not persistent and stays in effect only until reset. For power consumption information, refer to the mote product datasheet.
    # 
    # This command may be issued multiple times during the joining process. This command is only effective when the mote is in the Idle and Searching states.
    # 
    # \param dutyCycle 1-byte field formatted as a int.<br/>
    #     There is no restriction on the value of this field.
    # 
    # \returns The response to the command, formatted as a #Tuple_dn_setParameter_joinDutyCycle named tuple.
    # 
    def dn_setParameter_joinDutyCycle(self, dutyCycle) :
        res = HartMoteConnectorInternal.send(self, ['setParameter', 'joinDutyCycle'], {"dutyCycle" : dutyCycle})
        return HartMoteConnector.Tuple_dn_setParameter_joinDutyCycle(**res)

    ##
    # The named tuple returned by the dn_setParameter_batteryLife() function.
    # 
    # - <tt>RC</tt>: 1-byte field formatted as a int.<br/>
    #     This field can only take one of the following values:
    #      - 0: RC_OK
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
    #      - 18: RC_OPEN_FAIL
    #      - 19: RC_ERASE_FAIL
    # 
    Tuple_dn_setParameter_batteryLife = collections.namedtuple("Tuple_dn_setParameter_batteryLife", ['RC'])

    ##
    # The setParameter<batteryLife> command allows the microprocessor to update the remaining battery life information that the mote reports to WirelessHART Gateway in Command 778. This parameter must be set during the Idle state prior to joining, and should be updated periodically throughout operation. This parameter is only used in WirelessHART-compliant devices.
    # 
    # Command 778 is deprecated in version 7.4 of the HART specification as most existing gateways do not use battery life information.
    # 
    # \param batteryLife 2-byte field formatted as a int.<br/>
    #     There is no restriction on the value of this field.
    # \param powerStatus 1-byte field formatted as a int.<br/>
    #     This field can only take one of the following values:
    #      - 0: Nominal
    #      - 1: Low
    #      - 2: Critically low
    #      - 3: Recharging low
    #      - 4: Recharging high
    # 
    # \returns The response to the command, formatted as a #Tuple_dn_setParameter_batteryLife named tuple.
    # 
    def dn_setParameter_batteryLife(self, batteryLife, powerStatus) :
        res = HartMoteConnectorInternal.send(self, ['setParameter', 'batteryLife'], {"batteryLife" : batteryLife, "powerStatus" : powerStatus})
        return HartMoteConnector.Tuple_dn_setParameter_batteryLife(**res)

    ##
    # The named tuple returned by the dn_setParameter_service() function.
    # 
    # - <tt>RC</tt>: 1-byte field formatted as a int.<br/>
    #     This field can only take one of the following values:
    #      - 0: RC_OK
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
    #      - 18: RC_OPEN_FAIL
    #      - 19: RC_ERASE_FAIL
    # - <tt>numServices</tt>: 1-byte field formatted as a int.<br/>
    #     There is no restriction on the value of this field.
    # 
    Tuple_dn_setParameter_service = collections.namedtuple("Tuple_dn_setParameter_service", ['RC', 'numServices'])

    ##
    # The setParameter<service> command is used to request new device-originated bandwidth services and modify existing device-initiated services (now called "Timetables" in WirelessHART 7.4). Calling this command updates the motes internal service table, which later initiates a request to the network manager for bandwidth allocation. A subsequent serviceIndication notification will be sent indicating the response from the network manager. The getParameter<service> command may be used to read the service table, including the state of the service request.
    # 
    # The setParameter<service> command may be sent at any time. If the network manager rejects a service request, the microprocessor can try again by re-issuing the setParameter<service> command.
    # 
    # To delete a service, set the time field of the desired service to zero. Service request flags, application domain, and destination address are ignored by the mote when time equals zero.
    # 
    # Normally all service requests are compared against the power limits set with the setNVParameter<powerInfo> command. Services that would cause the device to exceed its power budget are denied. In Manager 4.1.1, a service request of 1 ms will result in the manager respecting the power limit for publish services, but will allow a block-transfer service requests (see the SmartMesh WirelessHART User's Guide section on Services) that would result in a fast pipe being activated.
    # 
    # \param serviceId 1-byte field formatted as a int.<br/>
    #     There is no restriction on the value of this field.
    # \param serviceReqFlags 1-byte field formatted as a int.<br/>
    #     There is no restriction on the value of this field.
    # \param appDomain 1-byte field formatted as a int.<br/>
    #     This field can only take one of the following values:
    #      - 0: Publish
    #      - 1: Event
    #      - 2: Maintenance
    #      - 3: Block transfer
    # \param destAddr 2-byte field formatted as a hex.<br/>
    #     There is no restriction on the value of this field.
    # \param time 4-byte field formatted as a int.<br/>
    #     There is no restriction on the value of this field.
    # 
    # \returns The response to the command, formatted as a #Tuple_dn_setParameter_service named tuple.
    # 
    def dn_setParameter_service(self, serviceId, serviceReqFlags, appDomain, destAddr, time) :
        res = HartMoteConnectorInternal.send(self, ['setParameter', 'service'], {"serviceId" : serviceId, "serviceReqFlags" : serviceReqFlags, "appDomain" : appDomain, "destAddr" : destAddr, "time" : time})
        return HartMoteConnector.Tuple_dn_setParameter_service(**res)

    ##
    # The named tuple returned by the dn_setParameter_hartDeviceStatus() function.
    # 
    # - <tt>RC</tt>: 1-byte field formatted as a int.<br/>
    #     This field can only take one of the following values:
    #      - 0: RC_OK
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
    #      - 18: RC_OPEN_FAIL
    #      - 19: RC_ERASE_FAIL
    # 
    Tuple_dn_setParameter_hartDeviceStatus = collections.namedtuple("Tuple_dn_setParameter_hartDeviceStatus", ['RC'])

    ##
    # The setParameter<hartDeviceStatus> command sets the current status of a WirelessHART device. The value passed in this parameter is used in all subsequent WirelessHART communications between the mote and the manager. This command is only required for WirelessHART-compliant devices. Refer to the HART Command Specifications for the appropriate value to use.
    # 
    # \param hartDevStatus 1-byte field formatted as a int.<br/>
    #     There is no restriction on the value of this field.
    # \param hartExtDevStatus 1-byte field formatted as a int.<br/>
    #     There is no restriction on the value of this field.
    # 
    # \returns The response to the command, formatted as a #Tuple_dn_setParameter_hartDeviceStatus named tuple.
    # 
    def dn_setParameter_hartDeviceStatus(self, hartDevStatus, hartExtDevStatus) :
        res = HartMoteConnectorInternal.send(self, ['setParameter', 'hartDeviceStatus'], {"hartDevStatus" : hartDevStatus, "hartExtDevStatus" : hartExtDevStatus})
        return HartMoteConnector.Tuple_dn_setParameter_hartDeviceStatus(**res)

    ##
    # The named tuple returned by the dn_setParameter_hartDeviceInfo() function.
    # 
    # - <tt>RC</tt>: 1-byte field formatted as a int.<br/>
    #     This field can only take one of the following values:
    #      - 0: RC_OK
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
    #      - 18: RC_OPEN_FAIL
    #      - 19: RC_ERASE_FAIL
    # 
    Tuple_dn_setParameter_hartDeviceInfo = collections.namedtuple("Tuple_dn_setParameter_hartDeviceInfo", ['RC'])

    ##
    # The setParameter<hartDeviceInfo> command is used to set HART device information that the mote passes to gateway during join. This command must be issued prior to join. This command is only required for WirelessHART-compliant devices. Note that the contents of this command are not validated by mote.
    # 
    # \param hartCmd0 22-byte field formatted as a hex.<br/>
    #     There is no restriction on the value of this field.
    # \param hartCmd20 32-byte field formatted as a hex.<br/>
    #     There is no restriction on the value of this field.
    # 
    # \returns The response to the command, formatted as a #Tuple_dn_setParameter_hartDeviceInfo named tuple.
    # 
    def dn_setParameter_hartDeviceInfo(self, hartCmd0, hartCmd20) :
        res = HartMoteConnectorInternal.send(self, ['setParameter', 'hartDeviceInfo'], {"hartCmd0" : hartCmd0, "hartCmd20" : hartCmd20})
        return HartMoteConnector.Tuple_dn_setParameter_hartDeviceInfo(**res)

    ##
    # The named tuple returned by the dn_setParameter_eventMask() function.
    # 
    # - <tt>RC</tt>: 1-byte field formatted as a int.<br/>
    #     This field can only take one of the following values:
    #      - 0: RC_OK
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
    #      - 18: RC_OPEN_FAIL
    #      - 19: RC_ERASE_FAIL
    # 
    Tuple_dn_setParameter_eventMask = collections.namedtuple("Tuple_dn_setParameter_eventMask", ['RC'])

    ##
    # The setParameter<eventMask> command allows the microprocessor to subscribe to the types of events that may be sent in the motes events notification message. This command may be called at any time and takes effect at the next event notification. The mote includes an event in the notification message if the corresponding bit in <eventMask> is set to 1, and excludes the event if the bit is set to 0. At mote reset, the default value of <eventMask> is 1 for all events.
    # 
    # New event type may be added in future revisions of mote software. It is recommended that the client code only subscribe to known events and gracefully ignore all unknown events.
    # 
    # \param eventMask 4-byte field formatted as a int.<br/>
    #     There is no restriction on the value of this field.
    # 
    # \returns The response to the command, formatted as a #Tuple_dn_setParameter_eventMask named tuple.
    # 
    def dn_setParameter_eventMask(self, eventMask) :
        res = HartMoteConnectorInternal.send(self, ['setParameter', 'eventMask'], {"eventMask" : eventMask})
        return HartMoteConnector.Tuple_dn_setParameter_eventMask(**res)

    ##
    # The named tuple returned by the dn_setParameter_writeProtect() function.
    # 
    # - <tt>RC</tt>: 1-byte field formatted as a int.<br/>
    #     This field can only take one of the following values:
    #      - 0: RC_OK
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
    #      - 18: RC_OPEN_FAIL
    #      - 19: RC_ERASE_FAIL
    # 
    Tuple_dn_setParameter_writeProtect = collections.namedtuple("Tuple_dn_setParameter_writeProtect", ['RC'])

    ##
    # The setParameter<writeProtect> command allows the microprocessor to enable or disable access to selected WirelessHART commands via wireless or the hartPayload command. Refer to the SmartMesh WirelessHART User's Guide for the list of affected commands. If writeProtect is enabled and the mote receives any of these commands (either via wireless connection or via the hartPayload command), the command will have no effect, and the mote will return RC_7 (In Write Protect Mode). At mote boot, writeProtect is set to 0 (writes allowed). The current status of writeProtect may be read via the getParameter<moteStatus> command. This command is for WirelessHART-compliant devices only.
    # 
    # \param writeProtect 1-byte field formatted as a int.<br/>
    #     This field can only take one of the following values:
    #      - 0: Write allowed
    #      - 1: Write not allowed
    # 
    # \returns The response to the command, formatted as a #Tuple_dn_setParameter_writeProtect named tuple.
    # 
    def dn_setParameter_writeProtect(self, writeProtect) :
        res = HartMoteConnectorInternal.send(self, ['setParameter', 'writeProtect'], {"writeProtect" : writeProtect})
        return HartMoteConnector.Tuple_dn_setParameter_writeProtect(**res)

    ##
    # The named tuple returned by the dn_setParameter_lock() function.
    # 
    # - <tt>RC</tt>: 1-byte field formatted as a int.<br/>
    #     This field can only take one of the following values:
    #      - 0: RC_OK
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
    #      - 18: RC_OPEN_FAIL
    #      - 19: RC_ERASE_FAIL
    # 
    Tuple_dn_setParameter_lock = collections.namedtuple("Tuple_dn_setParameter_lock", ['RC'])

    ##
    # The setParameter<lock> command locks/unlocks select HART commands (ones that affect the configuration changed flag) to a specific master (GW or serial maintenance port) to prevent the other master from changing it. This command is intended for use when the lock is temporary, i.e. it does not persist through power cycle or reset. For nonvolatile locking, use the setNVParameter<lock> command. Note: This parameter is available in devices running mote software >= 1.1.0
    # 
    # \param code 1-byte field formatted as a int.<br/>
    #     There is no restriction on the value of this field.
    # \param master 2-byte field formatted as a int.<br/>
    #     There is no restriction on the value of this field.
    # 
    # \returns The response to the command, formatted as a #Tuple_dn_setParameter_lock named tuple.
    # 
    def dn_setParameter_lock(self, code, master) :
        res = HartMoteConnectorInternal.send(self, ['setParameter', 'lock'], {"code" : code, "master" : master})
        return HartMoteConnector.Tuple_dn_setParameter_lock(**res)

    ##
    # The named tuple returned by the dn_getParameter_joinDutyCycle() function.
    # 
    # - <tt>RC</tt>: 1-byte field formatted as a int.<br/>
    #     This field can only take one of the following values:
    #      - 0: RC_OK
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
    #      - 18: RC_OPEN_FAIL
    #      - 19: RC_ERASE_FAIL
    # - <tt>joinDutyCycle</tt>: 1-byte field formatted as a int.<br/>
    #     There is no restriction on the value of this field.
    # 
    Tuple_dn_getParameter_joinDutyCycle = collections.namedtuple("Tuple_dn_getParameter_joinDutyCycle", ['RC', 'joinDutyCycle'])

    ##
    # The getParameter<joinDutyCycle> command return mote's join duty cycle, which determines the percentage of time the mote spends in radio receive mode while searching for network. The value of join duty cycle is expressed in increments of 1/255th of 100%, where 0 corresponds to 0% and 255 corresponds to 100%.
    # 
    # 
    # 
    # \returns The response to the command, formatted as a #Tuple_dn_getParameter_joinDutyCycle named tuple.
    # 
    def dn_getParameter_joinDutyCycle(self, ) :
        res = HartMoteConnectorInternal.send(self, ['getParameter', 'joinDutyCycle'], {})
        return HartMoteConnector.Tuple_dn_getParameter_joinDutyCycle(**res)

    ##
    # The named tuple returned by the dn_getParameter_service() function.
    # 
    # - <tt>RC</tt>: 1-byte field formatted as a int.<br/>
    #     This field can only take one of the following values:
    #      - 0: RC_OK
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
    #      - 18: RC_OPEN_FAIL
    #      - 19: RC_ERASE_FAIL
    # - <tt>serviceId</tt>: 1-byte field formatted as a int.<br/>
    #     There is no restriction on the value of this field.
    # - <tt>serviceState</tt>: 1-byte field formatted as a int.<br/>
    #     This field can only take one of the following values:
    #      - 0: Inactive
    #      - 1: Active
    #      - 2: Requested
    # - <tt>serviceFlags</tt>: 1-byte field formatted as a int.<br/>
    #     There is no restriction on the value of this field.
    # - <tt>appDomain</tt>: 1-byte field formatted as a int.<br/>
    #     This field can only take one of the following values:
    #      - 0: Publish
    #      - 1: Event
    #      - 2: Maintenance
    #      - 3: Block transfer
    # - <tt>destAddr</tt>: 2-byte field formatted as a hex.<br/>
    #     There is no restriction on the value of this field.
    # - <tt>time</tt>: 4-byte field formatted as a int.<br/>
    #     There is no restriction on the value of this field.
    # 
    Tuple_dn_getParameter_service = collections.namedtuple("Tuple_dn_getParameter_service", ['RC', 'serviceId', 'serviceState', 'serviceFlags', 'appDomain', 'destAddr', 'time'])

    ##
    # The getParameter<service> command retrieves information about the service allocation that is currently available to the field device. Services (now called "Timetables" in WirelessHART 7.4) in the range 0x00-7F are those requested by the device, and those in the range 0x80-FF are assigned independently by the network manager.
    # 
    # \param serviceId 1-byte field formatted as a int.<br/>
    #     There is no restriction on the value of this field.
    # 
    # \returns The response to the command, formatted as a #Tuple_dn_getParameter_service named tuple.
    # 
    def dn_getParameter_service(self, serviceId) :
        res = HartMoteConnectorInternal.send(self, ['getParameter', 'service'], {"serviceId" : serviceId})
        return HartMoteConnector.Tuple_dn_getParameter_service(**res)

    ##
    # The named tuple returned by the dn_getParameter_moteInfo() function.
    # 
    # - <tt>RC</tt>: 1-byte field formatted as a int.<br/>
    #     This field can only take one of the following values:
    #      - 0: RC_OK
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
    #      - 18: RC_OPEN_FAIL
    #      - 19: RC_ERASE_FAIL
    # - <tt>apiVersion</tt>: 1-byte field formatted as a int.<br/>
    #     There is no restriction on the value of this field.
    # - <tt>serialNum</tt>: 8-byte field formatted as a hex.<br/>
    #     There is no restriction on the value of this field.
    # - <tt>hwModel</tt>: 1-byte field formatted as a int.<br/>
    #     There is no restriction on the value of this field.
    # - <tt>hwRev</tt>: 1-byte field formatted as a int.<br/>
    #     There is no restriction on the value of this field.
    # - <tt>swMajorRev</tt>: 1-byte field formatted as a int.<br/>
    #     There is no restriction on the value of this field.
    # - <tt>swMinorRev</tt>: 1-byte field formatted as a int.<br/>
    #     There is no restriction on the value of this field.
    # - <tt>swPatch</tt>: 1-byte field formatted as a int.<br/>
    #     There is no restriction on the value of this field.
    # - <tt>swBuild</tt>: 2-byte field formatted as a int.<br/>
    #     There is no restriction on the value of this field.
    # 
    Tuple_dn_getParameter_moteInfo = collections.namedtuple("Tuple_dn_getParameter_moteInfo", ['RC', 'apiVersion', 'serialNum', 'hwModel', 'hwRev', 'swMajorRev', 'swMinorRev', 'swPatch', 'swBuild'])

    ##
    # The getParameter<moteInfo> command returns static information about the motes hardware and software. Note that network state-related information about the mote may be retrieved using getParameter<networkInfo>.
    # 
    # 
    # 
    # \returns The response to the command, formatted as a #Tuple_dn_getParameter_moteInfo named tuple.
    # 
    def dn_getParameter_moteInfo(self, ) :
        res = HartMoteConnectorInternal.send(self, ['getParameter', 'moteInfo'], {})
        return HartMoteConnector.Tuple_dn_getParameter_moteInfo(**res)

    ##
    # The named tuple returned by the dn_getParameter_networkInfo() function.
    # 
    # - <tt>RC</tt>: 1-byte field formatted as a int.<br/>
    #     This field can only take one of the following values:
    #      - 0: RC_OK
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
    #      - 18: RC_OPEN_FAIL
    #      - 19: RC_ERASE_FAIL
    # - <tt>macAddress</tt>: 8-byte field formatted as a hex.<br/>
    #     There is no restriction on the value of this field.
    # - <tt>moteId</tt>: 2-byte field formatted as a int.<br/>
    #     There is no restriction on the value of this field.
    # - <tt>networkId</tt>: 2-byte field formatted as a int.<br/>
    #     There is no restriction on the value of this field.
    # 
    Tuple_dn_getParameter_networkInfo = collections.namedtuple("Tuple_dn_getParameter_networkInfo", ['RC', 'macAddress', 'moteId', 'networkId'])

    ##
    # The getParameter<networkInfo> command may be used to retrieve the mote's network-related parameters. Note that static information about the motes hardware and software may be retrieved using getParameter<moteInfo>.
    # 
    # 
    # 
    # \returns The response to the command, formatted as a #Tuple_dn_getParameter_networkInfo named tuple.
    # 
    def dn_getParameter_networkInfo(self, ) :
        res = HartMoteConnectorInternal.send(self, ['getParameter', 'networkInfo'], {})
        return HartMoteConnector.Tuple_dn_getParameter_networkInfo(**res)

    ##
    # The named tuple returned by the dn_getParameter_moteStatus() function.
    # 
    # - <tt>RC</tt>: 1-byte field formatted as a int.<br/>
    #     This field can only take one of the following values:
    #      - 0: RC_OK
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
    #      - 18: RC_OPEN_FAIL
    #      - 19: RC_ERASE_FAIL
    # - <tt>state</tt>: 1-byte field formatted as a int.<br/>
    #     This field can only take one of the following values:
    #      - 0: Init
    #      - 1: Idle
    #      - 2: Searching
    #      - 3: Negotiating
    #      - 4: Connected
    #      - 5: Operational
    #      - 6: Disconnected
    #      - 7: Radio test
    #      - 8: Promiscuous Listen
    #      - 9: Suspended
    # - <tt>moteStateReason</tt>: 1-byte field formatted as a int.<br/>
    #     There is no restriction on the value of this field.
    # - <tt>changeCounter</tt>: 2-byte field formatted as a int.<br/>
    #     There is no restriction on the value of this field.
    # - <tt>numParents</tt>: 1-byte field formatted as a int.<br/>
    #     There is no restriction on the value of this field.
    # - <tt>moteAlarms</tt>: 4-byte field formatted as a int.<br/>
    #     There is no restriction on the value of this field.
    # - <tt>statusFlags</tt>: 1-byte field formatted as a int.<br/>
    #     There is no restriction on the value of this field.
    # 
    Tuple_dn_getParameter_moteStatus = collections.namedtuple("Tuple_dn_getParameter_moteStatus", ['RC', 'state', 'moteStateReason', 'changeCounter', 'numParents', 'moteAlarms', 'statusFlags'])

    ##
    # The getParameter<moteStatus> command is used to retrieve the mote's state and frequently changing information. Note that static information about the state of the mote hardware and software may be retrieved using getParameter<moteInfo>.
    # 
    # 
    # 
    # \returns The response to the command, formatted as a #Tuple_dn_getParameter_moteStatus named tuple.
    # 
    def dn_getParameter_moteStatus(self, ) :
        res = HartMoteConnectorInternal.send(self, ['getParameter', 'moteStatus'], {})
        return HartMoteConnector.Tuple_dn_getParameter_moteStatus(**res)

    ##
    # The named tuple returned by the dn_getParameter_time() function.
    # 
    # - <tt>RC</tt>: 1-byte field formatted as a int.<br/>
    #     This field can only take one of the following values:
    #      - 0: RC_OK
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
    #      - 18: RC_OPEN_FAIL
    #      - 19: RC_ERASE_FAIL
    # - <tt>utcTime</tt>: 8-byte field formatted as a hex.<br/>
    #     There is no restriction on the value of this field.
    # - <tt>asn</tt>: 5-byte field formatted as a hex.<br/>
    #     There is no restriction on the value of this field.
    # - <tt>asnOffset</tt>: 2-byte field formatted as a int.<br/>
    #     There is no restriction on the value of this field.
    # 
    Tuple_dn_getParameter_time = collections.namedtuple("Tuple_dn_getParameter_time", ['RC', 'utcTime', 'asn', 'asnOffset'])

    ##
    # The getParameter<time> command is used to request the current time on the mote.
    # 
    # 
    # 
    # \returns The response to the command, formatted as a #Tuple_dn_getParameter_time named tuple.
    # 
    def dn_getParameter_time(self, ) :
        res = HartMoteConnectorInternal.send(self, ['getParameter', 'time'], {})
        return HartMoteConnector.Tuple_dn_getParameter_time(**res)

    ##
    # The named tuple returned by the dn_getParameter_charge() function.
    # 
    # - <tt>RC</tt>: 1-byte field formatted as a int.<br/>
    #     This field can only take one of the following values:
    #      - 0: RC_OK
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
    #      - 18: RC_OPEN_FAIL
    #      - 19: RC_ERASE_FAIL
    # - <tt>charge</tt>: 4-byte field formatted as a int.<br/>
    #     There is no restriction on the value of this field.
    # - <tt>uptime</tt>: 4-byte field formatted as a int.<br/>
    #     There is no restriction on the value of this field.
    # - <tt>temperature</tt>: 1-byte field formatted as a ints.<br/>
    #     There is no restriction on the value of this field.
    # - <tt>fractionalTemp</tt>: 1-byte field formatted as a int.<br/>
    #     There is no restriction on the value of this field.
    # 
    Tuple_dn_getParameter_charge = collections.namedtuple("Tuple_dn_getParameter_charge", ['RC', 'charge', 'uptime', 'temperature', 'fractionalTemp'])

    ##
    # The getParameter<charge> command retrieves estimated charge consumption of the mote since the last reset, as well as the mote uptime and last measured temperature.
    # 
    # 
    # 
    # \returns The response to the command, formatted as a #Tuple_dn_getParameter_charge named tuple.
    # 
    def dn_getParameter_charge(self, ) :
        res = HartMoteConnectorInternal.send(self, ['getParameter', 'charge'], {})
        return HartMoteConnector.Tuple_dn_getParameter_charge(**res)

    ##
    # The named tuple returned by the dn_getParameter_testRadioRxStats() function.
    # 
    # - <tt>RC</tt>: 1-byte field formatted as a int.<br/>
    #     This field can only take one of the following values:
    #      - 0: RC_OK
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
    #      - 18: RC_OPEN_FAIL
    #      - 19: RC_ERASE_FAIL
    # - <tt>rxOk</tt>: 2-byte field formatted as a int.<br/>
    #     There is no restriction on the value of this field.
    # - <tt>rxFailed</tt>: 2-byte field formatted as a int.<br/>
    #     There is no restriction on the value of this field.
    # 
    Tuple_dn_getParameter_testRadioRxStats = collections.namedtuple("Tuple_dn_getParameter_testRadioRxStats", ['RC', 'rxOk', 'rxFailed'])

    ##
    # The getParameter<testRadioRxStats> command retrieves statistics for the latest radio reception test performed using the testRadioRx command. The statistics show the number of good and bad packets (CRC failures) received during the test.
    # 
    # 
    # 
    # \returns The response to the command, formatted as a #Tuple_dn_getParameter_testRadioRxStats named tuple.
    # 
    def dn_getParameter_testRadioRxStats(self, ) :
        res = HartMoteConnectorInternal.send(self, ['getParameter', 'testRadioRxStats'], {})
        return HartMoteConnector.Tuple_dn_getParameter_testRadioRxStats(**res)

    ##
    # The named tuple returned by the dn_getParameter_lock() function.
    # 
    # - <tt>RC</tt>: 1-byte field formatted as a int.<br/>
    #     This field can only take one of the following values:
    #      - 0: RC_OK
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
    #      - 18: RC_OPEN_FAIL
    #      - 19: RC_ERASE_FAIL
    # - <tt>code</tt>: 1-byte field formatted as a int.<br/>
    #     There is no restriction on the value of this field.
    # - <tt>master</tt>: 2-byte field formatted as a int.<br/>
    #     There is no restriction on the value of this field.
    # 
    Tuple_dn_getParameter_lock = collections.namedtuple("Tuple_dn_getParameter_lock", ['RC', 'code', 'master'])

    ##
    # The getParameter<lock> command returns the current (RAM resident) lock code and locking master. To determine what the lock status will be after reset, use the getNVParameter<lock> command. Note: This parameter is available in devices running mote software >= 1.1.0
    # 
    # 
    # 
    # \returns The response to the command, formatted as a #Tuple_dn_getParameter_lock named tuple.
    # 
    def dn_getParameter_lock(self, ) :
        res = HartMoteConnectorInternal.send(self, ['getParameter', 'lock'], {})
        return HartMoteConnector.Tuple_dn_getParameter_lock(**res)

    ##
    # The named tuple returned by the dn_setNVParameter_macAddress() function.
    # 
    # - <tt>RC</tt>: 1-byte field formatted as a int.<br/>
    #     This field can only take one of the following values:
    #      - 0: RC_OK
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
    #      - 18: RC_OPEN_FAIL
    #      - 19: RC_ERASE_FAIL
    # 
    Tuple_dn_setNVParameter_macAddress = collections.namedtuple("Tuple_dn_setNVParameter_macAddress", ['RC'])

    ##
    # The setNVParameter<macAddress> command may be used to supersede the factory-configured MAC address of the mote.
    # 
    # \param macAddr 8-byte field formatted as a hex.<br/>
    #     There is no restriction on the value of this field.
    # 
    # \returns The response to the command, formatted as a #Tuple_dn_setNVParameter_macAddress named tuple.
    # 
    def dn_setNVParameter_macAddress(self, macAddr) :
        res = HartMoteConnectorInternal.send(self, ['setNVParameter', 'macAddress'], {"macAddr" : macAddr})
        return HartMoteConnector.Tuple_dn_setNVParameter_macAddress(**res)

    ##
    # The named tuple returned by the dn_setNVParameter_joinKey() function.
    # 
    # - <tt>RC</tt>: 1-byte field formatted as a int.<br/>
    #     This field can only take one of the following values:
    #      - 0: RC_OK
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
    #      - 18: RC_OPEN_FAIL
    #      - 19: RC_ERASE_FAIL
    # 
    Tuple_dn_setNVParameter_joinKey = collections.namedtuple("Tuple_dn_setNVParameter_joinKey", ['RC'])

    ##
    # The setNVParameter<joinKey> command may be used to set the join key. Upon receiving this request, the mote stores the new join key in its persistent storage. Using the write RAM option will only have an effect if the command is called while the mote is in Idle state. Otherwise, the new value will be used after the next mote boot.
    # 
    # \param joinKey 16-byte field formatted as a hex.<br/>
    #     There is no restriction on the value of this field.
    # 
    # \returns The response to the command, formatted as a #Tuple_dn_setNVParameter_joinKey named tuple.
    # 
    def dn_setNVParameter_joinKey(self, joinKey) :
        res = HartMoteConnectorInternal.send(self, ['setNVParameter', 'joinKey'], {"joinKey" : joinKey})
        return HartMoteConnector.Tuple_dn_setNVParameter_joinKey(**res)

    ##
    # The named tuple returned by the dn_setNVParameter_networkId() function.
    # 
    # - <tt>RC</tt>: 1-byte field formatted as a int.<br/>
    #     This field can only take one of the following values:
    #      - 0: RC_OK
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
    #      - 18: RC_OPEN_FAIL
    #      - 19: RC_ERASE_FAIL
    # 
    Tuple_dn_setNVParameter_networkId = collections.namedtuple("Tuple_dn_setNVParameter_networkId", ['RC'])

    ##
    # The setNVParameter<networkId> command may be used to set the persistent Network ID of the mote. The networkId is used to separate networks, and can be set during manufacturing or in the field. The mote reads this value from persistent storage at boot time. Note: while the mote is in Idle state, it is possible to update the value of mote's in-RAM Network ID by using the RAM flag in the header of this command. This avoids the extra reset that is needed to start using the Network ID. Network ID can also be set over the air using HART command 773 in a WirelessHART-compliant network.
    # 
    # As of version 1.1.1, a network ID of 0xFFFF can be used to indicate that the mote should join the first network heard.
    # 
    # 0xFFFF is never used over the air as a valid HART network ID - do not set the Manager's network ID to 0xFFFF.
    # 
    # \param networkId 2-byte field formatted as a int.<br/>
    #     There is no restriction on the value of this field.
    # 
    # \returns The response to the command, formatted as a #Tuple_dn_setNVParameter_networkId named tuple.
    # 
    def dn_setNVParameter_networkId(self, networkId) :
        res = HartMoteConnectorInternal.send(self, ['setNVParameter', 'networkId'], {"networkId" : networkId})
        return HartMoteConnector.Tuple_dn_setNVParameter_networkId(**res)

    ##
    # The named tuple returned by the dn_setNVParameter_txPower() function.
    # 
    # - <tt>RC</tt>: 1-byte field formatted as a int.<br/>
    #     This field can only take one of the following values:
    #      - 0: RC_OK
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
    #      - 18: RC_OPEN_FAIL
    #      - 19: RC_ERASE_FAIL
    # 
    Tuple_dn_setNVParameter_txPower = collections.namedtuple("Tuple_dn_setNVParameter_txPower", ['RC'])

    ##
    # The setNVParameter<txPower> command sets the mote output power. Refer to product datasheets for supported RF output power values. For example, if the mote has a typical RF output power of +8 dBm when the Power Amplifier (PA) is enabled, then set the txPower parameter to 8 to enable the PA. Similarly, if the mote has a typical RF output power of -2 dBm when the PA is disabled, then set the txPower parameter to -2 to turn off the PA. This command may be issued at any time and takes effect at the next mote boot. To change the transmit power immediately, use the write RAM option of this command, which can also be used at any time.
    # 
    # \param txPower 1-byte field formatted as a ints.<br/>
    #     There is no restriction on the value of this field.
    # 
    # \returns The response to the command, formatted as a #Tuple_dn_setNVParameter_txPower named tuple.
    # 
    def dn_setNVParameter_txPower(self, txPower) :
        res = HartMoteConnectorInternal.send(self, ['setNVParameter', 'txPower'], {"txPower" : txPower})
        return HartMoteConnector.Tuple_dn_setNVParameter_txPower(**res)

    ##
    # The named tuple returned by the dn_setNVParameter_powerInfo() function.
    # 
    # - <tt>RC</tt>: 1-byte field formatted as a int.<br/>
    #     This field can only take one of the following values:
    #      - 0: RC_OK
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
    #      - 18: RC_OPEN_FAIL
    #      - 19: RC_ERASE_FAIL
    # 
    Tuple_dn_setNVParameter_powerInfo = collections.namedtuple("Tuple_dn_setNVParameter_powerInfo", ['RC'])

    ##
    # The setNVParameter<powerInfo> command specifies the average current that is available to the mote. Using the write RAM option will only have an effect if the command is called while the mote is in Idle state. Otherwise, the new value will be used after the next mote boot.
    # 
    # \param powerSource 1-byte field formatted as a int.<br/>
    #     This field can only take one of the following values:
    #      - 0: Line
    #      - 1: Battery
    #      - 2: Rechargeable/Scavenging
    # \param dischargeCur 2-byte field formatted as a int.<br/>
    #     There is no restriction on the value of this field.
    # \param dischargeTime 4-byte field formatted as a int.<br/>
    #     There is no restriction on the value of this field.
    # \param recoverTime 4-byte field formatted as a int.<br/>
    #     There is no restriction on the value of this field.
    # 
    # \returns The response to the command, formatted as a #Tuple_dn_setNVParameter_powerInfo named tuple.
    # 
    def dn_setNVParameter_powerInfo(self, powerSource, dischargeCur, dischargeTime, recoverTime) :
        res = HartMoteConnectorInternal.send(self, ['setNVParameter', 'powerInfo'], {"powerSource" : powerSource, "dischargeCur" : dischargeCur, "dischargeTime" : dischargeTime, "recoverTime" : recoverTime})
        return HartMoteConnector.Tuple_dn_setNVParameter_powerInfo(**res)

    ##
    # The named tuple returned by the dn_setNVParameter_ttl() function.
    # 
    # - <tt>RC</tt>: 1-byte field formatted as a int.<br/>
    #     This field can only take one of the following values:
    #      - 0: RC_OK
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
    #      - 18: RC_OPEN_FAIL
    #      - 19: RC_ERASE_FAIL
    # 
    Tuple_dn_setNVParameter_ttl = collections.namedtuple("Tuple_dn_setNVParameter_ttl", ['RC'])

    ##
    # The setNVParameter<ttl> command sets the mote's persistent packet Time To Live (TTL) value. TTL specifies the maximum number of hops a packet may traverse before it is discarded from the network. A mote sets the initial value of the TTL field in the packets it generates to this value. The mote reads the value from persistent storage at boot time. To change the TTL used currently, this command may be issued with the RAM option.
    # 
    # The mote defaults TTL to 127. For compliant devices, the HART specification currently defaults to 32, but this will change to 249 in spec version 7.4, as will the mote default. We suggest not changing the mote default unless HART specifically raises it as a compliance issue when you submit your device for testing.
    # 
    # \param timeToLive 1-byte field formatted as a int.<br/>
    #     There is no restriction on the value of this field.
    # 
    # \returns The response to the command, formatted as a #Tuple_dn_setNVParameter_ttl named tuple.
    # 
    def dn_setNVParameter_ttl(self, timeToLive) :
        res = HartMoteConnectorInternal.send(self, ['setNVParameter', 'ttl'], {"timeToLive" : timeToLive})
        return HartMoteConnector.Tuple_dn_setNVParameter_ttl(**res)

    ##
    # The named tuple returned by the dn_setNVParameter_hartAntennaGain() function.
    # 
    # - <tt>RC</tt>: 1-byte field formatted as a int.<br/>
    #     This field can only take one of the following values:
    #      - 0: RC_OK
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
    #      - 18: RC_OPEN_FAIL
    #      - 19: RC_ERASE_FAIL
    # 
    Tuple_dn_setNVParameter_hartAntennaGain = collections.namedtuple("Tuple_dn_setNVParameter_hartAntennaGain", ['RC'])

    ##
    # The setNVParameter<hartAntennaGain> command stores value of the antenna gain in the mote's persistent storage. This value is added to the conducted output power of the mote when replying to HART command 797 (Write Radio Power Output) and to HART command 798 (Read Radio Output Power). The antenna gain should take into account both the gain of the antenna and any loss (for example, attenuation from a long coax cable) between the mote and the antenna. By default, this value is 2, assuming a +2 dBi antenna gain. To change the transmit power immediately, use the write RAM option of this command.
    # 
    # \param antennaGain 1-byte field formatted as a ints.<br/>
    #     There is no restriction on the value of this field.
    # 
    # \returns The response to the command, formatted as a #Tuple_dn_setNVParameter_hartAntennaGain named tuple.
    # 
    def dn_setNVParameter_hartAntennaGain(self, antennaGain) :
        res = HartMoteConnectorInternal.send(self, ['setNVParameter', 'hartAntennaGain'], {"antennaGain" : antennaGain})
        return HartMoteConnector.Tuple_dn_setNVParameter_hartAntennaGain(**res)

    ##
    # The named tuple returned by the dn_setNVParameter_OTAPlockout() function.
    # 
    # - <tt>RC</tt>: 1-byte field formatted as a int.<br/>
    #     This field can only take one of the following values:
    #      - 0: RC_OK
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
    #      - 18: RC_OPEN_FAIL
    #      - 19: RC_ERASE_FAIL
    # 
    Tuple_dn_setNVParameter_OTAPlockout = collections.namedtuple("Tuple_dn_setNVParameter_OTAPlockout", ['RC'])

    ##
    # The setNVParameter<OTAPlockout> command specifies whether the mote's firmware can be updated over the air. Over-The-Air-Programming (OTAP) is allowed by default. The mote reads the OTAPlockout value from persistent storage at boot time. To change the value used currently, this command may be issued with RAM option.
    # 
    # Dust Networks recommends that OEMs allow their devices to receive firmware updates, either by leaving the OTAPlockout parameter at its default value, or by making OTAPlockout settable using a WirelessHART command that is available both over the air and through its wired maintenance port. OEMs have the option of making such a command password protected.
    # 
    # \param otapLockout 1-byte field formatted as a int.<br/>
    #     This field can only take one of the following values:
    #      - 0: OTAP allowed (default)
    #      - 1: OTAP disabled
    # 
    # \returns The response to the command, formatted as a #Tuple_dn_setNVParameter_OTAPlockout named tuple.
    # 
    def dn_setNVParameter_OTAPlockout(self, otapLockout) :
        res = HartMoteConnectorInternal.send(self, ['setNVParameter', 'OTAPlockout'], {"otapLockout" : otapLockout})
        return HartMoteConnector.Tuple_dn_setNVParameter_OTAPlockout(**res)

    ##
    # The named tuple returned by the dn_setNVParameter_hrCounterMode() function.
    # 
    # - <tt>RC</tt>: 1-byte field formatted as a int.<br/>
    #     This field can only take one of the following values:
    #      - 0: RC_OK
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
    #      - 18: RC_OPEN_FAIL
    #      - 19: RC_ERASE_FAIL
    # 
    Tuple_dn_setNVParameter_hrCounterMode = collections.namedtuple("Tuple_dn_setNVParameter_hrCounterMode", ['RC'])

    ##
    # The setNVParameter<hrCounterMode> command may be used to control how the mote increments statistics counters reported via HART health reports. The two options are "saturating" (i.e. stop counting at maximum value) and "rollover" (i.e. continue counting through rollover). The default value of "saturating" is required for compatibility with Dust Wireless HART managers. This parameter takes effect upon mote reset.
    # 
    # Note: This parameter is available in devices running mote software >=1.1.0
    # 
    # \param hrCounterMode 1-byte field formatted as a int.<br/>
    #     This field can only take one of the following values:
    #      - 0: Rollover
    #      - 1: Saturating
    # 
    # \returns The response to the command, formatted as a #Tuple_dn_setNVParameter_hrCounterMode named tuple.
    # 
    def dn_setNVParameter_hrCounterMode(self, hrCounterMode) :
        res = HartMoteConnectorInternal.send(self, ['setNVParameter', 'hrCounterMode'], {"hrCounterMode" : hrCounterMode})
        return HartMoteConnector.Tuple_dn_setNVParameter_hrCounterMode(**res)

    ##
    # The named tuple returned by the dn_setNVParameter_autojoin() function.
    # 
    # - <tt>RC</tt>: 1-byte field formatted as a int.<br/>
    #     This field can only take one of the following values:
    #      - 0: RC_OK
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
    #      - 18: RC_OPEN_FAIL
    #      - 19: RC_ERASE_FAIL
    # - <tt>nvParamId</tt>: 1-byte field formatted as a int.<br/>
    #     There is no restriction on the value of this field.
    # 
    Tuple_dn_setNVParameter_autojoin = collections.namedtuple("Tuple_dn_setNVParameter_autojoin", ['RC', 'nvParamId'])

    ##
    # The setNVParameter<autojoin> command allows the microprocessor to change between automatic and manual joining by the mote's networking stack. In manual mode, an explicit join command from the application is required to initiate joining. This setting is persistent and takes effect after mote reset. (Available Mote >= 1.1) Note that auto join mode must not be set if the application is also configured to join (e.g combining 'auto join' with 'master' mode will result in mote not joining).
    # 
    # \param autojoin 1-byte field formatted as a int.<br/>
    #     There is no restriction on the value of this field.
    # 
    # \returns The response to the command, formatted as a #Tuple_dn_setNVParameter_autojoin named tuple.
    # 
    def dn_setNVParameter_autojoin(self, autojoin) :
        res = HartMoteConnectorInternal.send(self, ['setNVParameter', 'autojoin'], {"autojoin" : autojoin})
        return HartMoteConnector.Tuple_dn_setNVParameter_autojoin(**res)

    ##
    # The named tuple returned by the dn_setNVParameter_hartCompliantMode() function.
    # 
    # - <tt>RC</tt>: 1-byte field formatted as a int.<br/>
    #     This field can only take one of the following values:
    #      - 0: RC_OK
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
    #      - 18: RC_OPEN_FAIL
    #      - 19: RC_ERASE_FAIL
    # 
    Tuple_dn_setNVParameter_hartCompliantMode = collections.namedtuple("Tuple_dn_setNVParameter_hartCompliantMode", ['RC'])

    ##
    # The setNVParameter<hartCompliantMode> command may be used to force strict compliance to HART specification requirements, specifically:
    # 
    # - join timeouts (faster in non-compliant mode)
    # - Keepalive interval (adapts to synch quality in non-compliant mode)
    # - Health report format (uses saturating counters in non-compliant mode)
    # 
    # Note: This parameter is referred to as compliantMode in documentation for versions 1.1.x, and hartCompliantMode in >=1.2.x, but the parameter ID is the same in both versions. The corresponding CLI command is called mset compliantMode in 1.1.x, and mset hartCompliantMode in >=1.2.x
    # 
    # \param hartCompliantMode 1-byte field formatted as a int.<br/>
    #     There is no restriction on the value of this field.
    # 
    # \returns The response to the command, formatted as a #Tuple_dn_setNVParameter_hartCompliantMode named tuple.
    # 
    def dn_setNVParameter_hartCompliantMode(self, hartCompliantMode) :
        res = HartMoteConnectorInternal.send(self, ['setNVParameter', 'hartCompliantMode'], {"hartCompliantMode" : hartCompliantMode})
        return HartMoteConnector.Tuple_dn_setNVParameter_hartCompliantMode(**res)

    ##
    # The named tuple returned by the dn_setNVParameter_lock() function.
    # 
    # - <tt>RC</tt>: 1-byte field formatted as a int.<br/>
    #     This field can only take one of the following values:
    #      - 0: RC_OK
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
    #      - 18: RC_OPEN_FAIL
    #      - 19: RC_ERASE_FAIL
    # 
    Tuple_dn_setNVParameter_lock = collections.namedtuple("Tuple_dn_setNVParameter_lock", ['RC'])

    ##
    # The setNVParameter<lock> command persistently locks/unlocks select HART commands (ones that affect the configuration changed flag) to a specific master (GW or serial maintenance port) to prevent the other master from changing it. This command is intended for use when the lock persists through power cycle or reset. For temporary locking, use the setParameter<lock> command. Bit 7 in the flags field of the API header (see Packet Format) should be set (store in NV & RAM) when calling this command. Note: This parameter is available in devices running mote software >= 1.1.0
    # 
    # \param code 1-byte field formatted as a int.<br/>
    #     There is no restriction on the value of this field.
    # \param master 2-byte field formatted as a int.<br/>
    #     There is no restriction on the value of this field.
    # 
    # \returns The response to the command, formatted as a #Tuple_dn_setNVParameter_lock named tuple.
    # 
    def dn_setNVParameter_lock(self, code, master) :
        res = HartMoteConnectorInternal.send(self, ['setNVParameter', 'lock'], {"code" : code, "master" : master})
        return HartMoteConnector.Tuple_dn_setNVParameter_lock(**res)

    ##
    # The named tuple returned by the dn_setNVParameter_euCompliantMode() function.
    # 
    # - <tt>RC</tt>: 1-byte field formatted as a int.<br/>
    #     This field can only take one of the following values:
    #      - 0: RC_OK
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
    #      - 18: RC_OPEN_FAIL
    #      - 19: RC_ERASE_FAIL
    # 
    Tuple_dn_setNVParameter_euCompliantMode = collections.namedtuple("Tuple_dn_setNVParameter_euCompliantMode", ['RC'])

    ##
    # The setNVParameter<euCompliantMode> command may be used to enforce EN 300 328 duty cycle limits based on output power. This may cause the mote to skip some transmit opportunities to remain within average power limits. Motes below +10 dBm radiated power do not need to duty cycle to meet EN 300 328 requirements.
    # 
    # Note: This parameter is available in version >=1.2.x
    # 
    # \param euCompliantMode 1-byte field formatted as a int.<br/>
    #     There is no restriction on the value of this field.
    # 
    # \returns The response to the command, formatted as a #Tuple_dn_setNVParameter_euCompliantMode named tuple.
    # 
    def dn_setNVParameter_euCompliantMode(self, euCompliantMode) :
        res = HartMoteConnectorInternal.send(self, ['setNVParameter', 'euCompliantMode'], {"euCompliantMode" : euCompliantMode})
        return HartMoteConnector.Tuple_dn_setNVParameter_euCompliantMode(**res)

    ##
    # The named tuple returned by the dn_setNVParameter_joinShedTime() function.
    # 
    # - <tt>RC</tt>: 1-byte field formatted as a int.<br/>
    #     This field can only take one of the following values:
    #      - 0: RC_OK
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
    #      - 18: RC_OPEN_FAIL
    #      - 19: RC_ERASE_FAIL
    # 
    Tuple_dn_setNVParameter_joinShedTime = collections.namedtuple("Tuple_dn_setNVParameter_joinShedTime", ['RC'])

    ##
    # The setNVParameter<joinShedTime> command sets the join shed time u sed with HART command 771/772 to determine when the mote should transition between active and passive search. This command may be issued at any time and takes effect at the next mote boot.
    # 
    # \param joinShedTime 4-byte field formatted as a int.<br/>
    #     There is no restriction on the value of this field.
    # 
    # \returns The response to the command, formatted as a #Tuple_dn_setNVParameter_joinShedTime named tuple.
    # 
    def dn_setNVParameter_joinShedTime(self, joinShedTime) :
        res = HartMoteConnectorInternal.send(self, ['setNVParameter', 'joinShedTime'], {"joinShedTime" : joinShedTime})
        return HartMoteConnector.Tuple_dn_setNVParameter_joinShedTime(**res)

    ##
    # The named tuple returned by the dn_getNVParameter_macAddress() function.
    # 
    # - <tt>RC</tt>: 1-byte field formatted as a int.<br/>
    #     This field can only take one of the following values:
    #      - 0: RC_OK
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
    #      - 18: RC_OPEN_FAIL
    #      - 19: RC_ERASE_FAIL
    # - <tt>macAddr</tt>: 8-byte field formatted as a hex.<br/>
    #     There is no restriction on the value of this field.
    # 
    Tuple_dn_getNVParameter_macAddress = collections.namedtuple("Tuple_dn_getNVParameter_macAddress", ['RC', 'macAddr'])

    ##
    # The getNVParameter<macAddress> command returns the MAC address stored in mote's persistent storage (i.e. set with setNVParameter<macAddress>).
    # 
    # This command returns 0000000000000000 if the macAddress has not been set previously - the mote will use its hardware MAC in this case, but it is not displayed with this command.
    # 
    # 
    # 
    # \returns The response to the command, formatted as a #Tuple_dn_getNVParameter_macAddress named tuple.
    # 
    def dn_getNVParameter_macAddress(self, ) :
        res = HartMoteConnectorInternal.send(self, ['getNVParameter', 'macAddress'], {})
        return HartMoteConnector.Tuple_dn_getNVParameter_macAddress(**res)

    ##
    # The named tuple returned by the dn_getNVParameter_networkId() function.
    # 
    # - <tt>RC</tt>: 1-byte field formatted as a int.<br/>
    #     This field can only take one of the following values:
    #      - 0: RC_OK
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
    #      - 18: RC_OPEN_FAIL
    #      - 19: RC_ERASE_FAIL
    # - <tt>networkId</tt>: 2-byte field formatted as a int.<br/>
    #     There is no restriction on the value of this field.
    # 
    Tuple_dn_getNVParameter_networkId = collections.namedtuple("Tuple_dn_getNVParameter_networkId", ['RC', 'networkId'])

    ##
    # The getNVParameter<networkId> command returns the Network ID stored in mote's persistent storage.
    # 
    # 
    # 
    # \returns The response to the command, formatted as a #Tuple_dn_getNVParameter_networkId named tuple.
    # 
    def dn_getNVParameter_networkId(self, ) :
        res = HartMoteConnectorInternal.send(self, ['getNVParameter', 'networkId'], {})
        return HartMoteConnector.Tuple_dn_getNVParameter_networkId(**res)

    ##
    # The named tuple returned by the dn_getNVParameter_txPower() function.
    # 
    # - <tt>RC</tt>: 1-byte field formatted as a int.<br/>
    #     This field can only take one of the following values:
    #      - 0: RC_OK
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
    #      - 18: RC_OPEN_FAIL
    #      - 19: RC_ERASE_FAIL
    # - <tt>txPower</tt>: 1-byte field formatted as a ints.<br/>
    #     There is no restriction on the value of this field.
    # 
    Tuple_dn_getNVParameter_txPower = collections.namedtuple("Tuple_dn_getNVParameter_txPower", ['RC', 'txPower'])

    ##
    # The getNVParameter<txPower> command returns the transmit power value stored in mote's persistent storage.
    # 
    # 
    # 
    # \returns The response to the command, formatted as a #Tuple_dn_getNVParameter_txPower named tuple.
    # 
    def dn_getNVParameter_txPower(self, ) :
        res = HartMoteConnectorInternal.send(self, ['getNVParameter', 'txPower'], {})
        return HartMoteConnector.Tuple_dn_getNVParameter_txPower(**res)

    ##
    # The named tuple returned by the dn_getNVParameter_powerInfo() function.
    # 
    # - <tt>RC</tt>: 1-byte field formatted as a int.<br/>
    #     This field can only take one of the following values:
    #      - 0: RC_OK
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
    #      - 18: RC_OPEN_FAIL
    #      - 19: RC_ERASE_FAIL
    # - <tt>powerSource</tt>: 1-byte field formatted as a int.<br/>
    #     This field can only take one of the following values:
    #      - 0: Line
    #      - 1: Battery
    #      - 2: Rechargeable/Scavenging
    # - <tt>dischargeCur</tt>: 2-byte field formatted as a int.<br/>
    #     There is no restriction on the value of this field.
    # - <tt>dischargeTime</tt>: 4-byte field formatted as a int.<br/>
    #     There is no restriction on the value of this field.
    # - <tt>recoverTime</tt>: 4-byte field formatted as a int.<br/>
    #     There is no restriction on the value of this field.
    # 
    Tuple_dn_getNVParameter_powerInfo = collections.namedtuple("Tuple_dn_getNVParameter_powerInfo", ['RC', 'powerSource', 'dischargeCur', 'dischargeTime', 'recoverTime'])

    ##
    # The getNVParameter<powerInfo> command returns the power supply information stored in mote's persistent storage.
    # 
    # 
    # 
    # \returns The response to the command, formatted as a #Tuple_dn_getNVParameter_powerInfo named tuple.
    # 
    def dn_getNVParameter_powerInfo(self, ) :
        res = HartMoteConnectorInternal.send(self, ['getNVParameter', 'powerInfo'], {})
        return HartMoteConnector.Tuple_dn_getNVParameter_powerInfo(**res)

    ##
    # The named tuple returned by the dn_getNVParameter_ttl() function.
    # 
    # - <tt>RC</tt>: 1-byte field formatted as a int.<br/>
    #     This field can only take one of the following values:
    #      - 0: RC_OK
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
    #      - 18: RC_OPEN_FAIL
    #      - 19: RC_ERASE_FAIL
    # - <tt>timeToLive</tt>: 1-byte field formatted as a int.<br/>
    #     There is no restriction on the value of this field.
    # 
    Tuple_dn_getNVParameter_ttl = collections.namedtuple("Tuple_dn_getNVParameter_ttl", ['RC', 'timeToLive'])

    ##
    # The getNVParameter<ttl> command reads the Time To Live parameter from the mote's persistent storage. Time To Live is used when the mote sends a packet into the network, and specifies the maximum number of hops the packet may traverse before it is discarded from the network.
    # 
    # 
    # 
    # \returns The response to the command, formatted as a #Tuple_dn_getNVParameter_ttl named tuple.
    # 
    def dn_getNVParameter_ttl(self, ) :
        res = HartMoteConnectorInternal.send(self, ['getNVParameter', 'ttl'], {})
        return HartMoteConnector.Tuple_dn_getNVParameter_ttl(**res)

    ##
    # The named tuple returned by the dn_getNVParameter_HARTantennaGain() function.
    # 
    # - <tt>RC</tt>: 1-byte field formatted as a int.<br/>
    #     This field can only take one of the following values:
    #      - 0: RC_OK
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
    #      - 18: RC_OPEN_FAIL
    #      - 19: RC_ERASE_FAIL
    # - <tt>antennaGain</tt>: 1-byte field formatted as a ints.<br/>
    #     There is no restriction on the value of this field.
    # 
    Tuple_dn_getNVParameter_HARTantennaGain = collections.namedtuple("Tuple_dn_getNVParameter_HARTantennaGain", ['RC', 'antennaGain'])

    ##
    # The getNVParameter<HARTantennaGain> command reads the antenna gain value from the mote's persistent storage. This value is added to conducted output power of the Dust mote when replying to HART command 797 (Write Radio Power Output) and to HART command 798 (Read Radio Output Power).
    # 
    # 
    # 
    # \returns The response to the command, formatted as a #Tuple_dn_getNVParameter_HARTantennaGain named tuple.
    # 
    def dn_getNVParameter_HARTantennaGain(self, ) :
        res = HartMoteConnectorInternal.send(self, ['getNVParameter', 'HARTantennaGain'], {})
        return HartMoteConnector.Tuple_dn_getNVParameter_HARTantennaGain(**res)

    ##
    # The named tuple returned by the dn_getNVParameter_OTAPlockout() function.
    # 
    # - <tt>RC</tt>: 1-byte field formatted as a int.<br/>
    #     This field can only take one of the following values:
    #      - 0: RC_OK
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
    #      - 18: RC_OPEN_FAIL
    #      - 19: RC_ERASE_FAIL
    # - <tt>otapLockout</tt>: 1-byte field formatted as a int.<br/>
    #     This field can only take one of the following values:
    #      - 0: OTAP allowed (default)
    #      - 1: OTAP disabled
    # 
    Tuple_dn_getNVParameter_OTAPlockout = collections.namedtuple("Tuple_dn_getNVParameter_OTAPlockout", ['RC', 'otapLockout'])

    ##
    # The getNVParameter<OTAPlockout> command reads the OTAP lockout setting from the motes persistent storage. OTAP lockout specifies whether the mote can be Over-The-Air-Programmed (OTAP).
    # 
    # 
    # 
    # \returns The response to the command, formatted as a #Tuple_dn_getNVParameter_OTAPlockout named tuple.
    # 
    def dn_getNVParameter_OTAPlockout(self, ) :
        res = HartMoteConnectorInternal.send(self, ['getNVParameter', 'OTAPlockout'], {})
        return HartMoteConnector.Tuple_dn_getNVParameter_OTAPlockout(**res)

    ##
    # The named tuple returned by the dn_getNVParameter_hrCounterMode() function.
    # 
    # - <tt>RC</tt>: 1-byte field formatted as a int.<br/>
    #     This field can only take one of the following values:
    #      - 0: RC_OK
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
    #      - 18: RC_OPEN_FAIL
    #      - 19: RC_ERASE_FAIL
    # - <tt>hrCounterMode</tt>: 1-byte field formatted as a int.<br/>
    #     This field can only take one of the following values:
    #      - 0: Rollover
    #      - 1: Saturating
    # 
    Tuple_dn_getNVParameter_hrCounterMode = collections.namedtuple("Tuple_dn_getNVParameter_hrCounterMode", ['RC', 'hrCounterMode'])

    ##
    # The getNVParameter<hrCounterMode> command may be used to retrieve the health report counter mode that is used by devices. This mode controls how the mote deals with statistics counters when they reach their maximum value.
    # 
    # Note: This parameter is available in devices running mote software >=1.1.0
    # 
    # 
    # 
    # \returns The response to the command, formatted as a #Tuple_dn_getNVParameter_hrCounterMode named tuple.
    # 
    def dn_getNVParameter_hrCounterMode(self, ) :
        res = HartMoteConnectorInternal.send(self, ['getNVParameter', 'hrCounterMode'], {})
        return HartMoteConnector.Tuple_dn_getNVParameter_hrCounterMode(**res)

    ##
    # The named tuple returned by the dn_getNVParameter_autojoin() function.
    # 
    # - <tt>RC</tt>: 1-byte field formatted as a int.<br/>
    #     This field can only take one of the following values:
    #      - 0: RC_OK
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
    #      - 18: RC_OPEN_FAIL
    #      - 19: RC_ERASE_FAIL
    # - <tt>autojoin</tt>: 1-byte field formatted as a int.<br/>
    #     There is no restriction on the value of this field.
    # 
    Tuple_dn_getNVParameter_autojoin = collections.namedtuple("Tuple_dn_getNVParameter_autojoin", ['RC', 'autojoin'])

    ##
    # The getNVParameter<autojoin> command returns the autojoin status stored in mote's persistent storage (i.e. set with setNVParameter<autojoin>). Autojoin can be used to cause a mote in slave mode to join on its own when booted.
    # 
    # 
    # 
    # \returns The response to the command, formatted as a #Tuple_dn_getNVParameter_autojoin named tuple.
    # 
    def dn_getNVParameter_autojoin(self, ) :
        res = HartMoteConnectorInternal.send(self, ['getNVParameter', 'autojoin'], {})
        return HartMoteConnector.Tuple_dn_getNVParameter_autojoin(**res)

    ##
    # The named tuple returned by the dn_getNVParameter_hartCompliantMode() function.
    # 
    # - <tt>RC</tt>: 1-byte field formatted as a int.<br/>
    #     This field can only take one of the following values:
    #      - 0: RC_OK
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
    #      - 18: RC_OPEN_FAIL
    #      - 19: RC_ERASE_FAIL
    # - <tt>hartCompliantMode</tt>: 1-byte field formatted as a int.<br/>
    #     This field can only take one of the following values:
    #      - 0: Some timers and counters deviate from HART specification
    #      - 1: Strict HART compliance
    # 
    Tuple_dn_getNVParameter_hartCompliantMode = collections.namedtuple("Tuple_dn_getNVParameter_hartCompliantMode", ['RC', 'hartCompliantMode'])

    ##
    # The getNVParameter<hartCompliantMode> command may be used to retrieve the HART compliance mode that is used by devices. This mode controls strict compliance to HART specification requirements, specifically:
    # 
    # - join timeouts (faster in non-compliant mode)
    # - Keepalive interval (adapts to synch quality in non-compliant mode)
    # - Health report format (uses saturating counters in non-compliant mode)
    # 
    # Note: This parameter is available in devices running mote software >= 1.1.0
    # 
    # 
    # 
    # \returns The response to the command, formatted as a #Tuple_dn_getNVParameter_hartCompliantMode named tuple.
    # 
    def dn_getNVParameter_hartCompliantMode(self, ) :
        res = HartMoteConnectorInternal.send(self, ['getNVParameter', 'hartCompliantMode'], {})
        return HartMoteConnector.Tuple_dn_getNVParameter_hartCompliantMode(**res)

    ##
    # The named tuple returned by the dn_getNVParameter_lock() function.
    # 
    # - <tt>RC</tt>: 1-byte field formatted as a int.<br/>
    #     This field can only take one of the following values:
    #      - 0: RC_OK
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
    #      - 18: RC_OPEN_FAIL
    #      - 19: RC_ERASE_FAIL
    # - <tt>code</tt>: 1-byte field formatted as a int.<br/>
    #     There is no restriction on the value of this field.
    # - <tt>master</tt>: 2-byte field formatted as a int.<br/>
    #     There is no restriction on the value of this field.
    # 
    Tuple_dn_getNVParameter_lock = collections.namedtuple("Tuple_dn_getNVParameter_lock", ['RC', 'code', 'master'])

    ##
    # The getNVParameter < lock > command returns the persisted lock code and locking master (those to be used after reset). To determine the current lock status, use the getParameter<lock> command. Note: This parameter is available in devices running mote software >= 1.1.0
    # 
    # 
    # 
    # \returns The response to the command, formatted as a #Tuple_dn_getNVParameter_lock named tuple.
    # 
    def dn_getNVParameter_lock(self, ) :
        res = HartMoteConnectorInternal.send(self, ['getNVParameter', 'lock'], {})
        return HartMoteConnector.Tuple_dn_getNVParameter_lock(**res)

    ##
    # The named tuple returned by the dn_getNVParameter_euCompliantMode() function.
    # 
    # - <tt>RC</tt>: 1-byte field formatted as a int.<br/>
    #     This field can only take one of the following values:
    #      - 0: RC_OK
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
    #      - 18: RC_OPEN_FAIL
    #      - 19: RC_ERASE_FAIL
    # - <tt>euCompliantMode</tt>: 1-byte field formatted as a int.<br/>
    #     There is no restriction on the value of this field.
    # 
    Tuple_dn_getNVParameter_euCompliantMode = collections.namedtuple("Tuple_dn_getNVParameter_euCompliantMode", ['RC', 'euCompliantMode'])

    ##
    # The getNVParameter<euCompliantMode> command may be used to retrieve the EN 300 328 compliance mode that is used by devices. When enabled, the mote may skip some transmit opportunities to remain within average power limits. Motes below +10 dBm radiated power do not need to duty cycle to meet EN 300 328 requirements.
    # 
    # Note: This parameter is available in devices running mote software >=1.2.x
    # 
    # 
    # 
    # \returns The response to the command, formatted as a #Tuple_dn_getNVParameter_euCompliantMode named tuple.
    # 
    def dn_getNVParameter_euCompliantMode(self, ) :
        res = HartMoteConnectorInternal.send(self, ['getNVParameter', 'euCompliantMode'], {})
        return HartMoteConnector.Tuple_dn_getNVParameter_euCompliantMode(**res)

    ##
    # The named tuple returned by the dn_getNVParameter_joinShedTime() function.
    # 
    # - <tt>RC</tt>: 1-byte field formatted as a int.<br/>
    #     This field can only take one of the following values:
    #      - 0: RC_OK
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
    #      - 18: RC_OPEN_FAIL
    #      - 19: RC_ERASE_FAIL
    # - <tt>joinShedTime</tt>: 4-byte field formatted as a int.<br/>
    #     There is no restriction on the value of this field.
    # 
    Tuple_dn_getNVParameter_joinShedTime = collections.namedtuple("Tuple_dn_getNVParameter_joinShedTime", ['RC', 'joinShedTime'])

    ##
    # The getNVParameter<joinShedTime> command returns the join shed time used with HART command 771/772 to determine when the mote should transition between active and passive search.
    # 
    # 
    # 
    # \returns The response to the command, formatted as a #Tuple_dn_getNVParameter_joinShedTime named tuple.
    # 
    def dn_getNVParameter_joinShedTime(self, ) :
        res = HartMoteConnectorInternal.send(self, ['getNVParameter', 'joinShedTime'], {})
        return HartMoteConnector.Tuple_dn_getNVParameter_joinShedTime(**res)

    ##
    # The named tuple returned by the dn_send() function.
    # 
    # - <tt>RC</tt>: 1-byte field formatted as a int.<br/>
    #     This field can only take one of the following values:
    #      - 0: RC_OK
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
    #      - 18: RC_OPEN_FAIL
    #      - 19: RC_ERASE_FAIL
    # 
    Tuple_dn_send = collections.namedtuple("Tuple_dn_send", ['RC'])

    ##
    # The send command allows a serial device to send a packet into the network through the mote's serial port. The mote forwards the packet to the network upon receiving it. The microprocessor must not attempt to send data at a rate that exceeds its allocated bandwidth. For a WirelessHART device, the payload of the packet must include the status byte and the extended status byte, followed by one or more sets of HART commands up to the maximum send payload size, as follows:
    # 
    # Request: Status|Extended Status|Cmd1|Length1|Data1|Cmd2|Length2|Data2... Response: Status|Extended Status|Cmd1|Length1(includes response code)|RC1|Data1|Cmd2|Length2|RC2|Data2...
    # 
    # Prior to sending the payload into the network, the mote caches the value of Status and Extended Status to use in packets it originates locally. The send command is only valid when the mote is in the Operational state. If the mote receives this command when it is not in the Operational state, it returns the error RC_INV_STATE. Note: The serial device can receive a request while the mote is in the process of transition from the Connected state to the Operational state.
    # 
    # \param tranType 1-byte field formatted as a bool.<br/>
    #     This field can only take one of the following values:
    #      - False: bestEffort
    #      - True: Acked
    # \param tranDir 1-byte field formatted as a bool.<br/>
    #     This field can only take one of the following values:
    #      - False: request
    #      - True: response
    # \param destAddr 2-byte field formatted as a hex.<br/>
    #     There is no restriction on the value of this field.
    # \param serviceId 1-byte field formatted as a int.<br/>
    #     There is no restriction on the value of this field.
    # \param appDomain 1-byte field formatted as a int.<br/>
    #     This field can only take one of the following values:
    #      - 0: Publish
    #      - 1: Event
    #      - 2: Maintenance
    #      - 3: Block transfer
    # \param priority 1-byte field formatted as a int.<br/>
    #     This field can only take one of the following values:
    #      - 0: Low
    #      - 1: Medium
    #      - 2: High
    # \param reserved 2-byte field formatted as a int.<br/>
    #     There is no restriction on the value of this field.
    # \param seqNum 1-byte field formatted as a int.<br/>
    #     There is no restriction on the value of this field.
    # \param payloadLen 1-byte field formatted as a int.<br/>
    #     There is no restriction on the value of this field.
    # \param payload None-byte field formatted as a hex.<br/>
    #     There is no restriction on the value of this field.
    # 
    # \returns The response to the command, formatted as a #Tuple_dn_send named tuple.
    # 
    def dn_send(self, tranType, tranDir, destAddr, serviceId, appDomain, priority, reserved, seqNum, payloadLen, payload) :
        res = HartMoteConnectorInternal.send(self, ['send'], {"tranType" : tranType, "tranDir" : tranDir, "destAddr" : destAddr, "serviceId" : serviceId, "appDomain" : appDomain, "priority" : priority, "reserved" : reserved, "seqNum" : seqNum, "payloadLen" : payloadLen, "payload" : payload})
        return HartMoteConnector.Tuple_dn_send(**res)

    ##
    # The named tuple returned by the dn_join() function.
    # 
    # - <tt>RC</tt>: 1-byte field formatted as a int.<br/>
    #     This field can only take one of the following values:
    #      - 0: RC_OK
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
    #      - 18: RC_OPEN_FAIL
    #      - 19: RC_ERASE_FAIL
    # 
    Tuple_dn_join = collections.namedtuple("Tuple_dn_join", ['RC'])

    ##
    # The join command requests that a mote start searching for the network and attempt to join. The mote must be in the Idle state or the Promiscuous Listen state (see search) for this command to be valid. The join time is partly determined by the join duty cycle. For guidance on setting the join duty cycle, see setParameter<joinDutyCycle>.
    # 
    # 
    # 
    # \returns The response to the command, formatted as a #Tuple_dn_join named tuple.
    # 
    def dn_join(self, ) :
        res = HartMoteConnectorInternal.send(self, ['join'], {})
        return HartMoteConnector.Tuple_dn_join(**res)

    ##
    # The named tuple returned by the dn_disconnect() function.
    # 
    # - <tt>RC</tt>: 1-byte field formatted as a int.<br/>
    #     This field can only take one of the following values:
    #      - 0: RC_OK
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
    #      - 18: RC_OPEN_FAIL
    #      - 19: RC_ERASE_FAIL
    # 
    Tuple_dn_disconnect = collections.namedtuple("Tuple_dn_disconnect", ['RC'])

    ##
    # The disconnect command requests that the mote disconnect from the network. The mote will send an indication to its network neighbors that it is about to become unavailable. Just after the mote disconnects, it sends the microprocessor an events packet with the disconnected bit set, indicating it will reset. This command is only valid in when the mote is in the Connected or Operational state (see Mote State).
    # 
    # The OEM microprocessor should disconnect from the network if the device is going to power down, reset, or otherwise be unavailable for a long period.
    # 
    # A mote will reset itself after having sent the disconnect notification to the OEM microprocessor. The microprocessor should wait to acknowledge the boot event before shutting down.
    # 
    # 
    # 
    # \returns The response to the command, formatted as a #Tuple_dn_disconnect named tuple.
    # 
    def dn_disconnect(self, ) :
        res = HartMoteConnectorInternal.send(self, ['disconnect'], {})
        return HartMoteConnector.Tuple_dn_disconnect(**res)

    ##
    # The named tuple returned by the dn_reset() function.
    # 
    # - <tt>RC</tt>: 1-byte field formatted as a int.<br/>
    #     This field can only take one of the following values:
    #      - 0: RC_OK
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
    #      - 18: RC_OPEN_FAIL
    #      - 19: RC_ERASE_FAIL
    # 
    Tuple_dn_reset = collections.namedtuple("Tuple_dn_reset", ['RC'])

    ##
    # Upon receiving this command, the mote resets itself after a short delay. The mote will always send a response packet before initiating the reset. To force the mote to gracefully leave the network, use the disconnect command.
    # 
    # 
    # 
    # \returns The response to the command, formatted as a #Tuple_dn_reset named tuple.
    # 
    def dn_reset(self, ) :
        res = HartMoteConnectorInternal.send(self, ['reset'], {})
        return HartMoteConnector.Tuple_dn_reset(**res)

    ##
    # The named tuple returned by the dn_lowPowerSleep() function.
    # 
    # - <tt>RC</tt>: 1-byte field formatted as a int.<br/>
    #     This field can only take one of the following values:
    #      - 0: RC_OK
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
    #      - 18: RC_OPEN_FAIL
    #      - 19: RC_ERASE_FAIL
    # 
    Tuple_dn_lowPowerSleep = collections.namedtuple("Tuple_dn_lowPowerSleep", ['RC'])

    ##
    # The lowPowerSleep command shuts down all peripherals and places the mote in deep sleep mode. The lowPowerSleep command may be issued at any time and will cause the mote to interrupt all in-progress network operation. The command executes after the mote sends its response. The mote enters deep sleep within two seconds after the command executes.
    # 
    # The OEM microprocessor should put the mote into low power sleep when the mote needs to be offline for an extended period of time. In most cases, this will result in a lower current state of the mote than simply asserting /RST without putting the mote in low power sleep. To achieve a graceful disconnect, use the disconnect command before using the lowPowerSleep command. The mote can only be awakened from low power sleep by asserting a non-maskable interrupt, such as the /RST control line. For power consumption information, refer to the mote product datasheet.
    # 
    # 
    # 
    # \returns The response to the command, formatted as a #Tuple_dn_lowPowerSleep named tuple.
    # 
    def dn_lowPowerSleep(self, ) :
        res = HartMoteConnectorInternal.send(self, ['lowPowerSleep'], {})
        return HartMoteConnector.Tuple_dn_lowPowerSleep(**res)

    ##
    # The named tuple returned by the dn_hartPayload() function.
    # 
    # - <tt>RC</tt>: 1-byte field formatted as a int.<br/>
    #     This field can only take one of the following values:
    #      - 0: RC_OK
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
    #      - 18: RC_OPEN_FAIL
    #      - 19: RC_ERASE_FAIL
    # - <tt>payloadLen</tt>: 1-byte field formatted as a int.<br/>
    #     There is no restriction on the value of this field.
    # - <tt>payload</tt>: None-byte field formatted as a hex.<br/>
    #     There is no restriction on the value of this field.
    # 
    Tuple_dn_hartPayload = collections.namedtuple("Tuple_dn_hartPayload", ['RC', 'payloadLen', 'payload'])

    ##
    # The hartPayload command allows the microprocessor to forward a HART payload to the mote. The format of the command must be as follows:
    # 
    # 16-bit command number | data length | data
    # 
    # The reply (if any) will be in the form of a HART response and sent in the payload of the acknowledgement. This command always returns RC_OK - any HART errors are returned within the response payload, e.g. if a command is not implemented, the response payload field will contain the 16-bit command number, a length = 1, and data = 0x40 (HART RC 64).
    # 
    # \param payloadLen 1-byte field formatted as a int.<br/>
    #     There is no restriction on the value of this field.
    # \param payload None-byte field formatted as a hex.<br/>
    #     There is no restriction on the value of this field.
    # 
    # \returns The response to the command, formatted as a #Tuple_dn_hartPayload named tuple.
    # 
    def dn_hartPayload(self, payloadLen, payload) :
        res = HartMoteConnectorInternal.send(self, ['hartPayload'], {"payloadLen" : payloadLen, "payload" : payload})
        return HartMoteConnector.Tuple_dn_hartPayload(**res)

    ##
    # The named tuple returned by the dn_testRadioTx() function.
    # 
    # - <tt>RC</tt>: 1-byte field formatted as a int.<br/>
    #     This field can only take one of the following values:
    #      - 0: RC_OK
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
    #      - 18: RC_OPEN_FAIL
    #      - 19: RC_ERASE_FAIL
    # 
    Tuple_dn_testRadioTx = collections.namedtuple("Tuple_dn_testRadioTx", ['RC'])

    ##
    # The testRadioTx command initiates transmission over the radio. This command may only be issued prior to the mote joining the network. While executing this command the mote sends numPackets packets. Each packet consists of a payload of up to 125 bytes, and a 2-byte 802.15.4 CRC at the end. Bytes 0 and 1 contain the packet number (in big-endian format) that increments with every packet transmitted. Bytes 2..N contain a counter (from 0..N-2) that increments with every byte inside payload. Transmissions occur on the specified channel.
    # 
    # If number of packets parameter is set to 0x00, the mote will generate an unmodulated test tone on the selected channel. The test tone can only be stopped by resetting the mote.
    # 
    # 
    # 
    # Channel numbering is 0-15, corresponding to IEEE 2.4 GHz channels 11-26.
    # 
    # 
    # 
    # Note: this command is deprecated and should not be used in new designs. The replacement command is testRadioTxExt.
    # 
    # \param channel 1-byte field formatted as a int.<br/>
    #     There is no restriction on the value of this field.
    # \param numPackets 2-byte field formatted as a int.<br/>
    #     There is no restriction on the value of this field.
    # 
    # \returns The response to the command, formatted as a #Tuple_dn_testRadioTx named tuple.
    # 
    def dn_testRadioTx(self, channel, numPackets) :
        res = HartMoteConnectorInternal.send(self, ['testRadioTx'], {"channel" : channel, "numPackets" : numPackets})
        return HartMoteConnector.Tuple_dn_testRadioTx(**res)

    ##
    # The named tuple returned by the dn_testRadioRx() function.
    # 
    # - <tt>RC</tt>: 1-byte field formatted as a int.<br/>
    #     This field can only take one of the following values:
    #      - 0: RC_OK
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
    #      - 18: RC_OPEN_FAIL
    #      - 19: RC_ERASE_FAIL
    # 
    Tuple_dn_testRadioRx = collections.namedtuple("Tuple_dn_testRadioRx", ['RC'])

    ##
    # The testRadioRx command clears all previously collected statistics and initiates a test of radio reception for the specified channel and duration. During the test, the mote keeps statistics about the number of packets received (with and without error). The test results may be retrieved using the getParameter<testRadioRxStats> command. The mote must be reset (either hardware or software reset) after radio tests are complete and prior to joining.
    # 
    # 
    # 
    # Channel numbering is 0-15, corresponding to IEEE 2.4 GHz channels 11-26.
    # 
    # 
    # 
    # Note: this command is deprecated and should not be used in new designs. The replacement command is testRadioRxExt.
    # 
    # \param channel 1-byte field formatted as a int.<br/>
    #     There is no restriction on the value of this field.
    # \param time 2-byte field formatted as a int.<br/>
    #     There is no restriction on the value of this field.
    # 
    # \returns The response to the command, formatted as a #Tuple_dn_testRadioRx named tuple.
    # 
    def dn_testRadioRx(self, channel, time) :
        res = HartMoteConnectorInternal.send(self, ['testRadioRx'], {"channel" : channel, "time" : time})
        return HartMoteConnector.Tuple_dn_testRadioRx(**res)

    ##
    # The named tuple returned by the dn_clearNV() function.
    # 
    # - <tt>RC</tt>: 1-byte field formatted as a int.<br/>
    #     This field can only take one of the following values:
    #      - 0: RC_OK
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
    #      - 18: RC_OPEN_FAIL
    #      - 19: RC_ERASE_FAIL
    # 
    Tuple_dn_clearNV = collections.namedtuple("Tuple_dn_clearNV", ['RC'])

    ##
    # The clearNV command resets the motes Non-Volatile (NV) memory to its factory-default state. Refer to the WirelessHART User Guide for table of default values. Note that since this command clears the mote's security join counter, the corresponding manager's Access Control List (ACL) entry may need to be cleared as well to allow joining.
    # 
    # 
    # 
    # \returns The response to the command, formatted as a #Tuple_dn_clearNV named tuple.
    # 
    def dn_clearNV(self, ) :
        res = HartMoteConnectorInternal.send(self, ['clearNV'], {})
        return HartMoteConnector.Tuple_dn_clearNV(**res)

    ##
    # The named tuple returned by the dn_search() function.
    # 
    # - <tt>RC</tt>: 1-byte field formatted as a int.<br/>
    #     This field can only take one of the following values:
    #      - 0: RC_OK
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
    #      - 18: RC_OPEN_FAIL
    #      - 19: RC_ERASE_FAIL
    # 
    Tuple_dn_search = collections.namedtuple("Tuple_dn_search", ['RC'])

    ##
    # The search command causes the mote to listen for network advertisements and notify the microprocessor about each advertisement it hears. This is referred to as the Promiscuous Listen state. Notifications are sent using the advReceived notification. The search command may only be issued prior to join. The mote stays in listen mode until the join command is received or the mote is reset.
    # 
    # 
    # 
    # \returns The response to the command, formatted as a #Tuple_dn_search named tuple.
    # 
    def dn_search(self, ) :
        res = HartMoteConnectorInternal.send(self, ['search'], {})
        return HartMoteConnector.Tuple_dn_search(**res)

    ##
    # The named tuple returned by the dn_testRadioTxExt() function.
    # 
    # - <tt>RC</tt>: 1-byte field formatted as a int.<br/>
    #     This field can only take one of the following values:
    #      - 0: RC_OK
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
    #      - 18: RC_OPEN_FAIL
    #      - 19: RC_ERASE_FAIL
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
        res = HartMoteConnectorInternal.send(self, ['testRadioTxExt'], {"testType" : testType, "chanMask" : chanMask, "repeatCnt" : repeatCnt, "txPower" : txPower, "seqSize" : seqSize, "pkLen_1" : pkLen_1, "delay_1" : delay_1, "pkLen_2" : pkLen_2, "delay_2" : delay_2, "pkLen_3" : pkLen_3, "delay_3" : delay_3, "pkLen_4" : pkLen_4, "delay_4" : delay_4, "pkLen_5" : pkLen_5, "delay_5" : delay_5, "pkLen_6" : pkLen_6, "delay_6" : delay_6, "pkLen_7" : pkLen_7, "delay_7" : delay_7, "pkLen_8" : pkLen_8, "delay_8" : delay_8, "pkLen_9" : pkLen_9, "delay_9" : delay_9, "pkLen_10" : pkLen_10, "delay_10" : delay_10, "stationId" : stationId})
        return HartMoteConnector.Tuple_dn_testRadioTxExt(**res)

    ##
    # The named tuple returned by the dn_testRadioRxExt() function.
    # 
    # - <tt>RC</tt>: 1-byte field formatted as a int.<br/>
    #     This field can only take one of the following values:
    #      - 0: RC_OK
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
    #      - 18: RC_OPEN_FAIL
    #      - 19: RC_ERASE_FAIL
    # 
    Tuple_dn_testRadioRxExt = collections.namedtuple("Tuple_dn_testRadioRxExt", ['RC'])

    ##
    # The testRadioRxExt command clears all previously collected statistics and initiates a test of radio reception for the specified channel and duration. During the test, the mote keeps statistics about the number of packets received (with and without error). The test results may be retrieved using the getParameter<testRadioRxStats> command. The mote must be reset (either hardware or software reset) after radio tests are complete and prior to joining.
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
    # \returns The response to the command, formatted as a #Tuple_dn_testRadioRxExt named tuple.
    # 
    def dn_testRadioRxExt(self, channelMask, time, stationId) :
        res = HartMoteConnectorInternal.send(self, ['testRadioRxExt'], {"channelMask" : channelMask, "time" : time, "stationId" : stationId})
        return HartMoteConnector.Tuple_dn_testRadioRxExt(**res)

    ##
    # The named tuple returned by the dn_zeroize() function.
    # 
    # - <tt>RC</tt>: 1-byte field formatted as a int.<br/>
    #     This field can only take one of the following values:
    #      - 0: RC_OK
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
    #      - 18: RC_OPEN_FAIL
    #      - 19: RC_ERASE_FAIL
    # 
    Tuple_dn_zeroize = collections.namedtuple("Tuple_dn_zeroize", ['RC'])

    ##
    # The zeroize (zeroise) command erases flash area that is used to store configuration parameters, such as join keys. This command is intended to satisfy the zeroization requirement of the FIPS-140 standard. After the command executes, the mote should be reset. Available in mote >= 1.1.x
    # 
    # The zeroize command will render the mote inoperable. It must be re-programmed via SPI or JTAG in order to be useable.
    # 
    # \param password 4-byte field formatted as a int.<br/>
    #     There is no restriction on the value of this field.
    # 
    # \returns The response to the command, formatted as a #Tuple_dn_zeroize named tuple.
    # 
    def dn_zeroize(self, password) :
        res = HartMoteConnectorInternal.send(self, ['zeroize'], {"password" : password})
        return HartMoteConnector.Tuple_dn_zeroize(**res)

    ##
    # The named tuple returned by the dn_fileWrite() function.
    # 
    # - <tt>RC</tt>: 1-byte field formatted as a int.<br/>
    #     This field can only take one of the following values:
    #      - 0: RC_OK
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
    #      - 18: RC_OPEN_FAIL
    #      - 19: RC_ERASE_FAIL
    # - <tt>length</tt>: 4-byte field formatted as a ints.<br/>
    #     There is no restriction on the value of this field.
    # 
    Tuple_dn_fileWrite = collections.namedtuple("Tuple_dn_fileWrite", ['RC', 'length'])

    ##
    # The fileWrite command may be used to read data stored in the scratchpad file in the mote filesystem. The size of the data read is limited by the size of a serial API transaction.
    # 
    # \param descriptor 4-byte field formatted as a ints.<br/>
    #     There is no restriction on the value of this field.
    # \param offset 2-byte field formatted as a int.<br/>
    #     There is no restriction on the value of this field.
    # \param length 1-byte field formatted as a int.<br/>
    #     There is no restriction on the value of this field.
    # \param data None-byte field formatted as a hex.<br/>
    #     There is no restriction on the value of this field.
    # 
    # \returns The response to the command, formatted as a #Tuple_dn_fileWrite named tuple.
    # 
    def dn_fileWrite(self, descriptor, offset, length, data) :
        res = HartMoteConnectorInternal.send(self, ['fileWrite'], {"descriptor" : descriptor, "offset" : offset, "length" : length, "data" : data})
        return HartMoteConnector.Tuple_dn_fileWrite(**res)

    ##
    # The named tuple returned by the dn_fileRead() function.
    # 
    # - <tt>RC</tt>: 1-byte field formatted as a int.<br/>
    #     This field can only take one of the following values:
    #      - 0: RC_OK
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
    #      - 18: RC_OPEN_FAIL
    #      - 19: RC_ERASE_FAIL
    # - <tt>descriptor</tt>: 4-byte field formatted as a ints.<br/>
    #     There is no restriction on the value of this field.
    # - <tt>offset</tt>: 2-byte field formatted as a int.<br/>
    #     There is no restriction on the value of this field.
    # - <tt>length</tt>: 1-byte field formatted as a int.<br/>
    #     There is no restriction on the value of this field.
    # - <tt>data</tt>: None-byte field formatted as a hex.<br/>
    #     There is no restriction on the value of this field.
    # 
    Tuple_dn_fileRead = collections.namedtuple("Tuple_dn_fileRead", ['RC', 'descriptor', 'offset', 'length', 'data'])

    ##
    # The fileRead command may be used to read data stored in the scratchpad file in the mote filesystem. The size of the data read is limited by the size of a serial API transaction.
    # 
    # \param descriptor 4-byte field formatted as a ints.<br/>
    #     There is no restriction on the value of this field.
    # \param offset 2-byte field formatted as a int.<br/>
    #     There is no restriction on the value of this field.
    # \param length 1-byte field formatted as a int.<br/>
    #     There is no restriction on the value of this field.
    # 
    # \returns The response to the command, formatted as a #Tuple_dn_fileRead named tuple.
    # 
    def dn_fileRead(self, descriptor, offset, length) :
        res = HartMoteConnectorInternal.send(self, ['fileRead'], {"descriptor" : descriptor, "offset" : offset, "length" : length})
        return HartMoteConnector.Tuple_dn_fileRead(**res)

    ##
    # The named tuple returned by the dn_fileOpen() function.
    # 
    # - <tt>RC</tt>: 1-byte field formatted as a int.<br/>
    #     This field can only take one of the following values:
    #      - 0: RC_OK
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
    #      - 18: RC_OPEN_FAIL
    #      - 19: RC_ERASE_FAIL
    # - <tt>descriptor</tt>: 4-byte field formatted as a ints.<br/>
    #     There is no restriction on the value of this field.
    # 
    Tuple_dn_fileOpen = collections.namedtuple("Tuple_dn_fileOpen", ['RC', 'descriptor'])

    ##
    # The fileOpen command may be used to open the scratchpad file in the mote filesystem.
    # 
    # \param name 12-byte field formatted as a hex.<br/>
    #     There is no restriction on the value of this field.
    # \param options 1-byte field formatted as a int.<br/>
    #     This field can only take one of the following values:
    #      - 1: Create the file if it does not exist
    # \param size 2-byte field formatted as a int.<br/>
    #     There is no restriction on the value of this field.
    # \param mode 1-byte field formatted as a int.<br/>
    #     This field can only take one of the following values:
    #      - 1: Others have read permission
    #      - 2: Others have write permission
    #      - 3: Others have read/write permission
    #      - 4: This is a temporary file (it is deleted upon reset or power cycle)
    #      - 8: This file is created in shadow mode (for wear leveling)
    # 
    # \returns The response to the command, formatted as a #Tuple_dn_fileOpen named tuple.
    # 
    def dn_fileOpen(self, name, options, size, mode) :
        res = HartMoteConnectorInternal.send(self, ['fileOpen'], {"name" : name, "options" : options, "size" : size, "mode" : mode})
        return HartMoteConnector.Tuple_dn_fileOpen(**res)

    ##
    # The named tuple returned by the dn_testRadioRxPER() function.
    # 
    # - <tt>RC</tt>: 1-byte field formatted as a int.<br/>
    #     This field can only take one of the following values:
    #      - 0: RC_OK
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
    #      - 18: RC_OPEN_FAIL
    #      - 19: RC_ERASE_FAIL
    # 
    Tuple_dn_testRadioRxPER = collections.namedtuple("Tuple_dn_testRadioRxPER", ['RC'])

    ##
    # The testRadioRxPER command initiates Packet Error Rate (PER) test in rx mode. This command may be issued only when mote is in Idle state.
    # 
    # This command is available in WiHART Mote version 1.2.4.1 or later
    # 
    # 
    # 
    # \returns The response to the command, formatted as a #Tuple_dn_testRadioRxPER named tuple.
    # 
    def dn_testRadioRxPER(self, ) :
        res = HartMoteConnectorInternal.send(self, ['testRadioRxPER'], {})
        return HartMoteConnector.Tuple_dn_testRadioRxPER(**res)

    ##
    # The named tuple returned by the dn_testRadioTxPER() function.
    # 
    # - <tt>RC</tt>: 1-byte field formatted as a int.<br/>
    #     This field can only take one of the following values:
    #      - 0: RC_OK
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
    #      - 18: RC_OPEN_FAIL
    #      - 19: RC_ERASE_FAIL
    # 
    Tuple_dn_testRadioTxPER = collections.namedtuple("Tuple_dn_testRadioTxPER", ['RC'])

    ##
    # The testRadioTxPER command initiates Packet Error Rate (PER) test in tx mode. This command may be issued only when mote is in Idle state.
    # 
    # This command is available in WiHART Mote version 1.2.4.1 or later
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
        res = HartMoteConnectorInternal.send(self, ['testRadioTxPER'], {"txPower" : txPower, "numPackets" : numPackets, "chanMask" : chanMask, "numRepeat" : numRepeat})
        return HartMoteConnector.Tuple_dn_testRadioTxPER(**res)

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
    # For LTC5800-WHM based products, driving the TIMEn pin low (assert) wakes the processor. The pin must asserted for a minimum of t strobe s. De-asserting the pin latches the time, and a timeIndication will be generated within t response ms. Refer to the LTC5800-WHM Datasheet for additional information about TIME pin usage.
    # 
    # The processor will remain awake and drawing current while the TIMEn pin is asserted. To avoid drawing excess current, take care to minimize the duration of the TIMEn pin being asserted past t strobe minimum.
    #
    # Formatted as a Tuple_timeIndication named tuple. It contains the following fields:
    #   - <tt>utcSec</tt> 4-byte field formatted as a int.<br/>
    #     There is no restriction on the value of this field.
    #   - <tt>utcMicroSec</tt> 4-byte field formatted as a int.<br/>
    #     There is no restriction on the value of this field.
    #   - <tt>asn</tt> 5-byte field formatted as a hex.<br/>
    #     There is no restriction on the value of this field.
    #   - <tt>asnOffset</tt> 2-byte field formatted as a int.<br/>
    #     There is no restriction on the value of this field.    
    # 
    TIMEINDICATION = "timeIndication"
    notifTupleTable[TIMEINDICATION] = Tuple_timeIndication = collections.namedtuple("Tuple_timeIndication", ['utcSec', 'utcMicroSec', 'asn', 'asnOffset'])

    ##
    # \brief SERVICEINDICATION notification.
    # 
    # The serviceIndication notification describes new manager-originated services (ID = 0x80-FF), or changes in existing services (ID = 0x00-7F). For more info on when the serviceIndication notification is sent and details about the individual parameters, see Bandwidth Services. If the time field contains the value 0x07FFFFFF , the manager is unable to sustain the service due to network conditions and has effectively disabled the service. The service is not removed, however, and the microprocessor can elect to either delete the service or submit a request to update the service at a future time.
    #
    # Formatted as a Tuple_serviceIndication named tuple. It contains the following fields:
    #   - <tt>eventCode</tt> 1-byte field formatted as a int.<br/>
    #     There is no restriction on the value of this field.
    #   - <tt>netMgrCode</tt> 1-byte field formatted as a int.<br/>
    #     There is no restriction on the value of this field.
    #   - <tt>serviceId</tt> 1-byte field formatted as a int.<br/>
    #     There is no restriction on the value of this field.
    #   - <tt>serviceState</tt> 1-byte field formatted as a int.<br/>
    #     This field can only take one of the following values:
    #      - 0: Inactive
    #      - 1: Active
    #      - 2: Requested
    #   - <tt>serviceFlags</tt> 1-byte field formatted as a int.<br/>
    #     There is no restriction on the value of this field.
    #   - <tt>appDomain</tt> 1-byte field formatted as a int.<br/>
    #     This field can only take one of the following values:
    #      - 0: Publish
    #      - 1: Event
    #      - 2: Maintenance
    #      - 3: Block transfer
    #   - <tt>destAddr</tt> 2-byte field formatted as a hex.<br/>
    #     There is no restriction on the value of this field.
    #   - <tt>time</tt> 4-byte field formatted as a int.<br/>
    #     There is no restriction on the value of this field.    
    # 
    SERVICEINDICATION = "serviceIndication"
    notifTupleTable[SERVICEINDICATION] = Tuple_serviceIndication = collections.namedtuple("Tuple_serviceIndication", ['eventCode', 'netMgrCode', 'serviceId', 'serviceState', 'serviceFlags', 'appDomain', 'destAddr', 'time'])

    ##
    # \brief EVENTS notification.
    # 
    # The events notification sends an event notification packet to the microprocessor informing it of new events that have occurred. The reported event is cleared from the mote when the mote receives an acknowledgement in the form of a response packet from the microprocessor.
    #
    # Formatted as a Tuple_events named tuple. It contains the following fields:
    #   - <tt>events</tt> 4-byte field formatted as a int.<br/>
    #     There is no restriction on the value of this field.
    #   - <tt>state</tt> 1-byte field formatted as a int.<br/>
    #     This field can only take one of the following values:
    #      - 0: Init
    #      - 1: Idle
    #      - 2: Searching
    #      - 3: Negotiating
    #      - 4: Connected
    #      - 5: Operational
    #      - 6: Disconnected
    #      - 7: Radio test
    #      - 8: Promiscuous Listen
    #      - 9: Suspended
    #   - <tt>moteAlarms</tt> 4-byte field formatted as a int.<br/>
    #     There is no restriction on the value of this field.    
    # 
    EVENTS = "events"
    notifTupleTable[EVENTS] = Tuple_events = collections.namedtuple("Tuple_events", ['events', 'state', 'moteAlarms'])

    ##
    # \brief DATARECEIVED notification.
    # 
    # The dataReceived notification notifies the microprocessor that a packet was received. When the microprocessor receives a reliable dataReceived request, in addition to acknowledging the request with a dataReceived response it must also respond using the send command.
    #
    # Formatted as a Tuple_dataReceived named tuple. It contains the following fields:
    #   - <tt>srcAddr</tt> 2-byte field formatted as a hex.<br/>
    #     There is no restriction on the value of this field.
    #   - <tt>seqNum</tt> 1-byte field formatted as a int.<br/>
    #     There is no restriction on the value of this field.
    #   - <tt>pktLength</tt> 1-byte field formatted as a int.<br/>
    #     There is no restriction on the value of this field.
    #   - <tt>data</tt> None-byte field formatted as a hex.<br/>
    #     There is no restriction on the value of this field.    
    # 
    DATARECEIVED = "dataReceived"
    notifTupleTable[DATARECEIVED] = Tuple_dataReceived = collections.namedtuple("Tuple_dataReceived", ['srcAddr', 'seqNum', 'pktLength', 'data'])

    ##
    # \brief ADVRECEIVED notification.
    # 
    # The advReceived notification notifies the microprocessor each time the mote receives an advertisement packet while in promiscuous listen mode. The command contains information about the advertisement, including the Network ID, Mote ID, RSSI, and join priority (hop depth). Note that advReceived notifications are sent only if the mote has been placed in listen mode using the search command (see search).
    #
    # Formatted as a Tuple_advReceived named tuple. It contains the following fields:
    #   - <tt>netId</tt> 2-byte field formatted as a int.<br/>
    #     There is no restriction on the value of this field.
    #   - <tt>moteId</tt> 2-byte field formatted as a hex.<br/>
    #     There is no restriction on the value of this field.
    #   - <tt>rssi</tt> 1-byte field formatted as a ints.<br/>
    #     There is no restriction on the value of this field.
    #   - <tt>joinPri</tt> 1-byte field formatted as a int.<br/>
    #     There is no restriction on the value of this field.    
    # 
    ADVRECEIVED = "advReceived"
    notifTupleTable[ADVRECEIVED] = Tuple_advReceived = collections.namedtuple("Tuple_advReceived", ['netId', 'moteId', 'rssi', 'joinPri'])

    ##
    # \brief SUSPENDSTARTED notification.
    # 
    # The mote generates a suspendStarted notification when it enters the Suspended state as a result of processing Wireless HART command 972. When the suspend interval begins, the mote discontinues its radio operation and generates this notification. After the interval specified in command 972 ends, mote proceeds to reset. It is the responsibility of the attached microprocessor to re-join the network.
    #
    # Formatted as a Tuple_suspendStarted named tuple. It contains the following fields:
    #   - <tt>duration</tt> 4-byte field formatted as a int.<br/>
    #     There is no restriction on the value of this field.    
    # 
    SUSPENDSTARTED = "suspendStarted"
    notifTupleTable[SUSPENDSTARTED] = Tuple_suspendStarted = collections.namedtuple("Tuple_suspendStarted", ['duration'])

    ##
    # \brief TESTRADIOSTATSPER notification.
    # 
    # The testRadioStatsPER notification is generated by the mote when PER test in RX mode is completed.
    # 
    # This command is available in WiHART Mote version 1.2.4 or later.
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
            if  HartMoteConnector.notifTupleTable[ids[-1]] :
                return (ids[-1], HartMoteConnector.notifTupleTable[ids[-1]](**param))
            else :
                return (ids[-1], None)
        except KeyError :
            raise ApiException.NotificationError(ids, param)

##
# end of HartMoteConnector
# \}
# 
