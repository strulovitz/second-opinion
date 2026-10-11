"""kitchen/toc_apply_headings.py -- build the provinces from the headings.

The chapter list alone does not say which Part a chapter belongs to, and
asking the model for a Part's banner WHILE it transcribes fifty chapter
entries produces wrong section numbers (measured on HARRISON-22: "SECTION
5" where the page prints "SECTION 1"). So the banners are asked for on
their own, and each banner is then asked for one small question: "what is
the chapter number of the first entry printed below it?"

kitchen/toc_headings.py writes the two answers. This script turns them into
the geography:

  * the TOP-LEVEL kind is whichever banner word the book actually uses --
    PART, VOLUME, UNIT, SECTION, BOOK -- counted from the headings
    themselves, never assumed;
  * each top-level heading owns the chapters from its first chapter up to
    the chapter before the next top-level heading's first chapter;
  * a top-level heading with no first chapter is completed from its first
    sub-heading if it has one, and otherwise REPORTED, never guessed.

    python kitchen/toc_apply_headings.py HARRISON-22
"""
import json
import re
import sys
from collections import Counter
from pathlib import Path

KITCHEN = Path(__file__).resolve().parent
LOGS = KITCHEN / "logs"

TOP = re.compile(r"^(PART|VOLUME|VOL|UNIT|BOOK|SECTION|MODULE)\b", re.I)
SUB = re.compile(r"^(CHAPTER|SECTION|UNIT)\b", re.I)


def load(bid):
    names = json.loads((LOGS / f"{bid}-vis-headingnames.json").read_text())
    firsts = json.loads((LOGS / f"{bid}-vis-headings.json").read_text())
    return names, firsts


def main():
    bid = sys.argv[1]
    names, firsts = load(bid)
    order = []          # (kind, title, first_chapter) in printed order
    for img in sorted(names, key=int):
        for h in names[img]:
            m = TOP.match(h)
            if not m:
                continue
            kind = m.group(1).upper()
            f = firsts.get(img, {}).get(h)
            order.append({"kind": kind, "title": h,
                          "first": int(f) if f else None, "image": int(img)})
    if not order:
        print(f"{bid}: no headings found", flush=True)
        return 1
    kinds = Counter(o["kind"] for o in order)
    # PART / VOLUME / UNIT / BOOK / MODULE outrank SECTION: in Harrison and
    # in most textbooks SECTION is the level BELOW the part, so counting
    # words alone picked SECTION (57 headings) over PART (20) and built 56
    # provinces out of the wrong level.
    priority = ["VOLUME", "VOL", "PART", "UNIT", "MODULE", "BOOK", "SECTION"]
    top = next((k for k in priority if kinds.get(k)), None)
    print(f"{bid}: heading kinds seen {dict(kinds)} -> top level is {top}",
          flush=True)

    tops = [o for o in order if o["kind"] == top]
    # a top-level heading with no first chapter takes the first chapter of
    # the next heading below it, which IS printed on the page
    for i, t in enumerate(tops):
        if t["first"] is not None:
            continue
        for o in order[order.index(t) + 1:]:
            if o["kind"] != top and o["first"] is not None:
                t["first"] = o["first"]
                print(f"    {t['title'][:50]}: first chapter taken from "
                      f"'{o['title'][:40]}' = {o['first']}", flush=True)
                break
    missing = [t["title"] for t in tops if t["first"] is None]
    if missing:
        print(f"    STILL MISSING a first chapter (reported, not guessed): "
              f"{missing}", flush=True)

    doc = json.loads((LOGS / f"{bid}-vis-toc.json").read_text())
    chapters = [c for p in doc["provinces"] for c in p["chapters"]]
    chapters.sort(key=lambda c: int(c["number"]) if str(c["number"]).isdigit()
                  else 0)
    provinces = []
    for i, t in enumerate(tops):
        end = (tops[i + 1]["first"] - 1) if i + 1 < len(tops) else None
        mine = [c for c in chapters
                if t["first"] is not None
                and int(c["number"]) >= t["first"]
                and (end is None or int(c["number"]) <= end)]
        if not mine:
            continue
        provinces.append({"name": t["title"], "part_name": t["title"],
                          "chapters": mine})
    n = sum(len(p["chapters"]) for p in provinces)
    covered = {int(c["number"]) for p in provinces for c in p["chapters"]}
    left = [int(c["number"]) for c in chapters if int(c["number"]) not in covered]
    (LOGS / f"{bid}-vis-toc.json").write_text(
        json.dumps({"provinces": provinces}, indent=1, ensure_ascii=False))
    print(f"{bid}: provinces={len(provinces)} chapters={n} "
          f"chapters not under any province={len(left)} {left[:12]}",
          flush=True)
    for p in provinces:
        print(f"    {p['name'][:52]:54s} {len(p['chapters']):3d}", flush=True)
    return 0


if __name__ == "__main__":
    sys.exit(main())