# !/usr/bin/python  # Filename: class_li7000.py

import serial
import time


class li7000:
    def __init__(self, port, baudrate, time):
        self.ser = serial.Serial(port, baudrate, timeout=time)

    def li7000_readline(self):
        output = self.ser.readline()
        return output

    def li7000_header(self):
        self.ser.flushInput()
        self.ser.flushOutput()
        time.sleep(0.1)
        self.ser.write(bytes("(RS232(Sources?))\n".encode()))
        output = self.li7000_readline()
        return output

    def li7000_pollnow(self):
        self.ser.flushInput()
        self.ser.flushOutput()
        time.sleep(0.1)
        self.ser.write(bytes("(RS232(Poll Now))\n".encode()))
        for i in range(0, 3):
            if i == 2:
                output = self.li7000_readline()
            else:
                self.li7000_readline()
        return output

    def li7000_setreference(self, units, H2O, CO2):
        self.ser.flushInput()
        self.ser.flushOutput()
        self.ser.flush()
        time.sleep(0.1)
        str = "(Reference(H2O-units %s)(H2O %.3f)(CO2 %.3f))\n" % (units, H2O, CO2)
        self.ser.write(bytes(str.encode()))
        time.sleep(0.1)
        self.ser.flushInput()
        self.ser.flushOutput()

    def li7000_matchCO2(self):
        self.ser.flushInput()
        self.ser.flushOutput()
        self.ser.flush()
        time.sleep(0.1)
        str = "(UserCal(CO2 (Match Now)))\n"
        self.ser.write(bytes(str.encode()))
        time.sleep(0.1)
        self.ser.flushInput()
        self.ser.flushOutput()

    def li7000_matchH2O(self):
        self.ser.flushInput()
        self.ser.flushOutput()
        self.ser.flush()
        time.sleep(0.1)
        str = "(UserCal(H2O (Match Now)))\n"
        self.ser.write(bytes(str.encode()))
        time.sleep(0.1)
        self.ser.flushInput()
        self.ser.flushOutput()

    def li7000_zeroh2o(self, span_interval):
        self.ser.flushInput()
        self.ser.flushOutput()
        span_interval_sec = span_interval * 60
        time.sleep(span_interval_sec)
        self.ser.write(bytes("(UserCal (H2O (CellA-mm/m 0)))\n".encode()))
        time.sleep(0.1)
        self.ser.flushInput()
        self.ser.flushOutput()

    def li7000_h20calresult(self):
        self.ser.flushInput()
        self.ser.flushOutput()
        time.sleep(0.1)
        self.ser.write(bytes("(Cal(H2O(#)))\n".encode()))
        output = self.li7000_readline()
        return output

    def li7000_spanh2o(self, span, span_interval):
        self.ser.flushInput()
        self.ser.flushOutput()
        span_interval_sec = span_interval * 60
        time.sleep(span_interval_sec)
        str = "(UserCal (H2O (CellB-mm/m %.3f)))\n" % (span)
        self.ser.write(bytes(str.encode()))
        time.sleep(0.1)
        self.ser.flushInput()
        self.ser.flushOutput()

    def li7000_zeroco2(self, span_interval):
        self.ser.flushInput()
        self.ser.flushOutput()
        span_interval_sec = span_interval * 60
        time.sleep(span_interval_sec)
        self.ser.write(bytes("(UserCal (CO2 (CellA-um/m 0)))\n".encode()))
        time.sleep(0.1)
        self.ser.flushInput()
        self.ser.flushOutput()

    def li7000_spanco2(self, span, span_interval):
        self.ser.flushInput()
        self.ser.flushOutput()
        span_interval_sec = span_interval * 60
        time.sleep(span_interval_sec)
        str = "(UserCal (CO2 (CellB-um/m %.3f)))\n" % (span)
        self.ser.write(bytes(str.encode()))
        time.sleep(0.1)
        self.ser.flushInput()
        self.ser.flushOutput()

    def li7000_co2calresult(self):
        self.ser.flushInput()
        self.ser.flushOutput()
        time.sleep(0.1)
        self.ser.write(bytes("(Cal(CO2(#)))\n".encode()))
        output = self.li7000_readline()
        return output

    def li7000_calibration(self, h2o_zero_interval, h2o_span_interval, co2_zero_interval, co2_span_interval, h2o_span, co2_ref, co2_span):
        print("Initiate Calibration\n")
        print("Reference H20: Dry CO2: %.3f" % co2_ref)
        self.li7000_setreference("mm/m", 0, co2_ref)
        print("Zeroing H2O in Cell A for %.3f minutes\n" % h2o_zero_interval)
        self.li7000_zeroh2o(h2o_zero_interval)
        time.sleep(2)
        print("Zero H20 in Cell A completed \n")
        print("Matching H2O in Cell A and B \n")
        self.li7000_matchH2O()
        time.sleep(2)
        print("Matching H2O in Cell A and B completed \n")
        print("Spanning H2O in Cell B for %.3f minutes\n" % h2o_span_interval)
        self.li7000_spanh2o(h2o_span, h2o_span_interval)
        time.sleep(2)
        print("Spanning H2O in Cell B completed \n")
        print("Zeroing CO2 in Cell A for %.3f minutes\n" % co2_zero_interval)
        self.li7000_zeroco2(co2_zero_interval)
        time.sleep(2)
        print("Zero CO2 in Cell A completed \n")
        print("Matching CO2 in Cell A and B \n")
        self.li7000_matchCO2()
        time.sleep(2)
        print("Matching CO2 in Cell A and B completed \n")
        print("Spanning CO2 in Cell B for %.3f minutes\n" % co2_span_interval)
        self.li7000_spanco2(co2_span, co2_span_interval)
        time.sleep(2)
        print("Spanning CO2 in Cell B completed \n")
        print("Calibration complete!")

