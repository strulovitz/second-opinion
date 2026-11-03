#!/usr/bin/env python3
"""Part 0 / T4+T5+T7+T8+T9+T10: terms -> entities -> lit spots -> Neo4j, in bulk.

Usage: speed_entities.py [--no-neo4j] [--fts-cap 30]
Steps (all library-wide, idempotent):
  1. page offsets per book by code (printed folio found on the page)
  2. entities = terms merged by a normalised key (code only; no synonym guessing)
  3. groups: Harrison's saved classifications as labels, nearest neighbour
     (bge-m3 embeddings) for everything else
  4. lit spots: index references -> district by printed page; full-text hits
     for every entity in every book (capped per entity and book)
  5. bulk UNWIND into Neo4j (old entities are replaced)
"""
import argparse, json, re, sqlite3, sys, time, unicodedata
from collections import Counter, defaultdict
from pathlib import Path

import numpy as np
import requests

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "kitchen"))
DB = ROOT / "kitchen" / "logs" / "library.sqlite"
BOOKS = {b["book_id"]: b for b in json.loads((ROOT / "kitchen" / "books.json").read_text())}
GEO = json.loads((ROOT / "data" / "export" / "geography" / "geography.json").read_text())
GROUPS = ("symptoms-and-signs", "diseases-and-conditions", "treatments-and-drugs")
LABELS = dict(zip(GROUPS, ("Symptom", "Disease", "Treatment")))
EMBED_URL = "http://127.0.0.1:11434/api/embed"
STOP = {"the", "of", "and", "in", "for", "with", "to", "a", "an"}


def log(msg):
    print(time.strftime("%H:%M:%S"), msg, flush=True)


# ---------- 1. page offsets ----------
def page_offsets(con):
    out = {}
    for bid in BOOKS:
        if BOOKS[bid].get("page_offset") is not None:
            out[bid] = BOOKS[bid]["page_offset"]
            continue
        c = Counter()
        for pg, t in con.execute("SELECT page, text FROM pages WHERE book_id=? AND page % 5 = 0", (bid,)):
            ls = [l.strip() for l in t.split("\n") if l.strip()]
            for l in ls[:3] + ls[-3:]:
                m = re.fullmatch(r"(\d{1,4})", l) or re.match(r"^(\d{1,4})\s+\S", l) or re.search(r"\S\s+(\d{1,4})$", l)
                if m and 0 <= pg - int(m.group(1)) < 500:
                    c[pg - int(m.group(1))] += 1
        best = c.most_common(1)
        out[bid] = best[0][0] if best and best[0][1] >= 10 else None
        if out[bid] is None:  # fallback: chapter titles found in the text give pdf_page - printed_start
            votes = Counter()
            chapters = [t for t in GEO if t.get("level") == "district" and t["book_id"] == bid][:80]
            for t in chapters:
                title = re.sub(r"[^\w\s]", " ", t["name"]).strip()
                if len(title) < 8:
                    continue
                try:
                    hits = con.execute("SELECT page FROM pages_fts WHERE book_id=? AND pages_fts MATCH ? LIMIT 30",
                                       (bid, '"' + title + '"')).fetchall()
                except sqlite3.OperationalError:
                    continue
                for (pg,) in hits:
                    if 0 <= pg - t["page_start"] < 600:
                        votes[pg - t["page_start"]] += 1
            best = votes.most_common(2)
            if best and best[0][1] >= 4 and (len(best) == 1 or best[0][1] >= 1.5 * best[1][1]):
                out[bid] = best[0][0]
    return out


# ---------- 2. entity keys ----------
def norm(s):
    s = unicodedata.normalize("NFKD", s)
    s = "".join(ch for ch in s if not unicodedata.combining(ch)).casefold()
    s = re.sub(r"\s*\((?:[^()]*)\)\s*$", "", s)  # trailing "(abbrev)"
    s = re.sub(r"[^\w\s]", " ", s)
    words = [w for w in s.split() if w not in STOP]
    words = [re.sub(r"ies$", "y", w) if len(w) > 4 else w for w in words]
    words = [w[:-1] if len(w) > 4 and w.endswith("s") and not w.endswith("ss") else w for w in words]
    return " ".join(sorted(words))


def abbreviation(s):
    m = re.search(r"\(([A-Za-z][A-Za-z0-9-]{1,10})\)\s*$", s)
    return m.group(1) if m else None


# ---------- 3. embeddings ----------
def embed(texts, batch=128):
    vecs = []
    for i in range(0, len(texts), batch):
        r = requests.post(EMBED_URL, json={"model": "bge-m3", "input": texts[i:i + batch], "keep_alive": "30m"}, timeout=600)
        r.raise_for_status()
        vecs.extend(r.json()["embeddings"])
        if (i // batch) % 50 == 0:
            log(f"  embedded {min(i + batch, len(texts))}/{len(texts)}")
    v = np.array(vecs, dtype=np.float32)
    return v / np.maximum(np.linalg.norm(v, axis=1, keepdims=True), 1e-9)


def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--no-neo4j", action="store_true")
    ap.add_argument("--fts-cap", type=int, default=30)
    ap.add_argument("--min-fts-len", type=int, default=7)
    a = ap.parse_args()
    con = sqlite3.connect(DB)
    t0 = time.time()

    offsets = page_offsets(con)
    log(f"page offsets: {sum(v is not None for v in offsets.values())}/{len(offsets)} books resolved")

    districts = defaultdict(list)
    for t in GEO:
        if t.get("level") == "district":
            districts[t["book_id"]].append((t["page_start"], t["page_end"], t["territory_id"]))
    for v in districts.values():
        v.sort()

    def district_of(bid, printed):
        for s, e, did in districts.get(bid, ()):
            if s <= printed <= e:
                return did
        return None

    # terms -> entities
    rows = con.execute("SELECT book_id, headword, see, refs, sub_refs, page FROM terms").fetchall()
    ents = {}
    see_links = []
    junk = re.compile(r"^(?:in|for|with|of|and|due to|from|as|by|on|to|after|during|versus|vs)\b|\b\d{2,4}[tfb]?\b|\bsee\b", re.I)
    for bid, head, see, refs, sub_refs, page in rows:
        head = re.sub(r"[,;:]?\s+(?:and|or|in|of|for|with|the)$", "", head.strip())
        key = norm(head)
        if not key or junk.search(head) or len(head) > 90 or len(key.split()) > 7:
            continue
        e = ents.setdefault(key, {"names": Counter(), "aliases": set(), "spots": defaultdict(set), "books": set()})
        e["names"][head] += 1
        e["books"].add(bid)
        ab = abbreviation(head)
        if ab:
            e["aliases"].add(ab)
        if see:
            see_links.append((norm(see), head))
        for r in json.loads(refs) + json.loads(sub_refs):
            m = re.match(r"^(\d{1,4})", r)
            if m:
                e["spots"][bid].add(int(m.group(1)))
    for target, alias in see_links:
        if target in ents:
            ents[target]["aliases"].add(alias)
    log(f"terms {len(rows)} -> entities {len(ents)} (code merge only)")

    # classification labels from Harrison's saved classifications
    labels = {}
    cpath = ROOT / "kitchen" / "logs" / "HARRISON-22-classified.jsonl"
    if cpath.exists():
        for line in cpath.read_text().splitlines():
            if line.strip():
                d = json.loads(line)
                labels[norm(d["display"])] = d["group"]
    keys = list(ents)
    names = [ents[k]["names"].most_common(1)[0][0] for k in keys]
    log("embedding entity names with bge-m3 ...")
    vec = embed(names)
    labelled = [i for i, k in enumerate(keys) if labels.get(k) in GROUPS]
    L = vec[labelled]
    lab_groups = np.array([GROUPS.index(labels[keys[i]]) for i in labelled])
    groups = {}
    for i0 in range(0, len(keys), 2048):
        sims = vec[i0:i0 + 2048] @ L.T
        top = np.argpartition(-sims, 5, axis=1)[:, :5]
        for j, row in enumerate(top):
            i = i0 + j
            if labels.get(keys[i]) in GROUPS:
                groups[keys[i]] = labels[keys[i]]
            elif labels.get(keys[i]) == "not-an-entity":
                groups[keys[i]] = None
            else:
                votes = Counter(int(lab_groups[t]) for t in row)
                best_sim = float(sims[j, row].max())
                groups[keys[i]] = GROUPS[votes.most_common(1)[0][0]] if best_sim >= 0.55 else None
                if groups[keys[i]] and best_sim < 0.70 and votes.most_common(1)[0][1] < 3:
                    groups[keys[i]] = None
    kept = [k for k in keys if groups.get(k)]
    log(f"groups: {Counter(groups[k] for k in kept)}; dropped as not-an-entity/unsure: {len(keys) - len(kept)}")

    # full-text lit spots, every entity in every book
    log("full-text search for every entity in every book ...")
    fts_spots = defaultdict(lambda: defaultdict(set))
    n_q = 0
    for k in kept:
        name = ents[k]["names"].most_common(1)[0][0]
        q = re.sub(r"\s*\([^)]*\)\s*$", "", name).strip()
        if len(q) < a.min_fts_len or not re.search(r"[a-zA-Z]{3}", q):
            continue
        phrase = '"' + q.replace('"', " ") + '"'
        try:
            hits = con.execute("SELECT book_id, page FROM pages_fts WHERE pages_fts MATCH ? LIMIT 2000", (phrase,)).fetchall()
        except sqlite3.OperationalError:
            continue
        n_q += 1
        per = Counter()
        for bid, page in hits:
            if per[bid] < a.fts_cap:
                per[bid] += 1
                fts_spots[k][bid].add(page)
        if n_q % 10000 == 0:
            log(f"  {n_q} searches")
    log(f"full-text done: {n_q} searches")

    # assemble rows
    ent_rows, spot_rows = [], []
    for k in kept:
        e = ents[k]
        name = e["names"].most_common(1)[0][0]
        slug = f"{groups[k]}-" + re.sub(r"[^a-z0-9]+", "-", unicodedata.normalize("NFKD", name).encode("ascii", "ignore").decode().lower()).strip("-")[:80]
        if not slug.split("-", 3)[-1]:
            continue
        aliases = list(dict.fromkeys([name] + list(e["names"]) + sorted(e["aliases"])))
        ent_rows.append({"slug": slug, "group": groups[k], "name": name, "aliases": aliases, "label": LABELS[groups[k]],
                         "books": sorted(e["books"])})
        for bid, pages in e["spots"].items():
            for p in pages:
                did = district_of(bid, p)
                if did:
                    spot_rows.append({"slug": slug, "did": did, "bid": bid, "page": p, "source": "index"})
        for bid, pdfpages in fts_spots[k].items():
            off = offsets.get(bid)
            if off is None:
                continue
            for pp in pdfpages:
                printed = pp - off
                did = district_of(bid, printed)
                if did and not (bid in e["spots"] and printed in e["spots"][bid]):
                    spot_rows.append({"slug": slug, "did": did, "bid": bid, "page": printed, "source": "text"})
    seen = set()
    ent_rows = [r for r in ent_rows if not (r["slug"] in seen or seen.add(r["slug"]))]
    log(f"entities {len(ent_rows)}, lit spots {len(spot_rows)} "
        f"(index {sum(r['source'] == 'index' for r in spot_rows)}, text {sum(r['source'] == 'text' for r in spot_rows)})")
    (ROOT / "kitchen" / "logs" / "speed_entities_summary.json").write_text(json.dumps({
        "entities": len(ent_rows), "lit_spots": len(spot_rows), "groups": Counter(r["group"] for r in ent_rows),
        "offsets": offsets, "seconds": round(time.time() - t0)}, indent=1, default=str))
    if a.no_neo4j:
        return 0

    from db import run
    log("Neo4j: replacing entities and lit spots ...")
    run("MATCH ()-[r:DISCUSSED_IN]->() CALL (r) { DELETE r } IN TRANSACTIONS OF 20000 ROWS")
    run("MATCH (e:Entity) CALL (e) { DETACH DELETE e } IN TRANSACTIONS OF 20000 ROWS")
    for lab in LABELS.values():
        batch = [r for r in ent_rows if r["label"] == lab]
        for i in range(0, len(batch), 5000):
            run(f"""UNWIND $rows AS r MERGE (e:Entity {{slug:r.slug}})
                SET e:{lab}, e.group=r.group, e.canonical_name=r.name, e.aliases=r.aliases,
                    e.aliases_text=reduce(s='', x IN r.aliases | s + CASE WHEN s='' THEN '' ELSE ' | ' END + x),
                    e.generic_names=[], e.brand_names=[], e.formulas=[], e.created_from='index-code',
                    e.created_book_id=r.books[0], e.frozen=false""", rows=batch[i:i + 5000])
    for i in range(0, len(spot_rows), 20000):
        run("""UNWIND $rows AS r MATCH (e:Entity {slug:r.slug}), (d:Territory {territory_id:r.did})
            MERGE (e)-[x:DISCUSSED_IN {book_id:r.bid, page_number:r.page, source:r.source}]->(d)
            ON CREATE SET x.read_date=date(), x.reader_model='code'""", rows=spot_rows[i:i + 20000])
        if (i // 20000) % 10 == 0:
            log(f"  spots {min(i + 20000, len(spot_rows))}/{len(spot_rows)}")
    print(run("MATCH (e:Entity) RETURN count(e) AS entities"), run("MATCH ()-[r:DISCUSSED_IN]->() RETURN count(r) AS spots"))
    log(f"done in {time.time() - t0:.0f}s")
    return 0


if __name__ == "__main__":
    sys.exit(main())
