"""kitchen/merge_vis.py -- write the vision-located Table of Contents ranges.

Rule for choosing a range (measured 2026-10-10):
  * if the previous run already produced a usable number of chapters for that
    book, KEEP the old range -- it worked, and a wider range only adds body
    text the reader has to ignore;
  * otherwise take the range the vision pass found, which was correct on
    every book where it answered (it reproduced Harrison's known-correct 7-18
    exactly).

Never invents a range. A book the vision pass could not locate keeps
toc_images null and stays on the open list.
"""
import json
from pathlib import Path

KITCHEN = Path(__file__).resolve().parent
BOOKS = KITCHEN / "books.json"
VIS = KITCHEN / "logs" / "vis_locate.json"
RUNLOG = KITCHEN / "logs" / "toc_run.log"

# books that already produced a usable chapter count, so keep their old range
GOOD_ENOUGH = 10


def old_chapters() -> dict:
    out = {}
    try:
        for line in RUNLOG.read_text().splitlines():
            # "  ADAMS-12  provinces= 12 chapters= 49 chunks=1 OK"
            p = line.split()
            if len(p) >= 5 and p[1] == "provinces=" and p[3] == "chapters=":
                out[p[0]] = int(p[4])
    except OSError:
        pass
    return out


def main():
    books = json.loads(BOOKS.read_text())
    vis = {r["book_id"]: r for r in json.loads(VIS.read_text())}
    old = old_chapters()
    updated, kept, still = [], [], []
    for b in books:
        bid = b["book_id"]
        if b["status"] != "candidate" or bid not in vis:
            continue
        pages = sorted(set(vis[bid]["pages"]))
        if not pages:
            still.append(bid)
            b["toc_images"] = None
            continue
        if old.get(bid, 0) >= GOOD_ENOUGH:
            kept.append(bid)
            continue
        b["toc_images"] = [pages[0], pages[-1]]
        b["notes"] = (b["notes"] +
                      f"; TOC range set by the vision pass on 2026-10-10 "
                      f"(found {len(pages)} contents pages)").strip("; ")
        updated.append(bid)
    BOOKS.write_text(json.dumps(books, indent=1, ensure_ascii=False))
    print(f"updated from vision ({len(updated)}): {', '.join(updated)}")
    print(f"kept existing range ({len(kept)}): {', '.join(kept)}")
    print(f"STILL NOT LOCATED ({len(still)}): {', '.join(still)}")


if __name__ == "__main__":
    main()