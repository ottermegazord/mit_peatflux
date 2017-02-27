#!/usr/bin/python

import datetime
from class_li7000 import li7000

#test

"""Serial Configuration"""
port = '/dev/li7000'
baudrate = 115200
time = 1

"""Calibration Constants"""
h2o_zero_interval = 0.5
h2o_span_interval = 0.5
co2_zero_interval = 0.5
co2_span_interval = 0.5
co2_ref = 0
co2_span = [350, 390, 430]
h2o_span = [0, 0, 0]

"""Log Files"""
log_txt = '/home/pi/Desktop/peatflux-code/eddy_covariance/li7000_log.txt'
cal_txt = '/home/pi/Desktop/peatflux-code/eddy_covariance/li7000_calibration.txt'

"""Time/Intervals/Periods"""
li7000_time_period = 0.1  # in seconds

"""Valve Pin Assignments"""
open_chan_list = [31, 33, 35, 37]
close_chan_list = [32, 36, 38, 40]
SWITCH_OPEN = 29
SWITCH_CLOSE = 22
SWITCH_INTERVAL = 0.5
EC_channels = [9, 10, 11, 12]  # First element is zeroing Channel

"""Initialization"""
test = li7000(port, baudrate, time, SWITCH_OPEN, SWITCH_CLOSE, open_chan_list, close_chan_list, log_txt,
              cal_txt)

"""Routine"""

while 1:
	test.li7000_calibration(EC_channels, h2o_zero_interval, h2o_span_interval, co2_zero_interval, co2_span_interval,
                                    h2o_span, co2_ref, co2_span)
