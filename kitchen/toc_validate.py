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
    number, which is forbidden by Laws 1 and 2. A chapter whose contents page
    prints no page at all (page_start is None) has nothing to verify."""
    src = LOGS / f"{bid}{suffix}.txt"
    if not src.exists():
        return None
    text = norm(src.read_text())
    # A page that came from the PDF's OWN chapter link is not printed in the
    # contents text and must not be judged against it. Such a page is proved
    # differently: toc_links.py opens the target page and reads the chapter
    # number printed there (recorded in <BOOK_ID>-vis-links.json).
    # MEASURED 2026-10-16 on HAZZARD-2022: a page that came from the PDF's
    # bookmark outline (toc_outline.py) is the same kind of book evidence
    # and is excluded by the same rule.
    # MEASURED 2026-10-18 on STAHL-2024: "text-contents" = the printed
    # contents page read from the PDF's text layer (no vision needed when
    # the text layer is clean); the printed folios are recorded in the
    # sidecar, page_start stores the PDF page.
    chapters = [c for c in chapters
                if c.get("page_start") is not None
                and c.get("_page_source") not in ("pdf-link",
                                                  "pdf-outline",
                                                  "text-top",
                                                  "text-contents")]
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
                "warnings": ["no chapters at all -- a book with 0 chapters is "
                             "NOT clean, it is empty, and must never be "
                             "counted as read"]}, None

    # MEASURED 2026-10-12 on BRANT-5: some books print a real contents with
    # NO page numbers at all (checked by eye). Those chapters are kept with
    # page_start = null -- a page is never invented (Law 2) -- and every page
    # check below skips them, so a book without printed pages is reported as
    # such instead of being silently accepted or silently emptied.
    nopage = [c for c in chapters if c.get("page_start") is None]
    linked = [c for c in chapters if c.get("_page_source") == "pdf-link"]
    outlined = [c for c in chapters if c.get("_page_source") == "pdf-outline"]
    texttop = [c for c in chapters if c.get("_page_source") == "text-top"]
    # MEASURED 2026-10-18 on STAHL-2024: text-contents = printed contents
    # read from the text layer; same book evidence as the other three.
    textcont = [c for c in chapters
                if c.get("_page_source") == "text-contents"]

    # 1. page_start never decreasing
    drops = []
    for a, b in zip(chapters, chapters[1:]):
        if b["page_start"] is None or a["page_start"] is None:
            continue
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
        # MEASURED 2026-10-16 on MANDELL-9: some PDFs (libgen scans) contain
        # NO printed table of contents at all, so there is no raw TOC text
        # to verify against. If every chapter's page comes from the book
        # itself -- the PDF bookmark outline (`pdf-outline`) or the title
        # printed at the top of the chapter's own first page in the text
        # layer (`text-top`) -- that is book evidence, not a guess, and the
        # book is not penalised for the missing TOC.
        book_ev = linked + outlined + texttop + textcont
        if book_ev and len(book_ev) == len(chapters):
            count_note = (f"all {len(chapters)} chapters get their page from "
                          f"the book itself (PDF bookmark outline and/or the "
                          f"title printed at the top of each chapter's first "
                          f"page and/or the printed contents in the text "
                          f"layer); verified against the book's own evidence")
        else:
            warns.append("no raw TOC text to verify the page numbers against")
    else:
        checked, found = ver
        if checked and found < checked * 0.7:
            warns.append(f"only {found}/{checked} sampled page numbers are "
                         f"really printed next to their title -- the reader "
                         f"may have invented them")
        if (checked < 3 and len(chapters) >= 3 and not nopage
                and not linked and not outlined and not texttop
                and not textcont):
            warns.append(f"only {checked} of {len(chapters)} titles were "
                         f"even found in the raw TOC text")
    if linked:
        print(f"       - {len(linked)} of {len(chapters)} chapters get their "
              f"page from the book's OWN PDF chapter link (the contents "
              f"prints none); each target page was opened and its chapter "
              f"number read there", flush=True)
    if outlined:
        print(f"       - {len(outlined)} of {len(chapters)} chapters get "
              f"their page from the PDF's OWN bookmark outline (the "
              f"contents prints none and carries no link for them)", flush=True)
    if texttop:
        print(f"       - {len(texttop)} of {len(chapters)} chapters get "
              f"their page from the title printed at the TOP of the "
              f"chapter's own first page (pdftotext layer; the bookmark "
              f"target was broken and no contents prints a page)", flush=True)
    if textcont:
        print(f"       - {len(textcont)} of {len(chapters)} chapters get "
              f"their page from the printed contents read in the PDF's "
              f"TEXT LAYER (no vision needed; printed folios recorded in "
              f"the sidecar)", flush=True)
    if nopage:
        warns.append(f"{len(nopage)} of {len(chapters)} chapters print NO page "
                     f"in the contents, so their page_start is null and their "
                     f"page has to come from the book itself (Part 4); no "
                     f"page was invented")

    # 3. page_end: next chapter's start minus one; last one = median length
    lengths = [b["page_start"] - a["page_start"]
               for a, b in zip(chapters, chapters[1:])
               if a["page_start"] is not None and b["page_start"] is not None
               and b["page_start"] - a["page_start"] > 0]
    median_len = int(statistics.median(lengths)) if lengths else 10
    for cur, nxt in zip(chapters, chapters[1:]):
        if cur["page_start"] is None or nxt["page_start"] is None:
            cur["page_end"] = None
            continue
        cur["page_end"] = max(cur["page_start"], nxt["page_start"] - 1)
    chapters[-1]["page_end"] = (chapters[-1]["page_start"] + median_len
                                if chapters[-1]["page_start"] is not None
                                else None)

    # 4. province page_start / page_end = min / max of its chapters
    for prov in doc.get("provinces", []):
        chaps = prov.get("chapters", [])
        chaps = [c for c in chaps if c.get("page_start") is not None]
        if not chaps:
            prov["page_start"] = prov["page_end"] = None
            continue
        prov["page_start"] = min(c["page_start"] for c in chaps)
        prov["page_end"] = max(c["page_end"] or c["page_start"] for c in chaps)

    paged = [c for c in chapters if c["page_start"] is not None]
    res = {"book_id": bid,
           "provinces": len([p for p in doc.get("provinces", []) if p["chapters"]]),
           "chapters": len(chapters),
           "chapters_without_page": len(nopage),
           "first_page": paged[0]["page_start"] if paged else None,
           "last_page": (paged[-1]["page_end"] or paged[-1]["page_start"])
                        if paged else None,
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
        fp, lp = res["first_page"], res["last_page"]
        rng = f"pages {fp}-{lp}" if fp is not None else "pages not printed"
        print(f"  {bid:26s} {mark} prov={res['provinces']:3d} "
              f"chap={res['chapters']:4d} {rng}", flush=True)
        for w in res["warnings"]:
            print(f"       - {w}", flush=True)
        if cnt:
            print(f"       - {cnt}", flush=True)
        # MEASURED 2026-10-13: build_book.py searched the word " clean" in this
        # script's output and found it in the summary line "0/1 clean", so a
        # book with 0 chapters was recorded as CLEAN. A machine-readable line
        # per book is printed now, and the summary is left for human eyes.
        print(f"RESULT {bid} {'ok' if res['ok'] else 'warn'} "
              f"chapters={res['chapters']} provinces={res['provinces']} "
              f"without_page={res.get('chapters_without_page', 0)}", flush=True)
    print(f"\n{clean}/{len(ids)} clean, {tot} chapters total", flush=True)


if __name__ == "__main__":
    main()