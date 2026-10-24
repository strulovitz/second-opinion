# DeepSeek handoff: index pages to the entity registry

## 24 Oct SMART repair: Qwen first-page trial now passes

Nir explicitly required keeping the SAME `qwen3.8:27b` reader and repairing
the existing workflow. Three bounded experiments and their exact local
evidence paths are in the newest PROGRESS.md DONE entry. Final Harrison
PDF 4044 trial: 84.555 seconds, 75 main entries, 112 flat subentries, all
278 original page-reference tokens retained. The actual production parser
has cached that exact successful Qwen response: 1/230 pages, incomplete.
Geography was already loaded by DeepSeek; do not repeat that step.

`index_parse.py` now requests compact verbatim flat JSON and disables hidden
reasoning for index parsing only. Other reader jobs keep their existing
settings. Rejected parsed answers are saved locally, nested fields are
rejected rather than silently losing references, and length-truncated
responses are errors. No model/global configuration was changed.

Next, WITH Nir's okay, time ONE classification batch using the cached page:

```bash
time .venv/bin/python kitchen/index_classify.py HARRISON-22 --limit 1
```

Classify time is still unknown. The measured first-page parsing rate alone
projects to about 5.4 hours for 230 pages; it is not a full-workflow estimate.
Show Nir measured total hours before any full book run. Current repair work
does not authorise that run or another book. A repeat parse with `--limit 1`
means one NEW page, not another call on the successful cached page.

For a bounded diagnostic ONLY when needed (not a routine rerun):

```bash
.venv/bin/python kitchen/index_diagnose.py HARRISON-22 --page 4044 --timeout 300 --no-reasoning
```

This makes one Qwen request and saves its full raw response locally. It
does not populate normal parse caches or touch Neo4j. Omit --no-reasoning
only for an explicitly agreed comparison experiment. The older readiness
and trial status statements below describe the pre-repair checkpoint.

LATEST GEOMETRY: Amendment 3.5 replaced the rectangles with one whole
honeycomb tile per chapter. Nir approved its displayed appearance on 23 Oct;
the canonical manifest records it. Read HANDOFF-2026-10-23-NIGHT-DEEPSEEK.md
first: he paused for sleep, and the completed implementation was subsequently
pushed to GitHub as 726d5c4. Next is the supervised reader/index trial.
Chapter/territory IDs, hierarchy and page bounds are unchanged.

## Current assignment and boundaries

The A6 generic software is delivered in programming checkpoint `41fbd27`.
The 88-test suite passes. The actual Neo4j server accepted the production
geography and entity/proving-page transaction plans using EXPLAIN (no writes).
One real index page, Harrison PDF 4044, was extracted as the programmer pilot.
The free reader had no model loaded, so the live-reader trial is still to do.
Synthetic parsing/classification/resolution tests are not a claim that a real
book's index has been processed. Neo4j still contains only three Meta nodes.

DeepSeek now handles the long execution, with the FREE reader doing all page
reading, term classification and synonym decisions. Stay with DeepSeek across
books and review iterations. Nir supervises. Run in a visible foreground
terminal; do not start unattended jobs, parallel books or chat-polling loops.
Existing completed chapter lists and the approved geography are read-only
inputs. The old contents-checking queue is cancelled.

Read AGENTS.md, the newest PROGRESS.md pointers, BIBLE Part 3 sections 7-9,
and this file. Commands below run from `/home/nir/second-opinion`.

## 1. Start with the bounded real-reader trial

Check git status/recent commits. Check Python, pdftotext, pdftoppm and the
configured reader are available. The installed versions checked by SMART are
in PROGRESS.md. The book reader is **Qwen `qwen3.8:27b` on this laptop's
existing Ollama server**, not another paid chat. DeepSeek can load/test it
for Nir using the existing BIBLE helper, with Nir watching:

```bash
.venv/bin/python kitchen/reader.py
```

This loads the already-installed model on demand if needed, and should print
`{'ok': True}`. GPU startup can take time. No model download or separate AI
conversation is needed. If it fails, preserve the exact error and diagnose
before starting an index batch. Do not change the model/server configuration
or install anything. Never print .env, passwords or tokens. Scripts use
reader.py and db.run. SMART did not run this reader test during viewer work.

Metadata-only readiness (no model or database access):

```bash
.venv/bin/python kitchen/index_pipeline.py HARRISON-22 --plan --limit 1
.venv/bin/python kitchen/load_geography.py
```

Harrison's configured index is PDF 4044-4273 (230 pages); its geometry has
505 districts. The 170-page figure in the BIBLE was an estimate, not a cap.
PDF 4044's text and source-image receipt already exist from the pilot.

After the free reader is loaded, test ONE page and ONE classification batch:

```bash
.venv/bin/python kitchen/index_parse.py HARRISON-22 --limit 1
.venv/bin/python kitchen/index_classify.py HARRISON-22 --limit 1
```

`--limit 1` means one NEW page or one NEW batch (25 terms for classification),
not that already-cached work is requested again. Examine the page and saved
reader output with Nir: it must be a back-of-book index, preserve main versus
subentries and actual page refs, and keep a continuation attached to its parent.
The free reader interprets the terms; the manager checks structure/provenance.
Parsing has two validation attempts. Record a persistent failure with source
and error instead of inventing replacement entries.

## 2. Put the approved map into Neo4j before entity resolution

BIBLE 3.7.7 MATCHes existing district nodes. The 3.8.1 geography loader is
therefore a database dependency before the resolve stage can make lit spots.
It is included as a ready script; the approved seating/texture already exists.
Loading it is not a new approval or a Freeze, and is not the whole A7 review.

```bash
.venv/bin/python kitchen/load_geography.py --apply
```

This uses one Neo4j transaction through db.run, creates the approved Book/
Territory/CHILD_OF/REPRESENTS data and prints the counts. It preserves an
already completed book's status on a repeat load, refuses conflicting existing
territory identity/bounds and refuses a frozen/missing schema. No source lists
or books.json are edited. Expected geometry: 37 books, 5,334 territories
(37 continents + 534 provinces + 4,763 districts). Save actual query counts.

## 3. Run Harrison, then show its registry review

Once the bounded trial is satisfactory and geography is loaded:

```bash
.venv/bin/python kitchen/index_pipeline.py HARRISON-22
.venv/bin/python kitchen/review_sample.py HARRISON-22
```

The pipeline runs extract -> parse -> classify -> resolve, one book only.
It reuses the pilot page/batch. Progress appears in the terminal; stage
summaries also append to `kitchen/logs/HARRISON-22-run.log`. The job can be
stopped and resumed. Keep the long work with DeepSeek/free reader, not SMART.
Use `--stop-after parse` or `--stop-after classify` to stage without resolving.
Resolution requires complete source parsing, current classifications and
supported printed-page references; it never writes from partial term context.

The review is `kitchen/logs/HARRISON-22-review.md`: counts, twenty sampled
terms per group, aliases and top districts, twenty not-an-entity terms, group
conflicts, doubtful merges and slug collisions. Show this to Nir. The seating
approval does NOT approve this new registry review.

ONLY after Nir approves that review (Checkpoint 3.5), record his actual words:

```bash
.venv/bin/python kitchen/review_sample.py HARRISON-22 --approve "ok"
```

Use "ok" here only if that is what Nir said. Also record the decision/commands/
raw counts in PROGRESS.md, commit/push the intended public records and report.
Local page text, reader answers, source images and index caches stay ignored.
Pause for Nir's instruction after the book. Do not switch back to SMART merely
because Harrison or another book ended.

## 4. Remaining books: same tools, alphabetical order

After Harrison's review, continue accepted books alphabetically. Each prior
book's current registry review must be approved before the next starts.
For the first remaining book, for example:

```bash
BOOK=ADAMS-12
.venv/bin/python kitchen/index_pipeline.py "$BOOK" --plan
.venv/bin/python kitchen/index_pipeline.py "$BOOK"
.venv/bin/python kitchen/review_sample.py "$BOOK"
```

For each new index, do a bounded reader-page/batch trial before its full run.
The default text extraction follows reading order. If the actual index sample
needs column preservation, use `--layout` or `--columns` (left then right).
Choose the extraction format before parsing; changing it invalidates old
source caches. Do not hand-edit guessed JSON to make validation pass.

Metadata inspection found 25 usable index ranges and 12 unset/invalid ranges.
An unset locator is NOT proof of no index. Use the free reader to locate/check
the real back-of-book index, and record an index locator correction with a
backup where needed. This is index work, not another chapter-list audit.

### Explicit fallback for a confirmed unusable index (BIBLE 3.7.9)

Only after confirming that the index is genuinely unusable, use the existing
chapter titles and saved opener targets as the BIBLE's thinner registry source:

```bash
.venv/bin/python kitchen/index_fallback.py "$BOOK" --fallback --limit 1
.venv/bin/python kitchen/index_classify.py "$BOOK" --fallback --limit 1
.venv/bin/python kitchen/index_pipeline.py "$BOOK" --fallback
.venv/bin/python kitchen/review_sample.py "$BOOK" --fallback
```

Keep `--fallback` for all stages and the later review approval. The fallback
reads only the already recorded opener pages, through the free reader, for
verbatim terms. It preserves title/opener provenance, labels itself a THIN
registry and stores page-derived spots as source=page, not a fictitious index.
It does not verify, rebuild or rewrite chapter lists. A missing existing
opener or unreadable printed folio remains unresolved, never a guessed number.
Reader results/cache reuse are identity-bound just like the index route.

## 5. What the machinery does automatically

- Keeps exact source blocks, source index image and original reference strings.
- Merges a first CONTINUED entry with the preceding page's main entry.
- Strips t/f/b page suffixes; expands shortened/full numeric ranges; ranges
  over thirty pages keep endpoints only. Online/e-page/malformed refs are
  kept in counts, not reinterpreted as integer printed folios.
- Maps printed refs to all matching districts, including shared pages. For
  PDF-unit district bounds it uses actual configured uniform/per-range offsets.
  An unknown mapping is an explicit unresolved count and stops resolution.
- Sends batches of twenty-five terms with subentry/district context to P-A4b.
  LAW 7's chronic/test-finding/measured-abnormality disease rule takes priority.
- Automatically merges only exact same-group names/aliases. Full-text and
  rapidfuzz results are candidates, not permission to merge. P-A4c decides;
  SAME below 0.6 creates a separate entity and a doubtful-merges record.
- Preserves the first canonical name, uses separate same-group slugs where
  needed, records group conflicts and slug collisions, and adds See aliases
  only to unique existing targets. Unresolved See targets retry later.
- Uses Neo4j Entity/Symptom/Disease/Treatment and DISCUSSED_IN data. A6 can
  create entities; Phase B quarantine applies later after registry freezing.
- Leaves a human-directed classification/group correction explicit. It refuses
  to silently replace already stored relationships with a different group.

## 6. Resume, evidence and costs

Rerun the SAME stage/command. Caches identify PDF/configuration, extraction
mode, prompts and models. Unchanged pages/terms do not call the reader again.
Atomic cache/JSONL writes and a saved pre-transaction resolution decision allow
recovery after a stop, including between DB commit and completion receipt.
Completion is checked against actual database entities/links, not just a local
"done" flag. Global registry and per-book locks prevent concurrent writers.

An identity mismatch stops rather than mixing evidence. Preserve/archive the
affected book's index state under kitchen/logs before an intentional source,
mode, prompt or model change. Do not remove accepted chapter/map inputs.
No-op retries are expected; repeated assignments are not distinct discoveries.

All generated cache/review/reader files are under kitchen/logs. Use actual
Neo4j counts in the ledger; an index-status JSON is an execution receipt, not
the entity registry. Never mark a book complete with unresolved page mapping.
Use existing accepted printed/PDF evidence where available; an unknown
page_offset is not zero. Do not start a new contents verification queue.

## 7. Exact return to SMART

Remain on DeepSeek for page/batch execution, index-location bookkeeping,
review iterations and subsequent books. A book boundary is not a model switch.
Return a reproducible generic software failure after two attempts with the
exact command, source/cache identity and full error. Collect related genuine
exceptions for one review; do not spend paid-model time reading every page.

After all registry reviews (Checkpoint 3.6), return to SMART for the BIBLE's
entity-resolution/Freeze review with counts, unresolved See targets, doubtful
merges, group conflicts, slug collisions and any printed-mapping gaps. No
Freeze, schema change, altitude assignment or reading-pipeline launch is
implied by an A6 script completing.
