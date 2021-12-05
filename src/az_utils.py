'''
@author: Chang Min Park (cpark22@buffalo.edu)
'''
from re import findall
from subprocess import Popen, PIPE
import sys
import os
import glob

# Local package
from src.config import AzCredentials as AC
import src.config as cfg
import src.aapt_utils as aapt
from src.logger import Logger
import src.common as common

encoding = "utf-8"

TEMP_APP_LIST = ".temp_app_list"
TEMP_OUT = ".temp_out"

logger = Logger.get_instance()


def download(pkg_name: str, out_dir: str, sdk_version: int) -> bool:

    # Create a temporary out directory to store downloaded apps
    if os.path.exists(TEMP_OUT):
        command = ['rm', '-rf', TEMP_OUT]
        common.run_command(command)
    os.mkdir(TEMP_OUT)

    # Check environment variables
    envs_names = [AC.API_KEY, AC.INPUT_FILE]
    if not all([True if v in os.environ else False for v in envs_names]):
        sys.exit("Please set global variables for:\n  - " + str(envs_names))

    # Download all app versions that are after targetted sdk release date
    logger.info("Downloading %s ..." % (pkg_name))
    sdk_release_date = cfg.SDK_VERSION_DATE[sdk_version]
    command = [
        cfg.AZ, '-k', os.environ[AC.API_KEY], '-i', os.environ[AC.INPUT_FILE],
        '-d', sdk_release_date + ':', '-pn', pkg_name, '-m', 'play.google.com',
        '-o', TEMP_OUT
    ]
    common.run_command(command)

    # Find if target sdk version exists among downloaded apps
    logger.info(
        " - %d different version apps have been downloaded." %
        (len(glob.glob(os.path.join(TEMP_OUT, "**/*.apk"), recursive=True))))
    found = False
    for apk_path in \
        glob.glob(os.path.join(TEMP_OUT, "**/*.apk"), recursive=True):

        # If target sdk version found, move the app to out_dir
        tgt_sdk_version = aapt.get_tgt_sdk_version(apk_path)
        logger.info("   - %s: %d" % (apk_path, tgt_sdk_version))
        if tgt_sdk_version == sdk_version:
            found = True
            command = ['mv', apk_path, os.path.abspath(out_dir)]
            common.run_command(command)
            break

    # Delete temporary directory containing downloaded apps
    command = ['rm', '-rf', TEMP_OUT]
    common.run_command(command)

    if found:
        logger.info(" - Found an app with SDK version %d.\n" % (sdk_version))
    else:
        logger.info(" - Couldn't find any app with SDK version %d.\n" \
                %(sdk_version))
    return found
