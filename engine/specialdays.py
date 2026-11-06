"""
Special days, ported from the old clock (test32.py) with the drawing code
copied as-is: holiday field colors + effects, flag-stripe days, birthdays,
the anniversary page, April Fools, trash day and the countdown.

The dates and messages themselves live in settings.py (special days section).
The old clock drew into a "Frame" (a little picture in memory that it then
sent to the panel); that Frame is copied here too, plus flush() to send it.
"""
import math
from datetime import date, datetime, timedelta
from zoneinfo import ZoneInfo

import settings
from settings import (SPECIAL_DAYS, STRIPED_DAYS, BIRTHDAYS, APRIL_FOOLS_DATE,
                      ANNIVERSARY_YEAR, COUNTDOWN_SKIP, TRASH_WEEKDAY, RECYCLING_ANCHOR)
from engine.bitfonts import F3, F5
from engine.teamcolors import hexc as rgb, lum, mix, display_color

W, H = 64, 32
HOME = ZoneInfo(settings.HOME[2])
AMBER = rgb("#FFB000")
WHITE = rgb("#F2F2F2")
CYAN = rgb("#40D0FF")
MARQUEE_HOLD = 1.5
MARQUEE_PX_PER_SEC = 14
_now = None     # set by the pages each frame, so --at fake dates work everywhere


def dim(night=False):
    return (190, 190, 190) if night else (122, 122, 122)


def home_today(now=None):
    return (now or _now or datetime.now(HOME)).astimezone(HOME).date()


# ======================================================================
# frame (copied from test32.py)
# ======================================================================
class Frame:
    def __init__(self):
        self.px = {}
        self.clip = (0, W - 1)
        self.bg = None   # field color behind everything (special days)

    def clear(self):
        self.px.clear()
        self.clip = (0, W - 1)
        self.bg = None

    def get(self, x, y):
        return self.px.get((x, y)) or self.bg or (0, 0, 0)

    def blend(self, x, y, c, a):
        if 0 <= x < W and 0 <= y < H:
            base = self.get(x, y)
            self.set(x, y, tuple(int(b + (v - b) * a) for b, v in zip(base, c)))

    def set(self, x, y, c):
        if self.clip[0] <= x <= self.clip[1] and 0 <= y < H:
            self.px[(x, y)] = c

    def text(self, font, s, x, y, c, scale=1):
        """Draw s at (x, y); returns the horizontal advance."""
        cx = x
        for ch in s:
            g = font.get(ch, font[" "])
            w = len(g[0])
            for r, row in enumerate(g):
                for q, bit in enumerate(row):
                    if bit == "1":
                        for a in range(scale):
                            for b in range(scale):
                                self.set(cx + q * scale + a, y + r * scale + b, c)
            cx += (w + 1) * scale
        return cx - x

    @staticmethod
    def width(font, s, scale=1):
        if not s:
            return 0
        return sum((len(font.get(ch, font[" "])[0]) + 1) * scale for ch in s) - scale

    def icon(self, name, x, y, scale=1):
        for i, row in enumerate(ICONS.get(name, [])):
            for j, ch in enumerate(row):
                if ch != ".":
                    for a in range(scale):
                        for b in range(scale):
                            self.set(x + j * scale + a, y + i * scale + b, ICON_COLORS[ch])

    def border(self, c):
        for x in range(W):
            self.set(x, 0, c)
            self.set(x, H - 1, c)
        for y in range(H):
            self.set(0, y, c)
            self.set(W - 1, y, c)

    def fill(self, x0, y0, x1, y1, c):
        for x in range(x0, x1 + 1):
            for y in range(y0, y1 + 1):
                self.set(x, y, c)

    def flush(self, canvas):
        """Send this picture to the panel canvas (BILLY5000 addition)."""
        if self.bg:
            canvas.Fill(*self.bg)
        for (x, y), (r, g, b) in self.px.items():
            canvas.SetPixel(x, y, r, g, b)


def _bottom(f, segs, t_page, x0=2):
    full = "".join(s for s, _ in segs)
    w = Frame.width(F3, full)
    space = 61 - x0 + 1
    f.clip = (x0, 61)
    if w <= space:
        x = x0 + (space - w) // 2
        for s, c in segs:
            x += f.text(F3, s, x, 26, c)
    else:
        period = w + 16
        off = int(max(0.0, t_page - MARQUEE_HOLD) * MARQUEE_PX_PER_SEC) % period
        for start in (x0 - off, x0 - off + period):
            x = start
            for s, c in segs:
                x += f.text(F3, s, x, 26, c)
    f.clip = (0, 63)


# ======================================================================
# special days (copied from test32.py)
# ======================================================================
def easter_date(y):
    a, b, c = y % 19, y // 100, y % 100
    d, e = b // 4, b % 4
    g = (8 * b + 13) // 25
    h = (19 * a + b - d - g + 15) % 30
    i, k = c // 4, c % 4
    l = (32 + 2 * e + 2 * i - h - k) % 7
    m = (a + 11 * h + 22 * l) // 451
    month = (h + l - 7 * m + 114) // 31
    day = (h + l - 7 * m + 114) % 31 + 1
    return date(y, month, day)


def nth_weekday(y, month, wd, n):
    if n > 0:
        d = date(y, month, 1)
        d += timedelta(days=(wd - d.weekday()) % 7)
        return d + timedelta(weeks=n - 1)
    nxt = date(y + (month == 12), month % 12 + 1, 1)
    d = nxt - timedelta(days=1)
    return d - timedelta(days=(d.weekday() - wd) % 7)


def rule_date_this_year(entry, year):
    if "rule" in entry:
        r = entry["rule"]
        if "easter" in r:
            return easter_date(year) + timedelta(days=r["easter"])
        return nth_weekday(year, *r["nth_weekday"])
    if "date" in entry:
        m, d = map(int, entry["date"].split("-"))
        return date(year, m, d)
    return None


def field_day_for(d):
    for sd in SPECIAL_DAYS:
        if "start" in sd:
            sm, sdd = map(int, sd["start"].split("-"))
            em, ed = map(int, sd["end"].split("-"))
            s = date(d.year - (1 if (sm, sdd) > (d.month, d.day) else 0), sm, sdd)
            e = date(s.year + (1 if em < sm else 0), em, ed)
            if s <= d <= e:
                return sd
        elif rule_date_this_year(sd, d.year) == d:
            return sd
    return None


def striped_day_for(d):
    for sd in STRIPED_DAYS:
        if rule_date_this_year(sd, d.year) == d:
            return sd
    return None


def is_recycling_week(d):
    monday = d - timedelta(days=d.weekday())
    return (monday - RECYCLING_ANCHOR).days % 14 == 0


def trash_items_for(d):
    """What goes out if d is trash day; None on every other day."""
    if d.weekday() != TRASH_WEEKDAY:
        return None
    items = ["GARBAGE", "COMPOST"]
    if is_recycling_week(d):
        items.append("RECYCLING")
    return items


def trash_page_for(d):
    if d.weekday() == TRASH_WEEKDAY:
        return ("TODAY", trash_items_for(d))
    if (d + timedelta(days=1)).weekday() == TRASH_WEEKDAY:
        return ("TOMORROW", trash_items_for(d + timedelta(days=1)))
    return None


def special_pages_for(d):
    """Today's extra pages, in the order test64.py shows them."""
    pages = []
    trash = trash_page_for(d)
    if trash:
        pages.append(("trash", trash))
    if (d.month, d.day) == APRIL_FOOLS_DATE:
        pages.append(("aprilfools", None))
    for msg in BIRTHDAYS.get((d.month, d.day), []):
        pages.append(("anniversary" if "ANNIVERSARY" in msg else "birthday", msg))
    sd = field_day_for(d)
    if sd:
        pages.append(("special", sd))
    st = striped_day_for(d)
    if st:
        pages.append(("striped", st))
    return pages


# ---------------------------------------------------------------- countdown
def _who(msg):
    """'HAPPY BIRTHDAY AUNT SARAH!' -> 'AUNT SARAH'; 'GRANDPA BOSETTI BIRTHDAY' -> 'GRANDPA BOSETTI'."""
    s = msg.replace("!", "").strip()
    for lead in ("HAPPY BIRTHDAY ", "HAPPY ANNIVERSARY "):
        if s.startswith(lead):
            s = s[len(lead):]
    if s.endswith(" BIRTHDAY"):
        s = s[: -len(" BIRTHDAY")]
    return s.strip()


def _holiday_name(sd):
    if "greeting" in sd:  # field days: their greeting without HAPPY/MERRY
        g = sd["greeting"].replace("!", "")
        for lead in ("HAPPY ", "MERRY "):
            if g.startswith(lead):
                g = g[len(lead):]
        return g
    return sd["name"]     # striped days: JULY 4TH, FLAG DAY, ...


def _next_on_or_after(month, day, d):
    for y in (d.year, d.year + 1):
        try:
            nd = date(y, month, day)
        except ValueError:  # Feb 29
            continue
        if nd > d:
            return nd
    return None


def next_special(d):
    """Soonest special day after d -> {date, kind, name, color}, or None."""
    found = []
    for sd in SPECIAL_DAYS + STRIPED_DAYS:
        if "start" in sd:     # a season (Christmas): count down to its last day
            m, dd = map(int, sd["end"].split("-"))
            nd = _next_on_or_after(m, dd, d)
        else:
            nd = next((x for x in (rule_date_this_year(sd, d.year), rule_date_this_year(sd, d.year + 1))
                       if x and x > d), None)
        if not nd:
            continue
        if "stripes" in sd:
            col = max((rgb(s) for s in sd["stripes"]), key=lambda c_: lum(c_) if lum(c_) < 230 else 0)
        else:
            col = rgb(sd["accent"]) if lum(rgb(sd["accent"])) > 45 else rgb(sd["text"])
        found.append((nd, "HOLIDAY", _holiday_name(sd), display_color(col)))
    for (m, dd), msgs in BIRTHDAYS.items():
        nd = _next_on_or_after(m, dd, d)
        for msg in msgs:
            if "ANNIVERSARY" in msg:
                found.append((nd, "ANNIVERSARY", _who(msg), ANNIV_GOLD))
            else:
                found.append((nd, "BIRTHDAY", _who(msg), (64, 184, 255)))
    nd = _next_on_or_after(*APRIL_FOOLS_DATE, d)
    found.append((nd, "HOLIDAY", "APRIL FOOLS", (48, 208, 96)))
    found = [x for x in found if x[0] and f"{x[0]:%m-%d}" not in COUNTDOWN_SKIP]
    if not found:
        return None
    soonest = min(x[0] for x in found)
    same = [x for x in found if x[0] == soonest]
    # two birthdays on one day -> "BILLY & JACK LEE"
    kind, color = same[0][1], same[0][3]
    names = [x[2] for x in same if x[1] == kind]
    return {"date": soonest, "kind": kind, "name": " & ".join(names), "color": color}


# ---------------------------------------------------------------- effects (32 rows tall)
def rnd(i):
    x = (i * 2654435761 + 1013904223) & 0xFFFFFFFF
    x ^= x >> 13
    x = (x * 1274126177) & 0xFFFFFFFF
    return (x & 0xFFFF) / 65535.0


def draw_effect(f, effect, t, accent):
    if effect == "snow":
        for i in range(20):
            sp = 2 + rnd(i) * 4
            x = int(rnd(i + 99) * W + math.sin(t * 0.8 + i) * 2) % W
            y = int(rnd(i + 7) * H + t * sp) % H
            f.blend(x, y, (220, 230, 255), 0.35 + rnd(i + 3) * 0.4)
    elif effect == "fireworks":
        for b in range(2):
            period = 2.2
            tb = t + b * 1.1
            k = int(tb / period)
            p = (tb % period) / period
            cx, cy = 10 + rnd(k * 7 + b) * 44, 6 + rnd(k * 13 + b) * 14
            col = [accent, (255, 255, 255), (80, 160, 255), (255, 210, 60)][int(rnd(k + b * 5) * 4) % 4]
            rad, fade = p * 8, max(0.0, 1 - p)
            for j in range(12):
                a = j / 12 * math.tau
                f.blend(int(cx + math.cos(a) * rad), int(cy + math.sin(a) * rad + p * p * 3), col, fade * 0.9)
    elif effect == "hearts":
        heart = ["0101", "1111", "0110"]
        for i in range(5):
            x = int(rnd(i) * 60 + math.sin(t + i) * 2)
            y = H - 1 - int((rnd(i + 5) * H + t * 4) % (H + 6))
            for r, row in enumerate(heart):
                for q, bit in enumerate(row):
                    if bit == "1":
                        f.blend(x + q, y + r, accent, 0.45)
    elif effect == "leaves":
        cols = [(210, 105, 30), (180, 60, 20), (230, 160, 40)]
        for i in range(12):
            x = int(rnd(i) * W + math.sin(t * 1.3 + i) * 3) % W
            y = int(rnd(i + 11) * H + t * (2 + rnd(i + 2) * 3)) % H
            f.blend(x, y, cols[i % 3], 0.55)
    elif effect == "sparkle":
        for i in range(14):
            ph = (t * (0.6 + rnd(i) * 0.8) + rnd(i + 40)) % 1
            if ph < 0.35:
                f.blend(int(rnd(i + 1) * W), int(rnd(i + 2) * H), accent,
                        math.sin(ph / 0.35 * math.pi) * 0.7)


# ---------------------------------------------------------------- greeting layout
FILLER = {"HAPPY", "BIRTHDAY", "ANNIVERSARY", "MERRY", "FELIZ", "DAY"}


def _h(lines):
    return sum(7 if fnt is F5 else 5 for fnt, _ in lines) + 2 * (len(lines) - 1)


def fit_lines(words, max_w=60, max_h=26):
    """Lay out a greeting for a 64x32 panel. Returns [(font, text), ...].
    Big 5x7 font for the words that matter (names, holidays); filler words like
    HAPPY / BIRTHDAY drop to the small 3x5 font and share a line when they fit."""
    # 1. wrap by big-font width; a word too long for the big font sits alone, small
    lines, cur = [], ""
    for w in words:
        trial = (cur + " " + w).strip()
        if cur and Frame.width(F5, trial) > max_w:
            lines.append(cur)
            cur = w
        else:
            cur = trial
    if cur:
        lines.append(cur)
    out = [[F5 if Frame.width(F5, s) <= max_w else F3, s] for s in lines]

    # 2. shrink filler-only lines when something more important is on the page
    def filler(s):
        return all(w.strip("!.,") in FILLER for w in s.split())
    if any(not filler(s) for _, s in out):
        for ln in out:
            if filler(ln[1]):
                ln[0] = F3

    # 3. merge neighbouring small lines that fit together
    def merge(rows):
        out_ = []
        for fnt, s in rows:
            if out_ and fnt is F3 and out_[-1][0] is F3 and \
                    Frame.width(F3, out_[-1][1] + " " + s) <= max_w:
                out_[-1][1] += " " + s
            else:
                out_.append([fnt, s])
        return out_
    out = merge(out)

    # 4. still too tall? shrink big lines from the bottom up, re-merging as we go
    for i in range(len(out) - 1, -1, -1):
        if _h(out) <= max_h or i >= len(out):
            continue
        out[i][0] = F3
        out = merge(out)
    result = [(fnt, s) for fnt, s in out]
    if _h(result) <= max_h:
        return result

    # 5. last resort: everything small
    lines, cur = [], ""
    for w in words:
        trial = (cur + " " + w).strip()
        if cur and Frame.width(F3, trial) > max_w:
            lines.append(cur)
            cur = w
        else:
            cur = trial
    return [(F3, s) for s in lines + ([cur] if cur else [])]


def draw_lines(f, lines, color, top=0, bottom=H):
    total = sum(7 if fnt is F5 else 5 for fnt, _ in lines) + 2 * (len(lines) - 1)
    y = top + (bottom - top - total) // 2
    for fnt, s in lines:
        f.text(fnt, s, 32 - Frame.width(fnt, s) // 2, y, color)
        y += (7 if fnt is F5 else 5) + 2


# ---------------------------------------------------------------- special pages
def render_special(f, sd, t):
    """Holiday greeting: field color, effect, accent bars, greeting."""
    accent = rgb(sd["accent"])
    f.bg = rgb(sd["field"])
    draw_effect(f, sd.get("effect"), t, accent)
    bar = mix((0, 0, 0), accent, 0.6)
    f.fill(0, 0, W - 1, 1, bar)
    f.fill(0, H - 2, W - 1, H - 1, bar)
    draw_lines(f, fit_lines(sd["greeting"].split()), rgb(sd["text"]), top=2, bottom=H - 2)


def render_striped(f, sd, t):
    """Flag-style: three bands, each word centered in its own band."""
    stripes = [rgb(s) for s in sd["stripes"]]
    n = len(stripes)
    edges = [round(i * H / n) for i in range(n + 1)]   # 0, 11, 21, 32
    for i, col in enumerate(stripes):
        f.fill(0, edges[i], W - 1, edges[i + 1] - 1, col)
    for i, (word, col) in enumerate(zip(sd["words"], sd["text"])):
        band_top, band_h = edges[i], edges[i + 1] - edges[i]
        fnt = F5 if Frame.width(F5, word) <= 62 else F3
        th = 7 if fnt is F5 else 5
        f.text(fnt, word, 32 - Frame.width(fnt, word) // 2, band_top + (band_h - th) // 2, rgb(col))


BIRTHDAY_FIELD = (255, 255, 255)
BIRTHDAY_TEXT = (32, 80, 208)
BIRTHDAY_CONFETTI = [(255, 80, 80), (255, 204, 0), (48, 192, 96), (176, 96, 255),
                     (255, 144, 32), (64, 184, 255), (255, 112, 176)]
# confetti kept to the edges so it never sits on the words
CONFETTI_DOTS = [(1, 0), (9, 1), (18, 0), (28, 1), (37, 0), (46, 1), (55, 0), (62, 1),
                 (0, 24), (62, 25), (1, 29), (11, 30), (19, 29), (44, 29), (52, 30), (61, 29)]


def render_birthday(f, message, t):
    f.bg = BIRTHDAY_FIELD
    for i, (dx, dy) in enumerate(CONFETTI_DOTS):
        col = BIRTHDAY_CONFETTI[i % len(BIRTHDAY_CONFETTI)]
        bob = int(round(math.sin(t * 1.5 + i) * 0.6))
        f.fill(dx, max(0, dy + bob), dx + 1, min(H - 1, dy + bob + 1), col)
    words = message.replace("!", "").split()
    lines = fit_lines(words, max_w=58, max_h=23)
    draw_lines(f, lines, BIRTHDAY_TEXT, top=2, bottom=26)
    # small cake, bottom center, candles flicker
    cx = 32
    f.fill(cx - 5, 29, cx + 4, 31, (235, 200, 220))
    f.fill(cx - 5, 28, cx + 4, 28, (255, 140, 180))
    for k, dx in enumerate((-4, -1, 2)):
        f.set(cx + dx, 27, (255, 220, 120))
        flick = 0.7 + 0.3 * math.sin(t * 8 + k)
        f.set(cx + dx, 26, tuple(int(v * flick) for v in (255, 200, 60)))


TRASH_ROWS = [  # label, color, 7x6 icon
    ("GARBAGE",   (150, 150, 155), ["..###..", "#######", ".#####.", ".#.#.#.", ".#.#.#.", ".#####."]),
    ("RECYCLING", (70, 140, 230),  ["...#...", "..#.#..", ".#...#.", "#.....#", "#######", "......."]),
    ("COMPOST",   (80, 170, 90),   ["....##.", "..####.", ".#####.", ".####..", "..##...", "#......"]),
]
CHECK = ["....#", "...#.", "#.#..", ".#..."]


def render_trash(f, arg, t):
    """Header + one row per bin: icon, name, and a check (goes out) or dash (not)."""
    when, items = arg
    f.text(F5, "TRASH", 1, 1, AMBER)
    f.text(F3, when, 63 - Frame.width(F3, when), 2, CYAN if when == "TODAY" else WHITE)
    for i, (name, col, icon) in enumerate(TRASH_ROWS):
        y = 10 + i * 7
        on = name in items
        shade = col if on else mix((0, 0, 0), col, 0.3)
        for r, row in enumerate(icon):
            for q, ch in enumerate(row):
                if ch == "#":
                    f.set(3 + q, y + r, shade)
        f.text(F3, name, 13, y + 1, (220, 220, 220) if on else (65, 65, 65))
        if on:
            for r, row in enumerate(CHECK):
                for q, ch in enumerate(row):
                    if ch == "#":
                        f.set(55 + q, y + 1 + r, (70, 230, 100))
        else:
            f.fill(55, y + 3, 59, y + 3, (70, 70, 75))


def render_countdown(f, nxt, now, t_page, night=False):
    """Kind on top; big number of days with the date beside it; who/what below."""
    today = home_today(now)
    days = (nxt["date"] - today).days
    col = nxt["color"]
    f.text(F3, nxt["kind"], 32 - Frame.width(F3, nxt["kind"]) // 2, 2, col)
    if days == 1:
        f.text(F5, "TOMORROW", 32 - Frame.width(F5, "TOMORROW") // 2, 13, WHITE)
    else:
        num = str(days)
        nw = Frame.width(F5, num, 2)
        ds = nxt["date"].strftime("%b ").upper() + str(nxt["date"].day)
        side = max(Frame.width(F3, ds), Frame.width(F3, "DAYS"))
        x = 32 - (nw + 4 + side) // 2
        f.text(F5, num, x, 9, WHITE, 2)
        f.text(F3, ds, x + nw + 4, 11, dim(night))
        f.text(F3, "DAYS", x + nw + 4, 18, dim(night))
    _bottom(f, [(nxt["name"], col)], t_page)   # centered; scrolls only if too long


ANNIV_FIELD = (8, 22, 52)       # house navy
ANNIV_GOLD = (201, 162, 39)     # house brass
ANNIV_CREAM = (245, 230, 200)
ANNIV_RED = (220, 40, 70)


def _ring(f, cx, cy, r, color, skip=None):
    """Pixel circle outline; skip = predicate(x, y) for the over/under weave."""
    pts = set()
    for a in range(0, 360, 2):
        x = int(round(cx + r * math.cos(math.radians(a))))
        y = int(round(cy + r * math.sin(math.radians(a))))
        pts.add((x, y))
    for x, y in pts:
        if not (skip and skip(x, y)):
            f.set(x, y, color)


def _heart(f, x, y, color):
    for r, row in enumerate(["0101", "1111", "0110"]):
        for q, bit in enumerate(row):
            if bit == "1":
                f.set(x + q, y + r, color)


def render_anniversary(f, message, t):
    """Navy and brass, two interlocked rings, names in gold -- not a birthday party."""
    f.bg = ANNIV_FIELD
    lx, rx, cy, r = 27, 36, 6, 5
    light = mix(ANNIV_GOLD, (255, 240, 190), 0.35)
    _ring(f, lx, cy, r, light)
    # right ring drawn second, but tucked UNDER the left ring along the top crossing
    _ring(f, rx, cy, r, ANNIV_GOLD,
          skip=lambda x, y: y < cy and (x - lx) ** 2 + (y - cy) ** 2 <= (r + 0.6) ** 2)
    for i, (sx, sy) in enumerate([(4, 3), (58, 4), (11, 9), (52, 10)]):  # twinkles
        ph = (t * 0.9 + i * 0.37) % 1
        if ph < 0.4:
            f.blend(sx, sy, (255, 255, 255), math.sin(ph / 0.4 * math.pi))
    who = _who(message)
    lines = fit_lines(who.split(), max_w=60, max_h=9)
    draw_lines(f, lines, ANNIV_GOLD, top=13, bottom=21)
    bottom = "ANNIVERSARY"
    if ANNIVERSARY_YEAR and int(t / 3) % 2:
        n = home_today().year - ANNIVERSARY_YEAR
        bottom = f"{n} YEAR" if n == 1 else f"{n} YEARS"
    bw = Frame.width(F3, bottom)
    bx = 32 - bw // 2
    f.text(F3, bottom, bx, 25, ANNIV_CREAM)
    _heart(f, bx - 7, 26, ANNIV_RED)
    _heart(f, bx + bw + 3, 26, ANNIV_RED)


APRIL_FOOLS_WORDS = ["S1GNL L0ST", "RECONNECTING..."]
APRIL_FOOLS_RAINBOW = [(255, 64, 64), (255, 204, 0), (48, 208, 96), (64, 200, 255), (162, 89, 255)]


def render_april_fools(f, t):
    if t < 2.5:
        word = APRIL_FOOLS_WORDS[int(t / 0.3) % len(APRIL_FOOLS_WORDS)]
        draw_lines(f, fit_lines(word.split()), (255, 32, 32))
    else:
        col = APRIL_FOOLS_RAINBOW[int((t - 2.5) / 0.2) % len(APRIL_FOOLS_RAINBOW)]
        draw_lines(f, fit_lines(["APRIL", "FOOLS!"]), col)
