'''
@author: Chang Min Park (cpark22@buffalo.edu)
'''
import sys
import os
import math
import time
from typing import Tuple
from gpapi.googleplay import GooglePlayAPI

# Local package
from src.config import LoginCredentials as LC
from src.config import GpapiSettings as GS
from src.parser import *
import src.aapt_utils as aapt
import src.config as cfg
from src.logger import Logger


class Downloader:

    # ------------------------------------------------------------------------ #
    #  Download Mode                                                           #
    #   - GPAPI: Google Play API (https://github.com/NoMore201/googleplay-api) #
    #   - AZ: AndroZoo (https://github.com/ArtemKushnerov/az)                  #
    # ------------------------------------------------------------------------ #
    MODE_GPAPI = 'MODE_GPAPI'
    MODE_AZ = 'MODE_AZ'

    def __init__(self, mode: str):

        # Check environment variables
        envs_names = [LC.EMAIL, LC.PASSWORD, LC.GSFID, LC.TOKEN]
        if not all([True if v in os.environ else False for v in envs_names]):
            sys.exit("Please set global variables for:\n  - " +
                     str(envs_names))

        # Trace how manys apps have been tried
        self._tried = 0

        # Set the mode
        if not Downloader._check_mode_validity(mode):
            sys.exit("Given mode is not valid: %s" % (mode))
        self._mode = mode

        # Login
        self._server = GooglePlayAPI(locale=GS.LOCALE, timezone=GS.TIMEZONE)
        self._server.login(email=os.environ[LC.EMAIL],
                           password=os.environ[LC.PASSWORD],
                           gsfId=os.environ[LC.GSFID],
                           authSubToken=os.environ[LC.TOKEN])

        self._logger = Logger.get_instance()
        self._logger.info("Google Play login successful")

    def download(self,
                 pkg_name: str,
                 output_path: str,
                 sdk_version: int = None,
                 vc: int = None,
                 enable_sleep: bool = False) -> bool:

        if self._mode == Downloader.MODE_GPAPI:
            return self._download_gpapi(pkg_name, output_path, sdk_version, vc,
                                        enable_sleep)

        elif self._mode == Downloader.MODE_AZ:
            self._download_az(pkg_name, output_path, sdk_version)

    """ 
        Download the app paackage to the given path with Google Play API
          - If 'sdk_version' is not given, download the latest version
          - If 'sdk_version' is given, find and download using binary serach
    """

    def _download_gpapi(self,
                        pkg_name: str,
                        output_path: str,
                        sdk_version: int = None,
                        vc: int = None,
                        enable_sleep: bool = False) -> Tuple[bool, str, int]:
        """ Download the app package to the given path """
        def _download_inner(pkg_name: str,
                            apk_path: str,
                            vc: str = None) -> Tuple[bool, str]:
            try:
                if vc:
                    fl = self._server.download(pkg_name, vc=vc)
                else:
                    fl = self._server.download(pkg_name)

                with open(apk_path, "wb") as apk_file:
                    for chunk in fl.get("file").get("data"):
                        apk_file.write(chunk)

                return True, None

            except Exception as e:
                return False, str(e)

        apk_path = os.path.join(output_path, pkg_name + '.apk')
        self._tried += 1

        # Sleep for every given app numbers because of Google API's
        # rejections for frequent requests
        if enable_sleep and self._tried % cfg.NUM_APPS_BETWEEN_SLEEP == 0:
            time.sleep(cfg.SLEEP_WAIT_SERVER)

        # Check the Given Path
        if not os.path.exists(output_path):
            sys.exit("Given path to download the app does not exist.")

        # Download the Latest Version
        if not sdk_version:
            res, err = _download_inner(pkg_name, apk_path)
            if not res:
                self._logger.warning(err)
                return False, err, None
            else:
                return True, None, None

        # Find and download the target SDK version
        else:
            # Download the app for the given version code
            if vc:
                res, err = _download_inner(pkg_name, apk_path, vc=vc)
                return res, err, vc

            try:
                latest_vc = self._server.details(pkg_name)\
                        .get('details').get('appDetails').get('versionCode')
            except Exception as err:
                return False, str(err), None
            if not latest_vc:
                return False, None, None

            l_vc = 0
            r_vc = latest_vc
            prev_tried_vc = 0
            err = ""
            l_vc_not_found = None
            while True:
                if l_vc_not_found:
                    vc = math.ceil((l_vc_not_found + r_vc) / 2)
                else:
                    vc = math.ceil((l_vc + r_vc) / 2)

                if prev_tried_vc == vc:
                    if vc == l_vc_not_found:
                        err = "%s download unavailable for the given sdk_version: %s"
                    else:
                        err = "%s does not exist for the given sdk_version: %s"
                    self._logger.warning(err % (pkg_name, sdk_version))
                    break

                # Download
                prev_tried_vc = vc
                res, err = _download_inner(pkg_name, apk_path, vc=vc)
                if not res:
                    l_vc = vc
                    l_vc_not_found = l_vc
                    continue

                # Find targetSdkVersion information
                found_sdk_version = aapt.get_tgt_sdk_version(apk_path)
                if found_sdk_version == -1:
                    err = "%s - targetSdkVersion not found in manifest"
                    self._logger.warning(err % (pkg_name))
                    os.popen("rm -rf " + apk_path)
                    break

                # If targetSdkVersion is different, delete and continue
                if found_sdk_version > sdk_version:
                    if l_vc_not_found:
                        l_vc = math.ceil((vc + l_vc_not_found) / 2)
                    r_vc = vc
                    os.popen("rm -rf " + apk_path)
                    continue
                elif found_sdk_version < sdk_version:
                    l_vc = vc
                    l_vc_not_found = None
                    os.popen("rm -rf " + apk_path)
                    continue

                # Download succeeded
                self._logger.info("%s has been downloaded successfully." %
                                  (pkg_name))
                return True, None, vc

            # Not found
            return False, err, None

    """ 
        Download the app paackage to the given path with AndroZoo
          - If 'sdk_version' is not given, download the latest version
          - If 'sdk_version' is given, find and download using binary serach
    """

    def _download_az(self,
                     pkg_name: str,
                     output_path: str,
                     sdk_version: int = None) -> bool:
        pass

    @staticmethod
    def _check_mode_validity(mode: str) -> bool:
        if not mode == Downloader.MODE_GPAPI \
            and not mode == Downloader.MODE_AZ:
            return False

        return True
