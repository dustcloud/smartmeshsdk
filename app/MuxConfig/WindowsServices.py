'''Windows service utilities and Process Manager class

'''

import os
import platform
import subprocess

# note: should only be imported when running under Windows
import pywintypes
import win32service
import win32serviceutil
import win32com.client
import _winreg

import ProcessManager

# Set up directory constants
if os.name in ['nt']:
    if platform.win32_ver()[0] in ['XP']:
        # set up paths for Windows XP
        PROGRAM_FILES = os.environ['PROGRAMFILES']
        # there is no single XP environment variable for common application data
        # to get '/Docs.../All Users/Application Data', we do some path operations
        PROGRAM_DATA = os.path.join(os.environ['ALLUSERSPROFILE'],
                                    os.path.split(os.environ['APPDATA'])[1])

    elif platform.win32_ver()[0] in ['7']:
        # set up paths for Windows 7
        if '64' in platform.machine():
            PROGRAM_FILES = os.environ['PROGRAMFILES(X86)']
        else:
            PROGRAM_FILES = os.environ['PROGRAMFILES']
        PROGRAM_DATA = os.environ['PROGRAMDATA']

else:
    raise NotImplemented('Unknown platform')

# ----------------------------------------------------------------------
# Windows Service Management

class WindowsProcessManager(ProcessManager.ProcessManager):

    SERIAL_MUX_BINARY = os.path.join(PROGRAM_FILES,
                                     'Dust Networks', 'SerialMux', 'serial_mux.exe')
    SERIAL_MUX_CONFIG_DIR = os.path.join(PROGRAM_DATA,
                                         'Dust Networks', 'SerialMux')

    def __init__(self):
        ProcessManager.ProcessManager.__init__(self)

    def create(self, name):
        'Create a Serial Mux configuration and daemon/service'
        self.create_serial_mux_service(name)

    def remove(self, name):
        'Remove a Serial Mux configuration and daemon/service'
        self.remove_serial_mux_service(name)

    def start(self, name):
        'Start a Serial Mux daemon/service'
        self.start_service(name)

    def stop(self, name):
        'Stop a Serial Mux daemon/service'
        self.stop_service(name)

    def get_serial_mux_version(self):
        p = subprocess.Popen([self.SERIAL_MUX_BINARY, '--version'],
                             stdout=subprocess.PIPE)
        outp, errp = p.communicate()
        # TODO: parse
        return outp.strip()

    def _make_service_name(self, name):
        return 'SerialMux_' + name

    def create_serial_mux_service(self, name):
        service_name = self._make_service_name(name)
        service_cmd = ' '.join(['"%s"' % self.SERIAL_MUX_BINARY,
                                '--daemon',
                                '--directory',
                                '"%s"' % os.path.join(self.SERIAL_MUX_CONFIG_DIR, name)])
        p = subprocess.Popen(['sc', 'create', service_name, 'binPath=', service_cmd,
                              'start=', 'auto'])
        outp, errp = p.communicate()
        # TODO: expect '[SC] CreateService SUCCESS'
        return outp

    def remove_serial_mux_service(self, name):
        self.stop_service(name)
        win32serviceutil.RemoveService(self._make_service_name(name))
    
    def start_service(self, name):
        svc_name = self._make_service_name(name)
        try:
            win32serviceutil.StartService(svc_name)
            # TODO: what happens on timeout
            win32serviceutil.WaitForServiceStatus(svc_name,
                                                  win32service.SERVICE_RUNNING, 5)
        except pywintypes.error:
            raise RuntimeError("can not start service '%s'" % name)
        
    def stop_service(self, name):
        svc_name = self._make_service_name(name)
        try:
            win32serviceutil.StopService(svc_name)
            # TODO: exception on timeout
            win32serviceutil.WaitForServiceStatus(svc_name,
                                                  win32service.SERVICE_STOPPED, 5)
        except pywintypes.error:
            pass

# ----------------------------------------------------------------------
# Utility functions


def scan_services(service_prefix = 'SerialMux'):
    'Returns a list of Windows services named with a given prefix'
    wmi = win32com.client.GetObject('winmgmts:')
    services = wmi.InstancesOf('Win32_Service')
    service_configs = []
    for svc in services:
        if svc.Name.startswith(service_prefix):
            # TODO: if a service is created manually, it might be possible for
            # the service name to have a different suffix than its config name
            # it would be more accurate to scan the binPath for the config
            # directory
            sc = {'service_name': svc.Name.lstrip(service_prefix+'_'),
                  'state': svc.State}
            service_configs.append(sc)

    return service_configs


def get_virtual_serial_ports():
    'Returns a list of the VCP serial ports'
    serial_ports = []
    if os.name in ['nt']:
        REGISTRY_SERIAL_PORTS = 'HARDWARE\\DEVICEMAP\\SERIALCOMM'
        key = _winreg.OpenKey(_winreg.HKEY_LOCAL_MACHINE, REGISTRY_SERIAL_PORTS)
        for i in range(_winreg.QueryInfoKey(key)[1]):
            try:
                val = _winreg.EnumValue(key, i)
            except:
                pass
            else:
                if val[0].find('VCP') > -1:
                    serial_ports.append(str(val[1]))
    else:
        raise NotImplemented()
    
    return serial_ports
