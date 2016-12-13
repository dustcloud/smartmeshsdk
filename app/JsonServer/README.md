This page details the entire JSON API of the `JsonServer` application.
For a fun tutorial on how to use it, see https://dustcloud.atlassian.net/wiki/display/SMSDK/JsonServer.

# Introduction

* all requests/responses are JSON strings (i.e. the `Content-Type` HTTP heades MUST be set to `application/json`)
* the base URL for ALL requests is `/api/v1/`
* you can exercise all of these requests using the [Postman](https://www.getpostman.com/) collection/environment in the source-code directory of the `JsonServer` application.

The following aliases are used throughout this documentation:

| alias            | meaning                                                              |
|------------------|----------------------------------------------------------------------|
| `{{host}}`       | IP address or hostname of the machine running `JsonServer`           |
| `{{port}}`       | TCP port `JsonServer` listens to (default: 8080)                     |
| `{{serialport}}` | serial port a SmartMesh IP manager is connected to (e.g. `COM27`)    |
| `{{mote}}`       | MAC address of the mote of interest (e.g. `00-17-0d-00-00-38-06-45`) |

# JSON API: commands

This section lists examples of requests/responses, i.e. JSON formats sent and received from the `JsonServer` application.

## retrieve `index.html`

| Method | URL                                     |
|--------|-----------------------------------------|
| `GET`  |`http://{{host}}:{{port}}/`              |

#### Example body of the request

*empty*

#### Example body of the response

The exact contents of the `index.html` file.

## retrieve a static file

| Method | URL                                           |
|--------|-----------------------------------------------|
| `GET`  |`http://{{host}}:{{port}}/static/{{filename}}` |

#### Example body of the request

*empty*

#### Example body of the response

The exact contents of the `static/{{filename}}` file.

**Note**: Any file in the `static/` directory can be retrieved this way; be mindful of the content of that directory!

## retrieve the status of the `JsonServer` application

| Method | URL                                     |
|--------|-----------------------------------------|
| `GET`  |`http://{{host}}:{{port}}/api/v1/status` |

#### Example body of the request

*empty*

#### Example body of the response

```
{
  "threads running": [
    "Thread-1",
    "COM27_HDLC",
    "IpMgrSubscribe",
    "MainThread",
    "ManagerHandler@COM27"
  ],
  "running since": "11/12/2016 16:11:31 (0:07:04.617000 ago)",
  "managers": {
    "COM27": "connected"
  },
  "SmartMesh SDK version": "1.1.0.2",
  "current time": "11/12/2016 16:18:35"
}
```

## exercise the raw SmartMesh IP Manager serial API

Through the `JsonServer`, you can call any SmartMesh IP serial API command.
Just specify in the body of your request the name of the command to call, and the value of any field, if any.
The HTTP response contains the response from the SmartMesh IP Manager.
The HTTP status code is `200` if the serial API command was issued successfully.

You can specify the MAC address of a mote as a string (e.g. `00-01-02-03-04-05-06-07`) or a list (e.g. `[0,1,2,3,4,5,6,7]`); the `JsonServer` app understands both.

### no parameters are present in the request

| Method | URL                                                  |
|--------|------------------------------------------------------|
| `POST`  |`http://{{host}}:{{port}}/api/v1/raw`                |

#### Example body of the request

```
{
    "manager": "COM31",
    "command": "getNetworkConfig"
}
```

#### Example body of the response

```
{
  "networkId": 425,
  "apTxPower": 8,
  "ccaMode": 0,
  "locMode": 0,
  "numParents": 2,
  "channelList": 32767,
  "baseBandwidth": 9000,
  "maxMotes": 33,
  "bbSize": 2,
  "bbMode": 2,
  "oneChannel": 255,
  "isRadioTest": 0,
  "downFrameMultVal": 1,
  "RC": 0,
  "bwMult": 300,
  "frameProfile": 1,
  "autoStartNetwork": true
}
```

### MAC address passed as a string

| Method | URL                                                  |
|--------|------------------------------------------------------|
| `POST`  |`http://{{host}}:{{port}}/api/v1/raw`                |

#### Example body of the request

```
{
    "manager": "COM31",
    "command": "getMoteConfig",
    "fields": {
    	"macAddress": "{{mote}}",
    	"next": false
    }
}
```

#### Example body of the response

**Note**: in this case, the response contains a MAC address also formatted as a string.

```
{
  "macAddress": "00-17-0d-00-00-38-06-45",
  "reserved": 0,
  "state": 4,
  "isRouting": true,
  "RC": 0,
  "moteId": 4,
  "isAP": false
}
```

### MAC address passed as a list

| Method | URL                                                  |
|--------|------------------------------------------------------|
| `POST`  |`http://{{host}}:{{port}}/api/v1/raw`                |

#### Example body of the request

```
{
    "manager": "COM31",
    "command": "getMoteConfig",
    "fields": {
    	"macAddress": [0,0,0,0,0,0,0,0],
    	"next": true
    }
}
```

#### Example body of the response

**Note**: in this case, the response contains a MAC address also formatted as a list.

```
{
  "macAddress": [
    0,
    23,
    13,
    0,
    0,
    56,
    6,
    103
  ],
  "reserved": 1,
  "state": 4,
  "isRouting": true,
  "RC": 0,
  "moteId": 1,
  "isAP": true
}
```

## exercise the On-Chip Application Protocol (OAP)

**Note**: this is the protocol implemented by the SmartMesh IP motes running the default firmware in master mode.

### read `info` resource

| Method | URL                                                |
|--------|----------------------------------------------------|
| `GET`  |`http://{{host}}:{{port}}/api/v1/oap/{{mote}}/info` |

#### Example body of the request

*empty*

#### Example body of the response

```
{
  "status": "OK",
  "fields": {
    "appId": 1,
    "resetCounter": 0,
    "swRevMaj": 1,
    "changeCounter": 0,
    "swRevPatch": 0,
    "swRevBuild": 24,
    "swRevMin": 3
  },
  "resource": "info",
  "method": "GET"
}
```

### read `main` resource

| Method | URL                                                |
|--------|----------------------------------------------------|
| `GET`  |`http://{{host}}:{{port}}/api/v1/oap/{{mote}}/main` |

#### Example body of the request

*empty*

#### Example body of the response

```
{
  "status": "OK",
  "fields": {
    "destAddr": "ff020000000000000000000000000002",
    "destPort": 61625
  },
  "resource": "main",
  "method": "GET"
}
```

### write `main` resource

| Method | URL                                                |
|--------|----------------------------------------------------|
| `PUT`  |`http://{{host}}:{{port}}/api/v1/oap/{{mote}}/main` |

#### Example body of the request

```
{
    "destAddr": "ff020000000000000000000000000002",
    "destPort": 61625
}
```

#### Example body of the response

```
{
  "status": "OK",
  "fields": {},
  "resource": "main",
  "method": "PUT"
}
```

### read the `digital_in/D0` resource

**Note**: the exact same applies for the `digital_in/D1`, `digital_in/D2` and `digital_in/D3` resources.

| Method | URL                                                         |
|--------|-------------------------------------------------------------|
| `GET`  |`http://{{host}}:{{port}}/api/v1/oap/{{mote}}/digital_in/D0` |

#### Example body of the request

*empty*

#### Example body of the response

```
{
  "status": "OK",
  "fields": {
    "sampleCount": 1,
    "rate": 10000,
    "enable": 0,
    "dataFormat": 0,
    "value": []
  },
  "resource": "digital_in/D0",
  "method": "GET"
}
```

### write the `digital_in/D0` resource

**Note**: the exact same applies for the `digital_in/D1`, `digital_in/D2` and `digital_in/D3` resources.

| Method | URL                                                         |
|--------|-------------------------------------------------------------|
| `PUT`  |`http://{{host}}:{{port}}/api/v1/oap/{{mote}}/digital_in/D0` |

#### Example body of the request

```
{
    "enable":      0,
    "rate":        10000,
    "sampleCount": 1,
    "dataFormat":  0
}
```

#### Example body of the response

```
{
  "status": "OK",
  "fields": {},
  "resource": "digital_in/D0",
  "method": "PUT"
}
```

### write the `digital_out/D4`

**Note**: the exact same applies for the `digital_out/D5` and `digital_out/INDICATOR_0` resources.

| Method | URL                                                          |
|--------|--------------------------------------------------------------|
| `PUT`  |`http://{{host}}:{{port}}/api/v1/oap/{{mote}}/digital_out/D4` |

#### Example body of the request

```
{
    "value":    0
}
```

#### Example body of the response

```
{
  "status": "OK",
  "fields": {},
  "resource": "digital_out/D4",
  "method": "PUT"
}
```

### read the `analog/A0` resource

**Note**: the exact same applies for the `analog/A1`, `analog/A2`, `analog/A3` and `temperature` resources.

| Method | URL                                                     |
|--------|---------------------------------------------------------|
| `GET`  |`http://{{host}}:{{port}}/api/v1/oap/{{mote}}/analog/A0` |

#### Example body of the request

*empty*

#### Example body of the response

```
{
  "status": "OK",
  "fields": {
    "sampleCount": 1,
    "rate": 10000,
    "enable": 0,
    "dataFormat": 0,
    "value": []
  },
  "resource": "analog/A0",
  "method": "GET"
}
```

### write the `analog/A0` resource

**Note**: the exact same applies for the `analog/A1`, `analog/A2`, `analog/A3` and `temperature` resources.

| Method | URL                                                     |
|--------|---------------------------------------------------------|
| `PUT`  |`http://{{host}}:{{port}}/api/v1/oap/{{mote}}/analog/A0` |

#### Example body of the request

```
{
    "enable":      0,
    "rate":        10000,
    "sampleCount": 1,
    "dataFormat":  0
}
```

#### Example body of the response

```
{
  "status": "OK",
  "fields": {},
  "resource": "analog/A0",
  "method": "PUT"
}
```

### read the `pkgen/echo` resource

| Method | URL                                                      |
|--------|----------------------------------------------------------|
| `GET`  |`http://{{host}}:{{port}}/api/v1/oap/{{mote}}/pkgen/echo` |

#### Example body of the request

*empty*

#### Example body of the response

```
{
  "status": "OK",
  "fields": {
    "echo": 2
  },
  "resource": "pkgen/echo",
  "method": "GET"
}
```

### write the `pkgen` resource

| Method | URL                                                 |
|--------|-----------------------------------------------------|
| `PUT`  |`http://{{host}}:{{port}}/api/v1/oap/{{mote}}/pkgen` |

#### Example body of the request

```
{
    "echo":       12,
    "numPackets": 2,
    "rate":       5000,
    "packetSize": 10,
    "startPID":   0
}
```

#### Example body of the response

```
{
  "status": "OK",
  "fields": {},
  "resource": "pkgen",
  "method": "PUT"
}
```

## helpers

The `JsonServer` comes with a number of handy helpers.

### list all available serial port

| Method | URL                                                  |
|--------|------------------------------------------------------|
| `GET`  |`http://{{host}}:{{port}}/api/v1/helpers/serialports` |

#### Example body of the request

*empty*

#### Example body of the response

```
{
  "serialports": [
    "COM24",
    "COM25",
    "COM26",
    "COM27"
  ]
}
```

### list all motes

| Method | URL                                            |
|--------|------------------------------------------------|
| `GET`  |`http://{{host}}:{{port}}/api/v1/helpers/motes` |

#### Example body of the request

*empty*

#### Example body of the response

```
{
  "COM27": [
    "00-17-0d-00-00-38-06-d5",
    "00-17-0d-00-00-38-06-ad",
    "00-17-0d-00-00-38-06-45"
  ]
}
```

**Notes**:

* only motes which are operational are listed
* the manager is *not* listed
* motes are grouped by manager, here `COM27` is the serial port the manager is connected to

### list all OAP motes

**Note**: an "OAP mote" is a mote from which we have already received an OAP notification, or to which we have already sent an OAP request.

| Method | URL                                               |
|--------|---------------------------------------------------|
| `GET`  |`http://{{host}}:{{port}}/api/v1/helpers/oapmotes` |

#### Example body of the request

*empty*

#### Example body of the response

```
{
  "oapmotes": [
    "00-17-0d-00-00-38-06-ad",
    "00-17-0d-00-00-38-06-d5",
    "00-17-0d-00-00-38-06-45"
  ]
}
```

**Note**: motes are grouped by manager, here `COM27` is the serial port the manager is connected to

## configuration of the `JsonServer` application

### read the current configuration

| Method | URL                                     |
|--------|-----------------------------------------|
| `GET`  |`http://{{host}}:{{port}}/api/v1/config` |

#### Example body of the request

*empty*

#### Example body of the response

```
{
  "notification_urls": {
    "hr": "http://127.0.0.1:1880/hr",
    "notifData": "http://127.0.0.1:1880/notifData",
    "oap": "http://127.0.0.1:1880/oap",
    "notifLog": "http://127.0.0.1:1880/notifLog",
    "notifIpData": "http://127.0.0.1:1880/notifIpData",
    "event": "http://127.0.0.1:1880/event",
    "notifHealthReport": "http://127.0.0.1:1880/notifHealthReport"
  },
  "managers": []
}
```

### change the configuration

| Method  |  URL                                     |
|---------|------------------------------------------|
| `POST`  | `http://{{host}}:{{port}}/api/v1/config` |

#### Example body of the request

**Note**: The configuration changes sent in the request are merged, i.e. new fields are added (the `someconfig` and `otherconfig` fields in the example below), others are updated (the `notification_urls/hr` field).

```
{
  "notification_urls": {
    "hr": "http://127.0.0.1:1880/hr2"
  },
  "someconfig": 1,
  "otherconfig": 2
}
```

#### Example body of the response

```
{
  "someconfig": 1,
  "notification_urls": {
    "hr": "http://127.0.0.1:1880/hr2",
    "notifData": "http://127.0.0.1:1880/notifData",
    "oap": "http://127.0.0.1:1880/oap",
    "notifLog": "http://127.0.0.1:1880/notifLog",
    "notifIpData": "http://127.0.0.1:1880/notifIpData",
    "event": "http://127.0.0.1:1880/event",
    "notifHealthReport": "http://127.0.0.1:1880/notifHealthReport"
  },
  "managers": [],
  "otherconfig": 2
}
```

### adding a manager

**Note**: There is no limit to the number of SmartMesh IP managers you can connect to the `JsonServer` application, you just need to call this function to tell it to connect to a new one.

| Method | URL                                              |
|--------|--------------------------------------------------|
| `PUT`  |`http://{{host}}:{{port}}/api/v1/config/managers` |

#### Example body of the request

```
{
    "managers": ["{{serialport}}"]
}
```

#### Example body of the response

*empty*

### deleting a manager

| Method   | URL                                               |
|----------|---------------------------------------------------|
| `DELETE` | `http://{{host}}:{{port}}/api/v1/config/managers` |

#### Example body of the request

```
{
    "managers": ["{{serialport}}"]
}
```

#### Example body of the response

*empty*

# JSON API: notifications

The SmartMesh IP manager issues commands over its serial port.
The `JsonServer` application translates those serial notifications into JSON strings which it HTTP POST's to some URL.

The name of the fields and general formatting of the serial and JSON notifications are strictly the same.

The user specifies the list of URLs to post the notifications to, one per type of notification.
Reading/writing the notification URLs is done by accessing the `notification_urls` configuration.
You can disable notifications for a particular category by setting its corresponding notification URL to `''` (empty string).

All notifications contain a `name` element which indicates what type of notification it is.
This means that you can configure all `notification_urls` to the same URL and still easily distinguish the different types of notifications.

The MAC address in all notifications are encoded as a string, e.g. `00-01-02-03-04-05-06-07`.

The following subsections give one of more examples for each category of notification.

## `notifData` notifications

```
{   u'fields': {   u'data': [   0,
                                0,
                                5,
                                0,
                                255,
                                1,
                                5,
                                0,
                                0,
                                0,
                                0,
                                61,
                                35,
                                131,
                                96,
                                0,
                                9,
                                168,
                                43,
                                0,
                                0,
                                19,
                                136,
                                1,
                                16,
                                11,
                                5],
                   u'dstPort': 61625,
                   u'macAddress': u'00-17-0d-00-00-38-06-ad',
                   u'srcPort': 61625,
                   u'utcSecs': 1025737568,
                   u'utcUsecs': 630000},
    u'manager': u'COM27',
    u'name': u'notifData'}
```

## `oap` notifications

**Note**: The `oap` notification does *not* correspond to a SmartMesh IP serial notification.
Rather, when the manager issues a `notifData` notification, the `JsonServer` always tries to parse it as if it were an OAP notification.
If it is a valid OAP notification, it issues an `oap` JSON notification with the parsed contents.
This means that, if notifications on the `JsonServer` are enabled for both `notifData` and `oap`, both notifications are issued.

```
{   u'fields': {   u'channel': [5],
                   u'channel_str': u'temperature',
                   u'num_samples': 1,
                   u'packet_timestamp': [262588817408L, 162016000],
                   u'rate': 5000,
                   u'received_timestamp': u'2016-11-13 10:18:35.166000',
                   u'sample_size': 16,
                   u'samples': [2821]},
    u'mac': u'00-17-0d-00-00-38-06-ad',
    u'name': u'oap'}
```

## `event` notifications

```
{   u'fields': {   u'callbackId': 25, u'eventId': 80, u'rc': 0},
    u'manager': u'COM27',
    u'name': u'eventPacketSent'}
```

## `notifHealthReport` notifications


```
{   u'fields': {   u'macAddress': u'00-17-0d-00-00-38-06-45',
                   u'payload': [   128,
                                   24,
                                   0,
                                   0,
                                   5,
                                   31,
                                   49,
                                   22,
                                   11,
                                   210,
                                   0,
                                   43,
                                   0,
                                   0,
                                   0,
                                   11,
                                   0,
                                   0,
                                   0,
                                   0,
                                   0,
                                   0,
                                   0,
                                   0,
                                   0,
                                   0]},
    u'manager': u'COM27',
    u'name': u'notifHealthReport'}
```

## `hr` notifications

**Note**: The `hr` notification does *not* correspond to a SmartMesh IP serial notification.
Rather, when the manager issues a `notifHealthReport` notification, the `JsonServer` application parses it and issues an `hr` JSON notification with the parsed contents.
This means that, if notifications on the `JsonServer` are enabled for both `notifHealthReport` and `hr`, both notifications are issued.

```
{   u'hr': {   u'Neighbors': {   u'neighbors': [   {   u'neighborFlag': 0,
                                                       u'neighborId': 4,
                                                       u'numRxPackets': 2,
                                                       u'numTxFailures': 2,
                                                       u'numTxPackets': 59,
                                                       u'rssi': -29},
                                                   {   u'neighborFlag': 0,
                                                       u'neighborId': 1,
                                                       u'numRxPackets': 2,
                                                       u'numTxFailures': 3,
                                                       u'numTxPackets': 92,
                                                       u'rssi': -17},
                                                   {   u'neighborFlag': 0,
                                                       u'neighborId': 3,
                                                       u'numRxPackets': 59,
                                                       u'numTxFailures': 0,
                                                       u'numTxPackets': 0,
                                                       u'rssi': -36}],
                                 u'numItems': 3}},
    u'name': u'hr'}
```

```
{   u'hr': {   u'Device': {   u'badLinkFrameId': 0,
                              u'badLinkOffset': 0,
                              u'badLinkSlot': 0,
                              u'batteryVoltage': 3026,
                              u'charge': 3393,
                              u'numMacDropped': 0,
                              u'numRxLost': 0,
                              u'numRxOk': 0,
                              u'numTxBad': 0,
                              u'numTxFail': 0,
                              u'numTxOk': 32,
                              u'queueOcc': 33,
                              u'temperature': 25},
               u'Discovered': {   u'discoveredNeighbors': [   {   u'neighborId': 3,
                                                                  u'numRx': 2,
                                                                  u'rssi': -9}],
                                  u'numItems': 1,
                                  u'numJoinParents': 1}},
    u'name': u'hr'}
```

## `notifLog` notifications

*See formatting of the `notifLog` notification of the SmartMesh IP serial API notification.*

## `notifIpData` notifications


```
{   u'fields': {   u'data': [   126,
                                112,
                                255,
                                2,
                                0,
                                0,
                                0,
                                0,
                                0,
                                0,
                                0,
                                0,
                                0,
                                0,
                                0,
                                0,
                                0,
                                3,
                                247,
                                153,
                                0,
                                0,
                                5,
                                0,
                                255,
                                1,
                                5,
                                0,
                                0,
                                0,
                                0,
                                61,
                                34,
                                122,
                                94,
                                0,
                                14,
                                69,
                                93,
                                0,
                                0,
                                117,
                                48,
                                1,
                                16,
                                8,
                                152],
                   u'macAddress': u'00-17-0d-00-00-38-06-45',
                   u'utcSecs': 1025669726,
                   u'utcUsecs': 929000},
    u'manager': u'COM27',
    u'name': u'notifIpData'}
```