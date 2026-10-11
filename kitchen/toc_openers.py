"""kitchen/toc_openers.py -- build the geography from CHAPTER OPENING PAGES.

THE PROBLEM (measured 2026-10-11 on SLEISENGER-11): this book has no table
of contents at all. Its front matter is title (images 1-2), copyright (3-4),
contributors (5-14), foreword, editors, preface, acknowledgments and an
abbreviation list (19-20), and then image 21 opens the book with

    PART I   Biology of the Gastrointestinal Tract
    1        Cellular Growth and Neoplasia

Nothing was missed: 24 contact sheets covering images 1-144 were shown to
the multimodal model and it reported no contents page anywhere in them. The
text-layer locator had "found" pages 21-33 and produced 22 chapters, which
is why last night's run looked plausible and was wrong.

THE ANSWER, and it uses the model as much as possible: every chapter opens
on its own page, and that page prints the PART banner, the chapter number,
the chapter title and the printed page. So the model is shown the whole
book as contact sheets and asked which pages open a chapter -- it decides,
page by page, and a regex never votes -- and then each page it names is
read on its own at high resolution.

    python kitchen/toc_openers.py SLEISENGER-11 [--from 1] [--windows 460]

Writes kitchen/logs/<BOOK_ID>-openers.txt (the model's own words),
kitchen/logs/<BOOK_ID>-vis-toc.json (provinces + chapters) and
kitchen/logs/<BOOK_ID>-vis-toc.txt so the ordinary validator works on it.
"""
import json
import os
import re
import subprocess
import sys
import time
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from reader import ask  # noqa: E402
from toc_vision import (BOOKS, LOGS, PAGES, PER_SHEET, COLS, READ_DPI,  # noqa: E402
                        parse, render, sheet)

FIND_SYSTEM = """You are looking at a contact sheet: 6 scanned pages from a medical textbook, each thumbnail labelled with its page number.

Tell me which of those page numbers OPEN A NEW CHAPTER. A chapter-opening page is the FIRST page of a chapter and is unmistakable: a LARGE chapter number sits next to the chapter's title near the top of the page, usually a "Chapter Outline" box listing the sections inside that chapter sits under them, and the top of the page is NOT a thin running header.

Do NOT count: ordinary text pages; pages in the middle of a chapter; the table of contents; contributor lists; prefaces; index pages; and above all the RUNNING HEADER, which on an ordinary page prints a small page number followed by a part name such as "6   PART I   Biology of the Gastrointestinal Tract". That is a page header, not a chapter number. If the biggest number on the page is the page number itself, it is not a chapter opening.

Answer with exactly two lines and nothing else:
PAGES=<comma separated page numbers, in order, or NONE>
NOTE=<one short sentence>"""

OPEN_SYSTEM = """You are looking at ONE page: the OPENING PAGE of a chapter in a medical textbook.

Report exactly what is printed there.

Answer with these lines and nothing else:
PART<TAB>the part banner printed at the top of the page, exactly as printed (for example "PART I   Biology of the Gastrointestinal Tract"). If no part is printed, write a single dash.
NUM<TAB>the chapter number exactly as printed
TITLE<TAB>the chapter title exactly as printed
PAGE<TAB>the PRINTED page number of this page, read from the page's own header or footer

The chapter title is the text printed NEXT TO that large chapter number. It is NOT the part banner and NOT a running header.

A thin running header along the top of an ordinary page -- a small page number followed by a part name such as "6   PART I   Biology of the Gastrointestinal Tract" -- means this is an ordinary page, NOT a chapter opening. In that case, and in any other case where no large chapter number with a title is printed, write NOTHING at all."""


def find_openers(pdf, pages_total, start, windows, visdir):
    found, notes = [], []
    cursor = start
    w = 0
    while cursor <= pages_total and w < windows:
        last = min(cursor + PER_SHEET - 1, pages_total)
        files = render(pdf, visdir / f"w{w+1}", cursor, last, 70)
        if not files:
            break
        sp = sheet(files, cursor, visdir / f"w{w+1}" / "sheet.png")
        ans = ask(FIND_SYSTEM,
                  f"This sheet shows pages {cursor} to {last}.",
                  images=[sp], max_tokens=2000, expect_json=False,
                  retries=2, no_reasoning=True)
        m = re.search(r"PAGES\s*=\s*([^\n]*)", ans)
        got = []
        if m and "NONE" not in m.group(1).upper():
            got = sorted({int(x) for x in re.findall(r"\d+", m.group(1))})
        found += [p for p in got if p not in found]
        w += 1
        if w % 20 == 0 or got:
            print(f"    scanned up to image {last} ({w} sheets) -> "
                  f"{len(found)} chapter openers so far", flush=True)
        cursor = last + 1
    return sorted(set(found)), notes


def read_openers(pdf, images, visdir):
    raw, doc, province = [], {"provinces": []}, None
    for n, img in enumerate(images, 1):
        files = render(pdf, visdir / f"read-{img}", img, img, READ_DPI)
        try:
            ans = ask(OPEN_SYSTEM, f"Image number {img}.",
                      images=files, max_tokens=1500, expect_json=False,
                      retries=2, no_reasoning=True)
        except Exception as exc:  # noqa: BLE001
            print(f"    image {img} FAILED: {exc}", flush=True)
            continue
        raw.append(f"\n===== image {img} =====\n{ans}")
        got = {}
        for line in ans.splitlines():
            f = line.split("\t")
            if len(f) >= 2 and f[0] in ("PART", "NUM", "TITLE", "PAGE"):
                got[f[0]] = f[1].strip()
        if "TITLE" not in got or "NUM" not in got:
            print(f"    [{n}/{len(images)}] image {img:4d} -> no chapter "
                  f"here", flush=True)
            continue
        part = got.get("PART", "-")
        if part and part != "-":
            province = {"name": part, "part_name": part, "chapters": []}
            doc["provinces"].append(province)
        if province is None:
            province = {"name": "ALL", "part_name": "ALL", "chapters": []}
            doc["provinces"].append(province)
        page = got.get("PAGE", "-")
        province["chapters"].append({
            "number": got["NUM"],
            "title": got["TITLE"],
            "page_start": int(m.group(0)) if (m := re.search(r"[0-9]+", page))
            else None,
            "_image": img,
        })
        print(f"    [{n}/{len(images)}] image {img:4d}  {got['NUM']:>5s}  "
              f"p{province['chapters'][-1]['page_start']}  "
              f"{got['TITLE'][:44]}", flush=True)
    return doc, raw


def main():
    argv = sys.argv[1:]
    bid = [a for a in argv if not a.startswith("--")][0]
    rec = {b["book_id"]: b for b in
           json.loads((Path(__file__).resolve().parent / "books.json").read_text())}
    pdf = BOOKS / rec[bid]["pdf_file"]
    total = rec[bid]["page_count_images"]

    def flag(name, default):
        m = re.search(rf"--{name}\s+(\d+)", " ".join(argv) + " ")
        return int(m.group(1)) if m else default

    start = flag("from", 1)
    windows = flag("windows", total // PER_SHEET + 1)
    visdir = PAGES / bid / "openers"
    print(f"{bid}: {total} images. Showing the whole book to the model in "
          f"{PER_SHEET}-page sheets and asking which pages open a chapter ...",
          flush=True)
    t0 = time.time()
    images, _ = find_openers(pdf, total, start, windows, visdir)
    print(f"  the model named {len(images)} chapter openers in "
          f"{int(time.time() - t0)}s: {images[:20]}{'...' if len(images) > 20 else ''}",
          flush=True)
    (LOGS / f"{bid}-openers.json").write_text(json.dumps(images))
    if not images:
        print("  none found -- recorded, not invented.", flush=True)
        return 0
    print("  reading each opener page on its own ...", flush=True)
    doc, raw = read_openers(pdf, images, visdir)
    (LOGS / f"{bid}-openers.txt").write_text("\n".join(raw))
    (LOGS / f"{bid}-vis-toc.txt").write_text("\n".join(raw))
    (LOGS / f"{bid}-vis-toc.json").write_text(
        json.dumps(doc, indent=1, ensure_ascii=False))
    n = sum(len(p["chapters"]) for p in doc["provinces"])
    print(f"  DONE {bid}: parts={len(doc['provinces'])} chapters={n}", flush=True)
    print(f"  next: python kitchen/toc_dedupe.py {bid} --vis && "
          f"python kitchen/toc_validate.py {bid} --vis", flush=True)
    return 0


if __name__ == "__main__":
    sys.exit(main())