# TOC repair -- ONE switch to DeepSeek for the library

Generic-tool checkpoint: `4d378da`, committed and pushed to GitHub main.

## Assignment

Stay with DeepSeek for the entire common chapter-range repair queue.
Do not send Nir back to SMART for each book. The human explicitly asked
for a generic procedure covering at least the majority of the library.
The shared tool now has valid read-only repair plans for ALL 37 books.
Actual library application is your job; SMART has not applied those plans.
Harrison's earlier repair remains the only real-book apply pilot so far.

Work serially, one book per invocation, with Nir watching. Report and
save each book; if Nir pauses at a book boundary, resume with this SAME
model. The existing book-end stop rule does not mean changing models.
Source-specific failures go into one consolidated exceptions list, and
the next invocation moves on to the next book. Return to SMART ONCE at
the end for review of that list, rather than once per exception.

Governing text: BIBLE Part 3 sections 4.4 and 4.6, AMENDMENT 3.4 in
PROGRESS.md, and BIBLE Part 8. This assignment is section 4.4 range
repair, not a claim that Step A3 mapping or all geography is finished.

## Commands -- same for every book

Workdir: `/home/nir/second-opinion`. Read AGENTS.md and CURRENT PHASE /
NEXT STEP in PROGRESS.md. Check git status and tool versions as usual.

One initial read-only readiness check (opens NO PDFs and writes nothing):

```bash
PYTHONDONTWRITEBYTECODE=1 .venv/bin/python kitchen/toc_repair.py --audit
```

Expected at handoff: `37/37 books repairable; 0 blocked` for the range
calculation. This is a dry-run readiness result, not 37 completed books.

Then use this SAME command for each work unit:

```bash
PYTHONDONTWRITEBYTECODE=1 .venv/bin/python kitchen/toc_repair.py --next --check-index --apply
```

The script selects the next unprocessed book alphabetically, checks its
plan, backs up the original JSONs, applies its ranges, and records a
receipt in the small public `TOC-REPAIR-STATUS.json`. It processes at most
ONE book. It never writes books.json, accepts a book, or changes its field
name, frozen data, or status. Completed unchanged books get a receipt too.

A source-specific failure returns exit 1, leaves that book's outputs
unchanged, and records `blocked`. The NEXT invocation skips that book.
Do not try to rewrite scripts or rerun the reader to force it through.
Do not ask Nir to switch models. Continue the remaining queue in the same
DeepSeek session when the human continues. The blocked book remains part
of the library and is visible in the final review, not silently dropped.

Optional dry run of the next book: omit `--apply`. Optional explicit
book retry: replace `--next` with its BOOK_ID. Never reset the status file
to restart the whole library. Receipt hashes detect changed inputs/outputs;
unchanged completed books are skipped on resume.

After each book:

1. Give the short result: book, chapters, changed ends, final-boundary
   method, image repairs/issues, backup path. Keep the SAME model.
2. Append the exact command/output to PROGRESS.md, including whether
   the final end is provisional, and the selected accepted source.
3. Inspect git status/diff/recent log, stage only these intended reports:
   `git add PROGRESS.md TOC-REPAIR-STATUS.json`, commit with the book ID,
   and PUSH. Do not stage unrelated user changes or force-add local logs.
4. Honour the human's book-end pause; the same command resumes the queue
   without deciding a new procedure or changing models.

When the command says the queue is finished:

```bash
PYTHONDONTWRITEBYTECODE=1 .venv/bin/python kitchen/toc_repair.py --summary
```

Record this ONE consolidated report in PROGRESS.md, commit and push.
It lists applied/blocked/pending counts, provisional final boundaries,
image issues and variable-offset books. Return this handoff plus
TOC-REPAIR-STATUS.json to SMART once for the remaining review.

## What is generic now

- Chapter ends follow the next chapter across the WHOLE book, including
  province boundaries. Equal starts use the approved shared-page rule.
- Geography's page-range arithmetic does not depend on a constant PDF
  offset. All 13 variable-offset books pass the common range plan.
  Their accepted printed/PDF pairs stay unchanged. Do not run the old
  strict offset verifier and treat its expected variable-offset refusal
  as a failure of this independent range-repair step.
- The 27 books with complete saved eyes use those accepted observations;
  their exported chapter identities/starts/PDF pages must agree exactly.
- The ten books accepted without eyes use their accepted vis-toc files.
  No fake eyes are created and no accepted book is re-read. Eight legacy
  -toc exports have different chapter counts from those accepted sources;
  the tool restores the source chapter list and records both counts.
  This fixes stale/empty exports using already accepted contents, not a
  new reading or a decision to remove chapters from the accepted source.
- Printed and PDF citation units are kept separate. A PDF-page citation
  is not relabelled as a printed folio. No global offsets are invented.
- Province bounds and name provenance are preserved. Chapter starts,
  identities and order from the selected accepted source never change.
- A stale image link is corrected only with an existing picture and
  matching saved backward observation. Image issues are reported without
  holding unrelated chapter-range arithmetic hostage.

## Final chapter: verified when possible, explicit fallback otherwise

Internal chapter ends are exact arithmetic on accepted starts. The last
chapter has no next start, so its boundary is a separate task:

- `--check-index` uses at most THREE individual PDF-page text extractions,
  serially, each with a 20-second timeout. No full-PDF conversion.
- For PDF citations, a confirmed index opener gives the previous PDF page.
- For printed citations with uniform saved pairs, the verified index is
  converted using those pairs. No offset is saved to books.json.
- For changing/unknown offsets, two actual consecutive printed tail folios
  can prove the final end without extrapolating an offset through inserts.
- Missing, stale or unconfirmed index information uses the BIBLE's
  positive-median chapter-length fallback. Its receipt says
  `median-fallback` and explains why. It stays PROVISIONAL; do not call
  that physical chapter end verified, geography-done, or ready to Freeze.
  Continue the other common repairs; review unresolved tails together.

Metadata-only audit before handoff: 36 final boundaries need the optional
check/fallback; Harrison's existing matching index end is preserved. The
new tool's direct Harrison index check passed: 505 chapters, 0 end changes.
All 37 plan inspections were read-only; no generic repair receipts exist
yet. Do not report these checks as an applied library-wide repair.

## Proof, resources and persistence

31 regression tests passed in 0.015s, including absent eyes, stale legacy
exports, variable offsets, mixed units, preservation of accepted starts,
tail-folio proof, explicit fallback, backups, queue resume/skipped failures,
and new evidence invalidating a completed receipt. The old pilot tests pass.

The all-library metadata check found: 27 saved-eyes sources, 10 accepted
vis-toc sources, 13 variable-offset books, 8 legacy count mismatches,
2 further evidence-backed image-link repairs available (FIRESTEIN-12),
and 0 unresolved image issues. These repairs have NOT yet been applied.

Main scripts: `kitchen/toc_repair.py`, `kitchen/toc_repair_source.py`,
`kitchen/toc_ranges.py`. The stricter `toc_reexport.py` and `page_offset.py`
remain the historical offset pilot; use the generic queue above for this job.

Backups: `kitchen/logs/toc-repair-backups/<BOOK>/<timestamp>/`.
Run receipts: `TOC-REPAIR-STATUS.json` (committed, small metadata/hashes).
The receipts are an execution ledger, not a substitute for Neo4j. This
repair does not access Neo4j. PDFs/images/transcripts/local logs/.env stay
gitignored and are never force-added to the public repository.

No AI calls, rendering, GPU workloads, whole-PDF reads, parallel book jobs
or background jobs. Do not start geography, registry, viewer or Phase B.
BIBLE files stay untouched. State stays in this handoff and PROGRESS.md;
both AGENTS.md files contain only the short pointer.
