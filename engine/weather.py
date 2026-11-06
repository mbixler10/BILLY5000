"""
Weather from Open-Meteo (free, no API key).

One background thread fetches every place in a single request every
WEATHER_REFRESH_MINUTES. Pages just ask weather.get("JFK"), which never waits
on the network. If the internet drops, the last good reading stays up until it
is WEATHER_STALE_HOURS old, then the weather quietly disappears.
"""
import json
import logging
import threading
import time
import urllib.parse
import urllib.request

import settings

log = logging.getLogger("billy5000.weather")
URL = "https://api.open-meteo.com/v1/forecast"

_lock = threading.Lock()
_data = {}            # code -> {"temp": 52, "code": 3, "day": True}
_updated = 0.0        # time.time() of last good fetch


def get(code):
    """Latest weather for an airport code, or None if we don't have fresh data."""
    with _lock:
        if time.time() - _updated > settings.WEATHER_STALE_HOURS * 3600:
            return None
        return _data.get(code)


def _fetch(places):
    params = {
        "latitude": ",".join(str(p[3]) for p in places),
        "longitude": ",".join(str(p[4]) for p in places),
        "current": "temperature_2m,weather_code,is_day",
        "temperature_unit": "fahrenheit",
    }
    req = urllib.request.Request(URL + "?" + urllib.parse.urlencode(params),
                                 headers={"User-Agent": "BILLY5000-clock"})
    with urllib.request.urlopen(req, timeout=20) as r:
        body = json.load(r)
    if isinstance(body, dict):        # one place comes back as a dict, many as a list
        body = [body]
    out = {}
    for place, item in zip(places, body):
        cur = item["current"]
        out[place[0]] = {
            "temp": round(cur["temperature_2m"]),
            "code": cur["weather_code"],
            "day": bool(cur["is_day"]),
        }
    return out


def _loop(places):
    global _updated
    while True:
        try:
            fresh = _fetch(places)
            with _lock:
                _data.update(fresh)
                _updated = time.time()
            log.info("weather updated for %d places", len(fresh))
            wait = settings.WEATHER_REFRESH_MINUTES * 60
        except Exception as e:
            log.warning("weather fetch failed (%s); keeping last reading", e)
            wait = 60          # retry sooner after a failure
        time.sleep(wait)


def start():
    if not settings.WEATHER_ON:
        return
    places = [settings.HOME] + list(settings.PLACES)
    threading.Thread(target=_loop, args=(places,), daemon=True, name="weather").start()
