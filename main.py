#!/usr/bin/env python3.7
'''
@author: Chang Min Park (cpark22@buffalo.edu)
'''
import os

# Local packages
from src.logger import Logger
from src.parser import *
import src.config as cfg
from src.downloader import Downloader

logger = Logger.get_instance()


def main():
    '''
    Download apps
    '''
    # Settings
    sdk_version = 30
    mode = Downloader.MODE_GPAPI

    # Set output path
    out_dir = os.path.join(os.path.abspath(cfg.OUT))
    if not os.path.exists(out_dir): os.mkdir(out_dir)

    # Read the given list of packages
    # e.g., [(pkg_name, category), ...]
    pkg_list = []
    app_list_file = 'data/example_app_list'
    with open(app_list_file, 'r') as f:
        for line in f.readlines():
            splitted = line.strip().replace(' ', '').split(',')
            if not len(splitted) == 2:
                continue
            pkg_list.append((splitted[0], splitted[1]))

    # Start downloading
    d = Downloader(mode, sdk_version=None, sdk_version_match=False)
    d.download_all(pkg_list[0:3], out_dir)

    logger.info("Completed.")


if __name__ == "__main__":
    main()
