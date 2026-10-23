#!/usr/bin/env python3
"""BIBLE 6.3-4: read Neo4j and export the entity maps and elevator index."""

from pathlib import Path

from viewer_export import GROUPS, RELATIONS, ROOT, identifier, write_json

ENTITIES = "MATCH (e:Entity) RETURN e { .* } AS e ORDER BY e.slug"
BOOKS = "MATCH (b:Book) WHERE b.status IN ['index-done','reading','read'] RETURN count(b) AS n"
LIT = """MATCH (e:Entity {slug:$slug})-[l:DISCUSSED_IN]->(d:Territory)
MATCH (d)-[:CHILD_OF*1..2]->(c:Territory {level:'continent'})
RETURN d.territory_id AS district_id, d.name AS district_name,
       l.book_id AS book_id, c.name AS book_field,
       collect(DISTINCT l.page_number) AS pages, collect(DISTINCT l.source) AS sources,
       collect(l { .* }) AS mentions ORDER BY district_id, book_id"""
EDGES = f"""MATCH (e:Entity {{slug:$slug}})-[r:{RELATIONS}]-(o:Entity)
MATCH (d:Territory {{territory_id:r.district_id}})
RETURN type(r) AS relation,
 CASE WHEN type(r)='MISTAKEN_FOR' THEN 'both'
      WHEN startNode(r)=e THEN 'out' ELSE 'in' END AS direction,
 r.subtype AS subtype, o.slug AS other_slug, o.canonical_name AS other_name,
 o.group AS other_group, d.name AS district_name, r {{ .* }} AS statement"""
COLOURS = {"PRESENTS_WITH": 0, "TREATED_BY": 0, "HARMS": 1, "LEADS_TO": 1, "MISTAKEN_FOR": 2}


def aggregate(rows):
    groups = {}
    for row in rows:
        statement = row["statement"] | {"district_name": row["district_name"]}
        required = ("book_id", "district_id", "page_number", "quote", "image_file")
        if any(statement.get(key) is None or statement.get(key) == "" for key in required):
            raise ValueError("Relationship lacks book/page/quote/image provenance; export refused")
        if type(statement.get("f_scale")) is not int or not 0 <= statement["f_scale"] <= 5:
            raise ValueError("Relationship has no valid stated F-scale; export refused")
        key = (row["relation"], row["direction"], row["subtype"], row["other_slug"])
        if key not in groups:
            groups[key] = {k: row[k] for k in ("relation", "direction", "subtype", "other_slug", "other_name", "other_group")}
            groups[key]["statements"] = []
        groups[key]["statements"].append(statement)
    for edge in groups.values():
        statements = edge["statements"]
        statements.sort(key=lambda s: (-s["f_scale"], s["book_id"], s["page_number"]))
        edge["f_scale"] = max(s["f_scale"] for s in statements)
        edge["severity"] = any(s.get("severity", False) for s in statements)
        percentages = [s["numeric_pct"] for s in statements if s.get("numeric_pct") is not None]
        edge["numeric_pct"] = max(percentages) if percentages else None
    return sorted(groups.values(), key=lambda e: (COLOURS[e["relation"]], -e["f_scale"], -int(e["severity"]), e["other_name"], e["other_slug"]))


def export(run, root=ROOT):
    entities = run(ENTITIES)
    if not entities:
        raise ValueError("Neo4j has no entities yet; run the supervised registry workflow before exporting")
    books_total = run(BOOKS)[0]["n"]
    search, changed, largest = [], 0, 0
    for row in entities:
        entity = row["e"]
        slug = identifier(entity["slug"])
        if entity["group"] not in GROUPS:
            raise ValueError(f"Unknown entity group: {slug}")
        for key in ("aliases", "abbreviations", "generic_names", "brand_names", "formulas"):
            entity[key] = entity.get(key) or []
        for key in ("drug_class", "class_canonical", "heaviness_group", "heaviness_confidence", "altitude", "rank", "altitude_status", "ordering_value", "tie1", "tie2", "tldr", "eli5", "text_model", "text_date"):
            entity.setdefault(key, None)
        entity.setdefault("text_quote_count", 0)
        entity.setdefault("text_status", "none")
        entity["books_total"] = books_total
        spots = run(LIT, slug=slug)
        for spot in spots:
            spot["pages"] = sorted(set(spot["pages"]))
            spot["sources"] = sorted(set(spot["sources"]))
            spot["mentions"].sort(key=lambda m: (m.get("page_number", 0), m.get("source", ""), m.get("quote", "")))
        entity["lit_spots"] = spots
        entity["edges"] = aggregate(run(EDGES, slug=slug))
        quotes = {s["quote"] for e in entity["edges"] for s in e["statements"]}
        quotes.update(m["quote"] for s in spots for m in s["mentions"] if m.get("source") == "page" and m.get("quote"))
        entity["quotes_total"] = len(quotes)
        count, size = write_json(Path("entities") / f"{slug}.json", entity, root)
        changed += count; largest = max(largest, size)
        search.append({k: entity[k] for k in ("slug", "group", "canonical_name", "aliases", "altitude", "rank")} | {
            "lit_spot_count": len(spots), "edge_count": len(entity["edges"]), "has_text": entity["text_status"] in ("written", "stale")})
    search.sort(key=lambda e: (e["group"], e["canonical_name"], e["slug"]))
    changed += write_json("search.json", search, root, dated=False)[0]
    result = {"entities": len(entities), "files_changed_both_copies": changed, "largest_bytes": largest}
    print(result)
    return result


def main():
    from db import run
    export(run)


if __name__ == "__main__":
    main()
