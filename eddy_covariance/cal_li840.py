#!/usr/bin/python

"""Li840 for Eddy Covariance System"""

import time
import datetime
from class_li840 import li840
from class_valve import Valve

"""Serial Configuration"""
port = '/dev/ttyUSB1'
baudrate = 9600
timeout = 1

"""Calibration Constants"""
h2o_zero_interval = 0.05
h2o_span_interval = 0.05
co2_zero_interval = 0.05
co2_span_interval = 0.05
co2_ref = 0
co2_span = [0, 0, 0]
h2o_span = [0, 0, 0]

"""Log Files"""
files_timed = list()
files_raw = '/home/pi/Desktop/peatflux-code/eddy_covariance/profile_nodes/li840_raw.xml'
nodes = 8  # Number of profile nodes
for i in range(1, nodes + 1):
    f = open('/home/pi/Desktop/peatflux-code/eddy_covariance/profile_nodes/li840_timed_%i.xml' % i, 'a')
    files_timed.append("/home/pi/Desktop/peatflux-code/eddy_covariance/profile_nodes/li840_timed_%i.xml" % i)
    f.close()

#  Calibration Log
log_txt = '/home/pi/Desktop/peatflux-code/eddy_covariance/profile_nodes/li840_log.txt'
cal_txt = '/home/pi/Desktop/peatflux-code/eddy_covariance/profile_nodes/li840_cal.xml'

"""Time/Intervals/Periods"""
li840_read_period = 10  # in seconds

"""Valve Pin Assignments"""
open_chan_list = [31, 33, 35, 37]
close_chan_list = [32, 36, 38, 40]
SWITCH_OPEN = 29
SWITCH_CLOSE = 22
SWITCH_INTERVAL = 0.5
EC_channels = [1, 2, 3, 4]  # First element is zeroing Channel


"""Initialization"""
test = li840(port, baudrate, timeout, SWITCH_OPEN, SWITCH_CLOSE, open_chan_list, close_chan_list, log_txt,
                 cal_txt)
valve = Valve(SWITCH_OPEN, SWITCH_CLOSE, open_chan_list, close_chan_list)

"""Routine"""
test.li840_calibration(EC_channels, h2o_zero_interval, h2o_span_interval, co2_zero_interval, co2_span_interval, h2o_span, co2_span)
