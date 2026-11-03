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
        e.update({"text_quote_count": 0, "text_status": "none", "books_total": 37, "quotes_total": 0, "edges": []})
        e["lit_spots"] = sorted(spots.get(slug, []), key=lambda s: (s["district_id"], s["book_id"]))
        (OUT / "entities" / f"{slug}.json").write_text(json.dumps(e, ensure_ascii=False, separators=(",", ":")))
        search.append({"slug": slug, "group": e["group"], "canonical_name": e["canonical_name"], "aliases": e["aliases"],
                       "altitude": None, "rank": None, "lit_spot_count": len(e["lit_spots"]), "edge_count": 0, "has_text": False,
                       "books": len({s["book_id"] for s in e["lit_spots"]})})
    search.sort(key=lambda s: (s["group"], s["canonical_name"]))
    (OUT / "search.json").write_text(json.dumps(search, ensure_ascii=False, separators=(",", ":")))
    print(f"wrote {len(search)} entity files + search.json in {time.time() - t0:.0f}s")


if __name__ == "__main__":
    main()
