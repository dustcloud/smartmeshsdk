#!/usr/bin/python

#============================ imports =========================================

import time
import requests
import random
import json

#============================ defines =========================================

SERVER_HOST        = 'clouddata.dustcloud.org'
SERVER_PORT        = '80'

#============================ main ============================================

print 'PublishToWebRandom - (c) Dust Networks'

while True:
    time.sleep(1)
    
    try:
        mac         = random.choice([
            '33-33-33-33-33-33-33-33',
            '44-44-44-44-44-44-44-44',
        ])
        temperature = 20+10*random.random()
        
        r = requests.post(
            "http://{0}:{1}/api/v1/oap".format(SERVER_HOST,SERVER_PORT),
            data = json.dumps({
                'mac':          mac,
                'temperature':  temperature,
            }),
            headers = {
                'Content-type': 'application/json',
            }
        )
    except Exception as err:
        print err
    else:
        print 'sent mac={0} temperature={1:.2f}C'.format(mac,temperature)
