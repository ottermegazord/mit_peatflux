"""this program transfers the file based on the frequency set in either crontab or daemon"""

import datetime
import os
import shutil


"""(/original directory,/directory to be copied to with the date stamp)"""
shutil.copyfile('/home/pi/peatflux-code/eddy_covariance/li7000_log.txt','/media/pi/SAMSUNG/li7000_log_'+datetime.date.today().isoformat()+'.txt')


"""deleting old file"""
os.remove('/home/pi/peatflux-code/eddy_covariance/li7000_log.txt')

