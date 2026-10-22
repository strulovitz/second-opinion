# HAND-OFF -- Second Opinion, end of 22 Oct 2026 (night)

Written so the next session can start from exactly this point without
reading any chat. Read this file first, then `PROGRESS.md`.

## 1. THE ONE RULE FOR THE NEXT SESSIONS

**One book at a time. After each book: stop and report to the human.**
This is the human's rule (22 Oct 2026) so that an interruption never leaves
a long batch half-explained. Nothing runs unattended.

The job in this phase is the Table of Contents ("my lane", decided by the
human on 21 Oct 2026): for each book, check its chapter list against the
real pages with the free local reader (Qwen 3.8 27B through Ollama), and
write the BIBLE-format `<BOOK>-toc.json`.

Do NOT work on the globe, the entity registry, the viewer, or the reading
pipeline. Those belong to paid models.

## 2. START HERE TOMORROW

Next book: **MILLER-10** (Miller's Anesthesia, 10th edition).

    cd /home/nir/second-opinion
    .venv/bin/python kitchen/eyes_folio.py MILLER-10 --all --scan 6

Run it in the background (see section 7), poll the log, fix any unresolved
chapters with `--only ... --from ... --scan ... --proof`, then write the
PROGRESS.md DONE entry, commit, push, report, and stop.

After MILLER-10 the order is the one in section 5.

## 3. WHERE THE WORK STANDS (the whole library, 37 books)

Verified with the eyes and finished (15 books):

    BRAUNWALD-12       102/102   0 unresolved, 0 disagree
    BOLOGNIA-2024      161/161   0 unresolved, 0 disagree
    AVERY-2021          61/61    0 unresolved, 0 disagree
    BENZON-2023         86/86    0 unresolved, 0 disagree
    BRANT-5             83/83    0 unresolved, 0 disagree
    BRENNER-11          71/71    0 unresolved, 0 disagree
    DELISA-6            62/62    0 unresolved, 0 disagree
    DEVITA-12          107/107   0 unresolved, 0 disagree
    FIRESTEIN-12       125/125   0 unresolved, 0 disagree
    GRAY-2020           79/79    0 unresolved, 0 disagree
    GREEN-HAND-2021     60/60    0 unresolved, 0 disagree
    GUYTON-2026         85/85    0 unresolved, 0 disagree
    HAZZARD-2022       108/108   0 unresolved, 1 TOC finding (see 8)
    IRWIN-RIPPE-2023   215/215   0 unresolved, 0 disagree
    KAPLAN-11           60/60    0 unresolved, 0 disagree

Verified with the eyes before this run (3 books):

    HARRISON-22         503/505  ch46 and ch417 not placed; ch46's page is
                                 NOT in our PDF (the book jumps from printed
                                 292 to 293, checked by hand); ch417 needs
                                 one more look
    ROBBINS-10           29/29
    THOMPSON-2023        20/20

Accepted earlier and deliberately NOT tested again (10 books):

    YOUMANS-4, MANDELL-9, ROSEN-2022, MURRAY-7, MIDDLETON-2019,
    KRAUSE-16, SABISTON-22, CAMPBELL-2020, GOODMAN-14, ADAMS-12

Still to do (9 books, in this order):

    1. MILLER-10
    2. NELSON-2024
    3. OXFORD-6
    4. ROCKWOOD-10          (prints no folio -- pdf-page rule)
    5. SLEISENGER-11
    6. STAHL-2024
    7. WILLIAMS-ENDO-2024
    8. WILLIAMS-HEMATOLOGY-2021
    9. WILLIAMS-OBSTETRICS-26  (prints no folio -- pdf-page rule)

## 4. WHAT WAS DONE TODAY (22 Oct 2026)

### Session A (morning/day): the two half-books

* BRAUNWALD-12 and BOLOGNIA-2024 arrived as only volume 1 of a 2-volume
  set. Both were made whole and verified: BRAUNWALD-12 is now 2,549 pages
  (TOC 102/102), BOLOGNIA-2024 is now 3,233 pages (TOC 161/161), both 0
  unresolved and 0 disagreements.
* The superseded sources were DELETED (the human's "no souvenirs" rule):
  `kitchen/books-superseded/` (about 2.8 GB: the old Braunwald half, the
  Bolognia volume-1 and volume-2 sources) and a 498 MB duplicate Braunwald
  download from `/home/nir/Downloads/`.
* `kitchen/books.json` and `kitchen/build_books_json.py` were updated to
  point at the new PDFs, with the new page counts and notes.
* The library is exactly 37 PDFs, all referenced by `books.json`. The BIBLE
  was checked: it never names a PDF file or an edition for these books, only
  book IDs such as BRAUNWALD-12 or HARRISON-22, and those IDs did not
  change. So the BIBLE needed NO edit.

### Session B: the eyes on ten books

Each one was run with `--all --scan 6`, fixed where needed, recorded in
PROGRESS.md, committed and pushed:

    AVERY-2021        61/61
    BENZON-2023       86/86
    BRANT-5           83/83
    BRENNER-11        71/71
    DELISA-6          62/62
    DEVITA-12        107/107
    FIRESTEIN-12     125/125
    GRAY-2020         79/79
    GREEN-HAND-2021   60/60
    GUYTON-2026       85/85

### Session C: the last three books of the day

    HAZZARD-2022     108/108   one TOC finding (ch7, see 8)
    IRWIN-RIPPE-2023 215/215   two divider pages and one front-matter
                               list needed a tool fix (see 7)
    KAPLAN-11         60/60    clean first pass

## 5. THE ORDER AFTER MILLER-10

MILLER-10, NELSON-2024, OXFORD-6, ROCKWOOD-10, SLEISENGER-11, STAHL-2024,
WILLIAMS-ENDO-2024, WILLIAMS-HEMATOLOGY-2021, WILLIAMS-OBSTETRICS-26.

## 6. BEFORE ANY OTHER WORK: ASK THE HUMAN TO CHECK COMPLETENESS

The human said he will check the OTHER PDFs himself for completeness
(missing pages in the middle of a book are possible). Remind him before
starting a new book if he has not mentioned it. Do NOT build him a table
or do the check for him.

## 7. THE MECHANICS (exact commands and files)

The tool needs the project venv. Plain `python3` fails with
`ModuleNotFoundError: No module named 'neo4j'`.

    cd /home/nir/second-opinion

    # whole book
    .venv/bin/python kitchen/eyes_folio.py <BOOK> --all --scan 6

    # repair selected chapters (1-based chapter numbers, comma separated)
    .venv/bin/python kitchen/eyes_folio.py <BOOK> --only 167,184,185 --scan 6 --proof

    # when the linked page is far off (front matter, a divider page, an
    # e-page): start the forward scan at a given PDF page
    .venv/bin/python kitchen/eyes_folio.py <BOOK> --only 7 --from 285 --scan 10 --proof

Run it in the background so the bash tool's timeout does not kill it:

    setsid -f bash -c 'cd /home/nir/second-opinion && \
      .venv/bin/python kitchen/eyes_folio.py <BOOK> --all --scan 6 \
      >> kitchen/logs/eyes-<BOOK>.log 2>&1'

Then poll (about 3.5-5 s per chapter):

    tail -6 kitchen/logs/eyes-<BOOK>.log
    grep -c "^ok\|^XX" kitchen/logs/eyes-<BOOK>.log
    ps -eo args | grep "eyes_folio.py <BOOK>" | grep -v grep   # empty = done

Outputs (all in `kitchen/logs/`, which is gitignored):

    <BOOK>-eyes.json      every chapter: pointer, tries, picture, status
    <BOOK>-toc.json       BIBLE-format TOC: provinces + chapters + page_start
    <BOOK>-folio.txt      pdftotext cache (checked against page_count_images)
    <BOOK>-vis-toc.json   the input chapter list (working file)
    eyes-<BOOK>.log       run log
    eyes-render/<BOOK>/   page pictures the reader saw

The eyes tool MERGES with an existing `<BOOK>-eyes.json`; it does not
overwrite it. `--only` also rewrites the merged `<BOOK>-toc.json`, so a
repaired chapter is never dropped from the TOC (that was a bug, fixed).

Reading a single page by hand (useful for diagnosis):

    .venv/bin/python - <<'EOF'
    import sys, json
    sys.path.insert(0, 'kitchen')
    import eyes_folio as E
    from pathlib import Path
    b = [x for x in json.load(open('kitchen/books.json'))
         if x['book_id'] == '<BOOK>'][0]
    pdf = Path('kitchen/books') / b['pdf_file']
    for pg in (100, 101):
        k, h, f, raw, png = E.ask_page(pdf, '<BOOK>', pg)
        print(pg, 'KIND', k, 'FOLIO', f, 'HEADING', h)
    EOF

## 8. FINDINGS RECORDED IN THE BOOKS (do not "fix" the books silently)

* HAZZARD-2022 ch7 "Decision Making and Advance Care Planning: What
  Matters Most": the book's own outline points at PDF page 284, which is
  the Part II divider page (it lists chapter 7 there). The real opener is
  PDF page 286. Recorded as a disagreement (contents 284 vs page 286).
* BRENNER-11 ch31: "Primary Glomerular Disease", page 1007. ch56:
  "Endocrine Aspects of Chronic Kidney Disease", page 1901. The outline had
  duplicate entries pointing at e-pages 1091 and 1915.e7; the working
  vis-toc was corrected and the result recorded.
* HARRISON-22: ch46's page is not in our PDF (printed 292 jumps to 293);
  ch417 still needs one more look.

## 9. FOUR BOOKS PRINT NO FOLIO (the pdf-page rule)

DELISA-6, BRANT-5, ROCKWOOD-10, WILLIAMS-OBSTETRICS-26 (and every
link/outline-sourced book that prints none, such as HAZZARD-2022,
IRWIN-RIPPE-2023 and KAPLAN-11) are recorded with the PDF page as the
number (`page_offset` 0 by construction). The proof is the link page plus
the heading; no printed folio is required.

## 10. TOOL CHANGES MADE ON 22 Oct 2026 (`kitchen/eyes_folio.py`)

1. `--only` seeds its forward scan from the nearest earlier placed chapter
   (before, it searched the first 400 pages only).
2. `--only` rewrites the merged `<BOOK>-toc.json` (before, repaired
   chapters were missing from the TOC: BENZON had 84 of 86).
3. A link-sourced, no-folio book is proved by the link page plus the
   heading (pdf-page branch), with no printed folio.
4. The floor rule now keeps `min(page, contents)` in BOTH directions
   (BRENNER ch31/ch56: the old TOC pointed at an e-page).
5. New `--from PAGE` starts the forward scan at a given PDF page.
6. Folio-cache guard: if the cached text has fewer pages than the PDF, the
   cache is rebuilt (FIRESTEIN-12 had 2,750 of 2,875 pages).
7. The scan branch accepts pdf-page matches, and refine/reconcile/floor are
   skipped for pdf-page chapters (HAZZARD-2022 ch7: the floor rule was
   putting the wrong outline number 284 back).
8. New `pdf_page_matches()`: accepts an OPENING page with a matching
   heading, or a divider page whose heading starts with "Chapter N"
   (IRWIN-RIPPE-2023 ch167/ch184); a front-matter listing is KIND=OTHER and
   is rejected (ch185 had been placed on PDF 95 by the image-field
   fallback).

## 11. GIT

Branch `main`, remote `origin` (github.com/strulovitz/second-opinion),
everything pushed, working tree clean at `afb8916`.

Commits from this day, newest last:

    82c52d8  BENZON-2023
    bdbfbd8  BRANT-5 (pdf-page rule)
    46a9de8  BRENNER-11 (floor rule, --from)
    966bec5  DELISA-6
    6dd36ed  DEVITA-12
    63c7a5a  FIRESTEIN-12 (cache guard)
    54f2717  GRAY-2020
    0d73d5d  GREEN-HAND-2021
    9c1bea0  GUYTON-2026
    5353a38  HAZZARD-2022 (scan accepts pdf-page; no refine for pdf-page)
    6737e8e  IRWIN-RIPPE-2023 (pdf_page_matches)
    afb8916  KAPLAN-11

The whole-book work (Braunwald, Bolognia, deletions, books.json,
build_books_json.py) is in the earlier commits `81de062`, `63c5680`,
`82c52d8`, `bdbfbd8`, `46a9de8`, `966bec5`, `6dd36ed`, `63c7a5a`,
`54f2717`, `0d73d5d` and the ones before them; `git log` has the detail.

## 12. STANDING RULES (do not forget)

* The BIBLE is NEVER edited. Corrections go into `PROGRESS.md` as
  amendments. The BIBLE still says "42 books"; AMENDMENT 3.3 in PROGRESS.md
  says the truth is 37.
* 37 books. `kitchen/books.json` is the single source of truth.
* One book at a time; stop and report after each.
* No emojis in files, commits, or GitHub reports (only in chat replies).
* `kitchen/logs/`, `kitchen/books/`, and `kitchen/.venv` are gitignored;
  the tracked results are PROGRESS.md, the tool, and books.json.
* Do not use `mimo-v2.6-flash-free`'s rewrite of `page_folio.py`; it is
  archived in `kitchen/logs/mimo-2026-10-21/` and is not used. The file in
  git is the 19 Oct morning version by `space-bunny-free`.
* When a plan fails, STOP and say "I don't know"; do not keep tinkering.

## 13. THE MOST USEFUL FILES

    PROGRESS.md                     the ledger: every DONE entry, newest first
    kitchen/eyes_folio.py           the eyes tool (all fixes above)
    kitchen/books.json              the 37 books, page counts, notes
    kitchen/logs/<BOOK>-eyes.json   the evidence for each chapter
    kitchen/logs/<BOOK>-toc.json    the BIBLE-format TOC per book
    kitchen/books/                  the PDFs (gitignored)
    AGENTS.md                       the 15 project laws + a pointer here
