"""Script file that writes to a socket

Used for exercising the SocketServer port type
"""

import socket
import sys


def main():
    host, port, messages = sys.argv[1:4]
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.connect((host, int(port)))
    for message in messages.split():
        try:
            sock.send(message)
        except socket.error:
            sys.stderr.write('while sending {0!r}:\r\n'.format(message))
            raise
    sock.close()

if __name__ == '__main__':
    main()
