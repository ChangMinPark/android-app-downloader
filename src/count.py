'''
@author: Chang Min Park (cpark22@buffalo.edu)
'''

# Local package
from src.parser import *


def main():

    # Settings
    tgt_sdk_version = 27

    # Parse SDK version data
    sdk_version_data_parser = \
            VersionCodeParser.get_instance(tgt_sdk_version)
    data = sdk_version_data_parser._found

    # Store in categories
    cat_data = {}
    for pkg_name in data.keys():
        item = data[pkg_name]
        if not item[CATEGORY] in cat_data:
            cat_data[item[CATEGORY]] = []
        cat_data[item[CATEGORY]].append(item)

    for cat in cat_data:
        count = 0
        for item in cat_data[cat]:
            if item[RESULT] == "True":
                count += 1

        print("[%s] - %d / %d" % (cat, count, len(cat_data[cat])))


if __name__ == "__main__":
    main()
