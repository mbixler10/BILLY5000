"""
Builds data/names_911.txt (and data/names_911_check.txt) from a spreadsheet of
the 9/11 victims with the columns:
    Name | Age | Place | Town/City | Province/State | Country | Job | Employer
(the layout of Wikipedia's victim lists). Usage:
    python tools/names_from_xlsx.py "9-11_Victims_List.xlsx"

Order of the reading: FDNY, NYPD, PAPD, WTC (everyone else in New York, incl.
Flights 11 and 175), the Pentagon by service then Flight 77, Flight 93.
Alphabetical by last name within each. "and her unborn child" rows are joined
to the person above them, as on the memorial. The six victims of the 1993
bombing (who share Wikipedia's lists) are left out.
"""
import collections
import re
import sys
from pathlib import Path

import openpyxl

ROOT = Path(__file__).resolve().parent.parent
OUT = ROOT / "data" / "names_911.txt"
CHECK = ROOT / "data" / "names_911_check.txt"

VICTIMS_1993 = {"John DiGiovanni", "Robert Kirkpatrick", "Stephen A. Knapp",
                "William Macko", "Wilfredo Mercado", "Monica Rodriguez Smith"}
ORDER = ["FDNY", "NYPD", "PAPD", "WTC", "DC", "PA"]
SERVICES = ["ARMY", "NAVY", "MARINES", "AIR FORCE", "COAST GUARD", "CIVILIAN", "FLIGHT 77"]
# words that mark someone in uniform (Army ranks, Navy ranks and enlisted ratings)
UNIFORM = re.compile(r"\b(colonel|lt\.? ?gen|general|sgt|sergeant|warrant officer|commander|"
                     r"ltjg|lieutenant|seaman|class|surface warfare officer|"
                     r"officer in the navy|adjutant general's corps|petty officer|major|captain|"
                     r"chief information systems technician)\b", re.I)
SUFFIX = {"JR", "JR.", "SR", "SR.", "II", "III", "IV", "V"}


def clean(v):
    return re.sub(r"\[\d+\]|\|", "", str(v)).strip() if v is not None else ""


def surname_key(name):
    n = re.sub(r'"[^"]*"', "", name)                    # drop nicknames
    words = [w for w in re.split(r"[\s,]+", n) if w]
    while len(words) > 1 and words[-1].upper() in SUFFIX:
        words.pop()
    last = words[-1] if words else name
    return (last.lower().replace("’", "'"), name.lower())


def group_of(place, job, emp):
    p, j, e = place.upper(), job.lower(), emp.upper()
    if p == "UA93":
        return "PA"
    if p in ("PENTAGON", "AA77"):
        return "DC"
    if "FDNY" in e or "NEW YORK FIRE DEPARTMENT" in e:
        return "FDNY"
    if "NYPD" in e or (not e and ("detective" in j or "police" in j)):
        return "NYPD"
    if ("PANYNJ" in e or "PORT AUTHORITY" in e) and re.search(r"police|patrolman|path sergeant", j):
        return "PAPD"
    return "WTC"


def service_of(place, job, emp):
    if place.upper() == "AA77":
        return "FLIGHT 77"
    j, e = job.lower(), emp.upper()
    if "civilian" in j or "contractor" in j:
        return "CIVILIAN"
    if UNIFORM.search(job):
        for svc, key in (("MARINES", "MARINE"), ("COAST GUARD", "COAST GUARD"),
                         ("AIR FORCE", "AIR FORCE"), ("NAVY", "NAVY"), ("ARMY", "ARMY")):
            if key in e:
                return svc
    return "CIVILIAN"


def main(path):
    ws = openpyxl.load_workbook(path, read_only=True).worksheets[0]
    people, skipped, seen = [], [], set()
    for row in list(ws.iter_rows(values_only=True))[1:]:
        name, age, place, town, state, country, job, emp = (list(row) + [None] * 8)[:8]
        name, place, job, emp = clean(name), clean(place), clean(job), clean(emp)
        if name.lower() == "and her unborn child":
            if people:
                people[-1]["unborn"] = True
            continue
        if not name or name.lower().startswith("continued at"):
            if job or emp:
                skipped.append("row with no name (job: %s, employer: %s)" % (job, emp))
            continue
        if not place:
            skipped.append("%s (no place given)" % name)
            continue
        key = (name, age, place)
        if key in seen:
            skipped.append("%s (listed twice, kept once)" % name)
            continue
        seen.add(key)
        people.append({"name": name, "place": place, "job": job, "emp": emp, "unborn": False})

    groups = collections.defaultdict(list)
    for p in people:
        if p["name"] in VICTIMS_1993:
            continue
        g = group_of(p["place"], p["job"], p["emp"])
        p["svc"] = service_of(p["place"], p["job"], p["emp"]) if g == "DC" else ""
        groups[g].append(p)
    for g in groups:
        groups[g].sort(key=lambda p: surname_key(p["name"]))
    groups["DC"].sort(key=lambda p: SERVICES.index(p["svc"]))       # stable: A-Z kept

    total = sum(len(v) for v in groups.values())
    OUT.parent.mkdir(exist_ok=True)
    with OUT.open("w", encoding="utf-8") as fh:
        for g in ORDER:
            for p in groups[g]:
                fh.write("\t".join([g, p["name"], p["svc"], "UNBORN" if p["unborn"] else ""]).rstrip("\t") + "\n")
    with CHECK.open("w", encoding="utf-8") as fh:
        for g in ORDER:
            fh.write("\n===== %s (%d) =====\n" % (g, len(groups[g])))
            for p in groups[g]:
                fh.write("%-10s %-40s %-45s %s%s\n" % (p["svc"] or g, p["name"], p["job"][:45], p["emp"],
                                                        "  + unborn child" if p["unborn"] else ""))
        fh.write("\n===== skipped =====\n" + "\n".join(skipped) + "\n")
    for g in ORDER:
        print("  %-5s %4d" % (g, len(groups[g])))
        if g == "DC":
            for s in SERVICES:
                n = sum(1 for p in groups[g] if p["svc"] == s)
                if n:
                    print("        %-12s %d" % (s, n))
    print("  total %d   (+ %d unborn children named with their mothers)" %
          (total, sum(p["unborn"] for g in ORDER for p in groups[g])))
    print("  skipped:", *skipped, sep="\n    ")
    print("Saved", OUT, "and", CHECK)


if __name__ == "__main__":
    main(sys.argv[1])
