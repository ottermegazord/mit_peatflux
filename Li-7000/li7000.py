#!/usr/bin/python

import datetime
from class_li7000 import li7000
import time

"""Serial Configuration"""

port = '/dev/ttyUSB0'
baudrate = 115200
timeout = 1

"""Calibration Constants"""
h2o_zero_interval = 0.2
h2o_span_interval = 0.2
co2_zero_interval = 0.2
co2_span_interval = 0.2
h2o_span = 1
co2_ref = 1
co2_span = 1

"""Log Files"""
log_txt = '/home/pi/Desktop/peatflux-code/Li-7000/log.txt'
cal_txt = '/home/pi/Desktop/peatflux-code/Li-7000/calibration.txt'

"""Time/Intervals/Periods"""
li7000_time_period = 0.1  # in seconds

test = li7000(port, baudrate, timeout, log_txt, cal_txt)

test.li7000_calibration(h2o_zero_interval, h2o_span_interval, co2_zero_interval, co2_span_interval, h2o_span, co2_ref, co2_span)

"""Routine"""
# while 1:
#     dt = datetime.datetime.now()
#     try:
#         if dt.minute == 18:
#             test.li7000_calibration(h2o_zero_interval, h2o_span_interval, co2_zero_interval, co2_span_interval,
#                                     h2o_span, co2_ref, co2_span)
#         else:
#             poll = test.li7000_pollnow()
#             print(poll)
#             f2 = open(log_txt, 'a')
#             f2.write(poll + '\n')
#             f2.close()
#
#     except:
#         continue
