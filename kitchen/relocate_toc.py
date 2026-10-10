"""kitchen/relocate_toc.py -- fix the Tables of Contents that A2 located wrong.

Measured 2026-10-10. The first locator (kitchen/find_toc.py) scored pages by
"a title-ish string followed by a number", which also matches NUMBERED
REFERENCE LISTS ("143. Moore MW, Klein RD, ...") and contributor pages. It
therefore sent 14 books to the reader as if they were Tables of Contents and
got 0-2 chapters from them:

  BRADDOM-6 [58,61]      contents mixed with chapter body text
  BRAUNWALD-12 [40,49]   body text
  BRENNER-11 [64,79]     contents, then the reference list
  GREEN-HAND-2021 [24,27]  contents mixed with body text
  MANDELL-9 [50,54]      body text
  MIDDLETON-2019 [32,36] contents mixed with body text
  NELSON-2024 [5,21]     Contributors
  ROCKWOOD-10 [67,71]    References
  ROSEN-2022 [30,33]     contents mixed with body text
  STAHL-2024 [66,67]     a drug monograph
  WILLIAMS-ENDO-2024 [56,59]  References
  WILLIAMS-OBSTETRICS-26 [45,48]  body text
  YOUMANS-4 [9,9]        Dedication

The fix is to exclude the known impostors (reference lists, contributor
lists, dedications, indexes) and then choose the contiguous run of pages
with the MOST Table-of-Contents signal, preferring a run that carries a
real "Contents" heading.

Writes the corrected ranges to kitchen/logs/relocate.json and prints a
one-line verdict per book so the human can eyeball it (Law 11).
"""
import json
import re
import sys
from concurrent.futures import ProcessPoolExecutor
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from find_toc import pages_text, toc_score, CONTENTS_HEAD  # noqa: E402

KITCHEN = Path(__file__).resolve().parent
BOOKS = KITCHEN / "books"
LOGS = KITCHEN / "logs"

# a page that is definitely NOT a Table of Contents
IMPOSTOR = re.compile(
    r"^\s*(references?|bibliography|contributors?|dedication|acknowledg\w*|"
    r"index|about the authors?|front matter|preface|foreword)\b",
    re.I | re.M)
IMPOSTOR_TITLE = re.compile(r"^\s*(references?|contributors?|dedication)\s*$",
                           re.I | re.M)
HEAD_LIMIT = 160


def verdict_for(bid, pdf_path, pages):
    """Pick the best contiguous TOC run from the first HEAD_LIMIT images."""
    runs = []          # (first, last, headed, total_score)
    run, score, headed = [], 0, False
    for n in sorted(pages):
        t = pages[n]
        s = toc_score(t)
        if IMPOSTOR.search(t) and s < 40:
            s = 0
        if s >= 15:
            run.append(n)
            score += s
            headed = headed or bool(CONTENTS_HEAD.search(t))
        else:
            if run:
                runs.append((run[0], run[-1], headed, score))
            run, score, headed = [], 0, False
    if run:
        runs.append((run[0], run[-1], headed, score))
    if not runs:
        return None
    # a run carrying a real "Contents" heading wins; then the richest run
    runs.sort(key=lambda r: (r[2], r[3]), reverse=True)
    return (runs[0][0], runs[0][1])


def work(rec):
    pdf = BOOKS / rec["pdf_file"]
    pages = pages_text(pdf, 1, min(HEAD_LIMIT, rec["page_count_images"]))
    best = verdict_for(rec["book_id"], pdf, pages)
    head = ""
    if best:
        t = pages.get(best[0], "")
        head = " | ".join([l.strip() for l in t.splitlines() if l.strip()][:3])
    return {"book_id": rec["book_id"], "old": rec["toc_images"],
            "new": list(best) if best else None, "head": head,
            "chars": len(pages.get(best[0], "")) if best else 0}


def main():
    targets = sys.argv[1:]
    books = [b for b in json.loads((KITCHEN / "books.json").read_text())
             if b["status"] == "candidate"]
    if targets:
        books = [b for b in books if b["book_id"] in targets]
    print(f"re-locating the Table of Contents for {len(books)} books ...",
          flush=True)
    with ProcessPoolExecutor(max_workers=6) as pool:
        res = list(pool.map(work, books))
    (LOGS / "relocate.json").write_text(json.dumps(res, indent=1,
                                                   ensure_ascii=False))
    for r in res:
        print(f"  {r['book_id']:24s} {str(r['old']):10s} -> {str(r['new']):10s} "
              f"| {r['head'][:80]}")


if __name__ == "__main__":
    main()