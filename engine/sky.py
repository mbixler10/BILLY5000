"""
Sky dates for the special days, worked out on the Pi with no internet:
first day of each season (equinoxes and solstices), full moons, and Seattle's
sunrise and sunset. Low-precision formulas from the Astronomical Almanac: the
sun to about 0.01 degree (a few minutes of time), the moon to about 0.3 degree
(under an hour) - plenty to get the right day.

Check:  python -m engine.sky 2027
"""
import functools
import math
import sys
from datetime import date, datetime, timedelta, timezone
from zoneinfo import ZoneInfo

import settings

HOME = ZoneInfo(settings.HOME[2])
LAT, LON = settings.HOME[3], settings.HOME[4]
J2000 = 2451545.0
SEASONS = {"spring": 0, "summer": 90, "fall": 180, "winter": 270}
_GUESS = {"spring": (3, 20), "summer": (6, 21), "fall": (9, 22), "winter": (12, 21)}
MOON_NAMES = {1: "WOLF", 2: "SNOW", 3: "WORM", 4: "PINK", 5: "FLOWER", 6: "STRAWBERRY",
              7: "BUCK", 8: "STURGEON", 9: "HARVEST", 10: "HUNTER'S", 11: "BEAVER", 12: "COLD"}


def _jd(dt):
    return dt.timestamp() / 86400.0 + 2440587.5


def _dt(jd):
    return datetime.fromtimestamp((jd - 2440587.5) * 86400.0, tz=timezone.utc)


def _sin(deg):
    return math.sin(math.radians(deg))


def sun_longitude(jd):
    n = jd - J2000
    L = 280.460 + 0.9856474 * n
    g = 357.528 + 0.9856003 * n
    return (L + 1.915 * _sin(g) + 0.020 * _sin(2 * g)) % 360


def moon_longitude(jd):
    T = (jd - J2000) / 36525.0
    lam = (218.32 + 481267.881 * T
           + 6.29 * _sin(134.9 + 477198.85 * T) - 1.27 * _sin(259.2 - 413335.38 * T)
           + 0.66 * _sin(235.7 + 890534.23 * T) + 0.21 * _sin(269.9 + 954397.70 * T)
           - 0.19 * _sin(357.5 + 35999.05 * T) - 0.11 * _sin(186.6 + 966404.05 * T))
    return lam % 360


@functools.lru_cache(maxsize=64)
def season_start(year, season):
    """Local (Seattle) date of the equinox or solstice."""
    target = SEASONS[season]
    m, d = _GUESS[season]
    jd = _jd(datetime(year, m, d, 12, tzinfo=timezone.utc))
    for _ in range(6):
        diff = (target - sun_longitude(jd) + 180) % 360 - 180
        jd += diff / 0.9856
    return _dt(jd).astimezone(HOME).date()


@functools.lru_cache(maxsize=8)
def full_moons(year):
    """Local (Seattle) dates of every full moon in the year."""
    out = []
    jd = _jd(datetime(year - 1, 12, 1, tzinfo=timezone.utc))
    end = _jd(datetime(year + 1, 1, 2, tzinfo=timezone.utc))
    while jd < end:
        e = (moon_longitude(jd) - sun_longitude(jd)) % 360
        jd += ((180 - e) % 360) / 12.19 + 0.01         # jump near the next full moon
        for _ in range(5):                             # then home in on it
            e = (moon_longitude(jd) - sun_longitude(jd)) % 360
            jd += ((180 - e + 180) % 360 - 180) / 12.19
        d = _dt(jd).astimezone(HOME).date()
        if d.year == year and (not out or d != out[-1]):
            out.append(d)
        jd += 2
    return tuple(out)


def full_moon_name(d):
    """'HARVEST', or 'BLUE' for a second full moon in one month."""
    same = [x for x in full_moons(d.year) if x.month == d.month]
    if len(same) > 1 and d == same[-1]:
        return "BLUE"
    return MOON_NAMES[d.month]


def sun_times(d):
    """(sunrise, sunset) in Seattle time for date d."""
    noon = datetime(d.year, d.month, d.day, 20, tzinfo=timezone.utc)   # ~local noon
    n = _jd(noon) - J2000
    lam = math.radians(sun_longitude(_jd(noon)))
    eps = math.radians(23.439 - 0.0000004 * n)
    dec = math.asin(math.sin(eps) * math.sin(lam))
    ra = math.degrees(math.atan2(math.cos(eps) * math.sin(lam), math.cos(lam))) % 360
    L = (280.460 + 0.9856474 * n) % 360
    eqt = ((L - ra + 180) % 360 - 180) * 4                    # minutes
    lat = math.radians(LAT)
    cos_h = (math.sin(math.radians(-0.833)) - math.sin(lat) * math.sin(dec)) / (math.cos(lat) * math.cos(dec))
    h = math.degrees(math.acos(max(-1.0, min(1.0, cos_h))))
    solar_noon = 720 - 4 * LON - eqt                          # minutes after 00:00 UTC
    base = datetime(d.year, d.month, d.day, tzinfo=timezone.utc)
    rise = (base + timedelta(minutes=solar_noon - 4 * h)).astimezone(HOME)
    sset = (base + timedelta(minutes=solar_noon + 4 * h)).astimezone(HOME)
    return rise, sset


if __name__ == "__main__":
    y = int(sys.argv[1]) if len(sys.argv) > 1 else date.today().year
    for s in SEASONS:
        d = season_start(y, s)
        r, t = sun_times(d)
        print(f"{s:7} {d}  sunrise {r:%H:%M}  sunset {t:%H:%M}")
    for d in full_moons(y):
        print("full moon", d, full_moon_name(d))
