#!/usr/bin/python

"""Li840 for Eddy Covariance System"""

import time
import datetime
from class_li840 import li840
from class_valve import Valve
from class_threeway import Threeway

"""Serial Configuration"""
port = '/dev/li840'
baudrate = 9600
timeout = 1

"""Calibration Constants"""
h2o_zero_interval = 0.2
h2o_span_interval = 0.2
co2_zero_interval = 0.2
co2_span_interval = 0.2
co2_ref = 0
co2_span = [350, 0, 430]
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
log_txt = '/home/pi/Desktop/peatflux-code/eddy_covariance/profile_nodes/li840_log.xml'
cal_txt = '/home/pi/Desktop/peatflux-code/eddy_covariance/profile_nodes/li840_cal.txt'

"""Time/Intervals/Periods"""
li840_read_period = 10  # in seconds

"""Valve Pin Assignments"""
open_chan_list = [31, 33, 35, 37]
close_chan_list = [32, 36, 38, 40]
SWITCH_OPEN = 29
SWITCH_CLOSE = 22
SWITCH_INTERVAL = 0.5
EC_channels = [9, 10, 11, 12]  # First element is zeroing Channel
THREE_WAY = [13, 15]
EDDY_CAL_CHAN = 16

"""Initialization"""
test = li840(port, baudrate, timeout, SWITCH_OPEN, SWITCH_CLOSE, open_chan_list, close_chan_list, log_txt,
                 cal_txt)
threeway = Threeway(THREE_WAY)
valve = Valve(SWITCH_OPEN, SWITCH_CLOSE, open_chan_list, close_chan_list)


"""Routine"""
while 1:
    dt = datetime.datetime.now()
    try:
	
	if (dt.hour == 11 and dt.minute == 00):
	   threeway.open(2)
	   valve.open_valve_channel(EDDY_CAL_CHAN, 0.25)
	   test.li840_calibration(EC_channels, h2o_zero_interval, h2o_span_interval, co2_zero_interval, co2_span_interval, h2o_span, co2_span)
           valve.close_valve_channel(EDDY_CAL_CHAN, 0.25)
	   threeway.close(2)
        elif dt.minute == 0 or dt.minute == 10 or dt.minute == 20 or dt.minute == 30 or dt.minute == 40 or dt.minute == 48 :
            print(dt.minute)
            for i in range(1, 9):
                valve.open_valve_channel(i, 0.15)
		print("channel %d\n" %i)
                print(files_timed[i-1])
                time.sleep(li840_read_period)
                test.li840_pullnow(files_raw, files_timed[i-1])
                valve.close_valve_channel(i, 0.15)

    except:
        continue
