#!/usr/bin/env python3
"""BIBLE 3.7.3: free-reader page parsing, continuations and page mapping."""

import hashlib
import json
import time
from datetime import datetime, timezone

from index_common import (Context, arguments, ask_checked, cli, fingerprint,
                          lock, reader_access, require, save)
from index_pages import assemble, citation_unit, ground_entries
from index_order import reading_text
from index_prompts import PARSE
from index_schema import PARSE_CONTROLS, check_shape
from index_fragments import FORMAT, parse_fragments
from toc_evidence import pdf_identity

OCR = "Transcribe this textbook index page verbatim. Keep indentation, line breaks, page references and See targets. Output the transcription only; do not add, correct, explain or classify terms."


def checkpoint(ctx, cached):
    unit = citation_unit(ctx)
    entries, counts = assemble(cached, ctx, unit)
    result = {"book_id": ctx.bid, "input_identity": ctx.identity, "unit": unit,
              "pages_parsed": len(cached), "expected_pages": len(ctx.pages),
              "complete": len(cached) == len(ctx.pages), "entries": entries, "reference_counts": counts}
    save(ctx.path("index-entries.json"), result)
    return result


def parse(ctx, ask, model, vision_model):
    cached, newly = [], 0
    resumed_partial = False
    started = time.monotonic()
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
        inputs = [source, ctx.identity, PARSE, OCR if needs_ocr else None, model,
                  vision_model if needs_ocr else None]
        legacy_key = fingerprint(["index-parse-v2-no-reasoning", *inputs])
        path = ctx.path(f"index-{page}.json")
        record = json.loads(path.read_text()) if path.exists() else None
        if record and "output_format" not in record:
            require(record["key"] == legacy_key, "stale parsed page; archive old index caches before changing input/model/prompt")
            if needs_ocr:
                transcription = json.loads(ctx.path(f"index-{page}-ocr.json").read_text())
                require(transcription["key"] == legacy_key, "stale OCR transcription")
                text = transcription["text"]
            # Legacy syntax is reusable only when all source references survived.
            ground_entries({"entries": record["entries"]}, text, page, str(image))
            cached.append(record["entries"])
            continue
        if not record and ctx.args.limit and newly >= ctx.args.limit:
            break
        order_key = None
        if not needs_ocr:
            text, order_key = reading_text(ctx, page, source, text)
        key = fingerprint(["index-parse-v3-json-object", *inputs, order_key])
        controls = {"reader": PARSE_CONTROLS, "fragments": FORMAT, "max_tokens": 12000}
        new_key = fingerprint(["index-parse-v4-structured-fragments", *inputs, order_key, controls])
        if record:
            if record.get("output_format") == "json_schema":
                require(record.get("parse_controls") == controls, "parsed-page controls changed")
                key = new_key
            require(record["key"] == key, "stale parsed page; archive old index caches before changing input/model/prompt")
            require(record.get("output_format") in ("json_object", "json_schema") and record.get("reading_order_key") == order_key,
                    "parsed-page output/order receipt changed")
            if needs_ocr:
                transcription = json.loads(ctx.path(f"index-{page}-ocr.json").read_text())
                require(transcription["key"] == key, "stale OCR transcription")
                text = transcription["text"]
            ground_entries({"entries": record["entries"]}, text, page, str(image))
        else:
            key = new_key
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
            has_answer = False
            def validator(result):
                nonlocal has_answer
                has_answer = True
                try:
                    check_shape(result)
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
            def capture(response):
                nonlocal has_answer
                has_answer = True
                stamp = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%S%fZ")
                save(ctx.path(f"index-{page}-response-{stamp}.json"),
                     {"key": key, "source": source, "reader_model": model, **response})
            print(f"  reading index PDF {page} ({len(cached)}/{len(ctx.pages)} pages saved)", flush=True)
            if ctx.path(f"index-{page}-fragments.json").exists():
                resumed_partial = True
                entries = parse_fragments(ctx, ask, text, page, str(image), key)
            else:
                try:
                    entries = ask_checked(ask, PARSE, text, validator, max_tokens=12000,
                                          on_response=capture, **PARSE_CONTROLS)
                except ValueError:
                    if not has_answer:
                        raise  # No model completion: do not multiply transport failures.
                    print(f"  PDF {page}: whole-page validation failed; using bounded fragments", flush=True)
                    entries = parse_fragments(ctx, ask, text, page, str(image), key)
            validator({"entries": [{k: row[k] for k in ("headword", "display", "see", "pages", "subentries")}
                                   for row in entries]})
            record = {"key": key, "reader_model": model, "output_format": "json_schema",
                      "reading_order_key": order_key, "parse_controls": controls, "entries": entries}
            save(path, record)
            checkpoint(ctx, cached + [entries])
            newly += 1
            elapsed = time.monotonic() - started
            left = (len(ctx.pages) - len(cached) - 1) * elapsed / newly
            estimate = ("PARSE ETA unavailable: resumed partial page; time a fresh page"
                        if resumed_partial else f"estimated PARSE left={left / 3600:.2f} h")
            print(f"  parsed index PDF {page}; saved={len(cached) + 1}/{len(ctx.pages)}; "
                  f"command elapsed={elapsed / 60:.1f} min; {estimate} "
                  "at this command's pace (classification additional)", flush=True)
        cached.append(record["entries"])
    result = checkpoint(ctx, cached)
    ctx.summary("parse", new_pages=newly, parsed_pages=len(cached), entries=len(result["entries"]),
                complete=result["complete"], **result["reference_counts"])
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
