#!/usr/bin/python

from class_ge50A import Ge50a
import datetime
import os.path

"""Serial Configuration"""
port = '/dev/ge50a'
baudrate = 9600
timeout = 1
address = "254"

"""Log Files"""
log_txt = 'ge50a.txt'

"""Initialization"""
ge50a = Ge50a('/dev/ttyUSB-ge50a', baudrate, timeout, address)


"""printing header file if log does not exist"""
if (not os.path.isfile(log_txt)):
    log = open('ge50a.txt','w+')
    header = 'Date\tTime\tFlow Rate\n'
    log.write(header)
    log.close()

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

