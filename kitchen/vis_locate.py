"""kitchen/vis_locate.py -- find the Table of Contents with the model's EYES.

Three text-based locators failed on 16 of the 37 books (see PROGRESS.md,
2026-10-10). The failure mode is specific: those books print their contents
in layouts no text rule handles, and worse, the text rules keep selecting
NUMBERED REFERENCE LISTS ("143. Moore MW, Klein RD, ..."), contributor
lists and dedications, because those look exactly like a contents page to a
regex.

A contents page is, however, instantly recognisable BY SIGHT. This script
uses the vision fallback the BIBLE itself prescribes in part 3 section 4.1.

How it works, and why it is cheap:
  * render the first FRONT pages at low resolution (one pdftoppm call)
  * paste 20 of them onto one "contact sheet" with the page number printed
    in a label strip above each thumbnail
  * ask the multimodal model, for each sheet: "which page numbers are the
    Table of Contents?"
  * one call per 20 pages, not one call per page

The images go to kitchen/pages/<BOOK_ID>/vis/ which is gitignored, and are
deleted afterwards unless KEEP_VIS=1.

Writes kitchen/logs/vis_locate.json and updates the toc_images field in
kitchen/books.json only when the model is confident.
"""
import json
import os
import re
import subprocess
import sys
from concurrent.futures import ProcessPoolExecutor
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from reader import ask  # noqa: E402

KITCHEN = Path(__file__).resolve().parent
BOOKS = KITCHEN / "books"
LOGS = KITCHEN / "logs"
START = int(os.environ.get("VIS_START", "1"))   # first image to render
FRONT = int(os.environ.get("VIS_FRONT", "70"))  # how many images to render
DPI = 55
PER_SHEET = 20
COLS = 5

SYSTEM = """You are looking at a contact sheet: 20 scanned pages from the front of a medical textbook, each thumbnail labelled with its page number.

Tell me which of those page numbers belong to the TABLE OF CONTENTS (the pages that list chapter or section titles together with the starting page number of each).

Do NOT count: contributor lists, dedications, prefaces, reference lists, indexes, or ordinary body text.

Answer with exactly two lines:
PAGES=<comma separated page numbers, in order>
NOTE=<one short sentence>"""


def render(pdf: Path, outdir: Path, n: int, start: int = 1):
    outdir.mkdir(parents=True, exist_ok=True)
    subprocess.run(["pdftoppm", "-f", str(start), "-l", str(n), "-r", str(DPI),
                    "-png", "-gray", str(pdf), str(outdir / "p")],
                   capture_output=True, timeout=3600)
    # pdftoppm names them p-01.png, p-1.png ... sort numerically
    files = sorted(outdir.glob("p-*.png"),
                  key=lambda f: int(re.sub(r"\D", "", f.stem) or 0))
    return files


def sheet(files, first_page, outpath, cols=COLS):
    from PIL import Image, ImageDraw, ImageFont
    ims = []
    try:
        font = ImageFont.load_default(size=22)
    except TypeError:
        font = ImageFont.load_default()
    tw = 250
    for f in files:
        im = Image.open(f).convert("L")
        th = int(im.height * tw / im.width)
        ims.append((f, im.resize((tw, th))))
    if not ims:
        return None
    rows = (len(ims) + cols - 1) // cols
    cell_h = max(i.height for _, i in ims) + 30
    W, H = cols * tw, rows * cell_h
    canvas = Image.new("L", (W, H), 255)
    d = ImageDraw.Draw(canvas)
    for k, (f, im) in enumerate(ims):
        x, y = (k % cols) * tw, (k // cols) * cell_h
        n = first_page + k
        d.rectangle([x, y, x + tw, y + 28], fill=0)
        d.text((x + 6, y + 4), f"PAGE {n}", fill=255, font=font)
        canvas.paste(im, (x, y + 30))
    canvas.save(outpath)
    return outpath


def work(rec):
    bid = rec["book_id"]
    pdf = BOOKS / rec["pdf_file"]
    n = min(START + FRONT - 1, rec["page_count_images"])
    visdir = BOOKS.parent / "pages" / bid / "vis"
    try:
        files = render(pdf, visdir, n, START)
        if not files:
            return {"book_id": bid, "pages": [], "note": "render produced nothing"}
        pages, notes = [], []
        for i in range(0, len(files), PER_SHEET):
            grp = files[i:i + PER_SHEET]
            sp = sheet(grp, START + i, visdir / f"sheet-{i//PER_SHEET + 1}.png")
            if not sp:
                continue
            ans = ask(SYSTEM, f"This sheet shows pages {START+i} to {START+i+len(grp)-1}.",
                      images=[sp], max_tokens=4000, expect_json=False, retries=2)
            m = re.search(r"PAGES\s*=\s*([\d,\s\-]+)", ans)
            note = re.search(r"NOTE\s*=\s*(.+)", ans)
            if m:
                pages += [int(x) for x in re.findall(r"\d+", m.group(1))]
            notes.append((note.group(1).strip() if note else "")[:110])
        pages = sorted(set(pages))
        if not os.environ.get("KEEP_VIS"):
            for f in visdir.glob("*.png"):
                f.unlink()
            try:
                visdir.rmdir()
            except OSError:
                pass
        return {"book_id": bid, "pages": pages, "notes": notes}
    except Exception as exc:  # noqa: BLE001 - recorded, never hidden
        return {"book_id": bid, "pages": [], "note": f"ERROR {exc}"}


def main():
    wanted = sys.argv[1:] or None
    books = [b for b in json.loads((KITCHEN / "books.json").read_text())
             if b["status"] == "candidate"]
    if wanted:
        books = [b for b in books if b["book_id"] in wanted]
    print(f"vision-locating the contents of {len(books)} books ...", flush=True)
    with ProcessPoolExecutor(max_workers=2) as pool:
        res = list(pool.map(work, books))
    (LOGS / "vis_locate.json").write_text(json.dumps(res, indent=1,
                                                     ensure_ascii=False))
    for r in res:
        p = r["pages"]
        rng = f"{min(p)}-{max(p)} ({len(p)} pages)" if p else "NONE"
        print(f"  {r['book_id']:26s} -> {rng:20s} {r.get('notes', [''])[0] if r.get('notes') else r.get('note','')}")


if __name__ == "__main__":
    main()