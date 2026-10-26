# Second Opinion -- paused at Nir's request; November restart handoff

Written 26 October 2026. Repository: `/home/nir/second-opinion`.
GitHub: https://github.com/strulovitz/second-opinion

## 1. The latest human instruction wins

Nir said he cannot spend more money on AI this month. He asked for a detailed
description, a GitHub push, a link in AGENTS.md, and continuation next month.
**The project is PAUSED. Do not start a reader job, paid-model repair, scheduled
restart or another book until Nir returns and explicitly asks to continue.**

This handoff supersedes the restart commands and counts in
HANDOFF-2026-10-26-DEEPSEEK.md, the 25 October handoffs, INDEX-PIPELINE.md and
older PROGRESS.md entries. Keep those files as history. The BIBLE remains
read-only; human decisions and amendments are recorded in PROGRESS.md.

The actual book reader is still free, LOCAL `qwen3.8:27b` through Ollama and
kitchen/reader.py. The OpenCode operator is a separate model selected by Nir.
Nir switched from a free operator to a paid operator during today's run, then
requested this budget pause. Do not select a paid model or switch models for him.

## 2. Exact saved position, checked after stopping the process

| Item | Saved state |
| --- | --- |
| Current book / scope | HARRISON-22 index parsing, then classification only |
| Index pages extracted | 230/230, PDF 4044-4273 |
| Whole pages parsed and accepted | **54/230 (23.5%)**, PDF 4044-4097 inclusive |
| Whole pages still unfinished | **176**, including the partly read 4098 |
| Next unfinished PDF page | **4098** |
| Accepted pieces of page 4098 | **89/91**, consecutive pieces 1-89 |
| First piece still needed | **90/91**, then 91/91 and whole-page validation |
| Entries assembled from accepted pages | **3,262** |
| Classification terms in this accepted prefix | **3,044** |
| Previously saved, still-current classifications | **25** |
| Unclassified terms in this prefix | **3,019** |
| Whole-book term count | Unknown until all 230 pages parse |
| Assembly complete flag | `false` |

The last displayed chat summary said 53 pages. The interrupted command saved
4097 successfully, raising the accepted prefix to **54**, then read most of
4098. Therefore 53 pages / next 4097, and especially 49 pages / next 4093,
are obsolete restart positions.

Reference mapping counters in the current assembly:

```text
online-only=514
non-integer-or-malformed=24
outside-districts=0
mapping-unresolved=0
```

Do not combine these categories. `expand_reference()` treats a leading-letter
reference as online-only; other unsupported numeric forms go into
non-integer-or-malformed. The latter are recorded issues, not a claim that
every reference was mapped successfully. Earlier chat guesses that appendix
references explain the malformed counter were not established.

No new classification was run in today's continuation; the original 25
records remain unchanged and current. Entity resolution, registry review,
Neo4j ingestion, another book and Phase B were not run by this continuation.
This is intermediate index preparation, not a completed Harrison registry.

## 3. What was actually stopped

Nir interrupted the terminal call, but the parser process was still alive
when checked at 17:41 local (+02:00). It was stopped with SIGINT, and both
the parser and its timeout wrapper were confirmed gone. Their PIDs were
102140 and 102139, respectively; these are historical, NOT PIDs to kill later.

The last command was the following, in `/home/nir/second-opinion`:

```bash
timeout --signal=INT --kill-after=10s 900s .venv/bin/python -u kitchen/index_parse.py HARRISON-22 --limit 4
```

It had been wrapped with elapsed-time reporting and output redirected to
`/tmp/opencode/parse.log`. Its durable local copy is now
`kitchen/logs/HARRISON-22-pause-command-log-20261026.txt`.

This is a **human budget stop**, not a demonstrated new validation failure
on page 4098. An interrupted in-flight piece may have no saved completion;
do not invent its result. Piece 90 is not accepted. The assembly intentionally
excludes page 4098 until all its pieces and the whole page validate.

Ollama's model-serving process may remain resident. That is separate from
the stopped book job; no detached parser, monitoring loop or automatic
restart was created for this pause.

## 4. Today's work and the software now being saved

At the afternoon restart there were 9 accepted pages. The supervised run
added **45 accepted pages**, plus 89 accepted pieces of the next page.
Chunks of one, three and four new pages were used, with pauses for errors.

### Earlier GPT repairs, included in this GitHub save

- `kitchen/index_order.py`: physical left-to-right PDF column ordering from
  Poppler bbox geometry, separate from original extraction evidence. It
  rejects ambiguous columns and mismatched text inventories. The inventory
  comparison tolerates subscript/superscript whitespace and the documented
  discretionary line-hyphen difference, while preserving literal source text.
- `kitchen/reader.py`: opt-in JSON/schema constraints, request-local sampling
  controls and raw-response capture before JSON decoding. Other jobs retain
  their existing defaults.
- `kitchen/index_schema.py`: complete entry schema and explicit rejection of
  stray top-level fields, which previously could hide omitted entries.
- `kitchen/index_fragments.py`: whole-page failure fallback, one main-entry
  block per request, long entries split at complete reference runs (24-line
  target), checked CONTINUED merges, persistent plans and piece caches,
  and final full-page grounding/quotes.
- `kitchen/index_parse.py`: compatible revalidation of old v2/v3 caches,
  v4 input/control receipts, raw/rejected evidence, checkpoint assembly after
  every successful page and progress messages that distinguish partial resumes.
- `kitchen/index_pages.py`: missing/duplicate-reference census and literal
  matching of numeric ranges wrapped after ASCII/en/em dashes.
- `kitchen/index_classify.py`: saved/expected counts, command elapsed time and
  classification-stage ETA. `kitchen/index_diagnose.py`: bounded explicit
  schema/order/sampling/reasoning diagnostic controls.

### Further changes made by the operator during the continuation

These were made in response to actual rejected answers, not just proposed:

1. A superscript label prefix on a line by itself was mistaken for a page
   reference (4054). `wrapped_label_references()` excludes the observed
   deeper-indented label-continuation shape from the expected census.
2. Headwords wrapped after `/` failed literal matching (4054). Slash joins
   now have the same whitespace tolerance as dash joins, with original quotes
   retained.
3. Page fields containing See targets now produce a specific validation
   error. The census error includes extra-token samples as well as missing ones.
4. `canonical_subentry()` strips an appended See tail from a non-contiguous
   subentry label when its label and target both occur in the source block.
   This followed repeated failures on 4055; it is a structural normalization,
   not merely a better error message. Contiguous See-label text can remain.
5. `split_references()` expands comma-packed references into separate items,
   removes a terminal sentence period, and now removes a misplaced See tail
   when its target is present in the source block. All remaining reference
   items must pass the page-reference pattern and full census.
6. `split_text_references()` moves a trailing reference from subentry text
   into an otherwise empty pages list when the remaining label grounds.
7. Reference-shaped entry names were misread as page runs (4074). The census
   and planner now distinguish a labelled line from a comma-continued page
   run. The original 4074 plan and pieces 1-9 are preserved under
   `-stale-20261026.json`; its replanned pieces and whole page then passed.
8. Continuation/indentation validation now runs before grounding, so the
   retry receives the actual layout error. Feedback explicitly preserves an
   indented first subentry and supplies the printed label for a new main entry.
   This repaired failures on 4092 and 4093.

The last demonstrated failure before the pause was 4097: the reader put
references plus a See tail into page fields. The latest normalization and its
regression test were added; **4097 then completed successfully**. Page 4098
was subsequently interrupted by Nir's stop, not rejected by that old error.

### Review considerations for the returning operator

- The normalizers MODIFY a deep copy of the model answer before saving;
  raw original completions remain separate in the ignored logs. Do not say
  today's work changed only error text or left every rejection rule intact.
- The earlier strict rejection fixture for a subentry combining a label and
  See tail was changed to test normalization; rejection remains tested when
  the purported target is absent. A passing suite does not itself approve
  that policy or prove reference-to-subentry assignments medically correct.
- The new checks use block-wide text searches and layout heuristics. They
  have not received a separate SMART review since the operator added them.
  On return, inspect them offline before assuming they cover every later case.
  Keep original responses available for any review; do not silently broaden
  normalization or hand-edit medical entries to get a pass.
- These subsequent validator/planner edits retained the existing v4 FORMAT
  label. An offline pause audit confirmed all current complete-page plans
  and the partial 4098 plan agree with the current recipe, and all 54 saved
  pages revalidate without further normalization. Do not change recipe,
  model, prompt or keys casually; do not re-stamp stale caches.

## 5. Verification completed for this pause

```text
OPENBLAS_NUM_THREADS=2 .venv/bin/python -m unittest discover -s kitchen -p 'test_*.py'
149 tests passed, 2.365 seconds.
git diff --check: passed.
```

An independent OFFLINE pause audit then checked:

- 836 files from the earlier protected snapshot remain byte-identical,
  including all 230 original text/image/receipt sets, the original eight
  accepted page caches, classification data, BIBLE, geography/viewer/config
  and the base index prompts.
- The current PDF metadata and extraction/image hashes for all 230 sources.
- Input/model/order/control keys and grounding for all 54 accepted page caches.
- All 54 grounded results equal their saved entries; no extra normalization
  would change them. Assembly recomputation equals the saved assembly.
- Every accepted-page fragment plan matches the current recipe; partial
  page 4098's plan and its 89 saved piece keys/groundings also match.
- All 25 classifications still have current term/model/prompt keys.
- Zero reader/network requests and zero database queries during this audit.

Receipt: `kitchen/logs/HARRISON-22-pause-state-20261026.json`, audited
26 October at 15:45:40 UTC (17:45:40 local). The audit was subsequently rerun
to retain its helpers outside `/tmp`; the final receipt has its later clock.

Versions checked for the save: Python 3.13.5, git 2.47.3, GitHub CLI 2.97.0,
GNU timeout 9.7. Earlier reader environment: Debian 13, RTX 5090,
Ollama 0.32.14, local qwen3.8:27b. Do not assume those versions stay the same
next month. The runtime context was previously observed as 32768; the requested
65536 value through the OpenAI-compatible endpoint was not established effective.

No new reader/model or database job was run while preparing this pause save.

## 6. Where the data lives -- important for resuming

Public GitHub holds the handoffs, progress ledger, generic scripts and tests.
The PDFs, images, extracted book text, model answers and reading caches remain
**LOCAL and gitignored**. Pushing the handoff is not a cloud backup of the
private reading progress. Resume on this machine with those directories intact.

Relative to `/home/nir/second-opinion`:

```text
kitchen/books/                         Original local PDFs
kitchen/pages/HARRISON-22/             All 230 saved index images
kitchen/logs/HARRISON-22-index-entries.json
kitchen/logs/HARRISON-22-index-4044.json ... -4097.json
kitchen/logs/HARRISON-22-index-4098-fragments.json
kitchen/logs/HARRISON-22-index-4098-fragment-1.json ... -89.json
kitchen/logs/HARRISON-22-classified.jsonl
kitchen/logs/HARRISON-22-pause-state-20261026.json
kitchen/logs/HARRISON-22-pause-command-log-20261026.txt
kitchen/logs/HARRISON-22-pause-audit-20261026.py
kitchen/logs/HARRISON-22-pause-progress-20261026.py
```

Other evidence remains alongside them: source receipts/text, ordered/bbox
receipts, timestamped raw completions and rejected answers, earlier repair
snapshots/verification receipts and archived fragment trials. Do not delete
those directories, repeat extraction or reconstruct accepted outputs manually.
Private configuration stays private; do not display credentials or upload .env.

The preserved `pause-progress-20261026.py` helper is read-only, makes no reader
request, and computes classification key validity from the actual configured
reader model. It avoids depending on temporary `/tmp/opencode` files surviving
until November. The old repair verifier that asserts exactly nine accepted
pages is historical and must not be run as if it described today's prefix.

## 7. Time so far and honest remaining-time estimate

Today's afternoon resume clock was **14:59:11 +02:00**. The job was explicitly
stopped around **17:41 +02:00**: roughly **2 hours 42 minutes wall time**,
including model switches, discussion, debugging and pauses. This is not a
measurement of pure reader time. A reliable full sum of all command runtimes
was not retained; do not fabricate it or AI billing/token costs.

Three recent entirely fresh, successful chunks took 330, 405 and 384 seconds
for three pages each (4081-4089). Combined: 1119/9 = 124.3 seconds/page.
That sample would imply about **6.1 hours parsing** for 176 unfinished pages.
Slower chunks and fallbacks also occurred; **6-9 hours parsing** is a rough
planning range, not a guarantee. The nearly completed 4098 costs less than a
fresh page and must not be extrapolated as one.

Classification has only the old **51.220 seconds / 25 terms** measurement.
If the current prefix density, 3044/54 terms per page, continued across all
230 pages, the book would have roughly 13,000 terms. Subtracting 25 already
saved gives approximately 518 batches, or **7.4 hours classification**.
This is a density extrapolation, NOT a census; classification-context changes,
retries and later-page density can change it.

Thus a rough remaining parse+classify planning estimate is **13.5-16.5 hours**
under those sample assumptions, before new pauses/debugging. It does not
include matching/database/registry review, which remain separately unmeasured.
Remeasure a small fresh chunk on return and report the combined stages, not
just the parser's stage-only ETA. No work is scheduled during the budget pause.

## 8. Restart next month -- only after Nir says continue

1. Read AGENTS.md, the governing BIBLE additions/Part 3 sections 7-9, this
   file and the newest PROGRESS.md. Check current files/versions and that
   no book-stage process is already running. Recognize that this save included
   the previously uncommitted repairs and historical handoffs.
2. Check local progress without generating:

   ```bash
   .venv/bin/python kitchen/logs/HARRISON-22-pause-progress-20261026.py
   ```

   Expected saved prefix: 54/230, 3262 entries, 3044 current terms,
   25 valid saved classifications, 3019 pending-prefix terms. Check 4098's
   manifest and pieces 1-89 exist. If local data differs, inspect and explain;
   do not overwrite it from this document.
3. Explain the saved position and timing uncertainty to Nir briefly. Respect
   his chosen operator/model and budget. Inspect the new normalization helpers
   offline; if a substantive uncertainty remains, report it instead of more
   unapproved repair work. Do not rerun warm-ups, cloud-reader comparisons,
   successful parse trials or the classification trial as a restart ritual.
4. After Nir's explicit resume instruction, finish the partial next page with
   ONE supervised foreground invocation, using tool workdir
   `/home/nir/second-opinion` and tool timeout at least 930000 milliseconds:

   ```bash
   time timeout --signal=INT --kill-after=10s 900s .venv/bin/python -u kitchen/index_parse.py HARRISON-22 --limit 1
   ```

   The existing script checks/reuses 4044-4097 without model calls, reuses
   4098 pieces 1-89, then requests 90 onward. On success expect 55/230 and
   next fresh PDF 4099. Do not call this partial-page duration a fresh-page
   timing sample.
5. Continue the already defined parse scope in visible foreground chunks,
   usually `--limit 3` or `--limit 4` under the same timeout. Measure fresh
   pages, update the hours estimate and tell Nir if materially slower. Show
   pages done/left, wall elapsed, command runtime, parse time left,
   classification time left and their sum. Never launch a detached job or
   silently continue after a genuine error or human stop. A tool interruption
   may leave a process alive: explicitly check/stop that exact process.
6. Only after `parsed_pages=230` and `complete=True`, classify in supervised
   chunks (the limit here means batches of up to 25 terms):

   ```bash
   time timeout --signal=INT --kill-after=10s 900s .venv/bin/python -u kitchen/index_classify.py HARRISON-22 --limit 5
   ```

   Preserve/reuse all current saved keys; do not assume 3019 is the full-book
   pending count. Update exact totals after full parsing, and measure the
   actual batch pace rather than relying indefinitely on the old trial.
7. STOP after classification and report. Matching, database resolution,
   registry approval, another book and Phase B require their own next steps.
   Do not run the unrestricted pipeline. Do not edit the BIBLE, approved
   geography/viewer, book identities or closed TOCs.

## 9. GitHub save

Nir explicitly authorized this commit and push. It includes this handoff,
restart pointers, accumulated public ledger/handoffs and the generic parser/
reader/progress fixes and their tests. Source PDFs, extracted text, images,
responses, caches and private configuration remain excluded.

Stable handoff URL:
https://github.com/strulovitz/second-opinion/blob/main/HANDOFF-2026-10-26-PAUSED-UNTIL-NOVEMBER.md

That link is also in AGENTS.md. No calendar action or automatic next-month
restart is implied: Nir returns, chooses the model, and says continue.
