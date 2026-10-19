# HANDOFF -- 2026-10-19 evening, page_offset REWRITTEN after a real bug was found

READ FIRST, IN ORDER:
1. This file
2. `HANDOFF-2026-10-19-page-offset.md` (this morning's handoff -- still correct
   about the TOC work, but its "10 trusted books" claim is WITHDRAWN, see 3)
3. `PROGRESS.md` (the ledger)

## ONE-LINE SUMMARY

HARRISON-22 was finished and checked with the new tool (505/505 chapters have
both a PDF page and a printed page, 12 random pages re-read by Qwen, 12/12
agreed, 1 re-read by the manager's own eyes, agreed). While doing it the real
bug behind yesterday's partial results was found and fixed: **`page_start`
does not mean the same thing in every book**, so yesterday's folio layer is
wrong for the contents-read books and off-by-one for the others. Nothing was
loaded into Neo4j; nothing was frozen; the 4,755 chapters, the provinces and
every geography file are UNTOUCHED and safe.

## 1. THE BUG -- page_start HOLDS TWO DIFFERENT NUMBERS UNDER ONE NAME

Two different tools wrote that one field:

  A. `toc_vision.py` / `toc_openers.py` wrote the number the CONTENTS PRINTS
     -> page_start IS THE PRINTED PAGE. 22 books.
  B. `toc_outline.py` (PDF bookmark / link destination)
     -> page_start IS THE PDF PAGE. 15 books.

Which is which, per book, from the entries' own evidence
(`_page_source`, `_image`): IMAGE books = BRANT-5, HAZZARD-2022,
IRWIN-RIPPE-2023, KAPLAN-11, MANDELL-9, MIDDLETON-2019, MILLER-10, MURRAY-7,
NELSON-2024, ROCKWOOD-10, ROSEN-2022, WILLIAMS-ENDO-2024,
WILLIAMS-HEMATOLOGY-2021, WILLIAMS-OBSTETRICS-26, DELISA-6 (15).
All the rest are PRINTED books (22).

PROOF, by rendering pages to images and looking at them (this is the method,
not a guess):

  HARRISON-22 pdf 2044  -> it is the opener of chapter 266, the contents say
                           "266 ... 2001", the corner prints 2001, and
                           page_start is 2001, while the PDF page is 2044
                           (offset 43).  page_start = PRINTED.
  SABISTON-22 contents pdf 36 prints "54 Pancreas Transplantation, 651" and
                           page_start is 651; the chapter's real PDF page is
                           1080 (offset 429).  page_start = PRINTED.
  MANDELL-9 pdf 1835     -> opener of chapter 107, page_start 1835, the corner
                           prints 1452.  page_start = IMAGE.
  NELSON-2024 pdf 2430   -> opener of chapter 394, page_start 2430, the corner
                           prints 2415.  page_start = IMAGE.

CONSEQUENCE: yesterday's `folio.json` files read every entry as a PDF page. For
the 22 contents-read books that is off by the whole front matter (Harrison by
43, Sabiston by 347-429 and worse, because the book also RESTARTS its numbering
inside each Section). **The "10 books / 1,485 chapters verified" claim of the
morning handoff is WITHDRAWN.** The 4 pages that were eye-checked only proved
that the script can read a folio off a page; they never proved that the page
it looked at was the chapter's page.

SECOND BUG (independent, also fixed): when a chapter's own page printed no
detectable folio, `folio_at()` returned the NEXT page's folio unchanged --
off by one per page of distance. Measured: Mandell-9 chapter 107 came out
1453; the page prints 1452 (rendered, looked at). The fix: a later page with
gap g means the earlier page's folio is `start - g`.

## 2. THE NEW TOOL (zero model calls, ~5 s per book)

    kitchen/page_folio.py     rewritten. Decides the meaning of page_start PER
                              ENTRY from its own evidence, gives every chapter
                              BOTH numbers, and refuses to answer when it
                              cannot prove one (Law 2).
    kitchen/folio_sample.py   the independent check: renders a random sample of
                              chapters to PNGs and lets Qwen 3.8 27B (TIER
                              FREE, Law 14) look at them -- is this really the
                              chapter's first page, and what corner number is
                              printed? Disagreements are listed, never
                              swallowed.

    cd ~/second-opinion && source .venv/bin/activate
    python kitchen/page_folio.py HARRISON-22          # one book
    python kitchen/page_folio.py --all                # all 37, no model calls
    python kitchen/folio_sample.py HARRISON-22 --n 12 # 12 pictures for Qwen
    python kitchen/folio_sample.py HARRISON-22 --n 12 --eyes   # just render
                                                      # them for a human to see

OUTPUT `kitchen/logs/<BOOK>-folio.json` (the file is gitignored, rebuildable):

    {"_meta": {page_start_means, image_role, chapters, resolved_both,
               conflicts, median_offset, offset_mode, offset_mode_share,
               offset_constant, pdf_pages, ...},
     "pages": {"<pdf page>": <printed page>},          <- the citation form
     "chapters": [{province, number, title, image, printed, src, page_start,
                   check}, ...],
     "conflicts": [...]}

`check` per chapter: ok / shared-page (two chapters really share one printed
page -- Harrison 45 and 46 both start at 291, printed in the book's own
contents) / no-folio-on-that-page / no-page-prints-that-folio / conflict /
folio-missing-reader-page-used. Anything that is not ok or shared-page is a
CONFLICT and the book must not be trusted until a human has looked.

## 3. WHAT IS FINISHED AND CHECKED

HARRISON-22, 505/505 chapters, both numbers, 0 conflicts.
  * offset 43, CONSTANT: 2,542 pages of the book vote for 43, and the vote is
    43 in every 500-page block from page 0 to page 4,499 (no drift at all).
  * folio_sample.py --n 12: 12/12 chapters agree with Qwen on BOTH questions
    (is it the chapter's first page, what does the corner print).
  * the manager's own eyes on pdf 357: corner prints 314, page is the opener of
    chapter 50 "Unintentional Weight Loss" -- matches the script.
  * detail: kitchen/logs/HARRISON-22-folio-sample.json

EVERY OTHER BOOK still has yesterday's wrong folio.json and must be redone with
the new tool before it is used for anything.

## 4. WHAT TO DO NEXT (agreed with Nir before he left)

1. Run `python kitchen/page_folio.py --all` -- free, no model calls, ~5 s a
   book, writes only `kitchen/logs/<BOOK>-folio.json`. Report which books come
   out with 0 conflicts and which do not.
2. Then `folio_sample.py <BOOK> --n 12` book by book -- ONE book at a time,
   check it, report, next. A book is trusted only when its own sample passes.
3. Books with conflicts get looked at by the manager (render + eye) or, if it
   cannot be solved, go on the question list for Nir -- never dropped (his
   standing rule).
4. Only after a book passes: write its `page_offset` / folio into
   `kitchen/books.json` (never done yet -- `page_offset` is still null for all
   37 books) -- and only for books that actually passed.
5. THEN, and only then, BIBLE part 3 continues: seating, raster, registry,
   load/verify, FREEZE. Nothing is in Neo4j yet.

Nir's orders for this work (19 Oct): book by book; after each book check
everything properly; never again the two-day loss. One thing at a time, short
plain words, no walls of numbers in chat, give him a path or a link, ask him
before deciding, emojis in chat replies only.

## 5. INVARIANTS -- NOTHING IN THIS SESSION TOUCHED THEM

    python kitchen/toc_validate.py --vis      37/37 clean, 4755 chapters
    kitchen/books.json                        unchanged, page_offset still null
    BIBLE/                                    never edited
    Neo4j                                     nothing loaded, nothing frozen

No geography file was written. `page_folio.py` writes exactly one file per
book and nothing else; `folio_sample.py` writes a JSON and the PNGs under
`kitchen/logs/folio-render/` (both gitignored).

## 6. TOOLS AND STATE

  * Ollama is running on 127.0.0.1:11434 with `qwen3.8:27b` loaded -- that is
    the READER for folio_sample.py (Law 14: per-page checks are free).
  * The pdftotext caches (`kitchen/logs/<BOOK>-folio.txt`) are scratch, about
    500 MB for all 37 books, gitignored, rebuilt automatically. Delete them
    when disk is wanted; they are never committed.
  * New/changed files this session: `kitchen/page_folio.py` (rewritten),
    `kitchen/folio_sample.py` (new). `kitchen/page_offset.py` (yesterday's
    single-offset method) is kept ONLY as a comparison -- it is wrong for any
    book that restarts its numbering and must not be the method.

## 7. WHAT WAS DONE THIS MORNING -- DO NOT REDO (context only)

  * YOUMANS-4 rebuilt from scratch: 432 chapters, 49 provinces, validator clean.
    The library is 37/37 clean, 4,755 chapters.
  * `kitchen/toc_merge_dup_provinces.py` added, wired into build_book.py as
    step 4c. Commit 348cf67.
  * The laptop sound was fixed permanently (Option A, no BIOS, no sudo); see
    `/home/nir/AUDIO-FIX-HANDOFF.md`. Option B was refused by Nir.
  * The morning's page_offset run (10 books "at 100 percent") is superseded by
    section 1 above.
