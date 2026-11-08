"""
Olympic medal table, read from Wikipedia's "<year> Summer Olympics medal table"
page during the Games (and for a few days after). Checked every 20 minutes.

To test the reader on a past Games from the PC:
    python -m engine.medals "2024 Summer Olympics medal table"
"""
import json
import logging
import re
import threading
import time
import urllib.parse
import urllib.request
from html.parser import HTMLParser

log = logging.getLogger("billy5000.medals")
UA = "BILLY5000/1.0 (family LED clock; Olympic medal table every 20 min)"

# Country names as Wikipedia writes them -> the 3-letter codes on the board.
CODES = {
    "UNITED STATES": "USA", "CHINA": "CHN", "JAPAN": "JPN", "AUSTRALIA": "AUS",
    "FRANCE": "FRA", "NETHERLANDS": "NED", "GREAT BRITAIN": "GBR", "SOUTH KOREA": "KOR",
    "ITALY": "ITA", "GERMANY": "GER", "NEW ZEALAND": "NZL", "CANADA": "CAN",
    "UZBEKISTAN": "UZB", "HUNGARY": "HUN", "SPAIN": "ESP", "SWEDEN": "SWE", "KENYA": "KEN",
    "NORWAY": "NOR", "IRELAND": "IRL", "BRAZIL": "BRA", "IRAN": "IRI", "UKRAINE": "UKR",
    "ROMANIA": "ROU", "GEORGIA": "GEO", "BELGIUM": "BEL", "BULGARIA": "BUL", "SERBIA": "SRB",
    "CZECH REPUBLIC": "CZE", "CZECHIA": "CZE", "DENMARK": "DEN", "AZERBAIJAN": "AZE",
    "CROATIA": "CRO", "CUBA": "CUB", "BAHRAIN": "BRN", "SLOVENIA": "SLO",
    "CHINESE TAIPEI": "TPE", "AUSTRIA": "AUT", "HONG KONG": "HKG", "PHILIPPINES": "PHI",
    "ALGERIA": "ALG", "INDONESIA": "INA", "ISRAEL": "ISR", "POLAND": "POL",
    "KAZAKHSTAN": "KAZ", "JAMAICA": "JAM", "SOUTH AFRICA": "RSA", "THAILAND": "THA",
    "ETHIOPIA": "ETH", "SWITZERLAND": "SUI", "ECUADOR": "ECU", "PORTUGAL": "POR",
    "GREECE": "GRE", "ARGENTINA": "ARG", "EGYPT": "EGY", "TUNISIA": "TUN", "BOTSWANA": "BOT",
    "CHILE": "CHI", "SAINT LUCIA": "LCA", "UGANDA": "UGA", "DOMINICAN REPUBLIC": "DOM",
    "GUATEMALA": "GUA", "MOROCCO": "MAR", "DOMINICA": "DMA", "PAKISTAN": "PAK",
    "TURKEY": "TUR", "MEXICO": "MEX", "ARMENIA": "ARM", "COLOMBIA": "COL",
    "KYRGYZSTAN": "KGZ", "NORTH KOREA": "PRK", "LITHUANIA": "LTU", "INDIA": "IND",
    "MOLDOVA": "MDA", "KOSOVO": "KOS", "CYPRUS": "CYP", "FIJI": "FIJ", "JORDAN": "JOR",
    "MONGOLIA": "MGL", "ZAMBIA": "ZAM", "GRENADA": "GRN", "MALAYSIA": "MAS", "PERU": "PER",
    "PUERTO RICO": "PUR", "QATAR": "QAT", "SINGAPORE": "SGP", "SLOVAKIA": "SVK",
    "TAJIKISTAN": "TJK", "FINLAND": "FIN", "BAHAMAS": "BAH", "VENEZUELA": "VEN",
    "NIGERIA": "NGR", "GHANA": "GHA", "ESTONIA": "EST", "LATVIA": "LAT", "ICELAND": "ISL",
    "BELARUS": "BLR", "RUSSIA": "RUS", "VIETNAM": "VIE", "TRINIDAD AND TOBAGO": "TTO",
    "COTE D'IVOIRE": "CIV", "IVORY COAST": "CIV", "CAPE VERDE": "CPV", "SAMOA": "SAM",
}


def code_for(name):
    n = re.sub(r"[*†‡\[\]0-9]", "", name).strip().upper()
    n = n.replace("Ô", "O").replace("É", "E")
    return CODES.get(n, re.sub(r"[^A-Z]", "", n)[:3] or "???")


class _Rows(HTMLParser):
    """Text of every table row (only from tables marked 'wikitable')."""

    def __init__(self):
        super().__init__()
        self.depth = 0          # how deep inside a wikitable we are
        self.rows, self.row, self.cell, self.skip = [], None, None, 0

    def handle_starttag(self, tag, attrs):
        a = dict(attrs)
        if tag == "table":
            if self.depth or "wikitable" in (a.get("class") or ""):
                self.depth += 1
        elif not self.depth:
            return
        elif tag == "tr":
            self.row = []
        elif tag in ("td", "th") and self.row is not None:
            self.cell = []
        elif tag in ("sup", "style"):
            self.skip += 1

    def handle_endtag(self, tag):
        if tag == "table" and self.depth:
            self.depth -= 1
        elif not self.depth:
            return
        elif tag in ("td", "th") and self.cell is not None and self.row is not None:
            self.row.append(re.sub(r"\s+", " ", "".join(self.cell)).strip())
            self.cell = None
        elif tag == "tr" and self.row is not None:
            self.rows.append(self.row)
            self.row = None
        elif tag in ("sup", "style") and self.skip:
            self.skip -= 1

    def handle_data(self, data):
        if self.depth and self.cell is not None and not self.skip:
            self.cell.append(data)


def parse(html):
    """[(code, name, gold, silver, bronze), ...] in table order (best first)."""
    p = _Rows()
    p.feed(html)
    out, seen = [], set()
    for row in p.rows:
        nums = []
        for c in reversed(row):
            c2 = c.replace(",", "")
            if c2.isdigit():
                nums.insert(0, int(c2))
            else:
                break
        if len(nums) < 4:
            continue
        name_cells = row[:len(row) - len(nums)]
        if not name_cells:
            continue
        name = name_cells[-1]
        if not re.search(r"[A-Za-z]", name) or name.lower().startswith("total"):
            continue
        g, s, b = nums[-4], nums[-3], nums[-2]
        if g + s + b != nums[-1]:
            continue                                   # not a medal row
        code = code_for(name)
        if code in seen:
            break                                      # a second table (e.g. by sport) - stop
        seen.add(code)
        out.append((code, re.sub(r"[*†‡]", "", name).strip(), g, s, b))
    return out


def fetch(title):
    q = urllib.parse.urlencode({"action": "parse", "page": title, "prop": "text",
                                "format": "json", "formatversion": "2", "redirects": "1"})
    req = urllib.request.Request("https://en.wikipedia.org/w/api.php?" + q,
                                 headers={"User-Agent": UA})
    with urllib.request.urlopen(req, timeout=30) as r:
        return parse(json.load(r)["parse"]["text"])


_lock = threading.Lock()
_table = []
_updated = 0.0
_wanted = None


def get():
    """(table, minutes since updated) - table empty if we have nothing yet."""
    with _lock:
        return list(_table), (time.time() - _updated) / 60 if _updated else None


def want(title):
    """Ask the background reader to keep `title` fresh (None = stop)."""
    global _wanted
    _wanted = title


def _loop():
    global _table, _updated
    while True:
        title = _wanted
        if title:
            try:
                t = fetch(title)
                if t:
                    with _lock:
                        _table, _updated = t, time.time()
                    log.info("medal table: %s", ", ".join("%s %d" % (c, g) for c, _, g, s, b in t[:5]))
            except Exception as e:
                log.warning("medal table failed (%s)", e)
            time.sleep(20 * 60)
        else:
            time.sleep(60)


def start():
    threading.Thread(target=_loop, daemon=True, name="medals").start()


if __name__ == "__main__":
    import sys
    t = fetch(sys.argv[1] if len(sys.argv) > 1 else "2024 Summer Olympics medal table")
    for i, (c, n, g, s, b) in enumerate(t[:15], 1):
        print("%2d  %s  %-28s G %2d  S %2d  B %2d" % (i, c, n, g, s, b))
    print("... %d countries" % len(t))
