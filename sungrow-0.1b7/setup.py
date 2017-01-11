#!/usr/bin/python

from distutils.core import setup
import glob
import os
import os.path
import sys

## !!! this can be used to make Windows batch files that will
##   execute with minimal fuss
BAT_MAGIC = ('@setlocal enabledelayedexpansion && '
             'C:\Python27\python.exe -x "%~f0" %* & '
             'exit /b !ERRORLEVEL!')


def get_scripts():
    """Get script names, fixing them up for Windows if we are on Windows
    """
    scripts = ['scripts/sungrow'] + glob.glob('scripts/sungrow-*[!~]')
    if sys.platform.startswith('win'):
        bats = []
        for script in scripts:
            bat = os.path.splitext(script)[0] + '.bat'
            lines = open(script).readlines()
            lines[0] = BAT_MAGIC + os.linesep
            open(bat, 'w').write(''.join(lines))
            bats.append(bat)
        scripts = bats
    return scripts


setup(name='sungrow',
      version='0.1b7',
      description='sungrow',
      author='Alex Cobb',
      author_email='acobb@smart.mit.edu',
      long_description="""Interaction with solar power management devices

      Allows communication with several solar power management devices
      with serial interfaces from Sungrow, OutBack, and ASP.
      """,
      packages=['sungrow'],
      package_dir={'sungrow': 'sungrow'},
      package_data={'sungrow': ['data/*.yml']},
      scripts=get_scripts())
