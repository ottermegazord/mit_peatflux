
# peatflux-code

Welcome to the peatflux-code!

# Running a script as a service in Raspbian Jessie #

Step 1: Define the service definition to run your script (e.g. yourscript.py)
`cd /lib/systemd/system`
`sudo nano yourscript.service`

Step 2: Create a service definition
Type these out in your _yourscript.service_ service definition
`[Unit]`
`Description=This is my script`
`After=multi-user.target`

`[Service]`
`Type=simple`
`ExecStart=/usr/bin/python /home/pi/yourscript.py`
`Restart=on-abort`

`[Install]`
`WantedBy=multi-user.target`

Essentially, this code means that whenever service is stopped, it will be restarted automatically.

Step 4: Activate your service
`sudo chmod 644 /lib/systemd/system/yourscript.service`
`chmod +x /home/pi/yourscript.py`
`sudo systemctl daemon-reload`
`sudo systemctl enable yourscript.service`
`sudo systemctl start yourscript.service`

Step 4: Check for status of your service
`sudo systemctl status hello.service`

This command will show the status (active/inactive) of your service, and the last instructions and/or returns

Step 5: Restart your RPi and enjoy!

To stop the script we can enter the command
`sudo service yourscript stop`

# Persistent USB Device #

If you have multiple USB devices connected, it could happen that after a reboot the device order is changed (ttyUSB0 is ttyUSB1, or the other way around)

The good news is, that there is a solution for this:

=Find ID's of USB device=
Make sure all the usb devices are plugged in.

Run the following command:
sudo lsusb -v | more
and write down the:

 *idVendor
 *idProduct
 *iSerial

(you can press the spacebar to scroll down)

= Examples =
The FTDI cable used to connect to the Licor 7000 is reported as:
  
  idVendor           0x0403 Future Technology Devices International, Ltd
  idProduct          0x6001 FT232 USB-Serial (UART) IC
  bcdDevice            6.00
  iManufacturer           1 FTDI
  iProduct                2 UT232R
  iSerial                 3 FTWD9PPQ

The FTDI cable used to connect to the Licor 840 is reported as:

  idVendor           0x0403 Future Technology Devices International, Ltd
  idProduct          0x6001 FT232 USB-Serial (UART) IC
  bcdDevice            6.00
  iManufacturer           1 FTDI
  iProduct                2 UT232R
  iSerial                 3 FTYNX3XV

You need the part behind the '0x'. So you don't write down '0x0403' but '0403'.

=Creating rules file=
Create a rules file, with the following example content:

sudo nano /etc/udev/rules.d/99-usb-serial.rules

===Examples ===


GE50A USB

`SUBSYSTEM=="tty", ATTRS{idVendor}=="0403", ATTRS{idProduct}=="6001", ATTRS{serial}=="FTZ1T3BU", SYMLINK+="ttyUSB-ge50a"`

LI7000 USB

`SUBSYSTEM=="tty", ATTRS{idVendor}=="0403", ATTRS{idProduct}=="6001", ATTRS{serial}=="FTYNX3XV", SYMLINK+="li7000"`

LI840 USB

`SUBSYSTEM=="tty", ATTRS{idVendor}=="0403", ATTRS{idProduct}=="6001", ATTRS{serial}=="FTWD9PPQ", SYMLINK+="li840"`


(Put in the values you've written down between the quotes (e.g. replace '0403' with the idVendor of your USB device).

Some devices don't show a serial, for examples like this usb

Aeon ZWave USB stick is reported as:

  idVendor           0x10c4 Cygnal Integrated Products, Inc.
  idProduct          0xea60 CP210x UART Bridge / myAVR mySmartUSB light
  
you can remove that part in the file, so it looks like this:

<code>SUBSYSTEM=="tty", ATTRS{idVendor}=="1a86", ATTRS{idProduct}=="7523", SYMLINK+="ttyUSB-RFX433"</code>

Names should be ttyUSB-UNIQUENAME so you can easily identify them within Domoticz.

=== AeoTec Z-Stick ===
Gen2:
<code>SUBSYSTEM=="tty", ATTRS{idVendor}=="10c4", ATTRS{idProduct}=="ea60", SYMLINK+="ttyUSB-ZStick-2G" </code>

Gen5:
<code>SUBSYSTEM=="tty", ATTRS{idVendor}=="0658", ATTRS{idProduct}=="0200", SYMLINK+="ttyUSB-ZStick-5G"</code>

=When you see no device=
 sudo mknod /dev/ttyUSB0 c 188 0
 sudo mknod /dev/ttyUSB1 c 188 1
And do the steps again.

=Restart and check results=
Restart (sudo reboot) with<br>
<code>sudo shutdown -r now</code><br>
After the reboot you should have two new serial ports (ttyUSB21,ttyUSB22), and they will always be assigned to the devices you have configured in the rules file.<br>

To use the new ports, in Domoticz go to the Setup -> Hardware webpage, highlight the RFXtrx433, and in the Serial Port dropdown list select the new Port 'ttyUSB21'. <br>
Then save.<br>
<br>
Alternatively, you can reload the udev rules without rebooting by running the following command:<br>
<code>sudo  udevadm control --reload</code><br>
Then disconnect and reconnect the USB device, to see if it works.

= Alternative filtering =
When there is a situation that there are more devices with for example the same vendor and product and have no serial number, you can use the command below to add some other filtering.
<code>
udevadm info -a -n /dev/ttyUSBX
</code>

Udevadm info starts with the device specified by the devpath and then walks up the chain of parent devices. It prints for every device found, all possible attributes in the udev rules key format. A rule to match, can be composed by the attributes of the device and the attributes from one single parent device.

Now compare the output of both devices and find some non-sumularities and add it to the 99-usb-serial.rules file

An example is to use the de devpath. The devpath is the number of the bus and port, for example ATTRS{devpath}=="3.1". To make this levels more visual you can use
<code>
lsusb -t
</code>
This gives an example output of

/:  Bus 02.Port 1: Dev 1, Class=root_hub, Driver=ehci_hcd/5p, 480M
    |__ Port 3: Dev 2, If 0, Class=hub, Driver=hub/4p, 480M
        |__ Port 1: Dev 7, If 0, Class=vend., Driver=pl2303, 12M

# Raspberry Pi Set up for Profile Node:<br> #
Step 1: Download Raspbian Jessie image from https://www.raspberrypi.org/downloads/raspbian/ <br>
Step 2: Write Raspbian Jessie image into SD card using Win32DiskImager <br>
Step 3: Plug in Raspberry Pi (with SD card) and switch on connecting it to a LCD Screen <br>
Step 4: Run `sudo apt-get update` and `sudo apt-get dist-upgrade`<br>
Step 5: Download the repository via `git clone git@github.com:alex-cobb/peatflux-code.git`.<br>
Step 5: Enable SSH, SPI and I2C in sudo raspi-config or from the desktop interface Raspberry Configuration.<br>
Step 6: To install the latest version of python software `sudo apt-get install python-dev`<br>
Step 7: Download/transfer the SPI-Py Repository `git clone https://github.com/lthiery/SPI-Py.git`<br>
Step 8: Run `sudo python setup.py build` to build and `sudo python setup.py install` to install the SPI-Py repository. <br>
Step 9: Type `sudo nano /boot/cmdline.txt` and add ip=192.168.0.X at the end of the line. <br>
*note: Add any desired statics IP that you want. <br>

# Passwordless SSH and SCP<br> #
Step 1: Run `ssh-keygen –t rsa`<br>
	Just “Enter” at “Enter passphrase” & “Enter same passphrase again”<br>
Step 2: Run `ssh pi@IPaddress mkdir –p .ssh` to create .ssh directory.<br>
Step 3: Run ` cat .ssh/id_rsa.pub | ssh pi@IPaddresss ‘cat >> .ssh/authorized_keys’`<br>
	Enter pi@IPaddress password (upload generated public keys to designation IP address)<br>
Step 4: Run `ssh pi@IPaddress “chmod 700 .ssh; chmod 640 .ssh/authorized_keys”` (Set Permission)<br>
Step 5: Run `ssh pi@IPaddress` (login server without password)<br>
*Note: Step 1 should not be repeated for master node because id_rsa.pub will already be generated when syncing with the first node. <br>

# DS18B20<br> #
To use the DS18B20 temperature sensor, following steps must be done. <br>
Step 1: Type `sudo nano /boot/config.txt`, scroll to the bottom and add “dtoverlay=w1-gpio”. Once done reboot `sudo reboot`<br>
Step 2: Run `sudo modprobe w1-gpio` and `sudo modprobe w1-therm`. Once done, open the device directory `cd /sys/bus/w1/devices`.<br>
Step 3: List out the directory in devices using `ls` and look for a directory starting with “28- <br>
Step 4: Open the “28- “ directory and type `cat w1-slave`.<br>
Step 5: Run ds18b20.py program `sudo python ds18b20.py` to check if the temperature sensor is working. <br>

# Set RTC Time<br> #
Step 1: Type `sudo nano /boot/config.txt` and add “dtoverlay=i2c-etc,ds1307” at the bottom of the script. Save it and reboot. `sudo reboot`<br>
Step 2: Run `sudo i2cdetect –y 1` to see if the UU shows up where 0x68 should be. <br>
Step 3: Disable the fake hwclock as it will interferes with the real hwclock. `sudo apt-get –y remove fake-hwclock` and `sudo update-rc.d –f fake-hwclock remove`<br>
Step 4: Run `sudo nano /lib/udev/hwclock-set` and comment out these three lines:<br>
	#if [ -e /run/systemd/system ]; then<br>
	# exit 0	<br>
	#fi<br>
Step 5: Check the time of the RTC Pi by using `sudo hwclock –r` or `timedatectl`<br>
Step 6: Run `sudo hwclock –w` to write the internet time to RTC Pi and run `sudo hwclock –r` to check if the time is sync. 
#NTP Client Set up<br>#
Step 1: Run `sudo nano /etc/ntp.conf` and edit the file. Add “tinker panic 0” on top of “driftfile /var/lib/ntp/ntp.drift” and edit the server to “server desired IP address iburst”. <br>
Step 2: Restart NTP on the local machine `sudo service ntp restart`	<br>
Step 3: Test the NTP server `ntpq –c lpeer` and see if there is any responses on the “delay, offset and jitter”<br>

# GPS Hat Set Up for Master Node<br> #
# Prerequisite Settings<br> #
Step 1: Run `sudo raspi-config`, go to Advance Options and disable serial shell (optional) and reboot `sudo reboot`.<br>
Step 2: run update `sudo rpi-update` once done, reboot `sudo reboot`.<br>
Step 3: Install `sudo apt-get install pps-tools`, `sudo apt-get install libcap-dev`, `sudo apt-get install libssl-dev` (may not need this) and `sudo dpkg-reconfigure tzdata` (unless you want all times in UTC) <br>
Step 4: Run `sudo nano /boot/config.txt’ and add “dtoverlay=pps-gpio, gpiopin=18. Save and close. <br>
Step 5: Run `sudo nano /etc/modules` and add “pps-gpio” at the bottom of the script. <br>
Step 6: Run `lsmod | grep pps` and the output should be “pps_gpio 2539 1 pps_core 7943 2 pps_gpio”<br>

# Verifying PPS is working<br> #
Step 1: Run `dmesg | grep pps` <br>
Output should be similar to: <br>
[ 0.000000] Kernel command line: dma.dmachans=0x7f35 bcm2708_fb.fbwidth=656 bcm2708_fb.fbheight=416 bcm2708.boardrev=0x10 bcm2708.serial=0x1a25ea38 smsc95xx.macaddr=B8:27:EB:25:EA:38 bcm2708_fb.fbswap=1 bcm2708.disk_led_gpio=47 bcm2708.disk_led_active_low=0 sdhci-bcm2708.emmc_clock_freq=250000000 vc_mem.mem_base=0x1ec00000 vc_mem.mem_size=0x20000000 dwc_otg.lpm_enable=0 console=tty1 root=/dev/mmcblk0p2 rootfstype=ext4 elevator=deadline rootwait<br>
[ 0.029423] bcm2708: GPIO 18 setup as pps-gpio device<br>
[ 10.159940] pps_core: LinuxPPS API ver. 1 registered<br>
[ 10.161448] pps_core: Software ver. 5.3.6 - Copyright 2005-2007 Rodolfo Giometti <giometti@linux.it><br>
[ 10.172015] pps pps0: new PPS source pps-gpio.18<br>
[ 10.173557] pps pps0: Registered IRQ 188 as PPS source <br>
Step 2: Run `sudo ppstest /dev/pps0`<br>
Output should be similar to: <br>
trying PPS source "/dev/pps0"<br>
found PPS source "/dev/pps0"<br>
ok, found 1 source(s), now start fetching data... <br>
source 0 - assert 1418933982.9980424, sequence: 970 - clear 0.0000000, sequence: 0<br>
source 0 - assert 1418933983.9980454, sequence: 971 - clear 0.0000000, sequence: 0<br>
(Press CTRL+C to quit).<br>
*Note: This indicates the PPS module is loaded(dmesg) and is working (ppstest)<br>

#Enabling PPS/ATOM support in NTPD<br>#
Step 1: Make sure your Raspberry Pi is connected with wifi. <br>
Step 2: Run `wget http://archive.ntp.org/ntp4/ntp-4.2/ntp-4.2.8p6.tar.gz`<br>
	         `tar zxvf ntp-4.2.8p6.tar.gz`<br>
	         `cd ntp-4.2.8p6`<br>
	         `./configure`<br>
	         `make`<br>
                 `sudo make install`<br>
	         `sudo service ntp stop`<br>
	         `sudo cp /usr/local/bin/ntp* /usr/bin/ && sudo cp /usr/local/sbin/ntp* /usr/sbin/<br>
	      
Step 3: Edit the file in `sudo nano /etc/ntp.conf` and add the lines “server 127.127.22.0 minpoll 4 maxpoll 4” and “fudge 127.127.22.0”<br>
Step 4: Amend the line to add the word “prefer” (server 0.debian.pool.ntp.org iburst prefer) Save and close once done. <br>
Step 5: Restart the NTP server using `sudo service ntp restart`<br>
Step 6: Run `ntpq –pn` to check if the data is receiving. <br>

# Getting the time stand-alone<br> #
Step 1: Disable Serial Shell go to `sudo raspi-config` -> Advance Option and disable Serial Shell (optional)<br>
Step 2: Reboot Raspberry Pi `sudo reboot`<br>
Step 3: Install minicom `sudo apt-get install minicom`<br>
Step 4: Run `minicom –b 9600 –o –D /dev/ttyAMA0` (Ctrl –A to exit minicom)<br>
Step 5: Disable tty using:<br>
	`sudo systemctl1 stop serial-getty@ttyS0.service`<br>
	`sudo systemctl1 disable seria-getty@ttys0.service`<br>
Step 6: Reboot the system `sudo shutdown –r now`<br>
Step 7: Install GPSD `sudo apt-get install gpsd gpsd-clients python-gps<br>
Step 8: Disable GPSD socket:<br>
	`sudo systemctl stop gpsd.socket`<br>
	`sudo systemctl disable gpsd.socket`<br>
Step 9: Edit the gpsd file `sudo nano /etc/default/gpsd` into <br>
`#Default settings for gpsd.`<br>
`#Please do not edit this file directly – use ‘dpkg-reconfigure gpsd’ to `<br>
`#change the options.`<br>
START_DAEMON=”true”<br>
GPSD_OPTIONS=”-n”<br>
DEVICES=”/dev/ttyS0”<br>
USBAUTO=”false”<br>
GPSD_SOCKET=”var/run/gpsd.sock”<br>
Step 10: Reboot again `sudo reboot`<br>

# Raspberry Pi 3 UART & Bluetooth complications<br> #
Step 1: Make sure your Raspberry Pi is on the latest update. Run `sudo apt-get update`, `sudo apt-get upgrade`, `sudo apt-get dist-upgrade` and `sudo rpi-update`. To check if there is any updates. <br>
Step 2: Edit config.txt file `sudo nano /boot/config.txt` and add 2 lines at the endof the file. <br>
	`#Allow the normal UART pins to work`<br>
	`dtoverlay=pi3-disable-bt-overlay`<br>
Step 3: Stop the Bluetooth modem from trying to use the UART<br>
	`sudo systemctl disable hciuart`<br>
Step 4: If you have “smsc95xx.turbo_mode=N in your /boot/cmdline.txt, remove it. <br>

# GPSD Software <br> #
Step 1: Install GPSD software `sudo apt-get install gpsd gpsd-clients python-gps<br>
Step 2: If there is error, re-run `sudo apt-get update` and `sudo apt-get upgrade`.<br>
Step 3: Try and start the gpsd service temporarily `sudo gpsd /dev/ttyAMA0 –n –F /var/run/gpsd.sock`<br>
Step 4: run `cgps –s` and there should be an output. <br>

# Configuring gpsd to auto-start<br> #
Step 1: Run `sudo nano /etc/default/gpsd` and edit the file to GPSD_OPTIONS=”-n”, USBAUTO=”false” and DEVICE=”/dev/ttyAMA0”.<br>
Step 2: If GPSD did not auto-start, run `sudo ln –s /lib/system/system/gpsd.service /etc/systemd/system/multi=user.targer.wants/<br>

# Raspbian Jessie system service fix <br> # 
To disable gpsd system service run `sudo systemctl stop gpsd.socket` and `sudo systemctl disable gpsd.socket`<br>

# Changes to your NTP configuration #
Edit the file in `sudo nano /etc/ntp.conf` and change/add in these lines:<br>
	#Kernel-mode PPS reference-clock for the precise seconds<br>
	server 127.127.22.0 minpoll 4 maxpoll 4<br>
	fudge 127.127.22.0 refid kPPS<br>

	#Coarse time reference-clock – nearest second<br>
	server 127.127.28.0. minpoll 4 maxpoll 4 iburst prefer<br>
	fudge 127.127.28.0. time1 +0.105 flag1 1 refid GPSD stratum 1<br>
Save and reboot after done. <br>
