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
    tgt_sdk_version = 16
    mode = Downloader.MODE_AZ

    # Set output path
    out_dir = os.path.join(os.path.abspath(cfg.OUT), str(tgt_sdk_version))
    if not os.path.exists(out_dir): os.mkdir(out_dir)

    # Read the given list of packages
    pkg_list = []  # [(pkg_name, cat), ...]
    app_list_file = 'temp/app_list_api_15/top_100_apps_list_pkg_name_with_category'
    with open(app_list_file, 'r') as f:
        for line in f.readlines():
            splitted = line.strip().split(',')
            if not len(splitted) == 2:
                continue
            pkg_list.append((splitted[0], splitted[1]))

    # Start downloading
    d = Downloader(mode)
    d.download_all(pkg_list, out_dir, sdk_version=tgt_sdk_version)
    logger.info("Completed.")
    '''
    Download apps using AndroZoo
     - from a given package list for the target SDK version
    '''
    '''
    import glob
    import src.aapt_utils as aapt
    
    # Settings
    sdk_version = 16    # 16=4.1.1_r1, 15=4.0.4_r1
    i_dir = '/Volumes/Expansion/Research/az_out'
    o_dir = '/Users/cpark22/Projects/SecondChance/android-app-downloader/out/' \
            + str(sdk_version)

    # TEMP
    apps = set()
    found = set()
    for apk_path in \
        glob.glob(os.path.join(i_dir, "**/*.apk"), recursive=True):
        try:
            # If target sdk version found, move the app to out_dir
            tgt_sdk_version = aapt.get_tgt_sdk_version(apk_path)
            pkg_name = aapt.get_package_name(apk_path)
        except Exception as e:
            print(e)
            continue

        apps.add(pkg_name)
        logger.info(" - %s, %d" %(apk_path, tgt_sdk_version))
        if tgt_sdk_version == sdk_version and not pkg_name in found:
            logger.info(" !!!!!! found %s" %(pkg_name))
            found.add(pkg_name)
            command = ['mv', apk_path, 
                        os.path.join(os.path.abspath(o_dir), pkg_name + '.apk')]
            az.run_command(command)

    print('len(apps): %d, len(found): %d' %(len(apps), len(found)))
    print(' - found: %s' %(str(found)))
    '''


if __name__ == "__main__":
    main()
