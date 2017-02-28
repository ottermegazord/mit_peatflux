from class_ge50A import Ge50a
import datetime

"""Serial Configuration"""
port = '/dev/ttyGE50A'
baudrate = 9600
timeout = 1
address = "254"

"""Log Files"""
log_txt = '/home/pi/Desktop/peatflux-code/eddy_covariance/ge50a_log.txt'

"""Initialization"""
ge50a = Ge50a('/dev/ttyGE50A', baudrate, timeout, address)
f = open('log_txt', 'a')

"""Routine"""

while 1:
    try:
        datetimer = datetime.datetime.now().isoformat()
        f.write(datetimer+" "+ge50a.ge50a_writecomm("F?"))

    except:
        continue

