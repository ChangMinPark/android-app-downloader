'''
@author: Chang Min Park (cpark22@buffalo.edu)
'''
from re import findall
from subprocess import Popen, PIPE
from typing import List

# Local package
import src.config as conf

encoding = "utf-8"

TEMP_APP_LIST = ".temp_app_list"
TEMP_OUT = ".temp_out"


def run_command(command):
    try:
        proc = Popen(command, stdout=PIPE)
        out, err = proc.communicate()
    except:
        print("Caught Exception while running command: %s" % (command))
    return out


def download_apps(sdk_version: int, package_names: list, out_dir: str) -> None:

    command = [conf.AZ, 'dump', 'badging', apk_path]
    output = run_command(command).decode(encoding)
    return findall("(?<=package: name=')[^']*", output)[0]
