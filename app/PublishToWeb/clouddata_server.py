#!/usr/bin/python

#============================ define ==========================================

DFLT_PORT      = 8080
INFLUX_HOST    = 'localhost'
INFLUX_PORT    = 8086
INFLUX_DBNAME  = 'grafana'

#============================ imports =========================================

from bottle import post,request,run
import influxdb

print 'CloudData Server'

influxClient   = influxdb.client.InfluxDBClient(
   host        = INFLUX_HOST,
   port        = INFLUX_PORT,
   database    = INFLUX_DBNAME,
)

@post('/oap')
def root_post():
    mac            = request.json['mac']
    temperature    = request.json['temperature']
    influxClient.write_points(
        [
            {
                "measurement": "temperature",
                "tags": {
                    "mac":    mac,
                },
                "fields": {
                    "value":  temperature,
                }
            },
        ]
    )
    print 'received mac={0} temperature={1}'.format(mac,temperature)

print 'Server started on port {0}'.format(DFLT_PORT)
run(host='0.0.0.0', port=DFLT_PORT, quiet=True)
