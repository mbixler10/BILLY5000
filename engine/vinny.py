"""
vinny.py - Agent Vinny's ELFNET traffic.

THE STORY: ELFNET is Santa's worldwide classified network. Vinny, Billy's
Elf on the Shelf, is one of its field agents, posted at Billy's house. That's
why this board picks up ELFNET at all: now and then it intercepts Vinny's
encrypted reports to the North Pole, and Santa's replies. Santa's TOY alerts
and radar are the network in full operation; Vinny is the agent on the ground.

Vinny is Billy's little secret-agent buddy, looking out for him. Reports are
warm, funny or innocently bureaucratic - never "behave, he's watching you".

A DAY ON STATION (from the day he arrives through Christmas Eve):
    ~7:30 am   FIELD REPORT    he moved overnight: new post, cover intact
    late morn  SITREP or INTEL
    early aft  SITREP, INTEL or a REPLY FROM SANTA
    late aft   SITREP or INTEL
    ~6:45 pm   MOVEMENT ORDERS relocate before dawn, new post classified
    + 1 or 2   INTERCEPTS      signal detected... static... fragments... lost
All at slightly different times each day, never next to a TOY alert.

The week before he arrives: one intercept a day hinting at a deployment, and
orders the night before. Arrival day: DEPLOYED. Christmas Eve: final report
and exfil with Santa. Christmas morning: Santa signs off. Then quiet.

Preview:   python main.py --demo-vinny            (a random transmission now)
           python main.py --demo-vinny intercept  (sitrep, intel, santa, orders,
                                                   post, intercept, arrival, eve, xmas)
           python -m engine.vinny 2026-12-10      (that day's schedule + messages)
"""
import math
import random
from datetime import date, datetime, timedelta

import settings
from engine import santa
from engine.santa import (_local, _px, _c, _text, _big, _type, _blink, graphics, small,
                          ROW, SMALL_W, mode, RED, DARK_RED, GOLD, AMBER, GREEN, DIM_GREEN,
                          WHITE, GREY, BLACK)

# --------------------------------------------------------------------------
# Settings
# --------------------------------------------------------------------------
VINNY_ON = True
AGENT = "VINNY"
KID = "BILLY"
ARRIVES = (11, 27)              # (month, day) Vinny's first morning at the house
TEASER_DAYS = 7                 # intercepts hinting he's coming, this many days before
TOY_GAP_MINUTES = 3             # never this close to a Santa TOY alert
SLOTS = [                       # (hour, minute, +/- minutes of wiggle, kind)
    (7, 30, 20, "post"),
    (10, 30, 30, "day"),
    (13, 30, 30, "day_or_santa"),
    (16, 0, 30, "day"),
    (18, 45, 15, "orders"),
]
INTERCEPTS_PER_DAY = (1, 2)     # random intercepts between 8 am and 7 pm

LIGHT_GREEN = _c(120, 255, 140)
SCREEN_HOLD = 1.6               # seconds a screen stays after it's typed

# --------------------------------------------------------------------------
# The words. Every line is 12 characters or less (the panel's width).
# --------------------------------------------------------------------------
NEW_POST = [                  # morning field reports - one per day, no repeats all season
    ["NEW OBS POST", "ESTABLISHED.", "COVER INTACT"],
    ["AGENT HAS", "RELOCATED.", "ALL QUIET."],
    ["POSITION", "CHANGED", "OVERNIGHT."],
    ["NEW POST:", "SECURE.", "VIEW: GOOD."],
    ["MOVED AT", "0300 HRS.", "NOBODY SAW."],
    ["RELOCATED.", "DO NOT", "COMPROMISE", "HIS COVER."],
    ["ON STATION.", "SUBJECT", "LOCATED.", "ALL QUIET."],
    ["NEW POST", "SECURED.", "LOOK. NO", "TOUCHING."],
    ["SNUCK PAST", "SCULLY AT", "0200. NICE."],
    ["NEW SPOT.", "BEST YET.", "CONFIRMED."],
    ["MOVED IN", "THE DARK.", "TIPTOE MODE."],
    ["POST CHANGED", "COVER: GOOD.", "MAGIC: GOOD."],
    ["RELOCATION", "COMPLETE.", "NO WITNESSES"],
    ["NEW POST.", "SEARCH TEAM", "BILLY: GO!"],
    ["OVERNIGHT", "MOVE: CLEAN.", "ALL QUIET."],
    ["FOUND A", "SNEAKY SPOT.", "HEE HEE."],
    ["MOVED.", "SCULLY", "SNORED THE", "WHOLE TIME."],
    ["NEW VIEW.", "VERY COZY.", "STAYING PUT."],
    ["FLEW TO THE", "N. POLE AND", "BACK. NEW", "POST SET."],
    ["REPORTED IN", "AT 0100.", "NEW POST", "SECURED."],
    ["GOT LOST", "FOR A SEC.", "FOUND A GOOD", "SPOT. OK!"],
    ["NEW POST:", "EXCELLENT.", "COVER: SOLID"],
    ["MOVED BEFORE", "SUNRISE.", "HOUSE: QUIET"],
    ["TRICKY SPOT", "TODAY. GOOD", "LUCK, BILLY!"],
    ["NEW POST.", "TOP SECRET.", "SHHH."],
    ["RELOCATED.", "CREAKY STEP.", "NOBODY WOKE."],
    ["AGENT MOVED.", "MAGIC CHECK:", "PASSED."],
    ["NEW POST.", "BILLY: FIND", "ME IF YOU", "CAN!"],
    ["POSITION", "UPDATED.", "ALL CLEAR."],
    ["SWITCHED", "SPOTS AGAIN.", "CLASSIC."],
]
SITREP_FIELDS = {
    "BILLY": ["GREEN", "HAPPY", "BUSY", "GIGGLY", "AWESOME", "ON THE MOVE"],
    "HOUSE": ["SECURE", "COZY", "LOUD", "WARM", "TOY-COVERED"],
    "SPIRIT": ["HIGH", "V. HIGH", "MAX", "RISING"],
    "SCULLY": ["ASLEEP", "ON PATROL", "SNACKING", "GOOD BOY", "SNORING"],
    "COOKIES": ["STABLE", "LOW", "MISSING 2", "NOT YET"],
    "MAGIC": ["100%", "99%", "STRONG"],
    "LIGHTS": ["ONLINE", "TWINKLING", "ALL ON"],
}
INTEL_FIELDS = [
    ("TREE LIGHTS:", ["ONLINE", "TWINKLING"]), ("STOCKINGS:", ["CONFIRMED", "HUNG", "EMPTY..."]),
    ("COOKIES:", ["NOT YET", "BAKING", "CONFIRMED"]), ("SNOW:", ["NEGATIVE", "RAIN INSTEAD"]),
    ("PLANES:", ["MANY", "OVERHEAD"]), ("BATH TIME:", ["SPLASHY", "COMPLETE"]),
    ("BEDTIME:", ["NEGOTIATED", "ON TIME"]), ("NAP:", ["SUCCESSFUL", "REFUSED"]),
    ("HUGS:", ["PLENTY", "MANY"]), ("SCULLY:", ["NAPPING", "WAGGING"]),
    ("BOOKS READ:", ["SEVERAL", "SAME ONE x5"]), ("DAD JOKES:", ["DETECTED", "TOO MANY"]),
    ("DANCE PARTY:", ["CONFIRMED", "IN PROGRESS"]), ("TOYS:", ["EVERYWHERE", "PUT AWAY?"]),
    ("VEGGIES:", ["EATEN. WOW", "HIDDEN"]), ("SHARING:", ["OBSERVED", "EXCELLENT"]),
    ("SNOWMEN:", ["ZERO", "RAINED OUT"]), ("HOT COCOA:", ["DETECTED", "ALL GONE"]),
    ("WRAPPING:", ["SUSPICIOUS", "IN PROGRESS"]), ("TAPE:", ["MISSING", "EVERYWHERE"]),
    ("DOORBELL:", ["PACKAGES!", "3 BOXES"]), ("BOXES:", ["HIDDEN", "CLASSIFIED"]),
    ("SINGING:", ["DETECTED", "LOUD. GOOD."]), ("GIGGLES:", ["MANY", "OFF CHARTS"]),
    ("SOCKS:", ["MISSING 1", "SCULLY HAS"]), ("RAIN:", ["CONFIRMED", "OF COURSE"]),
    ("PUDDLES:", ["JUMPED IN", "SPLASHED"]), ("BOOTS:", ["MUDDY", "BY THE DOOR"]),
    ("STROLLER:", ["DEPLOYED", "PARKED"]), ("PARK TRIP:", ["SUCCESS", "SLIDE: YES"]),
    ("BALL GAME:", ["STRONG", "INTENSE"]), ("TOWER:", ["BUILT", "KNOCKED DOWN"]),
    ("BUBBLES:", ["MANY", "POPPED"]), ("BLANKET:", ["FORT BUILT", "COZY"]),
    ("PIZZA:", ["DETECTED", "ALL GONE"]), ("DAD:", ["SINGING", "DANCING"]),
    ("MOM:", ["IN CHARGE", "AWESOME"]), ("CANDY CANES:", ["COUNTED", "1 MISSING"]),
    ("ORNAMENTS:", ["SPARKLY", "ALL OK"]), ("WREATH:", ["ON DOOR", "FESTIVE"]),
    ("CARDS:", ["ARRIVING", "ON FRIDGE"]), ("FLIGHTS:", ["LOUD", "ON TIME"]),
    ("BOAT RIDES:", ["NONE. RAIN", "MAYBE SOON"]), ("WAVES:", ["AT PLANES", "AT MAILMAN"]),
    ("HIGH FIVES:", ["3", "MANY"]), ("TEETH:", ["BRUSHED", "SPARKLY"]),
]
INTEL_CLOSERS = ["WILL ADVISE.", "MORE LATER.", "STANDING BY.", "AGENT OUT."]
SANTA_REPLIES = [            # two lines each; Santa signs every one
    ["REPORT RCVD.", "KEEP LOOKING"], ["GOOD WORK,", "VINNY."], ["TELL BILLY", "I SAID HI."],
    ["COOKIE INTEL", "NOTED. YUM."], ["MRS. CLAUS", "SAYS HI."], ["REINDEER IN", "TRAINING."],
    ["NICE LIST", "UPDATED."], ["WORKSHOP ON", "SCHEDULE."], ["HO HO HO.", "CARRY ON."],
    ["SCULLY IS A", "GOOD BOY."], ["RUDOLPH SAYS", "HELLO."], ["ELVES ARE", "BUSY. VERY."],
    ["SLEIGH GOT", "NEW PAINT."], ["BILLY: STILL", "AWESOME."], ["GREAT INTEL.", "SANTA HAPPY."],
    ["MORE COOKIE", "DATA PLEASE"], ["SNOWING HERE", "AGAIN. BRR."], ["YOUR REPORTS", "ARE THE BEST"],
    ["DASHER SAYS", "HI TO SCULLY"], ["TOY COUNT:", "ON TRACK."], ["KEEP UP THE", "GOOD WORK."],
    ["NORTH POLE:", "-40. COZY."], ["GIGGLE LEVEL", "NOTED. GOOD."], ["MRS. CLAUS", "BAKED. YUM."],
    ["ELF CHOIR", "PRACTICING."], ["I READ EVERY", "REPORT."], ["BIG SMILE", "HERE. HO HO."],
    ["SLEIGH BELLS", "FIXED."], ["CHECKED THE", "LIST TWICE."], ["HUGS FOR", "BILLY."],
]
ORDERS = [                    # evening orders from Santa - one per night, no repeats
    ["RELOCATE", "BEFORE DAWN.", "NEW POST:", "CLASSIFIED"],
    ["MOVE AFTER", "LIGHTS OUT.", "STAY HIDDEN."],
    ["NEW POST", "TONIGHT.", "PICK A GOOD", "ONE."],
    ["RELOCATE", "AT 0300.", "MIND SCULLY."],
    ["REPORT TO", "N. POLE AT", "0100. THEN", "MOVE."],
    ["TONIGHT:", "FLY HOME,", "REPORT, FLY", "BACK."],
    ["NEW SPOT", "TONIGHT.", "MAKE IT A", "FUN ONE."],
    ["STAY QUIET.", "MOVE AFTER", "BILLY SLEEPS"],
    ["RELOCATE.", "BRING BACK", "GOOD NEWS."],
    ["TONIGHT:", "CHECK THE", "COOKIE JAR."],
    ["MOVE", "TONIGHT. NO", "PEEKING!"],
    ["NEW POST", "BY 0600.", "OVER & OUT."],
    ["RELOCATE.", "AVOID THE", "SQUEAKY STEP"],
    ["TONIGHT:", "TIPTOE MODE.", "ENGAGED."],
    ["FIND A SPOT", "BILLY WILL", "LOVE."],
    ["MOVE AFTER", "STORY TIME."],
    ["REPORT IN", "AT MIDNIGHT.", "THEN HIDE."],
    ["RELOCATE.", "BRING YOUR", "BEST MOVES."],
    ["NEW POST", "TONIGHT.", "SURPRISE ME."],
    ["BEDTIME", "SOON. THEN", "YOU MOVE."],
    ["TONIGHT:", "MAGIC CHECK.", "THEN MOVE."],
    ["GOOD DAY.", "REST, THEN", "RELOCATE."],
    ["MOVE AFTER", "LIGHTS OUT.", "BE SNEAKY."],
    ["TONIGHT:", "A TRICKY ONE", "HEE HEE."],
    ["RELOCATE", "BEFORE THE", "SUN RISES."],
    ["NEW POST.", "KEEP IT", "SECRET."],
    ["STAND BY", "FOR NIGHT", "MOVE."],
    ["TONIGHT:", "SNEAK PAST", "SCULLY AGAIN"],
    ["RELOCATE.", "MRS. CLAUS:", "BE CAREFUL!"],
    ["MOVE AT", "0300. ZZZ.", "(NOT YOU.)"],
]
INCIDENTS = [                 # rare, and always kind
    ["MINOR", "INCIDENT.", "SUBJECT", "RECOVERED", "WELL."],
    ["SMALL", "MELTDOWN.", "FULLY", "RECOVERED."],
]
INTERCEPT_FRAGMENTS = ["...VINNY...", "...BILLY...", "..N. POLE...", "NICE LIST...",
                       "...COOKIES..", "...SLEIGH...", "...SEATTLE..", "...REINDEER.",
                       "...TONIGHT..", "...SCULLY...", "...SANTA...", "...STAR..."]
TEASER_FRAGMENTS = ["...AGENT...", "...DEPLOY...", "...SEATTLE..", "...SOON...",
                    "...BILLY...", "..N. POLE...", "...VINNY..."]


def _wx_line():
    """Real Seattle weather for the sitrep, if the board has it."""
    try:
        from engine import seattle_weather
        w = seattle_weather.get()
        if not w:
            return None
        code = w["code"]
        word = ("CLEAR" if code <= 1 else "CLOUDY" if code <= 3 else "FOG" if code in (45, 48)
                else "SNOW" if 71 <= code <= 77 or code in (85, 86) else "RAIN")
        return f"WX: {word} {round(w['temp'])}F"[:12]
    except Exception:
        return None


# --------------------------------------------------------------------------
# Drawing
# --------------------------------------------------------------------------
def _static(canvas, t, amount=0.25, rng_seed=None):
    rng = random.Random(int(t * 30) if rng_seed is None else rng_seed)
    for _ in range(int(2048 * amount)):
        v = rng.randint(30, 110)
        _px(canvas, rng.randrange(64), rng.randrange(32), _c(0, v, v // 3))


def _scene_signal(canvas, t):
    """Every Vinny transmission arrives like this: a burst of static."""
    _static(canvas, t, 0.18 if t < 0.9 else 0.05)
    if t > 0.3 and _blink(t, 0.2):
        _text(canvas, 1, GREEN, "SIGNAL", center=True)
        _text(canvas, 2, GREEN, "DETECTED...", center=True)


def _screen_seconds(lines):
    return 0.4 + sum(len(l) for l in lines) / 16 + 0.3 * len(lines) + SCREEN_HOLD


def _make_screen(lines, header=None, body=WHITE):
    """Up to 4 typed lines. header=True: first line blinks green like TOY's."""
    starts, at = [], 0.2
    for l in lines:
        starts.append(at)
        at += len(l) / 16 + 0.3
    def scene(canvas, t):
        for i, (l, s) in enumerate(zip(lines[:4], starts)):
            if i == 0 and header:
                if t > s and _blink(t, 0.3):
                    _text(canvas, 0, GREEN, l)
                continue
            _type(canvas, i, AMBER if header else body, l, t, s)
    return scene


def _screens(*pages, header_first=True):
    out = []
    for i, lines in enumerate(pages):
        lines = [l[:12] for l in lines if l][:4]
        out.append((_screen_seconds(lines), _make_screen(lines, header=(i == 0 and header_first))))
    return out


def _scene_end(canvas, t):
    _type(canvas, 1, AMBER, "END TRAFFIC", t, 0.0, center=True)
    _type(canvas, 2, GREY, "ELFNET OUT", t, 0.8, center=True)


# --- big Vinny, drawn from his photo (used on his agent card) --------------
ELF_ART = [                   # 14 x 28: Vinny on a ship's yard, like his photo
    "..........R...",
    ".........RR...",
    "........RRR...",
    ".......RRRR...",
    "......RRRRR...",
    ".....RRRRRR...",
    "....RRRRRRR...",
    "...WWWWWWWWW..",
    "..WWWWWWWWWW..",
    "..HHHHSSSSHW..",
    "..HSSSSSSSSH..",
    "..HSEESSEESS..",
    "..SSKESSKESS..",
    "..SSSSSSSSSS..",
    "...SSSPPSSS...",
    "....SSSSSS....",
    "..WWWWWWWWWW..",
    "...WRWWRWWR...",
    "...RRRRRRRR...",
    "..RRRRRRRRRR..",
    ".WRRRRRRRRRRW.",
    "DDDDDDDDDDDDDD",
    "FFFFFFFFFFFFFF",
    ".FFRRFFFFRRFF.",
    "..FRRFFFFRRF..",
    "...RR....RR...",
    "...RR....RR...",
    "...RR....RR...",
]
_ELF_COLORS = {"R": (215, 0, 0), "W": (240, 240, 240), "S": (255, 185, 140),
               "H": (110, 55, 15), "E": (30, 120, 255), "K": (0, 30, 110),
               "P": (255, 80, 110), "D": (150, 65, 25), "F": (200, 195, 180)}
EYE_ROWS = (11, 12)




def _night_vision(rgb):
    lum = int(0.3 * rgb[0] + 0.59 * rgb[1] + 0.11 * rgb[2])
    return (0, min(255, 50 + lum), lum // 4)


def draw_elf(canvas, x0, y0, t, wave=False, tint=None, scan=None):
    """Big Vinny. tint: a color function (night vision); scan: rows to drop out."""
    blink = (t % 2.6) < 0.14
    wink = 1.4 < (t % 5.0) < 1.7
    for y, row in enumerate(ELF_ART):
        if scan and y in scan:
            continue
        for x, ch in enumerate(row):
            if ch == ".":
                continue
            if ch in "EK" and y in EYE_ROWS and (blink or (wink and x > 6)):
                ch = "S" if y == EYE_ROWS[0] else "H"   # lid down, lash line
            r, g, b = _ELF_COLORS[ch] if not tint else tint(_ELF_COLORS[ch])
            _px(canvas, x0 + x, y0 + y, _c(r, g, b))
    if wave and int(t / 0.3) % 2 == 0:          # white mitten up: a wave
        _px(canvas, x0 + 12, y0 + 20, BLACK)
        for dx, dy, ch in ((12, 19, "R"), (13, 18, "R"), (13, 17, "W")):
            _px(canvas, x0 + dx, y0 + dy, _c(*_ELF_COLORS[ch]))




def _make_agent_card(status):
    def scene(canvas, t):
        draw_elf(canvas, 1, 2, t, wave=t > 2.5)
        graphics.DrawText(canvas, small(), 18, ROW[0], AMBER, "AGENT:")
        graphics.DrawText(canvas, small(), 18, ROW[1], WHITE, AGENT)
        if t > 0.8:
            graphics.DrawText(canvas, small(), 18, ROW[2], AMBER, "STATUS:")
        if t > 1.4 and (t < 2.0 or _blink(t, 0.4)):
            graphics.DrawText(canvas, small(), 18, ROW[3], GREEN, status[:9])
    return scene


# --------------------------------------------------------------------------
# The intercept: you weren't supposed to see this
# --------------------------------------------------------------------------
def _make_intercept(fragments, rng):
    frags = rng.sample(fragments, min(4, len(fragments)))
    spots = [(rng.choice([0, 1, 2, 3]), rng.choice([True, False])) for _ in frags]
    glimpse_at = rng.choice([1, 2])                      # which slot shows Vinny instead
    rng_j = random.Random(rng.random())
    def scene(canvas, t):
        if t < 1.6:                                          # lock on
            _static(canvas, t, 0.22)
            if _blink(t, 0.2):
                _text(canvas, 1, GREEN, "ENCRYPTED", center=True)
                _text(canvas, 2, GREEN, "TRAFFIC...", center=True)
            return
        if t < 7.6:                                          # fragments flicker through
            _static(canvas, t, 0.07)
            i = min(len(frags) - 1, int((t - 1.6) / 1.5))
            local = (t - 1.6) - i * 1.5
            if i == glimpse_at:                              # for a moment: Vinny himself
                if local < 1.3:
                    jitter = rng_j.choice((-1, 0, 0, 1)) if int(t * 20) % 3 == 0 else 0
                    drop = {int(local * 40) % 28, int(local * 40 + 9) % 28}
                    draw_elf(canvas, 25 + jitter, 2, t, tint=_night_vision, scan=drop)
                return
            if local < 1.2 and not (0.5 < local < 0.58):     # a little dropout
                row, centered = spots[i]
                _text(canvas, row, LIGHT_GREEN, frags[i], center=centered)
            return
        if t < 9.4:                                          # and it's gone
            _static(canvas, t, max(0.0, 0.25 - (t - 7.6) * 0.14))
            if _blink(t, 0.25):
                _text(canvas, 1, RED, "SIGNAL", center=True)
                _text(canvas, 2, RED, "LOST", center=True)
    return [(9.4, scene)]


# --------------------------------------------------------------------------
# Making every day different
# --------------------------------------------------------------------------
SPECIAL_DAYS = {              # (month, day): (from, lines, tag) - replaces that day's 10:30
    (11, 28): ("VINNY", ["FIRST FULL", "DAY ON POST.", "HOUSE: GREAT", "BILLY: GREAT"], "AGENT OUT"),
    (12, 1): ("VINNY", ["DEC 1.", "COUNTDOWN", "STARTED.", "24 SLEEPS."], "STAND BY"),
    (12, 6): ("VINNY", ["ST. NICHOLAS", "DAY. EXTRA", "MAGIC IN", "THE AIR."], "CONFIRMED"),
    (12, 12): ("SANTA", ["12 DAYS TO", "XMAS EVE.", "ELVES:", "FULL SPEED."], "-SANTA"),
    (12, 18): ("SANTA", ["ONE WEEK", "TO GO.", "REINDEER:", "READY."], "-SANTA"),
    (12, 21): ("VINNY", ["LONGEST", "NIGHT OF", "THE YEAR.", "MORE SNEAK."], "HEE HEE"),
    (12, 22): ("SANTA", ["SLEIGH:", "LOADING.", "2 DAYS."], "-SANTA"),
    (12, 23): ("VINNY", ["TOMORROW", "IS THE BIG", "DAY. HOUSE:", "READY."], "STAND BY"),
}
CUSTOM_FILE = settings.__file__.replace("settings.py", "data/vinny_custom.txt")
_custom = {"mtime": None, "items": []}


def custom_messages():
    """Your own messages from data/vinny_custom.txt (reloaded whenever you change it).
    Each: (month, day, year or None, (hour, minute) or None, from, [lines])."""
    import os
    try:
        mtime = os.path.getmtime(CUSTOM_FILE)
    except OSError:
        return []
    if mtime == _custom["mtime"]:
        return _custom["items"]
    items = []
    for raw in open(CUSTOM_FILE, encoding="utf-8"):
        line = raw.split("#", 1)[0].strip()
        if not line:
            continue
        try:
            head, body = line.split(None, 3)[:3], line.split(None, 3)[3]
            when, at, who = head
            parts = when.split("-")
            year = int(parts[0]) if len(parts) == 3 else None
            month, day = int(parts[-2]), int(parts[-1])
            hm = None if at in ("-", "AUTO", "auto") else tuple(int(x) for x in at.split(":"))
            who = who.upper()
            lines = [l.strip().upper()[:12] for l in body.split("|") if l.strip()][:6]
            if who in ("VINNY", "SANTA") and lines:
                items.append((month, day, year, hm, who, lines))
        except (ValueError, IndexError):
            continue                              # a line that doesn't parse is skipped
    _custom.update(mtime=mtime, items=items)
    return items


def _customs_for(d):
    return [(i, it) for i, it in enumerate(custom_messages())
            if it[0] == d.month and it[1] == d.day and (it[2] is None or it[2] == d.year)]


_season_cache = {}


def _season(year):
    if year not in _season_cache:
        d, end, plan = date(year, 11, 1), date(year, 12, 26), []
        while d <= end:
            plan += day_plan(d, include_custom=False)
            d += timedelta(days=1)
        _season_cache[year] = plan
    return _season_cache[year]


def _seq(now, kind):
    """How many times this kind has gone out earlier this season (so nothing repeats)."""
    now = _local(now).replace(second=0, microsecond=0)
    return sum(1 for t, k in _season(now.year) if k == kind and t < now)


def _pick(pool, name, now, seq, n=1):
    order = list(range(len(pool)))
    random.Random(f"{name}-{_local(now).year}").shuffle(order)
    return [pool[order[(seq * n + j) % len(pool)]] for j in range(n)]


def _day_on_station(now):
    return (_local(now).date() - date(_local(now).year, *ARRIVES)).days + 1


def _sleeps(now):
    d = _local(now).date()
    return (date(d.year, 12, 25) - d).days


# --------------------------------------------------------------------------
# One transmission of each kind: [(seconds, draw(canvas, t))]
# --------------------------------------------------------------------------
def _hdr(rng):
    return rng.choice([["ELFNET //", "FIELD REPORT", f"AGENT: {AGENT}"],
                       ["ELFNET //", "SECURE", "N.POLE: EYES", "ONLY"],
                       ["ELFNET BURST", f"FM: {AGENT}", "TO: N.P. CMD"]])


# --------------------------------------------------------------------------
# TOY-style parts: strobe, header, authenticate, message, status, end
# --------------------------------------------------------------------------
ELF_GREEN = _c(0, 220, 70)


def _make_flash(words, color, fill):
    """The opening strobe with hazard stripes - TOY's, in Vinny's colors."""
    def scene(canvas, t):
        word = words[int(t / 0.72) % len(words)]
        if int(t / 0.18) % 2 == 0:
            canvas.Fill(*fill)
            santa._big(canvas, 21, BLACK, word)
        else:
            santa._big(canvas, 21, color, word)
        for x in range(64):
            c = color if ((x + int(t * 20)) // 4) % 2 == 0 else BLACK
            _px(canvas, x, 0, c); _px(canvas, x, 1, c)
            _px(canvas, x, 30, c); _px(canvas, x, 31, c)
    return scene


def _make_header(title, frm, to, pri, title_color):
    def scene(canvas, t):
        if _blink(t, 0.3):
            _text(canvas, 0, title_color, title[:12], center=True)
        _type(canvas, 1, AMBER, f"FROM: {frm}"[:12], t, 0.3)
        _type(canvas, 2, AMBER, f"TO: {to}"[:12], t, 1.2)
        typed_at = 2.1 + len(pri[0]) / 16 + 0.3
        if t < typed_at:
            _type(canvas, 3, AMBER, pri[0][:12], t, 2.1)
        else:
            word = pri[int((t - typed_at) / 0.6) % len(pri)]
            _text(canvas, 3, GREEN if word != pri[0] else AMBER, word[:12])
    return scene


def _make_msg(label, line1, line2, tag):
    """One message screen, laid out like TOY's MSG BEGINS."""
    def scene(canvas, t):
        _type(canvas, 0, AMBER, label[:12], t, 0.0)
        if line1:
            _type(canvas, 1, GREEN, line1[:12], t, 0.7)
        if line2:
            _type(canvas, 2, WHITE, line2[:12], t, 1.5)
        if tag and t > 2.6 and _blink(t, 0.5):
            _text(canvas, 3, AMBER, tag[:12])
    return scene


def _make_status(label, word, level, sub, word_color=WHITE):
    """Five blocks and a big blinking word, like TOY's SANTCON screen."""
    def scene(canvas, t):
        _text(canvas, 0, AMBER, label[:12], center=True)
        if t < 0.8 or _blink(t, 0.35):
            santa._big(canvas, 20, word_color, word[:9])
        for i in range(5):
            x0 = 2 + i * 12
            lit = i < level and t > 0.3 + i * 0.15
            col = (GREEN if i == level - 1 else _c(0, 120, 40)) if lit else DIM_GREEN
            for x in range(x0, x0 + 10):
                _px(canvas, x, 22, col); _px(canvas, x, 23, col)
        subs = sub if isinstance(sub, (list, tuple)) else [sub]
        _text(canvas, 3, AMBER, subs[int(t / 1.2) % len(subs)][:12], center=True)
    return scene


def _msg_screens(lines, first_label, tag):
    """Split lines into TOY-style message screens, two lines each."""
    lines = [l for l in lines if l]
    out = []
    pairs = [lines[i:i + 2] for i in range(0, len(lines), 2)]
    for i, pair in enumerate(pairs):
        label = first_label if i == 0 else "CONT'D"
        last = i == len(pairs) - 1
        out.append((4.2, _make_msg(label, pair[0], pair[1] if len(pair) > 1 else None,
                                   tag if last else "STAND BY")))
    return out


def _code(rng, suffix="07"):
    return "".join(rng.choice(santa.CODE_CHARS) for _ in range(3)) + "-" + suffix


def _vinny_open(rng, title, pri=("PRI: SNEAKY", "PRI: SHHHH"), to="N.POLE"):
    return [(2.2, _make_flash(["ELFNET", AGENT], ELF_GREEN, (0, 200, 60))),
            (5.0, _make_header(title, AGENT, to, list(pri), GREEN)),
            (4.5, santa._make_auth(_code(rng)))]


def _santa_open(rng, title="*** MSG ***"):
    return [(2.2, _make_flash(["ELFNET", "SANTA"], RED, (255, 0, 0))),
            (5.0, _make_header(title, "SANTA", AGENT, ["PRI: JOLLY", "PRI: HOHOHO"], RED)),
            (4.5, santa._make_auth(_code(rng, "25")))]


def _magic(rng):
    return 97.5 + rng.random() * 2.4


# --------------------------------------------------------------------------
# One transmission of each kind: [(seconds, draw(canvas, t))]
# --------------------------------------------------------------------------
def transmission(kind, now, rng=None):
    rng = rng or random.Random()
    now = _local(now)
    n_day, sleeps = _day_on_station(now), _sleeps(now)
    if kind.startswith("custom:"):                       # one of yours
        items = custom_messages()
        i = int(kind.split(":")[1])
        _, _, _, _, who, lines = items[i] if i < len(items) else (0, 0, 0, 0, "VINNY", ["ALL QUIET."])
        if who == "SANTA":
            return _santa_open(rng) + _msg_screens(lines, "MSG BEGINS", "-SANTA") + \
                [(4.0, _make_agent_card("MSG RCVD")), (2.4, santa._scene_end)]
        return _vinny_open(rng, "*** RPT ***") + [(4.0, _make_agent_card("REPORTING"))] + \
            _msg_screens(lines, "RPT BEGINS", "AGENT OUT") + [(2.4, santa._scene_end)]
    if kind == "special":
        who, lines, tag = SPECIAL_DAYS[(now.month, now.day)]
        if who == "SANTA":
            return _santa_open(rng) + _msg_screens(lines, "MSG BEGINS", tag) + \
                [(4.0, _make_agent_card("MSG RCVD")), (2.4, santa._scene_end)]
        return _vinny_open(rng, "*** RPT ***") + [(4.0, _make_agent_card("REPORTING"))] + \
            _msg_screens(lines, "RPT BEGINS", tag) + [(2.4, santa._scene_end)]
    if kind in ("intercept", "teaser"):
        frags = INTERCEPT_FRAGMENTS if kind == "intercept" else TEASER_FRAGMENTS
        if kind == "intercept" and 0 < sleeps < 100:
            frags = frags + [f"...T-{sleeps} DAYS"[:12]]
        return [(2.2, _make_flash(["SIGNAL", "INTERCEPT"[:9]], ELF_GREEN, (0, 120, 40)))] + \
            _make_intercept(frags, rng)
    if kind == "post":
        out = _vinny_open(rng, "*** RPT ***")
        out.append((4.0, _make_agent_card("ON POST")))
        out += _msg_screens(_pick(NEW_POST, "post", now, _seq(now, "post"))[0], "RPT BEGINS", "AGENT OUT")
        out.append((4.0, _make_status("COVER STATUS", "INTACT", 5,
                                      [f"DAY {n_day}", f"MAGIC {_magic(rng):.1f}%", f"T-{sleeps} TO XMAS"])))
    elif kind == "sitrep":
        out = _vinny_open(rng, "** SITREP **")
        out.append((4.0, _make_agent_card(rng.choice(["REPORTING", "ON WATCH", "SNEAKY"]))))
        k2, k3 = rng.sample([k for k in SITREP_FIELDS if k != "BILLY"], 2)
        if rng.random() < 0.08:                              # once in a while, and kindly
            out += _msg_screens(rng.choice(INCIDENTS), "RPT BEGINS", "STILL NICE.")
        else:
            wx = _wx_line()
            lines = [f"{KID}:", rng.choice(SITREP_FIELDS["BILLY"]),
                     f"{k2}:", rng.choice(SITREP_FIELDS[k2])]
            if wx and rng.random() < 0.6:                    # real Seattle weather
                lines += [wx, "SPIRIT: HIGH"]
            else:
                lines += [f"{k3}:", rng.choice(SITREP_FIELDS[k3])]
            out += _msg_screens(lines, "SITREP", "ALL QUIET.")
        out.append((3.5, _make_status("NICE-O-METER", "NICE", 5, ["NICE LIST", f"T-{sleeps} TO XMAS"])))
    elif kind == "intel":
        out = _vinny_open(rng, "** INTEL **")
        out.append((4.0, _make_agent_card(rng.choice(["ON WATCH", "LISTENING", "UNDERCOVR"]))))
        body = []
        for label, vals in _pick(INTEL_FIELDS, "intel", now, _seq(now, "intel"), n=2):
            body += [label, rng.choice(vals)]
        out += _msg_screens(body, "INTEL", rng.choice(INTEL_CLOSERS))
    elif kind == "santa":
        out = _santa_open(rng)
        out += _msg_screens(_pick(SANTA_REPLIES, "santa", now, _seq(now, "santa"))[0], "MSG BEGINS", "-SANTA")
        out.append((4.0, _make_agent_card("MSG RCVD")))
    elif kind == "orders":
        out = _santa_open(rng, "** ORDERS **")
        out += _msg_screens(_pick(ORDERS, "orders", now, _seq(now, "orders"))[0], "ORDERS", "-SANTA")
        out.append((4.0, _make_agent_card("WILCO")))
    elif kind == "deploy":                                   # the night before he arrives
        out = _santa_open(rng, "** ORDERS **")
        out += _msg_screens([f"AGENT {AGENT}", "DEPLOY", "TONIGHT.", f"POST: {KID}"], "ORDERS",
                            "SEATTLE, WA")
        out.append((3.5, _make_status("DEPLOYMENT", "T-1 DAY", 4, "STAND BY", GOLD)))
    elif kind == "arrival":
        out = _vinny_open(rng, "** DEPLOY **")
        out.append((4.0, _make_agent_card("DEPLOYED")))
        out += _msg_screens([f"AGENT: {AGENT}", f"POST: {KID}", "STATUS:", "DEPLOYED"],
                            "FIELD OPS", "ON STATION")
        out.append((3.5, _make_status("COVER STATUS", "INTACT", 5, f"MAGIC {_magic(rng):.1f}%")))
    elif kind == "arrival_santa":
        out = _santa_open(rng)
        out += _msg_screens(["WELCOME TO", "YOUR POST."], "MSG BEGINS", "-SANTA")
        out.append((4.0, _make_agent_card("MSG RCVD")))
    elif kind == "eve_post":
        out = _vinny_open(rng, "*** RPT ***")
        out.append((4.0, _make_agent_card("LAST DAY")))
        out += _msg_screens(["FINAL DAY", "ON STATION."], "RPT BEGINS", "ALL QUIET.")
    elif kind == "eve_report":
        out = _vinny_open(rng, "** FINAL **", pri=("PRI: TOP", "PRI: XMAS!"))
        out.append((4.0, _make_agent_card("FINAL RPT")))
        out += _msg_screens([f"{KID}: NICE.", "HOUSE: READY", "COOKIES: OUT", "STOCKING: UP"],
                            "FINAL RPT", "NICE LIST.")
        out.append((3.5, _make_status("NICE-O-METER", "MAX NICE", 5, f"{KID}: YES", GOLD)))
    elif kind == "eve_santa":
        out = _santa_open(rng)
        out += _msg_screens(["SEE YOU", "TONIGHT."], "MSG BEGINS", "-SANTA")
        out.append((4.0, _make_agent_card("PACKED!")))
    elif kind == "eve_orders":
        out = _santa_open(rng, "** ORDERS **")
        out += _msg_screens(["EXFIL WITH", "ME TONIGHT."], "ORDERS", "WHEELS UP -S")
        out.append((4.0, _make_agent_card("WILCO")))
    elif kind == "xmas":
        out = _santa_open(rng)
        out += _msg_screens(["MISSION", "COMPLETE.", "WELL DONE,", f"{AGENT}.",
                             "MERRY XMAS,", f"{KID}!"], "MSG BEGINS", "HO HO HO -S")
        out.append((4.0, _make_agent_card("OFF DUTY")))
    else:
        raise ValueError(kind)
    return out + [(2.4, santa._scene_end)]


# --------------------------------------------------------------------------
# The schedule
# --------------------------------------------------------------------------
def _toy_clear(t):
    if mode(t) not in ("test", "live"):
        return True
    toy = santa._alert_minutes(t)
    return all(min(abs(t.minute - k), 60 - abs(t.minute - k)) >= TOY_GAP_MINUTES for k in toy)


def _clear(t, taken):
    """Nudge a time later until it's clear of TOY alerts and other Vinny traffic."""
    for _ in range(60):
        if _toy_clear(t) and all(abs((t - x).total_seconds()) >= 300 for x in taken):
            return t
        t += timedelta(minutes=1)
    return t


def day_plan(d, include_custom=True):
    """[(datetime, kind)] for one date, the same every time it's asked."""
    if not VINNY_ON:
        return []
    tz = santa.HOME_TZ
    rng = random.Random(f"vinny-{d.isoformat()}")
    arrive = date(d.year, *ARRIVES)
    at = lambda h, m, wiggle: datetime(d.year, d.month, d.day, h, m, tzinfo=tz) + \
        timedelta(minutes=rng.randint(-wiggle, wiggle))
    plan = []
    if arrive - timedelta(days=TEASER_DAYS) <= d < arrive:      # he's coming
        plan.append((at(rng.randint(9, 17), rng.randint(0, 59), 0), "teaser"))
        if d == arrive - timedelta(days=1):
            plan.append((at(18, 45, 15), "deploy"))
    elif d == arrive:
        plan += [(at(7, 30, 20), "arrival"), (at(10, 30, 30), "intel"),
                 (at(13, 30, 30), "arrival_santa"), (at(16, 0, 30), "sitrep"),
                 (at(18, 45, 15), "orders")]
    elif arrive < d < date(d.year, 12, 24):
        for h, m, w, kind in SLOTS:
            if kind == "day":
                kind = rng.choice(["sitrep", "intel"])
            elif kind == "day_or_santa":
                kind = rng.choice(["sitrep", "intel", "santa", "santa"])
            plan.append((at(h, m, w), kind))
        for _ in range(rng.randint(*INTERCEPTS_PER_DAY)):
            plan.append((at(rng.randint(8, 18), rng.randint(0, 59), 0), "intercept"))
        if (d.month, d.day) in SPECIAL_DAYS:                  # a special date: its own message
            plan[1] = (plan[1][0], "special")
    elif d == date(d.year, 12, 24):
        plan += [(at(7, 30, 20), "eve_post"), (at(11, 0, 30), "eve_report"),
                 (at(14, 0, 30), "intercept"), (at(15, 30, 30), "eve_santa"),
                 (at(17, 30, 15), "eve_orders")]
    elif d == date(d.year, 12, 25):
        plan.append((at(8, 0, 15), "xmas"))
    if include_custom:                                        # your own messages
        for i, (_, _, _, hm, _, _) in _customs_for(d):
            if hm:
                plan.append((datetime(d.year, d.month, d.day, hm[0], hm[1], tzinfo=tz), f"custom:{i}"))
            else:                                             # no time: takes the early-afternoon slot
                slot = next((j for j, (t, k) in enumerate(plan) if 12 <= t.hour < 15 and
                             not k.startswith("custom")), None)
                if slot is None:
                    plan.append((at(13, 30, 30), f"custom:{i}"))
                else:
                    plan[slot] = (plan[slot][0], f"custom:{i}")
    taken, out = [], []
    for t, kind in sorted(plan):
        if not (kind.startswith("custom:") and t.second == 0 and include_custom and
                custom_messages()[int(kind.split(":")[1])][3]):
            t = _clear(t, taken)
        taken.append(t)
        out.append((t.replace(second=0, microsecond=0), kind))
    return out


_fired = set()


def due(now=None):
    """The kind of transmission to start this minute, or None."""
    now = _local(now)
    for t, kind in day_plan(now.date()):
        key = (t, kind)
        if t <= now < t + timedelta(minutes=1) and key not in _fired:
            _fired.add(key)
            return kind
    return None


def scene_at(scene_list, t):
    return santa.scene_at(scene_list, t)


if __name__ == "__main__":
    import sys
    arg = sys.argv[1] if len(sys.argv) > 1 else date.today().isoformat()
    if arg == "check":                                        # check your custom file
        items = custom_messages()
        print(f"{CUSTOM_FILE}: {len(items)} message(s) read")
        for m, d_, y, hm, who, lines in items:
            when = f"{y}-{m:02d}-{d_:02d}" if y else f"every {m:02d}-{d_:02d}"
            at = f"{hm[0]:02d}:{hm[1]:02d}" if hm else "auto (early afternoon)"
            print(f"  {when} {at:>22}  {who:5}  " + " | ".join(lines))
        sys.exit()
    d = date.fromisoformat(arg)
    plan = day_plan(d)
    print(f"Vinny on {d:%a %b %d}: {len(plan)} transmissions")
    for t, kind in plan:
        print(f"  {t:%I:%M %p}  {kind}")
