import re
import time
import traceback

EVENT_TEMPERATURE   = 'temperature'
EVENT_STARTAPP      = 'start_app'
EVENT_STOPAPP       = 'stop_app'
EVENT_CONNECTED     = 'connected'
EVENT_DISCONNECTED  = 'disconnected'
EVENT_ALL           = [
    EVENT_TEMPERATURE,
    EVENT_STARTAPP,
    EVENT_STOPAPP,
    EVENT_CONNECTED,
    EVENT_DISCONNECTED
]

class Printer(object):
    _instance = None
    _init     = False
    def __new__(cls, *args, **kwargs):
        if not cls._instance:
            cls._instance = super(Printer, cls).__new__(cls, *args, **kwargs)
        return cls._instance
    def __init__(self):
        # don't re-initialize an instance (needed because singleton)
        if self._init:
            return
        self._init = True
        self.f = open('statistics.txt','w')
    def printline(self,line):
        print line
        self.f.write(line)
    def __def__(self):
        self.f.close()

#============================ statistics ======================================

class Stats(object):
    def feedstat(self,stat):
        raise NotImplementedError()
    def formatheader(self):
        output  = []
        output += ['']
        output += ['']
        output += ['='*79]
        output += [self.description]
        output += ['='*79]
        output += ['']
        output  = '\n'.join(output)
        return output

class NumDataPoints(Stats):
    description = 'Number of Data Points Received'
    
    def __init__(self):
        self.numDataPoints = {}
    
    def feedstat(self,statline):
        
        if statline['eventType']!=EVENT_TEMPERATURE:
            return
        
        # count number of packets
        if statline['mac'] not in self.numDataPoints:
            self.numDataPoints[statline['mac']] = 0
        self.numDataPoints[statline['mac']] += 1
    
    def formatstat(self):
        
        # identify missing
        maxMumDataPoints = max([v for (k,v) in self.numDataPoints.items()])
        
        # format output
        output  = []
        output += [self.formatheader()]
        output += ['({0} motes)'.format(len(self.numDataPoints))]
        for (mac,num) in self.numDataPoints.items():
            if num<maxMumDataPoints:
                remark = ' ({0} missing)'.format(maxMumDataPoints-num)
            else:
                remark = ''
            output += [' - {0} : {1}{2}'.format(mac,num,remark)]
        output  = '\n'.join(output)
        return output

class MaxTimeGap(Stats):
    description = 'Maximum Time Gap Between Consecutive Data Points'
    
    def __init__(self):
        self.maxgap = {}
    
    def feedstat(self,statline):
        
        if statline['eventType']!=EVENT_TEMPERATURE:
            return
        
        mac        = statline['mac']
        timestamp  = statline['timestamp']
        
        # count number of packets
        if mac not in self.maxgap:
            self.maxgap[mac] = {
                'lasttimestamp' :   None,
                'maxgap':           None,
            }
        if self.maxgap[mac]['lasttimestamp']!=None:
            thisgap = timestamp-self.maxgap[mac]['lasttimestamp']
            if self.maxgap[mac]['maxgap']==None or thisgap>self.maxgap[mac]['maxgap']:
                self.maxgap[mac]['maxgap'] = thisgap
        
        self.maxgap[mac]['lasttimestamp'] = timestamp
    
    def formatstat(self):
        
        output  = []
        output += [self.formatheader()]
        output += ['({0} motes)'.format(len(self.maxgap))]
        for (mac,v) in self.maxgap.items():
            if v['maxgap']:
                output += [' - {0} : {1}s'.format(mac,int(v['maxgap']))]
            else:
                output += [' - {0} : {1}'.format(mac,    v['maxgap'] )]
        output  = '\n'.join(output)
        return output

class BurstSpread(Stats):
    description      = 'Maximum time spread among measurements (for each burst)'
    
    MAX_BURST_SPREAD = 5.0
    
    def __init__(self):
        self.bursts = {}
    
    def calculateBurstId(self,timestamp):
        return int(self.MAX_BURST_SPREAD * round(float(timestamp)/self.MAX_BURST_SPREAD))
    
    def feedstat(self,statline):
        
        if statline['eventType']!=EVENT_TEMPERATURE:
            return
        
        timestamp = statline['timestamp']
        
        burstId   = self.calculateBurstId(timestamp)
        
        # count number of packets
        if burstId not in self.bursts:
            self.bursts[burstId] = {
                'numpoints':        0,
                'mintimestamp' :    None,
                'maxtimestamp':     None,
            }
        
        self.bursts[burstId]['numpoints'] += 1
        if self.bursts[burstId]['mintimestamp']==None or timestamp<self.bursts[burstId]['mintimestamp']:
            self.bursts[burstId]['mintimestamp'] = timestamp
        if self.bursts[burstId]['maxtimestamp']==None or timestamp>self.bursts[burstId]['maxtimestamp']:
            self.bursts[burstId]['maxtimestamp'] = timestamp
    
    def formatstat(self):
        
        # calculate spread
        for (k,v) in self.bursts.items():
            if v['mintimestamp']!=None and v['maxtimestamp']!=None:
                v['spread'] = v['maxtimestamp']-v['mintimestamp']
            else:
                v['spread'] = None
        
        output  = []
        output += [self.formatheader()]
        output += [
            '({0} bursts separated by {1:.03f}s or more)'.format(
                len(self.bursts),
                self.MAX_BURST_SPREAD
            )
        ]
        
        allts = sorted(self.bursts.keys())
        
        for ts in allts:
            b = self.bursts[ts]
            
            tsString              = time.strftime("%Y-%m-%d %H:%M:%S",time.localtime(ts))
            if b['spread']!=None:
                spreadString      = '{0:>5}ms'.format(int(1000*b['spread']))
            else:
                spreadString      = 'not enough data'
            
            output += [' - around {0} : {1} ({2} points)'.format(tsString,spreadString,b['numpoints'])]
        
        output  = '\n'.join(output)
        return output
    
#============================ main ============================================

def main():
    
    try:
    
        print 'logAnalysis - Dust Networks (c) 2014'
        
        # initialize stats
        stats = [s() for s in Stats.__subclasses__()]
        
        # parse file and fill in statistics
        with open('temperaturelog.csv','r') as f:
            for line in f:
                m = re.search('([0-9\- :]*).([0-9]{3}),([a-zA_Z _]*),([0-9a-f\-]*),([0-9.]*)',line)
                if not m:
                    print 'WARNING: following line not parsed: {0}'.format(line)
                    assert(0)
                    continue
                
                # rawline
                rawline = {}
                rawline['timestamp']       = m.group(1)
                rawline['timestampMs']     = m.group(2)
                rawline['eventType']       = m.group(3)
                rawline['mac']             = m.group(4)
                rawline['temperature']     = m.group(5)
                
                # print
                output  = []
                output += ['']
                output += ['====================']
                output += ['']
                output += ['{0:>20} : "{1}"'.format("line",line.strip())]
                output += ['']
                for (k,v) in rawline.items():
                    output += ['{0:>20} : {1}'.format(k,v)]
                output  = '\n'.join(output)
                #Printer().printline(output)
                
                # statline
                statline = {}
                statline['timestamp']         = time.mktime(time.strptime(rawline['timestamp'],"%Y-%m-%d %H:%M:%S"))
                statline['timestamp']        += int(rawline['timestampMs'])/1000.0
                statline['eventType']         = rawline['eventType']
                assert rawline['eventType'] in EVENT_ALL
                if rawline['mac']:
                    statline['mac']           = rawline['mac']
                else:
                    statline['mac']           = None
                if rawline['temperature']:
                    statline['temperature']   = float(rawline['temperature'])
                else:
                    statline['temperature']   = None
                
                # print
                output  = []
                output += ['']
                output += ['{0:>20} : {1:.03f}'.format("timestamp",statline['timestamp'])]
                output += ['{0:>20} : {1}'.format("eventType",statline['eventType'])]
                output += ['{0:>20} : {1}'.format("mac",rawline['mac'])]
                if statline['temperature']:
                    output += ['{0:>20} : {1:.02f}'.format("temperature",statline['temperature'])]
                else:
                    output += ['{0:>20} : {1}'.format("temperature",statline['temperature'])]
                output  = '\n'.join(output)
                #Printer().printline(output)
                
                # feed stat
                for stat in stats:
                    stat.feedstat(statline)
        
        # print statistics
        for stat in stats:
            Printer().printline(stat.formatstat())
        
    except Exception as err:
        print "FATAL: ({0}) {1}".format(type(err),err)
        print traceback.print_exc()
    else:
        print "\n\nScript ended normally"
    
    raw_input("\nPress enter to close.")

if __name__=="__main__":
    main()
