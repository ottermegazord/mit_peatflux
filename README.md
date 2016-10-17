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