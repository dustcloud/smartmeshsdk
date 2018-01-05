#!/usr/bin/python

#============================ adjust path =====================================

import sys
import os
if __name__ == "__main__":
    here = sys.path[0]
    sys.path.insert(0, os.path.join(here, '..', '..','libs'))
    sys.path.insert(0, os.path.join(here, '..', '..','external_libs'))

#============================ imports =========================================

# built-in
import time
import threading
import traceback
import pdb

# SmartMeshSDK
from SmartMeshSDK                      import sdk_version
from SmartMeshSDK.IpMoteConnector      import IpMoteConnector
from SmartMeshSDK.ApiException         import APIError, \
                                              ConnectionError

# DustCli
from dustCli                           import DustCli

#============================ defines =========================================

DFLT_DURATION = 2 # seconds

#============================ globals =========================================

range_tester  = None

#============================ helpers =========================================

def printExcAndQuit(err):

    output  = []
    output += ["="*30]
    output += ["error"]
    output += [str(err)]
    output += ["="*30]
    output += ["traceback"]
    output += [traceback.format_exc()]
    output += ["="*30]
    output += ["Script ended because of an error. Press Enter to exit."]
    output  = '\n'.join(output)

    raw_input(output)
    sys.exit(1)

#============================ objects =========================================

class RangeTester(threading.Thread):

    def __init__(self,port):

        # store params
        self.port            = port
        self.stationId       = 26
        self.goOn            = True
        self.rxOk            = [None]*4    # rxOk per channel
        
        # init the parent
        threading.Thread.__init__(self)
        self.name            = "RangeTester"
        self.start()

    #======================== public ==========================================

    def run(self):
        
        while self.goOn:
        
            try:
                # create a connector
                self.connector = IpMoteConnector.IpMoteConnector()

                # connect to the manager
                print 'connecting to {0}...'.format(self.port),
                self.connector.connect({
                    'port': self.port,
                })
                print 'done.'
                
                # set the current channel to default
                chanIdx = 0
                
                # loop to the infinite and beyond
                while self.goOn:
                    
                    # channel
                    mask     = 0x1<<chanIdx*4

                    # listen for packets
                    mask_hex = self._num_to_list(mask,2)
                    self.connector.dn_testRadioRx(
                        channelMask      = mask_hex,         # channel
                        time             = DFLT_DURATION,    # listening time
                        stationId        = self.stationId    # stationId
                    )
                    radioRxDone = False
                    
                    while self.goOn:
                        time.sleep(1)

                        # get last statistics
                        try:
                            testRadioRxStats = self.connector.dn_getParameter_testRadioRxStats()
                        except APIError:
                            continue
                        
                        break
                    
                    # save rxOk
                    self.rxOk[chanIdx] = testRadioRxStats.rxOk
                    
                    # print rxOk
                    output  = []
                    output += ['']
                    sum     = 0
                    num     = 0
                    for i in range(0,4):
                        channel = i*4
                        if i == chanIdx:
                            star = "*"
                        else:
                            star = " "
                        if self.rxOk[i]==None:
                            bar = ''
                        else:
                            num += 1
                            sum += self.rxOk[i]
                            bar = "{0}|".format(
                                '-'*(self.rxOk[i]/2),
                            )
                        output += [
                            "{0} channel={1}\t{2} {3}".format(
                                star,
                                channel,
                                bar,
                                self.rxOk[i]
                            )
                        ]
                    output += ["Total: {0} packets\t({1:.2f}%)".format(sum,float(sum)/float(num))]
                    output  = '\n'.join(output)
                    print output
                    
                    # switch to next channel
                    chanIdx = (chanIdx+1)%4

            except Exception as err:
                print err
                try:
                    self.connector.disconnect()
                except:
                    pass
                time.sleep(1)

    def close(self):
        try:
            self.connector.disconnect()
        except:
            # can happen if connector not connected
            pass
        
        self.goOn = False

    #======================== private =========================================

    def _num_to_list(self,num,length):
        output = []
        for l in range(length):
            output = [(num>>8*l)&0xff]+output
        return output

#============================ CLI handlers ====================================

def quit_clicb():
    global range_tester

    range_tester.close()

    print "bye bye."
    time.sleep(0.3)

def connect_clicb(params):
    global range_tester
    
    # filter params
    port = params[0]
    
    # create main RangeTester thread
    range_tester = RangeTester(port)

#============================ main ============================================

def main():

    # CLI interface
    cli = DustCli.DustCli(
        quit_cb  = quit_clicb,
        versions = {
            'SmartMesh SDK': sdk_version.VERSION,
        },
    )
    cli.registerCommand(
        name                      = 'connect',
        alias                     = 'c',
        description               = 'connect to a serial port',
        params                    = ['portname'],
        callback                  = connect_clicb,
        dontCheckParamsLength     = False,
    )

if __name__=='__main__':
    main()
