#!/usr/bin/python

import logging
class NullHandler(logging.Handler):
    def emit(self, record):
        pass
log = logging.getLogger('Oap')
log.setLevel(logging.ERROR)
log.addHandler(NullHandler())

from SmartMeshSDK.IpMgrConnectorSerial import IpMgrConnectorSerial
import   OAPDispatcher, \
         OAPClient,     \
         OAPMessage,    \
         OAPNotif

class Oap(object):
    
    clients = {}
    
    def __init__(self,connector,notifcb):
        self.connector = connector
        self.notifcb   = notifcb
        
        self.oap_dispatch = OAPDispatcher.OAPDispatcher()
        self.oap_dispatch.register_notif_handler(self._handle_oap_notif)
    
    #======================== public ==========================================
    
    def indicateNotifData(self,notifName,notifParams):
        assert notifName==IpMgrConnectorSerial.IpMgrConnectorSerial.NOTIFDATA
        
        print notifName
        print notifParams
        print "TODO indicateNotifData"
        
        mac = tuple(notifParams.macAddress)
        
        if mac not in self.clients:
            self.clients[mac] = OAPClient.OAPClient(
                mac,
                self.connector.dn_sendData,
                self.oap_dispatch
            )
    
    #======================== private =========================================
    
    def _handle_oap_notif(self,mac,notif):
        
        print mac
        print notif
        print "TODO _handle_oap_notif"
    
    #======================== helpers =========================================
