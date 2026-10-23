"""Neo4j persistence and deterministic candidate selection for BIBLE 3.7."""

import re

from rapidfuzz import fuzz, process

from index_common import GROUPS, require
from slug import slug, slugify

LABELS = dict(zip(GROUPS, ("Symptom", "Disease", "Treatment")))
CATALOG = """MATCH (e:Entity)
OPTIONAL MATCH (e)-[:DISCUSSED_IN]->(d:Territory)
RETURN e.slug AS slug, e.group AS group, e.canonical_name AS canonical_name,
       e.aliases AS aliases, collect(DISTINCT d.book_id) AS lit_spot_books"""


class Registry:
    def __init__(self, run):
        self.run = run
        self.entities = {}
        self.spots = set()

    def ready(self, districts):
        frozen = self.run("MATCH (m:Meta {key:'skeleton_frozen'}) RETURN m.value AS value")
        require(len(frozen) == 1 and frozen[0]["value"] == "false", "registry creation requires the existing unfrozen schema")
        ids = [r["territory_id"] for r in districts]
        found = self.run("MATCH (d:Territory {level:'district'}) WHERE d.territory_id IN $ids RETURN d.territory_id AS id", ids=ids)
        require({r["id"] for r in found} == set(ids), "districts are not loaded in Neo4j; run load_geography.py after the approved map checkpoints before resolving")
        if districts[0]["book_id"] != "HARRISON-22":
            seed = self.run("MATCH (b:Book {book_id:'HARRISON-22'}) RETURN b.status AS status")
            require(len(seed) == 1 and seed[0]["status"] in ("index-done", "reading", "read"),
                    "the seed book's registry is not present in Neo4j; do not rely on a stale local approval")
        self.entities = {r["slug"]: r for r in self.run(CATALOG)}
        bids = sorted({d["book_id"] for d in districts})
        self.spots = {(r["slug"], r["did"], r["page"], r["source"]) for r in self.run("""MATCH (e:Entity)-[r:DISCUSSED_IN]->(d:Territory)
            WHERE r.book_id IN $bids AND r.source IN ['index','page']
            RETURN e.slug AS slug, d.territory_id AS did, r.page_number AS page, r.source AS source""", bids=bids)}

    def committed(self, entry, record):
        if record.get("how") == "not-an-entity":
            return True
        entity = self.entities.get(record.get("slug"))
        return bool(entity and entity["group"] == record["group"]
                    and entry["display"] in (entity.get("aliases") or [])
                    and all((record["slug"], did, ref["printed_page"], ref.get("source", "index")) in self.spots
                            for ref in entry["references"] for did in ref["district_ids"]))

    def exact(self, name, group=None):
        matches = []
        for entity in self.entities.values():
            if group is not None and entity["group"] != group:
                continue
            aliases = [entity["canonical_name"], *(entity.get("aliases") or [])]
            literal = any(name.casefold() == a.casefold() for a in aliases)
            # The 80-character slug truncation must not collapse distinct long terms.
            named_slug = len(name) <= 80 and entity["slug"] == slug(entity["group"], name)
            if literal or named_slug:
                matches.append(entity)
        return matches

    def candidates(self, display, group):
        words = re.findall(r"[^\W_]+", display, re.UNICODE)
        query = " OR ".join(word + ("~" if len(word) >= 5 else "") for word in words)
        fulltext = self.run("""CALL db.index.fulltext.queryNodes('entity_fulltext', $q)
            YIELD node, score RETURN node.slug AS slug, score ORDER BY score DESC LIMIT 8""", q=query) if query else []
        selected, conflicts = {}, []
        for hit in fulltext:
            entity = self.entities.get(hit["slug"])
            if not entity or hit["score"] < 1.0:
                continue
            if entity["group"] != group:
                conflicts.append(entity["slug"])
            else:
                selected[entity["slug"]] = entity
        names = {}
        for entity in self.entities.values():
            if entity["group"] == group:
                for name in [entity["canonical_name"], *(entity.get("aliases") or [])]:
                    names.setdefault(name, []).append(entity)
        for name, score, _ in process.extract(display, list(names), scorer=fuzz.token_set_ratio, limit=5):
            if score >= 60:
                for entity in names[name]:
                    selected[entity["slug"]] = entity
        for entity in self.exact(display):
            if entity["group"] != group and entity["slug"] not in conflicts:
                conflicts.append(entity["slug"])
        return list(selected.values())[:8], conflicts

    def unused_slug(self, display, group):
        require(slugify(display), "term has no usable ASCII slug; human decision required")
        base, suffix = slug(group, display), 1
        chosen = base
        while chosen in self.entities:
            suffix += 1
            chosen = f"{base}-{suffix}"
        return chosen, base if suffix > 1 else None

    def persist(self, chosen, entry, group, bid, model):
        spots = {}
        for ref in entry["references"]:
            for did in ref["district_ids"]:
                spots.setdefault((did, ref["printed_page"], ref.get("source", "index")), {
                    "did": did, "page": ref["printed_page"], "quote": ref["quote"], "image": ref["image_file"],
                    "source": ref.get("source", "index"), "model": ref.get("reader_model", model)})
        payload = list(spots.values())
        query = """MATCH (m:Meta {key:'skeleton_frozen'}) WHERE m.value = 'false'
        CALL () { UNWIND $dids AS did MATCH (d:Territory {territory_id:did, book_id:$bid})
               RETURN collect(d.territory_id) AS found }
        WITH found WHERE size(found) = size($dids)
        MERGE (e:Entity {slug:$slug})
        ON CREATE SET e.group=$group, e.canonical_name=$name, e.aliases=[$name],
          e.aliases_text=$name, e.generic_names=[], e.brand_names=[], e.formulas=[],
          e.created_from=$origin, e.created_book_id=$bid, e.frozen=false
        WITH e WHERE e.group=$group AND e.frozen=false
        SET e:LABEL
        SET e.aliases=reduce(a=coalesce(e.aliases, []), x IN $aliases |
            CASE WHEN x IN a THEN a ELSE a + [x] END)
        SET e.aliases_text=reduce(s='', x IN e.aliases | s + CASE WHEN s='' THEN '' ELSE ' | ' END + x)
        CALL (e) { UNWIND $spots AS spot
          MATCH (d:Territory {territory_id:spot.did, book_id:$bid})
          MERGE (e)-[r:DISCUSSED_IN {book_id:$bid, page_number:spot.page, source:spot.source}]->(d)
          ON CREATE SET r.quote=spot.quote, r.image_file=spot.image,
                        r.reader_model=spot.model, r.read_date=date()
          RETURN count(r) AS spots }
        RETURN e.slug AS slug, spots""".replace("LABEL", LABELS[group])
        result = self.run(query, slug=chosen, name=entry["display"], group=group, bid=bid, model=model,
                          origin=entry.get("created_from", "index"),
                          dids=sorted({s["did"] for s in payload}), spots=payload,
                          aliases=list(dict.fromkeys([entry["display"], entry["headword"]])))
        require(len(result) == 1 and result[0]["slug"] == chosen, "entity/spot transaction refused; no completion receipt written")
        old = self.entities.get(chosen, {"slug": chosen, "group": group, "canonical_name": entry["display"],
                                         "aliases": [], "lit_spot_books": []})
        old["aliases"] = list(dict.fromkeys((old.get("aliases") or []) + [entry["display"], entry["headword"]]))
        old["lit_spot_books"] = list(dict.fromkeys(old["lit_spot_books"] + [bid]))
        self.entities[chosen] = old
        self.spots.update((chosen, s["did"], s["page"], s["source"]) for s in payload)
        return result[0]["spots"]

    def alias(self, target, alias):
        result = self.run("""MATCH (m:Meta {key:'skeleton_frozen'}) WHERE m.value='false'
            MATCH (e:Entity {slug:$slug}) WHERE e.frozen=false
            SET e.aliases=CASE WHEN $alias IN e.aliases THEN e.aliases ELSE e.aliases+[$alias] END
            SET e.aliases_text=reduce(s='', x IN e.aliases | s + CASE WHEN s='' THEN '' ELSE ' | ' END + x)
            RETURN e.slug AS slug""", slug=target, alias=alias)
        require(len(result) == 1, "See alias update refused")
        entity = self.entities[target]
        entity["aliases"] = list(dict.fromkeys((entity.get("aliases") or []) + [alias]))

    def finish_book(self, bid):
        result = self.run("""MATCH (m:Meta {key:'skeleton_frozen'}) WHERE m.value='false'
            MATCH (b:Book {book_id:$bid}) SET b.status='index-done' RETURN b.book_id AS book_id""", bid=bid)
        require(len(result) == 1 and result[0]["book_id"] == bid, "book completion could not be recorded in Neo4j")


def validate_resolution(answer, candidates):
    require(answer["decision"] in ("SAME", "NEW"), "invalid resolution decision")
    require(type(answer["confidence"]) in (int, float) and 0 <= answer["confidence"] <= 1, "invalid resolution confidence")
    require(isinstance(answer["reason"], str) and len(answer["reason"].split()) <= 15, "invalid resolution reason")
    require((answer["decision"] == "NEW" and answer.get("candidate_slug") is None)
            or (answer["decision"] == "SAME" and answer.get("candidate_slug") in {c["slug"] for c in candidates}), "reader chose an invented candidate")
    return answer
