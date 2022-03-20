#!/usr/bin/env python3.7
'''
@author: Chang Min Park (cpark22@buffalo.edu)
'''
import os

# ----------------------- #
#   Sleep Time Settings   #
# ----------------------- #
ENABLE_SLEEP = True
SLEEP_WAIT_SERVER = 600  # 10 minutes
NUM_APPS_BETWEEN_SLEEP = 10

# -------------------- #
#   Path for Command   #
# -------------------- #
AAPT_PATH = "aapt"
AZ = "az"

# --------------- #
#   Other Paths   #
# --------------- #
OUT = "out"
DATA = "data"
RESULT = "result.txt"


# ---------------------------------------- #
#   Settings for Google Play API (GPAPI)   #
# ---------------------------------------- #
class GpapiSettings:
    LOCALE = "us_US"
    TIMEZONE = "America/Chicago"


# ---------------------------------- #
#   Environment Variables Required   #
# ---------------------------------- #
class GpLoginCredentials:
    # Make sure that these environment variables are set already
    EMAIL = "GPAPI_EMAIL"
    PASSWORD = "GPAPI_PASSWORD"
    GSFID = "GPAPI_GSFID"
    TOKEN = "GPAPI_TOKEN"


class AzCredentials:
    # Make sure that these environment variables are set already
    # - API_KEY: please refer a below website to request the key.
    #            https://androzoo.uni.lu/access
    # - INPUT_FILE: the latest input dataset can be found from a below website.
    #               https://androzoo.uni.lu/lists
    API_KEY = "AZ_API_KEY"
    INPUT_FILE = "AZ_INPUT_FILE"


# ------------- #
#   Constants   #
# ------------- #
APP_CATEGORY = {
    # Key: category name, Value: URL name to parse
    "Adventure": "GAME_ADVENTURE",
    "Racing": "GAME_RACING",
    "Puzzle": "GAME_PUZZLE",
    "Arcade": "GAME_ARCADE",
    "Board": "GAME_BOARD",
    "Educational": "GAME_EDUCATIONAL",
    "Casual": "GAME_CASUAL",
    "Card": "GAME_CARD",
    "Trivia": "GAME_TRIVIA",
    "Strategy": "GAME_STRATEGY",
    "Word": "GAME_WORD",
    "Action": "GAME_ACTION",
    "Simulation": "GAME_SIMULATION",
    "Music": "GAME_MUSIC",
    "Role Playing": "GAME_ROLE_PLAYING",
    "Casino": "GAME_CASINO",
    "Tools": "TOOLS",
    "Productivity": "PRODUCTIVITY",
    "Communication": "COMMUNICATION",
    "Social": "SOCIAL",
    "Libraries & Demo": "LIBRARIES_AND_DEMO",
    "Lifestyle": "LIFESTYLE",
    "Personalization": "PERSONALIZATION",
    "Maps & Navigation": "MAPS_AND_NAVIGATION",
    "Travel & Local": "TRAVEL_AND_LOCAL",
    "Food & Drink": "FOOD_AND_DRINK",
    "Books & Reference": "BOOKS_AND_REFERENCE",
    "Medical": "MEDICAL",
    "Entertainment": "ENTERTAINMENT",
    "Auto & Vehicles": "AUTO_AND_VEHICLES",
    "Photography": "PHOTOGRAPHY",
    "Health & Fitness": "HEALTH_AND_FITNESS",
    "Education": "EDUCATION",
    "Shopping": "SHOPPING",
    "Music & Audio": "MUSIC_AND_AUDIO",
    "Sports": "SPORTS",
    "Beauty": "BEAUTY",
    "Business": "BUSINESS",
    "Finance": "FINANCE",
    "News & Magazines": "NEWS_AND_MAGAZINES",
    "Art & Design": "ART_AND_DESIGN",
    "House & Home": "HOUSE_AND_HOME",
    "Events": "EVENTS",
    "Video Players & Editors": "VIDEO_PLAYERS",
    "Dating": "DATING",
    "Weather": "WEATHER",
    "Comics": "COMICS",
    "Parenting": "PARENTING",
}

# --------------------------------------------- #
#   Release Date for Each Android SDK Version   #
# --------------------------------------------- #
SDK_VERSION_DATE = {
    # https://en.wikipedia.org/wiki/Android_version_history
    1: '2008-09-23',
    2: '2009-02-09',
    3: '2009-04-27',
    4: '2009-09-15',
    5: '2009-10-27',
    6: '2009-12-03',
    7: '2010-01-11',
    8: '2010-05-20',
    9: '2010-12-06',
    10: '2011-02-09',
    11: '2011-02-22',
    12: '2011-05-10',
    13: '2011-07-15',
    14: '2011-10-18',
    15: '2011-12-16',
    16: '2012-07-09',
    17: '2012-11-13',
    18: '2013-07-24',
    19: '2013-10-31',
    20: '2014-06-25',
    21: '2014-11-04',
    22: '2015-03-02',
    23: '2015-10-02',
    24: '2016-08-22',
    25: '2016-10-04',
    26: '2017-08-21',
    27: '2017-12-05',
    28: '2018-08-06',
    29: '2019-09-03',
    30: '2020-09-08',
    31: '2021-10-04',
}
