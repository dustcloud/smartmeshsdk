#!/usr/bin/python

import os
import sys
import threading
import logging
import time
from   datetime import timedelta
import traceback

class NullLogHandler(logging.Handler):
    def emit(self, record):
        pass

class DustCli(threading.Thread):
    '''
    \brief Thread which handles CLI commands entered by the user.
    '''
    
    CMD_LEVEL_USER   = "user"
    CMD_LEVEL_SYSTEM = "system"
    CMD_LEVEL_ALL    = [
        CMD_LEVEL_USER,
        CMD_LEVEL_SYSTEM,
    ]
    
    def __init__(self,appName=None,quit_cb=None,versions=None):
    
        # store params
        self.appName         = appName
        if not self.appName:
            self.appName = sys.argv[0]                     # C:\one\two\three.py
            self.appName = os.path.basename(self.appName)  # three.py
            self.appName = self.appName.split('.')[0]      # three
        self.quit_cb         = quit_cb
        self.versions        = versions
        
        # local variables
        self.commandLock     = threading.Lock()
        self.commands        = []
        self.goOn            = True
        
        # logging
        self.log             = logging.getLogger('DustCli')
        self.log.setLevel(logging.DEBUG)
        self.log.addHandler(NullLogHandler())
        
        # initialize parent class
        threading.Thread.__init__(self)
        
        # give this thread a name
        self.name            = 'DustCli'
        
        # print banner
        print '{0} - (c) Analog Devices, Dust Networks products'.format(self.appName)
        if self.versions:
            print '  running versions:'
            length = max([len(k) for k in self.versions.keys()])
            for (k,v) in versions.items():
                while len(k)<length:
                    k += ' '
                if type(v) in [tuple,list]:
                    v = '.'.join([str(e) for e in v])
                print '    - {0}: {1}'.format(k,v)
        
        # register system commands (user commands registered by child object)
        self._registerCommand_internal(
            self.CMD_LEVEL_SYSTEM,
            'help',
            'h',
            'print this menu',
            [],
            self._handleHelp,
        )
        self._registerCommand_internal(
            self.CMD_LEVEL_SYSTEM,
            'info',
            'i',
            'information about this application',
            [],
            self._handleInfo,
        )
        self._registerCommand_internal(
            self.CMD_LEVEL_SYSTEM,
            'quit',
            'q',
            'quit this application',
            [],
            self._handleQuit,
        )
        self._registerCommand_internal(
            self.CMD_LEVEL_SYSTEM,
            'uptime',
            'ut',
            'how long this application has been running',
            [],
            self._handleUptime,
        )
        
        # start myself
        self.start()
    
    def run(self):
        
        self.startTime = time.time()
        
        try:
            while self.goOn:
                
                # CLI stops here each time a user needs to call a command
                params = raw_input('> ')
                
                # log
                self.log.debug('Following command entered:'+params)
                
                params = params.split()
                if len(params)<1:
                    continue
                
                # print usage
                if len(params)==2 and params[1]=='?':
                    if not self._printUsageFromName(params[0]):
                        if not self._printUsageFromAlias(params[0]):
                            print ' unknown command or alias \''+params[0]+'\''
                    continue

                # find this command
                found = False
                with self.commandLock:
                    for command in self.commands:
                        if command['name']==params[0] or command['alias']==params[0]:
                            found = True
                            cmdParams               = command['params']
                            cmdCallback             = command['callback']
                            cmdDontCheckParamsLenth = command['dontCheckParamsLength']
                            break
                
                # call its callback or print error message
                if found:
                    if cmdDontCheckParamsLenth or len(params[1:])==len(cmdParams):
                        cmdCallback(params[1:])
                    else:
                        if not self._printUsageFromName(params[0]):
                            self._printUsageFromAlias(params[0])
                else:
                    print ' unknown command or alias \''+params[0]+'\''
        
        except Exception as err:
            output  = []
            output += ['===== crash in thread {0} ====='.format(self.name)]
            output += ['\nerror:\n']
            output += [str(err)]
            output += ['\ncall stack:\n']
            output += [traceback.format_exc()]
            output  = '\n'.join(output)
            print output
            self.log.critical(output)
            raise
    
    #======================== public ==========================================
    
    def registerCommand(self,name,alias,description,params,callback,dontCheckParamsLength=False):
        self._registerCommand_internal(
            self.CMD_LEVEL_USER,
            name,
            alias,
            description,
            params,
            callback,
            dontCheckParamsLength,
        )
    
    #======================== private =========================================
    
    def _registerCommand_internal(self,cmdLevel,name,alias,description,params,callback,dontCheckParamsLength=False):
        
        assert cmdLevel in self.CMD_LEVEL_ALL
        assert isinstance(name,str)
        assert isinstance(alias,str)
        assert isinstance(description,str)
        assert isinstance(params,list)
        for p in params:
            assert isinstance(p,str)
        assert callable(callback)
        assert dontCheckParamsLength in [True,False]
        
        if self._doesCommandExist(name):
            raise SystemError("command {0} already exists".format(name))
        
        with self.commandLock:
            self.commands.append(
                {
                    'cmdLevel':                cmdLevel,
                    'name':                    name,
                    'alias':                   alias,
                    'description':             description,
                    'params':                  params,
                    'callback':                callback,
                    'dontCheckParamsLength':   dontCheckParamsLength,
                }
            )
    
    def _printUsageFromName(self,commandname):
        return self._printUsage(commandname,'name')
    
    def _printUsageFromAlias(self,commandalias):
        return self._printUsage(commandalias,'alias')
    
    def _printUsage(self,name,paramType):
        
        usageString = None
        
        with self.commandLock:
            for command in self.commands:
                if command[paramType]==name:
                    usageString  = []
                    usageString += ['usage: {0}'.format(name)]
                    usageString += [" <{0}>".format(p) for p in command['params']]
                    usageString  = ''.join(usageString)
        
        if usageString:
            print usageString
            return True
        else:
            return False
    
    def _doesCommandExist(self,cmdName):
    
        returnVal = False
        
        with self.commandLock:
            for cmd in self.commands:
                if cmd['name']==cmdName:
                    returnVal = True
        
        return returnVal
    
    #=== command handlers (system commands only, a child object creates more)
    
    def _handleHelp(self,params):
        output  = []
        output += ['Available commands:']
        
        with self.commandLock:
            for command in self.commands:
                output += [' - {0} ({1}): {2}'.format(
                    command['name'],
                    command['alias'],
                    command['description']
                )]
        
        print '\n'.join(output)
    
    def _handleInfo(self,params):
        output  = []
        output += ['This is application "{0}".'.format(self.appName)]
        output += ['Current time is "{0}".'.format(time.ctime())]
        output += ['']
        output += ['{0} threads running:'.format(threading.activeCount())]
        threadNames = [t.getName() for t in threading.enumerate()]
        threadNames.sort()
        for t in threadNames:
            output += ['- {0}'.format(t)]
        output += ['This is thread {0}.'.format(threading.currentThread().getName())]
        
        print '\n'.join(output)
    
    def _handleQuit(self,params):
        
        # call the quit callback
        if self.quit_cb:
            self.quit_cb()
        
        # kill this thread
        self.goOn = False
    
    def _handleUptime(self,params):
        
        upTime = timedelta(seconds=time.time()-self.startTime)
        
        print 'Running since {0} ({1} ago)'.format(
            time.strftime("%m/%d/%Y %H:%M:%S",time.localtime(self.startTime)),
            upTime,
        )
    
    #======================== helpers =========================================
    
###############################################################################

if __name__=='__main__':

    def quitCallback():
        print "quitting!"

    def echoCallback(params):
        print "echo {0}!".format(params[0])
        
    cli = DustCli(
        "DustCli App",
        quitCallback,
        versions = {
            'shortname':                  (1,2,3,4),
            'averagelengthname':          '1.2.3.4',
            'someothertoolwithalongname': [1,2,3,4],
        }
    )
    cli.registerCommand(
        'echo',
        'e',
        'echoes the first param',
        ['string to echo'],
        echoCallback,
    )