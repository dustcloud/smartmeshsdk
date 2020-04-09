import copy
import xmlrpc.client

from .NotifReader                  import NotifReader

from SmartMeshSDK                 import ApiException
from SmartMeshSDK.ApiConnector    import ApiConnector
from SmartMeshSDK.ApiDefinition   import HartMgrDefinition

# Add a log handler for the HART Manager

import logging
class NullHandler(logging.Handler):
    def emit(self, record):
        pass

log = logging.getLogger('HartManager')
log.setLevel(logging.INFO)
log.addHandler(NullHandler())

##
# \ingroup ApiConnector
# 
class HartMgrConnectorInternal(ApiConnector):
    '''\brief Connector object for WirelessHART Manager using the XML API
    '''

    DEFAULT_HOST = '192.168.99.100'
    DEFAULT_PORT = 4445
    DEFAULT_USER = 'admin'
    DEFAULT_PASS = 'admin'

    DEFAULT_CONNECT_PARAMS = {'host':     DEFAULT_HOST,
                              'port':     DEFAULT_PORT,
                              'user':     DEFAULT_USER,
                              'password': DEFAULT_PASS,
                              'use_ssl':  False,
                              }

    def __init__(self):
        # TODO: init super?
        ApiConnector.__init__(self) # TODO: maxQSize
        self.apidef = HartMgrDefinition.HartMgrDefinition()
        self.manager = None
        self.login_token = None
        self.notif_token = None
        self.notif_thread = None

    def getApiDefinition(self):
        return self.apidef

    def _init_xmlrpc(self, host, port, use_ssl = False):
        scheme = 'http' if not use_ssl else 'https'
        xmlrpc_url = "%s://%s:%d" % (scheme, host, port)
        rpc_client = xmlrpc.client.ServerProxy(xmlrpc_url)        
        # xmlrpclib.Fault exceptions are passed up to the caller
        return rpc_client
        
    def connect(self, resource):
        # set up the connection parameters
        self.connect_params = copy.copy(self.DEFAULT_CONNECT_PARAMS)
        self.connect_params.update(resource)        
        # TODO: allow HTTPS
        try:
            self.manager = self._init_xmlrpc(self.connect_params['host'],
                                             int(self.connect_params['port']),
                                             bool(self.connect_params['use_ssl']))

            self.login(self.connect_params['user'], self.connect_params['password'])

        except xmlrpc.client.Fault as ex:
            log.error(str(ex))
            raise ApiException.ConnectionError(str(ex))
        log.info('Connected to %s' % self.connect_params['host'])
        ApiConnector.connect(self)

    def disconnect(self, reason = None):
        self.unsubscribe_override(['unsubscribe'], {})
        self.logout()
        log.info('Disconnected from %s' % self.connect_params['host'])
        ApiConnector.disconnect(self, reason)
        

    def send(self, cmd_name, cmd_params):
        # ensure the application is connected
        if not self.login_token:
            raise ApiException.ConnectionError('not connected')
        
        # handle command overrides - replacement methods for processing a command
        cmd_metadata = self.apidef.getDefinition(self.apidef.COMMAND, cmd_name)
        if 'command_override' in cmd_metadata:
            cmd_override = getattr(self, cmd_metadata['command_override'])
            resp = cmd_override(cmd_name, cmd_params)
            return resp
        
        # construct the XML-RPC parameter list
        # validation happens automatically as part of serialization
        param_list = self.apidef.serialize(cmd_name, cmd_params)
        log.info('Sending %s: %s' % (cmd_name, param_list))

        # call method by string name, params is a list of the parameters
        params = [self.login_token] + param_list
        cmd_id = self.apidef.nameToId(self.apidef.COMMAND, cmd_name)
        try: 
            xmlrpc_resp = getattr(self.manager, cmd_id)(*params)
        except xmlrpc.client.Fault as ex:
            log.error(str(ex))
            raise ApiException.APIError(cmd_name[0], str(ex))

        log.info('Received response %s: %s' % (cmd_name, xmlrpc_resp))
        # call deserialize to parse the response into a dict
        resp = self.apidef.deserialize(cmd_name, xmlrpc_resp)
        
        # call a command-specific post-processor method
        cmd_metadata = self.apidef.getDefinition(self.apidef.COMMAND, cmd_name)
        if 'post_processor' in cmd_metadata:
            post_processor = getattr(self, cmd_metadata['post_processor'])
            post_processor(resp)
        return resp
    

    def login(self, user = DEFAULT_USER, password = DEFAULT_PASS):
        # TODO: what if we need to reauthenticate?
        if not self.login_token:
            result = self.manager.login(user, password)
            # LATER: add some processing to detect faults
            self.login_token = result
        return self.login_token
    
    def logout(self):
        if self.login_token:
            try:
                result = self.manager.logout(self.login_token)
            except xmlrpc.client.Fault:
                pass
            self.login_token = None

    # ----------------------------------------------------------------------
    # notification management methods

    def subscribe_override(self, cmd_name, cmd_params):
        'Implement the subscribe operation'
        # create a new notif session unless a notif session already exists
        token = self.login_token
        if self.notif_token:
            token = self.notif_token
        try:
            notif_filter = cmd_params['filter']
        except KeyError:
            raise ApiException.APIError(ApiException.CommandError.TOO_FEW_FIELDS,
                                        "expected 'filter' parameter")
        # call the Manager API subscribe command
        try:
            log.info('Sending %s: %s' % (cmd_name, [token, notif_filter]))
            (self.notif_token, self.notif_port) = self.manager.subscribe(token, notif_filter)
            log.info('Received response %s: %s %s' % (cmd_name, self.notif_token, self.notif_port))

        except xmlrpc.client.Fault as ex:
            log.error(str(ex))
            raise ApiException.APIError(cmd_name[0], str(ex))

        # create the notification thread
        if not self.notif_thread:
            self.notif_thread = NotifReader(self.connect_params['host'],
                                            int(self.notif_port),
                                            self.notif_token,
                                            use_ssl=self.connect_params['use_ssl'],
                                            notif_callback=self.handle_notif,
                                            disconnect_callback=self.handle_notif_disconnect)
            self.notif_thread.connect()
            self.notif_thread.daemon = True
            self.notif_thread.start()
        return {'notif_token': self.notif_token}

    def unsubscribe_override(self, cmd_name, cmd_params):
        'Implement the unsubscribe operation'
        try:
            if self.notif_token:
                log.info('Sending %s: %s' % (cmd_name, self.notif_token))
                resp = self.manager.unsubscribe(self.notif_token)
                log.info('Received response %s: %s' % (cmd_name, resp))
                self.notif_thread.join()
                self.notif_thread = None
                self.notif_token = None
            return {'result': "OK"}
        except xmlrpc.client.Fault as ex:
            log.error(str(ex))
            raise ApiException.APIError(cmd_name[0], str(ex))

    def handle_notif_disconnect(self, reason):
        'Handle a disconnection from the notification channel'
        self.queue.putDisconnectNotification(reason)

    def handle_notif(self, notif_name, notif_str):
        'Parse a notification'
        try:
            notif = self.apidef.parse_notif([notif_name], notif_str)
            log.info('Received notification %s: %s', notif_name, str(notif))
            self.putNotification(notif)
        except ApiException.CommandError as ex:
            log.warn('Unknown notification type %s: %s', notif_name, notif_str)
        
