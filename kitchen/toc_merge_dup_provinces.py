# kitchen/toc_merge_dup_provinces.py
# A multi-volume book (Youmans) prints "PART 1", "PART 2" ... once per
# volume, so the same part can be read twice: once from a short contents and
# once from the full one. That leaves two provinces with the same name AND the
# same first page, holding chapters that overlap. This merges them into one
# province and keeps every chapter once, in printed page order.
#
# Nothing is typed by hand: it reads the JSON the reader produced and writes
# the JSON back. Zero model calls.
#
#   python kitchen/toc_merge_dup_provinces.py <BOOK_ID>

import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
LOGS = ROOT / "kitchen" / "logs"


def key(ch):
    """Identity of a chapter: its printed number and its first page."""
    return (str(ch.get("number")), ch.get("page_start"), str(ch.get("title")))


def main(bid):
    path = LOGS / f"{bid}-vis-toc.json"
    data = json.loads(path.read_text())
    provinces = data["provinces"]

    out = []
    seen = {}  # (name, page_start) -> index in out
    merged = 0
    dup_chapters = 0

    for p in provinces:
        k = (p.get("name"), p.get("page_start"))
        if k in seen:
            target = out[seen[k]]
            known = {key(c) for c in target["chapters"]}
            for c in p.get("chapters", []):
                if key(c) not in known:
                    target["chapters"].append(c)
                    known.add(key(c))
                else:
                    dup_chapters += 1
            merged += 1
            continue
        seen[k] = len(out)
        out.append(p)

    # Second repair: a truncated read can invent a whole part that is really
    # only a slice of the part before it. Youmans got a "PART 3" whose four
    # chapters all already sat in PART 2, while the real PART 3 stood further
    # on. Two parts cannot share one number, so the fragment goes -- but only
    # when every one of its chapters is already held, same number and same
    # page, by the larger part, AND another province already uses its name.
    dropped_parts = []
    for i, p in enumerate(list(out)):
        mine = {key(c) for c in p["chapters"]}
        if not mine:
            continue
        host = None
        for j, q in enumerate(out):
            if j == i:
                continue
            theirs = {key(c) for c in q["chapters"]}
            if mine <= theirs and len(q["chapters"]) > len(p["chapters"]):
                host = q
                break
        if host is None:
            continue
        if any(j != i and q.get("name") == p.get("name") for j, q in enumerate(out)):
            out.remove(p)
            dropped_parts.append((p.get("name"), len(p["chapters"])))

    for p in out:
        p["chapters"].sort(key=lambda c: (c.get("page_start") is None,
                                           c.get("page_start") or 0))

    data["provinces"] = out
    path.write_text(json.dumps(data, indent=1, ensure_ascii=False))

    total = sum(len(p["chapters"]) for p in out)
    print(f"  {bid}: provinces {len(provinces)} -> {len(out)} "
          f"(merged {merged}), chapters {total} "
          f"(dropped {dup_chapters} repeat(s))")


if __name__ == "__main__":
    if len(sys.argv) != 2:
        sys.exit(__name__)
    main(sys.argv[1])