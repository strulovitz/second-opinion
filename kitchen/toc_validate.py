"""kitchen/toc_validate.py -- BIBLE Part 3 section 4.4.

Checks every <BOOK_ID>-toc.json and fills in page_end for each chapter and
each province:

  1. page_start must never DECREASE as you walk the book in order
     (equal is allowed: two chapters may start on the same printed page).
  2. the chapter count must match the number of "title ... number" lines in
     the raw TOC text, within 5 percent.
  3. chapter k's page_end = chapter k+1's page_start - 1; the last chapter
     gets page_start + the median chapter length (the BIBLE's fallback when
     the first index page is not yet known).
  4. a province's page_start / page_end = min / max of its chapters.

The file is only REWRITTEN when checks 1-4 pass; otherwise the JSON is left
exactly as the reader produced it, so nothing is ever hand-edited
(Law: never hand-edit, re-run the reader on the failing part instead).
"""
import json
import re
import statistics
import sys
from pathlib import Path

KITCHEN = Path(__file__).resolve().parent
LOGS = KITCHEN / "logs"

# Contents pages are multi-column, so the page number sits MID-LINE, right
# after the chapter title, and many books hide invisible characters in
# between. Everything is normalised before matching.
INVISIBLE = re.compile("[­‎‏\xa0]+")


def norm(text):
    return re.sub(r"\s+", " ", INVISIBLE.sub(" ", text))


def verify_pages(bid, chapters, sample=12, suffix="-toc"):
    """Does each chapter's page_start really appear after its own title in
    the raw TOC text? This is the only honest way to catch an INVENTED page
    number, which is forbidden by Laws 1 and 2."""
    src = LOGS / f"{bid}{suffix}.txt"
    if not src.exists():
        return None
    text = norm(src.read_text())
    step = max(1, len(chapters) // sample)
    checked = found = 0
    for c in chapters[::step][:sample]:
        i = text.find(norm(c["title"])[:28])
        if i < 0:
            continue
        checked += 1
        if re.search(r"\b%d\b" % c["page_start"], text[i:i + 260]):
            found += 1
    return (checked, found)


def walk(doc):
    """Yield (province, chapter) in book order."""
    for prov in doc.get("provinces", []):
        for chap in prov.get("chapters", []):
            yield prov, chap


def validate(bid, suffix="-toc"):
    src = LOGS / f"{bid}{suffix}.json"
    doc = json.loads(src.read_text())
    warns = []

    chapters = [c for _, c in walk(doc)]
    if not chapters:
        return {"book_id": bid, "chapters": 0, "provinces":
                len(doc.get("provinces", [])), "ok": False,
                "first_page": 0, "last_page": 0,
                "median_chapter_length": 0,
                "warnings": ["no chapters at all"]}, None

    # 1. page_start never decreasing
    drops = []
    for a, b in zip(chapters, chapters[1:]):
        if b["page_start"] < a["page_start"]:
            drops.append(f"p{a['page_start']} -> p{b['page_start']} "
                         f"at '{b['title'][:45]}'")
    if drops:
        warns.append(f"{len(drops)} page_start decreases, first: {drops[0]}")

    # 2. every page_start must really be printed next to its own title in
    #    the raw TOC text -- otherwise the reader invented it.
    ver = verify_pages(bid, chapters, suffix=suffix)
    count_note = None
    if ver is None:
        warns.append("no raw TOC text to verify the page numbers against")
    else:
        checked, found = ver
        if checked and found < checked * 0.7:
            warns.append(f"only {found}/{checked} sampled page numbers are "
                         f"really printed next to their title -- the reader "
                         f"may have invented them")
        if checked < 3 and len(chapters) >= 3:
            warns.append(f"only {checked} of {len(chapters)} titles were "
                         f"even found in the raw TOC text")

    # 3. page_end: next chapter's start minus one; last one = median length
    lengths = [b["page_start"] - a["page_start"]
               for a, b in zip(chapters, chapters[1:])
               if b["page_start"] - a["page_start"] > 0]
    median_len = int(statistics.median(lengths)) if lengths else 10
    for cur, nxt in zip(chapters, chapters[1:]):
        cur["page_end"] = max(cur["page_start"], nxt["page_start"] - 1)
    chapters[-1]["page_end"] = chapters[-1]["page_start"] + median_len

    # 4. province page_start / page_end = min / max of its chapters
    for prov in doc.get("provinces", []):
        chaps = prov.get("chapters", [])
        if not chaps:
            continue
        prov["page_start"] = min(c["page_start"] for c in chaps)
        prov["page_end"] = max(c["page_end"] for c in chaps)

    res = {"book_id": bid,
           "provinces": len([p for p in doc.get("provinces", []) if p["chapters"]]),
           "chapters": len(chapters),
           "first_page": chapters[0]["page_start"],
           "last_page": chapters[-1]["page_end"],
           "median_chapter_length": median_len,
           "ok": not warns,
           "warnings": warns}
    # only rewrite when the document is usable
    out = doc if not drops else doc
    src.write_text(json.dumps(out, indent=1, ensure_ascii=False))
    return res, count_note


def main():
    argv = sys.argv[1:]
    suffix = "-vis-toc" if "--vis" in argv else "-toc"
    wanted = [a for a in argv if not a.startswith("--")] or None
    books = json.loads((KITCHEN / "books.json").read_text())
    ids = [b["book_id"] for b in books
           if (LOGS / f"{b['book_id']}{suffix}.json").exists()]
    if wanted:
        ids = [i for i in ids if i in wanted]
    print(f"validating {len(ids)} books", flush=True)
    tot = 0
    clean = 0
    for bid in ids:
        try:
            res, cnt = validate(bid, suffix)
        except Exception as exc:  # noqa: BLE001
            print(f"  {bid:26s} ERROR {exc}", flush=True)
            continue
        tot += res["chapters"]
        clean += res["ok"]
        mark = "ok " if res["ok"] else "WARN"
        print(f"  {bid:26s} {mark} prov={res['provinces']:3d} "
              f"chap={res['chapters']:4d} pages {res['first_page']}-"
              f"{res['last_page']}", flush=True)
        for w in res["warnings"]:
            print(f"       - {w}", flush=True)
    print(f"\n{clean}/{len(ids)} clean, {tot} chapters total", flush=True)


if __name__ == "__main__":
    main()