"""
Lighthouse lesson: night navigation for Billy.

A lighthouse stands on its rock at night and blinks its REAL pattern, in real
time. Beside it: its name, its chart code (FL(2) W 20S...), and a timeline bar
that shows one full cycle with a marker riding along so Billy can see the
pattern coming. A ticker along the bottom says where it is and explains the
pattern in plain words.

Once per lap, at a random spot in the lap, a random lighthouse (no repeats
until every lighthouse has had its turn).
"""
import math
import random

import settings
from engine.bitfonts import F3
from engine.lighthouses import LIGHTHOUSES, LIGHT_RGB, STATES
from engine.specialdays import Frame
from engine.teamcolors import mix
from .base import Page

SKY_TOP = (2, 4, 18)
SKY_LOW = (10, 16, 44)
SEA = (4, 14, 40)
ROCK = (46, 44, 50)
TOWER_W = (210, 210, 205)
BLACK = (72, 72, 84)        # LED 'black' - still readable against the night sky
RED = (190, 30, 24)
BROWN = (120, 70, 36)
BRICK = (150, 64, 40)
LANTERN_DARK = (50, 50, 40)
NAVY = (8, 22, 52)
WHITE = (242, 242, 242)
GREY = (122, 122, 122)
AMBER = (255, 176, 0)
BAR_DARK = (34, 34, 52)
TOWN = (160, 170, 190)

TX = 17                     # text column starts here
TICKER_PX_PER_SEC = 16
TICKER_HOLD = 1.5

STARS = [(20, 6), (27, 2), (35, 9), (44, 3), (52, 8), (60, 1), (3, 2), (14, 1), (57, 15), (40, 14),
         (31, 16), (22, 12), (62, 11), (48, 18)]

CX = 7                      # tower center column
TOWER_TOP, TOWER_BOT = 9, 23


def _tower_color(style, x, y):
    """Paint scheme of the tower at pixel (x, y)."""
    rel = y - TOWER_TOP
    if style == "spiral":                               # Cape Hatteras, St. Augustine
        return BLACK if ((x - CX) + y) // 3 % 2 == 0 else TOWER_W
    if style == "bands":                                # Bodie Island, Fire Island
        return BLACK if rel // 3 % 2 == 0 else TOWER_W
    if style == "checker":                              # Cape Lookout diamonds / Cape Henry
        return BLACK if ((x - CX) // 2 + rel // 3) % 2 == 0 else TOWER_W
    if style == "redwhite":                             # West Quoddy, Assateague
        return RED if rel // 3 % 2 == 0 else TOWER_W
    if style == "brick":
        return BRICK
    if style == "red":
        return RED
    if style == "redtop":                               # Nauset, Barnegat
        return RED if rel < 7 else TOWER_W
    if style == "blacktop":                             # Tybee, Cape Disappointment
        return BLACK if rel < 4 or rel > 11 else TOWER_W
    if style == "redband":                              # Sankaty Head
        return RED if 5 <= rel <= 8 else TOWER_W
    if style == "brownband":                            # Montauk, Execution Rocks
        return BROWN if 5 <= rel <= 8 else TOWER_W
    if style == "brownbottom":                          # Point Judith
        return BROWN if rel > 7 else TOWER_W
    return TOWER_W


def _build_scene(style, lit):
    """Everything that doesn't move: sky, calm sea, beams, rocks, tower, lantern,
    glow, and the shading behind the words. Built once per tower + light color."""
    f = Frame()

    for y in range(0, 26):                              # night sky gradient
        c = mix(SKY_TOP, SKY_LOW, y / 25)
        for x in range(64):
            f.set(x, y, c)
    for y in range(22, 26):                             # calm sea (waves are added per frame)
        for x in range(64):
            f.set(x, y, SEA)

    if lit:                                             # beams sweep out both ways from the lantern
        for x in range(64):
            d = abs(x - CX)
            if d < 2:
                continue
            a = max(0.0, 0.85 - d / 55)
            if x >= TX - 1:
                a = min(a, 0.22)                       # keep the words readable
            for y, k in ((5, 0.6), (6, 1.0), (7, 0.6)):
                f.blend(x, y, lit, min(1.0, a * k))
            spread = d // 12
            for s in range(1, spread + 1):
                f.blend(x, 6 - 1 - s, lit, a * 0.3)
                f.blend(x, 6 + 1 + s, lit, a * 0.3)

    for x, y in ((3, 23), (4, 22), (5, 22), (9, 22), (10, 22), (11, 23), (12, 24), (2, 24), (3, 24),
                 (4, 23), (5, 23), (6, 23), (7, 23), (8, 23), (9, 23), (10, 23), (11, 24), (4, 24),
                 (5, 24), (6, 24), (7, 24), (8, 24), (9, 24), (10, 24), (13, 25), (1, 25)):
        f.set(x, y, ROCK)                               # the rock it stands on

    for y in range(TOWER_TOP, TOWER_BOT):               # tapered tower
        half = 1 + (y - TOWER_TOP) * 3 // (TOWER_BOT - TOWER_TOP)
        for x in range(CX - half, CX + half + 1):
            f.set(x, y, _tower_color(style, x, y))
    for x in range(CX - 3, CX + 4):                     # gallery walkway
        f.set(x, 8, BLACK)
    for x in (CX - 3, CX + 3):
        f.set(x, 7, BLACK)
    for y in (5, 6, 7):                                 # lantern room
        for x in range(CX - 1, CX + 2):
            f.set(x, y, lit or LANTERN_DARK)
    for x in range(CX - 2, CX + 3):                     # roof
        f.set(x, 4, RED if style in ("spiral", "redtop") else BLACK)
    for x in range(CX - 1, CX + 2):
        f.set(x, 3, RED if style in ("spiral", "redtop") else BLACK)
    f.set(CX, 2, BLACK)
    if lit:                                             # glow around the lantern
        for dy in range(-3, 4):
            for dx in range(-3, 4):
                d = math.hypot(dx, dy)
                if 1.4 < d < 3.6:
                    f.blend(CX + dx, 6 + dy, lit, 0.7 * (1 - d / 3.6))
    for x in range(TX - 1, 64):                         # darken behind the words a little
        for y in range(0, 22):
            f.blend(x, y, (0, 0, 0), 0.25)
    open_sea = [(x, y) for y in range(22, 26) for x in range(64) if f.px.get((x, y)) == SEA]
    return f.px, open_sea


_SCENES = {}
WAVE = mix(SEA, (40, 70, 120), 0.6)


def draw_scene(f, light, style, t):
    """The cached still scene, plus the moving bits: twinkling stars, waves,
    and the light's reflection on the water."""
    color = light.color_at(t)
    lit = LIGHT_RGB[color] if color else None
    key = (style, lit)
    if key not in _SCENES:
        _SCENES[key] = _build_scene(style, lit)
    px, open_sea = _SCENES[key]
    f.px = dict(px)
    for i, (x, y) in enumerate(STARS):                  # twinkling stars
        a = 0.35 + 0.35 * (0.5 + 0.5 * math.sin(t * 1.7 + i * 2.1))
        f.blend(x, y, (255, 255, 255), a * (0.75 if x >= TX - 1 and y < 22 else 1.0))
    step = int(t * 3)
    glint = int(t * 5)
    for x, y in open_sea:                               # little waves, and the light on the water
        if (x + step + y * 3) % 9 == 0:
            f.px[(x, y)] = WAVE
        if lit and y in (22, 23) and y == 22 + (x % 2) and (x + glint) % 3 == 0:
            f.blend(x, y, lit, max(0.0, 0.5 - abs(x - CX) / 40))


def _wrap(name, max_w):
    """Name on one or two lines; a line still too wide gets a marquee."""
    if Frame.width(F3, name) <= max_w:
        return [name]
    words = name.split()
    best = None
    for i in range(1, len(words)):
        a, b = " ".join(words[:i]), " ".join(words[i:])
        w = max(Frame.width(F3, a), Frame.width(F3, b))
        if best is None or w < best[0]:
            best = (w, [a, b])
    return best[1] if best else [name]


def _line(f, s, y, c, t):
    max_w = 63 - TX
    w = Frame.width(F3, s)
    f.clip = (TX, 63)
    if w <= max_w:
        f.text(F3, s, TX, y, c)
    else:
        period = w + 12
        off = int(max(0.0, t - TICKER_HOLD) * TICKER_PX_PER_SEC * 0.75) % period
        for x in (TX - off, TX - off + period):
            f.text(F3, s, x, y, c)
    f.clip = (0, 63)


def ticker_text(row):
    name, town, st, light, _ = row
    return "%s LIGHT - %s, %s - %s" % (name, town, STATES.get(st, st), light.words)


def page_seconds(row):
    light = row[3]
    w = Frame.width(F3, ticker_text(row))
    ticker = TICKER_HOLD + (w + 64) / TICKER_PX_PER_SEC + 0.5
    # at least one full blink cycle, plus the first flash coming around again
    cycles = 0 if light.retired or light.period <= 1 else min(2 * light.period, light.period + 10)
    # any name / town / code line too wide to fit gets one full pass of its marquee
    name, town, st = row[0], row[1], row[2]
    lines = _wrap(name, 63 - TX) + ([] if len(_wrap(name, 63 - TX)) > 1 else ["%s, %s" % (town, st)])
    lines.append(light.code)
    side = max((TICKER_HOLD + (Frame.width(F3, s) + 12) / (TICKER_PX_PER_SEC * 0.75) + 0.5
                for s in lines if Frame.width(F3, s) > 63 - TX), default=0)
    return max(settings.LIGHTHOUSE_MIN_SECONDS, ticker, cycles, side)


_BARS = {}


def draw_lighthouse(canvas, row, t):
    name, town, st, light, style = row
    f = Frame()
    draw_scene(f, light, style, t)

    lines = _wrap(name, 63 - TX)
    for i, s in enumerate(lines[:2]):
        _line(f, s, 1 + i * 6, WHITE, t)
    if len(lines) == 1:                                 # room for the town on line two
        _line(f, "%s, %s" % (town, st), 7, TOWN, t)

    if light.retired:
        f.text(F3, "RETIRED", TX, 13, GREY)
        f.text(F3, "IN %d" % light.retired, TX, 19, GREY)
    else:
        _line(f, light.code, 13, AMBER, t)
        # timeline: one full cycle across the bar, marker shows "now"
        x0, x1 = TX, 62
        span = x1 - x0 + 1
        per = light.period if light.period > 1 else 1
        bar = _BARS.get(id(light))
        if bar is None:                                 # the bar never changes: work it out once
            bar = []
            for i in range(span):
                c = light.color_at((i + 0.5) / span * per)
                bar.append(mix(LIGHT_RGB[c], (0, 0, 0), 0.15) if c else BAR_DARK)
            _BARS[id(light)] = bar
        for i, col in enumerate(bar):
            f.px[(x0 + i, 19)] = col
            f.px[(x0 + i, 20)] = col
        if light.period > 1:
            mx = x0 + int((t % per) / per * span)
            f.set(min(mx, x1), 18, WHITE)
            f.set(min(mx, x1), 21, WHITE)

    f.fill(0, 26, 63, 31, NAVY)                         # ticker: where it is + what it does
    msg = ticker_text(row)
    w = Frame.width(F3, msg)
    period = w + 24
    off = int(max(0.0, t - TICKER_HOLD) * TICKER_PX_PER_SEC) % period
    for x in (64 - 2 - off, 64 - 2 - off + period):
        f.text(F3, msg, x, 27, AMBER)
    f.flush(canvas)


# ------------------------------------------------------------------ placement
class _Picker:
    """Shared by the lap marker and the slots: which slot gets the lighthouse
    this lap, and which lighthouse it is."""

    def __init__(self):
        self.slots = 0
        self.pick = -1
        self.deck = []
        self.row = None
        self.lap = 0            # laps since start-up (other once-in-a-while pages use this too)

    def new_lap(self):
        self.lap += 1
        self.pick = random.randrange(self.slots) if self.slots else -1

    def next_row(self):
        if not self.deck:
            names = settings.LIGHTHOUSE_LIST or [r[0] for r in LIGHTHOUSES]
            self.deck = [r for r in LIGHTHOUSES if r[0] in names]
            random.shuffle(self.deck)
            if len(self.deck) > 1 and self.deck[-1] is self.row:
                self.deck[0], self.deck[-1] = self.deck[-1], self.deck[0]
        self.row = self.deck.pop() if self.deck else None
        return self.row


PICKER = _Picker()


class LapStart(Page):
    """Invisible: sits first in the lap and rolls where the lighthouse goes."""

    def is_active(self, now):
        PICKER.new_lap()
        from .home import GATE
        GATE.new_lap()
        return False

    def draw(self, canvas, now, t):
        pass


class LighthouseSlot(Page):
    def __init__(self):
        self.i = PICKER.slots
        PICKER.slots += 1
        self.row = None

    @property
    def seconds(self):
        return page_seconds(self.row) if self.row else 1

    def is_active(self, now):
        if not settings.LIGHTHOUSE_LESSON_ON or PICKER.pick != self.i:
            return False
        self.row = PICKER.next_row()
        return self.row is not None

    def draw(self, canvas, now, t):
        draw_lighthouse(canvas, self.row, t)
