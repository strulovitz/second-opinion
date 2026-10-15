"""kitchen/toc_fix_names.py -- province names = NUMBER + MEANING, together.

Nir's final rule (15 Oct 2026, evening): every territory keeps BOTH its
number and its meaning in the one name field the BIBLE already has --

    "SECTION V CARDIAC RADIOLOGY"  ->  "Section V - CARDIAC RADIOLOGY"
    "UNIT VI"                      ->  "Unit VI - Blood Cells, Immunity, ..."

Why: later, when something has to be put INTO or taken OUT OF "the book
numbered X", a bare meaning with no number cannot be found.

The meaning is NEVER invented. It is taken from the first source that has
it, and the source is recorded:

    toc      printed in the contents, the heading read, or the PDF text
    written  we composed it from the chapters (only when no book prints it)

Nothing here touches chapters, pages or structure, so the validator's
verdict for the book must not change. Provinces that are not numbered at
all ("ALL", "Appendices", a bare volume) are REPORTED, never guessed at --
they are a structure problem, not a name problem.

    python kitchen/toc_fix_names.py GUYTON-2026            # dry run
    python kitchen/toc_fix_names.py GUYTON-2026 --apply    # write it
    python kitchen/toc_fix_names.py --all --apply
"""
import json
import re
import subprocess
import sys
from pathlib import Path

KITCHEN = Path(__file__).resolve().parent
LOGS = KITCHEN / "logs"
BOOKS = KITCHEN / "books"

TOP = re.compile(
    r"^(PART|VOLUME|VOL|UNIT|BOOK|SECTION|MODULE)\b[\s:.\-\u2014]*"
    r"(\d+|[IVXLCDM]+|"
    r"ONE|TWO|THREE|FOUR|FIVE|SIX|SEVEN|EIGHT|NINE|TEN|ELEVEN|TWELVE|"
    r"THIRTEEN|FOURTEEN|FIFTEEN|SIXTEEN|SEVENTEEN|EIGHTEEN|NINETEEN|"
    r"TWENTY|THIRTY|FORTY|FIFTY|SIXTY|SEVENTY|EIGHTY|NINETY)", re.I)
# a heading-shaped line that is NOT a numbered one ("CARDIAC RADIOLOGY")
PLAIN_TITLE = re.compile(r"^[A-Z][A-Za-z0-9 ,'\-\(\)/&:\.]{2,70}$")
# The contents prints a heading and, right after it on the same line, the
# page where that heading starts: "PART 1: THE CLINICAL METHOD OF
# NEUROLOGY, 1". MEASURED on the printed page of ADAMS-12 -- the digit sits
# after a comma and is a page, never part of the title. It is kept in
# toc_page, never in the name.
TRAILING_PAGE = re.compile(r"[,;:]\s*(\d{1,4})\s*$")


def norm(t):
    return re.sub(r"\s+", " ", str(t)).strip()


def squash(t):
    return re.sub(r"[^a-z0-9]+", " ", str(t).lower()).strip()


def split_heading(text):
    """'SECTION V CARDIAC RADIOLOGY' -> ('Section', 'V', 'CARDIAC RADIOLOGY')
    Returns None when the text is not a numbered heading."""
    t = norm(text)
    m = TOP.match(t)
    if not m:
        return None
    kind = m.group(1).title()
    if kind == "Vol":
        kind = "Volume"
    num = m.group(2)
    rest = t[m.end():].strip(" :-\u2014.,;")
    if not num:
        return None
    return kind, num, rest


# ---------------------------------------------------------------- sources
def transcript_pairs(bid):
    """(a, b) for every P-line: both readings of the two columns."""
    f = LOGS / f"{bid}-vis-toc.txt"
    if not f.exists():
        return []
    out = []
    for raw in f.read_text().splitlines():
        if not raw.startswith("P"):
            continue
        parts = raw.split("\t")
        if len(parts) < 2:
            parts = re.split(r"\s{2,}", raw.strip())
        parts = [norm(x) for x in parts if norm(x)]
        if len(parts) >= 2:
            out.append((parts[1], parts[2] if len(parts) > 2 else ""))
        elif parts:
            out.append((parts[0], ""))
    return out


def heading_lines(bid):
    f = LOGS / f"{bid}-vis-headingnames.json"
    if not f.exists():
        return []
    d = json.loads(f.read_text())
    return [(int(k), d[k]) for k in sorted(d, key=int)]


def raw_texts(bid):
    """(contents_from_the_PDF, local_extracts). The PDF's own first pages
    are searched FIRST: CAMPBELL's local extract is the old chapter-level
    dump, whose running headers ("VOLUME III ... 46.9 ...") are page
    furniture, not the contents."""
    local = []
    for suffix in ("-vis-toc.txt", "-toc.txt"):
        f = LOGS / f"{bid}{suffix}"
        if f.exists():
            local.append(f.read_text(errors="replace"))
    cache = LOGS / f"{bid}-frontmatter.txt"
    if not cache.exists():
        try:
            recs = {b["book_id"]: b for b in
                    json.loads((KITCHEN / "books.json").read_text())}
            pdf = BOOKS / recs[bid]["pdf_file"]
            subprocess.run(["pdftotext", "-f", "1", "-l", "90", str(pdf),
                            str(cache)], capture_output=True, timeout=300)
        except Exception:
            pass
    front = cache.read_text(errors="replace") if cache.exists() else ""
    # DeVita prints its part letters one per character ("P A R T" / "I I I"),
    # which no sane pattern matches. Those letters are glued back together
    # here; real words such as "GI TRACT" are untouched because the letters
    # of a word are not separated by single-character boundaries.
    glue = lambda t: re.sub(r"(?<=\b[A-Z]) (?=[A-Z]\b)", "", t, flags=re.M)
    return glue(front), "\n".join(glue(x) for x in local)


def clean_title(t):
    """Strip the TOC page column glued to the end of a heading."""
    t = norm(t).strip(" :-\u2014.,;")
    t = re.sub(r"[\t]+", " ", t)
    return t.strip()


def meaning_from_transcript(bid, kind, num):
    best = ""
    for a, b in transcript_pairs(bid):
        for first, second in ((a, b), (b, a)):
            sp = split_heading(first)
            if not sp:
                continue
            if sp[0].lower() != kind.lower() or squash(sp[1]) != squash(num):
                continue
            if sp[2]:
                cand = clean_title(sp[2])
                if cand and len(cand) > len(best):
                    best = cand
            elif second and not split_heading(second) and \
                    squash(second) != squash(first):
                cand = clean_title(second)
                if cand and len(cand) > len(best):
                    best = cand
    return best


def meaning_from_headings(bid, kind, num):
    best = ""
    for _img, lines in heading_lines(bid):
        for i, h in enumerate(lines):
            sp = split_heading(h)
            if not sp:
                continue
            if sp[0].lower() != kind.lower() or squash(sp[1]) != squash(num):
                continue
            if sp[2]:
                return clean_title(sp[2])
            for nxt in lines[i + 1:i + 3]:
                if split_heading(nxt):
                    break
                cand = clean_title(nxt)
                if cand and PLAIN_TITLE.match(cand) and len(cand) > len(best):
                    best = cand
    return best


def merge_split_banners(lines):
    """'P A R T' on one line and 'I I I' on the next (DEVITA-12) become one
    'PART III' line, so the heading pattern can see them."""
    out, i = [], 0
    bare = re.compile(r"^\s*(PART|VOLUME|VOL|UNIT|SECTION|BOOK|MODULE)\s*$", re.I)
    roman = re.compile(r"^\s*(?:[IVXLCDM]+|\d+)\s*$", re.I)
    while i < len(lines):
        if bare.match(lines[i]):
            j = i + 1
            while j < len(lines) and not lines[j].strip():
                j += 1
            if j < len(lines) and roman.match(lines[j]):
                out.append(lines[i].strip() + " " + lines[j].strip())
                i = j + 1
                continue
        out.append(lines[i])
        i += 1
    return out


def meaning_from_raw(bid, kind, num):
    """Read the heading straight out of the printed contents.

    A book writes its title in three ways and all three are handled:
      UNIT I                      -> title on the following lines
      SECTION V CARDIAC RADIOLOGY -> title on the same line
      PART 1: THE CLINICAL        -> title wrapped onto the next line,
      METHOD OF                        which ends with the page column
      NEUROLOGY, 1
    """
    front, local = raw_texts(bid)
    return _scan_lines(front, kind, num) or _scan_lines(local, kind, num)


def _scan_lines(text, kind, num):
    if not text:
        return ""
    lines = merge_split_banners(text.splitlines())
    pat = re.compile(r"^\s*" + re.escape(kind) + r"[\s:.\-\u2014]*" +
                     re.escape(num) + r"\b(.*)$", re.I)
    best = ""
    for i, ln in enumerate(lines):
        m = pat.match(ln)
        if not m:
            continue
        block = [ln]
        rest = re.sub(r"[\u200b\u200c\u200d\ufeff\xa0\t]+", " ",
                      m.group(1)).strip(" :-\u2014.,;")
        if not rest:
            # no title on the heading's own line -> it is printed below.
            # One blank line under a banner is normal (WILLIAMS prints
            # "SECTION 10" / blank / "THE PUERPERIUM"); a blank AFTER the
            # title ends it (GUYTON prints the title, blank, then entries).
            started = False
            for nxt in lines[i + 1:i + 6]:
                s = nxt.strip()
                if not s:
                    if started:
                        break
                    continue
                if re.match(r"(?i)^(chapter|part|section|unit|volume|book|module)"
                            r"[\s:.\-]*\d", s) or \
                        re.match(r"^\d+[\s\.\)\-]", s) or \
                        re.fullmatch(r"\d{1,4}", s):
                    break
                block.append(nxt)
                started = True
        elif i + 1 < len(lines) and re.search(
                r"[,;]\s*\d{1,4}\s*$", lines[i + 1].strip()):
            # the heading's line was cut mid-title and the wrapped line
            # carries the page column (ADAMS-12: "NEUROLOGY, 1")
            block.append(lines[i + 1])
        whole = " ".join(x.strip() for x in block)
        whole = re.sub(r"[\u200b\u200c\u200d\ufeff\xa0\t]+", " ", whole)
        m2 = pat.match(whole)
        cand = m2.group(1) if m2 else whole
        cand = clean_title(cand)
        cand = TRAILING_PAGE.sub("", cand).strip(" :-\u2014.,;")
        if not cand or split_heading(cand):
            continue
        if re.match(r"(?i)^chapter\b", cand):
            continue
        # FIRST good answer wins -- a later, longer occurrence of the same
        # words is usually body text, not the contents (MEASURED on
        # CAMPBELL-2020, where "VOLUME II" appears again in the chapters).
        if not best:
            best = cand
            break
    return best


def written_name(province, kind, num):
    """Last resort: a short descriptive name composed from the chapters the
    book itself groups here. Marked name_source = 'written'."""
    titles = [c.get("title") or "" for c in province.get("chapters", [])]
    titles = [t for t in titles if t]
    if not titles:
        return ""
    words = []
    for t in titles:
        for w in re.findall(r"[A-Za-z\-]+", t):
            w = w.lower()
            if w not in {"of", "the", "and", "in", "a", "an", "to", "for",
                         "with", "on", "by", "their", "its", "from"}:
                words.append(w)
    # keep the words that describe the most chapters here
    seen, pick = set(), []
    for w in words:
        if w in seen:
            continue
        seen.add(w)
        pick.append(w)
        if len(pick) == 5:
            break
    if not pick:
        return ""
    return " ".join(w.capitalize() for w in pick[:5])


# ------------------------------------------------------------------ main
def fix_book(bid, apply=False):
    path = LOGS / f"{bid}-vis-toc.json"
    if not path.exists():
        print(f"{bid}: no -vis-toc.json")
        return None
    doc = json.loads(path.read_text())
    print(f"\n===== {bid} ({len(doc['provinces'])} provinces)")
    changed = 0
    structural = []
    for p in doc["provinces"]:
        old = p.get("name", "")
        sp = split_heading(old)
        if not sp:
            structural.append(old)
            print(f"  == NOT NUMBERED: {old!r}  (structure problem, not "
                  f"touched here)")
            continue
        kind, num, title = sp
        title = clean_title(title)
        src = "toc"
        if title:
            # a trailing page glued to a real title: keep only the title,
            # remember the page the book printed beside it
            m = TRAILING_PAGE.search(title)
            if m:
                p["toc_page"] = int(m.group(1))
                title = TRAILING_PAGE.sub("", title).strip(" :-\u2014.,;")
        else:
            # The printed contents in the PDF is searched FIRST: it is the
            # book's own words with nothing in between (the reader's
            # transcript once paired CAMPBELL's "VOLUME II" with a section
            # title printed fifty pages later).
            for fn in (meaning_from_raw, meaning_from_transcript,
                       meaning_from_headings):
                title = fn(bid, kind, num)
                if title:
                    break
        if not title:
            title = written_name(p, kind, num)
            src = "written" if title else "unknown"
        if not title:
            print(f"  ** {kind} {num}: NO MEANING FOUND anywhere "
                  f"(reported, not guessed)")
            continue
        new = f"{kind} {num} - {title}"
        if new != old:
            changed += 1
        p["name"] = new
        p["part_name"] = new
        p["name_source"] = src
        mark = "  " if new == old else "->"
        print(f"  {mark} [{src:7s}] {new}")
    if apply and changed:
        path.write_text(json.dumps(doc, indent=1, ensure_ascii=False))
        print(f"  WRITTEN: {changed} name(s) changed")
    elif changed:
        print(f"  (dry run -- {changed} name(s) would change; --apply to write)")
    return {"book": bid, "changed": changed, "structural": structural}


def main():
    argv = sys.argv[1:]
    apply = "--apply" in argv
    args = [a for a in argv if not a.startswith("--")]
    if "--all" in argv:
        args = sorted(p.name[:-13] for p in
                      LOGS.glob("*-vis-toc.json"))
    stats = [r for b in args if (r := fix_book(b, apply))]
    if stats:
        tot = sum(s["changed"] for s in stats)
        left = [f"{s['book']}: {s['structural']}" for s in stats
                if s["structural"]]
        print(f"\n--- total provinces renamed: {tot}")
        for l in left:
            print(f"--- structure still to fix -> {l}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
