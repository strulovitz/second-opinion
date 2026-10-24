# Restart handoff -- Qwen index repair and overnight stop, 24 October 2026

From: GPT 6.1 Sol (SMART)
For: the next supervised session with Nir; DeepSeek executes book workflows,
SMART handles genuine software repairs.

## 1. Read this first: stopped for the night

Nir explicitly requested a detailed text handoff, a SHORT pointer in the
project `AGENTS.md`, a GitHub push, and then a stop until tomorrow.
This is a save-only checkpoint. No overnight job was started or scheduled.
Do not resume reading just because this file is opened. Explain the next
small step and wait for Nir's okay.

This handoff supersedes the failure/next-step claims in
`HANDOFF-TO-SMART-2026-10-24-HARRISON-INDEX.md` and the starting-state
instructions in `HANDOFF-2026-10-24-DEEPSEEK.md`. Those files are history.
The BIBLE still governs; nobody except Opus had permission to edit it.
Read `AGENTS.md`, `PROGRESS.md` (current pointers, newest DONE, BLOCKED),
`INDEX-PIPELINE.md` and the governing BIBLE additions/Part 3 section 7.

## 2. The result, with its exact scope

The SAME local model, **qwen3.8:27b**, successfully parsed the SAME Harrison
index page that previously failed: PDF 4044.

- Final live request: **84.555 seconds**, finish_reason=stop.
- 75 main entries; 112 flat subentries.
- All 278 original page-reference tokens retained; none missing or extra
  in a structural multiset comparison of this sample.
- Actual production grounding and assembly pass: 280 expanded numeric
  reference records; online-only=9, non-integer-or-malformed=1 (video
  suffix), outside-districts=0, mapping-unresolved=0.
- The exact successful Qwen response is cached by the production parser:
  **1/230 pages, incomplete**. Do not spend another call rereading it.
- **112 automated tests pass**. This is not a completed book or registry.

No classification or entity resolution has run. There is no approved
whole-book duration or permission for a full Harrison run. No other book
was started. The table-of-contents lane remains closed.

## 3. What Nir corrected and decided

SMART initially suggested a plain-code index parser. Nir rejected that:

> "i want you to make experiments with Qwen, this exact model, and find
> out what is wrong"
>
> "try to fix the problem not throw away our main tool."

Therefore keep Qwen as the reader and repair/test its existing workflow.
Do not revive the replacement-parser proposal as the next step. Nir can
relay questions to Google or another model if genuinely needed. None was
needed for this repair.

Other standing decisions: one book at a time, small supervised steps,
plain short explanations, wait for okay on new steps, no unattended jobs.
Qwen is never run across thousands of chapter pages. Measure reader jobs
on a tiny trial and show total HOURS before requesting a full run. There
is no numerical "27-hour hard limit" from Nir: that was an overstatement
in the previous handoff. His actual limits and approval process still apply.

Emojis belong in chat only. The handoff and code have no emojis. The
global memory file was not expanded; only the short project pointer changed.

## 4. The experiments: facts, not the old hypothesis

All three calls used the existing `kitchen/reader.py` helper, the exact
qwen3.8:27b model and cached PDF 4044 text. Each diagnostic allowed ONE
request, no automatic retry, and a 300-second request timeout.

### Experiment 1: original prompt and current reader settings

```bash
.venv/bin/python kitchen/index_diagnose.py HARRISON-22 --page 4044 --timeout 300
```

234.460 s total; 3,265 input tokens; 12,000 completion tokens;
finish_reason=length. Qwen returned 19,159 hidden reasoning characters
in the response's `reasoning` field and an unfinished JSON answer. The
old `/no_think` prompt tag did not prevent this on the actual request.

The 47 complete entries in that truncated prefix were examined ONLY as
diagnostic evidence, not accepted as a page. Exact grounding mismatch:
headword `Abacavir`, subentry
`DIHS. See also Drug-induced hypersensitivity syndrome (DIHS)`.
That string joins words across intervening source page references; it is
not a contiguous verbatim source phrase. The old standalone-letter-A
hypothesis was not established; Qwen's captured answer did not start with
an entry for A.

### Experiment 2: change only the per-request reasoning switch

Same command plus `--no-reasoning`, otherwise original prompt:
162.030 s; 3,267 input / 9,297 completion tokens; finish_reason=stop;
zero reasoning characters; 75 main entries and all 278 source references.

But Qwen nested two Abacavir subentries beneath `adverse effects of`.
The old checker accepted extra nested fields, while the assembler ignored
their children. That would silently lose SIX references: 419 twice,
428f once, 1603 twice and 1585 once. This was a format/validation mismatch,
not evidence that Qwen had copied those page numbers incorrectly.

### Experiment 3: clarify the required format, keep reasoning off

Same no-reasoning command, repaired prompt:
84.555 s; 3,416 input / 4,671 completion tokens; finish_reason=stop;
zero reasoning characters. Correct flat structure, all 278 reference
tokens retained, actual production grounding/assembly pass.

The prompt now requests compact JSON, which substantially reduces output
tokens. It explicitly requires flat, ordered parent/child subentries with
all children's references and contiguous verbatim labels, not appended
See-also targets or paraphrases.

## 5. Code changes in this checkpoint

- `kitchen/index_diagnose.py`: one bounded request, saves raw response
  before parsing, reports timings/token counts/finish reason/validation.
  Raw evidence stays ignored and local. It records neither environment
  contents, database credentials, headers nor the server URL.
- `kitchen/index_prompts.py`: clarified, compact, flat, verbatim PARSE
  output. Qwen still does the reading and interpretation.
- `kitchen/index_parse.py`: explicitly uses `no_reasoning=True` for INDEX
  PARSE only. New cache version binds the changed behaviour. Saves
  validation-rejected parsed answers under unique local filenames.
- `kitchen/index_pages.py`: rejects unhandled nested subentry fields
  rather than silently losing references; reports the exact bad phrase
  and parent. Also repairs a separately reproduced validator bug: a
  headword mentioned inside a previous subentry can no longer cut the
  previous entry's source block in half. Matches are line-start anchored.
- `kitchen/reader.py`: rejects finish_reason=length rather than accepting
  potentially incomplete extractable JSON.
- `kitchen/test_index_pipeline.py`, `kitchen/test_reader.py`: regression
  tests for the failures, cache/evidence retention and request-local flags.
- `INDEX-PIPELINE.md`, `PROGRESS.md`: repair evidence and restart steps.
- This handoff and the short project `AGENTS.md` pointer.

No .env/global model configuration changed. Other reader jobs retain
their previous reasoning settings; do not assume classification has been
measured or tuned. No BIBLE, map, viewer, chapter lists or book metadata
were edited. No software was installed and no paid external reader used.

Verification already completed after the code changes:

```bash
OPENBLAS_NUM_THREADS=2 .venv/bin/python -m unittest discover -s kitchen -p 'test_*.py'
# Ran 112 tests in 1.926s -- OK
git diff --check
# passed
```

Do not repeat the whole test suite or the successful Qwen call merely
because the session restarted. Rerun relevant checks after new changes.

## 6. Local evidence and persistent state

Repo `/home/nir/second-opinion`, GitHub `strulovitz/second-opinion`, main.
Starting HEAD before this repair: a464c7a. The commit adding this handoff
contains the repair, tests and docs together; inspect current git log and
remote tracking to confirm the save.

Full raw diagnostics (ignored, never pushed):

1. `kitchen/logs/HARRISON-22-index-diagnostic-4044-20261024T150407006980Z.json`
2. `kitchen/logs/HARRISON-22-index-diagnostic-4044-20261024T150851262203Z.json`
3. `kitchen/logs/HARRISON-22-index-diagnostic-4044-20261024T151351817100Z.json`

Normal successful caches:

- `kitchen/logs/HARRISON-22-index-4044.txt` and `-source.json` (old extraction).
- `kitchen/logs/HARRISON-22-index-4044.json` (repaired successful parse).
- `kitchen/logs/HARRISON-22-index-entries.json` (1/230 pages, 75 entries).
- `kitchen/logs/HARRISON-22-run.log` includes the successful parse summary.

The successful third response was replayed UNCHANGED through the real
`index_parse.parse()` function, verifying model/prompt/source text/input
identity/token budget/reasoning flag and rechecking source PDF/image/text
hashes. This saved the normal caches without another model call; no entry
JSON was hand-edited or invented.

Read-only restart inventory confirmed 70 classification terms after the
normal alias/deduplication handling of the 75 entries; there is NO
`HARRISON-22-classified.jsonl` yet.

DeepSeek previously loaded Neo4j geography: 37 books, 5,334 territories
(37 continents, 534 provinces, 4,763 districts), 5,297 child links and 37
book links. SMART made no database queries or writes during these trials.
Do not reload the geography as a warm-up. No entity population is claimed.

Zero-byte lock files are normal fcntl lock handles; their existence does
not imply a reader is running. Do not remove caches/locks blindly.

## 7. Tomorrow: exactly the next small step

1. Read the state above, check `git status --short` and recent commits.
   Explain that the first-page Qwen repair passed and its answer is cached.
2. Ask Nir for ONE timed classification batch of 25 terms from that cache.
   This has not been approved yet. Keep it foreground and bounded; the
   ordinary command is:

   ```bash
   time .venv/bin/python kitchen/index_classify.py HARRISON-22 --limit 1
   ```

   Check the available terminal timeout mechanism before execution. Use a
   five-minute bound for the trial, stop cleanly on timeout/error, and save
   evidence rather than repeatedly running it. No full pipeline command.
   Classification currently keeps its original reasoning behaviour.
3. Review the batch structure, exact term coverage and groups with Nir.
   If it fails, capture its exact response/error before changing settings;
   do not guess or loop. The existing diagnostic tool is PARSE-specific,
   not a ready-made classification diagnostic.
4. Show measured hours before any full-book request. At the measured
   first-page rate, parsing all 230 pages alone projects to about 5.4 h.
   A rough term-count extrapolation is 70 x 230 = 16,100 terms, about 644
   classification batches. Those are SAMPLE-based estimates, not actual
   book totals. Resolution time is ALSO unmeasured; do not promise a
   whole-workflow time from parsing/classification alone or assume zero
   resolution calls. Get Nir's approval to the actual proposed scope/time.
5. Harrison only. Review/approval comes before another book. No Phase B,
   Freeze, all-book run or overnight job is authorised by this checkpoint.

## 8. Important unresolved preflight for a LATER full pipeline

During save-only metadata inspection, the old 4044 extraction receipt's
key was compared with the key the CURRENT default `index_extract.py`
would compute (`layout=False`, `columns=False`, current Context identity).
They differ. The reason was not investigated or repaired tonight.

Consequently a future full `index_pipeline.py HARRISON-22` may stop with
"stale extraction for PDF 4044" before reaching Qwen. This is separate
from the repaired reader failure. Direct classification of the existing
successful parser cache does not run extraction and can be trialled first.

Before an approved full run, diagnose that receipt mismatch, preserve the
existing evidence, and agree a safe cache reconciliation/backup with Nir.
Do not delete the successful parse, hand-edit hashes, weaken provenance
checks or start a new TOC audit to get past it. The current page's actual
PDF/text/image identity checks passed in all reader trials and replay.

## 9. Saving and restart message

Push only the repair code/tests/docs and short pointer. Never push
`kitchen/logs/`, PDFs, images, transcripts, responses or .env. No global
memory expansion. Once the push is verified, stop until Nir returns.

Nir can paste tomorrow:

> Please read ~/second-opinion/HANDOFF-2026-10-24-QWEN-REPAIR.md and the
> current PROGRESS.md pointers. Keep qwen3.8:27b as our reader. The first
> Harrison index page is repaired and cached. Explain the next small
> classification trial and wait for my okay. One book at a time.
