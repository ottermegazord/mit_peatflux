from class_valve import Valve
import time

"""Valve Pin Assignments"""
open_chan_list = [31, 33, 35, 37]
close_chan_list = [32, 36, 38, 40]
SWITCH_OPEN = 29
SWITCH_CLOSE = 22
SWITCH_INTERVAL = 0.5
EC_channels = [9, 10, 11, 12]  # First element is zeroing Channel

#""Routine""

valve = Valve(SWITCH_OPEN, SWITCH_CLOSE, open_chan_list, close_chan_list)

while 1:
	for i in range (1, 17):
		print(i)
		valve.open_valve_channel(i, 0.01)
		time.sleep(1)
		valve.close_valve_channel(i,0.01)
		time.sleep(1)
