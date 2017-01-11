"""Pysungrow user interface
"""

import argparse
import atexit
import datetime
import hashlib
import logging
import logging.handlers
import os
import os.path
import pickle
import yaml

import sungrow.config
import sungrow.system

LEVELS = [logging.ERROR, logging.WARNING, logging.INFO, logging.DEBUG]
DESCRIPTION = """sungrow: communicate with solar power management devices
"""
## UNIX exit codes
EXIT_ERROR = 1
EXIT_OK = 0
UNIT_MAPPING = {'h': 'hours',
                'm': 'minutes',
                's': 'seconds'}


class ArgumentParser(argparse.ArgumentParser):
    """Argument and option parser for sungrow script
    """
    def __init__(self, description, **kw):
        argparse.ArgumentParser.__init__(self, description, **kw)
        self.add_argument('-v', '--verbose', dest='verbosity',
                          action='count', default=0,
                          help='report more about what is being done')
        self.add_argument('-l', '--error-log', metavar='LOG_FILE',
                          dest='error_log',
                          help='log errors to LOG_FILE, default stderr')
        self.add_argument('-e', '--emulate',
                          default=False,
                          action='store_true',
                          help='emulate configured devices until terminated')
        self.add_argument('actions', metavar='FILE',
                          help='action configuration file')


## file layer
def script(argv):
    """Sungrow command-line script

    This takes list like sys.argv, uses argparse to get file names,
    options. Accepts file names, default stdin, stdout, stderr, does
    file exception handling and finalization on files. Sets up
    sys.excepthook with logging. Can use sys.atexit module
    """
    parser = ArgumentParser(DESCRIPTION)
    ## argv[0] is the command name, argument parser expects just
    ##   the arguments
    args = parser.parse_args(argv[1:])
    if args.verbosity >= len(LEVELS):
        level = LEVELS[-1]
    else:
        level = LEVELS[args.verbosity]
    logger = logging.getLogger('sungrow')
    if args.verbosity >= len(LEVELS):
        logger.warning('maximum verbosity exceeded, ignoring flag')
    if not os.path.isfile(args.actions):
        logger.error('{0} is not a regular file, exiting'.format(args.actions))
        return EXIT_ERROR
    if os.stat(args.actions).st_size == 0:
        logger.error('empty actions file {0}'.format(args.actions))
        return EXIT_ERROR
    original_log_level = logger.getEffectiveLevel()
    handler = None
    logger.setLevel(level)
    if args.error_log:
        handler = logging.handlers.TimedRotatingFileHandler(args.error_log,
                                                            when='midnight')
        formatter = logging.Formatter(sungrow.config.ERROR_FORMAT,
                                      sungrow.config.DATE_FORMAT)
        handler.setFormatter(formatter)
        logger.addHandler(handler)
    try:
        with open(args.actions) as actions_file:
            system = system_from_file(actions_file=actions_file,
                                      emulate=args.emulate)[0]
            if not args.emulate:
                system.perform_actions()
            else:
                import time
                while True:
                    system.perform_actions()
                    time.sleep(system.period.total_seconds())
    finally:
        ## to avoid side effects, reset logger to original state
        if handler is not None:
            logger.removeHandler(handler)
        logger.setLevel(original_log_level)
    return EXIT_OK


def save_system_state(system, file_name):
    """Save (pickle) the system to file_name
    """
    dirname = os.path.dirname(file_name)
    if not os.path.exists(dirname):
        os.mkdir(dirname)
    with open(file_name, 'wb') as pickle_file:
        pickle.dump(system, pickle_file)


def system_from_file(actions_file, emulate=False, resume=True):
    """Instantiate system described in actions_file

    actions_file is a file-like object containing a YAML stream describing
    a system.  Returns (system, state_file_name) where system is the
    newly instantiated system object and state_file_name is the name of
    a file where the system state will be saved on exit as described below.

    At exit, the state of the system is saved in file named according
    to a digest of actions_file.  If this function is called again
    with an actions_file with the same digest and resume is True,
    rather than re-reading the file, the saved state of the system is
    loaded.  State files for emulators and loggers are stored
    separately, so the state of an emulator loaded from an
    actions_file will not overwrite a logger from the same action file
    or vice versa.

    Note that if resume == False any previously saved state will be
    overwritten on exit.
    """
    content = actions_file.read()
    actions = yaml.load(content)
    if actions is None:
        raise ValueError('empty file')
    ## pylint: disable=E1101
    system_signature = hashlib.md5(content).hexdigest()
    state_dir = sungrow.config.USER_STATE_DIR
    if emulate:
        file_name_f = 'emulator_{0}'
    else:
        file_name_f = 'logger_{0}'
    state_file_name = os.path.join(state_dir,
                                   file_name_f.format(system_signature))
    if resume and os.path.exists(state_file_name):
        system = pickle.load(open(state_file_name, 'rb'))
    else:
        system = system_from_dict(actions, emulator=emulate)
    atexit.register(save_system_state, system, state_file_name)
    return (system, state_file_name)


def system_from_dict(mapping, emulator=False):
    """Instantiate a system from a descriptive mapping

    mapping contains the keys devices, actions, and period.
    period is a string consisting of a value and unit, where
      unit may be "h" for hours, "m" for minutes or "s" for seconds;
      for example, "1 h" means 1 hour, "0.25 s" means 0.25 seconds
    devices is a mapping of device names to device dicts allowing
      instantiation of device objects.  Each device dict has this
      structure:
      {'device_type': device type name,
       'port': port url,
       'data_streams': (optional) mapping from message names to
                       stream or file names}
    actions is a sequence of action dicts describing each action.
      The action dicts have this structure:
      {'device': device name,
       'action': action name (see main constructor for this class)
       'parameters': keyword arguments to pass to the action}

      If device type name ends with '_emulator', the corresponding
      emulator type is created, regardless of the "emulator" flag.
      This can be useful if you want emulators and non-emulators
      to talk to eachother within a single process (usually for
      debugging or configuration testing).

    If emulator is True, the actions in the file are ignored; instead,
    for each device in the action file, the single action
    handle_responses is invoked.

    Any extraneous keys in the mappings are ignored, so look out
    for typos!

    This constructor simplifies creating a system from a system
    configuration file in formats like YAML.
    """
    period = mapping['period']
    period, unit = period.split()
    try:
        period = int(period)
    except ValueError:
        period = float(period)
    try:
        unit = UNIT_MAPPING[unit]
    except KeyError:
        raise ValueError('period unit should be one of '
                         '{0}'.format(UNIT_MAPPING.keys()))
    period = datetime.timedelta(**{unit: period})  # pylint: disable=W0142
    buses = _construct_bus_list(mapping['devices'],
                                emulate_by_default=emulator)
    if emulator:
        mapping['actions'] = [{'action': 'handle_incoming_messages'}]
    actions = []
    for parameters in mapping['actions']:
        action = parameters.pop('action')
        actions.append((action, parameters))
    return sungrow.system.System(buses, actions, period)


def _construct_bus_list(devices, emulate_by_default=False):
    """Construct bus list from text descriptors

    Creates a list of buses from text descriptors coming from a
    configuration file.
    """
    devices = dict(devices)
    ports = {}
    all_devices = {}
    for key, device_dict in devices.items():
        device_type = device_dict['device_type']
        device_is_emulator = emulate_by_default
        if device_type.endswith('_emulator'):
            device_type = device_type[:-len('_emulator')]
            device_is_emulator = True
        module = getattr(__import__('sungrow.{0}'.format(device_type)),
                         device_type)
        ## make sure the same device string gives the same device
        port_name = device_dict['port']
        if port_name not in ports:
            ## sockets for emulators are servers; otherwise clients
            if (device_is_emulator and
                port_name.startswith('socket://')):
                port = sungrow.port.SocketServer(port_name)
            else:
                port_settings = device_dict.get('port_settings', {})
                ## pylint: disable=W0142
                port = sungrow.port.Serial(port_name, **port_settings)
            ports[port_name] = port
        port_devices = all_devices.setdefault(port_name, {})
        data_streams = device_dict.get('data_streams', {})
        if device_is_emulator:
            port_devices[key] = module.Emulator(data_streams=data_streams)
        else:
            port_devices[key] = module.Device(data_streams=data_streams)
    buses = []
    for port_name, port_devices in all_devices.items():
        port = ports[port_name]
        bus = sungrow.bus.Bus(port, port_devices)
        buses.append(bus)
    return buses
