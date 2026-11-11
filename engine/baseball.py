"""
Opening Day Mode (idea by Uncle Buck).

  * Countdown: starts a week after the World Series ends, runs to the day before
    Opening Day. From 99 days out, each day shows a jersey with that number and a
    player who wore it (data/jersey_countdown.txt - edit it anytime).
  * Milestones: 100 DAYS, ONE WEEK, the night before, plus any dates in
    settings.BASEBALL_MILESTONES (Truck Day, pitchers & catchers report...).
  * Opening Day itself: the bunting takeover a few times through the morning and
    30 minutes before each of our games (pages/opening.py).
  * Opening Day week: every clock in ballpark colors (settings.SPECIAL_DAYS).

Dates live in settings.py: OPENING_DAYS and WORLD_SERIES_END.

Check the countdown for any day:  python -m engine.baseball 2026-12-16
"""
import re
import sys
from datetime import date, timedelta
from pathlib import Path

import settings

JERSEY_FILE = Path(__file__).resolve().parent.parent / "data" / "jersey_countdown.txt"
DEFAULT_WS_END = (11, 5)      # if we don't know when the World Series ended, guess Nov 5
JERSEY_FROM = 99              # jersey days start this many days out
ROTATE_MINUTES = 10           # several players on one number take turns this often


# ------------------------------------------------------------------ dates

def _md(year, s):
    m, d = map(int, s.split("-"))
    return date(year, m, d)


def opening_day(year):
    s = getattr(settings, "OPENING_DAYS", {}).get(year)
    return _md(year, s) if s else None


def world_series_end(year):
    s = getattr(settings, "WORLD_SERIES_END", {}).get(year)
    return _md(year, s) if s else date(year, *DEFAULT_WS_END)


def next_opening_day(today):
    """The Opening Day we're counting toward (this year's, or next year's)."""
    for year in (today.year, today.year + 1):
        od = opening_day(year)
        if od and od >= today:
            return od
    return None


def countdown_start(od):
    return world_series_end(od.year - 1) + timedelta(days=7)


def days_to_go(today):
    """Days until Opening Day while the countdown runs, else None."""
    if not getattr(settings, "OPENING_DAY_MODE", True):
        return None
    od = next_opening_day(today)
    if not od or not (countdown_start(od) <= today < od):
        return None
    return (od - today).days


def is_opening_day(today):
    return getattr(settings, "OPENING_DAY_MODE", True) and opening_day(today.year) == today


# ------------------------------------------------------------------ jersey list

_cache = {"mtime": None, "data": {}}
_LINE = re.compile(r"^(\d{1,2})\s+([A-Z]{2,4})\s+(.+)$")


def parse_jerseys(text):
    """{number: [(team, line1, line2), ...]} in file order."""
    out = {}
    for raw in text.splitlines():
        line = raw.split("#", 1)[0].strip()
        if not line:
            continue
        m = _LINE.match(line.upper())
        if not m:
            continue
        num, team, name = int(m.group(1)), m.group(2), m.group(3)
        parts = [p.strip() for p in name.split("|")]
        l1 = parts[0][:8]
        l2 = parts[1][:8] if len(parts) > 1 else ""
        out.setdefault(num, []).append((team, l1, l2))
    return out


def jerseys():
    """The jersey list, re-read whenever the file changes."""
    try:
        mtime = JERSEY_FILE.stat().st_mtime
    except OSError:
        return {}
    if mtime != _cache["mtime"]:
        try:
            _cache["data"] = parse_jerseys(JERSEY_FILE.read_text(encoding="utf-8"))
        except OSError:
            _cache["data"] = {}
        _cache["mtime"] = mtime
    return _cache["data"]


def jersey_for(days, now_ts):
    """The player shown on this day (taking turns if several), or None."""
    if days is None or days > JERSEY_FROM:
        return None
    entries = jerseys().get(days)
    if not entries:
        return None
    return entries[int(now_ts // (ROTATE_MINUTES * 60)) % len(entries)]


# ------------------------------------------------------------------ milestones

def milestone(today, days):
    """Today's milestone card as (kind, arg), or None.
    kinds: eve, hundred, week, truck, pitchers, firstgame, text"""
    if days is None:
        return None
    for entry in getattr(settings, "BASEBALL_MILESTONES", []):
        when, kind = entry[0], entry[1]
        arg = entry[2] if len(entry) > 2 else ""
        d = date.fromisoformat(when) if len(when) == 10 else _md(today.year, when)
        if d == today:
            return kind, arg
    if days == 1:
        return "eve", ""
    if days == 100:
        return "hundred", ""
    if days == 7:
        return "week", ""
    return None


# ------------------------------------------------------------------ CLI

def _report(day):
    d = days_to_go(day)
    od = next_opening_day(day)
    if d is None:
        print(f"{day}: no countdown (Opening Day {od}, countdown starts "
              f"{countdown_start(od) if od else '?'})")
        return
    j = jerseys().get(d, [])
    ms = milestone(day, d)
    who = "; ".join(f"{t} {a} {b}".strip() for t, a, b in j) or "plain countdown"
    print(f"{day} {day.strftime('%a')}: {d} days  {who}" + (f"  [milestone: {ms[0]}]" if ms else ""))


if __name__ == "__main__":
    if len(sys.argv) > 1 and sys.argv[1] != "all":
        _report(date.fromisoformat(sys.argv[1]))
    else:
        today = date.today()
        od = next_opening_day(today)
        d = countdown_start(od) if od else today
        while od and d <= od:
            _report(d)
            d += timedelta(days=1)
