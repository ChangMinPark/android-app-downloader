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
    Download apps
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
    app_list_file = 'data/app_list/app_list_api_27/top_500_apps_no_target_with_category'
    with open(app_list_file, 'r') as f:
        for line in f.readlines():
            splitted = line.strip().split(',')
            if not len(splitted) == 2:
                continue
            pkg_list.append((splitted[0], splitted[1]))

    # Start downloading
    d = Downloader(mode, sdk_versions=sdk_versions, sdk_version_match=False)
    d.download_all(pkg_list, out_dir)

    logger.info("Completed.")


if __name__ == "__main__":
    main()
