"""
BILLY5000 start-up screen: plays once, the moment the clock launches (about 8 s).

  0.0 - 3.0 s  boot check, typed out like an ELFNET terminal:
                 BOOTING...
                 CLOCK        OK
                 17 PLACES    OK      <- real counts from settings.py
                 10 TEAMS     OK
  3.0 - 3.2 s  white flash
  3.2 - 8.0 s  BILLY5000 logo: letters stamp in one at a time, a shine sweeps
               across, a rule line grows out from the middle, WORLD CLOCK V1 types in

Turn it off with STARTUP_SPLASH = False in settings.py.
"""
import time

import settings
from engine import santa
from engine.bitfonts import F3
from engine.specialdays import Frame
from engine.teamcolors import mix
from .base import Page

SECONDS = 8.0
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


def _boot(f, t):
    places = len(settings.PLACES) + 1
    checks = [(f"CLOCK", 0.4, 0.9),
              (f"{places} PLACES", 1.1, 1.8),
              (f"{len(settings.TEAMS)} TEAMS" if settings.SPORTS_ON else "WEATHER", 2.0, 2.6)]
    dots = "." * (int(t / 0.3) % 4) if t > 0.5 else ""
    _type(f, 0, AMBER, "BOOTING" + dots, t, 0.0)
    for row, (label, start, ok_at) in enumerate(checks, start=1):
        _type(f, row, WHITE, label, t, start)
        if t >= ok_at:
            _text(f, santa.small(), 53, ROWS[row], GREEN, "OK")


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
        x0 = 32 - Frame.width(F3, sub) // 2
        f.text(F3, sub[:n], x0, 24, GOLD)


def draw_splash(canvas, t):
    f = _Frame()
    if t < 3.0:
        _boot(f, t)
    elif t < 3.2:
        f.bg = (255, 255, 255) if t < 3.08 else (90, 90, 90)
    else:
        _logo(f, t - 3.2)
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
        if time.monotonic() - self.started >= SECONDS:
            self.done = True
            return False
        return True

    def draw(self, canvas, now, t):
        draw_splash(canvas, time.monotonic() - self.started)
