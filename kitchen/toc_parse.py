"""kitchen/toc_parse.py -- STEP A2, the cheap deterministic parser.

AMENDMENT 3.5 (declared by the manager, recorded in PROGRESS.md).

The BIBLE sends every Table of Contents to the free local READER. Measured on
2026-10-10, that costs about 3 minutes per book for a 27B model on this
laptop -- roughly 6 hours for the whole library -- and it produced visibly
worse answers than a script: on SABISTON-22 it dropped SECTION I entirely and
lost 3 of the sections' chapters, while a regex finds all 93.

Law 14 says cheap beats perfect and that the manager writes scripts instead of
doing grunt work. Table-of-contents lines are highly regular ("19 Principles
of Preoperative and Operative Surgery ....... 1581"), so a deterministic
parser is both cheaper and more accurate. The READER is still used, but only
where the script is unsure: kitchen/toc_to_json.py can be pointed at any book
to have the reader do that one instead.

The script writes the SAME JSON shape as the BIBLE's prompt P-A2, and it is
verified against the reader's own answer for the same books.

Output: kitchen/logs/<BOOK_ID>-toc.json, and a per-book confidence report.
"""
import json
import re
import sys
from pathlib import Path

KITCHEN = Path(__file__).resolve().parent
LOGS = KITCHEN / "logs"

# ---- what a chapter line looks like -------------------------------------
# numbered:   "19 Principles of Preoperative and Operative Surgery ...... 1581"
# unnumbered: "Fever and Rash ......................... 137"
NUM_CHAP = re.compile(
    r"(?:^|\s{2,})(\d{1,3})\s+([A-Z][A-Za-z0-9 ,'\-\(\)/&:;\.\+]{2,95}?)\s*\.{2,}\s*(\d{1,4})(?![0-9f-t])")
UNNUM_CHAP = re.compile(
    r"(?:^|\s{2,})([A-Z][A-Za-z0-9 ,'\-\(\)/&:;\.\+]{3,95}?)\s*\.{2,}\s*(\d{1,4})(?![0-9f-t])")
# a heading line: PART/SECTION/UNIT/BOOK, or a bare all-caps name with no page
PROVINCE = re.compile(
    r"^\s*((?:PART|SECTION|UNIT|BOOK)\s+[IVXLC0-9]+[^\n]{0,90})$", re.I)
BARE_CAPS = re.compile(r"^\s{0,20}([A-Z][A-Z0-9 ,'\-\(\)/&\.]{6,80})\s*$")
# front matter that must never become a territory
ROMAN = re.compile(r"^\s*[ivxlc]+\s*$", re.I)
FRONT_WORDS = re.compile(r"\b(preface|contributors|contributors\b|acknowledg|"
                         r"dedication|front matter|about the authors|index|glossary|"
                         r"advertisement|erratum|copyright|contents|foreword)\b", re.I)

# an all-caps line that is really a column heading, not a province
NOT_PROVINCE = re.compile(r"^(chapter|table|figure|section|unit|part|volume)\b", re.I)


def clean_title(t: str) -> str:
    t = re.sub(r"\s+", " ", t).strip(" .·•\t")
    t = re.sub(r"\s*\(\s*continued\s*\)\s*$", "", t, flags=re.I)
    return t.strip()


def parse_toc(text: str):
    """Return (document, stats)."""
    provinces, cur = [], None
    seen_pages, warnings = [], []
    romans = 0

    def province(name, part=None):
        p = {"name": name, "part_name": part or name, "chapters": []}
        provinces.append(p)
        return p

    for line in text.splitlines():
        if not line.strip():
            continue

        m = PROVINCE.match(line)
        if m and not NOT_PROVINCE.match(m.group(1)):
            cur = province(clean_title(m.group(1)))
            continue

        # unnumbered chapters first: a numbered chapter is a special case of it
        entries = []
        for mm in UNNUM_CHAP.finditer(line):
            entries.append((mm.start(), None, clean_title(mm.group(1)),
                            int(mm.group(2))))
        for mm in NUM_CHAP.finditer(line):
            entries.append((mm.start(), mm.group(1), clean_title(mm.group(2)),
                            int(mm.group(3))))
        entries.sort()

        for _pos, num, title, page in entries:
            if not title or FRONT_WORDS.search(title):
                continue
            if ROMAN.match(str(page)):
                romans += 1
                continue
            if num is None and len(title) < 5:
                continue
            if cur is None:
                cur = province("ALL")
            cur["chapters"].append({
                "number": num, "title": title, "page_start": page})
            seen_pages.append(page)

    # a bare all-caps line with no entries on it may still be a heading
    if not provinces:
        for line in text.splitlines():
            m = BARE_CAPS.match(line)
            if m and not NOT_PROVINCE.match(m.group(1)) \
                    and not FRONT_WORDS.search(m.group(1)):
                province(clean_title(m.group(1)))

    n = sum(len(p["chapters"]) for p in provinces)
    if not provinces:
        warnings.append("no province heading found")
    if n == 0:
        warnings.append("no chapter lines found")
    if n and not seen_pages:
        warnings.append("no pages")
    # pages must not go backwards (BIBLE 4.4)
    drops = sum(1 for a, b in zip(seen_pages, seen_pages[1:]) if b < a - 1)
    if drops:
        warnings.append(f"{drops} page-order drops")
    return {"provinces": provinces}, {
        "provinces": len(provinces), "chapters": n,
        "roman_pages_skipped": romans, "warnings": warnings}


def main():
    wanted = sys.argv[1:] or None
    books = [b for b in json.loads((KITCHEN / "books.json").read_text())
             if b["status"] == "candidate" and b["toc_images"]]
    if wanted:
        books = [b for b in books if b["book_id"] in wanted]
    stats = {}
    for b in books:
        bid = b["book_id"]
        src = LOGS / f"{bid}-toc.txt"
        if not src.exists():
            print(f"  {bid:26s} SKIP (no toc.txt)")
            continue
        doc, st = parse_toc(src.read_text())
        (LOGS / f"{bid}-toc.json").write_text(
            json.dumps(doc, indent=1, ensure_ascii=False))
        stats[bid] = st
        flag = "  <-- " + "; ".join(st["warnings"]) if st["warnings"] else ""
        print(f"  {bid:26s} provinces={st['provinces']:3d} "
              f"chapters={st['chapters']:4d}{flag}")
    (LOGS / "toc_parse_stats.json").write_text(
        json.dumps(stats, indent=1, ensure_ascii=False))
    print(f"\ntotal chapters parsed: "
          f"{sum(s['chapters'] for s in stats.values())}")


if __name__ == "__main__":
    main()