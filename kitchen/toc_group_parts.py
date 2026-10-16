"""kitchen/toc_group_parts.py -- regroup chapters under their Part banner.

The supersede pass in toc_dedupe.py works on a flat list, so after it runs
the province column is a single placeholder. For books read from their
chapter-opening pages (kitchen/toc_openers.py) the Part is not printed in
the chapter list at all: it is in the model's PART line on that chapter's
own opening page, which is recorded in <BOOK_ID>-openers.txt. This script
puts the chapters back under their Part, and drops the entries whose
"chapter number" is not a number at all -- those are ordinary pages the
model was asked about and answered about incorrectly, and they are counted
rather than quietly kept.

    python kitchen/toc_group_parts.py SLEISENGER-11
"""
import json
import re
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from reader import ask  # noqa: E402
from toc_vision import BOOKS, PAGES, render  # noqa: E402

KITCHEN = Path(__file__).resolve().parent
LOGS = KITCHEN / "logs"

PART_SYSTEM = """You are looking at ONE page of a medical textbook. I only want the PART banner printed at the top of the page, for example "PART VI   Gastrointestinal Infections".

Many books print NO banner on the chapter-opening page itself. Instead the very top of an ORDINARY page carries a thin running header such as "1654 PART VII Bone and Soft Tissue Reconstructions" -- a page number, then the part name. If there is no banner but such a header names a Part, report that part WITHOUT the leading page number: "PART VII Bone and Soft Tissue Reconstructions".

Answer with exactly one line and nothing else:
PART<TAB>the banner exactly as printed, or the part taken from the running header

If the page carries no part banner and no running header naming a part, answer PART=-."""

# MEASURED 2026-10-16 on GREEN-HAND-2021: a chapter-OPENING page of this
# Elsevier book prints only the big chapter number and the title -- no
# banner, and not even a running header. The part name lives in the thin
# header of the ORDINARY pages inside the chapter (e.g. image 1903:
# "1664 PART VII Bone and Soft Tissue Reconstructions"). So when an
# opening page has no banner, the NEXT image is asked for its header.
HEADER_SYSTEM = """You are looking at ONE ordinary page of a medical textbook.

At the very top of the page there may be a thin running header: a small page number followed by the name of the Part or Section, for example "1664 PART VII Bone and Soft Tissue Reconstructions".

Answer with exactly one line and nothing else:
H<TAB>the running header text exactly as printed

If the page has no running header, or the header names no Part or Section, answer H=-."""


def fill_missing_parts(bid, part_of, dpi=220):
    """Ask the model again for the Part banner on every opening page where
    it came back empty. MEASURED: 40 of Sleisenger's 132 opening pages
    returned no part, which left 49 chapters stacked under one unnamed
    province. If the opening page itself carries nothing, the running
    header of the NEXT (ordinary) page is asked for instead."""
    import subprocess
    rec = {b["book_id"]: b for b in
           json.loads((KITCHEN / "books.json").read_text())}[bid]
    pdf = BOOKS / rec["pdf_file"]
    pages_total = int(re.search(
        r"Pages:\s+(\d+)",
        subprocess.run(["pdfinfo", str(pdf)], capture_output=True,
                       text=True).stdout).group(1))
    doc = json.loads((LOGS / f"{bid}-vis-toc.json").read_text())
    need = sorted({c["_image"] for p in doc["provinces"]
                   for c in p["chapters"]} - set(part_of))
    print(f"    {len(need)} opening page(s) have no Part banner; asking again",
          flush=True)
    got = 0
    part_words = re.compile(
        r"^(PART|VOLUME|VOL\.?|UNIT|SECTION|BOOK|MODULE|DIVISION)\b",
        re.I)
    for img in need:
        files = render(pdf, PAGES / "part-retry" / f"i{img}", img, img, dpi)
        ans = ask(PART_SYSTEM, f"Image number {img}.", images=files,
                  max_tokens=400, expect_json=False, retries=2,
                  no_reasoning=True)
        val = None
        m = re.search(r"PART\s*\t?\s*(.+)", ans)
        if m:
            v = m.group(1).strip()
            if v.startswith("="):  # the model often answers "PART=-"
                v = v[1:].strip()
            if v not in ("-", ""):
                val = v
        if val is None and img + 1 <= pages_total:
            # the opening page itself carries no header; ask the NEXT
            # (ordinary) page for its running header
            files = render(pdf, PAGES / "part-retry" / f"h{img}",
                           img + 1, img + 1, dpi)
            ans = ask(HEADER_SYSTEM, f"Image number {img + 1}.",
                      images=files, max_tokens=400, expect_json=False,
                      retries=2, no_reasoning=True)
            m = re.search(r"H\s*\t?\s*(.+)", ans)
            if m:
                v = re.sub(r"^\s*\d+\s*", "", m.group(1)).strip()
                v = re.sub(r"\s+", " ", v)
                if part_words.match(v):
                    val = v
        if val:
            part_of[img] = val
            got += 1
            print(f"    image {img}: part -> {val}", flush=True)
    print(f"    recovered {got} of {len(need)}", flush=True)
    return part_of


def main():
    bid = sys.argv[1]
    doc = json.loads((LOGS / f"{bid}-vis-toc.json").read_text())
    part_of = {}
    for block in (LOGS / f"{bid}-openers.txt").read_text().split(
            "===== image ")[1:]:
        img = int(block.split(" ")[0])
        for line in block.splitlines():
            f = [x.strip() for x in line.split("\t")]
            # the model sometimes splits a banner across tab fields
            # ("PART<TAB>VI<TAB>Biology of the ..."), so the whole rest of
            # the line is the banner, not just the first piece
            if len(f) >= 2 and f[0] == "PART":
                val = " ".join(f[1:]).replace("\t", " ").strip()
                val = re.sub(r"\s+", " ", val)
                if val and val not in ("-", "=-"):
                    part_of[img] = val
    if "--fix" in sys.argv and part_of:
        part_of = fill_missing_parts(bid, part_of)
    # targeted re-reads of the Part banner, kept in their own file so the
    # first reading is never overwritten in place
    fixfile = LOGS / f"{bid}-partfix.json"
    if fixfile.exists():
        words = ("PART", "VOLUME", "VOL", "UNIT", "SECTION", "BOOK", "MODULE")
        for img, ans in json.loads(fixfile.read_text()).items():
            raw = ans.replace("=", " ").replace("\t", " ")
            raw = re.sub(r"\s+", " ", raw).strip()
            # shapes seen: "PART<TAB>-", "PART<TAB>VIII<TAB>Biliary Tract",
            # "PART VIII<TAB>Biliary Tract", "PART=<TAB>IX<TAB>Liver",
            # "PART PART III<TAB>Symptoms..." -- so drop the leading
            # keyword and any "-" field, then put one keyword back
            parts = [x for x in raw.split(" ") if x and x != "-"]
            if not parts:
                continue
            if parts[0].upper() in words:
                parts = parts[1:]
            if not parts:
                continue
            val = "PART " + " ".join(parts)
            val = re.sub(r"^(PART|VOLUME|UNIT|SECTION|BOOK|MODULE)\s+\1\b",
                         r"\1", val, flags=re.I)
            part_of[int(img)] = val
            print(f"    part banner from a targeted re-read, image {img}: "
                  f"{val}", flush=True)
    chapters = [c for p in doc["provinces"] for c in p["chapters"]]
    provinces, cur, dropped = [], None, []
    for c in sorted(chapters, key=lambda x: x.get("page_start") or 0):
        if not str(c.get("number") or "").isdigit():
            dropped.append(c)
            continue
        part = part_of.get(c.get("_image"))
        if part and part != cur:
            cur = part
            provinces.append({"name": part, "part_name": part, "chapters": []})
        if provinces:
            provinces[-1]["chapters"].append(c)
        else:
            provinces.append({"name": "ALL", "part_name": "ALL",
                              "chapters": [c]})
    (LOGS / f"{bid}-vis-toc.json").write_text(
        json.dumps({"provinces": provinces}, indent=1, ensure_ascii=False))
    (LOGS / f"{bid}-vis-dropped.json").write_text(
        json.dumps(dropped, indent=1, ensure_ascii=False))
    n = sum(len(p["chapters"]) for p in provinces)
    print(f"{bid}: parts={len(provinces)} chapters={n} "
          f"dropped_non_chapters={len(dropped)}", flush=True)
    for p in provinces:
        print(f"    {p['name'][:60]:62s} {len(p['chapters']):3d} "
              f"ch {p['chapters'][0]['number']}-{p['chapters'][-1]['number']}",
              flush=True)
    return 0


if __name__ == "__main__":
    sys.exit(main())