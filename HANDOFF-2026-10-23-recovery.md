# Second Opinion -- crash recovery, 23 Oct 2026

Read this first, then PROGRESS.md and BIBLE Part 3 sections 4.4-4.7 and
Part 8 section 6. This supersedes the next-step text in the evening handoff.

## Current checkpoint

The previous session's work survived locally but was not committed:
the new `kitchen/page_offset.py`, seven regression tests, Harrison's
approved acceptance/field name and saved page_offset=43, and the ledger.
Rechecked on recovery: 7 tests pass; Harrison has 505/505 consistent saved
page pairs, 2 stale image references and 21 range warnings. The exporter
repair has NOT yet been applied at this checkpoint.

GitHub main was checked through gh: same HEAD as the laptop, e20cdb3.
The full BIBLE has now been read (all nine parts and all appendix files).

## Human instructions and decision

Nir asked for frequent commits AND pushes and a short AGENTS.md pointer
to detailed memory, not more detail inside AGENTS.md. Save after each
completed checkpoint. One book at a time; stop and report after each book.
No unattended runs. The PDF-completeness reminder was given this session.
No cause of the previous computer freeze has been established.

Asked about ch45/ch46 both beginning on printed page 291, Nir selected
"Yes, please continue" to letting both ranges include the page, fixing
the exporter, checking Harrison only and writing a DeepSeek handoff.
This is AMENDMENT 3.4 in PROGRESS.md; the BIBLE itself stays untouched.

## SMART's next action

Repair `eyes_folio.write_toc_json()`: compute ends across the WHOLE book,
not independently inside each province; permit equal starts; finish the
last chapter at the verified index boundary or the BIBLE's recorded median
fallback. Verify the configured Harrison index start before using it.

Repair stale selected image filenames after `refine_opener()` moves the
chosen PDF page (Harrison ch103 and ch448); use saved evidence only.
Add a no-reader, one-book re-export route using existing eyes records.
Preserve an on-disk backup before changing the gitignored evidence/output.
Prove the fix on HARRISON-22 only, then commit/push and write the exact
CHEAP-tier procedure. Do not start geography, registry, viewer or Phase B.

## Library state

37 books, not 42 (AMENDMENT 3.3). TOC opener readings are complete:
27 checked by the eyes; 10 previously accepted without those eyes runs.
The evening handoff has the historical counts and three recorded findings.
The newly found exporter defect does not undo the accepted opener readings.
Only Harrison has the new offset-verifier pilot in this session so far.
Its status is still accepted, not geography-done.

`kitchen/logs/`, PDFs, page images, transcripts and .env stay gitignored;
never force-add them. Scripts, tests, configuration and reports go to GitHub.
The detailed saved TOCs and eyes evidence remain on this laptop.
