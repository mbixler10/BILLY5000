"""
The page lineup. Adding a feature = import its page here and add it to the list.
"""
import settings
from .city import CityPage
from .alert import AlertPage
from .sports import SportsPage, ItfdbFlash
from .santa import SantaAlert, SantaRadar
from .seattle_weather import SeattleNow, SeattleHourly, SeattleDaily
from .special import SpecialSlot, Countdown, MAX_SLOTS
from .startup import StartupSplash
from .bells import ShipsBells


SANTA_RADAR = SantaRadar()


def _place(p):
    """A place = its city page, followed by its alert page (which only shows
    when NOAA has an active alert there)."""
    return [CityPage(*p), AlertPage(*p)]


def build_rotation():
    # Dec 24-25 the Santa radar rides along right after every Home page.
    home = _place(settings.HOME) + [SANTA_RADAR]
    others = [_place(p) for p in settings.PLACES]
    # Seattle's three detailed weather pages lead the lap, right after Home,
    # then the countdown to the next special day (same order as the old clock).
    lead = []
    if settings.WEATHER_ON and settings.SEATTLE_WEATHER_PAGES:
        lead += [[SeattleNow()], [SeattleHourly()], [SeattleDaily()]]
    if settings.SPECIAL_DAYS_ON and settings.COUNTDOWN_PAGE:
        lead += [[Countdown()]]
    others = lead + others

    # Home, then (HOME_EVERY - 1) other places, then Home again...
    # Today's special pages (holiday greeting, birthdays, trash day...) open each lap.
    lineup = [SpecialSlot(i) for i in range(MAX_SLOTS)] if settings.SPECIAL_DAYS_ON else []
    step = settings.HOME_EVERY - 1
    for i in range(0, len(others), step):
        lineup.extend(home)
        for place in others[i:i + step]:
            lineup.extend(place)

    # Sports run as one block at the end of each lap, no Home pages in between.
    # Teams that are out of season skip themselves.
    if settings.SPORTS_ON:
        lineup.extend(SportsPage(cfg) for cfg in settings.TEAMS)
    return lineup


# Pages that take over the whole screen the moment they're active,
# no matter what's showing.
SANTA_ALERT = SantaAlert()
SHIPS_BELLS = ShipsBells()
# First match wins, so ITFDB and Santa outrank the bells.
TAKEOVERS = [StartupSplash(), ItfdbFlash(), SANTA_ALERT, SHIPS_BELLS]
