#!/usr/bin/python

from class_ge50A import Ge50a
import datetime

"""Serial Configuration"""
port = '/dev/ttyGE50A'
baudrate = 9600
timeout = 1
address = "254"

"""Log Files"""
log_txt = 'ge50a.txt'

"""Initialization"""
ge50a = Ge50a('/dev/ttyGE50A', baudrate, timeout, address)

"""Routine"""

while 1:
    try:
	f = open(log_txt, 'a')
        datetimer = datetime.datetime.now().isoformat()
        output = datetimer+" "+ge50a.ge50a_writecomm("F?")+"\n"
	f.write(output)
	f.close()

    except:
        continue

