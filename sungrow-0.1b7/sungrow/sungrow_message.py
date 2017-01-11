"""Shared code for messages for Sungrow devices
"""

import struct

import sungrow.message


class Message(sungrow.message.Message):
    """Shared code for Sungrow device messages
    """

    def _raw_parameters_to_bytes(self, raw_parameters):
        """Convert raw parameters into binary message

        Raw parameters correspond naturally to the structure of the
        binary message
        """
        ## confirm field names
        assert set(raw_parameters.keys()) == set(self._raw_keys), \
            '{0} != {1}'.format(raw_parameters.keys(), self._raw_keys)
        ## enforce ordering
        values = [raw_parameters[key] for key in self._raw_keys]
        raw_message = bytearray(self.length)
        ## * magic okay here; pylint: disable=W0142
        struct.pack_into(self._data['struct'], raw_message, 0, *values)
        self._set_checksum(raw_message)
        return bytes(raw_message)

    @classmethod
    def _set_checksum(cls, raw_message):
        """Insert checksum into bytearray raw_message
        """
        digest = cls._get_digest(raw_message)
        digest_struct = cls._get_digest_struct()
        digest_size = struct.calcsize(digest_struct)
        struct.pack_into(digest_struct, raw_message, -digest_size, digest)

    @classmethod
    def _get_digest_struct(cls):
        """Get correct struct for message digest
        """
        raise NotImplementedError('deferred to subclasses')
