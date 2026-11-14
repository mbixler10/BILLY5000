"""
Pearl Harbor Day reading of the names (December 7).

At the moment the attack began (PEARL_START, Hawaii time: 7:48 AM, which is
9:48 AM in Seattle), the names of the 2,408 killed take over the screen one at
a time, read by location: a title card for each ship or station (USS ARIZONA,
1,177) and then its names, alphabetical, each with rank and service. It runs
without a break until every name has had its moment (about two hours), then the
normal clock comes back with the REMEMBER PEARL HARBOR page each lap.

The names come from data/names_pearl_harbor.txt (built by tools/pearl_from_xlsx.py).
Progress is saved as it goes, so a restart picks up at the next name.
"""
import bisect
import math
import time
from datetime import timedelta
from pathlib import Path
from zoneinfo import ZoneInfo

import settings
from engine.bitfonts import F3, F5
from engine.specialdays import Frame, HOME, mix

ROOT = Path(__file__).resolve().parent.parent
NAMES_FILE = ROOT / "data" / "names_pearl_harbor.txt"
STATE = ROOT / "state" / "names_pearl_harbor.txt"

WHITE = (235, 235, 235)
GOLD = (242, 196, 107)
WATER = (20, 45, 90)
SERVICE_COLOR = {"USN": (110, 150, 255), "USNR": (110, 150, 255),
                 "USMC": (225, 60, 60), "USMCR": (225, 60, 60),
                 "US ARMY": (220, 190, 70), "US ARMY RES": (220, 190, 70),
                 "CIVILIAN": (200, 200, 200)}

_cards = None
_times = None


def _fit(text, font=F3):
    """Wrap onto as few lines as fit the panel in the given font."""
    if Frame.width(font, text) <= 62:
        return [text]
    lines, cur = [], ""
    for w in text.split():
        trial = (cur + " " + w).strip()
        if cur and Frame.width(font, trial) > 62:
            lines.append(cur)
            cur = w
        else:
            cur = trial
    return lines + [cur]


def cards():
    """[(kind, lines, sub, sub color, place), ...] kind: intro / head / name."""
    global _cards
    if _cards is None:
        _cards = []
        try:
            rows = [ln.split("\t") for ln in NAMES_FILE.read_text(encoding="utf-8").splitlines() if ln.strip()]
        except Exception:
            rows = []
        if rows:
            _cards.append(("intro", ["DECEMBER 7", "1941"], "", GOLD, ""))
            _cards.append(("intro", ["REMEMBER", "PEARL", "HARBOR"], "", GOLD, ""))
        counts = {}
        for r in rows:
            counts[r[0]] = counts.get(r[0], 0) + 1
        place = None
        for r in rows:
            where, who = r[0], r[1]
            sub = r[2] if len(r) > 2 else ""
            if where != place:
                place = where
                n = counts[where]
                note = "" if where == "NAMES UNKNOWN" else "{:,}".format(n)
                lines = ["USS"] + _fit(where[4:], F5) if where.startswith("USS ") else _fit(where, F5)
                _cards.append(("head", lines, note, GOLD, where))
            svc = next((k for k in sorted(SERVICE_COLOR, key=len, reverse=True) if sub.endswith(k) or sub.startswith(k)), "")
            _cards.append(("name", _fit(who), sub, SERVICE_COLOR.get(svc, (170, 170, 170)), where))
    return _cards


def _seconds(kind):
    return {"intro": settings.PEARL_TITLE_SECONDS + 2,
            "head": settings.PEARL_TITLE_SECONDS}.get(kind, settings.PEARL_HOLD)


def _starts():
    global _times
    if _times is None:
        starts, t = [], 0.0
        for c in cards():
            starts.append(t)
            t += _seconds(c[0])
        _times = (starts, t)
    return _times


def _card_at(start, t):
    starts, total = _starts()
    n = len(starts)
    base = starts[start % n]
    wraps, rem = divmod(base + t, total)
    idx = max(0, bisect.bisect_right(starts, rem) - 1)
    return int(wraps) * n + idx, rem - starts[idx]


def render(f, start, t):
    """One card, still and centered, fading in and out, over calm dark water.
    Returns the index of the card on screen."""
    for y in range(24, 32):                                 # the harbor, barely there
        for x in range(64):
            a = 0.10 + 0.10 * (y - 24) / 7
            a *= 0.7 + 0.3 * math.sin(x * 0.45 + y * 1.3 + t * 0.8)
            f.blend(x, y, WATER, a)
    a, into = _card_at(start, max(0.0, t))
    all_cards = cards()
    kind, lines, sub, scol, place = all_cards[a % len(all_cards)]
    dur = _seconds(kind)
    fade = min(1.0, into / 0.35, max(0.0, (dur - into) / 0.35))

    def ink(c):
        return mix((0, 0, 0), c, fade)

    if kind == "name":
        h = 7 * len(lines) - 2 + (7 if sub else 0)
        top = max(0, (25 - h) // 2)
        for k, ln in enumerate(lines):
            f.text(F3, ln, 32 - Frame.width(F3, ln) // 2, top + 7 * k, ink(WHITE))
        if sub:
            y = top + 7 * len(lines)
            f.text(F3, sub, 32 - Frame.width(F3, sub) // 2, y, ink(scol))
        if len(lines) < 3:                     # long names get the whole screen
            lc = mix((0, 0, 0), GOLD, 0.7)
            f.text(F3, place, 32 - Frame.width(F3, place) // 2, 26, ink(lc))
    else:
        big = all(Frame.width(F5, ln) <= 62 for ln in lines)
        fnt, lh = (F5, 9) if big else (F3, 7)
        if big and len(lines) >= 3 and sub:
            lh = 8                              # USS / WEST / VIRGINIA + count
        h = lh * len(lines) - (lh - 7) + (7 if sub else 0)
        top = max(0, (32 - h) // 2)
        for k, ln in enumerate(lines):
            f.text(fnt, ln, 32 - Frame.width(fnt, ln) // 2, top + lh * k, ink(WHITE if kind == "head" else GOLD))
        if sub:
            y = top + lh * len(lines) - (lh - 7) + 2
            f.text(F3, sub, 32 - Frame.width(F3, sub) // 2, y, ink(GOLD if kind == "head" else WHITE))
    return a + 1 if into >= dur - 0.4 else a


class PearlReading:
    """The takeover. Same rules as the 9/11 reading: starts at PEARL_START
    (Hawaii time) on December 7 and runs until every name has been shown."""

    def __init__(self):
        self.cursor = 0
        self.year = None
        self.done = False
        self.anchor = None
        self.last_draw = 0.0
        self._saved_at = 0

    def _load(self, year):
        try:
            parts = STATE.read_text().strip().split(":")
            if int(parts[0]) == year:
                return int(parts[1]), len(parts) > 2 and parts[2] == "done"
        except Exception:
            pass
        return 0, False

    def _save(self):
        try:
            STATE.parent.mkdir(exist_ok=True)
            STATE.write_text("%d:%d%s" % (self.year, self.cursor, ":done" if self.done else ""))
        except Exception:
            pass

    def start_time(self, now):
        h, m = settings.PEARL_START
        hi = ZoneInfo("Pacific/Honolulu")
        return now.astimezone(hi).replace(hour=h, minute=m, second=0, microsecond=0)

    def is_active(self, now):
        if not getattr(settings, "PEARL_NAMES_ON", False) or not cards():
            return False
        local = now.astimezone(HOME)
        if (local.month, local.day) != (12, 7):
            return False
        if self.year != local.year:
            self.year = local.year
            self.cursor, self.done = self._load(local.year)
            self.anchor = None
        return not self.done and now >= self.start_time(now)

    def draw(self, canvas, now, mono):
        mono = time.monotonic()
        if self.anchor is None or mono - self.last_draw > 0.5:
            self.anchor = (self.cursor, mono)
        self.last_draw = mono
        start, t0 = self.anchor
        f = Frame()
        upto = render(f, start, mono - t0)
        f.flush(canvas)
        if upto > self.cursor:
            self.cursor = upto
            if self.cursor >= len(cards()):
                self.done = True
                self._save()
                return
        if mono - self._saved_at > 2:
            self._saved_at = mono
            self._save()

    def yields_to(self, page):
        return False

    def finish_estimate(self, now):
        return self.start_time(now) + timedelta(seconds=_starts()[1])


READING = PearlReading()
