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


def main():
    for bid in sys.argv[1:]:
        src = LOGS / f"{bid}-vis-toc.txt"
        if not src.exists():
            print(f"{bid}: no saved transcription", flush=True)
            continue
        doc = {"provinces": []}
        province = "ALL"
        pages = 0
        image_province = {}
        for block in src.read_text().split("===== image "):
            if not block.strip():
                continue
            n = block.split(" ")[0].strip()
            pages += 1
            body = block.split("=====\n", 1)[-1]
            before = len(doc["provinces"])
            if parse(body, doc, province, image=n):
                province = doc["provinces"][-1]["name"]
            # which province this IMAGE belongs to, decided the first time
            # the page is read normally. A gap repair is appended at the end
            # of the transcript and would otherwise be filed under the last
            # province of the book.
            image_province.setdefault(
                n, len(doc["provinces"]) - 1 if doc["provinces"] else 0)
        n = sum(len(p["chapters"]) for p in doc["provinces"])
        (LOGS / f"{bid}-vis-toc.json").write_text(
            json.dumps(doc, indent=1, ensure_ascii=False))
        (LOGS / f"{bid}-vis-imageprov.json").write_text(
            json.dumps(image_province, indent=1))
        print(f"{bid}: {pages} pages -> provinces={len(doc['provinces'])} "
              f"chapters={n}", flush=True)
        for p in doc["provinces"]:
            print(f"    {p['name'][:46]:48s} {len(p['chapters']):3d}", flush=True)


if __name__ == "__main__":
    sys.exit(main())