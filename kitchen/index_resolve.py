#!/usr/bin/env python3
"""BIBLE 3.7.5-7.7: resolve entities and proving pages into Neo4j, resumably."""

import json
from pathlib import Path

from index_classify import current_classifications
from index_common import (Context, arguments, ask_checked, cli, fingerprint,
                          lock, reader_access, require, rows, save, save_rows)
from index_prompts import RESOLVE
from index_registry import Registry, validate_resolution


def decide(entry, classification, registry, ask):
    name, group = entry["display"], classification["group"]
    exact = registry.exact(name, group)
    if len(exact) == 1:
        return {"slug": exact[0]["slug"], "how": "exact", "reason": "same-group name/alias", "conflicts": []}
    candidates, conflicts = registry.candidates(name, group)
    for entity in exact:
        if entity["slug"] not in {c["slug"] for c in candidates}:
            candidates.insert(0, entity)
    candidates = candidates[:8]
    decision = None
    if candidates:
        payload = {"term": name, "group": group, "subentries": [s["text"] for s in entry["subentries"][:8]],
                   "context_districts": entry.get("context_districts", [])[:5],
                   "candidates": [{k: (c.get(k) or [])[:8] if k == "aliases" else c.get(k)
                                   for k in ("slug", "canonical_name", "aliases", "lit_spot_books")} for c in candidates]}
        decision = ask_checked(ask, RESOLVE, payload, lambda value: validate_resolution(value, candidates), max_tokens=1200)
        if decision["decision"] == "SAME" and decision["confidence"] >= 0.6:
            return {"slug": decision["candidate_slug"], "how": "reader-merge", "reason": decision["reason"],
                    "decision": decision, "conflicts": conflicts}
    chosen, collision = registry.unused_slug(name, group)
    return {"slug": chosen, "how": "group-conflict" if conflicts else ("new-reader" if candidates else "new-no-candidates"),
            "reason": decision["reason"] if decision else "no qualifying same-group candidate",
            "decision": decision, "conflicts": conflicts, "collision": collision,
            "doubtful": bool(decision and decision["decision"] == "SAME" and decision["confidence"] < 0.6)}


def retry_see(ctx, registry, entries):
    paths = list(ctx.logs.glob("*-unresolved-see.json"))
    current = ctx.path("unresolved-see.json")
    if current not in paths:
        paths.append(current)
    inherited = {str(p): json.loads(p.read_text()) if p.exists() else [] for p in paths}
    pending = inherited[str(current)]
    known = {(r["headword"], r["target"]) for r in pending}
    for entry in entries:
        if entry.get("see") and (entry["headword"], entry["see"]) not in known:
            pending.append({"headword": entry["headword"], "target": entry["see"], "book_id": ctx.bid,
                            "sources": entry["sources"]})
            known.add((entry["headword"], entry["see"]))
    unresolved = 0
    for path, records in inherited.items():
        again = records
        while True:
            remaining = []
            for row in again:
                candidates = registry.exact(row["target"])
                if len(candidates) == 1:
                    registry.alias(candidates[0]["slug"], row["headword"])
                    history_path = ctx.logs / f"{row['book_id']}-see-aliases.jsonl"
                    history = rows(history_path)
                    key = fingerprint(row)
                    if key not in {r["key"] for r in history}:
                        save_rows(history_path, history + [row | {"key": key, "slug": candidates[0]["slug"]}])
                else:
                    remaining.append(row)
            if len(remaining) == len(again):
                break
            again = remaining
        save(Path(path), remaining)
        unresolved += len(remaining)
    return unresolved


def resolve(ctx, registry, ask, model, dry_run=False):
    parsed = json.loads(ctx.path("index-entries.json").read_text())
    require(parsed["input_identity"] == ctx.identity, "parsed index inputs changed")
    require(parsed["entries"], "no source entries have been parsed yet")
    require(parsed["complete"], "complete the source parsing before resolving partial term context into Neo4j")
    require(parsed["reference_counts"]["mapping-unresolved"] == 0, "printed-to-district mapping is unresolved; do not invent provenance")
    classifications = current_classifications(ctx, parsed, model)
    ctx.execution_guard()
    registry.ready(ctx.districts)
    log_path, decisions_path = ctx.path("resolved.jsonl"), ctx.path("resolve-decisions.jsonl")
    log, decisions = rows(log_path), rows(decisions_path)
    done, planned = {r["key"]: r for r in log}, {r["key"]: r for r in decisions}
    count = skipped = 0
    for original in parsed["entries"]:
        if original.get("see"):
            continue
        entry = dict(original)
        names = {d["territory_id"]: d["name"] for d in ctx.districts}
        entry["context_districts"] = list(dict.fromkeys(names[did] for ref in entry["references"] for did in ref["district_ids"]))[:5]
        classification = classifications[entry["display"]]
        previous_groups = {r["group"] for r in log if r["entry_id"] == entry["id"] and r.get("group")}
        require(not previous_groups or previous_groups == {classification["group"]},
                "an already-stored entry changed group; record a human-directed correction before replacing its relationships")
        key = fingerprint([ctx.identity, entry, classification, RESOLVE])
        if key in done and registry.committed(entry, done[key]):
            skipped += 1
            continue
        if classification["group"] == "not-an-entity":
            record = {"key": key, "entry_id": entry["id"], "display": entry["display"], "how": "not-an-entity"}
        else:
            for ref in entry["references"]:
                require(Path(ref["image_file"]).is_file() and ref["quote"], "missing index image/verbatim proving quote")
            decision = planned.get(key)
            if decision is None:
                decision = decide(entry, classification, registry, ask) | {"key": key}
                if not dry_run:
                    decisions.append(decision)
                    save_rows(decisions_path, decisions)  # Durable before the DB transaction.
            elif decision["how"] in ("exact", "reader-merge"):
                require(decision["slug"] in registry.entities, "cached merge target was removed; human review required")
            elif decision["slug"] in registry.entities:
                require(registry.entities[decision["slug"]]["canonical_name"] == entry["display"],
                        "cached new slug now belongs to another name; human review required")
            count_spots = 0 if dry_run else registry.persist(decision["slug"], entry, classification["group"], ctx.bid, model)
            record = decision | {"entry_id": entry["id"], "display": entry["display"],
                                  "group": classification["group"], "lit_spots": count_spots}
        if not dry_run:
            for field, suffix in (("doubtful", "doubtful-merges.jsonl"), ("collision", "slug-collisions.jsonl")):
                if record.get(field):
                    path = ctx.path(suffix)
                    prior = rows(path)
                    if key not in {r["key"] for r in prior}:
                        save_rows(path, prior + [record])
            log.append(record)
            save_rows(log_path, log)
        count += 1
        if count == 1 or count % 25 == 0:
            print(f"  resolved new index entries: {count}", flush=True)
        if ctx.args.limit and count >= ctx.args.limit:
            break
    unresolved = None if dry_run else retry_see(ctx, registry, parsed["entries"])
    complete = parsed["complete"] and (count + skipped == sum(not e.get("see") for e in parsed["entries"]))
    if not dry_run:
        if complete:
            registry.finish_book(ctx.bid)
        save(ctx.path("index-status.json"), {"book_id": ctx.bid, "input_identity": ctx.identity,
                                           "complete": complete, "unresolved_see": unresolved,
                                           "mode": "chapter-fallback" if ctx.fallback else "index"})
    ctx.summary("resolve", new_entries=count, cached_entries=skipped, unresolved_see=unresolved, complete=complete, dry_run=dry_run)
    return log


def main(argv=None):
    parser = arguments(__doc__)
    parser.add_argument("--dry-run", action="store_true", help="compute decisions without database/decision-cache writes")
    args = parser.parse_args(argv)
    ctx = Context(args)
    if args.plan:
        ctx.plan("resolve")
        return 0
    from db import run
    with lock(ctx.logs / "index-registry.lock"), lock(ctx.path("index.lock")):
        ask, model, _ = reader_access()
        resolve(ctx, Registry(run), ask, model, args.dry_run)
    return 0


if __name__ == "__main__":
    raise SystemExit(cli(main))
