#!/usr/bin/python

import sys
import threading
import binascii
import time
import logging

from pydispatch import dispatcher

from dustCli import DustCli

from SmartMeshSDK import ApiException

class GatewayCli(DustCli.DustCli):
    '''
    \brief Thread which handles CLI commands entered by the user.
    '''
    
    DEFAULT_SERIALMUX_HOST = '127.0.0.1'
    DEFAULT_SERIALMUX_PORT = 9900
    
    def __init__(self,appName,nsnap):
        
        # record parameters
        self.appName  = appName
        self.nsnap    = nsnap
        
        # instanciate parent class
        DustCli.DustCli.__init__(self,self.appName)
        self.name     = 'GatewayCli'
        
        # register commands
        self.registerCommand('connect',
                             'c',
                             'connect to the manager',
                             ['serial <serialport>\nserialmux <hostip> <tcpport>'],
                             self._handleConnect,
                             dontCheckParamsLength=True)
        self.registerCommand('disconnect',
                             'd',
                             'disconnect from the manager',
                             ['<partial_mac> or \'*\''],
                             self._handleDisconnect)
        self.registerCommand('snap',
                             'sn',
                             'gets a snapshot from a subset of connected managers',
                             ['<partial_mac> or \'*\''],
                             self._handleSnap)
        self.registerCommand('stats',
                             'st',
                             'display statistics from a subset of connected managers',
                             ['<partial_mac> or \'*\''],
                             self._handleStats)
    
    #======================== private =========================================
    
    #=== command handlers
    
    def _handleConnect(self,params):
        
        if len(params)==0:
            self.nsnap.connectMux(self.DEFAULT_SERIALMUX_HOST,
                                  self.DEFAULT_SERIALMUX_PORT)
            
        else:
            connectType = params[0]
            
            if   connectType in ['serial','s']:
                
                if len(params)!=2:
                    self._printUsageFromName('connect')
                    return
                
                serialport  = params[1]
                
                try:
                    self.nsnap.connectSerial(serialport)
                except ApiException.ConnectionError as err:
                    print err
                
            elif connectType in ['serialmux','mux','m']:
                
                if len(params)!=3:
                    self._printUsageFromName('connect')
                    return
                
                hostip      = params[1]
                try:
                    tcpport     = int(params[2])
                except TypeError:
                    print "tcpport should be an int"
                
                try:
                    self.nsnap.connectMux(hostip,tcpport)
                except ApiException.ConnectionError as err:
                    print err
            
            else:
                self._printUsageFromName('connect')
                return
    
    def _handleDisconnect(self,params):
        
        # usage
        if len(params)!=1:
            self._printUsageFromName('disconnect')
            return
        
        macToMatch = params[0]
        
        macsDisconnected = self.nsnap.disconnect(macToMatch)
        
        output  = []
        output += ["disconnected {0} manager(s)".format(len(macsDisconnected))]
        for mac in macsDisconnected:
            output += [' - {0}'.format(mac)]
        print '\n'.join(output)
    
    def _handleSnap(self,params):
        
        # usage
        if len(params)!=1:
            self._printUsageFromName('stats')
            return
        
        macToMatch = params[0]
        
        # perform snapshots on all matching MACs
        macsSnapped = self.nsnap.snap(macToMatch)
        
        output  = []
        output += ["\nsnasphot performed on {0} manager(s)".format(len(macsSnapped))]
        for mac in macsSnapped:
            output += [' - {0}'.format(mac)]
        print '\n'.join(output)
    
    def _handleStats(self,params):
        
        # usage
        if len(params)!=1:
            self._printUsageFromName('stats')
            return
        
        allStats = dispatcher.send(
            signal       = 'getStats',
            data         = None,
        )
        
        output  = []
        for moduleStats in allStats:
            module = moduleStats[0].im_self.name
            stats  = moduleStats[1]
            
            output += [" - {0}:".format(module)]
            keys = stats.keys()
            keys.sort()
            for k in keys:
                output += ["       - {0:>20}: {1}".format(k,stats[k])]
        
        print '\n'.join(output)
        
    #======================== helpers =========================================
    