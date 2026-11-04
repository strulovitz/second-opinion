#!/usr/bin/env python3
"""BIBLE Part 0 section 13: rough heights by a code rule, seconds, no model.

common = distinct chapters + distinct books that mention the thing (index lit spots).
The further from the centre, the more rare. Places:
  underground 0.30-0.95  causes (from of an article LEADS_TO/HARMS into a disease,
                         when the from is not a treatment), common deep
  surface     1.00       diseases = the hexagons
  air         1.02-1.50  symptoms, common low
  orbit       1.52-2.98  treatments, common low
Writes e.altitude, e.rank, e.place, e.common, e.altitude_status = "rough".
A disease that leads to another and is itself caused by nothing entered is a cause.
Run after kitchen/golden_load.py (causes come from the golden facts).
"""
import sys, time
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from db import run

BANDS = {"underground": (0.30, 0.95), "air": (1.02, 1.50), "orbit": (1.52, 2.98)}
PLACE = {"symptoms-and-signs": "air", "treatments-and-drugs": "orbit", "diseases-and-conditions": "surface", "causes": "underground"}


def main():
    t0 = time.time()
    rows = run("""MATCH (e:Entity)
        OPTIONAL MATCH (e)-[l:DISCUSSED_IN]->(d:Territory)
        WITH e, count(DISTINCT d) AS chapters, count(DISTINCT l.book_id) AS books
        RETURN e.slug AS slug, e.group AS grp, e.canonical_name AS name, chapters + books AS common""")
    causes = {r["slug"] for r in run("""MATCH (a:Entity)-[r:LEADS_TO|HARMS]->(b:Entity)
        WHERE r.source = 'article' AND a.group <> 'treatments-and-drugs'
          AND NOT EXISTS { MATCH (:Entity)-[q:HARMS|LEADS_TO]->(a) WHERE q.source = 'article' }
        RETURN DISTINCT a.slug AS slug""")}
    groups = {}
    for r in rows:
        place = "underground" if r["slug"] in causes else PLACE[r["grp"]]
        groups.setdefault(place, []).append(r)
    out = []
    for place, lst in groups.items():
        if place == "surface":
            out += [{"slug": r["slug"], "alt": 1.0, "rank": 0, "place": place, "common": r["common"]} for r in lst]
            continue
        lo, hi = BANDS[place]
        lst.sort(key=lambda r: (-r["common"], (r["name"] or "").lower()))
        n = len(lst)
        for k, r in enumerate(lst):
            alt = (lo + hi) / 2 if n == 1 else lo + (hi - lo) * k / (n - 1)
            out.append({"slug": r["slug"], "alt": round(alt, 6), "rank": k, "place": place, "common": r["common"]})
    for i in range(0, len(out), 5000):
        run("""UNWIND $rows AS r MATCH (e:Entity {slug: r.slug})
            SET e.altitude = r.alt, e.rank = r.rank, e.place = r.place, e.common = r.common,
                e.altitude_status = 'rough', e.role = CASE r.place WHEN 'underground' THEN 'cause' ELSE null END""",
            rows=out[i:i + 5000])
    for r in run("""MATCH (e:Entity) RETURN e.place AS place, count(*) AS n, min(e.altitude) AS lo,
            max(e.altitude) AS hi ORDER BY lo"""):
        print(r)
    print(f"rough heights for {len(out)} entities in {time.time() - t0:.0f}s")


if __name__ == "__main__":
    main()
