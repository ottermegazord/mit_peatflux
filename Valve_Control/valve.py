import RPi.GPIO as GPIO
from class_valve import Valve
import time

""" Pin Assignments """

open_chan_list = [31, 33, 35, 37]
close_chan_list = [32, 36, 38, 40]
SWITCH_OPEN = 29
SWITCH_CLOSE = 22
SWITCH_INTERVAL = 0.5


valve = Valve(SWITCH_OPEN, SWITCH_CLOSE, open_chan_list, close_chan_list)

valve.open_valve_channel(2, SWITCH_INTERVAL)
