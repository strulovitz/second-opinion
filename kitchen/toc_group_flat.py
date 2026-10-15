"""kitchen/toc_group_flat.py -- give a flat book the parts its author left out.

MEASURED 2026-10-15: ROBBINS-10, THOMPSON-2023 and BRENNER-11 print a
contents with no Part or Section banner at all, so each one came out as a
single province called "ALL" holding every chapter. Nir's decision: do the
work the author should have done -- group the chapters under written parts
whose titles cover every chapter in the group, in the same style as the
books that DID print theirs ("Part 9 - Rheumatoid Arthritis and Sjogren's
Syndrome").

The grouping is a HUMAN decision and lives in kitchen/parts/<BOOK>.json as
a list of {"name": ..., "chapters": [...]}. This script only applies it and
records name_source = "written" on every province, so the database can
always tell a part the book printed from a part we wrote (Law 2). A chapter
that no group claims is reported and left unfiled; nothing is invented and
no chapter is dropped.

    python kitchen/toc_group_flat.py ROBBINS-10 [--apply]
"""
import json
import sys
from pathlib import Path

KITCHEN = Path(__file__).resolve().parent
LOGS = KITCHEN / "logs"
PARTS = KITCHEN / "parts"


def main():
    argv = [a for a in sys.argv[1:] if not a.startswith("--")]
    apply = "--apply" in sys.argv
    for bid in argv:
        spec_path = PARTS / f"{bid}.json"
        toc_path = LOGS / f"{bid}-vis-toc.json"
        if not spec_path.exists():
            print(f"{bid}: no grouping written yet -> {spec_path}")
            continue
        if not toc_path.exists():
            print(f"{bid}: no {toc_path.name}")
            continue
        spec = json.loads(spec_path.read_text())
        doc = json.loads(toc_path.read_text())
        flat = [c for p in doc["provinces"] for c in p.get("chapters", [])]
        by_num = {}
        for c in flat:
            by_num.setdefault(str(c.get("number")), c)
        print(f"\n===== {bid} ({len(flat)} chapters, "
              f"{len(spec)} written part(s))")
        used, new = set(), []
        for grp in spec:
            chs, missing = [], []
            for n in grp["chapters"]:
                c = by_num.get(str(n))
                if c is None:
                    missing.append(n)
                else:
                    chs.append(c)
                    used.add(str(n))
            if missing:
                print(f"  !! {grp['name']}: no such chapter(s) {missing}")
            print(f"  -> {grp['name']}  ({len(chs)} ch)")
            if chs:
                new.append({"name": grp["name"], "part_name": grp["name"],
                            "name_source": "written", "chapters": chs})
        orphan = [str(c.get("number")) for c in flat
                  if str(c.get("number")) not in used]
        if orphan:
            print(f"  !! chapters in NO part (left unfiled, never dropped): "
                  f"{orphan}")
        if not new:
            print(f"{bid}: nothing to write")
            continue
        n = sum(len(p["chapters"]) for p in new)
        print(f"{bid}: provinces={len(new)} chapters={n}"
              + ("" if apply else "  (dry run -- --apply to write)"))
        if apply:
            doc["provinces"] = new
            toc_path.write_text(json.dumps(doc, indent=1, ensure_ascii=False))
            print(f"{bid}: written")


if __name__ == "__main__":
    main()
