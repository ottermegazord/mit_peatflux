import datetime
import serial

def li7000_readline(port):
	#port.flush()
	output = port.readline()
	return output

def li7000_write(port, str):
	port.write(bytes(str.encode()))
	

f1 = open("LI-7000.txt", "a")
#f2 = open("time.txt", "a")
ser = serial.Serial('/dev/ttyUSB1', 115200, timeout = 1)

while 1:
	choice = raw_input("read or write? \n")
	#print(choice)
	if choice == "read":
		for i in range (0, 3):
			print(li7000_readline(ser))
	elif choice == "write":
		str = raw_input("key in command: \n")
		str_lf = str + '\n'
		ser.write(bytes(str_lf.encode()))

