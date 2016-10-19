
import RPi.GPIO as GPIO
import time
import serial
import datetime

class Valve:
    def __init__(self, open_chan_list, close_chan_list):
        self.open_chan_list = open_chan_list
        self.close_chan_list = close_chan_list

    def int2bin(self, n, count = 4):
        if (n > 16) | (n < 0):
            print("Number out of range")
            raise
        else:
            return "".join([str((n >> y) & 1) for y in range(count - 1, -1, -1)])

    def open_valve_channel(self, channel):
        channel_bits = self.int2bin(channel)
        # print(channel_bits)
        for i in range(0, 4):
            if channel_bits[i] == '1':
                # print("HIGH")
                GPIO.output(self.open_chan_list[i], GPIO.HIGH)
            elif channel_bits[i] == '0':
                # print("LOW")
                GPIO.output(self.open_chan_list[i], GPIO.LOW)
