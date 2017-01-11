# -*- coding: utf-8 -*-

"""Sungrow charge controller device and messages
"""

import datetime
import logging
import struct

import sungrow.sungrow_message

DEVICE_TYPE = 'sungrow_charge_controller'

LOG = logging.getLogger('sungrow.sungrow_charge_controller')


class Query(sungrow.sungrow_message.Message):
    """Sungrow charge controller query

    Simple queries are 4-byte messages with no parameters and a 1-byte checksum
    """

    device_type = DEVICE_TYPE
    _data = NotImplemented
    code = NotImplemented
    _signature = NotImplemented
    struct_string = NotImplemented
    _digest_bytes = 1

    @classmethod
    def _get_digest(cls, raw_message):
        """Compute big-endian sum from raw_message[:cls._digest_bytes]
        """
        num_bytes = cls._digest_bytes
        mod = 1 << (8 * num_bytes)
        return sum(bytearray(raw_message[:-num_bytes])) % mod

    @classmethod
    def _get_digest_struct(cls):
        """Get correct struct for message digest
        """
        num_bytes = cls._digest_bytes
        if num_bytes == 1:
            return '>B'
        else:
            assert num_bytes == 4
            return '>I'

    @classmethod
    def _get_checksum(cls, raw_message):
        """Get checksum from last bytes of raw_message
        """
        digest_struct = cls._get_digest_struct()
        num_bytes = struct.calcsize(digest_struct)
        return struct.unpack(digest_struct, str(raw_message[-num_bytes:]))[0]

    def to_bytes(self):
        """Produce native-format bytestring from message
        """
        return self._signature


class Message(Query):
    """Sungrow charge controller message

    Longer messages have a 4-byte checksum
    """

    _digest_bytes = 4


class StatusQuery(Query):
    """Sungrow status query
    """

    regexp = '\xed\x03\x03\xf3'


class HistoryQuery(Query):
    """Sungrow history query
    """

    regexp = '\xed\x05\x09\xfb'


class ConfigurationQuery(Query):
    """Sungrow configuration query
    """

    regexp = '\xed\x06\x26\x19'


class ConfigurationPage(Message):
    """Sungrow charge controller configuration page
    """

    regexp = '\xed\x06\x26\x19[^z]+z.{4}'

    @classmethod
    def from_bytes(cls, raw_message):
        """Create message from native-format bytestring
        """
        cls._verify_message(raw_message)
        content = raw_message[4:-4]
        ## These messages are null-separated text fields
        raw_values = content.split('\0')
        ## last value should be a terminator, 'z'
        terminator = raw_values.pop()
        if terminator != 'z':
            raise sungrow.BadBinaryMessage('last field is %s, '
                                           'not terminator ("z")' %
                                           terminator)
        keys = cls.names
        if len(raw_values) != len(keys):
            raise sungrow.BadBinaryMessage('%d fields, %d expected' %
                                           (len(raw_values), len(keys)))
        message = cls._raw_to_user_parameters(zip(keys, raw_values))
        assert set(message.keys()) == set(cls.names), \
            '{0} != {1}'.format(message.keys(), cls.names)
        return cls(message)

    def to_bytes(self):
        """Produce native-format bytestring from message
        """
        raw_values = [bytes(self[key]) for key in self.names]
        ## terminator
        raw_values += ['z']
        content = '\0'.join(raw_values)
        signature = sungrow.hex_to_bytes(self.code)
        ## placeholder for checksum
        checksum_placeholder = '    '
        raw_message = bytearray(''.join((signature,
                                         content,
                                         checksum_placeholder)))
        ## now compute real checksum
        digest = self._get_digest(raw_message)
        struct.pack_into('>I', raw_message, -4, digest)
        self._verify_message(raw_message)
        return bytes(raw_message)


class HistoryPage(Message):
    """Sungrow charge controller history page
    """

    ## all these guys are in tenths of a unit
    _tenths = ('daily_battery_voltage_maximum',
               'daily_battery_voltage_minimum')
    regexp = '\xed\x05\x09\xfb.{244}'

    @classmethod
    def from_bytes(cls, raw_message):
        """Create message from native-format bytestring
        """
        cls._verify_message(raw_message)
        raw_values = struct.unpack(cls._data['struct'], raw_message)
        assert len(cls._raw_keys) == 4
        ## discard signature and checksum
        values = list(raw_values[1:-1])
        ## there are 4 groups of 30-day records
        assert len(values) == 30 * 4
        values = [values[(i * 30):((i + 1) * 30)] for i in range(4)]
        message = cls(zip(cls._raw_keys, values))
        for key in cls._tenths:
            message[key] = [value * 0.1 for value in message[key]]
        return message

    def to_bytes(self):
        """Produce native-format bytestring from message
        """
        raw_values = [self._signature]
        for key in self.names:
            if key in self._tenths:
                seq = [int(round(value * 10)) for value in self[key]]
            else:
                seq = self[key]
            raw_values += seq
        ## dummy checksum, for now
        raw_values.append(0)
        raw_message = bytearray(self.length)
        ## * magic okay here; pylint: disable=W0142
        struct.pack_into(self._data['struct'], raw_message, 0, *raw_values)
        ## now compute real checksum
        num_bytes = 4
        mod = 1 << (8 * num_bytes)
        digest = sum(raw_message[:-num_bytes]) % mod
        struct.pack_into('>I', raw_message, -num_bytes, digest)
        self._verify_message(raw_message)
        return bytes(raw_message)

    def format_data(self, read_time, delimiter=','):
        """Create a delimited text version of message, ordered per names

        For a history page, this results in one row per day for 30 days
        """
        ## note that this does not conform to sungrow.config.DATE_FORMAT,
        ##   which is really for datetimes for LOG messages and the like
        date_format = '%Y-%m-%d'
        values = [self[key] for key in self.names]
        lines = zip(*values)  # pylint: disable=W0142
        if len(lines) != 30:
            LOG.warning('unexpected number of lines: '
                        '{0} != 30'.format(len(lines)))
        start = datetime.date(year=read_time.year,
                              month=read_time.month,
                              day=read_time.day)
        dates = [start - datetime.timedelta(days=days) for days
                 in range(len(lines))]
        lines = [[dates[i].strftime(date_format)] + [str(v) for v in line]
                  for i, line in enumerate(lines)]
        import os
        return os.linesep.join(','.join(line) for line in lines)


class StatusPage(Message):
    """Sungrow charge controller status page
    """

    _discard = {'signature': '\xed\x03\x00\x00',
                'checksum': '    '}
    regexp = '\xed\x03\x00\x00.{56}'

    @classmethod
    def from_bytes(cls, raw_message):
        """Create message from native-format bytestring
        """
        cls._verify_message(raw_message)
        raw_values = struct.unpack(cls._data['struct'], raw_message)
        raw = dict(zip(cls._raw_keys, raw_values))
        message = cls._raw_to_user_parameters(raw)
        cls._assert_keys_ok(message.keys())
        return cls(message)

    def to_bytes(self):
        """Produce native-format bytestring from message
        """
        raw = self._to_raw_parameters()
        raw_message = self._raw_parameters_to_bytes(raw)
        self._verify_message(raw_message)
        return raw_message


import sungrow.config
import sungrow.device


class Device(sungrow.device.Device):
    """Sungrow charge controller object
    """
    name = 'sungrow_charge_controller'
    message_types = {'status_query': StatusQuery,
                     'history_query': HistoryQuery,
                     'configuration_query': ConfigurationQuery,
                     'status_page': StatusPage,
                     'history_page': HistoryPage,
                     'configuration_page': ConfigurationPage}
    handled_message_types = (StatusPage,
                             HistoryPage,
                             ConfigurationPage)
    data = sungrow.config.DEVICE_TYPE_DATA[name]
    ## first four bytes, total number of bytes; None for indefinite
    _signatures = dict((key, (sungrow.hex_to_bytes(value['code']),
                              value['length']))
                       for key, value in data['messages'].items())
    _message_types = dict((value, key) for key, value in
                         _signatures.items())
    sungrow.device.Device._add_message_class_data()

    @classmethod
    def unpack(cls, message):
        """Unpack raw message into a message object of appropriate type
        """
        this_signature = message[:4]
        this_length = len(message)
        candidates = [(signature, length) for signature, length
                      in cls._message_types if
                      signature == this_signature and
                      (length is None or length == this_length)]
        if not candidates:
            error_message = ('no known message with signature {0!r} '
                             'and length {1}').format(this_signature,
                                                      this_length)
            raise sungrow.BadBinaryMessage(error_message)
        if len(candidates) > 1:
            candidates = [(signature, length) for signature, length
                          in candidates if length is not None]
        assert len(candidates) == 1, candidates
        message_type_name = cls._message_types[candidates[0]]
        assert message_type_name in cls.message_types
        return cls.message_types[message_type_name].from_bytes(message)


class Emulator(Device):
    """Sungrow charge controller emulator
    """

    handled_message_types = (StatusQuery,
                             HistoryQuery,
                             ConfigurationQuery)
    respond = Device.emulate_response
    Device._add_message_class_data()
