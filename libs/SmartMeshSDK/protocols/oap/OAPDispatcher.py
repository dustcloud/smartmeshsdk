'''
Parse and dispatch an OAP packet to the correct handler based on its type.

Objects wanting to receive callbacks on OAP events can register a
notification callback or a response callback.

A notification callback has the form:
  notif_callback(mac, oap_notif)
  
  The OAPDispatcher parses the notification, oap_notif is an OAPNotif (or
  child) instance.

A response callback has the form:
  resp_callback(mac, oap_resp, oap_transport)
  
  The OAPDispatcher parses the OAP transport header and the OAP response
  into Dicts. The oap_resp Dict has fields for the command type, result
  code and a list of TLV tags. The oap_transport Dict has fields for each
  of the transport flags.
'''

import OAPMessage
import OAPNotif
#from muxclient.FilterExpr import FilterExpr

# TODO: OAP parsing assumes payload data as array
from array import array

class OAPDispatcher(object):
    """
    The OAP Dispatcher receives OAP packets, parses them and calls registered
    callbacks.

    The caller is responsible for ensuring that the dispatchers is subscribed
    to Data notifications with the dispatch_pkt callback.
    """
    
    def __init__(self):
        # TODO: the callback registry should be refactored
        # TODO: is there enough in common with the MuxClient CallbackRegistry
        # to reuse?
        self.response_handlers = []
        self.notif_handlers = []

        # add the dispatcher to OAP data notifications

        # TODO: modify Filters to work
        #oap_filt = FilterExpr()
        #oap_filt.whitelist_attrib('dest_port', OAPMessage.OAP_PORT)

        # TODO: caller must subscribe
        # client.addNotifHook(API.NOTIF_DATA, self.dispatch_pkt, oap_filt)
    
    def register_response_handler(self, resp_cb, filt = None):
        'Register a response handler with an optional filter'
        if not resp_cb in self.response_handlers:
            self.response_handlers.append((resp_cb, filt))
    
    def delete_response_handler(self, resp_cb):
        # TODO: is there any reason to remove only a specific instance of
        # resp_callback + filter?
        # note: the comprehension creates a new list -- probably not a problem
        # since there shouldn't be other copies
        self.response_handlers = [el for el in self.response_handlers 
                                  if not el[0] == resp_cb]
    
    def register_notif_handler(self, notif_cb, filt = None):
        'Register a notification handler with an optional filter'
        if not notif_cb in self.notif_handlers:
            self.notif_handlers.append((notif_cb, filt))
    
    def delete_notif_handler(self, notif_cb):
        # TODO: is there any reason to remove only a specific instance of
        # resp_callback + filter?
        # note: the comprehension creates a new list -- probably not a problem
        # since there shouldn't be other copies        
        self.notif_handlers = [el for el in self.notif_handlers 
                               if not el[0] == notif_cb]
    
    # TODO: for filters to work consistently, the mac should be part of the
    # object passed to filter()
    def _response_callbacks(self, mac, resp, trans):
        for cb in self.response_handlers:
            filt = cb[1]
            if not filt:  # TODO: or filt.filter(resp)
                cb[0](mac, resp, trans)
    
    def _notif_callbacks(self, mac, notif):
        for cb in self.notif_handlers:
            filt = cb[1]
            if not filt:  # TODO: or filt.filter(resp)
                cb[0](mac, notif)
    
    def dispatch_pkt(self, notif_type, data_notif):
        """Parse and dispatch an OAP packet to the correct handler based on its type"""
        if data_notif.dstPort != OAPMessage.OAP_PORT:
            return
    
        payload = array('B', data_notif.data)
        # first two bytes are transport header
        trans = OAPMessage.extract_oap_header(payload)
        # third byte is OAP command type
        cmd_type = payload[2]
        
        #print trans
        #print int(cmd_type)
        
        if trans['response']:
            oap_resp = OAPMessage.parse_oap_response(payload, 2)
            self._response_callbacks(data_notif.macAddress, oap_resp, trans)
            self.last_response = oap_resp
            
        elif cmd_type == OAPMessage.CmdType.NOTIF:
            oap_notif = OAPNotif.parse_oap_notif(payload, 3)
            self._notif_callbacks(data_notif.macAddress, oap_notif)
            self.last_notif = oap_notif
