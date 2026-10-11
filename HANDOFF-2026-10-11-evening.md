# HANDOFF -- Second Opinion, end of session Sunday 11 October 2026, 21:30 Israel time

Written at bedtime so a new session can pick up exactly where this one
stopped. **Read this file first, then `PROGRESS.md`, then the BIBLE part
that governs the current phase.**

---

## 1. WHERE WE ARE IN ONE SENTENCE

Part 2 (the kitchen) is finished and proven. Part 3 (building the
skeleton) is going well: **four of the 37 books have now been read with the
model's eyes and pass the validator**, and the pipeline that does it is
built, measured and recorded.

## 2. THE BIG NEWS OF TODAY: LAST NIGHT'S NUMBER WAS WRONG

At the start of this session I wrote the validation script the BIBLE asks
for and had to **retract the "22 books, 2,859 chapters" figure** recorded
on 2026-10-10. Measured damage:

* **Whole stretches of contents were never read.** GUYTON-2026 had been
  given the page range `[14, 14]` -- ONE page -- so units I to V were never
  read and the book came out as 11 chapters starting at printed page 447.
  CAMPBELL-2020, GRAY-2020, MIDDLETON-2019, SLEISENGER-11 and others lost
  the same way.
* **Two books carried page numbers printed nowhere in the book.**
  ROCKWOOD-10 and WILLIAMS-OBSTETRICS-26 have contents pages with no page
  numbers in their text layer, so the model filled the column with the
  *chapter* number. Page 46 of the book is not chapter 46. This breaks
  Law 2 and must never be loaded.
* **The BIBLE's own completeness check is useless as written.** "Chapter
  count must match the number of TOC lines ending in a number" returned a
  near-constant -45% for every book, which is a property of the REGEX, not
  of the books. It was replaced by an honest one: *is this page number
  really printed next to this chapter's title?*

**Nothing from last night has been loaded into Neo4j, so no damage has
reached the database.**

## 3. THE HUMAN'S ORDER, AND WHY IT WAS RIGHT

Nir's instruction today: in the critical Table-of-Contents stage, use the
AI model **as much as possible, not as little as possible**; go book by
book; do not launch the 28-book job; later repeat everything with a second
model (Gemma 4 31B, which he will install) and compare the two brains.

Every improvement today came from that. Two proofs:

* **The model beats the text layer.** On GUYTON-2026 the text-layer rule
  had placed Unit V's chapters in a separate unit. I opened the page image
  with my own eyes: the model was right and the rule was wrong.
* **The model found a whole book the text layer could not.** SLEISENGER-11
  has **no table of contents at all** (checked page by page, and 24
  contact sheets shown to the model). Last night's locator "found"
  images 21-33 and produced 22 chapters. Reading the book from its own
  chapter-opening pages produced **132 chapters**.

## 4. BOOKS FINISHED TODAY (all four pass the validator)

| book | before | now |
|---|---|---|
| **GUYTON-2026** | 11 chapters (units I-V missing) | **85 chapters, 15 units**, pages 3-1101 |
| **CAMPBELL-2020** | 1,686 techniques, unusable as a map | **4 volumes, 82 districts**; the 1,736 techniques kept in `kitchen/logs/CAMPBELL-2020-vis-detail.json` |
| **HARRISON-22** | 435 chapters | **20 Parts, 505 chapters**, numbers 1-505 complete, pages 1-4002 |
| **SLEISENGER-11** | 22 chapters | **9 Parts, 132 chapters**, numbers 1-132 complete, pages 1-2221 |

Every one of these numbers was checked three ways: the validator, a direct
structural check (numbers complete and unique, pages strictly increasing),
and -- for the doubtful cases -- by opening the rendered page image and
looking at it.

## 5. THE DECISIONS NIR MADE TODAY (both recorded)

1. **CAMPBELL-2020's structure.** Its contents is three levels deep
   (Volume / chapter block / 1,686 techniques). Nir ruled that the
   geography must stay comparable with every other book, so the **chapter
   block is the district** and the techniques are kept for later, inside
   the chapters. "All this detail will have time in the future inside the
   chapters. It will not be lost. But we do not want to drown in detail
   like this at this stage now."
2. **Both remaining suggestions, not one.** Nir briefly thought two
   suggested books competed; on being told they are different fields
   (surgery vs pathology) he said he wants both and the order does not
   matter.

## 6. THE REUSABLE PIPELINE (all in `kitchen/`)

| script | what it does | cost |
|---|---|---|
| `toc_vision.py` | **finds** the contents with the model's eyes (6 pages per contact sheet at 100 dpi), then **reads** each page alone at 150 dpi | ~2 s per locate call, 6-110 s per page |
| `toc_openers.py` | for books with NO contents: shows the whole book as sheets and asks which pages open a chapter | 455 sheets ~45 min for a 2,725-page book |
| `toc_openers_build.py` | retries empty pages at 240 dpi, then hunts chapter numbers that are still missing | only for the failures |
| `toc_headings.py` | asks for the Part/Section banners ALONE (they get misread while transcribing 50 chapters beside them), then the first chapter under each | ~10 s per heading |
| `toc_apply_headings.py` | builds the provinces from those banners | instant |
| `toc_fill_gaps.py` | asks the model for a numbered gap directly | one call per gap |
| `toc_dedupe.py` | removes exact duplicates; a targeted re-read supersedes the first reading, and every replacement is reported | instant |
| `toc_reparse.py` | rebuilds the JSON from the model's saved words -- **no model call, ever** | instant |
| `toc_validate.py` | the BIBLE's own check, rewritten to be honest | instant |
| `toc_group_parts.py` | regroups chapters under their Part banner for opener-read books | instant |
| `toc_normalize.py` | flattens a nested contents to one level (Campbell) | instant |

**Every one of these regenerates its JSON from the model's recorded words
on disk. Nothing is ever typed by hand.** That is why most fixes cost no
model time at all.

## 7. THE FIVE LESSONS THAT COST THE MOST TODAY

1. **A thumbnail too small to read produces a confident wrong answer.** At
   55 dpi the model said "no contents page here" about GUYTON-2026 image
   14, which plainly is one. At 100 dpi, 6 pages per sheet, it reads them
   correctly -- and the call costs only ~2 seconds, because the answer is
   two short lines.
2. **Ask the model to read COLUMN BY COLUMN, left first, and not to stop
   early.** On CAMPBELL-2020 one page went from 5 lines to 107 and the
   book went from 1,205 to 1,686 entries.
3. **A page thinner than 20 lines is read again at 220 dpi, and the answer
   with more lines wins.** A "fewer than 5 lines" test had let a page
   through that returned 8 lines while its neighbours returned 111.
4. **The page number is sometimes its own field and sometimes inside the
   title field.** CAMPBELL-2020 uses the second form, and a parser that
   required four fields was silently discarding **1,300 of 1,686 entries**.
5. **A thin running header is not a chapter number.** The header
   "6 PART I Biology of the Gastrointestinal Tract" on an ordinary page was
   first reported as "chapter 6". Both prompts now say so explicitly.

## 8. WHAT TO DO NEXT, IN ORDER

### 8a. Continue book by book (Nir: "please continue", one at a time)

Nir wants **Sabiston** and **Robbins**, in any order, plus the rest.
Suggested order after those: the books the validator flagged as broken
(`WILLIAMS-ENDO-2024` had 19 chapters, `KRAUSE-16` 87, `ROBBINS-10` 29,
`MIDDLETON-2019` 22, `SLEISENGER-11` done, `ROCKWOOD-10` 24 with
**invented page numbers**), then the 15 that have never been read at all.

```bash
cd ~/second-opinion && source .venv/bin/activate
python kitchen/toc_vision.py SABISTON-22 --start 1 --windows 20
python kitchen/toc_reparse.py SABISTON-22
python kitchen/toc_dedupe.py SABISTON-22 --vis
python kitchen/toc_headings.py SABISTON-22          # only if it has a real
                                                     # contents page
python kitchen/toc_apply_headings.py SABISTON-22
python kitchen/toc_validate.py SABISTON-22 --vis
```
If the locator reports **no contents page**, do not give up: run
`python kitchen/toc_openers.py <BOOK_ID>` instead. That is what
SLEISENGER-11 needed.

### 8b. Two books need VISION, not the text layer
`ROCKWOOD-10` and `WILLIAMS-OBSTETRICS-26` print **no page numbers in
their contents at all**. Their contents pages must be read as IMAGES
(`reader.ask(..., images=[...])`), never from the text layer, or the page
numbers will be invented.

### 8c. `YOUMANS-4` and `BRAUNWALD-12`
Image-only contents (`pdftotext` returns 0 characters). They need the
same image reading as 8b.

### 8d. Gemma 4 31B, when Nir installs it
Same place as Qwen: **Ollama on 127.0.0.1:11434**. Add a `--model` switch
to `reader.py` and run the same books through it, then diff the two
outputs chapter by chapter.

### 8e. Still not started
`page_offset` detection (BIBLE part 3 section 4.6, printed page =
image number - offset). Every citation depends on it, so it must not be
skipped. Then the rest of Part 3: seating and the raster, the entity
registry from the 26 indexes, load and verify, and **the Freeze**.

## 9. QUESTIONS FOR NIR -- ONE AT A TIME, IN PLAIN WORDS

The 15 books he offered to open by hand are still waiting:
`STAHL-2024, ROSEN-2022, BRAUNWALD-12, MANDELL-9, MURRAY-7, NELSON-2024,
YOUMANS-4, BRADDOM-6, BRANT-5, GREEN-HAND-2021, HAZZARD-2022,
IRWIN-RIPPE-2023, KAPLAN-11, MILLER-10, WILLIAMS-HEMATOLOGY-2021`.
**But today's finding changes the question.** For SLEISENGER the answer
turned out to be "there is no contents page, and the chapter openers give
us everything". Before asking Nir to spend an evening with a book, **try
`toc_openers.py` on it first.** His rule stands and is absolute: no book is
ever set aside on our own initiative.

## 10. HOUSEKEEPING

* The BIBLE files are **never edited**; corrections are AMENDMENTS in
  `PROGRESS.md` (3.1, 3.2, 3.3, 3.4 so far).
* `kitchen/logs/` is **gitignored** -- the model's raw answers live only on
  this laptop. They are the evidence; do not delete them.
* The Neo4j password is Nir's and lives only in `kitchen/.env`.
* Commits pushed today: `0b67ddd`, `874f9d7`, `5b4d983`, `dfbc67b`,
  `2023276`, plus this handoff.
* Nothing has been loaded into Neo4j yet. That is deliberate.