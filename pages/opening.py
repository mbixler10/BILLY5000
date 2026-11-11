"""
Opening Day Mode pages (Uncle Buck's idea). Dates and the jersey list: engine/baseball.py.

  OpeningCountdown   in the rotation from a week after the World Series to the day
                     before Opening Day: plain day count, the jersey-number countdown
                     from 99 days out, and milestone cards (100 DAYS, TRUCK DAY...)
  OpeningDayAlert    Opening Day takeover: bunting strobe, today's games, ballpark
                     with the lights on - a few times in the morning and 30 minutes
                     before each of our games
  HomeRunFlash       all season: HOME RUN!! when the Dodgers or Mariners go deep
"""
import math
from datetime import datetime, timedelta
from zoneinfo import ZoneInfo

import settings
from engine import baseball, sports
from engine.bitfonts import F3, F5
from engine.specialdays import Frame, rnd
from engine.teamcolors import hexc, display_color, lum, mix, resolve
from .base import Page

HOME_TZ = ZoneInfo(settings.HOME[2])
WHITE = (242, 242, 242)
DIM = (122, 122, 122)
GOLD = (255, 200, 0)
AMBER = (255, 140, 0)
TAN = (242, 196, 107)
GRASS = (0, 110, 30)
GRASS2 = (0, 92, 26)
DIRT = (150, 90, 40)
BUNT = [(20, 50, 150), (235, 235, 235), (200, 20, 30)]   # blue / white / red
TEAM_STYLE = {   # jersey body, number color
    "LAD": ((235, 235, 235), (0, 90, 170)),
    "SEA": ((20, 50, 100), (0, 170, 170)),
}


def _team_cfg(abbr):
    for cfg in settings.TEAMS:
        if cfg["league"].startswith("baseball") and cfg["team"].upper() == abbr:
            return cfg
    return None


def _dim(c, k):
    return tuple(int(v * k) for v in c)


def center(f, font, s, y, c, scale=1):
    f.text(font, s, 32 - Frame.width(font, s) * scale // 2, y, c, scale)


# ------------------------------------------------------------------ little pictures

def bunting(f, y0=0, k=1.0, fans=(10, 32, 54), rx=10, ry=7):
    """Ballpark bunting: pleated half-fans, blue / white / red."""
    for cx in fans:
        for y in range(ry):
            for x in range(cx - rx, cx + rx + 1):
                if (x - cx) ** 2 / (rx * rx) + y * y / (ry * ry) <= 1:
                    band = 0 if y < ry * 3 // 7 else (1 if y < ry * 5 // 7 else 2)
                    c = BUNT[band]
                    if (x - cx) % 4 == 0:
                        c = _dim(c, 0.6)
                    f.set(x, y0 + y, _dim(c, k))


def ball(f, cx, cy, r=4):
    for y in range(cy - r, cy + r + 1):
        for x in range(cx - r, cx + r + 1):
            if (x - cx) ** 2 + (y - cy) ** 2 <= r * r + r * 0.6:
                f.set(x, y, WHITE)
    for dy in range(-r + 1, r):
        f.set(cx - 2 + abs(dy) // 2, cy + dy, (210, 0, 0))
        f.set(cx + 2 - abs(dy) // 2, cy + dy, (210, 0, 0))


TRIM = {"LAD": (200, 30, 40), "SEA": (0, 170, 170)}


def _jersey_rows(w=28, h=24):
    """Back of a jersey, 28 x 24: shoulders, collar notch, sleeves with trim, hem trim."""
    rows = []
    for y in range(h):
        r = [" "] * w
        if y == 0:
            for x in list(range(6, 12)) + list(range(16, 22)):
                r[x] = "W"
        elif y == 1:
            for x in range(2, 26):
                r[x] = "W"
            r[13] = r[14] = " "
        elif y < 7:
            for x in range(w):
                r[x] = "T" if y == 6 and (x < 3 or x > 24) else "W"
        else:
            for x in range(3, 25):
                r[x] = "T" if y == h - 1 else "W"
        rows.append("".join(r))
    return rows


JERSEY = _jersey_rows()


def jersey(f, num, team):
    """Big jersey back on the left (x 0-27, y 0-23), the day count as its number."""
    body, ink = TEAM_STYLE.get(team, TEAM_STYLE["LAD"])
    trim = TRIM.get(team, TRIM["LAD"])
    for y, row in enumerate(JERSEY):
        for x, ch in enumerate(row):
            if ch == "W":
                f.set(x, y, body)
            elif ch == "T":
                f.set(x, y, trim)
    s = str(num)
    w = len(s) * 12 - 2
    f.text(F5, s, 14 - w // 2, 8, ink, 2)


def truck(f, team, t):
    body, ink = TEAM_STYLE.get(team, TEAM_STYLE["LAD"])
    name = (_team_cfg(team) or {}).get("name", "SPRING")
    roll = int(t * 6) % 3
    for x in range(64):
        f.set(x, 27, (60, 60, 60))
        if (x + roll) % 6 < 3:
            f.set(x, 29, (90, 90, 50))
    f.fill(2, 13, 42, 24, body if team == "LAD" else (235, 235, 235))
    f.fill(2, 13, 42, 13, ink)
    w = Frame.width(F5, name[:7])
    f.text(F5, name[:7], 22 - w // 2, 16, ink if team == "LAD" else (20, 50, 100))
    f.fill(44, 16, 53, 24, ink)
    f.fill(49, 17, 52, 20, (150, 200, 255))
    for x in (8, 16, 36, 48):
        for dx in (-2, -1, 0, 1, 2):
            for dy in (-1, 0, 1):
                if abs(dx) + abs(dy) < 3:
                    f.set(x + dx, 25 + dy, (70, 70, 70))
        f.set(x, 25, (170, 170, 170))


def ballpark(f, t):
    """Night game: light towers, stands, the diamond."""
    f.bg = (0, 0, 22)
    for i in range(14):
        f.set(int(rnd(i) * 64), int(rnd(i + 30) * 10), (110, 110, 150))
    on = 0.75 + 0.25 * math.sin(t * 3)
    for x in (6, 57):
        f.fill(x, 6, x, 19, (90, 90, 100))
        f.fill(x - 2, 3, x + 2, 5, _dim((255, 250, 200), on))
        for y in range(6, 14):
            for dx in range(-3 - (y - 6) // 2, 4 + (y - 6) // 2):
                if (x + dx + y) % 3 == 0:
                    f.blend(x + dx, y, (255, 250, 200), 0.18 * on)
    for y in range(14, 20):
        for x in range(64):
            crowd = (40, 40, 60) if (x + y) % 2 else (70, 70, 90)
            if rnd(x * 7 + y * 131 + int(t * 4)) > 0.93:
                crowd = (200, 200, 200)                 # camera flashes
            f.set(x, y, crowd)
    f.fill(0, 13, 63, 13, (0, 90, 156))
    for y in range(20, 32):
        for x in range(64):
            f.set(x, y, GRASS if (x // 2 + y // 2) % 2 == 0 else GRASS2)
    for i in range(8):
        for x in range(32 - i * 2, 32 + i * 2 + 1):
            f.set(x, 23 + i, DIRT)
    for i in range(6):
        for x in range(32 - i, 32 + i + 1):
            f.set(x, 25 + i, GRASS)
    for p in ((32, 23), (18, 30), (46, 30), (32, 27)):
        f.set(*p, WHITE)


def stars(f, n=25, seed=9):
    for i in range(n):
        f.set(int(rnd(i + seed) * 64), int(rnd(i + seed + 50) * 32), (150, 150, 200))


# ------------------------------------------------------------------ countdown page

def render_countdown(f, days, t, od, now_ts):
    who = baseball.jersey_for(days, now_ts)
    if who:
        team, l1, l2 = who
        jersey(f, days, team)
        f.text(F5, "DAYS" if days != 1 else "DAY", 31, 1, WHITE)
        f.text(F3, "OPENING", 31, 10, GOLD)
        f.text(F3, "DAY!", 31, 16, GOLD)
        name = f"{l1} {l2}".strip()
        for fnt, y in ((F5, 25), (F3, 26)):
            if Frame.width(fnt, name) <= 63:
                break
        else:
            name = l2 or l1                   # too long even small: last name only
        f.text(fnt, name, 32 - Frame.width(fnt, name) // 2, y, (190, 190, 190))
        return
    f.text(F5, "OPENING DAY", 1, 0, GOLD)
    s = str(days)
    w = f.text(F5, s, 2, 10, WHITE, 2)
    f.text(F5, "DAYS", 2 + w + 2, 17, DIM)
    if 2 + w + 2 + Frame.width(F5, "DAYS") < 51:      # room for a baseball
        ball(f, 57, 15)
    f.text(F3, od.strftime("%a %b ").upper() + str(od.day), 2, 26, (0, 140, 200))


def render_milestone(f, kind, arg, days, t):
    blink = (t % 0.8) < 0.5
    if kind == "eve":
        f.bg = (0, 0, 15)
        stars(f)
        center(f, F5, "TOMORROW IS", 1, WHITE)
        bunting(f, 11, fans=(16, 47), rx=9, ry=7)
        center(f, F5, "OPENING DAY", 24, GOLD if blink else WHITE)
    elif kind == "hundred":
        for i in range(40):
            f.set(int(rnd(i + int(t * 3) * 97) * 64), int(rnd(i + 7) * 32),
                  [GOLD, WHITE, (0, 90, 170), (220, 40, 40)][i % 4])
        f.fill(0, 9, 63, 23, (0, 0, 0))
        center(f, F5, "100 DAYS!", 12, GOLD if blink else WHITE)
        center(f, F3, "TO OPENING DAY", 25, WHITE)
        center(f, F3, "COUNTDOWN", 1, AMBER)
    elif kind == "week":
        center(f, F5, "ONE WEEK!", 2, GOLD if blink else WHITE)
        center(f, F3, "7 DAYS TO", 13, WHITE)
        center(f, F5, "OPENING DAY", 21, GOLD)
    elif kind == "truck":
        f.bg = (0, 0, 20)
        f.text(F5, "TRUCK DAY!", 1, 1, AMBER)
        truck(f, arg or "LAD", t)
    elif kind == "pitchers":
        center(f, F5, "SPRING BALL", 0, AMBER)
        f.text(F5, "PITCHERS &", 1, 9, WHITE)
        f.text(F5, "CATCHERS", 1, 17, WHITE)
        f.text(F5, "REPORT!", 1, 25, (0, 200, 60) if blink else (0, 140, 40))
        ball(f, 57, 25, 3)
    elif kind == "firstgame":
        team = (_team_cfg(arg) or {}).get("name", "")
        center(f, F5, "SPRING BALL", 0, AMBER)
        center(f, F5, "FIRST GAME", 10, WHITE)
        center(f, F5, "TODAY!", 18, GOLD if blink else WHITE)
        if team:
            center(f, F3, team, 27, (0, 170, 170) if arg == "SEA" else (60, 140, 255))
    else:   # "text": arg is the message
        center(f, F5, "OPENING DAY", 2, GOLD)
        center(f, F3, str(arg)[:15], 14, WHITE)
        center(f, F3, f"{days} DAYS", 24, DIM)


class OpeningCountdown(Page):
    """Days to Opening Day; the day's milestone card first when there is one."""
    PLAIN = 10

    def __init__(self):
        self.days = None
        self.ms = None

    def is_active(self, now):
        today = now.astimezone(HOME_TZ).date()
        self.days = baseball.days_to_go(today)
        self.ms = baseball.milestone(today, self.days)
        self.od = baseball.next_opening_day(today)
        return self.days is not None

    @property
    def seconds(self):
        return self.PLAIN + (8 if self.ms else 0)

    def draw(self, canvas, now, t):
        f = Frame()
        if self.ms and t < 8:
            render_milestone(f, self.ms[0], self.ms[1], self.days, t)
        else:
            render_countdown(f, self.days, t, self.od, now.timestamp())
        f.flush(canvas)


# ------------------------------------------------------------------ Opening Day takeover

STROBE, CARD, PARK = 6.0, 5.0, 6.0


def chip(f, abbr, prim, sec, x0, x1, y0=0, y1=8):
    col = display_color(prim)
    bg = mix((0, 0, 0), col, 0.6) if lum(col) > 45 else col
    f.fill(x0, y0, x1, y1, bg)
    sx = x0 if x0 == 0 else x1 - 1
    f.fill(sx, y0, sx + 1, y1, display_color(sec))
    i0, i1 = (x0 + 2, x1) if x0 == 0 else (x0, x1 - 2)
    ink = (20, 20, 20) if lum(bg) > 150 else WHITE
    font = F5 if Frame.width(F5, abbr) <= i1 - i0 + 1 else F3
    f.text(font, abbr, i0 + (i1 - i0 + 1 - Frame.width(font, abbr)) // 2,
           y0 + (1 if font is F5 else 2), ink)


def render_strobe(f, t):
    on = (t % 0.5) < 0.25
    bunting(f, 0, 1.0 if on else 0.55)
    center(f, F5, "OPENING DAY", 11, GOLD if (t % 0.4) < 0.2 else WHITE)
    for x in (4, 59):
        ball(f, x, 25, 3)
    center(f, F5, "IS HERE!", 22, AMBER)


def render_game_card(f, game, our_abbr, cfg, t):
    us = next((tm for tm in game["teams"] if tm["abbr"] == our_abbr), game["teams"][-1])
    them = next((tm for tm in game["teams"] if tm is not us), game["teams"][0])
    op, osec = resolve(cfg["league"], them["abbr"], them.get("color"), them.get("alt"))
    ours = (us["abbr"][:4], hexc(cfg["primary"]), hexc(cfg["secondary"]))
    theirs = (them["abbr"][:4], op, osec)
    left, right = (theirs, ours) if us["home"] else (ours, theirs)
    chip(f, *left, 0, 26)
    chip(f, *right, 37, 63)
    vs = "VS" if us["home"] else "@"
    f.text(F3, vs, 32 - Frame.width(F3, vs) // 2, 2, DIM)
    start = game["date"].astimezone(HOME_TZ)
    if game["state"] == "in":
        center(f, F5, "LIVE NOW", 13, (255, 60, 60))
    elif game.get("time_valid", True):
        hh = f"{start.hour % 12 or 12}:{start.minute:02d}"
        ap = "AM" if start.hour < 12 else "PM"
        w = Frame.width(F5, hh) * 2 + 2 + Frame.width(F3, ap)
        x = 32 - w // 2
        x += f.text(F5, hh, x, 11, WHITE, 2)
        f.text(F3, ap, x + 1, 11, DIM)
    else:
        center(f, F5, "TIME TBD", 13, WHITE)
    label, col = ("HOME OPENER", TAN) if us["home"] else ("1ST PITCH", DIM)
    if (t % 1.0) < 0.7 or not us["home"]:
        center(f, F3, label, 26, col)


def render_park(f, t):
    ballpark(f, t)
    center(f, F5, "PLAY BALL!", 6, WHITE if (t % 0.6) < 0.4 else GOLD)


class OpeningDayAlert(Page):
    """Opening Day takeover. --demo-opening plays it right away with sample games."""

    def __init__(self):
        self.force_at = None
        self.demo_games = None
        self.games = []
        self.start = None

    def _games(self, now):
        if self.demo_games is not None:
            return self.demo_games
        today = now.astimezone(HOME_TZ).date()
        out = []
        for cfg in settings.TEAMS:
            if not cfg["league"].startswith("baseball"):
                continue
            g = sports.game_on(cfg["name"], today, HOME_TZ)
            if g:
                out.append((g[0], cfg["team"].upper(), cfg))
        return sorted(out, key=lambda x: x[0]["date"])

    def duration(self):
        return STROBE + CARD * len(self.games) + PARK

    def _triggers(self, now):
        local = now.astimezone(HOME_TZ)
        out = []
        for hhmm in settings.OPENING_DAY_ALERTS:
            h, m = map(int, hhmm.split(":"))
            out.append(local.replace(hour=h, minute=m, second=0, microsecond=0))
        before = timedelta(minutes=settings.OPENING_DAY_ALERT_BEFORE_MIN)
        for game, _, _ in self.games:
            if game.get("time_valid", True):
                out.append(game["date"].astimezone(HOME_TZ) - before)
        return out

    def is_active(self, now):
        if self.force_at is True:
            self.force_at = now
        if self.force_at is not None:
            self.games = self._games(now)
            if (now - self.force_at).total_seconds() < self.duration():
                self.start = self.force_at
                return True
            self.force_at = None
            return False
        if not baseball.is_opening_day(now.astimezone(HOME_TZ).date()):
            return False
        self.games = self._games(now)
        for trig in self._triggers(now):
            if 0 <= (now - trig).total_seconds() < self.duration():
                self.start = trig
                return True
        return False

    def draw(self, canvas, now, t):
        f = Frame()
        s = (now - self.start).total_seconds()
        if s < STROBE:
            render_strobe(f, s)
        elif s < STROBE + CARD * len(self.games):
            i = int((s - STROBE) // CARD)
            game, abbr, cfg = self.games[i]
            render_game_card(f, game, abbr, cfg, s - STROBE - i * CARD)
        else:
            render_park(f, s)
        f.flush(canvas)


def demo_games(now):
    """Sample Opening Day: Braves at Dodgers 1:10, Red Sox at Mariners 7:10."""
    def g(away, home, hh, mm, our):
        start = now.astimezone(HOME_TZ).replace(hour=hh, minute=mm, second=0, microsecond=0)
        teams = [{"id": "2", "abbr": away, "home": False, "score": None, "color": None, "alt": None},
                 {"id": "1", "abbr": home, "home": True, "score": None, "color": None, "alt": None}]
        return ({"id": away + home, "date": start, "state": "pre", "detail": "",
                 "time_valid": True, "teams": teams}, our, _team_cfg(our))
    out = []
    if _team_cfg("LAD"):
        out.append(g("ATL", "LAD", 13, 10, "LAD"))
    if _team_cfg("SEA"):
        out.append(g("BOS", "SEA", 19, 10, "SEA"))
    return out


# ------------------------------------------------------------------ home run flash

def render_homer(f, team, grand, s):
    f.bg = (0, 0, 25)
    cfg = next((c for c in settings.TEAMS if c["name"] == team), None)
    wall = display_color(hexc(cfg["primary"])) if cfg else (0, 90, 156)
    for y in range(24, 32):
        for x in range(64):
            f.set(x, y, GRASS if (x // 2 + y // 2) % 2 == 0 else GRASS2)
    f.fill(0, 22, 63, 23, wall)
    pts = [(6 + i * 9, int(22 - math.sin(i / 6 * math.pi) * 17)) for i in range(7)]
    fly = min(1.0, s / 2.2)
    n = fly * 6
    for i in range(int(n)):
        f.set(*pts[i], (110, 110, 110))
    if fly < 1:
        i = int(n)
        a = n - i
        x = int(pts[i][0] + (pts[i + 1][0] - pts[i][0]) * a)
        y = int(pts[i][1] + (pts[i + 1][1] - pts[i][1]) * a)
        f.fill(x, y, x + 1, y + 1, WHITE)
    else:
        k = s - 2.2
        for b, (cx, cy, col) in enumerate(((50, 8, GOLD), (14, 9, (220, 40, 40)), (32, 6, WHITE))):
            p = ((k + b * 0.45) % 1.4) / 1.4
            r = p * 8
            for j in range(12):
                a = j / 12 * math.tau
                f.blend(int(cx + math.cos(a) * r), int(cy + math.sin(a) * r), col, max(0.0, 1 - p))
        msg = "GRAND SLAM!" if grand else "HOME RUN!!"
        center(f, F5, msg, 24, WHITE if (k % 0.4) < 0.2 else GOLD)


class HomeRunFlash(Page):
    def __init__(self):
        self.force = False
        self.grand = False

    def is_active(self, now):
        if self.force:
            sports.trigger_homer(self.force if isinstance(self.force, str) else "DODGERS", self.grand)
            self.force = False
        return sports.homer_active()

    def draw(self, canvas, now, t):
        import time
        team, grand = sports.homer_info()
        s = settings.HOMER_SECONDS - (sports._homer["until"] - time.time())
        f = Frame()
        render_homer(f, team, grand, s)
        f.flush(canvas)
