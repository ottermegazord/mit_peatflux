# Li-7000 Repository
Copyright (c) 2016
Idaly Ali
All rights reserved.

License information
-------------------

See the file "LICENSE" for information on the history of this
software, terms & conditions for usage, and a DISCLAIMER OF ALL
WARRANTIES.

All trademarks referenced herein are property of their respective
holders.

What is pyli7000?
-------------------

This is a Python library and script for interacting with the LICOR
LI-7000 H2O and CO2 gas analyser system using RS232 serial interface

Classes
-------------------

Native ports

class_li7000.li7000
__init__(self, port, baudrate)

Parameters:
    - port - Device name, dependent on operating system. For example,
    on GNU/Linux system "/dev/ttyUSB0"
    - baudrate (int) - Baudrate (9600|19200|38400|57600|115200)

As soon as object is created, port will be be immediately opened

li7000_pollnow()
Query instrument measurement
Output: (str)



