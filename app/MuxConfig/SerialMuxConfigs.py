#!/usr/bin/env python

import os
import sys

# only when on Windows
if os.name in ['nt']:
    from WindowsServices import scan_services, get_virtual_serial_ports

class SerialMuxConfig(object):
    '''The Serial Mux configuration has the following properties:
    - com port
    - listener (TCP) port
    - service status: Running, Stopped, No service
    - device type: Manager, Mote or Unknown
    - identifier: MAC address of the device
    '''

    STATUS_RUNNING = 'Running'
    STATUS_STOPPED = 'Stopped'
    STATUS_NONE = 'No service'

    DEVICE_MANAGER = 'Manager'
    DEVICE_MOTE = 'Mote'
    DEVICE_UNKNOWN = 'Unknown'
    
    def __init__(self, config_name):
        self.config_name = config_name
        self.com_port = ''
        self.listener_port = ''
        self.status = self.STATUS_NONE
        self.device_type = self.DEVICE_UNKNOWN
        self.identifier = ''

    def device_info(self):
        dev_info = self.device_type
        if self.device_type != self.DEVICE_UNKNOWN and self.identifier:
            dev_info += ': ' + '-'.join(['%02X' % b for b in self.identifier[-2:]])
        return dev_info


# TODO: rework to organize by config name

class SerialMuxTable(object):
    '''The Serial Mux table holds the description for each known configuration'''

    def __init__(self):
        self._service_map = {}
        self._all_ports = []
        
    def add(self, config_name):
        try:
            smc = self.find_config(config_name)
        except KeyError:
            smc = SerialMuxConfig(config_name)
            self._service_map[config_name] = smc
        return smc

    def remove(self, config_name):
        try:
            del(self._service_map[config_name])
        except KeyError:
            pass

    def find_com_port(self, com_port):
        return [smc for smc in self._service_map.values()
                if smc.com_port == com_port][0]

    def find_config(self, config_name):
        return self._service_map[config_name]

    def all_ports(self):
        'Returns the list of all (virtual) serial ports'
        return self._all_ports

    def get_ports(self):
        'Returns the list of all ports configured with Serial Mux services'
        return [smc.com_port for smc in self._service_map.values()]

    def get_mux_version(self):
        return 'unknown'


import os
import glob
import re

def scan_configs(config_dir):
    savedir = os.getcwd()
    os.chdir(config_dir)

    configs = []
    config_files = glob.glob('*/serial_mux.cfg')
    for config_file in config_files:
        with open(config_file, 'r') as cf:
            sm_config = {'config_name': os.path.dirname(config_file)}
            for l in cf.readlines():
                m = re.search('port\s*=\s*(.*)$', l)
                if m:
                    sm_config['com_port'] = m.group(1)
                m = re.search('listen\s*=\s*([0-9]+)$', l)
                if m:
                    sm_config['listener_port'] = m.group(1)

            configs.append(sm_config)
    
    os.chdir(savedir)
    return configs


CONFIG_PREFIX = 'Config'

# TODO: should this search the SerialMuxTable instead?
def find_available_name(config_dir):
    savedir = os.getcwd()
    os.chdir(config_dir)
    for idx in range(1, 100):
        config_name = CONFIG_PREFIX + '%02d' % idx
        if not os.path.isdir(config_name):
            break
    else:
        raise RuntimeError('too many configurations')
    os.chdir(savedir)
    return config_name


import socket
from SmartMeshSDK                      import ApiException
from SmartMeshSDK.IpMgrConnectorMux    import IpMgrConnectorMux

def check_device(sm_data):
    if (sm_data.com_port and sm_data.listener_port
        and sm_data.status == SerialMuxConfig.STATUS_RUNNING):
        mgr = IpMgrConnectorMux.IpMgrConnectorMux()
        try: 
            mgr.connect({'port': int(sm_data.listener_port)})
            sys_info = mgr.dn_getSystemInfo()
            sm_data.device_type = SerialMuxConfig.DEVICE_MANAGER
            sm_data.identifier = sys_info.macAddress
            mgr.disconnect()
        except ApiException.ConnectionError:
            sm_data.identifier = ''
        except socket.error:
            sm_data.identifier = ''
