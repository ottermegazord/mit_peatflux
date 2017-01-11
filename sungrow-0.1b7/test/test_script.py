"""Test sungrow script execution

A simple test of an OS call to the sungrow script. Details of the
script code are tested elsewhere without going through sys.argv,
stdin, stdout, etc.  This script just ensures that a call with no
arguments gives a usage message and returns exit code 2
"""

import os
from os import path
import stat
import subprocess
import platform
import sys

import sungrow.ui

## Trick is to make sure we are executing the script and importing the
##   package from the working tree
## There are two elements to this:
##   * set PATH to the script directory so the os can execute it
##   * set PYTHONPATH to the parent directory to import the working
##     tree

PARDIR = path.split(path.dirname(__file__))[0]
SCRIPT_DIR = path.join(PARDIR, 'scripts')
COMMAND = 'sungrow'
EXIT_SYNTAX_ERROR = 2
USAGE_MESSAGE_HEAD = 'usage: {0}'.format(sungrow.ui.DESCRIPTION)
## correct line breaks for platform:
USAGE_MESSAGE_HEAD = os.linesep.join(USAGE_MESSAGE_HEAD.split('\n'))


def test_sungrow_pipe():
    """Test sungrow script in working tree with no arguments

    Tests that calling the script with no arguments results in an exit code
    indicating a syntax error and prints a usage message.

    The code in the script file itself doesn't do much; this test is just
    enough to make sure there are no critical problems in the script file.
    Further functionality is tested elsewhere.
    """
    script_path = path.join(SCRIPT_DIR, COMMAND)
    if platform.system() == 'Windows':
        args = [sys.executable, script_path]
    else:
        args = [COMMAND]
    env = os.environ.copy()
    env['PATH'] = SCRIPT_DIR
    env['PYTHONPATH'] = PARDIR
    ## make script executable to run, then revert
    exec_mask = stat.S_IXUSR | stat.S_IXGRP | stat.S_IXOTH
    mode = os.stat(script_path).st_mode
    os.chmod(script_path, mode | exec_mask)
    try:
        popen = subprocess.Popen(args,
                                 stdout=subprocess.PIPE,
                                 stderr=subprocess.PIPE,
                                 env=env)
    finally:
        os.chmod(script_path, mode)
    stdout, stderr = popen.communicate()
    return_code = popen.returncode
    ## no promises about exit code on Windows
    if platform.system() != 'Windows':
        assert return_code == EXIT_SYNTAX_ERROR, \
            '{0} != {1}'.format(return_code, EXIT_SYNTAX_ERROR)
    assert stdout == '', '{0} != ""'.format(stdout)
    assert stderr.startswith(USAGE_MESSAGE_HEAD), \
        '{0!r} does not start with {1!r}'.format(stderr, USAGE_MESSAGE_HEAD)
