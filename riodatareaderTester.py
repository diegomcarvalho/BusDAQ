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

import moblab.connections as cmm

counter = 0
cm = cmm.CommunicationManager("RioBrtDataTesterReader", async=False)

def call_back(name, userdata, payload ):
    global counter
    global cm
    
    print "Service update from:" + userdata + " Value for " + name + " is " + payload
    counter = counter + 1
        

def main():

    global cm
    
    cm.subscribe("RioBrtDataLogger", "TIMESTAMP", call_back, "RioBrtDataLogger")
    cm.subscribe("RioBrtDataLogger", "AVGSPEED", call_back, "RioBrtDataLogger")
    cm.subscribe("RioBrtDataLogger", "COUNT", call_back, "RioBrtDataLogger")

    cm.subscribe("RioBusDataLogger", "TIMESTAMP", call_back, "RioBusDataLogger")
    cm.subscribe("RioBusDataLogger", "AVGSPEED", call_back, "RioBusDataLogger")
    cm.subscribe("RioBusDataLogger", "COUNT", call_back, "RioBusDataLogger")

    with cm:

        cm.loop_forever()

if __name__ == "__main__":
    main()
