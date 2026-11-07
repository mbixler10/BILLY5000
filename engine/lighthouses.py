"""
Lighthouses for Billy's night-navigation lesson.

Every lighthouse has its own blinking "signature" (its light characteristic),
so a sailor at night can tell exactly which light they're looking at.
The codes are the ones printed on nautical charts:

    FL       flashing      - short flashes, dark most of the time
    FL(2)    group flash   - two flashes together, then dark
    OC       occulting     - ON most of the time, blinks OFF briefly
    ISO      isophase      - equal time on and off
    F        fixed         - steady light, never blinks
    AL WR    alternating   - white and red take turns
    MO(U)    morse code    - spells a letter (U = dot dot dash)
    W / R    white / red,  then the number of seconds for one full cycle

To add a lighthouse, copy a line in LIGHTHOUSES and change it.
    (name, town, state, light, tower)
    light = a pattern from the helpers below, or retired(year)
    tower = "white", "spiral", "bands", "checker", "redwhite", "brick",
            "red", "redtop", "blacktop", "redband", "brownband", "brownbottom"

Light patterns are a list of (seconds, color) steps; color None = dark.
"""

W, R, G = "W", "R", "G"
LIGHT_RGB = {W: (255, 244, 200), R: (255, 40, 30), G: (40, 255, 80)}
COLOR_WORD = {W: "WHITE", R: "RED", G: "GREEN"}
NUM_WORD = {1: "ONE", 2: "TWO", 3: "THREE", 4: "FOUR", 5: "FIVE", 6: "SIX"}
STATES = {
    "WA": "WASHINGTON", "OR": "OREGON", "CA": "CALIFORNIA", "ME": "MAINE",
    "MA": "MASSACHUSETTS", "RI": "RHODE ISLAND", "CT": "CONNECTICUT",
    "NY": "NEW YORK", "NJ": "NEW JERSEY", "DE": "DELAWARE", "MD": "MARYLAND",
    "VA": "VIRGINIA", "NC": "NORTH CAROLINA", "SC": "SOUTH CAROLINA",
    "GA": "GEORGIA", "FL": "FLORIDA",
}


def _secs(p):
    return ("%g" % p).upper()


class Light:
    def __init__(self, code, steps, words, retired=None):
        self.code = code            # chart code, e.g. "FL(2) W 20S"
        self.steps = steps          # [(seconds, color or None), ...]
        self.words = words          # plain English for Billy
        self.retired = retired      # year it went dark, or None
        self.period = sum(d for d, _ in steps) if steps else 0

    def color_at(self, t):
        """Which color is showing t seconds into the pattern (None = dark)."""
        if self.retired:
            return None
        if self.period == 0:
            return self.steps[0][1] if self.steps else None
        t %= self.period
        for d, c in self.steps:
            if t < d:
                return c
            t -= d
        return None


def fl(period, color=W, n=1, flash=0.6, gap=1.2):
    """n quick flashes, then dark for the rest of the period."""
    steps = []
    for i in range(n):
        steps.append((flash, color))
        if i < n - 1:
            steps.append((gap, None))
    steps.append((period - sum(d for d, _ in steps), None))
    code = "FL%s %s %sS" % ("" if n == 1 else "(%d)" % n, color, _secs(period))
    if n == 1:
        words = "ONE %s FLASH EVERY %s SECONDS" % (COLOR_WORD[color], _secs(period))
    else:
        words = "%s %s FLASHES EVERY %s SECONDS" % (NUM_WORD[n], COLOR_WORD[color], _secs(period))
    return Light(code, steps, words)


def oc(period, color=W, n=1, eclipse=1.0, gap=1.0):
    """On most of the time, blinks off n times."""
    steps = []
    for i in range(n):
        steps.append((eclipse, None))
        if i < n - 1:
            steps.append((gap, color))
    steps.append((period - sum(d for d, _ in steps), color))
    code = "OC%s %s %sS" % ("" if n == 1 else "(%d)" % n, color, _secs(period))
    times = "BLINKS OFF" if n == 1 else "BLINKS OFF %s TIMES" % NUM_WORD[n]
    words = "%s LIGHT THAT %s EVERY %s SECONDS" % (COLOR_WORD[color], times, _secs(period))
    return Light(code, steps, words)


def iso(period, color=W):
    steps = [(period / 2, color), (period / 2, None)]
    words = "%s, EQUAL ON AND OFF, EVERY %s SECONDS" % (COLOR_WORD[color], _secs(period))
    return Light("ISO %s %sS" % (color, _secs(period)), steps, words)


def fixed(color=W):
    return Light("F %s" % color, [(1, color)], "STEADY %s LIGHT, IT NEVER BLINKS" % COLOR_WORD[color])


def alt(period, colors=(W, R), flash=1.0):
    """Colors take turns, one flash each, evenly spaced."""
    each = period / len(colors)
    steps = []
    for c in colors:
        steps += [(flash, c), (each - flash, None)]
    names = " AND ".join(COLOR_WORD[c] for c in colors)
    words = "%s FLASHES TAKE TURNS EVERY %s SECONDS" % (names, _secs(period))
    return Light("AL %s %sS" % ("".join(colors), _secs(period)), steps, words)


def morse(period, letter, pattern, color=W, dot=0.5):
    """pattern like '..-' for U."""
    steps = []
    for i, s in enumerate(pattern):
        steps.append((dot if s == "." else dot * 3, color))
        if i < len(pattern) - 1:
            steps.append((dot, None))
    steps.append((period - sum(d for d, _ in steps), None))
    spoken = " ".join("DOT" if s == "." else "DASH" for s in pattern)
    words = "MORSE CODE %s (%s) EVERY %s SECONDS" % (letter, spoken, _secs(period))
    return Light("MO(%s) %s %sS" % (letter, color, _secs(period)), steps, words)


def retired(year):
    return Light("RETIRED", [], "RETIRED IN %d, IT NO LONGER SHINES" % year, retired=year)


# Point Wilson: white light, goes dark with a red flash in the middle of the dark spell.
POINT_WILSON = Light("AL OC WR 20S", [(15, W), (2, None), (1, R), (2, None)],
                     "WHITE LIGHT, GOES DARK WITH A RED FLASH, EVERY 20 SECONDS")

LIGHTHOUSES = [
    # ----------------------------------------------------------- WEST COAST
    # Washington
    ("CAPE FLATTERY", "NEAH BAY", "WA", fl(20, n=2), "white"),
    ("NEW DUNGENESS", "SEQUIM", "WA", fl(5), "white"),
    ("POINT WILSON", "PORT TOWNSEND", "WA", POINT_WILSON, "white"),
    ("MUKILTEO", "MUKILTEO", "WA", fl(5, flash=2.0), "white"),
    ("WEST POINT", "SEATTLE", "WA", alt(10), "white"),
    ("ALKI POINT", "SEATTLE", "WA", fl(5), "white"),
    ("GRAYS HARBOR", "WESTPORT", "WA", alt(15), "white"),
    ("NORTH HEAD", "ILWACO", "WA", fl(30, n=2, gap=6.9), "white"),
    ("CAPE DISAPPOINTMENT", "ILWACO", "WA", alt(30), "blacktop"),
    # Oregon
    ("HECETA HEAD", "FLORENCE", "OR", fl(10), "white"),
    ("YAQUINA HEAD", "NEWPORT", "OR", fl(20, n=2, flash=2.0, gap=2.0), "white"),
    ("CAPE BLANCO", "PORT ORFORD", "OR", fl(20), "white"),
    # California
    ("BATTERY POINT", "CRESCENT CITY", "CA", fl(30), "white"),
    ("POINT ARENA", "POINT ARENA", "CA", fl(15), "white"),
    ("POINT BONITA", "SAUSALITO", "CA", oc(4), "white"),
    ("PIGEON POINT", "PESCADERO", "CA", fl(10), "white"),
    ("POINT PINOS", "PACIFIC GROVE", "CA", oc(4), "white"),
    ("POINT SUR", "BIG SUR", "CA", fl(15), "white"),
    ("PIEDRAS BLANCAS", "SAN SIMEON", "CA", fl(10), "white"),
    ("POINT CONCEPTION", "LOMPOC", "CA", fl(30), "white"),
    ("POINT VICENTE", "RANCHO PALOS VERDES", "CA", fl(20, n=2), "white"),
    ("POINT LOMA", "SAN DIEGO", "CA", fl(15), "white"),     # the "new" 1891 light at the bottom of the cliff
    # ----------------------------------------------------------- EAST COAST
    # Maine
    ("WEST QUODDY HEAD", "LUBEC", "ME", fl(15, n=2), "redwhite"),
    ("BASS HARBOR HEAD", "TREMONT", "ME", oc(4, R), "white"),
    ("OWLS HEAD", "OWLS HEAD", "ME", fixed(W), "white"),
    ("PEMAQUID POINT", "BRISTOL", "ME", fl(6), "white"),
    ("PORTLAND HEAD", "CAPE ELIZABETH", "ME", fl(4), "white"),
    ("CAPE NEDDICK (NUBBLE)", "YORK", "ME", iso(6, R), "white"),
    # Massachusetts
    ("BOSTON LIGHT", "BOSTON HARBOR", "MA", fl(10), "white"),
    ("RACE POINT", "PROVINCETOWN", "MA", fl(10), "white"),
    ("HIGHLAND (CAPE COD)", "TRURO", "MA", fl(5), "white"),
    ("NAUSET", "EASTHAM", "MA", alt(10), "redtop"),
    ("CHATHAM", "CHATHAM", "MA", fl(10, n=2), "white"),
    # Nantucket
    ("BRANT POINT", "NANTUCKET", "MA", oc(4, R), "white"),
    ("SANKATY HEAD", "SIASCONSET", "MA", fl(7.5), "redband"),
    ("GREAT POINT", "NANTUCKET", "MA", fl(5), "white"),
    # Rhode Island
    ("POINT JUDITH", "NARRAGANSETT", "RI", oc(15, n=3), "brownbottom"),
    ("BEAVERTAIL", "JAMESTOWN", "RI", fl(10), "white"),
    # Connecticut
    ("NEW LONDON LEDGE", "NEW LONDON", "CT",
     Light("FL(3) W + R 30S",
           [(0.6, W), (1.2, None), (0.6, W), (1.2, None), (0.6, W), (1.2, None), (0.6, R), (24.0, None)],
           "THREE WHITE FLASHES THEN A RED ONE, EVERY 30 SECONDS"), "brick"),
    # New York
    ("MONTAUK POINT", "MONTAUK", "NY", fl(5), "brownband"),
    ("FIRE ISLAND", "BAY SHORE", "NY", fl(7.5), "bands"),
    ("EXECUTION ROCKS", "SANDS POINT", "NY", fl(10), "brownband"),
    # New Jersey
    ("SANDY HOOK", "HIGHLANDS", "NJ", fixed(W), "white"),
    ("BARNEGAT", "BARNEGAT LIGHT", "NJ", fl(10), "redtop"),
    ("CAPE MAY", "CAPE MAY POINT", "NJ", fl(15), "white"),
    # Delaware / Maryland / Virginia
    ("HARBOR OF REFUGE", "LEWES", "DE", fl(5), "white"),
    ("THOMAS POINT SHOAL", "ANNAPOLIS", "MD", fl(5), "white"),
    ("CAPE HENRY", "VIRGINIA BEACH", "VA", morse(20, "U", "..-"), "checker"),
    ("ASSATEAGUE", "CHINCOTEAGUE", "VA", fl(5, n=2, flash=0.4, gap=0.8), "redwhite"),
    # North Carolina
    ("CURRITUCK BEACH", "COROLLA", "NC", fl(20), "brick"),
    ("BODIE ISLAND", "NAGS HEAD", "NC", fl(30, n=2, flash=2.5, gap=2.5), "bands"),
    ("CAPE HATTERAS", "BUXTON", "NC", fl(7.5), "spiral"),
    ("OCRACOKE", "OCRACOKE", "NC", fixed(W), "white"),
    ("CAPE LOOKOUT", "HARKERS ISLAND", "NC", fl(15), "checker"),
    # South Carolina / Georgia / Florida
    ("TYBEE ISLAND", "TYBEE ISLAND", "GA", fixed(W), "blacktop"),
    ("ST. AUGUSTINE", "ST. AUGUSTINE", "FL", fl(30), "spiral"),
    ("JUPITER INLET", "JUPITER", "FL", fl(30, n=2), "red"),
    ("CAPE FLORIDA", "KEY BISCAYNE", "FL", fl(6), "white"),
]


def get(name):
    for row in LIGHTHOUSES:
        if row[0] == name:
            return row
    return None
