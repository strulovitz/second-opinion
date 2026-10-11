"""kitchen/toc_normalize.py -- flatten a NESTED contents to one level.

THE HUMAN'S DECISION (2026-10-11), about CAMPBELL-2020 (Campbell's
Operative Orthopaedics): that book's contents has three levels -- VOLUME,
chapter block ("Amputations of the Foot"), and 1,686 individual techniques
("Syme Amputation"). The human ruled that the geography must stay
comparable with every other book, so the CHAPTER BLOCK is the district and
the techniques are kept for later, inside the chapter, where they belong.

Nothing is thrown away. The techniques are written to
kitchen/logs/<BOOK_ID>-vis-detail.json, one list per district, and the
geography JSON keeps only the district itself.

This is a rule, applied by script -- no JSON is ever typed by hand:
  * a province whose name is a container (VOLUME / VOL / PART / UNIT /
    BOOK / SECTION) stays a province;
  * every other heading is a district; its page_start is the SMALLEST page
    of the entries printed under it (the chapter begins where its first
    technique begins) and its page_end the largest;
  * the district's number is the common prefix of its entries, when they
    share one (Campbell prints 15.1, 15.2, ... under chapter 15).

    python kitchen/toc_normalize.py CAMPBELL-2020
"""
import json
import re
import sys
from pathlib import Path

KITCHEN = Path(__file__).resolve().parent
LOGS = KITCHEN / "logs"

CONTAINER = re.compile(r"^(volume|vol\.?|part|unit|book|section|module)\b",
                       re.I)


def is_container(name):
    return bool(CONTAINER.match(name.strip()))


def number_of(entries):
    """The chapter number shared by the entries printed under a heading."""
    pref = set()
    for e in entries:
        m = re.match(r"^(\d+)\.", str(e.get("number") or ""))
        if m:
            pref.add(int(m.group(1)))
    if len(pref) == 1:
        return str(pref.pop())
    return None


def normalize(bid):
    """Districts are the CHAPTER BLOCKS, grouped by the number printed on
    their entries (CAMPBELL-2020 prints 15.1, 15.2, ... under chapter 15).
    The number is the only grouping the page itself guarantees; the bold
    heading is used as the district's title whenever the reader captured it
    just above, and the chapter is reported as UNTITLED when it did not."""
    src = LOGS / f"{bid}-vis-toc.json"
    doc = json.loads(src.read_text())
    provinces = []
    volume = None
    blocks = {}          # chapter number -> district record, in order
    order = []
    detail = {}
    untitled = []

    for prov in doc["provinces"]:
        name, entries = prov["name"], prov["chapters"]
        if is_container(name):
            volume = {"name": name, "part_name": prov.get("part_name", name),
                      "chapters": []}
            provinces.append(volume)
            pending_title = None
        for e in entries:
            m = re.match(r"^(\d+)\.", str(e.get("number") or ""))
            if not m:
                continue                       # an unnumbered body-text line
            key = int(m.group(1))
            if key not in blocks:
                blocks[key] = {"number": str(key),
                               "title": None if is_container(name) else name,
                               "page_start": e.get("page_start"),
                               "page_end": e.get("page_start"),
                               "image": e.get("_image"),
                               "prov": volume}
                order.append(key)
            dist = blocks[key]
            if dist["title"] is None and not is_container(name):
                dist["title"] = name
            if dist["page_start"] is None:
                dist["page_start"] = e.get("page_start")
            if e.get("page_start"):
                dist["page_end"] = max(dist["page_end"] or 0,
                                       e["page_start"])
            detail.setdefault(key, []).append(
                {"number": e.get("number"), "title": e.get("title"),
                 "page_start": e.get("page_start")})

    # Which read pages belong to the main block of contents? The longest
    # unbroken run of page numbers. On CAMPBELL-2020 that is images 2-20;
    # images 27-28 sit six pages away and are the body's "CHAPTER 1
    # SURGICAL TECHNIQUES" opener, which the locator swept in by mistake.
    # Their entries would otherwise appear as chapters on printed pages
    # 1 to 7, inside a volume that runs from page 3300.
    images = sorted({e["_image"] for p in doc["provinces"]
                     for e in p["chapters"] if e.get("_image")})
    main, run = set(), []
    for img in images:
        if run and img == run[-1] + 1:
            run.append(img)
        elif run:
            if len(run) > len(main):
                main = set(run)
            run = [img]
        else:
            run = [img]
    if run and len(run) > len(main):
        main = set(run)
    outside = {e.get("_image") for p in doc["provinces"]
               for e in p["chapters"] if e.get("_image")} - main

    for key in order:
        dist = blocks[key]
        home = dist.pop("prov")
        if home is None:
            home = {"name": "ALL", "part_name": "ALL", "chapters": []}
            provinces.append(home)
        if dist["title"] is None:
            untitled.append(dist["number"])
            dist["title"] = f"Chapter {dist['number']} (title not captured)"
        home["chapters"].append(dist)

    # drop the chapters that came only from pages outside the main block
    kept, suspects = [], []
    for prov in provinces:
        good = []
        for dist in prov["chapters"]:
            if dist["page_start"] is None or dist["image"] in outside:
                suspects.append(dist)
            else:
                good.append(dist)
        prov["chapters"] = sorted(good, key=lambda d: d["page_start"])
    provinces = [p for p in provinces if p["chapters"]]

    (LOGS / f"{bid}-vis-toc.json").write_text(
        json.dumps({"provinces": provinces}, indent=1, ensure_ascii=False))
    (LOGS / f"{bid}-vis-detail.json").write_text(
        json.dumps({str(k): v for k, v in detail.items()},
                   indent=1, ensure_ascii=False))
    (LOGS / f"{bid}-vis-suspect.json").write_text(
        json.dumps({"suspect_districts": suspects, "untitled": untitled,
                    "pages_outside_main_block": sorted(outside),
                    "main_block_images": sorted(main)},
                   indent=1, ensure_ascii=False))
    n = sum(len(p["chapters"]) for p in provinces)
    return len(provinces), n, len(detail), len(suspects), untitled


def main():
    for bid in sys.argv[1:]:
        np_, nc, nd, ns, untitled = normalize(bid)
        print(f"{bid}: provinces={np_} districts={nc} detail lists={nd}",
              flush=True)
        if ns:
            print(f"    SUSPECT (not a contents page, reported not kept): {ns}",
                  flush=True)
        if untitled:
            print(f"    UNTITLED chapters (need the model's eyes again): "
                  f"{untitled}", flush=True)
        doc = json.loads((LOGS / f"{bid}-vis-toc.json").read_text())
        for p in doc["provinces"]:
            print(f"    {p['name'][:34]:36s} {len(p['chapters']):3d}",
                  flush=True)


if __name__ == "__main__":
    sys.exit(main())