from class_threeway import Threeway
import time

THREE_WAY = [13 ,15]

threeway = Threeway(THREE_WAY)

while 1:
	threeway.open(1)
	time.sleep(1)
	threeway.close(2)
	time.sleep(1)
