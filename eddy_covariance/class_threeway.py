import RPi.GPIO as GPIO
import time


class Threeway:
    def __init__(self, THREE_WAY):
	self.THREE_WAY = THREE_WAY

        GPIO.setmode(GPIO.BOARD)
        GPIO.setwarnings(False)
	GPIO.setup(THREE_WAY, GPIO.OUT)

    def open(self, channel):
	GPIO.output(self.THREE_WAY[channel-1], GPIO.HIGH)	
       
    def close(self, channel):
	GPIO.output(self.THREE_WAY[channel-1], GPIO.LOW)


