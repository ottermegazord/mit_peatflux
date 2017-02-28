import serial


class Ge50a:
    def __init__(self, port, baudrate, time, address="254"):
        self.ser = serial.Serial(port, baudrate, timeout=time)
        self.address = address

    def ge50a_concatenator(self, comm):
        return "@@@" + str(self.address) + comm + ";FF"

    def ge50a_readline(self):
        raw_output = self.ser.readline()
        output = raw_output.replace("@@@000ACK", "").replace(";FF", "")
        return output

    def ge50a_readaddress(self):
        self.ser.write(bytes("@@@254CA?;FF".encode()))
        output = self.ge50a_readline()
        return output

    def ge50a_writecomm(self, comm):
        self.ser.write(bytes(self.ge50a_concatenator(comm)).encode())
        output = self.ge50a_readline().strip()
        return output
