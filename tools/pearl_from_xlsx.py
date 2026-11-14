"""
Builds data/names_pearl_harbor.txt from the Pearl Harbor casualty spreadsheet
(sheet "Casualty List", columns: # | Last Name | First & Middle Names | Rank / Rate |
Service | Service (Full) | Ship / Unit / Location | Category | Age | Occupation | Original).
Usage:
    python tools/pearl_from_xlsx.py "Pearl_Harbor_Casualty_List_1941.xlsx"

The names are read by location: the ship or station with the most lost first
(USS ARIZONA), then the next, and so on; alphabetical within each, as listed.
Sub-listings are folded into their ship or field: USS PENNS(TRACY) etc. go with
USS PENNSYLVANIA, HICKAM(B-17) etc. with HICKAM FIELD. The eight whose names are
unknown come last. Spellings are left as published.

Output, one line per person:  LOCATION <tab> NAME <tab> RANK AND SERVICE
"""
import collections
import re
import sys
from pathlib import Path

import openpyxl

ROOT = Path(__file__).resolve().parent.parent
OUT = ROOT / "data" / "names_pearl_harbor.txt"

# shown on the panel in full, so they read plainly
PLACE_NAMES = {
    "FT KAMEHAMEHA": "FORT KAMEHAMEHA",
    "FT SHAFTER": "FORT SHAFTER",
    "SCHOFIELD BKS": "SCHOFIELD BARRACKS",
    "KANEOHE NAS": "NAS KANEOHE BAY",
    "EWA MCAS": "MCAS EWA",
    "MIDWAY IS NAS": "NAS MIDWAY ISLAND",
    "FORD ISLAND NAS": "NAS FORD ISLAND",
    "NAVAL HOSP P.H.": "NAVAL HOSPITAL",
    "NAV MBL HOSP #2": "MOBILE HOSPITAL 2",
    "—": "NAMES UNKNOWN",
}
SUFFIX = {"JR", "JR.", "SR", "SR.", "II", "III", "IV"}
SERVICE = {"USN": "USN", "USNR": "USNR", "USMC": "USMC", "USMCR": "USMCR",
           "USA": "US ARMY", "USAR": "US ARMY RES"}


def place(raw):
    raw = (raw or "—").strip()
    if raw.startswith("USS PENNS("):
        return "USS PENNSYLVANIA"
    if raw.startswith("HICKAM("):
        return "HICKAM FIELD"
    return PLACE_NAMES.get(raw, raw)


def full_name(first, last):
    words = (first or "").split()
    suffix = [w for w in words if w.upper() in SUFFIX]
    words = [w for w in words if w.upper() not in SUFFIX]
    name = " ".join(words + [last.strip()] + [s.upper().rstrip(".") + "." if s.upper().startswith(("JR", "SR")) else s for s in suffix])
    name = name.replace('"', "").replace("*", "").replace("`", "'")   # "J" "D" -> J D
    return re.sub(r"\s+", " ", name).upper()


def main(path):
    wb = openpyxl.load_workbook(path, read_only=True)
    rows = [r for r in wb["Casualty List"].iter_rows(min_row=5, values_only=True) if r and r[0]]
    groups = collections.OrderedDict()
    for num, last, first, rank, svc, _full, loc, cat, age, _occ, _orig in rows:
        where = place(loc)
        if cat == "Unknown":
            who, sub = "NAME UNKNOWN", ""
        elif cat == "Civilian":
            who = full_name(first, last)
            sub = ("CIVILIAN, AGE %s" % age).upper() if age else "CIVILIAN"
        else:
            who = full_name(first, last)
            sub = " ".join(x for x in ((rank or "").upper(), SERVICE.get(svc, svc or "")) if x)
        groups.setdefault(where, []).append((who, sub))
    order = sorted((g for g in groups if g != "NAMES UNKNOWN"), key=lambda g: (-len(groups[g]), g))
    if "NAMES UNKNOWN" in groups:
        order.append("NAMES UNKNOWN")
    lines = []
    for g in order:
        for who, sub in groups[g]:
            lines.append("%s\t%s\t%s" % (g, who, sub))
    OUT.write_text("\n".join(lines) + "\n", encoding="utf-8")
    print("%d names in %d locations -> %s" % (len(lines), len(order), OUT))


if __name__ == "__main__":
    main(sys.argv[1])
