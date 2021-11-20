'''
@author: Chang Min Park (cpark22@buffalo.edu)
'''
from re import findall
from subprocess import Popen, PIPE
from typing import List

# Local package
import src.config as conf

encoding = "utf-8"


def run_command(command):
    try:
        proc = Popen(command, stdout=PIPE)
        out, err = proc.communicate()
    except:
        print("Caught Exception while running command: %s" % (command))
    return out


def get_package_name(apk_path: str) -> str:
    command = [conf.AAPT_PATH, 'dump', 'badging', apk_path]
    output = runCommand(command).decode(encoding)
    return findall("(?<=package: name=')[^']*", output)[0]


def get_launchable_activity_list(apk_path: str) -> List[str]:
    command = [conf.AAPT_PATH, 'dump', 'badging', apk_path]
    output = runCommand(command).decode(encoding)
    return findall("(?<=launchable-activity: name=')[^']*", output)


def get_tgt_sdk_version(apk_path: str) -> int:
    command = [conf.AAPT_PATH, 'dump', 'badging', apk_path]
    output = run_command(command).decode(encoding)
    v = findall("(?<=targetSdkVersion:')[^']*", output)
    if v == None or len(v) == 0:
        return -1
    else:
        return int(v[0])
