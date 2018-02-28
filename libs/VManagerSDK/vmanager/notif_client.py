'''Notifications API

The NotifClient manages client connections to the notification resource. The 
NotifClient creates a NotifThread to handle reading notifications from the stream. 
The NotifClient uses a Queue to hold parsed notifications that are ready to be 
handled by the application.

Usage:

>>> client = NotifClient(BASE_URL, api_client)
>>> notif_thread = client.get_notifications(my_filter)
>>> notif_thead.start()

>>> notif_queue = client.get_notif_queue()
>>> notif = notif_queue.get()

'''

import os
import threading
import json
import logging

try:
    # for python3
    from queue import Queue
except ImportError:
    # for python2
    from Queue import Queue

# import all notifications
from .models import data_packet_received
from .models import ip_packet_received
from .models import device_health_report
from .models import neighbor_health_report
from .models import discovery_health_report
from .models import raw_mote_notification
from .models import mote_state_changed
from .models import ap_state_changed
from .models import path_state_changed
from .models import service_changed
from .models import ping_response
from .models import join_failed
from .models import invalid_mic
from .models import alarm_opened
from .models import alarm_closed
from .models import packet_sent
from .models import cmd_finished
from .models import config_changed
from .models import config_deleted
from .models import config_loaded
from .models import config_restored
from .models import manager_started
from .models import manager_stopping
from .models import opt_phase
from .models import path_alert
from .models import ap_gps_sync_changed
from .models import frame_capacity
from .models import mote_trace

log = logging.getLogger('vmanager.notif_client')

class NotifThread(threading.Thread):
    '''Thread for receiving notification objects
    '''
    def __init__(self, response, callback, disconnect_callback):
        threading.Thread.__init__(self, target=self.run)
        self.daemon = True
        self.response = response
        self.callback = callback
        self.disconnect_callback = disconnect_callback
        self.input_buffer = ''
        self.start()

    def stop(self):
        self.done = True

    def parse_notif(self, notif_input):
        notif_input = notif_input.decode('utf-8')
        self.input_buffer += notif_input
        notifs = self.input_buffer.split('\r\n')
        # the last element of notifs is empty if the input ended with \r\n
        # or it contains the start of the next notif
        self.input_buffer = notifs.pop()
        for notif_str in notifs:
            try:
                notif_json = json.loads(notif_str)
                self.callback(notif_json)
            except ValueError:
                log.warning('warning: can not parse notif: "{0}"'.format(notif_str))
        
    def run(self):
        self.done = False
        try:
            for chunk in self.response.getstream():
                self.parse_notif(chunk)
                if self.done:
                    break
        except:
            log.info('notification connection closed')
            self.disconnect_callback()

# TODO: can this be generated ?
NOTIF_TYPE_MAP = {
    # Data
    'dataPacketReceived': data_packet_received.DataPacketReceived,
    'ipPacketReceived': ip_packet_received.IpPacketReceived,
    # Health Reports
    'deviceHealthReport': device_health_report.DeviceHealthReport,
    'neighborHealthReport': neighbor_health_report.NeighborHealthReport,
    'discoveryHealthReport': discovery_health_report.DiscoveryHealthReport,
    'rawMoteNotification': raw_mote_notification.RawMoteNotification,
    # Events
    'moteStateChanged': mote_state_changed.MoteStateChanged,
    'apStateChanged': ap_state_changed.ApStateChanged,
    'pathStateChanged': path_state_changed.PathStateChanged,
    'serviceChanged': service_changed.ServiceChanged,
    'pingResponse': ping_response.PingResponse,
    'joinFailed': join_failed.JoinFailed,
    'invalidMIC': invalid_mic.InvalidMIC,
    'alarmOpened': alarm_opened.AlarmOpened, 
    'alarmClosed': alarm_closed.AlarmClosed,
    'packetSent': packet_sent.PacketSent,
    'cmdFinished': cmd_finished.CmdFinished,
    'managerStarted': manager_started.ManagerStarted,
    'managerStopping': manager_stopping.ManagerStopping,
    'pathAlert': path_alert.PathAlert,
    'optPhase': opt_phase.OptPhase,
    'apGpsSyncChanged': ap_gps_sync_changed.ApGpsSyncChanged,
    'frameCapacity': frame_capacity.FrameCapacity,
    'moteTrace': mote_trace.MoteTrace,
    # Config
    'configChanged': config_changed.ConfigChanged,
    'configDeleted': config_deleted.ConfigDeleted,
    'configLoaded': config_loaded.ConfigLoaded,
    'configRestored': config_restored.ConfigRestored,
}

class QueueFinished(object):
    def __init__(self):
        self.type = 'queueFinished'

class NotifClient(object):
    '''Client for handling notification connections
    '''
    def __init__(self, base_url, api_client):
        self.base_url = base_url
        self.api_client = api_client
        self.queue = Queue()
        self.thread = None
        self.notif_response = None
        self.auth_settings = ['dust_basic']

    def _handle_notif(self, notif_json):
        try:
            notif_type = notif_json['type']
            notif_klass = NOTIF_TYPE_MAP[notif_type]
            notif_obj = self.api_client.deserialize_json(notif_json, notif_klass)
            self.queue.put(notif_obj)
        except KeyError:
            log.warning('warning: unknown notification type: ' + notif_type)

    def _handle_disconnect(self):
        self.queue.put(QueueFinished())

    def get_notif_queue(self):
        '''Returns the queue which holds parsed notifications
        '''
        return self.queue

    def get_notifications(self, notif_filter=None):
        '''Start a notification connection
        '''
        notif_url = self.base_url + '/notifications'
        headers = {}
        query_params = []
        if notif_filter:
            query_params = [('filter', notif_filter)]
        # sanitize parameters
        query_params = self.api_client.sanitize_for_serialization(query_params)
        # set up authentication
        self.api_client.update_params_for_auth(headers, query_params, 
                                               self.auth_settings)
        # start the notification connection
        resp = self.api_client.rest_client.GET(notif_url, headers=headers, 
                                               query_params=query_params, stream=True)
        # the request raises an ApiException when the response has an error status
        self.notif_response = resp
        self.thread = NotifThread(resp, self._handle_notif, self._handle_disconnect)
        # the thread is started by the caller
        return self.thread
    
    def stop(self):
        if self.notif_response:
            self.notif_response.close()

