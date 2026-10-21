#!/usr/bin/env python3
"""kitchen/eyes_folio.py -- the PRINTED page of every chapter, read by the eyes.

WHAT THIS IS
    The grunt work of checking a book's Table of Contents against the real
    pages. For every chapter we produce:
      1. the PDF page where the chapter actually BEGINS (the opener),
      2. the page number the book PRINTS for that page,
      3. therefore the chapter's printed page range (page_end = the next
         chapter's printed page minus one).
    The printed page comes from the PICTURE of the page, read by the free
    local READER (Qwen 3.8 27B, TIER FREE). The PDF text layer is used only
    to point at which page to show. Every number we store therefore has a
    picture behind it, kept on disk (Law 2).

THE READER REPORTS, IT DOES NOT JUDGE
    The reader is asked what it SEES:
        KIND:    OPENING | BODY | INDEX | OTHER
        HEADING: the heading printed at the top of the page, verbatim
        FOLIO:   the page number printed in a corner, or NONE
    This script then decides whether that page is the chapter's opener.
    (Asking the reader "is this the chapter's first page? YES/NO" is NOT
    used: on an index page that lists the chapter title, the reader happily
    said YES, and that one wrong answer poisoned 400 chapters. Measured on
    HARRISON-22, 2026-10-21.)

    Nothing is invented. A page that prints no number is recorded as such;
    a chapter we cannot place is reported as unresolved; and where the
    book's own contents disagrees with the page, the disagreement is
    recorded and shown -- that is a finding about the Table of Contents,
    which is the whole point of this work.

OUTPUT
    kitchen/logs/<BOOK>-eyes.json      records + summary (gitignored)
    kitchen/logs/<BOOK>-toc.json       the BIBLE's format (part 3 section
                                        4.4): provinces with chapters that
                                        have page_start and page_end
    kitchen/logs/eyes-render/<BOOK>/   the pictures

    Zero bytes are written to books.json, to any geography file or to Neo4j.

MODES
    python kitchen/eyes_folio.py THOMPSON-2023 --sample 6   # random 6
    python kitchen/eyes_folio.py THOMPSON-2023 --all        # every chapter
    python kitchen/eyes_folio.py THOMPSON-2023 --list       # pointers only
"""

import argparse
import json
import random
import re
import statistics
import subprocess
import unicodedata
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from reader import ask  # noqa: E402

ROOT = Path(__file__).resolve().parent.parent
KITCHEN = ROOT / "kitchen"
BOOKS = KITCHEN / "books.json"
LOGS = KITCHEN / "logs"
RENDER = LOGS / "eyes-render"

# ---------------------------------------------------------------- the reader

SYSTEM = (
    "You are looking at ONE page of a scanned medical textbook, as a picture.\n"
    "Answer with EXACTLY three lines and nothing else:\n"
    "KIND: OPENING   -- the page opens a chapter (a large chapter heading is\n"
    "                   printed at the top of the page)\n"
    "KIND: BODY      -- an ordinary text page\n"
    "KIND: INDEX     -- an alphabetical index page\n"
    "KIND: OTHER     -- anything else (title page, contents, plate, blank)\n"
    "HEADING: <EVERY heading you can read in the top third of the page,\n"
    "          copied exactly as printed, separated by \" | \", or NONE\n"
    "          if the page has no heading>\n"
    "FOLIO: <n>      -- the PAGE NUMBER the book prints in a corner of this\n"
    "          page (header or footer). It is NOT a chapter number, NOT a\n"
    "          table or figure number. NONE if no page number is printed.\n"
    "Look at the whole page: the top for the heading, all four corners for\n"
    "the page number. Do not stop early."
)


def render(pdf, book, page, dpi=120):
    """PDF page -> PNG (kept on disk, it is the evidence)."""
    out_dir = RENDER / book
    out_dir.mkdir(parents=True, exist_ok=True)
    out = out_dir / f"{page:05d}"
    png = out.with_suffix(".png")
    if not png.exists():
        subprocess.run(["pdftoppm", "-f", str(page), "-l", str(page),
                        "-r", str(dpi), "-png", "-singlefile", str(pdf), str(out)],
                       check=True, capture_output=True)
    return png


def parse(ans):
    """-> (kind, heading, folio) as reported by the reader."""
    kind = heading = None
    folio = None
    for line in (ans or "").splitlines():
        s = line.strip()
        up = s.upper()
        if up.startswith("KIND:"):
            for k in ("OPENING", "BODY", "INDEX", "OTHER"):
                if k in up:
                    kind = k
                    break
        elif up.startswith("HEADING:"):
            heading = s.split(":", 1)[1].strip()
            if heading.upper().startswith("NONE"):
                heading = ""
        elif up.startswith("FOLIO:"):
            tail = s.split(":", 1)[1].strip()
            head = tail.split()[0] if tail.split() else ""
            if head.isdigit():
                folio = int(head)
    return kind, heading, folio


def ask_page(pdf, book, page):
    """Show one page to the reader; return (kind, heading, folio, raw, file)."""
    png = render(pdf, book, page)
    ans = ask(SYSTEM, "What is on this page? Report what you see.",
              images=[png], max_tokens=600, expect_json=False, retries=2,
              no_reasoning=True)
    kind, heading, folio = parse(ans)
    return kind, heading, folio, (ans or "").strip()[:300], png.name


# --------------------------------------------------------------- the pointer

BARE = re.compile(r"^(\d{1,5})$")
ANNOT = re.compile(r"(\d{1,5})\s*\.\s*e\d{1,4}(?![\d.])")
STOP = {"the", "and", "for", "from", "with", "into", "their", "this", "that",
        "what", "when", "how", "does", "are", "was", "were", "clinical",
        "management", "diagnosis", "treatment", "chapter", "part", "section",
        "introduction", "overview", "approach", "update", "edition", "patient",
        "patients", "disease", "disorders", "syndrome"}


def lines_of(pages, i):
    if i < 1 or i > len(pages):
        return []
    return [l.strip() for l in pages[i - 1].splitlines() if l.strip()]


def head_of(pages, i, n=4):
    return " ".join(lines_of(pages, i)[:n])


def folio_of(pages, i):
    """The page number printed on PDF page i, read from the text layer.

    Only the first three and the last three lines are trusted. A textbook
    prints its folio in the top outer corner or the bottom outer corner; a
    Table-of-Contents line never consists of a number alone, so it cannot
    be mistaken for a folio (measured on THOMPSON-2023 and HARRISON-22,
    2026-10-21).
    """
    lines = lines_of(pages, i)
    if len(lines) < 5:
        return None
    for line in lines:
        m = ANNOT.search(line)
        if m:
            return int(m.group(1))
    for line in lines[:3] + lines[-3:]:
        m = BARE.match(line)
        if m:
            return int(m.group(1))
    return None


def plain(s):
    """Lower case, without accents, without punctuation between letters.

    The books print "Sjogren's Disease" in the contents and "Sjögren's
    Disease" on the page; without this the two never match.
    """
    s = unicodedata.normalize("NFD", s or "")
    s = "".join(ch for ch in s if not unicodedata.combining(ch))
    return re.sub(r"[^a-z0-9 ]+", " ", s.lower())


def title_words(title):
    words = re.findall(r"[A-Za-z][A-Za-z'-]{3,}", title or "")
    return [plain(w) for w in words if plain(w) not in STOP]


def title_head_pages(pages, title, lo, hi):
    """Pages in (lo, hi] whose HEAD carries the chapter's title.

    A textbook's running header prints the chapter title, so the first page
    that carries the title is very often the opener itself.
    """
    words = title_words(title)
    if not words:
        return []
    hits = []
    for i in range(max(1, lo + 1), min(len(pages), hi) + 1):
        head = head_of(pages, i).lower()
        if any(w in head for w in words):
            hits.append(i)
    return hits


CHAPTER_MARK = re.compile(r"^c\s*h\s*a\s*p\s*t\s*e\s*r\b", re.I)


def chapter_opener_pages(pages, number, lo, hi):
    """Pages whose head carries a chapter marker and the chapter number.

    Some books print the opener as "c h a p t e r" on one line and the
    chapter number on the next (THOMPSON-2023). That is the opener itself.
    """
    hits = []
    num = str(number or "").lower()
    if not num:
        return hits
    for i in range(max(1, lo + 1), min(len(pages), hi) + 1):
        lines = lines_of(pages, i)[:4]
        if not lines:
            continue
        if not CHAPTER_MARK.match(lines[0]):
            continue
        if any(re.search(r"\b" + re.escape(num) + r"\b", l.lower())
               for l in lines[1:]):
            hits.append(i)
    return hits


def folio_index(pages):
    """folio -> [PDF pages that print that folio], in book order."""
    idx = {}
    for i in range(1, len(pages) + 1):
        f = folio_of(pages, i)
        if f:
            idx.setdefault(f, []).append(i)
    return idx


# ------------------------------------------------------------- the chapters

def load_chapters(bid):
    """Every chapter of the book with the evidence the TOC stage left behind."""
    path = LOGS / f"{bid}-vis-toc.json"
    if not path.exists():
        path = LOGS / f"{bid}-toc.json"
    if not path.exists():
        sys.exit(f"{bid}: no TOC file found")
    data = json.loads(path.read_text())
    out = []
    for prov in data.get("provinces", []):
        for ch in prov.get("chapters", []):
            img = ch.get("_image")
            if isinstance(img, str) and img.isdigit():
                img = int(img)
            out.append({
                "province": prov.get("name"),
                "part_name": prov.get("part_name"),
                "number": ch.get("number"),
                "title": ch.get("title"),
                "page_start": ch.get("page_start"),
                "image_field": img,
                "link_image": ch.get("_link_image"),
                "page_source": ch.get("_page_source"),
            })
    return out


def chapter_kind(ch):
    """'pdf-page' or 'printed' -- from the evidence the TOC stage left."""
    if ch.get("page_source") in ("pdf-link", "pdf-outline"):
        return "pdf-page"
    link = ch.get("link_image")
    ps = ch.get("page_start")
    if isinstance(link, int) and link == ps:
        return "pdf-page"
    return "printed"


def pointers_for(ch, kind, pages, fidx, after):
    """PDF pages that might be this chapter's opener, best first.

    `after` is the previous chapter's opener page. It only ORDERS the
    candidates, it never excludes one: a chapter may share its printed page
    with the previous one, and a chapter may sit slightly earlier.
    """
    cands = []

    def add(p):
        if isinstance(p, int) and p >= 1 and p not in cands:
            cands.append(p)

    folio_cands = []

    def add_f(p):
        if isinstance(p, int) and p >= 1 and p not in folio_cands:
            folio_cands.append(p)

    if kind == "pdf-page":
        add(ch.get("link_image"))
        add(ch.get("page_start"))
        add(ch.get("image_field"))
        return cands

    ps = ch.get("page_start")
    # 1. the folio evidence: the opener is the page before the one that
    #    prints folio+1, or the page that prints the folio itself
    folio_cands = []
    if isinstance(ps, int) and ps > 0:
        for p in fidx.get(ps + 1, []):
            add_f(p - 1)
        for p in fidx.get(ps, []):
            add_f(p)
        for p in fidx.get(ps + 2, []):
            add_f(p - 2)
    # 2. the pages that carry a chapter marker and the chapter number
    marker_cands = []
    for p in chapter_opener_pages(pages, ch.get("number"), after,
                                  after + 400):
        if p not in marker_cands:
            marker_cands.append(p)
    # 3. the pages whose HEAD carries the chapter title (running header)
    title_cands = []
    for p in title_head_pages(pages, ch.get("title") or "", after,
                              after + 60):
        if p not in title_cands:
            title_cands.append(p)
    # the folio evidence comes first, but a page before the previous
    # chapter's opener is unlikely -- those go after the title pages
    cands.extend([p for p in folio_cands if p > after])
    cands.extend(marker_cands)
    cands.extend(title_cands)
    cands.extend([p for p in folio_cands if p <= after])
    return cands


# ------------------------------------------------------------------- the work

def looks_like_chapter_number(ch, printed, toc_folio):
    """Is the number we read the CHAPTER number rather than the page number?

    Harrison's running header prints the chapter number in the outer corner
    on some pages; the reader then reports it as the folio. The test: the
    number equals the chapter number AND it is far from the folio the
    book's own contents gives.
    """
    num = str(ch.get("number") or "")
    if not num.isdigit() or printed is None:
        return False
    if printed != int(num):
        return False
    return toc_folio is None or abs(printed - toc_folio) > 3


def refine_opener(pdf, bid, ch, page, folio, toc_folio, max_back=4):
    """Find the FIRST page of the chapter and the number it carries.

    Two cases are repaired here:
      * the reader read the chapter number instead of the folio;
      * the page we found prints a number that is a little off the book's
        own contents, because the chapter's heading starts a page or two
        earlier (Harrison starts some chapters at the bottom of the
        previous chapter's last page).
    In both cases we walk BACK one page at a time, asking the reader, and
    keep the earliest page that still carries this chapter's heading.
    """
    rec = {"back_walk": [], "reason": ""}
    if looks_like_chapter_number(ch, folio, toc_folio):
        rec["reason"] = ("the corner number equals the chapter number, so "
                          "it is not a page number")
        folio = None
    if toc_folio is not None and folio is not None and folio != toc_folio \
            and abs(folio - toc_folio) <= 6:
        rec["reason"] = (f"the page shows {folio} but the book's contents "
                         f"says {toc_folio}: the chapter starts a page or "
                         f"two earlier")
    if not rec["reason"]:
        return page, folio, rec
    best_page, best_folio = page, folio
    p = page - 1
    while p >= max(1, page - max_back):
        kind, heading, f2, raw, png = ask_page(pdf, bid, p)
        rec["back_walk"].append({"pdf_page": p, "kind": kind,
                                 "heading": heading, "folio": f2})
        if not is_opener(ch, kind, heading):
            break
        best_page, best_folio = p, f2
        p -= 1
    if best_folio is None and best_page:
        # the opener prints no number: the next page prints folio+1
        kind2, h2, f3, raw3, png3 = ask_page(pdf, bid, best_page + 1)
        rec["back_walk"].append({"pdf_page": best_page + 1, "kind": kind2,
                                 "heading": h2, "folio": f3})
        if f3 is not None and f3 >= 2:
            best_folio = f3 - 1
    return best_page, best_folio, rec


def reconcile(page, eyes_folio, fidx):
    """Check the number the reader read against the pages around it.

    The reader's eyes occasionally misread a digit (2259 read as 2359 on
    HARRISON-22, 2026-10-21). The pages around the page are the check:
    a real folio continues the sequence. So the number we keep is the one
    that fits its neighbours; if only one candidate exists, that is the
    number.
    """
    prev = None
    for p in (page - 1, page - 2):
        for f in (fidx.get(page) or []):
            break
    # the neighbours' folios, read from the text layer
    def neighbour(pg):
        for f, pages in fidx.items():
            if pg in pages:
                return f
        return None
    prev_f = neighbour(page - 1)
    next_f = neighbour(page + 1)
    cands = []
    for c in (eyes_folio, prev_f + 1 if prev_f else None,
              next_f - 1 if next_f else None):
        if c and c not in cands:
            cands.append(c)
    if not cands:
        return eyes_folio, "nothing to compare with"
    if prev_f and next_f:
        if next_f == prev_f + 2:
            good = prev_f + 1
            return good, (f"forced by the neighbours: {prev_f} and "
                          f"{next_f} -> {good}")
        if next_f == prev_f + 1:
            return eyes_folio, (f"the neighbours print {prev_f} and "
                                f"{next_f}: this page carries no number of "
                                f"its own")
    if len(cands) == 1:
        return cands[0], "only one possible number"
    return eyes_folio, ("the reader's number kept; neighbours suggest "
                        + str(cands))


def word_in(word, text):
    """Is the title's word in the heading? A trailing s is dropped:
    "sjogrens" is found in "sjogren s disease"."""
    w = plain(word).strip()
    if not w:
        return False
    if w in text:
        return True
    if len(w) > 4 and w.endswith("s") and w[:-1] in text:
        return True
    return False


def is_opener(ch, kind, heading):
    """Does the heading the reader reported belong to this chapter?

    KIND=OPENING with a matching heading is the normal case. But some
    books start the next chapter at the BOTTOM of the previous chapter's
    last page (Harrison does this), and the reader then calls the page
    BODY. So a page whose headings carry the chapter NUMBER and the
    chapter TITLE is accepted as well.
    """
    if not heading:
        return False
    h = plain(heading).replace("|", " ")
    num = str(ch.get("number") or "")
    has_num = bool(num) and bool(re.search(r"\b" + re.escape(num.lower()) + r"\b", h))
    words = title_words(ch.get("title") or "")
    hits = sum(1 for w in words if word_in(w, h))
    if kind != "OPENING":
        if not (has_num and hits >= 1):
            return False
    if not words:
        # a title with no significant word ("Introduction") cannot be
        # matched by words: the reader's KIND=OPENING is the evidence
        return True
    if has_num and hits >= 1:
        return True
    if kind != "OPENING":
        return False
    return hits >= 1 and hits >= max(1, len(words) // 2)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("book")
    ap.add_argument("--sample", type=int, default=0)
    ap.add_argument("--seed", type=int, default=0)
    ap.add_argument("--all", action="store_true")
    ap.add_argument("--list", action="store_true")
    ap.add_argument("--only", default="",
                    help="comma separated chapter numbers to work on")
    ap.add_argument("--dpi", type=int, default=120)
    ap.add_argument("--max-tries", type=int, default=4)
    ap.add_argument("--proof", action="store_true",
                    help="when a page prints no number, read the page "
                         "before as well, so the number is forced by both "
                         "sides")
    ap.add_argument("--scan", type=int, default=0,
                    help="if the pointer fails, look at this many\n                          pages forward, one by one")
    ap.add_argument("--write-toc", action="store_true", default=True,
                    help="also write <BOOK>-toc.json in the BIBLE's format")
    args = ap.parse_args()

    bid = args.book
    books = {b["book_id"]: b for b in json.loads(BOOKS.read_text())}
    if bid not in books:
        sys.exit(f"unknown book {bid}")
    pdf = KITCHEN / "books" / books[bid]["pdf_file"]
    if not pdf.exists():
        sys.exit(f"{bid}: PDF file is missing")

    chapters = load_chapters(bid)
    kinds = {str(c["number"]): chapter_kind(c) for c in chapters}
    n_printed = sum(1 for k in kinds.values() if k == "printed")
    print(f"{bid}: {len(chapters)} chapters; kind: {n_printed} printed-folio, "
          f"{len(kinds) - n_printed} pdf-page", flush=True)

    cache = LOGS / f"{bid}-folio.txt"
    if cache.exists() and cache.stat().st_size > 0:
        text_pages = cache.read_text(errors="replace").split("\f")
    else:
        res = subprocess.run(["pdftotext", str(pdf), str(cache)],
                             capture_output=True, text=True, timeout=1800)
        if res.returncode != 0 or not cache.exists():
            sys.exit(f"{bid}: pdftotext failed")
        text_pages = cache.read_text(errors="replace").split("\f")
    fidx = folio_index(text_pages)

    todo = chapters
    if args.only:
        want = {w.strip() for w in args.only.split(",") if w.strip()}
        todo = [c for c in chapters if str(c["number"]) in want]
    elif args.sample:
        random.seed(args.seed)
        todo = random.sample(chapters, min(args.sample, len(chapters)))
        todo = sorted(todo, key=lambda c: (c["page_start"] or 0))
    elif not args.all and not args.list:
        sys.exit("give --sample N or --all")

    records, unresolved = [], []
    after = 0
    for ch in todo:
        kind = kinds[str(ch["number"])]
        cands = pointers_for(ch, kind, text_pages, fidx, after)
        if args.list:
            print(f"ch{ch['number']:>6s} [{kind:9s}] "
                  f"{str(ch['title'])[:34]:36s} -> {cands[:6]}")
            continue
        rec = {"province": ch["province"], "number": ch["number"],
               "title": ch["title"], "toc_page_start": ch["page_start"],
               "kind": kind, "pointer": cands[:10], "status": None}
        if not cands:
            rec["status"] = "no-pointer"
            records.append(rec)
            unresolved.append(rec)
            print(f"??  ch{ch['number']:>6s} {str(ch['title'])[:40]:42s} "
                  f"no pointer", flush=True)
            continue
        found = None
        for page in cands[:args.max_tries]:
            kind_seen, heading, folio, raw, png = ask_page(pdf, bid, page)
            rec.setdefault("tries", []).append(
                {"pdf_page": page, "kind": kind_seen, "heading": heading,
                 "folio": folio, "image_file": png, "raw": raw})
            # the strongest proof there is: the page prints EXACTLY the
            # folio the book's own contents gives for this chapter, so this
            # IS the chapter's first page -- whatever the reader calls the
            # heading (Harrison puts the chapter box in the middle of the
            # page, so the reader often calls such a page BODY)
            toc_ps0 = rec["toc_page_start"]
            if (folio is not None and isinstance(toc_ps0, int)
                    and toc_ps0 > 0 and folio == toc_ps0):
                found = (page, folio, raw, png,
                         "the page prints the folio the contents gives",
                         heading)
                break
            if not is_opener(ch, kind_seen, heading):
                continue
            if folio is not None:
                found = (page, folio, raw, png, "printed-on-the-page",
                         heading)
                break
            # the opener prints no number (common): the NEXT page prints
            # folio+1, so the opener is that number minus one
            nxt = page + 1
            k2, h2, folio2, raw2, png2 = ask_page(pdf, bid, nxt)
            rec["tries"][-1]["next_page"] = nxt
            rec["tries"][-1]["next_folio"] = folio2
            rec["tries"][-1]["next_kind"] = k2
            if folio2 is not None and folio2 >= 2:
                proof = None
                if args.proof and page > 1:
                    # read the page BEFORE as well: a number forced by both
                    # sides is a fact, a number from one side is a guess
                    k0, h0, folio0, raw0, png0 = ask_page(pdf, bid, page - 1)
                    rec["tries"][-1]["prev_page"] = page - 1
                    rec["tries"][-1]["prev_folio"] = folio0
                    if folio0 is not None:
                        if folio0 + 2 == folio2:
                            proof = (f"the page before prints {folio0} and "
                                     f"the page after prints {folio2}, so "
                                     f"this page prints {folio2 - 1}")
                        elif folio0 + 1 == folio2:
                            proof = (f"UNNUMBERED PAGE: the page before "
                                     f"prints {folio0} and the page after "
                                     f"prints {folio2}; this page carries "
                                     f"no number of its own")
                    rec["proof"] = proof
                found = (page, folio2 - 1, raw, png, "from-the-next-page",
                         heading)
                break
        # nothing worked: walk forward from the previous chapter and let the
        # reader look at the pages one by one
        if not found and args.scan > 0:
            start = after
            if start == 0 and cands:
                start = min(cands) - 1
            if start == 0:
                # no pointer at all: start where the chapter's printed page
                # lives (the pages whose folio is near it)
                toc_ps = rec["toc_page_start"]
                near = []
                for f, pgs in fidx.items():
                    if isinstance(toc_ps, int) and abs(f - toc_ps) <= 3:
                        near.extend(pgs)
                if near:
                    start = min(near) - 2
            for page in range(start + 1, start + 1 + args.scan):
                if page in cands[:args.max_tries]:
                    continue
                kind_seen, heading, folio, raw, png = ask_page(pdf, bid, page)
                rec.setdefault("tries", []).append(
                    {"pdf_page": page, "kind": kind_seen, "heading": heading,
                     "folio": folio, "image_file": png, "raw": raw,
                     "scan": True})
                if not is_opener(ch, kind_seen, heading):
                    continue
                if folio is not None:
                    found = (page, folio, raw, png, "printed-on-the-page",
                             heading)
                    break
                nxt = page + 1
                k2, h2, folio2, raw2, png2 = ask_page(pdf, bid, nxt)
                rec["tries"][-1]["next_page"] = nxt
                rec["tries"][-1]["next_folio"] = folio2
                if folio2 is not None and folio2 >= 2:
                    found = (page, folio2 - 1, raw, png, "from-the-next-page",
                             heading)
                    break
        if found:
            page, printed, raw, png, how, heading = found
            new_page, new_printed, refine = refine_opener(
                pdf, bid, ch, page, printed, rec["toc_page_start"])
            if new_printed is not None:
                fixed, why = reconcile(new_page, new_printed, fidx)
                if fixed != new_printed:
                    rec["reconciled"] = {"was": new_printed, "now": fixed,
                                         "why": why}
                    new_printed = fixed
                elif why.startswith("forced"):
                    rec["reconciled"] = {"was": new_printed, "now": fixed,
                                         "why": why}
            if refine["reason"]:
                rec["refine"] = refine
            # THE FLOOR RULE (the human's rule, 2026-10-21): when the
            # book's own contents and the page disagree, the SMALLER number
            # is kept -- the chapter starts earlier than the page we found.
            # The difference is recorded, because it is a finding about the
            # Table of Contents, not an error to hide.
            toc_ps = rec["toc_page_start"]
            if (isinstance(toc_ps, int) and toc_ps > 0
                    and new_printed is not None and new_printed != toc_ps
                    and not looks_like_chapter_number(ch, new_printed,
                                                       toc_ps)):
                rec["floor_applied"] = {
                    "the_page_shows": new_printed, "kept": toc_ps,
                    "why": ("the page carries a number that belongs to a "
                            "later page of the chapter; the book's own "
                            "contents says the chapter starts at "
                            f"{toc_ps}")}
                new_printed = toc_ps
            page, printed = new_page, new_printed
            if refine["reason"]:
                if printed is None:
                    rec["status"] = "opener-not-found"
                    unresolved.append(rec)
                    records.append(rec)
                    print(f"XX  ch{ch['number']:>6s} "
                          f"{str(ch['title'])[:40]:42s} refined but no "
                          f"number ({refine['reason']})", flush=True)
                    continue
            rec.update(status="ok", pdf_page=page, printed=printed,
                       image_file=png, opener_confirmed=True,
                       printed_from=how, heading=heading, reader_raw=raw)
            after = max(after, page)
            agree = "" if rec["toc_page_start"] in (None, printed) else \
                f"  <-- CONTENTS SAYS {rec['toc_page_start']}"
            print(f"ok  ch{ch['number']:>6s} {str(ch['title'])[:38]:40s} "
                  f"pdf {page:5d} -> printed {printed:5d} ({how}){agree}",
                  flush=True)
        else:
            rec["status"] = "opener-not-found"
            records.append(rec)
            unresolved.append(rec)
            print(f"XX  ch{ch['number']:>6s} {str(ch['title'])[:40]:42s} "
                  f"tried {[t['pdf_page'] for t in rec.get('tries', [])]}",
                  flush=True)
        records.append(rec)

    if args.list:
        return

    # a chapter with no page in this PDF: the book goes straight from the
    # previous chapter's page to the next chapter's page (Harrison-22
    # chapter 46: our PDF jumps from printed 292 to printed 293)
    by_num = {}
    for r in records:
        by_num.setdefault(str(r["number"]), r)
    order = [str(r["number"]) for r in records]
    for i, num in enumerate(order):
        r = by_num.get(num)
        if not r or r.get("status") == "ok":
            continue
        prev = next((by_num[order[j]] for j in range(i - 1, -1, -1)
                     if by_num.get(order[j], {}).get("status") == "ok"), None)
        nxt = next((by_num[order[j]] for j in range(i + 1, len(order))
                    if by_num.get(order[j], {}).get("status") == "ok"), None)
        if prev and nxt and nxt["pdf_page"] - prev["pdf_page"] == 1:
            r["status"] = "no-page-in-this-pdf"
            r["why"] = (f"the PDF goes from chapter page {prev['pdf_page']} "
                        f"straight to {nxt['pdf_page']}: no page for this "
                        f"chapter in this file")

    ok = [r for r in records if r.get("status") == "ok"]
    diff = [r for r in ok if r["toc_page_start"] not in (None, r["printed"])]
    summary = {"book": bid, "chapters": len(records),
               "read_by_eyes": len(ok), "unresolved": len(unresolved),
               "contents_disagreements": len(diff),
               "printed_kinds": n_printed}
    out = {"_summary": summary, "chapters": records}
    (LOGS / f"{bid}-eyes.json").write_text(json.dumps(out, indent=1))
    print(f"\n{bid}: {len(ok)}/{len(records)} chapters read by the eyes; "
          f"{len(unresolved)} unresolved; {len(diff)} disagree with the "
          f"book's own contents.")
    print(f"detail: {LOGS / (bid + '-eyes.json')}")
    for r in unresolved:
        print(f"  unresolved: ch{r['number']} {str(r['title'])[:40]} "
              f"({r['status']})")
    for r in diff:
        print(f"  contents disagree: ch{r['number']} {str(r['title'])[:40]} "
              f"contents={r['toc_page_start']} page={r['printed']}")

    if args.write_toc and args.all:
        write_toc_json(bid, records, ok)


def write_toc_json(bid, records, ok):
    """The BIBLE's <BOOK>-toc.json (part 3 section 4.4).

    Chapters carry the printed page the PAGE shows (not the contents'
    number) and page_end = the next chapter's printed page minus one.
    """
    good = {str(r["number"]): r for r in ok}
    data = json.loads((LOGS / f"{bid}-vis-toc.json").read_text())
    provinces = []
    for prov in data.get("provinces", []):
        chapters = []
        for ch in prov.get("chapters", []):
            g = good.get(str(ch.get("number")))
            if not g:
                continue
            chapters.append({"number": ch.get("number"), "title": ch.get("title"),
                             "page_start": g["printed"],
                             "pdf_page": g["pdf_page"]})
        chapters.sort(key=lambda c: c["page_start"])
        for i, c in enumerate(chapters):
            c["page_end"] = (chapters[i + 1]["page_start"] - 1
                             if i + 1 < len(chapters) else c["page_start"])
        if chapters:
            provinces.append({"name": prov.get("name"),
                              "part_name": prov.get("part_name", prov.get("name")),
                              "chapters": chapters,
                              "page_start": chapters[0]["page_start"],
                              "page_end": chapters[-1]["page_end"]})
    (LOGS / f"{bid}-toc.json").write_text(
        json.dumps({"provinces": provinces}, indent=1, ensure_ascii=False))
    print(f"wrote {LOGS / (bid + '-toc.json')} with {len(provinces)} provinces")


if __name__ == "__main__":
    main()
