# Restart prompt for GPT 6.1 Sol -- generic programming, not book execution

## Current handoff -- A6 software delivered

Geography was approved and exported in a816e30. The A6 index-to-Neo4j
machinery is implemented and tested in 41fbd27. Read INDEX-PIPELINE.md and
the newest PROGRESS.md pointers. NEXT is DeepSeek/free-reader execution,
Harrison first, with its registry review before later books. Older geography
programming and contents-checking assignments below are historical.

## Latest direction -- geography, not the old book queue

After cf9fd27 Nir explicitly cancelled further contents work and told SMART
to build the project. Follow the newest PROGRESS.md pointers: BIBLE Part 3
section 6 geography programming. The book-checking queue below and in the
DeepSeek runbook is historical and must not be restarted.

## Programming delivered -- 23 Oct 2026

The generic assignment below is implemented and tested. Read the latest
PROGRESS.md entry and DEEPSEEK-TOC-RUNBOOK.md. NEXT: DeepSeek executes the
per-book work with Nir watching. Do not repeat this programming assignment
or restart SMART's cancelled book investigations. The text below preserves
the assignment and cost boundary for reference.

## Read this first: Nir's latest instruction overrides earlier handoffs

You are the SMART programmer for Second Opinion, not the book operator.
Nir stopped the latest session because SMART was starting another book
review instead of doing the reusable programming. His exact instruction:

> processes that are book by book need to be done by deepseek. processes
> that are the heavy lifting of GENERIC programming need to be done by you.

He also requested this detailed restart prompt and a reference to it from
AGENTS.md, rather than more material in memory. Do not inflate AGENTS.md
or global memory. Keep detailed state in this file and PROGRESS.md.

Nir is paying per token and explicitly demands economy. Do the work with
short updates. Do not expose long internal deliberations, reread the whole
repository repeatedly, or spend the session proposing work without doing
it. Do not turn the next task into another book investigation.

## Immediate assignment after restart

Build the missing GENERIC software needed to finish the current BIBLE
stage, then give DeepSeek ONE usable procedure for the remaining per-book
work. SMART writes and tests the reusable machinery. DeepSeek operates it
on books, uses the free reader when needed, records results, and saves/pushes.

Do not ask Nir to switch back to SMART for every book. Common variations
must be handled by the same tools. Collect genuine unresolved cases for
one consolidated review; a book boundary is not a model-switch boundary.

Do not ask which book SMART should check next. That is DeepSeek's work.
If inspecting existing evidence is necessary to understand its format,
read a small saved sample. Do not reopen PDFs to search for another issue.

## Start economically

1. Read this file, project AGENTS.md, and only the current pointers,
   unanswered questions and relevant newest evidence in PROGRESS.md.
2. Inspect git status and recent commits before touching files. User work
   must not be overwritten. The last session started clean at `6de5b6d`.
   This restart-document checkpoint will be newer.
3. Read the governing BIBLE sections: Part 3 sections 0.5, 4.2-4.7;
   Part 8 sections 4 and 6. The BIBLE is authoritative and never edited.
   All 14 BIBLE files were already read by SMART in this conversation;
   a fresh session needs the governing sections, not another full reread.
4. Inspect the existing scripts listed below, identify their missing
   generic capabilities, and implement those. Reuse working code.
5. Run focused regression tests and one small proof of the new machinery.
   The default proof should use synthetic fixtures or saved evidence,
   not start another physical-book audit. Part 8 section 6.4 permits a
   one-unit programmer pilot; it does not authorise a library execution.
6. Commit/push the completed programming and write the DeepSeek operating
   handoff with exact working commands, resumption and exception handling.
   End there and report briefly to Nir.

## Current project stage and what the BIBLE actually requires

Repository: `/home/nir/second-opinion`, GitHub `strulovitz/second-opinion`,
branch `main`. There are 37 books, not 42 (AMENDMENT 3.3 in PROGRESS.md).

We are in Part 3 Phase A, the TOC/page-mapping work around A2-A3.
Part 3 section 4.2 defines chapters and innermost heading-level provinces.
Section 4.4 defines range arithmetic; section 4.6 defines printed/PDF
mapping; section 4.7 contains Checkpoint 3.2.

In particular:
- Preserve verbatim chapter titles and the real Part/Section hierarchy.
- Internal end = next chapter start minus one, with the human-approved
  shared-page rule: max(current start, next start minus one).
- Province bounds are derived from their children.
- The final end is the page before the index when known. The BIBLE
  explicitly permits a median-length estimate when it is unknown.
  Label that estimate honestly; do not invent a requirement for perfect
  physical verification of every final page before declaring arithmetic
  complete. Do not present an estimate as a verified page.
- Step A3 needs actual evidence for printed-to-PDF mapping. Four spread
  samples must agree before a uniform offset is saved; check against all
  available accepted pairs, not just a majority. Disagreements require
  the documented per-range/per-province approach or the human's decision.
- Checkpoint 3.2 gives Nir a short summary and warnings; approval is his.

Nir's latest routing instruction assigns book execution to DeepSeek and
generic software to SMART. Do not let an old handoff's suggestion to
"ask which book" restart the expensive model-switch loop.

## Facts already established -- do not re-investigate them here

- The generic internal-range repair was applied to all 37 exports.
  SMART's read-only review found matching receipt/file hashes and correct
  internal arithmetic. These checks do not prove every input list correct.
- The inherited regression suite passed 39 tests. No new programming or
  book edits were made in the latest, interrupted SMART session; it only
  read the handoff, ledger, instructions and governing BIBLE section.
- The repair receipts live in root `TOC-REPAIR-STATUS.json`. Its `applied`
  state records execution, not a physical-book certification.
- Only HARRISON-22 currently has `page_offset` configured (43).
  The other 36 records are null. Thirteen saved-evidence books have
  variable offsets. A PDF-page citation is not a verified printed folio,
  and a numeric zero offset must not be invented to make a report pass.
- Books.json has 36 `candidate` records and one `accepted` (Harrison).
  Field names/acceptance and Checkpoint 3.2 must follow recorded human
  decisions. Do not promote everything just because a script ran.
- No geography/registry load or Freeze was performed in this work.

### Campbell is repaired -- use its result, do not redo the book

DeepSeek repaired CAMPBELL-2020 in `d5da35e`; the subsequent handoff is
`6de5b6d`. Its earlier 82-chapter/four-volume list was wrong. The actual
PDF bookmarks supply 90 chapters under 19 Parts. DeepSeek checked all
90 destination pages by text, without AI calls.

Chapter 1 is Surgical Techniques at PDF 27. Chapter 90 is Sports Injuries
of the Ankle at PDF 4990; the last PDF page 5036 still names chapter 90.
The repaired source and export use PDF-page units. Printed mapping
remains separate. The library now has 4,763 exported chapter entries.

The final receipt mode is `verified-document-end`, explicitly distinct
from an index or printed-folio proof. The existing summary conservatively
counts Campbell among its 32 provisional cases: 5 index proofs, 1 Campbell
document-end proof, 31 median estimates. Correct reporting should keep
these categories distinct without recomputing all books.

Campbell evidence and backups are in local, gitignored kitchen/logs;
the paths are in PROGRESS.md. Its one-off rebuild script was temporary,
not a committed general-purpose implementation. That is a reason to build
reusable tooling, not to repeat its physical audit with paid tokens.

### Remaining execution is DeepSeek's queue, not SMART's next assignment

The latest handoff lists physical checks of KRAUSE-16 (93 current entries),
MIDDLETON-2019 (99) and SABISTON-22 (92). It also suggests checking the
rebuilt-from-empty/stale exports MANDELL-9 (210), MURRAY-7 (142),
ROSEN-2022 (208), YOUMANS-4 (432). These counts are current saved counts,
not independent guarantees of completeness.

DeepSeek should handle the necessary per-book checks/corrections with the
generic tools. Preserve the accepted eyes work and avoid reopening all
already-confirmed books merely because the tools have improved.

## Generic programming that is needed next

First assess the existing code; implement missing capabilities rather
than rewrite the project. The reusable TOC validation/correction and A3
mapping path must handle the common evidence types consistently:

1. **Authoritative input and provenance.** Distinguish chapter contents,
   PDF chapter bookmarks, saved reader evidence, technique lists,
   chapter-internal outlines, and online-only listings. Agreement of two
   generated JSON files is not independent proof. Evidence should say
   what was checked and what remains uncertain.
2. **Common bookmark formats.** Support both "Chapter N: Title" and
   number-plus-title forms, with real parent depth/heading membership.
   Recognise the innermost heading above chapters. Do not hardcode
   Campbell's 90 chapters or 19 Parts as universal requirements.
3. **Cheap target verification.** Open a PDF once, work on the selected
   pages, reuse cached results keyed to the PDF/evidence identity, and
   print concise progress. Campbell's repeated per-page pdftotext
   launches timed out; one-open pypdf checks worked for DeepSeek.
   Its text split CHAPTER into a drop-cap C and HAPTER. Handle extraction
   spacing robustly while still matching the exact chapter number/title
   (chapter 1 must not match chapter 10 just by prefix).
4. **Units and mapping.** Keep PDF destinations, printed folios and
   e-pages distinct. Never trust PDF page labels without checking them:
   Campbell's label for its chapter-1 opener disagreed with the page.
   Preserve accepted printed/PDF pairs; use the free local reader for
   ambiguous pages. Do not invent a constant mapping through inserts.
5. **Safe minimal changes.** Range-only repairs preserve chapter starts,
   names and grouping. A physically supported list repair may replace a
   stale source/export together with backups and a clear before/after
   report. Do not flatten existing Sections into Parts as an incidental
   side effect. Do not silently reuse a folio cache built for a bad list.
6. **Final boundaries.** Separate index proof, adjacent-folio proof,
   document-end evidence and median estimates. In a variable-offset book,
   extrapolating the last opener's offset to the file's end is still an
   estimate. Also note that inclusive start=end is ONE page, not zero;
   its validity needs evidence, not an automatic rejection rule.
7. **Resumption and truthful receipts.** One book per execution unit,
   dry-run/apply, backups, atomic writes, input checks, durable proof,
   and an exception summary. Preserve meaningful history and backup
   references on retries. Counts of repeated assignments are not counts
   of distinct physically verified corrections. Avoid automatic repeated
   full-library passes that overwrite evidence without improving it.
8. **A3 output.** Produce a supported uniform offset or a clear proposed
   range mapping, plus unresolved cases. Respect BIBLE section 4.6 and
   its human decision for irregular mappings. Do not add or change the
   Neo4j schema to solve a local TOC problem.

Regression tests should target real failure modes above, using small
fixtures. Do not mirror the implementation or keep broadening tests
after the relevant checks pass. Do not claim tests alone certify books.

## Existing files to inspect selectively

- `kitchen/toc_repair.py`: queue, apply/backup, receipts and summary.
- `kitchen/toc_repair_source.py`: source choice, units, final boundary.
- `kitchen/toc_ranges.py`: internal/province range arithmetic.
- `kitchen/page_offset.py`: saved-pair verification and four sample checks.
- `kitchen/toc_outline.py`: PDF bookmark walking and older matching.
- `kitchen/toc_links.py`: PDF contents links and target checking.
- `kitchen/eyes_folio.py`: saved opener evidence and free-reader workflow.
- Existing test files and `kitchen/reader.py` as needed. Do not expose .env.

## Completion of this SMART assignment

Deliver working generic code, focused test evidence, and one detailed
DeepSeek runbook covering the remaining common per-book work. The runbook
must name real working commands, explain units, resumption, backups,
success criteria and unresolved cases. Do not hand over half-written code
or promise flags that were never implemented/tested. No demand for 37
switches to SMART and back.

Save the programming and handoff to GitHub in sensible checkpoints.
Update PROGRESS.md accurately and keep the AGENTS.md pointer short.
Chat only needs the result, test summary, commit and handoff link.

## Subsequent BIBLE order, once the current data/checkpoint is approved

A2/A3 precede A4/A5. SMART's later generic work is Part 3 sections 5-6
(reader helper/geography scripts), then section 7 (index pipeline) and
the loading/verification tools of section 8. DeepSeek runs the per-book
and batch execution; the free reader does page/term work; Nir approves
the checkpoints. Freeze A follows the required checkpoints, not just a
TOC repair. Parts 4-9 are later phases; do not start them as a substitute
for completing the current stage.

## Operational limits and communication

Use simple, short chat replies with emojis; no emojis in committed files.
Check tool versions before use. No unattended reader runs, GPU workloads,
whole-PDF conversions, installations, service changes or parallel book
jobs for this programming session. No subagents unless Nir asks.
PDFs, images, full-page transcripts, local logs and secrets remain ignored.
Keep BIBLE and unrelated user changes untouched. No force-add or force-push.

The latest user request is this restart document and short pointer ONLY.
After saving it, stop. The new SMART session starts the generic programming
assignment above; it does not resume the cancelled KRAUSE book inspection.
