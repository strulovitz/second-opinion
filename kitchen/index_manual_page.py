#!/usr/bin/env python3
"""Save one hand-read index page record with normal grounding and page keys.

The operator reads the page image and supplies the entries JSON. This tool
does not read the image and does not call the local reader; it recomputes the
same page key/controls used by index_parse.py, grounds every headword,
subentry and reference against the extracted page text, and writes the
ordinary page record. reader_model names the operator hand-read so the
provenance is visible.
"""
from argparse import ArgumentParser
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

from index_common import Context, arguments, fingerprint, reader_access
from index_fragments import FORMAT
from index_order import reading_text
from index_pages import ground_entries
from index_parse import OCR
from index_prompts import PARSE
from index_schema import PARSE_CONTROLS, check_shape


def main():
    parser = ArgumentParser(description=__doc__)
    parser.add_argument("book")
    parser.add_argument("page", type=int)
    parser.add_argument("entries", type=Path, help="JSON list of page entries")
    parser.add_argument("--force", action="store_true", help="replace an existing page record")
    parser.add_argument("--books", type=Path, default=Path(__file__).resolve().parents[1] / "kitchen/books.json")
    parser.add_argument("--logs", type=Path, default=Path(__file__).resolve().parents[1] / "kitchen/logs")
    parser.add_argument("--geography", type=Path, default=Path(__file__).resolve().parents[1] / "data/export/geography/geography.json")
    args = parser.parse_args()
    ctx = Context(arguments("manual page").parse_args(
        [args.book, "--books", str(args.books), "--logs", str(args.logs), "--geography", str(args.geography)]))
    out = ctx.path(f"index-{args.page}.json")
    if out.exists() and not args.force:
        raise SystemExit(f"{out} exists; use --force only after preserving the old record")
    entries = json.loads(args.entries.read_text())
    source = json.loads(ctx.path(f"index-{args.page}-source.json").read_text())
    original = ctx.path(f"index-{args.page}.txt").read_text()
    text, order_key = reading_text(ctx, args.page, source, original)
    needs_ocr = len(text.strip()) < 30
    _, model, vision_model = reader_access()
    inputs = [source, ctx.identity, PARSE, OCR if needs_ocr else None, model,
              vision_model if needs_ocr else None]
    controls = {"reader": PARSE_CONTROLS, "fragments": FORMAT, "max_tokens": 12000}
    key = fingerprint(["index-parse-v4-structured-fragments", *inputs, order_key, controls])
    check_shape({"entries": entries})
    grounded = ground_entries({"entries": entries}, text, args.page, str(ctx.image(args.page)))
    record = {"key": key, "reader_model": "operator hand-read (vision, not the local reader)",
              "output_format": "json_schema", "reading_order_key": order_key,
              "parse_controls": controls, "entries": grounded}
    out.write_text(json.dumps(record, ensure_ascii=False, indent=1))
    print(f"saved {out}; entries={len(grounded)}; key={key}")


if __name__ == "__main__":
    main()
