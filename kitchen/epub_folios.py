#!/usr/bin/env python3
"""Printed page -> PDF page for a book whose PDF was converted from an EPUB
(calibre pages, no printed folios). The publisher EPUB carries invisible
print page markers (<a id="page123"/>, epub:type="pagebreak"). For each
printed page, the first words after its marker are searched (FTS phrase) in
the book's PDF text; the unique hit nearest the previous one gives the PDF
page. Writes kitchen/logs/<BOOK>-folios.json {"printed": [...], "pdf": [...]},
which speed_entities.folio_map uses instead of reading folios from the text.

Usage: epub_folios.py BOOK-ID file.epub
"""
import html, json, re, sqlite3, sys, zipfile
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
DB = ROOT / "kitchen" / "logs" / "library.sqlite"
MARK = re.compile(r'<[^>]*\b(?:id="page_?(\d+)"|epub:type="pagebreak"[^>]*title="(\d+)"|title="(\d+)"[^>]*epub:type="pagebreak")[^>]*>')


def spine_texts(epub):
    z = zipfile.ZipFile(epub)
    opf = re.search(r'full-path="([^"]+)"', z.read("META-INF/container.xml").decode()).group(1)
    base = opf.rsplit("/", 1)[0] + "/" if "/" in opf else ""
    o = z.read(opf).decode("utf-8", "ignore")
    items = dict(re.findall(r'<item\b[^>]*?id="([^"]+)"[^>]*?href="([^"]+)"', o))
    items.update({i: h for h, i in re.findall(r'<item\b[^>]*?href="([^"]+)"[^>]*?id="([^"]+)"', o)})
    for idref in re.findall(r'<itemref\b[^>]*idref="([^"]+)"', o):
        if idref in items:
            yield z.read(base + items[idref]).decode("utf-8", "ignore")


def main(bid, epub):
    pages, cur = {}, None
    for doc in spine_texts(epub):
        doc = re.sub(r"(?s)<(script|style|head)\b.*?</\1>", " ", doc)
        doc = MARK.sub(lambda m: f" \x00{next(g for g in m.groups() if g)}\x00 ", doc)
        text = html.unescape(re.sub(r"<[^>]+>", " ", doc))
        for i, part in enumerate(text.split("\x00")):
            if i % 2:
                cur = int(part)
            elif cur is not None:
                pages[cur] = pages.get(cur, "") + " " + part
    con = sqlite3.connect(DB)
    out, prev, miss = {}, 0, 0
    for n in sorted(pages):
        words = re.findall(r"[A-Za-z]{3,}", pages[n])
        found = None
        for s in range(0, min(len(words) - 6, 60), 7):
            q = '"' + " ".join(words[s:s + 6]) + '"'
            hits = [p for (p,) in con.execute("SELECT page FROM pages_fts WHERE book_id=? AND pages_fts MATCH ?", (bid, q))]
            hits = [p for p in hits if p >= prev - 2]
            if hits:
                found = min(hits)
                break
        if found is None:
            miss += 1
            continue
        out[n], prev = found, found
    keys = sorted(out)
    path = ROOT / "kitchen" / "logs" / f"{bid}-folios.json"
    path.write_text(json.dumps({"source": Path(epub).name, "printed": keys, "pdf": [out[k] for k in keys]}))
    mono = sum(out[a] <= out[b] for a, b in zip(keys, keys[1:]))
    print(f"{bid}: {len(pages)} printed pages in EPUB, mapped {len(out)}, not found {miss}, "
          f"in order {mono}/{max(len(keys) - 1, 0)}; wrote {path.name}")


if __name__ == "__main__":
    main(sys.argv[1], sys.argv[2])
