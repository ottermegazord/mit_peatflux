"""Outback charge controller device and messages
"""

import sungrow.message

DEVICE_TYPE = 'outback_charge_controller'


class StatusPage(sungrow.message.Message):
    """Outback charge controller status page
    """

    device_type = DEVICE_TYPE
    _digest_bytes = 3
    length = NotImplemented
    _data = NotImplemented
    names = NotImplemented
    regexp = '\n.[0-9,]{46}\r'

    @classmethod
    def _get_digest(cls, raw_message):
        """Compute digest of message

        Digest is sum of all the (non-comma, non-whitespace) ASCII
        decimal values in the message, except that the value for the
        address is the ASCII code for the character minus 48; for
        example, the value for 'A' is ord('A')-48, or 17
        """
        raw_message = raw_message.strip().replace(',', '')
        content = raw_message[:-cls._digest_bytes]
        ## address is treated specially; A corresponds to 17
        address_value = ord(content[0]) - 48
        return sum((int(c) for c in content[1:]), address_value)

    @classmethod
    def _get_checksum(cls, raw_message):
        """Get checksum from last num_bytes of raw_message
        """
        return int(raw_message[-cls._digest_bytes:])

    @classmethod
    def from_bytes(cls, raw_message):
        """Create message from native-format bytestring
        """
        cls._verify_message(raw_message)
        raw_values = raw_message.strip().split(',')
        assert len(cls._raw_keys) == len(raw_values), \
            '%s != %s' % (len(cls._raw_keys), len(raw_values))
        raw = dict(zip(cls._raw_keys, raw_values))
        ## bit 7 of aux_mode is flag for aux mode being active
        aux_mode = int(raw['aux_mode'])
        aux_mode_active = bool(aux_mode & 64)
        if aux_mode_active:
            aux_mode -= 64
        raw['aux_mode'] = aux_mode
        message = cls._raw_to_user_parameters(raw)
        message['address'] = ord(message['address']) - 65
        charge_current = message['charge_current']
        charge_current_tenths = message.pop('charge_current_tenths')[1]
        charge_current = float('{0}.{1}'.format(charge_current,
                                                charge_current_tenths))
        message['charge_current'] = charge_current
        message['aux_mode_active'] = aux_mode_active
        cls._assert_keys_ok(message.keys())
        return cls(message)

    def to_bytes(self):
        """Produce native-format bytestring from message
        """
        raw = self._to_raw_parameters()
        raw['address'] = chr(raw['address'] + 65)
        charge_current = raw['charge_current']
        raw['charge_current'] = int(charge_current)
        raw['charge_current_tenths'] = int((charge_current * 10) % 10)
        aux_mode_active = raw.pop('aux_mode_active')
        raw['aux_mode'] |= int(aux_mode_active) << 7
        ref_key_set = set(self._raw_keys)
        assert set(raw.keys()) == ref_key_set, \
            (set(raw.keys()) ^ ref_key_set)
        ## ** magic okay here; pylint: disable=W0142
        raw_message = self._format.format(**raw)
        digest = self._get_digest(raw_message)
        raw_message = '{0}{1:0>3}\r'.format(raw_message[:-4], digest)
        self._verify_message(raw_message)
        return raw_message


import sungrow.device


class Device(sungrow.device.Device):
    """Outback charge controller
    """

    name = DEVICE_TYPE
    message_types = {'status_page': StatusPage}
    handled_message_types = (StatusPage,)
    sungrow.device.Device._add_message_class_data()

    ## pylint: disable=W0613
    def emulate_response(self, message, read_time=None):
        """Handle a of new message, returning any responses

        The Outback charge controller sends a status page at 1 Hz, no
        matter what.  At this point, it doesn't respond to anything,
        so this method just returns a status page
        """
        message_type = self.message_types['status_page']
        message = self.unpack(message_type.examples[0]['raw_message'])
        return [message]


class Emulator(Device):
    """Outback charge controller emulator
    """

    handled_message_types = ()
    respond = Device.emulate_response
    Device._add_message_class_data()


## pylint: disable=W0212
StatusPage._format = ','.join(StatusPage._data['format'])
