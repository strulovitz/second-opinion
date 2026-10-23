# Hand-off to SMART -- section 4.4 chapter-end repair is complete (2026-10-23)

CURRENT TASK: read `HANDOFF-TO-DEEPSEEK-CAMPBELL-2026-10-23.md` first.
SMART found a Campbell chapter-list mismatch; Nir assigned its repair to
DeepSeek. This older handoff's completion claim is not physical-book proof.

From: DeepSeek (executor)
To: GPT 6.1 Sol (SMART, project manager)
Read with: `AGENTS.md`, `PROGRESS.md`, `TOC-REPAIR-STATUS.json`,
`HANDOFF-TOC-REPAIR.md` (the detailed repair procedure).

## Bottom line

The section 4.4 chapter-end repair you assigned is COMPLETE for all 37
books.

- 37 applied, 0 blocked, 0 pending/stale.
- 1,730 wrong or missing end values corrected in total.
- 39 regression tests pass.
- `books.json` was not changed: no book was accepted, frozen, or marked
  geography-done.
- 5 final pages were proved from the index. The other 32 are provisional
  median estimates; 8 of those are capped at the book's last page.
- No zero-length last chapter and no end past the book length remain.

## What was done

- 29 books were repaired in place. Only `page_end` and the province
  bounds derived from it changed. A field-by-field comparison against
  every original backup found 0 changes to numbers, titles, starts, PDF
  pages or province names.
- 3 books needed nothing and wrote no file: ADAMS-12, GOODMAN-14,
  HARRISON-22.
- 8 books were rebuilt from their already accepted contents:
  - Empty or unusable exports: MANDELL-9 (0 -> 210 chapters), MURRAY-7
    (1 -> 142), ROSEN-2022 (0 -> 208), YOUMANS-4 (missing -> 432).
  - The four exceptions Nir reviewed and approved:
    - CAMPBELL-2020: the old export was 862 operation sub-entries
      (45.1...90.10) covering pages 2222-4526 only; now the accepted 82
      chapters, starting page 14.
    - KRAUSE-16: old 87 entries, missing chapters 22-25, appendices
      numbered 1-48; now the accepted 93 (appendices A1-A48).
    - MIDDLETON-2019: old 22 rows, mostly chapter 3 repeated, pages
      1-59; now the accepted 99 chapters (pdf-outline).
    - SABISTON-22: old 124 rows including chapters 1-19 marked
      "(online only)" and duplicate sections; now the accepted 92
      printed chapters. Online-only content is not a territory
      (BIBLE 4.2).
- FIRESTEIN-12 also had 2 stale image links fixed (ch92, ch115); 0 image
  issues remain.
- 13 variable-offset books kept their accepted printed/PDF pairs.

### Final-page rule actually used

1. A verified index boundary wins (bounded single-page `pdftotext` checks).
2. Otherwise, a plausible existing final end is kept only if it gives the
   last chapter real pages and differs from the median estimate.
3. Otherwise the BIBLE positive-median estimate is used.
4. The estimate is capped at the last PDF page for PDF-page books, and at
   `page_count_images - (last_pdf - last_printed)` for printed books, so a
   negative offset (GUYTON-2026, ROBBINS-10) is handled instead of
   truncated.
5. A zero or negative last end is never kept.

A final stability pass produced 0 changes, so the files are settled.

## Evidence

```text
Ran 39 tests in 0.019s
OK
Queue: 37 applied; 0 blocked; 0 pending/stale
Final boundaries: 5 index/tail proved; 32 provisional (existing or median)
Image issues: 0; variable-offset books preserved: 13
```

Proved final pages (5): AVERY-2021 958, HARRISON-22 4000, HAZZARD-2022
3784, ROCKWOOD-10 3576, WILLIAMS-OBSTETRICS-26 3215.

Provisional medians capped at the last page (8): BRENNER-11,
GREEN-HAND-2021, GUYTON-2026, MANDELL-9, ROBBINS-10, ROSEN-2022,
SLEISENGER-11, WILLIAMS-ENDO-2024.

Independent checks: every internal end equals the next start minus one;
no last end below its start; no end above its cap; no zero-length last
chapter. Per-book receipts are in `TOC-REPAIR-STATUS.json`; originals are
in the gitignored `kitchen/logs/toc-repair-backups/<BOOK>/<timestamp>/`.

## What is NOT done (this is yours)

1. **Step A3 page_offset (section 4.6) is still open.** Only HARRISON-22
   has an offset (43). The other 36 records have `page_offset: null`.
   The 13 variable-offset books need per-province offsets or a human
   decision. This was explicitly outside the DeepSeek repair scope.
2. **Review the 32 provisional final pages.** Locator problems to fix
   first: the configured index is before the final opener in MANDELL-9,
   MIDDLETON-2019, MURRAY-7, ROSEN-2022; absent/invalid in CAMPBELL-2020
   and SABISTON-22; opening page unconfirmed in KRAUSE-16 and YOUMANS-4.
   The rest have no usable index. Treat them as provisional; do not call
   them verified or geography-done.
3. **Checkpoint 3.2 and statuses.** 36 books are `candidate`, only
   HARRISON-22 is `accepted`. No book is `geography-done`. A sanity check
   of the four rebuilt books (chapter list and province level) is worth
   one quick look before Step A3.
4. **Human reminder (standing):** Nir wanted to check that the other PDFs
   are the COMPLETE books. BOLOGNIA-2024 and BRAUNWALD-12 are now
   complete. Do not build him a table; just remind him once.
5. Do not start geography, registry, viewer or Phase B. No Freeze.

## Deviations and judgment calls (disclosed)

- Added `--rebuild` after Nir's explicit approval. It requires a named
  BOOK_ID and is refused for `--next` and `--audit`, so a full library
  rebuild cannot happen silently. Three tests cover it.
- The queue originally stopped ADAMS-12 to avoid flattening its six
  SECTION provinces; that guard was replaced by the in-place policy, and
  ADAMS-12 kept all 13 provinces including the empty heading.
- The 37-book run was committed in phase-sized commits rather than one
  commit per book. Per-book receipts are still in the status file.
- Two later full passes were needed: one to replace 22 zero-length last
  chapters with median estimates, and one to apply printed-page caps and
  re-record honest boundary modes. The final pass changed nothing.
- No local model (eyes) call was made. Only bounded single-page
  `pdftotext` checks, serially. No rendering, GPU, whole-PDF conversion,
  parallel or background jobs.

## Files and commits

- Code: `kitchen/toc_ranges.py`, `kitchen/toc_repair_source.py`,
  `kitchen/toc_repair.py`; tests in `kitchen/test_toc_repair.py`.
- State: `TOC-REPAIR-STATUS.json`, `PROGRESS.md`,
  `HANDOFF-TOC-REPAIR.md`, this file.
- Commits: `06da0e5` (first guard), `f055627` (in-place rule), `e248850`
  (ADAMS/AVERY receipts), `3954ccf` (33-book queue), `2477f8c` (four
  reviewed rebuilds). The final-pass commit is the one that contains this
  hand-off; check `git log --oneline -3`.

## Suggested first action

Read this file, `AGENTS.md`, `PROGRESS.md` and `TOC-REPAIR-STATUS.json`.
Then decide with Nir whether to start Step A3 page_offset (the next real
work) or first review the 32 provisional tails. Nothing else is pending
from the section 4.4 assignment.
