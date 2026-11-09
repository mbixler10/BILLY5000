"""
vinnykit.py - the little toolkit every Vinny episode is built from.

An episode is a short script: a background plus timed layers (Vinny, props,
words, effects), each with a start/stop time and optional movement:

    Ep("cookie_heist", "pole", "COOKIE HEIST", 8, "kitchen",
       prop("plate", 34, 24),
       vin(4, 17, to=(22, 17), move=(0.5, 3)),
       say(0, "COOKIES: 3", until=4.5),
       say(0, "CRUMBS: NO", GREEN, at=4.5))

Times are seconds from the start of the episode. Sprites are drawn as text
pictures below; each letter is a color (see PAL).
"""
import math
import random

from engine.santa import graphics, _font

# --------------------------------------------------------------------------
# Colors
# --------------------------------------------------------------------------
PAL = {
    "R": (215, 0, 0), "r": (120, 0, 0), "W": (240, 240, 240), "w": (160, 160, 170),
    "S": (255, 185, 140), "H": (110, 55, 15), "E": (30, 120, 255), "K": (30, 30, 35),
    "B": (150, 85, 35), "b": (90, 50, 20), "T": (210, 155, 85), "G": (0, 180, 50),
    "g": (0, 95, 30), "Y": (255, 200, 0), "O": (255, 140, 0), "U": (40, 110, 255),
    "u": (20, 40, 120), "C": (90, 210, 255), "P": (255, 120, 160), "M": (160, 70, 220),
    "N": (120, 120, 130), "n": (60, 60, 70), "L": (150, 255, 60), "A": (200, 200, 215),
    "D": (60, 30, 10), "F": (255, 230, 170), "Z": (0, 0, 0),
}
WHITE = (235, 235, 235); RED = (255, 30, 30); GREEN = (0, 255, 60); GOLD = (255, 200, 0)
AMBER = (255, 140, 0); BLUE = (90, 160, 255); PINK = (255, 120, 170); GREY = (120, 120, 130)
CYAN = (90, 220, 255); PURPLE = (190, 110, 255); BROWN = (150, 85, 35); DIM = (60, 60, 70)


def font(size="s"):
    return _font({"s": "5x7.bdf", "t": "4x6.bdf", "m": "6x10.bdf", "b": "7x13.bdf"}[size])


FONT_W = {"s": 5, "t": 4, "m": 6, "b": 7}
TEXT_H = {"s": 7, "t": 6, "m": 9, "b": 12}
ROWS = [7, 15, 23, 31]                     # 5x7 baselines, 4 rows


def px(c, x, y, col):
    x, y = int(x), int(y)
    if 0 <= x < 64 and 0 <= y < 32:
        c.SetPixel(x, y, *col)


class _Col:                                   # what graphics.DrawText wants
    def __init__(self, rgb):
        self.red, self.green, self.blue = rgb


def text(c, x, y, col, s, size="s"):
    return graphics.DrawText(c, font(size), int(x), int(y), _Col(col), s)


def rect(c, x0, y0, x1, y1, col):
    for y in range(int(y0), int(y1) + 1):
        for x in range(int(x0), int(x1) + 1):
            px(c, x, y, col)


def circle(c, cx, cy, r, col):
    for y in range(int(cy - r), int(cy + r) + 1):
        for x in range(int(cx - r), int(cx + r) + 1):
            if (x - cx) ** 2 + (y - cy) ** 2 <= r * r + r * 0.6:
                px(c, x, y, col)


def line(c, x0, y0, x1, y1, col, every=1):
    n = int(max(abs(x1 - x0), abs(y1 - y0), 1))
    for i in range(n + 1):
        if i % every == 0:
            px(c, round(x0 + (x1 - x0) * i / n), round(y0 + (y1 - y0) * i / n), col)


def lerp(a, b, f):
    return a + (b - a) * f


def ease(t, t0, t1):
    if t1 <= t0:
        return 1.0 if t >= t0 else 0.0
    f = min(1.0, max(0.0, (t - t0) / (t1 - t0)))
    return f * f * (3 - 2 * f)


# --------------------------------------------------------------------------
# Sprites: a picture is a list of strings, one letter per pixel, "." = clear
# --------------------------------------------------------------------------
_V_HEAD = ["....R..", "...RR..", "..RRR..", ".WWWWW.", ".HSSSS.", ".SESES.", ".SSPSS."]
SPRITES = {
    # --- Vinny (7 x 12) -----------------------------------------------------
    "v_stand": _V_HEAD + ["..WWW..", ".RRRRR.", "W.RRR.W", "..R.R..", "..R.R.."],
    "v_wave":  _V_HEAD[:6] + [".SSPSSW", "..WWWR.", ".RRRR..", "W.RRR..", "..R.R..", "..R.R.."],
    "v_up":    _V_HEAD[:6] + ["WSSPSSW", "R.WWW.R", ".RRRRR.", "..RRR..", "..R.R..", "..R.R.."],
    "v_walk1": _V_HEAD + ["..WWW..", ".RRRRR.", "W.RRR.W", ".R...R.", "R.....R"],
    "v_walk2": _V_HEAD + ["..WWW..", ".RRRRR.", "W.RRR.W", "..R.R..", "..RR..."],
    "v_sit":   _V_HEAD + ["..WWW..", ".RRRRR.", "W.RRR.W", "..RRRRR", "......."],
    "v_wink":  _V_HEAD[:5] + [".SESSS.", ".SSPSS.", "..WWW..", ".RRRRR.", "W.RRR.W", "..R.R..", "..R.R.."],
    "v_shock": _V_HEAD[:5] + [".SESES.", ".SSKSS.", "W.WWW.W", "R.RRR.R", "..RRR..", ".R...R.", "R.....R"],
    "v_sleep": _V_HEAD[:5] + [".SHSHS.", ".SSSSS.", "..WWW..", ".RRRRR.", "W.RRR.W", "..R.R..", "..R.R.."],
    "v_head":  _V_HEAD,
    # --- Scully, Billy's dog (he's a good boy) -------------------------------
    "dog_sit":   ["..bb.bb......", "..bBBBb......", "..BEBEB......", "..BBBBBK.....",
                  "...BPBB......", "...BBBBBB....", "..BBBBBBBB..b", "..BBBBBBBBBb.",
                  "..BB.BBBBBB..", "..BB.BB..BB.."],
    "dog_sleep": [".............", ".............", ".............", "..........bb.",
                  ".....BBBBBbBBb", "b..BBBBBBBBHBK", ".bBBBBBBBBBBB.", "..BBBBBBBBBB.."],
    "dog_walk":  [".bb.bb..............", ".bBBBb..............", ".BEBEB..............",
                  "KBBBBB..............", "..BBBBBBBBBBBBB....b", "...BBBBBBBBBBBBB..b.",
                  "...BBBBBBBBBBBBBBb..", "...BB.BB.....BB.BB..", "...B...B.....B...B.."],
    "bone": ["W....W", "WWWWWW", "W....W"],
    # --- food ---------------------------------------------------------------
    "cookie": [".TTT.", "TbTTT", "TTTbT", "TbTTT", ".TTT."],
    "plate": ["WWWWWWWWWWWWWWWWWWWW", ".AAAAAAAAAAAAAAAAAA."],
    "mug": ["WWWWWWW..", "WBBBBBW..", "WWWWWWWWW", "WWWWWWW.W", "WWWWWWWWW", "WWWWWWW..",
            ".WWWWW..."],
    "milk": [".WWW.", "WUUUW", "WWWWW", "WWWWW", "WWWWW", "WWWWW"],
    "candy_cane": [".WRW.", "R...W", "W...R", "R....", "W....", "R....", "W...."],
    "lollipop": [".RWR.", "WRWRW", "RWRWR", ".WRW.", "..A..", "..A..", "..A.."],
    "gingerman": [".TT.", "TFFT", ".TT.", "TTTT", ".TT.", "T..T"],
    "pie": ["..TTTTT..", ".TTRTRTT.", "TTTTTTTTT", ".NNNNNNN."],
    "broccoli": [".GgG.", "GgGgG", ".GgG.", "..L..", "..L.."],
    "carrot": ["..G.G", "...G.", "..OO.", ".OO..", "OO..."],
    "pizza": ["YYYYYYY", ".YRYRY.", "..YYY..", "...Y..."],
    "marshmallow": ["WWW", "WWW"],
    "coffee": [".WWWW.", "UGGGGU", ".GGGG.", ".GGGG.", "..GG.."],
    "fish": ["....OO..", "O.OOOOO.", "OOOOOOKO", "O.OOOOO.", "....OO.."],
    "banana": ["....Y", "...YY", "YYYY.", ".YY.."],
    # --- holiday ------------------------------------------------------------
    "tree": [".......Y.......", "......YYY......", ".......G.......", "......GGG......",
             ".....GRGGG.....", "....GGGGGUG....", ".....GGGGG.....", "....GGYGGGG....",
             "...GGGGGGRGG...", "..GUGGGGGGGGG..", "....GGGGGYG....", "...GGRGGGGGGG..",
             "..GGGGGGUGGGGG.", ".GGYGGGGGGGGRGG", "......BBB......", "......BBB......"],
    "star": ["..Y..", "YYYYY", ".YYY.", ".Y.Y."],
    "ornament": ["..Y..", ".YYY.", ".RRR.", "RRWRR", "RWRRR", "RRRRR", ".RRR."],
    "gift": ["..R.R..", "...R...", "GGGRGGG", "GGGRGGG", "RRRRRRR", "GGGRGGG", "GGGRGGG"],
    "gift_big": ["....R...R....", ".....R.R.....", "GGGGGGRGGGGGG", "GGGGGGRGGGGGG",
                 "GGGGGGRGGGGGG", "RRRRRRRRRRRRR", "GGGGGGRGGGGGG", "GGGGGGRGGGGGG",
                 "GGGGGGRGGGGGG", "GGGGGGRGGGGGG"],
    "sock": ["WWW.", "RRR.", "RRR.", "RRR.", "RRRR", "RRRR"],
    "stocking": ["WWWW..", "RRRR..", "RRRR..", "RRRR..", "RRRRRR", "RRRRRR", ".RRRR."],
    "bell": ["..Y..", ".YYY.", ".YYY.", "YYYYY", "..Y.."],
    "wreath": [".GGGG.", "GG..GG", "G....G", "G....G", "GG..RG", ".GGRR.", "...R.."],
    "snowflake": ["W.W.W", ".WWW.", "WWWWW", ".WWW.", "W.W.W"],
    "snowman": ["...KKK...", "..KKKKK..", "...WWW...", "..WKWKW..", "..WWOWW..", "...WWW...",
                "..WWWWW..", ".WWWKWWW.", ".WWWWWWW.", ".WWWKWWW.", "WWWWWWWWW", ".WWWWWWW."],
    "candle": [".O.", ".Y.", "WWW", "WWW", "WWW", "WWW"],
    "nutcracker": ["..KKK..", ".KKKKK.", "..SSS..", "..SKS..", ".WSSSW.", "RRRRRRR", "R.RRR.R",
                   "YRRRRRY", "..uuu..", "..u.u..", "..u.u..", ".KK.KK."],
    "letter": ["WWWWWWW", "WW...WW", "W.W.W.W", "W..W..W", "WWWWWWW"],
    "mailbox": [".UUUU.R", "UUUUUUR", "UUUUUUR", "UUUUUU.", "...N...", "...N...", "...N..."],
    "chimney": ["RRRRRRRR", ".RrRRrR.", ".RRrRRR.", ".rRRRrR.", ".RRRrRR.", ".RrRRRR."],
    "sleigh": ["R.........", "RR........", "RRRRRRRRR.", "RRRRRRRRRY", ".Y......Y.",
               "YYYYYYYYYY"],
    "reindeer": ["b.b...", ".bb...", ".BBB..", "BBEB..", "..BBBBBBB", "...BBBBBB", "...B.B.BB",
                 "...B.B..B"],
    "sled": ["R........", "RRRRRRRRR", ".A.....A.", "AAAAAAAAA"],
    "skates": ["WWW..", "WWW..", "WWWW.", "AAAAA"],
    "skis": ["R........R", ".R......R.", "..R....R..", "...R..R..."],
    "trophy": ["Y.YYY.Y", "YYYYYYY", ".YYYYY.", "..YYY..", "...Y...", "..YYY..", ".BBBBB."],
    "medal": ["R...R", ".R.R.", "..Y..", ".YYY.", "YYYYY", ".YYY."],
    "crown": ["Y.Y.Y", "YYYYY", "YRYUY", "YYYYY"],
    # --- things around the house -------------------------------------------
    "lamp": ["..YYYY..", ".YYYYYY.", "YYYYYYYY", "...NN...", "...NN...", "...NN...",
             "...NN...", "..NNNN.."],
    "couch": ["..MMMMMMMMMMMM..", ".MMMMMMMMMMMMMM.", "MMMMMMMMMMMMMMMM", "MM.MMMMMMMMMM.MM",
              "MM............MM"],
    "fridge": ["AAAAAAAA", "AAAAAAAN", "AAAAAAAA", "NNNNNNNN", "AAAAAAAA", "AAAAAAAN",
               "AAAAAAAA", "AAAAAAAA", "AAAAAAAA", "AAAAAAAA", "AAAAAAAA", "AAAAAAAA"],
    "washer": ["AAAAAAAA", "AYAUANAA", "AAAAAAAA", "AA.CC.AA", "A.CCCC.A", "A.CCCC.A",
               "AA.CC.AA", "AAAAAAAA"],
    "tub": ["N..............", "WWWWWWWWWWWWWWW", "WCCCCCCCCCCCCCW", "WWWWWWWWWWWWWWW",
            ".WWWWWWWWWWWWW.", "..N.........N.."],
    "duck": ["..YY.", ".YYKY", "YYYYO", "YYYY.", ".YY.."],
    "book": ["UUUUUUU", "UWWWWWU", "UWWWWWU", "UUUUUUU"],
    "books": ["R.U.G.Y", "R.U.G.Y", "RUUGGYY", "RUUGGYY", "RUUGGYY"],
    "pillow": [".WWWWWW.", "WWWWWWWW", "WWWWWWWW", ".WWWWWW."],
    "blanket_fort": ["......U......", ".....UUU.....", "....UUUUU....", "...UUWUUUU...",
                     "..UUUUUUWUU..", ".UUUUUUUUUUU.", "UUUUU...UUUUU", "UUUUU...UUUUU"],
    "phone": ["NNNN", "NCCN", "NCCN", "NCCN", "NNNN"],
    "camera": [".NN....", "NNNNNNN", "NNACANN", "NAKKKAN", "NNACANN", "NNNNNNN"],
    "toothbrush": ["WWW.........", "CCCAAAAAAAAA"],
    "suitcase": ["...NN...", "BBBBBBBB", "BBYBBYBB", "BBBBBBBB", "BBBBBBBB", "BBBBBBBB"],
    "umbrella": ["...GGG...", ".GGGGGGG.", "GGGGGGGGG", "....N....", "....N....", "....N....",
                 "...NN...."],
    "balloon": [".RRR.", "RRWRR", "RRRRR", "RRRRR", ".RRR.", "..R..", "..N..", "..N..",
                "...N.", "..N.."],
    "kite": ["..U..", ".UYU.", "UYYYU", ".UYU.", "..U..", "...R.", "..R..", "...R."],
    "teddy": ["B...B", "BBBBB", "BKBKB", "BBTBB", ".BBB.", "BBBBB", "BB.BB"],
    "robot": [".A.", "AAA", "ACA", "AAA", "NAN", "A.A"],
    "train": ["...K......", "..KK.RRRR.", "RRRRRRRRR.", "RRRRRRRRRR", ".K..K..K.."],
    "car": ["..UUUU...", ".UCCCUU..", "UUUUUUUUU", ".K....K.."],
    "ball": [".RR.", "RWWR", "RWWR", ".RR."],
    "drum": ["YYYYY", "RYRYR", "RYRYR", "RYRYR", "YYYYY"],
    "mic": [".AA.", "AAAA", ".AA.", "..N.", "..N.", "..N."],
    "guitar": ["....N", "...N.", "..N..", ".OO..", "OOOO.", "OKOO.", ".OO.."],
    "magnifier": [".AAA..", "A...A.", "A...A.", "A...A.", ".AAA..", "....N.", ".....N"],
    "binoculars": ["NN.NN", "NNNNN", "NC.NC"],
    "walkie": ["N...", "N...", "NNNN", "NCCN", "NNNN", "NANN", "NNNN"],
    "map": ["FFFFFFFF", "FRFFFFFF", "FFRFFUUF", "FFFRFUFF", "FFFFRFFF", "FUFFFRXF",
            "FFFFFFFF"],
    "clipboard": [".NN.", "WWWW", "WKKW", "WWWW", "WKKW", "WWWW"],
    "toilet_paper": ["WWW", "WNW", "WWW", "WWW"],
    "paper_plane": ["W..........", "WWW........", ".WWWWWW....", "..WWWWWWWWW", ".WWWWWW....",
                    "WWW........"],
    "paper_boat": ["...W...", "...WW..", "...WWW.", "WWWWWWW", ".WWWWW."],
    "rocket": ["..W..", ".WWW.", ".WUW.", ".WWW.", "WWWWW", "W.O.W", "..O.."],
    "parachute": ["...RRRRR...", ".RWWRRRWWR.", "RRWWRRRWWRR", "W.........W", ".W.......W.",
                  "..W.....W..", "...W...W..."],
    "chalkboard": ["BBBBBBBBBBBBBBBBBBBBBBBBB"] + ["BggggggggggggggggggggggggB"[:25]] * 10 +
                  ["BBBBBBBBBBBBBBBBBBBBBBBBB"],
    "boxing_glove": [".RRR.", "RRRRR", "RRRRR", "RRRR.", ".WW.."],
    "box": ["TTTTTTTTTTTT", "TbbbbbbbbbbT", "TTTTTTTTTTTT", "TTTTTTTTTTTT", "TTTTbbbbTTTT",
            "TTTTTTTTTTTT", "TTTTTTTTTTTT", "TTTTTTTTTTTT", "TTTTTTTTTTTT"],
    "box_angry": ["TTTTTTTTTTTT", "TbbbbbbbbbbT", "TTTTTTTTTTTT", "TTKTTTTTTKTT", "TTTKTTTTKTTT",
                  "TTTTTTTTTTTT", "TTTTKKKKTTTT", "TTTKTTTTKTTT", "TTTTTTTTTTTT"],
    # --- Seattle & sea ------------------------------------------------------
    "needle": ["...Y...", "...A...", "...A...", ".AAAAA.", "AAAAAAA", ".AAAAA.", "..A.A..",
               "..A.A..", "..A.A..", ".A...A.", ".A...A.", ".A...A.", "A.....A", "A.....A"],
    "jet": ["...........U..", "..........UU..", "AAAAAAAAAAAAAA", ".AUAUAUAUAAAAA",
            "...........UU.", "...........U.."],
    "ferry": ["......GG.......", "....WWWWWW.....", "..WWKWKWKWKW...", "WWWWWWWWWWWWWWW",
              ".GGGGGGGGGGGGG.", "..WWWWWWWWWWW.."],
    "ship": ["...........R........", "......N....N....N...", ".....WWW..WWW..WWW..",
             ".....WWW..WWW..WWW..", "....WWWW.WWWWW.WWW..", "......N....N....N...",
             "BBBBBBBBBBBBBBBBBBBB", ".BBYBBYBBYBBYBBYBBB.", "..BBBBBBBBBBBBBBBB.."],
    "sailboat": ["....W...", "....WW..", "....WWW.", "....WWWW", "....N...", "BBBBBBBB",
                 ".BBBBBB."],
    "lighthouse": ["..YYY..", ".NNNNN.", "..RRR..", "..WWW..", "..RRR..", ".WWWWW.",
                   ".RRRRR.", ".WWWWW.", "RRRRRRR"],
    "seagull": ["W.....W", ".WW.WW.", "...W..."],
    "whale": ["......n......", "...nnnnnnn...", ".nnnnnnnnnnn.", "nnKnnnnnnnnnnn",
              "nWWWWWWWWnnn.n", ".WWWWWWWnn...."],
    "crab": ["R.....R", "RR...RR", ".RRRRR.", "RRKRKRR", ".RRRRR.", "R.R.R.R"],
    "puck": [".nnnn.", "nnnnnn", ".nnnn."],
    "football": [".BBB.", "BWBWB", ".BBB."],
    "baseball": [".WW.", "WRWW", "WWRW", ".WW."],
    "cap": [".UUUU.", "UUUUUU", "UUUUUUUU"],
    "foam_finger": ["...G.", "..GG.", "GGGG.", "GGGG.", "GGGG.", ".GG..", ".GG.."],
    "moon": [".FFF.", "FFFFF", "FFF..", "FFFFF", ".FFF."],
    "sun": ["Y.Y.Y", ".YYY.", "YYYYY", ".YYY.", "Y.Y.Y"],
    "cloud": ["..WWW....", ".WWWWW.WW", "WWWWWWWWW", ".WWWWWWW."],
    "raincloud": ["..NNN....", ".NNNNN.NN", "NNNNNNNNN", ".NNNNNNN."],
    "penguin": [".KK.", "KWWK", "KWOK", "KWWK", "KWWK", ".OO."],
    "polar_bear": ["W.....W.....", "WWW.WWWWW...", "WKWWWWWWWWW.", "WWWWWWWWWWWW", "..WW.WW.WW.W"],
    "igloo": ["...WWWWW...", ".WWAWWWAWW.", "WWAWWWWWAWW", "WWWWKKKWWWW", "WWWWKKKWWWW"],
    "elf_hat": ["....R", "...RR", "..RRR", ".RRRR", "WWWWW"],
    "bar": ["NNNNNNNNNNNNNN", "N............N", "N............N", "N............N",
            "N............N", "N............N", "N............N", "N............N"],
}


def sprite_size(name):
    rows = SPRITES[name]
    return max(len(r) for r in rows), len(rows)


def draw_sprite(c, name, x0, y0, flip=False, flipv=False, pal=None, tint=None):
    rows = SPRITES[name]
    w = max(len(r) for r in rows)
    h = len(rows)
    for y, row in enumerate(rows):
        for x, ch in enumerate(row):
            if ch == ".":
                continue
            col = (pal or {}).get(ch) or PAL.get(ch)
            if col is None:
                continue
            if tint:
                col = tint(col)
            px(c, x0 + (w - 1 - x if flip else x), y0 + (h - 1 - y if flipv else y), col)


# --------------------------------------------------------------------------
# Layers: each returns a function (canvas, t) that draws itself when it's on
# --------------------------------------------------------------------------
TEXTS = []          # every caption, so a check can catch any that run off the panel


def _on(t, at, until):
    return t >= at and (until is None or t < until)


def _pos(t, x, y, to, move, at, until):
    if to is None:
        return x, y
    t0, t1 = move if move else (at, until if until is not None else at + 1)
    f = ease(t, t0, t1)
    return lerp(x, to[0], f), lerp(y, to[1], f)


def spr(name, x, y, at=0, until=None, to=None, move=None, flip=False, flipv=False,
        bob=0, hop=0, shake=0, blink=None, pal=None, path=None, spin=False):
    """A sprite, optionally moving (to/move), bobbing, hopping or shaking.
    path = [(t, x, y), ...] for multi-point moves."""
    def layer(c, t):
        if not _on(t, at, until):
            return
        if blink and int((t - at) / blink) % 2:
            return
        if path:
            pts = path
            if t <= pts[0][0]:
                xx, yy = pts[0][1], pts[0][2]
            elif t >= pts[-1][0]:
                xx, yy = pts[-1][1], pts[-1][2]
            else:
                for (ta, xa, ya), (tb, xb, yb) in zip(pts, pts[1:]):
                    if ta <= t <= tb:
                        f = ease(t, ta, tb)
                        xx, yy = lerp(xa, xb, f), lerp(ya, yb, f)
                        break
        else:
            xx, yy = _pos(t, x, y, to, move, at, until)
        if bob:
            yy += round(math.sin(t * 6) * bob)
        if hop:
            yy -= abs(round(math.sin(t * 7) * hop))
        if shake:
            xx += (1 if int(t * 30) % 2 else -1) * shake
        fl = flip
        fv = flipv
        if spin:
            phase = int(t * 6) % 4
            fl, fv = phase in (1, 2), phase in (2, 3)
        draw_sprite(c, name, round(xx), round(yy), fl, fv, pal)
    return layer


def vin(x, y, pose="stand", at=0, until=None, to=None, move=None, flip=False, walk=False,
        **kw):
    """Vinny. walk=True swaps leg frames while he's moving."""
    if not walk:
        return spr("v_" + pose, x, y, at, until, to, move, flip, **kw)
    layers = [spr("v_walk1", x, y, at, until, to, move, flip, blink=0.18, **kw),
              _offset_blink(spr("v_walk2", x, y, at, until, to, move, flip, **kw), at)]
    return group(*layers)


def _offset_blink(layer, at):
    def f(c, t):
        if int((t - at) / 0.18) % 2:
            layer(c, t)
    return f


def group(*layers):
    def f(c, t):
        for L in layers:
            L(c, t)
    return f


def say(row, s, col=WHITE, at=0, until=None, typed=True, x=None, center=False, blink=None,
        size="s", y=None, cps=18, wobble=False, back=True):
    """Words. row 0-3 for the 4 normal lines, or give y for a custom baseline."""
    w = FONT_W[size]
    TEXTS.append((s, x, center, w))
    def layer(c, t):
        if not _on(t, at, until):
            return
        if blink and int((t - at) / blink) % 2:
            return
        shown = s[:int((t - at) * cps)] if typed else s
        xx = x if x is not None else ((64 - len(s) * w) // 2 if center else 1)
        yy = y if y is not None else ROWS[row]
        if wobble:
            yy += 1 if int(t * 5) % 2 else 0
        if back and shown:                    # dark plate so words read over anything
            rect(c, xx - 1, yy - TEXT_H[size], xx + len(shown) * w - 1, yy, (0, 0, 0))
        text(c, xx, yy, col, shown, size)
    return layer


def big(s, col=GOLD, at=0, until=None, y=24, x=None, bounce=False, blink=None):
    TEXTS.append((s, x, x is None, 7))
    def layer(c, t):
        if not _on(t, at, until):
            return
        if blink and int((t - at) / blink) % 2:
            return
        yy = y - (abs(round(math.sin((t - at) * 8) * 2)) if bounce else 0)
        xx = x if x is not None else (64 - len(s) * 7) // 2
        text(c, xx, yy, col, s, "b")
    return layer


def box(x0, y0, x1, y1, col, at=0, until=None, fill=None):
    def layer(c, t):
        if not _on(t, at, until):
            return
        if fill:
            rect(c, x0, y0, x1, y1, fill)
        for x in range(x0, x1 + 1):
            px(c, x, y0, col); px(c, x, y1, col)
        for y in range(y0, y1 + 1):
            px(c, x0, y, col); px(c, x1, y, col)
    return layer


def bar(x0, x1, y, at=0, until=None, start=0.0, end=1.0, grow=(None, None), h=3,
        colors=(GREEN, GOLD, RED), back=(0, 40, 10)):
    """A meter that fills from start to end (fractions) between grow=(t0, t1)."""
    def layer(c, t):
        if not _on(t, at, until):
            return
        t0, t1 = grow
        f = lerp(start, end, ease(t, t0 if t0 is not None else at,
                                  t1 if t1 is not None else at + 2))
        col = colors[0] if f < 0.5 else colors[1] if f < 0.8 else colors[2]
        edge = x0 + int((x1 - x0) * min(f, 1.0))
        for x in range(x0, x1):
            for yy in range(y, y + h):
                px(c, x, yy, col if x < edge else back)
    return layer


def count(x, y, a, b, at=0, until=None, run=(None, None), fmt="{}", col=WHITE, size="s"):
    """A number that counts from a to b over run=(t0, t1)."""
    def layer(c, t):
        if not _on(t, at, until):
            return
        t0, t1 = run
        f = ease(t, t0 if t0 is not None else at, t1 if t1 is not None else at + 2)
        s = fmt.format(int(round(lerp(a, b, f))))
        rect(c, x - 1, y - TEXT_H[size], x + len(s) * FONT_W[size] - 1, y, (0, 0, 0))
        text(c, x, y, col, s, size)
    return layer


def draw(fn, at=0, until=None):
    """Any custom drawing: fn(canvas, t)."""
    def layer(c, t):
        if _on(t, at, until):
            fn(c, t)
    return layer


# --------------------------------------------------------------------------
# Effects
# --------------------------------------------------------------------------
def fx(kind, at=0, until=None, x=32, y=16, n=30, col=None, seed=1, w=64, h=32):
    rnd = random.Random(seed)
    pts = [(rnd.random(), rnd.random(), rnd.random()) for _ in range(n)]

    def layer(c, t):
        if not _on(t, at, until):
            return
        lt = t - at
        if kind == "rain":
            for a, b, s in pts:
                xx = a * 64; yy = (b * 34 + lt * (25 + s * 15)) % 34 - 2
                px(c, xx, yy, col or (80, 130, 220)); px(c, xx, yy + 1, (50, 80, 160))
        elif kind == "snow":
            for a, b, s in pts:
                xx = (a * 64 + math.sin(lt * 2 + s * 6) * 1.5) % 64
                yy = (b * 34 + lt * (4 + s * 5)) % 34 - 1
                px(c, xx, yy, col or WHITE)
        elif kind == "stars":
            for a, b, s in pts:
                if int(lt * 3 + s * 10) % 7:
                    px(c, a * 64, b * (h * 0.6), col or (200, 200, 255))
        elif kind == "zzz":
            for i in range(3):
                ph = (lt * 0.7 + i / 3) % 1
                text(c, x + i * 3 + ph * 3, y - ph * 10, col or (150, 190, 255), "z" if i < 2 else "Z")
        elif kind == "sparkle":
            for i, (a, b, s) in enumerate(pts[:8]):
                if int(lt * 8 + i) % 3 == 0:
                    xx, yy = x + (a - 0.5) * w * 0.4, y + (b - 0.5) * h * 0.4
                    for dx, dy in ((0, 0), (1, 0), (-1, 0), (0, 1), (0, -1)):
                        px(c, xx + dx, yy + dy, col or GOLD)
        elif kind == "burst":                        # explosion of dots from x,y
            for a, b, s in pts:
                ang = a * 6.283; r = lt * (10 + s * 14)
                px(c, x + math.cos(ang) * r, y + math.sin(ang) * r,
                   col or [GOLD, RED, GREEN, WHITE, BLUE][int(s * 5)])
        elif kind == "splash":
            for a, b, s in pts[:12]:
                ang = math.pi + a * math.pi; r = lt * (8 + s * 8)
                px(c, x + math.cos(ang) * r, y + math.sin(ang) * r + lt * lt * 12,
                   col or (130, 70, 30))
        elif kind == "notes":
            for i in range(3):
                ph = (lt * 0.6 + i / 3) % 1
                xx, yy = x + i * 5 + math.sin(ph * 6) * 2, y - ph * 14
                cc = col or [GOLD, PINK, CYAN][i]
                px(c, xx, yy, cc); px(c, xx + 1, yy, cc)
                for k in range(1, 4):
                    px(c, xx + 1, yy - k, cc)
        elif kind == "hearts":
            for i in range(3):
                ph = (lt * 0.5 + i / 3) % 1
                xx, yy = x + i * 6, y - ph * 12
                for dx, dy in ((0, 0), (2, 0), (-1, 1), (0, 1), (1, 1), (2, 1), (3, 1), (0, 2),
                               (1, 2), (2, 2), (1, 3)):
                    px(c, xx + dx, yy + dy, col or PINK)
        elif kind == "confetti":
            for a, b, s in pts:
                xx = (a * 64 + math.sin(lt * 3 + s * 9) * 2) % 64
                yy = (b * 20 + lt * (8 + s * 6)) % 34 - 2
                px(c, xx, yy, [GOLD, RED, GREEN, BLUE, PINK, WHITE][int(s * 6)])
        elif kind == "flash":
            if int(lt * 10) % 2 == 0 and lt < 0.6:
                rect(c, 0, 0, 63, 31, col or (255, 255, 230))
        elif kind == "speed":
            for a, b, s in pts[:10]:
                yy = y + (b - 0.5) * h
                xx = (a * 64 - lt * 90 * (0.6 + s)) % 80 - 8
                line(c, xx, yy, xx + 6, yy, col or (120, 120, 140))
        elif kind == "dizzy":
            for i in range(3):
                ang = lt * 6 + i * 2.09
                xx, yy = x + math.cos(ang) * 5, y + math.sin(ang) * 2
                for dx, dy in ((0, 0), (1, 0), (-1, 0), (0, 1), (0, -1)):
                    px(c, xx + dx, yy + dy, col or GOLD)
        elif kind == "steam":
            for i in range(3):
                ph = (lt * 0.8 + i / 3) % 1
                px(c, x + i * 2 + math.sin(ph * 8) * 1.5, y - ph * 9, col or (170, 170, 180))
        elif kind == "bubbles":
            for i, (a, b, s) in enumerate(pts[:10]):
                ph = (lt * (0.3 + s * 0.4) + a) % 1
                xx, yy = x + (a - 0.5) * w * 0.5 + math.sin(ph * 9) * 2, y - ph * h * 0.7
                px(c, xx, yy, col or CYAN)
        elif kind == "aurora":
            for xx in range(64):
                band = 6 + math.sin(xx * 0.15 + lt * 1.5) * 3
                for yy in range(int(band), int(band) + 4):
                    k = 1 - abs(yy - band - 2) / 3
                    px(c, xx, yy, (0, int(140 * k), int(80 * k + 40 * math.sin(xx * 0.1 + lt))))
        elif kind == "shake":
            pass                                      # handled by spr(shake=)
        elif kind == "smoke":
            for i in range(4):
                ph = (lt * 0.6 + i / 4) % 1
                circle(c, x + ph * 4, y - ph * 12, 1 + ph * 2, (90, 90, 100))
        elif kind == "fireworks":
            for k in range(3):
                cyc = (lt + k * 0.7) % 2.1
                cx, cy = 12 + k * 20, 8 + (k % 2) * 4
                if cyc < 0.6:
                    px(c, cx, 31 - cyc / 0.6 * (31 - cy), GOLD)
                else:
                    r = (cyc - 0.6) * 8
                    for j in range(10):
                        ang = j * 0.628
                        px(c, cx + math.cos(ang) * r, cy + math.sin(ang) * r,
                           [RED, GREEN, GOLD][k])
    return layer


# --------------------------------------------------------------------------
# Backgrounds
# --------------------------------------------------------------------------
def _fill(c, col):
    if hasattr(c, "Fill"):
        c.Fill(*col)
    else:
        rect(c, 0, 0, 63, 31, col)


def _floor(c, col, y=29, col2=None):
    for yy in range(y, 32):
        for x in range(64):
            px(c, x, yy, col if (col2 is None or (x // 4 + yy) % 2) else col2)


def background(c, kind, t):
    if kind is None or kind == "dark":
        _fill(c, (0, 0, 0))
    elif kind == "night":
        _fill(c, (0, 0, 22))
    elif kind == "room":                              # living room at night
        _fill(c, (14, 6, 22)); _floor(c, (70, 40, 15), 29, (60, 34, 12))
    elif kind == "kitchen":
        _fill(c, (20, 14, 8))
        for y in range(0, 22, 4):
            for x in range(0, 64, 4):
                px(c, x, y, (40, 30, 20))
        _floor(c, (200, 200, 205), 29, (40, 40, 50))
    elif kind == "snow":
        _fill(c, (0, 8, 35)); _floor(c, (230, 235, 245), 27, (200, 210, 230))
    elif kind == "pole":                              # North Pole: aurora + snow
        _fill(c, (0, 4, 20)); fx("aurora")(c, t); _floor(c, (230, 235, 245), 27, (200, 210, 230))
    elif kind == "sea":
        _fill(c, (0, 8, 30))
        for x in range(64):
            for y in range(26, 32):
                px(c, x, y, (0, 60 + 30 * ((x // 3 + y + int(t * 3)) % 2), 150))
    elif kind == "day":
        _fill(c, (40, 110, 200))
        for x in range(64):
            for y in range(27, 32):
                px(c, x, y, (40, 140, 40))
    elif kind == "city":                              # Seattle skyline at night
        _fill(c, (0, 6, 28))
        heights = [5, 9, 6, 12, 8, 15, 7, 11, 6, 13, 9, 5, 10, 7, 4, 8]
        for i, hgt in enumerate(heights):
            for x in range(i * 4, i * 4 + 4):
                for y in range(31 - hgt, 32):
                    px(c, x, y, (25, 25, 50))
                    if (x + y) % 3 == 0 and y < 30 and (x * 7 + y) % 5 == 0:
                        px(c, x, y, (200, 180, 80))
    elif kind == "blueprint":
        _fill(c, (0, 20, 70))
        for x in range(0, 64, 4):
            for y in range(32):
                px(c, x, y, (0, 35, 100))
        for y in range(0, 32, 4):
            for x in range(64):
                px(c, x, y, (0, 35, 100))
    elif kind == "nv":                                # night-vision camera
        rnd = random.Random(int(t * 8))
        for y in range(32):
            for x in range(64):
                px(c, x, y, (0, 16 + rnd.randint(0, 14), 0))
    elif kind == "stage":
        _fill(c, (25, 0, 30)); _floor(c, (110, 0, 110), 29)
        for x in range(0, 64, 2):
            px(c, x, 0, (200, 30, 30)); px(c, x + 1, 1, (200, 30, 30))
    elif kind == "workshop":
        _fill(c, (30, 12, 6))
        for x in range(0, 64, 8):
            for y in range(0, 26):
                px(c, x, y, (45, 20, 10))
        _floor(c, (110, 60, 25), 28, (90, 50, 20))
    elif kind == "chalk":
        _fill(c, (15, 40, 25)); _floor(c, (90, 50, 20), 30)
    elif kind == "gym":
        _fill(c, (25, 18, 10)); _floor(c, (180, 120, 60), 28, (160, 105, 50))
    elif kind == "ring":                              # boxing ring
        _fill(c, (10, 0, 20)); _floor(c, (40, 40, 140), 27)
        for y in (17, 21):
            for x in range(64):
                px(c, x, y, (220, 30, 30) if y == 17 else (230, 230, 230))
    else:
        _fill(c, (0, 0, 0))


# --------------------------------------------------------------------------
# Episode
# --------------------------------------------------------------------------
class Ep:
    def __init__(self, key, phase, title, seconds, bg, *layers):
        self.key, self.phase, self.title, self.seconds, self.bg = key, phase, title, seconds, bg
        self.layers = layers

    def draw(self, c, t):
        background(c, self.bg, t)
        for L in self.layers:
            L(c, t)
