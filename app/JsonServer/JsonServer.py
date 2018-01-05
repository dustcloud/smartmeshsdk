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

# built-in
import argparse
import socket
import time
import pprint
import threading
import json
import traceback

# requirements
import requests
import bottle
from bottle                  import hook

# SmartMeshSDK
from SmartMeshSDK            import sdk_version
from SmartMeshSDK.utils      import JsonManager

# DustCli
from dustCli                 import DustCli

#============================ helpers =========================================

pp = pprint.PrettyPrinter(indent=4)

#============================ classes =========================================

class JsonServer(object):
    
    def __init__(self, tcpport, autoaddmgr, autodeletemgr, serialport, configfilename):
        
        # store params
        self.tcpport              = tcpport
        self.autoaddmgr           = autoaddmgr
        self.autodeletemgr        = autodeletemgr
        self.serialport           = serialport
        self.configfilename       = configfilename
        
        # local variables
        self.jsonManager          = JsonManager.JsonManager(
            autoaddmgr            = autoaddmgr,
            autodeletemgr         = autodeletemgr,
            serialport            = serialport,
            configfilename        = configfilename,
            notifCb               = self._notif_cb,
        )
        
        #=== CLI interface
        
        self.cli                  = DustCli.DustCli(
            quit_cb  = self._clihandle_quit,
            versions = {
                'SmartMesh SDK': sdk_version.VERSION,
            },
        )
        self.cli.registerCommand(
            name                  = 'status',
            alias                 = 's',
            description           = 'get the current status of the application',
            params                = [],
            callback              = self._clihandle_status,
        )
        self.cli.registerCommand(
            name                  = 'serialports',
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
        self.websrv.route('/api/v1/helpers/snapshot',                     'POST',   self._webhandle_helpers_snapshot_POST)
        self.websrv.route('/api/v1/helpers/snapshot',                     'GET',    self._webhandle_helpers_snapshot_GET)
        #=== config
        self.websrv.route('/api/v1/config',                               'GET',    self._webhandle_config_GET)
        self.websrv.route('/api/v1/config',                               'POST',   self._webhandle_config_POST)
        #=== managers
        self.websrv.route('/api/v1/config/managers',                      'PUT',    self._webhandle_managers_PUT)
        self.websrv.route('/api/v1/config/managers',                      'DELETE', self._webhandle_managers_DELETE)
        self.websrv.error(code=404)(self._webhandler_error_404)
        self.websrv.error(code=500)(self._webhandler_error_500)
        self.websrv.hook('after_request')(self._add_JsonServer_token_if_requested)
        webthread = threading.Thread(
            target = self._bottle_try_running_forever,
            args   = (self.websrv.run,),
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
    
    #======================== admin ===========================================
    
    def _bottle_try_running_forever(self,*args,**kwargs):
        RETRY_PERIOD = 3
        while True:
            try:
                args[0](**kwargs) # blocking
            except socket.error as err:
                if err[0]==10013:
                    print 'FATAL: cannot open TCP port {0}.'.format(kwargs['port'])
                    print '    Is another application running on that port?'
                else:
                    print logError(err)
            except Exception as err:
                print logError(err)
            print '    Trying again in {0} seconds'.format(RETRY_PERIOD),
            for _ in range(RETRY_PERIOD):
                time.sleep(1)
                print '.',
            print ''
    
    #======================== CLI handlers ====================================
    
    def _clihandle_quit(self):
        
        self.jsonManager.close()
        
        time.sleep(.3)
        print "bye bye."
    
    def _clihandle_status(self,params):
        pp.pprint(self.jsonManager.status_GET())
    
    def _clihandle_serialports(self,params):
        pp.pprint(self.jsonManager.serialports_GET())
    
    def _clihandle_connectmanager(self,params):
        self.jsonManager.managers_PUT([params[0],])
    
    def _clihandle_disconnectmanager(self,params):
        self.jsonManager.managers_DELETE([params[0],])
    
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
    
    def _webhandle_status_GET(self):
        return self.jsonManager.status_GET()
    
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
        
        return self.jsonManager.raw_POST(commandArray, fields, manager)
    
    #=== oap
    
    # /info
    
    def _webhandle_oap_info_GET(self,mac):
        return self.jsonManager.oap_info_GET(mac)
    
    # /main
    
    def _webhandle_oap_main_GET(self,mac):
        return self.jsonManager.oap_main_GET(mac)
    
    def _webhandle_oap_main_PUT(self,mac):
        return self.jsonManager.oap_main_PUT(mac,body=bottle.request.json)
    
    # /digital_in
    
    def _webhandle_oap_digital_in_D0_GET(self,mac):
        return self.jsonManager.oap_digital_in_GET(mac,0)
    
    def _webhandle_oap_digital_in_D0_PUT(self,mac):
        return self.jsonManager.oap_digital_in_PUT(mac,0,body=bottle.request.json)
    
    def _webhandle_oap_digital_in_D1_GET(self,mac):
        return self.jsonManager.oap_digital_in_GET(mac,1)
    
    def _webhandle_oap_digital_in_D1_PUT(self,mac):
        return self.jsonManager.oap_digital_in_PUT(mac,1,body=bottle.request.json)
    
    def _webhandle_oap_digital_in_D2_GET(self,mac):
        return self.jsonManager.oap_digital_in_GET(mac,2)
    
    def _webhandle_oap_digital_in_D2_PUT(self,mac):
        return self.jsonManager.oap_digital_in_PUT(mac,2,body=bottle.request.json)
    
    def _webhandle_oap_digital_in_D3_GET(self,mac):
        return self.jsonManager.oap_digital_in_GET(mac,3)
    
    def _webhandle_oap_digital_in_D3_PUT(self,mac):
        return self.jsonManager.oap_digital_in_PUT(mac,3,body=bottle.request.json)
    
    # /digital_out
    
    def _webhandle_oap_digital_out_D4_PUT(self,mac):
        return self.jsonManager.oap_digital_out_PUT(mac,0,body=bottle.request.json)
    
    def _webhandle_oap_digital_out_D5_PUT(self,mac):
        return self.jsonManager.oap_digital_out_PUT(mac,1,body=bottle.request.json)
    
    def _webhandle_oap_digital_out_INDICATOR_0_PUT(self,mac):
        return self.jsonManager.oap_digital_out_PUT(mac,2,body=bottle.request.json)
    
    # /analog
    
    def _webhandle_oap_analog_A0_GET(self,mac):
        return self.jsonManager.oap_analog_GET(mac,0)
    
    def _webhandle_oap_analog_A0_PUT(self,mac):
        return self.jsonManager.oap_analog_PUT(mac,0,body=bottle.request.json)
    
    def _webhandle_oap_analog_A1_GET(self,mac):
        return self.jsonManager.oap_analog_GET(mac,1)
    
    def _webhandle_oap_analog_A1_PUT(self,mac):
        return self.jsonManager.oap_analog_PUT(mac,1,body=bottle.request.json)
    
    def _webhandle_oap_analog_A2_GET(self,mac):
        return self.jsonManager.oap_analog_GET(mac,2)
    
    def _webhandle_oap_analog_A2_PUT(self,mac):
        return self.jsonManager.oap_analog_PUT(mac,2,body=bottle.request.json)
    
    def _webhandle_oap_analog_A3_GET(self,mac):
        return self.jsonManager.oap_analog_GET(mac,3)
    
    def _webhandle_oap_analog_A3_PUT(self,mac):
        return self.jsonManager.oap_analog_PUT(mac,3,body=bottle.request.json)
    
    # /temperature
    
    def _webhandle_oap_temperature_GET(self,mac):
        return self.jsonManager.oap_temperature_GET(mac)
    
    def _webhandle_oap_temperature_PUT(self,mac):
        return self.jsonManager.oap_temperature_PUT(mac,body=bottle.request.json)
    
    # /pkgen
    
    def _webhandle_oap_pkgen_echo_GET(self,mac):
        return self.jsonManager.oap_pkgen_echo_GET(mac)
    
    def _webhandle_oap_pkgen_PUT(self,mac):
        return self.jsonManager.oap_pkgen_PUT(mac,body=bottle.request.json)
    
    #=== helpers
    
    def _webhandle_helpers_serialports_GET(self):
        return self.jsonManager.serialports_GET()
    
    def _webhandle_helpers_motes_GET(self):
        return self.jsonManager.motes_GET()
    
    def _webhandle_helpers_oapmotes_GET(self):
        return self.jsonManager.oapmotes_GET()
    
    def _webhandle_helpers_snapshot_POST(self):
        try:
            correlationID = bottle.request.json['correlationID']
        except KeyError:
            correlationID = None
        return self.jsonManager.snapshot_POST(
            manager       = bottle.request.json['manager'],
            correlationID = correlationID,
        )
    
    def _webhandle_helpers_snapshot_GET(self):
        return self.jsonManager.snapshot_GET()
    
    #=== config
    
    def _webhandle_config_GET(self):
        return self.jsonManager.config_GET()
    
    def _webhandle_config_POST(self):
        return self.jsonManager.config_POST(bottle.request.json)
    
    def _webhandle_managers_PUT(self):
        return self.jsonManager.managers_PUT(bottle.request.json['managers'])
    
    def _webhandle_managers_DELETE(self):
        return self.jsonManager.managers_DELETE(bottle.request.json['managers'])
    
    #=== errors
    
    def _webhandler_error_404(self,error):
        error_data = {
            'body': 'There\'s nothing there! https://vine.co/v/OiZOJxjDitQ/embed/simple?audio=1',
        }
        bottle.response.status = 404
        bottle.response.content_type = 'application/json'
        return json.dumps(error_data)
    
    def _webhandler_error_500(self,error):
        if type(error.exception)==NotImplementedError:
            error_data = {
                'body': 'Not implemented, yet :-)',
            }
            bottle.response.status = 501
        else:
            error_data = {
                'body':      'internal server error',
                'exception': str(error.exception),
                'traceback': error.traceback,
            }
        bottle.response.content_type = 'application/json'
        return json.dumps(error_data)
    
    #=== notifications
    
    def _notif_cb(self,notifName,notifJson):
        
        # find notification URLs
        urls = self.jsonManager.config_GET()['notification_urls'][notifName]
        
        # send notifications
        if urls:
            for url in urls:
                notifthread = threading.Thread(
                    target = self._send_notif_thread,
                    args = (
                        url,
                    ),
                    kwargs = {
                        'data'        : json.dumps(notifJson),
                        'headers'     : {
                            'Content-type': 'application/json',
                        },
                    }
                )
                notifthread.name = '{0}->{1}'.format(notifName,url)
                notifthread.start()
    
    def _send_notif_thread(self,*args,**kwargs):
        try:
            requests.post(*args,**kwargs)
        except requests.exceptions.ConnectionError:
            pass
        except Exception as err:
            print err
    
#============================ main ============================================

def main(args):
    jsonServer = JsonServer(**args)

if __name__=="__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument('--tcpport',        default=8080)
    parser.add_argument('--autoaddmgr',     default=True)
    parser.add_argument('--autodeletemgr',  default=True)
    parser.add_argument('--serialport',     default=None)
    parser.add_argument('--configfilename', default='JsonServer.config')
    args = vars(parser.parse_args())
    main(args)
