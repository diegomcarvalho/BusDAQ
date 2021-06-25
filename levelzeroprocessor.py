# -*- coding: utf-8 -*-
# Copyright (c) 2015 Diego Carvalho <d.carvalho@ieee.org>
# All rights reserved.
#
# Redistribution and use in source and binary forms, with or without
# modification, are permitted provided that the following conditions are met:
#
# 1. Redistributions of source code must retain the above copyright notice,
#   this list of conditions and the following disclaimer.
# 2. Redistributions in binary form must reproduce the above copyright
#   notice, this list of conditions and the following disclaimer in the
#   documentation and/or other materials provided with the distribution.
# 3. Neither the name of MOB-LAB, moblab nor the names of its
#   contributors may be used to endorse or promote products derived from
#   this software without specific prior written permission.
#
# THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS IS"
# AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE
# IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE
# ARE DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT OWNER OR CONTRIBUTORS BE
# LIABLE FOR ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR
# CONSEQUENTIAL DAMAGES (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF
# SUBSTITUTE GOODS OR SERVICES; LOSS OF USE, DATA, OR PROFITS; OR BUSINESS
# INTERRUPTION) HOWEVER CAUSED AND ON ANY THEORY OF LIABILITY, WHETHER IN
# CONTRACT, STRICT LIABILITY, OR TORT (INCLUDING NEGLIGENCE OR OTHERWISE)
# ARISING IN ANY WAY OUT OF THE USE OF THIS SOFTWARE, EVEN IF ADVISED OF THE
# POSSIBILITY OF SUCH DAMAGE.
#
"""
Created on Tue Jul 21 13:45:25 2015

@author: d.carvalho@ieee.org
"""

from ConfigParser import SafeConfigParser
import sys

import StringIO as stio
import moblab.connections as cmm
import moblab.patterns as pt
import moblab.tools as t
import pandas as pd

dataPool = {}

def merge_data(name, userdata, payload):
    #(bag.name,bag.userdata,msg.payload)
    global dataPool
    
    cm = userdata.cm
    my_logger =  userdata.logger
    server = userdata.server
    deadline = userdata.deadline
    directory = userdata.directory
    writestream = userdata.writestream
    
    dataPool[server] = payload
    
    my_logger.debug('merge_data processing data stream from ' + server)

    now = t.now()
    cm.publish_datum('TIMESTAMP', str(now))

    dfList = []
    
    for key in dataPool:
        fl = stio.StringIO(dataPool[key])
        dfK = pd.read_csv(fl, dtype={'linha': str}, parse_dates=[0], 
                          dayfirst=True)
        dfK.dropna()
        # drop all info older than 10 minutes. Actually, now() == last measure
        dfK['timediff'] = dfK['dataHora'].max() - dfK['dataHora']
        dfK = dfK[dfK['timediff'] < deadline]
        dfList.append(dfK)
        
    df = pd.concat(dfList,ignore_index=True)
        
    filename = t.date_to_file_name(now,"csv")
    
    # Process data from service

#    cm.publish_datum('DATASTREAM', fstr)

    if writestream:
        df.to_csv(directory + "/" + filename)

    cm.publish_datum('AVGSPEED', str(df['velocidade'].mean()))
    cm.publish_datum('COUNT', str(df['velocidade'].count()))

    return

def main( config_file ):

    try:    
        parser = SafeConfigParser()
        parser.read(config_file)

        lzp_name = parser.get('LevelZero', 'name')
        lzp_nstreams = int(parser.get('LevelZero', 'nstreams'))
        lzp_writestream = parser.get('LevelZero', 'writestream')
        lzp_dir = parser.get('LevelZero', 'dir')
        lzp_logfile = parser.get('LevelZero', 'logfile')
        lzp_deadline = parser.get('LevelZero','deadline')

        lzp_streams = []
        for i in range(lzp_nstreams):
            server = parser.get('Stream'+str(i),'server')
            data = parser.get('Stream'+str(i),'data')
            lzp_streams.append(pt.Bag(server=server,data=data))
            
    except:
        print 'Cannot parse the config file ' + config_file + '. Exiting.'
    
    my_logger = t.get_logger(lzp_logfile)

    my_logger.info('Initiating a new process (%s,streams=%d)' % (lzp_name,
                                                         lzp_nstreams))  

    cm = cmm.CommunicationManager(lzp_name,async=False)
    
    cm.create_datum('TIMESTAMP',retain=True)
    cm.create_datum('DATASTREAM')
    cm.create_datum('AVGSPEED')
    cm.create_datum('COUNT')    

    for i in lzp_streams:
        bag = pt.Bag(cm=cm, 
                     logger=my_logger, 
                     server=i.server, 
                     directory=lzp_dir,
                     deadline=lzp_deadline,
                     writestream=lzp_writestream)
        cm.subscribe(i.server, 
                     i.data, 
                     merge_data, 
                     userdata=bag)

    with cm:

        my_logger.info('Initiating communications.')  

        cm.loop_forever()

if __name__ == '__main__':
    if len(sys.argv) != 2:
        print 'DataLogger <configuration.ini>'
        sys.exit(0)
    main(sys.argv[1])