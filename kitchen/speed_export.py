#!/usr/bin/env python3
"""Part 0 stage 3: fast export of entities and lit spots from Neo4j to site/data.

One aggregated query instead of two per entity. Writes site/data/entities/<slug>.json
(viewer shape: lit_spots, edges=[], text fields null) and site/data/search.json.
"""
import json, sys, time
from collections import defaultdict
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "kitchen"))
from db import run

OUT = ROOT / "site" / "data"
FIELDS = ("drug_class", "class_canonical", "heaviness_group", "heaviness_confidence", "altitude", "rank",
          "altitude_status", "ordering_value", "tie1", "tie2", "tldr", "eli5", "text_model", "text_date")


def main():
    t0 = time.time()
    ents = {r["e"]["slug"]: r["e"] for r in run("MATCH (e:Entity) RETURN e { .* } AS e")}
    print(f"{len(ents)} entities read", flush=True)
    fields = {r["book_id"]: r["field"] for r in run("MATCH (c:Territory {level:'continent'}) RETURN c.book_id AS book_id, c.name AS field")}
    spots = defaultdict(list)
    rows = run("""MATCH (e:Entity)-[l:DISCUSSED_IN]->(d:Territory)
        WITH e.slug AS slug, d.territory_id AS did, d.name AS dname, l.book_id AS bid,
             collect(DISTINCT l.page_number) AS pages, collect(DISTINCT l.source) AS sources
        RETURN slug, did, dname, bid, pages, sources""")
    for r in rows:
        spots[r["slug"]].append({"district_id": r["did"], "district_name": r["dname"], "book_id": r["bid"],
                                 "book_field": fields.get(r["bid"]), "pages": sorted(r["pages"]),
                                 "sources": sorted(r["sources"]), "mentions": []})
    print(f"{len(rows)} lit-spot groups read in {time.time() - t0:.0f}s", flush=True)
    (OUT / "entities").mkdir(parents=True, exist_ok=True)
    search = []
    for slug, e in ents.items():
        for key in ("aliases", "abbreviations", "generic_names", "brand_names", "formulas"):
            e[key] = e.get(key) or []
        for key in FIELDS:
            e.setdefault(key, None)
        e["lit_spots"] = sorted(spots.get(slug, []), key=lambda s: (s["district_id"], s["book_id"]))
        e.update({"text_quote_count": 0, "text_status": "none", "books_total": 37, "quotes_total": 0, "edges": [],
                  "ordering_value": len({s["book_id"] for s in e["lit_spots"]})})
        (OUT / "entities" / f"{slug}.json").write_text(json.dumps(e, ensure_ascii=False, separators=(",", ":")))
        search.append({"slug": slug, "group": e["group"], "canonical_name": e["canonical_name"], "aliases": e["aliases"],
                       "altitude": None, "rank": None, "lit_spot_count": len(e["lit_spots"]), "edge_count": 0, "has_text": False,
                       "books": len({s["book_id"] for s in e["lit_spots"]})})
    # per-district files: which entities are discussed in this chapter (index mentions first)
    (OUT / "districts").mkdir(exist_ok=True)
    by_district = defaultdict(list)
    for slug, lst in spots.items():
        e = ents.get(slug)
        if not e:
            continue
        for s in lst:
            by_district[s["district_id"]].append({"slug": slug, "canonical_name": e["canonical_name"], "group": e["group"],
                                                   "edges_here": 0, "mentions": len(s["pages"]), "pages": s["pages"],
                                                   "index": "index" in s["sources"]})
    for did, lst in by_district.items():
        lst.sort(key=lambda r: (not r["index"], -r["mentions"], r["canonical_name"]))
        (OUT / "districts" / f"{did}.json").write_text(json.dumps({"territory_id": did, "entities": lst}, ensure_ascii=False, separators=(",", ":")))
    print(f"wrote {len(by_district)} district files")
    search.sort(key=lambda s: (s["group"], s["canonical_name"]))
    (OUT / "search.json").write_text(json.dumps(search, ensure_ascii=False, separators=(",", ":")))
    print(f"wrote {len(search)} entity files + search.json in {time.time() - t0:.0f}s")


if __name__ == "__main__":
    main()
