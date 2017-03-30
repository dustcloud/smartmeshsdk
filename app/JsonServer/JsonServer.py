#!/usr/bin/python

#============================ adjust path =====================================

import sys
import os
if __name__ == "__main__":
    here = sys.path[0]
    sys.path.insert(0, os.path.join(here, '..', '..','libs'))
    sys.path.insert(0, os.path.join(here, '..', '..','external_libs'))

#============================ define ==========================================

#============================ imports =========================================

if os.name=='nt':       # Windows
   import _winreg as winreg
elif os.name=='posix':  # Linux
   import glob

import argparse
import collections
import time
import datetime
import threading
import copy
import pickle
import traceback
import binascii
import pprint

import requests
import json
import bottle
from bottle import hook

from SmartMeshSDK                      import sdk_version
from SmartMeshSDK.utils                import FormatUtils as u
from SmartMeshSDK.IpMgrConnectorSerial import IpMgrConnectorSerial
from SmartMeshSDK.IpMgrConnectorMux    import IpMgrSubscribe
from SmartMeshSDK.ApiException         import APIError,      \
                                              ConnectionError
from SmartMeshSDK.protocols.Hr         import HrParser
from SmartMeshSDK.protocols.oap        import OAPDispatcher, \
                                              OAPClient,     \
                                              OAPMessage,    \
                                              OAPNotif,      \
                                              OAPDefines as oapdefs

from dustCli      import DustCli

#============================ helpers =========================================

def currentUtcTime():
    return time.strftime("%a, %d %b %Y %H:%M:%S UTC", time.gmtime())

def logCrash(threadName,err):
    output  = []
    output += ["============================================================="]
    output += [currentUtcTime()]
    output += [""]
    output += ["CRASH in Thread {0}!".format(threadName)]
    output += [""]
    output += ["=== exception type ==="]
    output += [str(type(err))]
    output += [""]
    output += ["=== traceback ==="]
    output += [traceback.format_exc()]
    output  = '\n'.join(output)
    
    print output

def reversedict(d):
    return dict((v,k) for (k,v) in d.iteritems())

pp = pprint.PrettyPrinter(indent=4)

#============================ classes =========================================

class ManagerHandler(threading.Thread):

    def __init__(self,serialport,notifHandler):

        # store params
        self.serialport      = serialport
        self.notifHandler    = notifHandler
        
        # local variables
        self.reconnectEvent  = threading.Event()
        self.dataLock        = threading.RLock()
        self.connector       = None
        self.goOn            = True

        # start the thread
        threading.Thread.__init__(self)
        self.name            = 'ManagerHandler@{0}'.format(self.serialport)
        self.start()
    
    def run(self):
        try:
            while self.goOn:
                try:
                    
                    # connect to the manager
                    self.connector = IpMgrConnectorSerial.IpMgrConnectorSerial()
                    self.connector.connect({
                        'port': self.serialport,
                    })

                    # subscribe to notifications
                    self.subscriber = IpMgrSubscribe.IpMgrSubscribe(self.connector)
                    self.subscriber.start()
                    self.subscriber.subscribe(
                        notifTypes =    [
                                            IpMgrSubscribe.IpMgrSubscribe.NOTIFDATA,
                                        ],
                        fun =           self._notifAll,
                        isRlbl =        False,
                    )
                    self.subscriber.subscribe(
                        notifTypes =    [
                                            IpMgrSubscribe.IpMgrSubscribe.NOTIFEVENT,
                                            IpMgrSubscribe.IpMgrSubscribe.NOTIFHEALTHREPORT,
                                            IpMgrSubscribe.IpMgrSubscribe.NOTIFIPDATA,
                                            IpMgrSubscribe.IpMgrSubscribe.NOTIFLOG,
                                        ],
                        fun =           self._notifAll,
                        isRlbl =        True,
                    )
                    self.subscriber.subscribe(
                        notifTypes =    [
                                            IpMgrSubscribe.IpMgrSubscribe.ERROR,
                                            IpMgrSubscribe.IpMgrSubscribe.FINISH,
                                        ],
                        fun =           self._notifErrorFinish,
                        isRlbl =        True,
                    )

                except Exception as err:
                    
                    try:
                        self.connector.disconnect()
                    except Exception:
                        pass

                    # wait to reconnect
                    time.sleep(1)

                else:
                    self.reconnectEvent.clear()
                    self.reconnectEvent.wait()
                    
                    try:
                        self.connector.disconnect()
                    except Exception:
                        pass

        except Exception as err:
            logCrash(self.name,err)
    
    #======================== public ==========================================
    
    def close(self):

        try:
            self.connector.disconnect()
        except Exception:
            pass

        self.goOn = False
    
    def isConnected(self):
        try:
            return self.connector.isConnected
        except AttributeError:
            return False
    
    #======================== private =========================================

    #=== Dust API notifications
    
    def _notifAll(self, notif_name, dust_notif):
        
        try:
            self.notifHandler(
                self.serialport,
                notif_name,
                dust_notif,
            )
        except Exception as err:
            logCrash(self.name,err)

    def _notifErrorFinish(self,notifName,dust_notif):

        try:
            assert notifName in [
                IpMgrSubscribe.IpMgrSubscribe.ERROR,
                IpMgrSubscribe.IpMgrSubscribe.FINISH,
            ]

            if not self.reconnectEvent.isSet():
                self.reconnectEvent.set()
        except Exception as err:
            logCrash(self.name,err)

class JsonServer(object):
    
    OAP_TIMEOUT = 30.000
    
    def __init__(self, tcpport, serialport, notifprefix, configfilename):
        
        # store params
        self.tcpport              = tcpport
        self.serialport           = serialport
        self.notifprefix          = notifprefix
        self.configfilename       = configfilename
        
        # local variables
        self.startTime            = time.time()
        self.dataLock             = threading.RLock()
        self._loadConfig()   # populates self.config dictionnary
        self.managerHandlers      = {}
        self.oapDispatch          = OAPDispatcher.OAPDispatcher()
        self.oapDispatch.register_notif_handler(self._manager_oap_notif_handler)
        self.oapClients           = {}
        self.outstandingEvents    = {}
        self.responses            = {}
        self.hrParser             = HrParser.HrParser()
        
        #=== CLI interface
        
        self.cli                  = DustCli.DustCli("JsonServer",self._clihandle_quit)
        self.cli.registerCommand(
            name                  = 'status',
            alias                 = 's',
            description           = 'get the current status of the application',
            params                = [],
            callback              = self._clihandle_status,
        )
        self.cli.registerCommand(
            name                  = 'seriaports',
            alias                 = 'sp',
            description           = 'list the available serialports',
            params                = [],
            callback              = self._clihandle_serialports,
        )
        self.cli.registerCommand(
            name                  = 'connectmanager',
            alias                 = 'cm',
            description           = 'connect to a manager\'s API serial port',
            params                = ['serialport'],
            callback              = self._clihandle_connectmanager,
        )
        self.cli.registerCommand(
            name                  = 'disconnectmanager',
            alias                 = 'dm',
            description           = 'disconnect from a manager\'s API serial port',
            params                = ['serialport'],
            callback              = self._clihandle_disconnectmanager,
        )
    
        #=== web server
        self.websrv   = bottle.Bottle()
        #=== root
        self.websrv.route('/',                                            'GET',    self._webhandle_root_GET)
        #=== static
        self.websrv.route('/static/<filename>',                           'GET',    self._webhandle_static)
        #=== status
        self.websrv.route('/api/v1/status',                               'GET',    self._webhandle_status_GET)
        #=== raw
        self.websrv.route('/api/v1/raw',                                  'POST',   self._webhandle_raw_POST)
        #=== oap
        # /info
        self.websrv.route('/api/v1/oap/<mac>/info',                       'GET',    self._webhandle_oap_info_GET)
        self.websrv.route('/api/v1/oap/<mac>/0',                          'GET',    self._webhandle_oap_info_GET)
        # /main
        self.websrv.route('/api/v1/oap/<mac>/main',                       'GET',    self._webhandle_oap_main_GET)
        self.websrv.route('/api/v1/oap/<mac>/1',                          'GET',    self._webhandle_oap_main_GET)
        self.websrv.route('/api/v1/oap/<mac>/main',                       'PUT',    self._webhandle_oap_main_PUT)
        self.websrv.route('/api/v1/oap/<mac>/1',                          'PUT',    self._webhandle_oap_main_PUT)
        # /digital_in
        self.websrv.route('/api/v1/oap/<mac>/digital_in/D0',              'GET',    self._webhandle_oap_digital_in_D0_GET)
        self.websrv.route('/api/v1/oap/<mac>/2/0',                        'GET',    self._webhandle_oap_digital_in_D0_GET)
        self.websrv.route('/api/v1/oap/<mac>/digital_in/D0',              'PUT',    self._webhandle_oap_digital_in_D0_PUT)
        self.websrv.route('/api/v1/oap/<mac>/2/0',                        'PUT',    self._webhandle_oap_digital_in_D0_PUT)
        self.websrv.route('/api/v1/oap/<mac>/digital_in/D1',              'GET',    self._webhandle_oap_digital_in_D1_GET)
        self.websrv.route('/api/v1/oap/<mac>/2/1',                        'GET',    self._webhandle_oap_digital_in_D1_GET)
        self.websrv.route('/api/v1/oap/<mac>/digital_in/D1',              'PUT',    self._webhandle_oap_digital_in_D1_PUT)
        self.websrv.route('/api/v1/oap/<mac>/2/1',                        'PUT',    self._webhandle_oap_digital_in_D1_PUT)
        self.websrv.route('/api/v1/oap/<mac>/digital_in/D2',              'GET',    self._webhandle_oap_digital_in_D2_GET)
        self.websrv.route('/api/v1/oap/<mac>/2/2',                        'GET',    self._webhandle_oap_digital_in_D2_GET)
        self.websrv.route('/api/v1/oap/<mac>/digital_in/D2',              'PUT',    self._webhandle_oap_digital_in_D2_PUT)
        self.websrv.route('/api/v1/oap/<mac>/2/2',                        'PUT',    self._webhandle_oap_digital_in_D2_PUT)
        self.websrv.route('/api/v1/oap/<mac>/digital_in/D3',              'GET',    self._webhandle_oap_digital_in_D3_GET)
        self.websrv.route('/api/v1/oap/<mac>/2/3',                        'GET',    self._webhandle_oap_digital_in_D3_GET)
        self.websrv.route('/api/v1/oap/<mac>/digital_in/D3',              'PUT',    self._webhandle_oap_digital_in_D3_PUT)
        self.websrv.route('/api/v1/oap/<mac>/2/3',                        'PUT',    self._webhandle_oap_digital_in_D3_PUT)
        # /digital_out
        self.websrv.route('/api/v1/oap/<mac>/digital_out/D4',             'PUT',    self._webhandle_oap_digital_out_D4_PUT)
        self.websrv.route('/api/v1/oap/<mac>/3/0',                        'PUT',    self._webhandle_oap_digital_out_D4_PUT)
        self.websrv.route('/api/v1/oap/<mac>/digital_out/D5',             'PUT',    self._webhandle_oap_digital_out_D5_PUT)
        self.websrv.route('/api/v1/oap/<mac>/3/1',                        'PUT',    self._webhandle_oap_digital_out_D5_PUT)
        self.websrv.route('/api/v1/oap/<mac>/digital_out/INDICATOR_0',    'PUT',    self._webhandle_oap_digital_out_INDICATOR_0_PUT)
        self.websrv.route('/api/v1/oap/<mac>/3/2',                        'PUT',    self._webhandle_oap_digital_out_INDICATOR_0_PUT)
        # /analog
        self.websrv.route('/api/v1/oap/<mac>/analog/A0',                  'GET',    self._webhandle_oap_analog_A0_GET)
        self.websrv.route('/api/v1/oap/<mac>/4/0',                        'GET',    self._webhandle_oap_analog_A0_GET)
        self.websrv.route('/api/v1/oap/<mac>/analog/A0',                  'PUT',    self._webhandle_oap_analog_A0_PUT)
        self.websrv.route('/api/v1/oap/<mac>/4/0',                        'PUT',    self._webhandle_oap_analog_A0_PUT)
        self.websrv.route('/api/v1/oap/<mac>/analog/A1',                  'GET',    self._webhandle_oap_analog_A1_GET)
        self.websrv.route('/api/v1/oap/<mac>/4/1',                        'GET',    self._webhandle_oap_analog_A1_GET)
        self.websrv.route('/api/v1/oap/<mac>/analog/A1',                  'PUT',    self._webhandle_oap_analog_A1_PUT)
        self.websrv.route('/api/v1/oap/<mac>/4/1',                        'PUT',    self._webhandle_oap_analog_A1_PUT)
        self.websrv.route('/api/v1/oap/<mac>/analog/A2',                  'GET',    self._webhandle_oap_analog_A2_GET)
        self.websrv.route('/api/v1/oap/<mac>/4/2',                        'GET',    self._webhandle_oap_analog_A2_GET)
        self.websrv.route('/api/v1/oap/<mac>/analog/A2',                  'PUT',    self._webhandle_oap_analog_A2_PUT)
        self.websrv.route('/api/v1/oap/<mac>/4/2',                        'PUT',    self._webhandle_oap_analog_A2_PUT)
        self.websrv.route('/api/v1/oap/<mac>/analog/A3',                  'GET',    self._webhandle_oap_analog_A3_GET)
        self.websrv.route('/api/v1/oap/<mac>/4/3',                        'GET',    self._webhandle_oap_analog_A3_GET)
        self.websrv.route('/api/v1/oap/<mac>/analog/A3',                  'PUT',    self._webhandle_oap_analog_A3_PUT)
        self.websrv.route('/api/v1/oap/<mac>/4/3',                        'PUT',    self._webhandle_oap_analog_A3_PUT)
        # /temperature
        self.websrv.route('/api/v1/oap/<mac>/temperature',                'GET',    self._webhandle_oap_temperature_GET)
        self.websrv.route('/api/v1/oap/<mac>/5',                          'GET',    self._webhandle_oap_temperature_GET)
        self.websrv.route('/api/v1/oap/<mac>/temperature',                'PUT',    self._webhandle_oap_temperature_PUT)
        self.websrv.route('/api/v1/oap/<mac>/5',                          'PUT',    self._webhandle_oap_temperature_PUT)
        # /pkgen
        self.websrv.route('/api/v1/oap/<mac>/pkgen/echo',                 'GET',    self._webhandle_oap_pkgen_echo_GET)
        self.websrv.route('/api/v1/oap/<mac>/254/0',                      'GET',    self._webhandle_oap_pkgen_echo_GET)
        self.websrv.route('/api/v1/oap/<mac>/pkgen',                      'PUT',    self._webhandle_oap_pkgen_PUT)
        self.websrv.route('/api/v1/oap/<mac>/254',                        'PUT',    self._webhandle_oap_pkgen_PUT)
        #=== helpers
        self.websrv.route('/api/v1/helpers/serialports',                  'GET',    self._webhandle_helpers_serialports_GET)
        self.websrv.route('/api/v1/helpers/motes',                        'GET',    self._webhandle_helpers_motes_GET)
        self.websrv.route('/api/v1/helpers/oapmotes',                     'GET',    self._webhandle_helpers_oapmotes_GET)
        #=== config
        self.websrv.route('/api/v1/config',                               'GET',    self._webhandle_config_GET)
        self.websrv.route('/api/v1/config',                               'POST',   self._webhandle_config_POST)
        #=== managers
        self.websrv.route('/api/v1/config/managers',                      'PUT',    self._webhandle_managers_PUT)
        self.websrv.route('/api/v1/config/managers',                      'DELETE', self._webhandle_managers_DELETE)
        self.websrv.error(code=404)(self._errorhandle_404)
        self.websrv.error(code=500)(self._errorhandle_500)
        self.websrv.hook('after_request')(self._add_JsonServer_token_if_requested)
        webthread = threading.Thread(
            target = self.websrv.run,
            kwargs = {
                'host'          : '127.0.0.1',
                'port'          : self.tcpport,
                'quiet'         : True,
                'debug'         : False,
            }
        )
        webthread.name = 'WebServer'
        webthread.daemon = True
        webthread.start()
        
        # connect to managers (if any)
        self._syncManagers()
        
        # start CLI
        print 'SmartMesh SDK {0}'.format('.'.join([str(i) for i in sdk_version.VERSION]))
        self.cli.start()
    
    #======================== CLI handlers ====================================
    
    def _clihandle_quit(self):
        
        for (k,v) in self.managerHandlers.items():
            try:
                v.close()
            except:
                pass
        
        time.sleep(.3)
        print "bye bye."
    
    def _clihandle_status(self,params):
        pp.pprint(self._status_GET())
    
    def _clihandle_serialports(self,params):
        pp.pprint(self._serialports_GET())
    
    def _clihandle_connectmanager(self,params):
        self._managers_PUT([params[0],])
    
    def _clihandle_disconnectmanager(self,params):
        self._managers_DELETE([params[0],])
    
    #======================== web handlers ====================================
    
    def _add_JsonServer_token_if_requested(self):
        try:
            bottle.response.headers['X-Correlation-ID'] = bottle.request.headers['X-Correlation-ID']
        except KeyError:
            pass
    
    #=== root
    
    def _webhandle_root_GET(self):
        return bottle.static_file('index.html', root='.')
    
    #=== static
    
    def _webhandle_static(self,filename):
        return bottle.static_file(filename, root='static/')
    
    #=== status
    
    def _formatManagersStatus(self):
        returnVal = {}
        
        with self.dataLock:
            for (k,v) in self.managerHandlers.items():
                if v.isConnected():
                    returnVal[k] = 'connected'
                else:
                    returnVal[k] = 'disconnected'
        
        return returnVal
    
    def _webhandle_status_GET(self):
        return self._status_GET()
    
    #=== raw
    
    def _webhandle_raw_POST(self):
        
        commandArray = []
        commandArray        += [bottle.request.json['command']]
        try:
            commandArray    += [bottle.request.json['subcommand']]
        except KeyError:
            pass
        
        try:
            fields           = bottle.request.json['fields']
        except KeyError:
            fields           = {}
        manager              = bottle.request.json['manager']
        if type(manager)==int:
            manager = sorted(self.managerHandlers.keys())[manager]
        
        # mac addresses: '00-01-02-03-04-05-06-07' -> [0,1,2,3,4,5,6,7]
        wasDestringified = self._destringifyMacAddresses(fields)
        
        with self.dataLock:
            try:
                returnVal = self.managerHandlers[manager].connector.send(
                    commandArray = commandArray,
                    fields       = fields,
                )
            except APIError as err:
                returnVal = {
                    'RC': err.rc,
                }
        
        if wasDestringified:
            # mac addresses: [0,1,2,3,4,5,6,7] -> '00-01-02-03-04-05-06-07'
            self._stringifyMacAddresses(returnVal)
        
        return returnVal
    
    #=== oap
    
    # /info
    
    def _webhandle_oap_info_GET(self,mac):
        return self._oap_send_and_wait_for_reply(
            mac         = mac,
            method      = OAPMessage.CmdType.GET,
            resource    = 'info',
        )
    
    # /main
    
    def _webhandle_oap_main_GET(self,mac):
        return self._oap_send_and_wait_for_reply(
            mac         = mac,
            method      = OAPMessage.CmdType.GET,
            resource    = 'main',
        )
    
    def _webhandle_oap_main_PUT(self,mac):
        return self._oap_send_and_wait_for_reply(
            mac         = mac,
            method      = OAPMessage.CmdType.PUT,
            resource    = 'main',
        )
    
    # /digital_in
    
    def _digital_in_GET(self,mac,pin):
        return self._oap_send_and_wait_for_reply(
            mac         = mac,
            method      = OAPMessage.CmdType.GET,
            resource    = 'digital_in',
            subresource = pin,
        )
    
    def _digital_in_PUT(self,mac,pin):
        return self._oap_send_and_wait_for_reply(
            mac         = mac,
            method      = OAPMessage.CmdType.PUT,
            resource    = 'digital_in',
            subresource = pin,
        )
    
    def _webhandle_oap_digital_in_D0_GET(self,mac):
        return self._digital_in_GET(mac,0)
    
    def _webhandle_oap_digital_in_D0_PUT(self,mac):
        return self._digital_in_PUT(mac,0)
    
    def _webhandle_oap_digital_in_D1_GET(self,mac):
        return self._digital_in_GET(mac,1)
    
    def _webhandle_oap_digital_in_D1_PUT(self,mac):
        return self._digital_in_PUT(mac,1)
    
    def _webhandle_oap_digital_in_D2_GET(self,mac):
        return self._digital_in_GET(mac,2)
    
    def _webhandle_oap_digital_in_D2_PUT(self,mac):
        return self._digital_in_PUT(mac,2)
    
    def _webhandle_oap_digital_in_D3_GET(self,mac):
        return self._digital_in_GET(mac,3)
    
    def _webhandle_oap_digital_in_D3_PUT(self,mac):
        return self._digital_in_PUT(mac,3)
    
    # /digital_out
    
    def _digital_out_PUT(self,mac,pin):
        return self._oap_send_and_wait_for_reply(
            mac         = mac,
            method      = OAPMessage.CmdType.PUT,
            resource    = 'digital_out',
            subresource = pin,
        )
    
    def _webhandle_oap_digital_out_D4_PUT(self,mac):
        return self._digital_out_PUT(mac,0)
    
    def _webhandle_oap_digital_out_D5_PUT(self,mac):
        return self._digital_out_PUT(mac,1)
    
    def _webhandle_oap_digital_out_INDICATOR_0_PUT(self,mac):
        return self._digital_out_PUT(mac,2)
    
    # /analog
    
    def _analog_GET(self,mac,pin):
        return self._oap_send_and_wait_for_reply(
            mac         = mac,
            method      = OAPMessage.CmdType.GET,
            resource    = 'analog',
            subresource = pin,
        )
    
    def _analog_PUT(self,mac,pin):
        return self._oap_send_and_wait_for_reply(
            mac         = mac,
            method      = OAPMessage.CmdType.PUT,
            resource    = 'analog',
            subresource = pin,
        )
    
    def _webhandle_oap_analog_A0_GET(self,mac):
        return self._analog_GET(mac,0)
    
    def _webhandle_oap_analog_A0_PUT(self,mac):
        return self._analog_PUT(mac,0)
    
    def _webhandle_oap_analog_A1_GET(self,mac):
        return self._analog_GET(mac,1)
    
    def _webhandle_oap_analog_A1_PUT(self,mac):
        return self._analog_PUT(mac,1)
    
    def _webhandle_oap_analog_A2_GET(self,mac):
        return self._analog_GET(mac,2)
    
    def _webhandle_oap_analog_A2_PUT(self,mac):
        return self._analog_PUT(mac,2)
    
    def _webhandle_oap_analog_A3_GET(self,mac):
        return self._analog_GET(mac,3)
    
    def _webhandle_oap_analog_A3_PUT(self,mac):
        return self._analog_PUT(mac,3)
    
    # /temperature
    
    def _webhandle_oap_temperature_GET(self,mac):
        return self._oap_send_and_wait_for_reply(
            mac         = mac,
            method      = OAPMessage.CmdType.GET,
            resource    = 'temperature',
        )
    
    def _webhandle_oap_temperature_PUT(self,mac):
        return self._oap_send_and_wait_for_reply(
            mac         = mac,
            method      = OAPMessage.CmdType.PUT,
            resource    = 'temperature',
        )
    
    # /pkgen
    
    def _webhandle_oap_pkgen_echo_GET(self,mac):
        return self._oap_send_and_wait_for_reply(
            mac         = mac,
            method      = OAPMessage.CmdType.GET,
            resource    = 'pkgen',
            subresource = 0,
        )
    
    def _webhandle_oap_pkgen_PUT(self,mac):
        return self._oap_send_and_wait_for_reply(
            mac         = mac,
            method      = OAPMessage.CmdType.PUT,
            resource    = 'pkgen',
        )
    
    def _oap_send_and_wait_for_reply(self, mac, method, resource, subresource=None):
        
        # use only lowercase
        mac = mac.lower()
        
        # add an oapClient, if needed
        self._add_oapClient_if_needed(mac)
        
        # create data_tags
        data_tags = []
        if method==OAPMessage.CmdType.PUT:
            for (i,(n,t,d)) in enumerate(oapdefs.FIELDS[resource]):
                if d.count('w'):
                    if   t=='INT8U':
                        data_tags += [OAPMessage.TLVByte(   t=i,v=bottle.request.json[n])]
                    elif t=='INT16U':
                        data_tags += [OAPMessage.TLVShort(  t=i,v=bottle.request.json[n])]
                    elif t=='INT32U':
                        data_tags += [OAPMessage.TLVLong(   t=i,v=bottle.request.json[n])]
                    elif t=='INT8U[16]':
                        temp = bottle.request.json[n]
                        temp = ''.join([chr(int(b,16)) for b in [temp[2*j:2*j+2] for j in range(len(temp)/2)]])
                        data_tags += [OAPMessage.TLVString( t=i,v=temp)]
        
        # send OAP request
        addr           = [b for b in oapdefs.ADDRESS[resource]]
        if subresource!=None:
            addr      += [subresource]
        self.oapClients[mac].send(
            cmd_type   = method,
            addr       = addr,
            data_tags  = data_tags,
            cb         = self._oap_handle_response,
        )
        
        # wait for and handle OAP response
        with self.dataLock:
            if mac in self.outstandingEvents:
                raise SystemError('busy waiting for response')
            event = threading.Event()
            self.outstandingEvents[mac] = event
        if event.wait(self.OAP_TIMEOUT):
            # received response
            with self.dataLock:
                response = self.responses[mac]
                del self.responses[mac]
            return self._oap_format_response(resource,response)
        else:
            # timeout
            with self.dataLock:
                del self.outstandingEvents[mac]
            bottle.response.status = 504 # Gateway Timeout
            bottle.response.content_type = 'application/json'
            return json.dumps({
                'body': 'timeout!',
            })
    
    def _oap_handle_response(self, mac, oap_resp):
        macString = u.formatMacString(mac)
        
        with self.dataLock:
            if macString in self.responses:
                raise SystemError('response unread')
            
            if macString in self.outstandingEvents:
                self.responses[macString] = oap_resp
                self.outstandingEvents[macString].set()
                del self.outstandingEvents[macString]
            else:
                # received a response I'm not waiting for anymore (increase timeout?)'
                pass
    
    def _oap_format_response(self,resource,response):
        '''
        {
            'command': 1,
            'result': 0,
            'tags': [
                (255, 1, array('B', [0])),
                (0, 1, array('B', [1])),
                (1, 1, array('B', [3])),
                (2, 1, array('B', [0])),
                (3, 2, array('B', [0, 24])),
                (4, 2, array('B', [0, 1])),
                (5, 4, array('B', [0, 0, 0, 0])),
                (6, 4, array('B', [0, 0, 0, 0]))
            ]
        }
        {
            'resource': [0],
            'method':   1,
            'status':   0,
            'fields': {
                0: [1],
                1: [3],
                2: [0],
                3: [0, 24],
                4: [0, 1],
                5: [0, 0, 0, 0],
                6: [0, 0, 0, 0]
            }
        }
        '''
        tags = {k:v.tolist() for (k,_,v) in response['tags']}
        returnVal = {}
        # status
        returnVal['status']       = reversedict(oapdefs.RC)[response['result']]
        # resource
        returnVal['resource']     = reversedict(oapdefs.ADDRESS)[tuple(tags[255])]
        del tags[255]
        # method
        returnVal['method']       = reversedict(oapdefs.COMMAND)[response['command']]
        # fields
        desc = oapdefs.FIELDS[resource]
        fields = {}
        for (k,v) in tags.items():
            (n,t,d)               = desc[k]
            if t=='INT8U[16]':
                fields[n]         = ''.join(["%.2x"%i for i in v])
            elif v==[]:
                fields[n]         = v
            else:
                fields[n]         = int(''.join([chr(b) for b in v]).encode('hex'), 16)
        returnVal['fields']       = fields
        return returnVal
    
    #=== helpers
    
    def _webhandle_helpers_serialports_GET(self):
        return self._serialports_GET()
    
    def _list_motes_per_manager(self,manager):
        returnVal = []
        
        try:
            currentMac     = (0,0,0,0,0,0,0,0) # start getMoteConfig() iteration with the 0 MAC address
            continueAsking = True
            while continueAsking:
                try:
                    with self.dataLock:
                        res = self.managerHandlers[manager].connector.dn_getMoteConfig(currentMac,True)
                except APIError:
                    continueAsking = False
                else:
                    if ((not res.isAP) and (res.state in [4,])):
                        returnVal.append(u.formatMacString(res.macAddress))
                    currentMac = res.macAddress
        except ConnectionError as err:
            pass # happens when manager is disconnected
        
        return returnVal
    
    def _list_all_motes(self):
        with self.dataLock:
            returnVal = {m:self._list_motes_per_manager(m) for m in self.managerHandlers.keys()}
        return returnVal
    
    def _webhandle_helpers_motes_GET(self):
        return self._list_all_motes()
    
    def _webhandle_helpers_oapmotes_GET(self):
        with self.dataLock:
            return {'oapmotes': self.oapClients.keys(),}
    
    #=== config
    
    def _webhandle_config_GET(self):
        with self.dataLock:
           return copy.deepcopy(self.config)
    
    def _webhandle_config_POST(self):
        with self.dataLock:
            self.config = self._recursive_dict_update(
                self.config,
                bottle.request.json
            )
        self._saveConfig()
        self._syncManagers()
        with self.dataLock:
           return copy.deepcopy(self.config)
    
    def _recursive_dict_update(self,d,u):
        for k, v in u.items():
            if isinstance(v, collections.Mapping):
                r = self._recursive_dict_update(d.get(k, {}), v)
                d[k] = r
            else:
                d[k] = u[k]
        return d
    
    #=== managers
    
    def _webhandle_managers_PUT(self):
        self._managers_PUT(bottle.request.json['managers'])
    
    def _webhandle_managers_DELETE(self):
        self._managers_DELETE(bottle.request.json['managers'])
    
    #======================== error handlers ==================================
    
    def _errorhandle_404(self,error):
        error_data = {
            'body': 'There\'s nothing there! https://vine.co/v/OiZOJxjDitQ/embed/simple?audio=1',
        }
        bottle.response.status = 404
        bottle.response.content_type = 'application/json'
        return json.dumps(error_data)
    
    def _errorhandle_500(self,error):
        if type(error.exception)==NotImplementedError:
            error_data = {
                'body': 'Not implemented, yet :-)',
            }
            bottle.response.status = 501
        else:
            error_data = {
                'body': error.body,
            }
        bottle.response.content_type = 'application/json'
        return json.dumps(error_data)
    
    #======================== private =========================================
    
    def _status_GET(self):
        return {
            'SmartMesh SDK version': '.'.join([str(b) for b in sdk_version.VERSION]),
            'current time':          self._formatTime(),
            'running since':         '{0} ({1} ago)'.format(
                    self._formatTime(self.startTime),
                    datetime.timedelta(seconds=time.time()-self.startTime)
                ),
            'threads running':       [t.getName() for t in threading.enumerate()],
            'managers':              self._formatManagersStatus(),
        }
    
    def _serialports_GET(self):
        try:
            serialports = []
            
            if os.name=='nt':
                key  = winreg.OpenKey(winreg.HKEY_LOCAL_MACHINE, 'HARDWARE\\DEVICEMAP\\SERIALCOMM')
                for i in range(winreg.QueryInfoKey(key)[1]):
                    try:
                        val = winreg.EnumValue(key,i)
                    except:
                        pass
                    else:
                        if val[0].find('VCP')>-1:
                            serialports.append(str(val[1]))
            elif os.name=='posix':
                serialports = glob.glob('/dev/ttyUSB*')
            
            serialports.sort()
            
            return {
                'serialports': serialports
            }
        except Exception as err:
            return ['Could not scan for serial port. Error={0}'.format(err)]
    
    def _managers_PUT(self,newmanagers):
        with self.dataLock:
            for m in newmanagers:
                if m not in self.config['managers']:
                    self.config['managers'] += [m]
        self._saveConfig()
        self._syncManagers()
    
    def _managers_DELETE(self,oldmanagers):
        with self.dataLock:
            for m in oldmanagers:
                self.config['managers'].remove(m)
        self._saveConfig()
        self._syncManagers()
    
    def _syncManagers(self):
        with self.dataLock:
            # add
            for m in self.config['managers']:
                if m not in self.managerHandlers:
                    self.managerHandlers[m] = ManagerHandler(m,self._manager_raw_notif_handler)
            # remove
            for m in self.managerHandlers.keys():
                if m not in self.config['managers']:
                    self.managerHandlers[m].close()
                    del self.managerHandlers[m]
    
    def _manager_raw_notif_handler(self,manager,notifName,notif):
        
        # parse further
        if   notifName==IpMgrSubscribe.IpMgrSubscribe.NOTIFDATA:
            # try to parse data notifications as OAP (fails if not OAP payload, no problem)
            self.oapDispatch.dispatch_pkt(notifName,notif)
        elif notifName==IpMgrSubscribe.IpMgrSubscribe.NOTIFHEALTHREPORT:
            hr  = self.hrParser.parseHr(notif.payload)
            # POST HR to some URL
            self._send_notif(
                notifname    = 'hr',
                jsonToSend   = {
                            'name':    'hr',
                            'mac':     u.formatMacString(notif.macAddress),
                            'hr':      hr,
                        },
            )
        
        # POST raw notification to some URL
        if notifName.startswith('event'):
            nm           = 'event'
        else:
            nm           = notifName
        fields = self._stringifyMacAddresses(notif._asdict())
        self._send_notif(
            notifname    = nm,
            jsonToSend   = {
                'manager': manager,
                'name':    notifName,
                'fields':  fields,
            },
        )
    
    def _manager_oap_notif_handler(self,mac,notif):
        
        macString = u.formatMacString(mac)
        
        # add an oapClient, if needed
        self._add_oapClient_if_needed(mac)
        
        # POST OAP notification to some URLs
        fields = self._stringifyMacAddresses(notif._asdict())
        self._send_notif(
            notifname    = 'oap',
            jsonToSend   = {
                'name':    'oap',
                'mac':     macString,
                'fields':  fields,
            },
        )
    
    def _send_notif(self,notifname,jsonToSend):
        # find notification URLs
        with self.dataLock:
            urls = self.config['notification_urls'][notifname]
        
        # send notifications
        if urls:
            for url in urls:
                threading.Thread(
                    target = self._send_notif_thread,
                    args = (
                        url,
                    ),
                    kwargs = {
                        'data'        : json.dumps(jsonToSend),
                        'headers'     : {
                            'Content-type': 'application/json',
                        },
                    }
                ).start()
    
    def _send_notif_thread(self,*args,**kwargs):
        try:
            requests.post(*args,**kwargs)
        except requests.exceptions.ConnectionError:
            pass
        except Exception as err:
            print err
    
    def _stringifyMacAddresses(self,indict):
        '''
        in: {
            'field1':     123,
            'macAddress': [0,1,2,3,4,5,6,7],
        }
        out: {
            'field1':     123,
            'macAddress': '00-01-02-03-04-05-06-07',
        }
        '''
        outdict = indict
        for name in ['macAddress','source','dest']:
            try:
                assert len(outdict[name])==8
                outdict[name] = u.formatMacString(outdict[name])
            except KeyError:
                pass
        return outdict
    
    def _destringifyMacAddresses(self,d):
        '''
        in: {
            'field1':     123,
            'macAddress': '00-01-02-03-04-05-06-07',
        }
        out: {
            'field1':     123,
            'macAddress': [0,1,2,3,4,5,6,7],
        }
        returns whether was destringified
        '''
        wasDestringified = False
        for name in ['macAddress','source','dest']:
            try:
                if type(d[name]) in [str,unicode]:
                    d[name] = [int(b,16) for b in d[name].split('-')]
                    wasDestringified = True
            except KeyError:
                pass
        return wasDestringified
    
    def _add_oapClient_if_needed(self,mac):
        if type(mac)==str:
            macString = mac
            mac       = [int(b,16) for b in mac.split('-')]
        else:
            macString = u.formatMacString(mac)
        
        with self.dataLock:
            if macString not in self.oapClients:
                # get MACs per manager
                for (manager,motes) in self._list_all_motes().items():
                    if macString in manager:
                       break
                # create OAPClient
                self.oapClients[macString] = OAPClient.OAPClient(
                    mac,
                    self.managerHandlers[manager].connector.dn_sendData,
                    self.oapDispatch,
                )
    
    def _formatTime(self,ts=None):
        return time.strftime("%m/%d/%Y %H:%M:%S",time.localtime(ts))
    
    def _loadConfig(self):
        with self.dataLock:
            try:
                self.config = pickle.load(open(self.configfilename,"rb"))
            except IOError as err:
                if self.serialport:
                    managers = [self.serialport]
                else:
                    managers = []
                if self.notifprefix:
                    raise NotImplementedError()
                self.config     = {
                    'managers':         managers,
                    'notification_urls': {
                        'event':            [
                            'http://127.0.0.1:1880/event',
                            'http://127.0.0.1:8081/event',
                        ],
                        'notifLog':         [
                            'http://127.0.0.1:1880/notifLog',
                        ],
                        'notifData':        [
                            'http://127.0.0.1:1880/notifData',
                        ],
                        'notifIpData':      [
                            'http://127.0.0.1:1880/notifIpData',
                        ],
                        'notifHealthReport':[
                            'http://127.0.0.1:1880/notifHealthReport',
                        ],
                        'oap':              [
                            'http://127.0.0.1:1880/oap',
                        ],
                        'hr':               [
                            'http://127.0.0.1:1880/hr',
                        ],
                    }
                }
                self._saveConfig()
    
    def _saveConfig(self):
        with self.dataLock:
            pickle.dump(self.config, open(self.configfilename,"wb"))

#============================ main =======================================

def main(args):
    jsonServer = JsonServer(**args)

if __name__=="__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument('--tcpport',        default=8080)
    parser.add_argument('--serialport',     default=None)
    parser.add_argument('--notifprefix',    default='')
    parser.add_argument('--configfilename', default='JsonServer.config')
    args = vars(parser.parse_args())
    main(args)
