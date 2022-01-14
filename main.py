'''
@author: Chang Min Park (cpark22@buffalo.edu)
'''
import os
import time

from src.logger import Logger
from src.parser import *
import src.config as cfg
from src.downloader import Downloader
import src.az_utils as az

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
    Download apps using Google API
    - from a given package list for the target SDK version
    '''
    # Settings
    sdk_versions = [27]
    mode = Downloader.MODE_GPAPI

    # Set output path
    out_dir = os.path.join(os.path.abspath(cfg.OUT))
    if not os.path.exists(out_dir): os.mkdir(out_dir)

    # Read the given list of packages
    pkg_list = []  # [(pkg_name, cat), ...]
    app_list_file = 'temp/app_list_api_27/top_500_apps_list_pkg_name_with_category'
    with open(app_list_file, 'r') as f:
        for line in f.readlines():
            splitted = line.strip().split(',')
            if not len(splitted) == 2:
                continue
            pkg_list.append((splitted[0], splitted[1]))

    # Start downloading
    d = Downloader(mode)
    d.download_all(pkg_list, out_dir, sdk_versions=sdk_versions)
    logger.info("Completed.")


if __name__ == "__main__":
    main()
