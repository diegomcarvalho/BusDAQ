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

from configparser import SafeConfigParser
import logging.handlers
import sys
import time
import io

import moblab.connections as cmm
import moblab.tools as t
import pandas as pd
import requests as rq
import requests.exceptions as rqe


def main(config_file):

    try:
        parser = SafeConfigParser()
        parser.read(config_file)

        data_logger_name = parser.get('Logger', 'name')
        data_logger_url = parser.get('Logger', 'url')
        data_logger_directory = parser.get('Logger', 'dir')
        data_logger_sleep = float(parser.get('Logger', 'sleeptime'))
        data_logger_logfile = parser.get('Logger', 'logfile')
    except:
        print(f'Cannot parse the config file {config_file}. Exiting.')

    my_logger = t.get_logger(data_logger_logfile)

    my_logger.info('Initiating a new process (%s,%s)' % (data_logger_name,
                                                         data_logger_url))

    cm = cmm.CommunicationManager(data_logger_name)

    cm.create_datum('TIMESTAMP', retain=True)
    cm.create_datum('DATASTREAM')
    cm.create_datum('AVGSPEED')
    cm.create_datum('COUNT')

    with cm:

        my_logger.info('Initiating communications.')

        cm.start()

        while True:

            now = t.now()
            filename = t.date_to_file_name(now, "csv")

            try:
                r = rq.get(data_logger_url, timeout=10.0)
                r.close()
                r.raise_for_status()
            except rqe.ConnectionError as rqes:
                my_logger.error('Connection Error - URL fetching error')
                my_logger.error(rqes)
            except rqe.HTTPError as rqes:
                my_logger.error('HTTPError - invalid HTTP response')
                my_logger.error(rqes)
            except rqe.Timeout as rqes:
                my_logger.error('Timeout - the server timedout')
                my_logger.error(rqes)
            except rqe.TooManyRedirects as rqes:
                my_logger.error('TooManyRedirects - http_server error config')
                my_logger.error(rqes)
            except:
                e = sys.exc_info()[0]
                my_logger.error('URL fetching error')
                my_logger.error(e)
            else:
                fstr = r.content
                fl = io.StringIO(fstr.decode('ascii'))
                df = pd.read_csv(fl)

                my_logger.debug('cm.publish_datum TIMESTAMP')
                cm.publish_datum('TIMESTAMP', str(now))
                cm.publish_datum('DATASTREAM', fstr)

                df.to_csv(data_logger_directory + "/" + filename)

                cm.publish_datum('AVGSPEED', str(df['velocidade'].mean()))
                cm.publish_datum('COUNT', str(df['velocidade'].count()))

            time.sleep(data_logger_sleep)


if __name__ == '__main__':
    if len(sys.argv) != 2:
        print('DataLogger <configuration.ini>')
        sys.exit(0)
    main(sys.argv[1])
