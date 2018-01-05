This page details the entire JSON API of the `JsonServer` application.
For a fun tutorial on how to use it, click [here](https://dustcloud.atlassian.net/wiki/display/SMSDK/JsonServer).

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

# Command Line Interface

The application has a command line interface which allows you to configure and verify the status of the application.

```
JsonServer - (c) Dust Networks

> SmartMesh SDK 1.1.2.1
```

Type `help` to see the list of available commands:

```
> help
Available commands:
 - help (h): print this menu
 - info (i): information about this application
 - quit (q): quit this application
 - uptime (ut): how long this application has been running
 - status (s): get the current status of the application
 - seriaports (sp): list the available serialports
 - connectmanager (cm): connect to a manager's API serial port
 - disconnectmanager (dm): disconnect from a manager's API serial port
```

The `info` command prints general information about the application:

```
> info
General status of the application

current time: Thu Jun 08 14:46:13 2017

4 threads running:
- MainThread
- ManagerHandler@COM7
- WebServer
- DustCli

This is thread DustCli.
```

The `uptime` application allows you to see how long the application has been running:

```
> uptime
Running since 06/08/2017 14:45:23 (0:01:41.690000 ago)
```

The `status` command allows you to see status of the application. The example below shows that:
* the application runs on top of SmartMesh SDK version 1.1.2.1
* the time on the computer running the application (handy when running a `JsonServer` on a computer in a different timezone)
* the list of managers. Here, the manager which is supposed to be attached to serial port `COM7` is not there.
* how long the application has been running
* the list of threads running (for debugging only)

```
> status
{   'SmartMesh SDK version': '1.1.2.1',
    'current time': '06/08/2017 14:47:20',
    'managers': {   'COM7': 'disconnected'},
    'running since': '06/08/2017 14:45:23 (0:01:56.949000 ago)',
    'threads running': [   'MainThread',
                           'ManagerHandler@COM7',
                           'WebServer',
                           'DustCli']}
>
```

The `serialports` command allows you to list all available serial ports:

```
> serialports
{   'serialports': ['COM10', 'COM11', 'COM8', 'COM9']}
```

The `connectmanager` command allows you to connect to an additional SmartMesh IP manager.
Issuing `status` (as in the example below) allows you to verify the manager was indeed added.

**Note**: you can connect to as many managers as you want.

```
> connectmanager COM10
> status
{   'SmartMesh SDK version': '1.1.2.1',
    'current time': '06/08/2017 15:02:15',
    'managers': {   'COM10': 'disconnected', 'COM7': 'disconnected'},
    'running since': '06/08/2017 15:01:31 (0:00:43.839000 ago)',
    'threads running': [   'WebServer',
                           'DustCli',
                           'ManagerHandler@COM7',
                           'MainThread',
                           'ManagerHandler@COM10']}
```

The `disconnectmanager ` command allows you to disconnect from a manager.
Issuing `status` (as in the example below) allows you to verify the manager is indeed gone.

```
> disconnectmanager COM7
> status
{   'SmartMesh SDK version': '1.1.2.1',
    'current time': '06/08/2017 15:04:19',
    'managers': {   'COM10': 'connected'},
    'running since': '06/08/2017 15:01:31 (0:02:48.501000 ago)',
    'threads running': [   'WebServer',
                           'DustCli',
                           'MainThread',
                           'ManagerHandler@COM10',
                           'COM10_HDLC']}
```

# JSON API: commands

This section lists examples of requests/responses, i.e. JSON strings sent and received from the `JsonServer` application, over HTTP.

## Retrieve `index.html`

| Method | URL                                     |
|--------|-----------------------------------------|
| `GET`  |`http://{{host}}:{{port}}/`              |

#### Example body of the request

*empty*

#### Example body of the response

The exact contents of the `index.html` file.

## Retrieve a static file

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

## Exercise the raw SmartMesh IP Manager serial API

Through the `JsonServer`, you can call any SmartMesh IP serial API command.
Just specify in the body of your request the name of the command to call, and the value of any field, if any.
The HTTP response contains the response from the SmartMesh IP Manager.
The HTTP status code is `200` if the serial API command was issued successfully.

You can specify the MAC address of a mote as a string (e.g. `00-01-02-03-04-05-06-07`) or a list (e.g. `[0,1,2,3,4,5,6,7]`); the `JsonServer` app understands both.

### No parameters are present in the request

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

## Exercise the On-Chip Application Protocol (OAP)

**Note**: this is the protocol implemented by the SmartMesh IP motes running the default firmware in _master_ mode.

### Read the `info` resource

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

### Read the `main` resource

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

### Write the `main` resource

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

### Read the `digital_in/D0` resource

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

### Write the `digital_in/D0` resource

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

### Write the `digital_out/D4`

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

### Read the `analog/A0` resource

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

### Write the `analog/A0` resource

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

### Read the `pkgen/echo` resource

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

### Write the `pkgen` resource

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

## Helpers

The `JsonServer` comes with a number of handy helpers.

### List all available serial ports

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

### List all motes

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

### List all OAP motes

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

### Trigger a snapshot

When performing a "snapshot", the JsonServer application issues a number of API commands to retrieve:

* information about all the motes in the network
* information about all the paths in the network

Depending on the size of your SmartMesh network, this might take a number of seconds.
Issuing this command just triggers the beginning of a snapshot, and returns the appropriate status code.
When the snapshot if over, the JsonServer generates a snapshot notification, see below.

| Method  | URL                                               |
|---------|---------------------------------------------------|
| `POST`  |`http://{{host}}:{{port}}/api/v1/helpers/snapshot` |

Internally, when a snapshot is triggered, the JsonServer issues:
* a `getMoteConfig` API command on all motes
* a `getMoteInfo` API command on all motes
* a `getNextPathInfo` API command for all paths on all motes

This resource returns the following HTTP status codes

| HTTP status code | meaning                                       |
|------------------|-----------------------------------------------|
| `200`            | success, snapshot succesfully triggered       |
| `503`            | not available, other snapshot already ongoing |

**Note**: only one snapshot can be ongoing for all managers connected to the JsonServer

#### Example body of the request

You must specify the manager you want to start the snapshot on.

```
{
    "manager": "COM31"
}
```

Optionally, you can also add a `correlationID` field, which contains any string you want, and which will appear also in the snapshot notification.

```
{
    "manager": "COM31",
    "correlationID": "foobar"
}
```

#### Example body of the response

*empty*

### Get the latest snapshot

The JsonServer keeps a copy of the latest snapshot for each of the manager's connected to it.
You can use this resource to retrieve all latest snapshots

| Method  | URL                                               |
|---------|---------------------------------------------------|
| `GET`   |`http://{{host}}:{{port}}/api/v1/helpers/snapshot` |

#### Example body of the request

*empty*

#### Example body of the response

The response contains the latest snapshot for each manager.
In the example below, "0" identifies the manager.
The format of the snapshot is exactly the same as in a snapshot notification, with the extra `age_seconds` field indicating how long ago the snapshot was taken.

```
{
    "0": {
        "age_seconds": 4,
        <exact same contents as a snapshot notification>
    }
}
```

## Configuration of the `JsonServer` application

### Read the current configuration

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

### Change the configuration

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

### Adding a manager

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

### Deleting a manager

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

The SmartMesh IP manager issues notifications over its serial port.
The `JsonServer` application translates those serial notifications into JSON strings and performs an HTTP POST with each notification as the JSON body to a configured URL.

The name of the fields and general formatting of the serial and JSON notifications are strictly the same.

The user specifies the list of URLs to post the notifications to, one per type of notification.
Reading/writing the notification URLs is done by accessing the `notification_urls` configuration.
You can disable notifications for a particular category by setting its corresponding notification URL to `""` (empty string).

All notifications contain a `name` element which indicates what type of notification it is.
This means that you can configure all `notification_urls` to POST to the same URL and still distinguish the different types of notifications.

The MAC address in all notifications are encoded as a string, e.g. `00-01-02-03-04-05-06-07`.

The following subsections show examples for each category of notification.

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

## `snapshot` notifications

This notification is generated when a snaphot is done.
See above for how to trigger a snapshot.

A snapshot notification contains metadata and the (unmodified) response of a number of API commands.
A snapshot contains general information about the networks, as well as information about all motes, links and paths.

```
{
    'manager': 0,
    'correlationID': 'foobar'.
    'snapshot': {
        // metadata
        
        u'valid': True
        u'timestamp_start': u'Wed, 28 Jun 2017 10:07:00 UTC',
        u'timestamp_stop': u'Wed, 28 Jun 2017 10:07:00 UTC'},
        'epoch_stop': 1498644420.962,
        
        // general
        
        u'getSystemInfo': {
            u'RC': 0,
            u'hwModel': 16,
            u'hwRev': 1,
            u'macAddress': u'00-17-0d-00-00-30-5d-39',
            u'swBuild': 9,
            u'swMajor': 1,
            u'swMinor': 4,
            u'swPatch': 1
        },
        'getNetworkInfo': {
            u'RC': 0,
            u'advertisementState': 0,
            u'asnSize': 7250,
            u'downFrameState': 1,
            u'ipv6Address': u'fe80:0000:0000:0000:0017:0d00:0030:5d39',
            u'maxNumbHops': 3,
            u'netLatency': 700,
            u'netPathStability': 99,
            u'netReliability': 100,
            u'netState': 0,
            u'numArrivedPackets': 995,
            u'numLostPackets': 0,
            u'numMotes': 3
        },
        'getNetworkConfig': {
            u'RC': 0,
            u'apTxPower': 8,
            u'autoStartNetwork': True,
            u'baseBandwidth': 9000,
            u'bbMode': 0,
            u'bbSize': 1,
            u'bwMult': 300,
            u'ccaMode': 0,
            u'channelList': 32767,
            u'downFrameMultVal': 1,
            u'frameProfile': 1,
            u'isRadioTest': 0,
            u'locMode': 0,
            u'maxMotes': 101,
            u'networkId': 430,
            u'numParents': 2,
            u'oneChannel': 255
        },
        
        // motes
        
        'getMoteInfo': {
            '00-17-0d-00-00-30-5d-39': {
                u'RC': 0,
                u'assignedBw': 0,
                u'avgLatency': 0,
                u'hopDepth': 0,
                u'macAddress': u'00-17-0d-00-00-30-5d-39',
                u'numGoodNbrs': 3,
                u'numJoins': 1,
                u'numNbrs': 3,
                u'packetsLost': 0,
                u'packetsReceived': 12,
                u'requestedBw': 61770,
                u'state': 4,
                u'stateTime': 11226,
                u'totalNeededBw': 2472
            },
            ...
        },
        'getMoteConfig': {
            '00-17-0d-00-00-30-5d-39': {
                'RC': 0,
                u'isAP': True,
                u'isRouting': True,
                u'macAddress': u'00-17-0d-00-00-30-5d-39',
                u'moteId': 1,
                u'reserved': 1,
                u'state': 4,
            },
            ...
        },
        
        // links
        
        'getMoteLinks': {
            '00-17-0d-00-00-30-5d-39': {
                'RC': 0,
                u'utilization': 1
                u'links': [
                    {
                        'channelOffset': 1,
                        u'flags': 2,
                        u'frameId': 1,
                        u'moteId': 2,
                        u'slot': 241
                    },
                    ...
                ],
            },
            ...
        },
        
        // paths
        
        u'getPathInfo': {
            u'00-17-0d-00-00-30-5d-39': {
                u'0': {
                    u'RC': 0,
                    u'dest': u'00-17-0d-00-00-38-06-f0',
                    u'direction': 3,
                    u'numLinks': 2,
                    u'pathId': 2,
                    u'quality': 97,
                    u'rssiDestSrc': -46,
                    u'rssiSrcDest': 0,
                    u'source': u'00-17-0d-00-00-30-5d-39'
                },
                ...
            },
            ...
        }
    }
}
```
