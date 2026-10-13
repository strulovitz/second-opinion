# HANDOFF -- Second Opinion, end of session Tuesday 13 October 2026

**Read this file first, then `PROGRESS.md`, then the BIBLE part that governs
the current phase (Part 3).**

---

## 1. WHERE WE ARE IN ONE SENTENCE

Part 2 is finished. Part 3 step A2 (reading the Tables of Contents) has **15
books read with the model's eyes**, and the last thing that happened today is
that the human himself opened a book, found it has no table of contents at all,
and replaced it with a better one for the same subject.

## 2. THE HUMAN'S ORDERS TODAY -- BOTH ARE STANDING RULES

1. **ONE BOOK AT A TIME.** I started a queue of 23 books on my own initiative.
   Nir stopped it and said: *"who asked you to do this? we are doing one book
   at a time, stop what you are doing."* Never launch `build_queue.py`, a
   batch, or any multi-book job again unless he asks for that batch in that
   message. Ask him which book, then do that one book. The 12 Oct order still
   stands in the parts he did not object to: do not stop and ask in the MIDDLE
   of a single book -- take it through, and send short progress reports so he
   can see nothing is stuck.
2. **HOW TO WRITE TO HIM.** He said: *"I consider myself to be an intelligent
   person and I cannot understand what you said."* Short sentences, plain
   words, one thing per message, no walls of text, no jargon, no tables, no
   long lists of file names. Say what happened, what I did, and ONE question
   at the end. He checks facts with his own eyes, so give him the full path or
   a `file:///...` link. He decides about books -- never delete, keep or
   replace one without asking him first.

## 3. THE BOOK HE REPLACED BY HIMSELF

**BRADDOM-6** (Braddom's Physical Medicine and Rehabilitation, 6th 2021) was
removed from the library on his order. He opened the PDF himself and confirmed
it prints **no table of contents at all**, so no chapter can ever be read from
it. It was not a duplicate and not a bad book -- it is simply unreadable for
this project.

Its subject is now carried by **DELISA-6** -- *DeLisa's Physical Medicine and
Rehabilitation: Principles and Practice*, 6th edition 2019, **3742 pages**,
which Nir downloaded himself on 13 Oct into `~/Downloads` and I moved into
`kitchen/books/`:

* not damaged -- `pdftotext` reads it perfectly near the end (checked image
  1900 of 3742);
* **it HAS a table of contents, on PDF page 9**, with numbered chapters 1, 2,
  3 ... and their titles, plus their authors;
* it has a real text layer, so it is also readable by the cheap path.

**DELISA-6 is the next book to read.**

Braddom's size, SHA-256 and the reason are recorded forever in
`data/registry/removed-books.json`, exactly like the five files removed on
10 Oct. The library is **37 books again** (37 on 10 Oct, plus DeLisa, minus
Braddom).

**A subject is never covered with a different subject.** When a book cannot be
read, Nir downloads a real replacement for the SAME subject.

## 4. BRANT-5 WAS NOT A BROKEN BOOK -- WE HAD THROWN IT AWAY

Yesterday's handoff left BRANT-5 as "17 provinces and 0 chapters" and blamed
the reader. The transcript on disk held **84 correct chapter lines**. I opened
the rendered page myself
(`kitchen/pages/BRANT-5/vis/read-36/p-0036.png`) and the reader was right:
**Brant and Helms' Fundamentals of Diagnostic Radiology prints a real contents
with NO page numbers anywhere** ("9 Spine Imaging", "SECTION III / CHEST",
"10 Methods of Examination...").

`toc_vision.parse()` demanded a page number and discarded every entry without
one, so the whole book was emptied. It now keeps those entries with
`page_start = null`, and the validator reports "pages not printed". **No page
is invented** (Law 2); the pages will come from the book itself in Part 4.

BRANT-5 is now **12 sections / 83 chapters**, and the section sizes match the
book's own banners exactly: I:1, II:8, III:8, IV:6, V:7, VI:12, VII:7,
VIII:3, IX:5, X:10, XI:6, XII:10 = 83. The book's own chapter numbers include
letters (32A, 36B, 71A, 72D), which is why "missing numbers" 32/36/37/71/72
are not missing chapters.

## 5. THE FAULTS FOUND AND FIXED TODAY (all general, all with the evidence)

1. **AN EMPTY BOOK PASSED AS "CLEAN".** `build_book.py` searched the word
   " clean" inside the validator's output and found it in the summary line
   `0/1 clean`, so BRANT-5 was recorded CLEAN with 0 chapters. Now
   `toc_validate.py` prints one machine-readable `RESULT <BOOK_ID> ok|warn
   chapters=... provinces=... without_page=...` line per book, `build_book.py`
   reads that line, **0 chapters is a FAILED build**, and `build_queue.py`
   stores the chapter count in the ledger.
2. **`int("32A")` killed the heading step.** Chapter numbers with a letter
   suffix are now read as their digits.
3. **A heading with no chapter under its banner was guessed at.** SECTION XII of
   BRANT-5 prints no chapter below its banner (its chapters are on the next
   contents page), so the model answered NONE; deriving the number from the
   remaining chapter list gave **66 and swallowed six paediatric chapters**.
   The reader's own transcript says the banner is followed by **71A**, so the
   transcript is now authoritative and the guess is not used.
4. **The provinces were thrown away at the end of a `--no-gaps` build** (the
   last reparse starts again from the flat transcript). The headings step now
   always runs LAST.
5. **A hallucinated chapter (FIRESTEIN-12).** The validator reported
   `p574 -> p452 at 'Cytokines and Chemokines'`. The gap repair had answered
   "**28** Occupational Therapy, Physical Therapy, and Rehabilitation **574**"
   -- the exact title and page the contents already prints for **chapter 38**.
   `toc_reparse.py` now refuses any entry repeating another entry's (title,
   page) under a different number and logs it to
   `<BOOK_ID>-vis-copytitles.json`. Related: an entry given with an **empty**
   page field is recorded in `<BOOK_ID>-online-only.json` and kept out of the
   geography when the book prints pages elsewhere. FIRESTEIN-12 is now
   **2 volumes / 125 chapters / pages 1-2229 / validator ok**, with chapters
   2, 6, 28, 78, 79 **reported as still missing, not invented**.
6. **OPTION VALUES WERE THROWN AWAY.** `build_book.py` kept only the `--word`
   arguments, so `--windows 40` reached `toc_vision.py` as `--windows` and the
   book was read with the default 20 windows. Values are passed through now,
   in `build_book.py` and `build_queue.py` (which also takes `--windows` and
   `--start`).
7. **`--no-read` rebuilds a book from the transcript already on disk for ZERO
   model calls** -- that is how BRANT-5 was recovered. A book with no contents
   page found now stops with one clear line instead of six
   FileNotFoundErrors.

## 6. STATE OF THE BOOKS (13 Oct, after `toc_validate.py --vis`)

| book | sections | chapters | printed pages | validator |
|---|---|---|---|---|
| HARRISON-22 | 20 | 505 | 1-4002 | ok |
| BOLOGNIA-2024 | 1 | 161 | 1-2720 | ok |
| DEVITA-12 | 4 | 107 | 2-1885 | ok |
| SLEISENGER-11 | 9 | 132 | 1-2221 | ok |
| FIRESTEIN-12 | 2 | 125 | 1-2229 | ok |
| BRAUNWALD-12 | 11 | 102 | 1-1910 | ok |
| SABISTON-22 | 10 | 92 | 38-2084 | ok |
| BENZON-2023 | 8 | 86 | 3-1140 | ok |
| GUYTON-2026 | 15 | 85 | 3-1113 | ok |
| CAMPBELL-2020 | 4 | 82 | 14-4545 | ok |
| BRANT-5 | 12 | 83 | **none printed** | warn (by design) |
| AVERY-2021 | 4 | 61 | 1-943 | ok |
| ADAMS-12 | 6 | 49 | 3-1530 | ok |
| ROBBINS-10 | 1 | 29 | 1-1352 | ok |

Nothing is loaded into Neo4j. The validator is the gate, by design.

## 7. WHAT TO DO NEXT -- IN THIS ORDER

1. **DELISA-6** (one book, with his go-ahead already given this evening):
   `python kitchen/build_book.py DELISA-6`
2. **BRENNER-11** -- never located a contents page; try `--windows 40` now
   that option values actually reach the script, then `toc_openers.py`
   (that is how SLEISENGER-11 was solved).
3. The books the validator flagged on 11 Oct, read with the model's eyes:
   WILLIAMS-ENDO-2024, KRAUSE-16, MIDDLETON-2019, ROCKWOOD-10,
   WILLIAMS-OBSTETRICS-26, THOMPSON-2023.
4. Every book never attempted: GOODMAN-14, GREEN-HAND-2021, HAZZARD-2022,
   IRWIN-RIPPE-2023, KAPLAN-11, MANDELL-9, MILLER-10, MURRAY-7, NELSON-2024,
   OXFORD-6, ROSEN-2022, STAHL-2024, WILLIAMS-HEMATOLOGY-2021, YOUMANS-4.
5. GRAY-2020 was killed by the 12 Oct shutdown before writing any JSON, so it
   has never been read with the model's eyes.
6. Still not started at all (Part 3): `page_offset` detection (BIBLE part 3
   section 4.6, printed page = image number - offset), which **every citation
   depends on**, then seating and the raster (5-6), the entity registry from
   the indexes (7), load and verify (8-9), and **the Freeze** (11).

## 8. HOUSEKEEPING

* The BIBLE files are **never edited**; corrections are AMENDMENTS in
  `PROGRESS.md`.
* `kitchen/logs/` is gitignored -- the reader's raw answers live only on this
  laptop. They are the evidence; do not delete them.
* The Neo4j password is Nir's and lives only in `kitchen/.env`. Keep it out of
  chat, out of git and out of every report.
* Long jobs must be started detached or they die with the tool call:
  `setsid nohup python kitchen/build_book.py <ID> > kitchen/logs/build_<ID>.log 2>&1 < /dev/null & disown`
* Commits today: `3417dbc` (BRANT-5 recovered, the false-CLEAN bug, the copy
  guard, option values) and `cde9467` (DeLisa replaces Braddom). Both pushed.
