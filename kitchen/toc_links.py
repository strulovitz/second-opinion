#!/usr/bin/env python3
"""Read the invisible hyperlinks a PDF's contents page carries.

Many textbooks print no page number in the contents, but the PDF still stores
one hidden link per chapter line. The link target is the true first page of
that chapter, which is evidence from the book itself (Law 2) -- it is NOT a
guess.

Writes kitchen/logs/<BOOK_ID>-vis-links.json:
    {"book_id":..., "pages": n, "links": [{"label","rect","image"}...],
     "matched": [{"number","title","image","label"}...],
     "unmatched": ["label", ...]}

Costs ZERO model calls.
"""
import json
import re
import sys
from pathlib import Path

from pypdf import PdfReader

ROOT = Path(__file__).resolve().parent.parent
KITCHEN = ROOT / "kitchen"
LOGS = KITCHEN / "logs"


def norm(s):
    return re.sub(r"[^a-z0-9]+", " ", (s or "").lower()).strip()


def opener_number(page):
    """The chapter number printed at the top of a chapter's first page.

    This is read from the BOOK ITSELF, not guessed from the link's position.
    Returns (number, first_lines) or (None, first_lines).
    """
    txt = page.extract_text() or ""
    lines = [re.sub(r"\s+", " ", l).strip() for l in txt.splitlines()]
    lines = [l for l in lines if l]
    head = " ".join(lines[:8])
    m = re.search(r"CHAPTER\s+([0-9]+[A-Z]?)", head, re.I)
    if m:
        return [m.group(1)], lines[:6], "chapter-word"
    # ROCKWOOD-10 style: the opener prints the number alone on one of its
    # first lines and the title on the next. The number may not be the FIRST
    # line (image 3452 prints a stray "7" above the real "68"), so every
    # plausible number is offered and the title decides.
    cands = [l for l in lines[:3] if re.fullmatch(r"[0-9]{1,3}[A-Z]?", l)]
    return cands, lines[:6], ("bare-number" if cands else "none")


def title_agrees(page_head, toc_title):
    """Does the page we were sent to actually carry THIS chapter's title?

    An index page also prints '7' and then a title, so a bare number alone is
    not enough; the book's own words must agree (Law 2).
    """
    words = [w for w in norm(toc_title).split() if len(w) > 3][:4]
    if not words:
        return True
    hay = norm(" ".join(page_head))
    return all(w in hay for w in words)


def main():
    argv = sys.argv[1:]
    bid = [a for a in argv if not a.startswith("--")][0]
    books = json.loads((KITCHEN / "books.json").read_text())
    book = [b for b in books if b["book_id"] == bid][0]
    pdf = KITCHEN / "books" / book["pdf_file"]

    toc_path = LOGS / f"{bid}-vis-toc.json"
    doc = json.loads(toc_path.read_text())
    chapters = [c for p in doc.get("provinces", []) for c in p.get("chapters", [])]
    by_num = {}
    for c in chapters:
        n = str(c.get("number", "")).strip()
        if n:
            by_num.setdefault(n, c)

    reader = PdfReader(str(pdf))
    ids = {p.indirect_reference.idnum: i + 1 for i, p in enumerate(reader.pages)}

    # every contents image this book was read from
    imgs = sorted({int(c["_image"]) for c in chapters
                   if str(c.get("_image", "")).isdigit()})

    links, matched, unmatched, conflicts = [], [], [], []
    for img in imgs:
        page = reader.pages[img - 1]
        annots = page.get("/Annots") or []
        if not annots:
            continue
        for a in annots:
            o = a.get_object()
            if o.get("/Subtype") != "/Link":
                continue
            dest = o.get("/Dest")
            if not dest:
                continue
            ref = dest[0]
            num_id = getattr(ref, "idnum", None)
            if num_id not in ids:
                continue
            target = ids[num_id]
            cands, head, how = opener_number(reader.pages[target - 1])
            links.append({"image": target, "contents_image": img,
                          "chapter_number": cands[0] if cands else None,
                          "how": how, "page_head": head})
            c = None
            for cand in cands:
                cand_ch = by_num.get(str(cand))
                if cand_ch is None:
                    continue
                # a bare number alone can also be an INDEX page, so the book's
                # own words on that page must agree with this chapter's title
                if how == "chapter-word" or title_agrees(head,
                                                         cand_ch.get("title", "")):
                    c = cand_ch
                    break
            if c is None:
                unmatched.append({"image": target,
                                  "chapter_number": cands[0] if cands else None,
                                  "how": how, "page_head": head})
            else:
                prev = c.get("_link_image")
                if prev is not None and prev != target:
                    # two links claim the same chapter: the chapter begins at
                    # the EARLIER page. Recorded, never silently dropped.
                    conflicts.append({"number": c.get("number"),
                                      "title": c.get("title"),
                                      "images": sorted([prev, target])})
                    target = min(prev, target)
                c["_link_image"] = target
                c["_link_head"] = head
                if c.get("page_start") is None:
                    c["page_start"] = target
                    c["_page_source"] = "pdf-link"
                matched.append({"number": c.get("number"),
                                "title": c.get("title"),
                                "image": target})

    res = {"book_id": bid, "contents_images": imgs,
           "links_found": len(links), "links": links,
           "matched": matched, "unmatched": unmatched,
           "conflicts": conflicts}
    (LOGS / f"{bid}-vis-links.json").write_text(
        json.dumps(res, indent=1, ensure_ascii=False))
    toc_path.write_text(json.dumps(doc, indent=1, ensure_ascii=False))
    print(f"{bid}: {len(links)} links on images {imgs}")
    print(f"  matched to chapters: {len(matched)}")
    print(f"  conflicts: {json.dumps(conflicts)[:400]}")
    print(f"  unmatched (front matter, part pages, index): {len(unmatched)}")


if __name__ == "__main__":
    main()