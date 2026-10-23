# Second Opinion -- recovery and DeepSeek handoff, 23 Oct 2026

SUPERSEDED for next actions by `HANDOFF-TOC-REPAIR.md`. The generic tool
supports all 37 saved contents sources and variable offsets. Use ONE
DeepSeek session for the queue, not a switch back to SMART per book.
The older restrictions/procedure below are the historical Harrison pilot.

Read this first, then PROGRESS.md and BIBLE Part 3 sections 4.4-4.7 and
Part 8 section 6. This supersedes the evening handoff's next-step text.

## 1. Ready for the cheaper model

SMART's exporter repair is implemented and proved on HARRISON-22 only.
Repair checkpoint **70189c8** is committed and pushed to GitHub main.
CHEAP (DeepSeek) may supervise the tested one-book commands below after
Nir chooses the next book. Stop and report after EVERY book. Nothing
runs unattended. Do not start geography, registry, viewer or Phase B.

The computer previously froze; its cause is unknown. This recovery used
small standard-library tests and a few single-page pdftotext calls. No
local model, rendering, full-PDF conversion or library-wide run was used.
Continue this lightweight approach; do not launch eyes_folio --all,
toc_validate --vis, build_book, background jobs or any re-reading task.

## 2. What survived and what was fixed

The prior session's offset verifier, seven tests, Harrison acceptance /
field name / offset=43, and ledger survived on disk but were uncommitted.
GitHub and local main were checked: both e20cdb3. They were saved and
pushed as recovery checkpoint **2762f1f** before the exporter repair.
All 14 BIBLE files (nine parts and appendices/templates) were read.

The exporter had computed ends inside each province, truncating each
province's last chapter to its own first page. Equal starts could also
produce a negative range, and the final chapter was truncated. Fixed:
ends now follow the next chapter across the whole book; source order is
preserved; province bounds are min/max of their chapters; name_source
and other source province metadata survive export.

Nir selected "Yes, please continue" to shared-page ranges, the repair,
Harrison-only verification and this handoff. AMENDMENT 3.4 records
`page_end = max(page_start, next_page_start - 1)`; ch45/ch46 both include
printed page 291. No BIBLE file was edited.

`refine_opener()` also retained an old picture after choosing an earlier
page. Future observations now keep the chosen picture/raw answer together.
For the old Harrison ch103/ch448 records, saved back_walk evidence proved
the corrected pictures already existed. The initial observation is kept
in refine.initial_observation; a missing old raw answer is null, not made up.

## 3. Harrison proof and human review

Five-line Checkpoint 3.2 summary:

    HARRISON-22
    20 provinces
    505 chapters
    citation pages 1-4000 (printed units)
    page_offset=43; image-reference warnings=0; range warnings=0

All 505 chapter identities, starts, PDF pages and order stayed unchanged.
Exactly 21 chapter ends changed; exactly two evidence records changed.
The eyes summary stayed unchanged: 505 read, 0 unresolved, 0 disagreements.
books.json and the source vis-toc are byte-identical to their backup.
The full per-chapter changes and raw verifier output are in PROGRESS.md.

Index boundary was verified: PDF 4044 starts "Index"; PDF 4043 is an
intentionally blank page. Per the BIBLE, final end = 4044 - 43 - 1 = 4000.
The range includes that pre-index blank page; it is not a claim of text on it.

19 regression tests passed in 0.006s. Status remains accepted; do not mark
geography-done without Nir's Checkpoint 3.2 review. First report the summary
above and ask which ONE book he wants next. There is no approved next book.

## 4. Exact CHEAP procedure for one named book

Check versions and Git state before work; PROGRESS.md has today's versions
(Python 3.13.5, pdftotext 25.03.0, Git 2.47.3, gh 2.97.0).
Run from `/home/nir/second-opinion`. Replace BOOK_ID with Nir's chosen ID.

1. Dry run only:

       PYTHONDONTWRITEBYTECODE=1 .venv/bin/python kitchen/toc_reexport.py BOOK_ID

   This reads the existing vis-toc, toc and eyes JSONs, requires complete
   confirmed chapter coverage and uniform units/offset, checks existing
   images, and verifies the configured index start using TWO PDF pages.
   It refuses to change accepted chapter starts, identities or order.
   It imports neither the reader nor database helper. It writes nothing.

2. Explain the dry-run result to Nir. If any check fails, STOP and record
   the exact output under BLOCKED; do not modify code or guess a boundary.
   If clean and Nir approves applying this book:

       PYTHONDONTWRITEBYTECODE=1 .venv/bin/python kitchen/toc_reexport.py BOOK_ID --apply
       PYTHONDONTWRITEBYTECODE=1 .venv/bin/python kitchen/page_offset.py BOOK_ID

   The apply command makes a timestamped backup of all three input JSONs
   plus books.json before replacing individual output files atomically.
   Rerunning is safe after an interruption. The verifier cross-checks the
   BIBLE's four sample chapter titles against the current PDF.

3. Report province/chapter counts, first/last citation page, unit, offset,
   changes, warnings and backup path. Do not call a PDF-page unit "printed".
   For PDF-page citations offset=0 is only that citation coordinate;
   it does not establish the PDF's physical printed-folio mapping.

4. Record commands and raw results under DONE in PROGRESS.md, or BLOCKED
   if verification failed. The re-exporter does NOT change books.json.
   Saving an offset (`page_offset.py BOOK_ID --save`) requires an accepted
   record with approved field name and successful verification. Do not
   invent field names, statuses, numbering policies or checkpoint approval.

5. Inspect git status, diff and recent log, check sizes and secrets, stage
   only intended scripts/config/reports, commit and PUSH. No blanket add
   of local logs. Give Nir the commit and short summary, then STOP. Human
   review is required before the next book or geography-done status.

## 5. Known limits -- do not turn failures into new reading runs

Only Harrison has received this repair/offset pilot. The other 36 books
have not been re-exported. The tool intentionally stops if the saved eyes
are absent/incomplete, units are mixed, offsets vary, accepted starts/order
would change, images lack saved proof, or the index boundary is unconfirmed.
An unknown index uses the BIBLE's median-length fallback and says so;
an incorrect configured index causes a failure, not a silent fallback.

The ten books previously accepted WITHOUT eyes runs are: YOUMANS-4,
MANDELL-9, ROSEN-2022, MURRAY-7, MIDDLETON-2019, KRAUSE-16, SABISTON-22,
CAMPBELL-2020, GOODMAN-14, ADAMS-12. Their existing accepted work stands.
If a chosen book has no usable saved eyes, this tool cannot process it;
report that to Nir/SMART. Do not re-read it or fake eyes evidence.
Irregular numbering/per-province offsets need the human's decision under
Part 3 section 4.6. Two failures in CHEAP go back to SMART, per Part 8.

## 6. Files, backups and memory

    kitchen/eyes_folio.py        repaired exporter and future refinement
    kitchen/toc_reexport.py      no-reader, dry-run/apply, one book only
    kitchen/page_offset.py       complete saved-pair verifier + 4 PDF samples
    kitchen/test_toc_reexport.py 12 regression cases
    kitchen/test_page_offset.py   7 regression cases

Harrison local backup (before repair):
`kitchen/logs/toc-reexport-backups/HARRISON-22/20261023T155058442741/`.
It contains the original eyes, toc, vis-toc and books.json.
PDFs, pictures, transcripts, .env and kitchen/logs remain gitignored;
NEVER force-add them to the public repository. Their backup is on this
laptop, not GitHub. Scripts, tests, configuration and reports are in Git.

Both repository AGENTS.md and `~/.config/opencode/AGENTS.md` now point
here; detail belongs here and in PROGRESS.md, not in either AGENTS.md.
Future sessions must read this file explicitly. The PDF-completeness
reminder was given on recovery; do not repeat it every session.

## 7. Historical library state

37 books, not 42 (AMENDMENT 3.3). TOC opener readings complete: 27 checked
by the eyes, 10 previously accepted without those eyes runs. The evening
handoff has historical counts and the three recorded contents/page findings.
This exporter defect does not undo accepted opener readings. No Freeze has
been performed. Neo4j was not accessed in this recovery.

The older open questions and "not started" sentences in historical ledger
entries are snapshots, not new tasks. Use CURRENT PHASE, NEXT STEP and the
newest DONE entries. The shared-page question is answered in the ledger.
