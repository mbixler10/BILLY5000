"""
BILLY5000 start-up screen: plays once, the moment the clock launches (about 26 s).

  POWER-ON      the panel snaps on like an old CRT - a bright line, it opens up,
                static fizzles out
  SYSTEM CHECK  diagnostics scroll past (power bus, panel, Billy's Buds, sat uplink,
                NOAA, ESPN, each team with a check in its own color, ITFDB, ELFNET...);
                about half a second per line so you can read them; progress bar to 100%
  ALL SYSTEMS GO
  white flash
  BILLY5000 logo: letters stamp in, shine sweeps across, rule line grows,
                WORLD CLOCK + version types in, then holds

Speed: STARTUP_PACE in settings.py (1.0 = easy to read, 0.5 = quick, 1.5 = slower).
Turn it off with STARTUP_SPLASH = False.
"""
import time

import settings
from engine import santa
from engine.bitfonts import F3, F3_NARROW, F5
from engine.specialdays import Frame
from engine.teamcolors import mix, hexc
from .base import Page

AMBER = (255, 140, 0)
GREEN = (0, 255, 60)
WHITE = (242, 242, 242)
GOLD = (255, 176, 0)
RULE = (120, 80, 0)
LOGO = "BILLY5000"
ROWS = [7, 15, 23, 31]          # 5x7 text baselines, same grid as the Santa screens


class _Frame(Frame):
    """The old clock's Frame, taught the two calls the font code uses."""
    def SetPixel(self, x, y, r, g, b):
        self.set(x, y, (r, g, b))


def _text(f, font, x, y, rgb, s):
    return santa.graphics.DrawText(f, font, x, y, santa.graphics.Color(*rgb), s)


def _width(font, s):
    return sum(font.glyphs.get(ch, font.glyphs["?"])[0] for ch in s)


def _type(f, row, rgb, s, t, start, cps=16):
    """Teletype: reveal one character at a time with a block cursor."""
    if t < start:
        return
    n = min(len(s), int((t - start) * cps))
    _text(f, santa.small(), 1, ROWS[row], rgb, s[:n])
    if n < len(s) and int(t / 0.08) % 2 == 0:
        f.fill(1 + n * 5, ROWS[row] - 6, 4 + n * 5, ROWS[row], rgb)


CYAN = (64, 208, 255)
RED = (255, 48, 48)
DIM = (90, 90, 90)
ROW_SECONDS = 0.55      # how long each system-check line gets (at STARTUP_PACE 1.0)
FLASH = 0.2


def _pace():
    return max(0.3, float(getattr(settings, "STARTUP_PACE", 1.0)))


def timeline():
    """(power-on end, check end, GO end, logo seconds, total) for the current pace."""
    pace = _pace()
    _, raw = _checks()
    power = 1.2 * pace
    check_end = power + raw * (ROW_SECONDS / 0.24) * pace + 0.6 * pace
    go_end = check_end + 1.6 * pace
    logo = 7.5 * pace
    return power, check_end, go_end, logo, go_end + FLASH + logo


def _noise(f, seed, density, top=0, bottom=31, level=1.0):
    import random as _r
    rng = _r.Random(seed)
    for _ in range(int(64 * (bottom - top + 1) * density)):
        v = int(rng.randint(60, 255) * level)
        f.set(rng.randrange(64), rng.randint(top, bottom), (v, v, v))


def _power_on(f, t):
    """Old-CRT turn-on: a hot line stretches out, the picture opens up, static fades."""
    if t < 0.22:                                   # the line grows from the middle
        half = int(32 * t / 0.22)
        f.fill(32 - half, 15, 31 + half, 16, (255, 255, 255))
    elif t < 0.45:                                 # ...and opens up top and bottom
        p = (t - 0.22) / 0.23
        h = max(1, int(16 * p))
        f.fill(0, 16 - h, 63, 15 + h, (40, 40, 48))
        f.fill(0, 15, 63, 16, (255, 255, 255))
        _noise(f, int(t * 40), 0.12, 16 - h, 15 + h)
    else:                                          # static fizzles out
        _noise(f, int(t * 40), 0.35 * (1 - (t - 0.45) / 0.35), level=0.8)


LEAGUES = {"baseball/mlb": "MLB", "football/nfl": "NFL", "hockey/nhl": "NHL",
           "football/college-football": "NCAAF", "basketball/mens-college-basketball": "NCAAB"}
SHORT_NAMES = {}


def _led_bright(c, floor=170):
    """Team primary, brightened (same hue) so dark navies still glow on the LEDs."""
    m = max(c)
    if m >= floor:
        return c
    k = floor / max(m, 1)
    return tuple(min(255, int(v * k)) for v in c)


def _team_rows():
    rows = []
    chants = getattr(settings, "STARTUP_CHANTS", {})
    for cfg in settings.TEAMS:
        color = cfg["secondary"] if cfg.get("check") == "secondary" else cfg["primary"]
        color = _led_bright(hexc(color))
        if cfg["name"] in chants:
            tag, cry = chants[cfg["name"]]
            rows.append((tag, cry.upper(), color, 0.1, "chant"))
            continue
        lg = LEAGUES.get(cfg["league"], "")
        name = SHORT_NAMES.get(cfg["name"], cfg["name"])
        label = f"{lg} {name}".strip()
        if Frame.width(F3, label) > 50:              # too long for the row: drop the league
            label = name
        rows.append((label, "CHECK", color, 0, ""))
    return rows


MEMTEST = 0.7      # raw seconds of RAM test before the first line


def _checks():
    flags = len(getattr(settings, "FLAG_QUIZ_COUNTRIES", [])) + 36
    rows = [
        ("POWER BUS", "OK", GREEN, 0, ""),
        ("PANEL 64X32", "OK", GREEN, 0, ""),
        ("FONT ROM", "OK", GREEN, 0, ""),
        ("CLOCK SYNC", "TIME", GREEN, 0.35, "clock"),     # shows the real time
        ("BILLY'S BUDS", "BUDS", GREEN, 0.45, "buds"),    # counts the family cities
        ("SAT UPLINK", "LOCK", CYAN, 0.55, "sats"),       # hunting for satellites
        ("NOAA FEED", "OK", GREEN, 0, ""),
        ("ESPN FEED", "OK", GREEN, 0.5, "retry"),         # one RETRY, then OK
    ] + _team_rows() + [
        ("ITFDB", "ARMED", RED, 0, ""),
        ("SHIP BELL", "OK", GREEN, 0, ""),
        (f"{flags} FLAGS", "OK", GREEN, 0, ""),
        ("ELFNET", "SECURE", AMBER, 0.6, "stall"),        # the bar stalls at 90% for this one
    ]
    out, at = [], MEMTEST
    for label, status, color, wait, kind in rows:
        out.append((label, status, color, at, at + 0.14 + wait, kind))
        at += 0.24 + wait
    return out, at


CHECKMARK = ["....#", "...#.", "#.#..", ".#..."]


def _buds():
    return len(settings.PLACES) + 1


def _status_text(status, kind):
    if kind == "clock":
        from datetime import datetime
        n = datetime.now()
        return f"{n.hour % 12 or 12}:{n.minute:02d}"
    if kind == "buds":
        return f"{_buds()}/{_buds()}"
    return status


def _spinner(f, x, y, t, color):
    k = int(t * 12) % 4
    for dx, dy in [[(0, 2), (1, 2), (2, 2)], [(0, 1), (1, 2), (2, 3)],
                   [(1, 1), (1, 2), (1, 3)], [(2, 1), (1, 2), (0, 3)]][k]:
        f.set(x + dx, y + dy, color)


def _system_check(f, t):
    rows, total = _checks()
    power, check_end, _, _, _ = timeline()
    scale = (check_end - power - 0.6 * _pace()) / total  # half a second a line, then hold at 100%
    shown = [r for r in rows if t >= r[3] * scale]
    done = sum(1 for r in rows if t >= r[4] * scale)
    pct = min(100, int(100 * done / len(rows)))
    if done < len(rows):
        pct = min(pct, 90)                                # the classic stall near the end

    # header: RAM test first (fast hex count), then system name, spinner, percent
    mem_end = MEMTEST * scale
    if t < mem_end:
        addr = min(0xFFFF, int(0xFFFF * t / mem_end))
        f.text(F3, "RAM TEST", 1, 0, AMBER)
        h = f"{addr:04X}"
        f.text(F3, h, 62 - Frame.width(F3, h), 0, WHITE if t < mem_end * 0.9 else GREEN)
        for i in range(3):                                # memory blocks filling in below
            y = 9 + i * 6
            cells = int(min(1.0, max(0.0, t / mem_end * 3 - i)) * 15)
            for c in range(15):
                col = (0, 120, 40) if c < cells else (25, 25, 30)
                f.fill(2 + c * 4, y, 4 + c * 4, y + 3, col)
    else:
        f.text(F3, "SYS CHECK", 1, 0, AMBER)
        if pct < 100:
            _spinner(f, 39, 0, t, AMBER)
        p = f"{pct}%"
        f.text(F3, p, 62 - Frame.width(F3, p), 0, WHITE if pct < 100 else GREEN)
    f.fill(0, 6, 63, 6, (40, 30, 0))

    # log: last 3 lines, newest at the bottom
    for i, (label, status, color, start, ok_at, kind) in enumerate(shown[-3:]):
        y = 8 + i * 6
        f.text(F3, label, 1, y, WHITE)
        lx = 1 + Frame.width(F3, label) + 2
        if t >= ok_at * scale:                            # result types in
            if status == "CHECK":
                sx = 58
                for r, row in enumerate(CHECKMARK):
                    for q, ch in enumerate(row):
                        if ch == "#":
                            f.set(sx + q, y + r, color)
            else:
                full = _status_text(status, kind)
                n = 1 + int((t - ok_at * scale) * 18)
                font = F3 if lx + Frame.width(F3, full) + 2 <= 62 else F3_NARROW
                sx = 62 - Frame.width(font, full)
                f.text(font, full[:n], sx, y, color)
        else:                                             # still working on it
            work = (t - start * scale) / max(0.01, (ok_at - start) * scale)
            sx = 56
            if kind == "sats":
                s_ = f"{min(12, 1 + int(work * 12))}/12"
                sx = 62 - Frame.width(F3_NARROW, s_)
                f.text(F3_NARROW, s_, sx, y, DIM)
            elif kind == "buds":
                s_ = f"{max(1, int(work * _buds()))}"
                sx = 62 - Frame.width(F3, s_)
                f.text(F3, s_, sx, y, DIM)
            elif kind == "retry" and 0.3 < work < 0.75:
                sx = 62 - Frame.width(F3, "RETRY")
                if int(t * 6) % 2 == 0:
                    f.text(F3, "RETRY", sx, y, AMBER)
            else:
                _spinner(f, 59, y, t, DIM)
                sx = 58
        for x in range(lx, sx - 2, 2):                    # leader dots
            f.set(x, y + 4, DIM)

    # progress bar
    f.fill(0, 27, 63, 31, (25, 25, 30))
    fill = int(62 * pct / 100)
    if fill:
        f.fill(1, 28, fill, 30, GREEN if pct == 100 else CYAN)


def _all_systems_go(f, t):
    on = int(t / 0.12) % 2 == 0
    edge = GREEN if on else (0, 90, 25)
    f.fill(0, 0, 63, 0, edge); f.fill(0, 31, 63, 31, edge)
    f.fill(0, 0, 0, 31, edge); f.fill(63, 0, 63, 31, edge)
    s = "ALL SYSTEMS"
    f.text(F3, s, 32 - Frame.width(F3, s) // 2, 4, WHITE)
    go_w = Frame.width(F5, "GO", 2)
    f.text(F5, "GO", 32 - go_w // 2, 12, GREEN if on or t > 0.5 else (0, 140, 40), 2)


def _boot(f, t):
    power, check_end, _, _, _ = timeline()
    if t < power:
        _power_on(f, t * 0.8 / power)          # same CRT turn-on, played slower
    elif t < check_end:
        _system_check(f, t - power)
    else:
        _all_systems_go(f, t - check_end)


def _logo(f, t):
    big = santa.big()
    x = (64 - _width(big, LOGO)) // 2
    for i, ch in enumerate(LOGO):
        appear = i * 0.1
        w = _width(big, ch)
        if t >= appear:
            color = WHITE if ch.isalpha() else GOLD
            if t - appear < 0.15:            # each letter stamps in bright white
                color = (255, 255, 255)
            _text(f, big, x, 18, color, ch)
        x += w

    # shine: a bright diagonal band sweeps across the logo once
    sheen_t = t - 1.1
    if 0 <= sheen_t < 0.7:
        sx = -8 + sheen_t / 0.7 * 80
        for (px, py), c in list(f.px.items()):
            if abs(px - sx - (py - 12) * 0.6) < 2.5:
                f.px[(px, py)] = mix(c, (255, 255, 255), 0.8)

    # rule line grows out from the middle
    if t > 1.2:
        half = min(31, int((t - 1.2) / 0.5 * 31))
        f.fill(32 - half, 21, 31 + half, 21, RULE)

    # subtitle types in
    if t > 1.7:
        sub = f"WORLD CLOCK {settings.VERSION}".strip()
        n = min(len(sub), int((t - 1.7) * 14))
        font = F3 if Frame.width(F3, sub) <= 63 else F3_NARROW   # long versions use the slimmer font
        x0 = 32 - Frame.width(font, sub) // 2
        f.text(font, sub[:n], x0, 24, GOLD)


def draw_splash(canvas, t):
    f = _Frame()
    _, _, go_end, logo, _ = timeline()
    if t < go_end:
        _boot(f, t)
    elif t < go_end + FLASH:
        f.bg = (255, 255, 255) if t < go_end + 0.08 else (90, 90, 90)
    else:
        _logo(f, (t - go_end - FLASH) * 4.8 / logo)   # same logo animation, stretched out
    f.flush(canvas)


class StartupSplash(Page):
    def __init__(self):
        self.started = None
        self.done = not settings.STARTUP_SPLASH

    def is_active(self, now):
        if self.done:
            return False
        if self.started is None:
            self.started = time.monotonic()
        if time.monotonic() - self.started >= timeline()[4]:
            self.done = True
            return False
        return True

    def draw(self, canvas, now, t):
        draw_splash(canvas, time.monotonic() - self.started)
