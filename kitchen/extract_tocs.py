"""kitchen/extract_tocs.py -- STEP A2 (BIBLE part 3, section 4.1).

For every accepted book with a located TOC, dump the TOC pages as layout
text to kitchen/logs/<BOOK_ID>-toc.txt, one file per book. Those files are
what the free local READER converts into provinces + chapters (section 4.3).

ONE pdftotext call per book (see the lesson in find_toc.py). Nothing is
guessed: a book with no located TOC is reported, not faked (Law 11).
"""
import json
import subprocess
import sys
from concurrent.futures import ProcessPoolExecutor
from pathlib import Path

KITCHEN = Path(__file__).resolve().parent
BOOKS = KITCHEN / "books"
LOGS = KITCHEN / "logs"


def extract(rec: dict) -> dict:
    bid = rec["book_id"]
    pdf = BOOKS / rec["pdf_file"]
    first, last = rec["toc_images"]
    out = LOGS / f"{bid}-toc.txt"
    p = subprocess.run(
        ["pdftotext", "-f", str(first), "-l", str(last), "-layout", str(pdf), "-"],
        capture_output=True, text=True, timeout=1800)
    out.write_text(p.stdout)
    pages = p.stdout.split("\f")
    chars = sum(len(x) for x in pages)
    return {
        "book_id": bid,
        "images": [first, last],
        "page_count": len(pages) - 1,
        "chars": chars,
        "file": out.name,
    }


def main():
    LOGS.mkdir(exist_ok=True)
    books = [b for b in json.loads((KITCHEN / "books.json").read_text())
             if b["status"] == "candidate"]
    todo = [b for b in books if b["toc_images"]]
    print(f"extracting TOCs for {len(todo)} of {len(books)} books ...", flush=True)
    with ProcessPoolExecutor(max_workers=6) as pool:
        res = list(pool.map(extract, todo))
    (LOGS / "toc_extract.json").write_text(json.dumps(res, indent=1))
    tot = sum(r["chars"] for r in res)
    print(f"done: {len(res)} files, {tot:,} characters of TOC text")
    thin = [r for r in res if r["chars"] < 1500]
    if thin:
        print("\nsuspiciously small TOC dumps:")
        for r in thin:
            print(f"  {r['book_id']:26s} {r['chars']:6d} chars from images {r['images']}")
    missing = [b["book_id"] for b in books if not b["toc_images"]]
    print(f"\nno located TOC ({len(missing)}): {', '.join(missing)}")


if __name__ == "__main__":
    sys.exit(main())