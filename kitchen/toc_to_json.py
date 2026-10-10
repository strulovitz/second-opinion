"""kitchen/toc_to_json.py -- STEP A2, page-at-a-time extraction.

WHY THIS VERSION EXISTS (all measured on 2026-10-10, see PROGRESS.md):

1. One giant prompt per book fails. qwen3.8:27b spends hidden-reasoning
   tokens BEFORE answering; with max_tokens=3000 it burned the whole budget
   reasoning and returned an EMPTY string (finish_reason="length"). With
   16,000 it usually answered, but it dropped whole sections -- SABISTON-22
   lost SECTION I entirely.

2. reasoning_effort="none" fixes the empty answer but hurts quality on
   judgement tasks.

3. The resolution is to make each call so small that no reasoning is needed:
   ONE TABLE-OF-CONTENTS PAGE AT A TIME, reasoning off, as pure
   transcription. Small inputs, small outputs, no truncation, no drift, and
   a failure costs one page instead of a whole book.

Output: kitchen/logs/<BOOK_ID>-toc.json in the BIBLE's schema
(provinces -> chapters -> number / title / page_start).

AMENDMENT 3.4: the BIBLE's prompt P-A2 asks for one JSON object per book.
That shape cannot survive a 27B local model on a real Table of Contents
(unescaped quotes in chapter titles, truncation mid-object). The same
information schema is kept; only the framing changes, to tab separated
records, which cannot be truncated into invalid syntax:

    P<TAB>province name<TAB>heading of the level above (or the same name)
    C<TAB>chapter number or a dash<TAB>verbatim chapter title<TAB>printed page

Everything is written per book as soon as it finishes, and every page is
logged, so an interrupted run never loses completed work.
"""
import json
import re
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from reader import ask  # noqa: E402

KITCHEN = Path(__file__).resolve().parent
LOGS = KITCHEN / "logs"

SYSTEM = """You transcribe the Table of Contents page you are given. Output ONLY the lines described, nothing else.

For every heading that names a Part, Section, Unit or Book, and that has chapters under it, output:
P<TAB>heading name<TAB>heading of the level above it (or the same name)

For every chapter entry -- a title together with the printed page number where that chapter starts -- output:
C<TAB>chapter number as printed, or a single dash if there is none<TAB>the complete chapter title exactly as printed<TAB>the printed page number

Rules:
- Copy titles word for word, including punctuation. If a title wraps onto a second line, join it into one.
- A TAB separates the fields.
- Skip: author and editor names, contributor lists, front matter with roman numerals, and lines with no page number.
- If the page has no Table of Contents entries at all, output nothing.
- No commentary, no markdown, no JSON, no explanation."""

FRONT_WORDS = re.compile(r"\b(preface|contributors?|acknowledg\w*|dedication|"
                         r"about the authors?|front matter|index|glossary|"
                         r"advertisement|erratum|copyright|foreword)\b", re.I)
PAGE_FIELD = re.compile(r"(\d{1,5})\s*$")


def pages_of(text: str):
    """pdftotext separates pages with a form feed, so pages come back exactly."""
    return [p for p in text.split("\f")]


def parse(answer: str, doc: dict, province: str):
    """Fold one page's P/C lines into the document. Returns lines accepted."""
    cur = None
    got = 0
    for raw in answer.splitlines():
        if not raw.strip():
            continue
        f = raw.split("\t")
        if len(f) < 2:
            # tolerate spaces if the model dropped the tabs
            f = re.split(r"\s{2,}", raw.strip())
        f = [x.strip() for x in f]
        if f[0] == "P" and len(f) >= 3 and f[1]:
            cur = {"name": f[1], "part_name": f[2] or f[1], "chapters": []}
            doc["provinces"].append(cur)
            got += 1
        elif f[0] == "C" and len(f) >= 4:
            num, title, tail = f[1], f[2], f[3]
            m = PAGE_FIELD.search(tail)
            if not title or not m or FRONT_WORDS.search(title):
                continue
            if cur is None:
                cur = {"name": province, "part_name": province, "chapters": []}
                doc["provinces"].append(cur)
            cur["chapters"].append({
                "number": None if num in ("-", "", "—") else num,
                "title": title,
                "page_start": int(m.group(1)),
            })
            got += 1
    return got


def extract(bid):
    src = LOGS / f"{bid}-toc.txt"
    if not src.exists():
        return None, f"no {bid}-toc.txt"
    pages = pages_of(src.read_text())
    doc = {"provinces": []}
    province, empty, failed = "ALL", [], []
    for i, page in enumerate(pages):
        if len(page.strip()) < 40:
            continue
        try:
            ans = ask(SYSTEM, page, max_tokens=6000, expect_json=False,
                      retries=2, no_reasoning=True)
        except Exception as exc:  # noqa: BLE001 - recorded, never hidden
            failed.append(i + 1)
            continue
        if not ans.strip():
            empty.append(i + 1)
            continue
        got = parse(ans, doc, province)
        if got:
            province = doc["provinces"][-1]["name"]
        elif not empty:
            empty.append(i + 1)
    (LOGS / f"{bid}-toc.json").write_text(
        json.dumps(doc, indent=1, ensure_ascii=False))
    n = sum(len(p["chapters"]) for p in doc["provinces"])
    note = f"{len(empty)} pages with no entries"
    if failed:
        note += f", {len(failed)} failed"
    return (len(doc["provinces"]), n, note), None


def main():
    wanted = sys.argv[1:] or None
    books = [b for b in json.loads((KITCHEN / "books.json").read_text())
             if b["status"] == "candidate" and b["toc_images"]]
    if wanted:
        books = [b for b in books if b["book_id"] in wanted]
    print(f"reader: extracting {len(books)} TOCs page by page", flush=True)
    for b in books:
        bid = b["book_id"]
        res, err = extract(bid)
        if err:
            print(f"  {bid:26s} SKIP ({err})", flush=True)
            continue
        np_, nc, note = res
        flag = "  <-- " if nc < 5 else ""
        print(f"  {bid:26s} provinces={np_:3d} chapters={nc:4d} {note}{flag}",
              flush=True)


if __name__ == "__main__":
    main()