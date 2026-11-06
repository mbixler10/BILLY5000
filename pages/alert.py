"""
Alert explanation page. Shows up right after a place's city page, only when
that place has an active NOAA alert:

    [ARV      WARNING]   <- red bar
      WINTER STORM       <- scrolls if long
     UNTIL 4AM SAT       <- in that place's local time

Several alerts at once? Each gets its own turn, most serious first.
"""
from zoneinfo import ZoneInfo

import settings
from engine import alerts
from engine.draw import centered, marquee, alert_bar
from .base import Page


def _until(ends, tz):
    if ends is None:
        return "IN EFFECT"
    local = ends.astimezone(tz)
    hour = local.hour % 12 or 12
    ampm = "AM" if local.hour < 12 else "PM"
    clock = f"{hour}{ampm}" if local.minute == 0 else f"{hour}:{local.minute:02d}{ampm}"
    return f"UNTIL {clock} {local.strftime('%a').upper()}"


class AlertPage(Page):
    def __init__(self, code, name, tz, lat=None, lon=None):
        self.code = code
        self.tz = ZoneInfo(tz)
        self.current = []

    def is_active(self, now):
        self.current = alerts.get(self.code, now)
        return bool(self.current)

    @property
    def seconds(self):
        return settings.PAGE_SECONDS * max(1, len(self.current))

    def draw(self, canvas, now, t):
        n = int(t // settings.PAGE_SECONDS) % len(self.current)
        a = self.current[n]
        sub_t = t % settings.PAGE_SECONDS

        alert_bar(canvas, self.code, a["kind"],
                  settings.COLOR_ALERT_BAR, settings.COLOR_ALERT_TEXT)
        marquee(canvas, "5x7", 19, settings.COLOR_ALERT_WHAT, a["what"], sub_t)
        centered(canvas, "4x6", 29, settings.COLOR_NAME, _until(a["ends"], self.tz))
