#!/usr/bin/env python3
"""Read the PDF's own bookmark outline -- chapter numbers AND page targets.

MEASURED 2026-10-16 on HAZZARD-2022: the contents prints no page numbers,
and only 64 of 128 chapters carry a clickable hyperlink (toc_links.py).
The same PDF, however, stores a full bookmark outline: 140 entries, one
per Part, Section and CHAPTER, each pointing at the chapter's true first
page. That is evidence from the book itself (Law 2), exactly like a
hyperlink -- it is NOT a guess and it costs ZERO model calls.

Writes kitchen/logs/<BOOK_ID>-vis-outline.json:
    {"book_id":..., "entries": n, "chapters_matched": n,
     "filled": n, "filled_numbers": [...], "structure": [...]}

Chapter pages are filled only where the geography still has none; a page
the reader printed or a PDF hyperlink gave is never overwritten.

    python kitchen/toc_outline.py HAZZARD-2022
"""
import json
import re
import sys
from pathlib import Path

from pypdf import PdfReader

ROOT = Path(__file__).resolve().parent.parent
KITCHEN = ROOT / "kitchen"
LOGS = KITCHEN / "logs"

BANNER = re.compile(
    r"^(PART|SECTION|VOLUME|VOL\.?|UNIT|BOOK|MODULE|DIVISION)\b"
    r"[\s:.\-]*([IVXLC0-9]+)?\b\s*(.*)$", re.I)
CHAPTER = re.compile(r"^(\d{1,3}[A-Z]?)\s+(.{2,})$")


def norm(s):
    return re.sub(r"[^a-z0-9]+", " ", (s or "").lower()).strip()


def title_agrees(outline_title, toc_title):
    words = [w for w in norm(toc_title).split() if len(w) > 3][:4]
    if not words:
        return True
    hay = norm(outline_title)
    return all(w in hay for w in words)


def walk(reader, items, depth=0, out=None):
    out = [] if out is None else out
    for it in items:
        if isinstance(it, list):
            walk(reader, it, depth + 1, out)
            continue
        try:
            pg = reader.get_destination_page_number(it)
        except Exception:  # noqa: BLE001
            pg = None
        out.append({"title": str(it.title).strip(), "depth": depth,
                    "image": (pg + 1) if pg is not None and pg >= 0
                    else None})
    return out


def main():
    argv = sys.argv[1:]
    bid = [a for a in argv if not a.startswith("--")][0]
    books = json.loads((KITCHEN / "books.json").read_text())
    book = [b for b in books if b["book_id"] == bid][0]
    pdf = KITCHEN / "books" / book["pdf_file"]

    toc_path = LOGS / f"{bid}-vis-toc.json"
    doc = json.loads(toc_path.read_text())

    reader = PdfReader(str(pdf))
    entries = walk(reader, reader.outline)

    chapters, structure = [], []
    for e in entries:
        t = e["title"]
        m = CHAPTER.match(t)
        if m and e["image"]:
            chapters.append({"number": m.group(1), "title": m.group(2).strip(),
                             "image": e["image"]})
            continue
        if BANNER.match(t):
            structure.append({"name": t, "image": e["image"],
                              "depth": e["depth"]})

    by_num = {}
    for c in chapters:
        by_num.setdefault(str(c["number"]), c)

    filled, filled_numbers, skipped = [], [], []
    for prov in doc.get("provinces", []):
        for c in prov.get("chapters", []):
            num = str(c.get("number", "")).strip()
            oc = by_num.get(num)
            if oc is None or c.get("page_start") is not None:
                if oc is not None and c.get("page_start") is None:
                    skipped.append({"number": num, "why": "no outline match"})
                continue
            if not title_agrees(oc["title"], c.get("title", "")):
                skipped.append({"number": num,
                                "why": "outline title disagrees",
                                "outline_title": oc["title"],
                                "toc_title": c.get("title")})
                continue
            c["page_start"] = oc["image"]
            c["_page_source"] = "pdf-outline"
            c["_outline_image"] = oc["image"]
            filled.append({"number": num, "title": c.get("title"),
                           "image": oc["image"]})
            filled_numbers.append(num)

    toc_path.write_text(json.dumps(doc, indent=1, ensure_ascii=False))
    res = {"book_id": bid, "entries": len(entries),
           "outline_chapters": len(chapters), "matched": len(filled),
           "filled": filled, "skipped": skipped, "structure": structure}
    (LOGS / f"{bid}-vis-outline.json").write_text(
        json.dumps(res, indent=1, ensure_ascii=False))
    print(f"{bid}: outline entries={len(entries)} "
          f"outline chapters={len(chapters)}")
    print(f"  chapters filled from the outline: {len(filled)}")
    print(f"  skipped: {json.dumps(skipped)[:400]}")
    print(f"  structure banners kept in vis-outline.json: {len(structure)}")

    if "--regroup" in argv:
        # MEASURED 2026-10-16 on HAZZARD-2022: the contents was read page by
        # page and its Section banners came back duplicated across Parts, so
        # the provinces sat in a wrong order. The PDF outline prints the SAME
        # banners with their true positions, so the geography is rebuilt from
        # them: every chapter joins the last banner printed BEFORE it. Book
        # evidence, zero model calls.
        banners = sorted([b for b in structure if b["image"]],
                         key=lambda b: b["image"])
        flat = [c for prov in doc["provinces"] for c in prov["chapters"]]

        def cimg(c):
            for k in ("_outline_image", "_link_image"):
                if isinstance(c.get(k), int):
                    return c[k]
            v = c.get("page_start")
            return v if isinstance(v, int) else None

        for c in flat:
            c["_sort_image"] = cimg(c)
        ordered = sorted([c for c in flat if c["_sort_image"]],
                         key=lambda c: (c["_sort_image"],
                                        str(c.get("number"))))
        provinces = []
        for c in ordered:
            home = None
            for b in banners:
                if b["image"] <= c["_sort_image"]:
                    home = b
                else:
                    break
            name = home["name"] if home else "ALL"
            if not provinces or provinces[-1]["name"] != name:
                provinces.append({"name": name, "part_name": name,
                                  "chapters": []})
            provinces[-1]["chapters"].append(c)
        orphans = [c for c in flat if not c["_sort_image"]]
        if orphans and provinces:
            provinces[-1]["chapters"].extend(orphans)
        doc["provinces"] = provinces
        toc_path.write_text(json.dumps(doc, indent=1, ensure_ascii=False))
        print(f"  regrouped under the outline banners: "
              f"{len(provinces)} provinces", flush=True)
        for p in provinces:
            nums = [c["number"] for c in p["chapters"]]
            print(f"    {p['name'][:58]:60s} {len(nums):3d} ch "
                  f"{nums[0]}-{nums[-1]}", flush=True)


if __name__ == "__main__":
    sys.exit(main())
