# kitchen/page_offset.py -- BIBLE part 3, section 4.6 (Step A3).
#
#   printed_page = image_number - page_offset
#
# Every page number we have stored so far is a PDF page (what the computer
# counts). The number printed on the paper starts somewhere else, and the gap
# is page_offset. EVERY citation depends on it, so it is measured from the
# book's OWN pages and never guessed.
#
# Method (the direct one): our geography already knows the exact PDF page of
# every chapter, so we open that page and read the folio the book itself
# prints in its running header or footer. offset = pdf_page - printed_folio.
#
# HONESTY RULES:
#   - A page whose folio cannot be read yields NO offset. It is reported, not
#     filled in (Law 2, Law 11).
#   - If the sampled pages do not agree, the book has more than one numbering
#     sequence and a single offset is NOT printed as if it were certain. The
#     spread is reported and the book is left for a human decision, which is
#     what BIBLE 3.4.6 asks for.
#
# ZERO model calls: this reads the PDF text layer only.
#
#   python kitchen/page_offset.py <BOOK_ID>          one book, verbose
#   python kitchen/page_offset.py --all             every book, one line each
#   python kitchen/page_offset.py --all --save      write the agreed offsets
#                                                   into kitchen/books.json

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

SAMPLES = 24          # pages spread through the body of the book
SEARCH = 3            # how far forward to look for a printed folio

# A folio may be "412", "CD102", "A-77", "S12-4", "412." It is printed either
# alone on its own line or at the end of a running header. Section and chapter
# numbers look identical, so they are NOT filtered here by guessing: the
# correct offset is the one most pages agree on (see score_offsets).
FOLIO = re.compile(r"(?<![A-Za-z0-9])([A-Za-z]{0,4}[-–]?\d{1,4})\s*$")
# running heads that are never a folio
NOTFOLIO = re.compile(r"^\s*(SECTION|CHAPTER|PART|TABLE|FIGURE|Fig\.|CASE|CASE\s)", re.I)


def chapter_pages(bid):
    """PDF pages of the chapters, from our own geography. Never invented."""
    for name in (f"{bid}-vis-toc.json", f"{bid}-toc.json"):
        path = LOGS / name
        if not path.exists():
            continue
        try:
            data = json.loads(path.read_text())
        except json.JSONDecodeError:
            continue
        pages = []
        stack = [data]
        while stack:
            node = stack.pop()
            if isinstance(node, dict):
                for key in ("page_start", "page", "first_page"):
                    v = node.get(key)
                    if isinstance(v, int):
                        pages.append(v)
                stack.extend(node.values())
            elif isinstance(node, list):
                stack.extend(node)
        return sorted({p for p in pages if p > 0})
    return []


def printed_numbers(text):
    """Every number the page could be using as its own folio."""
    lines = [l.strip() for l in text.splitlines() if l.strip()]
    if not lines:
        return []
    edges = lines[:SEARCH] + lines[-SEARCH:]
    found = []
    for line in edges:
        if NOTFOLIO.match(line):
            continue
        bare = re.fullmatch(r"(\d{1,4})", line)
        if bare:
            found.append(int(bare.group(1)))
            continue
        m = FOLIO.search(line)
        if m:
            digits = re.findall(r"\d+", m.group(1))
            if digits:
                found.append(int(digits[-1]))
    return found


def score_offsets(per_page):
    """Let the pages vote. Every page offers the offsets it could be saying;
    the real one is the value most pages agree on. A section number or a
    copyright year produces a DIFFERENT offset on every page, so it can never
    win the vote -- that is why no guessing is needed.

    Returns (best_offset, votes_for_best, pages_with_any_candidate)."""
    votes = Counter()
    for pdf_page, nums in per_page:
        for f in set(nums):
            if 1 <= f <= 9999:
                votes[pdf_page - f] += 1
    if not votes:
        return None, 0, 0
    best, n = votes.most_common(1)[0]
    return best, n, len(per_page)


def sample_pages(pdf, pages):
    """Read the sampled pages once and collect their folio candidates.
    The front and back matter are skipped on purpose: unnumbered roman-numeral
    front matter carries a different sequence and would only add noise."""
    lo = int(len(pages) * 0.05)
    hi = max(lo + 1, int(len(pages) * 0.98))
    body = pages[lo:hi]
    n = len(body)
    picks = [body[min(n - 1, round(i * (n - 1) / (SAMPLES - 1)))]
             for i in range(SAMPLES)]
    per_page = []
    for p in sorted(set(picks)):
        try:
            out = subprocess.run(
                ["pdftotext", "-f", str(p), "-l", str(p), str(pdf), "-"],
                capture_output=True, text=True, timeout=60).stdout
        except subprocess.TimeoutExpired:
            continue
        nums = printed_numbers(out)
        if nums:
            per_page.append((p, nums))
    return per_page


def sample_offsets(pdf, pages):
    """(offsets, rows) for pages spread through the book."""
    per_page = sample_pages(pdf, pages)
    best, votes, offered = score_offsets(per_page)

    rows = []
    offsets = []
    for pdf_page, nums in per_page:
        off = pdf_page - min(set(nums), key=lambda f: abs(f - (pdf_page - best))) \
            if best is not None else None
        if off == best:
            offsets.append(off)
        printed = pdf_page - off if off is not None else None
        rows.append((pdf_page, printed, off))

    # report every distinct offset the book could be saying, so a human can
    # see the disagreement instead of trusting one number blindly
    allvotes = Counter()
    for pdf_page, nums in per_page:
        for f in set(nums):
            if 1 <= f <= 9999:
                allvotes[pdf_page - f] += 1
    return offsets, rows, best, votes, offered, allvotes


def main(argv):
    books = json.loads(BOOKS.read_text())
    by_id = {b["book_id"]: b for b in books}

    args = [a for a in argv if not a.startswith("--")]
    want_all = "--all" in argv
    do_save = "--save" in argv
    targets = [a for a in args if a in by_id]
    if not want_all and not targets:
        sys.exit("give a BOOK_ID, or --all")

    for bid in (by_id.keys() if want_all else targets):
        rec = by_id[bid]
        pdf = KITCHEN / "books" / rec["pdf_file"]
        if not pdf.exists():
            print(f"{bid:26s} MISSING PDF")
            continue
        pages = chapter_pages(bid)
        if not pages:
            print(f"{bid:26s} NO CHAPTER PAGES YET")
            continue
        offsets, rows, best, votes, offered, allvotes = sample_offsets(pdf, pages)
        if best is None:
            print(f"{bid:26s} no printed folio could be read on any sample")
            continue
        agree = len(offsets)
        state = "OK " if agree >= max(2, (offered + 1) // 2) else "MIX"
        print(f"{bid:26s} {state} offset={best} "
              f"(agree {agree}/{offered})  pdf {pages[0]}..{pages[-1]}"
              f"   runners-up: "
              f"{[o for o, _ in allvotes.most_common(4)[1:]]}")
        if not want_all:
            print("    " + "  ".join(
                f"pdf{p}=printed{f}" if f else f"pdf{p}=?" for p, f, o in rows))
            rec["page_offset"] = best if state == "OK " else None

    if do_save:
        BOOKS.write_text(json.dumps(books, indent=2, ensure_ascii=False))
        print("\nwrote kitchen/books.json")


if __name__ == "__main__":
    main(sys.argv[1:])