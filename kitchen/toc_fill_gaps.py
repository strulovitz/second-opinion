"""kitchen/toc_fill_gaps.py -- ask the model for the chapters that fell in a gap.

MEASURED 2026-10-11 on HARRISON-22: the reader produced chapters 1-141 and
147-505 with nothing in between. Image 9 ends at 141 and image 10 starts at
147, so five chapters printed on that page boundary were skipped -- the
automatic high-resolution retry did not fire because image 10 returned 42
lines, which is not "thin".

This script therefore asks the MODEL directly, with the model doing the
reading: for every gap it re-reads the two pages around it at high
resolution and asks for the missing numbers by name. Whatever the model
returns is parsed with exactly the same rules as a normal page, appended to
the recorded transcription, and the JSON is regenerated. Nothing is typed
by hand and nothing is invented here.

    python kitchen/toc_fill_gaps.py HARRISON-22 --dpi 240
"""
import json
import re
import subprocess
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from reader import ask  # noqa: E402
from toc_vision import BOOKS, LOGS, render, parse  # noqa: E402

GAP_SYSTEM = """You are looking at ONE page of a medical textbook's Table of Contents.

Our earlier reading of this page MISSED some entries. Read the whole page again, column by column, and pay special attention to the TOP of each column.

List ONLY the entries whose chapter number falls between {lo} and {hi} (inclusive). Copy each one exactly as printed, with its printed page number.

Answer with one line per entry and nothing else:
C<TAB>chapter number<TAB>the complete title exactly as printed<TAB>the printed page number

If the page really does not contain any entry between {lo} and {hi}, answer NONE."""


def numbers(doc):
    out = set()
    for p in doc["provinces"]:
        for c in p["chapters"]:
            if c.get("number") and str(c["number"]).isdigit():
                out.add(int(c["number"]))
    return out


def images_of(doc):
    """printed chapter number -> the image it came from"""
    m = {}
    for p in doc["provinces"]:
        for c in p["chapters"]:
            if c.get("number") and str(c["number"]).isdigit() and c.get("_image"):
                m.setdefault(int(c["number"]), c["_image"])
    return m


def main():
    argv = sys.argv[1:]
    bid = [a for a in argv if not a.startswith("--")][0]
    dpi = int(re.search(r"--dpi\s+(\d+)", " ".join(argv) + " ").group(1)
              ) if re.search(r"--dpi\s+(\d+)", " ".join(argv) + " ") else 240
    path = LOGS / f"{bid}-vis-toc.json"
    doc = json.loads(path.read_text())
    rec = {b["book_id"]: b for b in
           json.loads((Path(__file__).resolve().parent / "books.json").read_text())}
    pdf = BOOKS / rec[bid]["pdf_file"]
    seen = numbers(doc)
    src_by_num = images_of(doc)
    lo, hi = min(seen), max(seen)
    gaps, run = [], []
    for n in range(lo, hi + 1):
        if n in seen:
            if run:
                gaps.append((run[0], run[-1]))
                run = []
        else:
            run.append(n)
    if run:
        gaps.append((run[0], run[-1]))
    print(f"{bid}: chapters {lo}-{hi}, {len(seen)} present, "
          f"{len(gaps)} gap(s): {gaps}", flush=True)
    if not gaps:
        return 0

    txt = LOGS / f"{bid}-vis-toc.txt"
    blocks = txt.read_text().split("\n===== image ")
    added = 0
    for glo, ghi in gaps:
        # The contents runs forwards, so a gap belongs to the page that
        # holds the FIRST chapter after it -- the entries were skipped at
        # the TOP of that page. Asking the page BEFORE the gap as well
        # invites a confident wrong answer: on HARRISON-22 image 9 was
        # asked and returned "142 Approach to the Patient with an
        # Infectious Disease, 957" for a chapter that image does not
        # contain. Verified by eye on the rendered page: 142 is
        # "Encephalitis, 1111" at the top of image 10.
        after = src_by_num.get(ghi + 1)
        near = [after] if after else []
        for img in near:
            d = Path("/tmp/opencode") / f"gap-{bid}-{img}"
            files = render(pdf, d, img, img, dpi)
            ans = ask(GAP_SYSTEM.format(lo=glo, hi=ghi), f"Image number {img}.",
                      images=files, max_tokens=4000, expect_json=False,
                      retries=2, no_reasoning=True)
            print(f"    image {img}: {(ans.strip()[:90] or 'EMPTY')}", flush=True)
            # The targeted re-read is APPENDED, not substituted: it holds
            # only the missing numbers, while the original block holds the
            # other 42 entries of the same page. toc_dedupe.py then removes
            # the entries the two blocks share, because they are identical
            # in number, title and printed page.
            blocks.append(f"{img} =====\n{ans}")
            added += parse(ans, {"provinces": []}, "ALL", image=img)
    txt.write_text("\n===== image ".join(blocks))
    print(f"  asked for the gap on images {near}; {added} candidate lines",
          flush=True)
    print("  now run:  python kitchen/toc_reparse.py %s && "
          "python kitchen/toc_dedupe.py %s --vis && "
          "python kitchen/toc_validate.py %s --vis" % (bid, bid, bid),
          flush=True)
    return 0


if __name__ == "__main__":
    sys.exit(main())