import serial
from lxml import etree
import time
import datetime
from class_valve import Valve


class li840:
    def __init__(self, port, baudrate, time, SWITCH_OPEN, SWITCH_CLOSE, open_chan_list, close_chan_list, log_txt,
                 cal_txt):
        self.ser = serial.Serial(port, baudrate, timeout=time)
        self.valve = Valve(SWITCH_OPEN, SWITCH_CLOSE, open_chan_list, close_chan_list)
        self.log_txt = log_txt
        self.cal_txt = cal_txt

    def li840_readline(self):
        self.ser.write(bytes("<LI840><DATA>?</DATA></LI840>\n".encode()))
        output = self.ser.readline()
        return output

    def li840_adddate(self, li840_xml):
        doc = etree.parse(li840_xml)
        data_element = doc.find('data')
        datetimer = etree.SubElement(data_element, 'datetime')
        datetimer.text = datetime.datetime.now().isoformat()
        return doc

    def li840_pullnow(self, li840_raw, li840_timed):
        f1 = open(li840_raw, 'w')
        serial_output = self.li840_readline()
        serial_output_eol = serial_output + '\n'
        print(serial_output)
        f1.write(serial_output_eol)
        f1.close()

        doc = self.li840_adddate(li840_raw)
        doc.write(open(li840_timed, 'a'))
        f2 = open(li840_timed, 'a')
        f2.write('\n')
        f2.close()

    def li840_writelog(self, stringer):
        log = open(self.log_txt, 'a')
        log.write(stringer)
        log.close()

    def li840_writecal(self, stringer):
        cal = open(self.cal_txt, 'a')
        cal.write(stringer)
        cal.close()

    def li840_zeroco2(self, span_interval):
        self.ser.flushInput()
        self.ser.flushOutput()
        t_end = time.time() + span_interval * 60
        while time.time() < t_end:
            poll = self.li840_readline() + '\n'
            print(poll)
            self.li840_writelog(poll)
        dt = datetime.datetime.now()
        isodate = "%s-%s-%s" % (dt.year, dt.month, dt.day)
        str = "<LI840><CAL><DATE>%s</DATE><CO2ZERO>TRUE</CO2ZERO></CAL></LI840>\n" % isodate
        self.ser.write(bytes(str.encode()))
        time.sleep(0.1)
        self.ser.flushInput()
        self.ser.flushOutput()

    def li840_zeroh2o(self, span_interval):
        self.ser.flushInput()
        self.ser.flushOutput()
        t_end = time.time() + span_interval * 60
        while time.time() < t_end:
            poll = self.li840_readline() + '\n'
            print(poll)
            self.li840_writelog(poll)
        dt = datetime.datetime.now()
        isodate = "%s-%s-%s" % (dt.year, dt.month, dt.day)
        str = "<LI840><CAL><DATE>%s</DATE><H2OZERO>TRUE</H2OZERO></CAL></LI840>\n" % isodate
        self.ser.write(bytes(str.encode()))
        time.sleep(0.1)
        self.ser.flushInput()
        self.ser.flushOutput()

    def li840_spanco2(self, span, span_interval):
        self.ser.flushInput()
        self.ser.flushOutput()
        t_end = time.time() + span_interval * 60
        while time.time() < t_end:
            poll = self.li840_readline() + '\n'
            print(poll)
            self.li840_writelog(poll)
        dt = datetime.datetime.now()
        isodate = "%s-%s-%s" % (dt.year, dt.month, dt.day)
        str = "<LI840><CAL><DATE>%s</DATE><CO2SPAN>%.3f</CO2SPAN></CAL></LI840>\n" % (isodate,span)
        self.ser.write(bytes(str.encode()))
        time.sleep(0.1)
        self.ser.flushInput()
        self.ser.flushOutput()

    def li840_spanh2o(self, span, span_interval):
        self.ser.flushInput()
        self.ser.flushOutput()
        t_end = time.time() + span_interval * 60
        while time.time() < t_end:
            poll = self.li840_readline() + '\n'
            print(poll)
            self.li840_writelog(poll)
        dt = datetime.datetime.now()
        isodate = "%s-%s-%s" % (dt.year, dt.month, dt.day)
        str = "<LI840><CAL><DATE>%s</DATE><H2OSPAN>%.3f</H2OSPAN></CAL></LI840>\n" % (isodate,span)
        self.ser.write(bytes(str.encode()))
        time.sleep(0.1)
        self.ser.flushInput()
        self.ser.flushOutput()


    def li840_calibration(self, calib_channels, h2o_zero_interval, h2o_span_interval, co2_zero_interval,
                          co2_span_interval, h2o_span, co2_span):
        self.li840_writecal(datetime.datetime.now().isoformat() + '\n')
        print("Initiate Calibration\n")
        """Zeroing Cell A"""

        print("Zeroing H2O for %.3f minutes\n" % h2o_zero_interval)
        self.valve.open_valve_channel(calib_channels[0], 0.25)
        self.li840_zeroh2o(h2o_zero_interval)
        time.sleep(2)
        print("Zero H2O completed \n")

        print("Zeroing CO2 for %.3f minutes\n" % co2_zero_interval)
        self.li840_zeroco2(co2_zero_interval)
        time.sleep(2)
        print("Zero CO2 in Cell A completed \n")
        self.valve.close_valve_channel(calib_channels[0], 0.25)
        print("Matching CO2 in Cell A and B completed \n")

        """Spanning"""

        for i in range(0, len(co2_span)):
            print("Spanning %.3f H2O for %.3f minutes\n" % (h2o_span[i], h2o_span_interval))
            self.valve.open_valve_channel(calib_channels[i + 1], 0.25)
            self.li840_spanh2o(h2o_span[i], h2o_span_interval)
            time.sleep(3)
            print("Spanning %.3f H2O completed \n" % h2o_span[i])

            print("Spanning %.3f CO2 for %.3f minutes\n" % (co2_span[i], co2_span_interval))
            time.sleep(3)
            self.li840_spanco2(co2_span[i], co2_span_interval)
            time.sleep(2)
            self.valve.close_valve_channel(calib_channels[i + 1], 0.25)
            print("Spanning %.3f CO2 completed \n" % co2_span[i])
            time.sleep(2)

        time.sleep(3)
        print("Calibration complete!")
