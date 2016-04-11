#!/usr/bin/python

#============================ adjust path =====================================

import sys
import os
if __name__ == "__main__":
    here = sys.path[0]
    sys.path.insert(0, os.path.join(here, '..', '..','libs'))
    sys.path.insert(0, os.path.join(here, '..', '..','external_libs'))

#============================ imports =========================================

import time
import threading
import traceback
import pdb

from SmartMeshSDK.IpMoteConnector      import IpMoteConnector
from SmartMeshSDK.ApiException         import APIError, \
                                              ConnectionError

from dustCli                           import DustCli
from SmartMeshSDK                      import sdk_version

#============================ defines =========================================

#============================ globals =========================================

connector     = None
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

class RangeTester(object):

    def __init__(self,connector):

        # store params
        self.connector              = connector
        self.stationId              = 26
        self.goOn                   = True
        self.stats                  = [""]*16              # a list of statistic per channel



    #======================== public ==========================================

    def start(self):

        # set the current channel to default
        cc = 0

        # loop to the infinite and beyond
        while(self.goOn):
            # current channel
            cc = cc % 16

            # channel mask
            cm = 0x1<<cc

            # listen for packets
            resp = self._readPackets(cm)
            radioRxDone = False

            while not radioRxDone:
                time.sleep(1)

                # try to get last statistics
                try:
                    last_stats = self._getStats()
                except APIError:
                    continue

                radioRxDone = True

            # save stats
            self._saveStats(cc, last_stats)

            # print stats
            self._printStats(cc)

            # next channel
            cc = cc+4

    def disconnect(self):
        try:
            self.connector.disconnect()
        except:
            # can happen if connector not connected
            pass

    #======================== private =========================================

    #=== actions

    def _readPackets(self, channel, duration=17):
        """
        Call the API to start listening for incomming packets
        """

        channel_hex = self._num_to_list(channel,2)
        connector.dn_testRadioRx(
                channelMask     = channel_hex,      # channel
                time            = duration,         # reading time
                stationId       = self.stationId    # stationId
            )

    def _getStats(self):
        """
        Get the latest radiotest statistics
        """
        return connector.dn_getParameter_testRadioRxStats()

    def _saveStats(self, channel, last_stats):
        """
        Populate the statistics list
        """
        self.stats[channel] = str(last_stats[1])

    def _printStats(self, channel):
        """
        Refresh page and print the statistics
        """
        print "Channel\tRxOK"
        for i in range(0,4):
            if i*4 == channel:
                star = "*"
            else:
                star = " "
            print "%s %s\t%s" % (star, i*4, self.stats[i*4])

    def _num_to_list(self,num,length):
        output = []
        for l in range(length):
            output = [(num>>8*l)&0xff]+output
        return output

#============================ CLI handlers ====================================

def quit_clicb():
    global connector

    try:
        connector.disconnect()
    except:
        # can happen if connector not created
        pass

    print "bye bye."
    time.sleep(0.3)

def connect_clicb(params):
    global connector
    global range_tester

    # filter params
    port = params[0]

    # create a coonnector
    connector = IpMoteConnector.IpMoteConnector()

    # connect to the manager
    try:
        connector.connect({
            'port': port,
        })
    except ConnectionError as err:
        printExcAndQuit(err)

    # create main object
    range_tester = RangeTester(connector)

def start_clicb(params):
    global range_tester
    range_tester.start()

#============================ main ============================================

def main():

    # create CLI interface
    cli = DustCli.DustCli("BroadcastLeds Application",quit_clicb)
    cli.registerCommand(
        name                      = 'connect',
        alias                     = 'c',
        description               = 'connect to a serial port',
        params                    = ['portname'],
        callback                  = connect_clicb,
        dontCheckParamsLength     = False,
    )
    cli.registerCommand(
        name                      = 'start',
        alias                     = 's',
        description               = 'start the range test',
        params                    = [],
        callback                  = start_clicb,
        dontCheckParamsLength     = False,
    )

    # print SmartMesh SDK version
    print 'SmartMesh SDK {0}'.format('.'.join([str(i) for i in sdk_version.VERSION]))
    cli.start()

if __name__=='__main__':
    main()
