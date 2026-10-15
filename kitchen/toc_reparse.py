"""kitchen/toc_reparse.py -- rebuild a TOC json from the SAVED transcription.

The reader's raw answer is kept in kitchen/logs/<BOOK_ID>-vis-toc.txt, so a
parser fix costs nothing: no model call is repeated, the same words the
model actually printed are re-read with the corrected rules. This is what
Law 11 means by not hand-editing the JSON -- the JSON is never typed by
hand, it is always regenerated from the recorded text.

    python kitchen/toc_reparse.py GUYTON-2026
"""
import json
import re
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from toc_vision import parse  # noqa: E402

KITCHEN = Path(__file__).resolve().parent
LOGS = KITCHEN / "logs"


def norm(t):
    return re.sub(r"[^a-z0-9]+", " ", str(t).lower()).strip()


def main():
    for bid in sys.argv[1:]:
        src = LOGS / f"{bid}-vis-toc.txt"
        if not src.exists():
            print(f"{bid}: no saved transcription", flush=True)
            continue
        text = src.read_text()
        # GUARD: this parser only understands the reader's "P" and "C"
        # lines. Some books were read in a different format (BRENNER-11's
        # transcript is a field list of PART/NUM/TITLE/PAGE), and running
        # this over such a transcript wrote an EMPTY document and wiped
        # 71 chapters that the backup happened to hold. Refuse to replace
        # a document that has chapters with one that has none.
        has_pc = bool(re.search(r"^(P|C)\t", text, re.M))
        out_path = LOGS / f"{bid}-vis-toc.json"
        if not has_pc:
            keep = 0
            if out_path.exists():
                keep = sum(len(p.get("chapters", [])) for p in
                            json.loads(out_path.read_text())["provinces"])
            print(f"{bid}: transcript has no P/C lines to re-parse "
                  f"(different reader format); the existing "
                  f"{keep} chapter(s) are left untouched", flush=True)
            continue
        doc = {"provinces": []}
        province = "ALL"
        pages = 0
        skipped = []
        for block in text.split("===== image "):
            if not block.strip():
                continue
            n = block.split(" ")[0].strip()
            body = block.split("=====\n", 1)[-1]
            # MEASURED 2026-10-12 on SABISTON-22: pages the reader refused as
            # look-alikes (VIDEO CONTENTS, a podcast list, a divider page with
            # no page numbers) are recorded in the same transcript as a bare
            # "KIND=OTHER" line. Re-parsing must skip them exactly as the
            # reader did, or the videos come back as chapters.
            if re.search(r"^\s*KIND\s*=\s*OTHER", body):
                skipped.append(n)
                continue
            pages += 1
            before = len(doc["provinces"])
            if parse(body, doc, province, image=n):
                province = doc["provinces"][-1]["name"]
        n = sum(len(p["chapters"]) for p in doc["provinces"])
        # MEASURED 2026-10-13 on FIRESTEIN-12, caught by the honest validator:
        # the gap repair was asked for the chapters missing from the range and
        # answered "28 Occupational Therapy, Physical Therapy, and
        # Rehabilitation 574" -- the exact title and page the contents already
        # prints for chapter 38. Two different chapters cannot start on the
        # same printed page with the same title, so an entry that repeats a
        # (title, page) pair already in the book under a different number is a
        # mis-numbered copy of another entry, not a reading. It is refused
        # here and written to <BOOK_ID>-vis-copytitles.json, so the number it
        # claimed is reported as still missing instead of being invented.
        pairs, copies = {}, []
        for prov in doc["provinces"]:
            keep = []
            for c in prov["chapters"]:
                key = (norm(c["title"]), c.get("page_start"))
                if c.get("page_start") is not None and key in pairs \
                        and str(pairs[key]) != str(c.get("number")):
                    copies.append({"number": c.get("number"),
                                   "title": c["title"],
                                   "page_start": c.get("page_start"),
                                   "same_title_and_page_as_chapter":
                                       pairs[key]})
                    continue
                pairs.setdefault(key, c.get("number"))
                keep.append(c)
            prov["chapters"] = keep
        if copies:
            doc["provinces"] = [p for p in doc["provinces"] if p["chapters"]]
            (LOGS / f"{bid}-vis-copytitles.json").write_text(
                json.dumps({"refused_mis_numbered_copies": copies},
                           indent=1, ensure_ascii=False))
        # WHICH PROVINCE OWNS WHICH IMAGE -- derived from the data itself.
        # MEASURED 2026-10-15 on FIRESTEIN-12: the old way recorded the
        # province INDEX while parsing ("len(provinces)-1") and empty
        # provinces were dropped afterwards, so every index shifted and
        # toc_dedupe's reassign filed 81 of 125 chapters into the wrong
        # Part. Every chapter already stores the image it was read from,
        # so the province that holds a chapter from image N is that
        # image's province. setdefault keeps the FIRST (the original
        # reading; a gap repair is appended later and must not re-home
        # the page).
        image_province = {}
        for i, p in enumerate(doc["provinces"]):
            for c in p.get("chapters", []):
                if c.get("_image") is not None:
                    image_province.setdefault(str(c["_image"]), i)
        (LOGS / f"{bid}-vis-toc.json").write_text(
            json.dumps(doc, indent=1, ensure_ascii=False))
        (LOGS / f"{bid}-vis-imageprov.json").write_text(
            json.dumps(image_province, indent=1))
        # MEASURED 2026-10-13 on BRANT-5: the book's own banner lines are the
        # only place that says which printed chapter each section really
        # starts on. The reader printed "SECTION XII NUCLEAR RADIOLOGY" as the
        # LAST banner of the contents and its chapters on the next page, so
        # asking the page for the first chapter under the banner answered
        # NONE; deriving the number from the remaining chapter list instead
        # gave 66 and swallowed six paediatric chapters. What is written here
        # is the banner order and the first chapter printed under each banner,
        # both read straight off the transcript.
        (LOGS / f"{bid}-vis-rawprov.json").write_text(json.dumps(
            [{"name": p["name"],
              "first_number": (p["chapters"][0].get("number")
                               if p["chapters"] else None),
              "chapters": len(p["chapters"])} for p in doc["provinces"]],
            indent=1, ensure_ascii=False))
        print(f"{bid}: {pages} pages -> provinces={len(doc['provinces'])} "
              f"chapters={n}"
              + (f"  look-alike pages skipped: {skipped}" if skipped else "")
              + (f"  REFUSED {len(copies)} mis-numbered copy/copies of "
                 f"another chapter: "
                 + ", ".join(f"{c['number']}={c['title'][:30]}"
                             for c in copies[:5]) if copies else ""),
              flush=True)
        for p in doc["provinces"]:
            print(f"    {p['name'][:46]:48s} {len(p['chapters']):3d}", flush=True)


if __name__ == "__main__":
    sys.exit(main())