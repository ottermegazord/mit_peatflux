"""Sungrow configuration module

Handles package configuration and user configuration files.
"""

import os.path as path

import yaml

## for logging
ERROR_FORMAT = '%(asctime)-19s %(name)s %(levelname)s %(message)s'
DATE_FORMAT = '%Y-%m-%d %H:%M:%S'

DATA_PATH = path.normpath(path.join(path.dirname(__file__),
                                    'data'))
DEVICE_TYPE_PATH = path.join(DATA_PATH, 'device_types.yml')
DEVICE_EXAMPLE_PATH = path.join(DATA_PATH, 'device_example_data.yml')

DEVICE_TYPE_DATA = yaml.load(open(DEVICE_TYPE_PATH))
DEVICE_EXAMPLE_DATA = yaml.load(open(DEVICE_EXAMPLE_PATH))

USER_STATE_DIR = path.expanduser('~/.sungrow')
