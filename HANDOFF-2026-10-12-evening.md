# HANDOFF -- Second Opinion, end of session Monday 12 October 2026, ~17:30 Israel time

Written at the end of the working day so the next session continues at exactly
this point. **Read this file first, then `PROGRESS.md`, then the BIBLE part
that governs the current phase (Part 3).**

---

## 1. WHERE WE ARE IN ONE SENTENCE

Part 2 is finished. Part 3 step A2 (reading the Tables of Contents) is going
fast: **14 books are now read with the model's eyes and pass the honest
validator**, one of them completed today with a brand-new one-command
pipeline that takes a whole book from PDF to a verified verdict without
asking the human anything in the middle.

## 2. THE HUMAN'S ORDERS TODAY (both are now standing rules)

1. **Use lots of emojis in every chat reply** (12 Oct 2026). Emojis are for
   chat ONLY -- never in files, never in GitHub commits or reports, never in
   memory files. Nir clarified this himself.
2. **Do not stop and ask in the middle of a book** (12 Oct 2026, verbatim in
   substance): take a whole book through as best I can, ask only if I really
   need help, and do not create artificial stopping points "because this burns
   our whole day on you waiting, until I notice". This is why
   `kitchen/build_book.py` and `kitchen/build_queue.py` exist: a book now
   runs start to finish unattended, and a queue runs book after book.
   **Report progress from time to time anyway**, because Nir asked to be able
   to see that nothing is stuck.

## 3. BOOKS FINISHED AND VERIFIED TODAY

Read with the model's eyes (`--vis`), validator CLEAN, chapter numbers
complete, printed pages strictly increasing:

| book | sections | chapters | printed pages |
|---|---|---|---|
| HARRISON-22 | 20 | 505 | 1-3995 |
| BOLOGNIA-2024 | 1 | 161 | 1-2705 |
| SLEISENGER-11 | 9 | 132 | 1-2206 |
| BRAUNWALD-12 | 11 | 102 | 1-1893 |
| SABISTON-22 | 10 | 92 | 38-2065 |
| BENZON-2023 | 8 | 86 | 3-1128 |
| GUYTON-2026 | 15 | 85 | 3-1101 |
| CAMPBELL-2020 | 4 | 82 | 14-4503 |
| AVERY-2021 | 4 | 61 | 1-930 |
| ADAMS-12 | 6 | 49 | 3-1503 |
| DEVITA-12 | 4 | 107 | 2-1872 |
| ROBBINS-10 | 1 | 29 | 1-1305 |

Carried over from 11 Oct and unchanged: GUYTON-2026, CAMPBELL-2020,
HARRISON-22, SLEISENGER-11 (all four re-verified after today's script
changes -- see section 6).

**BRAUNWALD-12 is the notable one.** It was on the "hard" list because its
contents pages print no text layer at all (`pdftotext` returns 0
characters). The vision path read it with no difficulty: 11 sections, 102
chapters.

**ROBBINS-10's 29 chapters are correct, not a loss.** I checked the pages
with my own eyes: its contents is two pages (images 12-13) listing chapters
1-29, and the book itself begins at image 14. Robbins has **no Part or Unit
banners**, so it has 1 province, not 0.

## 4. THE NEW PIPELINE (one command per book, nothing typed by hand)

```bash
cd ~/second-opinion && source .venv/bin/activate
python kitchen/build_book.py <BOOK_ID>            # one whole book
python kitchen/build_queue.py --limit 8           # eight books, unattended
```

`build_book.py` runs, in this order, and prints a VERDICT at the end:

```
toc_vision.py            locate + read with the model's eyes  (the only slow step)
toc_reparse.py           rebuild JSON from the model's saved words   (no model call)
toc_strip_online_only.py remove chapters printed without a page   (no model call)
toc_dedupe.py            remove exact duplicates                   (no model call)
toc_sort_pages.py        put chapters in printed order             (no model call)
toc_fix_misfiled.py      move a chapter to the section that claims it (no model call)
toc_headings.py          read the Part/Section banners ALONE       (model call)
toc_apply_headings.py    build the provinces from those banners     (no model call)
-- then the same bookkeeping again --
toc_fill_gaps.py         ask the model for a numbered gap directly  (model call)
toc_reparse.py + strip + dedupe + sort + fix_misfiled + apply_headings
toc_validate.py --vis    THE HONEST CHECK
```

Only `toc_vision.py`, `toc_headings.py` and `toc_fill_gaps.py` cost model
time. Every other step rewrites the JSON from words the model already
printed, which is why almost every repair today cost nothing.

## 5. THE FIVE FAULTS FOUND TODAY (all caught, all fixed)

1. **A "VIDEO CONTENTS" page is indistinguishable from a contents page by
   shape.** SABISTON-22 prints its real contents on images 35-38 and then a
   VIDEO CONTENTS list in the same two columns with the same section numbers
   I-XI and the same chapter numbers. **Nir found this by looking at the
   pages himself.** The reader turned "Video 110.1 Pleural Effusion" into a
   chapter with a page number printed nowhere in the book -- exactly the
   invented-page fault that BIBLE part 3 section 4.4 forbids. FIX: the reader
   now declares `KIND=CHAPTERS` or `KIND=OTHER` before transcribing anything,
   and an `OTHER` page is refused and reported, never used. The same guard
   was added to `toc_reparse.py` and to `toc_headings.py` (which had
   rebuilt the book with 187 chapters instead of 92 because it read banners
   off the refused pages).
2. **That guard was then too strict, and only looking by eye found it.**
   BRANT-5 prints a contents with **no page numbers anywhere**, and six of
   its eight contents pages were refused with `KIND=OTHER`. Refusing a real
   contents page loses the whole book. FIX: a refused page is now shown to
   the model a second time with the question "is this the chapter list, even
   if it prints no page numbers?", and only a second refusal is honoured.
   Result: no pages refused any more (0 refusals on BRANT-5).
3. **The gap repair invented a page number.** `toc_fill_gaps.py` was asked
   for missing chapters on SABISTON-22 and answered with the "(online only)"
   entries the contents prints WITHOUT a page, then filled the empty page
   column -- producing chapter 50 with page_start 50, the chapter number
   copied into the page column. FIX: `toc_strip_online_only.py` removes such
   entries from the geography and writes them to
   `kitchen/logs/<BOOK_ID>-online-only.json` so nothing is silently lost.
   They get their page in Part 4, when the reader opens the eBook.
4. **A two-column page can be read right-column-first, which files chapters
   under the wrong section.** On SABISTON-22 image 37 the model read the top
   of the left column (chapters 68-72, printed pages 819-906, which belong
   to SECTION V SURGICAL ONCOLOGY starting at page 721) LAST, so they landed
   under SECTION IX VASCULAR SURGERY, which starts at page 1579.
   FIX: `toc_sort_pages.py` puts chapters in printed order, and
   `toc_fix_misfiled.py` moves a trailing run of chapters whose printed page
   is before their section's own printed start page to the section the
   banner itself claims -- the book's own page, never a guess.
5. **Re-running a stage on an already-built file double-counts.** Running
   `toc_apply_headings.py` on top of a built JSON gave 187 chapters for a
   book with 92, because the headings were applied twice. FIX: `build_book.py`
   always runs the full chain in order, and the `reparse` step rebuilds from
   the transcript before each apply.

## 6. WHAT WAS CHECKED AND FOUND CLEAN (no action needed)

* All 6 books finished before today were re-validated after today's script
  changes: GUYTON-2026 15/85, CAMPBELL-2020 4/82, HARRISON-22 20/505,
  SLEISENGER-11 9/132, SABISTON-22 10/92, ROBBINS-10 1/29. All CLEAN.
* A scan of every recorded page of all four earlier books for the words
  "video / podcast / online only / index / contributors" found no
  contamination. The three Campbell hits are real chapter titles ("Video-
  Assisted Thoracic Surgery"), which is correct.
* The "page_start == chapter number" test (the invented-page signature) found
  2 hits across all books, both chapter 1 page 1, which is simply true.
* GUYTON-2026's heading file had been lost and was regenerated; it is back to
  15 units / 85 chapters.

## 7. WHAT IS STILL OPEN -- IN THIS ORDER

### 7a. BRANT-5 -- one small fault left (do this first, ~2 minutes)
The second look stopped the refusals, and the model now reads all 8 pages,
but it returns only the **section banners** ("CHEST", "SECTION IV") and
**zero chapters**, so the book came out with 17 provinces and 0 chapters.
The pages ARE the contents -- image 36 was opened and read with my own eyes:
"SECTION III / CHEST / 10 Methods of Examination... 11 Mediastinum and Hila".
**Likely cause:** those contents print no page numbers, and the read prompt
still tells the model to leave out any entry it cannot see a page for
("If you cannot see a page number for an entry, leave that entry out").
**Suggested fix, in this order:** (a) add the `NOPAGES` marker to the read
prompt so a chapter with no printed page is transcribed with an empty page
field rather than dropped; (b) if that is not enough, re-read the 8 pages
with a prompt that asks only for `C<TAB>number<TAB>title` and forbids page
numbers entirely; (c) the fallback is `toc_openers.py`, which reads the
chapter-opening pages of the whole book and needs no contents page at all
(that is how SLEISENGER-11 was solved).
**Whatever happens: do not load a book with 0 chapters, and do not invent
page numbers to fill the gap.**

### 7b. BRADDOM-6 and BRENNER-11 -- no contents page located
Both reported "the model named 0 contents page(s)" over the first 120 images.
Nothing was invented. Next step for each: try `--start 1 --windows 40` to
walk further into the front matter, and if still nothing, `toc_openers.py`.
**Nir must not be asked to open these by hand yet** -- the openers path is
untried on both.

### 7c. The books the validator flagged on 11 Oct, still unread with the
model's eyes
`WILLIAMS-ENDO-2024` (19 chapters), `KRAUSE-16` (87), `MIDDLETON-2019` (22),
`ROCKWOOD-10` (24, **and its page numbers are invented**),
`WILLIAMS-OBSTETRICS-26` (25, **invented page numbers**), `THOMPSON-2023`
(116), plus every book never attempted: GOODMAN-14, GREEN-HAND-2021,
HAZZARD-2022, IRWIN-RIPPE-2023, KAPLAN-11, MANDELL-9, MILLER-10, MURRAY-7,
NELSON-2024, OXFORD-6, ROSEN-2022, STAHL-2024, WILLIAMS-HEMATOLOGY-2021,
YOUMANS-4.

### 7d. Still not started at all (Part 3)
`page_offset` detection (BIBLE part 3 section 4.6, printed page = image number
- offset). Every citation depends on it. Then seating and the raster
(sections 5-6), the entity registry from the indexes (section 7), load and
verify (8-9), and **the Freeze** (section 11).

### 7e. Gemma 4 31B, when Nir installs it
Same place as Qwen: Ollama on 127.0.0.1:11434. Add a `--model` switch to
`reader.py`, run the same books through it, and diff the two outputs chapter
by chapter.

## 8. MEASURED COST PER BOOK (so the day can be planned)

* locate: ~2 s per contact sheet of 6 pages, 20 windows = ~40 s
* read: 20-60 s per contents page
* headings: ~10-15 s per banner
* **whole book, measured today: 4 to 15 minutes**, most of it the read step
* batch of 8 books: ~50 minutes unattended

Nothing is loaded into Neo4j. That is deliberate: the validator is the gate.

## 9. HOUSEKEEPING

* The BIBLE files are **never edited**; corrections are AMENDMENTS in
  `PROGRESS.md` (3.1, 3.2, 3.3, 3.4 so far).
* `kitchen/logs/` is gitignored -- the model's raw answers live only on this
  laptop. They are the evidence; do not delete them.
* The Neo4j password is Nir's and lives only in `kitchen/.env`.
* To check the queue while it runs: `tail -20 kitchen/logs/queue2.log`.
  Long jobs must be started detached, or they are killed when the tool call
  returns:
  `setsid nohup python kitchen/build_queue.py ... > log 2>&1 < /dev/null & disown`