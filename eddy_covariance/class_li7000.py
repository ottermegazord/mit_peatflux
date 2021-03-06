# !/usr/bin/python
#  Filename: class_li7000.py

import serial
import time
import datetime

from class_valve import Valve


class li7000:
    def __init__(self, port, baudrate, time, SWITCH_OPEN, SWITCH_CLOSE, open_chan_list, close_chan_list, log_txt,
                 cal_txt):
        self.ser = serial.Serial(port, baudrate, timeout=time)
        self.log_txt = log_txt
        self.cal_txt = cal_txt
        self.valve = Valve(SWITCH_OPEN, SWITCH_CLOSE, open_chan_list, close_chan_list)

    def li7000_writelog(self, stringer):
        log = open(self.log_txt, 'a')
        log.write(stringer)
        log.close()

    def li7000_writecal(self, stringer):
        cal = open(self.cal_txt, 'a')
        cal.write(stringer)
        cal.close()

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
        # time.sleep(0.1)
        self.ser.write(bytes("(RS232(Poll Now))\n".encode()))
        for i in range(0, 3):
            if i == 2:
                output = self.li7000_readline()
            else:
                self.li7000_readline()
        return output

    def li7000_setreference(self, units, h2o, co2):
        self.ser.flushInput()
        self.ser.flushOutput()
        self.ser.flush()
        time.sleep(0.1)
        str = "(Reference(h2o-units %s)(h2o %.3f)(co2 %.3f))\n" % (units, h2o, co2)
        self.ser.write(bytes(str.encode()))
        time.sleep(0.1)
        self.ser.flushInput()
        self.ser.flushOutput()

    def li7000_matchco2(self):
        self.ser.flushInput()
        self.ser.flushOutput()
        self.ser.flush()
        time.sleep(0.1)
        str = "(UserCal(co2 (Match Now)))\n"
        self.ser.write(bytes(str.encode()))
        time.sleep(0.1)
        self.ser.flushInput()
        self.ser.flushOutput()

    def li7000_matchh2o(self):
        self.ser.flushInput()
        self.ser.flushOutput()
        self.ser.flush()
        time.sleep(0.1)
        str = "(UserCal(h2o (Match Now)))\n"
        self.ser.write(bytes(str.encode()))
        time.sleep(0.1)
        self.ser.flushInput()
        self.ser.flushOutput()

    def li7000_zeroh2o(self, span_interval):
        self.ser.flushInput()
        self.ser.flushOutput()
        t_end = time.time() + span_interval * 60
        while time.time() < t_end:
            poll = self.li7000_pollnow() + '\n'
            print(poll)
            self.li7000_writelog(poll)
        self.ser.write(bytes("(UserCal (h2o (CellA-mm/m 0)))\n".encode()))
        time.sleep(0.1)
        self.ser.flushInput()
        self.ser.flushOutput()

    def li7000_h2ocalresult(self):
        self.ser.flushInput()
        self.ser.flushOutput()
        time.sleep(0.1)
        self.ser.write(bytes("(Cal(h2o(#)))\n".encode()))
        output = self.li7000_readline()
        return output

    def li7000_spanh2o(self, span, span_interval):
        self.ser.flushInput()
        self.ser.flushOutput()
        t_end = time.time() + span_interval * 60
        while time.time() < t_end:
            poll = self.li7000_pollnow() + '\n'
            print(poll)
            self.li7000_writelog(poll)
        str = "(UserCal (h2o (CellB-mm/m %.3f)))\n" % (span)
        self.ser.write(bytes(str.encode()))
        time.sleep(0.1)
        self.ser.flushInput()
        self.ser.flushOutput()

    def li7000_zeroco2(self, span_interval):
        self.ser.flushInput()
        self.ser.flushOutput()
        t_end = time.time() + span_interval * 60
        while time.time() < t_end:
            poll = self.li7000_pollnow() + '\n'
            print(poll)
            self.li7000_writelog(poll)
        self.ser.write(bytes("(UserCal (co2 (CellA-um/m 0)))\n".encode()))
        time.sleep(0.1)
        self.ser.flushInput()
        self.ser.flushOutput()

    def li7000_spanco2(self, span, span_interval):
        self.ser.flushInput()
        self.ser.flushOutput()
        t_end = time.time() + span_interval * 60
        while time.time() < t_end:
            poll = self.li7000_pollnow() + '\n'
            print(poll)
            self.li7000_writelog(poll)
        str = "(UserCal (co2 (CellB-um/m %.3f)))\n" % (span)
        self.ser.write(bytes(str.encode()))
        time.sleep(0.1)
        self.ser.flushInput()
        self.ser.flushOutput()

    def li7000_co2calresult(self):
        self.ser.flushInput()
        self.ser.flushOutput()
        time.sleep(0.1)
        self.ser.write(bytes("(Cal(co2(#)))\n".encode()))
        output = self.li7000_readline()
        return output

    def li7000_calibration(self, calib_channels, h2o_zero_interval, h2o_span_interval, co2_zero_interval, co2_span_interval, h2o_span,
                           co2_ref, co2_span):
        self.li7000_writecal(datetime.datetime.now().isoformat() + '\n')
        print("Initiate Calibration\n")
        print("Reference h2o: Dry co2: %.3f" % co2_ref)
        self.li7000_setreference("mm/m", 0, co2_ref)

        """Zeroing Cell A"""

        print("Zeroing h2o in Cell A for %.3f minutes\n" % h2o_zero_interval)
        self.valve.open_valve_channel(calib_channels[0], 0.25)
        self.li7000_zeroh2o(h2o_zero_interval)
        time.sleep(2)
        print("Zero h2o in Cell A completed \n")
        print("Matching h2o in Cell A and B \n")
        self.li7000_matchh2o()
        time.sleep(2)
        print("Matching h2o in Cell A and B completed \n")

        print("Zeroing co2 in Cell A for %.3f minutes\n" % co2_zero_interval)
        self.li7000_zeroco2(co2_zero_interval)
        time.sleep(2)
        print("Zero co2 in Cell A completed \n")
        print("Matching co2 in Cell A and B \n")
        self.li7000_matchco2()
        time.sleep(2)
        self.valve.close_valve_channel(calib_channels[0], 0.25)
        print("Matching co2 in Cell A and B completed \n")
        time.sleep(10)

        """Spanning Cell B"""

        for i in range(0, len(co2_span)):

            print("Spanning %.3f h2o in Cell B for %.3f minutes\n" % (h2o_span[i], h2o_span_interval))
            self.valve.open_valve_channel(calib_channels[i+1], 0.25)
            self.li7000_spanh2o(h2o_span[i], h2o_span_interval)
            time.sleep(3)
            print("Spanning %.3f h2o in Cell B completed \n" % h2o_span[i])

            print("Spanning %.3f co2 in Cell B for %.3f minutes\n" % (co2_span[i], co2_span_interval))
            time.sleep(3)
            self.li7000_spanco2(co2_span[i], co2_span_interval)
            time.sleep(2)
            self.valve.close_valve_channel(calib_channels[i+1], 0.25)
            print("Spanning %.3f co2 in Cell B completed \n" % co2_span[i])
            time.sleep(10)

        time.sleep(3)
        print("Calibration complete!")

