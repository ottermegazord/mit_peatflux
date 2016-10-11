#!/usr/bin/python

import time
from class_li7000 import li7000


""" Assignments """

LI7000_USB = '/dev/ttyUSB2'
baudrate = 115200
f1 = open('li7000.txt', 'a')

""" Routine """

test = li7000('/dev/ttyUSB2', 115200)

test.li7000_matchH2O()

"""while 1:
	units = raw_input("Key in units\n")
	h2o = input("key in h2o\n")
	co2 = input("key in co2\n")
	test.li7000_setreference(units, h2o, co2)"""

