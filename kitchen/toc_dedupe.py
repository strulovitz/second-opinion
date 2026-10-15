"""kitchen/toc_dedupe.py -- remove chapters that were captured twice.

MEASURED 2026-10-11 on HARRISON-22: 522 chapters came back but only 500
distinct numbers, and the 22 extras were 11 chapters (495-505) captured
TWICE, identical in number, title and printed page -- the contents ran over
a page boundary and the reader emitted the same block at the end of one
page and again at the start of the next.

An entry that is identical in all three fields is the same printed entry,
not a second chapter, so it is removed and counted. An entry that shares a
number with another but differs in title or page is NEVER touched here: a
real duplicate number is a question for the human, not something to tidy
away (Law 15).

    python kitchen/toc_dedupe.py HARRISON-22 [--vis]
"""
import json
import sys
from pathlib import Path

KITCHEN = Path(__file__).resolve().parent
LOGS = KITCHEN / "logs"


def reassign(doc, bid):
    """Put every chapter back under the province of the PAGE it was printed
    on. A gap repair is appended at the end of the transcript, so without
    this the chapters it recovers land under the last province of the book
    instead of the section they belong to."""
    provmap_path = LOGS / f"{bid}-vis-imageprov.json"
    if not provmap_path.exists():
        return 0
    provmap = json.loads(provmap_path.read_text())
    # by INDEX, not by name: many provinces share a name ("SECTION 4"
    # appears more than once in Harrison), so a name map would collapse them
    by_index = {i: p for i, p in enumerate(doc["provinces"])}
    moved = 0
    # ONLY a chapter stuck in the LAST province can be a gap repair
    # appended at the end of the transcript. MEASURED 2026-10-15 on
    # FIRESTEIN-12: its 18 Parts are printed across only 5 contents pages,
    # so "page -> one province" is false there and reassign pulled 99 of
    # 125 chapters out of the Part they were read under and into the first
    # Part sharing that page. Chapters are now left where they were read
    # unless they are in the last province and their page belongs to an
    # earlier one.
    last = len(doc["provinces"]) - 1
    # A gap repair is appended to the LAST province, so it sits there while
    # carrying numbers far from that province's own run. The province's
    # LONGEST CONSECUTIVE run of chapter numbers is its real body, and
    # anything outside that run is a stray. A single "first chapter" or
    # "minimum" marker fails: FIRESTEIN-12 appends its strays after the
    # real chapters, BOLOGNIA-2024 puts them before. The page test alone
    # is not enough either: FIRESTEIN prints Parts 17 and 18 on one
    # contents page.
    core = None
    nums = [int(c["number"]) for c in doc["provinces"][last]["chapters"]
            if str(c.get("number")).isdigit()]
    if nums:
        best_run, run = [], []
        for a, b in zip(sorted(nums), sorted(nums)[1:] + [None]):
            run.append(a)
            if b is None or b != a + 1:
                if len(run) > len(best_run):
                    best_run = run
                run = []
        core = (min(best_run), max(best_run)) if best_run else None

    def is_stray(c):
        if core is None or not str(c.get("number")).isdigit():
            return False
        return not (core[0] <= int(c["number"]) <= core[1])
    for idx, prov in enumerate(doc["provinces"]):
        stay = []
        for c in prov["chapters"]:
            stray = is_stray(c)
            if not (idx == last and stray):
                stay.append(c)
                continue
            # WHERE it goes: by chapter NUMBER first. A province whose own
            # numbers sit nearest the stray is its true home. Page alone is
            # not enough because a mis-filed stray inflates the wrong
            # province's page range until it looks like a match:
            # BOLOGNIA-2024 filed "30 Pemphigoid Group, 31 Dermatitis
            # Herpetiformis, 32 Epidermolysis Bullosa" (all blistering
            # diseases) under SECTION 7 instead of SECTION 5, whose last
            # chapter is 29.
            page = c.get("page_start")
            num = int(c["number"]) if str(c.get("number")).isdigit() else None
            best, best_gap, best_pages = None, None, None
            for j, other in by_index.items():
                if j == idx:
                    continue
                ons = [int(x["number"]) for x in other["chapters"]
                       if str(x.get("number")).isdigit()]
                if not ons or num is None:
                    continue
                gap = 0 if min(ons) <= num <= max(ons) else min(
                    abs(num - min(ons)), abs(num - max(ons)))
                pgs = [x.get("page_start") for x in other["chapters"]
                       if x.get("page_start") is not None]
                pdist = 0
                if page is not None and pgs:
                    pdist = (0 if min(pgs) <= page <= max(pgs)
                             else min(abs(page - min(pgs)),
                                      abs(page - max(pgs))))
                key = (gap, pdist)
                if best_gap is None or key < best_gap:
                    best, best_gap, best_pages = j, key, pgs
            if best is None:
                home = provmap.get(str(c.get("_image")))
                if home in by_index and home != idx:
                    best = home
            # Already in the province its page belongs to: leave it.
            # Appending to the list being iterated never ends
            # (MEASURED 2026-10-15: BOLOGNIA-2024's dedupe spun forever
            # because a stray's page fell inside the last SECTION's range).
            if best is None or best == idx:
                stay.append(c)
                continue
            by_index[best]["chapters"].append(c)
            moved += 1
        prov["chapters"] = stay
    return moved


def dedupe(bid, suffix="-vis-toc"):
    path = LOGS / f"{bid}{suffix}.json"
    doc = json.loads(path.read_text())
    removed, conflicts = 0, []
    if suffix == "-vis-toc":
        reassign(doc, bid)
    for prov in doc["provinces"]:
        seen, keep = {}, []
        for c in prov["chapters"]:
            key = (str(c.get("number")), c.get("title"), c.get("page_start"))
            if key in seen:
                removed += 1
                continue
            seen[key] = True
            keep.append(c)
        prov["chapters"] = keep
    # Chapters run forwards through a book, so they are put back into
    # printed-page order inside each province. The reader sometimes emits a
    # two-column page right-column-first, and a targeted gap repair is
    # appended at the end of the transcript; both leave the list out of
    # order without anything being wrong with the entries themselves.
    # A TARGETED re-read appended to the transcript supersedes the first
    # reading of the same chapter when the two disagree: the model had
    # swapped the numbers of HARRISON-22's chapters 270 and 271, which the
    # validator's page-order check exposed. The decision is made on a FLAT
    # list -- an appended block lands under whatever province happened to be
    # last, so comparing province by province compares the wrong things.
    # Every replacement is reported; none is silent.
    flat = [c for prov in doc["provinces"] for c in prov["chapters"]]
    by_number, replaced, seen_keys = {}, [], set()
    for c in flat:
        key = str(c.get("number"))
        sig = (c["title"], c.get("page_start"))
        if key in ("None", ""):
            continue
        if key in by_number:
            old = by_number[key]
            if (old["title"], old.get("page_start")) != sig:
                replaced.append({"number": key,
                                 "was": [old["title"], old.get("page_start")],
                                 "now": [c["title"], c.get("page_start")]})
            else:
                removed += 1
                continue
        by_number[key] = c
    flat = [c for c in flat if str(c.get("number")) not in ("None", "")
            and by_number[str(c["number"])] is c]
    flat.sort(key=lambda c: int(c["number"]) if str(c["number"]).isdigit() else 0)
    # KEEP the provinces. MEASURED 2026-10-15 on FIRESTEIN-12: reparse
    # built 18 correct "Part n: Title" provinces from the reader's own
    # words, and this step threw them all into one province called "ALL",
    # so the later banner step could only rebuild from the ten banners the
    # banner read happened to catch. The winning object per chapter number
    # is kept and every other chapter is dropped; nothing is re-filed.
    winners = {id(c) for c in flat}
    for prov in doc["provinces"]:
        kept = [c for c in prov.get("chapters", []) if id(c) in winners]
        kept.sort(key=lambda c: int(c["number"])
                  if str(c.get("number")).isdigit() else 0)
        prov["chapters"] = kept
    doc["provinces"] = [p for p in doc["provinces"] if p.get("chapters")]
    (LOGS / f"{bid}-vis-conflicts.json").write_text(
        json.dumps({"superseded_by_targeted_reread": replaced}, indent=1,
                   ensure_ascii=False))
    path.write_text(json.dumps(doc, indent=1, ensure_ascii=False))
    n = sum(len(p["chapters"]) for p in doc["provinces"])
    return len(doc["provinces"]), n, removed, conflicts


def main():
    argv = sys.argv[1:]
    suffix = "-vis-toc" if "--vis" in argv else "-toc"
    for bid in [a for a in argv if not a.startswith("--")]:
        np_, nc, rm, _ = dedupe(bid, suffix)
        print(f"{bid}: provinces={np_} chapters={nc} "
              f"exact duplicates removed={rm}", flush=True)


if __name__ == "__main__":
    sys.exit(main())