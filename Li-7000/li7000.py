import datetime
import serial
import time

f1 = open("LI-7000.txt", "a")
#f2 = open("time.txt", "a")
ser = serial.Serial('/dev/ttyUSB0', 115200)
ser.flush()
while 1:
	#ser.write(bytes("(RS232(Poll Now))\n".encode()))
	x = ser.readline()
	print(x)
	f1.write(x)

