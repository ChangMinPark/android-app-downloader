#!/usr/bin/env python3.7
'''
@author: Chang Min Park (cpark22@buffalo.edu)
'''

import sys

sys.path.append('..')

from src.parser import AppDataParser

# Cut for without category
p = AppDataParser(top_num=10, min_release_date=None, cut_for_cat=False)
data = p.parse_all('../data/app_rank/2021-06-15')
for idx, item in enumerate(data):
    print('[%d] %s, %s' % (idx, item['App Id'], item['Category']))
