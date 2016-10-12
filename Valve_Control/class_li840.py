import serial
import xmlformatter
from lxml import etree
import time
import datetime

class li840:

    def __init__(self, port, baudrate, time):
        self.ser = serial.Serial(port, baudrate, timeout = time)

    def li840_readline(self):
        self.ser.flushInput()
        self.ser.flushOutput()
        output = self.ser.readline()
        return output

    def li840_adddate(self, li840_xml):
        doc = etree.parse(li840_xml)
        data_element = doc.find('data')
        datetimer = etree.SubElement(data_element, 'datetime')
        datetimer.text = datetime.datetime.now().isoformat()
	#print(datetimer.text)
	#print(doc)
        return doc

    def li840_pullnow(self, li840_raw, li840_timed):
        f1 = open(li840_raw, 'w')
        serial_output = self.li840_readline()
	serial_output_eol = serial_output + '\n'
        f1.write(serial_output_eol)
        f1.close()

        doc = self.li840_adddate(li840_raw)
        doc.write(open(li840_timed, 'a'))
        f2 = open(li840_timed, 'a')
        f2.write('\n')
        f2.close()
	

