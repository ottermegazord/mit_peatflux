from Adafruit_MCP4725 import MCP4725
import time
from smbus import SMBus
import re
import time

class PID:
    """ Simple PID Control.

        This class implements a simplistic PID Control algorithm. When
        first instatiated all the gain variables are set to zero, so calling
        the method GenOut will just return a zero.
    """
    def _init_(self):
        # initialize gains
        self.Kp = 0
        self.Kd = 0
        self.Ki = 0

        self.Initialize()

    def SetKp(self, invar):
        """Set proportional gain. """
        self.Kp = invar

    def SetKi(self, invar):
        """Set integral gain. """
        self.Ki = invar

    def SetKd(self, invar):
        """Set derivative gain. """
        self.Kd = invar

    def SetPrevErr(self, preverr):
        """Set previous error value. """
        self.prev_err = preverr

    def Initialize(self):
        # initialize delta t variables
        self.currtm = time.time()
        self.prevtm = self.currtm

        self.prev_err = 0

        #term result variables
        self.Cp = 0
        self.Ci = 0
        self.Cd = 0

    def GenOut(self, error):
        """ Performs a PID computation and returns a control value based
        on the elapsed time (dt) and the error signal from a summing
        junction (the error parameter).
        """

        self.currtm = time.time()           #get t
        dt = self.currtm - self.prevtm      #get delta t
        de = error - self.prev_err          #get delta error

        self.Cp = self.Kp * error           #proportional term
        self.Ci += error * dt               #integral term

        self.Cd = 0
        if dt > 0:                          #no div by zero
            self.Cd = de/dt                 #no derivative term

        self.prevtm = self.currtm           #save t for next pass
        self.prev_err = error               #save t-1 error

        # sum the terms and return the result
        return self.Cp + (self.Ki * self.Ci) + (self.Kd * self.Cd)

#breakout board addresses

adc_address1 = 0x6A #address of ADC CH1-CH4
adc_address2 = 0x6B #address of ADC CH5-CH8
dac = MCP4725(0x62) #address of DAC board
DAC_RESOLUTION = 12 #DAC Resolution

#set parameters
Kp = 1
Ki = 2
Kd = 3
pid = PID()
pid.SetKp(Kp)
pid.SetKi(Ki)
pid.SetKd(Kd)

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


fb = 0
outv = 0
sp = 2.5

PID_loop = True

while PID_loop:

    file = open("testfile.txt", "a")
    now = time.strftime("%c")
    print ("Current date & time ") + time.strftime("%c")

    # summing node
    err = sp - fb   # assume sp is set elsewhere
    outv = pid.GenOut(err)
    address = int(round(outv/5.030581 * 4095))
    dac.setVoltage(address, False)

    #show analog output
    outvoltage = (5.04 / 4095) * address
    print("Output Voltage: %d V" %outvoltage)
    time.sleep(.05)

    changechannel(adc_address1, 0x9C)
    fb = getadcreading(adc_address1, 0x9c)
    #show analog input
    print ("Input Voltage: %02f V" % getadcreading(adc_address1,0x9C))

    #logging
    #print time
    file.write(time.strftime("%c"))
	#print input and outvoltages with return
    file.write(" %02f %02f \n" % (fb, outvoltage))


