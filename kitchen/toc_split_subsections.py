#!/usr/bin/env python3
"""Keep the book's sub-section numbers OUT of the district list.

MEASURED 2026-10-16 on KAPLAN-11 (Kaplan & Sadock's Comprehensive Textbook
of Psychiatry): its contents prints a strict hierarchy -- chapter "11
Substance-Related Disorders", then numbered sub-entries "11.1", "11.2"...
(and deeper still, "33.13a.1", which the reader never saw as chapters).
Reading every printed number as a chapter produced 414 entries where other
books have 60, and every other book's districts are its CHAPTERS: books
whose sub-headings print no number are skipped by the reader (toc_vision
prompt: "Those have no number. SKIP THEM."), so a printed decimal number
must not silently change what a district is.

So: an entry whose printed number carries a decimal point or a letter
("1.1", "33.13a") is a SUB-ENTRY of the chapter whose integer number
matches. It is moved -- never dropped -- to
kitchen/logs/<BOOK_ID>-vis-subsections.json, with its parent chapter, so
Part 4 can use it later. Chapters (plain integers) stay in the geography.

    python kitchen/toc_split_subsections.py KAPLAN-11
"""
import json
import re
import sys
from pathlib import Path

KITCHEN = Path(__file__).resolve().parent
LOGS = KITCHEN / "logs"
SUB = re.compile(r"^(\d+)[.\-]?[a-zA-Z0-9]*\.[0-9a-zA-Z.\-]+$")
PLAIN = re.compile(r"^\d+[A-Z]?$")


def main():
    for bid in sys.argv[1:]:
        if bid.startswith("--"):
            continue
        jf = LOGS / f"{bid}-vis-toc.json"
        doc = json.loads(jf.read_text())
        moved, kept = [], 0
        parents = {str(c.get("number")).strip()
                   for p in doc["provinces"] for c in p["chapters"]
                   if PLAIN.match(str(c.get("number")).strip())}
        for prov in doc["provinces"]:
            keep = []
            for c in prov["chapters"]:
                num = str(c.get("number", "")).strip()
                if PLAIN.match(num):
                    keep.append(c)
                    continue
                m = SUB.match(num)
                parent = m.group(1) if m else num.split(".")[0].rstrip(".")
                moved.append({"parent_chapter": parent,
                              "province": prov["name"], **c})
            kept += len(keep)
            prov["chapters"] = keep

        # RECOVER CHAPTER-SHAPED HEADINGS. MEASURED 2026-10-16 on
        # KAPLAN-11: because a chapter's numbered sub-entries follow it,
        # the reader printed those chapters as P heading lines instead of
        # C chapter lines ("P  3  Contributions of the Psychological
        # Sciences"), and they vanished from the geography when their
        # heading province kept no chapter. The heading number alone ("3")
        # also lost the title, so the TRANSCRIPT P lines are read here --
        # the model's own words carry number AND title, nothing is
        # invented; the line is only re-read as what this book makes it:
        # a chapter that has entries under it.
        have = {str(c.get("number")).strip()
                for p in doc["provinces"] for c in p["chapters"]}
        tr = LOGS / f"{bid}-vis-toc.txt"
        recovered = []
        if tr.exists():
            seen = set()
            for line in tr.read_text().splitlines():
                if not line.startswith("P\t"):
                    continue
                fields = [f.strip() for f in line.split("\t")[1:] if f.strip()]
                if not fields:
                    continue
                if re.fullmatch(r"\d{1,3}", fields[0]):
                    num, rest = fields[0], fields[1:]
                else:
                    m = re.match(r"^(\d{1,3})\s+(.+)$", fields[0])
                    if not m:
                        continue
                    num, rest = m.group(1), [m.group(2)] + fields[1:]
                if not rest:
                    continue
                title = re.sub(rf"^\s*{num}\s+", "", rest[0]).strip()
                title = re.sub(rf"\s+\b{num}\s*$", "", title).strip()
                if not title or num in have or num in seen:
                    continue
                seen.add(num)
                have.add(num)
                recovered.append({"number": num, "title": title,
                                  "page_start": None,
                                  "_from_heading_line": True})
            if recovered:
                by_name = {p["name"].strip(): p for p in doc["provinces"]}
                for r in recovered:
                    home = by_name.get(r["number"])
                    if home is None:
                        home = doc["provinces"][0]
                    home["chapters"].append(r)
                kept += len(recovered)

        doc["provinces"] = [p for p in doc["provinces"] if p["chapters"]]
        if moved or recovered:
            jf.write_text(json.dumps(doc, indent=1, ensure_ascii=False))
            out = LOGS / f"{bid}-vis-subsections.json"
            out.write_text(json.dumps(
                {"note": "printed sub-section entries kept out of the "
                         "district list; parent_chapter is the chapter they "
                         "belong to (recorded, never dropped)",
                 "count": len(moved), "entries": moved},
                indent=1, ensure_ascii=False))
        print(f"{bid}: {len(moved)} sub-section entr(ies) moved to "
              f"{bid}-vis-subsections.json, {len(recovered)} heading-line "
              f"chapter(s) recovered, {kept} chapters remain", flush=True)


if __name__ == "__main__":
    sys.exit(main())
