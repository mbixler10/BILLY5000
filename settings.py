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
VERSION = "V4.1"          # shown on the start-up screen
STARTUP_SPLASH = True   # BILLY5000 boot + logo screen when the clock launches
STARTUP_PACE = 1.0      # start-up speed: 1.0 = easy to read (~26 s), 0.5 = quick, 1.5 = slower

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

# Show the date next to the weekday on the city pages ("SAT 11/07").
# Each city shows its OWN date, so Hong Kong is often a day ahead.
CITY_DATE_ON = True

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
     "primary": "#4B2E83", "secondary": "#B7A57A", "check": "secondary"},
    {"name": "NAVY",      "league": "football/college-football", "team": "navy",
     "primary": "#00205B", "secondary": "#C5B783", "check": "secondary"},
    {"name": "KRAKEN",    "league": "hockey/nhl", "team": "sea",
     "primary": "#001628", "secondary": "#99D9D9", "check": "secondary"},
    {"name": "DUCKS",     "league": "hockey/nhl", "team": "ana",
     "primary": "#FC4C02", "secondary": "#B9975B"},
]
# Start-up screen: each team's row types out its rallying cry instead of a check mark.
# name: (short tag, cry). Tag + cry must fit one row: about 12 letters together.
# A team not listed here gets its league + name and a check mark.
STARTUP_CHANTS = {
    "DODGERS":  ("LAD",  "ITFDB"),
    "MARINERS": ("SEA",  "GO M'S!"),
    "SEAHAWKS": ("SEA",  "12S READY"),
    "RAMS":     ("LAR",  "RAMS HOUSE"),
    "TROJANS":  ("USC",  "FIGHT ON!"),
    "HUSKIES":  ("UW",   "BOW DOWN"),
    "NAVY":     ("NAVY", "BEAT ARMY"),
    "KRAKEN":   ("SEA",  "BUOY"),
    "DUCKS":    ("ANA",  "QUACK!"),
}

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
                        "aprilfools": 8, "trash": 10, "countdown": 10,
                        "credit": 7, "fullmoon": 8, "halfbirthday": 8, "coliseum": 29, "dallasbday": 28}

# Holidays with solid-field theming. On these days every clock page (Home and each
# city) takes the field color + effect, and a greeting page leads the rotation.
# home_label (optional): what Home's bottom line says that day instead of the name.
# effect: snow | fireworks | hearts | leaves | petals | confetti | apples | gridiron |
#         candles | sparkle | ballpark | none
# art (optional): a drawn greeting page instead of plain words.
# countdown_name / countdown: False - how (or whether) the countdown page names it.
#
# ---- Opening Day Mode (Uncle Buck's idea) - see engine/baseball.py ----
# OPENING_DAYS: add each new season's date once MLB announces it. Everything keys off it:
#   * the countdown page (starts a week after the World Series, see WORLD_SERIES_END)
#   * the jersey-number countdown from 99 days out (data/jersey_countdown.txt)
#   * the Opening Day takeover, and the "opening_week" entry below that themes every
#     clock Monday-Sunday of Opening Day week
OPENING_DAY_MODE = True
OPENING_DAYS = {2027: "03-25"}
# Day the World Series ended (the countdown starts 7 days later). Unknown year = Nov 5.
WORLD_SERIES_END = {2026: "10-28"}
# Extra milestone cards on the countdown page. ("MM-DD" or "YYYY-MM-DD", kind, team)
#   kinds: truck (Truck Day; team LAD or SEA paints the truck), pitchers (pitchers &
#   catchers report), firstgame (first spring training game). 100 DAYS, ONE WEEK and the
#   night before happen on their own.
BASEBALL_MILESTONES = [
    ("2027-02-19", "firstgame", "SEA"),     # Mariners' first spring game (Peoria)
    # ("2027-02-xx", "truck", "LAD"),       # add when announced
    # ("2027-02-xx", "pitchers", ""),
]
# Opening Day takeover: these times (Seattle time), plus this many minutes before each
# of our games that day.
OPENING_DAY_ALERTS = ["07:30", "09:00", "10:30", "12:00"]
OPENING_DAY_ALERT_BEFORE_MIN = 30
# All season: live baseball shows bases, count, outs and who's up.
BASEBALL_LIVE_PAGE = True
# All season: when one of our baseball teams homers, a quick HOME RUN!! flash.
HOMER_FLASH_ON = True
HOMER_SECONDS = 8
# Opening Day week also shows a credit card after PLAY BALL!: "OPENING DAY MODE BY ...".
# Set to "" to leave it off.
OPENING_DAY_CREDIT = "UNCLE BUCK"
# Hanukkah: the evening of the first candle each year (25 Kislev). The theme runs from
# that evening's day through the last day; the greeting page shows a menorah with
# the right number of candles lit (a new candle at sundown). Add years as needed.
HANUKKAH_DATES = {2026: "12-04", 2027: "12-24", 2028: "12-12", 2029: "12-01", 2030: "12-20"}
CANDLE_LIGHTING = "16:30"

# Holidays that move with the moon or a schedule: the day(s) they're on each year.
# ["first", "last"] = a run of days. Add years as they're announced. Jewish holidays
# begin at sundown the evening BEFORE the first date shown here.
FULL_MOON_PAGE = True          # a FULL MOON TONIGHT page (with the moon's name) on full-moon days
ROSH_HASHANAH_DATES = {2026: ["09-12", "09-13"], 2027: ["10-02", "10-03"], 2028: ["09-21", "09-22"]}
YOM_KIPPUR_DATES = {2026: "09-21", 2027: "10-11", 2028: "09-30"}
SUKKOT_DATES = {2026: ["09-26", "10-02"], 2027: ["10-16", "10-22"], 2028: ["10-05", "10-11"]}
PURIM_DATES = {2027: "03-23", 2028: "03-12", 2029: "03-01"}
PASSOVER_DATES = {2027: ["04-22", "04-29"], 2028: ["04-11", "04-18"], 2029: ["03-31", "04-07"]}
LUNAR_NEW_YEAR_DATES = {2027: "02-06", 2028: "01-26"}
SUPER_BOWL_DATES = {2027: "02-14", 2028: "02-13"}
ARMY_NAVY_DATES = {2026: "12-12", 2027: "12-04"}   # moves to the first Saturday in Dec from 2027      # when the next candle "lights" on the board (Seattle sunset-ish)

SPECIAL_DAYS = [
    {"name": "NEW YEAR",       "date": "01-01", "field": "#0A0A0A", "text": "#FFCC00", "accent": "#FFCC00", "effect": "fireworks", "greeting": "HAPPY NEW YEAR!", "home_label": "HAPPY NEW YEAR"},
    {"name": "GROUNDHOG DAY",  "date": "02-02", "field": "#6B4226", "text": "#D2B48C", "accent": "#D2B48C", "effect": "none",      "greeting": "HAPPY GROUNDHOG DAY", "home_label": "HAPPY GROUNDHOG DAY"},
    {"name": "VALENTINES",     "date": "02-14", "field": "#8B0000", "text": "#FFC0CB", "accent": "#FF6FA0", "effect": "hearts",    "greeting": "HAPPY VALENTINE'S DAY", "home_label": "HAPPY VALENTINE'S DAY"},
    {"name": "PRESIDENTS DAY", "rule": {"nth_weekday": [2, 0, 3]},  "field": "#14213D", "text": "#FFFFFF", "accent": "#E03A3E", "effect": "sparkle", "greeting": "HAPPY PRESIDENTS DAY", "home_label": "HAPPY PRESIDENTS DAY"},
    {"name": "ST PATRICKS",    "date": "03-17", "field": "#0B6B23", "text": "#FFFFFF", "accent": "#2ECC40", "effect": "sparkle",   "greeting": "HAPPY ST. PATRICK'S DAY", "home_label": "HAPPY ST. PATRICK'S DAY"},
    {"name": "LABOR DAY",      "rule": {"nth_weekday": [9, 0, 1]},  "field": "#1A5276", "text": "#FFFFFF", "accent": "#7CC242", "effect": "sparkle", "greeting": "HAPPY LABOR DAY", "home_label": "HAPPY LABOR DAY"},
    {"name": "HALLOWEEN",      "date": "10-31", "field": "#1A0A2E", "text": "#FF8C00", "accent": "#9EFF3A", "effect": "leaves",    "greeting": "HAPPY HALLOWEEN", "home_label": "HAPPY HALLOWEEN"},
    {"name": "THANKSGIVING",   "rule": {"nth_weekday": [11, 3, 4]}, "field": "#3A1E0B", "text": "#FFC24D", "accent": "#E8731A", "effect": "leaves", "greeting": "HAPPY THANKSGIVING", "home_label": "HAPPY THANKSGIVING"},
    {"name": "OPENING DAY",    "opening_week": True,                "field": "#0E4A1C", "text": "#FFFFFF", "accent": "#F2C46B", "effect": "ballpark", "greeting": "PLAY BALL!"},
    {"name": "HANUKKAH",       "first_candle": "HANUKKAH_DATES",    "field": "#123A8C", "text": "#FFFFFF", "accent": "#C8D8FF", "effect": "candles", "greeting": "HAPPY HANUKKAH", "menorah": True, "home_label": "HAPPY HANUKKAH"},
    {"name": "MLK DAY",        "rule": {"nth_weekday": [1, 0, 3]},  "field": "#1C1A3A", "text": "#FFFFFF", "accent": "#F2C46B", "effect": "none",     "greeting": "HONORING DR. KING", "home_label": "MARTIN LUTHER KING JR. DAY", "countdown_name": "MLK DAY"},
    {"name": "LUNAR NEW YEAR", "dates": "LUNAR_NEW_YEAR_DATES",     "field": "#6E0A0C", "text": "#FFD34D", "accent": "#FFD34D", "effect": "fireworks", "greeting": "HAPPY LUNAR NEW YEAR", "home_label": "YEAR OF THE {ZODIAC}", "art": "lunar"},
    {"name": "SCOUTING",       "date": "02-08", "field": "#262E12", "text": "#F2E3B3", "accent": "#D9A441", "effect": "sparkle",   "greeting": "HAPPY BIRTHDAY SCOUTING", "home_label": "DAD & GRANDPA BOSETTI: EAGLE SCOUTS", "countdown_name": "SCOUTING'S BIRTHDAY", "art": "scouting"},
    {"name": "SUPER BOWL",     "dates": "SUPER_BOWL_DATES",         "field": "#0F4D1A", "text": "#FFFFFF", "accent": "#FFFFFF", "effect": "gridiron", "greeting": "SUPER BOWL SUNDAY", "home_label": "SUPER BOWL SUNDAY"},
    {"name": "MARDI GRAS",     "rule": {"easter": -47},             "field": "#3B0A57", "text": "#FFD700", "accent": "#00C878", "effect": "confetti", "greeting": "HAPPY MARDI GRAS", "home_label": "HAPPY MARDI GRAS"},
    {"name": "LEAP DAY",       "date": "02-29", "field": "#0B4F3A", "text": "#B6FF6A", "accent": "#B6FF6A", "effect": "sparkle",   "greeting": "HAPPY LEAP DAY", "home_label": "HAPPY LEAP DAY"},
    {"name": "SPRING FORWARD", "rule": {"nth_weekday": [3, 6, 2], "offset": -1}, "field": "#102A43", "text": "#9EE493", "accent": "#9EE493", "effect": "none", "greeting": "SPRING FORWARD TONIGHT", "home_label": "SPRING FORWARD TONIGHT: CLOCKS +1 HOUR", "countdown": False},
    {"name": "PI DAY",         "date": "03-14", "field": "#14213D", "text": "#FFFFFF", "accent": "#F2C46B", "effect": "none",      "greeting": "HAPPY PI DAY 3.14159", "home_label": "PI = 3.14159265...", "countdown_name": "PI DAY"},
    {"name": "SPRING",         "astro": "spring", "field": "#1E4D2B", "text": "#FFFFFF", "accent": "#FF9ECF", "effect": "sparkle", "greeting": "FIRST DAY OF SPRING", "home_label": "FIRST DAY OF SPRING", "art": "season"},
    {"name": "PURIM",          "dates": "PURIM_DATES",              "field": "#3B0A57", "text": "#FFE14D", "accent": "#FF6FD8", "effect": "confetti", "greeting": "HAPPY PURIM", "home_label": "HAPPY PURIM"},
    {"name": "ASH WEDNESDAY",  "rule": {"easter": -46},             "field": "#16141A", "text": "#E4E0EA", "accent": "#6E6878", "effect": "none",   "greeting": "ASH WEDNESDAY", "home_label": "ASH WEDNESDAY: LENT BEGINS", "art": "quiet", "subtitle": "LENT BEGINS"},
    {"name": "PALM SUNDAY",    "rule": {"easter": -7},              "field": "#0E2A16", "text": "#F2F0D8", "accent": "#5DBB4A", "effect": "none",   "greeting": "PALM SUNDAY", "home_label": "PALM SUNDAY", "art": "palm"},
    {"name": "GOOD FRIDAY",    "rule": {"easter": -2},              "field": "#140A1E", "text": "#E6DDF0", "accent": "#7A5C99", "effect": "none",   "greeting": "GOOD FRIDAY", "home_label": "GOOD FRIDAY", "art": "good_friday"},
    {"name": "EASTER",         "rule": {"easter": 0},               "field": "#3D2C6B", "text": "#FFE1F0", "accent": "#9EFFC9", "effect": "sparkle", "greeting": "HAPPY EASTER", "home_label": "HAPPY EASTER", "art": "eggs"},
    {"name": "PASSOVER",       "dates": "PASSOVER_DATES",           "field": "#102A55", "text": "#FFFFFF", "accent": "#E8D9B5", "effect": "none",     "greeting": "HAPPY PASSOVER", "home_label": "CHAG PESACH SAMEACH", "art": "matzah"},
    {"name": "EARTH DAY",      "date": "04-22", "field": "#0B2E59", "text": "#7CFC9A", "accent": "#4FC3F7", "effect": "sparkle",   "greeting": "HAPPY EARTH DAY", "home_label": "HAPPY EARTH DAY"},
    {"name": "BOATING OPENING DAY", "rule": {"nth_weekday": [5, 5, 1]}, "field": "#0A2342", "text": "#FFFFFF", "accent": "#F2C46B", "effect": "none", "greeting": "OPENING DAY BOATING SEASON", "home_label": "OPENING DAY OF BOATING SEASON", "countdown_name": "BOATING OPENING DAY", "art": "boating"},
    {"name": "KENTUCKY DERBY", "rule": {"nth_weekday": [5, 5, 1]},  "field": "#0B5D1E", "text": "#FFFFFF", "accent": "#E0115F", "effect": "petals",  "greeting": "RUN FOR THE ROSES", "home_label": "KENTUCKY DERBY DAY", "countdown_name": "KENTUCKY DERBY"},
    {"name": "MOTHERS DAY",    "rule": {"nth_weekday": [5, 6, 2]},  "field": "#5A1036", "text": "#FFD1E8", "accent": "#FF7AB6", "effect": "hearts",  "greeting": "HAPPY MOTHER'S DAY", "home_label": "HAPPY MOTHER'S DAY"},
    {"name": "FATHERS DAY",    "rule": {"nth_weekday": [6, 6, 3]},  "field": "#0A2342", "text": "#FFFFFF", "accent": "#4FC3F7", "effect": "sparkle", "greeting": "HAPPY FATHER'S DAY", "home_label": "HAPPY FATHER'S DAY"},
    {"name": "SUMMER",         "astro": "summer", "field": "#0B4F8A", "text": "#FFE066", "accent": "#FFE066", "effect": "sparkle", "greeting": "FIRST DAY OF SUMMER", "home_label": "FIRST DAY OF SUMMER: LONGEST DAY", "art": "season"},
    {"name": "DOG DAY",        "date": "08-26", "field": "#4A2C17", "text": "#FFE0B2", "accent": "#FFB74D", "effect": "sparkle",   "greeting": "HAPPY DOG DAY SCULLY!", "home_label": "WOOF! HAPPY DOG DAY, SCULLY", "countdown_name": "DOG DAY"},
    {"name": "ROSH HASHANAH",  "dates": "ROSH_HASHANAH_DATES",      "field": "#3A1C05", "text": "#FFD34D", "accent": "#E0303A", "effect": "apples",  "greeting": "SHANAH TOVAH", "home_label": "SHANAH TOVAH: A SWEET NEW YEAR", "countdown_name": "ROSH HASHANAH", "art": "apples_honey"},
    {"name": "PIRATE DAY",     "date": "09-19", "field": "#111111", "text": "#FFFFFF", "accent": "#F2C46B", "effect": "none",      "greeting": "AHOY CAPTAIN BILLY!", "home_label": "ARRR! TALK LIKE A PIRATE DAY", "countdown_name": "PIRATE DAY", "art": "pirate"},
    {"name": "YOM KIPPUR",     "dates": "YOM_KIPPUR_DATES",         "field": "#0E0E16", "text": "#E8E8F0", "accent": "#8A8AA0", "effect": "none",     "greeting": "YOM KIPPUR", "home_label": "YOM KIPPUR: DAY OF ATONEMENT", "art": "quiet", "subtitle": "DAY OF ATONEMENT"},
    {"name": "FALL",           "astro": "fall",   "field": "#5A2A0A", "text": "#FFB347", "accent": "#E8731A", "effect": "leaves",  "greeting": "FIRST DAY OF FALL", "home_label": "FIRST DAY OF FALL", "art": "season"},
    {"name": "SUKKOT",         "dates": "SUKKOT_DATES",             "field": "#0B2240", "text": "#FFFFFF", "accent": "#7CC242", "effect": "none",     "greeting": "CHAG SAMEACH", "home_label": "HAPPY SUKKOT", "countdown_name": "SUKKOT", "art": "sukkah"},
    {"name": "NAVY BIRTHDAY",  "date": "10-13", "field": "#0A1F44", "text": "#F2C46B", "accent": "#FFFFFF", "effect": "sparkle",   "greeting": "HAPPY BIRTHDAY US NAVY", "home_label": "US NAVY BIRTHDAY: SINCE 1775", "countdown_name": "NAVY BIRTHDAY"},
    {"name": "FALL BACK",      "rule": {"nth_weekday": [11, 6, 1], "offset": -1}, "field": "#2B1A0E", "text": "#FFB347", "accent": "#FFB347", "effect": "none", "greeting": "FALL BACK TONIGHT", "home_label": "FALL BACK TONIGHT: CLOCKS -1 HOUR", "countdown": False},
    {"name": "WINTER",         "astro": "winter", "field": "#0D2B4D", "text": "#DDEEFF", "accent": "#FFFFFF", "effect": "snow",    "greeting": "FIRST DAY OF WINTER", "home_label": "SHORTEST DAY: THE LIGHT COMES BACK", "art": "season"},
    {"name": "NEW YEARS EVE",  "date": "12-31", "field": "#0A0A0A", "text": "#FFCC00", "accent": "#FFFFFF", "effect": "fireworks", "greeting": "HAPPY NEW YEAR'S EVE", "home_label": "NEW YEAR'S EVE", "countdown_name": "NEW YEAR'S EVE"},
    {"name": "ROSE BOWL",      "rule": {"rose_bowl": True},         "field": "#0B3D1E", "text": "#FFFFFF", "accent": "#FF4D6D", "effect": "petals",  "greeting": "ROSE BOWL DAY", "home_label": "THE GRANDDADDY OF THEM ALL"},
    {"name": "ARMY-NAVY",      "dates": "ARMY_NAVY_DATES",          "field": "#0A1F44", "text": "#F2C46B", "accent": "#F2C46B", "effect": "sparkle", "greeting": "GO NAVY! BEAT ARMY!", "home_label": "GO NAVY! BEAT ARMY!", "countdown_name": "ARMY-NAVY GAME", "art": "beat_army"},
    {"name": "GOLD MEDAL DAY", "date": "08-11",                     "field": "#0B1F4F", "text": "#F2C46B", "accent": "#F2C46B", "effect": "sparkle", "greeting": "GOLD MEDAL DAY", "home_label": "GREAT-GRANDPA DALLAS: GOLD 1932", "countdown_name": "DALLAS'S GOLD DAY", "art": "gold_day"},
    {"name": "OLYMPIC GAMES",  "olympics": True,                     "field": "#0B1F4F", "text": "#FFFFFF", "accent": "#F2C46B", "effect": "sparkle", "greeting": "THE OLYMPIC GAMES", "home_label": "{GAMES} OLYMPICS: DAY {GAMEDAY}", "countdown": False, "art": "olympics"},
    {"name": "CHRISTMAS",      "start": "12-09", "end": "12-25",    "field": "#0A5C2E", "text": "#FFFFFF", "accent": "#D0202C", "effect": "snow",    "greeting": "MERRY CHRISTMAS", "home_label": "MERRY CHRISTMAS"},
    {"name": "BOXING DAY",     "date": "12-26", "field": "#A3121C", "text": "#FFFFFF", "accent": "#F2C46B", "effect": "none",      "greeting": "HAPPY BOXING DAY", "home_label": "HAPPY BOXING DAY"},
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
    {"name": "VETERANS DAY", "date": "11-11", "stripes": ["#B0202C", "#F0F0F0", "#2040A0"],
     "text": ["#F0F0F0", "#B0202C", "#F0F0F0"], "words": ["THANK YOU", "VETERANS", "11-11"]},
    {"name": "PEARL HARBOR", "date": "12-07", "stripes": ["#6B2C33", "#D8D4C8", "#253A5E"],
     "text": ["#8FA3C9", "#6B2C33", "#D8D4C8"], "words": ["REMEMBER", "PEARL", "HARBOR"]},
    {"name": "JUNETEENTH",   "date": "06-19", "stripes": ["#BF0A30", "#111111", "#007A3D"],
     "text": ["#FFFFFF", "#F4C430", "#FFFFFF"], "words": ["HAPPY", "JUNE-", "TEENTH"]},
]

# Veterans Day honor roll: shown right after the THANK YOU VETERANS page on 11-11,
# two names per screen. Branch is one of: ARMY, NAVY, MARINES, MERCHANT MARINE,
# AIR FORCE, COAST GUARD, SPACE FORCE.
HONOR_ROLL_DATE = "11-11"
HONOR_ROLL_SPEED = 6            # pixels per second the names roll upward (bigger = faster)
HONOR_ROLL = [
    ("DALE BIXLER", "ARMY"),
    ("JACK SKAHEN", "NAVY"),
    ("THOMAS HINES", "ARMY"),
    ("AUSTIN FLEMING", "NAVY"),
    ("RYAN MCGEOUGH", "NAVY"),
    ("NATHAN GIBSON", "ARMY"),
    ("LARRY STROMAN", "MARINES"),
    ("TED O'CONNER", "NAVY"),
    ("IAN VOSS", "MARINES"),
    ("TED STEFANI", "ARMY"),
    ("JIM KROLOPP", "NAVY"),
    ("JOHN BACH", "NAVY"),
    ("DALLAS BIXLER", "MERCHANT MARINE"),
    ("AL BOSETTI", "ARMY"),
    ("GREG MURRAY", "MARINES"),
    ("KYLE MCGHIE", "NAVY"),
    ("GYLES DREW", "ARMY"),
    ("DR. MARGARET SHANNON", "NAVY"),
    ("STUART MURPHY", "NAVY"),
]

# 9/11 reading of the names: on September 11, starting the minute the first plane
# struck (8:46 AM Eastern = 5:46 AM Pacific), the names of the 2,977 people killed
# take over the screen one at a time and run without a break until every name
# has been shown (about 2.5 hours). The rest of the day is the normal clock,
# with the WE REMEMBER page each lap.
# The names file comes from tools/get_911_names.py (run it once on the PC).
NAMES_911_ON = False           # on hold until the names are downloaded and checked
NAMES_911_START = (8, 46)       # Eastern time
NAMES_911_HOLD = 3              # seconds each name is on screen by itself
NAMES_911_TITLE_SECONDS = 4     # FDNY / NYPD / PAPD / WTC / PENTAGON ... title cards

# Pearl Harbor Day reading of the names: on December 7, starting the minute the
# attack began (7:48 AM Hawaii time = 9:48 AM in Seattle), the 2,408 killed are
# read by location: USS ARIZONA first, then each ship and station by how many
# were lost there, with rank and service under each name. Runs about two hours.
# The names file comes from tools/pearl_from_xlsx.py.
PEARL_NAMES_ON = True
PEARL_START = (7, 48)           # Hawaii time
PEARL_HOLD = 3                  # seconds each name is on screen
PEARL_TITLE_SECONDS = 5         # USS ARIZONA / 1,177 title cards

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
# Half birthdays: (name, (month, day) of the birthday, birth year). The page shows
# six months after the birthday, with the half age ("BILLY IS 2 AND A HALF!").
HALF_BIRTHDAYS = [("BILLY", (3, 21), 2025)]

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

# ----------------------------------------------------------------- Olympics
# Countdown to the next Games. Shows at the end of every Nth lap, not every lap.
OLYMPICS_ON = True
OLYMPICS_EVERY_LAPS = 3
OLYMPICS_SECONDS = 16
# After the countdown, a tribute card to Billy's great-grandfather.
# Set OLYMPICS_TRIBUTE = None to skip it.
OLYMPICS_TRIBUTE = {
    "first": "DALLAS",
    "last": "BIXLER",
    "medal": "GOLD 1932",
    "ticker": "GREAT-GRANDPA DALLAS BIXLER - OLYMPIC CHAMPION - HORIZONTAL BAR - "
              "LOS ANGELES 1932, THE XTH OLYMPIAD - LA MEMORIAL COLISEUM",
}
# Great-Grandpa Dallas's birthday page (Feb 17). Set to None to skip it.
DALLAS_BIRTHDAY = {"date": (2, 17), "ticker": "BORN FEB 17 1910 IN HUTCHINSON, KANSAS - "
                   "OLYMPIC CHAMPION, HORIZONTAL BAR, LOS ANGELES 1932"}
# Upcoming Games: (short name, ticker name, opening ceremony, closing day,
# time zone of the opening, Wikipedia medal table page). Add the next ones as
# they get close.
OLYMPICS = [
    # (short name, ticker name, opening "YYYY-MM-DD HH:MM" local, closing date, time zone, medal page)
    # Opening times after LA28 are set to the evening; fix them when the ceremonies are scheduled.
    # After the last Games on this list the countdown just stops showing - add the next ones here.
    ("LA28", "THE LOS ANGELES OLYMPICS", "2028-07-14 17:00", "2028-07-30", "America/Los_Angeles",
     "2028 Summer Olympics medal table"),
    ("FRA30", "THE FRENCH ALPS WINTER OLYMPICS", "2030-02-01 20:00", "2030-02-17", "Europe/Paris",
     "2030 Winter Olympics medal table"),
    ("BNE32", "THE BRISBANE OLYMPICS", "2032-07-23 20:00", "2032-08-08", "Australia/Brisbane",
     "2032 Summer Olympics medal table"),
    ("SLC34", "THE SALT LAKE CITY WINTER OLYMPICS", "2034-02-10 19:00", "2034-02-26", "America/Denver",
     "2034 Winter Olympics medal table"),
]
# During the Games the Olympic page shows every lap, with the medal table
# (top 4, plus Team USA if it isn't in the top 4). It stays a few days after.
MEDALS_ON = False               # on hold for now
MEDALS_SECONDS = 12
MEDALS_AFTER_DAYS = 3
