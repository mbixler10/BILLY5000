"""
Home (SEA) placement: Home shows after every HOME_EVERY - 1 pages that were
actually on screen. Pages that skip themselves (no data yet, out of season...)
don't count, and neither does Home's own alert page, so Home never doubles up
and the alert never pushes Home sooner.

The main loop calls shown(page) each time a page goes up.
"""
import settings
from .city import CityPage
from .alert import AlertPage
from .santa import SantaRadar


class _Gate:
    def __init__(self):
        self.count = 0
        self.home_up = False      # Home's city page was the last thing shown

    @property
    def step(self):
        return max(1, settings.HOME_EVERY - 1)

    def new_lap(self):
        self.count = self.step    # every lap opens with Home (after today's special pages)


GATE = _Gate()


class HomeCity(CityPage):
    counts_toward_home = False

    def is_active(self, now):
        if GATE.count < GATE.step:
            GATE.home_up = False
            return False
        GATE.count = 0
        GATE.home_up = True
        return super().is_active(now)


class HomeAlert(AlertPage):
    counts_toward_home = False

    def is_active(self, now):
        return GATE.home_up and super().is_active(now)


class HomeSantaRadar(SantaRadar):
    counts_toward_home = False

    def is_active(self, now):
        return GATE.home_up and super().is_active(now)


def shown(page):
    """Called by the main loop whenever a page actually goes on screen."""
    if getattr(page, "counts_toward_home", True):
        GATE.count += 1
        GATE.home_up = False
