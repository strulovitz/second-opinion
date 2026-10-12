"""kitchen/toc_vision.py -- read a book's Table of Contents WITH THE MODEL'S EYES.

THE HUMAN'S INSTRUCTION (2026-10-11): in this critical stage the AI model
must be used as MUCH as possible, not as little as possible. The text-layer
tricks (expand_toc.py) are kept only as a cheap cross-check; the contents
are LOCATED and READ by qwen3.8:27b looking at rendered page images.

Two model-driven stages, both offline and free:

  STAGE 1  LOCATE. Pages are rendered at 55 dpi, 20 of them pasted onto one
           labelled contact sheet, and the multimodal model is asked which
           page numbers hold the Table of Contents. It is asked again for
           the NEXT window of pages, so a second volume's contents block
           (CAMPBELL-2020, GRAY-2020) is found too. The model decides;
           nothing is taken from a regex.

  STAGE 2  READ. Every page the model named is rendered at 150 dpi and sent
           to the model ONCE, alone, as an image, with reasoning switched
           off. Output is tab separated so a truncated answer can never
           become invalid syntax:

               P<TAB>province name<TAB>the heading above it
               C<TAB>chapter number or a dash<TAB>title verbatim<TAB>printed page

Usage (ONE BOOK AT A TIME, as the human asked):
    python kitchen/toc_vision.py GUYTON-2026
    python kitchen/toc_vision.py GUYTON-2026 --windows 4

Writes kitchen/logs/<BOOK_ID>-vis-toc.txt (the raw transcription),
kitchen/logs/<BOOK_ID>-vis-toc.json (provinces -> chapters), and leaves
the rendered pages in kitchen/pages/<BOOK_ID>/vis/ (gitignored) so the
result can be checked by eye afterwards.
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

KITCHEN = Path(__file__).resolve().parent
BOOKS = KITCHEN / "books"
LOGS = KITCHEN / "logs"
PAGES = KITCHEN / "pages"

# MEASURED 2026-10-11: at 55 dpi the thumbnails were too small to read and
# the model answered NONE on GUYTON-2026 image 14, which IS a contents page.
# At 100 dpi in 3 columns it reads them correctly, and one such call costs
# only about 2 seconds -- the answer is two short lines, so the cost is the
# image tokens, not the generation.
PER_SHEET = 6
COLS = 3
LOCATE_DPI = 100
READ_DPI = 150
RETRY_DPI = 220     # a page that yields almost nothing is read again at this
# MEASURED 2026-10-11 on CAMPBELL-2020: one page dropped to 8 lines while its
# neighbours gave 111, and a "fewer than 5 lines" test did not notice. Any
# contents page thinner than this is read again at RETRY_DPI and the answer
# with MORE lines wins; more lines means a fuller transcription of the same
# printed page, so the retry cannot make the result worse.
THIN_LINES = 20

LOCATE_SYSTEM = """You are looking at a contact sheet: 6 scanned pages from a medical textbook, each thumbnail labelled with its page number.

Tell me which of those page numbers belong to the TABLE OF CONTENTS -- the pages that list chapter, unit, part or section titles together with the printed page number where each one starts.

Do NOT count: contributor lists, dedications, prefaces, reference lists, indexes, or ordinary body text.

VERY IMPORTANT -- A contents page is not the only page that looks like one.
Many textbooks print a SECOND contents page that lists something OTHER than
chapters, and it has the same columns and the same chapter numbers:
  * "VIDEO CONTENTS", "VIDEO ATLAS", "LIST OF VIDEOS", "SURGICAL VIDEOS"
  * "PODCAST", "AUDIO", "EXPERT INSIGHTS", "INTERACTIVE", "CASE STUDIES"
  * "ABBREVIATION LIST", "INDEX", "CONTRIBUTORS"
If a page's heading says it lists videos, podcasts or anything other than
the chapters themselves, it is NOT a contents page. Report it separately.

If this window contains no contents page at all, answer PAGES=NONE.

Answer with exactly these lines and nothing else:
PAGES=<comma separated page numbers, in order, or NONE>
OTHER=<comma separated page numbers of look-alike pages such as VIDEO CONTENTS or PODCAST, or NONE>
NOTE=<one short sentence>"""

READ_SYSTEM = """You are looking at ONE page of a medical textbook. Read what is printed on it, exactly as printed.

FIRST, BEFORE YOU TRANSCRIBE ANYTHING, decide what KIND of page this is, and say so on the very first line:
KIND=CHAPTERS   if it lists the book's chapters/parts/sections with the printed page where each one starts.
KIND=OTHER      if it is a look-alike: "VIDEO CONTENTS", "VIDEO ATLAS", "LIST OF VIDEOS", "PODCAST", "AUDIO", "EXPERT INSIGHTS", "INTERACTIVE", "CASE INDEX", "ABBREVIATIONS", "INDEX", "CONTRIBUTORS", or any page that lists something other than the chapters themselves.
KIND=OTHER      also if it is a part-divider page that lists chapter titles but prints NO page numbers at all.

MEASURED 2026-10-12 on SABISTON-22: that book prints its real contents on 4 pages and then a "VIDEO CONTENTS" list in the SAME two-column layout with the SAME section numbers I to XI and the SAME chapter numbers. Reading the video list as if it were the contents produced fake chapters such as "Video 110.1 Pleural Effusion" and page numbers printed nowhere in the book. A video/podcast entry is NEVER a chapter.

IF KIND=OTHER: output ONLY the KIND line and nothing else. Do not transcribe. Do not list any chapter. Do not invent page numbers.

IF KIND=CHAPTERS, carry on exactly as follows:

WORK THROUGH THE WHOLE PAGE. It is printed in columns. Read column by column, top to bottom, left column first, then the next column, and do not stop early. Every chapter on the page must appear in your answer, however many there are.

WHAT COUNTS AS A CHAPTER -- read this rule twice, it decides most of the output:
  A chapter is an entry that is marked "Chapter N" / "CHAPTER N", or that is
  numbered the same way as those are.
  It is NOT a chapter: the smaller sub-headings printed underneath a chapter
  (for example "Red Blood Cells (Erythrocytes)", "Iron Metabolism",
  "Anemia", "Determinants of GFR"). Those have no number. SKIP THEM.
  A heading that has no chapter number under it is not a chapter. Skip it.

For every heading that names a Part, Unit, Section, Volume or Book AND has chapters under it, output:
P<TAB>heading name<TAB>the heading of the level above it (or the same name)

ALSO output a P line for a BOLD chapter heading that has numbered entries under it, whenever no higher grouping (Volume/Part/Section) is printed above it on that page. Many surgical and specialty books print no higher grouping at all and open each block with a bold title such as "Amputations of the Foot". Every one of those bold headings must be a P line, and it must be printed BEFORE the entries that belong to it. A heading with nothing under it is not a P line.

For every CHAPTER entry -- its title together with the printed page number where the chapter starts -- output:
C<TAB>chapter number as printed, or a single dash if there is none<TAB>the complete chapter title exactly as printed<TAB>the printed page number

WHAT THE "ENTRIES" OF A BLOCK ARE, for books like a surgical atlas: when a bold heading is followed by numbered items such as "15.1", "15.2", "15.3" that all share the same first number, those items are the CONTENT OF THAT ONE CHAPTER, not separate chapters. Output the bold heading as P, and output each numbered item as a C line keeping its full printed number (15.1, 15.2, ...).

Rules:
- Copy titles word for word, including punctuation. If a title wraps to a second line, join it into one.
- A TAB separates the fields.
- The page number MUST be the one printed on the page. NEVER invent, guess or reuse a chapter number as a page number. If you cannot see a page number for an entry, leave that entry out.
- Skip: author and editor names, contributor lists, front matter with roman numerals, and lines with no page number.
- If this page holds no Table of Contents entries at all, output nothing at all.
- No commentary, no markdown, no JSON, no explanation."""

FRONT_WORDS = re.compile(r"\b(preface|contributors?|acknowledg\w*|dedication|"
                         r"about the authors?|front matter|index|glossary|"
                         r"advertisement|erratum|copyright|foreword)\b", re.I)
PAGE_FIELD = re.compile(r"(\d{1,5})\s*$")


# ---------------------------------------------------------------- rendering
def render(pdf: Path, outdir: Path, first: int, last: int, dpi: int):
    outdir.mkdir(parents=True, exist_ok=True)
    for f in outdir.glob("*.png"):
        f.unlink()
    subprocess.run(["pdftoppm", "-f", str(first), "-l", str(last), "-r", str(dpi),
                    "-png", "-gray", str(pdf), str(outdir / "p")],
                   capture_output=True, timeout=3600)
    got = {}
    for f in outdir.glob("p-*.png"):
        got[int(re.sub(r"\D", "", f.stem) or 0)] = f
    return [got[k] for k in sorted(got)]


def sheet(files, first_page, outpath, cols=COLS):
    from PIL import Image, ImageDraw, ImageFont
    ims = []
    try:
        font = ImageFont.load_default(size=40)
    except TypeError:
        font = ImageFont.load_default()
    tw = 520
    for f in files:
        im = Image.open(f).convert("L")
        ims.append((f, im.resize((tw, int(im.height * tw / im.width)))))
    if not ims:
        return None
    cell_h = max(i.height for _, i in ims) + 50
    canvas = Image.new("L", (cols * tw, ((len(ims) + cols - 1) // cols) * cell_h), 255)
    d = ImageDraw.Draw(canvas)
    for k, (f, im) in enumerate(ims):
        x, y = (k % cols) * tw, (k // cols) * cell_h
        d.rectangle([x, y, x + tw, y + 46], fill=0)
        d.text((x + 10, y + 8), f"PAGE {first_page + k}", fill=255, font=font)
        canvas.paste(im, (x, y + 50))
    canvas.save(outpath)
    return outpath


# ------------------------------------------------------------------ parsing
def parse(answer, doc, province, image=None):
    """Fold one page's P/C lines into the document. Returns lines accepted."""
    cur, got = None, 0
    for raw in answer.splitlines():
        if not raw.strip():
            continue
        f = raw.split("\t")
        if len(f) < 2:
            f = re.split(r"\s{2,}", raw.strip())
        f = [x.strip() for x in f]
        if f[0] == "P" and len(f) >= 2 and f[1]:
            # the model often prints a bare "P<TAB>UNIT III" with no third
            # field; dropping those silently moved a whole unit's chapters
            # into the unit before it (measured on GUYTON-2026: 15 units
            # instead of 11). The same heading also reappears on the next
            # page, so one province per heading, not one per line.
            above = f[2] if len(f) >= 3 and f[2] else f[1]
            # the same heading often reappears on the next page; one
            # province per heading, not one per line (measured on
            # GUYTON-2026: 15 "units" for a book that has 11)
            if doc["provinces"] and doc["provinces"][-1]["name"] == f[1]:
                cur = doc["provinces"][-1]
            else:
                cur = {"name": f[1], "part_name": above, "chapters": []}
                doc["provinces"].append(cur)
            got += 1
        elif f[0] == "C" and len(f) >= 3:
            num, title = f[1], f[2]
            # the page number is sometimes its own field and sometimes sits
            # at the end of the title field. CAMPBELL-2020 printed it inside
            # the title, and rejecting those lines silently threw away 1,300
            # of the book's 1,686 entries.
            tail = f[3] if len(f) > 3 else f[2]
            m = PAGE_FIELD.search(tail)
            if not title or not m or FRONT_WORDS.search(title):
                continue
            if len(f) <= 3:
                title = title[:m.start()].strip().rstrip(",;:").strip()
            if cur is None:
                # a contents page often STARTS in the middle of a unit,
                # before its banner is printed. Those chapters belong to
                # the unit above; creating a second province with the same
                # name duplicated whole units (measured on GUYTON-2026:
                # "UNIT V" appeared twice).
                if doc["provinces"]:
                    cur = doc["provinces"][-1]
                else:
                    cur = {"name": province, "part_name": province,
                           "chapters": []}
                    doc["provinces"].append(cur)
            entry = {
                "number": None if num in ("-", "", "—") else num,
                "title": title,
                "page_start": int(m.group(1)),
            }
            if image is not None:
                entry["_image"] = image
            cur["chapters"].append(entry)
            got += 1
    return got


# -------------------------------------------------------------------- stages
def locate(bid, pdf, start, windows, visdir, stop_early=False):
    """Stage 1: the model names the contents pages, window after window."""
    found, notes, cursor, empty_run = [], [], start, 0
    for w in range(windows):
        last = cursor + PER_SHEET - 1
        files = render(pdf, visdir / f"w{w+1}", cursor, last, LOCATE_DPI)
        if not files:
            break
        sp = sheet(files, cursor, visdir / f"w{w+1}" / f"sheet.png")
        ans = ask(LOCATE_SYSTEM,
                  f"This sheet shows pages {cursor} to {cursor + len(files) - 1}.",
                  images=[sp], max_tokens=3000, expect_json=False, retries=2)
        m = re.search(r"PAGES\s*=\s*([^\n]*)", ans)
        note = re.search(r"NOTE\s*=\s*(.+)", ans)
        got = []
        if m and "NONE" not in m.group(1).upper():
            got = sorted({int(x) for x in re.findall(r"\d+", m.group(1))})
        new = [p for p in got if p not in found]
        found += new
        notes.append(f"window {cursor}-{cursor + len(files) - 1}: "
                     f"{got or 'NONE'}"
                     + (f" -- {note.group(1).strip()[:90]}" if note else ""))
        print(f"    window {cursor:4d}-{cursor + len(files) - 1:4d} -> "
              f"{got or 'NONE'}", flush=True)
        cursor = last + 1
        # MEASURED 2026-10-11 on SLEISENGER-11: stopping after two empty
        # windows declared "no contents page found" for a book whose
        # contents starts at image 21. Front matter can run to 40 pages, and
        # one locate call costs about 2 seconds, so the windows are simply
        # all scanned. --stop-early brings the old behaviour back.
        empty_run = 0 if new else empty_run + 1
        if stop_early and empty_run >= 2:
            break
    return sorted(set(found)), notes


def kind_of(answer):
    """What KIND of page did the model say it was? CHAPTERS / OTHER / ?."""
    m = re.search(r"KIND\s*=\s*(\w+)", answer or "")
    return m.group(1).upper() if m else "?"


def read_page(pdf, p, dpi, visdir):
    """One page, one call, alone. Returns (answer, lines)."""
    d = visdir / f"read-{p}"
    files = render(pdf, d, p, p, dpi)
    ans = ask(READ_SYSTEM, f"Image number {p}. Transcribe its contents.",
              images=files, max_tokens=6000, expect_json=False,
              retries=2, no_reasoning=True)
    if kind_of(ans) == "OTHER":
        return ans, 0
    probe = {"provinces": []}
    return ans, parse(ans, probe, "ALL")


def read_pages(bid, pdf, pages, visdir):
    """Stage 2: every named page rendered at 150 dpi and read ALONE.

    A page that yields almost nothing is read AGAIN at a higher resolution:
    some books print their contents in three columns of small type and the
    model gives up at 150 dpi (measured on CAMPBELL-2020, where images 9 and
    15 returned 5 and 1 lines and chapters 2, 14 and 20 went missing).
    """
    doc = {"provinces": []}
    raw, province, empty, weak, rejected = [], "ALL", [], [], []
    for n, p in enumerate(pages, 1):
        t = time.time()
        try:
            ans, _ = read_page(pdf, p, READ_DPI, visdir)
        except Exception as exc:  # noqa: BLE001 - recorded, never hidden
            print(f"    page {p} FAILED: {exc}", flush=True)
            continue
        # MEASURED 2026-10-12 on SABISTON-22 (found by the human, not by the
        # model): a "VIDEO CONTENTS" page is printed in the same columns with
        # the same section numbers as the real contents, so the locator named
        # it and the reader turned "Video 110.1 Pleural Effusion" into a
        # chapter. A page the model itself calls OTHER is now refused and
        # listed, never silently dropped.
        if kind_of(ans) == "OTHER":
            rejected.append(p)
            raw.append(f"\n===== image {p} =====\n{ans.strip()}")
            print(f"    [{n}/{len(pages)}] image {p:4d} "
                  f"{int(time.time()-t):3d}s REFUSED (look-alike page, "
                  f"not the contents)", flush=True)
            continue
        before = len(doc["provinces"]), sum(
            len(x["chapters"]) for x in doc["provinces"])
        mark = ""
        if not ans.strip():
            got = 0
        else:
            got = parse(ans, doc, province)
        if got < THIN_LINES:
            try:
                ans2, _ = read_page(pdf, p, RETRY_DPI, visdir)
                if kind_of(ans2) == "OTHER":
                    doc["provinces"] = doc["provinces"][:before[0]]
                    rejected.append(p)
                    raw.append(f"\n===== image {p} =====\n{ans2.strip()}")
                    print(f"    [{n}/{len(pages)}] image {p:4d} "
                          f"{int(time.time()-t):3d}s REFUSED at {RETRY_DPI}dpi "
                          f"(look-alike page)", flush=True)
                    continue
                doc["provinces"] = doc["provinces"][:before[0]]
                got2 = parse(ans2, doc, province)
                if got2 > got:
                    ans, got = ans2, got2
                    mark = f" retried at {RETRY_DPI}dpi -> {got2}"
                else:
                    doc["provinces"] = doc["provinces"][:before[0]]
                    parse(ans, doc, province)
            except Exception as exc:  # noqa: BLE001
                mark = f" retry failed: {exc}"
        raw.append(f"\n===== image {p} =====\n{ans}")
        if not ans.strip():
            empty.append(p)
        if got < THIN_LINES:
            weak.append((p, got))
        if got:
            province = doc["provinces"][-1]["name"]
        print(f"    [{n}/{len(pages)}] image {p:4d} {int(time.time()-t):3d}s "
              f"+{got} lines{mark}", flush=True)
    (LOGS / f"{bid}-vis-toc.txt").write_text("\n".join(raw))
    (LOGS / f"{bid}-vis-toc.json").write_text(
        json.dumps(doc, indent=1, ensure_ascii=False))
    # which IMAGE each entry came from, so a normalizer can distrust the
    # pages the reader found nearly empty (they are usually body text that
    # the locator swept in, not a contents page)
    (LOGS / f"{bid}-vis-pages.json").write_text(
        json.dumps({"thin": [p for p, _ in weak], "empty": empty,
                    "refused_lookalike": rejected}, indent=1))
    return doc, empty, weak, rejected


def main():
    argv = " ".join(sys.argv[1:]) + " "
    args = [a for a in sys.argv[1:] if not a.startswith("--")]
    flags = [argv]
    books = {b["book_id"]: b for b in json.loads((KITCHEN / "books.json").read_text())}
    if not args:
        print("usage: python kitchen/toc_vision.py <BOOK_ID> [--start N] "
              "[--windows K]", flush=True)
        return 1
    bid = args[0]
    rec = books[bid]
    def flag(name, default):
        m = re.search(rf"--{name}\s+(\d+)", " ".join(flags) + " ")
        return int(m.group(1)) if m else default

    start = flag("start", 1)
    windows = flag("windows", 20)
    pdf = BOOKS / rec["pdf_file"]
    visdir = PAGES / bid / "vis"

    print(f"{bid}: model-locating the contents from image {start}, "
          f"{windows} window(s) of {PER_SHEET} pages ...", flush=True)
    pages, notes = locate(bid, pdf, start, windows, visdir,
                         stop_early='--stop-early' in argv)
    print(f"  the model named {len(pages)} contents page(s): {pages}", flush=True)
    if not pages:
        print("  no contents page found -- recorded, not invented.", flush=True)
        return 0
    print(f"  reading each one at {READ_DPI} dpi, one page per call ...",
          flush=True)
    doc, empty, weak, rejected = read_pages(bid, pdf, pages, visdir)
    n = sum(len(p["chapters"]) for p in doc["provinces"])
    print(f"  DONE {bid}: provinces={len(doc['provinces'])} chapters={n} "
          f"{len(empty)} pages empty", flush=True)
    if rejected:
        print(f"  LOOK-ALIKE PAGES REFUSED (videos/podcasts/index, not the "
              f"contents): {rejected}", flush=True)
    if weak:
        print(f"  THIN PAGES (ask the human, do not guess): {weak}", flush=True)
    (LOGS / "vis_read_latest.json").write_text(json.dumps(
        {"book_id": bid, "pages": pages, "notes": notes,
         "provinces": len(doc["provinces"]), "chapters": n,
         "empty_pages": empty, "thin_pages": weak,
         "refused_lookalike_pages": rejected}, indent=1,
        ensure_ascii=False))
    return 0


if __name__ == "__main__":
    sys.exit(main())