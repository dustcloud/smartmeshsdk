'''Platform agnostic process (service) management functions
'''

import os
import platform
import shutil

SERIAL_MUX_CONFIG_TEMPLATE = '''# Configuration file for Serial Mux
port = {com_port}
listen = {listener_port}
'''

SERIAL_MUX_CONFIG_FILE = 'serial_mux.cfg'

def create_config(dir, name, com_port = '', listener_port = 0):
    # create the config directory
    os.makedirs(os.path.join(dir, name))
    # write the configuration file
    update_config(dir, name, com_port, listener_port)

def update_config(dir, name, com_port, listener_port):
    cf_path = os.path.join(dir, name, SERIAL_MUX_CONFIG_FILE)
    with open(cf_path, 'w') as cf:
        cf.write(SERIAL_MUX_CONFIG_TEMPLATE.format(com_port=com_port,
                                                   listener_port = listener_port)) 

def remove_config(dir, name):
    # remove the config directory
    config_dir = os.path.join(dir, name)
    shutil.rmtree(config_dir)

    
class ProcessManager(object):
    'Interface for managing Serial Mux processes'

    # Standard path constants
    SERIAL_MUX_BINARY = ''
    SERIAL_MUX_CONFIG_DIR = ''
    
    def create(self, name):
        'Create a Serial Mux configuration and daemon/service'
        raise NotImplemented('create not implemented')

    def remove(self, name):
        'Remove a Serial Mux configuration and daemon/service'
        raise NotImplemented('remove not implemented')

    def update(self, name, com_port, listener_port, restart = False):
        'Update a Serial Mux configuration'
        self.stop(name)
        update_config(self.SERIAL_MUX_CONFIG_DIR, name, com_port, listener_port)
        if restart:
            self.start(name)

    def start(self, name):
        'Start a Serial Mux daemon/service'
        raise NotImplemented('start not implemented')

    def stop(self, name):
        'Stop a Serial Mux daemon/service'
        raise NotImplemented(' not implemented')


def GetProcessManager():
    '''Factory for ProcessManager objects

    Returns: ProcessManager object for the current platform
    '''

    if os.name in ['nt']:
        from WindowsServices import WindowsProcessManager
        return WindowsProcessManager()

    elif platform.platform().startswith('Linux'):
        # TODO: import the right thing
        return ProcessManager()

    elif platform.platform().startswith('CYGWIN_NT'):
        # TODO: import the right thing
        return ProcessManager()


