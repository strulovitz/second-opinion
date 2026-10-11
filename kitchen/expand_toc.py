"""kitchen/expand_toc.py -- widen the located Table-of-Contents page range.

WHY (measured 2026-10-11, see PROGRESS.md):

The ranges found by vis_locate.py were too SMALL. GUYTON-2026 was given
[14, 14] -- a single page -- so units I to V were never read and the book
came out with 11 chapters starting at printed page 447. In total 8 of the
22 "finished" books had lost part or all of their contents, and 2 had page
numbers that were never printed in the book at all.

A contents page is recognisable from the TEXT LAYER alone: it holds many
"words ... number" fragments per page, while an ordinary text page does
not. So the range can be widened with no model calls at all -- free, and
seconds per book.

For every book that already has a located range:
  * dump a generous window starting at the located start;
  * score each page by how many title-then-number fragments it holds;
  * keep the CONTIGUOUS run of pages that starts at (or just after) the
    located start and stops after 2 consecutive pages fall below the
    threshold;
  * write the widened range to books.json, keeping the original under
    "toc_images_found" so nothing is lost.

The old range is kept if widening finds nothing, and every change is
printed, so the human can see exactly what moved (Law 11).
"""
import json
import re
import subprocess
import sys
from concurrent.futures import ProcessPoolExecutor
from pathlib import Path

KITCHEN = Path(__file__).resolve().parent
BOOKS = KITCHEN / "books"
WINDOW = 60          # how many pages after the located start to look at
THRESHOLD = 8        # title-then-number fragments that make a page a TOC page
MAX_TAIL = 2         # stop after this many consecutive non-TOC pages
VOL2_GAP = 26        # a second contents block (a second volume) may start
VOL2_PEAK = 15       # ...but only if that block scores at least this high
INVISIBLE = re.compile("[­‎‏\xa0]+")
FRAGMENT = re.compile(
    r"[A-Za-z][A-Za-z0-9 ,'\-\(\)/&:\.]{2,70}?[,\.]?\s*(?:\.{2,})?\s\d{1,4}\b")


def score(page):
    return len(FRAGMENT.findall(INVISIBLE.sub(" ", page)))


def expand(rec):
    bid = rec["book_id"]
    pdf = BOOKS / rec["pdf_file"]
    first = rec["toc_images"][0]
    last = first + WINDOW
    p = subprocess.run(
        ["pdftotext", "-f", str(first), "-l", str(last), "-layout", str(pdf), "-"],
        capture_output=True, text=True, timeout=1800)
    pages = p.stdout.split("\f")[:-1]
    scores = [score(x) for x in pages]

    # walk forward from the first page that looks like a contents page
    start_idx = next((i for i, s in enumerate(scores) if s >= THRESHOLD), None)
    if start_idx is None:
        return {"book_id": bid, "changed": False,
                "note": f"no page in {first}-{last} scores >= {THRESHOLD}",
                "scores": scores}
    run_start = first + start_idx
    before = list(rec["toc_images"])
    end_idx, miss = start_idx, 0
    for i in range(start_idx + 1, len(scores)):
        if scores[i] >= THRESHOLD:
            end_idx, miss = i, 0
        else:
            miss += 1
            if miss >= MAX_TAIL:
                break
    run_end = first + end_idx
    ranges = [[min(before[0], run_start), run_end]]

    # a second contents block inside the window is the second VOLUME's
    # contents (CAMPBELL-2020 and GRAY-2020 both have one and it was lost)
    for i in range(end_idx + 1, min(end_idx + VOL2_GAP, len(scores))):
        if scores[i] >= VOL2_PEAK:
            e2, m2 = i, 0
            for j in range(i + 1, min(i + VOL2_GAP, len(scores))):
                if scores[j] >= THRESHOLD:
                    e2, m2 = j, 0
                else:
                    m2 += 1
                    if m2 >= MAX_TAIL:
                        break
            ranges.append([first + i, first + e2])
            break

    after = [min(r[0] for r in ranges), max(r[1] for r in ranges)]
    return {"book_id": bid, "changed": after != before,
            "was": before, "now": after, "blocks": ranges,
            "peak": max(scores[start_idx:end_idx + 1] or [0]),
            "first_scoring_page": run_start}


def main():
    books = json.loads((KITCHEN / "books.json").read_text())
    todo = [b for b in books if b.get("toc_images")]
    print(f"widening the TOC range of {len(todo)} books "
          f"(window +{WINDOW} pages, threshold {THRESHOLD}) ...", flush=True)
    with ProcessPoolExecutor(max_workers=6) as pool:
        res = list(pool.map(expand, todo))
    by = {r["book_id"]: r for r in res}
    changed = 0
    for b in books:
        r = by.get(b["book_id"])
        if not r or not r["changed"]:
            if r:
                print(f"  {b['book_id']:26s} unchanged {b['toc_images']}"
                      f"  ({r.get('note', '')})", flush=True)
            continue
        b["toc_images_found"] = b["toc_images"]
        b["toc_images"] = r["now"]
        b["toc_blocks"] = r["blocks"]
        changed += 1
        print(f"  {b['book_id']:26s} {r['was']} -> {r['now']}  "
              f"blocks={r['blocks']} peak={r['peak']}", flush=True)
    (KITCHEN / "books.json").write_text(
        json.dumps(books, indent=1, ensure_ascii=False))
    print(f"\n{changed} ranges widened, books.json written", flush=True)


if __name__ == "__main__":
    sys.exit(main())