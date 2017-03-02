import pigpio
from ABE_ADCPi import ADCPi
from ABE_helpers import ABEHelpers
import time
import os
import spi
from math import sqrt
from subprocess import *

"""IP Declaration"""

cmd = "ip addr show eth0 | grep inet | awk '{print $2}' | cut -d/ -f1"

"""Anemometer Pulse Counter Configuration"""

WIND_GPIO = 14  # output signal of anemometer GPI0 14
wind_time_period = 1 # time period for reading pulses from WIND_GPIO
an = pigpio.pi()

an.set_mode(WIND_GPIO, pigpio.INPUT)
an.set_pull_up_down(WIND_GPIO, pigpio.PUD_UP)

wind_cb = an.callback(WIND_GPIO, pigpio.FALLING_EDGE)

"""ADCPi Configuration"""
i2c_helper = ABEHelpers()
bus = i2c_helper.get_smbus()
adc = ADCPi(bus, 0x6A, 0x6B, 12)

"""MAX31865 Configuration"""

a = 0.00390830
b = -0.0000005775
c = 0  # 0 for temperature above 0 degrees
rtdR = 400
rtd0 = 100

# registers
REG_CONFIGURATION = 0x00
REG_RTD_MSB = 0x01
REG_RTD_LSB = 0x02
REG_HF_MSB = 0x03
REG_HF_LSB = 0x04
REG_LF_MSB = 0x05
REG_LF_LSB = 0x06
REG_FAULT_STATUS = 0x07

# configuration options
REG_CONF_50HZ_FILTER = (1 << 0)
REG_CONF_FAULT_STATUS_AUTO_CLEAR = (1 << 1)
REG_CONF_3WIRE_RTD = (1 << 4)
REG_CONF_1SHOT = (1 << 5)
REG_CONF_CONVERSION_MODE_AUTO = (1 << 6)
REG_CONF_VBIAS_ON = (1 << 7)


class max31865:
    def __init__(self, name, bus, channel, _3wire=True):
        self.serial = name
        device = "/dev/spidev%s.%s" % (bus, channel)

        spi.openSPI(speed=100000, mode=1, device=device)

        self.config = REG_CONF_VBIAS_ON | REG_CONF_50HZ_FILTER | REG_CONF_CONVERSION_MODE_AUTO
        if (_3wire):
            self.config |= REG_CONF_3WIRE_RTD

        self.__write__(REG_CONFIGURATION, self.config | REG_CONF_FAULT_STATUS_AUTO_CLEAR)
        self.__write__(REG_LF_MSB, 0x00)
        self.__write__(REG_LF_LSB, 0x00)
        self.__write__(REG_HF_MSB, 0xFF)
        self.__write__(REG_HF_LSB, 0xFF)

    def getSerial(self):
        return self.serial

    def __read__(self, address):
        assert (address >= 0 and address <= 0x07)

        return spi.transfer((address, 0))[1]

    def __write__(self, address, n):
        assert (address >= 0 and address <= 0x07)
        assert (n >= 0 and n <= 0xFF)

        spi.transfer((address | 0x80, n))

    def pull(self):
        msb_rtd = self.__read__(REG_RTD_MSB)
        lsb_rtd = self.__read__(REG_RTD_LSB)
        rtdRaw = ((msb_rtd << 7) + ((lsb_rtd & 0xFE) >> 1))
        rtdT = (rtdRaw * rtdR) / float(32768)  # 15-bits
        temp = -rtd0 * a + sqrt(rtd0 ** 2 * a ** 2 - 4 * rtd0 * b * (rtd0 - rtdT))
        temp = temp / (2 * rtd0 * b)
        return temp


# IP Address Method

def run_cmd(cmd):
    p = Popen(cmd, shell=True, stdout=PIPE)
    output = p.communicate()[0]
    return output

"""Log Files"""
log_txt = '/home/pi/py-max31865/profile.txt'

"""Routine"""

# Humidity Program Algorithm

humidity_voltage = float(adc.read_voltage(1))  # read voltage from microvane
humidity = humidity_voltage / 5.00 * 100

# Temperature Program Algorithm

probe = max31865("myprobe", 0, 0, False)
temperature = probe.pull()
spi.closeSPI()

# Anemometer Pulse Counter Algorithm

t_end = time.time() + 60 * wind_time_period
while time.time() < t_end:
    count = wind_cb.tally()
total = 0.293 * float(count) / 60

# Timestamp Definition
current_time = time.strftime("%Y%m%d %H:%M:%S", time.localtime())
print(current_time)

print("Temp: %.10f Humidity: %.10f Windspeed: %.10f" % (temperature, humidity, total))

# Get IP Address
ipaddr = run_cmd(cmd)
print(ipaddr)

# Append Humidity Readings to profile.txt
file = open(log_txt, "a")
file.write("%s, %.10f, %.10f, %.10f, %s" % (current_time, temperature, humidity, total, ipaddr))
file.close()

# os.system("lifepo4wered-cli set wake_time 1")
# os.system("sudo shutdown now")
