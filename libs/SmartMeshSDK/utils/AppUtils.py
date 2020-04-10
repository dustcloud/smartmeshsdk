#!/usr/bin/python

import os
import re
import logging.config
import inspect
import threading
import traceback

#============================ logging =========================================

def filenameCallingModule():
    # fine filename of calling module
    frame,filename,line_number,function_name,lines,index=\
        inspect.getouterframes(inspect.currentframe())[2]
    
    filename = os.path.split(filename)[1]
    filename = filename.split('.')[0]
    
    return filename
    
def setupModuleLogging():
    
    # get the filename of the calling module
    filename = filenameCallingModule()
    
    # create logger with name that filename
    log = logging.getLogger(filename)
    log.setLevel(logging.CRITICAL)
    
    return log

def configureLoggingNoFile(logfilename=None,debugmodules=[]):
    
    #=== create formatter
    
    formatter = logging.Formatter("%(asctime)s [%(name)s:%(levelname)s] %(message)s")
    
    #=== create handlers
    
    # determine the log filename
    if not logfilename:
        logfilename = '{0}.log'.format(filenameCallingModule())
    
    # create a log handler which write to a file
    fileHandler = logging.handlers.RotatingFileHandler(
        logfilename,
        mode            = 'a',
        backupCount     = 5,
        maxBytes        = 2*1024*1024,
    )
    fileHandler.setFormatter(formatter)
    fileHandler.setLevel(logging.INFO)
    
    # create a log handler which print to console
    consoleHandler = logging.StreamHandler()
    consoleHandler.setFormatter(formatter)
    consoleHandler.setLevel(logging.ERROR)
    
    # create a log handler which print to console
    consoleHandler2 = logging.StreamHandler()
    consoleHandler2.setFormatter(logging.Formatter("%(asctime)s %(message)s", "%H:%M:%S"))
    consoleHandler2.setLevel(logging.DEBUG)
    
    #=== associated handlers with loggers
    
    loggerNames = list(logging.Logger.manager.loggerDict.keys())
    
    for n in loggerNames:
        temp = logging.getLogger(n)
        temp.setLevel(logging.INFO)
        temp.addHandler(fileHandler)
        temp.addHandler(consoleHandler)
    
    for n in debugmodules:
        temp = logging.getLogger(n)
        temp.setLevel(logging.DEBUG)
        temp.addHandler(consoleHandler2)

def configureLogging():
    
    # compute the log filename
    fullpath       = inspect.stack()[1][1]
    filename       = (os.path.split(fullpath)[-1]).split('.')[0]
    logfilename    = '{0}.log'.format(filename)
    
    # find the log configuration file, if any
    logconf = None
    for p in [
            os.path.join('.',  'logging.conf'),
            os.path.join('..', 'logging.conf'),
            os.path.join('app','logging.conf'),
        ]:
        if os.path.exists(p):
            logconf = p
            break
    
    # start logging
    if logconf:
        logging.config.fileConfig(
            fname      = logconf,
            defaults   = {
                'logfilename': logfilename,
            }
        )
    else:
        print("WARNING: no log configuration file could be found.")


#============================ configuration ===================================

class AppConfig(object):
    '''
    \brief A singleton which contains some configuration, typically for an
        application.
    '''
    
    #===== singleton start
    _instance = None
    _init     = False
    def __new__(cls, *args, **kwargs):
        if not cls._instance:
            cls._instance = super(AppConfig, cls).__new__(cls, *args, **kwargs)
        return cls._instance
    #===== singleton stop
    
    def __init__(self):
        
        #===== singleton start
        if self._init:
            return
        self._init = True
        #===== singleton stop
        
        # store params
        self.dataLock   = threading.RLock()
        self.config     = {}
    
    def get(self,*args):
        with self.dataLock:
            if   len(args)==1:
                return self.config.get(args[0])
            elif len(args)==2:
                return self.config.get(args[0],args[1])
            else:
                raise SystemError()
    
    def set(self,name,value):
        with self.dataLock:
            self.config[name] = value
    
    def readFile(self,filename):
        try:
            with open(filename,'r') as f:
                for line in f:
                    line = line.strip()
                    
                    # comments
                    if line.startswith('#'):
                        continue
                    
                    # configuration
                    m = re.search('(\S+)\s*=\s*(\S+)',line)
                    if m:
                        name   = m.group(1)
                        values = m.group(2).split(',')
                        values = [v.strip() for v in values]
                        
                        for i in range(len(values)):
                            # int
                            try:
                                values[i] = int(values[i])
                            except:
                                pass
                            # float
                            try:
                                values[i] = float(values[i])
                            except:
                                pass
                        
                        if len(values)==1:
                            values = values[0]
                        
                        self.set(name,values)
        except IOError:
            # could not open/read file, that's OK
            pass
