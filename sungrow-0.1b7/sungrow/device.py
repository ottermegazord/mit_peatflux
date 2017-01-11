"""Device objects

The device knows the message type, so only the device can know
when a complete message has been received.  The device reads the
port, looking for the starting signature of a message, and then
continues to read until it reaches the end of the message. Depending
on the device type, this can happen after a fixed number of bytes,
after a number of bytes determined by the message header, or when
a magic character or characters are encountered.

The device is responsible for finalization and release of resources
associated with a port after a raw message read or write.
"""

import datetime
import logging

import sungrow.config
import sungrow.data_logging


class Device(object):
    """Device object

    data_streams: mapping from message type names to the stream to which
                  their data records are written, default sys.stdout.
                  Stream can be text, in which case it is interpreted
                  as a file name, or a file-like object
    device_id: a name for the device, used in error log messages.
               Default is name associated with class
    """

    name = NotImplemented
    message_types = {}
    handled_message_types = ()

    def __init__(self, data_streams=None, device_id=None):
        if device_id is None:
            if self.name != NotImplemented:
                device_id = self.name
            else:
                device_id = 'device'
        self.device_id = device_id
        self.log = logging.getLogger('sungrow.{0}'.format(device_id))
        if data_streams is None:
            data_streams = {}
        data_logger_cls = sungrow.data_logging.DataLogger
        self.log_data = dict((key, data_logger_cls(data_stream))
                             for key, data_stream in data_streams.items())

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

    @classmethod
    def pack(cls, message):
        """Pack a message mapping into a binary message
        """
        return message.to_bytes()

    @classmethod
    def unpack(cls, raw_message):
        """Unpack binary message into a message of appropriate type
        """
        ## Base implementation: try all message types until one of
        ##   them doesn't throw BadBinaryMessage
        message = None
        for message_type in cls.message_types.values():
            try:
                return message_type.from_bytes(raw_message)
            except sungrow.BadBinaryMessage:
                continue
        if message is None:
            raise sungrow.BadBinaryMessage('{0!r}'.format(raw_message))

    def _reverse_name_lookup(self, message):
        """Find the name associated with the type of a message
        """
        reverse_mapping = dict((value, key) for key, value in
                               self.message_types.items())
        return reverse_mapping[type(message)]

    def respond(self, message, read_time=None):
        """Respond to a new message

        read_time is the time at which the raw message was read from
        the port

        Any responses will be returned as a sequence of messages

        If the device has a data stream associated with a message type,
        it is logged to the corresponding data stream.
        """
        self.log.debug('received message {0}'.format(message))
        name = self._reverse_name_lookup(message)
        if name in self.log_data:
            self.log.debug('have data stream for %s' % name)
            if read_time is None:
                read_time = datetime.datetime.now()
            self.log_data[name](message, read_time)
        else:
            self.log.debug('no data stream for %s' % name)
        return []

    ## read_time is not used for response emulation
    ## pylint: disable=W0613
    def emulate_response(self, message, read_time=None):
        """Handle a new message, returning any response

        Returns a sequence of messages, the emulated device's response
        """
        name = self._reverse_name_lookup(message)
        if not name.endswith('query'):
            raise ValueError('I only reply to messages that end with '
                             '"query"')
        page_name = '{0}_page'.format(name.split('_')[0])
        message_type = self.message_types[page_name]
        message = self.unpack(message_type.examples[0]['raw_message'])
        return [message]

    @classmethod
    def messages_from_bytes(cls, bytestring):
        """Find all valid handled messages in bytestring

        The returned sequence is the concatenation of sequences
        obtained by calling message_class.many_from_bytes(bytestring)
        for each message class in this_class.handled_message_types, in
        no particular order.

        Each item in the return sequence is a
        (start_byte, negative_length, message) tuple;
        negative_length is present as a tiebreaker to facilitate
        sorting by earliest-starting and longest messages.

        The matched portions of the bytestring may overlap!  It is up
        to the caller to resolve any such conflicts.
        """
        return sum((message_class.many_from_bytes(bytestring)
                    for message_class in cls.handled_message_types), [])

    @classmethod
    def _add_message_class_data(cls):
        """Add class data to all message classes
        """
        for name, message_class in cls.message_types.items():
            ## pylint: disable=W0212
            message_class._add_class_data(name, cls.name)
