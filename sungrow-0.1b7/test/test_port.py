"""Tests for port objects - especially sockets
"""

import cPickle
import os
import os.path
import socket
import subprocess
import sys

from nose.tools import raises

import sungrow.port

SCRIPT_PATH = os.path.join(os.path.dirname(__file__), 'write_to_socket.py')
HOST = 'localhost'
PORT = 50001
URL = 'socket://localhost:50001'
BAD_URLS = ['sprocket://localhost:50001',
            'socket://localhost:foo']


def test_loop():
    """Test write / read to loop serial device
    """
    message = 'cheerio'
    port = sungrow.port.Serial('loop://')
    port.write(message)
    bytestring = port.read()
    assert bytestring == message


def test_pickle():
    """Test pickling of serial port
    """
    obj = sungrow.port.Serial('loop://')
    s = cPickle.dumps(obj)
    o = cPickle.loads(s)
    assert o.url == obj.url
    assert o._port.getSettingsDict() == obj._port.getSettingsDict()


def test_socket_port():
    """Test simple read from SocketServer port
    """
    port = sungrow.port.SocketServer(URL)
    port.set_timeout(None)
    message = 'banana slug'
    expected_reply = ''.join(message.split())
    subproc = subprocess.Popen([sys.executable, SCRIPT_PATH, HOST, str(PORT),
                                message])
    reply = port.read(num_bytes=len(expected_reply))
    assert reply == ''.join(message.split()), \
        '{0!r} != {1!r}'.format(reply, expected_reply)
    port.write('equestrian statue')
    subproc.wait()
    ## launch again, a new process
    new_message = 'torpedo'
    subproc = subprocess.Popen([sys.executable, SCRIPT_PATH, HOST, str(PORT),
                                new_message])
    port.write('Spanish Inquisition')
    new_reply = port.read(num_bytes=len(new_message))
    assert new_reply == new_message, repr(new_reply)
    subproc.wait()
    ## okay, now try an empty message
    empty_message = ''
    subproc = subprocess.Popen([sys.executable, SCRIPT_PATH, HOST, str(PORT),
                                empty_message])
    empty_reply = port.read(num_bytes=0)
    assert empty_reply == ''
    subproc.wait()
    port.close()


def test_bad_url():
    """Bad URLs for SocketServer port should raise ValueError
    """
    for url in BAD_URLS:
        try:
            port = sungrow.port.SocketServer(url)
        except ValueError:
            pass
        else:
            raise AssertionError('expected ValueError '
                                 'for url {0}'.format(url))


def test_close_sockets():
    """Test cleanup function that closes sockets on exit
    """
    sungrow.port._close_sockets(sungrow.port._SOCKETS)
