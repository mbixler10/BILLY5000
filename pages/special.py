"""
Special-day pages. All the drawing is the old clock's code in engine/specialdays.py;
these classes just decide when each page shows.

  SpecialSlot  today's greeting pages (trash day, April Fools, birthdays,
               anniversary, holiday greeting, flag-stripe day), leading each lap
  Countdown    days until the next special day
  holiday_theme()  used by the clock pages to paint the holiday field + effect
"""
import settings
from engine import specialdays as sd
from engine.teamcolors import hexc
from .base import Page

MAX_SLOTS = 6     # most special pages one day can have


def _today(now):
    sd._now = now
    return sd.home_today(now)


class SpecialSlot(Page):
    """Slot i shows today's i-th special page, if there is one."""

    def __init__(self, i):
        self.i = i
        self.kind = self.arg = None

    def is_active(self, now):
        pages = sd.special_pages_for(_today(now))
        if self.i >= len(pages):
            return False
        self.kind, self.arg = pages[self.i]
        return True

    @property
    def seconds(self):
        if self.kind == "honorroll":
            return sd.honor_seconds(self.arg)
        return settings.SPECIAL_PAGE_SECONDS.get(self.kind, 10)

    def draw(self, canvas, now, t):
        sd._now = now
        f = sd.Frame()
        if self.kind == "special":
            sd.render_special(f, self.arg, t)
        elif self.kind == "striped":
            sd.render_striped(f, self.arg, t)
        elif self.kind == "birthday":
            sd.render_birthday(f, self.arg, t)
        elif self.kind == "anniversary":
            sd.render_anniversary(f, self.arg, t)
        elif self.kind == "aprilfools":
            sd.render_april_fools(f, t)
        elif self.kind == "honorroll":
            sd.render_honor_roll(f, self.arg, t)
        elif self.kind == "trash":
            sd.render_trash(f, self.arg, t)
        f.flush(canvas)


class Countdown(Page):
    seconds = settings.SPECIAL_PAGE_SECONDS["countdown"]

    def is_active(self, now):
        if not settings.COUNTDOWN_PAGE:
            return False
        self.nxt = sd.next_special(_today(now))
        return self.nxt is not None

    def draw(self, canvas, now, t):
        f = sd.Frame()
        sd.render_countdown(f, self.nxt, now, t)
        f.flush(canvas)


def holiday_theme(canvas, now, t):
    """On a field holiday (Christmas season, Halloween...): paint the field color
    and effect, and return the holiday plus its text/accent colors. Else None."""
    if not settings.SPECIAL_DAYS_ON:
        return None
    day = sd.field_day_for(_today(now))
    if not day:
        return None
    f = sd.Frame()
    f.bg = hexc(day["field"])
    sd.draw_effect(f, day.get("effect"), t, hexc(day["accent"]))
    f.flush(canvas)
    return day, hexc(day["text"]), hexc(day["accent"])
