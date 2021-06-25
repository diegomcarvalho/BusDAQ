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

import datetime as dt
import logging.handlers

LOG_FORMAT = '%(asctime)s %(name)-12s %(levelname)-8s %(message)s'

def now():
    return dt.datetime.now()

def date_to_file_name( date, extention ):
    return dt.datetime.strftime(date, "%Y%m%d%H%M%S") + "." + extention

def file_name_to_date( name, extention ):
    return dt.datetime.strptime(name, "%Y%m%d%H%M%S" + "." + extention)

def get_logger( data_logger_logfile ):
    my_logger = logging.getLogger()
    my_logger.setLevel(logging.INFO)    
    
    formatter = logging.Formatter(LOG_FORMAT)
    
    handler = logging.handlers.RotatingFileHandler(data_logger_logfile,
                                               maxBytes=16*1024*1024,
                                               backupCount=5
                                               )
    handler.setFormatter(formatter)
    my_logger.addHandler(handler)
    
    return my_logger