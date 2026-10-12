"""kitchen/toc_fix_misfiled.py -- move chapters that were filed under the WRONG section.

MEASURED 2026-10-12 on SABISTON-22, found by the honest validator (Law 11):
the contents of image 37 is printed in two columns and the model read the
top of the LEFT column (chapters 68-72, printed pages 819-906, which belong
to SECTION V SURGICAL ONCOLOGY) LAST. They therefore landed under
"SECTION IX VASCULAR SURGERY, 1579", whose printed start page is 1579 --
pages 819-906 are printed nowhere inside that section.

THE RULE IS THE BOOK'S OWN, not a guess: every section banner prints the
page where that section starts. A chapter whose printed page is BEFORE the
section it was filed under cannot belong to it. Such trailing chapters
continue the section above, which is exactly what the book prints.

Nothing is invented: page numbers are never changed and no entry is dropped.
Every move is written to kitchen/logs/<BOOK_ID>-vis-misfiled.json.

    python kitchen/toc_fix_misfiled.py SABISTON-22
"""
import json
import re
import sys
from pathlib import Path

KITCHEN = Path(__file__).resolve().parent
LOGS = KITCHEN / "logs"


def section_start(name):
    """The page a section banner prints, e.g. 'SECTION V SURGICAL ONCOLOGY, 721'."""
    m = re.search(r",\s*(\d{1,5})\s*$", name.strip())
    return int(m.group(1)) if m else None


def main():
    for bid in sys.argv[1:]:
        src = LOGS / f"{bid}-vis-toc.json"
        doc = json.loads(src.read_text())
        provs = [p for p in doc["provinces"] if p["chapters"]]
        moves = []
        for i in range(1, len(provs)):
            start = section_start(provs[i]["name"])
            if start is None:
                continue
            keep, moved = [], []
            for c in provs[i]["chapters"]:
                p = c.get("page_start")
                # only a TRAILING run counts: one out-of-place chapter in the
                # middle is a different fault and must not be swept along
                if p is not None and p < start:
                    moved.append(c)
                else:
                    keep.append(c)
            if not moved or len(moved) == len(provs[i]["chapters"]):
                provs[i]["chapters"] = keep + moved
                continue
            provs[i]["chapters"] = keep
            # MEASURED 2026-10-12 on SABISTON-22: chapters 68-72 (printed
            # pages 819-906) belong to SECTION V SURGICAL ONCOLOGY, which
            # starts on page 721 -- not to the section immediately above,
            # which starts on page 1107. The banner's own printed page says
            # which section a page belongs to: walk every province in printed
            # order and take the last one that starts at or before the page.
            target = None
            for j in range(len(provs)):
                s = section_start(provs[j]["name"])
                if s is None:
                    continue
                if all(s <= (c.get("page_start") or 0) for c in moved):
                    target = j
            home = provs[target if target is not None else i - 1]
            home["chapters"].extend(moved)
            home["chapters"].sort(
                key=lambda c: (c.get("page_start") is None,
                               c.get("page_start") or 0))
            moves.append({"from": provs[i]["name"], "to": home["name"],
                          "section_starts_at_page": start,
                          "chapters": [{"number": c.get("number"),
                                        "title": c.get("title"),
                                        "page_start": c.get("page_start")}
                                       for c in moved]})
        doc["provinces"] = [p for p in doc["provinces"] if p["chapters"]]
        src.write_text(json.dumps(doc, indent=1, ensure_ascii=False))
        (LOGS / f"{bid}-vis-misfiled.json").write_text(
            json.dumps({"moves": moves}, indent=1, ensure_ascii=False))
        n = sum(len(p["chapters"]) for p in doc["provinces"])
        print(f"{bid}: provinces={len(doc['provinces'])} chapters={n} "
              f"misfiled_groups_moved={len(moves)}", flush=True)
        for m in moves:
            print(f"    {len(m['chapters'])} chapter(s) moved from "
                  f"'{m['from'][:40]}' to '{m['to'][:40]}'", flush=True)
            for c in m["chapters"]:
                print(f"        {c['number']} p{c['page_start']} {c['title'][:52]}",
                      flush=True)


if __name__ == "__main__":
    sys.exit(main())