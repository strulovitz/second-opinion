"""kitchen/toc_strip_online_only.py -- keep "(online only)" chapters out of the map.

MEASURED 2026-10-12 on SABISTON-22, caught by the honest validator: the gap
repair was asked for chapters missing from the range and answered with the
"(online only)" entries the contents prints WITHOUT a page number -- then
filled the empty page column with a number that came from somewhere else.
It produced chapter 50 with page_start 50, which is exactly the invented
page that BIBLE part 3 section 4.4 forbids: the number printed in the
chapter-number column was copied into the page column.

The book is the authority: an entry printed as "(online only)" has NO
printed page, so it cannot be placed in the geography by page. Such entries
are not thrown away -- they are written to
kitchen/logs/<BOOK_ID>-online-only.json and reported, because Law 11 says
nothing is dropped silently. They will be read in Part 4, where the reader
opens the eBook and the page is recorded from the book itself.

    python kitchen/toc_strip_online_only.py SABISTON-22
"""
import json
import re
import sys
from pathlib import Path

KITCHEN = Path(__file__).resolve().parent
LOGS = KITCHEN / "logs"
ONLINE = re.compile(r"\(\s*online only\s*\)|\(online only\)", re.I)


def main():
    for bid in sys.argv[1:]:
        # 1. the transcript: drop gap-repair lines that paired an
        #    "(online only)" entry with a page number
        src = LOGS / f"{bid}-vis-toc.txt"
        kept_blocks, stripped, seen = [], [], set()
        if src.exists():
            for block in src.read_text().split("===== image "):
                if not block.strip():
                    continue
                head, _, body = block.partition("=====\n")
                img = head.split(" ")[0].strip()
                out = []
                for line in body.splitlines():
                    f = line.split("\t")
                    if (f and f[0] == "C" and len(f) >= 3
                            and ONLINE.search(line)
                            and re.search(r"\d", "\t".join(f[3:]))):
                        stripped.append({"image": img, "line": line})
                        continue
                    out.append(line)
                kept_blocks.append(f"\n===== image {img} =====\n"
                                   + "\n".join(out))
            src.write_text("\n".join(kept_blocks))

        # 2. the JSON: same entries, removed from the geography
        jf = LOGS / f"{bid}-vis-toc.json"
        removed = []
        if jf.exists():
            doc = json.loads(jf.read_text())
            for prov in doc["provinces"]:
                keep = []
                for c in prov["chapters"]:
                    if ONLINE.search(c.get("title", "")):
                        removed.append({"province": prov["name"], **c})
                    else:
                        keep.append(c)
                prov["chapters"] = keep
            doc["provinces"] = [p for p in doc["provinces"] if p["chapters"]]
            jf.write_text(json.dumps(doc, indent=1, ensure_ascii=False))

        # 3. entries the reader transcribed with an EMPTY page field.
        # MEASURED 2026-10-13 on FIRESTEIN-12: a book whose contents prints
        # pages everywhere, but where the gap repair answered "6 Biomechanics"
        # with no page at all. Such an entry cannot be placed on the map and
        # cannot be cited (Law 2 wants a printed page), so it is recorded here
        # and kept out of the geography, exactly like an "(online only)" one.
        # A book that prints NO page anywhere (BRANT-5, checked by eye) is a
        # different case: there every chapter has no page, none of them is an
        # anomaly, and the validator reports the book as printing no pages.
        # MEASURED 2026-10-16 on HAZZARD-2022: that book's contents prints no
        # page numbers either, but on half its contents pages the model still
        # copied the CHAPTER number into the page column (chapter 88 -> page
        # 88). Those few invented pages made the old test below see a
        # "majority with pages" and strip the 109 honest page-less chapters
        # from the transcript. Two repairs, both general:
        #   a. a page carried on a NOPAGES page is INVENTED -- the marker
        #      says the book printed no number there; clear it, keep the
        #      chapter, and record the clearing;
        #   b. page-less chapters are stripped only when they are a small
        #      minority (fewer than one third of all chapters).
        jf = LOGS / f"{bid}-vis-toc.json"
        nopage, cleared = [], []
        nopages_images = set()
        if src.exists():
            for block in src.read_text().split("===== image ")[1:]:
                img = block.split(" ")[0].strip()
                if "NOPAGES" in block.split("=====\n", 1)[-1]:
                    nopages_images.add(img)
        if jf.exists():
            doc = json.loads(jf.read_text())
            for prov in doc["provinces"]:
                for c in prov["chapters"]:
                    # a page the PDF's own hyperlink gave us is EVIDENCE
                    # (toc_links.py), never an invention; it is never cleared
                    if c.get("_page_source") == "pdf-link":
                        continue
                    invented = False
                    if (str(c.get("_image", "")) in nopages_images
                            and c.get("page_start") is not None):
                        invented = True
                    # MEASURED again 2026-10-16 on HAZZARD-2022: on the
                    # contents pages that did NOT carry NOPAGES the model
                    # still copied the chapter number into the page column
                    # (chapter 88 -> page 88, chapter 1 -> page 1). That
                    # number-in-the-page-column copy is the invention the
                    # BIBLE forbids since SABISTON-22; a page equal to its
                    # own chapter number is cleared, kept, and recorded.
                    if (not invented and c.get("page_start") is not None
                            and str(c.get("page_start")) ==
                            str(c.get("number")).strip()):
                        invented = True
                    if invented and c.get("page_start") is not None:
                        cleared.append({"province": prov["name"],
                                        "number": c.get("number"),
                                        "title": c.get("title"),
                                        "page_was": c["page_start"],
                                        "image": c.get("_image")})
                        c["page_start"] = None
            flat = [c for p in doc["provinces"] for c in p["chapters"]]
            withpage = [c for c in flat if c.get("page_start") is not None]
            pageless = len(flat) - len(withpage)
            if withpage and pageless * 3 <= len(flat):
                for prov in doc["provinces"]:
                    keep = []
                    for c in prov["chapters"]:
                        if c.get("page_start") is None:
                            nopage.append({"province": prov["name"], **c})
                        else:
                            keep.append(c)
                    prov["chapters"] = keep
                doc["provinces"] = [p for p in doc["provinces"]
                                    if p["chapters"]]
                jf.write_text(json.dumps(doc, indent=1, ensure_ascii=False))
                # the same lines are removed from the saved transcription, so
                # the text on disk and the JSON always tell the same story
                gone = {c["title"] for c in nopage}
                if src.exists():
                    blocks, out_lines = [], []
                    for block in src.read_text().split("===== image "):
                        if not block.strip():
                            continue
                        img = block.split(" ")[0].strip()
                        head, _, body = block.partition("=====\n")
                        keep = []
                        for line in body.splitlines():
                            f = line.split("\t")
                            if (f and f[0] == "C" and len(f) >= 3
                                    and f[2].strip() in gone
                                    and not re.search(r"\d",
                                                       "\t".join(f[3:]))):
                                out_lines.append({"image": img, "line": line})
                                continue
                            keep.append(line)
                        blocks.append(f"\n===== image {img} =====\n"
                                      + "\n".join(keep))
                    src.write_text("\n".join(blocks))
                    stripped += out_lines
            elif cleared:
                jf.write_text(json.dumps(doc, indent=1, ensure_ascii=False))

        out = LOGS / f"{bid}-online-only.json"
        prev = json.loads(out.read_text()) if out.exists() else {}
        out.write_text(json.dumps(
            {"note": "chapters the contents prints without a printed page; "
                     "they carry no page until Part 4 opens the eBook",
             "count": len(removed) + len(nopage),
             "chapters": removed,
             "transcript_lines_stripped": stripped,
             "printed_without_any_page": nopage,
             "cleared_invented_pages": cleared,
             "online_only_count": prev.get("online_only_count", len(removed))},
            indent=1, ensure_ascii=False))
        n = sum(len(p["chapters"]) for p in
                json.loads(jf.read_text())["provinces"]) if jf.exists() else 0
        print(f"{bid}: removed {len(removed)} online-only and {len(nopage)} "
              f"page-less chapter(s) from the geography, {len(stripped)} "
              f"transcript line(s) stripped, {len(cleared)} invented page(s) "
              f"cleared; {n} chapters remain -- recorded "
              f"in {out.name}", flush=True)


if __name__ == "__main__":
    sys.exit(main())