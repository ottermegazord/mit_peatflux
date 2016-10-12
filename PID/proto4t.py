from Adafruit_MCP4725 import MCP4725
import time
from smbus import SMBus
import re
import time
import os

class PID:
	"""
	Discrete PID control
	"""

	def __init__(self, P=2.0, I=0.0, D=1.0, Derivator=0, Integrator=0, Integrator_max=500, Integrator_min=-500):

		self.Kp=P
		self.Ki=I
		self.Kd=D
		self.Derivator=Derivator
		self.Integrator=Integrator
		self.Integrator_max=Integrator_max
		self.Integrator_min=Integrator_min

		self.set_point=0.0
		self.error=0.0

	def update(self,current_value):
		"""
		Calculate PID output value for given reference input and feedback
		"""

		self.error = self.set_point - current_value

		self.P_value = self.Kp * self.error
		self.D_value = self.Kd * ( self.error - self.Derivator)
		self.Derivator = self.error

		self.Integrator = self.Integrator + self.error

		if self.Integrator > self.Integrator_max:
			self.Integrator = self.Integrator_max
		elif self.Integrator < self.Integrator_min:
			self.Integrator = self.Integrator_min

		self.I_value = self.Integrator * self.Ki

		PID = self.P_value + self.I_value + self.D_value

		return PID

	def setPoint(self,set_point):
		"""
		Initilize the setpoint of PID
		"""
		self.set_point = set_point
		self.Integrator=0
		self.Derivator=0

	def setIntegrator(self, Integrator):
		self.Integrator = Integrator

	def setDerivator(self, Derivator):
		self.Derivator = Derivator

	def setKp(self,P):
		self.Kp=P

	def setKi(self,I):
		self.Ki=I

	def setKd(self,D):
		self.Kd=D

	def getPoint(self):
		return self.set_point

	def getError(self):
		return self.error

	def getIntegrator(self):
		return self.Integrator

	def getDerivator(self):
		return self.Derivator


#breakout board addresses

adc_address1 = 0x6A #address of ADC CH1-CH4
adc_address2 = 0x6B #address of ADC CH5-CH8
dac = MCP4725(0x62) #address of DAC board
DAC_RESOLUTION = 10  #DAC Resolution

# create byte array and fill with initial values to define size
adcreading = bytearray()

adcreading.append(0x00)
adcreading.append(0x00)
adcreading.append(0x00)
adcreading.append(0x00)

varDivisior = 64 # from pdf sheet on adc addresses and config
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
	m = adcreading[1]
	l = adcreading[2]
	s = adcreading[3]
	# wait for new data
	while (s & 128):
		adcreading = bus.read_i2c_block_data(address,adcConfig)
		h = adcreading[0]
		m = adcreading[1]
		l = adcreading[2]
		s = adcreading[3]

	# shift bits to product result
	t = ((h & 0b00000001) << 16) | (m << 8) | l
	# check if positive or negative number and invert if needed
	if (h > 128):
		t = ~(0x020000 - t)
	return t * varMultiplier

p=PID(6,0.37397,0.009349289)
p.setPoint(1.135)
while True:


    os.system('clear')	 
    changechannel(adc_address1, 0x9c)
    measurement_value = getadcreading(adc_address1, 0x9c) # channel 1 address == 0x9c
    pid = p.update(measurement_value)
    address = int(round(pid/5.030581 * 4095)) * -1
    dac.setVoltage(address,False)	
#    print("pid output to pump: %.5f" % pid)
 #   print("process variable from barometer: %.5f" %measurement_value)

    file = open("testfile2.txt", "a")

    file.write(" %.3f %.3f \n" % (measurement_value, pid))

    file.close()
	
