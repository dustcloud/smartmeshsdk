#!/usr/bin/python

import threading

from ApiException import ConnectionError

class NotifWaitThread(threading.Thread):
    
    def __init__(self,connector,notifCb):
        self.connector       = connector
        self.notifCb         = notifCb
        threading.Thread.__init__(self)
        self.name            = "NotifWaitThread"
    
    def run(self):
        while (1):
            try:
                notif = self.connector.getNotification()
            except ConnectionError as err:
                # when we disconnect, kill this thread
                return
            self.notifCb(notif)
            