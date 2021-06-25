#!/opt/local/bin/python
# -*- coding: utf-8 -*-
"""
Created on Thu Jul 23 23:30:32 2015

@author: carvalho
"""

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
# 3. Neither the name of mosquitto nor the names of its
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

@author: carvalho
"""




import tkinter as tk
import sys
import moblab.connections as cmm
import moblab.patterns as pt
def create_tk_simple_table(frame, name, table_info, cm ):
    """ create_tk_simple_table
        table_info is a list with Bags
        Bag(text,srv,short_topic,func)
            text - Row label
            srv - info provider
            short_topic - shared variable
            func - call back
    """
    tk.Label(frame, text=name, bg='blue', fg='white').pack(fill=tk.X)
    f = tk.Frame(frame, relief=tk.RIDGE)

    row = 0
    for i in table_info:
        l0 = tk.Label(f, text=i.text, justify=tk.LEFT, anchor=tk.W, bd=2)
        l0.grid(row=row, column=0, sticky=tk.W)
        l1 = tk.Label(f, text='NOLINK', justify=tk.RIGHT, anchor=tk.NE)
        l1.grid(row=row, column=1, sticky=tk.E)
        cm.subscribe(i.srv, i.short_topic, i.func, userdata=l1)
        row = row + 1
    f.pack()


def on_message(name, userlabel, payload):

    if name == 'TIMESTAMP':
        strtext = payload
    elif name == 'AVGSPEED':
        strtext = payload + ' km/h'
    elif name == 'COUNT':
        strtext = payload + ' vehicles'
    else:
        strtext = 'UNKNOWN'

    userlabel.configure(text=strtext)

    return


def on_button():
    sys.exit(0)


def main():

    cm = cmm.CommunicationManager('BORG')
    win = tk.Tk()
#    win.option_add("*Font", 'Helvetia')

    # Bag(text,srv,short_topic,func)
    w_list = []
    w_list.append(pt.Bag(text='Bus Time stamp    :',
                         srv='RioBusDataLogger',
                         short_topic='TIMESTAMP',
                         func=on_message))
    w_list.append(pt.Bag(text='Bus Average Speed :',
                         srv='RioBusDataLogger',
                         short_topic='AVGSPEED',
                         func=on_message))
    w_list.append(pt.Bag(text='Bus Vehicle count :',
                         srv='RioBusDataLogger',
                         short_topic='COUNT',
                         func=on_message))

    w_list.append(pt.Bag(text='Brt Time stamp    :',
                         srv='RioBrtDataLogger',
                         short_topic='TIMESTAMP',
                         func=on_message))
    w_list.append(pt.Bag(text='Brt Average Speed :',
                         srv='RioBrtDataLogger',
                         short_topic='AVGSPEED',
                         func=on_message))
    w_list.append(pt.Bag(text='Brt Vehicle count :',
                         srv='RioBrtDataLogger',
                         short_topic='COUNT',
                         func=on_message))

    w_list.append(pt.Bag(text='LZ Time stamp    :',
                         srv='LevelZeroProcessor',
                         short_topic='TIMESTAMP',
                         func=on_message))
    w_list.append(pt.Bag(text='Lz Average Speed :',
                         srv='LevelZeroProcessor',
                         short_topic='AVGSPEED',
                         func=on_message))
    w_list.append(pt.Bag(text='Lz Vehicle count :',
                         srv='LevelZeroProcessor',
                         short_topic='COUNT',
                         func=on_message))

    f = tk.Frame(win)
    create_tk_simple_table(f, 'Data Logger', w_list, cm)

    b1 = tk.Button(win, text='Exit')
    f.pack()
    b1.pack()
    b1.configure(command=on_button)

    with cm:
        cm.start()
        win.mainloop()

    return


if __name__ == '__main__':
    main()
