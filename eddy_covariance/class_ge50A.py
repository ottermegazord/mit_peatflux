import serial


class Ge50a:
    def __init__(self, port, baudrate, time, log_txt, address="254"):
        self.ser = serial.Serial(port, baudrate, timeout=time)
        self.log_txt = log_txt
        self.address = address

    def ge50a_concatenator(self, comm):
        return "@@@"+str(self.address)+comm+";FF"

    def ge50a_readline(self):
        raw_output = self.ser.readline()
        output = int((raw_output.replace("@@@00ACK", "")).replace(";FF", ""))
        return output

    def ge50a_writelog(self, stringer):
        log = open(self.log_txt, 'a')
        log.write(stringer)
        log.close()

    def ge50a_readaddress(self):
        self.ser.write(bytes("@@@254CA?;FF".encode()))
        output = self.ge50a_readline()
        return output

