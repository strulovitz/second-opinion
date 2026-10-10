"""kitchen/toc_to_json.py -- STEP A2 (BIBLE part 3, sections 4.3 and 4.4).

Send each book's Table of Contents text to the free local READER and save
kitchen/logs/<BOOK_ID>-toc.json.

AMENDMENT 3.4 (declared by the manager, recorded in PROGRESS.md): the BIBLE's
prompt P-A2 asks for one JSON object per book. That FAILED on real books, and
the BIBLE's own rule for that case (section 4.4) is to re-send the failing
portion with the error appended -- never to hand-edit. Two concrete failures
were measured on 2026-10-10:

  * SABISTON-22 -- "Expecting ',' delimiter" at character 2214: chapter titles
    contain double quotes, which the model did not escape, and the answer was
    also cut off at the 8000-token limit because the book has many chapters.
  * NELSON-2024 -- "no JSON found" on chunk 2: the answer was truncated mid
    object, so no closing brace ever appeared.

A single JSON object spanning a whole book's contents is therefore the wrong
shape for a local 27B model. The SAME information schema as the BIBLE is kept
verbatim -- province name, part name, chapter number, verbatim chapter title,
printed page_start -- but emitted one record per LINE. A line cannot be
truncated into invalid syntax, quotes need no escaping, and a partial answer
still yields the chapters that did arrive.

Output lines, tab separated:
    P<TAB>province_name<TAB>part_name
    C<TAB>chapter_number_or_dash<TAB>chapter_title<TAB>page_start
"""
import json
import re
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from reader import ask  # noqa: E402

KITCHEN = Path(__file__).resolve().parent
LOGS = KITCHEN / "logs"

SYSTEM = """You extract the Table of Contents of one medical textbook into a list. Output ONLY those lines, nothing else.

For every PROVINCE (a Part, Section, Unit or Book heading) output one line:
P<TAB>name of the province heading<TAB>heading of the level above it (or the same name)

For every CHAPTER (the smallest numbered unit that has its own starting page) output one line:
C<TAB>chapter number as printed, or a single dash if the book does not number chapters<TAB>the full chapter title, verbatim including punctuation<TAB>the printed starting page as a bare integer

Rules:
- Keep titles VERBATIM including punctuation. Join titles that wrap over two lines.
- Ignore author names, editors and contributor lists.
- Ignore front matter with roman-numeral pages (preface, contributors, dedication).
- Ignore entries with no page number (online-only chapters, videos, atlases).
- If the book has no heading above the chapters, use one province named ALL.
- Never write commentary, notes, markdown, code fences or JSON. Only P and C lines."""

MAX_CHARS = 20000
CUT = re.compile(r"^\s*(P|C)\t")


def split_toc(text: str):
    """Split at a Part/Section heading so no entry is cut in half."""
    if len(text) <= MAX_CHARS:
        return [text]
    lines = text.splitlines()
    marks = [i for i, ln in enumerate(lines)
             if re.match(r"\s*(PART|SECTION|UNIT|BOOK)\s+[IVXLC0-9]", ln, re.I)]
    if not marks:
        return [text[i:i + MAX_CHARS] for i in range(0, len(text), MAX_CHARS)]
    chunks, start, pos = [], 0, 0
    for m in marks[1:]:
        # compare CHARACTERS consumed, not line numbers
        if sum(len(l) + 1 for l in lines[start:m]) > MAX_CHARS * 0.5:
            chunks.append("\n".join(lines[start:m]))
            start = m
    chunks.append("\n".join(lines[start:]))
    return [c for c in chunks if c.strip()]


def parse(answer: str, doc: dict):
    """Turn the reader's P/C lines into the BIBLE's JSON shape."""
    cur = None
    for raw in answer.splitlines():
        if not CUT.match(raw):
            continue
        f = raw.rstrip("\n").split("\t")
        if f[0] == "P" and len(f) >= 3:
            cur = {"name": f[1].strip(), "part_name": f[2].strip(), "chapters": []}
            doc["provinces"].append(cur)
        elif f[0] == "C" and len(f) >= 4:
            num, title, page = f[1].strip(), f[2].strip(), f[3].strip()
            m = re.match(r"^(\d+)", page)
            if not m or not title:
                continue
            if cur is None:
                cur = {"name": "ALL", "part_name": "ALL", "chapters": []}
                doc["provinces"].append(cur)
            cur["chapters"].append({
                "number": None if num in ("-", "") else num,
                "title": title,
                "page_start": int(m.group(1)),
            })
    return doc


def run_chunk(text, repair=""):
    user = text
    if repair:
        user = text[:3000] + "\n[...]\n\n" + repair
    return ask(SYSTEM, user, max_tokens=16000, expect_json=False)


def main():
    wanted = sys.argv[1:] or None
    books = [b for b in json.loads((KITCHEN / "books.json").read_text())
             if b["status"] == "candidate" and b["toc_images"]]
    if wanted:
        books = [b for b in books if b["book_id"] in wanted]
    print(f"reader: converting {len(books)} TOCs", flush=True)
    for b in books:
        bid = b["book_id"]
        src = LOGS / f"{bid}-toc.txt"
        if not src.exists():
            print(f"  {bid:26s} SKIP (no toc.txt)", flush=True)
            continue
        parts = split_toc(src.read_text())
        doc = {"provinces": []}
        failed = 0
        for i, chunk in enumerate(parts):
            got, doc, bad = "", doc, None
            for attempt in range(2):
                try:
                    got = run_chunk(chunk, bad or "")
                except Exception as exc:  # noqa: BLE001 - recorded, never hidden
                    bad = f"The previous attempt failed: {exc}. Output only P and C lines."
                    continue
                before = len(doc["provinces"]) and sum(
                    len(p["chapters"]) for p in doc["provinces"])
                parse(got, doc)
                after = sum(len(p["chapters"]) for p in doc["provinces"])
                if after == before:
                    bad = ("The previous attempt returned no parsable C line with a "
                           "page number. Use a TAB between the four fields.")
                else:
                    break
            else:
                failed += 1
        ch = sum(len(p["chapters"]) for p in doc["provinces"])
        (LOGS / f"{bid}-toc.json").write_text(
            json.dumps(doc, indent=1, ensure_ascii=False))
        print(f"  {bid:26s} provinces={len(doc['provinces']):3d} "
              f"chapters={ch:4d} chunks={len(parts)} "
              f"{'OK' if not failed else f'{failed} FAILED CHUNKS'}", flush=True)


if __name__ == "__main__":
    main()