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
co2_span_interval = 7,5
co2_ref = 0
co2_span = [0, 0, 0]
h2o_span = [0, 0, 0]

"""Log Files"""
raw_xml = '/home/pi/Desktop/peatflux-code/eddy_covariance/li840_raw.xml'
timed_xml = '/home/pi/Desktop/peatflux-code/eddy_covariance/li840_timed.xml'

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
	test.li840_pullnow(raw_xml, timed_xml)

    except:
        continue
