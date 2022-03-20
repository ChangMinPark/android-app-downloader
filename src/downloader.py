#!/usr/bin/env python3.7
'''
@author: Chang Min Park (cpark22@buffalo.edu)
'''

import sys
import os
import math
import time
import glob
from typing import Tuple

# Local package
from src.gpapi.googleplay import GooglePlayAPI
from src.logger import Logger
import src.aapt_utils as aapt
import src.common as common
from src.config import GpLoginCredentials as GPAPI_C
from src.config import GpapiSettings as GS
from src.config import AzCredentials as AZ_C
import src.config as cfg

encoding = "utf-8"


class Downloader:
    # Download Mode
    # - GPAPI: Google Play API (https://github.com/NoMore201/googleplay-api)
    # - AZ: AndroZoo (https://github.com/ArtemKushnerov/az)
    MODE_GPAPI = 'GPAPI'
    MODE_AZ = 'AZ'

    def __init__(self, mode: str, sdk_version: str, \
                                    sdk_version_match: bool=False) -> None:
        self._sdk_version = str(sdk_version) if sdk_version else 'latest'
        self._sdk_version_match = sdk_version_match
        self._tried = 0
        self._logger = Logger.get_instance()
        self._gpapi_server = \
            GooglePlayAPI(locale=GS.LOCALE, timezone=GS.TIMEZONE)

        # Set the mode
        self._mode = mode
        self._check_mode_validity()
        self._check_env_for_mode()

    def download_all(self, pkg_list: list, out_path: str) -> None:
        '''
        Download apps in the given list for the given sdk version.
        '''
        # Login if the given mode is GPAPI
        if self._mode == Downloader.MODE_GPAPI: self._login_gpapi()

        # Download apps with either Google Play API or AndroZoo tool
        for pkg_name, cat in pkg_list:
            downloaded = self._prep_out_path(out_path, cat, pkg_name)
            if downloaded: continue

            msg = "[%s] Downloading %s ..." % (self._mode, pkg_name)
            self._logger.info(msg)
            apk_path = self._get_apk_path(out_path, cat, pkg_name)
            if self._mode == Downloader.MODE_GPAPI:
                self._download_gpapi(pkg_name, apk_path)
            elif self._mode == Downloader.MODE_AZ:
                self._download_az(pkg_name, apk_path)

    # ----------------- #
    #   Local Methods   #
    # ----------------- #
    def _download_gpapi(self, pkg_name: str, apk_path: str) -> str:
        '''
        Download the app paackage to the given path with Google Play API
        - If 'sdk_version' is not given, download the latest version
        - If 'sdk_version' is given, find and download using binary serach
        '''
        def download_inner(pkg_name: str,
                           apk_path: str,
                           vc: str = None) -> Tuple[bool, str]:
            # Sleep for every given app numbers because of Google API's
            # rejections for frequent requests
            self._tried += 1
            if cfg.ENABLE_SLEEP and self._tried % cfg.NUM_APPS_BETWEEN_SLEEP == 0:
                time.sleep(cfg.SLEEP_WAIT_SERVER // 10)
            try:
                fl = self._gpapi_server.download(pkg_name) if vc is None \
                    else self._gpapi_server.download(pkg_name, versionCode=vc)
                self._write_apk(fl, apk_path)
                return True, None
            except Exception as e:
                err = ' - GPAPI failed to download (vc: %s). %s' % (vc, e)
                self._logger.debug(err)
                return False, str(e)

        def get_latest_vc(pkg_name: str) -> str:
            # Get the latest version code from Google Play API server
            try:
                latest_vc = self._gpapi_server.details(pkg_name)\
                        .get('details').get('appDetails').get('versionCode')
                return latest_vc
            except Exception as err:
                return str(err)

        # Download the Latest Version if SDK version is not provided
        if self._sdk_version is 'latest':
            res, err = download_inner(pkg_name, apk_path)

        # Find and download the target SDK version
        else:
            latest_vc = get_latest_vc(pkg_name)
            if not latest_vc:
                err = " - Couldn't find version code information for %s." \
                    %(pkg_name)+ "\n - try downloading for the latest version."
                self._logger.warning(err)
                res, err = download_inner(pkg_name, apk_path)

            else:
                l_vc, r_vc, prev_tried_vc = 0, latest_vc, 0
                l_vc_not_found = None
                while True:
                    if l_vc_not_found:
                        vc = math.ceil((l_vc_not_found + r_vc) / 2)
                    else:
                        vc = math.ceil((l_vc + r_vc) / 2)

                    if prev_tried_vc == vc:
                        if vc == l_vc_not_found:
                            err = " - download unavailable for the given " +\
                                 "sdk_version: %s" %(self._sdk_version)
                        else:
                            err = " - does not exist for the given " +\
                                "sdk_version: %s" %(self._sdk_version)
                        self._logger.debug(err)
                        res = False
                        break

                    # Download
                    prev_tried_vc = vc
                    res, err = download_inner(pkg_name, apk_path, vc=vc)
                    if not res:
                        l_vc = vc
                        l_vc_not_found = l_vc
                        continue

                    # Find targetSdkVersion information
                    min_sdk_app = aapt.get_min_sdk_version(apk_path)
                    tgt_sdk_app = aapt.get_tgt_sdk_version(apk_path)
                    if tgt_sdk_app == -1 or min_sdk_app == -1:
                        err = " - SDK versions are not found in manifest "+\
                            "(minSdkVersion or targetSdkVersion)."
                        self._logger.warning(err)
                        common.rm(apk_path)
                        res = False
                        break

                    # Download succeeded
                    if self._check_sdk_version(int(self._sdk_version),
                                               min_sdk_app=min_sdk_app,
                                               tgt_sdk_app=tgt_sdk_app):
                        res = True
                        break

                    # If targetSdkVersion is different, delete and continue
                    elif tgt_sdk_app > int(self._sdk_version):
                        if l_vc_not_found:
                            l_vc = math.ceil((vc + l_vc_not_found) / 2)
                        r_vc = vc
                        common.rm(apk_path)
                        continue
                    elif tgt_sdk_app < int(self._sdk_version):
                        l_vc = vc
                        l_vc_not_found = None
                        common.rm(apk_path)
                        continue

        msg = " - Found an app with the given SDK version." if res else \
        " - Couldn't find an app for any of the given SDK versions."
        self._logger.info(msg)

        # Sleep awhile for download fails
        if err and "busy" in err.lower():
            time.sleep(cfg.SLEEP_WAIT_SERVER)
        return None if res else err

    def _download_az(self, pkg_name: str, apk_path: str) -> bool:
        '''
        Download the given app using AndroZoo tool
        '''
        def download_inner(path: str):
            command = [cfg.AZ, \
                '-k', os.environ[AZ_C.API_KEY], \
                '-i', os.environ[AZ_C.INPUT_FILE], \
                '-pn', pkg_name, \
                '-m', 'play.google.com', \
                '-o', path
            ]
            if not self._sdk_version == 'latest':
                # sdk_release_date = cfg.SDK_VERSION_DATE[int(self._sdk_version)]
                sdk_release_date = '2008-09-23'
                command += ['-d', sdk_release_date + ':']
            common.run_command(command)

        # Download the latest if SDK version is not given
        res, err = False, ''
        if self._sdk_version is 'latest':
            download_inner(apk_path)
            res = True

        else:
            # Create a temporary out directory to store downloaded apps
            tmp_out = ".temp_out"
            common.mkdir_if_not_exists(tmp_out)

            # Download all app versions that are after targetted sdk release date
            download_inner(tmp_out)

            # Check sdk versions of the downloaded apps
            downloaded = glob.glob(os.path.join(tmp_out, "**/*.apk"),
                                   recursive=True)
            msg = " - %d different version apps have been downloaded." \
                %(len(downloaded))
            self._logger.info(msg)
            for apk in downloaded:

                # If target sdk version found, move the app to out_dir
                min_sdk_app = aapt.get_min_sdk_version(apk)
                tgt_sdk_app = aapt.get_tgt_sdk_version(apk)
                if tgt_sdk_app == -1 or min_sdk_app == -1:
                    err = " - SDK versions are not found in manifest " + \
                            "(minSdkVersion or targetSdkVersion)."
                    self._logger.debug(err)
                    common.rm(apk)
                    continue

                msg = "  - %s (minSdkVersion: %d, targetSdkVersion: %d)" \
                    %(apk, min_sdk_app, tgt_sdk_app)
                self._logger.debug(msg)

                if self._check_sdk_version(target_sdk=int(self._sdk_version),
                                           min_sdk_app=min_sdk_app,
                                           tgt_sdk_app=tgt_sdk_app):
                    command = ['mv', apk, apk_path]
                    common.run_command(command)
                    res = True
                    break

            # Delete temporary directory containing downloaded apps
            common.rm(tmp_out)

        msg = " - Found an app with the given SDK version." if res else \
            " - Couldn't find an app for any of the given SDK versions."
        self._logger.info(msg)
        return None if res else err

    def _prep_out_path(self, out_path: str, cat: str, pkg_name: str) -> bool:
        '''
        Prepare output path 
        '''
        downloaded = False
        out_path_sdk = os.path.join(out_path, self._sdk_version)
        if self._sdk_version_match and self._sdk_version != 'latest':
            out_path_sdk += '_match'
        out_path_cat = os.path.join(out_path_sdk, cat)
        out_path_pkg = os.path.join(out_path_cat, pkg_name + '.apk')
        common.mkdir_if_not_exists(out_path_sdk)
        common.mkdir_if_not_exists(out_path_cat)
        if os.path.exists(out_path_pkg):
            self._logger.info('Skip for already downloaded app: %s' %
                              (pkg_name))
            downloaded = True
        return downloaded

    def _check_mode_validity(self) -> None:
        '''
        Checks if the given mode is valid
        '''
        res = False if not self._mode == Downloader.MODE_GPAPI \
            and not self._mode == Downloader.MODE_AZ else True
        if not res:
            sys.exit("Given mode is not valid: %s" % (self.mode))

    def _check_env_for_mode(self) -> None:
        '''
        Check environment variables
        '''
        if self._mode == Downloader.MODE_GPAPI:
            envs = \
                [GPAPI_C.EMAIL, GPAPI_C.PASSWORD, GPAPI_C.GSFID, GPAPI_C.TOKEN]
            res = all([True if v in os.environ else False for v in envs])
        elif self._mode == Downloader.MODE_AZ:
            envs = [AZ_C.API_KEY, AZ_C.INPUT_FILE]
            res = all([True if v in os.environ else False for v in envs])
        if not res:
            sys.exit("Please set global variables for:\n - " + str(envs))

    def _check_sdk_version(self, target_sdk: int, min_sdk_app: int,
                           tgt_sdk_app: int) -> bool:
        '''
        Check SDK version if matches or is above the minimum SDK version
        '''
        if self._sdk_version_match:
            return target_sdk == tgt_sdk_app
        else:
            return target_sdk <= tgt_sdk_app and target_sdk >= min_sdk_app

    def _write_apk(self, fl: dict, apk_path: str) -> None:
        '''
        Write downloaded apk file
        '''
        with open(apk_path, "wb") as apk_file:
            for chunk in fl.get("file").get("data"):
                apk_file.write(chunk)

    def _login_gpapi(self):
        '''
        Login to Google Play API server
        '''
        #            self._server.login(email=os.environ[GPAPI_C.EMAIL],
        #                               password=os.environ[GPAPI_C.PASSWORD],
        #                               gsfId=os.environ[GPAPI_C.GSFID],
        #                               authSubToken=os.environ[GPAPI_C.TOKEN])
        self._gpapi_server.login(email=os.environ[GPAPI_C.EMAIL],
                                 password=os.environ[GPAPI_C.PASSWORD],
                                 gsfId=None,
                                 authSubToken=None)

        self._logger.info("Google Play login successful")

    def _get_apk_path(self, out_path: str, cat: str, pkg_name: str) -> str:
        '''
        Get APK path for the given category and package name 
        '''
        sdk_path = os.path.join(out_path, self._sdk_version)
        if self._sdk_version_match and self._sdk_version != 'latest':
            sdk_path += '_match'
        apk_path = os.path.join(sdk_path, cat, pkg_name + '.apk')
        return apk_path
