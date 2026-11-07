"""
Sports pages, in the same layout as the old clock (test32.py):

    [LAD ▌]  @  [▐ SF ]     <- team chips: team color, stripe on the outside edge
      3          2          <- big double-size scores (live / final)
    • LIVE TOP 7TH          <- small text; "FINAL" after the game

Upcoming game: the chips, then the start time as a big clock (Seattle time),
then TODAY or the date underneath.
"""
from zoneinfo import ZoneInfo

import settings
from engine import sports
from engine.bitfonts import F3, F5, draw, width
from engine.draw import fill
from engine.teamcolors import hexc, resolve, display_color, lum, mix
from .base import Page

WHITE = hexc("#F2F2F2")
RED = hexc("#FF3030")
CYAN = hexc("#40D0FF")
DODGER = hexc("#3C7DFF")
DIM = (122, 122, 122)
HOME_TZ = ZoneInfo(settings.HOME[2])
MARQUEE_HOLD = 1.5
MARQUEE_PX_PER_SEC = 14


def team_chip(canvas, abbr, prim, sec, x0, x1):
    """Team block: primary color field, secondary stripe on the outside edge,
    white abbreviation (dark if the field is very bright)."""
    col = display_color(prim)
    bg = mix((0, 0, 0), col, 0.6) if lum(col) > 45 else col
    fill(canvas, x0, 0, x1 - x0 + 1, 9, bg)
    stripe = display_color(sec)
    sx = x0 if x0 == 0 else x1 - 1
    fill(canvas, sx, 0, 2, 9, stripe)
    inner0, inner1 = (x0 + 2, x1) if x0 == 0 else (x0, x1 - 2)
    ink = (20, 20, 20) if lum(bg) > 150 else WHITE
    font = F5 if width(F5, abbr) <= inner1 - inner0 + 1 else F3
    w = width(font, abbr)
    y = 1 if font is F5 else 2
    draw(canvas, font, abbr, inner0 + (inner1 - inner0 + 1 - w) // 2, y, ink)


def big_score(canvas, score, left):
    s = str(score)
    if len(s) <= 2:
        s = s.rjust(2)
        xs = (3, 15) if left else (39, 51)
        for ch, x in zip(s, xs):
            if ch != " ":
                draw(canvas, F5, ch, x, 10, WHITE, scale=2)
    else:   # 3-digit score: normal size, centered in its half
        w = width(F5, s)
        x = (16 if left else 48) - w // 2
        draw(canvas, F5, s, x, 14, WHITE)


def big_clock(canvas, t, color):
    """Start time in fixed digit slots, AM/PM small on the right."""
    hh = str(t.hour % 12 or 12)
    mm = f"{t.minute:02d}"
    if len(hh) == 2:
        draw(canvas, F5, hh[0], 3, 10, color, 2)
    draw(canvas, F5, hh[-1], 15, 10, color, 2)
    draw(canvas, F5, ":", 27, 10, color, 2)
    draw(canvas, F5, mm[0], 31, 10, color, 2)
    draw(canvas, F5, mm[1], 43, 10, color, 2)
    draw(canvas, F3, "AM" if t.hour < 12 else "PM", 55, 10, DIM)


def bottom(canvas, segs, t, x0=2):
    """Small text on the bottom row: centered if it fits, otherwise scrolls."""
    full = "".join(s for s, _ in segs)
    w = width(F3, full)
    space = 61 - x0 + 1
    clip = (x0, 61)
    if w <= space:
        starts = [x0 + (space - w) // 2]
    else:
        period = w + 16
        off = int(max(0.0, t - MARQUEE_HOLD) * MARQUEE_PX_PER_SEC) % period
        starts = [x0 - off, x0 - off + period]
    for x in starts:
        for s, c in segs:
            x += draw(canvas, F3, s, x, 26, c, clip=clip)


class SportsPage(Page):
    def __init__(self, cfg):
        self.cfg = cfg
        self.name = cfg["name"]
        self.views = []

    def is_active(self, now):
        self.views = sports.view(self.name, now)
        return bool(self.views)

    @property
    def seconds(self):
        # each page (final, then next game) gets its own turn
        return settings.PAGE_SECONDS * max(1, len(self.views))

    def draw(self, canvas, now, t):
        n = min(int(t // settings.PAGE_SECONDS), len(self.views) - 1)
        kind, game, our_id = self.views[n]
        t = t - n * settings.PAGE_SECONDS
        us = next((tm for tm in game["teams"] if tm["id"] == our_id), game["teams"][0])
        them = next((tm for tm in game["teams"] if tm is not us), game["teams"][-1])
        opp_prim, opp_sec = resolve(self.cfg["league"], them["abbr"], them["color"], them["alt"])

        team_chip(canvas, us["abbr"][:4], hexc(self.cfg["primary"]),
                  hexc(self.cfg["secondary"]), 0, 26)
        team_chip(canvas, them["abbr"][:4], opp_prim, opp_sec, 37, 63)
        vs = "VS" if us["home"] else "@"
        draw(canvas, F3, vs, 32 - width(F3, vs) // 2, 2, DIM)

        if kind in ("live", "final"):
            big_score(canvas, us["score"] or "0", left=True)
            big_score(canvas, them["score"] or "0", left=False)
            if kind == "live":
                if now.timestamp() % 1.2 < 0.6:          # blinking red dot
                    fill(canvas, 2, 27, 2, 2, RED)
                bottom(canvas, [("LIVE ", RED), (game["detail"], WHITE)], t, x0=6)
            else:
                bottom(canvas, [("FINAL", DIM)], t)
        else:
            start = game["date"].astimezone(HOME_TZ)
            if game["time_valid"]:
                big_clock(canvas, start, WHITE)
            else:
                draw(canvas, F5, "TBD", 32 - width(F5, "TBD", 2) // 2, 10, WHITE, 2)
            if start.date() == now.astimezone(HOME_TZ).date():
                label = [("TODAY", CYAN)]
            else:
                label = [(start.strftime("%a %b ").upper() + str(start.day), DIM)]
            bottom(canvas, label, t)


class ItfdbFlash(Page):
    """Full-screen takeover the moment a Dodgers game starts (old clock's look)."""

    def is_active(self, now):
        return sports.itfdb_active()

    def draw(self, canvas, now, t):
        flip = (now.timestamp() % 0.5) < 0.25
        c1, c2 = (DODGER, WHITE) if flip else (WHITE, DODGER)
        fill(canvas, 0, 0, 64, 1, c1)       # border
        fill(canvas, 0, 31, 64, 1, c1)
        fill(canvas, 0, 0, 1, 32, c1)
        fill(canvas, 63, 0, 1, 32, c1)
        fill(canvas, 1, 1, 62, 1, c1)       # inner rails, top and bottom
        fill(canvas, 1, 30, 62, 1, c1)
        s = "ITFDB!!!"
        draw(canvas, F5, s, 32 - width(F5, s) // 2, 12, c2)
