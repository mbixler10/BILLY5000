"""
Ship's Bells: every half hour (home time) the panel takes over to strike the
bells for the current watch, US Navy style, then hands the screen back.

        SECOND DOG              <- watch name (gold)
     [] []  [] []  [] [] ..     <- 8 bell slots; struck in pairs, ding-ding ... ding-ding
       5 BELLS   6:30P          <- bell count + home time

Interrupts anything EXCEPT:
  * the ITFDB flash and the Santa TOY alert (they outrank it), and
  * the Santa radar page or the MERRY CHRISTMAS greeting while they're on screen.
In those cases the bells wait and strike as soon as the screen is free
(up to BELLS_WAIT_MINUTES late; after that they're skipped for that half hour).

Watch names and bell counts are from the old clock (test32.py).
"""
import time
from zoneinfo import ZoneInfo

import settings
from engine.bitfonts import F3, F5
from engine.specialdays import Frame
from .base import Page

HOME = ZoneInfo(settings.HOME[2])
GOLD = (255, 176, 0)
DIM_GOLD = (58, 40, 0)
WHITE = (255, 255, 255)
GREY = (122, 122, 122)

# US Navy watch names (Naval History and Heritage Command list)
WATCHES = [(20, "1ST NIGHT"), (18, "SECOND DOG"), (16, "FIRST DOG"), (12, "AFTERNOON"),
           (8, "FORENOON"), (4, "MORNING"), (0, "MID WATCH")]

BELL = ["..#..",
        ".###.",
        ".###.",
        ".###.",
        "#####",
        "..#.."]

PAIR_GAP = 0.35      # seconds between the two strikes of a pair
NEXT_PAIR = 0.9      # seconds between pairs
FIRST_STRIKE = 0.6


def watch_name(hour):
    return next(name for start, name in WATCHES if hour >= start)


def bells_at(hour, minute):
    """Bells most recently struck at local time hour:minute (1-8)."""
    mins = hour * 60 + minute
    b = (mins // 30) % 8 or 8
    if settings.TRADITIONAL_DOG_WATCH and 18 * 60 + 30 <= mins < 20 * 60:
        b -= 4  # traditional last dog watch: 1, 2, 3, then 8 at 20:00
    return b


def strike_times(n):
    """When each of n bells is struck, in seconds: pairs, ding-ding ... ding-ding."""
    out, t = [], FIRST_STRIKE
    for i in range(n):
        out.append(t)
        t += PAIR_GAP if i % 2 == 0 else NEXT_PAIR
    return out


def draw_bells(canvas, when, t):
    """One frame of the bells page. when = the half-hour being struck (home time)."""
    f = Frame()
    n = bells_at(when.hour, when.minute)
    strikes = strike_times(n)

    name = watch_name(when.hour)
    f.text(F5, name, 32 - Frame.width(F5, name) // 2, 1, GOLD)

    for i in range(8):
        x = 6 + (i // 2) * 14 + (i % 2) * 6
        y = 12
        struck = i < n and t >= strikes[i]
        ringing = struck and t - strikes[i] < 0.3
        color = WHITE if ringing else GOLD if struck else DIM_GOLD
        if i >= n:
            color = DIM_GOLD
        for r, row in enumerate(BELL):
            for q, ch in enumerate(row):
                if ch == "#":
                    f.set(x + q, y + r, color)
        if ringing:   # little sound lines either side of the bell
            for dy in (1, 3):
                f.set(x - 2, y + dy, WHITE)
                f.set(x + 6, y + dy, WHITE)

    done = t >= strikes[-1] + 0.4
    label = "1 BELL" if n == 1 else f"{n} BELLS"
    clock = f"{when.hour % 12 or 12}:{when.minute:02d}" + ("A" if when.hour < 12 else "P")
    if done:
        line = f"{label}  {clock}"
        f.text(F3, line, 32 - Frame.width(F3, line) // 2, 25, GREY)
    f.flush(canvas)


class ShipsBells(Page):
    def __init__(self):
        self.pending = None      # half-hour waiting to be struck
        self.showing = None
        self.started = 0.0
        self.last_mark = None
        self.force = False       # --demo-bells

    def _length(self):
        n = bells_at(self.showing.hour, self.showing.minute)
        return strike_times(n)[-1] + settings.BELLS_HOLD_SECONDS

    def is_active(self, now):
        if not settings.BELLS_ON:
            return False
        here = now.astimezone(HOME)
        mark = here.replace(minute=30 if here.minute >= 30 else 0, second=0, microsecond=0)
        if self.last_mark is None:
            self.last_mark = mark          # clock just started: wait for the next half hour
        elif mark != self.last_mark:
            self.last_mark = mark          # a new half hour: time to strike
            self.pending = mark
        if self.force:
            self.pending, self.force = mark, False
        if self.showing is not None:
            if time.monotonic() - self.started < self._length():
                return True
            self.showing = None
        if self.pending is not None:
            late = (here - self.pending).total_seconds() / 60
            if late > settings.BELLS_WAIT_MINUTES:
                self.pending = None
                return False
            return True
        return False

    def yields_to(self, page):
        """Don't cut into Christmas: wait while the Santa radar or the MERRY
        CHRISTMAS greeting is on screen."""
        if self.showing is not None:
            return False                 # already striking: finish
        kind = type(page).__name__
        if kind in ("SantaRadar", "HomeSantaRadar"):
            return True
        if kind == "SpecialSlot" and getattr(page, "kind", None) == "special" \
                and page.arg.get("name") == "CHRISTMAS":
            return True
        return False

    def draw(self, canvas, now, t):
        if self.showing is None:          # first frame: start striking
            self.showing, self.pending = self.pending, None
            self.started = time.monotonic()
        draw_bells(canvas, self.showing, time.monotonic() - self.started)
