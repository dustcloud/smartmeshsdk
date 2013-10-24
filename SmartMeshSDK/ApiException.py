'''
Created on Mar 6, 2012

\author alushin
'''

class ConnectionError(Exception) :
    '''
    \brief Exception class associated with connection to the device.
    '''
    
    def __init__(self, reason):
        self.value = reason

    def __str__(self) :
        return "Connection Error: {0}".format(self.value)
        
class QueueError(Exception) :
    def __init__(self):
        pass

class CommandTimeoutError(Exception) :
    '''
    \brief Device timeout error (disconnection)
    '''
    def __init__(self, cmd):
        self.cmd = cmd
    def __str__(self) :
        return "Device timeout error for command {0}".format(self.cmd)
    
class APIError(Exception) :
    '''
    \brief Exception class associated with connection the API.
    '''
    
    def __init__(self, cmd, rc, desc=None):
        self.cmd   = cmd
        self.rc    = rc
        self.desc  = desc

    def __str__(self) :
        return "Command {0} returns RC={1} {2}".format(self.cmd,
                                                       self.rc,
                                                       self.desc)

class NotificationError(Exception) :
    def __init__(self, notifIds, params):
        self.notifIds = notifIds
        self.params  = params

    def __str__(self) :
        return "Notification {0} params {1}".format(self.notifIds, self.params)
    
class CommandError(Exception):
    '''
    \brief Exception class associated with an API definition.
    '''
    
    INVALID_COMMAND          = 1
    INVALID_SUBCOMMAND       = 2
    ONLY_SUBCOMMANDS         = 3
    NO_SUBCOMMANDS           = 4
    UNKNOWN_SUBCOMMAND       = 5
    NO_REQUEST               = 6
    NO_RESPONSE              = 7
    TOO_FEW_FIELDS           = 8
    TOO_MANY_FIELDS          = 9
    UNKNOWN_FIELD            = 10
    MALFORMED_FIELD          = 11
    TOO_FEW_BYTES            = 12
    VALUE_NOT_IN_OPTIONS     = 14
    
    descriptions = { 
        INVALID_COMMAND:     'Command does not exist', 
        INVALID_SUBCOMMAND:  'Subcommand does not exist', 
        ONLY_SUBCOMMANDS:    'This function has subcommands only', 
        NO_SUBCOMMANDS:      'This function does not have any subcommands', 
        UNKNOWN_SUBCOMMAND:  'This subcommand does not exist', 
        NO_REQUEST:          'No request format defined for this command', 
        NO_RESPONSE:         'No response format defined for this command', 
        TOO_FEW_FIELDS:      'Too few fields passed', 
        TOO_MANY_FIELDS:     'Too many fields passed', 
        UNKNOWN_FIELD:       'Unknown field', 
        MALFORMED_FIELD:     'Field malformed',
        TOO_FEW_BYTES:       'Too few bytes in received packet',
        VALUE_NOT_IN_OPTIONS:'The value of this field is not in the valid options',
    }
    
    def __init__(self,errorCode,details=None):
        self.errorCode  = errorCode
        self.details    = details
    
    def __str__(self):
        try:
            output = self.descriptions[self.errorCode]
            if self.details:
                output += ': ' + str(self.details)
            return output
        except KeyError:
            return "Unknown error: #" + str(self.errorCode)