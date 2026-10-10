"""kitchen/find_toc.py -- STEP A2 prep (BIBLE part 3, section 2.5).

Finds, for every candidate book:
  toc_images   : the image numbers of the Table of Contents pages
  index_images : the image numbers of the back-of-book Index pages

Method (section 2.5): score the first 60 images for "looks like a Table of
Contents" and the last 300 images for "looks like an Index", then take the
longest contiguous run of pages that scores.

Two lessons are baked in here:
  * ONE pdftotext call per range. Poppler separates pages with a form feed
    (\x0c), so pages are recovered by splitting. Calling pdftotext once per
    page re-parses the whole PDF each time and takes hours.
  * Scoring, not strict line matching. Index pages are printed in THREE
    COLUMNS, so a physical text line can hold three unrelated entries and
    never "ends with a page number". Counting fragments works; anchoring to
    end-of-line does not.

Writes kitchen/logs/locate.json. A book whose TOC or index cannot be found
is reported, never faked (Law 11).
"""
import json
import re
import subprocess
import sys
from concurrent.futures import ProcessPoolExecutor
from pathlib import Path

KITCHEN = Path(__file__).resolve().parent
BOOKS = KITCHEN / "books"
LOGS = KITCHEN / "logs"

CONTENTS_HEAD = re.compile(r"\b(table\s+of\s+contents|contents)\b", re.I)
INDEX_HEAD = re.compile(r"^\s*(index|subject index|general index)\s*$", re.I | re.M)

# a Table of Contents fragment: a title-ish string followed by a page number,
# with or without dot leaders. Multi-column TOC pages interleave columns, so
# the number is often in the MIDDLE of the physical line -- it must never be
# anchored to the end of the line (that was the first attempt, and it scored
# ZERO on every real TOC page).
TOC_FRAG = re.compile(
    r"[A-Za-z][A-Za-z0-9 ,'\-\(\)/&:\.]{2,70}?[,\.]?\s*(?:\.{2,})?\s(\d{1,4})\b")
# an Index fragment: "Hypercalcemia, 3277" (letters, then comma, then digits)
INDEX_FRAG = re.compile(r"[A-Za-z][A-Za-z0-9 '\-\(\)/&\.]{1,45},\s*\d{1,5}")


def pages_text(pdf: Path, first: int, last: int) -> dict:
    """Return {image_number: text} for the inclusive range, in one call."""
    last = min(last, first + 6000)
    try:
        p = subprocess.run(
            ["pdftotext", "-f", str(first), "-l", str(last), "-layout", str(pdf), "-"],
            capture_output=True, text=True, timeout=1200)
        chunks = p.stdout.split("\f")
    except Exception:
        chunks = []
    return {first + i: c for i, c in enumerate(chunks) if first + i <= last}


def toc_score(txt: str) -> int:
    if not txt:
        return 0
    lines = txt.splitlines()
    n = sum(1 for ln in lines if TOC_FRAG.search(ln))
    return n + (3 if CONTENTS_HEAD.search(txt) else 0)


def index_score(txt: str) -> int:
    if not txt:
        return 0
    n = len(INDEX_FRAG.findall(txt))
    return n + (3 if INDEX_HEAD.search(txt) else 0)


def longest_run(pages: dict, score_fn, threshold: int, allow_gap: int = 1):
    """Longest contiguous run of pages scoring >= threshold."""
    scored = {n: score_fn(t) for n, t in pages.items()}
    best = []
    run = []
    for n in sorted(scored):
        if scored[n] >= threshold:
            run.append(n)
        else:
            if len(run) > len(best):
                best = run
            run = [] if not run else run[-allow_gap:]
            if not run:
                run = []
            else:
                run = []
    if len(run) > len(best):
        best = run
    return (best[0], best[-1]) if best else (None, None)


def find_toc(pages: dict):
    """The TOC is the run of TOC-looking pages that has a 'Contents' heading."""
    runs, cur = [], []
    for n in sorted(pages):
        if toc_score(pages[n]) >= 15:
            cur.append(n)
        else:
            if cur:
                runs.append(cur)
            cur = []
    if cur:
        runs.append(cur)
    if not runs:
        return (None, None)
    headed = [r for r in runs if any(CONTENTS_HEAD.search(pages[n]) for n in r)]
    best = max(headed or runs, key=len)
    return (best[0], best[-1])


def find_index(pages: dict):
    return longest_run(pages, index_score, 25)


def work(rec: dict) -> dict:
    bid = rec["book_id"]
    pdf = BOOKS / rec["pdf_file"]
    n = rec["page_count_images"]
    head = pages_text(pdf, 1, min(80, n))
    toc = find_toc(head)
    tail = pages_text(pdf, max(1, n - 400), n)
    idx = find_index(tail)
    return {
        "book_id": bid,
        "pdf_file": rec["pdf_file"],
        "pages": n,
        "toc_images": list(toc) if toc[0] else None,
        "index_images": list(idx) if idx[0] else None,
    }


def main():
    LOGS.mkdir(exist_ok=True)
    books = [b for b in json.loads((KITCHEN / "books.json").read_text())
             if b["status"] == "candidate"]
    print(f"locating TOC and Index for {len(books)} books ...", flush=True)
    with ProcessPoolExecutor(max_workers=6) as pool:
        results = list(pool.map(work, books))
    (LOGS / "locate.json").write_text(json.dumps(results, indent=1, ensure_ascii=False))
    print(f"TOC found   for {sum(1 for r in results if r['toc_images'])}/{len(results)}")
    print(f"Index found for {sum(1 for r in results if r['index_images'])}/{len(results)}")
    print("\n--- problems ---")
    bad = 0
    for r in results:
        if not r["toc_images"] or not r["index_images"]:
            bad += 1
            print(f"  {r['book_id']:26s} toc={r['toc_images']} index={r['index_images']}")
    if not bad:
        print("  none")


if __name__ == "__main__":
    sys.exit(main())