# HANDOFF -- 2026-10-14 evening session

## WHAT HAPPENED TODAY

Nir opened GRAY-2020's PDF himself, saw a clean contents on pages 8-11, and
asked why we had reported "154 chapters, pages going backwards". He was
right: the model had read the book correctly, but the pipeline mangled it.
He also asked us to check ALL previous books for the same bug.

### Fixes made

1. **GRAY-2020 cleaned.** The 154-chapter mess was a stale build artifact.
   The real data was always 81 chapters. Two supplementary chapters (80, 81)
   print no page and were removed on Nir's order. Now 17 provinces / 79
   chapters, validator ok.

2. **KRAUSE-16 fixed.** Appendices renumbered A1-A48 (they were colliding
   with chapters 1-45). Two appendix entries ("Body Mass Index Table" and
   "Glycemic Index...") were being thrown away by a FRONT_WORDS regex bug
   that matched "Index" inside those titles. Regex fixed. Now 7 provinces /
   93 chapters, validator ok.

3. **All 22 books re-verified.** Automated scan for duplicate numbers,
   backwards pages, missing pages, duplicate provinces. Only KRAUSE-16
   failed (fixed). Result: 22/23 clean, 2,239 chapters.

### Files changed
- `kitchen/toc_vision.py` -- FRONT_WORDS regex fixed (Index only at start)
- `kitchen/logs/GRAY-2020-vis-toc.json` -- rebuilt, chapters 80-81 removed
- `kitchen/logs/KRAUSE-16-vis-toc.json` -- rebuilt from transcript, appendices renumbered

## CURRENT STATE

- **37 books total** in kitchen/books.json
- **22 books read and clean** (2,239 chapters)
- **15 books not yet read:**
  GREEN-HAND-2021, HAZZARD-2022, IRWIN-RIPPE-2023, KAPLAN-11, MANDELL-9,
  MIDDLETON-2019, MILLER-10, MURRAY-7, NELSON-2024, OXFORD-6, ROSEN-2022,
  STAHL-2024, WILLIAMS-ENDO-2024, WILLIAMS-HEMATOLOGY-2021, YOUMANS-4
- **Neo4j is empty.** Nothing loaded yet.
- **page_offset not started.** Every citation depends on it.

## NIR'S STANDING ORDERS (14 Oct 2026)

1. **ONE BOOK AT A TIME.** Never launch a batch queue unless he asks for
   that batch in that message. This overrides the 12 Oct "do not stop"
   order where they conflict.
2. **When a book is finished, say so clearly with evidence** (the validator
   output, the chapter count, the page range).
3. **When something is wrong, look at the ACTUAL logs and images**, not
   guesses. Nir checks facts himself and expects us to do the same.
4. **Short, plain words.** One thing per message. No walls of text.
5. **Use lots of emojis in chat replies** (not in files or commits).
6. **Do not give up on any book on our own.** Every book was hard to get.
   If a book looks hard, it goes on the question list, not a discard list.

## HOW TO READ THE NEXT BOOK

```bash
cd ~/second-opinion && source .venv/bin/activate
python kitchen/build_book.py <BOOK_ID>
```

This runs the whole book start to finish without stopping. Takes 4-15
minutes. For a long book, run it detached:

```bash
setsid nohup python kitchen/build_book.py <BOOK_ID> > kitchen/logs/build_<BOOK_ID>.log 2>&1 < /dev/null & disown
```

A book with no `>>>` line in `kitchen/logs/queue*.log` and no entry in
`kitchen/logs/build_queue_verdicts.json` was NOT finished -- re-run it.

## WHAT'S NEXT AFTER ALL BOOKS ARE READ

1. `page_offset` (BIBLE part 3 section 4.6) -- measure the offset between
   PDF image numbers and printed page numbers for every book.
2. Seating, raster, registry, load/verify into Neo4j.
3. The FREEZE.

## OPEN QUESTIONS FOR NIR

- STAHL-2024 (Prescriber's Guide) is organised one monograph per drug, not
  by chapters. Where is the contents page? (Asked 11 Oct, not yet answered.)
- ROSEN-2022: the model said image 3 is the contents; it is actually the
  copyright page. Which page really shows the contents? (Asked 11 Oct.)
