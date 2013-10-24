
import os
import logging.config
import inspect

def configureLogging():
    
    # compute the log filename
    fullpath       = inspect.stack()[1][1]
    filename       = (os.path.split(fullpath)[-1]).split('.')[0]
    logfilename    = '{0}.log'.format(filename)
    
    # find the log configuration file, if any
    logconf = None
    for p in [
            os.path.join('..', 'logging.conf'),
            os.path.join('bin','logging.conf'),
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
        print "WARNING: no log configuration file could be found."