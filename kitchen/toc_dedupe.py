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
    # A gap repair is appended at the END of the transcript, so it sits in
    # the LAST province while carrying numbers EARLIER than that province's
    # own first chapter. The FIRST chapter in transcript order is the
    # marker -- taking the minimum would let the strays themselves drag it
    # down (FIRESTEIN-12: Part 18's real chapters are 121-130 and the
    # strays 11, 52, 67, 105 are appended after them). The page test alone
    # is not enough: FIRESTEIN prints Parts 17 and 18 on one contents page.
    last_start = None
    head = doc["provinces"][last]["chapters"][:1]
    if head and str(head[0].get("number")).isdigit():
        last_start = int(head[0]["number"])
    for idx, prov in enumerate(doc["provinces"]):
        stay = []
        for c in prov["chapters"]:
            home = provmap.get(str(c.get("_image")))
            num = c.get("number")
            earlier = (last_start is not None and str(num).isdigit()
                       and int(num) < last_start)
            if (idx == last and home is not None and home in by_index
                    and home < last and earlier):
                # WHERE it goes: by printed page, not by page-of-contents.
                # FIRESTEIN-12 reads "11 Neutrophils 175" in the Part 18
                # block; page 175 belongs to Part 2, but the contents page
                # it sits on carries Part 1, so the image map would have
                # filed it one Part too early. A province whose chapters
                # span the stray's own printed page is its true home.
                page = c.get("page_start")
                best = home
                if page is not None:
                    for j, other in by_index.items():
                        pages = [x.get("page_start") for x in other["chapters"]
                                 if x.get("page_start") is not None]
                        if pages and min(pages) <= page <= max(pages):
                            best = j
                            break
                by_index[best]["chapters"].append(c)
                moved += 1
            else:
                stay.append(c)
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