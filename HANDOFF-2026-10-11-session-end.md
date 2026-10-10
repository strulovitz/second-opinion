# HANDOFF -- Second Opinion, end of session Saturday 10 / Sunday 11 October 2026

Written at 00:07 Israel time so a new session can pick up exactly where this
one stopped. Read this file first, then `PROGRESS.md`, then the BIBLE part
that governs the current phase.

---

## 1. WHERE WE ARE IN ONE SENTENCE

Part 2 (the "kitchen") is **finished and proven**. Part 3 (building the
skeleton) is **half done**: the 37 books are inventoried and cleaned up, and
**22 of the 37 now have a verified Table of Contents totalling 2,859
chapters**; the other 15 need a human eye before the work can continue.

## 2. WHAT IS FINISHED AND PROVEN (do not redo any of this)

### Part 2 -- complete, all ten checkpoint lines passed
- 37 PDFs in `kitchen/books/` (gitignored; `git check-ignore` proves they can
  never reach GitHub).
- Java 21 + Neo4j CE 2026.09.0 installed and running; password set by Nir;
  database listens on 127.0.0.1 only, so the internet cannot reach it.
- Python `.venv` inside the repo with all 7 libraries; `kitchen/requirements.txt`.
- Neo4j schema applied: 4 constraints, 12 indexes, 3 Meta rows.
- `python kitchen/db.py` prints `[{'ok': 1}]`; slug test prints
  `diseases-and-conditions-sjogrens-disease`.
- `AGENTS.md` (the Fifteen Laws, copied verbatim out of the BIBLE),
  `PROGRESS.md` (the ledger), `LICENSE`, `LICENSE-CONTENT.md`, `README.md`.
- **The website is live: https://www.strulovitz.org/2nd-opinion/** (200 OK).
  It is mounted by ONE symlink Nir approved:
  `~/strulovitz-website/exports/2nd-opinion -> ~/second-opinion/site`.
  No change was made to Caddy, to the Cloudflare Tunnel, or to Apache.

### Part 3 -- steps A0 and A1 complete
- **The library is 37 books, not 42** (AMENDMENT 3.3). Five PDFs were deleted
  on Nir's order: three byte-identical duplicate pairs (Goodman & Gilman,
  Brenner & Rector's Kidney, Bailey & Love's) plus two same-field losers
  (Bailey & Love's lost to Sabiston; Marino's ICU Book lost to Irwin & Rippe).
  Every deleted file is recorded with its SHA-256 in
  `data/registry/removed-books.json`, which is committed.
  **Brenner, Goodman & Gilman, Bailey & Love's and Marino's ICU Book were NOT
  duplicates -- they were unique books we chose not to use. If Nir ever wants
  them they must be downloaded again.**
- `kitchen/books.json` is the single source of truth: 37 records, all with
  status "candidate", 130,457 pages in total.
- All 37 books have a real text layer (except two whose contents pages are
  images: BRAUNWALD-12 and YOUMANS-4).

## 3. THE FOUR SCRIPTS THAT WORK (this is the reusable pipeline)

Put them in this order, they build on each other:

| script | what it does | cost |
|---|---|---|
| `kitchen/intake.py` | pdfinfo + font check on every PDF | 1 min |
| `kitchen/build_books_json.py` | builds `books.json` with the book_id rules | instant |
| `kitchen/find_toc.py` | finds contents and index page ranges by scoring | 1 min |
| `kitchen/vis_locate.py` | **finds the contents page with the model's EYES** (contact sheets of 20 pages, multimodal) | ~2 min/book |
| `kitchen/extract_tocs.py` | dumps the contents pages as text with `pdftotext` | 15 s for all |
| `kitchen/toc_to_json.py` | **reads ONE page at a time** and outputs provinces + chapters | 1-2 min/book |
| `kitchen/reader.py` | talks to the local model (verbatim from the BIBLE + 2 documented fixes) | -- |

Current result of that pipeline: **22 books, 2,859 chapters.**

## 4. THE FIVE LESSONS THAT COST HOURS (do not relearn them)

1. **Never call `pdftotext` once per page.** One call per page RANGE, then
   split the output on the form-feed character `\f`. 301 pages takes 1.0 s
   that way; per-page calls took hours on the 1.7 GB books.
2. **Never match a Table-of-Contents line by "ends with a page number".**
   Contents pages are multi-column, so a physical line interleaves entries and
   the number sits in the middle. Counting title-then-number fragments fixed
   detection from 18/39 to 33/39.
3. **Regex cannot find a contents page reliably.** It keeps selecting
   NUMBERED REFERENCE LISTS (`143. Moore MW, Klein RD...`), contributor lists
   and dedications, because those look exactly like contents to a pattern.
   Ask the multimodal model instead -- it reproduced Harrison's known-correct
   range 7-18 exactly.
4. **Ask the model ONE PAGE AT A TIME with `reasoning_effort="none"`.** This
   model burns hidden-reasoning tokens *before* answering. With a small
   `max_tokens` the answer comes back as an EMPTY string with
   `finish_reason="length"`. Ollama's `"think": false` is **ignored** on
   `/v1/chat/completions`; the working switch is `reasoning_effort="none"`.
   One giant prompt per book also silently dropped whole sections. Page-at-a
   time roughly doubled the chapters found (Campbell 415 -> 862, DeVita
   64 -> 269, Sabiston 93 -> 124).
5. **Long jobs must be detached** with
   `setsid nohup <cmd> > log 2>&1 < /dev/null & disown`, or they are killed
   when the tool call returns. Scripts that use `pool.map` print nothing
   until the very end -- print incrementally instead.

## 5. WHAT IS STILL TO BE DONE, IN ORDER

### 5a. THE BOOKS NIR WILL LOOK AT BY HAND (see section 6 for the questions)
Nine books have **no contents located at all**:
`BRADDOM-6, BRANT-5, GREEN-HAND-2021, HAZZARD-2022, IRWIN-RIPPE-2023,
KAPLAN-11, MILLER-10, STAHL-2024, WILLIAMS-HEMATOLOGY-2021`

Six books have a contents range located but produced **fewer than 5
chapters**: `BRAUNWALD-12, MANDELL-9, MURRAY-7, NELSON-2024, ROSEN-2022,
YOUMANS-4`

### 5b. Vision reading for the image-only contents
`YOUMANS-4` (images 21-52) and part of `BRAUNWALD-12` have **no text layer at
all** -- `pdftotext` returns 0 characters. They must be read by sending the
rendered page images to `reader.ask(..., images=[...])`. The model has
`vision` capability, so this works offline and free. Nothing to install.

### 5c. Validate before loading anything into Neo4j
`kitchen/toc_validate.py` from BIBLE part 3 section 4.4 is still to be
written: page numbers must increase through the book; chapter counts must
match the number of lines in the contents text.
**Specifically: HARRISON-22 went from 494 chapters to 435 when the method
changed. Determine whether chapters were duplicated or lost.**

### 5d. page_offset detection (BIBLE part 3 section 4.6)
`printed_page = image_number - page_offset`. Every citation depends on this.
Not started.

### 5e. The rest of Part 3
Seating and the raster (sections 5-6), the entity registry from the 26
indexes (section 7), load and verify (8-9), and **the Freeze** (section 11).

## 6. OPEN QUESTIONS FOR NIR -- TO BE ASKED ONE AT A TIME, IN PLAIN WORDS

Nir asked to be walked through these one by one, with simple explanations,
and to be the one who decides. Do not present a menu of options without
explaining what each one means.

1. **STAHL-2024** (The Prescriber's Guide: Children and Adolescents). Our
   tool pointed at pages 66-67 expecting a contents list, and those pages
   turned out to be the entry for the drug *aripiprazole* -- ordinary drug
   text. That is all it means: we did not find a table of contents; it does
   not mean the book has none. This book is arranged one monograph per drug,
   so its structure may differ from a normal textbook. Nir will open it.
   **Question: does it have a contents/contents-list page, and if so on
   roughly which page?**
2. **ROSEN-2022** (Rosen's Emergency Medicine). The vision model answered
   "image 3 is the contents". Image 3 is actually the **copyright page**
   ("Elsevier, 1600 John F. Kennedy Blvd... ISBN... VOLUME 1"). So the model
   was wrong; the reader then correctly refused to invent chapters from it.
   **Question: which page in Rosen's actually shows the list of contents?**
3. The other thirteen books in 5a/5b: same question -- where is the contents?
4. If a book truly has no contents page, the decision is whether to use its
   structure differently (for example, by drug class for Stahl) or to set it
   aside. **Nir decides; do not set any book aside on our own.**

## 7. HOW TO PICK THIS UP TOMORROW

```bash
cd ~/second-opinion
git pull                                  # in case anything changed
source .venv/bin/activate
tail -20 kitchen/logs/toc_run3.log        # last reader run, 22 books OK
python kitchen/toc_to_json.py <BOOK_ID>   # re-extract one book's chapters
```
Check that Neo4j is still up with `systemctl is-active neo4j`, and remember
the local websites are NOT started at boot -- `sites-on` starts them.

## 8. HOUSEKEEPING NOTES

- The BIBLE files are **never edited**. Corrections are declared as
  AMENDMENTS in `PROGRESS.md` (AMENDMENT 3.1, 3.2 and 3.3 so far).
- Every failure is written into `PROGRESS.md` with its evidence, so the same
  dead end is never walked twice.
- The Neo4j password is Nir's and is **not** in any committed file; it lives
  only in `kitchen/.env`, which is gitignored.
- Git commits on `main`: `9658b85`, `e33d024`, `239784b`, `b59bbfe`,
  `032121f`, `f8a4ad0`, `576a36a` and this handoff.