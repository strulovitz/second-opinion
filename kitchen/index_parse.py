#!/usr/bin/env python3
"""BIBLE 3.7.3: free-reader page parsing, continuations and page mapping."""

import hashlib
import json
from datetime import datetime, timezone

from index_common import (Context, arguments, ask_checked, cli, fingerprint,
                          lock, reader_access, require, save)
from index_pages import assemble, citation_unit, ground_entries
from index_prompts import PARSE
from toc_evidence import pdf_identity

OCR = "Transcribe this textbook index page verbatim. Keep indentation, line breaks, page references and See targets. Output the transcription only; do not add, correct, explain or classify terms."


def parse(ctx, ask, model, vision_model):
    cached, newly = [], 0
    current_pdf = pdf_identity(ctx.pdf)
    for page in ctx.pages:
        text_path, source_path = ctx.path(f"index-{page}.txt"), ctx.path(f"index-{page}-source.json")
        if not source_path.exists():
            break  # Only an extracted, contiguous prefix can be assembled.
        source = json.loads(source_path.read_text())
        require(source["pdf_identity"] == current_pdf, "index text belongs to a changed PDF; rerun extraction checks")
        text = text_path.read_text()
        require(source["text_hash"] == fingerprint(text), "index text changed since extraction")
        image = ctx.image(page)
        require(image.is_file() and hashlib.sha256(image.read_bytes()).hexdigest() == source["image_hash"], "index image changed")
        needs_ocr = len(text.strip()) < 30
        key = fingerprint(["index-parse-v2-no-reasoning", source, ctx.identity, PARSE, OCR if needs_ocr else None, model,
                           vision_model if needs_ocr else None])
        path = ctx.path(f"index-{page}.json")
        if path.exists():
            record = json.loads(path.read_text())
            require(record["key"] == key, "stale parsed page; archive old index caches before changing input/model/prompt")
        else:
            if ctx.args.limit and newly >= ctx.args.limit:
                break
            if needs_ocr:
                ocr_path = ctx.path(f"index-{page}-ocr.json")
                if ocr_path.exists():
                    transcription = json.loads(ocr_path.read_text())
                    require(transcription["key"] == key, "stale OCR transcription")
                    text = transcription["text"]
                else:
                    text = ask(OCR, "Transcribe the index page.", images=[image], expect_json=False, max_tokens=10000)
                    require(isinstance(text, str) and text.strip(), "empty reader transcription")
                    save(ocr_path, {"key": key, "text": text, "model": vision_model})
            def validator(result):
                try:
                    entries = ground_entries(result, text, page, str(image))
                    require(entries or len(text.strip()) < 30, "reader returned no entries from a nonempty page")
                    if entries and entries[0]["headword"] == "CONTINUED":
                        previous = next((row for batch in reversed(cached) for row in reversed(batch)
                                         if row["headword"] != "CONTINUED"), None)
                        require(previous is not None and not previous.get("see"), "orphan CONTINUED entry; this page must contain its main headword")
                    return entries
                except (ValueError, KeyError, TypeError) as exc:
                    stamp = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%S%fZ")
                    save(ctx.path(f"index-{page}-rejected-{stamp}.json"),
                         {"key": key, "reader_model": model, "answer": result,
                          "error": f"{type(exc).__name__}: {exc}"})
                    raise
            entries = ask_checked(ask, PARSE, text, validator, max_tokens=12000, no_reasoning=True)
            record = {"key": key, "reader_model": model, "entries": entries}
            save(path, record)
            newly += 1
            print(f"  parsed index PDF {page}", flush=True)
        cached.append(record["entries"])
    unit = citation_unit(ctx)
    entries, counts = assemble(cached, ctx, unit)
    result = {"book_id": ctx.bid, "input_identity": ctx.identity, "unit": unit,
              "pages_parsed": len(cached), "expected_pages": len(ctx.pages), "complete": len(cached) == len(ctx.pages),
              "entries": entries, "reference_counts": counts}
    save(ctx.path("index-entries.json"), result)
    ctx.summary("parse", new_pages=newly, parsed_pages=len(cached), entries=len(entries), complete=result["complete"], **counts)
    return result


def main(argv=None):
    args = arguments(__doc__).parse_args(argv)
    ctx = Context(args)
    if args.plan:
        ctx.plan("parse")
        return 0
    ctx.execution_guard()
    require(not ctx.fallback, "use index_fallback.py --fallback for opener-based parsing")
    with lock(ctx.path("index.lock")):
        parse(ctx, *reader_access())
    return 0


if __name__ == "__main__":
    raise SystemExit(cli(main))
