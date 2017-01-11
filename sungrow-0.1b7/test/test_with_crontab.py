"""Test running of logger script from crontab
"""

import os
import os.path as path
import platform
import shutil
import subprocess
import sys
import tempfile
import time

import yaml
import nose

CRONTAB_COMMAND_TEMPLATE = '*/1 * * * * cd {0}; {1} {2} -vvv {3} 2>{4} 1>{5}'
SCRIPT_PATH = path.join(path.split(path.dirname(__file__))[0],
                        'scripts',
                        'sungrow')
CONFIG_DICT = {'period': '1 m',
               'devices':
                   {'charge_controller':
                        {'device_type': 'sungrow_charge_controller',
                         'port': 'loop://',
                         'data_streams': {}},
                    'charge_controller_emulator':
                        {'device_type': 'sungrow_charge_controller_emulator',
                         'port': 'loop://'}},
               'actions':
                   [{'action': 'send',
                     'device': 'charge_controller',
                     'message_type': 'status_query'},
                    {'action': 'handle_incoming_messages'},
                    {'action': 'handle_incoming_messages'}]}
## time to wait for cron to run command at 1-minute interval; should be at
##   least 60 s
## cron examines cron entries every minute
CRON_DELAY = 61


def test_with_crontab():
    """Test running logger script using crontab
    """
    if platform.system() == 'Windows':
        raise nose.SkipTest('no crontab on Windows')
    config = CONFIG_DICT.copy()
    tempdir = tempfile.mkdtemp(suffix='sungrowtest')
    try:
        output_file = path.join(tempdir, 'output')
        error_file = path.join(tempdir, 'errors')
        data_streams = config['devices']['charge_controller']['data_streams']
        data_streams['status_page'] = output_file
        config_file = path.join(tempdir, 'config.yml')
        yaml.dump(config, open(config_file, 'w'))
        new_crontab = CRONTAB_COMMAND_TEMPLATE.format(tempdir,
                                                      sys.executable,
                                                      SCRIPT_PATH,
                                                      config_file,
                                                      error_file,
                                                      output_file)
        crontab_file_name = path.join(tempdir, 'crontab')
        old_crontab_file_name = path.join(tempdir, 'old_crontab')
        subproc = subprocess.Popen(['crontab', '-l'],
                                   stdout=subprocess.PIPE,
                                   stderr=subprocess.PIPE)
        old_crontab, error = subproc.communicate()
        if subproc.returncode != 0:
            ## fails if user has no crontab entry
            if not error or error.startswith('no crontab'):
                old_crontab = None
            else:
                raise subprocess.CalledProcessError(error)
        else:
            with open(old_crontab_file_name, 'w') as f:
                f.write(old_crontab)
        with open(crontab_file_name, 'w') as f:
            f.write(''.join((new_crontab, os.linesep * 2)))
        subprocess.check_call(['crontab', crontab_file_name])
        time.sleep(CRON_DELAY)
        if old_crontab:
            argv = ['crontab', old_crontab_file_name]
        else:
            argv = ['crontab', '-r']
        try:
            ## restore old crontab
            subprocess.check_call(argv)
        except:
            print 'error restoring old crontab'
            print old_crontab
            raise
        output = open(output_file).read()
    finally:
        shutil.rmtree(tempdir)
    assert output.strip().endswith('3.5,5.2,5.2,5.2,-159,52,52,52,16,0,512,'
                                   '5,False,False,False,False,False'), output
