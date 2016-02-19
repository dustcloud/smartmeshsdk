import OAPMessage
import OAPDispatcher

# from muxclient.FilterExpr import FilterExpr

class OAPClient(object):
    '''
    Transport manager for specific mote

    send_data is the SmartMesh IP sendData API function
    '''
    
    def __init__(self, mac, send_data, dispatch):
        self.mac             = mac
        self.session_id      = 0
        self.seq_num         = 0
        self.message_queue   = []
        
        self.send_data       = send_data
        self.dispatch        = dispatch
        # TODO: handle filters
        #self.my_filter = FilterExpr()
        #self.my_filter.whitelist_mac(self.mac)
        
        self.dispatch.register_response_handler(self._handle_response)
    
    def close(self):
        self.dispatch.delete_response_handler(self._handle_response)
    
    def send(self, cmd_type, addr, data_tags = None, cb = None):
        """Send the msg to the mote
        """
        oap_msg = OAPMessage.build_oap(
            self.seq_num,
            self.session_id,
            cmd_type,
            addr,
            tags=data_tags,
            sync=True
        )

        # TODO: adjust send_data to match connector
        # send_data expects msg as list of integers
        oap_payload = [ord(b) for b in oap_msg]
        
        #print ' '.join(['TX: ']+["%.2x"%c for c in oap_payload])
        
        self.send_data(
            self.mac,
            0,
            OAPMessage.OAP_PORT,
            OAPMessage.OAP_PORT,
            0,
            oap_payload
        )
        
        # append the callback for the response to the message queue
        if cb:
            self.message_queue.append((self.seq_num, cmd_type, cb))
    
    def _handle_response(self, mac, oap_resp, oap_trans):
        '''
        Compare the response to our message queue to check whether it belongs
        to us.
        '''
        # TODO: assume that we only get messages addressed to our mac
        # TODO: update transport values
        
        matchcb = [el for el in self.message_queue
                   if oap_trans['sequence'] == el[0] and oap_resp['command'] == el[1]]
        
        if matchcb:
            matchcb[0][2](mac, oap_resp)
            self.message_queue.remove(matchcb[0])
