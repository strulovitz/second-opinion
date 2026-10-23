#!/usr/bin/env python3
"""BIBLE 3.7.4: classify 25 main index terms per free-reader batch."""

import json

from index_common import (Context, arguments, ask_checked, classification_terms,
                          cli, fingerprint, lock, reader_access, require, rows,
                          save_rows, validate_classification)
from index_prompts import CLASSIFY


def classify(ctx, ask, model):
    parsed = json.loads(ctx.path("index-entries.json").read_text())
    require(parsed["input_identity"] == ctx.identity, "parsed entries belong to changed inputs")
    terms = classification_terms(parsed["entries"], ctx.districts)
    path = ctx.path("classified.jsonl")
    saved = rows(path)
    done = {r["key"] for r in saved}
    pending = []
    for term in terms:
        key = fingerprint([ctx.identity, term, CLASSIFY, model])
        if key not in done:
            pending.append((key, term))
    count = 0
    for offset in range(0, len(pending), 25):
        batch = pending[offset:offset + 25]
        payload = [term for _, term in batch]
        result = ask_checked(ask, CLASSIFY, payload, lambda answer: validate_classification(answer, payload), max_tokens=6000)
        keyed = {term["display"]: key for key, term in batch}
        saved.extend(row | {"key": keyed[row["display"]], "reader_model": model,
                            "input_identity": ctx.identity, "prompt_hash": fingerprint(CLASSIFY)} for row in result)
        save_rows(path, saved)
        count += 1
        print(f"  classified {min(offset + 25, len(pending))}/{len(pending)} new terms", flush=True)
        if ctx.args.limit and count >= ctx.args.limit:
            break
    ctx.summary("classify", new_batches=count, expected_terms=len(terms), saved_records=len(saved))
    return saved


def current_classifications(ctx, parsed, model):
    terms = classification_terms(parsed["entries"], ctx.districts)
    saved = {r["key"]: r for r in rows(ctx.path("classified.jsonl"))}
    result = {}
    for term in terms:
        key = fingerprint([ctx.identity, term, CLASSIFY, model])
        require(key in saved, f"classification missing/current inputs changed: {term['display']}")
        result[term["display"]] = saved[key]
    return result


def main(argv=None):
    args = arguments(__doc__).parse_args(argv)
    ctx = Context(args)
    if args.plan:
        ctx.plan("classify")
        return 0
    ctx.execution_guard()
    with lock(ctx.path("index.lock")):
        ask, model, _ = reader_access()
        classify(ctx, ask, model)
    return 0


if __name__ == "__main__":
    raise SystemExit(cli(main))
