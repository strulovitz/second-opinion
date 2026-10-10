"""kitchen/locate_with_reader.py -- let the READER find the Table of Contents.

Two regex-based locators were tried on 2026-10-10 and both failed on real
books: scoring pages by "a title followed by a number" matches numbered
REFERENCE LISTS, and excluding impostors still lands on body pages because
many textbooks print their contents mixed with chapter openings. Regex
cannot tell a contents page from a reference list reliably.

The local READER can, and it is cheap: this script gives the model one line
per page -- the image number and the first 90 characters of that page -- and
asks it which of those images belong to the Table of Contents. One call per
book, small input, no generation of chapters yet.

Writes kitchen/logs/reader_locate.json.
"""
import json
import re
import sys
from concurrent.futures import ProcessPoolExecutor
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from find_toc import pages_text  # noqa: E402
from reader import ask  # noqa: E402

KITCHEN = Path(__file__).resolve().parent
BOOKS = KITCHEN / "books"
LOGS = KITCHEN / "logs"
LIMIT = 200

SYSTEM = """You are given a numbered list of pages from the front of a medical textbook. Each line is "page_number | first words of that page".

Find the Table of Contents of the book. Rules:
- The Table of Contents is the block of pages that lists chapter or section titles together with their starting page numbers.
- It is NOT a contributor list, a dedication, a preface, a reference list, a chapter's body text, or an index.
- Some books print the contents together with the first chapter's opening pages; include only the pages that actually list titles with page numbers.
- Some books have a short contents listing the parts, then a longer detailed contents listing every chapter. Prefer the DETAILED one: it has the most lines of the form "chapter title ... page".

Answer with exactly three lines and nothing else:
FIRST=<first page number>
LAST=<last page number>
CONF=<one of: high, medium, low>"""


def build(rec):
    pdf = BOOKS / rec["pdf_file"]
    pages = pages_text(pdf, 1, min(LIMIT, rec["page_count_images"]))
    lines = []
    for n in sorted(pages):
        head = " ".join(pages[n].split())[:90]
        lines.append(f"{n} | {head}")
    return "\n".join(lines)


def work(rec):
    bid = rec["book_id"]
    try:
        ans = ask(SYSTEM, build(rec), max_tokens=200, expect_json=False,
                  retries=2, timeout=1800)
        first = re.search(r"FIRST\s*=\s*(\d+)", ans)
        last = re.search(r"LAST\s*=\s*(\d+)", ans)
        conf = re.search(r"CONF\s*=\s*(\w+)", ans)
        got = [int(first.group(1)), int(last.group(1))] if first and last else None
    except Exception as exc:  # noqa: BLE001 - recorded, never hidden
        got, conf, ans = None, None, str(exc)
    return {"book_id": bid, "toc_images": got,
            "confidence": conf.group(1) if conf else None,
            "old": rec["toc_images"]}


def main():
    wanted = sys.argv[1:] or None
    books = [b for b in json.loads((KITCHEN / "books.json").read_text())
             if b["status"] == "candidate"]
    if wanted:
        books = [b for b in books if b["book_id"] in wanted]
    print(f"asking the reader to locate the contents of {len(books)} books ...",
          flush=True)
    with ProcessPoolExecutor(max_workers=2) as pool:
        res = list(pool.map(work, books))
    (LOGS / "reader_locate.json").write_text(
        json.dumps(res, indent=1, ensure_ascii=False))
    for r in res:
        print(f"  {r['book_id']:24s} {str(r['old']):10s} -> "
              f"{str(r['toc_images']):10s} confidence={r['confidence']}")


if __name__ == "__main__":
    main()