"""
The page lineup. Adding a feature = import its page here and add it to the list.
"""
import settings
from .city import CityPage
from .alert import AlertPage
from .sports import SportsPage, ItfdbFlash
from .santa import SantaAlert, SantaRadar
from .vinny import VinnyAlert
from .seattle_weather import SeattleNow, SeattleHourly, SeattleDaily
from .special import SpecialSlot, Countdown, MAX_SLOTS
from .startup import StartupSplash
from .bells import ShipsBells
from .flagquiz import FlagQuiz, NauticalLesson
from .lighthouse import LapStart, LighthouseSlot
from .olympics import OlympicCountdown
from .opening import OpeningCountdown, OpeningDayAlert, HomeRunFlash
from .home import HomeCity, HomeAlert, HomeSantaRadar, GATE, shown


SANTA_RADAR = HomeSantaRadar()


def _place(p):
    """A place = its city page, followed by its alert page (which only shows
    when NOAA has an active alert there). Alert pages never count as one of the
    pages between Home visits."""
    alert = AlertPage(*p)
    alert.counts_toward_home = False
    return [CityPage(*p), alert]


def build_rotation():
    # Home = SEA's clock, its alert (if any) right behind it, and on Dec 24-25 the
    # Santa radar. One Home stop waits in front of every group; it only shows once
    # HOME_EVERY - 1 pages have actually been on screen since the last Home.
    home_city, home_alert = HomeCity(*settings.HOME), HomeAlert(*settings.HOME)
    home = [home_city, home_alert, SANTA_RADAR]
    others = [_place(p) for p in settings.PLACES]
    # Seattle's three detailed weather pages lead the lap, right after Home,
    # then the countdown to the next special day (same order as the old clock).
    lead = []
    if settings.WEATHER_ON and settings.SEATTLE_WEATHER_PAGES:
        lead += [[SeattleNow()], [SeattleHourly()], [SeattleDaily()]]
    if settings.SPECIAL_DAYS_ON and settings.COUNTDOWN_PAGE:
        lead += [[Countdown()]]
    if settings.OPENING_DAY_MODE:          # days to Opening Day (skips itself off-season)
        lead += [[OpeningCountdown()]]
    others = lead + others

    # Today's special pages (holiday greeting, birthdays, trash day...) open each lap,
    # then Home, then the other pages with Home coming back after every few.
    groups = [[SpecialSlot(i) for i in range(MAX_SLOTS)]] if settings.SPECIAL_DAYS_ON else []
    for g in others:
        groups.append(home)
        groups.append(g)

    # The lighthouse lesson shows once per lap at a random spot: a hidden slot
    # waits after every group, and LapStart picks which one gets it this lap.
    # (Never between a city and its alert page, never inside the sports block.)
    lineup = [LapStart()]
    for g in groups:
        lineup.extend(g)
        if settings.LIGHTHOUSE_LESSON_ON and g is not home:
            lineup.append(LighthouseSlot())

    # Sports run as one block at the end of each lap, no Home pages in between.
    # Teams that are out of season skip themselves.
    if settings.SPORTS_ON:
        lineup.extend(SportsPage(cfg) for cfg in settings.TEAMS)

    # End of every lap: one flag-game flag (countries/states), then one nautical lesson.
    if settings.FLAG_QUIZ_ON:
        lineup.append(FlagQuiz())
    if settings.NAUTICAL_LESSON_ON:
        lineup.append(NauticalLesson())
    if settings.LIGHTHOUSE_LESSON_ON:
        lineup.append(LighthouseSlot())
    # Every few laps: the countdown to the next Olympics.
    if settings.OLYMPICS_ON:
        lineup.append(OlympicCountdown())
    return lineup


# Pages that take over the whole screen the moment they're active,
# no matter what's showing.
SANTA_ALERT = SantaAlert()
VINNY_ALERT = VinnyAlert()
SHIPS_BELLS = ShipsBells()
OPENING_ALERT = OpeningDayAlert()
HOMER_FLASH = HomeRunFlash()
# First match wins, so ITFDB and Santa outrank the bells. The 9/11 reading of
# the names (and the Pearl Harbor reading on Dec 7) outrank everything except
# the start-up screen.
from engine.specialdays import READING as NAMES_911
from engine.pearlharbor import READING as NAMES_PEARL
TAKEOVERS = [StartupSplash(), NAMES_911, NAMES_PEARL, ItfdbFlash(), HOMER_FLASH, OPENING_ALERT,
             SANTA_ALERT, VINNY_ALERT, SHIPS_BELLS]
