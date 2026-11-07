"""
Flag quiz: a flag fills the panel, a pause to guess, then the name is revealed.
One flag per lap, right after the sports block. Every round of flags is a fresh
random order (no repeats until all have shown), so there's no sequence to memorize.

Reveal styles (settings.FLAG_REVEAL_STYLE):
  "plate"   a black name plate with a gold edge slides up over the bottom of the flag
  "box"     the flag dims and a framed box drops in over the middle with the name
  "corner"  the flag shrinks to a small picture at the top, name big underneath
  "stamp"   a white box with a red border stamps on with a flash, "IT'S" + the name
"""
import random

import settings
from engine.bitfonts import F3, F5
from engine.flags import FLAGS
from engine.nautical import SIGNALS, draw_signal
from engine.specialdays import Frame
from engine.teamcolors import mix
from .base import Page

GOLD = (255, 176, 0)
WHITE = (242, 242, 242)
GREY = (122, 122, 122)
SLIDE = 0.4                     # seconds for the reveal animation


def name_lines(name, max_w):
    """Fit a name: one big line, else two big lines, else small (wrapped)."""
    if Frame.width(F5, name) <= max_w:
        return F5, [name]
    words = name.split()
    if len(words) > 1:
        best = None
        for i in range(1, len(words)):
            a, b = " ".join(words[:i]), " ".join(words[i:])
            w = max(Frame.width(F5, a), Frame.width(F5, b))
            if w <= max_w and (best is None or w < best[0]):
                best = (w, [a, b])
        if best:
            return F5, best[1]
    if Frame.width(F3, name) <= max_w:
        return F3, [name]
    half = len(words) // 2 or 1
    return F3, [" ".join(words[:half]), " ".join(words[half:])]


def lines_height(font, lines):
    h = 7 if font is F5 else 5
    return len(lines) * h + (len(lines) - 1) * 2


def draw_lines(f, font, lines, top, color, cx=32):
    h = 7 if font is F5 else 5
    for i, s in enumerate(lines):
        f.text(font, s, cx - Frame.width(font, s) // 2, top + i * (h + 2), color)


def flag_frame(name):
    f = Frame()
    FLAGS[name](f)
    return f


def _ease(p):
    p = max(0.0, min(1.0, p))
    return 1 - (1 - p) ** 3


# ------------------------------------------------------------------ reveal styles
def reveal_plate(f, name, t):
    font, lines = name_lines(name, 60)
    ph = lines_height(font, lines) + 6
    y0 = 32 - int(round(ph * _ease(t / SLIDE)))
    f.fill(0, y0, 63, 31, (0, 0, 0))
    f.fill(0, y0, 63, y0, GOLD)
    draw_lines(f, font, lines, y0 + 4, WHITE)


def reveal_box(f, name, t):
    k = 1 - 0.65 * _ease(t / SLIDE)                    # dim the flag
    for xy, c in list(f.px.items()):
        f.px[xy] = tuple(int(v * k) for v in c)
    font, lines = name_lines(name, 54)
    bw = max(Frame.width(font, s) for s in lines) + 8
    bh = lines_height(font, lines) + 8
    x0, y0 = 32 - bw // 2, 16 - bh // 2
    drop = int((1 - _ease(t / SLIDE)) * -(y0 + bh))     # drops in from the top
    y0 += drop
    f.fill(x0, y0, x0 + bw - 1, y0 + bh - 1, (0, 0, 0))
    for x in range(x0, x0 + bw):
        f.set(x, y0, WHITE); f.set(x, y0 + bh - 1, WHITE)
    for y in range(y0, y0 + bh):
        f.set(x0, y, WHITE); f.set(x0 + bw - 1, y, WHITE)
    draw_lines(f, font, lines, y0 + 4, WHITE)


def reveal_corner(f, name, t):
    big = dict(f.px)
    f.px.clear()
    p = _ease(t / SLIDE)
    s = 1 - 0.5 * p                                     # shrink 100% -> 50%
    w, h = int(64 * s), int(32 * s)
    ox = (64 - w) // 2
    for y in range(h):
        for x in range(w):
            c = big.get((int(x / s), int(y / s)))
            if c:
                f.set(ox + x, y, c)
    if p >= 1:
        font, lines = name_lines(name, 62)
        top = 17 + (15 - lines_height(font, lines)) // 2
        draw_lines(f, font, lines, top, WHITE)


def reveal_stamp(f, name, t):
    font, lines = name_lines(name, 54)
    bw = max(max(Frame.width(font, s) for s in lines), Frame.width(F3, "IT'S")) + 8
    bh = lines_height(font, lines) + 15
    x0, y0 = 32 - bw // 2, 16 - bh // 2
    if t < 0.12:                                        # the thump
        f.fill(0, 0, 63, 31, (255, 255, 255))
        return
    red = (220, 30, 40)
    f.fill(x0, y0, x0 + bw - 1, y0 + bh - 1, (255, 255, 255))
    for i in (0, 1):
        for x in range(x0 + i, x0 + bw - i):
            f.set(x, y0 + i, red); f.set(x, y0 + bh - 1 - i, red)
        for y in range(y0 + i, y0 + bh - i):
            f.set(x0 + i, y, red); f.set(x0 + bw - 1 - i, y, red)
    f.text(F3, "IT'S", 32 - Frame.width(F3, "IT'S") // 2, y0 + 4, red)
    draw_lines(f, font, lines, y0 + 11, (20, 20, 20))


REVEALS = {"plate": reveal_plate, "box": reveal_box, "corner": reveal_corner, "stamp": reveal_stamp}


# ------------------------------------------------------------------ nautical signal flags
NAVY = (8, 22, 52)
OUTLINE = (70, 70, 80)
AMBER = (255, 176, 0)
TICKER_PX_PER_SEC = 18
TICKER_HOLD = 1.0


def is_signal(name):
    return name.startswith("SIGNAL ")


def meaning_seconds(letter):
    """Reveal time for a signal flag: long enough for the meaning to scroll past once."""
    w = Frame.width(F3, SIGNALS[letter][1])
    if w <= 60:
        return settings.FLAG_REVEAL_SECONDS
    return max(settings.FLAG_REVEAL_SECONDS, TICKER_HOLD + (w + 64) / TICKER_PX_PER_SEC + 1)


def draw_signal_quiz(canvas, letter, t):
    """
    Signal flags are a lesson, not a quiz: everything shows right away.
        [flag]  B          <- big letter
                BRAVO
        I AM TAKING IN, DISCHARGING...   <- meaning ticker
    """
    f = Frame()
    draw_signal(f, letter, 2, 1, 24)
    # faint outline so black parts (Lima, Zulu, 6, 9) don't vanish on the dark panel
    shape = set(f.px)
    for (x, y) in shape:
        for nx, ny in ((x + 1, y), (x - 1, y), (x, y + 1), (x, y - 1)):
            if (nx, ny) not in shape and 0 <= nx < 64 and 0 <= ny < 26:
                f.set(nx, ny, OUTLINE)
    name, meaning = SIGNALS[letter]
    x = 33 if letter.isdigit() else 31                 # pennants are a little longer
    f.text(F5, letter, x, 1, AMBER, 2)
    f.text(F3, name, x, 18, WHITE)
    f.fill(0, 26, 63, 31, NAVY)
    w = Frame.width(F3, meaning)
    if w <= 60:
        f.text(F3, meaning, 32 - w // 2, 27, AMBER)
    else:
        period = w + 24
        off = int(max(0.0, t - TICKER_HOLD) * TICKER_PX_PER_SEC) % period
        for x in (2 - off, 2 - off + period):
            f.text(F3, meaning, x, 27, AMBER)
    f.flush(canvas)


def draw_quiz(canvas, name, t, style=None):
    """Guess phase (flag only), then the reveal. t = seconds into the page."""
    if is_signal(name):
        draw_signal_quiz(canvas, name[-1], t)
        return
    f = flag_frame(name)
    guess = settings.FLAG_GUESS_SECONDS
    if t >= guess:
        REVEALS[style or settings.FLAG_REVEAL_STYLE](f, name, t - guess)
    elif settings.FLAG_COUNTDOWN_BAR:
        left = int(64 * (1 - t / guess))                # thin timer line along the bottom
        for x in range(64):
            c = f.px.get((x, 31), f.bg or (0, 0, 0))
            f.set(x, 31, mix(c, (255, 255, 255), 0.7) if x < left else mix(c, (0, 0, 0), 0.6))
    f.flush(canvas)


class FlagQuiz(Page):
    def __init__(self):
        self.deck = []
        self.name = None

    @property
    def seconds(self):
        if self.name and is_signal(self.name):
            return meaning_seconds(self.name[-1])          # no guessing for signal flags
        return settings.FLAG_GUESS_SECONDS + settings.FLAG_REVEAL_SECONDS

    def is_active(self, now):
        if not settings.FLAG_QUIZ_ON:
            return False
        if not self.deck:
            # a fresh random order every round, so there's no sequence to memorize
            self.deck = [n for n in settings.FLAG_QUIZ_COUNTRIES if n in FLAGS]
            random.shuffle(self.deck)
            if len(self.deck) > 1 and self.deck[-1] == self.name:
                self.deck[0], self.deck[-1] = self.deck[-1], self.deck[0]   # no back-to-back repeat
        if not self.deck:
            return False
        self.name = self.deck.pop()
        return True

    def draw(self, canvas, now, t):
        draw_quiz(canvas, self.name, t)



class NauticalLesson(Page):
    """Teaching page: one signal flag every lap, answer shown right away.
    Goes A-Z then 0-9 (or random, see NAUTICAL_ORDER) and remembers its place
    across restarts in state/nautical.txt."""

    STATE = __import__("pathlib").Path(__file__).resolve().parent.parent / "state" / "nautical.txt"

    def __init__(self):
        self.order = list(SIGNALS)
        self.i = self._load()
        self.letter = None

    def _load(self):
        try:
            return int(self.STATE.read_text().strip())
        except Exception:
            return 0

    def _save(self):
        try:
            self.STATE.parent.mkdir(exist_ok=True)
            self.STATE.write_text(str(self.i))
        except Exception:
            pass        # never let a save problem stop the clock

    @property
    def seconds(self):
        return meaning_seconds(self.letter) if self.letter else 6

    def is_active(self, now):
        if not settings.NAUTICAL_LESSON_ON:
            return False
        if settings.NAUTICAL_ORDER == "random":
            choices = [k for k in self.order if k != self.letter]
            self.letter = random.choice(choices)
        else:
            self.letter = self.order[self.i % len(self.order)]
            self.i = (self.i + 1) % len(self.order)
            self._save()
        return True

    def draw(self, canvas, now, t):
        draw_signal_quiz(canvas, self.letter, t)
