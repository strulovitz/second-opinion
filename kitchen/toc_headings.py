"""kitchen/toc_headings.py -- re-read ONLY the Part/Section headings.

MEASURED 2026-10-11 on HARRISON-22: the chapter list came out perfect
(505 chapters, numbered 1 to 505, every printed page in order, validator
clean) but the PROVINCE names were not. The page prints a small banner
such as

    SECTION 1   Alterations in Circulatory and Respiratory Physiology

beside a dense two-column chapter list, and while transcribing 50 chapter
entries the model got the banner wrong -- HARRISON-22's first province came
out as "SECTION 5" where the page says "SECTION 1", and one province came
out with the whole banner repeated in the "level above" column.

So the headings are asked for on their own, one page per call, with
nothing else on the page to distract the model. Same model, same images,
same rules -- just a smaller question. The answers are written to
kitchen/logs/<BOOK_ID>-vis-headings.json and never overwrite the chapter
data; use kitchen/toc_apply_headings.py to put them in.

    python kitchen/toc_headings.py HARRISON-22
"""
import json
import re
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from reader import ask  # noqa: E402
from toc_vision import BOOKS, LOGS, render  # noqa: E402

TITLE_SYSTEM = """You are looking at ONE page of a medical textbook's Table of Contents.

Ignore the chapter list. I only want the HEADINGS printed on this page as grey banners or boxed labels: things like "PART 12", "SECTION 3", "VOLUME II", "UNIT IV", or a department name printed on its own line as a heading.

MEASURED 2026-10-12 on ROBBINS-10: this book's contents prints NO banner at all -- the chapters are one flat numbered list under a plain "Contents" title. Answering honestly is correct there, but a book whose chapters are grouped only by the subject line above them ("Diseases of the Immune System", "Neoplasia") still has no banner. Do not invent a heading that is not printed.

If the page has no printed banner, answer NONE.

Answer with one line per heading and nothing else:
H<TAB>the exact heading text

Copy the heading exactly as the book prints it. If the book prints a number with it ("SECTION V CARDIAC RADIOLOGY", "PART 3"), keep the number and the title together. If the book prints only a title and no number, write only the title. NEVER invent a number, NEVER drop a printed one, NEVER drop printed words.

If the page carries no such heading, answer NONE. Do not summarise, do not correct, do not guess a number you cannot see."""

FIRST_SYSTEM = """You are looking at ONE page of a medical textbook's Table of Contents.

I will name one heading. Tell me the chapter number of the FIRST entry printed directly below that heading on this page.

Answer with exactly one line:
F<TAB>the chapter number

If nothing is printed below that heading on this page -- because it started on an earlier page -- answer F=NONE. Never guess a number you cannot see."""


def main():
    argv = sys.argv[1:]
    bid = [a for a in argv if not a.startswith("--")][0]
    dpi = int(m.group(1)) if (m := re.search(r"--dpi\s+(\d+)",
                                              " ".join(argv) + " ")) else 200
    rec = {b["book_id"]: b for b in
           json.loads((Path(__file__).resolve().parent / "books.json").read_text())}
    pdf = BOOKS / rec[bid]["pdf_file"]
    path = LOGS / f"{bid}-vis-toc.txt"
    pages = sorted({int(b.split(" ")[0]) for b in
                    path.read_text().split("===== image ")[1:] if b.strip()})
    # MEASURED 2026-10-12 on SABISTON-22: the transcript also records the pages
    # the reader REFUSED as look-alikes (VIDEO CONTENTS, a podcast list, a
    # divider page), and every image there has an "===== image N =====" header.
    # Asking for their headings put "SECTION X" and "SECTION I" into the file and
    # rebuilt the book with 187 chapters instead of 92, the refused pages'
    # chapters landing under a catch-all province. A refused page has no heading.
    refused = set()
    rf = LOGS / f"{bid}-vis-pages.json"
    if rf.exists():
        refused = {int(x) for x in json.loads(rf.read_text())
                   .get("refused_lookalike") or []}
    if refused:
        pages = [p for p in pages if p not in refused]
        print(f"{bid}: skipping {len(refused)} refused look-alike image(s): "
              f"{sorted(refused)}", flush=True)
    namesfile = LOGS / f"{bid}-vis-headingnames.json"
    if namesfile.exists() and "--reuse" in argv:
        names = json.loads(namesfile.read_text())
        print(f"{bid}: reusing PASS 1 from {namesfile.name}", flush=True)
    else:
        names = {}
        print(f"{bid}: PASS 1 -- the exact heading text on {len(pages)} pages",
              flush=True)
    for n in pages if not ("--reuse" in argv) else []:
        files = render(pdf, Path("/tmp/opencode") / f"ht-{bid}-{n}", n, n, dpi)
        ans = ask(TITLE_SYSTEM, f"Image number {n}.", images=files,
                  max_tokens=2000, expect_json=False, retries=2,
                  no_reasoning=True)
        got = [l.split("\t", 1)[1].strip() for l in ans.splitlines()
               if l.startswith("H") and "\t" in l]
        names[str(n)] = got
        print(f"    image {n:>4d}: {len(got)} heading(s)", flush=True)
    (LOGS / f"{bid}-vis-headingnames.json").write_text(
        json.dumps(names, indent=1, ensure_ascii=False))

    print(f"{bid}: PASS 2 -- the first chapter under each heading", flush=True)
    firsts = {}
    for n in pages:
        for h in names[str(n)]:
            files = render(pdf, Path("/tmp/opencode") / f"hf-{bid}-{n}", n, n, dpi)
            q = (f"Image number {n}. The heading is: {h}\n"
                 f"What is the chapter number of the first entry printed "
                 f"directly below it on this page?")
            ans = ask(FIRST_SYSTEM, q, images=files, max_tokens=200,
                      expect_json=False, retries=2, no_reasoning=True)
            m = re.search(r"^F[\s=\t]+(\d+)", ans.strip(), re.M)
            firsts.setdefault(str(n), {})[h] = int(m.group(1)) if m else None
            print(f"    image {n:>4d}  {h[:48]:50s} first="
                  f"{firsts[str(n)][h]}", flush=True)
    (LOGS / f"{bid}-vis-headings.json").write_text(
        json.dumps(firsts, indent=1, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    sys.exit(main())
