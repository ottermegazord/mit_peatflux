import RPi.GPIO as GPIO
import time
 

"""Functions"""

def int2bin(n, count = 4):
	if ((n > 15) | (n < 0)) :
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
			GPIO.output(chan_list[i], GPIO.LOW)
		elif channel_bits[i] == '0':
			#print("LOW")
			GPIO.output(chan_list[i], GPIO.HIGH)	

"""Pin Configuration"""
SWITCH = 38
chan_list = [31, 33, 35, 37]

GPIO.setmode(GPIO.BOARD)
GPIO.setwarnings(False)
GPIO.setup(chan_list, GPIO.OUT)
GPIO.setup(SWITCH, GPIO.OUT)

while 1:
	time.sleep(1)
	for channel in range(0, 17):
		if channel == 16:
			GPIO.output(SWITCH, GPIO.HIGH)
			print("OFF")
			time.sleep(2)
		else:
			#channel = input("Key in channel: ")
			GPIO.output(SWITCH, GPIO.LOW)
			mux_channel(channel, chan_list)
			time.sleep(0.5)
			#GPIO.cleanup()
