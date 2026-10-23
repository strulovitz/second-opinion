#!/usr/bin/env python3
"""BIBLE 3.7.2: selected index-page text and provenance images, resumable."""

import hashlib
import json
import subprocess

from index_common import Context, arguments, cli, fingerprint, lock, require, save
from toc_evidence import pdf_identity


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
            key = fingerprint([ctx.identity, identity, page, layout, columns, "pdftotext-v1"])
            if meta.exists():
                saved = json.loads(meta.read_text())
                require(saved["key"] == key and target.exists() and fingerprint(target.read_text()) == saved["text_hash"],
                        f"stale extraction for PDF {page}; archive the old index cache, do not mix sources")
                image = ctx.image(page)
                require(image.is_file() and hashlib.sha256(image.read_bytes()).hexdigest() == saved["image_hash"], "index evidence image changed/missing")
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
            save(meta, {"key": key, "text_hash": fingerprint(text), "pdf_identity": identity,
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
    args = parser.parse_args(argv)
    ctx = Context(args)
    if args.plan:
        ctx.plan("extract")
        return 0
    ctx.execution_guard()
    require(not ctx.fallback, "use index_fallback.py --fallback for opener-based extraction")
    with lock(ctx.path("index.lock")):
        extract(ctx, args.layout, args.columns)
    return 0


if __name__ == "__main__":
    raise SystemExit(cli(main))
