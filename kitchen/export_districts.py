#!/usr/bin/env python3
"""BIBLE 7.3: export what is discussed in each Neo4j district, without writes."""

from pathlib import Path

from viewer_export import RELATIONS, ROOT, identifier, write_json

DISTRICTS = """MATCH (d:Territory {level:'district'})
OPTIONAL MATCH (d)-[:CHILD_OF]->(p:Territory)-[:CHILD_OF]->(c:Territory)
RETURN d { .territory_id, .name, .part_name, .book_id, .page_start, .page_end, .lat, .lon,
 province_id:p.territory_id, province_name:p.name, continent_id:c.territory_id,
 continent_name:c.name } AS district ORDER BY d.territory_id"""
MENTIONS = f"""MATCH (e:Entity)-[l:DISCUSSED_IN]->(d:Territory {{level:'district'}})
WITH d, e, count(l) AS mentions, collect(DISTINCT l.page_number) AS pages
CALL (d, e) {{
 OPTIONAL MATCH (e)-[r:{RELATIONS}]-() WHERE r.district_id=d.territory_id
 RETURN count(r) AS edges_here
}}
RETURN d.territory_id AS territory_id, e.slug AS slug,
 e.canonical_name AS canonical_name, e.group AS group, mentions, pages, edges_here"""


def export(run, root=ROOT):
    districts = [r["district"] for r in run(DISTRICTS)]
    if not districts:
        raise ValueError("No Neo4j districts; load the approved geography before exporting")
    by_id = {d["territory_id"]: d for d in districts}
    for district in districts:
        district["entities"] = []
    for row in run(MENTIONS):
        row = dict(row)
        did = row.pop("territory_id")
        row["pages"] = sorted(set(row["pages"]))
        if row.get("slug"):
            by_id[did]["entities"].append(row)
    changed = 0
    for district in districts:
        district["entities"].sort(key=lambda e: (-e["edges_here"], -e["mentions"], e["canonical_name"], e["slug"]))
        relative = Path("districts") / (identifier(district["territory_id"]) + ".json")
        changed += write_json(relative, district, root)[0]
    result = {"districts": len(districts), "files_changed_both_copies": changed}
    print(result)
    return result


def main():
    from db import run
    export(run)


if __name__ == "__main__":
    main()
