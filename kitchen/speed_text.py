#!/usr/bin/env python3
"""Part 0 / T1+T8: pdftotext every page of every book into SQLite + FTS5.

Usage: speed_text.py [--all | BOOK_ID ...] [--jobs N]
Writes kitchen/logs/library.sqlite: pages(book_id, page, text), pages_fts.
Reading-order text for search; the index range is ALSO stored in -layout
form in pages_layout for the code parser. Idempotent per book.
"""
import argparse, json, sqlite3, subprocess, sys, time
from concurrent.futures import ProcessPoolExecutor
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
DB = ROOT / "kitchen" / "logs" / "library.sqlite"
BOOKS = json.loads((ROOT / "kitchen" / "books.json").read_text())


def schema(con):
    con.executescript("""
    CREATE TABLE IF NOT EXISTS pages(book_id TEXT, page INTEGER, text TEXT, PRIMARY KEY(book_id, page));
    CREATE TABLE IF NOT EXISTS pages_layout(book_id TEXT, page INTEGER, text TEXT, PRIMARY KEY(book_id, page));
    CREATE VIRTUAL TABLE IF NOT EXISTS pages_fts USING fts5(book_id UNINDEXED, page UNINDEXED, text, tokenize='porter unicode61');
    CREATE TABLE IF NOT EXISTS text_done(book_id TEXT PRIMARY KEY, pages INTEGER, empty INTEGER, seconds REAL);
    """)


def extract(book, layout=False, first=None, last=None):
    pdf = ROOT / "kitchen" / "books" / book["pdf_file"]
    cmd = ["pdftotext", "-enc", "UTF-8"] + (["-layout"] if layout else [])
    if first:
        cmd += ["-f", str(first), "-l", str(last)]
    out = subprocess.run(cmd + [str(pdf), "-"], capture_output=True, text=True, errors="replace")
    pages = out.stdout.split("\f")
    if pages and pages[-1].strip() == "":
        pages = pages[:-1]
    return pages


def one_book(book):
    t0 = time.time()
    pages = extract(book)
    layout = []
    if book.get("index_images"):
        a, b = book["index_images"]
        layout = [(a + i, t) for i, t in enumerate(extract(book, layout=True, first=a, last=b))]
    empty = sum(1 for p in pages if len(p.strip()) < 20)
    return book["book_id"], pages, layout, empty, time.time() - t0


def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("books", nargs="*")
    ap.add_argument("--all", action="store_true")
    ap.add_argument("--jobs", type=int, default=6)
    ap.add_argument("--force", action="store_true")
    a = ap.parse_args()
    con = sqlite3.connect(DB)
    schema(con)
    done = {r[0] for r in con.execute("SELECT book_id FROM text_done")} if not a.force else set()
    wanted = [b for b in BOOKS if (a.all or b["book_id"] in a.books) and b["book_id"] not in done]
    print(f"books to extract: {len(wanted)} (already done: {len(done)})", flush=True)
    with ProcessPoolExecutor(a.jobs) as ex:
        for bid, pages, layout, empty, secs in ex.map(one_book, wanted):
            con.execute("DELETE FROM pages WHERE book_id=?", (bid,))
            con.execute("DELETE FROM pages_layout WHERE book_id=?", (bid,))
            con.execute("DELETE FROM pages_fts WHERE book_id=?", (bid,))
            con.executemany("INSERT INTO pages VALUES(?,?,?)", ((bid, i + 1, t) for i, t in enumerate(pages)))
            con.executemany("INSERT INTO pages_fts VALUES(?,?,?)", ((bid, i + 1, t) for i, t in enumerate(pages)))
            con.executemany("INSERT INTO pages_layout VALUES(?,?,?)", ((bid, n, t) for n, t in layout))
            con.execute("INSERT OR REPLACE INTO text_done VALUES(?,?,?,?)", (bid, len(pages), empty, secs))
            con.commit()
            flag = "  <-- MANY EMPTY PAGES (scan?)" if empty > len(pages) * 0.2 else ""
            print(f"{bid}: {len(pages)} pages, {empty} empty, {secs:.0f}s{flag}", flush=True)
    rows = con.execute("SELECT count(*), sum(pages), sum(empty), sum(seconds) FROM text_done").fetchone()
    print(f"TOTAL books={rows[0]} pages={rows[1]} empty={rows[2]} cpu_seconds={rows[3]:.0f}")


if __name__ == "__main__":
    sys.exit(main())
