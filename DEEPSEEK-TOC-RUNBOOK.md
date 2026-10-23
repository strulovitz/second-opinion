# DeepSeek operating handoff: TOC evidence, corrections and A3 mapping

SUPERSEDED AFTER cf9fd27: Nir explicitly cancelled the repeated contents
checks and instructed SMART to build the project. Do not execute the book
queue in this historical runbook. Read the latest PROGRESS.md pointers;
the active work is BIBLE Part 3 section 6 geography programming.

## 1. Assignment and cost boundary

Read AGENTS.md, the CURRENT PHASE/NEXT STEP/questions in PROGRESS.md, BIBLE
Part 3 sections 4.2-4.7 and Part 8 sections 4 and 6. The generic software
was written by GPT 6.1 Sol; the programming checkpoint is `1cd08c0`.
The final handoff commit also closes the explicit-new-pairs evidence loophole.
The final regression result is recorded in PROGRESS.md.

DeepSeek owns the book-by-book work for this whole stage. The free local
reader owns page transcription and ambiguous page/folio recognition. Stay
with DeepSeek between books; do not request a SMART switch at each book.
Nir watches execution. After each book, record evidence, save/push, report
briefly and STOP for his instruction. No unattended loops or parallel books.
Collect genuine exceptions for one consolidated review, rather than asking
SMART to repeat the physical book investigations.

Current queue, from the preceding handoff:

1. KRAUSE-16 (93 current exported chapters).
2. MIDDLETON-2019 (99), then SABISTON-22 (92).
3. Check the earlier rebuilt exports MANDELL-9 (210), MURRAY-7 (142),
   ROSEN-2022 (208), YOUMANS-4 (432), if still necessary after reviewing
   their saved evidence.

These are saved counts, not guarantees of completeness. CAMPBELL-2020 is
already repaired: 90 chapters under 19 Parts. Do not redo it. Preserve the
27 eyes-verified books and the ten previously accepted books; improved
software is not a reason to reopen all 37. A2 list-checking and A3 folio
mapping are separate jobs. No Neo4j load or geography execution is authorised
by a successful TOC command.

## 2. Start once; run commands from /home/nir/second-opinion

```bash
git status --short
git log --oneline -3
.venv/bin/python --version
.venv/bin/python -c "import pypdf; print('pypdf', pypdf.__version__)"
pdftotext -v
pdftoppm -v
```

Preserve unfamiliar changes. Do not print .env or credentials. The last
SMART check found Python 3.13.5, pypdf 6.20.1 and pdftotext 25.03.0.
Check pdftoppm before the first actual selected-page reader job. The free
reader must be started by Nir; do not launch a GPU job or change services
without his instruction. All reader calls go through kitchen/reader.py.

Select ONE book:

```bash
BOOK=KRAUSE-16
.venv/bin/python kitchen/toc_repair.py "$BOOK"
```

This last command is a range/source-consistency dry run. It does not prove
that an inherited list came from the correct contents page. Do not repeat
`--audit` or `--next --apply` over the library merely to refresh receipts.

## 3. Choose real chapter evidence

First use saved evidence and the PDF's chapter contents/bookmarks. Determine
whether the input is actual chapters, a list of techniques, an internal
chapter outline or online-only material. Two generated JSON files agreeing
is not independent proof. Compare completeness/grouping with the real
contents using the FREE reader where necessary, not paid manual page work.

### A. PDF chapter bookmarks

```bash
.venv/bin/python kitchen/toc_book.py "$BOOK" --outline --proposal --cache
```

This opens the PDF once and extracts selected target pages only. It accepts
both `Chapter 1: Title` and `1 Title`, including dotted numbers, keeps true
bookmark ancestry, and uses the innermost parent heading as province.
Numbered descendants of a chapter and excluded listings are not chapters.
PDF destinations are PDF pages, not printed folios; labels are never proof.

`--proposal` explicitly saves kitchen/logs/BOOK-toc-proposal.json, even if
some target text is ambiguous. `--cache` explicitly saves selected-page
text; it is keyed to PDF stat identity and source/evidence identity. Without
these options, dry runs do not write drafts/caches. Neither option changes
the source, export, books.json or repair receipt.

The command prints concise progress, confirmed/ambiguous targets, page units
and before/after counts. All matched bookmark targets still do not prove that
the bookmarks include every chapter. A technique list with plausible target
pages must not replace the chapter contents.

### B. Existing list already correct; only check its targets/ranges

```bash
.venv/bin/python kitchen/toc_book.py "$BOOK" --cache
```

This requires actual PDF targets in the existing export. A missing PDF target
is an unresolved mapping task, not permission to treat a printed number as a
PDF page. The default path preserves source names/grouping and accepted eyes.
Do not use `--outline` simply to rewrite a correct hierarchy.

### C. Saved reader/contents correction

When bookmarks are absent, ambiguous in scope or incomplete, prepare ONE
local input under kitchen/logs from the real contents/free reader. Its shape:

```json
{
  "book_id": "BOOK-ID",
  "kind": "chapter-contents",
  "pdf_identity": {"...": "exact object returned by pdf_identity()"},
  "unit": "pdf-page",
  "source_pages": [5, 6],
  "provinces": [
    {"name": "SECTION I Foundations", "part_name": "PART I Basics",
     "chapters": [
       {"number": "1", "title": "Exact printed title", "page_start": 27, "pdf_page": 27}
     ]}
  ]
}
```

This is a schema illustration; include the actual complete checked list,
not just the one sample row. `kind` is `chapter-contents` or `saved-reader`.
`source_pages` are the physical PDF contents pages, not generated JSON.
Use meaningful numbered headings exactly as the book/human's grouping
decision requires; preserve name_source for human-authored groups.

Obtain the exact local PDF identity with this generic command:

```bash
.venv/bin/python -c 'import json,sys; from pathlib import Path; sys.path.insert(0,"kitchen"); from toc_evidence import pdf_identity; b=next(b for b in json.loads(Path("kitchen/books.json").read_text()) if b["book_id"]==sys.argv[1]); print(json.dumps(pdf_identity(Path("kitchen/books")/b["pdf_file"]),indent=2))' "$BOOK"
```

DeepSeek may assemble this envelope from the saved free-reader output; it
must not invent titles, parents, chapter targets or printed folios. Reuse
existing reader tools/prompts to read the failing contents portion, as
BIBLE 4.4 prescribes. Do not hand-edit an unproved list to silence validation.

```bash
.venv/bin/python kitchen/toc_book.py "$BOOK" --source "kitchen/logs/$BOOK-checked-contents.json" --cache
```

With `unit=printed`, page_start is an actual printed integer folio and
pdf_page is the separate destination; the tool also requires readable corner
folio or a PDF-bound saved free-reader observation. E-pages such as 4536.e5
must not be truncated to integers. Use PDF-unit citations until a supported
printed mapping is established. Never sort away a printed-number restart.

A flat bookmark list reuses an existing matching human-authored grouping.
If it does not match, the tool stops for the human's grouping decision;
the draft is available. Do not manufacture Parts or flatten Sections.

## 4. Resolve only ambiguous targets with the free reader

For a listed ambiguous chapter, use its proposed PDF target. For example,
substitute the actual chapter number and target instead of these sample values:

```bash
.venv/bin/python kitchen/toc_observe.py "$BOOK" --number 1 --pdf-page 27 --source "kitchen/logs/$BOOK-toc-proposal.json"
```

For an existing unchanged TOC omit `--source`. For a contents correction use
its checked-contents file. If numbers restart, add `--province "EXACT NAME"`.
The tool renders ONE page and calls the FREE reader through reader.py.
The reader must report an actual chapter opening and the complete number/title;
a running header alone is insufficient. Folio NONE stays unknown.

It saves BOOK-checked-pairs.json, including opener_evidence, raw answer,
image SHA-256 and PDF/list identity. Images are stored in a PDF-identity-keyed
subdirectory of eyes-render/BOOK. The same saved observation is reused on
retry without another model call. `--refresh` explicitly obtains a new
observation and retains the previous answer in history. A changed PDF/list
requires archiving the previous checked-pairs file first; never reuse it blindly.

Then retry the SAME candidate/list with the observations:

```bash
.venv/bin/python kitchen/toc_book.py "$BOOK" --outline --observations "kitchen/logs/$BOOK-checked-pairs.json" --cache
```

For contents input replace `--outline` with `--source ...`. Alternatively,
include the helper's opener_evidence in the checked-contents envelope.
After two failed reader attempts on a portion, record the raw evidence and
question for Nir. Stay in DeepSeek for common work; collect genuine generic
software failures for one SMART review.

## 5. Apply only the supported correction; then refresh ONE range receipt

Repeat the successful dry-run command with `--apply`. For example:

```bash
.venv/bin/python kitchen/toc_book.py "$BOOK" --outline --apply --cache
.venv/bin/python kitchen/toc_repair.py "$BOOK"
.venv/bin/python kitchen/toc_repair.py "$BOOK" --apply
```

Retain `--observations ...` or `--source ...` if used in the successful check.
Do not drop them from the apply command. A source/list correction saves both
vis-toc and toc, plus BOOK-toc-proof.json, after checking inputs again.
Stale eyes/folio caches are archived in the transaction backup before removal
from their active paths. Their accepted printed/PDF observations are preserved
in that backup; compatible pairs can be carried into checked-pairs input
instead of rereading them. Never discard a disagreeing accepted pair just
because four newer samples agree.

The existing range tool preserves starts, titles and grouping; it calculates
internal ends as max(start, next_start - 1), then province bounds. It does not
certify a physically unverified list. Do not use `--rebuild` as a substitute
for chapter evidence. Receipts record execution, not human acceptance.

Final boundaries remain distinct:

- `--check-index` requests bounded physical checks of the configured index.
- `--document-end` on toc_book checks that the last PDF page still names the
  final chapter; it is allowed only for PDF-unit citations, not printed extrapolation.
- Otherwise the BIBLE's median estimate is allowed and labelled honestly.
- Inclusive start=end is one page. Do not reject it merely for equality.
- A variable-offset last-opener extrapolation is an estimate, not tail proof.

The proof binds verified boundaries to the source/export hashes and local
PDF identity so the range refresh can preserve them without another audit.
Do not ask for perfect final-page proof when the BIBLE permits an estimate.

## 6. A3: printed-to-PDF mapping, separately

First use accepted saved pairs:

```bash
.venv/bin/python kitchen/page_mapping.py "$BOOK" --report
```

The tool checks every supplied/inherited accepted pair, not a majority. For a
uniform mapping it requires the first/25%/50%/75% chapters, all available
accepted offsets agreeing, and current-PDF sample checks. A PDF-unit eyes row
does not imply a printed folio; only an actual saved folio observation counts.

For missing pairs, read only the needed sample openers with toc_observe.py,
using the current TOC (omit --source). Then:

```bash
.venv/bin/python kitchen/page_mapping.py "$BOOK" --pairs "kitchen/logs/$BOOK-checked-pairs.json" --report --cache
```

The explicit pair file is merged with active legacy eyes evidence. Conflicting
accepted pairs cannot silently replace each other; an unsampled old offset
disagreement still prevents a uniform save. Archived evidence from a corrected
list must be checked for compatible chapter identity/targets before carrying
it forward. Do not relabel a stale observation as new evidence.

Exit 0 means verified uniform mapping. Exit 2 means a human-review proposal;
exit 1 means invalid/missing evidence or a refused save. A proposal in
BOOK-mapping-proposal.json lists accepted pairs, missing samples, observed
constant-offset segments and unresolved transitions. `from_image` is the
first OBSERVED image in that segment, not a proved exact transition. Numbering
inserts between samples and the unsampled tail remain unproved.

For a verified uniform mapping and an already accepted book:

```bash
.venv/bin/python kitchen/page_mapping.py "$BOOK" --pairs "kitchen/logs/$BOOK-checked-pairs.json" --save
```

Omit --pairs if using only inherited eyes. This backs up and atomically saves
only that book's page_offset and a local mapping proof. Other fields/statuses
are preserved. A candidate book cannot be promoted here. Existing conflicting
offsets or page_offsets require Nir's decision. Do not write zero for unknown
printed mapping. Negative offsets are valid when supported by actual pairs.

For variable offsets, show Nir the four samples, observed ranges and transition
uncertainty. BIBLE 4.6 assigns the choice of majority-with-errors versus
per-range offsets to HIM. Record his exact decision before changing config.
The software deliberately does not install unapproved page_offsets proposals.
Collect these book questions in one review; do not switch to SMART per book.

## 7. Backups, interrupted runs and retries

New tools use kitchen/logs/toc-tool-backups/BOOK/TIMESTAMP/. Each changed bundle
has originals and transaction.json. Individual replacements are atomic; the
journal covers a crash between source/export/evidence/config replacements.
Ordinary write errors roll back automatically. If a process was killed and
a transaction is still `applying`, the next apply stops with this command:

```bash
.venv/bin/python kitchen/toc_store.py "kitchen/logs/toc-tool-backups/BOOK/TIMESTAMP" --recover
```

Use the EXACT path reported, then repeat the one-book dry run. Recovery refuses
to overwrite files edited since the interruption. Keep meaningful history and
backup paths. Range-tool legacy backups remain under toc-repair-backups.
No-op new-tool retries create no additional backup. Do not remove a backup
just to make a summary appear clean.

## 8. Per-book report, commit and pause

Checkpoint 3.2 needs: book ID, provinces, chapters, first/last printed page
(or explicitly UNKNOWN with PDF-unit bounds shown), page_offset/mapping
state, and warnings. An estimate, observed range proposal, target check and
human approval are four different things. Do not call them interchangeable.

Append a DONE entry in PROGRESS.md with exact commands/raw output, units,
source/proof/backup paths, changes and remaining questions. Record human
acceptance/field_name/checkpoint decisions explicitly. No automatic
geography-done promotion, database load, schema change, seating or Freeze.

Inspect git status/diff and stage only intended public records/config changes.
Logs, PDFs, images, page transcripts, proofs with reader answers and secrets
stay ignored. Commit/push one completed book using the existing part.section
message style. Report briefly to Nir and wait for the next book instruction.

Use `toc_repair.py --summary` for a consolidated metadata report when useful;
do not reapply all books. It separates index/tail proof, document-end proof
and estimates, and preserves earlier receipts/backups on explicit retries.
Only rerun the 58-test software suite if code changed or a failure warrants it;
passing software tests do not certify a book.
