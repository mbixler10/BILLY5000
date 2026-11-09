"""
vinny.py - Vinny and Buddy, running side by side with Santa's TOY alerts.

Vinny is Billy's Elf on the Shelf: ELFNET's scout elf, the agent in the field.
Buddy is ELFNET's transmissions officer: he runs every link (and spills cocoa).

TOY alerts are Santa spotting. Vinny's alerts are his own, on their own
schedule, never within a few minutes of a TOY alert:

    TOP SECRET stamp -> today's EPISODE -> Buddy transmits (something usually
    goes wrong) -> Vinny sneaks back into hiding

EPISODES - 150 little cartoons in engine/vinny_eps_*.py, on a calendar:
    Nov 1 until he lands     North Pole spy training, 2 a day
                             (the night before: "INBOUND" over Seattle)
    arrival day              AGENT LANDED + FIND ME
    then until Dec 23        in the field: 2 a day
    Dec 24                   Christmas Eve: Santa snacks, sleigh pickup
    Dec 25                   Christmas Day: mission success, shift over
    Dec 26                   the BOXING DAY special
Each day's alerts take turns between that day's two episodes; every 4th alert
is a bonus episode from the extras, so all 150 get screen time.

Preview:
    python main.py --demo-vinny                          today's episode
    python main.py --demo-vinny --at "2026-12-10 09:00"  another day
    python main.py --demo-vinny --vinny-ep boxing_day    one episode by name
    python -m engine.vinny                               print the calendar
"""
import math
import random
from datetime import date, timedelta

from engine import santa
from engine.santa import (_local, mode, _px, _c, _text, _type, _blink, graphics,
                          small, big, ROW, COMMAND, BLACK, WHITE, GREEN,
                          DARK_RED, AMBER, GOLD, GREY)
from engine import vinny_eps_field as _field
from engine.vinny_eps_pole import POLE
from engine.vinny_eps_field import ARRIVE, FIELD
from engine.vinny_eps_special import EVE, XMAS, BOXING

# ---------------------------------------------------------------------------
# Settings - change these freely
# ---------------------------------------------------------------------------
ELF_NAME = "VINNY"
COMMS_NAME = "BUDDY"          # ELFNET's transmissions officer: runs every link
ELF_ARRIVES = (11, 27)        # (month, day) Vinny first shows up at the house
ELF_ON = True
VINNY_PER_HOUR = 1            # Vinny alerts per hour (Santa's TOY alerts are separate)
VINNY_FIRST_HOUR = 7          # only while Billy's up: 7:00am ...
VINNY_LAST_HOUR = 19          # ... through 7:59pm
VINNY_SEASON = ((11, 1), (12, 26))   # first and last day (Boxing Day)
EPISODES_PER_DAY = 2
BONUS_EVERY = 4               # every 4th alert of the day is a bonus episode
TOY_GAP_MINUTES = 3           # never within this many minutes of a TOY alert

GLITCHES = [                  # what goes wrong at Buddy's radio
    ("BUDDY SPILT", "COCOA. OOPS"),
    ("BUDDY", "SNEEZED"),
    ("SCULLY ATE", "THE ANTENNA"),
    ("VINNY SAT", "ON ANTENNA"),
    ("RADIO PLAYS", "JINGLE BELLS"),
    ("BUDDY ON", "SNACK BREAK"),
]

# ---------------------------------------------------------------------------
# Big Vinny (the sign-off) - drawn from his photo
# ---------------------------------------------------------------------------
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



RED = _c(255, 0, 0)

# North Pole episodes that wait as bonus reruns (the family files go on the calendar)
POLE_BONUS = ["mail_cannon", "snow_fort", "telescope", "rain_sim", "coffee_test",
              "ready_check", "weather_desk", "lost_penguin", "sky_tv", "pole_vault"]

ALL_EPISODES = POLE + ARRIVE + FIELD + EVE + XMAS + BOXING
BY_KEY = {e.key: e for e in ALL_EPISODES}


def elf_days_until(now):
    now = _local(now)
    return (date(now.year, *ELF_ARRIVES) - now.date()).days


def elf_status(now):
    """'prep' before he lands, 'arrived', 'duty', 'flying' (Dec 24), 'home' (after)."""
    now = _local(now)
    if now.month == 12 and now.day >= 25:
        return "home"
    if now.month == 12 and now.day == 24:
        return "flying"
    d = elf_days_until(now)
    if d > 0:
        return "prep"
    return "arrived" if d == 0 else "duty"


def draw_elf(canvas, x0, y0, t, wave=False):
    blink = (t % 2.6) < 0.14
    wink = 1.4 < (t % 5.0) < 1.7
    for y, row in enumerate(ELF_ART):
        for x, ch in enumerate(row):
            if ch == ".":
                continue
            if ch in "EK" and y in EYE_ROWS and (blink or (wink and x > 6)):
                ch = "S" if y == EYE_ROWS[0] else "H"   # lid down, lash line
            r, g, b = _ELF_COLORS[ch]
            _px(canvas, x0 + x, y0 + y, _c(r, g, b))
    if wave and int(t / 0.3) % 2 == 0:          # white mitten up: a wave
        _px(canvas, x0 + 12, y0 + 20, BLACK)
        for dx, dy, ch in ((12, 19, "R"), (13, 18, "R"), (13, 17, "W")):
            _px(canvas, x0 + dx, y0 + dy, _c(*_ELF_COLORS[ch]))


def _ease(t, start, length):
    return min(1.0, max(0.0, (t - start) / length))


def _bar(canvas, x0, x1, y, frac, color, back=None, h=3):
    back = back or _c(0, 40, 10)
    edge = x0 + int((x1 - x0) * frac)
    for x in range(x0, x1):
        for yy in range(y, y + h):
            _px(canvas, x, yy, color if x < edge else back)


# ---------------------------------------------------------------------------
# The calendar
# ---------------------------------------------------------------------------
def _days(a, b):
    d = a
    while d <= b:
        yield d
        d += timedelta(days=1)


def calendar(year):
    """{date: [episode keys]} for the season, plus the leftover bonus lists."""
    start, end = date(year, *VINNY_SEASON[0]), date(year, *VINNY_SEASON[1])
    arrive = date(year, *ELF_ARRIVES)
    eve, xmas, boxing = date(year, 12, 24), date(year, 12, 25), date(year, 12, 26)
    cal = {}
    pole = [e.key for e in POLE if e.key != "inbound"]
    pole = [k for k in pole if k not in POLE_BONUS] + [k for k in pole if k in POLE_BONUS]
    pre_days = list(_days(start, arrive - timedelta(days=1)))
    i = 0
    for d in pre_days:
        n = EPISODES_PER_DAY
        todays = []
        if d == arrive - timedelta(days=1):
            todays.append("inbound")
            n -= 1
        for _ in range(n):
            todays.append(pole[i % len(pole)])
            i += 1
        cal[d] = todays
    pole_extra = pole[i:] + ["inbound"] * 0
    cal[arrive] = [e.key for e in ARRIVE]
    field = [e.key for e in FIELD]
    # the advent countdown needs to land in December
    field_days = list(_days(arrive + timedelta(days=1), eve - timedelta(days=2)))
    j = 0
    for d in field_days:
        cal[d] = []
        for _ in range(EPISODES_PER_DAY):
            cal[d].append(field[j % len(field)])
            j += 1
    used = [k for d in field_days for k in cal[d]]
    if "advent" in used:
        d_adv = next(d for d in field_days if "advent" in cal[d])
        if d_adv.month == 11:
            later = next((d for d in field_days if d.month == 12 and d.day >= 3), None)
            if later:
                k = cal[d_adv].index("advent")
                cal[d_adv][k], cal[later][0] = cal[later][0], "advent"
    cal[eve - timedelta(days=1)] = ["final_report", "pack_home"]
    cal[eve] = ["santa_snacks", "sleigh_pickup"]
    cal[xmas] = [e.key for e in XMAS]
    cal[boxing] = [e.key for e in BOXING]
    field_extra = field[j:] if j < len(field) else []
    return cal, pole_extra, field_extra


def episode_for(now, alert_index):
    """Which episode this alert shows."""
    now = _local(now)
    cal, pole_extra, field_extra = calendar(now.year)
    todays = cal.get(now.date())
    if not todays:
        return None
    status = elf_status(now)
    extras = pole_extra if status == "prep" else field_extra if status == "duty" else []
    if extras and BONUS_EVERY and alert_index % BONUS_EVERY == BONUS_EVERY - 1:
        # take turns through the extras so every one of them gets its day
        per_day = (VINNY_LAST_HOUR - VINNY_FIRST_HOUR + 1) // BONUS_EVERY or 1
        first = date(now.year, *VINNY_SEASON[0]) if status == "prep" else \
            date(now.year, *ELF_ARRIVES) + timedelta(days=1)
        slot = (now.date() - first).days * per_day + alert_index // BONUS_EVERY
        return BY_KEY[extras[slot % len(extras)]]
    return BY_KEY[todays[alert_index % len(todays)]]


# ---------------------------------------------------------------------------
# The parts around the episode
# ---------------------------------------------------------------------------
def _scene_stamp(canvas, t):
    _type(canvas, 0, AMBER, f"{COMMAND} FIELD", t, 0.0, cps=24, center=True)
    if t > 0.5:
        shake = (1 if int(t * 30) % 2 else -1) if t < 0.85 else 0
        x0, x1, y0, y1 = 4 + shake, 59 + shake, 10, 22
        for x in range(x0, x1 + 1):
            _px(canvas, x, y0, RED); _px(canvas, x, y1, RED)
        for y in range(y0, y1 + 1):
            _px(canvas, x0, y, RED); _px(canvas, x1, y, RED)
        graphics.DrawText(canvas, small(), 7 + shake, 20, RED, "TOP SECRET")
    if t > 1.2:
        _type(canvas, 3, GREY, f"AGENT {ELF_NAME}"[:12], t, 1.2, center=True)


def _make_title(ep):
    """A beat with the episode's name, like a TV show."""
    def scene(canvas, t):
        _type(canvas, 1, GOLD, "TODAY:", t, 0.0, center=True)
        _type(canvas, 2, WHITE, ep.title[:12], t, 0.3, center=True)
    return scene


def _make_episode(ep):
    def scene(canvas, t):
        ep.draw(canvas, t)
    return scene


def _make_transmit(rng):
    glitch = rng.choice(GLITCHES) if rng.random() < 0.7 else None
    def scene(canvas, t):
        _type(canvas, 0, AMBER, "TRANSMITTING", t, 0.0, cps=24)
        if glitch is None:
            _bar(canvas, 2, 62, 10, _ease(t, 0.6, 2.4), GREEN)
            if t > 3.1:
                _text(canvas, 2, GREEN, "SENT! N.POLE", center=True)
                _text(canvas, 3, GREY, f"OPR {COMMS_NAME}", center=True)
            return
        if t < 1.8:
            _bar(canvas, 2, 62, 10, _ease(t, 0.6, 1.2) * 0.6, GREEN)
        elif t < 3.8:                                      # uh oh
            _bar(canvas, 2, 62, 10, 0.6, RED if _blink(t, 0.15) else DARK_RED)
            _text(canvas, 2, WHITE, glitch[0][:12])
            _text(canvas, 3, WHITE, glitch[1][:12])
        else:
            f = 0.6 + 0.4 * _ease(t, 3.9, 1.0)
            _bar(canvas, 2, 62, 10, f, GREEN)
            _text(canvas, 2, GOLD if f < 1 else GREEN, "RETRYING..." if f < 1 else "SENT!")
            if f >= 1:
                _text(canvas, 3, GREY, f"OPR {COMMS_NAME}")
    return scene


def _make_signoff(now):
    status = elf_status(now)
    lines = {"flying": ("MISSION", "OVER.", "GO SANTA!"),
             "home": ("VINNY @", "N. POLE", "SEE YA!")}.get(
                 status, (f"{ELF_NAME} OUT", "BACK TO", "HIDING..."))
    def scene(canvas, t):
        x = 1 - int(_ease(t, 1.2, 1.2) * 16)
        if x > -15:
            draw_elf(canvas, x, 2, t, wave=t < 1.2)
        for i, line in enumerate(lines):
            if t > 0.3 + i * 0.4:
                graphics.DrawText(canvas, small(), 17, ROW[i + 1], [AMBER, WHITE, GREEN][i], line[:9])
    return scene


def scenes(now, rng=None, alert_index=None, episode=None):
    """The whole Vinny alert: [(seconds, draw(canvas, t))]."""
    now = _local(now)
    rng = rng or random.Random()
    if alert_index is None:
        alert_index = max(0, now.hour - VINNY_FIRST_HOUR)
    ep = BY_KEY.get(episode) if episode else episode_for(now, alert_index)
    if ep is None:
        ep = BY_KEY["spy_school"]
    d = now.date()
    if ep.key == "advent":
        dec_day = d.day if d.month == 12 else 0
        _field.DAYS[0] = min(24, dec_day)
        _field.DAYS[1] = max(0, (date(d.year, 12, 25) - d).days)
    return [(2.0, _scene_stamp), (1.6, _make_title(ep)), (ep.seconds, _make_episode(ep)),
            (6.0, _make_transmit(rng)), (3.2, _make_signoff(now))]


# ---------------------------------------------------------------------------
# Schedule
# ---------------------------------------------------------------------------
def in_season(now):
    now = _local(now)
    return date(now.year, *VINNY_SEASON[0]) <= now.date() <= date(now.year, *VINNY_SEASON[1])


def _vinny_minutes(now):
    """This hour's Vinny minutes: random, but clear of Santa's TOY minutes."""
    toy = santa._alert_minutes(now) if mode(now) in ("test", "live") else set()
    ok = [m for m in range(60)
          if all(min(abs(m - k), 60 - abs(m - k)) >= TOY_GAP_MINUTES for k in toy)]
    rng = random.Random(f"vinny-{now.date()}-{now.hour}")
    return set(rng.sample(ok, min(VINNY_PER_HOUR, len(ok))))


_last_key = None


def should_alert(now=None):
    global _last_key
    now = _local(now)
    if not (ELF_ON and in_season(now)):
        return False
    if not (VINNY_FIRST_HOUR <= now.hour <= VINNY_LAST_HOUR):
        return False
    if now.minute not in _vinny_minutes(now):
        return False
    key = (now.date(), now.hour, now.minute)
    if key == _last_key:
        return False
    _last_key = key
    return True


def scene_at(scene_list, t):
    return santa.scene_at(scene_list, t)


if __name__ == "__main__":
    import sys
    year = int(sys.argv[1]) if len(sys.argv) > 1 else date.today().year
    cal, pole_extra, field_extra = calendar(year)
    for d in sorted(cal):
        print(d.strftime("%a %b %d"), " + ".join(BY_KEY[k].title for k in cal[d]))
    print(f"\nBonus episodes (every {BONUS_EVERY}th alert): "
          f"{len(pole_extra)} before he lands, {len(field_extra)} after")
    print(f"{len(ALL_EPISODES)} episodes in all")
