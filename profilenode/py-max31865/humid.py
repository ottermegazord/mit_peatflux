#from Adafruit_MCP4725 import MCP4725
import time
from smbus import SMBus
import re
import time
import serial
import datetime
#breakout board addresses

adc_address1 = 0x6A #address of ADC CH1-CH4
adc_address2 = 0x6B #address of ADC CH5-CH8
#dac = MCP4725(0x62) #address of DAC board
#DAC_RESOLUTION = 12 #DAC Resolution

# create byte array and fill with initial values to define size
adcreading = bytearray()

adcreading.append(0x00)
adcreading.append(0x00)
adcreading.append(0x00)
adcreading.append(0x00)

varDivisior = 1 # from pdf sheet on adc addresses and config
varMultiplier = (2.4705882/varDivisior)/1000

# detect i2C port number and assign to i2c_bus
for line in open('/proc/cpuinfo').readlines():
    m = re.match('(.*?)\s*:\s*(.*)', line)
    if m:
        (name, value) = (m.group(1), m.group(2))
        if name == "Revision":
            if value [-4:] in ('0002', '0003'):
                i2c_bus = 0
            else:
                i2c_bus = 1
            break


bus = SMBus(i2c_bus)

def changechannel(address, adcConfig):
	tmp= bus.write_byte(address, adcConfig)

def getadcreading(address, adcConfig):
	adcreading = bus.read_i2c_block_data(address,adcConfig)
	h = adcreading[0]
	#m = adcreading[1]
	l = adcreading[1]
	s = adcreading[2]
	# wait for new data
	while (s & 128):
		adcreading = bus.read_i2c_block_data(address,adcConfig)
		h = adcreading[0]
		#m = adcreading[1]
		l = adcreading[1]
		s = adcreading[2]

	# shift bits to product result
	t = (h << 8) | l
	# check if positive or negative number and invert if needed
	if (h > 128):
		t = ~(0x020000 - t)
	return t * varMultiplier

while True:
		
	changechannel(adc_address1, 0x90)
	humidity_voltage = float(getadcreading(adc_address1, 0x90)) #read voltage from microvane
	humidity = humidity_voltage / 5.00 * 100
	s = datetime.datetime.now()
	print(humidity) 

	#Timestamp Definition
	current_time = time.strftime("%Y%m%d %H:%M:%S", time.localtime())

	#Append Humidity Readings to humid.txt
	file = open("humid.txt" , "a")
	file.write(current_time)
	file.write(', %.10f \n' % humidity)
	file.close()
	time.sleep(1)


