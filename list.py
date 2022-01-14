import src.config as cfg
from src.parser import AppDataParser

# Cut for without category
p = AppDataParser(top_num=500,
                  min_release_date=cfg.SDK_VERSION_DATE[27],
                  cut_for_cat=False)
data = p.parse_all('data/app_list/2021-06-15')
for idx, item in enumerate(data):
    print('%s' % (item))
