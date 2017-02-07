#enable function to specify date and time in the new file
import datetime
#enable function for file removal
import os
#enable function to copy files to a different directory
import shutil


#(/original directory,/directory to be copied to with the date stamp)
shutil.copyfile('/home/pi/peatflux-code/eddy_covariance/li7000_log.txt','/media/pi/SAMSUNG/li7000_log_'+datetime.date.today().isoformat()+'.txt')


#deleting old file
os.remove('/home/pi/peatflux-code/eddy_covariance/li7000_log.txt')

