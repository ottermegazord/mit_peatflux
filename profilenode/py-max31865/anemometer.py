import time
import pigpio
from datetime import datetime

WIND_GPIO = 4

an = pigpio.pi()

an.set_mode(WIND_GPIO, pigpio.INPUT)
an.set_pull_up_down(WIND_GPIO, pigpio.PUD_UP)

wind_cb = an.callback(WIND_GPIO, pigpio.FALLING_EDGE)

#count = 0
old_count = 0

while True:

	#Timestamp Definition
	current_time = time.strftime("%Y%m%d %H:%M:%S", time.localtime())
	
	time.sleep(1)
	
	count = wind_cb.tally()
	total = 0.293 * float((count - old_count))
	print("windspeed %f m/s" % total)

	#Append Temperature Readings to HMP155.txt
	file = open("anemometer.txt", "a")
	file.write(current_time)
	file.write(', %.10f \n' % total)
	file.close()

	old_count = count

an.stop()
