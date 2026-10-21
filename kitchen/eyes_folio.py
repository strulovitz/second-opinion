#!/usr/bin/env python3
"""kitchen/eyes_folio.py -- the PRINTED page of every chapter, read by the eyes.

WHAT THIS IS
    For every chapter of one book we need two facts (Law 2):
      1. the picture of the page where the chapter BEGINS, and
      2. the page number the book PRINTS for that page.
    This script produces both by showing pages to the free local READER
    (Qwen 3.8 27B, TIER FREE) as pictures and asking it the way a human
    would be asked:
        OPENER: YES / NO  -- does this page begin the chapter?
        FOLIO: <number>   -- what number is printed in the corner?
    The reader's answer is the answer. The PDF TEXT layer is used ONLY to
    point at WHICH page to show (a guess for the reader to correct), never
    as the value we store. Every stored number therefore comes from a
    picture that is kept on disk next to the record.

    Nothing is invented: a page that prints no number is recorded as such,
    a page where the chapter does not begin is recorded as a disagreement.
    Both are reported, never hidden.

HOW THE POINTER WORKS (the text layer only points)
    Two kinds of book exist (decided per chapter from the book's own
    evidence, never from its name):
      'pdf-page'  the TOC stage stored a PDF page number (bookmark/link
                  source). The chapter's first page is that page.
      'printed'   the TOC stage stored the folio the book's own contents
                  prints. The first page that PRINTS folio+1 is the page
                  after the opener, so the opener is the page before it.
    Chapters are walked in book order, so a page pointer must always be
    later than the previous chapter's page -- that keeps front-matter
    noise out.

MODES
    python kitchen/eyes_folio.py THOMPSON-2023 --sample 6      # random 6
    python kitchen/eyes_folio.py THOMPSON-2023 --all           # every chapter
    python kitchen/eyes_folio.py THOMPSON-2023 --list          # pointers only

OUTPUT
    kitchen/logs/<BOOK>-eyes.json      (records + summary)
    kitchen/logs/eyes-render/<BOOK>/   (the pictures)

    Zero bytes are written to any geography file, to books.json or to Neo4j.
"""

import argparse
import json
import random
import re
import statistics
import subprocess
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
    "Answer with EXACTLY two lines and nothing else:\n"
    "OPENER: YES   -- if a chapter heading visibly BEGINS on this page\n"
    "                (the chapter number and/or its title appear as a heading)\n"
    "OPENER: NO    -- otherwise\n"
    "FOLIO: <n>    -- the PAGE NUMBER the book prints in a corner of this page\n"
    "                (header or footer). It is NOT a chapter number, NOT a\n"
    "                section number, NOT a table or figure number.\n"
    "FOLIO: NONE   -- if this page prints no page number anywhere.\n"
    "Look at all four corners and both margins before you answer.\n"
    "Do not stop early."
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
    opener, folio = None, None
    for line in (ans or "").splitlines():
        s = line.strip()
        if s.upper().startswith("OPENER:"):
            opener = "YES" in s.upper()
        elif s.upper().startswith("FOLIO:"):
            tail = s.split(":", 1)[1].strip()
            head = tail.split()[0] if tail.split() else ""
            if head.isdigit():
                folio = int(head)
    return opener, folio


def ask_page(pdf, book, page, chapter, what):
    """Show one page to the reader; return (opener, folio, raw, image file)."""
    png = render(pdf, book, page)
    msg = (f"This is PDF page {page} of the book {book}. "
           f"Chapter {chapter['number']} \"{chapter['title']}\" is supposed to "
           f"BEGIN on this page. {what}")
    ans = ask(SYSTEM, msg, images=[png], max_tokens=600, expect_json=False,
              retries=2, no_reasoning=True)
    opener, folio = parse(ans)
    return opener, folio, (ans or "").strip()[:300], png.name


# --------------------------------------------------------------- the pointer

BARE = re.compile(r"^(\d{1,5})$")
ANNOT = re.compile(r"(\d{1,5})\s*\.\s*e\d{1,4}(?![\d.])")
CHAPTER_MARK = re.compile(r"c\s*h\s*a\s*p\s*t\s*e\s*r", re.I)


def lines_of(pages, i):
    if i < 1 or i > len(pages):
        return []
    return [l.strip() for l in pages[i - 1].splitlines() if l.strip()]


def folio_of(pages, i):
    """The page number printed on PDF page i, read from the text layer.

    Only the first two and the last two lines are trusted: those are where
    a folio sits. A running header line ("THOMPSON AND THOMPSON ...") is
    not a folio, and a bare number further down is a table cell.
    """
    lines = lines_of(pages, i)
    if not lines:
        return None
    for line in lines:
        m = ANNOT.search(line)
        if m:
            return int(m.group(1))
    for line in lines[:2] + lines[-2:]:
        m = BARE.match(line)
        if m:
            return int(m.group(1))
    return None


def title_words(title):
    words = re.findall(r"[A-Za-z][A-Za-z'-]{3,}", title or "")
    stop = {"the", "and", "for", "from", "with", "into", "their", "this",
            "that", "what", "when", "how", "does", "are", "was", "were",
            "into", "clinical", "management", "diagnosis", "treatment",
            "chapter", "part", "section", "introduction", "overview",
            "approach", "update", "edition"}
    return [w.lower() for w in words if w.lower() not in stop]


def opener_signature(pages, i):
    """Does PDF page i look like the first page of a chapter?"""
    lines = lines_of(pages, i)
    if not lines:
        return False, set()
    head = " ".join(lines[:8]).lower()
    has_mark = bool(CHAPTER_MARK.search(" ".join(lines[:4]).replace(" ", "")
                                         .lower()) or CHAPTER_MARK.search(head))
    return has_mark, set(title_words(head))


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
            link = ch.get("_link_image")
            out.append({
                "province": prov.get("name"),
                "number": ch.get("number"),
                "title": ch.get("title"),
                "page_start": ch.get("page_start"),
                "image_field": img,
                "link_image": link,
                "page_source": ch.get("_page_source"),
            })
    return out


def chapter_kind(ch):
    """'pdf-page' or 'printed' -- from the evidence the TOC stage left."""
    src = ch.get("page_source")
    if src in ("pdf-link", "pdf-outline"):
        return "pdf-page"
    link = ch.get("link_image")
    ps = ch.get("page_start")
    if isinstance(link, int) and link == ps:
        return "pdf-page"
    if ch.get("image_field") is not None and ch.get("image_field") != ps:
        return "printed"
    return "printed"


def role_of(chapters):
    """Is `_image` the chapter's OWN page, or the contents page it was read on?

    Decided from the book's own numbers: the median of (_image - page_start).
    toc_openers / toc_outline store the chapter's own page (image is at or
    after the number); toc_vision stores the CONTENTS page it was read from
    (image is before the printed number it carries).
    """
    diffs = [c["image_field"] - c["page_start"] for c in chapters
             if isinstance(c["image_field"], int)
             and isinstance(c["page_start"], int)]
    if len(diffs) < 5:
        return "unknown", None
    med = statistics.median(diffs)
    return ("chapter-page" if med >= 0 else "contents-page"), med


def pointers_for(ch, kind, pages, fidx, after):
    """PDF pages that might be this chapter's first page, best first."""
    cands = []

    def add(p):
        if isinstance(p, int) and p >= 1 and p > after and p not in cands:
            cands.append(p)

    if kind == "pdf-page":
        add(ch.get("link_image"))
        add(ch.get("page_start"))
        add(ch.get("image_field"))
        return cands

    # 'printed': page_start is the folio the book's contents prints.
    ps = ch.get("page_start")
    if isinstance(ps, int) and ps > 0:
        for p in fidx.get(ps + 1, []):
            add(p - 1)          # the opener is the page before it
        for p in fidx.get(ps, []):
            add(p)              # or the opener itself prints the folio
        for p in fidx.get(ps + 2, []):
            add(p - 2)
    # last resort: pages whose heading looks like this chapter's opener
    words = set(title_words(ch.get("title") or ""))
    if words:
        for i in range(after + 1, len(pages) + 1):
            has_mark, hw = opener_signature(pages, i)
            if has_mark and (words & hw):
                add(i)
    return cands


# ------------------------------------------------------------------- the work

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("book")
    ap.add_argument("--sample", type=int, default=0,
                    help="check a random sample of N chapters")
    ap.add_argument("--seed", type=int, default=0)
    ap.add_argument("--all", action="store_true", help="every chapter")
    ap.add_argument("--list", action="store_true",
                    help="only show the pointers, ask nobody")
    ap.add_argument("--dpi", type=int, default=120)
    ap.add_argument("--max-tries", type=int, default=3)
    args = ap.parse_args()

    bid = args.book
    books = {b["book_id"]: b for b in json.loads(BOOKS.read_text())}
    if bid not in books:
        sys.exit(f"unknown book {bid}")
    pdf = KITCHEN / "books" / books[bid]["pdf_file"]
    if not pdf.exists():
        sys.exit(f"{bid}: PDF file is missing")

    chapters = load_chapters(bid)
    role, med = role_of(chapters)
    kinds = {}
    for ch in chapters:
        kinds[ch["number"]] = chapter_kind(ch)
    n_printed = sum(1 for k in kinds.values() if k == "printed")
    print(f"{bid}: {len(chapters)} chapters; _image role = {role}; "
          f"kind: {n_printed} printed-folio, {len(kinds) - n_printed} pdf-page",
          flush=True)

    # the text layer, used ONLY to point at pages
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
    if args.sample:
        random.seed(args.seed)
        todo = random.sample(chapters, min(args.sample, len(chapters)))
    elif not args.all and not args.list:
        sys.exit("give --sample N or --all")

    # a random sample is still walked in book order, so the page pointers
    # (which use "later than the previous chapter") stay correct
    if args.sample:
        todo = sorted(todo, key=lambda c: (c["page_start"] or 0))

    records, unresolved = [], []
    after = 0
    for ch in todo:
        kind = kinds[ch["number"]]
        cands = pointers_for(ch, kind, text_pages, fidx, after)
        if args.list:
            print(f"ch{ch['number']:>6s} [{kind:9s}] "
                  f"{str(ch['title'])[:36]:38s} -> {cands[:6]}")
            continue
        rec = {"province": ch["province"], "number": ch["number"],
               "title": ch["title"], "page_start": ch["page_start"],
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
            opener, folio, raw, png = ask_page(
                pdf, bid, page, ch,
                "Tell me whether the chapter begins here and what page number "
                "the book prints in the corner.")
            rec.setdefault("tries", []).append(
                {"pdf_page": page, "opener": opener, "folio": folio,
                 "image_file": png, "raw": raw})
            if not opener:
                continue
            if folio is not None:
                found = (page, folio, raw, png, "printed-on-the-page")
                break
            # the opener prints no number (common): the NEXT page prints
            # folio+1, so the opener is that number minus one
            nxt = page + 1
            _, folio2, raw2, png2 = ask_page(
                pdf, bid, nxt, ch,
                "This is the page AFTER the chapter's first page. Just tell me "
                "what page number the book prints in the corner of it.")
            rec["tries"][-1]["next_page"] = nxt
            rec["tries"][-1]["next_folio"] = folio2
            rec["tries"][-1]["next_image"] = png2
            if folio2 is not None and folio2 >= 2:
                found = (page, folio2 - 1, raw, png, "from-the-next-page")
                break
        if found:
            page, printed, raw, png, how = found
            rec.update(status="ok", pdf_page=page, printed=printed,
                       image_file=png, opener_confirmed=True,
                       printed_from=how, reader_raw=raw)
            after = max(after, page)
            print(f"ok  ch{ch['number']:>6s} {str(ch['title'])[:40]:42s} "
                  f"pdf {page:5d} -> printed {printed:5d}  ({how})", flush=True)
        else:
            rec["status"] = "opener-not-found"
            records.append(rec)
            unresolved.append(rec)
            print(f"XX  ch{ch['number']:>6s} {str(ch['title'])[:40]:42s} "
                  f"tried {rec.get('tries', [])}", flush=True)
        records.append(rec)

    if args.list:
        return

    ok = [r for r in records if r.get("status") == "ok"]
    summary = {"book": bid, "chapters": len(records),
               "read_by_eyes": len(ok), "unresolved": len(unresolved),
               "role": role, "role_median": med,
               "printed_kinds": n_printed}
    out = {"_summary": summary, "chapters": records}
    (LOGS / f"{bid}-eyes.json").write_text(json.dumps(out, indent=1))
    print(f"\n{bid}: {len(ok)}/{len(records)} chapters read by the eyes; "
          f"{len(unresolved)} unresolved.")
    print(f"detail: {LOGS / (bid + '-eyes.json')}")
    for r in unresolved:
        print(f"  unresolved: ch{r['number']} {str(r['title'])[:40]} "
              f"({r['status']})")


if __name__ == "__main__":
    main()
