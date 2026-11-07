"""
BILLY5000 settings: the only file you should need to edit day to day.
"""

# ---------------------------------------------------------------- panel
PANEL = {
    "rows": 32,
    "cols": 64,
    "hardware_mapping": "adafruit-hat",   # Adafruit RGB Matrix Bonnet
    "gpio_slowdown": 4,                    # Pi 4 = 4. Try 2 on a Pi Zero 2 if it flickers.
    "brightness": 70,                      # 0-100
}

# ---------------------------------------------------------------- start-up
VERSION = "V2.6"          # shown on the start-up screen
STARTUP_SPLASH = True   # BILLY5000 boot + logo screen when the clock launches

# ---------------------------------------------------------------- ship's bells
BELLS_ON = True                # strike the bells every half hour (home time)
BELLS_HOLD_SECONDS = 4         # how long the page stays up after the last bell
BELLS_WAIT_MINUTES = 5         # if Christmas has the screen, wait up to this long
TRADITIONAL_DOG_WATCH = False  # False = US Navy: second dog watch strikes 5,6,7,8

# ---------------------------------------------------------------- rotation
PAGE_SECONDS = 8        # how long each page stays up
HOME_EVERY = 4          # Home shows up as every 4th page

# ---------------------------------------------------------------- places
# (airport code, name on screen, time zone, latitude, longitude)
# Latitude/longitude are for weather. Look up any airport on Google Maps:
# right-click the airport -> the first line is "lat, lon".
HOME = ("SEA", "HOME", "America/Los_Angeles", 47.45, -122.31)

PLACES = [
    ("SNA", "GRANDPA & GRANDMA",           "America/Los_Angeles", 33.68, -117.87),
    ("JFK", "AUNT ERIN & UNCLE LUKE",      "America/New_York",    40.64,  -73.78),
    ("HKG", "PETER & KATIE",               "Asia/Hong_Kong",      22.31,  113.91),
    ("SAN", "THE SKAHENS",                 "America/Los_Angeles", 32.73, -117.19),
    ("BOS", "AUNT KENDALL & UNCLE ANTONE", "America/New_York",    42.36,  -71.01),
    ("DCA", "AUNT HOPE",                   "America/New_York",    38.85,  -77.04),
    ("BWI", "THE MCGEOUGHS",               "America/New_York",    39.18,  -76.67),
    ("PRC", "AUNT SHAWN",                  "America/Phoenix",     34.65, -112.42),
    ("JAX", "AUNT PAM",                    "America/New_York",    30.49,  -81.69),
    ("ARV", "CARDINAL LODGE",              "America/Chicago",     45.93,  -89.73),
    ("DEN", "THE BELLS",                   "America/Denver",      39.86, -104.67),
    ("VCE", "VENICE",                      "Europe/Rome",         45.51,   12.35),
    ("HNL", "HONOLULU",                    "Pacific/Honolulu",    21.32, -157.92),
    ("ACK", "THE GREY LADY",               "America/New_York",    41.25,  -70.06),
    ("ATL", "UNCLE BUCK",                  "America/New_York",    33.64,  -84.43),
    ("SCC", "DEADHORSE",                   "America/Anchorage",   70.19, -148.47),
    ("AVX", "AVALON",                      "America/Los_Angeles", 33.40, -118.42),
]

# ---------------------------------------------------------------- weather
WEATHER_ON = True
WEATHER_REFRESH_MINUTES = 15
WEATHER_STALE_HOURS = 2       # hide weather if the last good update is older than this
SEATTLE_WEATHER_PAGES = True  # Seattle NOW / 12 HR / 5 DAY pages after Home

# ---------------------------------------------------------------- NOAA alerts
ALERTS_ON = True
ALERTS_REFRESH_MINUTES = 5

# ---------------------------------------------------------------- sports
SPORTS_ON = True
SPORTS_IN_SEASON_DAYS = 7      # only show a team if its next game is within this many days
SPORTS_NEXT_AFTER_FINAL_DAYS = 14  # right after a game, show the next game if it's within
                                   # this many days (covers NFL bye weeks)
# How long a final score stays up after the game, by sport. It also comes down
# the moment the team's next game starts.
SPORTS_FINAL_HOURS = {
    "football": 72,      # NFL + college football: 3 days
    "baseball": 24,      # MLB
    "hockey": 24,        # NHL
    "basketball": 24,    # college basketball (Point Loma)
}
ITFDB_SECONDS = 12             # length of the Dodgers game-start flash

# name    = just a label for the log
# league  = ESPN's sport/league path
# team    = ESPN team slug or ID number
# primary / secondary = team colors: chip color and the stripe on its edge
# check = "secondary" to color this team's boot-screen check with the secondary color
TEAMS = [
    {"name": "DODGERS",   "league": "baseball/mlb", "team": "lad",
     "primary": "#005A9C", "secondary": "#EF3E42", "itfdb": True},
    {"name": "MARINERS",  "league": "baseball/mlb", "team": "sea",
     "primary": "#0C2C56", "secondary": "#005C5C", "check": "secondary"},
    {"name": "SEAHAWKS",  "league": "football/nfl", "team": "sea",
     "primary": "#002244", "secondary": "#69BE28", "check": "secondary"},
    {"name": "RAMS",      "league": "football/nfl", "team": "lar",
     "primary": "#003594", "secondary": "#FFD100", "check": "secondary"},
    {"name": "TROJANS",   "league": "football/college-football", "team": "usc",
     "primary": "#990000", "secondary": "#FFC72C"},
    {"name": "HUSKIES",   "league": "football/college-football", "team": "wash",
     "primary": "#4B2E83", "secondary": "#B7A57A"},
    {"name": "NAVY",      "league": "football/college-football", "team": "navy",
     "primary": "#00205B", "secondary": "#C5B783"},
    {"name": "KRAKEN",    "league": "hockey/nhl", "team": "sea",
     "primary": "#001628", "secondary": "#99D9D9", "check": "secondary"},
    {"name": "DUCKS",     "league": "hockey/nhl", "team": "ana",
     "primary": "#FC4C02", "secondary": "#B9975B"},
    {"name": "SEA LIONS", "league": "basketball/mens-college-basketball", "team": "2500",
     "primary": "#0E553F", "secondary": "#FFC627", "final_only": True},
]

# ---------------------------------------------------------------- colors (R, G, B)
COLOR_CODE = (255, 160, 0)      # airport code
COLOR_AM = (255, 255, 255)      # time before noon: white
COLOR_PM = (60, 120, 255)       # time after noon: blue
COLOR_NAME = (180, 180, 180)    # name line
COLOR_TEMP = (255, 200, 120)    # temperature
COLOR_ALERT_BAR = (200, 0, 0)   # red bar behind the top line during an alert
COLOR_ALERT_TEXT = (255, 255, 255)
COLOR_ALERT_WHAT = (255, 90, 90)  # "WINTER STORM" on the explanation page

# ---------------------------------------------------------------- special days
# Copied from the old clock (test32.py). Preview any day with:
#     .\run.ps1 --at "2026-07-04 10:00"
from datetime import date

SPECIAL_DAYS_ON = True
# Seconds each special page stays up
SPECIAL_PAGE_SECONDS = {"special": 10, "striped": 10, "birthday": 12, "anniversary": 12,
                        "aprilfools": 8, "trash": 10, "countdown": 10}

# Holidays with solid-field theming. On these days every clock page (Home and each
# city) takes the field color + effect, and a greeting page leads the rotation.
# effect: snow | fireworks | hearts | leaves | sparkle | none
SPECIAL_DAYS = [
    {"name": "NEW YEAR",       "date": "01-01", "field": "#0A0A0A", "text": "#FFCC00", "accent": "#FFCC00", "effect": "fireworks", "greeting": "HAPPY NEW YEAR!"},
    {"name": "GROUNDHOG DAY",  "date": "02-02", "field": "#6B4226", "text": "#D2B48C", "accent": "#D2B48C", "effect": "none",      "greeting": "HAPPY GROUNDHOG DAY"},
    {"name": "VALENTINES",     "date": "02-14", "field": "#8B0000", "text": "#FFC0CB", "accent": "#FF6FA0", "effect": "hearts",    "greeting": "HAPPY VALENTINE'S DAY"},
    {"name": "PRESIDENTS DAY", "rule": {"nth_weekday": [2, 0, 3]},  "field": "#14213D", "text": "#FFFFFF", "accent": "#E03A3E", "effect": "sparkle", "greeting": "HAPPY PRESIDENTS DAY"},
    {"name": "ST PATRICKS",    "date": "03-17", "field": "#0B6B23", "text": "#FFFFFF", "accent": "#2ECC40", "effect": "sparkle",   "greeting": "HAPPY ST. PATRICK'S DAY"},
    {"name": "LABOR DAY",      "rule": {"nth_weekday": [9, 0, 1]},  "field": "#1A5276", "text": "#FFFFFF", "accent": "#7CC242", "effect": "sparkle", "greeting": "HAPPY LABOR DAY"},
    {"name": "HALLOWEEN",      "date": "10-31", "field": "#FF8C00", "text": "#1A0033", "accent": "#9B4DFF", "effect": "leaves",    "greeting": "HAPPY HALLOWEEN"},
    {"name": "THANKSGIVING",   "rule": {"nth_weekday": [11, 3, 4]}, "field": "#8B4513", "text": "#D4AF37", "accent": "#D2691E", "effect": "leaves", "greeting": "HAPPY THANKSGIVING"},
    {"name": "CHRISTMAS",      "start": "12-09", "end": "12-25",    "field": "#0A5C2E", "text": "#FFFFFF", "accent": "#D0202C", "effect": "snow",    "greeting": "MERRY CHRISTMAS"},
    {"name": "BOXING DAY",     "date": "12-26", "field": "#D0202C", "text": "#0A5C2E", "accent": "#0A5C2E", "effect": "none",      "greeting": "HAPPY BOXING DAY"},
]

# Flag-style days: three stripes, one word centered in each.
STRIPED_DAYS = [
    {"name": "JULY 4TH",     "date": "07-04", "stripes": ["#B0202C", "#F0F0F0", "#2040A0"],
     "text": ["#3060D0", "#B0202C", "#F0F0F0"], "words": ["HAPPY", "4TH OF", "JULY"]},
    {"name": "FLAG DAY",     "date": "06-14", "stripes": ["#B0202C", "#F0F0F0", "#2040A0"],
     "text": ["#3060D0", "#B0202C", "#F0F0F0"], "words": ["HAPPY", "FLAG", "DAY"]},
    {"name": "MEMORIAL DAY", "rule": {"nth_weekday": [5, 0, -1]}, "stripes": ["#6B2C33", "#D8D4C8", "#253A5E"],
     "text": ["#8FA3C9", "#6B2C33", "#D8D4C8"], "words": ["HAPPY", "MEMORIAL", "DAY"]},
    {"name": "WE REMEMBER",  "date": "09-11", "stripes": ["#6B2C33", "#D8D4C8", "#253A5E"],
     "text": ["#8FA3C9", "#6B2C33", "#D8D4C8"], "words": ["WE", "REMEMBER", "9/11"]},
    {"name": "CINCO DE MAYO", "date": "05-05", "stripes": ["#006341", "#F0F0F0", "#CE1126"],
     "text": ["#CE1126", "#006341", "#F0F0F0"], "words": ["FELIZ", "CINCO DE", "MAYO"]},
    {"name": "JUNETEENTH",   "date": "06-19", "stripes": ["#BF0A30", "#111111", "#007A3D"],
     "text": ["#FFFFFF", "#F4C430", "#FFFFFF"], "words": ["HAPPY", "JUNE-", "TEENTH"]},
]

# Family birthdays and anniversaries: confetti page on the day.
BIRTHDAYS = {
    (1, 6):   ["HAPPY BIRTHDAY AUNT SARAH!"],
    (1, 30):  ["HAPPY BIRTHDAY MOM!!!"],
    (3, 2):   ["GRANDPA BOSETTI BIRTHDAY"],
    (3, 18):  ["HAPPY BIRTHDAY AUNT HOPE!"],
    (3, 21):  ["HAPPY BIRTHDAY BILLY", "HAPPY BIRTHDAY JACK LEE"],
    (3, 30):  ["HAPPY ANNIVERSARY MOM & DAD"],
    (4, 24):  ["HAPPY BIRTHDAY UNCLE LUKE"],
    (6, 6):   ["HAPPY BIRTHDAY GRANDPAS BIXLER"],
    (6, 26):  ["HAPPY BIRTHDAY AUNT ERIN!!"],
    (7, 5):   ["HAPPY BIRTHDAY AUNT KENDALL"],
    (7, 10):  ["HAPPY BIRTHDAY SCULLY"],
    (7, 22):  ["GRANDMA CARDINAL BIRTHDAY"],
    (11, 7):  ["HAPPY BIRTHDAY GRANDMA BIXLER"],
    (12, 8):  ["HAPPY BIRTHDAY DAD"],
    (12, 27): ["HAPPY BIRTHDAY UNCLE BUCK"],
}
APRIL_FOOLS_DATE = (4, 1)

# Anniversary page (any BIRTHDAYS entry with "ANNIVERSARY" in it gets this page).
# Set the wedding year to have it alternate with "35 YEARS" etc.; None = leave it off.
ANNIVERSARY_YEAR = 2024   # married March 30, 2024

# Countdown page: days until the next special day (holiday, flag day, birthday,
# anniversary, April Fools). These dates are never counted down to:
COUNTDOWN_PAGE = True
COUNTDOWN_SKIP = ["09-11"]

# Trash day (same schedule as test64.py). Garbage + compost every Monday; recycling
# every OTHER Monday, counted from one confirmed recycling Monday. The reminder page
# shows Sunday ("TOMORROW") and Monday ("TODAY").
TRASH_WEEKDAY = 0                      # Monday
RECYCLING_ANCHOR = date(2026, 9, 21)   # confirmed real recycling Monday


# ---------------------------------------------------------------- flag quiz
FLAG_QUIZ_ON = True
FLAG_GUESS_SECONDS = 10       # flag alone, time to guess
FLAG_REVEAL_SECONDS = 6       # name showing
FLAG_REVEAL_STYLE = "stamp"   # "plate", "box", "corner" or "stamp"
FLAG_COUNTDOWN_BAR = True     # thin timer line along the bottom while guessing
# FLAG GAME (countries + states): one per lap, right after sports. Each round is a fresh
# random order (no repeats until all have shown). Remove a name to drop that flag.
FLAG_QUIZ_COUNTRIES = [
    "MALI", "REPUBLIC OF THE CONGO", "LITHUANIA", "BAHRAIN", "BAHAMAS", "BARBADOS",
    "BANGLADESH", "BOTSWANA", "BULGARIA", "CAMEROON", "CHAD", "CHILE", "COSTA RICA",
    "CZECHIA", "DJIBOUTI", "ESTONIA", "GAMBIA", "GEORGIA", "GHANA", "GREECE",
    "ICELAND", "SWITZERLAND", "NORWAY", "THAILAND", "HUNGARY", "JAMAICA", "ARMENIA",
    "LATVIA", "KUWAIT", "JORDAN", "FRANCE", "ITALY", "SWEDEN", "FINLAND",
    "GREENLAND", "DENMARK", "IRELAND", "IVORY COAST",
    # round 2
    "CANADA", "JAPAN", "UNITED KINGDOM", "GERMANY", "NETHERLANDS", "BELGIUM", "AUSTRIA",
    "POLAND", "UKRAINE", "ROMANIA", "RUSSIA", "LUXEMBOURG", "MONACO", "SCOTLAND",
    "ENGLAND", "FAROE ISLANDS", "NIGERIA", "BENIN", "GUINEA", "SENEGAL", "TOGO", "LIBYA",
    "SUDAN", "TANZANIA", "DR CONGO", "SEYCHELLES", "MAURITIUS", "COLOMBIA", "PERU",
    "PANAMA", "CUBA", "PUERTO RICO", "DOMINICAN REPUBLIC", "TRINIDAD & TOBAGO", "GUYANA",
    "SURINAME", "VIETNAM", "LAOS", "PALAU", "PHILIPPINES", "INDONESIA", "SINGAPORE",
    "TAIWAN", "NEW ZEALAND", "AUSTRALIA", "QATAR", "UNITED ARAB EMIRATES",
    # US states
    "TEXAS", "COLORADO", "ALASKA", "ARIZONA", "NEW MEXICO", "MARYLAND", "HAWAII",
    # round 3
    "SOUTH AFRICA", "LEBANON",
]

# ---------------------------------------------------------------- nautical lesson
# A teaching page (no guessing): one signal flag every lap, after the flag game,
# with its letter, radio name and meaning. A-Z, then the 0-9 pennants.
NAUTICAL_LESSON_ON = True
NAUTICAL_ORDER = "alphabet"    # "alphabet" (A, B, C... remembers its place) or "random"

# ----------------------------------------------------------------- lighthouses
# Night-navigation lesson: once per lap, at a random spot, a lighthouse blinks
# its real pattern. The lighthouses themselves live in engine/lighthouses.py.
LIGHTHOUSE_LESSON_ON = True
LIGHTHOUSE_MIN_SECONDS = 14       # shortest a lighthouse stays up
LIGHTHOUSE_LIST = []              # [] = all of them, or names like ["NORTH HEAD", "ALKI POINT"]
