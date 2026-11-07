"""
International Code of Signals: the 26 letter flags, their radio names and their
official single-flag meanings (ICS, IMO 2005 edition).

Letter flags are square (A and B swallow-tailed). Numeral pennants 0-9 are
tapered; they have no message of their own, so their "meaning" is the number
and how it's said on the radio.
"""
from engine.teamcolors import hexc as C

RED = C("#D21034")
BLUE = C("#0038A8")
YELLOW = C("#FFD100")
WHITE = C("#FFFFFF")
BLACK = C("#000000")

# letter: (radio name, meaning as a single flag)
SIGNALS = {
    "A": ("ALFA", "I HAVE A DIVER DOWN; KEEP WELL CLEAR AT SLOW SPEED"),
    "B": ("BRAVO", "I AM TAKING IN, DISCHARGING OR CARRYING DANGEROUS GOODS"),
    "C": ("CHARLIE", "AFFIRMATIVE (YES)"),
    "D": ("DELTA", "KEEP CLEAR OF ME; I AM MANEUVERING WITH DIFFICULTY"),
    "E": ("ECHO", "I AM ALTERING MY COURSE TO STARBOARD"),
    "F": ("FOXTROT", "I AM DISABLED; COMMUNICATE WITH ME"),
    "G": ("GOLF", "I REQUIRE A PILOT"),
    "H": ("HOTEL", "I HAVE A PILOT ON BOARD"),
    "I": ("INDIA", "I AM ALTERING MY COURSE TO PORT"),
    "J": ("JULIETT", "I AM ON FIRE AND HAVE DANGEROUS CARGO ON BOARD; KEEP WELL CLEAR OF ME"),
    "K": ("KILO", "I WISH TO COMMUNICATE WITH YOU"),
    "L": ("LIMA", "YOU SHOULD STOP YOUR VESSEL INSTANTLY"),
    "M": ("MIKE", "MY VESSEL IS STOPPED AND MAKING NO WAY THROUGH THE WATER"),
    "N": ("NOVEMBER", "NEGATIVE (NO)"),
    "O": ("OSCAR", "MAN OVERBOARD"),
    "P": ("PAPA", "IN HARBOR: ALL PERSONS REPORT ON BOARD; THE VESSEL IS ABOUT TO PROCEED TO SEA"),
    "Q": ("QUEBEC", "MY VESSEL IS HEALTHY AND I REQUEST FREE PRATIQUE"),
    "R": ("ROMEO", "NO MEANING ON ITS OWN; USED TO SPELL SIGNALS"),
    "S": ("SIERRA", "I AM OPERATING ASTERN PROPULSION"),
    "T": ("TANGO", "KEEP CLEAR OF ME; I AM ENGAGED IN PAIR TRAWLING"),
    "U": ("UNIFORM", "YOU ARE RUNNING INTO DANGER"),
    "V": ("VICTOR", "I REQUIRE ASSISTANCE"),
    "W": ("WHISKEY", "I REQUIRE MEDICAL ASSISTANCE"),
    "X": ("X-RAY", "STOP CARRYING OUT YOUR INTENTIONS AND WATCH FOR MY SIGNALS"),
    "Y": ("YANKEE", "I AM DRAGGING MY ANCHOR"),
    "Z": ("ZULU", "I REQUIRE A TUG"),
    # numeral pennants: (radio pronunciation, meaning line)
    "0": ("ZE-RO", "NUMBER 0 - SAID ZE-RO ON THE RADIO"),
    "1": ("WUN", "NUMBER 1 - SAID WUN ON THE RADIO"),
    "2": ("TOO", "NUMBER 2 - SAID TOO ON THE RADIO"),
    "3": ("TREE", "NUMBER 3 - SAID TREE ON THE RADIO"),
    "4": ("FOW-ER", "NUMBER 4 - SAID FOW-ER ON THE RADIO"),
    "5": ("FIFE", "NUMBER 5 - SAID FIFE ON THE RADIO"),
    "6": ("SIX", "NUMBER 6 - SAID SIX ON THE RADIO"),
    "7": ("SEV-EN", "NUMBER 7 - SAID SEV-EN ON THE RADIO"),
    "8": ("AIT", "NUMBER 8 - SAID AIT ON THE RADIO"),
    "9": ("NIN-ER", "NUMBER 9 - SAID NIN-ER ON THE RADIO"),
}


def _box(f, x0, y0, s, fn):
    """Paint each pixel of the s x s box with fn(u, v) -> color, u/v in 0..1."""
    for j in range(s):
        for i in range(s):
            c = fn((i + 0.5) / s, (j + 0.5) / s)
            if c is not None:
                f.set(x0 + i, y0 + j, c)


def _swallowtail(u, v):
    """True if (u, v) falls in the V notch cut from the fly end."""
    return u > 1 - 0.25 * (1 - abs(v - 0.5) * 2)


def _bands(colors, horizontal=True):
    n = len(colors)
    return lambda u, v: colors[min(n - 1, int((v if horizontal else u) * n))]


DESIGNS = {
    "A": lambda u, v: None if _swallowtail(u, v) else (WHITE if u < 0.5 else BLUE),
    "B": lambda u, v: None if _swallowtail(u, v) else RED,
    "C": _bands([BLUE, WHITE, RED, WHITE, BLUE]),
    "D": lambda u, v: BLUE if 0.25 <= v < 0.75 else YELLOW,
    "E": _bands([BLUE, RED]),
    "F": lambda u, v: RED if abs(u - 0.5) + abs(v - 0.5) <= 0.5 else WHITE,
    "G": _bands([YELLOW, BLUE] * 3, horizontal=False),
    "H": _bands([WHITE, RED], horizontal=False),
    "I": lambda u, v: BLACK if (u - 0.5) ** 2 + (v - 0.5) ** 2 <= 0.3 ** 2 else YELLOW,
    "J": _bands([BLUE, WHITE, BLUE]),
    "K": _bands([YELLOW, BLUE], horizontal=False),
    "L": lambda u, v: YELLOW if (u < 0.5) == (v < 0.5) else BLACK,
    "M": lambda u, v: WHITE if abs(u - v) < 0.11 or abs(u + v - 1) < 0.11 else BLUE,
    "N": lambda u, v: BLUE if (int(u * 4) + int(v * 4)) % 2 == 0 else WHITE,
    "O": lambda u, v: RED if u > v else YELLOW,            # red upper fly, yellow lower hoist
    "P": lambda u, v: WHITE if abs(u - 0.5) < 0.17 and abs(v - 0.5) < 0.17 else BLUE,
    "Q": lambda u, v: YELLOW,
    "R": lambda u, v: YELLOW if abs(u - 0.5) < 0.09 or abs(v - 0.5) < 0.09 else RED,
    "S": lambda u, v: BLUE if abs(u - 0.5) < 0.17 and abs(v - 0.5) < 0.17 else WHITE,
    "T": _bands([RED, WHITE, BLUE], horizontal=False),
    "U": lambda u, v: RED if (u < 0.5) == (v < 0.5) else WHITE,
    "V": lambda u, v: RED if abs(u - v) < 0.11 or abs(u + v - 1) < 0.11 else WHITE,
    "W": lambda u, v: (RED if max(abs(u - 0.5), abs(v - 0.5)) < 0.17
                       else WHITE if max(abs(u - 0.5), abs(v - 0.5)) < 0.34 else BLUE),
    "X": lambda u, v: BLUE if abs(u - 0.5) < 0.09 or abs(v - 0.5) < 0.09 else WHITE,
    "Y": lambda u, v: YELLOW if int((u - v + 1) * 5) % 2 == 0 else RED,   # "bendy of ten"
    "Z": lambda u, v: (YELLOW if v < u and v < 1 - u else BLUE if u > v and u > 1 - v
                       else RED if v > u and v > 1 - u else BLACK),
}


# numeral pennants, drawn as if square; the taper is applied in draw_signal
PENNANTS = {
    "0": _bands([YELLOW, RED, YELLOW], horizontal=False),
    "1": lambda u, v: RED if ((u - 0.3) * 1.6) ** 2 + (v - 0.5) ** 2 <= 0.27 ** 2 else WHITE,
    "2": lambda u, v: WHITE if ((u - 0.3) * 1.6) ** 2 + (v - 0.5) ** 2 <= 0.27 ** 2 else BLUE,
    "3": _bands([RED, WHITE, BLUE], horizontal=False),
    "4": lambda u, v: WHITE if abs(u - 0.3) < 0.07 or abs(v - 0.5) < 0.12 else RED,
    "5": _bands([YELLOW, BLUE], horizontal=False),
    "6": _bands([BLACK, WHITE]),
    "7": _bands([YELLOW, RED]),
    "8": lambda u, v: RED if abs(u - 0.3) < 0.07 or abs(v - 0.5) < 0.12 else WHITE,
    "9": lambda u, v: ((WHITE if v < 0.5 else RED) if u < 0.5 else (BLACK if v < 0.5 else YELLOW)),
}
TAPER = 0.72          # the fly end is 28% as tall as the hoist


def draw_signal(f, letter, x0, y0, s):
    if letter not in PENNANTS:
        _box(f, x0, y0, s, DESIGNS[letter])
        return
    w = int(s * 1.15)                                  # pennants are a bit longer than tall
    design = PENNANTS[letter]
    for j in range(s):
        for i in range(w):
            u, v = (i + 0.5) / w, (j + 0.5) / s
            half = 0.5 * (1 - TAPER * u)
            if abs(v - 0.5) <= half:
                vv = (v - 0.5) / (2 * half) + 0.5       # stripes follow the taper
                f.set(x0 + i, y0 + j, design(u, vv))
