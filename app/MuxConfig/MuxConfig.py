#!/usr/bin/env python

#============================ adjust path =====================================

import sys
import os
if __name__ == "__main__":
    here = sys.path[0]
    sys.path.insert(0, os.path.join(here, '..', '..','libs'))
    sys.path.insert(0, os.path.join(here, '..', '..','external_libs'))

#============================ verify installation =============================

from SmartMeshSDK.utils import SmsdkInstallVerifier
(goodToGo,reason) = SmsdkInstallVerifier.verifyComponents(
                            [
                                SmsdkInstallVerifier.PYTHON,
                                SmsdkInstallVerifier.PYWIN32,
                                SmsdkInstallVerifier.PYSERIAL,
                            ]
                        )
if not goodToGo:
    print "Your installation does not allow this application to run:\n"
    print reason
    raw_input("Press any button to exit")
    sys.exit(1)

#============================ imports =========================================

import Tkinter
try:
    import ttk
except ImportError:
    ttk = Tkinter
import re
import threading

import SerialMuxConfigs
import ProcessManager

from SmartMeshSDK import sdk_version
from dustUI       import dustWindow

#============================ defines =========================================

EXPAND_ALL    = Tkinter.N + Tkinter.E + Tkinter.S + Tkinter.W
EXPAND_HORIZ  = Tkinter.E + Tkinter.W

DESCRIPTION   = '''The Serial Mux Configurator provides a simple editor for Serial Mux configurations.'''


def serial_port_key(sp):
    'Returns a key value that can be used to sort serial port devices in a sensible order'
    if sp.startswith('COM'):
        return int(sp.lstrip('COM'))
    else:
        return sp

#============================ body ============================================

class dustStatusWindow(dustWindow.dustWindow):
    def __init__(self, appname, closeCallback):
        dustWindow.dustWindow.__init__(self, appname, closeCallback)

        self.status_var = Tkinter.StringVar()
        self.status = ttk.Label(self, textvariable=self.status_var)
        self.status.grid(row=100, column=0, padx=2, sticky=EXPAND_HORIZ)

        sep = ttk.Separator(self, orient='vertical')
        sep.grid(row=100, column=1, sticky=Tkinter.N+Tkinter.S)

        #re-grid the version
        self.version.grid(row=100, column=2, padx=2)

    def get_status_var(self):
        return self.status_var

# from: http://effbot.org/zone/tkinter-entry-validate.htm
class ValidatingEntry(ttk.Entry):
    # base class for validating entry widgets

    def __init__(self, master, value="", **kw):
        apply(ttk.Entry.__init__, (self, master), kw)
        self.__value = value
        self.__variable = Tkinter.StringVar()
        self.__variable.set(value)
        self.__variable.trace("w", self.__callback)
        self.config(textvariable=self.__variable)

    def __callback(self, *dummy):
        value = self.__variable.get()
        newvalue = self.validate(value)
        print 'Validating:', value
        if newvalue is None:
            #self.__variable.set(self.__value)
            print 'Bad'
            self.configure(background='red')
        elif newvalue != value:
            print 'Updating'
            self.__value = newvalue
            self.__variable.set(self.newvalue)
        else:
            self.__value = value

    def validate(self, value):
        # override: return value, new value, or None if invalid
        return value

    def get_var(self):
        return self.__variable

class IntegerEntry(ValidatingEntry):
    def validate(self, value):
        try:
            if value:
                v = int(value)
            return value
        except ValueError:
            return None

def setupStyle():
    style = ttk.Style()

    BACKGROUND_COLOR = '#f2f2f2'

    # Common settings
    for wclass in ['TFrame', 'TLabel', 'TEntry', 'TCombobox']:
        style.configure(wclass, background=BACKGROUND_COLOR)

    # Class-specific settings
    style.configure("TLabel",
                    padding=2)
    
    # Table header style
    style.configure("TableHeader.TLabel",
                    font='arial 9 bold')

    # Invalid entry
    style.configure("Invalid.TEntry",
                    background='red')


class SMConfigUI(object):
    '''UI for the Serial Mux Configuration Manager'''

    def __init__(self):
        self.controller = None

        self.root = dustStatusWindow('Serial Mux Configurator', self._close)
        self.root.resizable(1, 1)
        self.root.columnconfigure(0, weight=1)
        self.root.rowconfigure(0, weight=1)
        self.root.rowconfigure(99, weight=1)

        setupStyle()
        
        style = ttk.Style()
        self.root.configure(background=style.lookup('TFrame', 'background'))

        self.uiElements = {}
        self.uiValues = {}
        self.frame = ttk.Frame(self.root, width=300, height=200)
        self.frame.grid(row=0, column=0, columnspan=3, sticky=EXPAND_ALL)
        self.frame.columnconfigure(0, weight=1)
        self.frame.rowconfigure(0, weight=1)        

        self.description = ttk.Label(self.frame, text=DESCRIPTION)
        self.description.grid(row=0, column=0, columnspan=2,
                              padx=4, pady=4, sticky=EXPAND_HORIZ)
        
        self.table = ttk.Frame(self.frame)
        self.table.grid(row=1, column=0, columnspan=2,
                        padx=4, pady=4, sticky=EXPAND_ALL)
        self.table.columnconfigure(3, weight=1)
        self.table.rowconfigure(0, weight=1)

        h1 = ttk.Label(self.table, text='Serial port', style='TableHeader.TLabel')
        h1.grid(row=0, column=0, padx=3, sticky=Tkinter.W)
        h2 = ttk.Label(self.table, text='Device', style='TableHeader.TLabel')
        h2.grid(row=0, column=1, padx=3, sticky=Tkinter.W)
        h2 = ttk.Label(self.table, text='TCP port', style='TableHeader.TLabel')
        h2.grid(row=0, column=2, padx=3, sticky=Tkinter.W)
        h3 = ttk.Label(self.table, text='Status', style='TableHeader.TLabel')
        h3.grid(row=0, column=3, padx=3, sticky=Tkinter.W)

        sep = ttk.Separator(self.table, orient='horizontal')
        sep.grid(row=1, column=0, columnspan=4, sticky=EXPAND_HORIZ)

        self.add_button = ttk.Button(self.frame, text='Add configuration',
                                         command=self.create_service)
        self.add_button.grid(row=2, column=0, padx=2, sticky=Tkinter.E)
        self.add_button.columnconfigure(0, weight=1)

        self.refresh_button = ttk.Button(self.frame, text='Refresh',
                                         command=self.refresh)
        self.refresh_button.grid(row=2, column=1, padx=2, sticky=Tkinter.E)


    def register_controller(self, controller):
        self.controller = controller

    def set_status(self, msg):
        self.root.get_status_var().set(msg)

    def validate_listener_port(self, uiElement, listener_port):
        widget = self.root.nametowidget(uiElement)
        is_valid = False
        try: 
            is_valid = (int(listener_port) > 0)
        except:
            pass
        if is_valid:
            widget.configure(style='TEntry')
        else:
            widget.configure(style='Invalid.TEntry')
        return is_valid

    def _createRow(self, sm_config, row, port_list):
        grid_row = 2 * (row + 1)

        # Serial port
        port_var = Tkinter.StringVar()
        port_var.set(sm_config.com_port)
        cp_label = ttk.Combobox(self.table, width=6, textvariable=port_var,
                                values=port_list)
        cp_label.grid(row=grid_row, column=0, pady=3)

        #vcmd = (cp_label.register(self.validate_serial_port), cp_label, '%P')
        #cp_label.configure(validate='focusout', validatecommand=vcmd)

        # Device info
        device_var = Tkinter.StringVar()
        device_var.set(sm_config.device_info())
        dev_label = ttk.Label(self.table, width=16, textvariable=device_var)
        dev_label.grid(row=grid_row, column=1, padx=3, sticky=Tkinter.W)
        dev_label.columnconfigure(1, weight=1)

        # Listener port
        listener_var = Tkinter.StringVar()
        listener_var.set(sm_config.listener_port)
        lp_label = ttk.Entry(self.table, width=6, textvariable=listener_var)
        lp_label.grid(row=grid_row, column=2, padx=3)
        
        vcmd = (self.root.register(self.validate_listener_port), '%W', '%P')
        lp_label.configure(validate='focus', validatecommand=vcmd)

        # Status
        status_var = Tkinter.StringVar()
        status_var.set(sm_config.status)
        st_label = ttk.Label(self.table, width=16, textvariable=status_var)
        st_label.grid(row=grid_row, column=3, padx=3, sticky=Tkinter.W)
        st_label.columnconfigure(3, weight=1)

        # Command buttons
        save_button = ttk.Button(self.table, text='Save',
                                 width=6,
                                 command=lambda: self.update_service(sm_config))
        save_button.grid(row=grid_row, column=4, padx=2)

        start_button = ttk.Button(self.table, text='Start',
                                  width=6,
                                  command=lambda: self.controller.start_service(sm_config))
        start_button.grid(row=grid_row, column=5, padx=2)

        stop_button = ttk.Button(self.table, text='Stop',
                                 width=6,
                                 command=lambda: self.controller.stop_service(sm_config))
        stop_button.grid(row=grid_row, column=6, padx=2)

        remove_button = ttk.Button(self.table, text='Remove',
                                   width=7,
                                   command=lambda: self.controller.remove_service(sm_config))
        remove_button.grid(row=grid_row, column=7, padx=2)

        # variables are updated by service name
        self.uiValues[sm_config.config_name] = {'com_port': port_var,
                                                 'listener_port': listener_var,
                                                 'device': device_var,
                                                 'status': status_var}

        uiRow = {'com_port': cp_label,
                 'device': dev_label,
                 'listener_port': lp_label,
                 'status': st_label,
                 'save': save_button,
                 'start': start_button,
                 'stop': stop_button,
                 'remove': remove_button,
                 #'svc_button': svc_button,
                 #'menu': svc_menu,
                 }
        self.uiElements[sm_config.config_name] = uiRow

        # make sure states and values are up to date
        self.update_row_values(sm_config)


    def update(self, sm_data):
        # forget existing UI elements
        for row in self.uiElements.values():
            for name, ui_element in row.items():
                if not name.startswith('menu'):
                    ui_element.grid_forget()
        self.uiElements = {}
        self.uiValues = {}

        # TODO: drive update() from controller:
        # use clear_rows(), then add_row() for each service

        all_ports = self.controller._all_ports
        all_ports.sort(key=serial_port_key)
        ports = sm_data.get_ports()
        ports.sort(key=serial_port_key)
        for idx, port in enumerate(ports):
            self._createRow(sm_data.find_com_port(port), idx, all_ports)

    def update_row_values(self, sm_config):
        # get uiValues
        uiv = self.uiValues[sm_config.config_name]
        # get uiElement
        uiels = self.uiElements[sm_config.config_name]

        # TODO: update serial port? tcp port?
        
        # update device, status from model
        uiv['device'].set(sm_config.device_info())
        uiv['status'].set(sm_config.status)

        # Set the command states
        if sm_config.status == SerialMuxConfigs.SerialMuxConfig.STATUS_RUNNING:
            uiels['start'].configure(state='disabled')
            uiels['stop'].configure(state='normal')

        elif sm_config.status == SerialMuxConfigs.SerialMuxConfig.STATUS_STOPPED:
            uiels['start'].configure(state='normal')
            uiels['stop'].configure(state='disabled')


    # Commands - the controller isn't initialized in the very beginning, so
    # these command handlers redirect to the controller

    def create_service(self):
        self.controller.create_service()

    def refresh(self):
        self.controller.refresh()

    def update_service(self, sm_config):
        # get uiValues
        uiv = self.uiValues[sm_config.config_name]
        sm_config.com_port = uiv['com_port'].get()
        sm_config.listener_port = uiv['listener_port'].get()
        self.controller.update_service(sm_config)
        

    def run(self):
        self.root.mainloop()

    def _close(self):
        pass


from SerialMuxConfigs import scan_configs
# TODO: clean up scan functions
if os.name in ['nt']:
    from WindowsServices import scan_services, get_virtual_serial_ports


class SerialMuxController(object):
    def __init__(self, ui, model):
        self.ui = ui
        self.model = model
        self.processmgr = ProcessManager.GetProcessManager()
        self.ui.set_status(self.processmgr.get_serial_mux_version())
        
    def refresh(self):
        self.scan()
        self.ui.update(self.model)

    def scan(self):
        mux_configs = scan_configs(self.processmgr.SERIAL_MUX_CONFIG_DIR)
        for mux_config in mux_configs:
            smc = self.model.add(mux_config['config_name'])
            smc.listener_port = mux_config['listener_port']
            smc.com_port = mux_config['com_port']
            
        svc_configs = scan_services()
        for svc_config in svc_configs:
            #print 'Scanning', svc_config['service_name']
            smc = self.model.find_config(svc_config['service_name'])
            if svc_config['state'] == 'Running':
                smc.status = SerialMuxConfigs.SerialMuxConfig.STATUS_RUNNING
                SerialMuxConfigs.check_device(smc)
            elif svc_config['state'] == 'Stopped':
                smc.status = SerialMuxConfigs.SerialMuxConfig.STATUS_STOPPED

        self._all_ports = get_virtual_serial_ports()
        


    def create_service(self):
        config_dir = self.processmgr.SERIAL_MUX_CONFIG_DIR
        # create config
        config_name = SerialMuxConfigs.find_available_name(config_dir)
        self.model.add(config_name)
        ProcessManager.create_config(config_dir, config_name)
        # create daemon/service
        self.processmgr.create(config_name)
        # update UI
        self.ui.update(self.model)

    def remove_service(self, sm_config):
        print 'Removing', sm_config.config_name
        config_dir = self.processmgr.SERIAL_MUX_CONFIG_DIR
        # remove daemon/service
        self.processmgr.remove(sm_config.config_name)
        self.model.remove(sm_config.config_name)
        # remove config
        ProcessManager.remove_config(config_dir, sm_config.config_name)
        # update UI
        self.ui.update(self.model)

    def start_service(self, sm_config):
        print 'Starting', sm_config.config_name
        self.processmgr.start(sm_config.config_name)
        # TODO: handle errors
        sm_config.status = SerialMuxConfigs.SerialMuxConfig.STATUS_RUNNING
        SerialMuxConfigs.check_device(sm_config)
        # update UI
        self.ui.update_row_values(sm_config)

    def stop_service(self, sm_config):
        print 'Stopping', sm_config.config_name
        self.processmgr.stop(sm_config.config_name)
        sm_config.status = SerialMuxConfigs.SerialMuxConfig.STATUS_STOPPED
        # update UI
        self.ui.update_row_values(sm_config)

    def update_service(self, sm_config):
        do_restart = (sm_config.status == SerialMuxConfigs.SerialMuxConfig.STATUS_RUNNING)
        self.processmgr.update(sm_config.config_name,
                               sm_config.com_port, sm_config.listener_port, do_restart)
        if do_restart:
            sm_config.status = SerialMuxConfigs.SerialMuxConfig.STATUS_RUNNING
            SerialMuxConfigs.check_device(sm_config)
        else:
            sm_config.status = SerialMuxConfigs.SerialMuxConfig.STATUS_STOPPED
        # update UI
        self.ui.update_row_values(sm_config)

#============================ main ============================================

def main():
    # Create the UI
    ui = SMConfigUI()
    # Create the Model
    sm_data = SerialMuxConfigs.SerialMuxTable()
    # Create the controller
    controller = SerialMuxController(ui, sm_data)
    ui.register_controller(controller)

    # Update the UI 
    controller.refresh()

    # Run the UI main loop
    ui.run()


if __name__ == '__main__':
    main()

