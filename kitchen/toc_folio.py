#!/usr/bin/env python3
"""Turn the chapter's true first PAGE IMAGE into its PRINTED page number.

The PDF links give the image number (e.g. image 51). The printed folio is a
different thing (the number the reader sees in the book). The offset between
them is what BIBLE part 3 section 4.6 asks for.

Method: render a SAMPLE of chapter-opening pages, let the free local READER
read the printed folio off the page itself, and check the offset is constant.
Only if every sample agrees is the offset applied to all chapters. If the
samples disagree, nothing is written and the reason is printed (Law 2, Law 15).

Writes kitchen/logs/<BOOK_ID>-vis-offset.json
"""
import json
import re
import subprocess
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from reader import ask  # noqa: E402

ROOT = Path(__file__).resolve().parent.parent
KITCHEN = ROOT / "kitchen"
LOGS = KITCHEN / "logs"

PROMPT = (
    "Look at this scanned book page. It is the FIRST page of a chapter.\n"
    "The printed page number is usually in the header or the footer, alone on "
    "the line, often in small type.\n"
    "Answer with ONLY the printed page number as digits, nothing else.\n"
    "If you cannot see any printed page number, answer exactly: NONE\n"
)


def render(pdf: Path, outdir: Path, p: int, dpi: int = 150):
    outdir.mkdir(parents=True, exist_ok=True)
    subprocess.run(["pdftoppm", "-f", str(p), "-l", str(p), "-r", str(dpi),
                    "-png", "-singlefile", str(pdf), str(outdir / f"p-{p:05d}")],
                   check=True, capture_output=True)
    return outdir / f"p-{p:05d}.png"


def main():
    argv = sys.argv[1:]
    bid = [a for a in argv if not a.startswith("--")][0]
    n = 7
    for a in argv:
        if a.startswith("--samples"):
            n = int(a.split("=")[1])

    books = json.loads((KITCHEN / "books.json").read_text())
    book = [b for b in books if b["book_id"] == bid][0]
    pdf = KITCHEN / "books" / book["pdf_file"]

    doc = json.loads((LOGS / f"{bid}-vis-toc.json").read_text())
    chapters = [c for p in doc.get("provinces", []) for c in p.get("chapters", [])]
    withlink = [c for c in chapters if c.get("_link_image")]
    if not withlink:
        print("no links found -- run toc_links.py first")
        return
    withlink.sort(key=lambda c: c["_link_image"])
    step = max(1, len(withlink) // n)
    sample = withlink[::step][:n]

    imgdir = KITCHEN / "pages" / bid / "folio"
    rows = []
    for c in sample:
        img = c["_link_image"]
        png = render(pdf, imgdir, img)
        ans = ask(PROMPT, "", images=[png], max_tokens=40,
                  no_reasoning=True, expect_json=False)
        txt = (ans.get("answer") if isinstance(ans, dict) else str(ans)) or ""
        m = re.search(r"\d{1,5}", txt)
        printed = int(m.group(0)) if m else None
        rows.append({"number": c.get("number"), "title": c.get("title"),
                     "image": img, "printed": printed,
                     "offset": (img - printed) if printed else None,
                     "image_file": str(png.relative_to(ROOT))})
        print(f"  ch {c.get('number'):>4} image {img:>5} printed "
              f"{printed} offset {rows[-1]['offset']}   [{txt.strip()[:20]}]",
              flush=True)

    offs = sorted({r["offset"] for r in rows if r["offset"] is not None})
    res = {"book_id": bid, "samples": rows, "offsets_seen": offs,
           "offset_constant": len(offs) == 1 and len(rows) == n,
           "offset": offs[0] if len(offs) == 1 else None}
    (LOGS / f"{bid}-vis-offset.json").write_text(
        json.dumps(res, indent=1, ensure_ascii=False))
    print("offsets seen:", offs, "constant:", res["offset_constant"])


if __name__ == "__main__":
    main()