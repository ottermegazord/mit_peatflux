"""Sungrow inverter device and messages
"""

import datetime
import struct

import sungrow.device
import logging
import sungrow.modbus
import sungrow.sungrow_message

DEVICE_TYPE = 'sungrow_inverter'
LOG = logging.getLogger('sungrow.sungrow_inverter')
EPOCH = datetime.datetime(year=1970, month=1, day=1)


class Message(sungrow.sungrow_message.Message):
    """Sungrow inverter message
    """

    device_type = DEVICE_TYPE
    _data = NotImplemented
    code = NotImplemented
    _signature = NotImplemented
    length = 13
    names = NotImplemented

    @classmethod
    def _get_digest(cls, raw_message):
        """Compute message's little-endian MODBUS 16-bit CRC
        """
        return sungrow.modbus.compute_crc(bytearray(raw_message[:-2]))

    @classmethod
    def _get_digest_struct(cls):
        """Get correct struct for message digest
        """
        return '<H'

    @classmethod
    def _set_checksum(cls, raw_message):
        """Insert checksum into bytearray raw_message
        """
        digest = cls._get_digest(raw_message)
        digest_size = struct.calcsize('<H')
        struct.pack_into('<H', raw_message, -digest_size, digest)

    @classmethod
    def _get_checksum(cls, raw_message):
        """Get checksum from raw_message
        """
        return struct.unpack('<H', str(raw_message[-2:]))[0]

    def to_bytes(self):
        """Produce native-format bytestring from message
        """
        raw_message = bytearray(self.length)
        offset = len(self._signature)
        raw_message[:offset] = self._signature
        digest = sungrow.modbus.compute_crc(raw_message[:-2])
        struct.pack_into('<H', raw_message, -2, digest)
        self._verify_message(raw_message)
        return raw_message


class StatusQuery(Message):
    """Sungrow inverter status query
    """

    regexp = '\x01\x03\x07\x00\x01.{8}'


class StatusPage(Message):
    """Sungrow inverter status page
    """

    regexp = '\x01\x03\^\x00\x01.{95}'
    ## discarded fields, with apparent defaults from the docs
    _discard = {'signature': '\x01\x03\x5e\x00\x01',
                ## uh, okay, why not?
                'unused_0': '\x64\x00\x00\x00\x10\x01\x20\x01\x00\x00',
                'unused_1': '\xdc\x00\xb0\x04\x64',
                'unused_2': '\x00\x00\x00\x00',
                'unused_3': '\x00\x00',
                'checksum': '    '}

    @classmethod
    def from_bytes(cls, raw_message):
        """Create message from native-format bytestring
        """
        cls._verify_message(raw_message)
        assert struct.calcsize(cls._data['struct']) == cls.length
        raw_values = struct.unpack(cls._data['struct'], raw_message)
        assert len(cls._raw_keys) == len(raw_values), \
            '%s != %s' % (len(cls._raw_keys), len(raw_values))
        raw = dict(zip(cls._raw_keys, raw_values))
        message = cls._raw_to_user_parameters(raw)
        ## datetime is BCD
        stamp = [int(hex(ord(o))[2:])
                 for o in message['datetime']]
        stamp[5] += stamp[6] * 100
        del stamp[6]
        ## have gotten month of "0" in real data, disallowed by docs, which say
        ##   second in [0..59]
        ##   minute in [0..59]
        ##   hour in [0..23]
        ##   day in [1..31]
        ##   month in [1..12]
        ##   year in [2000..2099]
        ## So until we know more about the real behaviour of the time stamp,
        ##   we just issue a warning and use the epoch to indicate nodata
        try:
            message['datetime'] = datetime.datetime(year=stamp[5],
                                                    month=stamp[4],
                                                    day=stamp[3],
                                                    hour=stamp[2],
                                                    minute=stamp[1],
                                                    second=stamp[0])
        except ValueError:
            LOG.warning('bad datetime in {0}, using epoch'.format(stamp))
            message['datetime'] = EPOCH
        return cls(message)

    def to_bytes(self):
        """Produce native-format bytestring from message
        """
        raw = self._to_raw_parameters()
        ## turn timestamp back into BCD
        timestamp = raw['datetime'].strftime('%S %M %H %d %m %Y')
        ## split years into pairs of digits
        timestamp = '{0} {1} {2}'.format(timestamp[:-5],
                                         timestamp[-2:],
                                         timestamp[-4:-2])
        timestamp = sungrow.hex_to_bytes(timestamp)
        raw['datetime'] = timestamp
        raw_message = self._raw_parameters_to_bytes(raw)
        self._verify_message(raw_message)
        return raw_message


class Device(sungrow.device.Device):
    """Communication interface with Sungrow inverter

    Byte 0 is the address, byte 1 the command (always 0x03), and
    bytes 1-2 give the size of the data region in a little-endian
    short.

    The inverter receives a 13-byte request, including a 2-byte cyclic
    redundancy check (bytes 11 and 12 numbered from 0, i.e., the last
    two bytes). There is only one acceptable request type for the
    inverter. The inverter will emulate_response with a 100-byte response with
    a 2-byte little-endian MODBUS cyclic redundancy check (bytes
    98-99).
    """

    name = DEVICE_TYPE
    message_types = {'status_query': StatusQuery,
                     'status_page': StatusPage}
    handled_message_types = (StatusPage,)
    _signatures = {'status_query': ('\x01\x03\x07\x00', 13),
                   'status_page': ('\x01\x03\x94\x00', 100)}
    ## message class data from external data files
    sungrow.device.Device._add_message_class_data()


class Emulator(Device):
    """Sungrow inverter emulator
    """

    handled_message_types = (StatusQuery,)
    respond = Device.emulate_response
    Device._add_message_class_data()
