#!/usr/bin/env python3
"""BIBLE 3.8.1: load the approved geometry required by 3.7.7's MATCH.

Default is a local metadata dry run. --apply writes the approved geometry to
Neo4j through db.run in one transaction. It does not change books.json.
"""

import argparse
import json
from pathlib import Path

from index_common import ROOT, cli, lock, require

LOAD = """MATCH (m:Meta {key:'skeleton_frozen'}) WHERE m.value='false'
CALL () { UNWIND $books AS b
 MERGE (k:Book {book_id:b.book_id})
 SET k.title=b.title, k.edition=b.edition, k.year=b.year, k.field_name=b.field_name,
 k.page_count=b.page_count_images, k.page_offset=b.page_offset,
 k.image_name_pattern=b.image_name_pattern, k.index_image_start=b.index_images[0],
 k.index_image_end=b.index_images[1], k.continent_id=b.continent_id,
 k.status=CASE WHEN k.status IN ['index-done','reading','read'] THEN k.status ELSE 'geography-done' END
 RETURN count(k) AS books }
CALL () { UNWIND $territories AS t MERGE (x:Territory {territory_id:t.territory_id})
 SET x.level=t.level, x.name=t.name, x.part_name=t.part_name, x.book_id=t.book_id,
 x.page_start=t.page_start, x.page_end=t.page_end, x.page_count=t.page_count,
 x.lat=t.lat, x.lon=t.lon, x.area_fraction=t.area_fraction, x.seat_order=t.seat_order,
  x.raster_code=t.raster_code, x.colour_hex=t.colour_hex, x.bbox_px=t.bbox_px, x.border_geojson=null,
  x.tile_sides=t.tile_sides, x.layout_anchor_lat=t.layout_anchor_lat, x.layout_anchor_lon=t.layout_anchor_lon
 RETURN count(x) AS territories }
CALL () { UNWIND $territories AS t WITH t WHERE t.parent IS NOT NULL
 MATCH (c:Territory {territory_id:t.territory_id}), (p:Territory {territory_id:t.parent})
 MERGE (c)-[:CHILD_OF]->(p) RETURN count(*) AS child_links }
CALL () { MATCH (c:Territory {level:'continent'}), (b:Book {book_id:c.book_id})
 MERGE (c)-[:REPRESENTS]->(b) RETURN count(*) AS book_links }
RETURN books, territories, child_links, book_links"""


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--books", type=Path, default=ROOT / "kitchen/books.json")
    parser.add_argument("--geography", type=Path, default=ROOT / "data/export/geography/geography.json")
    parser.add_argument("--apply", action="store_true")
    args = parser.parse_args(argv)
    books = [b for b in json.loads(args.books.read_text()) if b["status"] in ("accepted", "geography-done", "index-done")]
    geography = json.loads(args.geography.read_text())
    # Supply null for optional fields on an older pre-honeycomb geography.
    geography = [dict(tile_sides=None, layout_anchor_lat=None, layout_anchor_lon=None) | t for t in geography]
    continents = {t["book_id"]: t for t in geography if t["level"] == "continent"}
    require(set(continents) == {b["book_id"] for b in books}, "book/continent coverage differs")
    ids = {t["territory_id"] for t in geography}
    require(len(ids) == len(geography) and all(t["parent"] is None or t["parent"] in ids for t in geography), "invalid territory hierarchy")
    payload = [b | {"continent_id": continents[b["book_id"]]["territory_id"]} for b in books]
    print(f"Geometry: {len(books)} books; {len(geography)} territories")
    if not args.apply:
        print("Dry run; no database access or writes")
        return 0
    manifest_path = args.geography.parent / 'build.json'
    if manifest_path.exists():
        require(not json.loads(manifest_path.read_text()).get('geometry_review_pending'),
                "the new honeycomb map awaits Nir's visual approval (Checkpoint 3.4); record his actual decision before loading")
    from db import run
    with lock(ROOT / "kitchen/logs/index-registry.lock"):
        freeze = run("MATCH (m:Meta {key:'skeleton_frozen'}) RETURN m.value AS value")
        require(len(freeze) == 1 and freeze[0]["value"] == "false", "schema missing or skeleton frozen")
        existing = run("MATCH (t:Territory) RETURN t.territory_id AS id, t.book_id AS book, t.name AS name, t.page_start AS start, t.page_end AS end")
        desired = {t["territory_id"]: (t["book_id"], t["name"], t["page_start"], t["page_end"]) for t in geography}
        require(all(r["id"] in desired and desired[r["id"]] == (r["book"], r["name"], r["start"], r["end"]) for r in existing),
                "existing database geometry differs; explicit human decision required")
        result = run(LOAD, books=payload, territories=geography)
        require(len(result) == 1 and result[0]["territories"] == len(geography), "geometry transaction refused")
        print(result)
        print(run("MATCH (t:Territory) RETURN t.level AS level, count(*) AS count ORDER BY level"))
    return 0


if __name__ == "__main__":
    raise SystemExit(cli(main))
