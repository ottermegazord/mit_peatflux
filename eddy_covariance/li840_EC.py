#!/usr/bin/python

import datetime
from class_li840 import li840
from class_valve import Valve
import time

"""Serial Configuration"""
port = '/dev/ttyUSB1'
baudrate = 9600
time = 1

"""Calibration Constants"""
h2o_zero_interval = 7.5
h2o_span_interval = 7.5
co2_zero_interval = 7.5
co2_span_interval = 7, 5
co2_ref = 0
co2_span = [0, 0, 0]
h2o_span = [0, 0, 0]

"""Log Files"""
files_timed = list()
files_raw = '/home/pi/Desktop/peatflux-code/eddy_covariance/profile_nodes/li840_raw.xml'
nodes = 6  # Number of profile nodes
for i in range(1, nodes + 1):
    f = open('/home/pi/Desktop/peatflux-code/eddy_covariance/profile_nodes/li840_timed_%i.xml' % i, 'a')
    files_timed.append("/home/pi/Desktop/peatflux-code/eddy_covariance/profile_nodes/li840_timed_%i.xml" % i)
    f.close()

"""Time/Intervals/Periods"""
li7000_time_period = 0.1  # in seconds

"""Valve Pin Assignments"""
open_chan_list = [31, 33, 35, 37]
close_chan_list = [32, 36, 38, 40]
SWITCH_OPEN = 29
SWITCH_CLOSE = 22
SWITCH_INTERVAL = 0.5
EC_channels = [1, 2, 3, 4]  # First element is zeroing Channel

"""Initialization"""
test = li840(port, baudrate, time)

"""Routine"""
while 1:

    try:
        for i in range(0, len(files_timed)):
	    print(files_timed[i])
            test.li840_pullnow(files_raw, files_timed[i])

    except:
        continue
