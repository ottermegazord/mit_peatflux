"""Test sungrow command-line script
"""

import datetime
import os
import os.path
import tempfile

from nose.tools import raises

import sungrow.ui

TEST_PATH = os.path.dirname(__file__)


def test_script():
    """Test basic run of script

    Also checks whether debugging information is written to error log
    """
    actions_file_name = os.path.join(TEST_PATH, 'system_config.yml')
    fid, error_file_name = tempfile.mkstemp('.log')
    argv = ['sungrow', '-vvv', '-l', error_file_name, actions_file_name]
    try:
        return_code = sungrow.ui.script(argv)
        assert return_code == 0, 'return code {0}'.format(return_code)
        assert os.path.exists(error_file_name), 'no error log created'
        with open(error_file_name) as error_file:
            log_text = error_file.read()
        assert 'sent StatusPage' in log_text
    finally:
        os.close(fid)
        if os.path.exists(error_file_name):
            os.remove(error_file_name)


def test_bad_actions_path():
    """Verify that a call with an empty or non-existent file name fails
    """
    ## we use a tempfile name because it is guaranteed not to
    ##   exist on the file system at the time of creation
    fid, bad_file_name = tempfile.mkstemp('.yml')
    try:
        argv = ['sungrow', bad_file_name]
        ## try first with empty file
        return_code = sungrow.ui.script(argv)
        assert return_code == 1, 'return code {0}'.format(return_code)
    finally:
        os.close(fid)
        if os.path.exists(bad_file_name):
            os.remove(bad_file_name)
    return_code = sungrow.ui.script(argv)
    assert return_code == 1, 'return code {0}'.format(return_code)


def test_system_from_dict():
    """Test instantiation of system from a dict
    """
    mapping = {'period': '1 h',
               'devices': {'rodrigo':
                           {'device_type': 'sungrow_charge_controller',
                            'port': 'loop://',
                            'data_streams': {}},
                           'umberto':
                           {'device_type': 'sungrow_inverter',
                            'port': 'loop://',
                            'data_streams': {'status_page': 'i_status'}}},
               'actions': [{'device': 'rodrigo',
                            'action': 'send',
                            'message_type': 'status_query'},
                           {'action': 'handle_incoming_messages'},
                           {'device': 'rodrigo',
                            'action': 'send',
                            'condition': 'device_back_online',
                            'message_type': 'history_query'}]}
    system = sungrow.ui.system_from_dict(mapping)
    system.perform_actions()


@raises(ValueError)
def test_bad_period_units():
    """Using bad units for period raises ValueError
    """
    mapping = {'period': '1 fortnight',
               'devices': {},
               'actions': []}
    system = sungrow.ui.system_from_dict(mapping)


@raises(ValueError)
def test_empty_actions_file():
    """Creating a system from an empty file raises ValueError
    """
    actions_file_name = os.path.join(TEST_PATH, 'system_config.yml')
    with open(actions_file_name) as actions_file:
        actions_file.read()
        sungrow.ui.system_from_file(actions_file)


def test_save_system_state():
    """Test saving of system state by script code

    A second call to perform_actions_from_file should carry over state
    from the first call if the actions file is unchanged
    """
    actions_file_name = os.path.join(TEST_PATH, 'system_config.yml')
    with open(actions_file_name) as actions_file:
        system, state_file_name = sungrow.ui.system_from_file(actions_file,
                                                              resume=False)
        original_period = system.period
        new_period = system.period + datetime.timedelta(seconds=1)
        system.period = new_period
        sungrow.ui.save_system_state(system, state_file_name)
        actions_file.seek(0)
        system = sungrow.ui.system_from_file(actions_file)[0]
        assert system.period == new_period
    ## now with an emulator
    with open(actions_file_name) as actions_file:
        system, state_file_name = sungrow.ui.system_from_file(actions_file,
                                                              emulate=True,
                                                              resume=False)
        assert system.period == original_period
        new_period = system.period - datetime.timedelta(seconds=2)
        system.period = new_period
        sungrow.ui.save_system_state(system, state_file_name)
        actions_file.seek(0)
        system = sungrow.ui.system_from_file(actions_file, emulate=True)[0]
        assert system.period == new_period
