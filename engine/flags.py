"""
Flags drawn as 64x32 pixel art for the flag quiz.

Each flag is a small function that paints a Frame (the old clock's in-memory
picture, see engine/specialdays.py). Shapes are built from a few helpers:
stripes, triangles/polygons, circles, stars and Nordic crosses.
Colors are the official ones where published, nudged only where an LED needs it.
"""
import math

from engine.teamcolors import hexc as C

W, H = 64, 32


# ------------------------------------------------------------------ helpers
def hstripes(f, colors, heights=None):
    heights = heights or _split(H, len(colors))
    y = 0
    for c, h in zip(colors, heights):
        f.fill(0, y, W - 1, y + h - 1, C(c))
        y += h


def vstripes(f, colors, widths=None):
    widths = widths or _split(W, len(colors))
    x = 0
    for c, w in zip(colors, widths):
        f.fill(x, 0, x + w - 1, H - 1, C(c))
        x += w


def _split(total, n):
    base = [total // n] * n
    for i in range(total - sum(base)):       # spread leftovers to the middle bands
        base[(n // 2 + i) % n] += 1
    return base


def poly(f, pts, c):
    """Fill a polygon; a pixel is in if its center is inside."""
    c = C(c)
    xs, ys = [p[0] for p in pts], [p[1] for p in pts]
    for y in range(max(0, int(min(ys))), min(H, int(math.ceil(max(ys))) + 1)):
        for x in range(max(0, int(min(xs))), min(W, int(math.ceil(max(xs))) + 1)):
            px, py, inside = x + 0.5, y + 0.5, False
            j = len(pts) - 1
            for i in range(len(pts)):
                (xi, yi), (xj, yj) = pts[i], pts[j]
                if (yi > py) != (yj > py) and px < (xj - xi) * (py - yi) / (yj - yi) + xi:
                    inside = not inside
                j = i
            if inside:
                f.set(x, y, c)


def circle(f, cx, cy, r, c, part=None):
    """Filled disc. part='top'/'bottom' fills only that half."""
    c = C(c)
    for y in range(H):
        for x in range(W):
            dx, dy = x + 0.5 - cx, y + 0.5 - cy
            if dx * dx + dy * dy <= r * r:
                if part == "top" and dy > 0 or part == "bottom" and dy <= 0:
                    continue
                f.set(x, y, c)


def star(f, cx, cy, r, c, points=5, inner=0.42):
    pts = []
    for i in range(points * 2):
        a = -math.pi / 2 + i * math.pi / points
        rr = r if i % 2 == 0 else r * inner
        pts.append((cx + rr * math.cos(a), cy + rr * math.sin(a)))
    poly(f, pts, c)


def nordic(f, field, cross, x0, x1, y0, y1, inner=None, ix0=0, ix1=0, iy0=0, iy1=0):
    """Nordic cross: bar from columns x0-x1 and rows y0-y1 (inclusive);
    optional inner cross (Norway, Iceland)."""
    f.fill(0, 0, W - 1, H - 1, C(field))
    f.fill(x0, 0, x1, H - 1, C(cross))
    f.fill(0, y0, W - 1, y1, C(cross))
    if inner:
        f.fill(ix0, 0, ix1, H - 1, C(inner))
        f.fill(0, iy0, W - 1, iy1, C(inner))


def near_line(x, y, x1, y1, x2, y2, d):
    px, py = x + 0.5, y + 0.5
    num = abs((y2 - y1) * px - (x2 - x1) * py + x2 * y1 - y2 * x1)
    return num / math.hypot(y2 - y1, x2 - x1) <= d


# ------------------------------------------------------------------ the flags
def mali(f):        vstripes(f, ["#14B53A", "#FCD116", "#CE1126"])
def lithuania(f):   hstripes(f, ["#FDB913", "#006A44", "#C1272D"])
def bulgaria(f):    hstripes(f, ["#FFFFFF", "#00966E", "#D62612"])
def chad(f):        vstripes(f, ["#002664", "#FECB00", "#C60C30"])
def estonia(f):     hstripes(f, ["#0072CE", "#000000", "#FFFFFF"])
def hungary(f):     hstripes(f, ["#CE2939", "#FFFFFF", "#477050"])
def armenia(f):     hstripes(f, ["#D90012", "#0033A0", "#F2A800"])
def france(f):      vstripes(f, ["#002395", "#FFFFFF", "#ED2939"])
def italy(f):       vstripes(f, ["#009246", "#FFFFFF", "#CE2B37"])
def ireland(f):     vstripes(f, ["#169B62", "#FFFFFF", "#FF883E"])
def ivory_coast(f): vstripes(f, ["#F77F00", "#FFFFFF", "#009E60"])


def congo(f):       # green / yellow / red, split on the diagonal
    for y in range(H):
        for x in range(W):
            v = (x + 0.5) / W + (y + 0.5) / H
            f.set(x, y, C("#009543") if v < 0.78 else C("#FBDE4A") if v < 1.22 else C("#DC241F"))


def bahrain(f):
    f.fill(0, 0, W - 1, H - 1, C("#CE1126"))
    pts = [(0, 0), (13, 0)]
    for i in range(5):
        y = i * 6.4
        pts += [(21, y + 3.2), (13, y + 6.4)]
    pts += [(0, 32)]
    poly(f, pts, "#FFFFFF")


def bahamas(f):
    hstripes(f, ["#00778B", "#FFC72C", "#00778B"])
    poly(f, [(0, 0), (27, 16), (0, 32)], "#000000")


def barbados(f):
    vstripes(f, ["#00267F", "#FFC726", "#00267F"])
    k = C("#000000")
    f.fill(31, 12, 32, 26, k)                       # shaft
    f.fill(30, 6, 33, 8, k); f.fill(31, 5, 32, 5, k)   # center prong tip
    f.fill(31, 9, 32, 12, k)
    f.fill(25, 13, 38, 14, k)                       # crossbar
    f.fill(25, 8, 26, 13, k); f.fill(37, 8, 38, 13, k)   # side prongs
    f.set(24, 7, k); f.set(27, 7, k); f.set(36, 7, k); f.set(39, 7, k)
    f.fill(29, 21, 34, 22, k)                       # cross guard on the shaft


def bangladesh(f):
    f.fill(0, 0, W - 1, H - 1, C("#006A4E"))
    circle(f, 29, 16, 10, "#F42A41")


def botswana(f):
    hstripes(f, ["#75AADB", "#FFFFFF", "#000000", "#FFFFFF", "#75AADB"], [12, 1, 6, 1, 12])


def cameroon(f):
    vstripes(f, ["#007A5E", "#CE1126", "#FCD116"])
    star(f, 32, 16.5, 6, "#FCD116")


def chile(f):
    hstripes(f, ["#FFFFFF", "#D52B1E"])
    f.fill(0, 0, 20, 15, C("#0039A6"))
    star(f, 10.5, 8.3, 4.5, "#FFFFFF")


def costa_rica(f):
    hstripes(f, ["#002B7F", "#FFFFFF", "#CE1126", "#FFFFFF", "#002B7F"], [5, 5, 12, 5, 5])


def czechia(f):
    hstripes(f, ["#FFFFFF", "#D7141A"])
    poly(f, [(0, 0), (32, 16), (0, 32)], "#11457E")


def djibouti(f):
    hstripes(f, ["#6AB2E7", "#12AD2B"])
    poly(f, [(0, 0), (28, 16), (0, 32)], "#FFFFFF")
    star(f, 9, 16.5, 4.5, "#D7141A")


def gambia(f):
    hstripes(f, ["#CE1126", "#FFFFFF", "#0C1C8C", "#FFFFFF", "#3A7728"], [11, 2, 6, 2, 11])


def georgia(f):
    f.fill(0, 0, W - 1, H - 1, C("#FFFFFF"))
    red = C("#FF0000")
    f.fill(28, 0, 35, H - 1, red)
    f.fill(0, 12, W - 1, 19, red)
    for cx, cy in ((13, 5), (50, 5), (13, 25), (50, 25)):
        f.fill(cx - 3, cy, cx + 4, cy + 1, red)
        f.fill(cx, cy - 3, cx + 1, cy + 4, red)


def ghana(f):
    hstripes(f, ["#CE1126", "#FCD116", "#006B3F"])
    star(f, 32, 16.5, 5.5, "#000000")


def greece(f):
    hstripes(f, ["#0D5EAF", "#FFFFFF"] * 4 + ["#0D5EAF"], [4, 3, 4, 3, 4, 3, 4, 3, 4])
    f.fill(0, 0, 17, 17, C("#0D5EAF"))
    f.fill(7, 0, 10, 17, C("#FFFFFF"))
    f.fill(0, 7, 17, 10, C("#FFFFFF"))


def iceland(f):
    nordic(f, "#02529C", "#FFFFFF", 17, 26, 11, 20, "#DC1E35", 19, 24, 13, 18)


def switzerland(f):
    f.fill(0, 0, W - 1, H - 1, C("#DA291C"))
    f.fill(29, 5, 34, 26, C("#FFFFFF"))
    f.fill(21, 13, 42, 18, C("#FFFFFF"))


def norway(f):
    nordic(f, "#BA0C2F", "#FFFFFF", 17, 28, 11, 20, "#00205B", 20, 25, 14, 17)


def thailand(f):
    hstripes(f, ["#A51931", "#FFFFFF", "#2D2A4A", "#FFFFFF", "#A51931"], [5, 5, 12, 5, 5])


def jamaica(f):
    for y in range(H):
        for x in range(W):
            px, py = x + 0.5, y + 0.5
            above_a, above_b = py < px / 2, py < (W - px) / 2       # the two diagonals
            if above_a and above_b or not above_a and not above_b:
                f.set(x, y, C("#009B3A"))     # top & bottom
            else:
                f.set(x, y, C("#000000"))     # hoist & fly
            if near_line(x, y, 0, 0, W, H, 2.6) or near_line(x, y, 0, H, W, 0, 2.6):
                f.set(x, y, C("#FED100"))


def latvia(f):
    hstripes(f, ["#9E3039", "#FFFFFF", "#9E3039"], [13, 6, 13])


def kuwait(f):
    hstripes(f, ["#007A3D", "#FFFFFF", "#CE1126"], [11, 10, 11])
    poly(f, [(0, 0), (16, 11), (16, 21), (0, 32)], "#000000")


def jordan(f):
    hstripes(f, ["#000000", "#FFFFFF", "#007A3D"], [11, 10, 11])
    poly(f, [(0, 0), (32, 16), (0, 32)], "#CE1126")
    star(f, 10.5, 16.5, 4.5, "#FFFFFF", points=7, inner=0.5)


def sweden(f):
    nordic(f, "#006AA7", "#FECC02", 19, 26, 13, 18)


def finland(f):
    nordic(f, "#FFFFFF", "#002F6C", 17, 26, 12, 19)


def greenland(f):
    hstripes(f, ["#FFFFFF", "#C8102E"])
    circle(f, 23, 16, 10.5, "#C8102E", part="top")
    circle(f, 23, 16, 10.5, "#FFFFFF", part="bottom")


def denmark(f):
    nordic(f, "#C8102E", "#FFFFFF", 20, 26, 13, 18)



# ------------------------------------------------------------------ round 2 helpers
def union_jack(f, x0=0, y0=0, w=64, h=32):
    """Union Jack in a w x h box (whole flag, or a canton)."""
    blue, white, red = C("#012169"), C("#FFFFFF"), C("#C8102E")
    sw = max(1.2, h * 0.10)      # white saltire half-width
    sr = max(0.6, h * 0.035)     # red saltire half-width
    cw = h * 0.167               # white cross half-width
    cr = h * 0.10                # red cross half-width
    cx, cy = x0 + w / 2, y0 + h / 2
    for y in range(y0, y0 + h):
        for x in range(x0, x0 + w):
            px, py = x + 0.5, y + 0.5
            c = blue
            d1 = near_line(x, y, x0, y0, x0 + w, y0 + h, sw) or near_line(x, y, x0, y0 + h, x0 + w, y0, sw)
            if d1:
                c = white
            if near_line(x, y, x0, y0, x0 + w, y0 + h, sr) or near_line(x, y, x0, y0 + h, x0 + w, y0, sr):
                c = red
            if abs(px - cx) <= cw or abs(py - cy) <= cw:
                c = white
            if abs(px - cx) <= cr or abs(py - cy) <= cr:
                c = red
            f.set(x, y, c)


def bitmap(f, rows, x0, y0, c):
    c = C(c)
    for j, row in enumerate(rows):
        for i, ch in enumerate(row):
            if ch == "#":
                f.set(x0 + i, y0 + j, c)


def crescent(f, cx, cy, r, cut_dx, cut_r, color, bg):
    circle(f, cx, cy, r, color)
    circle(f, cx + cut_dx, cy, cut_r, bg)


def rays_from(f, ox, oy, colors, start_deg, end_deg, ymax=None):
    """Fan of equal rays from (ox, oy) between two angles (degrees, 0 = right, 90 = up)."""
    n = len(colors)
    for y in range(H if ymax is None else ymax):
        for x in range(W):
            a = math.degrees(math.atan2(oy - (y + 0.5), (x + 0.5) - ox))
            if start_deg <= a <= end_deg:
                k = min(n - 1, int((end_deg - a) / (end_deg - start_deg) * n))
                f.set(x, y, C(colors[k]))


MAPLE = [
    "........#........",
    ".......###.......",
    "...#...###...#...",
    "...##.#####.##...",
    "#..###########..#",
    "##.###########.##",
    ".###############.",
    "..#############..",
    "...###########...",
    "..#############..",
    ".###############.",
    "....#########....",
    "......#####......",
    "........#........",
    "........#........",
    "........#........",
]


# ------------------------------------------------------------------ round 2 flags
def canada(f):
    vstripes(f, ["#D52B1E", "#FFFFFF", "#D52B1E"], [16, 32, 16])
    bitmap(f, MAPLE, 24, 8, "#D52B1E")


def japan(f):
    f.fill(0, 0, W - 1, H - 1, C("#FFFFFF"))
    circle(f, 32, 16, 9.6, "#BC002D")


def uk(f):          union_jack(f)
def germany(f):     hstripes(f, ["#000000", "#DD0000", "#FFCE00"])
def netherlands(f): hstripes(f, ["#AE1C28", "#FFFFFF", "#21468B"])
def belgium(f):     vstripes(f, ["#000000", "#FDDA24", "#EF3340"])
def austria(f):     hstripes(f, ["#C8102E", "#FFFFFF", "#C8102E"])
def poland(f):      hstripes(f, ["#FFFFFF", "#DC143C"])
def ukraine(f):     hstripes(f, ["#0057B7", "#FFD700"])
def romania(f):     vstripes(f, ["#002B7F", "#FCD116", "#CE1126"])
def russia(f):      hstripes(f, ["#FFFFFF", "#0039A6", "#D52B1E"])
def luxembourg(f):  hstripes(f, ["#EF3340", "#FFFFFF", "#00A3E0"])
def monaco(f):      hstripes(f, ["#CE1126", "#FFFFFF"])
def indonesia(f):   hstripes(f, ["#CE1126", "#FFFFFF"])
def nigeria(f):     vstripes(f, ["#008751", "#FFFFFF", "#008751"])
def guinea(f):      vstripes(f, ["#CE1126", "#FCD116", "#009460"])
def peru(f):        vstripes(f, ["#D91023", "#FFFFFF", "#D91023"])


def scotland(f):
    f.fill(0, 0, W - 1, H - 1, C("#005EB8"))
    for y in range(H):
        for x in range(W):
            if near_line(x, y, 0, 0, W, H, 3.2) or near_line(x, y, 0, H, W, 0, 3.2):
                f.set(x, y, C("#FFFFFF"))


def england(f):
    f.fill(0, 0, W - 1, H - 1, C("#FFFFFF"))
    f.fill(28, 0, 35, H - 1, C("#CE1124"))
    f.fill(0, 12, W - 1, 19, C("#CE1124"))


def faroe(f):
    nordic(f, "#FFFFFF", "#0065BD", 17, 28, 11, 20, "#EF303E", 20, 25, 14, 17)


def benin(f):
    f.fill(0, 0, 25, H - 1, C("#008751"))
    f.fill(26, 0, W - 1, 15, C("#FCD116"))
    f.fill(26, 16, W - 1, H - 1, C("#E8112D"))


def senegal(f):
    vstripes(f, ["#00853F", "#FDEF42", "#E31B23"])
    star(f, 32, 16.5, 6, "#00853F")


def togo(f):
    hstripes(f, ["#006A4E", "#FFCE00", "#006A4E", "#FFCE00", "#006A4E"], [7, 6, 6, 6, 7])
    f.fill(0, 0, 18, 18, C("#D21034"))
    star(f, 9.5, 9.8, 6, "#FFFFFF")


def libya(f):
    hstripes(f, ["#E70013", "#000000", "#239E46"], [8, 16, 8])
    crescent(f, 30, 16, 5.5, 1.8, 4.6, "#FFFFFF", "#000000")
    star(f, 37, 16.3, 2.8, "#FFFFFF")


def sudan(f):
    hstripes(f, ["#D21034", "#FFFFFF", "#000000"])
    poly(f, [(0, 0), (22, 16), (0, 32)], "#007229")


def tanzania(f):
    for y in range(H):
        for x in range(W):
            v = (x + 0.5) / W + (y + 0.5) / H
            c = ("#1EB53A" if v < 0.76 else "#FCD116" if v < 0.84 else "#000000" if v < 1.16
                 else "#FCD116" if v < 1.24 else "#00A3DD")
            f.set(x, y, C(c))


def congo_dr(f):
    for y in range(H):
        for x in range(W):
            v = (x + 0.5) / W + (y + 0.5) / H
            d = abs(v - 1)
            f.set(x, y, C("#CE1021") if d < 0.13 else C("#F7D618") if d < 0.2 else C("#007FFF"))
    star(f, 11, 9, 6.5, "#F7D618")


def seychelles(f):
    for y in range(H):
        for x in range(W):
            a = math.degrees(math.atan2(H - (y + 0.5), x + 0.5))
            c = ("#003F87" if a > 56.3 else "#FCD856" if a > 36.9 else "#D62828" if a > 26.6
                 else "#FFFFFF" if a > 14.0 else "#007A3D")
            f.set(x, y, C(c))


def mauritius(f):   hstripes(f, ["#EA2839", "#1A206D", "#FFD500", "#00A551"])
def colombia(f):    hstripes(f, ["#FCD116", "#003893", "#CE1126"], [16, 8, 8])


def panama(f):
    f.fill(0, 0, W - 1, H - 1, C("#FFFFFF"))
    f.fill(32, 0, 63, 15, C("#DA121A"))
    f.fill(0, 16, 31, 31, C("#072357"))
    star(f, 16, 8.3, 4.5, "#072357")
    star(f, 48, 24.3, 4.5, "#DA121A")


def cuba(f):
    hstripes(f, ["#002A8F", "#FFFFFF", "#002A8F", "#FFFFFF", "#002A8F"], [7, 6, 6, 6, 7])
    poly(f, [(0, 0), (28, 16), (0, 32)], "#CB1515")
    star(f, 9.5, 16.5, 5, "#FFFFFF")


def puerto_rico(f):
    hstripes(f, ["#ED0000", "#FFFFFF", "#ED0000", "#FFFFFF", "#ED0000"], [7, 6, 6, 6, 7])
    poly(f, [(0, 0), (28, 16), (0, 32)], "#0050F0")
    star(f, 9.5, 16.5, 5, "#FFFFFF")


def dominican_republic(f):
    f.fill(0, 0, W - 1, H - 1, C("#FFFFFF"))
    f.fill(0, 0, 28, 13, C("#002D62")); f.fill(35, 0, 63, 13, C("#CE1126"))
    f.fill(0, 18, 28, 31, C("#CE1126")); f.fill(35, 18, 63, 31, C("#002D62"))
    f.fill(31, 15, 32, 16, C("#00843D"))       # tiny coat of arms


def trinidad(f):
    f.fill(0, 0, W - 1, H - 1, C("#CE1126"))
    for y in range(H):
        for x in range(W):
            if near_line(x, y, 6, 0, W - 6, H, 6.0):
                f.set(x, y, C("#FFFFFF"))
            if near_line(x, y, 6, 0, W - 6, H, 4.3):
                f.set(x, y, C("#000000"))


def guyana(f):
    f.fill(0, 0, W - 1, H - 1, C("#009E49"))
    poly(f, [(0, 0), (64, 16), (0, 32)], "#FFFFFF")
    poly(f, [(0, 2), (59, 16), (0, 30)], "#FCD116")
    poly(f, [(0, 0), (33, 16), (0, 32)], "#000000")
    poly(f, [(0, 2), (30, 16), (0, 30)], "#CE1126")


def suriname(f):
    hstripes(f, ["#377E3F", "#FFFFFF", "#B40A2D", "#FFFFFF", "#377E3F"], [6, 3, 14, 3, 6])
    star(f, 32, 16.5, 6.5, "#ECC81D")


def vietnam(f):
    f.fill(0, 0, W - 1, H - 1, C("#DA251D"))
    star(f, 32, 17, 10, "#FFCD00")


def laos(f):
    hstripes(f, ["#CE1126", "#002868", "#CE1126"], [8, 16, 8])
    circle(f, 32, 16, 6.4, "#FFFFFF")


def palau(f):
    f.fill(0, 0, W - 1, H - 1, C("#4AADD6"))
    circle(f, 28, 16, 9.6, "#FFDE00")


def philippines(f):
    hstripes(f, ["#0038A8", "#CE1126"])
    poly(f, [(0, 0), (28, 16), (0, 32)], "#FFFFFF")
    y = C("#FCD116")
    circle(f, 9.5, 16, 3.2, "#FCD116")
    for dx, dy in ((0, -5), (0, 5), (-5, 0), (5, 0), (-4, -4), (4, -4), (-4, 4), (4, 4)):
        f.set(int(9.5 + dx), int(16 + dy), y)
    for sx, sy in ((2, 2), (2, 29), (23, 16)):
        f.set(sx, sy, y); f.set(sx - 1, sy, y); f.set(sx + 1, sy, y); f.set(sx, sy - 1, y); f.set(sx, sy + 1, y)


def singapore(f):
    hstripes(f, ["#EF3340", "#FFFFFF"])
    crescent(f, 10, 8, 5.5, 2.3, 5.0, "#FFFFFF", "#EF3340")
    w = C("#FFFFFF")
    for sx, sy in ((15, 4), (18, 7), (17, 11), (13, 11), (12, 7)):
        f.set(sx, sy, w); f.set(sx + 1, sy, w); f.set(sx, sy + 1, w); f.set(sx + 1, sy + 1, w)


def taiwan(f):
    f.fill(0, 0, W - 1, H - 1, C("#FE0000"))
    f.fill(0, 0, 31, 15, C("#000095"))
    star(f, 16, 8, 6.5, "#FFFFFF", points=12, inner=0.62)
    circle(f, 16, 8, 3.9, "#000095")
    circle(f, 16, 8, 3.2, "#FFFFFF")


def _southern_cross(f, color, border=None, r=3.0):
    for sx, sy in ((50, 6), (43, 14), (57, 12), (50, 26)):
        if border:
            star(f, sx, sy, r + 1.3, border)
        star(f, sx, sy, r, color)


def new_zealand(f):
    f.fill(0, 0, W - 1, H - 1, C("#00247D"))
    union_jack(f, 0, 0, 32, 16)
    _southern_cross(f, "#CC142B", "#FFFFFF", 2.3)


def australia(f):
    f.fill(0, 0, W - 1, H - 1, C("#00008B"))
    union_jack(f, 0, 0, 32, 16)
    star(f, 16, 24.5, 5, "#FFFFFF", points=7, inner=0.5)
    for sx, sy, r in ((50, 27, 3.3), (41, 15, 3.0), (57, 12, 3.0), (50, 5, 3.0)):
        star(f, sx, sy, r, "#FFFFFF", points=7, inner=0.5)
    f.set(53, 17, C("#FFFFFF")); f.set(54, 17, C("#FFFFFF"))


def qatar(f):
    f.fill(0, 0, W - 1, H - 1, C("#8A1538"))
    pts = [(0, 0), (15, 0)]
    step = 32 / 9
    for i in range(9):
        pts += [(22, i * step + step / 2), (15, (i + 1) * step)]
    pts += [(0, 32)]
    poly(f, pts, "#FFFFFF")


def uae(f):
    hstripes(f, ["#00732F", "#FFFFFF", "#000000"])
    f.fill(0, 0, 15, H - 1, C("#FF0000"))


def texas(f):
    f.fill(0, 0, 20, H - 1, C("#002868"))
    f.fill(21, 0, W - 1, 15, C("#FFFFFF"))
    f.fill(21, 16, W - 1, H - 1, C("#BF0A30"))
    star(f, 10.5, 16.8, 7, "#FFFFFF")


def colorado(f):
    hstripes(f, ["#002868", "#FFFFFF", "#002868"], [11, 10, 11])
    cx, cy = 25, 16
    for y in range(H):
        for x in range(W):
            dx, dy = x + 0.5 - cx, y + 0.5 - cy
            d = math.hypot(dx, dy)
            a = math.degrees(math.atan2(-dy, dx))
            if d <= 11 and not (-38 < a < 38 and d > 5.8):
                f.set(x, y, C("#BF0A30"))
            if d <= 5.8:
                f.set(x, y, C("#FFD700"))


def alaska(f):
    f.fill(0, 0, W - 1, H - 1, C("#0F204B"))
    gold = C("#FFB612")
    for sx, sy in ((7, 22), (8, 27), (15, 28), (16, 23), (21, 20), (26, 18), (31, 13)):
        f.set(sx, sy, gold); f.set(sx - 1, sy, gold); f.set(sx + 1, sy, gold)
        f.set(sx, sy - 1, gold); f.set(sx, sy + 1, gold)
    star(f, 52, 7, 4.2, "#FFB612")


def arizona(f):
    f.fill(0, 16, W - 1, H - 1, C("#002868"))
    rays_from(f, 32, 16, ["#BF0A30", "#FED700"] * 6 + ["#BF0A30"], 0, 180, ymax=16)
    star(f, 32, 16.5, 7.5, "#CE5C17")


def new_mexico(f):
    """Yellow field, red Zia sun: a disc with four groups of four rays."""
    f.fill(0, 0, W - 1, H - 1, C("#FFD700"))
    red = C("#BF0A30")
    cx, cy = 32, 16
    circle(f, cx, cy, 4.2, "#BF0A30")
    for i, off in enumerate((-4, -2, 1, 3)):          # 4 rays per group, inner two longer
        reach = 13 if i in (1, 2) else 11
        for d in range(6, reach + 1):
            f.set(cx + d - 1, cy + off, red); f.set(cx - d, cy + off, red)      # right / left
        reach_v = 9 if i in (1, 2) else 8
        for d in range(6, reach_v + 1):
            f.set(cx + off, cy - d, red); f.set(cx + off, cy + d - 1, red)      # up / down


def maryland(f):
    gold, black, red, white = C("#FFD700"), C("#000000"), C("#BF0A30"), C("#FFFFFF")

    def calvert(x0, y0):
        for y in range(16):
            for x in range(32):
                c = gold if (x // 6) % 2 == 0 else black
                if (x - y * 2) > 0 and (x - y * 2) < 34 and y + x / 2 > 9:   # the bend: colors swap
                    c = black if c == gold else gold
                f.set(x0 + x, y0 + y, c)

    def crossland(x0, y0):
        for y in range(16):
            for x in range(32):
                q = (x >= 16) ^ (y >= 8)
                base = white if q else red
                arm = abs(x - 15.5) <= 2 or abs(y - 7.5) <= 2
                c = (red if base == white else white) if arm else base
                f.set(x0 + x, y0 + y, c)

    calvert(0, 0); crossland(32, 0); crossland(0, 16); calvert(32, 16)


def south_africa(f):
    hstripes(f, ["#E03C31", "#001489"])
    for y in range(H):
        for x in range(W):
            py = y + 0.5
            if x < 26:
                dw = near_line(x, y, 0, 0, 26, 16, 5.2) or near_line(x, y, 0, 32, 26, 16, 5.2)
                dg = near_line(x, y, 0, 0, 26, 16, 3.3) or near_line(x, y, 0, 32, 26, 16, 3.3)
            else:
                dw, dg = abs(py - 16) <= 5.2, abs(py - 16) <= 3.3
            if dw:
                f.set(x, y, C("#FFFFFF"))
            if dg:
                f.set(x, y, C("#007749"))
    poly(f, [(0, 3), (20, 16), (0, 29)], "#FFB81C")
    poly(f, [(0, 6), (16, 16), (0, 26)], "#000000")


CEDAR = [
    "......#......",
    ".....###.....",
    "....#####....",
    ".....###.....",
    "...#######...",
    "..#########..",
    "....#####....",
    "..#########..",
    ".###########.",
    "#############",
    "......#......",
    "......#......",
]


def lebanon(f):
    hstripes(f, ["#EE161F", "#FFFFFF", "#EE161F"], [8, 16, 8])
    bitmap(f, CEDAR, 26, 10, "#00A651")


def hawaii(f):
    hstripes(f, ["#FFFFFF", "#C8102E", "#012169"] * 2 + ["#FFFFFF", "#C8102E"], [4] * 8)
    union_jack(f, 0, 0, 32, 16)


# name on the panel -> drawing function. The quiz uses settings.FLAG_QUIZ_COUNTRIES.
FLAGS = {
    "MALI": mali, "REPUBLIC OF THE CONGO": congo, "LITHUANIA": lithuania,
    "BAHRAIN": bahrain, "BAHAMAS": bahamas, "BARBADOS": barbados,
    "BANGLADESH": bangladesh, "BOTSWANA": botswana, "BULGARIA": bulgaria,
    "CAMEROON": cameroon, "CHAD": chad, "CHILE": chile, "COSTA RICA": costa_rica,
    "CZECHIA": czechia, "DJIBOUTI": djibouti, "ESTONIA": estonia, "GAMBIA": gambia,
    "GEORGIA": georgia, "GHANA": ghana, "GREECE": greece, "ICELAND": iceland,
    "SWITZERLAND": switzerland, "NORWAY": norway, "THAILAND": thailand,
    "HUNGARY": hungary, "JAMAICA": jamaica, "ARMENIA": armenia, "LATVIA": latvia,
    "KUWAIT": kuwait, "JORDAN": jordan, "FRANCE": france, "ITALY": italy,
    "SWEDEN": sweden, "FINLAND": finland, "GREENLAND": greenland,
    "DENMARK": denmark, "IRELAND": ireland, "IVORY COAST": ivory_coast,
    # round 2
    "CANADA": canada, "JAPAN": japan, "UNITED KINGDOM": uk, "GERMANY": germany,
    "NETHERLANDS": netherlands, "BELGIUM": belgium, "AUSTRIA": austria, "POLAND": poland,
    "UKRAINE": ukraine, "ROMANIA": romania, "RUSSIA": russia, "LUXEMBOURG": luxembourg,
    "MONACO": monaco, "SCOTLAND": scotland, "ENGLAND": england, "FAROE ISLANDS": faroe,
    "NIGERIA": nigeria, "BENIN": benin, "GUINEA": guinea, "SENEGAL": senegal,
    "TOGO": togo, "LIBYA": libya, "SUDAN": sudan, "TANZANIA": tanzania,
    "DR CONGO": congo_dr, "SEYCHELLES": seychelles, "MAURITIUS": mauritius,
    "COLOMBIA": colombia, "PERU": peru, "PANAMA": panama, "CUBA": cuba,
    "PUERTO RICO": puerto_rico, "DOMINICAN REPUBLIC": dominican_republic,
    "TRINIDAD & TOBAGO": trinidad, "GUYANA": guyana, "SURINAME": suriname,
    "VIETNAM": vietnam, "LAOS": laos, "PALAU": palau, "PHILIPPINES": philippines,
    "INDONESIA": indonesia, "SINGAPORE": singapore, "TAIWAN": taiwan,
    "NEW ZEALAND": new_zealand, "AUSTRALIA": australia, "QATAR": qatar,
    "UNITED ARAB EMIRATES": uae, "TEXAS": texas, "COLORADO": colorado,
    "ALASKA": alaska, "ARIZONA": arizona, "NEW MEXICO": new_mexico, "MARYLAND": maryland,
    # round 3
    "SOUTH AFRICA": south_africa, "LEBANON": lebanon, "HAWAII": hawaii,
}
