"""
Drawn greeting pages for the special days (64 x 32). Each takes the Frame, the
holiday entry from settings.SPECIAL_DAYS and the page time t, and draws the
whole page. Picked by the holiday's "art" key; plain words otherwise.
"""
import math
from datetime import datetime

from engine.bitfonts import F3, F5

W, H = 64, 32


def _sd():
    from engine import specialdays
    return specialdays


def center(f, font, s, y, c):
    Frame = _sd().Frame
    f.text(font, s, 32 - Frame.width(font, s) // 2, y, c)


def _dim(c, k):
    return tuple(max(0, min(255, int(v * k))) for v in c)


ZODIAC = ["RAT", "OX", "TIGER", "RABBIT", "DRAGON", "SNAKE", "HORSE", "GOAT",
          "MONKEY", "ROOSTER", "DOG", "PIG"]


def zodiac(year):
    return ZODIAC[(year - 2020) % 12]


def games_today(d):
    """(short name, ticker name, day number) of the Olympics running on day d, else None.
    Day 0 is the opening ceremony, like the official schedule."""
    import settings
    from datetime import date as _date
    for row in getattr(settings, "OLYMPICS", []):
        opening = _date.fromisoformat(row[2][:10])
        closing = _date.fromisoformat(row[3])
        if opening <= d <= closing:
            return row[0], row[1], (d - opening).days, False
    for row in getattr(settings, "PARALYMPICS", []):
        opening = _date.fromisoformat(row[1])
        closing = _date.fromisoformat(row[2])
        if opening <= d <= closing:
            return row[0], row[0] + " PARALYMPICS", (d - opening).days, True
    return None


def fill_in(text, d):
    """{ZODIAC} -> GOAT, {GAMES} -> LA28, {GAMEDAY} -> 5."""
    text = text.replace("{ZODIAC}", zodiac(d.year))
    g = games_today(d)
    if g:
        text = text.replace("{GAMES}", g[0]).replace("{GAMEDAY}", str(g[2]))
    return text


def _today():
    sd = _sd()
    return sd.home_today()


# ---------------------------------------------------------------- pieces
def disc(f, cx, cy, r, c):
    for y in range(cy - r, cy + r + 1):
        for x in range(cx - r, cx + r + 1):
            if (x - cx) ** 2 + (y - cy) ** 2 <= r * r + r * 0.5:
                f.set(x, y, c)


def apple(f, cx, cy, c=(220, 30, 40)):
    disc(f, cx - 1, cy, 3, c)
    disc(f, cx + 1, cy, 3, c)
    f.set(cx, cy - 4, (110, 70, 30))
    f.set(cx + 1, cy - 5, (60, 180, 60))
    f.set(cx + 2, cy - 5, (60, 180, 60))
    f.set(cx - 2, cy - 1, (255, 140, 140))            # shine


# ---------------------------------------------------------------- pages
def lunar(f, hol, t):
    """Red and gold: two lanterns swaying, HAPPY NEW YEAR / YEAR OF THE GOAT."""
    gold, red = (255, 211, 77), (230, 30, 30)
    for i, cx in enumerate((5, 58)):
        sway = int(round(math.sin(t * 1.6 + i) * 1))
        f.fill(cx, 0, cx, 2, gold)
        for y in range(4, 13):
            half = 3 if 6 <= y <= 10 else 2
            for x in range(cx - half + sway, cx + half + sway + 1):
                f.set(x, y, red if (x - cx - sway) % 2 else (170, 10, 10))
        f.fill(cx - 2 + sway, 3, cx + 2 + sway, 3, gold)
        f.fill(cx - 2 + sway, 13, cx + 2 + sway, 13, gold)
        f.fill(cx + sway, 14, cx + sway, 17, gold)
        f.blend(cx + sway, 8, (255, 220, 120), 0.5)
    center(f, F3, "HAPPY LUNAR", 1, gold)
    center(f, F5, "NEW YEAR", 9, (255, 255, 255))
    yr = f"YEAR OF THE {zodiac(_today().year)}"
    center(f, F5 if _sd().Frame.width(F5, yr) <= 62 else F3, yr, 23, gold)


def scouting(f, hol, t):
    """Scouting's birthday: BE PREPARED, since 1910, Dad & Grandpa Bosetti."""
    khaki, gold, cream = (90, 105, 45), (217, 164, 65), (242, 227, 179)
    f.fill(0, 0, W - 1, 1, gold)
    f.fill(0, H - 2, W - 1, H - 1, gold)
    center(f, F3, "HAPPY BIRTHDAY", 3, cream)
    center(f, F5, "SCOUTING", 10, gold)
    center(f, F3, "SINCE 1910", 19, cream)
    msg = "BE PREPARED" if (t % 8) < 4 else "2 EAGLE SCOUTS"
    center(f, F3, msg, 25, cream if msg[0] == "B" else gold)


def eggs(f, hol, t):
    cols = [(255, 160, 200), (160, 230, 255), (255, 230, 120), (170, 255, 170), (210, 170, 255)]
    for i, cx in enumerate((8, 20, 32, 44, 56)):
        bob = int(round(math.sin(t * 2 + i) * 1))
        c = cols[i]
        for y in range(-5, 6):
            half = int(round(3.4 * math.sqrt(max(0, 1 - (y / 5.5) ** 2)) * (1.05 if y > 0 else 0.9)))
            for x in range(cx - half, cx + half + 1):
                stripe = (y + i) % 4 == 0
                f.set(x, 22 + y + bob, _dim(c, 0.65) if stripe else c)
    center(f, F3, "HAPPY", 1, (255, 225, 240))
    center(f, F5, "EASTER", 7, (255, 225, 240))


def matzah(f, hol, t):
    """Passover: a sheet of matzah with its rows of holes, and the greeting on it."""
    tan, dark = (215, 190, 140), (160, 125, 80)
    f.fill(4, 3, 59, 28, tan)
    for y in range(5, 28, 3):
        for x in range(6, 58, 2):
            f.set(x, y, dark)
    for x in range(4, 60):
        if (x * 7) % 5 == 0:
            f.set(x, 3, dark)
            f.set(x, 28, dark)
    f.fill(6, 7, 57, 24, (16, 42, 85))
    center(f, F3, "HAPPY", 9, (255, 255, 255))
    center(f, F5, "PASSOVER", 16, (232, 217, 181))


def apples_honey(f, hol, t):
    """Rosh Hashanah: apples and a honey jar, SHANAH TOVAH."""
    gold = (255, 211, 77)
    center(f, F5, "SHANAH", 1, gold)
    center(f, F5, "TOVAH", 9, gold)
    apple(f, 12, 24)
    apple(f, 22, 25, (200, 20, 30))
    # honey jar
    f.fill(41, 18, 52, 30, (230, 150, 20))
    f.fill(42, 16, 51, 17, (120, 70, 30))
    f.fill(43, 20, 50, 21, (255, 200, 60))
    drip = int((t * 3) % 6)
    f.set(46, 15 - 0, (255, 190, 40))
    if drip < 4:
        f.set(46, 14 - drip, (255, 190, 40))


def sukkah(f, hol, t):
    """Sukkot: a little hut with a leafy roof and stars showing through."""
    green, wood, white = (60, 170, 70), (150, 100, 50), (255, 255, 255)
    for i in range(9):
        x, y = int((i * 23 + 5) % 60) + 2, int((i * 11) % 7)
        if math.sin(t * 2 + i) > -0.3:
            f.set(x, y, (200, 200, 120))
    for x in range(14, 50):                       # leafy roof (gaps for stars)
        for y in (8, 9, 10):
            if (x * 3 + y) % 5:
                f.set(x, y, green if (x + y) % 3 else (90, 200, 90))
    f.fill(15, 11, 15, 26, wood)
    f.fill(48, 11, 48, 26, wood)
    f.fill(15, 26, 48, 26, wood)
    for i, x in enumerate((21, 27, 34, 41)):     # hanging fruit decorations
        f.fill(x, 11, x, 12 + i % 2, (180, 180, 180))
        f.set(x, 13 + i % 2, [(255, 200, 40), (220, 40, 40), (255, 140, 0), (120, 220, 80)][i])
    center(f, F3, "CHAG SAMEACH", 17, white)
    center(f, F3, "HAPPY SUKKOT", 27, (124, 194, 66))


def quiet(f, hol, t):
    """Yom Kippur: calm and plain - no effects, soft white."""
    soft = (220, 220, 232)
    g = hol["greeting"]
    if _sd().Frame.width(F5, g) <= 62 or " " not in g:
        center(f, F5, g, 9, soft)
        sub_y = 19
    else:                                   # ASH / WEDNESDAY on two lines
        first, rest = g.split(" ", 1)
        center(f, F5, first, 3, soft)
        center(f, F5, rest, 12, soft)
        sub_y = 23
    if hol.get("subtitle"):
        center(f, F3, hol["subtitle"], sub_y, (150, 150, 170))


def good_friday(f, hol, t):
    """Quiet and plain: a simple cross in soft purple, GOOD FRIDAY beside it."""
    purple, soft = (122, 92, 153), (230, 221, 240)
    f.fill(13, 4, 15, 27, purple)          # upright
    f.fill(7, 10, 21, 12, purple)          # crossbar
    f.text(F5, "GOOD", 28, 8, soft)
    f.text(F5, "FRIDAY", 28, 17, soft)


def beat_army(f, hol, t):
    """Army-Navy Game: an anchor, GO NAVY! BEAT ARMY! in blue and gold."""
    gold, white = (242, 196, 107), (255, 255, 255)
    # anchor
    ax = 10
    f.fill(ax, 5, ax, 25, gold)
    f.fill(ax - 4, 9, ax + 4, 9, gold)
    for (x, y) in ((ax - 1, 3), (ax, 2), (ax + 1, 3), (ax - 1, 4), (ax + 1, 4)):
        f.set(x, y, gold)
    for k in range(7):
        f.set(ax - 1 - k, 25 - (k * k) // 6, gold)
        f.set(ax + 1 + k, 25 - (k * k) // 6, gold)
    f.set(ax - 7, 15, gold); f.set(ax + 7, 15, gold)
    blink = (t % 1.0) < 0.6
    f.text(F5, "GO", 24, 2, white)
    f.text(F5, "NAVY!", 24, 10, gold)
    f.text(F5, "BEAT", 24, 18, white if blink else gold)
    f.text(F3, "ARMY!", 24, 26, white if blink else gold)


def olympics(f, hol, t):
    """The Olympic Games: a torch with a live flame, the host, and which day it is.
    For LA, a line for Great-Grandpa Dallas (gold, LA 1932)."""
    d = _today()
    g = games_today(d)
    gold, white = (242, 196, 107), (255, 255, 255)
    # torch
    tx = 5
    f.fill(tx - 1, 16, tx + 1, 30, (190, 190, 200))
    f.fill(tx - 3, 13, tx + 3, 15, gold)
    for i in range(14):
        fl = math.sin(t * 9 + i * 1.3)
        y = 12 - i // 2
        w = max(0, 3 - i // 4)
        for x in range(tx - w, tx + w + 1):
            c = (255, 220, 80) if i < 5 else ((255, 140, 0) if i < 10 else (255, 70, 0))
            if (x + i) % 2 == 0 or fl > 0:
                f.set(x + (1 if fl > 0.7 else 0), y, c)
    if not g:
        center(f, F5, "OLYMPICS", 12, white)
        return
    short, name, day, para = g
    la = short.startswith("LA")
    f.text(F3, "PARALYMPICS" if para else "OLYMPIC GAMES", 12, 1, gold)
    if la and not para and (t % 9) >= 6:
        f.text(F3, "GREAT-GRANDPA", 12, 9, white)
        f.text(F3, "DALLAS BIXLER", 12, 16, gold)
        f.text(F3, "GOLD LA 1932", 12, 24, white)
        return
    host = {"LA28": "BACK IN LA!", "FRA30": "FRENCH ALPS", "BNE32": "BRISBANE", "SLC34": "SALT LAKE"}.get(short, short)
    f.text(F3, host, 12, 9, white)
    f.text(F5, "DAY " + str(day) if day else "OPENING", 12, 16, gold)
    f.text(F3, "CEREMONY" if day == 0 else "GO TEAM USA!", 12, 26, white)


COLISEUM_LINES = [
    "LA MEMORIAL COLISEUM",
    "OLYMPIC GAMES 1932 - 1984 - 2028",
    "GREAT-GRANDPA DALLAS WON GOLD HERE - AUG 11 1932",
]


GOLD_DAY_LINES = [
    "GOLD MEDAL DAY",
    "AUG 11 1932: GREAT-GRANDPA DALLAS WON OLYMPIC GOLD ON THE HORIZONTAL BAR",
    "RIGHT HERE AT THE LA MEMORIAL COLISEUM",
]


def gold_day(f, hol, t):
    coliseum(f, t, GOLD_DAY_LINES)


def palm(f, hol, t):
    """Palm Sunday: two crossed palm fronds, PALM SUNDAY beside them."""
    green, dark, soft = (93, 187, 74), (50, 120, 40), (242, 240, 216)
    for k, dx in enumerate((-0.35, 0.35)):
        sway = math.sin(t * 1.5 + k) * 0.8
        for i in range(25):
            x = 12 + dx * i + sway * i / 25
            y = 28 - i
            f.set(int(round(x)), y, dark)
            if 3 < i < 23:
                ln = 1 + min(i - 3, 23 - i) // 3
                for j in range(1, ln + 1):
                    f.set(int(round(x)) - j, y - j // 2, green)
                    f.set(int(round(x)) + j, y - j // 2, green)
    f.text(F5, "PALM", 28, 7, soft)
    f.text(F5, "SUNDAY", 26, 17, soft)


def dallas_birthday(f, t):
    """Feb 17: Great-Grandpa Dallas's birthday, with his gold medal."""
    import settings
    from pages.olympics import draw_medal, _scroll
    gold, white, navy = (242, 196, 107), (255, 255, 255), (11, 31, 79)
    draw_medal(f, 6, 14, t)
    f.text(F3, "HAPPY BDAY", 14, 1, gold)
    f.text(F3, "GREAT-GRANDPA", 13, 8, white)
    f.text(F5, "DALLAS", 18, 15, gold)
    f.fill(0, 26, 63, 31, navy)
    _scroll(f, settings.DALLAS_BIRTHDAY["ticker"], t, gold)


def coliseum(f, t, lines=None):
    """The LA Memorial Coliseum peristyle at night, the Olympic cauldron burning on top,
    and a caption ticker along the bottom."""
    W, H = 64, 32
    # night sky: deep blue fading to dusk at the horizon, a few stars
    for y in range(26):
        k = y / 25
        c = (int(6 + 50 * k * k), int(10 + 20 * k), int(40 + 50 * k))
        for x in range(W):
            f.set(x, y, c)
    for (x, y, ph) in ((4, 2, 0), (13, 5, 2), (50, 3, 4), (58, 7, 1), (20, 1, 3), (44, 1, 5)):
        if math.sin(t * 2 + ph) > -0.4:
            f.set(x, y, (200, 200, 230))
    stone, shade = (214, 178, 122), (150, 118, 76)
    gap = (24, 26, 58)
    # colonnade wings
    for x0, x1 in ((1, 21), (43, 62)):
        f.fill(x0, 16, x1, 17, stone)          # entablature
        f.fill(x0, 18, x1, 25, stone)
        x = x0 + 1
        while x + 2 <= x1 - 1:
            f.fill(x, 20, x + 2, 25, gap)       # small arch openings
            f.set(x + 1, 19, gap)
            x += 5
        f.fill(x0, 16, x1, 16, (240, 210, 150))
    # central arch block
    f.fill(22, 12, 42, 25, stone)
    f.fill(22, 12, 42, 13, (240, 210, 150))
    f.fill(22, 14, 42, 14, shade)
    f.fill(27, 19, 37, 25, gap)                 # the great arch
    for x, y in ((28, 18), (29, 17), (30, 17), (31, 16), (32, 16), (33, 16), (34, 17), (35, 17), (36, 18)):
        f.fill(x, y, x, 18, gap)
    f.fill(24, 16, 25, 25, shade)               # pilasters
    f.fill(39, 16, 40, 25, shade)
    # cauldron: a wide bowl on a short stem, sitting on the great arch
    f.fill(27, 9, 37, 9, (245, 205, 110))
    f.fill(28, 10, 36, 10, (200, 155, 70))
    f.fill(30, 11, 34, 11, shade)
    # the flame: wide at the bowl, licking up and swaying
    for i in range(9):
        y = 8 - i
        w = (4, 4, 4, 3, 3, 2, 2, 1, 0)[i]
        sway = int(round(math.sin(t * 6 + i * 0.8) * i / 4))
        for x in range(32 - w, 33 + w):
            edge = abs(x - 32) == w
            if edge and math.sin(t * 13 + x * 2.1 + i) < 0:
                continue
            core = abs(x - 32) < w - 1
            c = (255, 240, 160) if (i < 3 and core) else ((255, 170, 30) if i < 5 else (255, 90, 0))
            f.set(x + sway, y, c)
    if math.sin(t * 9) > 0.3:
        f.set(32 + int(math.sin(t * 3) * 2), 0, (255, 60, 0))
    # glow on the arch top
    for x in range(27, 38):
        f.blend(x, 12, (255, 160, 40), 0.4)
    # ground and caption ticker
    f.fill(0, 26, W - 1, H - 1, (8, 8, 16))
    # each line scrolls through once at 20 px a second, then the next
    Frame = _sd().Frame
    lines = lines or COLISEUM_LINES
    spans = [Frame.width(F3, m) + W for m in lines]
    pos = (t * 20) % sum(spans)
    for msg, span in zip(lines, spans):
        if pos < span:
            f.text(F3, msg, W - int(pos), 26, (242, 196, 107))
            break
        pos -= span


def pirate(f, hol, t):
    """A Jolly Roger on a pole and AHOY CAPTAIN BILLY!"""
    white, gold = (240, 240, 240), (242, 196, 107)
    f.fill(4, 1, 4, 30, (140, 100, 60))
    wave = [int(round(math.sin(t * 3 + x * 0.5))) for x in range(18)]
    for x in range(18):
        for y in range(12):
            f.set(5 + x, 2 + y + wave[x], (25, 25, 25) if 0 < y < 11 else (60, 60, 60))
    # skull + crossbones
    disc(f, 13, 6 + wave[8], 2, white)
    f.set(12, 6 + wave[7], (25, 25, 25))
    f.set(14, 6 + wave[9], (25, 25, 25))
    for k in range(-3, 4):
        f.set(13 + k, 10 + k // 2 + wave[8], white)
        f.set(13 + k, 10 - k // 2 + wave[8], white)
    f.text(F5, "AHOY", 30, 4, gold)
    f.text(F3, "CAPTAIN", 30, 14, white)
    f.text(F5, "BILLY!", 27, 21, gold)


def boating(f, hol, t):
    """Opening Day of boating season: a ship dressed in signal flags, a boat underway."""
    from engine.nautical import draw_signal
    letters = "ABCDEFGHIJ"
    for i, L in enumerate(letters):              # flags strung along a line
        y = 1 + int(round(2 - 2 * math.sin(math.pi * i / (len(letters) - 1))))
        draw_signal(f, L, 1 + i * 6 + (1 if i else 0), y, 5)
    center(f, F3, "OPENING DAY", 10, (255, 255, 255))
    center(f, F3, "BOATING SEASON", 17, (242, 196, 107))
    # water and a little boat
    for x in range(W):
        f.set(x, 29 + (1 if (x + int(t * 6)) % 8 < 4 else 0), (40, 110, 200))
    bx = int(t * 8) % 84 - 20
    f.fill(bx, 26, bx + 12, 27, (240, 240, 240))
    f.fill(bx + 1, 28, bx + 11, 28, (200, 40, 40))
    f.fill(bx + 4, 24, bx + 8, 25, (240, 240, 240))
    f.fill(bx + 6, 20, bx + 6, 23, (160, 160, 160))
    f.set(bx + 7, 20, (242, 196, 107))


def season(f, hol, t):
    """First day of a season: the name, and Seattle's sunrise and sunset that day."""
    from engine import sky
    d = _today()
    rise, sset = sky.sun_times(d)
    tc, ac = _sd().rgb(hol["text"]), _sd().rgb(hol["accent"])
    name = hol["greeting"].replace("FIRST DAY OF ", "")
    center(f, F3, "FIRST DAY OF", 1, tc)
    center(f, F5, name, 7, ac if sum(ac) > 300 else tc)
    def hm(x):
        return f"{x.hour % 12 or 12}:{x.minute:02d}"
    f.text(F3, "SUNRISE", 2, 15, tc)
    f.text(F3, hm(rise), 62 - _sd().Frame.width(F3, hm(rise)), 15, (255, 220, 120))
    f.text(F3, "SUNSET", 2, 21, tc)
    f.text(F3, hm(sset), 62 - _sd().Frame.width(F3, hm(sset)), 21, (255, 150, 80))
    if hol.get("astro") == "winter":
        msg = "LIGHT RETURNS!" if (t % 6) >= 3 else "SHORTEST DAY"
        center(f, F3, msg, 27, (255, 255, 255))
    elif hol.get("astro") == "summer":
        center(f, F3, "LONGEST DAY", 27, (255, 255, 255))


def full_moon(f, name, t):
    """FULL MOON TONIGHT with the moon's name, a glowing moon rising."""
    f.bg = (4, 6, 22)
    for i in range(16):
        x, y = int((i * 37 + 3) % 64), int((i * 13 + 1) % 30)
        if math.sin(t * 1.8 + i * 2.3) > 0:
            f.set(x, y, (110, 110, 150))
    cx, cy = 11, 16
    for y in range(cy - 11, cy + 12):
        for x in range(cx - 11, cx + 12):
            d2 = (x - cx) ** 2 + (y - cy) ** 2
            if 64 < d2 <= 121:
                f.blend(x, y, (255, 245, 200), 0.10)
    disc(f, cx, cy, 8, (235, 232, 210))
    for (dx, dy, r) in ((-3, -2, 2), (3, 2, 2), (1, -5, 1), (-4, 4, 1), (4, -3, 1)):
        disc(f, cx + dx, cy + dy, r, (200, 196, 175))
    Frame = _sd().Frame
    f.text(F3, "FULL MOON", 24, 4, (255, 245, 200))
    font = F5 if Frame.width(F5, name) <= 40 else F3
    f.text(font, name, 24, 12 if font is F5 else 13, (255, 255, 255))
    f.text(F3, "MOON", 24, 22, (180, 190, 230))


ART = {"lunar": lunar, "scouting": scouting, "eggs": eggs, "matzah": matzah,
       "apples_honey": apples_honey, "sukkah": sukkah, "quiet": quiet, "pirate": pirate, "good_friday": good_friday, "beat_army": beat_army, "gold_day": gold_day, "palm": palm, "olympics": olympics,
       "boating": boating, "season": season}
