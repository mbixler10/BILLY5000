"""
Team colors for the sports pages, ported from the old clock (test32.py / test64.py).
Pro opponents come from the color books below. College opponents use each
school's colors from ESPN, looked up once and remembered (see sports.py).
"""

# ---- opponent color books, ported from test64.py / test.py
# MLB: primary (chip) and secondary (stripe), official team colors.
MLB_COLORS = {
    "ARI": "#A71930", "ATL": "#13274F", "BAL": "#DF4601", "BOS": "#BD3039", "CHC": "#0E3386",
    "CWS": "#27251F", "CIN": "#C6011F", "CLE": "#00385D", "COL": "#33006F", "DET": "#0C2340",
    "HOU": "#002D62", "KC": "#004687", "LAA": "#BA0021", "LAD": "#005A9C", "MIA": "#00A3E0",
    "MIL": "#12284B", "MIN": "#002B5C", "NYM": "#002D72", "NYY": "#0C2340", "ATH": "#003831",
    "PHI": "#E81828", "PIT": "#27251F", "SD": "#2F241D", "SEA": "#0C2C56", "SF": "#FD5A1E",
    "STL": "#C41E3A", "TB": "#092C5C", "TEX": "#003278", "TOR": "#134A8E", "WSH": "#AB0003",
}
MLB_SECONDARY = {
    "ARI": "#E3D4AD", "ATL": "#CE1141", "BAL": "#000000", "BOS": "#0C2340", "CHC": "#CC3433",
    "CWS": "#C4CED4", "CIN": "#000000", "CLE": "#E50022", "COL": "#C4CED4", "DET": "#FA4616",
    "HOU": "#EB6E1F", "KC": "#BD9B60", "LAA": "#003263", "LAD": "#EF3E42", "MIA": "#EF3340",
    "MIL": "#FFC52F", "MIN": "#D31145", "NYM": "#FF5910", "NYY": "#C4CED4", "ATH": "#EFB21E",
    "PHI": "#002D72", "PIT": "#FDB827", "SD": "#FFC425", "SEA": "#005C5C", "SF": "#27251F",
    "STL": "#0C2340", "TB": "#8FBCE6", "TEX": "#C0111F", "TOR": "#E8291C", "WSH": "#14225A",
}
NFL_COLORS = {
    "ARI": ((151, 35, 63), (255, 255, 255)), "ATL": ((167, 25, 48), (165, 172, 175)),
    "BAL": ((36, 23, 115), (158, 124, 12)),  "BUF": ((0, 51, 141), (198, 12, 48)),
    "CAR": ((0, 133, 202), (191, 192, 191)), "CHI": ((11, 22, 42), (200, 56, 3)),
    "CIN": ((251, 79, 20), (20, 20, 20)),    "CLE": ((49, 29, 0), (255, 60, 0)),
    "DAL": ((4, 30, 66), (134, 147, 151)),   "DEN": ((251, 79, 20), (0, 34, 68)),
    "DET": ((0, 118, 182), (176, 176, 176)), "GB":  ((32, 55, 49), (255, 182, 18)),
    "HOU": ((3, 32, 47), (167, 25, 48)),     "IND": ((0, 44, 95), (162, 170, 173)),
    "JAX": ((0, 103, 120), (215, 162, 42)),  "KC":  ((227, 24, 55), (255, 182, 18)),
    "LV":  ((10, 10, 10), (165, 172, 175)),  "LAC": ((0, 128, 198), (255, 194, 14)),
    "LAR": ((0, 53, 148), (255, 209, 0)),    "MIA": ((0, 142, 151), (252, 76, 2)),
    "MIN": ((79, 38, 131), (255, 198, 10)),  "NE":  ((0, 34, 68), (198, 12, 48)),
    "NO":  ((16, 24, 32), (211, 188, 141)),  "NYG": ((11, 34, 101), (163, 13, 45)),
    "NYJ": ((18, 87, 64), (255, 255, 255)),  "PHI": ((0, 76, 84), (165, 172, 175)),
    "PIT": ((16, 24, 32), (255, 182, 18)),   "SF":  ((170, 0, 0), (173, 153, 93)),
    "SEA": ((0, 34, 68), (105, 190, 40)),    "TB":  ((213, 10, 10), (52, 48, 43)),
    "TEN": ((12, 35, 64), (75, 146, 219)),    "WSH": ((90, 20, 20), (255, 182, 18)),
}
# NHL: (primary, secondary) official team colors. Primary fills the chip,
# secondary is the stripe on its edge. Black is lifted to dark gray on the LEDs.
NHL_COLORS = {
    "ANA": ("#FC4C02", "#B9975B"),   # Ducks: orange, gold (black is the 3rd color)
    "BOS": ("#000000", "#FFB81C"),   # Bruins: black, gold
    "BUF": ("#003087", "#FFB81C"),   # Sabres: royal blue, gold
    "CGY": ("#C8102E", "#F1BE48"),   # Flames: red, gold
    "CAR": ("#CE1126", "#A2AAAD"),   # Hurricanes: red, silver
    "CHI": ("#CF0A2C", "#FFFFFF"),   # Blackhawks: red, white
    "COL": ("#6F263D", "#236192"),   # Avalanche: burgundy, blue
    "CBJ": ("#002654", "#CE1126"),   # Blue Jackets: navy, red
    "DAL": ("#006847", "#8F8F8C"),   # Stars: victory green, silver
    "DET": ("#CE1126", "#FFFFFF"),   # Red Wings: red, white
    "EDM": ("#041E42", "#FF4C00"),   # Oilers: navy, orange
    "FLA": ("#C8102E", "#041E42"),   # Panthers: red, navy
    "LA":  ("#111111", "#A2AAAD"),   # Kings: black, silver
    "MIN": ("#154734", "#A6192E"),   # Wild: forest green, iron range red
    "MTL": ("#AF1E2D", "#192168"),   # Canadiens: red, blue
    "NSH": ("#FFB81C", "#041E42"),   # Predators: gold, navy
    "NJ":  ("#CE1126", "#000000"),   # Devils: red, black
    "NYI": ("#00539B", "#F47D30"),   # Islanders: royal blue, orange
    "NYR": ("#0038A8", "#CE1126"),   # Rangers: blue, red
    "OTT": ("#C52032", "#C2912C"),   # Senators: red, gold (black is the 3rd color)
    "PHI": ("#F74902", "#000000"),   # Flyers: orange, black
    "PIT": ("#000000", "#FCB514"),   # Penguins: black, gold
    "SJ":  ("#006D75", "#EA7200"),   # Sharks: teal, orange
    "SEA": ("#001628", "#99D9D9"),   # Kraken: deep sea blue, ice blue
    "STL": ("#002F87", "#FCB514"),   # Blues: blue, gold
    "TB":  ("#002868", "#FFFFFF"),   # Lightning: blue, white
    "TOR": ("#00205B", "#FFFFFF"),   # Maple Leafs: blue, white
    "UTA": ("#6CACE4", "#010101"),   # Utah Mammoth: mountain blue, rock black
    "UTAH": ("#6CACE4", "#010101"),  # (ESPN sometimes spells it out)
    "VAN": ("#00205B", "#00843D"),   # Canucks: blue, green
    "VGK": ("#B4975A", "#333F42"),   # Golden Knights: gold, steel gray
    "WSH": ("#C8102E", "#041E42"),   # Capitals: red, navy
    "WPG": ("#041E42", "#AC162C"),   # Jets: navy, red
}
# College slugs that don't resolve on ESPN's team endpoint -> numeric id (from test64.py)
NCAAF_ID_OVERRIDES = {"AFA": "2005"}  # Air Force Falcons

_college = {}     # (league, abbr) -> (primary, secondary), filled in by sports.py


def hexc(h, default=(120, 120, 120)):
    if isinstance(h, tuple):
        return h
    try:
        h = str(h).lstrip("#")
        return (int(h[0:2], 16), int(h[2:4], 16), int(h[4:6], 16))
    except Exception:
        return default


def lum(c):
    return 0.299 * c[0] + 0.587 * c[1] + 0.114 * c[2]


def mix(a, b, t):
    return tuple(int(x + (y - x) * t) for x, y in zip(a, b))


def display_color(c):
    """Lift near-black team colors so they still read on LEDs."""
    L = lum(c)
    if L < 45:
        return mix(c, (255, 255, 255), 0.18) if L > 15 else mix(c, (90, 90, 110), 0.5)
    return c


def resolve(league, abbr, api_color=None, api_alt=None):
    """(primary, secondary) for an opponent. Never touches the network."""
    lg = league.split("/")[-1]
    if lg == "mlb" and abbr in MLB_COLORS:
        return hexc(MLB_COLORS[abbr]), hexc(MLB_SECONDARY.get(abbr, "#FFFFFF"))
    if lg == "nfl" and abbr in NFL_COLORS:
        return NFL_COLORS[abbr]
    if lg == "nhl" and abbr in NHL_COLORS:
        prim, sec = NHL_COLORS[abbr]
        return hexc(prim), hexc(sec)
    if (league, abbr) in _college:
        return _college[(league, abbr)]
    return hexc(api_color, (85, 85, 85)), hexc(api_alt, (200, 200, 200))


def needs_lookup(league, abbr):
    return league.startswith(("football/college", "basketball/")) and (league, abbr) not in _college


def remember(league, abbr, team_json):
    prim = hexc(team_json.get("color"), (60, 60, 65))
    sec = hexc(team_json.get("alternateColor"), (255, 255, 255))
    _college[(league, abbr)] = (prim, sec if sec != prim else (255, 255, 255))
