"""Bus object implementation
"""

import datetime
import logging


class Bus(object):
    """Bus objects

    A bus consists of one or more devices associated with a port and
    represents an interface that reads bytes off of the port and passes
    messages to devices and vice versa, writing bytes from devices
    onto the port.  Incoming data from the port, obtained with read()
    is buffered internally to retain stubs that may represent the
    beginning of incomplete messages; reads from the port should be
    non-blocking.  Outgoing data is not buffered but is written
    directly to the port using its write() method.

    port is an object that provides .read() and .write() methods
    devices is a {device_name: device, ...} mapping of device objects
    """
    def __init__(self, port, devices, online=False):
        self.port = port
        self.devices = devices
        self._read_buffer = ''
        self.log = logging.getLogger('sungrow.bus.{0}'.format(port.url))
        self.online = online
        self._back_online = False

    def __getstate__(self):
        """Retrieve internal state for pickling
        """
        state = self.__dict__.copy()
        log = state.pop('log')
        state['logger_name'] = log.name
        return state

    def __setstate__(self, state):
        """Set internal state for unpickling
        """
        state['log'] = logging.getLogger(state['logger_name'])
        self.__dict__.update(state)

    def is_back_online(self):
        """Check whether bus has come back online after being offline

        Returns True if a communication has succeeded where a previous
        one (if any) had failed.  Successful communication is any
        raw read that exits without raising an exception.
        """
        return self._back_online

    def _update_online_status(self, communication_okay):
        """Update internal state regarding whether bus is online

        In addition to marking bus as online or offline, also
        updates whether bus is back online.  If communication_okay
        and bus had been offline, marks as back online, otherwise
        as not back online.
        """
        self._back_online = not self.online and communication_okay
        self.online = communication_okay

    def read(self):
        """Read bytes from bus

        returns (read_time, raw_message)
        """
        try:
            buf = ''.join((self._read_buffer, self.port.read()))
        except:
            self._update_online_status(False)
            raise
        else:
            self._update_online_status(True)
        self._read_buffer = buf
        read_time = datetime.datetime.now()
        return (read_time, self._read_buffer)

    def write(self, raw_message):
        """Write bytes to bus
        """
        self.port.write(raw_message)

    def receive_messages(self):
        """Read any new data and convert to messages

        When this method is called, all available data is read from
        the port and appended to the internal read buffer.  The
        messages_from_bytes() method of each device on the bus is used
        to indicate any portions of data that represent valid messages
        for that device; then the bus determines a set of
        non-overlapping valid messages of maximum length starting from
        the beginning of the read data.  Each non-overlapping valid
        message is pushed onto the incoming message queue, which is then
        returned.

        Returns (read_time, message queue) where read_time is a datetime
        object indicating when the read off the port occurred and
        messages is a sequence of (device_name, message) duples
        """
        read_time, buf = self.read()
        all_messages = []
        for device_name, device in self.devices.items():
            all_messages += [message_tuple + (device_name,) for
                             message_tuple in device.messages_from_bytes(buf)]
        ## these matches may overlap
        all_messages.sort()
        messages = []
        first_unused_byte = 0
        for start_byte, neg_length, message, device_name in all_messages:
            ## skip over any matches that start before end of last
            ##   valid match
            if start_byte < first_unused_byte:
                continue
            ## this is a non-overlapping match, add it to message
            ##   queue
            messages.append((device_name, message))
            self.log.debug('received {0} for {1}'.format(\
                    type(message).__name__, device_name))
            length = -neg_length
            first_unused_byte = start_byte + length
        ## leave only unprocessed text
        self._read_buffer = buf[first_unused_byte:]
        self.log.debug('{0} message(s) received'.format(len(messages)))
        return (read_time, messages)

    def send_messages(self, messages):
        """Write messages to port

        messages is a sequence of (device_name, message) duples
        """
        for device_name, message in messages:
            raw_message = self.devices[device_name].pack(message)
            self.write(raw_message)
            self.log.debug('sent {0} from {1}'.format(type(message).__name__,
                                                      device_name))
        self.log.debug('{0} message(s) sent'.format(len(messages)))

    def handle_incoming_messages(self):
        """Receive and allow device to respond to incoming messages
        """
        read_time, messages = self.receive_messages()
        for device_name, message in messages:
            responses = self.devices[device_name].respond(message,
                                                          read_time)
            self.send_messages([(device_name, response) for response in
                                responses])
