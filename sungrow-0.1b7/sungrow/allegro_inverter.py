r"""Allegro inverter device and messages

Communication is RS232 4800Baud, 8N1

The manual indicates that upon connection with a terminal, the following
information is displayed:
*0 ASP ALLEGRO V1.1 1000/24, 230V/50Hz
*1 Vbatt = 24.7 Vdc
*2 Vout = 227 Vac
*3 Pac = 930 W
*4 Tint = 35 Cels
*5 Sby Level=99
*6 Remote enabled
*7 YOUR COMMAND:++
*8 (00-99,++,--),<ENTER>
*9 Legend:
*A 00=Continuous
*B 01-98=Sby Level
*C 99=Off
*D ++=Remote enable (On)
*E --=Remote disable (Off)

All commands need to be followed by "enter", presumably '\r\n'.

Remote interaction is enabled by entering '++'; this disables the
front-panel potentiometer.  Disabling interaction with '--'
re-activates the front-panel potentiometer.
"""

import re

import sungrow
import sungrow.device
import sungrow.message

DEVICE_TYPE = 'allegro_inverter'


class Message(sungrow.message.Message):
    """ASP Allegro inverter message
    """

    device_type = DEVICE_TYPE
    _signature = NotImplemented

    @classmethod
    def _get_checksum(cls, raw_message):
        """Compute digest of raw_message

        Allegro inverter messages contain no checksum, so this always
        returns the empty string.
        """
        return ''

    @classmethod
    def _get_digest(cls, raw_message):
        """Compute digest of raw_message

        Allegro inverter messages have no checksum convention, so this
        always returns the empty string.
        """
        return ''

    def to_bytes(self):
        """Produce native-format bytestring from message
        """
        return self._signature


class EnableRemote(Message):
    """ASP Allegro inverter enable_remote message
    """

    _signature = '++'
    regexp = '[+]{2}'


class DisableRemote(Message):
    """ASP Allegro inverter disable_remote message
    """

    _signature = '--'
    regexp = _signature


class SetStandbyLevel(Message):
    """ASP Allegro inverter set_standby_level message
    """

    regexp = '[0-9]{2}'

    @classmethod
    def from_bytes(cls, raw_message):
        """Create message from native-format bytestring
        """
        try:
            level = int(raw_message)
        except ValueError:
            raise sungrow.BadBinaryMessage('{0!r}'.format(raw_message))
        return cls({'standby_level': level})

    def to_bytes(self):
        """Produce native-format bytestring from message
        """
        return '{0:0>2}'.format(self['standby_level'])


## It's not at all clear what constitutes a status query, that is, how
##   you get the device to re-send the status page.  Does it look for
##   a hardware flag?


class StatusPage(Message):
    """ASP Allegro status page
    """

    regexp = r'\*0 ASP ALLEGRO .+?disable \(Off\)'

    @classmethod
    def from_bytes(cls, raw_message):
        """Create message from native-format bytestring
        """
        raw_message = raw_message.strip()
        regexp_s = r'.+?'.join(cls._data['regexp'])
        regexp = re.compile(regexp_s, re.MULTILINE | re.DOTALL)
        match = regexp.search(raw_message)
        if match is None:
            error_message = ('{0!r} does not match regexp '
                             '{1!r}'.format(raw_message, regexp_s))
            raise sungrow.BadBinaryMessage(error_message)
        raw_parameters = match.groupdict()
        parameters = cls._raw_to_user_parameters(raw_parameters)
        return cls(parameters)

    def to_bytes(self):
        """Produce native-format bytestring from message
        """
        raw = self._to_raw_parameters()
        output_f = '\r\n'.join(self._data['format'])
        return output_f.format(**raw)  # pylint: disable=W0142


class Device(sungrow.device.Device):
    """Allegro charge controller
    """

    name = DEVICE_TYPE
    message_types = {'status_page': StatusPage,
                     'enable_remote': EnableRemote,
                     'disable_remote': DisableRemote,
                     'set_standby_level': SetStandbyLevel}
    handled_message_types = (StatusPage,)
    sungrow.device.Device._add_message_class_data()


class Emulator(Device):
    """Allegro charge controller emulator
    """

    handled_message_types = (EnableRemote,
                             DisableRemote,
                             SetStandbyLevel)
    respond = Device.emulate_response
    Device._add_message_class_data()
