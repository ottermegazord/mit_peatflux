"""System objects

System has devices, generally of different kinds

one error stream for system, separate error stream for each device

each entry in schedule is the name of a method of the system object
system.action(device, parameters)

methods correspond to actions, customise by subclassing

Two state variables of interest:
 - device_back_online - a previous attempt at communication
     raised an exception; detectable if device.offline was false and
     communication now succeeds
 - system_back_online - a time point was missed for a
     scheduled action; detectable if system.last_loop_iteration was
     longer ago than indicated by loop interval

For timed events, there is more than one way to cope with an apparently
missed event.  One is to execute it as soon as possible after the scheduled
time, but that's not what's done here; rather, if the current time is within
a window (equal to loop period?) of the scheduled time, it is executed.
This results in data on an even grid with a slew of loop_period instead
of unevenly spaced data with an approximate grid spacing
"""

import datetime
import logging
import time

import sungrow
import sungrow.bus
import sungrow.port

LOG = logging.getLogger('sungrow.system')


class System(object):
    """System object

    buses is a sequence of bus objects, pairings between a port and a
      device_name: device_object mapping of devices
    actions is a sequence of actions,
      (action, parameters)
      where action is the name of a method of the system object and
      parameters is a mapping of parameters to be passed to the method.
        Common parameters:
          device_name is the handle of a device in the system
          condition is a condition to be checked before executing the action
            If the method check_condition(condition) returns False, the other
            members are not evaluated.
          period is the period of loop execution, a timedelta object
      last_loop_time: time of last loop iteration, None if never or unknown
    """
    def __init__(self, buses, actions, period, last_loop_time=None):
        self.buses = buses
        self.actions = actions
        self.period = period
        self._last_loop_time = last_loop_time
        self._back_online = False
        ## make sure internal variable _back_online is up-to-date
        self._update_online_status()
        devices = {}
        device_bus_mapping = {}
        num_devices = 0
        for bus in buses:
            num_devices += len(bus.devices)
            devices.update(bus.devices)
            for name in bus.devices:
                device_bus_mapping[name] = bus
        if len(devices) < num_devices:
            raise ValueError('device names must be unique')
        self._devices = devices
        self._device_bus_mapping = device_bus_mapping

    def handle_incoming_messages(self):
        """Handle all incoming messages

        Each bus checks for new data, and each device on each bus
        is given a chance to respond to each message.
        """
        for bus in self.buses:
            bus.handle_incoming_messages()

    def is_back_online(self):
        """Check whether system has come back online after being offline

        Returns True if last_loop_time is more than 1.5 * self.period
        prior to current time.
        """
        return self._back_online

    def _update_online_status(self):
        """Update internal state indicating whether system is up after
        having been down

        This is accomplished by checking whether the current time is
        more than 1.5 * self.period since the last check
        """
        reference_time = self._last_loop_time
        if reference_time is None:
            self._back_online = True
        else:
            elapsed = datetime.datetime.now() - reference_time
            ## integer multiplication works with timedeltas;
            ##   float multiplication does not.
            self._back_online = (elapsed * 2) > (self.period * 3)
        self._last_loop_time = datetime.datetime.now()

    def send(self, device, message_type, parameters=None):
        """Send message to device

        Sends message with given parameters and type to named device
        """
        device_obj = self._devices[device]
        cls = device_obj.message_types[message_type]
        if parameters is None:
            parameters = {}
        message = cls(**parameters)  # pylint: disable=W0142
        bus = self._device_bus_mapping[device]
        bus.send_messages([(device, message)])

    def set_port_flag(self, device, flag, level):
        """Set device port flag to level

        Flag may be RTS or DTR
        """
        port = self._device_bus_mapping[device].port
        port.set_flag(flag, level)

    def perform_actions(self):
        """Perform all queued actions
        """
        self._update_online_status()
        for action, parameters in self.actions:
            condition = parameters.pop('condition', None)
            device_name = parameters.get('device', None)
            if LOG.level <= logging.DEBUG:
                message_f = ['performing {0}']
                if parameters:
                    message_f += ['(**{1})']
                else:
                    message_f += ['()']
                if condition is not None:
                    message_f += [' on condition {2}']
                LOG.debug(''.join(message_f).format(action, parameters,
                                                    condition))
            if not hasattr(self, action):
                error_message = 'unrecognized action {0!r}'.format(action)
                raise sungrow.ConfigurationError(error_message)
            method = getattr(self, action)
            if self.check_condition(condition, device_name):
                method(**parameters)  # pylint: disable=W0142

    def check_condition(self, condition, device_name=None):
        """Evaluate condition, returning True or False

        condition is None or text.  If None, True is returned immediately.
        device_name is the name of a system device, or, if not given,
        the system itself is checked.
        Currently accepted text conditions are:
          * is_back_online: For the system, check whether the system
            has missed an earlier loop cycle, or has never made one
            before.  For a device, check whether a previously
            unresponsive device has responded.  Note that this will
            only be known, and evaluate to True, if a recent attempt
            at communication has been made
        """
        if condition is None:
            return True
        if condition == 'device_back_online':
            if device_name is None:
                error_msg = ('device_name required to check if '
                             'device_back_online')
                raise sungrow.ConfigurationError(error_msg)
            bus = self._device_bus_mapping[device_name]
            return bus.is_back_online()
        elif condition == 'system_back_online':
            return self.is_back_online()
        ## hardware flags? e.g., DTR?
        else:
            message = 'unexpected condition {0!r}'.format(condition)
            raise sungrow.ConfigurationError(message)

    @staticmethod
    def sleep(seconds):
        """Sleep (wait) for so many seconds
        """
        time.sleep(seconds)
