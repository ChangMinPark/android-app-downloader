#!/usr/bin/env python3.7
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
    ''' 
    Categories to Parse
    '''
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

    def parse_all(self, path: str) -> dict:
        path = os.path.abspath(path)
        '''
        Parse all CSV files under the given directory
        '''

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

    def parse(self, csv_file: str, cut_top_num: bool = True) -> dict:
        '''
        Parse a single CSV file
        '''
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
        '''
        Check validity of the given row dictionary
        '''
        if row_dict[FREE] != "True" and row_dict[FREE] != "False":
            return False
        elif row_dict[INSTALLS] == "" or not row_dict[INSTALLS].endswith('+'):
            return False
        elif row_dict[PACKAGE] == "" or row_dict[APP_NAME] == "":
            return False
        elif row_dict[SIZE] == "":
            return False
        else:
            return True

    def _convert_date(self, date: str) -> str:
        '''
        Convert the given date to a predefined string format
        '''
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