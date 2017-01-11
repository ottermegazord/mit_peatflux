"""Low-level abstraction of port for interacting with serial devices

These objects implement an API similar to the BufferedRWPair interface
defined in the Python standard library io package.  However, where
they differ is that upon instantiation they do not acquire the
specified resource, they only hold the information required to do so.
The user of the object is responsible for calling .opened() inside a
with statement to acquire the resource before IO; the resource will be
released when the with block is exited.

Serial
SocketServer

read_raw_message() scenario:
Only a device can know when a message is complete.  The device asks
the port for as many bytes as the device has right now (.read()) or
for a certain number of bytes.  The device looks for a signature
indicating the beginning of a message, and then keeps reading until
it gets a complete message.

The device object is responsible for finalization and release of
resources associated with a read or write.  Between reads or
writes of raw messages, the device object must call the port's
.close() method to release the associated resources.  On subsequent
reads or writes, the device object reacquires the resource using the
port's .opened() method.

Ports should be context managers, supporting the with statement via
their .opened() method.

These objects hold parameters for opening files or serial interfaces,
but do not keep these resources open when not in a read or write call.
They deal with context handling so that resources are released
after each such call.


The purpose of the Port abstraction is to ensure that:
 * consistent errors are raised for the same kinds of error conditions
 * the device can ask for a port with a timeout, so that a read
   (or write) never blocks forever
ports should always behave as if opened in nonblocking mode. Generally
io.RawIOBase.readall() behaviour is not suitable because we do not
depend on EOF in the stream.  Of course, if we do hit EOF, we know we
are done.  What we want to do on a call is the equivalent of non-blocking
readinto(b) where b is a byte buffer with len(b) the number of bytes
desired by the Device object.

Some port types get born in pairs, specifically when you have two
objects communicating within the same process.  This is the case for
StringIO and potentially for named pipes.

Port types:
 * Serial
 * SocketServer

The port object deals with select(), poll(), etc. to enforce the non-
blocking condition.

.read_into(b): read bytes into buffer b until:
  * len(b) bytes
  * EOF
  * whenever read call would block
.write(b): write b to port until:
  * len(b) bytes written
  * call blocks
The device will .flush() the write buffers of the stream.
"""

import atexit
import logging
import select
import socket
import urlparse

import serial

LOG = logging.getLogger('sungrow.port')
## global registry of opened sockets
_SOCKETS = []


def _close_sockets(sockets):
    """Call close on all sockets

    Used to ensure cleanup of socket connections.
    """
    for sock in sockets:
        try:
            sock.shutdown(socket.SHUT_RDWR)
        except socket.error:
            pass
        ## there is no harm in calling this multiple times
        sock.close()


atexit.register(_close_sockets, sockets=_SOCKETS)


class Port(object):
    """Port for interacting with serial devices
    """
    def __init__(self, port, url):
        self._port = port
        self.url = url
        self._timeout = 0

    def close(self):
        """Close port
        """
        self._port.close()

    def write(self, bytestring):
        """Write bytes to port
        """
        self._port.write(bytestring)
        self._port.flush()
        LOG.debug('wrote {0!r}'.format(bytestring))

    def read(self, num_bytes=None, ):
        """Read num_bytes from port

        If num_bytes is None, attempt to read as many bytes as are available
        """
        if num_bytes is not None:
            bytestring = self._port.read(num_bytes)
        else:
            ## hm, this is no good, will block till stream is closed
            bytestring = self._port.read()
        LOG.debug('read {0!r}'.format(bytestring))
        return bytestring

    def set_timeout(self, timeout):
        """Change timeout setting
        """
        self._timeout = timeout


class Serial(Port):
    """Serial port object
    """
    def __init__(self, url, *args, **kw):
        port = serial.serial_for_url(url, *args, **kw)
        Port.__init__(self, port, url)

    def set_flag(self, flag, level):
        """Set flag (control line) to level

        Flag may be RTS or DTR.
        """
        flags = ('RTS', 'DTR')
        flag = flag.upper()
        if flag not in flags:
            raise ValueError('flag must be one of {0}'.format(flags))
        method_name = 'set{0}'.format(flag)
        set_flag = getattr(self._port, method_name)
        set_flag(level)

    def __getstate__(self):
        """Retrieve internal state for pickling
        """
        state = self.__dict__.copy()
        port_settings = self._port.getSettingsDict()
        state['port_settings'] = port_settings
        del state['_port']
        return state

    def __setstate__(self, state):
        """Set internal state for unpickling
        """
        port_settings = state.pop('port_settings')
        port = serial.serial_for_url(state['url'])
        port.applySettingsDict(port_settings)
        state['_port'] = port
        self.__dict__.update(state)

    def read(self, num_bytes=None):
        """Read num_bytes from port

        If num_bytes is None, attempt to read as many bytes as are available
        """
        if num_bytes is None:
            num_bytes = self._port.inWaiting()
        return Port.read(self, num_bytes)


class SocketBase(Port):
    """Base class for SocketServer
    """

    broken_connection_messages = ('Broken pipe',
                                  ('An existing connection was '
                                   'forcibly closed by the remote host'),
                                  'Connection reset by peer')

    def __init__(self, url):
        self._socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        _SOCKETS.append(self._socket)
        self._socket.settimeout(None)
        Port.__init__(self, port=None, url=url)

    @staticmethod
    def _parse_url(url):
        """Split URL into host and port

        Expects url of the form used by PySerial, socket://HOST:PORT
        """
        ## pylint doesn't know that result has attributes "netloc"
        ##   and "scheme"
        ## pylint: disable=E1101
        result = urlparse.urlparse(url)
        if result.scheme != 'socket' or ':' not in result.netloc:
            raise ValueError('URL does not match format: '
                             'socket://HOST:PORT'.format(url))
        host, port = result.netloc.split(':')
        try:
            port = int(port)
        except ValueError:
            raise ValueError('port {0!r} not an integer'.format(port))
        return (host, port)


class SocketServer(SocketBase):
    """Socket server port

    Accepts a URL of the same form used by PySerial,
      socket://HOST:PORT

    For a socket client, use the SocketClient class.
    """
    def __init__(self, url):
        SocketBase.__init__(self, url)
        host, port = self._parse_url(url)
        ## in case the socket is in TIME_WAIT
        self._socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self._socket.bind((host, port))
        self._socket.listen(1)

    def read(self, num_bytes=0):
        """Read at least num_bytes from port

        If timeout setting is not None (default is 0), returns the
        empty string after configured timeout if no client has
        connected to the socket.
        """
        received_bytes = -1
        fragments = []
        while received_bytes < num_bytes:
            fragment = ''
            if self._port is None:
                self._port = self._socket.accept()[0]
                LOG.debug('socket server accepted new connection for read')
            readable = select.select([self._port], [], [], self._timeout)[0]
            if readable:
                try:
                    fragment = self._port.recv(4096)
                except socket.error, exception:
                    if exception.strerror in self.broken_connection_messages:
                        ## Windows seems to indicate a closed-connection
                        ##   this way
                        pass
                    else:
                        raise
                if not fragment:
                    ## select said socket is readable, but zero bytes,
                    ##   indicating remote end has hung up
                    LOG.debug('remote hang-up detected')
                    self._port = None
            else:
                fragment = ''
            fragments.append(fragment)
            received_bytes = sum(len(fragment) for fragment in fragments)
        return ''.join(fragments)

    def write(self, bytestring):
        """Write bytes to port
        """
        if self._port is None:
            self._port = self._socket.accept()[0]
            LOG.debug('socket server accepted new connection for write')
        writeable = select.select([], [self._port], [], 0)[1]
        if not writeable:
            LOG.debug('connection not writeable, awaiting new connection')
            self._port = None
            ## recurse for another connection
            self.write(bytestring)
        ## keep trying until all data are sent
        try:
            self._port.sendall(bytestring)
        except socket.error, exception:
            if exception.strerror in self.broken_connection_messages:
                ## connection broken, try again
                self._port = None
                return self.write(bytestring)
            raise
        LOG.debug('wrote {0!r} to socket'.format(bytestring))

    def close(self):
        """Close connection and socket
        """
        if self._port is not None:
            self._port.close()
        self._socket.close()
