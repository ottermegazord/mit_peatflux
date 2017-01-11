"""Data and error logging

Error messages of all kinds are logged using the builtin logging
module.  Data are logged by a simpler mechanism to a file or
stream using the DataLogger objects defined here.
"""

## name is "data_logging" instead of the more obvious "logging" to
##   avoid collisions with the built-in logging module.
##   absolute_import will fix this but it's not on by default in
##   current or earlier Python versions

import logging
import os
import os.path
import sys

import sungrow.config


def configure():
    """Configure data logging
    """
    logging.basicConfig(level=logging.WARNING,
                        format=sungrow.config.ERROR_FORMAT,
                        datefmt=sungrow.config.DATE_FORMAT)


## The additional keyword argument logging=logging ensures that
##   the logging module is still available in the local scope in case
##   an error prevents the module from being loaded and the exception
##   is raised while the module is being destroyed
##   See Python issue 11705: http://bugs.python.org/issue11705
## pylint: disable=W0621
def exception_handler(exception_class, exception_instance, traceback,
                      logging=logging):
    """Custom exception handler for logging

    Ensures that errors are logged rather than reported to the console
    when system is running in unsupervised mode.
    """
    logging.error('Unhandled exception:',
                  exc_info=(exception_class, exception_instance, traceback))


## install exception handler to ensure that exceptions are logged
sys.excepthook = exception_handler


class DataLogger(object):  # pylint: disable=R0903
    """Data logger object for recording data to a file

    data_stream is a file-like object or text; default is sys.stdout.
    If data_stream is text, it is interpreted as a file name;
    otherwise it is assumed to be a file-like object.
    """
    def __init__(self, data_stream=None):
        if data_stream is None:
            data_stream = sys.stdout
        self.data_stream = data_stream
        self._message_f = ''.join(('{0}', os.linesep))

    def __call__(self, message, read_time):
        """Write message to data stream
        """
        data_line = message.format_data(read_time)
        if isinstance(self.data_stream, basestring):
            appending = os.path.exists(self.data_stream)
            with open(self.data_stream, 'a') as data_file:
                if not appending:
                    header = message.format_header()
                    data_file.write(self._message_f.format(header))
                data_file.write(self._message_f.format(data_line))
        else:
            self.data_stream.write(self._message_f.format(data_line))

    def __getstate__(self):
        """Retrieve internal state for pickling
        """
        state = self.__dict__.copy()
        data_stream = state['data_stream']
        ## an open file can't, in general, be pickled, for good
        ##   reasons (see http://wiki.python.org/moin/UsingPickle) but
        ##   we can handle the common special cases of sys.stdout and
        ##   sys.stderr
        if self.data_stream == sys.stdout:
            state['data_stream'] = '<stdout>'
        elif self.data_stream == sys.stderr:
            state['data_stream'] = '<stderr>'
        elif isinstance(self.data_stream, file):
            raise ValueError("can't pickle file {0!r}".format(data_stream))
        return state

    def __setstate__(self, state):
        """Set internal state for unpickling
        """
        ## just need to handle special cases of stdout and stderr
        if state['data_stream'] in ('<stdout>', '<stderr>'):
            state['data_stream'] = getattr(sys, state['data_stream'][1:-1])
        self.__dict__.update(state)
