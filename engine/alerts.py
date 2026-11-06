"""
Active NOAA / National Weather Service alerts (warnings, watches, advisories,
statements) from api.weather.gov. Free, no key. US places only; places
outside the US (like Venice) are skipped automatically.

A background thread checks every place every ALERTS_REFRESH_MINUTES.
Pages call alerts.get("SEA", now) and never wait on the network.
"""
import json
import logging
import threading
import time
import urllib.error
import urllib.request
from datetime import datetime, timedelta

import settings

log = logging.getLogger("billy5000.alerts")
URL = "https://api.weather.gov/alerts/active?point={lat},{lon}"
HEADERS = {"User-Agent": "BILLY5000 family world clock",
           "Accept": "application/geo+json"}

SEVERITY = {"Extreme": 0, "Severe": 1, "Moderate": 2, "Minor": 3}
KIND = {"WARNING": 0, "EMERGENCY": 0, "WATCH": 1,
        "ADVISORY": 2, "ALERT": 2, "STATEMENT": 3}

_lock = threading.Lock()
_data = {}          # code -> list of alert dicts
_updated = 0.0
_not_us = set()     # codes the NWS doesn't cover


def get(code, now):
    """Active alerts for a place, most serious first. Empty list if none."""
    with _lock:
        if time.time() - _updated > 2 * 3600 and not _demo:
            return []
        items = _data.get(code, [])
    return [a for a in items if a["ends"] is None or a["ends"] > now]


def _parse(feature):
    p = feature["properties"]
    event = p["event"].upper()
    words = event.split()
    kind = words[-1] if words[-1] in KIND else "ALERT"
    # "WINTER STORM WARNING" -> what = "WINTER STORM", kind = "WARNING"
    what = " ".join(words[:-1]) if words[-1] in KIND and len(words) > 1 else event
    ends = p.get("ends") or p.get("expires")
    return {
        "event": event,
        "what": what,
        "kind": kind,
        "ends": datetime.fromisoformat(ends) if ends else None,
        "rank": (KIND.get(kind, 2), SEVERITY.get(p.get("severity"), 4)),
    }


def _fetch_one(place):
    req = urllib.request.Request(URL.format(lat=place[3], lon=place[4]), headers=HEADERS)
    with urllib.request.urlopen(req, timeout=20) as r:
        body = json.load(r)
    found = {}
    for f in body.get("features", []):
        p = f["properties"]
        if p.get("status") != "Actual" or p.get("messageType") == "Cancel":
            continue
        a = _parse(f)
        # the same alert often comes in several copies; keep one, latest end
        old = found.get(a["event"])
        if old is None or (a["ends"] and old["ends"] and a["ends"] > old["ends"]):
            found[a["event"]] = a
    return sorted(found.values(), key=lambda a: a["rank"])[:3]


def _loop(places):
    global _updated
    while True:
        fresh, ok = {}, 0
        for place in places:
            code = place[0]
            if code in _not_us:
                continue
            try:
                fresh[code] = _fetch_one(place)
                ok += 1
            except urllib.error.HTTPError as e:
                if e.code in (400, 404):
                    _not_us.add(code)
                    log.info("%s is outside NWS coverage; skipping alerts there", code)
                else:
                    log.warning("alerts for %s failed (%s)", code, e)
            except Exception as e:
                log.warning("alerts for %s failed (%s)", code, e)
            time.sleep(0.5)   # be polite to weather.gov
        if ok:
            with _lock:
                _data.update(fresh)
                _updated = time.time()
            active = {c: [a["event"] for a in v] for c, v in fresh.items() if v}
            log.info("alerts checked for %d places; active: %s", ok, active or "none")
        time.sleep(settings.ALERTS_REFRESH_MINUTES * 60 if ok else 60)


_demo = False


def demo():
    """Fake alerts for testing on the PC: python main.py --demo-alerts"""
    global _demo, _updated
    _demo = True
    soon = datetime.now().astimezone() + timedelta(hours=20)
    with _lock:
        _data["SEA"] = [
            {"event": "WIND ADVISORY", "what": "WIND", "kind": "ADVISORY",
             "ends": soon, "rank": (2, 3)},
        ]
        _data["ARV"] = [
            {"event": "WINTER STORM WARNING", "what": "WINTER STORM", "kind": "WARNING",
             "ends": soon, "rank": (0, 1)},
            {"event": "WIND CHILL ADVISORY", "what": "WIND CHILL", "kind": "ADVISORY",
             "ends": soon + timedelta(hours=12), "rank": (2, 2)},
        ]
        _updated = time.time()


def start(demo_mode=False):
    if demo_mode:
        demo()
        return
    if not settings.ALERTS_ON:
        return
    places = [settings.HOME] + list(settings.PLACES)
    threading.Thread(target=_loop, args=(places,), daemon=True, name="alerts").start()
