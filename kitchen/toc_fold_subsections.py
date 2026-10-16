"""kitchen/toc_fold_subsections.py -- fold loose sub-headings into their Section.

MEASURED 2026-10-16 on GRAY-2020: the printed contents puts SECTION banners
("SECTION 4: HEAD AND NECK") around groups of chapters, and prints smaller
unnumbered headings ("Head and neck", "Upper aerodigestive tract", "Special
senses") INSIDE those groups. The reader kept both as sibling provinces, so
the book came out with 17 provinces of which 8 were heading fragments of a
Section that already existed.

The rule is the book's own layout, never a guess: an unnumbered province is
folded into the numbered province printed ABOVE it, and its chapters join in
chapter-number order. MEASURED on GRAY-2020 the result is contiguous
(Section 4 = chapters 33-45, Section 7 = 52-58, Section 8 = 59-75), which is
the check that the fold is right.

No side file is written for a folded heading. Nir's rule (16 Oct 2026): ALL
books are treated the SAME way -- no book gets an extra file the others do
not have. The folded names remain available in the backup copy of
vis-toc.json and in the book's own printed contents, which we already hold.

Chapter count must not change. Nothing is invented, nothing is dropped
(Law 2, Law 11).

    python kitchen/toc_fold_subsections.py GRAY-2020            # dry run
    python kitchen/toc_fold_subsections.py GRAY-2020 --apply
"""
import json
import re
import sys
from pathlib import Path

KITCHEN = Path(__file__).resolve().parent
LOGS = KITCHEN / "logs"

TOP = re.compile(
    r"^(PART|VOLUME|VOL|UNIT|BOOK|SECTION|MODULE)\b[\s:.\-\u2014]*"
    r"(\d+|[IVXLCDM]+|"
    r"ONE|TWO|THREE|FOUR|FIVE|SIX|SEVEN|EIGHT|NINE|TEN|ELEVEN|TWELVE|"
    r"THIRTEEN|FOURTEEN|FIFTEEN|SIXTEEN|SEVENTEEN|EIGHTEEN|NINETEEN|"
    r"TWENTY|THIRTY|FORTY|FIFTY|SIXTY|SEVENTY|EIGHTY|NINETY)", re.I)


def numbered(name):
    return bool(TOP.match(str(name or "").strip()))


def ckey(c):
    n = c.get("number")
    try:
        return (0, int(n), "")
    except (TypeError, ValueError):
        return (1, 0, str(n))


def fold_book(bid, apply=False):
    path = LOGS / f"{bid}-vis-toc.json"
    if not path.exists():
        print(f"{bid}: no {path.name}")
        return None
    doc = json.loads(path.read_text())
    provs = doc.get("provinces", [])
    print(f"\n===== {bid} ({len(provs)} provinces before)")

    groups = []          # [(province, [folded provinces])]
    parent = None
    loose = []
    for p in provs:
        if numbered(p.get("name")):
            parent = (p, [])
            groups.append(parent)
        elif parent is None:
            print(f"  !! loose heading BEFORE any numbered one: "
                  f"{p.get('name')!r} -- left alone, nothing guessed")
            groups.append((p, []))   # kept as its own province
        else:
            parent[1].append(p)
            loose.append((p, parent[0]))

    if not loose:
        print(f"{bid}: no loose sub-headings -- nothing to do")
        return {"book": bid, "folded": 0}

    before = sum(len(p.get("chapters", [])) for p in provs)
    out = []
    for p, folded in groups:
        chs = list(p.get("chapters", []))
        for f in folded:
            chs.extend(f.get("chapters", []))
            print(f"  fold  {f.get('name')!r}  ({len(f.get('chapters', []))}"
                  f" ch)  ->  {p.get('name')!r}")
        chs.sort(key=ckey)
        nums = [c.get("number") for c in chs]
        if chs:
            pages = [c["page_start"] for c in chs
                     if isinstance(c.get("page_start"), (int, float))]
            p["page_start"] = int(min(pages)) if pages else None
            p["page_end"] = int(max(pages)) if pages else None
        p["chapters"] = chs
        print(f"  kept  {p.get('name')!r}  -> {len(chs)} chapters "
              f"{nums[0]}..{nums[-1]}" if chs else
              f"  kept  {p.get('name')!r}  (no chapters)")
        out.append(p)

    after = sum(len(p.get("chapters", [])) for p in out)
    if after != before:
        print(f"  !! CHAPTER COUNT CHANGED {before} -> {after} -- NOT WRITING")
        return None
    print(f"  chapters {before} -> {after} (unchanged), "
          f"provinces {len(provs)} -> {len(out)}")
    if not apply:
        print(f"  (dry run -- --apply to write)")
        return {"book": bid, "folded": len(loose)}

    doc["provinces"] = out
    path.write_text(json.dumps(doc, indent=1, ensure_ascii=False))
    print(f"  WRITTEN: {path.name}")
    return {"book": bid, "folded": len(loose)}


def main():
    argv = [a for a in sys.argv[1:] if not a.startswith("--")]
    apply = "--apply" in sys.argv
    stats = [r for b in argv if (r := fold_book(b, apply))]
    if stats:
        print(f"\n--- total sub-headings folded: "
              f"{sum(s['folded'] for s in stats)}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
