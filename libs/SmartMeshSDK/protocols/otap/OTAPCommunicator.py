'''
OTAP Communicator class
'''

from collections import namedtuple
import time
from threading import Condition, Event

from .FileParser import FileParser
from .GenStructs import parse_obj
from .OTAPStructs import *

from .NotifWorker import NotifWorker
from . import ReliableCommander

from SmartMeshSDK.IpMgrConnectorMux import IpMgrConnectorMux
from SmartMeshSDK.IpMgrConnectorMux import IpMgrSubscribe

import logging
class NullHandler(logging.Handler):
    def emit(self, record):
        pass

log = logging.getLogger('OTAPCommunicator')
log.setLevel(logging.INFO)
log.addHandler(NullHandler())

# TODO: look up RC values by name
OK = 0
END_OF_LIST = 11
DISCONNECTED = 5
NACK = 14


# TODO: refactor -- MacAddress should be a class
def print_mac(m):
    return '-'.join(["%02X" % b for b in m])


BROADCAST_ADDR = 8 * [ 0xFF, ]

# delays and timeouts

OtapOptions = namedtuple('OtapOptions', 'broadcast_threshold retry_delay data_retries inter_command_delay post_data_delay wait_timeout reliable_retry_delay reliable_command_timeout reliable_max_retries')

RETRY_DELAY = 1       # retry delay if Picard can't accept the command
DATA_RETRIES = 10     # number of retries before skipping the block 
# TODO: skip or fail?
INTER_COMMAND_DELAY = 3 # inter-packet delay for OTAP commands
POST_DATA_DELAY = 30   # delay after sending all data before sending a status query
WAIT_TIMEOUT = 10      # internal timeout for resetting waits
BROADCAST_THRESHOLD = 1 # threshold for sending OTAP data as broadcast   

DEFAULT_OPTIONS = OtapOptions(
    broadcast_threshold = BROADCAST_THRESHOLD,
    retry_delay = RETRY_DELAY,
    data_retries = DATA_RETRIES,
    inter_command_delay = INTER_COMMAND_DELAY,
    post_data_delay = POST_DATA_DELAY,
    wait_timeout = WAIT_TIMEOUT,
    reliable_retry_delay = ReliableCommander.RETRY_DELAY,
    reliable_command_timeout = ReliableCommander.COMMAND_TIMEOUT,
    reliable_max_retries = ReliableCommander.COMMAND_RETRIES,
    )


class BlockMetadata(object):
    'BlockMetadata contains information about unreceived blocks'

    def __init__(self):
        # blocks: block_num -> (num_dependents, macs)
        self.blocks = {}

    def add_all_dependents(self, max_block_num, all_motes):
        self.clear()
        for n in range(max_block_num):
            self.blocks[n] = (len(all_motes), all_motes)
    
    def add_dependent(self, block_num, mac):
        if not block_num in self.blocks:
            self.blocks[block_num] = (1, [mac])
        else:
            num_deps = self.blocks[block_num][0] + 1
            macs = self.blocks[block_num][1]
            macs.append(mac)
            self.blocks[block_num] = (num_deps, macs)

    def get_meta(self, block_num):
        return self.blocks[block_num]
    
    def clear(self):
        self.blocks.clear()
        
    def blocklist(self):
        blocks = list(self.blocks.keys())
        blocks.sort()
        return blocks

    
class OTAPCommunicator(object):
    '''
    Communicator class for controlling OTAP sessions to a network

    >>> motes = [ ...list of mote macs... ]
    >>> mgr = OTAPCommunicator(send_data, notif_listener, motes)
    >>> mgr.load_file(filename)
    >>> mgr.start_handshake(filename)
    
    '''
    def __init__(self, send_data, notif_listener, motes = None, auto_commit = True,
                 options = DEFAULT_OPTIONS):
        self.send_data = send_data
        self.notif_listener = notif_listener
        self.register()
        self.files = {}
        if motes:
            self.all_motes = motes
        else:
            self.all_motes = []
        self.auto_commit = auto_commit
        self.options = options
        self.transmit_list = BlockMetadata()
        # internal lists of motes
        self.handshake_motes = []
        self.incomplete_motes = []
        self.status_motes = []
        self.commit_motes = []
        self.complete_motes = []
        self.failure_motes = []
        # handle retries and failures
        self.orc = ReliableCommander.ReliableCommander(self.send_data,
                                                       self.handle_failure,
                                                       retry_delay = options.reliable_retry_delay,
                                                       command_timeout = options.reliable_command_timeout,
                                                       max_retries = options.reliable_max_retries)
        self.worker = NotifWorker()
        self.state = 'Init'
        # conditions
        self.data_event = Event()
        self.commit_event = Event()
        
    def load_file(self, filename, is_otap = True):
        self.files[filename] = FileParser(filename, is_otap)

    # for external control, we need to block while work is ongoing
    def wait_for_data_complete(self):
        # wait has a timeout so that we catch user interruptions
        while not self.data_event.is_set():
            self.data_event.wait(self.options.wait_timeout)

    def wait_for_commit_complete(self):
        # wait has a timeout so that we catch user interruptions
        while not self.commit_event.is_set():
            self.commit_event.wait(self.options.wait_timeout)

    def cancel(self):
        'Cancel the OTAP operation, ensure the caller is notified'
        self.notify_data_complete()
        self.notify_commit_complete()
    
    def register(self):
        self.notif_listener.register(self.data_callback)

    def status(self):
        s = "State: %s" % self.state
        s += "\nHandshaking: %s" % self.handshake_motes
        s += "\nIn progress: %s" % self.incomplete_motes
        s += "\nComplete: %s" % self.complete_motes
        s += "\nFailures: %s" % self.failure_motes
        s += "\nTransmit list: %s" % self.transmit_list.blocklist()
        return s

    # ------------------------------------------------------------
    # Callbacks
    
    def data_callback(self, data):
        # handle OTAP command responses
        if data.src_port == OTAP_PORT:
            index = 0
            # parse the payload for ALL responses in the packet
            while index < len(data.payload):
                # handle OTAP command responses
                cmd_type = data.payload[index]
                cmd_len = data.payload[index+1]
                cmd_data = data.payload_str[index+2:index+2+cmd_len]
                # the result of the received callback indicates whether
                # the command response was expected -- don't try to handle
                # unexpected responses
                if self.orc.received(data.mac, cmd_type):
                    if cmd_type == OTAP.HANDSHAKE_CMD:
                        self.worker.add_task(self.handshake_callback,
                                             data.mac, cmd_data)
                    elif cmd_type == OTAP.STATUS_CMD:
                        self.worker.add_task(self.status_callback,
                                             data.mac, cmd_data)
                    elif cmd_type == OTAP.COMMIT_CMD:
                        self.worker.add_task(self.commit_callback,
                                             data.mac, cmd_data)
                
                index += 2 + cmd_len

    def handle_failure(self, mac, cmd_id):
        # insert a task to handle failure so we don't interfere with mote lists
        # while the handshake or status collection task is running
        self.worker.add_task(self.cmd_failure_callback, mac, cmd_id)

    # OTAP response callbacks

    def handshake_callback(self, mac, cmd_data):
        log.info('Got Handshake response from %s' % print_mac(mac))
        log.debug('Data: ' + ' '.join(['%02X' % ord(b) for b in cmd_data]))
        oh_resp = parse_obj(OtapHandshakeResp, cmd_data)
        log.debug(str(oh_resp))

        if not self.state == 'Handshake':
            return

        if not mac in self.handshake_motes:
            log.info('Duplicate handshake response for %s: %d', print_mac(mac), oh_resp.otapResult)
            return
        
        # add a mote that accepts the handshake to the list of motes to send to
        if oh_resp.otapResult == 0:
            # validate mac is in the handshake list
            if mac in self.handshake_motes and not mac in self.incomplete_motes:
                self.incomplete_motes.append(mac)
        else:
            otap_err = otap_error_string(oh_resp.otapResult)
            msg = "Handshake rejected (%s) by %s" % (otap_err, print_mac(mac))
            print (msg)
            log.warning(msg)
        # TODO: handle the delay field
        # remove this mote from the list of expected handshakers
        self.handshake_motes.remove(mac)        
        # once the list of expected handshakers is empty, we're ready to move on
        if not len(self.handshake_motes):
            self.handshake_complete()

            
    def status_callback(self, mac, cmd_data):
        log.info('Got Status response from %s' % print_mac(mac))
        log.debug('Data: ' + ' '.join(['%02X' % ord(b) for b in cmd_data]))
        os_resp = OtapStatusResp()
        os_resp.parse(cmd_data)
        log.debug(str(os_resp))

        if not self.state == 'Status':
            return
        
        # remove this mote from the list of motes we need status from
        if mac in self.status_motes:
            self.status_motes.remove(mac)
        # if missing blocks, add_data_block
        if len(os_resp.missing_blocks):
            for b in os_resp.missing_blocks:
                self.transmit_list.add_dependent(b, mac)
        # otherwise, move the mote to the completed list
        elif os_resp.header.otapResult == 0:
            if mac in self.incomplete_motes:
                log.info('Data transmission to %s is complete' % print_mac(mac))
                self.incomplete_motes.remove(mac)
                self.complete_motes.append(mac)
        else:
            # no missing blocks, but status is an error
            if mac in self.incomplete_motes:
                msg = 'Status error (%s) for %s, declaring failure' % (otap_error_string(os_resp.header.otapResult), print_mac(mac))
                log.error(msg)
                self.incomplete_motes.remove(mac)
                self.failure_motes.append(mac)
        
        # TODO: handle the response that indicates the mote has reset or forgotten
        # about this OTAP session
        self.check_status_complete()

    def check_status_complete(self):
        # determine whether it's time to move to a new state
        # if there are no more incomplete motes, we're done sending data
        if not len(self.incomplete_motes):
            self.data_complete()
        # otherwise, we need to send more data when we've received all the statuses
        elif not len(self.status_motes):
            self.start_data()

            
    def commit_callback(self, mac, cmd_data):
        log.info('Got Commit response from %s' % print_mac(mac))
        log.debug('Data: ' + ' '.join(['%02X' % ord(b) for b in cmd_data]))
        oc_resp = parse_obj(OtapCommitResp, cmd_data)
        log.debug(str(oc_resp))
        
        if not self.state == 'Commit':
            return

        if mac in self.commit_motes:
            self.commit_motes.remove(mac)
            if oc_resp.otapResult == 0:
                fcs = self.files[self.current_file].fcs
                msg = '%s committed %s [FCS=0x%04x]' % (print_mac(mac),
                                                        self.current_file,
                                                        fcs)
                print (msg)
                log.info(msg)
            else:
                msg = 'Commit error (%s) on %s' % (otap_error_string(oc_resp.otapResult), print_mac(mac))
                print (msg)
                log.error(msg)
                self.complete_motes.remove(mac)
                self.failure_motes.append(mac)
                
        # detect when all motes have responded to the commit
        if not len(self.commit_motes):
            self.commit_complete()
        
    def cmd_failure_callback(self, mac, cmd_id):
        log.error('Command failure for %s, command %d' % (print_mac(mac), cmd_id))
        self.failure_motes.append(mac)
        # TODO: remove the failed mote from the all_motes list for the next file(s)?
        # remove the failed mote from the internal lists
        if mac in self.handshake_motes:
            self.handshake_motes.remove(mac)
        if mac in self.incomplete_motes:
            self.incomplete_motes.remove(mac)
        if mac in self.status_motes:
            self.status_motes.remove(mac)
        if mac in self.commit_motes:
            self.commit_motes.remove(mac)
        if mac in self.complete_motes:
            self.complete_motes.remove(mac)
        # detect if this command failure means we need to change state
        if self.state == 'Handshake' and not len(self.handshake_motes):
            self.handshake_complete()
        if self.state == 'Status':
            self.check_status_complete()
        if self.state == 'Commit' and not len(self.commit_motes):
            self.commit_complete()
    
    # ------------------------------------------------------------
    # Handshake operations

    def build_handshake(self, filename):
        # TODO: load file if not already loaded
        otap_file = self.files[filename]
        hs_data = otap_file.get_handshake_data()
        self.current_file = filename  # TODO: use FileParser object?
        self.current_mic = otap_file.mic
        try:
            hs_dump = ' '.join(['%02X' % ord(c) for c in hs_data])
        except TypeError:
            hs_dump = ' '.join(['%02X' % c for c in hs_data])
        log.debug('Handshake data [%d]: %s' % (len(hs_data), hs_dump))
        return hs_data

    
    def start_handshake(self, filename):
        self.worker.add_task(self.handshake_task, filename)
        
    def handshake_task(self, filename):        
        self.state = 'Handshake'
        msg = 'Starting handshake with %d motes' % len(self.all_motes)
        print (msg)
        log.info(msg)
        cmd_data = self.build_handshake(filename)
        # clear the various mote lists
        self.incomplete_motes = []
        self.complete_motes = []
        self.handshake_motes = self.all_motes[:]  # make a copy
        for m in self.handshake_motes:
            # send handshake command to each mote
            self.send_reliable_cmd(m, OTAP.HANDSHAKE_CMD, cmd_data)

    def handshake_complete(self):
        # build the list of blocks to send
        msg = 'Handshake completed, %d motes accepted' % len(self.incomplete_motes)
        print (msg)
        log.info(msg)
        if len(self.incomplete_motes):
            # initially, the list of blocks to send is all blocks to all
            # accepted (incomplete) motes
            num_blocks = len(self.files[self.current_file].blocks)
            self.transmit_list.add_all_dependents(num_blocks, self.incomplete_motes)
            self.start_data()        
        else:
            self.state = ''
            # if there are no motes to send to, signal the end of this operation
            self.cancel()
            
    # ------------------------------------------------------------
    # Data and Status operations
    
    def start_data(self):
        self.worker.add_task(self.data_task)

    def data_task(self):
        self.state = 'Data'
        blist = self.transmit_list.blocklist()
        msg = 'Starting data transmission of %d blocks, %d motes left' % (len(blist), len(self.incomplete_motes))
        print (msg)
        log.info(msg)
        file_info = self.files[self.current_file]
        try:
            for bnum in blist:
                block_data = file_info.blocks[bnum]
                cmd = OtapData(file_info.mic, bnum, block_data)
                (deps, macs) = self.transmit_list.get_meta(bnum)
                if deps <= self.options.broadcast_threshold and len(macs):
                    for m in macs:
                        log.info('Sending block %d to %s' % (bnum, print_mac(m)))
                        self.send_otap_cmd(m, OTAP.DATA_CMD, cmd.serialize())
                else:
                    log.info('Sending block %d via broadcast' % (bnum))
                    self.send_otap_cmd(BROADCAST_ADDR, OTAP.DATA_CMD, cmd.serialize())
                # wait for inter-command delay
                time.sleep(self.options.inter_command_delay)

        except IOError:
            log.error('Manager disconnected. Cancelling OTAP operation')
            self.cancel()
            return
            
        log.info('Finished sending data')
        # wait before querying status
        time.sleep(self.options.post_data_delay)
        self.start_status()

    def start_status(self):
        self.worker.add_task(self.status_task)
        
    def status_task(self):
        self.state = 'Status'
        msg = 'Starting status query to %d motes' % len(self.incomplete_motes)
        print (msg)
        log.info(msg)
        self.transmit_list.clear()
        self.status_motes = self.incomplete_motes[:]
        for m in self.status_motes:
            # send status command to each mote
            log.debug('Sending status to %s' % (print_mac(m)))
            self.send_reliable_cmd(m, OTAP.STATUS_CMD, struct.pack('!L', self.current_mic))

    def notify_data_complete(self):
        self.data_event.set()
            
    def data_complete(self):
        log.info('Data complete')
        print ('Data complete. No motes left on incomplete list')
        if self.auto_commit:
            self.start_commit(self.current_file)
        else:
            print (("Call start_commit('%s') to send OTAP commit" % self.current_file))
        # the completion signal is always the last step in the callback
        self.notify_data_complete()

    # ------------------------------------------------------------
    # Commit operations

    def start_commit(self, filename):
        if len(self.complete_motes):
            self.worker.add_task(self.commit_task, filename)
        else:
            self.commit_complete()
    
    def commit_task(self, filename = ''):
        commit_file = filename
        if not commit_file:
            commit_file = self.current_file
        commit_mic = self.files[commit_file].mic
        self.state = 'Commit'
        msg = "Starting commit for '%s' to %d motes" % (commit_file, len(self.complete_motes))
        print (msg)
        log.info(msg)
        self.commit_motes = self.complete_motes[:]
        for m in self.commit_motes:
            # send commit command to each mote
            self.send_reliable_cmd(m, OTAP.COMMIT_CMD, struct.pack('!L', commit_mic))

    def notify_commit_complete(self):
        self.commit_event.set()
    
    def commit_complete(self):
        log.info('Commit complete')
        # TODO: format the mote lists
        if len(self.complete_motes):
            msg = 'Successful OTAP to:\n'
            msg += '\n'.join(print_mac(m) for m in self.complete_motes)
            print (msg)
            log.info(msg)
        if len(self.failure_motes):
            msg = 'Failures:\n'
            msg += '\n'.join(print_mac(m) for m in self.failure_motes)
            print (msg)
            log.error(msg)
        # the completion signal is always the last step in the callback
        self.notify_commit_complete()
        
    
    # send a command to a mote

    def send_otap_cmd(self, mac, cmd_id, data):
        cmd = struct.pack('BB', cmd_id, len(data)) + data
        count = 0
        (rc, cbid) = self.send_data(mac, cmd, OTAP_PORT)
        while rc != 0 and count < self.options.data_retries:
            if rc == END_OF_LIST:
                # if the mote doesn't exist, return
                log.error('Mote %s is not in the network' % (print_mac(mac)))
                return
            elif rc == DISCONNECTED:
                # if we're disconnected, raise hell
                raise IOError('Manager disconnected')
            # Otherwise, wait and retry several times
            time.sleep(self.options.retry_delay)
            log.debug('Resending otap block to %s, error: %d' % (print_mac(mac), rc))
            (rc, cbid) = self.send_data(mac, cmd, OTAP_PORT)
            count += 1

    def send_reliable_cmd(self, mac, cmd_id, data):
        result = self.orc.send(mac, OTAP_PORT, cmd_id, data)
        # wait for the inter-command delay after sending any reliable message
        time.sleep(self.options.inter_command_delay)
        return result

