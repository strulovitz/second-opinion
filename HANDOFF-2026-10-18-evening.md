# HANDOFF -- 2026-10-18 evening, session end

READ FIRST, IN ORDER:
1. This file
2. `PROGRESS.md` entries (a)-(f), 18 Oct (newest first under DONE)
3. `HANDOFF-2026-10-16-evening.md` for the older method notes

## WHERE WE ARE

Validator: **36/36 books clean, 4,323 chapters. Every attempted book is
clean.** Nothing in Neo4j; nothing frozen. Safe to continue.

Today (18 Oct) six books were finished, one at a time, each approved by
Nir, each committed + pushed:

    (a) NELSON-2024               (b) OXFORD-6
    (c) ROSEN-2022                (d) STAHL-2024
    (e) WILLIAMS-ENDO-2024        (f) WILLIAMS-HEMATOLOGY-2021

Commits: 833f91f, fcab517, c1215f5, beedfbc, fe00c15 (all pushed).

## THE ONE BOOK LEFT

**YOUMANS-4** -- the LAST book. Nir approved starting it NEXT TIME
(his words tonight: "we will do the last one next time"). Per the
one-book rule: start only after he says go.

Known facts about it (from 10-11 Oct reconnaissance, re-check before
starting):
- IMAGE-ONLY: pdftotext returns 0 characters. No text layer at all.
- Therefore it needs the VISION path with model eyes, like the very
  early books: `kitchen/toc_vision.py YOUMANS-4 --start 1 --windows 20`
  (then the standard chain). If the locator finds no Contents, try
  `toc_openers.py` FIRST; only after that ask Nir to open it by hand.
- It was on Nir's "offered to open by hand" list, but the standing
  rule is: try toc_openers.py first.
- It is the 37th and last book of the library. After it: every book
  has its geography, and the next BIBLE phase is page_offset
  (BIBLE 3 section 4.6) -- NOT started, and every citation depends on it.

## THE PIPELINE FOR ONE BOOK (unchanged)

```bash
cd ~/second-opinion && source .venv/bin/activate
python kitchen/build_book.py YOUMANS-4        # whole book, start to finish
```
Or step by step (see PROGRESS / 16 Oct handoff for the full method).
Long jobs must be detached:
`setsid nohup python kitchen/build_book.py YOUMANS-4 > kitchen/logs/YOUMANS-4.log 2>&1 < /dev/null & disown`
ALWAYS copy a book's vis-toc.json aside before any rebuild.
Validator: `python kitchen/toc_validate.py YOUMANS-4 --vis`;
full library: `python kitchen/toc_validate.py --vis` must stay
36/36, 4323 (then 37/37 after YOUMANS-4).

## STANDING RULES (still in force)

- ONE BOOK AT A TIME; never a batch; never build_queue.py unless Nir
  asks in that message. Ask him which book, then go; do not stop mid-book.
- Provenance Law 2: pages from the book's own evidence, never invented.
  page_start currently stores PDF pages for the outline-sourced books;
  printed-folio drift is the future page_offset problem.
- Territory names: number + meaning together ("Part VI - The Erythrocyte").
- Books with no printed parts get written groups (name_source written).
- JSON is regenerated from recorded text (Law 11), never hand-typed.
- Emojis in chat only; none in files/commits/memory.
- Neo4j password stays in kitchen/.env, never in chat or git.
- Do not touch BIOS. Do not run both PCs' hosting at once.

## TODAY'S LAST BOOK, ONE LINE EACH (method reminders)

- ROSEN-2022: bookmark outline + banner scan + KEY CONCEPTS openers.
- STAHL-2024: printed Contents WAS in the PDF TEXT LAYER (old locator
  wrong) -- check the text layer before declaring a book contents-less.
- WILLIAMS-HEMATOLOGY-2021: 8th contents-less book; its Contents was a
  scraped AccessMedicine web TOC on pdf 82-83 (titles + parts, no page
  numbers); pages from misnamed libgen "ownload (N).pdf" bookmarks;
  14 titles eye-verified, 140/140 openers pdftotext-verified, ZERO
  model calls. Builder: kitchen/logs/WILLIAMS-HEMATOLOGY-2021-build.py.
