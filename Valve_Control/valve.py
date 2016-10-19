
from class_valve import Valve

""" Pin Assignments """

open_chan_list = [31, 33, 35, 37]
close_chan_list = [32, 36, 38, 40]

valve = Valve(open_chan_list, close_chan_list)

valve.open_valve_channel(2)