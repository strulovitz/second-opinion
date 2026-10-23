#!/usr/bin/env python3
"""Repair ONE book's TOC from saved eyes; no reader, rendering or database.

    .venv/bin/python kitchen/toc_reexport.py HARRISON-22          # dry run
    .venv/bin/python kitchen/toc_reexport.py HARRISON-22 --apply  # backup first

Requires complete confirmed eyes evidence. Missing evidence or ambiguous
page units/offsets stop the run; never re-read an already accepted book.
"""

import argparse
import copy
import json
import os
import re
import subprocess
import sys
import tempfile
from datetime import datetime
from pathlib import Path

from eyes_folio import toc_from_evidence
from page_offset import flatten, positive_integer, require, verify_pairs

KITCHEN = Path(__file__).resolve().parent
LOGS = KITCHEN / "logs"


def repair_images(eyes, image_dir):
    """Use an explicit saved backward observation, never just rename a file."""
    changes = []
    for row in eyes["chapters"]:
        pdf, folio = row["pdf_page"], row["printed"]
        name = f"{pdf:05d}.png"
        if row.get("image_file") == name:
            continue
        require((image_dir / name).is_file(), f"missing selected image {name}")
        refine = row.get("refine", {})
        match = next((r for r in refine.get("back_walk", [])
                      if r.get("pdf_page") == pdf and r.get("folio") == folio), None)
        require(match is not None, f"ch{row['number']}: no saved refinement proof")
        require(match.get("kind") in ("BODY", "OPENING") and match.get("heading"),
                f"ch{row['number']}: refinement has no chapter observation")
        old = row["image_file"]
        refine.setdefault("initial_observation", {
            k: row.get(k) for k in ("image_file", "heading", "reader_raw", "printed_from")})
        row.update(image_file=name, heading=match["heading"],
                   reader_raw=match.get("raw"), printed_from="saved-refinement")
        changes.append(f"ch{row['number']}: {old} -> {name}")
    return changes


def index_end(book, pdf, offset):
    """Check only the configured index opener and the preceding page."""
    index = book.get("index_images")
    if not index:
        return None, "index unknown; using median-length fallback"
    require(isinstance(index, list) and len(index) == 2
            and all(positive_integer(p) for p in index)
            and 1 < index[0] <= index[1] <= book["page_count_images"],
            "invalid index_images; ask the human")

    def heading(page):
        result = subprocess.run(
            ["pdftotext", "-layout", "-f", str(page), "-l", str(page), str(pdf), "-"],
            capture_output=True, text=True, check=True, timeout=30)
        lines = [line.strip() for line in result.stdout.splitlines() if line.strip()]
        return any(re.fullmatch(r"(?:Subject\s+)?Index", line, re.I)
                   for line in lines[:6])

    require(heading(index[0]), "configured index opener not confirmed; ask the human")
    require(not heading(index[0] - 1), "previous page is already index; ask the human")
    end = index[0] - offset - 1
    return end, f"index starts at PDF {index[0]}; final citation page {end}"


def atomic_write(path, payload):
    temporary = None
    try:
        with tempfile.NamedTemporaryFile(dir=path.parent, prefix=f".{path.name}.",
                                         mode="w", delete=False) as stream:
            temporary = Path(stream.name)
            stream.write(payload)
            stream.flush()
            os.fsync(stream.fileno())
        temporary.replace(path)
    finally:
        if temporary is not None:
            temporary.unlink(missing_ok=True)


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("book", help="one book ID, then stop and report")
    parser.add_argument("--apply", action="store_true", help="backup and save verified changes")
    args = parser.parse_args(argv)
    try:
        paths = {name: LOGS / f"{args.book}-{name}.json"
                 for name in ("eyes", "toc", "vis-toc")}
        books_path = KITCHEN / "books.json"
        originals = {p: p.read_text() for p in [books_path, *paths.values()]}
        matches = [b for b in json.loads(originals[books_path]) if b["book_id"] == args.book]
        require(len(matches) == 1, "unknown or duplicate book ID")
        book = matches[0]
        eyes = json.loads(originals[paths["eyes"]])
        source = json.loads(originals[paths["vis-toc"]])
        old_toc = json.loads(originals[paths["toc"]])
        require(eyes["_summary"]["unresolved"] == 0, "unresolved eyes; stop")
        require(all(r.get("status") == "ok" for r in eyes["chapters"]), "unfinished eyes; stop")
        provisional = toc_from_evidence(source, eyes["chapters"], require_complete=True)
        image_dir = LOGS / "eyes-render" / args.book
        _, kind, offset, _ = verify_pairs(book, provisional, eyes, image_dir)
        require(len(flatten(old_toc)) == len(flatten(provisional)), "chapter count changed; stop")
        require([(p, c["number"], c["title"], c["page_start"], c["pdf_page"])
                 for p, c in flatten(old_toc)] ==
                [(p, c["number"], c["title"], c["page_start"], c["pdf_page"])
                 for p, c in flatten(provisional)], "accepted openers/order changed; stop")
        end, boundary = index_end(book, KITCHEN / "books" / book["pdf_file"], offset)
        toc = toc_from_evidence(source, eyes["chapters"], end, require_complete=True)
        updated = copy.deepcopy(eyes)
        images = repair_images(updated, image_dir)
        verify_pairs(book, toc, updated, image_dir)
        ranges = [f"ch{a['number']}: {a['page_end']} -> {b['page_end']}"
                  for (_, a), (_, b) in zip(flatten(old_toc), flatten(toc))
                  if a["page_end"] != b["page_end"]]
        print(f"{args.book}: {len(toc['provinces'])} provinces; {len(flatten(toc))} chapters; "
              f"unit={kind}; offset={offset}")
        print(boundary)
        print(f"Chapter ends changed: {len(ranges)}; selected images repaired: {len(images)}")
        for change in ranges + images:
            print(f"  {change}")
        payloads = {paths["toc"]: json.dumps(toc, indent=1, ensure_ascii=False)}
        if updated != eyes:
            payloads[paths["eyes"]] = json.dumps(updated, indent=1)
        changed = {p: payload for p, payload in payloads.items() if payload != originals[p]}
        if not args.apply:
            print("Dry run; no files written; no reader calls")
            return 0
        require(all(p.read_text() == text for p, text in originals.items()),
                "inputs changed during verification; stop")
        if not changed:
            print("Already current; no files written")
            return 0
        backup = LOGS / "toc-reexport-backups" / args.book / datetime.now().strftime("%Y%m%dT%H%M%S%f")
        backup.mkdir(parents=True)
        for path, text in originals.items():
            (backup / path.name).write_text(text)
        # Each replacement is atomic. If interrupted between files, rerunning
        # is safe: accepted openers never change and all inputs are rechecked.
        for path, payload in changed.items():
            atomic_write(path, payload)
        print(f"Backup: {backup}")
        print(f"Saved {len(changed)} files; books.json/status unchanged; no reader calls")
        return 0
    except (ValueError, KeyError, TypeError, OSError, subprocess.SubprocessError) as exc:
        print(f"NOT SAVED: {args.book}: {exc}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    sys.exit(main())
