"""Interaction with solar power management devices

Allows communication with several solar power management devices
with serial interfaces from Sungrow, OutBack, and ASP.
"""

import sungrow.data_logging

sungrow.data_logging.configure()


def bytes_to_hex(sequence):
    """Produce a text version of bytes, mostly for debugging
    """
    return ' '.join(('%2s' % hex(c)[2:]).replace(' ', '0')
                    for c in bytearray(sequence))


def hex_to_bytearray(sequence):
    """Produce a bytearray from string or unicode
    """
    ## in newer Python versions, .fromhex only accepts unicode
    return bytearray.fromhex(unicode(' '.join(sequence.split())))


def hex_to_bytes(sequence):
    """Produce bytes from string or unicode
    """
    return bytes(hex_to_bytearray(sequence))


class BadBinaryMessage(Exception):
    """Malformed binary message
    """


class ChecksumError(BadBinaryMessage):
    """Checksum does not match
    """


class ConfigurationError(Exception):
    """Bad configuration
    """
