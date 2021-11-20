'''
@author: Chang Min Park (cpark22@buffalo.edu)
'''
import os

# ----------------------- #
#   Sleep Time Settings   #
# ----------------------- #
SLEEP_WAIT_SERVER = 600  # 10 minutes
NUM_APPS_BETWEEN_SLEEP = 10

# -------------------- #
#   Path for Command   #
# -------------------- #
AAPT_PATH = "aapt"

# --------------- #
#   Other Paths   #
# --------------- #
OUT = "out"
DATA = "data"
APP_LIST_DATA = os.path.join(DATA, "app_list")
APP_VERSION_CODE_DATA = os.path.join(DATA, "app_version_code")
RESULT = "result.txt"


# --------------------------------------------- #
#   Google Play API (GPAPI) Related Variables   #
# --------------------------------------------- #
class GpapiSettings:
    LOCALE = "us_US"
    TIMEZONE = "America/Chicago"


class LoginCredentials:
    # Make sure that all of these are set already
    EMAIL = "GPAPI_EMAIL"
    PASSWORD = "GPAPI_PASSWORD"
    GSFID = "GPAPI_GSFID"
    TOKEN = "GPAPI_TOKEN"


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
