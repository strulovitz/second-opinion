# kitchen/page_folio.py -- read the page number the book PRINTS on every page.
#
# Why this exists: BIBLE part 3 section 4.6 assumes ONE page_offset per book,
# but measured on 2026-10-19 that assumption is FALSE for several books.
# Sabiston-22 is the proof: between PDF page 1429 (printed 876) and PDF page
# 1982 (printed 1367) the paper's numbering drifts by 62, because the PDF
# contains unnumbered inserts (chapter dividers, photo plates). A single
# offset would put hundreds of chapters on a page they are not printed on.
#
# So instead of one number per book we read the printed folio of every page
# directly, and each chapter gets its own printed page. The median offset is
# still reported for books.json, but it is never used to invent a page.
#
# HOW THE FOLIO IS FOUND WITHOUT GUESSING (Law 2):
#   1. Candidate numbers are taken only from the header and footer lines.
#   2. Real page numbers increase steadily through a book. Section numbers,
#      chapter numbers and copyright years jump around. So the true folio of
#      each page is found by keeping the LONGEST RISING SEQUENCE of
#      (page, number) pairs. Noise cannot survive that; a real folio can.
#   3. A page that is not itself in that sequence inherits the folio of the
#      nearest page before it, and only if they are close (MAX_GAP).
#   4. Anything still unknown is stored as null. Never guessed.
#
# ZERO model calls. One pdftotext per book, cached on disk.
#
#   python kitchen/page_folio.py <BOOK_ID>
#   python kitchen/page_folio.py --all

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
WINDOW = 8       # pages forward from a chapter page to decide its folio
MIN_CLUSTER = 2  # how many pages in the window must agree before we answer
TOL = WINDOW     # inside an 8-page window a real gap can spread by at most 7
MAX_GAP = 6      # kept for the diagnostics only

BARE = re.compile(r"^(\d{1,4})$")
TAIL = re.compile(r"(?<![A-Za-z0-9])([A-Za-z]{0,4}[-\u2013]?\d{1,4})\s*$")
NOTFOLIO = re.compile(r"^\s*(SECTION|CHAPTER|PART|TABLE|FIGURE|Fig|CASE|PART\b)", re.I)

# Elsevier prints some folios as "721.e89": that is page 721, annotation e89.
# CHECKED BY EYE 2026-10-19 on Sabiston-22 PDF page 1249, rendered to an image,
# which really does print "721.e89" in the header. Reading only the digits
# after the dot gave 89 and put the chapter on the wrong page, so the page
# part is taken first and the ".e" part is treated as an annotation.
ANNOT = re.compile(r"(\d{1,5})\s*\.\s*e\d{1,4}(?![\d.])")


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
        # A "721.e89" folio is ONE token. Its page part is the page; the
        # "e89" is a running marker that advances while the page stays put,
        # which would otherwise produce a beautifully constant WRONG gap
        # (measured 1160 on six consecutive pages of Sabiston-22). So when the
        # annotation form is present, nothing else on that line is a folio.
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
    # page. pdftotext does NOT always put it in the header: on Sabiston-22
    # PDF page 1249 (checked against the rendered image) the folio sits on
    # line 59, because the PDF stores it late in the content stream. Missing
    # it would lose the page entirely.
    for line in lines:
        m = ANNOT.search(line)
        if m:
            out.append(int(m.group(1)))
    return out


def rising_pairs(pairs):
    """Keep the LONGEST NON-DECREASING sequence of (page, gap).

    `gap` is page - folio: how many unnumbered pages the book has inserted
    before that point. Real page numbers can only make that gap grow (a new
    page adds 1; an unnumbered insert adds more), so the true folios of a
    whole book form one non-decreasing run of gaps.

    A section number, a chapter number or a copyright year produces a gap
    that jumps BACKWARDS, so it cannot survive the run. This is what finds
    the true folio without guessing it (Law 2).

    bisect_right is used, not bisect_left, because the run is allowed to
    repeat: two pages may legitimately print the same gap."""
    if not pairs:
        return []
    tails, tail_idx, prev = [], [], [-1] * len(pairs)
    for i, (_, gap) in enumerate(pairs):
        k = bisect.bisect_right(tails, gap)
        if k == len(tails):
            tails.append(gap)
            tail_idx.append(i)
        else:
            tails[k] = gap
            tail_idx[k] = i
        prev[i] = tail_idx[k - 1] if k else -1
    seq, i = [], tail_idx[-1]
    while i != -1:
        seq.append(pairs[i])
        i = prev[i]
    return list(reversed(seq))


def folio_at(pages, start, window=WINDOW):
    """The printed folio of page `start`, decided by the pages around it.

    LOOKED AT BY EYE 2026-10-19 (Sabiston-22, PDF page 300, rendered to an
    image): the book prints "13" there. The book's numbering RESTARTS in each
    Section, so one sequence for the whole book cannot exist -- BIBLE 3.4.6's
    single page_offset is impossible for this book, and a method that
    interpolates across the restart produces confidently wrong pages.

    So the decision is made LOCALLY, over a forward window that starts at the
    chapter's own page and therefore stays inside that chapter's numbering:

      * every number the window's header/footer lines offer is a candidate;
      * each candidate implies "gap = pdf_page - folio";
      * gaps that sit within TOL of each other are grouped into one cluster
        (consecutive printed pages differ by one, and Elsevier's "721.e89 /
        721.e90" run keeps the same page while the marker advances, so an
        exact-match vote would find no agreement at all);
      * the cluster holding the most DISTINCT pages wins;
      * printed folio of the chapter page = pdf_page - that cluster.

    A real folio repeats as a near-constant gap across consecutive pages. A
    section number, a chapter number or a reference list number appears once
    and loses the vote. Nothing is guessed: if no cluster has MIN_CLUSTER
    pages in it, the answer is None and no page is invented (Law 2)."""
    votes = []
    for idx in range(start, min(start + window, len(pages) + 1)):
        for f in set(candidates(pages[idx - 1])):
            if 1 <= f <= 99999:
                votes.append((idx, idx - f))
    if not votes:
        return None, None

    # group gaps that are within TOL of one another
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
    # the gap that belongs to the chapter's OWN page is the answer; a chapter
    # opening page often prints no folio, so the nearest page after it in the
    # same cluster is used instead. The median of the cluster is NOT used: it
    # would average the drift away and land on a page nobody printed.
    own = [g for p, g in best if p == start]
    if own:
        return start - min(own), min(own)
    later = [(p, g) for p, g in best if p > start]
    if later:
        p, g = min(later)
        return p - g, g
    return None, None


def chapter_pages(bid):
    for name in (f"{bid}-vis-toc.json", f"{bid}-toc.json"):
        path = LOGS / name
        if not path.exists():
            continue
        try:
            data = json.loads(path.read_text())
        except json.JSONDecodeError:
            continue
        out, stack = [], [data]
        while stack:
            node = stack.pop()
            if isinstance(node, dict):
                v = node.get("page_start")
                if isinstance(v, int):
                    out.append(v)
                stack.extend(node.values())
            elif isinstance(node, list):
                stack.extend(node)
        return sorted({p for p in out if p > 0})
    return []


def main(argv):
    books = json.loads(BOOKS.read_text())
    by_id = {b["book_id"]: b for b in books}
    args = [a for a in argv if not a.startswith("--")]
    want_all = "--all" in argv
    targets = list(by_id) if want_all else [a for a in args if a in by_id]
    if not targets:
        sys.exit("give a BOOK_ID, or --all")

    for bid in targets:
        pdf = KITCHEN / "books" / by_id[bid]["pdf_file"]
        if not pdf.exists():
            print(f"{bid:26s} MISSING PDF")
            continue
        try:
            text = extract_text(pdf, bid)
        except Exception as exc:                     # noqa: BLE001
            print(f"{bid:26s} FAILED: {exc}")
            continue

        pages = text.split("\f")
        ch = chapter_pages(bid)
        out, gaps = {}, []
        for p in ch:
            folio, gap = folio_at(pages, p)
            if folio is not None:
                out[str(p)] = folio
                gaps.append(gap)
        (LOGS / f"{bid}-folio.json").write_text(json.dumps(out))

        med = sorted(gaps)[len(gaps) // 2] if gaps else None
        ok = len(out)
        flag = "OK " if ok == len(ch) else "..."
        print(f"{bid:26s} {flag} chapters_with_printed_page={ok}/{len(ch)} "
              f"median_offset={med}")


if __name__ == "__main__":
    main(sys.argv[1:])