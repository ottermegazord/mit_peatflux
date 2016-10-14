import datetime
from class_li7000 import li7000
import time

"""Serial Configuration"""

port = '/dev/ttyUSB0'
baudrate = 115200
timeout = 1

"""Calibration Constants"""
h2o_zero_interval = 3
h2o_span_interval = 3
co2_zero_interval = 3
co2_span_interval = 3
h2o_span = 3
co2_ref = 3
co2_span = 3

"""Time/Intervals/Periods"""
li7000_time_period = 0.1 #in seconds

test = li7000(port, baudrate, timeout)

"""Log Files"""
"""Routine"""
while 1:
	
    dt = datetime.datetime.now()
    if dt.minute == 14:
	f1 = open('calibration.txt', 'a')
        test.li7000_calibration(h2o_zero_interval, h2o_span_interval, co2_zero_interval, co2_span_interval, h2o_span, co2_ref, co2_span)
        f1.write(datetime.datetime.now().isoformat())
	f1.close()
    else:
	poll = test.li7000_pollnow()
	print(poll)
	f2 = open('log.txt', 'a')
	f2.write(poll + '\n')
	f2.close()
