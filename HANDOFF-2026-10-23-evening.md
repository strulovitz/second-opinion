# HAND-OFF -- Second Opinion, end of 23 Oct 2026

Written at the end of the day so the next session can start from exactly
this point without reading any chat. Read this file first, then
`PROGRESS.md` (the ledger, newest DONE entries first).

## 1. THE ONE RULE (unchanged)

One book at a time. After each book, stop and report to the human. Nothing
runs unattended (the human's rule, 22 Oct 2026).

## 2. WHERE THE WORK STANDS: THE TOC LANE IS COMPLETE

The job of this phase -- check every book's Table of Contents against the
real pages with the free local reader and write the BIBLE-format
`<BOOK>-toc.json` -- is FINISHED. There is no book left for the eyes.

The nine books the 22 Oct handoff left open were all done on 23 Oct, one
commit each:

    MILLER-10                  87/87    0 unresolved, 0 disagree
    NELSON-2024               519/519   0 unresolved, 1 finding (ch506)
    OXFORD-6                  127/127   0 unresolved, 0 disagree
    ROCKWOOD-10                69/69    0 unresolved, 0 disagree
    SLEISENGER-11             132/132   0 unresolved, 1 finding (ch4)
    STAHL-2024                 61/61    0 unresolved, 0 disagree
    WILLIAMS-ENDO-2024         48/48    0 unresolved, 0 disagree
    WILLIAMS-HEMATOLOGY-2021  140/140   0 unresolved, 0 disagree
    WILLIAMS-OBSTETRICS-26     68/68    0 unresolved, 0 disagree

1,251 chapters read on 23 Oct. HARRISON-22 was also finished the same day
(see section 3): it is now 505/505 clean.

LIBRARY STATE (37 books in `kitchen/books.json`, the single source of truth):

    27 books verified by the eyes -- 24 with 0 unresolved and 0 disagree,
       3 with one recorded contents-vs-page finding (HAZZARD-2022,
       NELSON-2024, SLEISENGER-11)
    10 books accepted earlier and deliberately NOT tested again:
       YOUMANS-4, MANDELL-9, ROSEN-2022, MURRAY-7, MIDDLETON-2019,
       KRAUSE-16, SABISTON-22, CAMPBELL-2020, GOODMAN-14, ADAMS-12

AMENDMENT 3.3 still stands: the library is 37 books, not 42 (the BIBLE is
never edited). `kitchen/books.json` holds exactly 37 records.

## 3. THE FINDINGS (recorded, never silently "fixed")

A "finding" means: the page we stored is the page the eyes SAW and proved;
the book's own contents said something else, and the difference is written
down as evidence. These chapters are DONE, not pending.

* HAZZARD-2022 ch7 "Decision Making and Advance Care Planning" -- the
  outlined page 284 is the Part II divider; the real opener is PDF page
  286. Recorded 22 Oct.
* NELSON-2024 ch506 "Definitions and Classification of Hemolytic Anemias"
  -- the outline says PDF page 2976; the opener is PDF 2975 (printed 2952).
  Page 2976 in our PDF is a duplicated, out-of-order page (printed 2950,
  the ch505 box); PDF pages 2974-2976 are repeated as 2977-2979.
* SLEISENGER-11 ch4 "Gut Sensory Transduction" -- the working contents
  said printed 51; the opener is printed 34 (PDF 54), and 51 is the
  chapter's LAST page. Verified by eye.

HARRISON-22, finished on 23 Oct: ch417 "Diabetes Mellitus: Complications"
is PDF 3264 / printed 3221; ch499 "Network Medicine and Multiomic
Approaches..." is PDF 3998 / printed 3955. Both openers sit at the FOOT of
the previous chapter's last page. The 2 old unresolved chapters are gone,
and the eyes file is now 505 rows (the old 507 was duplicate rows for
417/499, now cleaned).

## 4. TOOL CHANGES MADE ON 23 OCT (`kitchen/eyes_folio.py`)

All are recorded with the comment that explains the book that forced them.

1. A pdf-page book always stores the PDF page as the number; a printed
   folio the reader happens to see on that page is kept only as
   `reader_folio` evidence. Before, 12 NELSON chapters had the folio and
   507 had the PDF page, so the TOC mixed two units.
2. The "contents disagree" test compares like with like (contents PDF page
   vs PDF page for pdf-page books; contents folio vs printed folio for
   printed books).
3. `number_in()`: dotted chapter numbers ("4.2") match the reader's
   flattened heading ("chapter 4 2 ..."). Before, every chapter of OXFORD-6
   failed.
4. `head_names_chapter()`: the page's own head may prove the opener (a
   second chapter opening at the foot of a page, NELSON ch46; a head that
   is the title, STAHL).
5. When every pointer candidate fails, the forward scan starts at the first
   pointer, not at the previous chapter (OXFORD-6 ch4.9).
6. `chapter_kind()` honours `_printed_folio`: a text-read TOC that carries
   a printed folio different from `page_start` is storing PDF pages
   (STAHL-2024). Before, 51 STAHL chapters landed one drug late.
7. `text_names_chapter()`: the page's own text carries the "CHAPTER N
   title" opener box, so a foot-of-page opener is proved even when the
   reader names only the top of the page (HARRISON ch417/ch499).
8. The candidate list tries the EXPECTED page first, computed from the
   previous placed chapter's own offset. HARRISON ch417 had matched ch416's
   page because both titles begin "Diabetes Mellitus".

These changes were exercised on the nine books above and on HARRISON-22.
The 27 books verified before 23 Oct were checked with the older tool and
were NOT re-run; their recorded results stand.

## 5. WHERE THE OUTPUTS LIVE

    kitchen/logs/<BOOK>-eyes.json    every chapter: pointer, tries, picture,
                                     status, numbers, evidence
    kitchen/logs/<BOOK>-toc.json     the BIBLE-format TOC (provinces +
                                     chapters + page_start)
    kitchen/logs/<BOOK>-folio.txt    the pdftotext cache used as evidence
    kitchen/logs/eyes-<BOOK>.log     the run log
    kitchen/logs/eyes-render/<BOOK>/ page pictures the reader saw

`kitchen/logs/`, `kitchen/books/` and the venv are gitignored. The TRACKED
results are `PROGRESS.md`, `kitchen/eyes_folio.py`, `kitchen/books.json`
and this handoff. The TOC JSONs are on disk in `kitchen/logs/` and are the
input for the next phase; they are not in Git.

## 6. WHAT MUST NOT BE STARTED UNASKED

The globe, the entity registry, the viewer and the reading pipeline belong
to the PAID models (the human's decision, 21 Oct). Do not start them, do
not "prepare" them, and do not run anything unattended. If the human asks
for them, first read the BIBLE part that governs the phase and follow it.

## 7. HOW TO VERIFY TODAY'S WORK (copy-paste, run in the repo)

    cd /home/nir/second-opinion
    .venv/bin/python - <<'EOF'
    import json
    for b in ("MILLER-10","NELSON-2024","OXFORD-6","ROCKWOOD-10",
              "SLEISENGER-11","STAHL-2024","WILLIAMS-ENDO-2024",
              "WILLIAMS-HEMATOLOGY-2021","WILLIAMS-OBSTETRICS-26",
              "HARRISON-22"):
        s = json.load(open(f"kitchen/logs/{b}-eyes.json"))["_summary"]
        print(f"{b:24s} {s['read_by_eyes']:>4}/{s['chapters']:<4} "
              f"unresolved={s['unresolved']} "
              f"disagree={s['contents_disagreements']}")
    EOF

Expected: every line has unresolved=0; only NELSON-2024 and SLEISENGER-11
show disagree=1 (HAZZARD-2022 also shows 1). HARRISON-22 shows 505/505.

    git -C /home/nir/second-opinion log --oneline -12
    git -C /home/nir/second-opinion status --short --branch   # clean

## 8. GIT

Branch `main`, remote `origin` (github.com/strulovitz/second-opinion),
everything pushed, working tree clean at the commit that adds this file.

Commits from 23 Oct, oldest first (the start of the day was `3350938`, the
hand-off note itself):

    8b312d9  MILLER-10
    9263250  NELSON-2024 (+ pdf-page units, disagreement test)
    9164cc3  OXFORD-6 (+ dotted numbers, page-head proof)
    11be26d  ROCKWOOD-10
    b3edcc8  SLEISENGER-11
    c807b4d  STAHL-2024 (+ text-contents PDF-page kind)
    efe6629  WILLIAMS-ENDO-2024
    65927c3  WILLIAMS-HEMATOLOGY-2021
    b017226  WILLIAMS-OBSTETRICS-26 (+ TOC lane complete summary)
    a2d80bb  HARRISON-22 (foot-of-page openers, expected page first)

## 9. NEXT

Nothing is pending in this lane. When the human is ready, the paid-model
work (globe, registry, viewer, reading pipeline) starts from the BIBLE,
not from this file. Otherwise: ask the human what they want next.

Standing rules that still apply: the BIBLE is never edited (corrections go
into PROGRESS.md as amendments); no emojis in files, commits or GitHub
reports; when a plan fails, stop and say "I don't know" instead of
tinkering; report with evidence or not at all.
