#!/usr/bin/env python3
"""BIBLE Part 0 section 12.3: load the hand-entered golden facts into Neo4j.

  .venv/bin/python kitchen/golden_load.py            validate + load + rough heights
  .venv/bin/python kitchen/golden_load.py --check    validate only
  .venv/bin/python kitchen/golden_load.py --find "liver failure"   slug helper

data/golden/facts.json = {"sources": {"S001": {title, origin, year, file, kind, strength}},
  "new_entities": [{name, group, aliases}], "facts": [{id, relation, from, to, quote,
  source, frequency_phrase, severity_phrase, numeric_pct, subtype, price, availability,
  approval, note, strength, entered_by, entered_date}]}
Quotes must be found verbatim in data/golden/sources/<file>. Every run replaces all
relationships with source "article" (idempotent).
"""
import json, re, sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "kitchen"))
from db import run
from slug import slug as make_slug

FACTS = Path(__import__("os").environ.get("GOLDEN_FACTS", ROOT / "data" / "golden" / "facts.json"))
SRC = ROOT / "data" / "golden" / "sources"
S, D, T, C = "symptoms-and-signs", "diseases-and-conditions", "treatments-and-drugs", "causes"
LEGAL = {"PRESENTS_WITH": ({D, C}, {S}), "TREATED_BY": ({D, S, C}, {T}), "HARMS": ({T}, {D, S, C}),
         "LEADS_TO": ({D, C}, {D, S, C}), "MISTAKEN_FOR": ({D}, {D}), "SAME_CHEMICAL": ({T}, {T})}
LABEL = {S: "Symptom", D: "Disease", T: "Treatment", C: "Cause"}
F_WORDS = [  # Part 4 section 8.3, longest phrases first inside each level; F1 before F2 ("very rare")
    (1, "very rare|very rarely|extremely rare|exceedingly rare|exceptionally|exceptional|case reports|isolated reports|anecdotal"),
    (3, "infrequently|occasionally|sometimes|in some patients|some patients|a minority|less commonly|less common|less frequent|may occur|can occur|uncommonly|uncommon"),
    (2, "on rare occasions|in rare cases|rarely|rare|infrequent|unusual|seldom|few patients|a small number|a small proportion"),
    (5, "most patients|the majority|majority of|nearly all|almost all|virtually all|all patients|usually|typically|characteristic|hallmark|invariably|universal|cardinal|classically|classic|predominant|most common|the most frequent|in most"),
    (4, "not uncommon|commonly|common|frequently|frequent|often|many patients|a substantial|a significant proportion|a large proportion|regularly|well recognized|well-recognized|prominent"),
]
SEVERE = ["fatal", "fatality", "death", "life-threatening", "life threatening", "lethal", "boxed warning", "black box",
          "medical emergency", "requires immediate", "requires urgent", "potentially fatal", "mortality", "irreversible",
          "permanent", "failure"]


def norm(s):
    s = s.replace("*", "").replace("\u00ad", "").replace("\u2019", "'").replace("\u2018", "'").replace("\u201c", '"').replace("\u201d", '"')
    s = re.sub(r"[\u2013\u2014]", "-", s)
    return re.sub(r"\s+", " ", s).strip().lower()


def f_scale(phrase, pct):
    if pct is not None:
        return 5 if pct > 50 else 4 if pct > 10 else 3 if pct > 1 else 2 if pct > 0.1 else 1
    p = (phrase or "").lower()
    for f, words in F_WORDS:
        if re.search(r"\b(" + words + r")\b", p):
            return f
    return 0


def pct_of(phrase):
    nums = re.findall(r"(\d+(?:\.\d+)?)\s*(?:-\s*(\d+(?:\.\d+)?))?\s*%", phrase or "")
    if not nums:
        return None
    a, b = nums[0]
    return float(b or a)


def find(name):
    q = name.lower()
    rows = run("""MATCH (e:Entity) WHERE toLower(e.canonical_name) CONTAINS $q
        OR any(a IN coalesce(e.aliases, []) WHERE toLower(a) CONTAINS $q)
        RETURN e.slug AS slug, e.canonical_name AS name, coalesce(e.common, 0) AS common
        ORDER BY size(e.canonical_name), common DESC LIMIT 20""", q=q)
    for r in rows:
        print(f"{r['common']:6d}  {r['slug']}  |  {r['name']}")


def load(check_only=False):
    data = json.loads(FACTS.read_text())
    sources, errors = data.get("sources", {}), []
    new = {}
    for n in data.get("new_entities", []):
        if n["group"] not in LABEL:
            errors.append(f"new entity {n['name']}: bad group {n['group']}")
            continue
        new[make_slug(n["group"], n["name"])] = n
    slugs = list({x for f in data["facts"] for x in (f["from"], f["to"])} - set(new))
    known = {r["slug"]: r["grp"] for r in run("MATCH (e:Entity) WHERE e.slug IN $s RETURN e.slug AS slug, e.group AS grp", s=slugs)}
    known.update({s: n["group"] for s, n in new.items()})
    texts, rows, seen = {}, {}, set()
    for f in data["facts"]:
        fid, rel = f.get("id"), f.get("relation")
        if fid in seen:
            errors.append(f"{fid}: duplicate id")
        seen.add(fid)
        src = sources.get(f["source"]) if isinstance(f.get("source"), str) else f.get("source")
        if not src:
            errors.append(f"{fid}: unknown source {f.get('source')}")
            continue
        if rel not in LEGAL:
            errors.append(f"{fid}: bad relation {rel}")
            continue
        ga, gb = known.get(f["from"]), known.get(f["to"])
        if not ga or not gb:
            errors.append(f"{fid}: unknown slug {f['from'] if not ga else f['to']}")
            continue
        if ga not in LEGAL[rel][0] or gb not in LEGAL[rel][1]:
            errors.append(f"{fid}: {rel} not legal for {ga} -> {gb}")
        if src["file"] not in texts:
            texts[src["file"]] = norm((SRC / src["file"]).read_text())
        if not f.get("quote") or norm(f["quote"]) not in texts[src["file"]]:
            errors.append(f"{fid}: quote not found verbatim in {src['file']}: {f.get('quote', '')[:60]}")
        pct = f.get("numeric_pct", pct_of(f.get("frequency_phrase")))
        sev_words = f.get("severity_phrase") or next((w for w in SEVERE if w in norm(f.get("quote", ""))), "")
        rows.setdefault(rel, []).append({
            "id": fid, "from_slug": f["from"], "to_slug": f["to"], "quote": f["quote"],
            "frequency_phrase": f.get("frequency_phrase", ""), "numeric_pct": pct,
            "f_scale": f_scale(f.get("frequency_phrase"), pct), "severity": bool(sev_words), "severity_phrase": sev_words,
            "subtype": f.get("subtype"), "price": f.get("price", ""), "availability": f.get("availability", ""),
            "approval": f.get("approval", ""), "note": f.get("note", ""), "source_id": f["source"] if isinstance(f["source"], str) else "",
            "source_title": src.get("title", ""), "origin": src.get("origin", ""), "year": src.get("year"),
            "kind": src.get("kind", ""), "strength": f.get("strength") or src.get("strength", ""), "file": src["file"],
            "entered_by": f.get("entered_by", ""), "entered_date": f.get("entered_date", "")})
    for e in errors:
        print("ERROR", e)
    print(f"{len(data['facts'])} facts, {len(new)} new entities, {len(errors)} errors")
    if errors or check_only:
        return not errors
    for s, n in new.items():
        run(f"""MERGE (e:Entity {{slug: $slug}}) ON CREATE SET e.created_from = 'article', e.frozen = false
            SET e:{LABEL[n['group']]}, e.group = $group, e.canonical_name = $name, e.aliases = $aliases,
                e.aliases_text = $text, e.needs_review = true""",
            slug=s, group=n["group"], name=n["name"], aliases=[n["name"]] + n.get("aliases", []),
            text=" | ".join([n["name"]] + n.get("aliases", [])))
    run("MATCH ()-[r]->() WHERE r.source = 'article' DELETE r")
    for rel, lst in rows.items():
        run(f"""UNWIND $rows AS r MATCH (a:Entity {{slug: r.from_slug}}), (b:Entity {{slug: r.to_slug}})
            CREATE (a)-[x:{rel}]->(b) SET x = r, x.source = 'article'""", rows=lst)
    for r in run("MATCH ()-[r]->() WHERE r.source = 'article' RETURN type(r) AS rel, count(*) AS n ORDER BY rel"):
        print(r)
    import rough_heights
    rough_heights.main()
    return True


if __name__ == "__main__":
    if len(sys.argv) > 2 and sys.argv[1] == "--find":
        find(" ".join(sys.argv[2:]))
    else:
        sys.exit(0 if load("--check" in sys.argv) else 1)
