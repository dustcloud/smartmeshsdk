import datetime
import time

LOG_FORMAT_TIMESTAMP = '%Y/%m/%d %H:%M:%S'

def formatMacString(mac):
    return '-'.join(["%.2x"%i for i in mac])

def formatShortMac(mac):
    return '-'.join(["%.2x"%i for i in mac[6:]])

def formatConnectionParams(connectionParams):
    if   isinstance(connectionParams,str):
        return connectionParams.replace('/','-')
    elif isinstance(connectionParams,tuple):
        return '{0}-{1}'.format(connectionParams[0].replace('.','_'),connectionParams[1])

def formatTimestamp(timestamp=None):
    if timestamp==None:
        timestamp = time.time()
    return '{0}.{1}'.format(
        time.strftime(LOG_FORMAT_TIMESTAMP,time.localtime(timestamp)),
        int((timestamp*1000)%1000)
    )
