"""
Detailed Seattle weather (Open-Meteo, free, no key): current conditions,
next 12 hours, and the next several days. Same request as the old clock.
One background thread refreshes it every WEATHER_REFRESH_MINUTES.
"""
import json
import logging
import threading
import time
import urllib.parse
import urllib.request
from datetime import date, datetime
from zoneinfo import ZoneInfo

import settings

log = logging.getLogger("billy5000.seattle_weather")
URL = "https://api.open-meteo.com/v1/forecast"

_lock = threading.Lock()
_data = None
_updated = 0.0


def get():
    """Latest Seattle weather dict, or None if we don't have fresh data."""
    with _lock:
        if time.time() - _updated > settings.WEATHER_STALE_HOURS * 3600:
            return None
        return _data


def _fetch():
    _, _, tz, lat, lon = settings.HOME
    params = {
        "latitude": lat, "longitude": lon,
        "current": "temperature_2m,weather_code,wind_speed_10m,wind_direction_10m,"
                   "wind_gusts_10m,is_day,relative_humidity_2m",
        "hourly": "temperature_2m,precipitation_probability,weather_code",
        "daily": "temperature_2m_max,temperature_2m_min,sunrise,sunset,weather_code,"
                 "precipitation_probability_max",
        "temperature_unit": "fahrenheit", "wind_speed_unit": "mph",
        "timezone": tz, "forecast_days": 7,
    }
    req = urllib.request.Request(URL + "?" + urllib.parse.urlencode(params),
                                 headers={"User-Agent": "BILLY5000-clock"})
    with urllib.request.urlopen(req, timeout=20) as r:
        return parse(json.load(r), tz)


def parse(j, tz):
    z = ZoneInfo(tz)
    loc_t = lambda s: datetime.fromisoformat(s).replace(tzinfo=z)
    cur, hj, dj = j["current"], j["hourly"], j["daily"]
    hourly = [(loc_t(t), hj["temperature_2m"][i], hj["precipitation_probability"][i] or 0,
               hj["weather_code"][i]) for i, t in enumerate(hj["time"])]
    daily = [(date.fromisoformat(dj["time"][i]), dj["temperature_2m_max"][i],
              dj["temperature_2m_min"][i], dj["weather_code"][i],
              dj["precipitation_probability_max"][i] or 0) for i in range(len(dj["time"]))]
    return {"temp": cur["temperature_2m"], "code": cur["weather_code"],
            "wind": cur["wind_speed_10m"], "wind_dir": cur["wind_direction_10m"],
            "gust": cur.get("wind_gusts_10m"), "humidity": cur["relative_humidity_2m"],
            "is_day": bool(cur["is_day"]), "hi": dj["temperature_2m_max"][0],
            "lo": dj["temperature_2m_min"][0], "sunrise": loc_t(dj["sunrise"][0]),
            "sunset": loc_t(dj["sunset"][0]), "sunrise_next": loc_t(dj["sunrise"][1]),
            "hourly": hourly, "daily": daily[1:]}


def _loop():
    global _data, _updated
    while True:
        try:
            fresh = _fetch()
            with _lock:
                _data, _updated = fresh, time.time()
            log.info("Seattle forecast updated")
            wait = settings.WEATHER_REFRESH_MINUTES * 60
        except Exception as e:
            log.warning("Seattle forecast failed (%s); keeping last one", e)
            wait = 60
        time.sleep(wait)


def start():
    if settings.WEATHER_ON and settings.SEATTLE_WEATHER_PAGES:
        threading.Thread(target=_loop, daemon=True, name="seattle-weather").start()


def demo():
    """Sample forecast for previewing: python main.py --demo-weather"""
    global _data, _updated
    from datetime import timedelta
    z = ZoneInfo(settings.HOME[2])
    now = datetime.now(z).replace(minute=0, second=0, microsecond=0)
    today = now.date()
    temps = [48, 47, 47, 46, 45, 45, 44, 44, 45, 47, 50, 52, 53, 53]
    pops = [20, 30, 55, 70, 80, 65, 40, 25, 10, 5, 5, 10, 15, 20]
    with _lock:
        _data = {"temp": 48, "code": 61, "wind": 11, "wind_dir": 200, "gust": 19,
                 "humidity": 87, "is_day": False, "hi": 53, "lo": 44,
                 "sunrise": now.replace(hour=7, minute=4), "sunset": now.replace(hour=16, minute=41),
                 "sunrise_next": (now + timedelta(days=1)).replace(hour=7, minute=6),
                 "hourly": [(now + timedelta(hours=i), temps[i], pops[i], 61) for i in range(14)],
                 "daily": [(today + timedelta(days=i), hi, lo, code, pop) for i, (hi, lo, code, pop) in
                           enumerate([(52, 43, 61, 80), (50, 41, 3, 20), (55, 44, 2, 10),
                                      (49, 38, 71, 40), (46, 36, 0, 0)], start=1)]}
        _updated = time.time()
