import RPi.GPIO as GPIO
import time
 

"""Functions"""

def int2bin(n, count = 4):
	if ((n > 16) | (n < 0)) :
		print("Number out of range")
		raise;
	else:
		return "".join([str((n >> y) & 1) for y in range (count -1, -1, -1)])

def mux_channel(channel, chan_list):
	channel_bits = int2bin(channel)
	print(channel_bits)
	for i in range(0, 4):
		if channel_bits[i] == '1':
			#print("HIGH")
			GPIO.output(chan_list[i], GPIO.HIGH)
		elif channel_bits[i] == '0':
			#print("LOW")
			GPIO.output(chan_list[i], GPIO.LOW)

def valve_pulse_switch(channel, OPEN_chan_list, CLOSE_chan_list, SWITCH_OPEN, SWITCH_CLOSE, INTERVAL = 0.25, SWITCHING_INTERVAL = 2):
	time.sleep(INTERVAL)
	mux_channel(channel, OPEN_chan_list)
	GPIO.output(SWITCH_OPEN, GPIO.LOW)
	time.sleep(INTERVAL)
	GPIO.output(SWITCH_CLOSE, GPIO.HIGH)

	time.sleep(SWITCHING_INTERVAL)
	mux_channel(channel, CLOSE_chan_list)
	GPIO.output(SWITCH_CLOSE, GPIO.LOW)
	time.sleep(INTERVAL)
	GPIO.output(SWITCH_CLOSE, GPIO.HIGH)	
	
"""Pin Declaration"""
SWITCH_OPEN = 22
SWITCH_CLOSE = 29 
OPEN_chan_list = [32, 36, 38, 40] # chan_list = [S3, S2, S1, S0]
CLOSE_chan_list = [31, 33, 35, 37]
INTERVAL = 0.25
SWITCHING_INTERVAL = 2

GPIO.setmode(GPIO.BOARD)
GPIO.setwarnings(False)

GPIO.setup(OPEN_chan_list, GPIO.OUT)
GPIO.setup(CLOSE_chan_list, GPIO.OUT)
GPIO.setup(SWITCH_OPEN, GPIO.OUT)
GPIO.setup(SWITCH_CLOSE, GPIO.OUT)

while 1:
	
	try:

		for channel in range(1, 17):	
			time.sleep(INTERVAL)
			#channel = input("Select a Channel :/n")
		
			mux_channel(channel, OPEN_chan_list)
			GPIO.output(SWITCH_OPEN, GPIO.LOW)
			time.sleep(INTERVAL)
			GPIO.output(SWITCH_OPEN, GPIO.HIGH)

			time.sleep(SWITCHING_INTERVAL)

			mux_channel(channel, CLOSE_chan_list)
			GPIO.output(SWITCH_CLOSE, GPIO.LOW)
			time.sleep(INTERVAL)
			GPIO.output(SWITCH_CLOSE, GPIO.HIGH)
		
		time.sleep(5)
	except:
		pass
