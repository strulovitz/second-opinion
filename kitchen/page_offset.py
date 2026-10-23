#!/usr/bin/env python3
"""BIBLE Part 3 section 4.6: verify an offset from saved, checked page pairs.

The old majority-vote implementation mistook printed TOC pages for PDF
pages and could accept a false constant offset. This version uses the
completed eyes evidence and refuses ANY disagreeing chapter. It makes no
reader calls and never rebuilds a TOC. One book per invocation:

    .venv/bin/python kitchen/page_offset.py HARRISON-22
    .venv/bin/python kitchen/page_offset.py HARRISON-22 --save

Only page_offset is saved. Chapter-range and image-reference defects are
reported, not silently repaired or marked geography-done.
"""

import argparse
import json
import re
import subprocess
import sys
import unicodedata
from collections import Counter
from pathlib import Path

KITCHEN = Path(__file__).resolve().parent
BOOKS = KITCHEN / "books.json"
LOGS = KITCHEN / "logs"


def require(condition, message):
    if not condition:
        raise ValueError(message)


def positive_integer(value):
    return type(value) is int and value > 0


def key(province, chapter):
    return province, str(chapter.get("number")), chapter["title"]


def flatten(toc):
    return [(p["name"], c) for p in toc["provinces"] for c in p["chapters"]]


def verify_pairs(book, toc, eyes, image_dir):
    """Verify complete coverage and units before deriving a single offset."""
    chapters = flatten(toc)
    require(len(chapters) >= 4, "fewer than four chapters; ask the human")
    require(eyes["_summary"]["book"] == book["book_id"], "wrong evidence book")
    records = eyes["chapters"]
    by_key = {key(r["province"], r): r for r in records}
    toc_keys = [key(p, c) for p, c in chapters]
    require(len(by_key) == len(records), "duplicate eye records")
    require(len(set(toc_keys)) == len(toc_keys), "duplicate TOC chapters")
    require(set(toc_keys) == set(by_key), "TOC and eye chapter coverage differs")
    kinds = {r.get("kind") for r in records}
    require(kinds in ({"printed"}, {"pdf-page"}), "mixed or unknown page units")
    kind = next(iter(kinds))
    offsets, warnings = Counter(), []
    previous_pdf = previous_printed = 0
    for province, chapter in chapters:
        number = chapter.get("number")
        rec = by_key[key(province, chapter)]
        require(rec.get("status") == "ok" and rec.get("opener_confirmed") is True,
                f"ch{number}: unresolved or unconfirmed opener")
        pdf, printed = rec.get("pdf_page"), rec.get("printed")
        require(positive_integer(pdf) and pdf <= book["page_count_images"]
                and positive_integer(printed), f"ch{number}: invalid page pair")
        require((chapter.get("pdf_page"), chapter.get("page_start")) == (pdf, printed),
                f"ch{number}: TOC and eyes disagree")
        require(pdf >= previous_pdf and printed >= previous_printed,
                f"ch{number}: page sequence decreases")
        previous_pdf, previous_printed = pdf, printed
        require(kind != "pdf-page" or printed == pdf,
                f"ch{number}: PDF-page citation contains a printed folio")
        image = f"{pdf:05d}.png"
        require((image_dir / image).is_file(), f"ch{number}: missing evidence {image}")
        if rec.get("image_file") != image:
            # refine_opener() recorded the corrected page in back_walk but
            # retained the original image_file. Accept only explicit saved
            # reader evidence for the corrected page, never a guessed image.
            back = rec.get("refine", {}).get("back_walk", [])
            require(any(r.get("pdf_page") == pdf and r.get("folio") == printed
                        for r in back), f"ch{number}: image does not prove page pair")
            warnings.append(f"ch{number}: stale image_file={rec.get('image_file')}; "
                            f"back_walk proves {image} (file exists)")
        offsets[pdf - printed] += 1
    require(len(offsets) == 1,
            f"no single offset: {dict(sorted(offsets.items()))}; "
            "ask the human about page_offsets (Part 3 section 4.6)")
    require(not book.get("page_offsets"), "per-range offsets already exist; ask the human")
    offset = next(iter(offsets))
    require(book.get("page_offset") in (None, offset), "stored offset disagrees")
    return chapters, kind, offset, warnings


def folded(text):
    text = unicodedata.normalize("NFKD", text).casefold()
    text = "".join(c for c in text if not unicodedata.combining(c))
    return re.sub(r"[\W_]+", " ", text).strip()


def cross_check(pdf, chapters, kind):
    """Check the 1st, 25%, 50%, 75% chapters directly in the current PDF."""
    count = len(chapters)
    samples, folios_seen = [], 0
    for i in (0, count // 4, count // 2, 3 * count // 4):
        _, ch = chapters[i]
        page, printed = ch["pdf_page"], ch["page_start"]
        command = ["pdftotext", "-f", str(page), "-l", str(page), str(pdf), "-"]
        result = subprocess.run(command, capture_output=True, text=True,
                                check=True, timeout=60)
        text = result.stdout
        title = folded(ch["title"])
        title_text = text
        if title and title[:25] not in folded(title_text):
            # HARRISON-22 ch253: default reading order puts "to" BEFORE
            # "253 Approach". -layout preserves the printed heading order.
            layout = subprocess.run([command[0], "-layout", *command[1:]],
                                    capture_output=True, text=True,
                                    check=True, timeout=60)
            title_text = layout.stdout
        require(title and title[:25] in folded(title_text),
                f"ch{ch['number']}: sample PDF page does not contain the title")
        lines = [line.strip() for line in text.splitlines() if line.strip()]
        # ch1/page1: the bare "1" at the top is the CHAPTER number, and
        # the saved reader explicitly saw no folio. Do not call it a folio.
        footer = lines[-3:] if len(lines) > 6 else []
        header = lines[:3] if str(printed) != str(ch["number"]) else []
        folio_seen = str(printed) in header + footer
        folios_seen += folio_seen
        unit = "printed" if kind == "printed" else "PDF-page citation"
        samples.append(f"ch{ch['number']}: PDF {page} -> {unit} {printed}; "
                       f"title found; corner folio {'found' if folio_seen else 'not readable'}")
    require(kind != "printed" or folios_seen > 0,
            "no sampled printed folio readable; ask the human")
    return samples


def range_warnings(book, chapters, offset):
    """Expose the completed TOC writer's range defects without changing data."""
    warnings = []
    index = book.get("index_images")
    for i, (_, ch) in enumerate(chapters):
        end = ch.get("page_end")
        if i + 1 < len(chapters):
            expected = max(ch["page_start"], chapters[i + 1][1]["page_start"] - 1)
        elif index and len(index) == 2 and positive_integer(index[0]):
            expected = index[0] - offset - 1
        else:
            continue
        if end != expected:
            warnings.append(f"ch{ch['number']}: page_end={end}; "
                            f"next chapter/index boundary gives {expected}")
    return warnings


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("book", help="one book ID; no unattended batch mode")
    parser.add_argument("--save", action="store_true", help="save only a verified page_offset")
    args = parser.parse_args(argv)
    try:
        original = BOOKS.read_text()
        books = json.loads(original)
        matches = [b for b in books if b["book_id"] == args.book]
        require(len(matches) == 1, "unknown or duplicate book ID")
        book = matches[0]
        toc = json.loads((LOGS / f"{args.book}-toc.json").read_text())
        eyes = json.loads((LOGS / f"{args.book}-eyes.json").read_text())
        chapters, kind, offset, images = verify_pairs(
            book, toc, eyes, LOGS / "eyes-render" / args.book)
        pdf = KITCHEN / "books" / book["pdf_file"]
        require(pdf.is_file(), "book PDF missing")
        samples = cross_check(pdf, chapters, kind)
        ranges = range_warnings(book, chapters, offset)
        print(f"{args.book}: {len(chapters)}/{len(chapters)} saved pairs verified; "
              f"unit={kind}; page_offset={offset}")
        for sample in samples:
            print(f"  {sample}")
        print(f"Image-reference warnings: {len(images)}; range warnings: {len(ranges)}")
        for warning in images + ranges:
            print(f"  WARNING {warning}")
        if args.save:
            require(book["status"] in ("accepted", "geography-done"),
                    "book acceptance not recorded; cannot save")
            require(BOOKS.read_text() == original, "books.json changed during verification")
            if book.get("page_offset") != offset:
                book["page_offset"] = offset
                BOOKS.write_text(json.dumps(books, indent=1, ensure_ascii=False) + "\n")
                print(f"Saved {args.book}.page_offset={offset}; status unchanged")
            else:
                print(f"{args.book}.page_offset already {offset}; no write")
        else:
            print("Dry run; no files written")
        if images or ranges:
            print("Offset verified; geography readiness still needs the warnings resolved")
        return 0
    except (ValueError, KeyError, TypeError, OSError, subprocess.SubprocessError) as exc:
        print(f"NOT SAVED: {args.book}: {exc}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    sys.exit(main())
