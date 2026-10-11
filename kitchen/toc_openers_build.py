"""kitchen/toc_openers_build.py -- assemble the geography from the openers.

kitchen/toc_openers.py records, for every chapter-opening page the model
found, the model's own four lines (PART / NUM / TITLE / PAGE). This script
turns those recordings into the geography, and repairs two measured faults:

  1. PAGES THAT GAVE NOTHING. 37 of Sleisenger's 146 opening pages returned
     no chapter at 150 dpi. Each of them is read again at 240 dpi.
  2. MISSING CHAPTER NUMBERS. 31 of Sleisenger's chapters were absent. A
     chapter's opening page always lies between the opening pages of the
     chapters around it, so for each missing number the model is asked,
     page by page, "does this page open chapter N?" -- the model decides,
     the arithmetic only says where to look.

Chapters are then grouped under the PART banner printed on their own
opening page.

    python kitchen/toc_openers_build.py SLEISENGER-11
"""
import json
import re
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from reader import ask  # noqa: E402
from toc_vision import BOOKS, LOGS, PAGES, READ_DPI, render  # noqa: E402

RETRY_DPI = 240

ONE_SYSTEM = """You are looking at ONE page: the OPENING PAGE of a chapter in a medical textbook.

Report exactly what is printed there:
PART<TAB>the part banner printed at the top of the page, exactly as printed (for example "PART I   Biology of the Gastrointestinal Tract"), or a single dash if there is none
NUM<TAB>the LARGE chapter number printed with the chapter title
TITLE<TAB>that chapter's title exactly as printed
PAGE<TAB>the PRINTED page number of this page, from the page's own header or footer

A thin running header along the top of an ordinary page -- a small page number followed by a part name -- means this is an ordinary page, NOT a chapter opening. In that case write nothing."""

WHICH_SYSTEM = """You are looking at ONE page of a medical textbook.

Answer with exactly one line and nothing else:
H<TAB>the chapter number that opens on this page, or NONE

Only a page that shows a LARGE chapter number together with a chapter title counts. A thin running header at the top of an ordinary page is not a chapter number."""


def parse_openers(bid):
    """image -> {part, num, title, page}, straight from the model's words."""
    src = LOGS / f"{bid}-openers.txt"
    out = {}
    for block in src.read_text().split("===== image ")[1:]:
        img = int(block.split(" ")[0])
        got = {}
        for line in block.splitlines():
            f = [x.strip() for x in line.split("\t")]
            if len(f) >= 2 and f[0] in ("PART", "NUM", "TITLE", "PAGE"):
                got[f[0]] = f[1]
        if "TITLE" in got and "NUM" in got:
            out[img] = got
    return out


def read_one(pdf, img, dpi):
    files = render(pdf, PAGES / "openers-retry" / f"i{img}", img, img, dpi)
    ans = ask(ONE_SYSTEM, f"Image number {img}.", images=files,
              max_tokens=1500, expect_json=False, retries=2, no_reasoning=True)
    got = {}
    for line in ans.splitlines():
        f = [x.strip() for x in line.split("\t")]
        if len(f) >= 2 and f[0] in ("PART", "NUM", "TITLE", "PAGE"):
            got[f[0]] = f[1]
    return got if ("TITLE" in got and "NUM" in got) else None


def ask_which(pdf, img, want):
    files = render(pdf, PAGES / "openers-which" / f"i{img}", img, img, 200)
    ans = ask(WHICH_SYSTEM + f"\n\nThe chapter number I am looking for is {want}.",
              f"Image number {img}.", images=files, max_tokens=200,
              expect_json=False, retries=2, no_reasoning=True)
    m = re.search(r"H\s*\t?\s*(\d+)", ans)
    return int(m.group(1)) if m else None


def build(bid):
    rec = {b["book_id"]: b for b in
           json.loads((Path(__file__).resolve().parent / "books.json").read_text())}
    pdf = BOOKS / rec[bid]["pdf_file"]
    found = parse_openers(bid)
    print(f"{bid}: {len(found)} opening pages carry a chapter", flush=True)

    # 1. retry the pages that gave nothing
    images = json.loads((LOGS / f"{bid}-openers.json").read_text())
    for img in images:
        if img in found:
            continue
        got = read_one(pdf, img, RETRY_DPI)
        if got:
            found[img] = got
            print(f"    image {img} at {RETRY_DPI} dpi -> chapter "
                  f"{got['NUM']}", flush=True)

    # 2. look for the chapters that are still missing
    def numbers():
        return {int(g["NUM"]): i for i, g in found.items()
                if g["NUM"].isdigit()}

    for _ in range(3):
        nums = numbers()
        if not nums:
            break
        lo, hi = min(nums), max(nums)
        gaps = [n for n in range(lo, hi + 1) if n not in nums]
        if not gaps:
            break
        print(f"    still missing {len(gaps)} chapter(s): {gaps[:14]}",
              flush=True)
        found_any = False
        for n in gaps:
            below = [i for k, i in nums.items() if k < n]
            above = [i for k, i in nums.items() if k > n]
            if not below or not above:
                continue
            for img in range(max(below) + 1, min(above)):
                got = ask_which(pdf, img, n)
                if got == n:
                    one = read_one(pdf, img, READ_DPI)
                    if one:
                        found[img] = one
                        found_any = True
                        print(f"    chapter {n} found at image {img}: "
                              f"{one['TITLE'][:44]}", flush=True)
                        break
        if not found_any:
            break

    # 3. group under the part banner printed on each opening page
    provinces, cur = [], None
    for img in sorted(found):
        g = found[img]
        part = g.get("PART", "-")
        if part and part != "-":
            cur = {"name": part, "part_name": part, "chapters": []}
            provinces.append(cur)
        if cur is None:
            cur = {"name": "ALL", "part_name": "ALL", "chapters": []}
            provinces.append(cur)
        m = re.search(r"[0-9]+", g.get("PAGE", ""))
        cur["chapters"].append({
            "number": g["NUM"], "title": g["TITLE"],
            "page_start": int(m.group(0)) if m else None, "_image": img})
    doc = {"provinces": provinces}
    (LOGS / f"{bid}-vis-toc.json").write_text(
        json.dumps(doc, indent=1, ensure_ascii=False))
    n = sum(len(p["chapters"]) for p in provinces)
    nums = sorted(int(c["number"]) for p in provinces for c in p["chapters"]
                  if str(c["number"]).isdigit())
    miss = [x for x in range(min(nums), max(nums) + 1) if x not in set(nums)]
    print(f"{bid}: parts={len(provinces)} chapters={n} "
          f"numbers {min(nums)}-{max(nums)} missing={len(miss)} {miss[:14]}",
          flush=True)
    for p in provinces:
        print(f"    {p['name'][:58]:60s} {len(p['chapters']):3d}", flush=True)
    return 0


if __name__ == "__main__":
    sys.exit(build(sys.argv[1]))