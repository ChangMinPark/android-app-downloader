'''
@author: Chang Min Park (cpark22@buffalo.edu)
'''
import os
import time

from src.logger import Logger
from src.parser import *
import src.config as cfg
from src.downloader import Downloader

logger = Logger.get_instance()


def main():
    '''
    Getting App List Using AppDataParser
    '''
    '''
    # Parse app data
    #   app_data = { "SOCIAL": [{"App Id": "com.twitter.android"}],
    #               "TOOLS": [{"App Id": "cn.trinea.android.developertools"}],
    #               ... }
    n_apps_per_cat = 100
    app_list_date = "2021-06-15"
    app_data_parser = AppDataParser(top_num = n_apps_per_cat)
    app_list_dir = os.path.join(cfg.APP_LIST_DATA, app_list_date)
    app_data = app_data_parser.parse_all(app_list_dir)
    '''
    '''
    Download apps from a given package list for the target SDK version
    '''
    # Settings
    tgt_sdk_version = 27
    mode = Downloader.MODE_GPAPI

    # Set output path
    out_dir = os.path.join(os.path.abspath(cfg.OUT), str(tgt_sdk_version))
    if not os.path.exists(out_dir): os.mkdir(out_dir)

    # Initialize Downloader and VersionCodeParser (only for GPAPI)
    d = Downloader(mode)
    if mode == Downloader.MODE_GPAPI:
        vc_parser = VersionCodeParser.get_instance(tgt_sdk_version)

    # Read the given list of packages
    pkg_list = []
    with open('temp/popular_app_list_only_pkg_name', 'r') as f:
        for line in f.readlines():
            splitted = line.strip().split(',')
            if not len(splitted) == 2:
                continue
            pkg_list.append((splitted[0], splitted[1]))

    # Start downloading the packages
    count = 0
    for pkg_name, cat in pkg_list:
        count += 1
        if count == 11:
            break

        vc_found = vc_parser.find_version_code(pkg_name) \
                            if mode == Downloader.MODE_GPAPI else None

        out_cat_dir = os.path.join(out_dir, cat)
        res, err, vc = d.download(
            pkg_name,
            out_cat_dir,
            sdk_version=tgt_sdk_version,
            vc=vc_found,
            enable_sleep=True if mode == Downloader.MODE_GPAPI else False)

        # Download succeeded (only for GPAPI)
        if mode == Downloader.MODE_GPAPI:
            sdk_d = vc_parser.VersionCodeData(pkg_name, cat, str(res),
                                              "" if not err else err,
                                              "" if not vc else str(vc))
            vc_parser.write(sdk_d)

        # Sleep awhile for download fails
        if err and "busy" in err.lower():
            time.sleep(cfg.SLEEP_WAIT_SERVER)

    logger.info("Completed.")


if __name__ == "__main__":
    main()
