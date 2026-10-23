#!/usr/bin/env python3
"""Read ONE selected chapter opener with the free local reader, then stop.

  python kitchen/toc_observe.py BOOK_ID --number 1 --pdf-page 27
  python kitchen/toc_observe.py BOOK_ID --number 1 --pdf-page 27 --source checked.json

Writes reusable checked-pairs/opener_evidence with PDF and chapter-list
identities. No search, whole-PDF conversion, unattended loop or export write.
"""

import argparse
import hashlib
import json
import subprocess
import sys
from pathlib import Path

from eyes_folio import SYSTEM, parse
from page_offset import flatten, key, positive_integer, require
from toc_evidence import fingerprint, heading_names_chapter, pdf_identity
from toc_reexport import atomic_write

ROOT = Path(__file__).resolve().parents[1]


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("book")
    parser.add_argument("--number", required=True)
    parser.add_argument("--pdf-page", required=True, type=int)
    parser.add_argument("--province", help="required when chapter numbers restart")
    parser.add_argument("--source", type=Path, help="grouped contents proposal instead of current export")
    parser.add_argument("--refresh", action="store_true", help="explicitly repeat a saved observation; previous evidence is retained")
    args = parser.parse_args(argv)
    try:
        from reader import ask
        kitchen, logs = ROOT / "kitchen", ROOT / "kitchen/logs"
        books = json.loads((kitchen / "books.json").read_text())
        book = next(b for b in books if b["book_id"] == args.book)
        toc = json.loads((args.source or logs / f"{args.book}-toc.json").read_text())
        matches = [(p, ch) for p, ch in flatten(toc) if str(ch.get("number")) == args.number
                   and (args.province is None or p == args.province)]
        require(len(matches) == 1, "unknown/ambiguous chapter; provide --province or corrected --source")
        province, chapter = matches[0]
        page = args.pdf_page
        require(positive_integer(page) and page <= book["page_count_images"], "invalid PDF page")
        pdf = kitchen / "books" / book["pdf_file"]
        identity = pdf_identity(pdf)
        out = logs / f"{args.book}-checked-pairs.json"
        base = {"book_id": args.book, "pdf_identity": identity, "toc_hash": fingerprint(toc),
                "chapters": [], "opener_evidence": []}
        original = out.read_text() if out.exists() else None
        data = json.loads(original) if original else base
        require(data["pdf_identity"] == identity and data["toc_hash"] == base["toc_hash"],
                "checked-pairs belong to another PDF/list; archive that file before starting a new list")
        identity_key = key(province, chapter)
        prior = next((r for r in data["chapters"] if key(r["province"], r) == identity_key), None)
        if prior and prior["pdf_page"] == page and not args.refresh:
            image = logs / "eyes-render" / args.book / prior["image_file"]
            require(image.is_file() and hashlib.sha256(image.read_bytes()).hexdigest() == prior["image_sha256"],
                    "saved image changed; use --refresh to obtain new evidence")
            print(f"Saved observation already current: ch{args.number} PDF {page}; no reader call")
            return 0
        image_root = logs / "eyes-render" / args.book
        image = image_root / fingerprint(identity)[:16] / f"{page:05d}.png"
        image.parent.mkdir(parents=True, exist_ok=True)
        if not image.exists() or args.refresh:
            subprocess.run(["pdftoppm", "-f", str(page), "-l", str(page), "-r", "120", "-png", "-singlefile",
                            str(pdf), str(image.with_suffix(""))], check=True, capture_output=True, timeout=90)
        print(f"{args.book} ch{args.number}: showing PDF {page} to the free local reader", flush=True)
        system = SYSTEM + "\nA new chapter may begin at the bottom of a page. Report OPENING only if you see an actual chapter opening, not just its running header."
        raw = ask(system, "What is on this page? Report what you see.", images=[image], max_tokens=600,
                  expect_json=False, retries=2, no_reasoning=True)
        kind, heading, folio = parse(raw)
        require(kind == "OPENING" and heading_names_chapter(heading, args.number, chapter["title"]),
                f"reader did not name this chapter in full: {raw}")
        row = {"province": province, "number": chapter["number"], "title": chapter["title"],
               "status": "ok", "opener_confirmed": True, "pdf_page": page,
               "kind": "printed" if positive_integer(folio) else "pdf-page",
               "printed": folio if positive_integer(folio) else page,
               "printed_observed": positive_integer(folio), "heading": heading, "reader_raw": raw,
               "image_file": str(image.relative_to(image_root)),
               "image_sha256": hashlib.sha256(image.read_bytes()).hexdigest()}
        if prior:
            data.setdefault("observation_history", []).append(prior)
        data["chapters"] = [r for r in data["chapters"] if key(r["province"], r) != identity_key] + [row]
        observation = row | {"kind": "OPENING", "image_file": str(image.relative_to(logs))}
        data["opener_evidence"] = [r for r in data["opener_evidence"] if key(r["province"], r) != identity_key] + [observation]
        require(pdf_identity(pdf) == identity, "PDF changed during reading")
        require((out.read_text() if out.exists() else None) == original, "checked-pairs changed during reading")
        atomic_write(out, json.dumps(data, indent=2, ensure_ascii=False) + "\n")
        print(f"Saved {out}; folio={folio}; observations={len(data['chapters'])}; exports unchanged")
        return 0
    except (ValueError, KeyError, TypeError, OSError, StopIteration, RuntimeError, subprocess.SubprocessError) as exc:
        print(f"NOT SAVED: {args.book}: {exc}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    sys.exit(main())
