#!/usr/bin/env python

import socket
import ssl
import threading
import traceback

from SmartMeshSDK import ApiException

# Set up logging

import logging

class NullHandler(logging.Handler):
    def emit(self, record):
        pass

log = logging.getLogger('HartManager')
log.setLevel(logging.INFO)
log.addHandler(NullHandler())


class NotifSeparator(object):
    """Notification Separator

    Implements a simple parser to quickly grab individual notifications from the
    input stream. This object only parses the top-level notification types
    from the stream and treats the notification as a string.

    In the HartMgrConnector, the notification XML string is parsed by
    the HartMgrDefinition. 
    """
    NOTIF_TYPES = [ 'data', 'event', 'measurement', 'log', 'cli', 'stdMoteReport', 'vendorMoteReport' ]

    def __init__(self, cb):
        self.notif_handler = cb
        self.buffer = ''

    def _parse_one(self):
        # look for a notification start element, pick the first one
        current_notif = None
        notif_start = 9999
        for nt in self.NOTIF_TYPES:
            idx = self.buffer.find('<%s>' % nt)
            if idx != -1 and idx < notif_start:
                current_notif = nt
                notif_start = idx
                
        if current_notif:
            end_el = '</%s>' % current_notif
            notif_end = self.buffer.find(end_el)
            if notif_end != -1:
                notif_str = self.buffer[notif_start:notif_end+len(end_el)]
                self.buffer = self.buffer[notif_end+len(end_el):]
                self._handle_notif(current_notif, notif_str)
                return True

        return False

    def parse(self, input_str):
        # Append the input
        self.buffer += input_str
        # Parse as many notifications as possible
        while self._parse_one():
            pass
        
        
    def _handle_notif(self, notif_type, notif_str):
        'Pass the notification to the callback handler and clean up'
        log.debug('NOTIF: %s' % notif_str)
        try:
            # LATER: it might be nice to parse the notification XML here,
            # but that requires a reference to the HartMgrApiDefinition
            self.notif_handler(notif_type, notif_str)
        except Exception as ex:
            log.error('Exception handling notif: ' + str(ex))
            log.debug(traceback.format_exc())


class NotifReader(threading.Thread):
    '''NotifReader listens to the notification channel (TCP socket) and
    pushes notifications into the notification queue in the HartMgrConnector
    (via the handle_notif callback).
    '''

    def __init__(self, host, notif_port, notif_token, use_ssl=False,
                 notif_callback=None, disconnect_callback = None):
        threading.Thread.__init__(self)
        self.name = "NotifReader"
        self.notif_host = host
        self.notif_port = notif_port
        self.notif_token = notif_token
        self.use_ssl = use_ssl
        self.connected = False
        self.disconnect_callback = disconnect_callback
        self.notif_parser = NotifSeparator(notif_callback)

    def _build_auth(self):
        return '<dustnet><authrq><token>%s</token></authrq></dustnet>' % self.notif_token

    def connect(self):
        try:
            self.notif_socket = socket.create_connection((self.notif_host, self.notif_port))
            if self.use_ssl:
                self.notif_socket = ssl.wrap_socket(self.notif_socket)
            log.info("Connected to notification channel")
            # send authentication
            log.debug("Sending notif authentication: %s" % self.notif_token)
            self.notif_socket.send(self._build_auth())
            self.connected = True
        except socket.error as e:
            log.error('Exception reading from notification channel: ' + str(e))
            raise ApiException.ConnectionError(str(e))

    def run(self):
        disconnect_reason = ''
        try:
            while True:
                # read from notif socket
                input_data = self.notif_socket.recv(1024)
                if not input_data:
                    log.info('Notification channel closed')
                    break
                msg = 'Notif input [%d]: %s' % (len(input_data), input_data)
                log.debug(msg)
                try:
                    self.notif_parser.parse(input_data)
                except Exception as e:
                    log.error('Exception parsing notification: ' + str(e))
                    log.debug(traceback.format_exc())
        except socket.error as e:
            log.error('Exception reading from notification channel: ' + str(e))
            disconnect_reason = 'socket error'
        # on disconnect or socket error, the notif thread stops
        if self.disconnect_callback:
            self.disconnect_callback(disconnect_reason)


if __name__ == '__main__':
    import os
    import sys
    import pprint

    sys.path.insert(0, os.path.join(sys.path[0], '..'))
    from HartMgrConnector import HartMgrConnectorInternal

    DEFAULT_HOST = '10.10.16.126'
    DEFAULT_PORT = 4445
    
    pp = pprint.PrettyPrinter()
    
    mgr = HartMgrConnectorInternal.HartMgrConnectorInternal()
    mgr.connect({'host': DEFAULT_HOST, 'port': DEFAULT_PORT})
    
    notif_token, notif_port = mgr.subscribe('data events')
    print ('Subscribe')

    while True:
        notif = mgr.getNotification(1)
        if notif:
            pp.pprint(notif)

    #result = mgr.unsubscribe(notif_token)
    #print 'Unsubscribe'
