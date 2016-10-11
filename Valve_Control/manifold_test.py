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
			GPIO.output(chan_list[i], GPIO.HIGH)
		elif channel_bits[i] == '0':
			#print("LOW")
			GPIO.output(chan_list[i], GPIO.LOW)	

chan_list = [31, 33, 35, 37]
GPIO.setmode(GPIO.BOARD)
GPIO.setwarnings(False)
GPIO.setup(chan_list, GPIO.OUT)

while 1:
	channel = input("Key in channel: ")
	mux_channel(channel, chan_list)
	#time.sleep(1)
	#GPIO.cleanup()
