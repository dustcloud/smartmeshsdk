import struct
import time

from threading import Timer, Lock

# for Error Codes
from SmartMeshSDK.IpMgrConnectorMux import IpMgrConnectorMux

import logging
class NullHandler(logging.Handler):
    def emit(self, record):
        pass

log = logging.getLogger('ReliableCmd')
log.setLevel(logging.INFO)
log.addHandler(NullHandler())

# TODO: look up NACK RC by name
NACK = 14

RETRY_DELAY = 10      # retry delay if Picard can't accept the command
COMMAND_TIMEOUT = 30  # timeout for resending the command to the mote
COMMAND_RETRIES = 5   # number of retries before declaring the mote non-responsive

# TODO: refactor -- MacAddress should be a class
def print_mac(m):
    return '-'.join(["%02X" % b for b in m])


class ReliableCmd(object):
    'Structure for tracking reliable commands'
    
    def __init__(self, mac, port, cmd_id, data, command_timeout):
        self.mac = mac
        self.port = port
        self.cmd_id = cmd_id
        self.data = data
        self.command_timeout = command_timeout
        self.attempts = 0
        self.timer = None
        self.timer_lock = Lock()
        
    def macstr(self):
        return ''.join(['%02X' % b for b in self.mac])
        
    def start_timer(self, timeout_handler):
        with self.timer_lock:
            self.attempts += 1
            self.timer = Timer(self.command_timeout, timeout_handler, [self])
            self.timer.start()
        
    def stop_timer(self):
        with self.timer_lock:
            if self.timer:
                self.timer.cancel()
                self.timer = None


class ReliableCommander(object):
    '''Controller object for making sendData commands reliable

    The caller hands off responsibility for sending the command to the
    ReliableCommander object. The caller must call the received() method when
    it detects a response to an outstanding command.

    There can only be one "in progress" command to any mote.
    
    >>> orc = ReliableCommander(send_data, handle_failure)
    >>> orc.send([...mac...], OTAP.STATUS_CMD, data)
    ...
    ... somewhere in the data notification handler ...
    >>> orc.received([...mac...], OTAP.STATUS_CMD)
    
    '''
    
    def __init__(self, send_data, failure_cb,
                 retry_delay = RETRY_DELAY,
                 command_timeout = COMMAND_TIMEOUT,
                 max_retries = COMMAND_RETRIES):
        self.send_data = send_data
        self.failure_callback = failure_cb
        self.retry_delay = retry_delay
        self.command_timeout = command_timeout
        self.max_retries = max_retries
        self.in_progress = {}
        self.lock = Lock()  # multiple threads might access the in_progress dict

    def send(self, mac, port, cmd_id, data):
        'Send a command to a mote via sendData (with retries) until the mote replies'

        log.info('ORC sending cmd %d to %s' % (cmd_id, print_mac(mac)))
        otapcmd = ReliableCmd(mac, port, cmd_id, data, self.command_timeout)
        
        # record the operation in the in_progress map
        with self.lock:
            if not otapcmd.macstr() in self.in_progress:
                self.in_progress[otapcmd.macstr()] = otapcmd
            else:
                return -1

        self._send(otapcmd)

    def _send(self, otapcmd):
        'Internal send command. Try to send the command until Picard accepts it'     
        log.info('ORC (re)sending cmd to %s, attempt %d' % (print_mac(otapcmd.mac),
                                                            otapcmd.attempts))
        cmd = struct.pack('BB', otapcmd.cmd_id, len(otapcmd.data)) + otapcmd.data
        rc = NACK
        cbid = -1
        try:
            while rc == NACK:
                log.debug('Sending cmd for %s to Picard' % print_mac(otapcmd.mac))
                (rc, cbid) = self.send_data(otapcmd.mac, cmd, otapcmd.port)
                if rc == NACK:
                    time.sleep(self.retry_delay)
        except IOError:
            rc = -1
        
        # Because of timeouts and previous commands in transit, it's possible that
        # we will receive a response (to a previous command) while we're in the 
        # process of sending this command.
        # Therefore, before starting a timer, we need to check that we haven't already
        # received a response. 

        if rc == 0:
            with self.lock:
                # only start the timer if this command is still "in progress"
                macstr = otapcmd.macstr()
                if macstr in self.in_progress:
                    otapcmd.start_timer(self.handle_timeout)
                else:
                    log.info('Not setting timer for command %d to %s, response received',
                             otapcmd.cmd_id, print_mac(otapcmd.mac))
        else:
            log.debug('Picard returns rc %d for mote %s' % (rc, print_mac(otapcmd.mac)))
            self.handle_failure(otapcmd, rc)
        return cbid
    
    def handle_timeout(self, otapcmd):
        'Handle the command timeout'
        log.info('ORC timeout for %s, command %d' % (print_mac(otapcmd.mac),
                                                     otapcmd.cmd_id))
        if otapcmd.attempts < self.max_retries:
            self._send(otapcmd)
        else:
            self.handle_failure(otapcmd)

    def handle_failure(self, otapcmd, rc = 'timeout'):
        'Declare the command failed (too many retries or mote lost)'
        log.info('ORC declaring failure for %s, command %d, rc %s' % (print_mac(otapcmd.mac),
                                                               otapcmd.cmd_id,
                                                               str(rc)))
        # remove the cmd from in_progress dict
        self.in_progress.pop(otapcmd.macstr(), None)
        # call the failure_callback
        self.failure_callback(otapcmd.mac, otapcmd.cmd_id)
        
    def received(self, mac, cmd_id):
        '''Callback for command responses
        Returns: whether the response was expected based on an active command
        '''
        log.info('ORC received cmd %d from %s' % (cmd_id, print_mac(mac)))
        macstr = ''.join(['%02X' % b for b in mac])
        # the result indicates whether the command was "expected"
        result = False
        with self.lock:
            if macstr in self.in_progress:
                otapcmd = self.in_progress[macstr]
                if otapcmd.cmd_id == cmd_id:
                    self.in_progress.pop(macstr)
                    otapcmd.stop_timer()
                    result = True
                else:
                    # a different command is in progress ?!?
                    log.error('ORC received unexpected command type from %s, command %d, expecting %d' % (print_mac(mac), cmd_id, otapcmd.cmd_id))
                    
            else:
                # not expecting anything from this mote
                log.warning('ORC received unexpected response from %s, command %d, expecting nothing' % (print_mac(mac), cmd_id))
        return result
