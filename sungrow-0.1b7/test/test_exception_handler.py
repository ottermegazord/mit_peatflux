"""This module just exercises the exception handling function.

The actual installation as an exception hook is not easy to test
directly with nose, but there is not much to it; we can assume
it's working correctly if the exception handling function itself does.
"""

import cStringIO
import logging
import sys

import sungrow
import sungrow.data_logging


def test_exception_handling():
    """Confirm that a traceback is written to the error stream by the
    exception handler
    """
    buf = cStringIO.StringIO()
    handler = logging.StreamHandler(buf)
    logger = logging.getLogger('')
    logger.addHandler(handler)
    try:
        raise sungrow.BadBinaryMessage('bogus message!')
    except sungrow.BadBinaryMessage:
        info = sys.exc_info()
        sungrow.data_logging.exception_handler(*info)
    error_message_lines = buf.getvalue().splitlines()
    assert error_message_lines[1] == 'Traceback (most recent call last):'
    assert error_message_lines[-1] == 'BadBinaryMessage: bogus message!'
