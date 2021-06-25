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

import os
import logging
import urllib.parse as urlparse
import paho.mqtt.client as mqtt

from .patterns import Bag, Borg

#
# Information Directory
#
#
# CM_BASE_PROC = "MOBLAB/PROC/"
#    ProcessServer is in charge of this sub-tree and it creates a leaf for every
#    process in the system.
# CM_BASE_STAT = "MOBLAB/STAT/"
#    Every process creates a leaf (with the process name) and publishes its
#    status.
# CM_BASE_DATA = "MOBLAB/DATA/"
#    Branch reserved for all published data
# CM_BASE_CMD = "MOBLAB/CMD/"
#    Branch reserved for all commands
CM_BASE_TREE = "MOBLAB/"
CM_BASE_PROC = "/PROC/"
CM_BASE_STAT = "/STAT/"
CM_BASE_DATA = "/DATA/"
CM_BASE_CMD = "/CMD/"

#
# Connection Manager States
#
CM_ST_NOLINK = "NOLINK"
CM_ST_INIT = "INITIALIZING"
CM_ST_EXIT = "EXITING"
CM_ST_ONLINE = "ONLINE"


#
# Private support functions
#
def _proc_str_add(a, b):
    return CM_BASE_TREE + a + CM_BASE_PROC + b


def _stat_str_add(a, b):
    return CM_BASE_TREE + a + CM_BASE_STAT + b


def _data_str_add(a, b):
    return CM_BASE_TREE + a + CM_BASE_DATA + b


def _cmd_str_add(a, b):
    return CM_BASE_TREE + a + CM_BASE_CMD + b


def _get_broker():
    url_str = os.environ.get('MOBLAB_MQTT_SERVER_URL',
                             'mqtt://pppro.cefet-rj.br:8080')
    return urlparse.urlparse(url_str)


class CommunicationManager(Borg):
    """ Communication Manager Class
    """

    def __init__(self, clientid, async_mode=True):
        """ __init__(clientid, async_mode)
        clientid - process name on the communication tree. It should be unique
        async_mode - select if the CM runs multithreaded (True) or with user pooling
        """

        Borg.__init__(self)
        self._clientid = clientid
        self._async_mode = async_mode
        self._commands = {}
        self._topics = {}
        self._mqttc = mqtt.Client(clientid)
        self._mqttc.on_connect = self._on_connect
        self._mqttc.on_message = self._on_message
        self._url = _get_broker()
        if self._url.username:
            self._mqttc.username_pw_set(self._url.username, self._url.password)

        logging.info('Communication Manager __init__(%s,%r)' %
                     (clientid, async_mode))
        return

    def __enter__(self):
        """ ___enter___() - Communication Manager
        Connect with MQTT server
        """
        if self._async_mode:
            self._mqttc.connect_async(self._url.hostname, self._url.port)
        else:
            self._mqttc.connect(self._url.hostname, self._url.port)
        return self

    def __exit__(self, typeExc, value, traceback):
        """ ___exit___() - Communication Manager
        """
        if self._async_mode:
            self._mqttc.loop_stop()

        self._mqttc.disconnect()

        return

    def _on_connect(self, mqttc, obj, flags, rc):
        """ __on_connect() - Communication Manager
        """
        if self._commands:
            for key, bag in self._commands.items():
                self._mqttc.subscribe(bag.topic)
                logging.debug(
                    'CommunicationManager _on_connect command (%s)' % (key))

        return

    def _on_message(self, mqttc, obj, msg):
        """ _on_messages() - Communication Manager
        """
        if msg.topic in self._commands:
            bag = self._commands[msg.topic]
            bag.function(bag.name, bag.userdata, msg.payload)
        return

    def create_datum(self, name, qos=0, retain=False):
        topic = _data_str_add(self._clientid, name)
        self._topics[name] = Bag(topic=topic, qos=qos, retain=retain)
        return

    def subscribe(self, server, name, func, userdata=None, qos=0):
        t = _data_str_add(server, name)
        dat = Bag(topic=(t, qos), name=name, function=func, userdata=userdata)
        self._commands[t] = dat
        self._mqttc.subscribe(dat.topic)
        return

    def create_command(self, name, func, userdata=None, qos=0):
        t = _cmd_str_add(self._clientid, name)
        dat = Bag(topic=(t, qos), name=name, function=func, userdata=userdata)
        self._commands[t] = dat
        self._mqttc.subscribe(dat.topic)
        return

    def send_command(self, server, cmd, payload, qos=0):
        topic = _cmd_str_add(server, cmd)
        self._mqttc.publish(topic, payload, qos)
        logging.debug('CommunicationManager send_command (%s,%s)' %
                      (server, cmd))
        return

    def publish_datum(self, name, payload):
        bag = self._topics[name]
        self._mqttc.publish(bag.topic, payload, qos=bag.qos, retain=bag.retain)
        return

    def start(self):
        self._mqttc.loop_start()
        return

    def loop(self):
        self._mqttc.loop()
        return

    def loop_forever(self):
        self._mqttc.loop_forever()
        return
