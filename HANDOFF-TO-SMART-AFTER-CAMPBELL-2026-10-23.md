# Hand-off to SMART after the Campbell repair (2026-10-23)

From: DeepSeek (executor)
To: GPT 6.1 Sol (SMART, project manager)
Read with: `PROGRESS.md`, `TOC-REPAIR-STATUS.json`, `AGENTS.md`, and
BIBLE Part 3 sections 4.2-4.6 plus Part 8.

## Bottom line

CAMPBELL-2020 is repaired. Its saved list had 82 chapters in four fake
volume groups; chapter 1 was wrongly "Total Ankle Arthroplasty" at page
14. It now has **90 chapters in 19 real Parts**, taken from the PDF's own
bookmark outline. Chapter 1 is **"Surgical Techniques"** at PDF 27;
chapter 90 is **"Sports Injuries of the Ankle"** at PDF 4990, ending at
PDF 5036. All 90 bookmark destinations were checked against each page's
own text: **90/90 passed**. No reader or model call was used.

The library is 37 books with **4,763 chapters** (was 4,755: Campbell
82 -> 90). 39 tests pass. `kitchen/books.json` was not changed.

Commit: `d5da35e`. The task handoff
`HANDOFF-TO-DEEPSEEK-CAMPBELL-2026-10-23.md` is now completed history.

## What was changed

- `kitchen/logs/CAMPBELL-2020-vis-toc.json` (source) rebuilt with 19
  Parts and 90 chapters; chapters marked `pdf-outline`.
- `kitchen/logs/CAMPBELL-2020-toc.json` (export) rebuilt with the same
  chapters and `pdf_page`; internal ends are next-start-minus-one.
- `TOC-REPAIR-STATUS.json`: only Campbell's receipt changed. Its mode is
  `verified-document-end`, note says the final page is document-end proof,
  not an index or printed-folio proof. `changed_ends`/`ends_total` = 90.
- `PROGRESS.md`: CURRENT PHASE, NEXT STEP, BLOCKED and the newest DONE
  entry.
- `kitchen/logs/CAMPBELL-2020-outline-evidence.json` (gitignored): the
  90 per-chapter page checks and the final-page proof.
- Backup of the old source, export, receipt and books.json:
  `kitchen/logs/toc-repair-backups/CAMPBELL-2020/20261023T191458756251/`.

No new repository code was added. The one-book rebuild script lived under
`/tmp/opencode/` and is not committed.

## Important limitation to keep visible

Campbell's page numbers are **PDF pages, not printed folios**. This
matches the project's existing convention for pdf-page books, and the
handoff approved it. **Printed-page mapping remains Step A3** and must
not be claimed as done. The final end (5036) is proved only as the end of
the provided document; it is deliberately counted as provisional by
`toc_repair.py --summary`.

## What is still open (next work)

1. **Physical check of the other rebuilt books.** These were rebuilt from
   saved contents without a physical-book check:
   - KRAUSE-16 (93 chapters)
   - MIDDLETON-2019 (99; pdf-page)
   - SABISTON-22 (92)
   Also worth a quick check because they were rebuilt from empty/stale
   exports: MANDELL-9 (210), MURRAY-7 (142), ROSEN-2022 (208),
   YOUMANS-4 (432).
   Use the Campbell recipe first: read the PDF's bookmark outline and
   check every chapter destination's text. It costs zero model calls.
   Only use the free Qwen eyes where bookmarks are absent or ambiguous.
   If a list is wrong, fix that book's source and export the same way,
   update its receipt, record evidence and stop after each book.
2. **Step A3 page_offset (section 4.6).** Still only HARRISON-22 has an
   offset (43). Thirty-six records are null; 13 books have variable
   offsets and need per-province offsets or a human decision. The
   pdf-page books do not need a printed offset until printed pages are
   required.
3. **32 provisional final boundaries.** Five are index/tail proved; one
   is Campbell's document-end proof; the rest are median estimates. They
   are honest placeholders, not verified physical ends.
4. **Checkpoint 3.2 and statuses.** 36 books are `candidate`, only
   HARRISON-22 is `accepted`. No `geography-done`, no Freeze.
5. Do not start geography, registry, viewer or Phase B. Do not edit the
   BIBLE. No Freeze.

## Recommended first action

Ask Nir whether to check the rebuilt books first or start Step A3. If he
chooses the checks, do them one book at a time, save and push after each,
and report. The Campbell method is the cheap template; do not spend SMART
tokens reading pages that a bookmark and its target text can settle.
