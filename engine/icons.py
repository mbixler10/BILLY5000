"""
7x7 pixel weather icons. Each letter is a color, "." is off.
Edit the pictures right here: what you see is what lights up.
"""
from .display import color

PALETTE = {
    "Y": (255, 200, 0),     # sun / lightning
    "M": (230, 230, 170),   # moon
    "W": (220, 220, 220),   # light cloud
    "G": (130, 130, 140),   # gray cloud
    "B": (60, 140, 255),    # rain
    "S": (255, 255, 255),   # snow
    "F": (120, 120, 120),   # fog
}

ICONS = {
    "sun": [
        "...Y...",
        ".Y...Y.",
        "..YYY..",
        "Y.YYY.Y",
        "..YYY..",
        ".Y...Y.",
        "...Y...",
    ],
    "moon": [
        "..MMM..",
        ".MMM...",
        "MMM....",
        "MMM....",
        "MMM....",
        ".MMM...",
        "..MMM..",
    ],
    "partly": [
        "Y.Y.Y..",
        ".YYY...",
        "YYYWW..",
        ".WWWWW.",
        "WWWWWWW",
        "WWWWWWW",
        ".......",
    ],
    "cloud": [
        ".......",
        "..GGG..",
        ".GGGGG.",
        "GGGGGGG",
        "GGGGGGG",
        ".GGGGG.",
        ".......",
    ],
    "fog": [
        ".......",
        "FFFFFF.",
        ".......",
        ".FFFFFF",
        ".......",
        "FFFFFF.",
        ".......",
    ],
    "rain": [
        "..GGG..",
        ".GGGGG.",
        "GGGGGGG",
        ".......",
        "B.B.B..",
        ".B.B.B.",
        "B.B.B..",
    ],
    "snow": [
        "..GGG..",
        ".GGGGG.",
        "GGGGGGG",
        ".......",
        "S..S..S",
        ".......",
        ".S..S..",
    ],
    "storm": [
        "..GGG..",
        ".GGGGG.",
        "GGGGGGG",
        "...Y...",
        "..Y....",
        "..YY...",
        "...Y...",
    ],
}


def icon_for(wmo_code, is_day):
    """Turn Open-Meteo's weather code into one of the icons above."""
    c = wmo_code
    if c in (0, 1):
        return "sun" if is_day else "moon"
    if c == 2:
        return "partly" if is_day else "cloud"
    if c == 3:
        return "cloud"
    if c in (45, 48):
        return "fog"
    if 71 <= c <= 77 or c in (85, 86):
        return "snow"
    if c >= 95:
        return "storm"
    if 51 <= c <= 67 or 80 <= c <= 82:
        return "rain"
    return "cloud"


def draw_icon(canvas, name, x, y):
    for row, line in enumerate(ICONS[name]):
        for col, ch in enumerate(line):
            if ch != ".":
                r, g, b = PALETTE[ch]
                canvas.SetPixel(x + col, y + row, r, g, b)
