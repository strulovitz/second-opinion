#!/usr/bin/env python3
"""Part 0 / T2: parse a back-of-book index with code, from pages_layout.

Usage: speed_index.py [--all | BOOK_ID ...] [--check-qwen]
Writes table terms(book_id, headword, see, refs, sub_refs, subentries, page)
and index_done(book_id, pages, terms, refs_seen, refs_kept) in library.sqlite.
Validator: share of page-reference tokens in the raw text that ended up in a
term. Pages under 80 percent are listed for model repair (T-A), not guessed.
"""
import argparse, json, re, sqlite3, sys
from collections import Counter
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
DB = ROOT / "kitchen" / "logs" / "library.sqlite"
BOOKS = {b["book_id"]: b for b in json.loads((ROOT / "kitchen" / "books.json").read_text())}

REF = r"(?:[A-Z]{0,2}\d{1,4}(?:\.e\d{1,3})?(?:[\u2013\u2014-]\d{1,4}(?:\.e\d{1,3})?)?[a-z]{0,2}|e\d{1,4}[tf]?)"
REF_RE = re.compile(REF)
TAIL_RE = re.compile(r"(?:,\s*|\s+)(" + REF + r"(?:,\s*" + REF + r")*)\s*$")
SEE_RE = re.compile(r"^(.*?)[.,;]?\s+[Ss]ee( also)?\s+(.+)$")
LETTER_RE = re.compile(r"^[A-Z]$")


def columns(lines):
    """Return column start positions found from vertical whitespace gaps."""
    width = max((len(l) for l in lines), default=0)
    if not lines or width == 0:
        return [0]
    blank = [0] * (width + 1)
    for l in lines:
        for i in range(width + 1):
            if i >= len(l) or l[i] == " ":
                blank[i] += 1
    n = len(lines)
    cols, start, i = [], 0, 1
    while i < width:
        if blank[i] >= 0.9 * n:
            j = i
            while j < width and blank[j] >= 0.9 * n:
                j += 1
            if j - i >= 2 and j < width:
                cols.append((start, i))
                start = j
            i = j
        else:
            i += 1
    cols.append((start, 10 ** 6))
    return cols


def logical_lines(text, cols=None):
    """Split a layout page into (indent, text) per column in reading order,
    joining continuation lines. Header lines crossing columns are dropped."""
    text = text.replace("\u200b", "").replace("\xad", "")
    raw = [l.rstrip() for l in text.split("\n") if l.strip()]
    out = []
    for a, b in (cols or columns(raw)):
        col = []
        for l in raw:
            e = b
            while b < len(l) and l[b - 1] != " " and e < len(l) and e < b + 4 and l[e] != " ":
                e += 1  # finish the word cut by the gap estimate
            seg = l[a:e]
            if not seg.strip():
                continue
            if a > 0 and len(l) > a - 2 and l[a - 2:a].strip():
                continue  # text crossing the gap: header or garbage
            if b < 10 ** 6 and len(l) > b + 4 and l[b + 1:b + 4].strip() and l[e:b + 4].strip():
                continue  # line runs across the gap: page header
            col.append((len(seg) - len(seg.lstrip()), seg.strip()))
        if not col:
            continue
        base = min(i for i, _ in col)
        for ind, s in col:
            lvl = ind - base
            prev = out[-1][1] if out else ""
            if out and (lvl >= 8 or prev.endswith(("\u2013", "-", ","))):  # continuation of the previous logical line
                sep = ", " if not prev.endswith(",") and REF_RE.fullmatch(s.split(",")[0].strip()) and TAIL_RE.search(prev) else " "
                out[-1] = (out[-1][0], prev + sep + s)
            else:
                out.append((0 if lvl < 2 else 1 if lvl < 5 else 2, s))
    return out


def split_refs(s):
    m = TAIL_RE.search(s)
    if not m:
        return s.strip(" ,;"), []
    head = s[:m.start()].strip(" ,;")
    refs = [r.strip() for r in m.group(1).split(",") if r.strip()]
    return head, refs


def parse_page(text, cols=None):
    entries, cur = [], None
    for lvl, s in logical_lines(text, cols):
        if LETTER_RE.match(s) or s.lower() in ("index",):
            continue
        see = None
        m = SEE_RE.match(s)
        if m:
            s, see = m.group(1), (None if m.group(2) else m.group(3).strip(" ."))
        head, refs = split_refs(s)
        if lvl == 0 or cur is None:
            if not head and refs and cur:  # bare refs line: belongs to previous
                cur["refs"] += refs
                continue
            cur = {"headword": head, "see": see, "refs": refs, "sub_refs": [], "subentries": []}
            entries.append(cur)
        else:
            cur["subentries"].append(head)
            cur["sub_refs"] += refs
    for e in entries:
        e["headword"] = re.sub(r"\s*\(cont\.?\)\s*:?$", "", e["headword"]).strip()
    return [e for e in entries if e["headword"] and not re.fullmatch(r"(?i)i-\d+|index|\d+", e["headword"])]


def locate_index(con, bid):
    """Find the back-of-book index in the last 20 percent of pages: pages where
    most lines end in a page reference. Returns (first, last) or None."""
    pages = con.execute("SELECT page, text FROM pages WHERE book_id=? ORDER BY page", (bid,)).fetchall()
    if not pages:
        return None
    start = int(len(pages) * 0.8)
    flags = []
    for page, text in pages[start:]:
        lines = [l for l in text.split("\n") if len(l.strip()) > 3]
        hits = sum(1 for l in lines if REF_RE.search(l.strip()[-6:]) and l.strip()[-1].isalnum())
        flags.append((page, len(lines) >= 25 and hits >= 0.45 * len(lines)))
    runs, cur = [], []
    for page, ok in flags:
        if ok:
            cur.append(page)
        elif cur:
            if len(cur) >= 3:
                runs.append(cur)
            cur = []
    if cur and len(cur) >= 3:
        runs.append(cur)
    if not runs:
        return None
    best = max(runs, key=len)
    return best[0], best[-1]


def run_book(con, bid, check):
    rows = con.execute("SELECT page, text FROM pages_layout WHERE book_id=? ORDER BY page", (bid,)).fetchall()
    if len(rows) < 5:
        found = locate_index(con, bid)
        if not found:
            print(f"{bid}: NO INDEX FOUND by code; needs a look (scan? no index?)")
            return
        from speed_text import extract
        pages = extract(BOOKS[bid], layout=True, first=found[0], last=found[1])
        con.executemany("INSERT OR REPLACE INTO pages_layout VALUES(?,?,?)", ((bid, found[0] + i, t) for i, t in enumerate(pages)))
        con.commit()
        print(f"{bid}: index located by code at PDF pages {found[0]}-{found[1]}")
        rows = con.execute("SELECT page, text FROM pages_layout WHERE book_id=? ORDER BY page", (bid,)).fetchall()
    con.execute("DELETE FROM terms WHERE book_id=?", (bid,))
    seen = kept = 0
    weak = []
    total = 0
    parity = {k: columns([l.rstrip() for pg, t in rows if pg % 2 == k for l in t.split("\n") if l.strip()]) for k in (0, 1)}
    for page, text in rows:
        cols = []
        for a, b in columns([l.rstrip() for l in text.split("\n") if l.strip()]):
            near = [a2 for a2, _ in parity[page % 2] if 0 < a - a2 <= 4]
            cols.append((near[0] if near else a, b))  # a column with no main entry on this page
        entries = parse_page(text, cols)
        n_seen = len(REF_RE.findall(" ".join(l for l in text.split("\n") if l.strip() and not LETTER_RE.match(l.strip()))))
        n_kept = sum(len(e["refs"]) + len(e["sub_refs"]) for e in entries)
        seen += n_seen
        kept += n_kept
        if n_seen and n_kept < 0.8 * n_seen:
            weak.append((page, n_kept, n_seen))
        con.executemany("INSERT INTO terms VALUES(?,?,?,?,?,?,?)",
                        ((bid, e["headword"], e["see"], json.dumps(e["refs"]), json.dumps(e["sub_refs"]),
                          json.dumps(e["subentries"]), page) for e in entries))
        total += len(entries)
    con.execute("INSERT OR REPLACE INTO index_done VALUES(?,?,?,?,?)", (bid, len(rows), total, seen, kept))
    con.commit()
    share = kept / seen if seen else 0
    print(f"{bid}: {len(rows)} index pages, {total} terms, refs kept {kept}/{seen} = {share:.1%}, weak pages {len(weak)}"
          + (f" e.g. {weak[:5]}" if weak else ""), flush=True)
    if check:
        qwen = json.loads((ROOT / "kitchen" / "logs" / f"{bid}-index-entries.json").read_text())["entries"]
        q_heads = Counter(e["headword"].casefold() for e in qwen if e.get("headword") and e["headword"] != "CONTINUED")
        mine = Counter(r[0].casefold() for r in con.execute("SELECT headword FROM terms WHERE book_id=?", (bid,)))
        both = sum((q_heads & mine).values())
        print(f"  vs Qwen parse: qwen headwords {sum(q_heads.values())}, code headwords {sum(mine.values())}, "
              f"identical {both} ({both / max(1, sum(q_heads.values())):.1%} of Qwen)")
        missing = [h for h in q_heads if h not in mine][:12]
        extra = [h for h in mine if h not in q_heads][:12]
        print("  qwen-only examples:", missing)
        print("  code-only examples:", extra)


def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("books", nargs="*")
    ap.add_argument("--all", action="store_true")
    ap.add_argument("--check-qwen", action="store_true")
    a = ap.parse_args()
    con = sqlite3.connect(DB)
    con.executescript("""
    CREATE TABLE IF NOT EXISTS terms(book_id TEXT, headword TEXT, see TEXT, refs TEXT, sub_refs TEXT, subentries TEXT, page INTEGER);
    CREATE INDEX IF NOT EXISTS terms_book ON terms(book_id);
    CREATE TABLE IF NOT EXISTS index_done(book_id TEXT PRIMARY KEY, pages INTEGER, terms INTEGER, refs_seen INTEGER, refs_kept INTEGER);
    """)
    for bid in (list(BOOKS) if a.all else a.books):
        run_book(con, bid, a.check_qwen)


if __name__ == "__main__":
    sys.exit(main())
