'''
@author: Chang Min Park (cpark22@buffalo.edu)
'''
import csv
import sys
import os

# Local package
from src.config import APP_CATEGORY as CAT
import src.config as cfg


class AppDataParser:
    """ Categories to Parse """
    global APP_NAME, PACKAGE, CATEGORY, RATING, RATING_COUNT
    global SIZE, RELEASE, LAST_UPDATED, FREE, INSTALLS
    APP_NAME = "App Name"
    PACKAGE = "App Id"
    CATEGORY = "Category"
    RATING = "Rating"
    RATING_COUNT = "Rating Count"
    SIZE = "Size"
    RELEASE = 'Released'
    LAST_UPDATED = "Last Updated"
    FREE = "Free"
    INSTALLS = "Installs"

    def __init__(self,
                 top_num: int = 100,
                 min_release_date: str = None,
                 cut_for_cat: bool = True,
                 free_only: bool = True) -> None:
        self._top_num = top_num
        self._min_release_date = min_release_date
        self._cut_for_cat = cut_for_cat
        self._free_only = free_only

    """ Parse all CSV files under the given directory """

    def parse_all(self, path: str) -> dict:
        path = os.path.abspath(path)

        # Parse each CSV file in the given directory
        print("Parsing ...")
        data = {}
        csv_files = [os.path.join(path, f) \
                for f in os.listdir(path) if f.endswith(".csv")]
        for csv_file in csv_files:
            partial_data = self.parse(csv_file, cut_top_num=False)
            for cat in partial_data.keys():
                if not cat in data:
                    data[cat] = []
                data[cat] = data[cat] + partial_data[cat]

        # Sort each category
        if self._cut_for_cat:
            result = {}
            for cat in data.keys():
                sorted_data = \
                        sorted(data[cat], key=lambda d: d[INSTALLS], reverse=True)

                result[cat] = sorted_data[:self._top_num] \
                        if len(sorted_data) > self._top_num else sorted_data

        else:
            all_data = []
            for cat in data.keys():
                all_data += data[cat]

            sorted_data = sorted(all_data,
                                 key=lambda d: d[INSTALLS],
                                 reverse=True)
            result = sorted_data[:self._top_num] \
                        if len(sorted_data) > self._top_num else sorted_data

        return result

    """ Parse a single CSV file """

    def parse(self, csv_file: str, cut_top_num: bool = True) -> dict:

        # Check whether the given CSV exists
        if not os.path.exists(csv_file):
            sys.exit("Given CSV file doesn't exist: %s" % (csv_file))

        # Parse the CSV file in Dictionary form
        print(" - %s" % (csv_file))
        data = {}
        with open(csv_file, 'r') as file:
            for row in csv.DictReader(file):
                row_dict = dict(row)

                # Skip invalid data
                if not self._check_validity(row_dict):
                    continue

                # Prepare data to check
                app_name = row_dict[APP_NAME]
                pkg_name = row_dict[PACKAGE]
                category = CAT[row_dict[CATEGORY]]
                rating = row_dict[RATING]
                rating_count = row_dict[RATING_COUNT]
                size = row_dict[SIZE]
                release = row_dict[RELEASE]
                last_updated = row_dict[LAST_UPDATED]
                free = eval(row_dict[FREE])
                installs = int(row_dict[INSTALLS][:-1].replace(',', '')
                               if row_dict[INSTALLS].endswith('+') else
                               row_dict[INSTALLS].replace(',', ''))

                # Check FREE or PAID
                if self._free_only and not free:
                    continue

                # Check release date
                if self._min_release_date and \
                        self._convert_date(release) > self._min_release_date:
                    continue

                if not category in data:
                    data[category] = []
                data[category].append({
                    APP_NAME: app_name,
                    PACKAGE: pkg_name,
                    CATEGORY: category,
                    RATING: rating,
                    SIZE: size,
                    RELEASE: release,
                    LAST_UPDATED: last_updated,
                    FREE: free,
                    INSTALLS: installs
                })

        result = {}
        for cat in data.keys():
            sorted_data = \
                    sorted(data[cat], key=lambda d: d[INSTALLS], reverse=True)

            result[cat] = sorted_data[:self._top_num] \
                    if len(sorted_data) > self._top_num and cut_top_num \
                    else sorted_data

        return result

    def _check_validity(self, row_dict: dict) -> bool:
        if row_dict[FREE] != "True" and row_dict[FREE] != "False":
            return False
        elif row_dict[INSTALLS] == "" or not row_dict[INSTALLS].endswith('+'):
            return False
        elif row_dict[PACKAGE] == "" or row_dict[APP_NAME] == "":
            return False
        elif row_dict[SIZE] == "" or not row_dict[SIZE].endswith('M'):
            return False
        else:
            return True

    def _convert_date(self, date: str) -> str:
        months = {
            'Jan': '01',
            'Feb': '02',
            'Mar': '03',
            'Apr': '04',
            'May': '05',
            'Jun': '06',
            'Jul': '07',
            'Aug': '08',
            'Sep': '09',
            'Oct': '10',
            'Nov': '11',
            'Dec': '12'
        }

        try:
            year = date.split(', ')[1]
            month = months[date.split(', ')[0].split(' ')[0]]
            date = date.split(', ')[0].split(' ')[1]
            if int(date) < 10:
                date = '0' + date
            converted = '%s-%s-%s' % (year, month, date)

        except Exception as e:
            # Return a date with large numbers
            converted = '2050-12-12'

        return converted


class VersionCodeParser:
    _instances = {}

    global PACKAGE, CATEGORY, RESULT, ERR_MSG, VERSION_CODE, CATEGORIES
    PACKAGE = "App Id"
    CATEGORY = "Category"
    RESULT = "Result"
    ERR_MSG = "Error Message"
    VERSION_CODE = "Version Code"
    CATEGORIES = [PACKAGE, CATEGORY, RESULT, ERR_MSG, VERSION_CODE]

    class VersionCodeData:
        def __init__(self, pkg_name: str, cat: str, res: str, err: str,
                     version_code: str):
            self._pkg_name = pkg_name
            self._cat = cat
            self._res = res
            self._err = err
            self._version_code = version_code

    @staticmethod
    def get_instance(sdk_version: int):
        if not sdk_version in VersionCodeParser._instances:
            VersionCodeParser(sdk_version)
        return VersionCodeParser._instances[sdk_version]

    def __init__(self, sdk_version: int):

        # Create a directory if not eixsts
        sdk_data_dir = \
                os.path.join(cfg.APP_VERSION_CODE_DATA, str(sdk_version))
        if not os.path.exists(sdk_data_dir):
            os.mkdir(sdk_data_dir)

        # Parse existing data
        self._found = {}
        self._path = os.path.join(sdk_data_dir, cfg.RESULT)

        if os.path.exists(self._path):
            with open(self._path, 'r') as file:
                for row in csv.DictReader(file):
                    row_dict = dict(row)
                    self._found[row_dict[PACKAGE]] = row_dict

        # If not exist, create one and write categories (column)
        else:
            with open(self._path, 'w') as file:
                file.write(','.join(CATEGORIES))

        VersionCodeParser._instances[sdk_version] = self

    """ Find version code for the given package name from parsed data """

    def find_version_code(self, pkg_name: str) -> int:

        # Not found
        if not pkg_name in self._found \
                or self._found[pkg_name][VERSION_CODE] == "":
            return None

        # Found
        vc_found = self._found[pkg_name][VERSION_CODE]
        return int(vc_found)

    """ Write newly found version code data """

    def write(self, data: VersionCodeData) -> None:

        if data._pkg_name in self._found:
            return

        self._found[data._pkg_name] = {
            PACKAGE: data._pkg_name,
            CATEGORY: data._cat,
            RESULT: data._res,
            ERR_MSG: data._err,
            VERSION_CODE: data._version_code
        }

        with open(self._path, "a") as f:
            l = [
                data._pkg_name, data._cat, data._res, data._err,
                data._version_code
            ]
            f.write(",".join(l) + "\n")


# -------- #
#   TEST   #
# -------- #
'''
# Cut for each category
p = AppDataParser(top_num=100, cut_for_cat=True)
data = p.parse_all('data/app_list/2021-06-15')
for cat in data.keys():
    print("\n[ %s ] - %d" %(cat, len(data[cat])))
    for app in data[cat]:
        print(app)

# Cut for without category
p = AppDataParser(top_num=500, min_release_date=cfg.SDK_VERSION_DATE[15],
        cut_for_cat=False)
data = p.parse_all('../data/app_list/2021-06-15')
for idx, item in enumerate(data):
    print('%s' %(item))
'''
