'''
@author: Chang Min Park (cpark22@buffalo.edu)
'''
import sys
import os
import math
import time
import glob
from typing import Tuple
from src.gpapi.googleplay import GooglePlayAPI

# Local package
from src.config import GpLoginCredentials as GPAPI_C
from src.config import GpapiSettings as GS
from src.config import AzCredentials as AZ_C
from src.parser import *
from src.logger import Logger
import src.config as cfg
import src.aapt_utils as aapt
import src.common as common

encoding = "utf-8"


class Downloader:
    '''
    Download Mode                                                           
    - GPAPI: Google Play API (https://github.com/NoMore201/googleplay-api)
    - AZ: AndroZoo (https://github.com/ArtemKushnerov/az)
    '''
    MODE_GPAPI = 'MODE_GPAPI'
    MODE_AZ = 'MODE_AZ'

    def __init__(self,
                 mode: str,
                 sdk_versions: list,
                 sdk_version_match: bool = False) -> None:
        self._logger = Logger.get_instance()

        # Set the mode
        self._mode = mode
        if not self._check_mode_validity():
            sys.exit("Given mode is not valid: %s" % (mode))

        # Check environment variables
        res, missing_envs = self._check_env_for_mode()
        if not res:
            sys.exit("Please set global variables for:\n - " +
                     str(missing_envs))

        # Trace how manys apps have been tried
        self._tried = 0

        # Login
        if mode == Downloader.MODE_GPAPI:
            self._server = GooglePlayAPI(locale=GS.LOCALE,
                                         timezone=GS.TIMEZONE)
            #            self._server.login(email=os.environ[GPAPI_C.EMAIL],
            #                               password=os.environ[GPAPI_C.PASSWORD],
            #                               gsfId=os.environ[GPAPI_C.GSFID],
            #                               authSubToken=os.environ[GPAPI_C.TOKEN])
            self._server.login(email=os.environ[GPAPI_C.EMAIL],
                               password=os.environ[GPAPI_C.PASSWORD],
                               gsfId=None,
                               authSubToken=None)

            self._logger.info("Google Play login successful")

        self._sdk_versions = sdk_versions
        self._sdk_version_match = sdk_version_match

    '''
    Download apps in the given list for the given sdk versions.
    '''

    def download_all(self, pkg_list: list, out_path: str) -> None:

        # Set output paths for the apps to download
        self._set_output_path(out_path)

        # Download apps with either Google Play API or AndroZoo tool
        for pkg_name, cat in pkg_list:

            if self._mode == Downloader.MODE_GPAPI:
                self._download_gpapi_wrap(pkg_name,
                                          cat,
                                          out_path,
                                          enable_sleep=True)

            elif self._mode == Downloader.MODE_AZ:
                self._download_az(pkg_name, cat, out_path)

    # ----------------- #
    #   Local Methods   #
    # ----------------- #
    """ 
    Download the app paackage to the given path with Google Play API
    - If 'sdk_version' is not given, download the latest version
    - If 'sdk_version' is given, find and download using binary serach
    """

    def _download_gpapi_wrap(self,
                             pkg_name: str,
                             cat: str,
                             out_path: str,
                             enable_sleep: bool = False) -> None:

        if self._sdk_versions is None:
            out_path_sdk = \
                    os.path.join(out_path, 'latest', '_match') \
                    if self._sdk_version_match else \
                    os.path.join(out_path, 'latest')
            out_path_cat = os.path.join(out_path_sdk, cat)
            err = self._download_gpapi(pkg_name,
                                       out_path_cat,
                                       sdk_version=None,
                                       enable_sleep=enable_sleep)

            # Sleep awhile for download fails
            if err and "busy" in err.lower():
                time.sleep(cfg.SLEEP_WAIT_SERVER)

        else:
            for sdk_version in self._sdk_versions:
                out_path_sdk = \
                        os.path.join(out_path, str(sdk_version), '_match') \
                        if self._sdk_version_match else \
                        os.path.join(out_path, str(sdk_version))
                out_path_cat = os.path.join(out_path_sdk, cat)

                err = self._download_gpapi(pkg_name,
                                           out_path_cat,
                                           sdk_version=sdk_version,
                                           enable_sleep=enable_sleep)

                # Sleep awhile for download fails
                if err and "busy" in err.lower():
                    time.sleep(cfg.SLEEP_WAIT_SERVER)

    def _download_gpapi(self,
                        pkg_name: str,
                        out_path: str,
                        sdk_version: int = None,
                        enable_sleep: bool = False) -> str:
        """ Download the app package to the given path """
        def _download_inner(pkg_name: str,
                            apk_path: str,
                            vc: str = None) -> Tuple[bool, str]:
            try:
                if vc is None:
                    fl = self._server.download(pkg_name)
                else:
                    fl = self._server.download(pkg_name, versionCode=vc)

                with open(apk_path, "wb") as apk_file:
                    for chunk in fl.get("file").get("data"):
                        apk_file.write(chunk)
                return True, None

            except Exception as e:
                msg = 'Failed to download %s (vc: %s). %s' % (pkg_name, vc, e)
                self._logger.warning(msg)
                return False, str(e)

        # Download the Latest Version if SDK version is not provided
        common.mkdir_if_not_exists(out_path)
        if self._sdk_versions is None:
            apk_path = os.path.join(out_path, pkg_name + '.apk')
            if os.path.exists(apk_path):
                self._logger.info('Skip for already downloaded app.')
                self._logger.info(' - %s' % (pkg_name))
                return None
            res, err = _download_inner(pkg_name, apk_path)
            if res:
                self._logger.info("%s has been downloaded successfully." \
                                                                %(pkg_name))
            return None if res else err

        # Check and set paths
        apk_path = os.path.join(out_path, pkg_name + '.apk')
        if os.path.exists(apk_path):
            self._logger.info('Skip for already downloaded app.')
            self._logger.info(' - %s' % (pkg_name))
            return None
        self._tried += 1

        # Sleep for every given app numbers because of Google API's
        # rejections for frequent requests
        if enable_sleep and self._tried % cfg.NUM_APPS_BETWEEN_SLEEP == 0:
            time.sleep(cfg.SLEEP_WAIT_SERVER)

        # Find and download the target SDK version
        else:
            try:
                latest_vc = self._server.details(pkg_name)\
                        .get('details').get('appDetails').get('versionCode')
            except Exception as err:
                return str(err)

            if not latest_vc:
                msg = "Couldn't find version code information for %s." \
                    %(pkg_name)+ "\n - try downloading for the latest version."
                self._logger.warning(msg)
                res, err = _download_inner(pkg_name, apk_path)
                return None if res else err

            l_vc, r_vc, prev_tried_vc = 0, latest_vc, 0
            err = ""
            l_vc_not_found = None
            while True:
                # Sleep for every given app numbers because of Google API's
                # rejections for frequent requests
                if enable_sleep and self._tried % cfg.NUM_APPS_BETWEEN_SLEEP == 0:
                    time.sleep(cfg.SLEEP_WAIT_SERVER)

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
                min_sdk_app = aapt.get_min_sdk_version(apk_path)
                tgt_sdk_app = aapt.get_tgt_sdk_version(apk_path)
                if tgt_sdk_app == -1 or min_sdk_app == -1:
                    err = "%s - SDK versions are not found in manifest " + \
                          "(minSdkVersion or targetSdkVersion)."
                    self._logger.warning(err % (pkg_name))
                    os.popen("rm -rf " + apk_path)
                    break

                # Download succeeded
                if self._check_sdk_version(sdk_version,
                                           min_sdk_app=min_sdk_app,
                                           tgt_sdk_app=tgt_sdk_app):
                    self._logger.info("%s has been downloaded successfully." %
                                      (pkg_name))
                    return None

                # If targetSdkVersion is different, delete and continue
                elif tgt_sdk_app > sdk_version:
                    if l_vc_not_found:
                        l_vc = math.ceil((vc + l_vc_not_found) / 2)
                    r_vc = vc
                    os.popen("rm -rf " + apk_path)
                    continue
                elif tgt_sdk_app < sdk_version:
                    l_vc = vc
                    l_vc_not_found = None
                    os.popen("rm -rf " + apk_path)
                    continue

            # Not found
            return err

    def _download_az(self, pkg_name: str, cat: str, out_path: str) -> bool:
        found = []
        tmp_out = ".temp_out"
        sdk_versions = self._sdk_versions

        # Check for already downloaded app.
        if self._sdk_versions is None:
            out_path_cat = os.path.join(out_path, 'latest', cat)
            out_path_apk = os.path.join(out_path_cat, pkg_name + '.apk')
            if os.path.exists(out_path_apk):
                self._logger.info('Skip for already downloaded app.')
                self._logger.info(' - %s' % (pkg_name))
                return True
            else:
                self._logger.info("Downloading %s ..." % (pkg_name))
                command = [
                    cfg.AZ, '-k', os.environ[AZ_C.API_KEY], '-i',
                    os.environ[AZ_C.INPUT_FILE], '-pn', pkg_name, '-m',
                    'play.google.com', '-o', out_path_cat
                ]
                common.run_command(command)
                return True
        else:
            for sdk_version in self._sdk_versions:
                out_path_sdk = \
                                os.path.join(out_path, str(sdk_version), '_match') \
                                if self._sdk_version_match else \
                                os.path.join(out_path, str(sdk_version))
                out_path_cat = os.path.join(out_path_sdk, cat)
                out_path_app = os.path.join(out_path, pkg_name + '.apk')
                if os.path.exists(out_path_app):
                    self._logger.info('Skip for already downloaded app.')
                    self._logger.info(' - %s' % (pkg_name))
                    found.append(sdk_version)

        if len(found) == len(self._sdk_versions):
            return True

        # Create a temporary out directory to store downloaded apps
        if os.path.exists(tmp_out):
            command = ['rm', '-rf', tmp_out]
            common.run_command(command)
        os.mkdir(tmp_out)

        # Download all app versions that are after targetted sdk release date
        self._logger.info("Downloading %s ..." % (pkg_name))
        command = [
            cfg.AZ, '-k', os.environ[AZ_C.API_KEY], '-i',
            os.environ[AZ_C.INPUT_FILE], '-pn', pkg_name, '-m',
            'play.google.com', '-o', tmp_out
        ]

        common.run_command(command)

        # Check sdk versions of the downloaded apps
        self._logger.info(
            " - %d different version apps have been downloaded." % (len(
                glob.glob(os.path.join(tmp_out, "**/*.apk"), recursive=True))))
        for apk_path in \
            glob.glob(os.path.join(tmp_out, "**/*.apk"), recursive=True):

            # If target sdk version found, move the app to out_dir
            min_sdk_app = aapt.get_min_sdk_version(apk_path)
            tgt_sdk_app = aapt.get_tgt_sdk_version(apk_path)
            if tgt_sdk_app == -1 or min_sdk_app == -1:
                err = "%s - SDK versions are not found in manifest " + \
                        "(minSdkVersion or targetSdkVersion)."
                self._logger.warning(err % (pkg_name))
                os.popen("rm -rf " + apk_path)
                continue

            self._logger.info("  - %s (minSdkVersion: %d, targetSdkVersion: %d)" \
                % (apk_path, min_sdk_app, tgt_sdk_app))
            for sdk_version in sdk_versions:
                if sdk_version in found:
                    continue

                if self._check_sdk_version(target_sdk=sdk_version,
                                           min_sdk_app=min_sdk_app,
                                           tgt_sdk_app=tgt_sdk_app):
                    found.append(sdk_version)
                    out_path_sdk = \
                            os.path.join(out_path, str(sdk_version), '_match') \
                            if self._sdk_version_match else \
                            os.path.join(out_path, str(sdk_version))
                    out_path_cat = os.path.join(out_path_sdk, cat)
                    common.mkdir_if_not_exists(out_path_cat)
                    out_path_app = os.path.join(out_path_cat,
                                                pkg_name + '.apk')
                    command = ['mv', apk_path, out_path_app]
                    common.run_command(command)

        # Delete temporary directory containing downloaded apps
        command = ['rm', '-rf', tmp_out]
        common.run_command(command)

        if len(found) > 0:
            self._logger.info(" - Found an app with SDK version: %s.\n" %
                              (str(found)))
        else:
            self._logger.info(
                " - Couldn't find an app for any of the given SDK versions.\n")
        return True if len(found) > 0 else False

    def _set_output_path(self, out_path: str):
        if self._sdk_versions is None:
            out_path_sdk = os.path.join(out_path, 'latest', '_match') \
                            if self._sdk_version_match else \
                            os.path.join(out_path, 'latest')
            common.mkdir_if_not_exists(out_path_sdk)
        else:
            for sdk_version in self._sdk_versions:
                out_path_sdk = os.path.join(out_path, str(sdk_version), '_match') \
                                if self._sdk_version_match else \
                                os.path.join(out_path, str(sdk_version))
                common.mkdir_if_not_exists(out_path_sdk)

    def _check_mode_validity(self) -> bool:
        return False if not self._mode == Downloader.MODE_GPAPI \
            and not self._mode == Downloader.MODE_AZ else True

    def _check_env_for_mode(self) -> Tuple[bool, list]:
        # Check environment variables
        gpapi_envs = \
            [GPAPI_C.EMAIL, GPAPI_C.PASSWORD, GPAPI_C.GSFID, GPAPI_C.TOKEN]
        az_envs = [AZ_C.API_KEY, AZ_C.INPUT_FILE]

        if self._mode == Downloader.MODE_GPAPI:
            res = all([True if v in os.environ else False for v in gpapi_envs])
            return res, gpapi_envs

        elif self._mode == Downloader.MODE_AZ:
            res = all([True if v in os.environ else False for v in az_envs])
            return res, az_envs

    def _check_sdk_version(self, target_sdk: int, min_sdk_app: int,
                           tgt_sdk_app: int) -> bool:
        if self._sdk_version_match:
            return target_sdk == tgt_sdk_app
        else:
            return target_sdk <= tgt_sdk_app and target_sdk >= min_sdk_app
