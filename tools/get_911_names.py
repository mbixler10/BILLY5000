"""
Downloads the names of the 2,977 people killed in the September 11, 2001
attacks, as they are inscribed at the National September 11 Memorial,
from Wikipedia's three list pages, and saves them to data/names_911.txt
(one name per line) for the 9/11 "reading of the names" page.

Run once on the PC, check the count it prints, then commit the file:
    python tools/get_911_names.py
    git add data/names_911.txt
    git commit -m "9/11 names"
    git push

Uses only the Python standard library.
"""
import json
import re
import sys
import urllib.parse
import urllib.request
from html.parser import HTMLParser
from pathlib import Path

PAGES = [
    "List of victims of the September 11 attacks (A–G)",
    "List of victims of the September 11 attacks (H–N)",
    "List of victims of the September 11 attacks (O–Z)",
]
EXPECTED = 2977
OUT = Path(__file__).resolve().parent.parent / "data" / "names_911.txt"
UA = "BILLY5000/1.0 (family LED clock; one-time download of the 9/11 memorial names)"


def fetch_html(title):
    q = urllib.parse.urlencode({"action": "parse", "page": title, "prop": "text",
                                "format": "json", "formatversion": "2", "redirects": "1"})
    req = urllib.request.Request("https://en.wikipedia.org/w/api.php?" + q,
                                 headers={"User-Agent": UA})
    with urllib.request.urlopen(req, timeout=60) as r:
        return json.load(r)["parse"]["text"]


class Rows(HTMLParser):
    """Collects the text of every table row, cell by cell."""

    def __init__(self):
        super().__init__()
        self.rows, self.row, self.cell = [], None, None
        self.skip = 0                       # inside <sup> (footnote markers)

    def handle_starttag(self, tag, attrs):
        if tag == "tr":
            self.row = []
        elif tag in ("td", "th") and self.row is not None:
            self.cell = []
        elif tag == "sup":
            self.skip += 1
        elif tag == "br" and self.cell is not None:
            self.cell.append(" ")

    def handle_endtag(self, tag):
        if tag in ("td", "th") and self.row is not None and self.cell is not None:
            self.row.append(re.sub(r"\s+", " ", "".join(self.cell)).strip())
            self.cell = None
        elif tag == "tr" and self.row is not None:
            self.rows.append(self.row)
            self.row = None
        elif tag == "sup" and self.skip:
            self.skip -= 1

    def handle_data(self, data):
        if self.cell is not None and not self.skip:
            self.cell.append(data)


ORDER = ["FDNY", "NYPD", "PAPD", "WTC", "DC", "PA"]
SERVICES = ["ARMY", "NAVY", "MARINES", "AIR FORCE", "COAST GUARD", "CIVILIAN", "FLIGHT 77"]
RANKS = ("GENERAL", "COLONEL", "MAJOR", "CAPTAIN", "LIEUTENANT", "COMMANDER", "SERGEANT",
         "SPECIALIST", "PETTY OFFICER", "SEAMAN", "CHIEF", "PRIVATE", "CORPORAL", "AIRMAN",
         "ENSIGN", "ADMIRAL", "WARRANT", "YEOMAN", "INFORMATION SYSTEMS TECHNICIAN",
         "ELECTRONICS TECHNICIAN", "AVIATION", "MASTER", "PFC", "SGT", "CPT", "LT")


def service_of(place, job, employer):
    """Pentagon victims: which service (by uniform), or civilian; Flight 77 apart."""
    p, j, e = place.upper(), job.upper(), employer.upper()
    if "77" in p:
        return "FLIGHT 77"
    if "CIVILIAN" in j or "CONTRACTOR" in j:
        return "CIVILIAN"
    uniformed = any(re.search(r"\b" + r + r"\b", j) for r in RANKS)
    for svc, keys in (("MARINES", ("MARINE",)), ("COAST GUARD", ("COAST GUARD",)),
                      ("AIR FORCE", ("AIR FORCE",)), ("NAVY", ("NAVY", "NAVAL")),
                      ("ARMY", ("ARMY",))):
        if any(k in e for k in keys):
            return svc if uniformed else "CIVILIAN"
    return "CIVILIAN"


def group_of(place, job, employer):
    p, j, e = place.upper(), job.upper(), employer.upper()
    if "93" in p:
        return "PA"
    if "PENTAGON" in p or "77" in p:
        return "DC"
    if "FDNY" in e or "FIRE DEPARTMENT" in e:
        return "FDNY"
    if "NYPD" in e or "NEW YORK CITY POLICE" in e or "NEW YORK POLICE" in e:
        return "NYPD"
    if "PORT AUTHORITY" in e and ("POLICE" in j or "POLICE" in e or "OFFICER" in j):
        return "PAPD"
    return "WTC"


def main():
    groups = {g: [] for g in ORDER}
    places = {}
    for title in PAGES:
        print("Reading:", title)
        p = Rows()
        p.feed(fetch_html(title))
        col = {"name": 0, "place": 2, "job": 6, "employer": 7}     # usual layout
        for row in p.rows:
            if row and row[0].strip().lower() == "name":           # header row: map columns
                low = [c.strip().lower() for c in row]
                for key, label in (("name", "name"), ("place", "place"), ("job", "job"),
                                   ("employer", "employer")):
                    if label in low:
                        col[key] = low.index(label)
                continue
            if len(row) < 3 or not row[0]:
                continue
            if "1993" in " ".join(row):          # the six 1993 bombing victims share these pages
                continue
            get = lambda k: row[col[k]] if col[k] < len(row) else ""
            name = get("name")
            if not re.search(r"[A-Za-z]", name) or len(name) > 60:
                continue
            g = group_of(get("place"), get("job"), get("employer"))
            svc = service_of(get("place"), get("job"), get("employer")) if g == "DC" else ""
            groups[g].append((name, svc, get("job"), get("employer")))
            places[get("place")] = places.get(get("place"), 0) + 1

    total = sum(len(v) for v in groups.values())
    print()
    for place, n in sorted(places.items(), key=lambda kv: -kv[1]):
        print("  place %-20s %d" % (place, n))
    print()
    labels = {"FDNY": "Fire (FDNY)", "NYPD": "NYPD", "PAPD": "Port Authority Police",
              "WTC": "World Trade Center (others)",
              "DC": "Pentagon / Flight 77", "PA": "Flight 93 / Shanksville"}
    for g in ORDER:
        print("  %-26s %d" % (labels[g], len(groups[g])))
        if g == "DC":
            for svc in SERVICES:
                print("      %-22s %d" % (svc.title(), sum(1 for r in groups[g] if r[1] == svc)))
    print("\nTotal names: %d (expected %d)" % (total, EXPECTED))
    print("For reference: FDNY lost 343, NYPD 23 and Port Authority Police 37;")
    print("(Port Authority civilian staff belong under WTC, not PAPD.)")
    print("the Pentagon/Flight 77 toll is 184 and Flight 93 is 40.")
    if abs(total - EXPECTED) > 10:
        print("That count looks wrong, so nothing was saved. Send the output above to Claude.")
        sys.exit(1)
    OUT.parent.mkdir(exist_ok=True)
    # Pentagon: by service in the order above, alphabetical within each
    groups["DC"].sort(key=lambda r: SERVICES.index(r[1]))      # stable: keeps A-Z order
    with OUT.open("w", encoding="utf-8") as fh:
        for g in ORDER:
            for name, svc, _, _ in groups[g]:   # Wikipedia's lists are already alphabetical
                fh.write("%s\t%s\t%s\n" % (g, name, svc) if svc else "%s\t%s\n" % (g, name))
    check = OUT.parent / "pentagon_check.txt"
    with check.open("w", encoding="utf-8") as fh:
        for name, svc, job, emp in groups["DC"]:
            fh.write("%-12s %-35s %-40s %s\n" % (svc, name, job, emp))
    print("Saved", OUT)
    print("Pentagon sorting saved to", check, "- worth a quick look.")
    if total != EXPECTED:
        print("Close but not exact - send Claude the output above to double-check.")


if __name__ == "__main__":
    main()
