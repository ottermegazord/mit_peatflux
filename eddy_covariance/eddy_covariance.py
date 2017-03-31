#!/usr/bin/python

import datetime
from class_li7000 import li7000
from class_valve import Valve
from class_threeway import Threeway
import time
import os.path
import csv

"""Serial Configuration"""
port = '/dev/li7000'
baudrate = 115200
timeout = 1

"""Calibration Constants"""
h2o_zero_interval = 0.2
h2o_span_interval = 0.2
co2_zero_interval = 0.2
co2_span_interval = 0.2
co2_ref = 0
co2_span = [350, 0, 430]
h2o_span = [0 ,0, 0]

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
THREE_WAY = [13, 15]
EDDY_CAL_CHAN = 15

"""Initialization"""
test = li7000(port, baudrate, timeout, SWITCH_OPEN, SWITCH_CLOSE, open_chan_list, close_chan_list, log_txt,
              cal_txt)

threeway = Threeway(THREE_WAY)
valve = Valve(SWITCH_OPEN, SWITCH_CLOSE, open_chan_list, close_chan_list)

"""printing header file if log doesn not exist"""
if (not os.path.isfile(log_txt)):
    log = open('li7000_log.txt', 'w+')
    header=  "DATAH\tDate\tTime\t" + test.li7000_header()
    test.li7000_writelog(header) 
    log.close()

"""Routine"""
while 1:

    dt = datetime.datetime.now()
    try:
        if (dt.hour == 10 and dt.minute == 9):
	    threeway.open(1)
	    valve.open_valve_channel(EDDY_CAL_CHAN, 0.25)	
            test.li7000_calibration(EC_channels, h2o_zero_interval, h2o_span_interval, co2_zero_interval, co2_span_interval,
                                    h2o_span, co2_ref, co2_span)
	    valve.close_valve_channel(EDDY_CAL_CHAN, 0.25)
	    threeway.close(1)
        else:
	    threeway.close(1)
	    threeway.close(2)
            poll = test.li7000_pollnow()
	    print(poll)
            test.li7000_writelog(poll)

    except:
        continue
