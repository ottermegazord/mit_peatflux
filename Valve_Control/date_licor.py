import serial
import datetime
import time
import os
import xmlformatter
from lxml import etree

#functions



def print_date(file_name):
	date = datetime.datetime.now().isoformat("T")
	f = open(file_name, "a")
	f.write(date + '\n')
	f.close()

def pull_xml_840(port, baud_rate):
	ser = serial.Serial(port, baud_rate, timeout = 1)
	ser.flushOutput()
	x = ser.readline()
	ser.close()
	return(x)

def add_date_li840(li840_xml):

	doc = etree.parse(li840_xml)
	
	data_element = doc.find('data')
	#print(data_element)
	datetimer = etree.SubElement(data_element, 'datetimer')
	datetimer.text = datetime.datetime.now().isoformat()
	#print(datetimer.text)
	return doc

f1 = open('li840_temp.xml', 'w')
port = '/dev/ttyUSB1' 
baud_rate = 9600
serial_output = (pull_xml_840(port, baud_rate))#.replace('\n', '')
print(serial_output)
f1.write(serial_output + '\n')
f1.close()

doc = add_date_li840('li840_temp.xml')
doc.write(open('li840_timed.xml', 'a'))
f2 = open('li840_timed.xml', 'a')
f2.write('\n')
f2.close()




