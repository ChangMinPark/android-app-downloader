'''
@author: Chang Min Park (cpark22@buffalo.edu)
'''
from re import findall
from subprocess import Popen, PIPE
from typing import List

# Local package
import src.config as conf
import src.common as common

encoding = "utf-8"


def get_package_name(apk_path: str) -> str:
    command = [conf.AAPT_PATH, 'dump', 'badging', apk_path]
    output = common.run_command(command).decode(encoding)
    return findall("(?<=package: name=')[^']*", output)[0]


def get_tgt_sdk_version(apk_path: str) -> int:
    command = [conf.AAPT_PATH, 'dump', 'badging', apk_path]
    output = common.run_command(command).decode(encoding)
    v = findall("(?<=targetSdkVersion:')[^']*", output)
    if v == None or len(v) == 0:
        return -1
    else:
        return int(v[0])
