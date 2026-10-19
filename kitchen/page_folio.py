# kitchen/page_folio.py -- give every chapter its PRINTED page and its PDF page.
#
# WHY THIS EXISTS
# BIBLE part 3 section 4.6 assumes `printed = image - page_offset` with ONE
# number per book. That is false: Sabiston-22 prints 876 on PDF page 1429 and
# 1367 on PDF page 1982 -- the paper's numbering drifts by 62 because unnumbered
# inserts sit between them, and the book also RESTARTS its numbering inside each
# Section. So each chapter is decided locally from the pages around it.
#
# THE SECOND DISCOVERY (2026-10-19, later the same day) -- page_start DOES NOT
# MEAN THE SAME THING IN EVERY BOOK. It holds two different numbers under one
# name, because two different tools wrote it:
#
#   * toc_vision / toc_openers wrote the number the CONTENTS PRINTS
#     -> page_start IS THE PRINTED PAGE (Harrison-22, Sabiston-22, Youmans-4,
#        Adams-12, Goodman-14, Krause-16, Campbell-2020, ... 22 books).
#        PROVED BY EYE on Harrison-22 PDF page 2044: it is the opener of
#        chapter 266, the contents say "266 ... 2001", the corner prints 2001,
#        and page_start is 2001 -- while the PDF page is 2044 (offset 43).
#   * toc_outline (PDF bookmark / link) wrote the DESTINATION IMAGE
#     -> page_start IS THE PDF PAGE (Mandell-9, Nelson-2024, Rosen-2022,
#        Murray-7, Middleton-2019, ... 15 books).
#        PROVED BY EYE on Mandell-9 PDF page 1835: it is the opener of chapter
#        107, page_start is 1835, and the corner prints 1452. Nelson-2024 PDF
#        page 2430 prints 2415 (page_start 2430).
#
# The evidence for each entry is its own `_page_source` / `_image` field, so
# the decision is PER ENTRY and is written into the output (`src`). A book is
# not trusted because of a guess: every entry carries how it was decided.
#
# So each chapter ends up with BOTH numbers Law 2 needs:
#   image   = the PDF page the chapter starts on (for the image file name)
#   printed = the folio the book prints on that page (for the citation)
#
# WHAT WAS WRONG BEFORE (do not relearn these):
#   1. Every entry was read as if it were a PDF page. For the 22 contents-read
#      books that is off by the whole front matter (Harrison: 43 pages), so the
#      answer was confidently wrong by 43 (Sabiston: by ~350-430, and worse
#      because of the Section restarts).
#   2. When a chapter's own page printed no detectable folio, folio_at used the
#      NEXT page's folio and returned it unchanged -- an off-by-one-per-page of
#      distance error (Mandell-9 chapter 107 came out 1453; the page prints
#      1452, checked on the rendered image).
#      The fix: a later page with gap g says the earlier page's folio is
#      `start - g`, not `later - g`.
#
# ZERO model calls. One pdftotext per book, cached on disk.
#
#   python kitchen/page_folio.py <BOOK_ID> [--quiet]
#   python kitchen/page_folio.py --all
#
# OUTPUT  kitchen/logs/<BOOK_ID>-folio.json
#   {"_meta": {...kind, offset, coverage, conflicts...},
#    "pages": {"<pdf page>": <printed page>, ...},      <- citation form
#    "chapters": [{"number","title","image","printed","src","check"}, ...]}
# It never writes anything except this file.

import bisect
import json
import re
import subprocess
import sys
from collections import Counter
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
KITCHEN = ROOT / "kitchen"
BOOKS = KITCHEN / "books.json"
LOGS = KITCHEN / "logs"

EDGES = 3        # header/footer lines to look at
FWD = 14         # pages forward from the chapter page to decide its folio
BACK = 3         # pages backward (a chapter opener often prints no folio)
MIN_CLUSTER = 2  # how many pages in the window must agree before we answer
TOL = 10         # pages whose implied gap sits within TOL vote as one cluster
MAX_GAP = 6      # a folio may be inherited from a neighbour at most this far

BARE = re.compile(r"^(\d{1,4})$")
TAIL = re.compile(r"(?<![A-Za-z0-9])([A-Za-z]{0,4}[-\u2013]?\d{1,4})\s*$")
NOTFOLIO = re.compile(r"^\s*(SECTION|CHAPTER|PART|TABLE|FIGURE|Fig|CASE|PART\b)", re.I)

# Elsevier prints some folios as "721.e89": that is page 721, annotation e89.
# CHECKED BY EYE 2026-10-19 on Sabiston-22 PDF page 1249, rendered to an image.
# Reading only the digits after the dot gave 89 and put the chapter on the
# wrong page, and because the marker advances by one on every page while the
# page part stays put it forms a PERFECTLY CONSTANT WRONG OFFSET (1160 across
# six consecutive pages), so it wins a naive vote. The page part is the folio.
ANNOT = re.compile(r"(\d{1,5})\s*\.\s*e\d{1,4}(?![\d.])")

# Evidence for what page_start means.
IMAGE_SRC = {"pdf-outline", "pdf-link"}
PRINTED_SRC = {"text-contents", "text-top", "contents"}


def cache_path(bid):
    return LOGS / f"{bid}-folio.txt"


def extract_text(pdf, bid, refresh=False):
    """One pdftotext for the whole book, cached. 2,000 pages takes ~12 s."""
    cp = cache_path(bid)
    if cp.exists() and cp.stat().st_size > 0 and not refresh:
        return cp.read_text(errors="replace")
    res = subprocess.run(["pdftotext", str(pdf), str(cp)],
                         capture_output=True, text=True, timeout=1800)
    if res.returncode != 0 or not cp.exists():
        raise RuntimeError(res.stderr.strip() or "pdftotext failed")
    return cp.read_text(errors="replace")


def candidates(page_text):
    lines = [l.strip() for l in page_text.splitlines() if l.strip()]
    if not lines:
        return []
    out = []
    for line in lines[:EDGES] + lines[-EDGES:]:
        if NOTFOLIO.match(line):
            continue
        m = ANNOT.search(line)
        if m:
            out.append(int(m.group(1)))
            continue
        m = BARE.match(line)
        if m:
            out.append(int(m.group(1)))
            continue
        m = TAIL.search(line)
        if m:
            d = re.findall(r"\d+", m.group(1))
            if d:
                out.append(int(d[-1]))

    # The "721.e89" form is distinctive enough to be trusted anywhere on the
    # page: pdftotext does NOT always put it in the header (Sabiston-22 PDF
    # page 1249, checked against the rendered image, has it on line 59).
    for line in lines:
        m = ANNOT.search(line)
        if m:
            out.append(int(m.group(1)))
    return out


def folio_at(pages, start, fwd=FWD, back=BACK):
    """The printed folio of PDF page `start`, decided by the pages around it.

    LOOKED AT BY EYE 2026-10-19 (Sabiston-22 PDF page 300, rendered): the book
    prints "13" there. The book's numbering RESTARTS in every Section, so one
    sequence for the whole book cannot exist. The decision is therefore local:

      * every number the window's header/footer lines offer is a candidate;
      * each candidate implies "gap = pdf_page - folio";
      * gaps within TOL of one another group into one cluster (consecutive
        printed pages differ by one, and "721.e89 / 721.e90" keeps the same
        page while the marker advances, so an exact-match vote would find no
        agreement at all);
      * the cluster holding the most DISTINCT pages wins;
      * folio(start) = start - that gap.

    If the chapter's own page printed nothing, the nearest page of the winning
    cluster is used and the gap is carried BACK to `start` (`start - g`).
    Returning the neighbour's own folio instead -- the old behaviour -- was
    measured off by one per page of distance: Mandell-9 chapter 107 came out
    1453 while its page prints 1452 (rendered and read by eye).

    Nothing is guessed: no cluster with MIN_CLUSTER pages means None (Law 2)."""
    lo = max(1, start - back)
    hi = min(len(pages), start + fwd)
    votes = []
    for idx in range(lo, hi + 1):
        for f in set(candidates(pages[idx - 1])):
            if 1 <= f <= 99999:
                votes.append((idx, idx - f))
    if not votes:
        return None, None

    votes.sort(key=lambda t: t[1])
    clusters, cur = [], [votes[0]]
    for v in votes[1:]:
        if v[1] - cur[-1][1] <= TOL:
            cur.append(v)
        else:
            clusters.append(cur)
            cur = [v]
    clusters.append(cur)

    best = max(clusters, key=lambda c: (len({p for p, _ in c}), len(c)))
    if len({p for p, _ in best}) < MIN_CLUSTER:
        return None, None
    own = [g for p, g in best if p == start]
    if own:
        return start - min(own), min(own)
    later = [(p, g) for p, g in best if p > start]
    if later:
        _, g = min(later)
        return start - g, g
    earlier = [(p, g) for p, g in best if p < start]
    if earlier:
        _, g = max(earlier)
        return start - g, g
    return None, None


def page_folios(pages):
    """folio for every PDF page: 1..npages -> int or None."""
    return {i: folio_at(pages, i)[0] for i in range(1, len(pages) + 1)}


def toc_entries(bid):
    """Every chapter of the book, in book order, with its own evidence."""
    for name in (f"{bid}-vis-toc.json", f"{bid}-toc.json"):
        path = LOGS / name
        if not path.exists():
            continue
        try:
            data = json.loads(path.read_text())
        except json.JSONDecodeError:
            continue
        out = []
        for prov in data.get("provinces", []):
            for ch in prov.get("chapters", []):
                if isinstance(ch.get("page_start"), int) and ch["page_start"] > 0:
                    out.append({"province": prov.get("name"),
                                "number": ch.get("number"),
                                "title": ch.get("title"),
                                "page_start": ch["page_start"],
                                "_image": ch.get("_image"),
                                "_link_image": ch.get("_link_image"),
                                "_page_source": ch.get("_page_source")})
        return out
    return []


def entry_kind(ent, majority):
    """'image' if page_start is a PDF page, 'printed' if it is a folio, else None.

    Decided by the field that stored the number, never by assumption:
      _page_source pdf-outline / pdf-link  -> the PDF bookmark destination
      _page_source text-contents / text-top -> a number transcribed from the
                                               printed contents
      _image present, no _page_source       -> the number was transcribed from
                                               a contents page, so it is the
                                               printed folio
    """
    src = ent.get("_page_source")
    if src in IMAGE_SRC:
        return "image"
    if src in PRINTED_SRC:
        return "printed"
    link = ent.get("_link_image")
    if isinstance(link, int) and link == ent["page_start"]:
        return "image"
    if ent.get("_image") is not None:
        return "printed"
    return majority


def image_role(ents):
    """Is `_image` the CONTENTS page or the CHAPTER'S OWN page?

    toc_vision stores the contents page the number was read from (Harrison:
    `_image` 7-18 while `page_start` runs 1..3995 -> median difference
    negative).  toc_openers stores the chapter's own opening page (image is
    always a little AFTER the printed number -> median difference positive).
    The book is classified from its own entries, not from its name."""
    diffs = []
    for e in ents:
        img = e.get("_image")
        if img is None:
            continue
        img = int(img) if isinstance(img, str) and img.isdigit() else img
        if isinstance(img, int):
            diffs.append(img - e["page_start"])
    if len(diffs) < 5:
        return None, None
    diffs.sort()
    med = diffs[len(diffs) // 2]
    return ("chapter" if med > 0 else "contents"), med


def resolve(bid, quiet=False):
    books = json.loads(BOOKS.read_text())
    by_id = {b["book_id"]: b for b in books}
    if bid not in by_id:
        raise SystemExit(f"unknown book {bid}")
    pdf = KITCHEN / "books" / by_id[bid]["pdf_file"]
    if not pdf.exists():
        raise SystemExit(f"{bid}: missing PDF")

    text = extract_text(pdf, bid)
    pages = text.split("\f")
    ents = toc_entries(bid)
    if not ents:
        raise SystemExit(f"{bid}: no chapters in the TOC")

    # majority kind from the entries that carry their own evidence
    ev = Counter()
    for e in ents:
        k = entry_kind(e, None)
        if k:
            ev[k] += 1
    majority = ev.most_common(1)[0][0] if ev else None
    if majority is None:
        raise SystemExit(f"{bid}: cannot tell whether page_start is a PDF page "
                         f"or a printed page")

    fol = page_folios(pages)
    by_folio = {}
    for q, f in fol.items():
        if f is not None:
            by_folio.setdefault(f, []).append(q)
    for f in by_folio:
        by_folio[f].sort()

    def lookup(printed, lo):
        """smallest PDF page >= `lo` whose folio is exactly `printed`."""
        lst = by_folio.get(printed)
        if not lst:
            return None
        i = bisect.bisect_left(lst, lo)
        return lst[i] if i < len(lst) else None

    role, role_med = image_role(ents)
    rows, pages_out, conflicts = [], {}, []
    prev_q = 0
    for e in ents:
        kind = entry_kind(e, majority)
        p = e["page_start"]
        img = e.get("_image")
        if isinstance(img, str) and img.isdigit():
            img = int(img)
        image = printed = None
        check = "ok"

        # 1. the PDF link/bookmark destination, when the TOC has one
        link = e.get("_link_image")
        if isinstance(link, int) and link > 0:
            image = link
            printed = fol.get(image)
            if printed is None:
                check = "no-folio-on-that-page"
            elif kind == "printed" and abs(printed - p) > 1:
                check = "conflict"

        # 2. toc_openers books: `_image` IS the chapter's own opening page,
        #    and the reader's PAGE field is a second, independent reading of
        #    the same folio -- so the two are compared (this is what caught
        #    the off-by-one: Mandell-9 107 read 1453, the page prints 1452).
        elif role == "chapter" and isinstance(img, int) and img > 0:
            image = img
            printed = fol.get(image)
            if printed is None:
                printed, check = p, "folio-missing-reader-page-used"
            elif kind == "printed" and abs(printed - p) > 1:
                check = "conflict"

        # 3. page_start is a PDF page (pdf-outline / pdf-link books)
        elif kind == "image":
            image = p
            printed = fol.get(p)
            if printed is None:
                check = "no-folio-on-that-page"
            else:
                q = lookup(printed, max(1, p - 3))
                if q is None or q > p + 3:
                    check = "conflict"

        # 4. page_start is the printed folio (contents-read books): the PDF
        #    page is found by looking for the page that prints it, staying
        #    after the previous chapter (a Section restart can print the same
        #    folio twice, so book order is what breaks the tie).
        else:
            printed = p
            q = lookup(printed, prev_q + 1)
            if q is None and prev_q:
                # Harrison-22's OWN contents prints "45 Palpitations ... 291"
                # and "46 Exercise Intolerance ... 291" on the same line pair
                # (contents PDF page 8): two chapters really do share one
                # page, so the same PDF page is allowed twice.
                q = lookup(printed, prev_q)
            if q is None:
                check = "no-page-prints-that-folio"
            else:
                if q == prev_q:
                    check = "shared-page"
                image = q
                prev_q = max(prev_q, q)

        if image is not None:
            prev_q = max(prev_q, image)
        if check not in ("ok", "shared-page"):
            conflicts.append({"number": e["number"], "title": e["title"],
                              "page_start": p, "kind": kind, "why": check})
        rows.append({"province": e["province"], "number": e["number"],
                     "title": e["title"], "image": image, "printed": printed,
                     "src": kind, "page_start": p, "check": check})
        if image is not None and printed is not None:
            pages_out[str(image)] = printed

    offs = [r["image"] - r["printed"] for r in rows
            if r["image"] is not None and r["printed"] is not None]
    o = Counter(offs)
    offset = o.most_common(1)[0][0] if o else None
    offset_share = (o.most_common(1)[0][1] / len(offs)) if offs else 0.0
    have_both = sum(1 for r in rows if r["image"] is not None
                    and r["printed"] is not None)

    meta = {
        "book": bid,
        "page_start_means": majority,
        "image_role": role,
        "image_role_median": role_med,
        "kind_votes": dict(ev),
        "chapters": len(rows),
        "resolved_both": have_both,
        "conflicts": len(conflicts),
        "median_offset": sorted(offs)[len(offs) // 2] if offs else None,
        "offset_mode": offset,
        "offset_mode_share": round(offset_share, 3),
        "offset_constant": bool(offset is not None and offset_share >= 0.90),
        "pdf_pages": len(pages),
        "method": "page_folio.py v2 (local folio, per-entry kind)",
    }
    doc = {"_meta": meta, "pages": pages_out, "chapters": rows,
           "conflicts": conflicts}
    (LOGS / f"{bid}-folio.json").write_text(json.dumps(doc))

    if not quiet:
        flag = "OK " if have_both == len(rows) and not conflicts else "..."
        print(f"{bid:26s} {flag} both={have_both}/{len(rows)} "
              f"kind={majority} offset={meta['median_offset']}"
              f"{'' if meta['offset_constant'] else ' (drifting)'} "
              f"conflicts={len(conflicts)}")
    return meta


def main(argv):
    books = json.loads(BOOKS.read_text())
    by_id = {b["book_id"]: b for b in books}
    args = [a for a in argv if not a.startswith("--")]
    quiet = "--quiet" in argv
    targets = list(by_id) if "--all" in argv else [a for a in args if a in by_id]
    if not targets:
        sys.exit("give a BOOK_ID, or --all")
    bad = 0
    for bid in targets:
        try:
            meta = resolve(bid, quiet=quiet)
        except SystemExit as exc:
            print(f"{bid:26s} FAILED: {exc}")
            bad += 1
            continue
        if meta["conflicts"]:
            bad += 1
    sys.exit(1 if bad else 0)


if __name__ == "__main__":
    main(sys.argv[1:])
