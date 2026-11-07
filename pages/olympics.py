"""
Olympic countdown: the five rings, the next Games, and how many days to go.
During the Games it switches to "DAY 5 OF 17", and on opening day "TODAY!".
Shows every OLYMPICS_EVERY_LAPS laps (see settings), at the end of the lap.
"""
import math
from datetime import datetime, date
from zoneinfo import ZoneInfo

import settings
from engine.bitfonts import F3, F5
from engine.specialdays import Frame
from .base import Page
from .lighthouse import PICKER

RING_COLORS = [(0, 129, 200), (210, 210, 220), (238, 51, 78),      # blue, black (white on LEDs), red
               (252, 177, 49), (0, 166, 81)]                         # yellow, green
GOLD = (255, 190, 40)
WHITE = (242, 242, 242)
NAVY = (8, 22, 52)
TICKER_PX_PER_SEC = 16
TICKER_HOLD = 1.0


def draw_rings(f, cx, top, t):
    """Five interlocking rings, 7 px across, gently glinting."""
    r = 3.2
    centers = [(cx - 8, top + 3), (cx, top + 3), (cx + 8, top + 3),
               (cx - 4, top + 7), (cx + 4, top + 7)]
    for i, (x0, y0) in enumerate(centers):
        c = RING_COLORS[i]
        for y in range(y0 - 5, y0 + 6):
            for x in range(x0 - 5, x0 + 6):
                d = math.hypot(x + 0.5 - (x0 + 0.5), y + 0.5 - (y0 + 0.5))
                if abs(d - r) < 0.75:
                    glint = 0.5 + 0.5 * math.sin(t * 2 - i * 1.2 + math.atan2(y - y0, x - x0))
                    f.set(x, y, tuple(int(v * (0.75 + 0.25 * glint)) for v in c))


def next_games(now):
    """(games row, opening datetime, closing date) for the next or current Games."""
    for row in settings.OLYMPICS:
        short, name, opening, closing, tz = row
        z = ZoneInfo(tz)
        open_dt = datetime.fromisoformat(opening).replace(tzinfo=z)
        close_d = date.fromisoformat(closing)
        if now.astimezone(z).date() <= close_d:
            return row, open_dt, close_d
    return None


def status(now):
    """('countdown', days) / ('today', 0) / ('games', day_n, total) for the next Games."""
    g = next_games(now)
    if not g:
        return None
    row, open_dt, close_d = g
    home = ZoneInfo(settings.HOME[2])
    today = now.astimezone(home).date()
    days = (open_dt.astimezone(home).date() - today).days
    if days > 0:
        return row, ("countdown", days)
    if days == 0:
        return row, ("today", 0)
    total = (close_d - open_dt.date()).days + 1
    return row, ("games", (today - open_dt.date()).days + 1, total)


def ticker(row, st):
    short, name = row[0], row[1]
    if st[0] == "countdown":
        unit = "DAY" if st[1] == 1 else "DAYS"
        msg = "%d %s UNTIL %s - GO TEAM USA!" % (st[1], unit, name)
    elif st[0] == "today":
        msg = "%s START TODAY! - GO TEAM USA!" % name
    else:
        msg = "%s - DAY %d OF %d - GO TEAM USA!" % (name, st[1], st[2])
    return msg


def _scroll(f, msg, t, color):
    w = Frame.width(F3, msg)
    period = w + 24
    off = int(max(0.0, t - TICKER_HOLD) * TICKER_PX_PER_SEC) % period
    for x in (64 - 2 - off, 64 - 2 - off + period):
        f.text(F3, msg, x, 27, color)


def scroll_seconds(msg):
    return TICKER_HOLD + (Frame.width(F3, msg) + 64) / TICKER_PX_PER_SEC + 0.5


RED = (200, 30, 40)
BLUE = (30, 70, 200)


def draw_medal(f, cx, cy, t):
    """Gold medal on a red-white-blue ribbon, with a glint sweeping across."""
    for y in range(0, cy - 4):                       # ribbon: a V of stripes
        for k, c in enumerate((RED, WHITE, BLUE)):
            f.set(cx - 5 + y // 2 + k, y, c)
            f.set(cx + 5 - y // 2 - k, y, c)
    r = 5.3
    sweep = (t * 6) % 24 - 6
    for y in range(cy - 6, cy + 7):
        for x in range(cx - 6, cx + 7):
            d = math.hypot(x - cx, y - cy)
            if d <= r:
                c = (200, 140, 20) if d > r - 1.1 else GOLD
                if abs((x - cx) + (y - cy) - sweep) < 1.2:
                    c = (255, 250, 210)
                f.set(x, y, c)
    for x, y in ((cx, cy - 2), (cx - 1, cy - 1), (cx, cy - 1), (cx, cy), (cx, cy + 1),
                 (cx - 1, cy + 2), (cx, cy + 2), (cx + 1, cy + 2)):
        f.set(x, y, (150, 95, 10))                  # a stamped "1"


def draw_tribute(canvas, t):
    tr = settings.OLYMPICS_TRIBUTE
    f = Frame()
    draw_medal(f, 9, 14, t)
    f.text(F5, tr["first"], 20, 1, WHITE)
    f.text(F5, tr["last"], 20, 10, WHITE)
    f.text(F3, tr["medal"], 20, 19, GOLD)
    f.fill(0, 26, 63, 31, NAVY)
    _scroll(f, tr["ticker"], t, GOLD)
    f.flush(canvas)


def draw_olympics(canvas, now, t):
    s = status(now)
    f = Frame()
    if not s:
        f.flush(canvas)
        return
    row, st = s
    draw_rings(f, 14, 0, t)
    f.text(F5, row[0], 63 - Frame.width(F5, row[0]), 2, GOLD)        # "LA28"

    if st[0] == "countdown":
        big, small = "{:,}".format(st[1]), ("DAY" if st[1] == 1 else "DAYS")
    elif st[0] == "today":
        big, small = "TODAY!", ""
    else:
        big, small = "DAY %d" % st[1], "OF %d" % st[2]
    scale = 2 if Frame.width(F5, big, 2) + 2 + Frame.width(F3, small) <= 62 else 1
    w = Frame.width(F5, big, scale) + (2 + Frame.width(F3, small) if small else 0)
    x = (64 - w) // 2
    y = 12 if scale == 2 else 15
    x += f.text(F5, big, x, y, WHITE, scale)
    if small:
        f.text(F3, small, x + 2, 21 if scale == 2 else 17, GOLD)

    f.fill(0, 26, 63, 31, NAVY)
    _scroll(f, ticker(row, st), t, GOLD)
    f.flush(canvas)


def countdown_seconds(now):
    s = status(now)
    return max(settings.OLYMPICS_SECONDS, scroll_seconds(ticker(*s))) if s else 1


def tribute_seconds():
    tr = settings.OLYMPICS_TRIBUTE
    return max(10, scroll_seconds(tr["ticker"])) if tr else 0


class OlympicCountdown(Page):
    """Countdown first, then the tribute card to Great-Grandpa."""

    @property
    def seconds(self):
        return countdown_seconds(datetime.now().astimezone()) + tribute_seconds()

    def is_active(self, now):
        if not settings.OLYMPICS_ON or status(now) is None:
            return False
        every = max(1, settings.OLYMPICS_EVERY_LAPS)
        return PICKER.lap % every == 0

    def draw(self, canvas, now, t):
        first = countdown_seconds(now)
        if t < first or not settings.OLYMPICS_TRIBUTE:
            draw_olympics(canvas, now, t)
        else:
            draw_tribute(canvas, t - first)
