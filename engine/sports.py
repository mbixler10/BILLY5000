"""
Sports from ESPN's public API (free, no key).

For each team in settings.TEAMS, a background thread:
  * reads the team's schedule every SCHEDULE_MINUTES
  * when a game is live (or about to start) checks the live score every 30 seconds
  * fires the ITFDB flash the moment a Dodgers game goes from "pre" to "in"

Pages call sports.view("DODGERS", now) and get back what to show:
  ("live", game) / ("final", game) / ("next", game) / None (out of season -> skip)
"""
import json
import logging
import threading
import time
import urllib.request
from datetime import datetime, timedelta, timezone

import settings
from engine import teamcolors

log = logging.getLogger("billy5000.sports")
BASE = "https://site.api.espn.com/apis/site/v2/sports/"
HEADERS = {"User-Agent": "BILLY5000 family world clock"}

SCHEDULE_MINUTES = 30
LIVE_POLL_SECONDS = 30
WATCH_BEFORE = timedelta(minutes=15)   # start checking live score this long before first pitch
GAME_LENGTH = timedelta(hours=4)       # rough: start time + this = "when it ended"

_lock = threading.Lock()
_teams = {}             # name -> {"cfg", "events", "our_id", "fetched", "states"}
_itfdb_until = 0.0


# ------------------------------------------------------------------ reading ESPN

def _get(path):
    req = urllib.request.Request(BASE + path, headers=HEADERS)
    with urllib.request.urlopen(req, timeout=20) as r:
        return json.load(r)


def _when(s):
    return datetime.fromisoformat(s.replace("Z", "+00:00"))


def _score(v):
    if isinstance(v, dict):
        v = v.get("displayValue", v.get("value"))
    if v is None:
        return None
    try:
        return str(int(float(v)))
    except (TypeError, ValueError):
        return str(v)


def _game(event_id, date, comp):
    """Boil an ESPN competition down to what the panel needs."""
    status = comp.get("status", {}).get("type", {})
    teams = []
    for c in comp["competitors"]:
        team = c.get("team", {})
        teams.append({
            "id": str(team.get("id", "")),
            "abbr": team.get("abbreviation", "?").upper(),
            "home": c.get("homeAway") == "home",
            "score": _score(c.get("score")),
            "winner": c.get("winner"),
            "color": team.get("color"),
            "alt": team.get("alternateColor"),
        })
    teams.sort(key=lambda t: t["home"])        # away first, home second
    return {
        "id": str(event_id),
        "date": _when(date),
        "state": status.get("state", "pre"),     # pre / in / post
        "detail": status.get("shortDetail", "").upper(),
        "time_valid": comp.get("timeValid", True),
        "teams": teams,
    }


def _fetch_schedule(cfg):
    events, our_id = {}, None
    for extra in ("", "?seasontype=3"):        # regular season + postseason
        try:
            data = _get(f"{cfg['league']}/teams/{cfg['team']}/schedule{extra}")
        except Exception as e:
            if not extra:
                raise
            log.debug("no postseason schedule for %s (%s)", cfg["name"], e)
            continue
        our_id = our_id or str(data.get("team", {}).get("id", ""))
        for e in data.get("events", []):
            try:
                events[str(e["id"])] = _game(e["id"], e["date"], e["competitions"][0])
            except (KeyError, IndexError, ValueError):
                continue
    return list(events.values()), our_id


def _fetch_live(cfg, event_id):
    data = _get(f"{cfg['league']}/summary?event={event_id}")
    comp = data["header"]["competitions"][0]
    return _game(event_id, comp.get("date") or data["header"].get("date"), comp)


# ------------------------------------------------------------------ deciding what to show

def _pick(events, now):
    live = next((e for e in events if e["state"] == "in"), None)
    upcoming = sorted((e for e in events
                       if e["state"] == "pre" and e["date"] > now - timedelta(hours=6)),
                      key=lambda e: e["date"])
    past = sorted((e for e in events if e["state"] == "post"), key=lambda e: e["date"])
    return live, (upcoming[0] if upcoming else None), (past[-1] if past else None)


def view(name, now):
    """What this team should show right now, as a list of pages (empty = skip):
         live game          -> [live]
         just finished      -> [final, next]  (next only if within SPORTS_NEXT_AFTER_FINAL_DAYS)
         otherwise          -> [next]         (only if within SPORTS_IN_SEASON_DAYS)
       Final-only teams (Point Loma) only ever show [final]."""
    with _lock:
        t = _teams.get(name)
        if not t:
            return []
        events, our_id, cfg = list(t["events"]), t["our_id"], t["cfg"]

    live, nxt, last = _pick(events, now)
    if live and not cfg.get("final_only"):
        return [("live", live, our_id)]

    pages = []
    if last:
        sport = cfg["league"].split("/")[0]          # football / baseball / hockey / basketball
        hours = settings.SPORTS_FINAL_HOURS.get(sport, 24)
        until = last["date"] + GAME_LENGTH + timedelta(hours=hours)
        if nxt:
            until = min(until, nxt["date"])          # next game starting ends the final
        if now < until:
            pages.append(("final", last, our_id))
    if cfg.get("final_only"):
        return pages
    if nxt:
        days = settings.SPORTS_NEXT_AFTER_FINAL_DAYS if pages else settings.SPORTS_IN_SEASON_DAYS
        if nxt["date"] - now < timedelta(days=days):
            pages.append(("next", nxt, our_id))
    return pages


# ------------------------------------------------------------------ ITFDB

def trigger_itfdb():
    global _itfdb_until
    _itfdb_until = time.time() + settings.ITFDB_SECONDS
    log.info("IT'S TIME FOR DODGER BASEBALL!")


def itfdb_active():
    return time.time() < _itfdb_until


# ------------------------------------------------------------------ background thread

def _update(t):
    cfg = t["cfg"]
    now = datetime.now(timezone.utc)

    if time.time() - t["fetched"] > SCHEDULE_MINUTES * 60:
        events, our_id = _fetch_schedule(cfg)
        with _lock:
            t["events"], t["our_id"], t["fetched"] = events, our_id, time.time()

    _learn_colors(cfg, t)
    if cfg.get("final_only"):
        return

    live, nxt, _ = _pick(t["events"], now)
    watch = live or (nxt if nxt and nxt["date"] - now < WATCH_BEFORE else None)
    if not watch:
        return

    game = _fetch_live(cfg, watch["id"])
    before = t["states"].get(game["id"])
    if before == "pre" and game["state"] == "in" and cfg.get("itfdb"):
        trigger_itfdb()
    t["states"][game["id"]] = game["state"]
    with _lock:
        t["events"] = [game if e["id"] == game["id"] else e for e in t["events"]]
        if game["state"] == "post":
            t["fetched"] = 0          # game over: re-read the schedule for the next one


def _learn_colors(cfg, t):
    """College opponents: fetch each school's colors once (pro teams use the color books)."""
    live, nxt, last = _pick(t["events"], datetime.now(timezone.utc))
    for game in (live, nxt, last):
        for tm in (game or {}).get("teams", []):
            if tm["id"] != t["our_id"] and teamcolors.needs_lookup(cfg["league"], tm["abbr"]):
                try:
                    data = _get(f"{cfg['league']}/teams/{tm['id']}")
                    teamcolors.remember(cfg["league"], tm["abbr"], data.get("team", {}))
                except Exception as e:
                    log.debug("colors for %s failed (%s)", tm["abbr"], e)
                    teamcolors.remember(cfg["league"], tm["abbr"],
                                        {"color": tm["color"], "alternateColor": tm["alt"]})


def _loop():
    while True:
        for t in list(_teams.values()):
            try:
                _update(t)
            except Exception as e:
                log.warning("sports update for %s failed (%s)", t["cfg"]["name"], e)
            time.sleep(0.3)
        time.sleep(LIVE_POLL_SECONDS)


def start(demo_mode=False):
    if not settings.SPORTS_ON:
        return
    for cfg in settings.TEAMS:
        _teams[cfg["name"]] = {"cfg": cfg, "events": [], "our_id": None,
                               "fetched": 0.0, "states": {}}
    if demo_mode:
        _demo()
        return
    threading.Thread(target=_loop, daemon=True, name="sports").start()


# ------------------------------------------------------------------ demo data

def _demo():
    """Fake games so you can see every kind of page: python main.py --demo-sports"""
    now = datetime.now(timezone.utc)

    def g(our, opp, our_home, state, ours=None, theirs=None, detail="", start=now):
        us = {"id": "1", "abbr": our, "home": our_home, "score": ours, "color": None, "alt": None,
              "winner": state == "post" and int(ours) > int(theirs)}
        them = {"id": "2", "abbr": opp, "home": not our_home, "score": theirs,
                "color": "2D68C4", "alt": "F2A900",
                "winner": state == "post" and int(theirs) > int(ours)}
        teams = sorted([us, them], key=lambda t: t["home"])
        return [{"id": our + opp, "date": start, "state": state, "detail": detail,
                 "time_valid": True, "teams": teams}]

    fake = {
        "DODGERS": g("LAD", "SF", False, "in", "3", "2", "TOP 7TH"),
        "SEAHAWKS": g("SEA", "LAR", True, "pre", start=now + timedelta(days=3, hours=2)),
        "TROJANS": g("USC", "UCLA", True, "post", "34", "17", "FINAL", now - timedelta(hours=5)),
        "KRAKEN": g("SEA", "VAN", False, "in", "1", "1", "2ND 8:14"),
        "NAVY": g("NAVY", "ARMY", False, "post", "17", "20", "FINAL", now - timedelta(hours=5)),
        "SEA LIONS": g("PLNU", "AZU", True, "post", "78", "71", "FINAL", now - timedelta(hours=6)),
    }
    with _lock:
        for name, events in fake.items():
            if name in _teams:
                _teams[name]["events"] = events
                _teams[name]["our_id"] = "1"
