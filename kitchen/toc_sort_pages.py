"""kitchen/toc_sort_pages.py -- put a book's chapters back in PRINTED order.

MEASURED 2026-10-12 on SABISTON-22 (found by the honest validator, Law 11):
one contents page is printed in two columns and the model read the RIGHT
column before the left, so the chapter list came out with
"... 1676 Ventral Hernias" followed by "819 Diseases of the Breast". The
printed page number is the book's own, never guessed, so sorting by it puts
the book back exactly as it is printed. Nothing is invented and nothing is
lost: the sort is recorded in kitchen/logs/<BOOK_ID>-vis-sort.json.

    python kitchen/toc_sort_pages.py SABISTON-22
"""
import json
import sys
from pathlib import Path

KITCHEN = Path(__file__).resolve().parent
LOGS = KITCHEN / "logs"


def main():
    for bid in sys.argv[1:]:
        src = LOGS / f"{bid}-vis-toc.json"
        doc = json.loads(src.read_text())
        moved = []
        for prov in doc["provinces"]:
            before = [c.get("page_start") for c in prov["chapters"]]
            prov["chapters"].sort(key=lambda c: (c.get("page_start") is None,
                                                 c.get("page_start") or 0))
            after = [c.get("page_start") for c in prov["chapters"]]
            if before != after:
                moved.append({"province": prov["name"],
                              "before": before, "after": after})
        src.write_text(json.dumps(doc, indent=1, ensure_ascii=False))
        (LOGS / f"{bid}-vis-sort.json").write_text(
            json.dumps({"sorted_provinces": moved}, indent=1,
                       ensure_ascii=False))
        n = sum(len(p["chapters"]) for p in doc["provinces"])
        print(f"{bid}: provinces={len(doc['provinces'])} chapters={n} "
              f"provinces_reordered={len(moved)}", flush=True)
        for m in moved:
            print(f"    {m['province'][:46]:48s} {m['before']} -> {m['after']}",
                  flush=True)


if __name__ == "__main__":
    sys.exit(main())