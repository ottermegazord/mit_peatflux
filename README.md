
# peatflux-code

Welcome to the peatflux-code!

# Running a script as a service in Raspbian Jessie #

GE50A USB
SUBSYSTEM=="tty", ATTRS{idVendor}=="0403", ATTRS{idProduct}=="6001", ATTRS{serial}=="FTZ1T3BU", SYMLINK+="ttyUSB-ge50a"
LI7000 USB
SUBSYSTEM=="tty", ATTRS{idVendor}=="0403", ATTRS{idProduct}=="6001", ATTRS{serial}=="FTYNX3XV", SYMLINK+="li7000"
LI840
SUBSYSTEM=="tty", ATTRS{idVendor}=="0403", ATTRS{idProduct}=="6001", ATTRS{serial}=="FTWD9PPQ", SYMLINK+="li840"


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
The RFXtrx433 is reported as:

  idVendor           0x0403 Future Technology Devices International, Ltd
  idProduct          0x6001 FT232 USB-Serial (UART) IC
  iProduct                2 RFXtrx433
  iSerial                 3 07VYAR1X

Aeon ZWave USB stick is reported as:

  idVendor           0x10c4 Cygnal Integrated Products, Inc.
  idProduct          0xea60 CP210x UART Bridge / myAVR mySmartUSB light

You need the part behind the '0x'. So you don't write down '0x0403' but '0403'.

=Creating rules file=
Create a rules file, with the following example content:

sudo nano /etc/udev/rules.d/99-usb-serial.rules

=== RFX-433 ===

Put the following content in the file:

<code>SUBSYSTEM=="tty", ATTRS{idVendor}=="0403", ATTRS{idProduct}=="6001", ATTRS{serial}=="123YAOOW", SYMLINK+="ttyUSB-RFX433-A"

SUBSYSTEM=="tty", ATTRS{idVendor}=="0403", ATTRS{idProduct}=="6001", ATTRS{serial}=="123YX78C", SYMLINK+="ttyUSB-RFX433-B"</code>

(Put in the values you've written down between the quotes (e.g. replace '0403' with the idVendor of your USB device).

Some devices don't show a serial, you can remove that part in the file, so it looks like this:

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

