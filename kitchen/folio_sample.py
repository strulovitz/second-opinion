#!/usr/bin/env python3
"""kitchen/folio_sample.py -- INDEPENDENT check of page_folio.py on a sample.

page_folio.py reads the printed folio out of the PDF TEXT layer. This script
does not trust that at all: it renders the page to a PICTURE and lets the free
local READER (Qwen, TIER FREE -- Law 14) look at it the way a human does, and
then compares the two answers chapter by chapter.

For every sampled chapter it asks TWO questions, because Law 2 needs both:
  1. is this really the page where the chapter starts?   (the image)
  2. what number does the book PRINT in the corner?      (the folio)
A chapter whose picture disagrees with the script is reported as DISAGREE and
must be looked at by the manager (or the human) before that book is trusted.

    python kitchen/folio_sample.py HARRISON-22 --n 12
    python kitchen/folio_sample.py HARRISON-22 --n 12 --seed 3
    python kitchen/folio_sample.py HARRISON-22 --n 12 --eyes   # no model, just
                                          # render the pages for a human to see

Writes kitchen/logs/<BOOK_ID>-folio-sample.json.
Zero bytes are written to any geography file.
"""

import argparse
import json
import random
import subprocess
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import page_folio  # noqa: E402
from reader import ask  # noqa: E402

ROOT = Path(__file__).resolve().parent.parent
KITCHEN = ROOT / "kitchen"
LOGS = KITCHEN / "logs"
RENDER_DIR = LOGS / "folio-render"

SYSTEM = (
    "You are checking one page of a scanned medical textbook.\n"
    "Answer with EXACTLY two lines and nothing else:\n"
    "OPENER: YES   (if the chapter named below visibly BEGINS on this page,\n"
    "               i.e. its chapter number and title appear as a heading)\n"
    "OPENER: NO    (otherwise)\n"
    "FOLIO: <the printed page number>   (the digits the book prints in a\n"
    "               corner, in the header or the footer -- NOT the chapter\n"
    "               number, NOT a table or figure number)\n"
    "FOLIO: NONE   (if the page prints no page number at all)\n"
    "Work through the whole page. Check all four corners and both margins.\n"
    "Do not stop early."
)


def render(pdf, page, dpi=120):
    RENDER_DIR.mkdir(parents=True, exist_ok=True)
    out = RENDER_DIR / f"{page:05d}"
    png = out.with_suffix(".png")
    if png.exists():
        return png
    subprocess.run(["pdftoppm", "-f", str(page), "-l", str(page), "-r", str(dpi),
                    "-png", "-singlefile", str(pdf), str(out)],
                   check=True, capture_output=True)
    return png


def parse(ans):
    opener = folio = None
    for line in ans.splitlines():
        s = line.strip()
        if s.upper().startswith("OPENER:"):
            opener = "YES" in s.upper()
        elif s.upper().startswith("FOLIO:"):
            tail = s.split(":", 1)[1].strip()
            digits = "".join(ch for ch in tail if ch.isdigit())
            folio = int(digits) if digits and tail[:1].isdigit() else None
            if digits and not tail[:1].isdigit():
                folio = None
    return opener, folio


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("book")
    ap.add_argument("--n", type=int, default=12)
    ap.add_argument("--seed", type=int, default=0)
    ap.add_argument("--eyes", action="store_true",
                    help="only render the pages, ask no model")
    ap.add_argument("--keep", action="store_true",
                    help="also keep pages the script was unsure about")
    args = ap.parse_args()

    doc = json.loads((LOGS / f"{args.book}-folio.json").read_text())
    rows = [r for r in doc["chapters"]
            if r["image"] and r["printed"] is not None
            and (args.keep or r["check"] == "ok")]
    if not rows:
        sys.exit(f"{args.book}: nothing resolved to sample from")

    random.seed(args.seed)
    sample = random.sample(rows, min(args.n, len(rows)))

    books = {b["book_id"]: b["pdf_file"]
             for b in json.loads((KITCHEN / "books.json").read_text())}
    pdf = KITCHEN / "books" / books[args.book]

    results, bad = [], 0
    for r in sample:
        png = render(pdf, r["image"])
        item = {"number": r["number"], "title": r["title"],
                "image": r["image"], "printed": r["printed"],
                "image_file": png.name}
        if not args.eyes:
            msg = (f"PDF page {r['image']} of {args.book}. Chapter "
                   f"{r['number']} \"{r['title']}\" is supposed to START on "
                   f"this page, and the book is supposed to PRINT "
                   f"{r['printed']} in its corner.")
            try:
                ans = ask(SYSTEM, msg, images=[png], max_tokens=800,
                          expect_json=False, retries=2, no_reasoning=True)
            except Exception as exc:                     # noqa: BLE001
                item.update(reader_error=str(exc))
                results.append(item)
                continue
            opener, folio = parse(ans)
            item.update(reader_opener=opener, reader_folio=folio,
                        reader_raw=ans.strip()[:400])
            item["folio_ok"] = (folio == r["printed"])
            item["opener_ok"] = bool(opener)
            if not (item["folio_ok"] and item["opener_ok"]):
                bad += 1
        results.append(item)
        mark = "   " if args.eyes else ("ok " if item.get("folio_ok")
                                        and item.get("opener_ok") else "XX  ")
        print(f"{mark}ch{r['number']:>5s} pdf {r['image']:5d} -> printed "
              f"{r['printed']:5d}  {r['title'][:40]}", flush=True)
        if not args.eyes and not (item["folio_ok"] and item["opener_ok"]):
            print(f"      reader says: opener={item.get('reader_opener')} "
                  f"folio={item.get('reader_folio')}  | "
                  f"{item.get('reader_raw','')[:160]!r}", flush=True)

    out = {"book": args.book, "n": len(results), "seed": args.seed,
           "disagreements": bad, "results": results}
    (LOGS / f"{args.book}-folio-sample.json").write_text(json.dumps(out, indent=1))
    if args.eyes:
        print(f"\n{len(results)} pages rendered in {RENDER_DIR} -- look at them "
              f"yourself.")
    else:
        print(f"\n{args.book}: {len(results) - bad}/{len(results)} sampled "
              f"chapters agree with the reader; {bad} disagree.")
        print(f"detail: {LOGS / (args.book + '-folio-sample.json')}")
    sys.exit(1 if bad else 0)


if __name__ == "__main__":
    main()
