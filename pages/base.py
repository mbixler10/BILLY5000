"""
Every screen on BILLY5000 is a Page. To add a new feature (weather, tides,
sports, Santa...), make a new file in pages/ with a class like this one.
"""


class Page:
    seconds = None      # None = use PAGE_SECONDS from settings

    def is_active(self, now):
        """Return False to skip this page (e.g. team out of season)."""
        return True

    def draw(self, canvas, now, t):
        """Draw one frame. now = current datetime, t = seconds since page appeared."""
        raise NotImplementedError
