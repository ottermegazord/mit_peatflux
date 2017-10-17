#!/usr/bin/env python

import minimalmodbus
import struct
import binascii

__author__  = "Idaly Ali"
__email__   = "idaly@mit..."
__license__ = "Apache License, Version 2.0"

class Watlow(minimalmodbus.Instrument):

    def __init__(self, portname, slaveaddress, baudrate):
        minimalmodbus.Instrument.__init__(self, portname, slaveaddress)
        self.serial.baudrate = baudrate


    def get_current_temperatureA(self):
        return self.read_register(361, functioncode=3)

    def get_current_temperatureB(self):
        return self.read_register(360, functioncode=3)

    def get_current_temperature(self):
        raw_temp1 = self.get_current_temperatureA()
        raw_temp2 = self.get_current_temperatureB()
        temp1 = hex(raw_temp1) + hex(raw_temp2)[2:]
        return struct.unpack('>f', binascii.unhexlify(temp1[2:]))[0]

if __name__ == '__main__':
    instrument = Watlow('/dev/tty.usbserial-FTYJRTZV', 1, 9600)

    a = instrument.get_current_temperature()
    print a
