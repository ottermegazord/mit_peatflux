"""Test code and data for communicating with Sungrow charge controller
"""

import cPickle
import datetime
import StringIO

from nose.tools import raises

import sungrow
import sungrow.sungrow_charge_controller as device_module


EPOCH = datetime.datetime(year=1970, month=1, day=1)


class TestStatusPage(object):
    """Tests for status page message
    """

    module = device_module
    cls = device_module.StatusPage

    def __init__(self):
        self.examples = [(example['raw_message'],
                          example['parameters'])
                         for example in self.cls.examples]

    def test_check_sum(self):
        """Test checksum for message
        """
        for raw_message, parameters in self.examples:
            digest = self.cls._get_digest(raw_message)
            checksum = self.cls._get_checksum(raw_message)
            assert digest == checksum, '{0} != {1}'.format(digest, checksum)

    def test_from_bytes(self):
        """Test .from_bytes() and .many_from_bytes() classmethods
        """
        for raw_message, parameters in self.examples:
            message = self.cls.from_bytes(raw_message)
            assert set(message.keys()) == set(parameters.keys()), \
                (set(message.keys()) ^ set(parameters.keys()))
            if dict(message) != parameters:
                for key, value in message.items():
                    assert value == parameters[key], \
                       u'message[{0}] = {1!r} != ref {2!r}'.format(\
                        key, value, parameters[key])
            else:
                assert dict(message) == parameters
            ## this exercises the regexp for the class
            messages = self.cls.many_from_bytes(raw_message)
            assert len(messages) == 1, \
                '{0}: {1} messages found in {2!r}'.format(self.cls,
                                                          len(messages),
                                                          raw_message)
            start, minus_length, many_message = messages[0]
            assert start == 0, start
            assert -minus_length == len(raw_message), \
                '{0}: {1} != {2}'.format(self.cls, -minus_length,
                                         len(raw_message))
            assert many_message == message, \
                '{0!r} != {1!r}'.format(many_message, message)

    def test_to_bytes(self):
        """Test .to_bytes()
        """
        for raw_message, parameters in self.examples:
            message = self.cls.from_bytes(raw_message)
            if 'datetime' in message and message['datetime'] == EPOCH:
                ## special-casing for bad datetime values; an issue with
                ##   sungrow charge controller
                return
            roundtrip = message.to_bytes()
            assert roundtrip == raw_message, \
                '{0!r} != {1!r}'.format(roundtrip, raw_message)


class TestStatusQuery(TestStatusPage):
    """Tests for status query message
    """

    cls = device_module.StatusQuery

    @raises(sungrow.ChecksumError)
    def test_bad_checksum(self):
        """Trying to unpack a message with bad checksum raises ChecksumError
        """
        raw_message, parameters = self.examples[0]
        raw_message = bytearray(raw_message)
        raw_message[-1] = ~raw_message[-1] & 255
        self.cls.from_bytes(raw_message)


class TestHistoryQuery(TestStatusPage):
    """Tests for history query message
    """

    cls = device_module.HistoryQuery


class TestConfigurationQuery(TestStatusPage):
    """Tests for configuration query message
    """

    cls = device_module.ConfigurationQuery


class TestHistoryPage(TestStatusPage):
    """Test history page message
    """

    cls = device_module.HistoryPage


class TestConfigurationPage(TestStatusPage):
    """Test configuration page message
    """

    cls = device_module.ConfigurationPage


class TestDevice(object):
    """Test sungrow charge controller device
    """

    module = device_module

    def __init__(self):
        self.data_stream = StringIO.StringIO()
        ##  use this buffer as data stream for all message types
        data_streams = dict((name, self.data_stream)
                            for name in self.module.Device.message_types)
        self.device = self.module.Device(data_streams=data_streams)

    @raises(sungrow.BadBinaryMessage)
    def test_bad_unpack(self):
        """Trying to unpack a weird string raises BadBinaryMessage
        """
        self.device.unpack('aardvark')

    def test_message_classes(self):
        """Perform tests on all message classes
        """
        for message_class in self.device.message_types.values():
            for example in message_class.examples:
                self._message_unpack_pack_test(message_class, example)
                self._message_log_test(message_class, example)
                self._message_pickle_test(message_class)

    def _message_unpack_pack_test(self, message_class, example):
        """Test unpacking and packing of example from message_class
        """
        message = self.device.unpack(example['raw_message'])
        assert type(message) == message_class
        if 'datetime' in message and message['datetime'] == EPOCH:
            ## special-casing for bad datetime values; an issue with
            ##   sungrow charge controller
            return
        roundtrip = self.device.pack(message)
        assert roundtrip == example['raw_message']

    def _message_pickle_test(self, message_class):
        """Test pickling and unpickling of message class
        """
        pickle = cPickle.dumps(message_class)
        unpickled = cPickle.loads(pickle)
        assert unpickled == message_class, \
            '{0} != {1}'.format(unpickled, message_class)

    def _message_log_test(self, message_class, example):
        """Test that a log message is sent to the log stream on read
        """
        ## empty the data buffer
        self.data_stream.truncate(0)
        message = self.device.unpack(example['raw_message'])
        self.device.respond(message)
        self.data_stream.flush()
        logged_data = self.data_stream.getvalue()
        string_values = logged_data.strip().split(',')[1:]
        if len(message) == 0:
            expected = []
        else:
            ## this one is special
            multirow_cls = sungrow.sungrow_charge_controller.HistoryPage
            if isinstance(message, multirow_cls):
                import os
                string_values = zip(*[line.split(',')[1:] for line in
                                      logged_data.strip().split(os.linesep)])
                expected = [tuple(str(v) for v in message[key])
                            for key in message.names]
            else:
                ## first field is datetime, we don't check this one
                expected = [str(message[key]) for key in message.names]
        assert string_values == expected, \
            'logged values {0} != {1}'.format(string_values,
                                              expected)

    def test_pickle(self):
       """Test pickling of object
       """
       s = cPickle.dumps(self.device)
       o = cPickle.loads(s)
       assert o.log.name == self.device.log.name


def test_bad_checksum_example():
    """Bad checksums do not raise a fatal error in device.messages_from_bytes()
    """
    raw_message = '\xed\x03\x00\x00\x00\x00\x00\x00\x00\x00\x00\x1c\x00\x00\x02\x17\x00\x00\x00\x1c\x00\x00\x00\x1a\x00\x001\xee\x00\x00\x04E\x00\x00-\xa9\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x08\x00\x00\x02\xb4\x00\x00\x00l\x00\x00\x04\x00'
    device = device_module.Device()
    messages = device.messages_from_bytes(raw_message)
    ## no valid messages here, checksum is bad
    assert messages == []
