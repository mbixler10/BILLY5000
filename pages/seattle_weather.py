"""
The three Seattle weather pages, same layout as the old clock (test32.py):

  SeattleNow     SEATTLE + humidity, big icon + big temp, today's high/low,
                 scrolling conditions / wind / sunrise-sunset line
  SeattleHourly  next 12 hours: temperature line over blue rain-chance bars
  SeattleDaily   next 5 days: day, icon, high, low, rain chance (if 30%+)
"""
from datetime import datetime
from zoneinfo import ZoneInfo

import settings
from engine import seattle_weather
from engine.bitfonts import F3, F3_NARROW, F5, draw, width
from engine.draw import fill
from engine.teamcolors import hexc, mix
from .base import Page

AMBER = hexc("#FFB000")
DIM = (122, 122, 122)
HOME_TZ = ZoneInfo(settings.HOME[2])
MARQUEE_HOLD = 1.5
MARQUEE_PX_PER_SEC = 14

WMO_TEXT = {0: "CLEAR", 1: "MOSTLY CLEAR", 2: "PARTLY CLOUDY", 3: "CLOUDY", 45: "FOG",
            48: "FREEZING FOG", 51: "LIGHT DRIZZLE", 53: "DRIZZLE", 55: "HEAVY DRIZZLE",
            56: "FREEZING DRIZZLE", 57: "FREEZING DRIZZLE", 61: "LIGHT RAIN", 63: "RAIN",
            65: "HEAVY RAIN", 66: "FREEZING RAIN", 67: "FREEZING RAIN", 71: "LIGHT SNOW",
            73: "SNOW", 75: "HEAVY SNOW", 77: "SNOW GRAINS", 80: "SHOWERS", 81: "SHOWERS",
            82: "DOWNPOURS", 85: "SNOW SHOWERS", 86: "SNOW SHOWERS", 95: "THUNDERSTORM",
            96: "T-STORM + HAIL", 99: "T-STORM + HAIL"}
COMPASS8 = ["N", "NE", "E", "SE", "S", "SW", "W", "NW"]

# the old clock's 7x7 icons; letters index ICON_COLORS
ICONS = {
    "sun":    ["...y...", ".y...y.", "..yyy..", "y.yyy.y", "..yyy..", ".y...y.", "...y..."],
    "moon":   ["..mmm..", ".mm....", "mm.....", "mm.....", "mm.....", ".mm....", "..mmm.."],
    "partly": ["y.y....", ".yyww..", "yywwww.", ".wwwwww", "wwwwwww", ".......", "......."],
    "cloud":  [".......", "..ww...", ".wwww..", ".wwwwww", "wwwwwww", ".......", "......."],
    "fog":    [".......", "wwwww..", ".......", ".wwwwww", ".......", "wwwww..", "......."],
    "rain":   ["..www..", ".wwwww.", "wwwwwww", ".......", ".b.b.b.", "b.b.b..", "......."],
    "snow":   ["..www..", ".wwwww.", "wwwwwww", ".......", "w..w..w", "..w..w.", "......."],
    "storm":  ["..www..", ".wwwww.", "wwwwwww", "...y...", "..yy...", "...y...", "..y...."],
}
ICON_COLORS = {"y": (255, 200, 0), "w": (200, 200, 200), "b": (60, 140, 255), "m": (232, 224, 160)}


def wmo_icon(code, is_day=True):
    if code in (0, 1):
        return "sun" if is_day else "moon"
    if code == 2:
        return "partly" if is_day else "cloud"
    if code == 3:
        return "cloud"
    if code in (45, 48):
        return "fog"
    if code in (71, 73, 75, 77, 85, 86):
        return "snow"
    if code in (95, 96, 99):
        return "storm"
    return "rain"


def icon(canvas, name, x, y, scale=1):
    for i, row in enumerate(ICONS.get(name, [])):
        for j, ch in enumerate(row):
            if ch != ".":
                fill(canvas, x + j * scale, y + i * scale, scale, scale, ICON_COLORS[ch])


def box(canvas, x0, y0, x1, y1, c):          # inclusive corners, like the old Frame.fill
    fill(canvas, x0, y0, x1 - x0 + 1, y1 - y0 + 1, c)


def gradient(stops, v):
    if v <= stops[0][0]:
        return stops[0][1]
    for (v0, c0), (v1, c1) in zip(stops, stops[1:]):
        if v <= v1:
            return mix(c0, c1, (v - v0) / (v1 - v0))
    return stops[-1][1]


def temp_color(tf):
    return gradient([(20, (150, 180, 255)), (40, (80, 200, 255)), (55, (80, 230, 160)),
                     (68, (190, 230, 70)), (80, (255, 190, 40)), (92, (255, 90, 40)),
                     (105, (255, 40, 60))], tf)


def wind_color(mph):
    return gradient([(0, (80, 220, 120)), (12, (230, 220, 60)), (22, (255, 140, 40)),
                     (32, (255, 50, 50))], mph)


def short_time(dt):
    return f"{dt.hour % 12 or 12}:{dt.minute:02d}" + ("A" if dt.hour < 12 else "P")


def marquee(canvas, segments, y, t):
    """segments: [(text, color), ...]. Static if it fits, else hold then loop."""
    full = "".join(s for s, _ in segments)
    w = width(F3, full)
    if w <= 60:
        offsets = [2]
    else:
        period = w + 16
        off = int(max(0.0, t - MARQUEE_HOLD) * MARQUEE_PX_PER_SEC) % period
        offsets = [2 - off, 2 - off + period]
    for x in offsets:
        for s, c in segments:
            x += draw(canvas, F3, s, x, y, c, clip=(2, 61))


class _SeattlePage(Page):
    seconds = 12

    def is_active(self, now):
        self.w = seattle_weather.get()
        return self.w is not None


class SeattleNow(_SeattlePage):
    def draw(self, canvas, now, t):
        w = self.w
        draw(canvas, F5, "SEATTLE", 2, 2, AMBER)
        rh = f"{w['humidity']}%"
        draw(canvas, F3, rh, 62 - width(F3, rh), 3, (90, 160, 255))
        icon(canvas, wmo_icon(w["code"], w["is_day"]), 2, 10, scale=2)
        ts = str(round(w["temp"]))
        tc = temp_color(w["temp"])
        if width(F5, ts, 2) <= 26:
            draw(canvas, F5, ts, 20, 10, tc, 2)
            draw(canvas, F5, "°", 21 + width(F5, ts, 2), 10, tc)
        else:   # 100+ degrees: normal size
            draw(canvas, F5, ts + "°", 20, 14, tc)
        hi, lo = f"H{round(w['hi'])}", f"L{round(w['lo'])}"
        draw(canvas, F3, hi, 62 - width(F3, hi), 11, temp_color(w["hi"]))
        draw(canvas, F3, lo, 62 - width(F3, lo), 18, temp_color(w["lo"]))
        wind = f"WIND {COMPASS8[int((w['wind_dir'] + 22.5) // 45) % 8]} {round(w['wind'])}"
        if w.get("gust") and w["gust"] > w["wind"] + 3:
            wind += f" G{round(w['gust'])}"
        here = now.astimezone(HOME_TZ)
        sun = (f"SUNRISE {short_time(w['sunrise'])}" if here < w["sunrise"]
               else f"SUNSET {short_time(w['sunset'])}" if here < w["sunset"]
               else f"SUNRISE {short_time(w['sunrise_next'])}")
        marquee(canvas, [(WMO_TEXT.get(w["code"], "--") + "   ", (170, 200, 230)),
                         (wind + " MPH   ", wind_color(w["wind"])), (sun, AMBER)], 26, t)


class SeattleHourly(_SeattlePage):
    def draw(self, canvas, now, t):
        hour = now.astimezone(HOME_TZ).replace(minute=0, second=0, microsecond=0)
        hrs = [h for h in self.w["hourly"] if h[0] >= hour][:12]
        draw(canvas, F5, "SEA", 2, 2, AMBER)
        draw(canvas, F3, "12 HR", 22, 3, DIM)
        if not hrs:
            return
        temps = [h[1] for h in hrs]
        lo, hi = min(temps), max(temps)
        hs, ls = f"{round(hi)}", f"{round(lo)}"     # top right: high/low for the 12 hours
        x = 62 - width(F3, ls)
        draw(canvas, F3, ls, x, 3, temp_color(lo))
        draw(canvas, F3, "/", x - 4, 3, DIM)
        draw(canvas, F3, hs, x - 5 - width(F3, hs), 3, temp_color(hi))
        for i, (dt, tf, pop, _) in enumerate(hrs):
            x = 2 + i * 5
            bh = round(pop / 100 * 13)
            if bh:
                box(canvas, x, 24 - bh + 1, x + 3, 24, (30, 80, 180))
            y = 21 - round((tf - lo) / max(1, hi - lo) * 9)
            box(canvas, x, y, x + 3, y, temp_color(tf))
            if i % 4 == 0:
                lab = f"{dt.hour % 12 or 12}" + ("A" if dt.hour < 12 else "P")
                draw(canvas, F3, lab, x, 26, DIM)


class SeattleDaily(_SeattlePage):
    def draw(self, canvas, now, t):
        today = now.astimezone(HOME_TZ).date()
        days = [d for d in self.w["daily"] if d[0] > today][:5]
        for i, (d, hi, lo, code, pop) in enumerate(days):
            cx = 2 + i * 12 + 5
            day = d.strftime("%a").upper()[:2]
            draw(canvas, F3, day, cx - width(F3, day) // 2, 0, AMBER if i == 0 else DIM)
            icon(canvas, wmo_icon(code, True), cx - 3, 6)
            hs, ls = str(round(hi)), str(round(lo))
            draw(canvas, F3, hs, cx - width(F3, hs) // 2 + 1, 14, temp_color(hi))
            draw(canvas, F3, ls, cx - width(F3, ls) // 2 + 1, 20, (150, 150, 160))
            if pop >= 30:   # rain chance in blue, only when it's worth knowing
                ps = str(round(pop))
                draw(canvas, F3_NARROW, ps, cx - width(F3_NARROW, ps) // 2 + 1, 26, (90, 160, 255))
