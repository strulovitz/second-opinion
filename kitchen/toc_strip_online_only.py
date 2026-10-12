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

        out = LOGS / f"{bid}-online-only.json"
        out.write_text(json.dumps(
            {"note": "chapters the contents prints without a printed page; "
                     "they carry no page until Part 4 opens the eBook",
             "count": len(removed),
             "chapters": removed,
             "transcript_lines_stripped": stripped},
            indent=1, ensure_ascii=False))
        n = sum(len(p["chapters"]) for p in
                json.loads(jf.read_text())["provinces"]) if jf.exists() else 0
        print(f"{bid}: removed {len(removed)} online-only chapter(s) from the "
              f"geography, {len(stripped)} transcript line(s) stripped; "
              f"{n} chapters remain -- recorded in {out.name}", flush=True)


if __name__ == "__main__":
    sys.exit(main())