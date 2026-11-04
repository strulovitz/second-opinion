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
                  "ordering_value": e.get("common")})
        (OUT / "entities" / f"{slug}.json").write_text(json.dumps(e, ensure_ascii=False, separators=(",", ":")))
        search.append({"slug": slug, "group": e["group"], "canonical_name": e["canonical_name"], "aliases": e["aliases"],
                       "altitude": e.get("altitude"), "rank": e.get("rank"), "place": e.get("place"), "lit_spot_count": len(e["lit_spots"]), "edge_count": 0, "has_text": False,
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
    golden()


REL_KEYS = ("frequency_phrase", "numeric_pct", "f_scale", "severity", "severity_phrase", "subtype", "price",
            "availability", "approval", "note")


def golden():
    """Part 0 12.3/12.5: write site/data/golden.json and the edges of every entity on a golden connection."""
    rows = run("""MATCH (a:Entity)-[r]->(b:Entity) WHERE r.source = 'article'
        RETURN type(r) AS rel, r { .* } AS r, a.slug AS a, b.slug AS b ORDER BY r.id""")
    slugs = sorted({x for r in rows for x in (r["a"], r["b"])})
    nodes = {r["slug"]: r for r in run("""MATCH (e:Entity) WHERE e.slug IN $s
        RETURN e.slug AS slug, e.canonical_name AS name, e.group AS group, e.place AS place,
               e.altitude AS altitude, coalesce(e.common, 0) AS common, e.aliases AS aliases""", s=slugs)}
    best = {}
    for r in run("""MATCH (e:Entity)-[l:DISCUSSED_IN]->(d:Territory) WHERE e.slug IN $s
            RETURN e.slug AS slug, d.territory_id AS did, count(*) AS n""", s=slugs):
        if r["n"] > best.get(r["slug"], ("", 0))[1]:
            best[r["slug"]] = (r["did"], r["n"])
    for s, n in nodes.items():
        n["anchor"] = best.get(s, (None,))[0]
        n["aliases"] = (n["aliases"] or [])[:8]
    conns = []
    for r in rows:
        x = r["r"]
        c = {"id": x["id"], "rel": r["rel"], "from": r["a"], "to": r["b"], "quote": x["quote"],
             "source": {k: x.get(k2) for k, k2 in (("id", "source_id"), ("title", "source_title"), ("origin", "origin"),
                        ("year", "year"), ("kind", "kind"), ("strength", "strength"), ("file", "file"))}}
        c.update({k: x.get(k) for k in REL_KEYS})
        conns.append(c)
    for _ in range(3):  # a thing no book discusses sits on the tile of the thing it connects to
        for c in conns:
            a, b = nodes[c["from"]], nodes[c["to"]]
            a["anchor"] = a["anchor"] or b["anchor"]
            b["anchor"] = b["anchor"] or a["anchor"]
    old = OUT / "golden.json"
    stale = set(json.loads(old.read_text())["nodes"]) - set(nodes) if old.exists() else set()
    for slug in stale:
        p = OUT / "entities" / f"{slug}.json"
        if p.exists():
            e = json.loads(p.read_text()); e["edges"] = []
            p.write_text(json.dumps(e, ensure_ascii=False, separators=(",", ":")))
    (OUT / "golden.json").write_text(json.dumps({"nodes": nodes, "connections": conns}, ensure_ascii=False, indent=0))
    edges = defaultdict(dict)
    for c in conns:
        for me, other, direction in ((c["from"], c["to"], "out"), (c["to"], c["from"], "in")):
            if c["rel"] in ("MISTAKEN_FOR", "SAME_CHEMICAL"):
                direction = "both"
            o = nodes[other]
            key = (c["rel"], direction, c["subtype"], other)
            e = edges[me].setdefault(key, {"relation": c["rel"], "direction": direction, "subtype": c["subtype"],
                                           "other_slug": other, "other_name": o["name"], "other_group": o["group"],
                                           "f_scale": 0, "severity": False, "statements": []})
            e["f_scale"] = max(e["f_scale"], c["f_scale"] or 0)
            e["severity"] = e["severity"] or bool(c["severity"])
            e["statements"].append(c)
    search_p = OUT / "search.json"
    search = json.loads(search_p.read_text())
    have = {s["slug"] for s in search}
    for slug in slugs:
        p = OUT / "entities" / f"{slug}.json"
        n = nodes[slug]
        e = json.loads(p.read_text()) if p.exists() else {"slug": slug, "group": n["group"], "canonical_name": n["name"],
                                                          "aliases": n["aliases"], "lit_spots": []}
        e.update({"edges": list(edges[slug].values()), "altitude": n["altitude"], "place": n["place"]})
        p.write_text(json.dumps(e, ensure_ascii=False, separators=(",", ":")))
        if slug not in have:
            search.append({"slug": slug, "group": n["group"], "canonical_name": n["name"], "aliases": n["aliases"],
                           "altitude": n["altitude"], "rank": None, "place": n["place"], "lit_spot_count": 0,
                           "edge_count": 0, "has_text": False, "books": 0})
    ec = {s: sum(len(e["statements"]) for e in v.values()) for s, v in edges.items()}
    for s in search:
        s["edge_count"] = ec.get(s["slug"], 0)
    search_p.write_text(json.dumps(search, ensure_ascii=False, separators=(",", ":")))
    print(f"golden.json: {len(conns)} connections, {len(nodes)} things")


if __name__ == "__main__":
    golden() if "--golden" in sys.argv else main()
    # THE SITE FOLDER LAW (BIBLE Part 9 section 9.S): the export is not finished until
    # site/ is committed and pushed. This prints exactly what is still missing on GitHub.
    import subprocess
    print("\nSite Folder Law check (commit + push site/, then run kitchen/check_published.py again):")
    subprocess.run([sys.executable, str(ROOT / "kitchen" / "check_published.py")])
