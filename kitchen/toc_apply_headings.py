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


def num(chapter):
    """The chapter's own number as an integer.

    MEASURED 2026-10-13 on BRANT-5: some books print chapter numbers with a
    letter suffix ("32A", an appendix chapter), and int("32A") raised and
    killed the whole build. The number is used only to decide which chapters
    belong under which heading, so the digits are read and the rest ignored;
    a number with no digits at all returns None and is never forced into a
    range.
    """
    m = re.match(r"\s*(\d+)", str(chapter.get("number")))
    return int(m.group(1)) if m else None


def raw_first(bid, title):
    """The first chapter number printed under this banner, read from the
    reader's own transcript of the contents page.

    MEASURED 2026-10-13 on BRANT-5: SECTION XII's banner is the last thing on
    its contents page and its chapters are on the page after, so asking the
    model "what is the first chapter under this banner?" answered NONE. The
    transcript already says: the banner is followed by 71A. Guessing instead
    gave 66 and swallowed six paediatric chapters, so the transcript is
    authoritative and a guess is never used.
    """
    f = LOGS / f"{bid}-vis-rawprov.json"
    if not f.exists():
        return None
    raw = json.loads(f.read_text())
    pat = re.compile(r"^\s*" + re.escape(title.strip()) + r"\b", re.I)
    for i, rp in enumerate(raw):
        if pat.match(rp["name"]):
            for rp2 in raw[i:]:
                if rp2["first_number"] is not None:
                    m = re.match(r"\s*(\d+)", str(rp2["first_number"]))
                    return int(m.group(1)) if m else None
    return None


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
    chapters.sort(key=lambda c: num(c) or 0)
    # MEASURED 2026-10-13 on BRANT-5: SECTION XII prints no chapter number
    # below its banner on the page (the chapters are on the next page), and
    # the arithmetic below then died on None. The sections of a book run in
    # printed order over one numbered chapter list, so a section with no
    # first chapter of its own takes the lowest chapter number not yet
    # claimed by the section above it. That is the book's own numbering, not
    # an invented page, and every such value is marked and printed so it can
    # be checked by eye.
    for i, t in enumerate(tops):
        if t["first"] is not None or i == 0:
            continue
        floor = tops[i - 1]["first"]
        rf = raw_first(bid, t["title"])
        if rf is not None:
            t["first"] = rf
            t["first_from_transcript"] = True
            print(f"    {t['title'][:50]}: no chapter printed under the banner "
                  f"on that page; the transcript itself puts its first chapter "
                  f"at {rf}", flush=True)
            continue
        rest = [num(c) for c in chapters if num(c) is not None
                and (floor is None or num(c) > floor)]
        if rest:
            t["first"] = min(rest)
            t["first_derived"] = True
            print(f"    {t['title'][:50]}: no chapter printed under the "
                  f"banner; first chapter taken as the next unclaimed one = "
                  f"{t['first']} (derived from the book's own order)", flush=True)

    provinces = []
    for i, t in enumerate(tops):
        nxt = next((o["first"] for o in tops[i + 1:]
                    if o["first"] is not None), None)
        end = (nxt - 1) if nxt is not None else None
        mine = [c for c in chapters
                if t["first"] is not None
                and num(c) is not None
                and num(c) >= t["first"]
                and (end is None or num(c) <= end)]
        if not mine:
            continue
        prov = {"name": t["title"], "part_name": t["title"],
                "chapters": mine}
        if t.get("first_derived"):
            prov["first_chapter_derived"] = True
        provinces.append(prov)
    n = sum(len(p["chapters"]) for p in provinces)
    covered = {num(c) for p in provinces for c in p["chapters"]}
    left = [c["number"] for c in chapters if num(c) not in covered]
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