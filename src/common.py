'''
@author: Chang Min Park (cpark22@buffalo.edu)
'''
import os
from subprocess import Popen, PIPE


def run_command(command):
    out = ''
    try:
        proc = Popen(command, stdout=PIPE)
        out, err = proc.communicate()
    except:
        print("Caught Exception while running command: %s" % (command))
    return out


def mkdir_if_not_exists(path: str):
    if not os.path.exists(path): os.mkdir(path)
