#!/usr/bin/env python3
"""BIBLE 3.9: counts and 20 terms/group for Nir; explicit review receipt."""

import json
import random
from collections import Counter

from index_common import (Context, GROUPS, arguments, cli, fingerprint, require,
                          rows, save)
from toc_reexport import atomic_write


def main(argv=None):
    parser = arguments(__doc__)
    parser.add_argument("--approve", metavar="HUMAN_WORDS", help="only after Nir approves this exact review")
    args = parser.parse_args(argv)
    ctx = Context(args)
    if args.plan:
        ctx.plan("review")
        return 0
    status = json.loads(ctx.path("index-status.json").read_text())
    require(status["complete"] and status["input_identity"] == ctx.identity, "book index is incomplete or changed")
    if args.approve:
        require(ctx.path("review.md").is_file(), "generate/show the review before recording approval")
        save(ctx.path("index-review-approved.json"), {"book_id": ctx.bid, "status_hash": fingerprint(status),
                                                     "human_words": args.approve,
                                                     "review_hash": fingerprint(ctx.path("review.md").read_text())})
        print(f"{ctx.bid}: recorded human registry review; Checkpoint {'3.5' if ctx.bid == 'HARRISON-22' else '3.6'}")
        return 0
    from db import run
    parsed = json.loads(ctx.path("index-entries.json").read_text())
    resolved = rows(ctx.path("resolved.jsonl"))
    latest = {r["entry_id"]: r for r in resolved}
    classified = {r["display"]: r for r in rows(ctx.path("classified.jsonl")) if r["input_identity"] == ctx.identity}
    entities = run("""MATCH (e:Entity) WHERE e.created_book_id=$bid OR EXISTS {
        MATCH (e)-[:DISCUSSED_IN {book_id:$bid}]->(:Territory) }
        OPTIONAL MATCH (e)-[r:DISCUSSED_IN {book_id:$bid}]->(d:Territory)
        WITH e, d, count(r) AS hits
        RETURN e.slug AS slug, e.canonical_name AS name, e.group AS group, e.aliases AS aliases,
               collect({district:d.name, mentions:hits}) AS districts""", bid=ctx.bid)
    lines = [f"# {ctx.bid} registry review", "", f"Parsed entries: {len(parsed['entries'])}",
             f"Source pages: {parsed['pages_parsed']} (mode: {parsed.get('mode', 'index')})",
             parsed.get("limitation", "Index-derived registry"),
             f"Reference counts: {parsed['reference_counts']}",
             f"Classification groups: {dict(Counter(r['group'] for r in classified.values()))}",
             f"Resolution decisions: {dict(Counter(r['how'] for r in latest.values()))}",
             f"Unresolved See aliases: {status['unresolved_see']}", ""]
    randomizer = random.Random(0)
    for group in GROUPS:
        candidates = [e for e in entities if e["group"] == group]
        lines += [f"## {group}", ""]
        for entity in randomizer.sample(candidates, min(20, len(candidates))):
            districts = sorted(entity["districts"], key=lambda d: -d["mentions"])[:3]
            lines.append(f"- {entity['slug']}: {entity['name']} | aliases: {entity['aliases']} | districts: {districts}")
    excluded = [r for r in classified.values() if r["group"] == "not-an-entity"]
    lines += ["", "## Not an entity (sample)", ""]
    lines += [f"- {r['display']}: {r['reason']}" for r in randomizer.sample(excluded, min(20, len(excluded)))]
    lines += ["", "## Group conflicts, doubtful merges and slug collisions", ""]
    lines += [f"- {r}" for r in latest.values() if r.get("conflicts") or r.get("doubtful") or r.get("collision")]
    atomic_write(ctx.path("review.md"), "\n".join(lines) + "\n")
    print(f"{ctx.bid}: review saved to {ctx.path('review.md')}; approval not recorded")
    return 0


if __name__ == "__main__":
    raise SystemExit(cli(main))
