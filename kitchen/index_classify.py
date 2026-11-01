#!/usr/bin/env python3
"""BIBLE 3.7.4: classify 25 main index terms per free-reader batch."""

import json
import time

from index_common import (Context, arguments, ask_checked, classification_terms,
                          cli, fingerprint, lock, reader_access, require, rows,
                          save_rows, validate_classification)
from index_prompts import CLASSIFY


def classify_batch(ask, batch, depth=0):
    """Classify one batch, splitting it if the reader drops or invents terms.

    The local reader occasionally omits one term from a full 25-term batch and
    does so deterministically for that batch, although it handles the term in
    smaller groups. Retrying the whole batch cannot recover it, so keep the
    normal 25-term batch and fall back to halves only when validation fails.
    """
    payload = [term for _, term in batch]
    try:
        return ask_checked(ask, CLASSIFY, payload,
                           lambda answer: validate_classification(answer, payload),
                           max_tokens=6000)
    except ValueError:
        if len(batch) <= 1 or depth >= 4:
            raise
        middle = len(batch) // 2
        return (classify_batch(ask, batch[:middle], depth + 1)
                + classify_batch(ask, batch[middle:], depth + 1))


def classify(ctx, ask, model):
    started = time.monotonic()
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
        result = classify_batch(ask, batch)
        keyed = {term["display"]: key for key, term in batch}
        saved.extend(row | {"key": keyed[row["display"]], "reader_model": model,
                            "input_identity": ctx.identity, "prompt_hash": fingerprint(CLASSIFY)} for row in result)
        save_rows(path, saved)
        count += 1
        completed = min(offset + 25, len(pending))
        elapsed = time.monotonic() - started
        left = (len(pending) - completed) * elapsed / completed
        print(f"  classified {completed}/{len(pending)} new terms; "
              f"current saved={len(terms) - len(pending) + completed}/{len(terms)}; "
              f"command elapsed={elapsed / 60:.1f} min; estimated CLASSIFY left={left / 3600:.2f} h "
              "at this command's pace", flush=True)
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
