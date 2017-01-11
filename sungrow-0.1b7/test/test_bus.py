"""Test bus objects
"""

import cPickle

import sungrow.bus
import sungrow.device
import sungrow.port


class TestBus(object):
    def __init__(self):
        devices = {'device': sungrow.device.Device()}
        port = sungrow.port.Serial('loop://')
        self.bus = sungrow.bus.Bus(port, devices)

    def test_pickle(self):
        """Test pickling of bus objects
        """
        s = cPickle.dumps(self.bus)
        o = cPickle.loads(s)
        assert o.online == self.bus.online

    def test_online_status(self):
        """Test bookkeeping for online status
        """
        assert self.bus.online is False
        assert self.bus.is_back_online() is False
        raw_message = 'kiwifruit'
        self.bus.write(raw_message)
        self.bus.read()
        assert self.bus.online is True
        assert self.bus.is_back_online() is True
        self.bus.write(raw_message)
        self.bus.read()
        assert self.bus.online is True
        ## this is the second successful read, should be False now
        assert self.bus.is_back_online() is False
        ## now we sabotage the port by closing it, expect ValueError
        ##   on read
        self.bus.port.close()
        try:
            self.bus.read()
        except ValueError:
            pass
        else:
            raise AssertionError('read on closed port, expected ValueError')
        assert self.bus.online is False
        assert self.bus.is_back_online() is False
