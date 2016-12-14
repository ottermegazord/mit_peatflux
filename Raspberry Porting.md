Porting of sungrow:

Updating Raspbian
Step 1) sudo apt-get update
Step 2) sudo apt-get dist-upgrade

Installing dependencies
Step 3) sudo apt-get install python-dev

Step 4) wget http://pyyaml.org/download/libyaml/yaml-0.1.7.tar.gz
Step 5) tar -xzf yaml-0.1.7.tar.gz
Step 6) cd yaml-0.1.7
Step 7) ./configure && make && sudo su -c 'make install'

Step 8) wget http://pyyaml.org/download/pyyaml/PyYAML-3.10.tar.gz
Step 9) tar -xzf PyYAML-3.10.tar.gz
Step 10) cd PyYAML-3.10
Step 11) python setup.py build && sudo su -c 'python setup.py install'

Step 12) wget http://pypi.python.org/packages/source/p/pyserial/pyserial-2.6.tar.gz
Step 13) tar -xzf pyserial-2.6.tar.gz
Step 14) cd pyserial-2.6
Step 15) python setup.py build && sudo su -c 'python setup.py install' 

Checking for port number for RS-232
Step 16) dmesg | grep -i usb
Step 17) cd sungrow-0.1b7_4
Step 18) cd doc
Step 19) sudo nano example_system_config_2.yml (for allegro and outback charge controller)
Step 20) Change the usb port number according to whichever equipment is used for testing.

Testing
Step 21) At the doc directory, type sungrow -vvv example_system_config_2.yml
Step 22) sudo nano inverter_status.csv (to check for logging for allegro inverter)

Known bugs (Solved)
1) When setting up PyYaml, the python headers couldnt be detected.
   Solution:
   Use sudo apt-get python-dev (for python 2)
   Use sudo apt-get python3-dev (for python 3)

2) When doing python setup, there was a password prompt and neither 
   raspberry default password nor changing the password worked.
   Solution:
   Added sudo into the command to overwrite the password prompt.


