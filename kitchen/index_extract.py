#!/usr/bin/env python3
"""BIBLE 3.7.2: selected index-page text and provenance images, resumable."""

import hashlib
import json
import subprocess
from pathlib import Path

from index_common import Context, arguments, cli, fingerprint, lock, require, save
from toc_evidence import pdf_identity


def extraction_key(identity, page, layout=False, columns=False):
    """Text extraction depends on the PDF/page/recipe, not globe coordinates."""
    return fingerprint(["index-extract-v2", identity, page, layout, columns, "pdftotext-v1"])


def source_evidence(ctx, page, identity):
    saved = json.loads(ctx.path(f"index-{page}-source.json").read_text())
    target, image = ctx.path(f"index-{page}.txt"), ctx.image(page)
    require(saved["pdf_identity"] == identity, f"changed PDF for index page {page}")
    require(saved["source_index_pdf"] == page and saved["image_file"] == str(image),
            "index evidence page/image path changed")
    require(target.is_file() and fingerprint(target.read_text()) == saved["text_hash"],
            "index evidence text changed/missing")
    require(image.is_file() and hashlib.sha256(image.read_bytes()).hexdigest() == saved["image_hash"],
            "index evidence image changed/missing")
    return saved


def cached_source(ctx, page, identity, layout=False, columns=False):
    saved = source_evidence(ctx, page, identity)
    key = extraction_key(identity, page, layout, columns)
    if saved.get("format") == "index-extract-v2":
        valid = saved["key"] == key
    else:
        legacy = lambda context: fingerprint([context, identity, page, layout, columns, "pdftotext-v1"])
        valid = "format" not in saved and saved["key"] == legacy(ctx.identity)
        check_path = ctx.path(f"index-{page}-source-check.json")
        if not valid and "format" not in saved and check_path.exists():
            check = json.loads(check_path.read_text())
            valid = (check.get("format") == "index-extraction-reconciliation-v1"
                     and check.get("key") == key and check.get("source_hash") == fingerprint(saved)
                     and saved["key"] == legacy(check.get("legacy_context_identity")))
    require(valid, f"stale extraction for PDF {page}; reconcile a proven old geography receipt or archive the old index cache, do not mix sources")
    return saved


def reconcile(ctx, page, previous_geography, layout=False, columns=False):
    """Add proof for a legacy receipt; never rewrite it or any reader cache."""
    require(page in ctx.pages, "reconciliation page is outside the configured index")
    identity = pdf_identity(ctx.pdf)
    saved = source_evidence(ctx, page, identity)
    require("format" not in saved, "only legacy extraction receipts need reconciliation")
    geography = json.loads(previous_geography.read_text())
    legacy_context = fingerprint({"book": ctx.book, "geography": geography})
    require(saved["key"] == fingerprint([legacy_context, identity, page, layout, columns, "pdftotext-v1"]),
            "previous geography does not reproduce the original extraction key")
    check = {"format": "index-extraction-reconciliation-v1",
             "key": extraction_key(identity, page, layout, columns),
             "source_hash": fingerprint(saved), "legacy_context_identity": legacy_context,
             "previous_geography_hash": fingerprint(geography)}
    path = ctx.path(f"index-{page}-source-check.json")
    require(pdf_identity(ctx.pdf) == identity, "PDF changed during reconciliation")
    if path.exists():
        require(json.loads(path.read_text()) == check, "existing reconciliation differs; preserve it for review")
    else:
        save(path, check)
    cached_source(ctx, page, identity, layout, columns)
    print(f"Reconciled index PDF {page}; original receipt/text/image/reader caches unchanged; proof: {path}")


def extract(ctx, layout=False, columns=False):
    identity = pdf_identity(ctx.pdf)
    count, skipped = 0, 0
    reader = None
    try:
        if columns:
            from pypdf import PdfReader
            reader = PdfReader(str(ctx.pdf))
        for page in ctx.pages:
            target, meta = ctx.path(f"index-{page}.txt"), ctx.path(f"index-{page}-source.json")
            pending = ctx.path(f"index-{page}-pending.json")
            key = extraction_key(identity, page, layout, columns)
            if meta.exists():
                cached_source(ctx, page, identity, layout, columns)
                skipped += 1
                continue
            require(not target.exists() or (pending.exists() and json.loads(pending.read_text())["key"] == key),
                    f"unidentified legacy text {target}; archive it before extracting")
            save(pending, {"key": key})
            command = ["pdftotext", "-f", str(page), "-l", str(page)]
            if layout or columns:
                command.append("-layout")
            if columns:
                box = reader.pages[page - 1].mediabox
                half, height = float(box.width) / 2, float(box.height)
                text = "\n".join(subprocess.run(command + ["-x", str(x), "-y", "0", "-W", str(half), "-H", str(height), str(ctx.pdf), "-"],
                                               capture_output=True, text=True, check=True, timeout=60).stdout for x in (0, half))
            else:
                text = subprocess.run(command + [str(ctx.pdf), "-"], capture_output=True, text=True, check=True, timeout=60).stdout
            image = ctx.image(page)
            image.parent.mkdir(parents=True, exist_ok=True)
            if not image.exists():
                subprocess.run(["pdftoppm", "-f", str(page), "-l", str(page), "-r", "150", "-png", "-singlefile",
                                str(ctx.pdf), str(image.with_suffix(""))], capture_output=True, check=True, timeout=90)
            require(pdf_identity(ctx.pdf) == identity, "PDF changed during extraction")
            from toc_reexport import atomic_write
            atomic_write(target, text)
            save(meta, {"format": "index-extract-v2", "key": key, "text_hash": fingerprint(text), "pdf_identity": identity,
                        "source_index_pdf": page, "image_file": str(image),
                        "image_hash": hashlib.sha256(image.read_bytes()).hexdigest()})
            pending.unlink(missing_ok=True)
            count += 1
            print(f"  extracted index PDF {page}", flush=True)
            if ctx.args.limit and count >= ctx.args.limit:
                break
    finally:
        if reader:
            reader.close()
    ctx.summary("extract", new_pages=count, cached_pages=skipped, expected_pages=len(ctx.pages))


def main(argv=None):
    parser = arguments(__doc__)
    parser.add_argument("--layout", action="store_true")
    parser.add_argument("--columns", action="store_true", help="layout with left-column then right-column crops")
    parser.add_argument("--reconcile-page", type=int, help="verify ONE legacy receipt without extraction/model calls")
    parser.add_argument("--previous-geography", type=Path, help="saved geography that must reproduce the legacy key exactly")
    args = parser.parse_args(argv)
    require((args.reconcile_page is None) == (args.previous_geography is None),
            "--reconcile-page and --previous-geography must be supplied together")
    ctx = Context(args)
    if args.plan:
        ctx.plan("extract")
        return 0
    ctx.execution_guard()
    require(not ctx.fallback, "use index_fallback.py --fallback for opener-based extraction")
    with lock(ctx.path("index.lock")):
        if args.reconcile_page is not None:
            reconcile(ctx, args.reconcile_page, args.previous_geography, args.layout, args.columns)
        else:
            extract(ctx, args.layout, args.columns)
    return 0


if __name__ == "__main__":
    raise SystemExit(cli(main))
