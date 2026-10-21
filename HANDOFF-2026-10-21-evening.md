# HANDOFF -- 2026-10-21 evening, the printed page of every chapter, read by the eyes

# ############################################################################
# ## THE VERY FIRST THING TO CHECK -- BEFORE ANYTHING ELSE IN THIS PROJECT
#
# **Is every one of our 37 PDFs the COMPLETE book?** The human checks this
# by hand. The working list is `BOOKS-COMPLETENESS-CHECK.md` in the repo
# root: one row per book, with the number of chapters the book's own
# contents lists, how many of them are inside our PDF, how many are
# MISSING, our PDF's page count, the last printed page our PDF reaches and
# the last page the contents lists.
#
# Two books are already known to be HALF-BOOKS (only volume 1 of a
# two-volume set):
#   * BRAUNWALD-12 -- our PDF ends at printed page 888 (then publisher
#     advertisements); the contents lists 102 chapters up to printed 1893.
#     45 chapters inside, 57 MISSING (from chapter 46 onwards).
#   * BOLOGNIA-2024 -- our PDF ends at printed page 1692; the contents lists
#     161 chapters up to printed 2705. 95 inside, 66 MISSING.
# A missing chapter is not a lost chapter: the pages are simply not in our
# file, so we cannot read them and cannot cite them (Law 2).
#
# The human's decision: get the other volume, or another copy of the whole
# book, or accept the book as "volume 1 only" and build only what we have.
# He says he will check every book himself, because a bad scan is a real
# possibility -- the same check must also catch a PDF whose pages are
# missing in the middle.
#
# **REMINDER TO THE MANAGER: the first thing to raise with the human in
# the next session is this checklist. Do not start any other work before
# it is settled.**
# ############################################################################

READ FIRST, IN ORDER:
1. This file.
2. `PROGRESS.md` (the ledger; the newest entry is at the top of "DONE").
3. `HANDOFF-2026-10-19-evening.md` (the earlier state; still correct about
   the TOC work, but its folio numbers are WITHDRAWN -- see section 1).

## 0. ONE-LINE SUMMARY

The Tables of Contents of all 37 books were checked against the real pages
for the first time: for every chapter we now know the PDF page where the
chapter BEGINS and the page number the book PRINTS for that page, read by
the free local reader from a picture of the page, with the picture kept on
disk. HARRISON-22 (505 chapters) was finished and re-checked. The 10 books
the human had already accepted were left untouched. Nothing was loaded into
Neo4j, nothing was frozen, the geography is untouched.

## 1. WHAT THE HUMAN DECIDED TODAY (these override older notes)

1. **The 10 books are fine and are not tested again.** They are:
   YOUMANS-4, MANDELL-9, ROSEN-2022, MURRAY-7, MIDDLETON-2019, KRAUSE-16,
   SABISTON-22, CAMPBELL-2020, GOODMAN-14, ADAMS-12.
2. **Mimo v2.6's work is not to be continued.** The rewrite of
   `kitchen/page_folio.py` (19 Oct evening) and the uncommitted +188 lines
   (21 Oct morning) are archived in `kitchen/logs/mimo-2026-10-21/` and are
   NOT used. The file in git is the 19 Oct MORNING version written by
   `space-bunny-free`. Proof of who wrote what is in the OpenCode session
   database (`~/.local/share/opencode/opencode.db`, table `message`).
3. **The manager's lane is the Table of Contents.** "You are a free model;
   you do the grunt work of going over the tables of contents and making
   sure they are ok." The globe, the entity registry, the viewer and the
   reading pipeline are for PAID models. Do not write those scripts.
4. **Nothing runs unattended.** Every book is started only after the human
   says so, and the human watches the output.
5. **The floor rule.** When the book's own contents and the page disagree,
   the SMALLER number is kept, and the difference is recorded as a finding
   about that book's contents.
6. **The memory file must not grow.** The detailed state goes into a
   handoff file like this one; `~/.config/opencode/AGENTS.md` only POINTS at
   it.

## 2. THE TOOL: kitchen/eyes_folio.py (the only new script)

For every chapter of one book it produces:
  * the PDF page where the chapter begins (the opener),
  * the page number the book PRINTS for that page (the folio),
  * therefore the chapter's printed page range (page_end = the next
    chapter's printed page minus one),
  * the picture of every page it looked at, kept in
    `kitchen/logs/eyes-render/<BOOK>/`.

    cd ~/second-opinion && source .venv/bin/activate
    python kitchen/eyes_folio.py HARRISON-22 --all --scan 6
    python kitchen/eyes_folio.py HARRISON-22 --sample 12 --seed 0
    python kitchen/eyes_folio.py HARRISON-22 --only 46,103 --scan 6
    python kitchen/eyes_folio.py HARRISON-22 --list        # pointers only

It writes:
  * `kitchen/logs/<BOOK>-eyes.json`  -- every chapter with its picture, the
    number, the proof and the disagreements (gitignored, rebuildable),
  * `kitchen/logs/<BOOK>-toc.json`   -- the BIBLE's own file (part 3
    section 4.4): provinces with page ranges, chapters with page_start =
    the printed page and page_end = the next chapter's page minus one.

It writes NOTHING to books.json, to any geography file or to Neo4j.

### 2.1 THE READER REPORTS, THE SCRIPT DECIDES

The reader is asked what it SEES, never to judge:

    KIND:    OPENING | BODY | INDEX | OTHER
    HEADING: every heading in the top third of the page, verbatim
    FOLIO:   the page number printed in a corner, or NONE

The script then decides. Asking the reader "is this the chapter's first
page? YES/NO" is NOT used: on an index page (which lists the chapter title)
the reader said YES, and that one wrong answer poisoned 400 chapters of
HARRISON-22 on the first attempt (72 ok, 433 unresolved).

### 2.2 HOW A PAGE IS FOUND (the pointer only points; the eyes decide)

1. the folio evidence: the opener is the page before the one that prints
   folio+1, or the page that prints the folio itself;
2. pages whose head carries a chapter marker and the number
   ("c h a p t e r" / "19");
3. pages whose running head carries the chapter title;
4. if all of that fails, the pages after the previous chapter are read one
   by one (--scan N) until the reader finds the opener.

### 2.3 THE RULES THAT SETTLE A DISAGREEMENT (all measured today)

* **The strongest proof**: a page that prints EXACTLY the folio the book's
  own contents gives for that chapter IS that chapter's first page. The
  reader's KIND does not matter (Harrison puts the chapter box in the
  middle of the page and the reader calls such a page BODY).
* **The corner number can be the chapter number**, not a folio. Test: the
  number equals the chapter number AND it is far from the contents' folio.
* **The reader can misread a digit** (2259 read as 2359). The pages around
  the page are the check: the real folio continues the sequence.
* **The proof from both sides**: when a page prints no number, the page
  before and the page after are read as well. If they print L and L+2, this
  page prints L+1 -- forced, not a guess. If they print L and L+1, this
  page is an UNNUMBERED INSERT (a plate) and carries no number at all.
  In HARRISON-22 there are 813 pages of the first kind and exactly ONE of
  the second (in the front matter).
* **A Table-of-Contents line that is only a number is NOT a folio.** Only
  the first three and the last three lines of a page are trusted, or the
  front matter hijacks the pointer.
* **Accents**: the contents print "Sjogren's Disease", the page prints
  "Sjögren's Disease". The comparison strips accents and a trailing "s".
* **The floor rule** (the human's): when the contents and the page
  disagree, the smaller number is kept and the difference is recorded.

## 3. THE STATE OF THE BOOKS

  * All 37 books have a Table of Contents in
    `kitchen/logs/<BOOK>-vis-toc.json` (37/37 clean, 4,755 chapters).
  * THOMPSON-2023: 20/20 by the eyes, 0 unresolved, every folio equal to
    the contents' folio. 4 provinces.
  * ROBBINS-10: 29/29 by the eyes, 0 unresolved, every folio equal to the
    contents' folio. 6 provinces.
  * HARRISON-22: 505 chapters, finished and re-checked with the final
    rules; the exact final count is in `kitchen/logs/HARRISON-22-eyes.json`
    (`_summary`) and in `PROGRESS.md`.
  * The other 23 books: not yet run with this tool. The command is above;
    they take 5 to 30 minutes each and cost no money.

### 3.1 TWO FINDINGS TO BRING TO THE HUMAN

* **HARRISON-22 chapter 46 ("Exercise Intolerance") has no page in our
  PDF.** The book jumps from printed 292 straight to 293. Checked by hand.
  The tool reports this as "no-page-in-this-pdf".
* **BOLOGNIA-2024 and BRAUNWALD-12 may be volume 1 of a 2-volume set.**
  The claim came from Mimo's code and has NOT been verified. In BOLOGNIA,
  65 of 161 chapters are on printed pages beyond the last folio our PDF
  reaches; in BRAUNWALD, 57 of 102. Until a human confirms, do not treat
  those books as complete.

## 4. WHAT IS LEFT (for the paid models, not for the free model)

The BIBLE part 3 steps A4 to A8 and all of part 4 are NOT done:
  * `kitchen/geography.py` (the BIBLE gives its exact code in part 3
    section 6.5): seating, the 2048x1024 district raster, the textures;
    it needs `books.json` to carry `cluster`, `field_name` and
    `status: accepted` for the 37 books, which is still empty.
  * the index pipeline (part 3 section 7.10): index_extract, index_parse,
    index_classify, index_resolve, index_pipeline -- the entity registry
    and the Freeze A.
  * `kitchen/load_geography.py` and the verification queries of part 3
    section 8.2 (Neo4j is installed, the schema is applied, but NOTHING has
    ever been loaded).
  * all of part 4 (Phase B): the page plan, transcription, extraction,
    quote verification, resolution against the frozen registry, loading.
    Note for whoever writes it: all 37 books have a real TEXT layer
    (132,812 pages), so no book needs full-page OCR; the reader's eyes are
    needed only for figure/table pages (about 40% of Harrison's pages).

## 5. THE INVARIANTS (nothing today touched them)

    kitchen/books.json     unchanged (page_offset still null for all 37)
    the geography files    untouched
    the 4,755 chapters     untouched (only the TOC data was ADDED to)
    Neo4j                  still empty, nothing frozen
    BIBLE/                 never edited (corrections go into PROGRESS.md)

## 6. HOW THE HUMAN WORKS (read this before the next session)

* One book at a time. He names it or agrees to it. Never a queue.
* Short, plain words. No walls of numbers. He checks facts himself and
  wants a path so he can look.
* Emojis in the chat replies only -- never in files, commits or this file.
* He does not want to be told what to do; he wants to be asked.
* If a plan fails, say so plainly and stop. Do not keep tinkering.
* He is in a hurry: the project is huge and he wants it working within his
  lifetime. Prefer the simple thing that works now over the perfect thing.
