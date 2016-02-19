#!/usr/bin/python

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
    ]
)
if not goodToGo:
    print "Your installation does not allow this application to run:\n"
    print reason
    raw_input("Press any button to exit")
    sys.exit(1)

#============================ imports =========================================

import re
import traceback
import time
import json
import random

import plotly

from   SmartMeshSDK.utils import FormatUtils

#============================ logging =========================================

#============================ defines =========================================

#============================ globals =========================================

#============================ helpers =========================================

def currentUtcTime():
    return time.strftime("%a, %d %b %Y %H:%M:%S UTC", time.gmtime())

#============================ body ============================================

class TimelapseAnalyzer(object):
    
    def __init__(self,filename):
        self._get_data(filename)
        self._get_motes()
        self._get_allMoteInfo()
        self._print_allMoteInfo()
        self._get_topology()
        self._print_topology()
    
    def _get_data(self,filename):
        '''
        Read the data from the activity logfile.
        
        \post self.data is populated.
        '''
        self.data  = []
        with open(filename,'r') as f:
            for line in f:
                m = re.match('\[([a-zA-Z0-9\- :,]+)\]\s*\[([a-zA-Z]+)\]\s*(.*)', line)
                if m:
                    temp               = m.group(1)
                    ts                 = time.mktime(time.strptime(temp, "%a, %d %b %Y %H:%M:%S UTC"))
                    notifName          = m.group(2)
                    temp               = m.group(3).strip()
                    if temp:
                        notifParams    = json.loads(temp)
                    else:
                        notifParams    = None
                    self.data         += [
                        {
                            'ts':           ts,
                            'notifName':    notifName,
                            'notifParams':  notifParams
                        }
                    ]
                else:
                    print 'WARNING: could not match "{0}"'.format(line)
    
    def _get_motes(self):
        '''
        Retrieve the list of the motes in the network
        
        \post self.motes is populated
        '''
        self.motes = []
        
        for d in self.data:
            if not d['notifParams']:
                continue
            if 'macAddress' in d['notifParams']:
                self.motes += [d['notifParams']['macAddress']]
            if d['notifName']=='topology':
                for path in d['notifParams']:
                    if 'toMAC' in path:
                        self.motes += [path['toMAC']]
                    if 'fromMAC' in path:
                        self.motes += [path['fromMAC']]
        self.motes = [tuple(mac) for mac in self.motes]
        self.motes = list(set(self.motes))
        self.motes = [list(mac) for mac in self.motes]
    
    def _get_allMoteInfo(self):
        '''
        Retrieve the number of data notifications for each mote.
        
        \post self.numData is populated
        '''
        self.allMoteInfo = {}
        
        # moteConfig and moteInfo
        for d in self.data:
            if d['notifName'] in ['moteConfig','moteInfo']:
                for i in d['notifParams']:
                    mac  = tuple(i['macAddress'])
                    if mac not in self.allMoteInfo:
                        self.allMoteInfo[mac] = {}
                    self.allMoteInfo[mac].update(i)
        
        # numData
        for d in self.data:
            if d['notifName']=='notifData':
                mac = tuple(d['notifParams']['macAddress'])
                if mac not in self.allMoteInfo:
                    self.allMoteInfo[mac]            = {}
                if 'numData' not in self.allMoteInfo[mac]:
                    self.allMoteInfo[mac]['numData'] = 0
                self.allMoteInfo[mac]['numData'] += 1
    
    def _print_allMoteInfo(self):
        
        columnNames = []
        for (mac,v) in self.allMoteInfo.items():
            for n in v:
                if n in ['macAddress','RC','reserved']:
                    continue
                columnNames += [n]
        columnNames = sorted(list(set(columnNames)))
        
        data_matrix     = []
        data_matrix    += [['mac']+columnNames]
        for (mac,v) in self.allMoteInfo.items():
            thisline    = []
            thisline   += [FormatUtils.formatMacString(mac)]
            for n in columnNames:
                if n in v:
                    thisline += [v[n]]
                else:
                    thisline += ['']
            data_matrix += [thisline]
        
        table = plotly.tools.FigureFactory.create_table(data_matrix)
        
        plotly.offline.plot(table,filename='allMoteInfo.html',)
    
    def _get_topology(self):
        
        # mote positions
        self.pos   = {}
        with open('MotePositions.txt','r') as f:
           for line in f:
                if line.startswith('#'):
                    continue
                m = re.search('\s*([a-fA-F0-9\-]+)\s+([0-9]+)\s+([0-9]+)', line)
                if m:
                   mac  = tuple([int(b,16) for b in m.group(1).split('-')])
                   assert len(mac)==8
                   x    = int(m.group(2))
                   y    = int(m.group(3))
                   self.pos[mac] = (x,y)
                else:
                   print 'WARNING: could not match "{0}"'.format(line)
        
        # links
        self.links = []
        for d in self.data:
            if d['notifName']=='topology':
                self.links = d['notifParams']
    
    def _print_topology(self):
        
        # links
        links_x         = []
        links_y         = []
        for l in self.links:
            links_x += [
                self.pos[tuple(l['fromMAC'])][0],
                self.pos[tuple(l['toMAC'])][0],
                None,
            ]
            links_y += [
                self.pos[tuple(l['fromMAC'])][1],
                self.pos[tuple(l['toMAC'])][1],
                None,
            ]
        links_trace = plotly.graph_objs.Scatter(
            x           = links_x,
            y           = links_y,
            line        = plotly.graph_objs.Line(width=0.5,color='#888'),
            hoverinfo   = 'none',
            mode        = 'lines',
        )
        
        # annotations
        annotations = []
        for l in self.links:
            x0 = float(self.pos[tuple(l['fromMAC'])][0])
            y0 = float(self.pos[tuple(l['fromMAC'])][1])
            x1 = float(self.pos[tuple(l['toMAC'])][0])
            y1 = float(self.pos[tuple(l['toMAC'])][1])
            annotations+= [
                {
                    'x'           : (x0+x1)/2,
                    'y'           : (y0+y1)/2,
                    'xref'        : 'x',
                    'yref'        : 'y',
                    'text'        : '{0}%'.format(l['quality']),
                    'showarrow'   : False,
                    'ax'          : 0,
                    'ay'          : 0,
                }
            ]
        
        # motes
        motes_x         = [pos[0] for (mac,pos) in self.pos.items()]
        motes_y         = [pos[1] for (mac,pos) in self.pos.items()]
        motes_text      = []
        mote_weight     = []
        for (mac,pos) in self.pos.items():
            output      = []
            output     += ['{0}:'.format(FormatUtils.formatMacString(mac))]
            for (k,v) in self.allMoteInfo[mac].items():
                if k in ['macAddress','RC','reserved']:
                    continue
                output += ['{0}: {1}'.format(k,v)]
            output      = '<br>'.join(output)
            motes_text += [output]
            if 'numData' in self.allMoteInfo[mac]:
                mote_weight += [self.allMoteInfo[mac]['numData']]
            else:
                mote_weight += [0]
        motes_trace = plotly.graph_objs.Scatter(
            x                     = motes_x, 
            y                     = motes_y, 
            text                  = motes_text,
            mode                  = 'markers', 
            hoverinfo             = 'text',
            marker                = plotly.graph_objs.Marker(
                showscale         = True,
                colorscale        = 'Bluered',
                reversescale      = 'Picnic',
                color             = mote_weight, 
                size              = 10,
                colorbar          = dict(
                    thickness     = 15,
                    title         = 'Number Data Packet Received',
                    xanchor       = 'left',
                    titleside     = 'right'
                ),
                line              = dict(
                    width         = 2,
                )
            )
        )
        
        # plot
        fig = plotly.graph_objs.Figure(
            data                  = plotly.graph_objs.Data([links_trace, motes_trace]),
            layout                = plotly.graph_objs.Layout(
                title             = '',
                titlefont         = dict(size=16),
                showlegend        = False, 
                width             = 650,
                height            = 650,
                hovermode         = 'closest',
                margin            = dict(b=20,l=5,r=5,t=40),
                annotations       = annotations,
                xaxis             = plotly.graph_objs.XAxis(
                    showgrid      = False,
                    zeroline      = False,
                    showticklabels= False,
                ),
                yaxis             = plotly.graph_objs.YAxis(
                    showgrid      = False,
                    zeroline      = False,
                    showticklabels= False,
                )
            )
        )
        
        plotly.offline.plot(fig,filename='topology.html',)

#============================ main ============================================

def main():
    try:
        TimelapseAnalyzer('NetworkActivity.txt')
    except Exception as err:
        output  = []
        output += ["==============================================================="]
        output += [currentUtcTime()]
        output += [""]
        output += ["CRASH!!"]
        output += [""]
        output += ["=== exception type ==="]
        output += [str(type(err))]
        output += [""]
        output += ["=== traceback ==="]
        output += [traceback.format_exc()]
        output  = '\n'.join(output)
        print output
        raw_input('Press Enter to close.')
    else:
        raw_input('Script ended normally.\nPress Enter to close.')

if __name__ == '__main__':
    main()
