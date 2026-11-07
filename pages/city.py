"""
A place page:

    JFK   THU 11/06
    10:35PM  [icon]
             52°
    AUNT ERIN & UNC...   (scrolls if too long)

Time is white for AM, blue for PM. Weather sits on the right; if there's no
fresh weather, the time slides back to center.

On a holiday (Christmas season, Halloween, ...) the page takes the holiday's
field color, falling effect and text colors, and Home shows the holiday's name.
"""
from zoneinfo import ZoneInfo

import settings
from engine import weather, alerts, bitfonts
from engine.draw import text, text_width, centered, marquee, alert_bar, clock, clock_width
from engine.icons import icon_for, draw_icon
from .base import Page
from .special import holiday_theme


class CityPage(Page):
    def __init__(self, code, name, tz, lat=None, lon=None):
        self.code = code
        self.name = name
        self.tz = ZoneInfo(tz)
        self.is_home = (code, name) == tuple(settings.HOME[:2])

    def draw(self, canvas, now, t):
        local = now.astimezone(self.tz)
        code_c, day_c, name_c, temp_c = (settings.COLOR_CODE, settings.COLOR_NAME,
                                         settings.COLOR_NAME, settings.COLOR_TEMP)
        am_c, pm_c, name = settings.COLOR_AM, settings.COLOR_PM, self.name
        theme = holiday_theme(canvas, now, t)
        if theme:
            holiday, ink, accent = theme
            code_c = name_c = temp_c = am_c = pm_c = ink
            # weekday/date in the accent color, unless it's too close to the
            # field color to read (Thanksgiving, St. Patrick's) - then use the text color
            field = holiday.get("field", "#000000").lstrip("#")
            field = tuple(int(field[i:i + 2], 16) for i in (0, 2, 4))
            far = sum((a - b) ** 2 for a, b in zip(accent, field)) ** 0.5 >= 120
            day_c = accent if far else ink
            if self.is_home:
                name = holiday["name"]

        # top line: red alert bar if NOAA has something active, else code + weekday
        active = alerts.get(self.code, now)
        if active:
            alert_bar(canvas, self.code, active[0]["kind"],
                      settings.COLOR_ALERT_BAR, settings.COLOR_ALERT_TEXT)
        else:
            text(canvas, "5x7", 1, 7, code_c, self.code)
            # weekday + that city's own date, e.g. "SAT 11/07", pushed to the right
            # edge with a tighter gap so it doesn't crowd the airport code
            day = local.strftime("%a").upper()
            right = 64
            if settings.CITY_DATE_ON:
                date = local.strftime("%m/%d")
                right -= text_width("5x7", date)
                text(canvas, "5x7", right, 7, day_c, date)
                right -= 2
            text(canvas, "5x7", right - text_width("5x7", day), 7, day_c, day)

        hhmm = f"{local.hour % 12 or 12}:{local.minute:02d}"
        time_color = am_c if local.hour < 12 else pm_c

        wx = weather.get(self.code)
        # big time + small AM/PM, centered as a group (left 46 columns if there's weather)
        ampm = "AM" if local.hour < 12 else "PM"
        group = clock_width(hhmm) + 2 + bitfonts.width(bitfonts.F3, ampm)
        x = ((46 if wx else 64) - group) // 2
        w = clock(canvas, x, 20, time_color, hhmm)
        bitfonts.draw(canvas, bitfonts.F3, ampm, x + w + 1, 11, time_color)
        if wx:
            draw_icon(canvas, icon_for(wx["code"], wx["day"]), 48, 9)
            temp = f"{wx['temp']}°"
            x = 40 + (24 - text_width("5x7", temp)) // 2
            text(canvas, "5x7", x, 23, temp_c, temp)

        # bottom: name (scrolls only if too long)
        marquee(canvas, "5x7", 31, name_c, name, t)
