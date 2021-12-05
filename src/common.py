'''
@author: Chang Min Park (cpark22@buffalo.edu)
'''

from subprocess import Popen, PIPE


def run_command(command):
    try:
        proc = Popen(command, stdout=PIPE)
        out, err = proc.communicate()
    except:
        print("Caught Exception while running command: %s" % (command))
    return out
