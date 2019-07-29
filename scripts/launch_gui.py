#!/usr/bin/env python

import os 
import subprocess

SCIPION_HOME = os.getenv('SCIPION_HOME')
SCIPION_CONFIG = os.getenv('SCIPION_CONFIG')
SCIPION_EXE =os.path.join(SCIPION_HOME,'scipion') 
cmd_args = ('scipion','--config',SCIPION_CONFIG,)
cmd = ' '.join(str(i) for i in cmd_args)


subprocess.call(cmd,shell=True)
