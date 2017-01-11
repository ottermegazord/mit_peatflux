"""Test data logging module
"""

import cPickle
import sys

import sungrow.data_logging


class TestDataLogging(object):
    def __init__(self):
        ## data_stream defaults to stdout
        self.object = sungrow.data_logging.DataLogger()

    def test_pickle(self):
        """Test pickle / unpickle
        """
        pickle = cPickle.dumps(self.object)
        obj = cPickle.loads(pickle)
        ## there is no reasonable way to check the data stream for
        ##   equality, unfortunately, because of possible substitution
        ##   of sys.stdout - e.g, by nose
