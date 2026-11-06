"""
santa.py - ELFNET / TOY Santa Alert system for the 64x32 world clock.

NOV 1-DEC 23  TEST FLIGHTS
  A few times an hour (daytime only) the clock takes over with an
  TOY message (Top-secret Orders for Yuletide):
    JOLLY/HOHOHO strobe -> TOY header teletyped in amber -> authentication code
    match -> polar radar of the sleigh somewhere in the Arctic -> telemetry
    (place, MACH speed, lat/long) -> message to Billy -> SANTCON -> END OF MSG
  SANTCON is Santa's DEFCON: it counts down 5 -> 1 as Christmas gets close.

DEC 24  LIVE MISSION
  Same alerts, but "NOT A DRILL" at SANTCON 1, followed by a radar scope.
  The radar page also joins the normal page rotation: a sweeping scope with
  Sleigh 1 spiraling in toward home, the airport code where Santa was just
  spotted, and a T-minus to Seattle. Sightings are random cities where it
  just turned midnight, so Santa sweeps west from the dateline (2am Seattle
  time) and lands home at midnight.

DEC 25  Midnight: Santa over SEA (HOME!) for 10 minutes, then on through
        Alaska, Hawaii and the South Pacific to American Samoa, the last
        place to reach Christmas. 4am: RTB (return to base, North Pole).
        6am onward: MISSION COMPLETE.

Fonts: 5x7.bdf and 7x13.bdf from BILLY5000's fonts/ folder, loaded the moment
this file is imported (before the panel starts) so they can never hit the old
"Permission denied" crash.

Preview from the BILLY5000 folder (Ctrl+C to stop):
    .\run.ps1 --demo-santa                              TOY alert right now
    .\run.ps1 --demo-santa --at "2026-12-10 09:00"      test-flight TOY
    .\run.ps1 --demo-santa --at "2026-12-24 15:30"      live TOY (Christmas Eve)
    .\run.ps1 --at "2026-12-24 15:30"                   radar page in the rotation
    .\run.ps1 --at "2026-12-25 08:00"                   mission complete
"""

import math
from pathlib import Path
import random
import time
from datetime import datetime, date, timedelta
from zoneinfo import ZoneInfo

# ---------------------------------------------------------------------------
# Tiny built-in drawing kit (colors + BDF fonts), so santa.py draws onto
# anything with SetPixel(x, y, r, g, b): a real matrix canvas, the emulator,
# or test32.py's Frame. No rgbmatrix import needed.
# ---------------------------------------------------------------------------
class _Color:
    __slots__ = ("red", "green", "blue")

    def __init__(self, r, g, b):
        self.red, self.green, self.blue = r, g, b


class _Font:
    def __init__(self):
        self.glyphs = {}            # char -> (dwidth, w, h, xoff, yoff, rows)

    def LoadFont(self, path):
        enc = dw = None
        bbx = (0, 0, 0, 0)
        rows, in_bitmap = [], False
        with open(path, encoding="latin-1") as fh:
            for line in fh:
                parts = line.split()
                if not parts:
                    continue
                key = parts[0]
                if key == "ENCODING":
                    enc = int(parts[1])
                elif key == "DWIDTH":
                    dw = int(parts[1])
                elif key == "BBX":
                    bbx = tuple(int(v) for v in parts[1:5])
                elif key == "BITMAP":
                    rows, in_bitmap = [], True
                elif key == "ENDCHAR":
                    in_bitmap = False
                    if enc is not None and 0 <= enc < 0x110000:
                        w = bbx[0]
                        bits = [[(int(r, 16) >> (len(r) * 4 - 1 - i)) & 1 for i in range(w)] for r in rows]
                        self.glyphs[chr(enc)] = (dw if dw is not None else w, *bbx, bits)
                    enc = dw = None
                elif in_bitmap:
                    rows.append(key)


def _draw_text(canvas, font, x, y, color, text):
    """Draw text with its baseline at y; returns the width drawn."""
    cx = x
    for ch in text:
        g = font.glyphs.get(ch) or font.glyphs.get("?")
        if not g:
            continue
        dw, w, h, xoff, yoff, bits = g
        top = y - yoff - h
        for j, row in enumerate(bits):
            for i, on in enumerate(row):
                if on:
                    px, py = cx + xoff + i, top + j
                    if 0 <= px < 64 and 0 <= py < 32:
                        canvas.SetPixel(px, py, color.red, color.green, color.blue)
        cx += dw
    return cx - x


class graphics:                     # same names the rgbmatrix library uses
    Color = _Color
    Font = _Font
    DrawText = staticmethod(_draw_text)

# ---------------------------------------------------------------------------
# Settings - change these freely
# ---------------------------------------------------------------------------
KID_NAME = "BILLY"

# Who sends the alerts (max 6 characters so "FROM: ELFNET" fits).
# Other ideas: "ELFCOM", "NORELF", "NPHQ"
COMMAND = "ELFNET"

# The message type shown in the header: TOY = Top-secret Orders for Yuletide.
ACRONYM = "TOY"

# Priority line - flips between these once it has typed out.
PRIORITY = ["PRI: JOLLY", "PRI: HOHOHO"]

# Big words in the opening red strobe (max 9 characters).
STROBE_WORDS = ["JOLLY", "HOHOHO"]
HOME_TZ = ZoneInfo("America/Los_Angeles")   # same as Home in settings.py

TEST_SEASON_START = (11, 1)   # test flights start Nov 1 every year
ALERTS_PER_HOUR = 2        # TOY alerts per hour
ALERT_FIRST_HOUR = 0       # no alerts before 7am...
ALERT_LAST_HOUR = 23       # ...or after 7:59pm
RADAR_SECONDS = 12         # how long the radar page stays up in the rotation
CHRISTMAS_MORNING_HOUR = 6 # MISSION COMPLETE starts at 6am Dec 25

# Santa sightings. On Christmas Eve, Santa is "spotted" at a random city
# where it has just turned midnight (local time between 12:00 and 1:00am on
# Dec 25), so he sweeps west from the dateline. A new sighting is picked every
# SIGHTING_MINUTES. Add any city: (airport code, name max 12 chars, time zone).
# He passes over home (HOME_CODE) at midnight Seattle time, then keeps going
# through Alaska, Hawaii and the South Pacific until American Samoa - the last
# place on Earth to reach Christmas - then returns to base (RTB).
SIGHTING_MINUTES = 3
HOME_CODE = "SEA"
SIGHTINGS = [
    ("CXI", "KIRITIMATI",   "Pacific/Kiritimati"),
    ("TBU", "TONGA",        "Pacific/Tongatapu"),
    ("APW", "SAMOA",        "Pacific/Apia"),
    ("AKL", "AUCKLAND",     "Pacific/Auckland"),
    ("WLG", "WELLINGTON",   "Pacific/Auckland"),
    ("CHC", "CHRISTCHURCH", "Pacific/Auckland"),
    ("NAN", "FIJI",         "Pacific/Fiji"),
    ("MAJ", "MARSHALL IS",  "Pacific/Majuro"),
    ("FUN", "TUVALU",       "Pacific/Funafuti"),
    ("PKC", "KAMCHATKA",    "Asia/Kamchatka"),
    ("SYD", "SYDNEY",       "Australia/Sydney"),
    ("MEL", "MELBOURNE",    "Australia/Melbourne"),
    ("HBA", "HOBART",       "Australia/Hobart"),
    ("BNE", "BRISBANE",     "Australia/Brisbane"),
    ("GUM", "GUAM",         "Pacific/Guam"),
    ("POM", "PORT MORESBY", "Pacific/Port_Moresby"),
    ("ADL", "ADELAIDE",     "Australia/Adelaide"),
    ("DRW", "DARWIN",       "Australia/Darwin"),
    ("NRT", "TOKYO",        "Asia/Tokyo"),
    ("KIX", "OSAKA",        "Asia/Tokyo"),
    ("ICN", "SEOUL",        "Asia/Seoul"),
    ("PEK", "BEIJING",      "Asia/Shanghai"),
    ("HKG", "HONG KONG",    "Asia/Hong_Kong"),
    ("TPE", "TAIPEI",       "Asia/Taipei"),
    ("MNL", "MANILA",       "Asia/Manila"),
    ("SIN", "SINGAPORE",    "Asia/Singapore"),
    ("PER", "PERTH",        "Australia/Perth"),
    ("BKK", "BANGKOK",      "Asia/Bangkok"),
    ("SGN", "HO CHI MINH",  "Asia/Ho_Chi_Minh"),
    ("CGK", "JAKARTA",      "Asia/Jakarta"),
    ("DAC", "DHAKA",        "Asia/Dhaka"),
    ("KTM", "KATHMANDU",    "Asia/Kathmandu"),
    ("DEL", "DELHI",        "Asia/Kolkata"),
    ("BOM", "MUMBAI",       "Asia/Kolkata"),
    ("KHI", "KARACHI",      "Asia/Karachi"),
    ("DXB", "DUBAI",        "Asia/Dubai"),
    ("MCT", "MUSCAT",       "Asia/Muscat"),
    ("GYD", "BAKU",         "Asia/Baku"),
    ("MRU", "MAURITIUS",    "Indian/Mauritius"),
    ("SVO", "MOSCOW",       "Europe/Moscow"),
    ("IST", "ISTANBUL",     "Europe/Istanbul"),
    ("NBO", "NAIROBI",      "Africa/Nairobi"),
    ("ATH", "ATHENS",       "Europe/Athens"),
    ("HEL", "HELSINKI",     "Europe/Helsinki"),
    ("CAI", "CAIRO",        "Africa/Cairo"),
    ("BETH", "BETHLEHEM",   "Asia/Hebron"),   # no airport - "BETH" fits the radar
    ("JNB", "JOHANNESBURG", "Africa/Johannesburg"),
    ("CDG", "PARIS",        "Europe/Paris"),
    ("VCE", "VENICE",       "Europe/Rome"),
    ("FCO", "ROME",         "Europe/Rome"),
    ("BER", "BERLIN",       "Europe/Berlin"),
    ("MAD", "MADRID",       "Europe/Madrid"),
    ("AMS", "AMSTERDAM",    "Europe/Amsterdam"),
    ("ZRH", "ZURICH",       "Europe/Zurich"),
    ("OSL", "OSLO",         "Europe/Oslo"),
    ("ARN", "STOCKHOLM",    "Europe/Stockholm"),
    ("LHR", "LONDON",       "Europe/London"),
    ("DUB", "DUBLIN",       "Europe/Dublin"),
    ("LIS", "LISBON",       "Europe/Lisbon"),
    ("KEF", "REYKJAVIK",    "Atlantic/Reykjavik"),
    ("PDL", "AZORES",       "Atlantic/Azores"),
    ("RAI", "CAPE VERDE",   "Atlantic/Cape_Verde"),
    ("GOH", "NUUK",         "America/Nuuk"),
    ("FEN", "NORONHA",      "America/Noronha"),
    ("GRU", "SAO PAULO",    "America/Sao_Paulo"),
    ("MVD", "MONTEVIDEO",   "America/Montevideo"),
    ("GIG", "RIO",          "America/Sao_Paulo"),
    ("EZE", "BUENOS AIRES", "America/Argentina/Buenos_Aires"),
    ("SJU", "SAN JUAN",     "America/Puerto_Rico"),
    ("YHZ", "HALIFAX",      "America/Halifax"),
    ("JFK", "NEW YORK",     "America/New_York"),
    ("BOS", "BOSTON",       "America/New_York"),
    ("DCA", "WASHINGTON",   "America/New_York"),
    ("BWI", "BALTIMORE",    "America/New_York"),
    ("JAX", "JACKSONVILLE", "America/New_York"),
    ("ATL", "ATLANTA",      "America/New_York"),
    ("MIA", "MIAMI",        "America/New_York"),
    ("YYZ", "TORONTO",      "America/Toronto"),
    ("ORD", "CHICAGO",      "America/Chicago"),
    ("DFW", "DALLAS",       "America/Chicago"),
    ("MSY", "NEW ORLEANS",  "America/Chicago"),
    ("MEX", "MEXICO CITY",  "America/Mexico_City"),
    ("DEN", "DENVER",       "America/Denver"),
    ("SLC", "SALT LAKE",    "America/Denver"),
    ("PRC", "PRESCOTT",     "America/Phoenix"),
    ("PHX", "PHOENIX",      "America/Phoenix"),
    ("SEA", "SEATTLE",      "America/Los_Angeles"),   # home!
    ("SNA", "ORANGE CO",    "America/Los_Angeles"),
    ("SAN", "SAN DIEGO",    "America/Los_Angeles"),
    ("LAX", "LOS ANGELES",  "America/Los_Angeles"),
    ("SFO", "SAN FRAN",     "America/Los_Angeles"),
    ("PDX", "PORTLAND",     "America/Los_Angeles"),
    ("YVR", "VANCOUVER",    "America/Vancouver"),
    ("LAS", "LAS VEGAS",    "America/Los_Angeles"),
    ("ANC", "ANCHORAGE",    "America/Anchorage"),
    ("JNU", "JUNEAU",       "America/Juneau"),
    ("NHV", "MARQUESAS",    "Pacific/Marquesas"),
    ("HNL", "HONOLULU",     "Pacific/Honolulu"),
    ("OGG", "MAUI",         "Pacific/Honolulu"),
    ("PPT", "TAHITI",       "Pacific/Tahiti"),
    ("RAR", "COOK ISLANDS", "Pacific/Rarotonga"),
    ("ADK", "ADAK",         "America/Adak"),
    ("PPG", "AMER SAMOA",   "Pacific/Pago_Pago"),
    ("IUE", "NIUE",         "Pacific/Niue"),
    ("MDY", "MIDWAY",       "Pacific/Midway"),
]

# Santa gets 10 minutes over home right at midnight before moving on.
HOME_SPOTLIGHT_MINUTES = 10

# Messages to Billy during December test flights - two lines, max 12
# characters each. {name} becomes KID_NAME. Add as many as you like.
MESSAGES = [
    ("RUDOLPH SAYS", "HI {name}!"),
    ("NICE LIST", "STATUS: ON"),
    ("TEST FLIGHT", "WENT GREAT"),
    ("ELVES ARE", "BUILDING"),
    ("SANTA SAYS", "BE KIND"),
    ("BRUSH TEETH", "TONIGHT"),
    ("EAT YOUR", "VEGGIES"),
    ("LISTEN TO", "MOM & DAD"),
    ("REINDEER IN", "TRAINING"),
    ("SLEIGH IS", "FUELED UP"),
    ("COOKIES", "REQUESTED"),
    ("SANTA IS", "WATCHING"),
    ("SNOW AT THE", "N. POLE"),
    ("SANTA SAYS", "GOOD JOB"),
]

# Test-flight sightings around the Arctic: (code, name max 12, lat, lon).
# Each test flight picks one, plots it on a polar radar (North Pole in the
# middle, dashed ring = Arctic Circle) and shows the sleigh's speed in Mach.
ARCTIC = [
    ("NPL", "NORTH POLE",   90.0,    0.0),
    ("LYR", "SVALBARD",     78.2,   15.6),
    ("NYA", "NY-ALESUND",   78.9,   11.9),
    ("THU", "THULE",        76.5,  -68.7),
    ("YLT", "ALERT NU",     82.5,  -62.3),
    ("JAV", "ILULISSAT",    69.2,  -51.1),
    ("UMD", "UUMMANNAQ",    70.7,  -52.1),
    ("OBY", "SCORESBYSUND", 70.5,  -22.0),
    ("SCC", "DEADHORSE",    70.2, -148.5),
    ("BRW", "UTQIAGVIK",    71.3, -156.8),
    ("OTZ", "KOTZEBUE",     66.9, -162.6),
    ("YEV", "INUVIK",       68.4, -133.5),
    ("YHK", "GJOA HAVEN",   68.6,  -95.9),
    ("YRB", "RESOLUTE",     74.7,  -94.8),
    ("YGZ", "GRISE FIORD",  76.4,  -82.9),
    ("YIO", "POND INLET",   72.7,  -77.9),
    ("TOS", "TROMSO",       69.7,   18.9),
    ("RVN", "ROVANIEMI",    66.5,   25.7),
    ("KKN", "KIRKENES",     69.7,   30.0),
    ("MMK", "MURMANSK",     69.0,   33.1),
    ("AMV", "AMDERMA",      69.8,   61.6),
    ("DKS", "DIKSON",       73.5,   80.4),
    ("NSK", "NORILSK",      69.3,   88.1),
    ("IKS", "TIKSI",        71.7,  128.9),
    ("PWE", "PEVEK",        69.8,  170.6),
]
TEST_MACH = (0.85, 3.40)       # test-flight speed range
LIVE_MACH = (6.0, 12.0)        # Christmas Eve speed range

# Cheer Meter: rises from CHEER_START% on Nov 1 to 100% on Christmas Eve,
# with a little day-to-day wiggle. 95%+ pegs the needle.
CHEER_START = 35

# ---------------------------------------------------------------------------
# Colors - phosphor terminal palette
# ---------------------------------------------------------------------------
def _c(r, g, b):
    return graphics.Color(r, g, b)

RED = _c(255, 0, 0)
DARK_RED = _c(70, 0, 0)
GOLD = _c(255, 200, 0)
AMBER = _c(255, 140, 0)
GREEN = _c(0, 255, 60)
MID_GREEN = _c(0, 120, 30)
DIM_GREEN = _c(0, 40, 10)
WHITE = _c(230, 230, 230)
GREY = _c(90, 90, 90)
BLACK = _c(0, 0, 0)

SMALL_W, BIG_W = 5, 7
ROW = [7, 15, 23, 31]          # baselines for 4 rows of 5x7 text
CODE_CHARS = "ABCDEFGHJKLMNPQRSTUVWXYZ23456789"

_fonts = {}


FONT_DIR = Path(__file__).resolve().parent.parent / "fonts"


def _font(name):
    if name not in _fonts:
        f = graphics.Font()
        f.LoadFont(str(FONT_DIR / name))
        _fonts[name] = f
    return _fonts[name]


def small():
    return _font("5x7.bdf")


def big():
    return _font("7x13.bdf")


# ---------------------------------------------------------------------------
# Date logic
# ---------------------------------------------------------------------------
def _local(now):
    if now is None:
        return datetime.now(HOME_TZ)
    if now.tzinfo is None:
        return now.replace(tzinfo=HOME_TZ)
    return now.astimezone(HOME_TZ)


def _arrivals(year):
    """[(arrival_in_home_tz, code, name)] - midnight Dec 25 local, sorted."""
    out = []
    for code, name, tz in SIGHTINGS:
        midnight = datetime(year, 12, 25, 0, 0, tzinfo=ZoneInfo(tz))
        out.append((midnight.astimezone(HOME_TZ), code, name))
    out.sort()
    return out


def _home_arrival(year):
    return datetime(year, 12, 25, 0, 0, tzinfo=HOME_TZ)


def _mission_end(year):
    """One hour after the last city on the list reaches midnight."""
    return _arrivals(year)[-1][0] + timedelta(hours=1)


def _launch(year):
    return _arrivals(year)[0][0]


def spotted(now):
    """(code, name) where Santa is spotted right now, or None before liftoff."""
    now = _local(now)
    home = _home_arrival(now.year)
    if home <= now < home + timedelta(minutes=HOME_SPOTLIGHT_MINUTES):
        name = next(n for c, n, _ in SIGHTINGS if c == HOME_CODE)
        return HOME_CODE, name
    passed = [s for s in _arrivals(now.year) if s[0] <= now]
    if not passed:
        return None
    # cities where it turned midnight within the last hour
    fresh = [s for s in passed if (now - s[0]).total_seconds() < 3600]
    if not fresh:                       # gap between time zones: latest one
        latest = passed[-1][0]
        fresh = [s for s in passed if s[0] == latest]
    # shuffle that band once, then step through it so every city gets a turn
    fresh = sorted(fresh, key=lambda s: s[1])
    random.Random(f"band-{fresh[0][0]}-{len(fresh)}").shuffle(fresh)
    slot = int(now.timestamp() // (SIGHTING_MINUTES * 60))
    pick = fresh[slot % len(fresh)]
    return pick[1], pick[2]


def mode(now):
    """'test' Nov 1-Dec 23, 'live' Dec 24 until the last stop, 'rtb' (returning
    to base) until Christmas morning, 'complete' the rest of Dec 25."""
    now = _local(now)
    if now.month == 11 and now.day >= TEST_SEASON_START[1]:
        return "test"
    if now.month != 12 or now.day > 25:
        return None
    if now.day <= 23:
        return "test"
    if now < _mission_end(now.year):
        return "live"
    if now.day == 25 and now.hour < CHRISTMAS_MORNING_HOUR:
        return "rtb"
    return "complete"


def days_until_christmas(now):
    now = _local(now)
    return (date(now.year, 12, 25) - now.date()).days


def santcon(now):
    d = days_until_christmas(now)
    if d >= 30:          # November
        return 5
    if d >= 15:
        return 4
    if d >= 7:
        return 3
    if d >= 2:
        return 2
    return 1


def flight_status(now):
    """(progress 0..1, spotted (code, name) or None, to_home, to_launch)."""
    now = _local(now)
    first = _launch(now.year)
    home = _home_arrival(now.year)
    span = (_mission_end(now.year) - first).total_seconds()
    progress = min(1.0, max(0.0, (now - first).total_seconds() / span))
    return progress, spotted(now), home - now, first - now


def _alert_minutes(now):
    rng = random.Random(f"{now.date()}-{now.hour}")
    return set(rng.sample(range(60), ALERTS_PER_HOUR))


_last_alert_key = None


def should_alert(now=None):
    """True once per scheduled TOY minute (Dec 1-24, daytime)."""
    global _last_alert_key
    now = _local(now)
    if mode(now) not in ("test", "live"):
        return False
    if not (ALERT_FIRST_HOUR <= now.hour <= ALERT_LAST_HOUR):
        return False
    if now.minute not in _alert_minutes(now):
        return False
    key = (now.date(), now.hour, now.minute)
    if key == _last_alert_key:
        return False
    _last_alert_key = key
    return True


def tracker_page_active(now=None):
    """True Dec 24-25: put the radar / mission page in the rotation."""
    return mode(now) in ("live", "rtb", "complete")


# ---------------------------------------------------------------------------
# Drawing helpers
# ---------------------------------------------------------------------------
def _px(canvas, x, y, c):
    if 0 <= x < 64 and 0 <= y < 32:
        canvas.SetPixel(int(x), int(y), c.red, c.green, c.blue)


def _text(canvas, row, color, text, x=1, center=False):
    if center:
        x = max(0, (64 - len(text) * SMALL_W) // 2)
    graphics.DrawText(canvas, small(), x, ROW[row], color, text)


def _big(canvas, y, color, text, x=None):
    if x is None:
        x = max(0, (64 - len(text) * BIG_W) // 2)
    graphics.DrawText(canvas, big(), x, y, color, text)


def _blink(t, rate=0.25):
    return int(t / rate) % 2 == 0


def _type(canvas, row, color, text, t, start, cps=16, center=False):
    """Teletype: reveal text one character at a time, with a block cursor."""
    if t < start:
        return
    n = min(len(text), int((t - start) * cps))
    x0 = max(0, (64 - len(text) * SMALL_W) // 2) if center else 1
    graphics.DrawText(canvas, small(), x0, ROW[row], color, text[:n])
    if n < len(text) and _blink(t, 0.08):
        cx = x0 + n * SMALL_W
        for y in range(ROW[row] - 6, ROW[row] + 1):
            for x in range(cx, cx + 4):
                _px(canvas, x, y, color)


# ---------------------------------------------------------------------------
# TOY scenes - each is (seconds, draw(canvas, t))
# ---------------------------------------------------------------------------
def _scene_flash(canvas, t):
    word = STROBE_WORDS[int(t / 0.72) % len(STROBE_WORDS)]
    if int(t / 0.18) % 2 == 0:
        canvas.Fill(255, 0, 0)
        _big(canvas, 21, BLACK, word)
    else:
        _big(canvas, 21, RED, word)
    for x in range(64):                     # hazard stripes top and bottom
        c = RED if ((x + int(t * 20)) // 4) % 2 == 0 else BLACK
        _px(canvas, x, 0, c); _px(canvas, x, 1, c)
        _px(canvas, x, 30, c); _px(canvas, x, 31, c)


def _scene_header(canvas, t):
    if _blink(t, 0.3):
        _text(canvas, 0, RED, f"*** {ACRONYM} ***", center=True)
    _type(canvas, 1, AMBER, f"FROM: {COMMAND}", t, 0.3)
    _type(canvas, 2, AMBER, f"TO: {KID_NAME}", t, 1.2)
    # priority line: types out "PRI: JOLLY", then flips with "PRI: HOHOHO"
    typed_at = 2.1 + len(PRIORITY[0]) / 16 + 0.3
    if t < typed_at:
        _type(canvas, 3, AMBER, PRIORITY[0], t, 2.1)
    else:
        word = PRIORITY[int((t - typed_at) / 0.6) % len(PRIORITY)]
        _text(canvas, 3, GREEN if word != PRIORITY[0] else AMBER, word)


def _make_auth(code):
    def scene(canvas, t):
        _type(canvas, 0, AMBER, "AUTHENTICATE", t, 0.0, cps=24)
        if t > 0.6:
            _text(canvas, 1, WHITE, f"MSG {code}")
        if t > 1.0:
            graphics.DrawText(canvas, small(), 1, ROW[2], WHITE, "KEY")
            frame = int(t * 18)
            for i, ch in enumerate(code):
                x = 1 + (4 + i) * SMALL_W
                locked = t > 1.3 + i * 0.35
                if ch == "-":
                    shown, col = "-", WHITE
                elif locked:
                    shown, col = ch, GREEN
                else:
                    shown = CODE_CHARS[(frame * 7 + i * 13) % len(CODE_CHARS)]
                    col = GREY
                graphics.DrawText(canvas, small(), x, ROW[2], col, shown)
        done = 1.3 + len(code) * 0.35 + 0.3
        if t > done and _blink(t, 0.2):
            _text(canvas, 3, GREEN, "** VALID **", center=True)
    return scene


def _make_body(live, message, now):
    line1, line2 = (m.format(name=KID_NAME) for m in message)
    def scene(canvas, t):
        _type(canvas, 0, AMBER, "MSG BEGINS", t, 0.0)
        if live:
            _, seen, _, _ = flight_status(now)
            if seen:
                _type(canvas, 1, WHITE, "SANTA IS UP", t, 0.8)
                _type(canvas, 2, GREEN, "DELIVERING", t, 1.6)
            else:
                _type(canvas, 1, WHITE, "SANTA IS UP", t, 0.8)
                _type(canvas, 2, WHITE, "LAUNCH PREP", t, 1.6)
            if t > 2.6 and _blink(t, 0.2):
                _text(canvas, 3, RED, "NOT A DRILL", center=True)
        else:
            _type(canvas, 1, GREEN, line1, t, 0.8)
            _type(canvas, 2, WHITE, line2, t, 1.7)
            if t > 2.7 and _blink(t, 0.5):
                _text(canvas, 3, AMBER, "STAND BY")
    return scene


def _make_santcon(level, days):
    def scene(canvas, t):
        _text(canvas, 0, AMBER, "READINESS", center=True)
        on = t < 0.8 or _blink(t, 0.35)
        if on:
            _big(canvas, 20, RED if level <= 2 else WHITE, f"SANTCON{level}")
        # five readiness blocks - lit from 5 down to the current level
        for i in range(5):
            lvl = 5 - i
            x0 = 2 + i * 12
            lit = lvl >= level and t > 0.3 + i * 0.15
            col = (RED if lvl == level else DARK_RED) if lit else DIM_GREEN
            for x in range(x0, x0 + 10):
                _px(canvas, x, 22, col); _px(canvas, x, 23, col)
        label = "T-1 DAY" if days == 1 else f"T-{days} DAYS"
        if days <= 0:
            label = "T-0 TONIGHT"
        _text(canvas, 3, AMBER, label, center=True)
    return scene


def _scene_bedtime(canvas, t):
    _type(canvas, 0, AMBER, f"ORDERS FOR", t, 0.0)
    _type(canvas, 1, AMBER, f"{KID_NAME}:", t, 0.6)
    _type(canvas, 2, GREEN, "BED EARLY", t, 1.2)
    if t > 2.0 and _blink(t, 0.3):
        _text(canvas, 3, WHITE, "COOKIES OUT")


def _coord(lat, lon):
    return f"{lat:.1f}N {abs(lon):.1f}{'E' if lon >= 0 else 'W'}"


def _mach_now(base, t):
    """Base speed with a little live wobble, two decimals."""
    return base + 0.03 * math.sin(t * 3.1) + 0.015 * math.sin(t * 7.7)


ARCTIC_CIRCLE = 66.56
POLAR_EDGE = 60.0               # latitude at the scope's outer ring


def _polar_xy(lat, lon):
    r = R * (90 - lat) / (90 - POLAR_EDGE)
    a = math.radians(lon)
    return CX + r * math.sin(a), CY + r * math.cos(a)   # Greenwich points down


def _make_arctic_scope(spot, mach):
    code, name, lat, lon = spot
    def scene(canvas, t):
        # outer ring (60N), dashed Arctic Circle, crosshair, North Pole
        for deg in range(0, 360, 4):
            a = math.radians(deg)
            _px(canvas, CX + R * math.cos(a), CY + R * math.sin(a), MID_GREEN)
        ra = R * (90 - ARCTIC_CIRCLE) / (90 - POLAR_EDGE)
        for deg in range(0, 360, 8):
            a = math.radians(deg)
            _px(canvas, CX + ra * math.cos(a), CY + ra * math.sin(a), _c(0, 70, 120))
        for d in range(-R + 1, R):
            if d % 2 == 0:
                _px(canvas, CX + d, CY, DIM_GREEN); _px(canvas, CX, CY + d, DIM_GREEN)
        sweep = (t / SWEEP_SECONDS) * 2 * math.pi
        for k, col in ((0.0, GREEN), (0.12, MID_GREEN), (0.24, DIM_GREEN)):
            a = sweep - k
            for r in range(1, R):
                _px(canvas, CX + r * math.cos(a), CY + r * math.sin(a), col)
        _px(canvas, CX, CY, WHITE)
        bx, by = _polar_xy(lat, lon)
        bang = math.atan2(by - CY, bx - CX)
        since = (sweep - bang) % (2 * math.pi)
        glow = max(0.3, 1 - since / (2 * math.pi))
        if code in STAR_CODES:
            draw_star(canvas, bx, by, t)             # Star of Bethlehem
        else:
            col = _c(int(255 * glow), int(30 * glow), 0)
            for dx, dy in ((0, 0), (1, 0), (0, 1), (1, 1)):
                _px(canvas, bx + dx, by + dy, col)
        x = 33
        graphics.DrawText(canvas, small(), x, ROW[0], AMBER, "SLEIGH")
        _big(canvas, 20, WHITE, code, x)
        graphics.DrawText(canvas, small(), x, ROW[3], GREEN, f"M{_mach_now(mach, t):.2f}")
    return scene


# Places that get the twinkling gold star instead of the red blip
STAR_CODES = {"BETH"}

STAR_BIG = [            # 4-point star with a long tail, centered on (3, 3)
    "...#...",
    "...#...",
    "..###..",
    "#######",
    "..###..",
    "...#...",
    "...#...",
    "...#...",
    "...#...",
]
STAR_SMALL = [
    ".#.",
    "###",
    ".#.",
]


def draw_star(canvas, x, y, t, small=False):
    """Twinkling gold star centered at (x, y): pulses between big and small."""
    pulse = 0.5 + 0.5 * math.sin(t * 6)
    shape = STAR_SMALL if small or pulse < 0.35 else STAR_BIG
    cx = len(shape[0]) // 2
    cy = 1 if shape is STAR_SMALL else 3
    for j, row in enumerate(shape):
        for i, ch in enumerate(row):
            if ch != "#":
                continue
            core = (i == cx and j == cy)
            level = 1.0 if (core or small) else 0.55 + 0.45 * pulse
            col = _c(255, int(215 * level), int(60 * level) if core else 0)
            _px(canvas, x + i - cx, y + j - cy, col)
    if not small and pulse > 0.8:                     # sparkle glints
        for dx, dy in ((-2, -2), (2, -2), (-2, 2), (2, 2)):
            _px(canvas, x + dx, y + dy, _c(255, 240, 150))


def _make_telemetry(spot, mach, live=False):
    code, name, lat, lon = spot
    def scene(canvas, t):
        _type(canvas, 0, AMBER, "SPOTTED OVER" if live else "TEST FLIGHT", t, 0.0, cps=24)
        _type(canvas, 1, WHITE, name, t, 0.5)
        if code in STAR_CODES and t > 0.5 + len(name) / 16:
            draw_star(canvas, 1 + len(name) * SMALL_W + 5, ROW[1] - 4, t, small=True)
        if t > 1.2:
            _text(canvas, 2, GREEN, f"MACH {_mach_now(mach, t):.2f}")
        if t > 1.8:
            _text(canvas, 3, GREY, _coord(lat, lon) if lat is not None else code)
    return scene


def cheer_level(now):
    now = _local(now)
    if mode(now) in ("live", "rtb", "complete"):
        return 100
    start = date(now.year, *TEST_SEASON_START)
    total = (date(now.year, 12, 24) - start).days
    done = (now.date() - start).days
    base = CHEER_START + (100 - CHEER_START) * max(0, min(1, done / total))
    wiggle = random.Random(f"cheer-{now.date()}").uniform(-6, 6)
    return int(max(5, min(100, base + wiggle)))


def _cheer_word(level):
    if level >= 95:
        return "MAX CHEER!"
    if level >= 80:
        return "VERY JOLLY"
    if level >= 60:
        return "JOLLY"
    if level >= 40:
        return "RISING"
    return "NEEDS CHEER"


GX, GY, GR = 21, 30, 19         # gauge hub and radius (left side)


BREAK_AT = 2.2                  # Christmas Eve: seconds before the gauge breaks


def _make_cheer(level, broken=False):
    if broken:
        return _make_broken_cheer()

    def scene(canvas, t):
        # title, then the cheer word
        if t < 1.8:
            _type(canvas, 0, AMBER, "CHEER METER", t, 0.0, cps=20, center=True)
        elif level < 95 or _blink(t, 0.25):
            _text(canvas, 0, GREEN if level >= 60 else AMBER, _cheer_word(level), center=True)
        # colored dial: red (low) -> amber -> green (high)
        for i in range(0, 181, 5):
            frac = i / 180
            col = RED if frac < 0.33 else AMBER if frac < 0.66 else GREEN
            a = math.radians(180 - i)
            _px(canvas, GX + GR * math.cos(a), GY - GR * math.sin(a), col)
            if i % 30 == 0:                          # tick marks
                _px(canvas, GX + (GR - 2) * math.cos(a), GY - (GR - 2) * math.sin(a), col)
        # needle: sweeps up, overshoots, settles with a cheerful wobble
        target = level / 100
        if t < 1.2:
            frac = target * (t / 1.2) * 1.08
        elif t < 1.6:
            frac = target * (1.08 - 0.08 * (t - 1.2) / 0.4)
        else:
            frac = target + 0.015 * math.sin(t * 9)
        if level >= 95 and t > 1.6:                  # pegged - rattles at max
            frac = 1.0 - abs(0.02 * math.sin(t * 25))
        frac = max(0.0, min(1.0, frac))
        a = math.radians(180 - 180 * frac)
        for r in range(0, GR - 3):
            _px(canvas, GX + r * math.cos(a), GY - r * math.sin(a), WHITE)
        for dx in (-1, 0, 1):
            for dy in (-1, 0):
                _px(canvas, GX + dx, GY + dy, RED)
        # big reading on the right
        shown = int(round(100 * frac)) if t < 1.6 else level
        txt = "MAX" if shown >= 100 else f"{shown}%"
        col = GREEN if shown >= 66 else AMBER if shown >= 33 else RED
        if not (level >= 95 and t > 1.6 and not _blink(t, 0.25)):
            _big(canvas, 26, col, txt, 64 - len(txt) * BIG_W)
    return scene


def _make_broken_cheer():
    """Christmas Eve: the needle pegs at MAX, the gauge snaps, the needle
    spins wildly and pieces of the dial fall off."""
    # pick which dial dots fall off, and how fast
    pieces = []
    prng = random.Random(1225)
    for i in range(0, 181, 5):
        frac = i / 180
        col = RED if frac < 0.33 else AMBER if frac < 0.66 else GREEN
        a = math.radians(180 - i)
        x, y = GX + GR * math.cos(a), GY - GR * math.sin(a)
        falls = prng.random() < 0.45
        pieces.append((x, y, col, falls, prng.uniform(18, 45), prng.uniform(-6, 6)))

    def scene(canvas, t):
        f = int(t * 30)                      # frame number for randomness
        rng = random.Random(f)
        after = t - BREAK_AT

        # the SNAP: two quick full-screen flashes
        if 0 <= after < 0.25:
            if f % 2 == 0:
                canvas.Fill(255, 255, 255)
            _big(canvas, 21, RED, "SNAP!")
            return

        # dial - intact before the break, crumbling after
        for x, y, col, falls, g, drift in pieces:
            if after > 0 and falls:
                dt = after - 0.25
                x, y = x + drift * dt, y + 0.5 * g * dt * dt
            if after > 0 and rng.random() < 0.15:
                col = rng.choice((RED, AMBER, GREEN, WHITE))
            _px(canvas, x, y, col)

        # needle
        if after < 0:
            if t < 1.2:
                ang = math.pi - math.pi * min(1.0, t / 1.2 * 1.05)
            else:                             # pegged and rattling
                ang = 0.04 * abs(math.sin(t * 30))
            for r in range(0, GR - 3):
                _px(canvas, GX + r * math.cos(ang), GY - r * math.sin(ang), WHITE)
        else:
            # snapped off the hub - spins like a propeller, bouncing around
            spin = after * (14 + 10 * math.sin(after * 1.7)) + 0.5 * math.sin(after * 23)
            nx = GX + 7 * math.sin(after * 2.3)
            ny = 16 + 5 * math.sin(after * 3.1)
            for r in range(-8, 9):
                _px(canvas, nx + r * math.cos(spin), ny - r * math.sin(spin), WHITE)
        for dx in (-1, 0, 1):
            for dy in (-1, 0):
                _px(canvas, GX + dx, GY + dy, RED)

        # sparks flying off the hub
        if after > 0:
            for _ in range(6):
                a = rng.uniform(0, 2 * math.pi)
                r = rng.uniform(2, 16)
                _px(canvas, GX + r * math.cos(a), GY - abs(r * math.sin(a)),
                    rng.choice((GOLD, WHITE, AMBER)))

        # text
        if after < 0:
            if t > 1.2 and _blink(t, 0.15):
                _text(canvas, 0, GREEN, "MAX CHEER!", center=True)
            if t < 1.2:
                pct = f"{min(99, int(100 * t / 1.2 * 1.05))}%"
                _big(canvas, 26, GREEN if t > 0.8 else AMBER, pct, 64 - len(pct) * BIG_W)
            elif _blink(t, 0.15):
                _big(canvas, 26, GREEN, "MAX", 64 - 3 * BIG_W)
        else:
            top = "OVERLOAD!" if int(after / 0.5) % 2 == 0 else "TOO JOLLY!"
            _text(canvas, 0, RED if top == "OVERLOAD!" else GREEN, top, center=True)
            junk = rng.choice(["999%", "???", "ERR", "1E6", "MAX", "!!!", "OVR"])
            junk = junk if len(junk) <= 3 else junk
            _big(canvas, 26, rng.choice((RED, GOLD, GREEN)), junk[:3], 64 - 3 * BIG_W)
    return scene


def _scene_end(canvas, t):
    _type(canvas, 1, AMBER, "END OF MSG", t, 0.0, center=True)
    _type(canvas, 2, GREY, f"{COMMAND} OUT", t, 0.9, center=True)


def _make_radar(now_fn):
    def scene(canvas, t):
        draw_radar(canvas, now_fn(), t)
    return scene


def eam_scenes(now):
    now = _local(now)
    live = mode(now) == "live"
    rng = random.Random()
    code = "".join(rng.choice(CODE_CHARS) for _ in range(3)) + "-25"
    scenes = [
        (2.2, _scene_flash),
        (5.0, _scene_header),
        (4.5, _make_auth(code)),
    ]
    if live:
        seen = spotted(now)
        if seen:
            mach = round(rng.uniform(*LIVE_MACH), 2)
            scenes.append((4.0, _make_telemetry((seen[0], seen[1], None, None), mach, live=True)))
    else:
        spot = rng.choice(ARCTIC)
        mach = round(rng.uniform(*TEST_MACH), 2)
        scenes += [(4.5, _make_arctic_scope(spot, mach)), (4.0, _make_telemetry(spot, mach))]
    scenes += [
        (4.2, _make_body(live, rng.choice(MESSAGES), now)),
        (7.0 if live else 4.0, _make_cheer(cheer_level(now), broken=live)),
        (3.5, _make_santcon(santcon(now), days_until_christmas(now))),
    ]
    if live:
        scenes.append((6.0, _make_radar(lambda: now)))
        scenes.append((3.5, _scene_bedtime))
    scenes.append((2.4, _scene_end))
    return scenes


# ---------------------------------------------------------------------------
# Radar scope (Dec 24) and Christmas pages
# ---------------------------------------------------------------------------
CX, CY, R = 15, 15, 14          # scope center and radius (left half)
SWEEP_SECONDS = 2.4


def _hm(delta):
    mins = max(0, int(delta.total_seconds() // 60))
    return f"{mins // 60}:{mins % 60:02d}"


def draw_radar(canvas, now, t):
    now = _local(now)
    m = mode(now)

    # scope rings and crosshair
    for deg in range(0, 360, 4):
        a = math.radians(deg)
        _px(canvas, CX + R * math.cos(a), CY + R * math.sin(a), MID_GREEN)
        if deg % 12 == 0:
            _px(canvas, CX + 7 * math.cos(a), CY + 7 * math.sin(a), DIM_GREEN)
    for d in range(-R + 1, R):
        if d % 2 == 0:
            _px(canvas, CX + d, CY, DIM_GREEN)
            _px(canvas, CX, CY + d, DIM_GREEN)

    # sweep arm with a fading trail
    sweep = (t / SWEEP_SECONDS) * 2 * math.pi
    for k, col in ((0.0, GREEN), (0.12, MID_GREEN), (0.24, DIM_GREEN), (0.36, DIM_GREEN)):
        a = sweep - k
        for r in range(1, R):
            _px(canvas, CX + r * math.cos(a), CY + r * math.sin(a), col)

    _px(canvas, CX, CY, WHITE)       # center of the scope

    if m == "live":
        progress, seen, to_home, to_launch = flight_status(now)
        code = seen[0] if seen else None
    else:
        progress, code, to_home, to_launch = 1.0, "RTB", None, None

    # Sleigh 1 blip: spirals in toward the center as the night goes on.
    if code:
        ang = progress * 4 * math.pi - math.pi / 2
        rad = 1 + (R - 3) * (1 - progress)
        bx, by = CX + rad * math.cos(ang), CY + rad * math.sin(ang)
        since = (sweep - ang) % (2 * math.pi)        # glows after the sweep passes
        glow = max(0.25, 1 - since / (2 * math.pi))
        if m != "live":
            glow = 1.0 if _blink(t, 0.25) else 0.3
        if code in STAR_CODES:
            draw_star(canvas, bx, by, t)             # Star of Bethlehem
        else:
            col = _c(int(255 * glow), int(30 * glow), 0)
            for dx, dy in ((0, 0), (1, 0), (0, 1), (1, 1)):
                _px(canvas, bx + dx, by + dy, col)

    # readout on the right
    x = 33
    if m == "live" and code is None:
        graphics.DrawText(canvas, small(), x, ROW[0], AMBER, "SLEIGH")
        _big(canvas, 20, WHITE, "PRE", x)
        graphics.DrawText(canvas, small(), x, ROW[3], AMBER, "L-" + _hm(to_launch))
        return
    if m != "live":                                  # done - returning to base
        graphics.DrawText(canvas, small(), x, ROW[0], AMBER, "SLEIGH")
        if _blink(t, 0.4):
            _big(canvas, 20, WHITE, "RTB", x)
        graphics.DrawText(canvas, small(), x, ROW[3], GREEN, "N POLE")
        return
    at_home = code == HOME_CODE
    graphics.DrawText(canvas, small(), x, ROW[0], AMBER, "TRACK")
    if not at_home or _blink(t, 0.3):
        _big(canvas, 20, WHITE, code, x)
    if at_home:
        graphics.DrawText(canvas, small(), x, ROW[3], RED if _blink(t, 0.25) else GREEN, "HOME!")
    elif to_home.total_seconds() > 0:                # still on the way to Seattle
        hm = _hm(to_home)
        txt = ("T-" + hm) if len(hm) <= 4 else hm
        graphics.DrawText(canvas, small(), x, ROW[3], GREEN, txt)
    else:                                            # Seattle done, heading west
        graphics.DrawText(canvas, small(), x, ROW[3], GREEN, "SEA OK")


def draw_complete(canvas, t):
    cycle = t % 8
    if cycle < 4:
        _type(canvas, 0, AMBER, f"{ACRONYM} 12-25", cycle, 0.0)
        _type(canvas, 1, GREEN, "MISSION", cycle, 0.7)
        _type(canvas, 2, GREEN, "COMPLETE", cycle, 1.3)
        if cycle > 2.2 and _blink(t, 0.4):
            _text(canvas, 3, WHITE, "GIFTS: DONE")
    else:
        c = cycle - 4
        _big(canvas, 13, RED, "MERRY")
        _text(canvas, 2, GREEN, "CHRISTMAS", center=True)
        if _blink(t, 0.4):
            _text(canvas, 3, WHITE, f"{KID_NAME}!", center=True)
        for x in range(64):
            col = RED if ((x + int(c * 15)) // 3) % 2 == 0 else WHITE
            _px(canvas, x, 0, col)


# ---------------------------------------------------------------------------
# Run loops - these own the screen, then hand the canvas back
# ---------------------------------------------------------------------------
def run_scenes(matrix, canvas, scenes, fps=25):
    for seconds, draw in scenes:
        start = time.time()
        while (t := time.time() - start) < seconds:
            canvas.Clear()
            draw(canvas, t)
            canvas = matrix.SwapOnVSync(canvas)
            time.sleep(1 / fps)
    return canvas


def run_alert(matrix, canvas, now=None):
    """Full TOY sequence (~20-26 seconds)."""
    return run_scenes(matrix, canvas, eam_scenes(now))


def draw_page(canvas, now, t):
    """One frame of the Santa page in the clock rotation (Dec 24-25):
    radar, or MISSION COMPLETE on Christmas morning."""
    n = _local(now)
    if mode(n) == "complete":
        draw_complete(canvas, t)
    else:
        draw_radar(canvas, n, t)


def scene_at(scenes, t):
    """For a list of (seconds, draw) scenes: the draw function and its local
    time at t seconds in, or (None, None) once the sequence is over."""
    for seconds, draw in scenes:
        if t < seconds:
            return draw, t
        t -= seconds
    return None, None


def run_tracker(matrix, canvas, now=None, seconds=RADAR_SECONDS):
    """Radar page on Dec 24 / midnight; MISSION COMPLETE on Christmas morning."""
    fixed = now
    def draw(c, t):
        n = _local(fixed)
        if mode(n) == "complete":
            draw_complete(c, t)
        else:
            draw_radar(c, n, t)
    return run_scenes(matrix, canvas, [(seconds, draw)])


# Load both fonts right now, at import, while the program can still read them.
small()
big()
