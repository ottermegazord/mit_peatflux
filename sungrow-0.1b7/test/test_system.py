"""Test code for system objects
"""

import cPickle
import datetime

from nose.tools import raises

import sungrow
import sungrow.bus
import sungrow.port
import sungrow.sungrow_charge_controller
import sungrow.system


class TestSystem(object):
    """Test system objects
    """

    ## loop period in microseconds
    delay = 1000

    def __init__(self):
        buses = []
        actions = []
        period = datetime.timedelta(microseconds=self.delay)
        self.system = sungrow.system.System(buses, actions, period,
                                            last_loop_time=None)

    def test_pickle(self):
        """Test pickling of object
        """
        s = cPickle.dumps(self.system)
        o = cPickle.loads(s)

    def test_simple_action(self):
        """Test a simple action:  system sleep
        """
        buses = []
        actions = [('sleep', {'condition': 'system_back_online',
                              'seconds': 0.001})]
        period = datetime.timedelta(microseconds=100)
        system = sungrow.system.System(buses, actions, period,
                                       last_loop_time=None)
        system.perform_actions()

    @raises(sungrow.ConfigurationError)
    def test_bad_condition(self):
        """Bad condition should throw ConfigurationError
        """
        self.system.check_condition('is_sky_blue')

    def test_write_read(self):
        """Test a write / read on loopback
        """
        port = sungrow.port.Serial('loop://')
        device = sungrow.sungrow_charge_controller.Device()
        bus = sungrow.bus.Bus(port, {'frederico': device})
        actions = [('send', {'device': 'frederico',
                             'message_type': 'status_query'}),
                   ('handle_incoming_messages', {})]
        period = datetime.timedelta(seconds=1)
        system = sungrow.system.System([bus], actions, period)
        system.perform_actions()

    def test_online_status(self):
        """Check bookkeeping of online status
        """
        ## started with last_loop_time of None, so back_online should be True
        assert self.system.is_back_online() is True
        ## okay, this is cheating a little but all sorts of timing issues
        ##   arise for testing within a reasonable time frame if we try to
        ##   make sure that the action loop happens fast enough that
        ##   system_back_online has become False.  So we put last_loop_time
        ##   into the future.
        self.system._last_loop_time += datetime.timedelta(seconds=2)
        self.system.perform_actions()
        ## Now back_online should be false because we've had a successful loop
        assert self.system.is_back_online() is False
        ## If we sleep for more than 1.5 period, back_online should be
        ##    True again
        self.system.sleep(self.delay * 1.55 / 1e6)
        self.system.perform_actions()
        assert self.system.is_back_online() is True
