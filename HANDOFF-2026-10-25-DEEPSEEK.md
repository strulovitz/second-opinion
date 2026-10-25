# DeepSeek restart handoff -- 25 October 2026

From: GPT 6.1 Sol (SMART), at Nir's explicit request.
For: DeepSeek, including a free Flash variant if Nir chooses it, operating
the existing scripts with the free local Qwen reader and Nir watching.
Repository: `/home/nir/second-opinion`, GitHub `strulovitz/second-opinion`.

## Latest update: free-cloud trial, 25 October 2026

Read PROGRESS.md's newest CURRENT PHASE / NEXT STEP and DONE FIRST. Nir then
asked for a free cloud model to be tested as a drop-in reader, without changing
scripts. The identical saved Qwen page request, changing only the model in the
JSON body, was sent once to free DeepSeek Flash (OpenCode cloud) and once to
free Gemma 4 31B (OpenRouter). BOTH returned HTTP 429 usage/rate-limit errors;
neither returned an answer. Scripts and six production cache/evidence files
were unchanged. No Qwen rerun, classification or full-book job occurred.

STOP and report that blocker; ask Nir whether to retry a selected free route
later or continue Qwen. Do not automatically run section 5 below, loop retries,
switch production models, or choose a paid route. Earlier "next classification"
instructions below describe the workflow BEFORE this new comparison request.
The comparison is not a model-quality result. Details/error evidence paths and
the authenticated OpenRouter transport limitation are in the newest DONE.

## 1. Read this first

The globe is approved. Both software blockers encountered on Harrison's first
index page are repaired. That page and its successful Qwen answer are saved.
The NEXT task is just ONE classification batch of 25 terms from that cache,
timed and bounded, after explaining it and getting Nir's okay.

Do not execute the older Opus instructions from the beginning. Their FULL
original text is copied verbatim in section 11 because Nir requested it.
Section 3 explains which steps have already happened and which are still due.
The BIBLE and its Opus ADDITION blocks still govern; this handoff records
execution history and the repaired software, not changes to the BIBLE.

Read: project `AGENTS.md`, BIBLE Part 8 ADDITION and the other ADDITION blocks
it names, Part 3 sections 7-9, PROGRESS.md's current pointers/newest DONE,
then this handoff. Do not consume all the old logs or repeat completed work.

Nir cannot read a long screen or scroll up in OpenCode on Linux. Keep chat
answers SHORT, simple and friendly, with emojis in CHAT ONLY. Explain one
small step, wait for his okay, perform it, then report briefly. Detailed
evidence belongs in files. No emojis in files or commits.

## 2. What the work actually is; who does it

We are building the list of medical terms that will later power the globe.
The book's back-of-book index supplies terms and the pages that mention them.
This is Phase A, index-to-registry work (A6), not reading every chapter.

The existing scripts:
1. Extract index text and retain source-page evidence.
2. Ask Qwen to turn each index page into structured entries.
3. Ask Qwen to classify main terms as symptom/sign, disease/condition,
   treatment/drug, or not-an-entity. The last category is an exclusion
   decision, not a fourth entity group.
4. Match terms against existing same-group entities, using the reader for
   ambiguous synonym decisions; keep aliases and provenance; store real
   registry data in Neo4j through the supplied scripts.
5. Produce a review sample for Nir. Stop after the book for his review.

Roles:
- DeepSeek is the operator: explain, run the existing commands, time them,
  check structure/counts, record evidence, stop at errors and human checkpoints.
- The FREE LOCAL reader is the SAME `qwen3.8:27b`, through `kitchen/reader.py`.
  It does the actual page reading, medical classification and ambiguous matches.
- GPT 6.1 Sol / another Nir-chosen SMART model writes or repairs generic
  software and performs the later specialist reviews.

A less capable DeepSeek Flash can do this operator job if it follows the
written commands and stops rather than improvising. It must not take over
Qwen's per-page/per-term work in the cloud. The selected model's current price
is whatever OpenCode/provider shows; this handoff does not verify free pricing.
Use short operator messages, not repeated paid narration or chat polling.

## 3. Current state: corrections to the historical Opus instructions

As of this handoff:
- 37 books; TOC lane finished; Harrison has 505 chapters. Do not reopen TOCs
  or the closed question of PDF completeness.
- Approved Goldberg globe: 4,812 tiles = 4,763 chapter hexagons + 37 book-name
  tiles + 12 pentagon lakes. Approved viewer: Sand table / Atlas and flower map.
- Geography was ALREADY loaded by DeepSeek on 24 Oct: 37 books, 5,334
  territories, 5,297 child links, 37 book links. Do not reload it as a warm-up.
  SMART made no new database queries during either repair; this is the last
  reported load, not a new assertion from a fresh database check.
- Harrison index: PDF pages 4044-4273, 230 pages total.
- PDF 4044 was already extracted and successfully parsed. Cache: 1/230 pages,
  incomplete, 75 main entries, 112 flat subentries, 278 original reference
  tokens retained. Assembly expands these to 280 numeric reference records;
  online-only=9, non-integer-or-malformed=1, outside-districts=0,
  mapping-unresolved=0. These are structural counts, not a full-book review.
- The existing page yields 70 classification terms after normal alias and
  deduplication handling. No classification has run; no classified.jsonl existed
  at the last check. No entity-resolution/full-book execution is claimed.

How to read the Opus steps copied in section 11:
- Step 1 (starting-point check): still appropriate. Section 7 lists the five
  intended checkpoint files; verify normal status/tracking on restart.
- Step 2 (reader test): previously passed. Do not spend another reader call
  merely to restart. The approved classification trial will use the reader.
- Step 3 (read-only plan): checked after this repair. Can be used if genuinely
  needed; do not repeat it or the test suite as a ritual.
- Step 4 (geography load): ALREADY DONE. Do not repeat it.
- Step 5 (one-page parse): ALREADY DONE. Next is the classification batch ONLY.
  `index_parse.py --limit 1` means one NEW page, not rereading the saved page.
- Step 5b (hours estimate): STILL REQUIRED, with the corrections in section 6.
- Step 6 (full Harrison run/review): NOT YET AUTHORISED. Requires a satisfactory
  trial and Nir's explicit approval of the proposed scope and measured hours.
- Step 7 (GitHub save): Nir requested backing up this repair/handoff checkpoint.
  Verify remote tracking on restart; do not repeat a completed save.
- Step 8 (return to SMART): applies; the later phase boundary is detailed in
  section 9. A completed single book is not automatically a model switch.

## 4. What SMART repaired, and why the saved evidence is safe

### 4.1 Qwen parser repair on 24 Oct (already committed as c65b80d)

The same Qwen model failed the original first-page trial. Three bounded
experiments found hidden reasoning exhausting the token limit, ambiguous
format instructions, unhandled nested subentries, and a headword-boundary
validator defect. The repair:
- Uses a compact, flat, verbatim parse prompt and disables hidden reasoning
  for INDEX PARSING requests only.
- Rejects truncated responses and unexpected nesting instead of losing data.
- Saves rejected parsed responses locally for diagnosis.
- Fixes the source-block headword-boundary validator.

Final actual live request: 84.555 seconds, finish_reason=stop, all 278 source
reference tokens retained. The EXACT successful response was replayed through
the production parser, with source checks, without another Qwen call. It is
cached and must not be thrown away. Classification still has its original
reasoning settings; its speed and success are unmeasured.

Details and raw diagnostic paths: `HANDOFF-2026-10-24-QWEN-REPAIR.md`.
Nir expressly rejected replacing Qwen as the main tool. Do not revive that
replacement proposal or change the model/settings yourself.

### 4.2 Extraction-key repair on 25 Oct (included in this checkpoint)

DeepSeek correctly found that extraction would stop before reaching Qwen:
`ValueError: stale extraction for PDF 4044; archive the old index cache, do not mix sources`.

Cause: an extracted TEXT page was keyed to the entire map's coordinates and
appearance. Approved map rebuilds changed that key although the PDF/text/image
had not changed. SMART independently reproduced the old key exactly using the
saved pre-honeycomb geography; the current map produced the different key.

Only production file changed for this repair: `kitchen/index_extract.py`.
- New receipts use `index-extract-v2`: PDF local identity, PDF page, layout and
  columns flags, and the existing pdftotext recipe marker; no globe coordinates.
- Old receipt keys are NOT edited or silently reinterpreted.
- A generic, explicit one-page reconciliation path verifies the original key
  against the saved old geography plus the current book/PDF/page/flags/recipe,
  and checks the text, image and page/image-path evidence.
- It writes a SEPARATE proof bound to the old receipt and new extraction key:
  `kitchen/logs/HARRISON-22-index-4044-source-check.json`.
- No source receipt, text, image, saved Qwen parse or assembled entries changed.
  No new extraction, Qwen call, database operation or map/viewer edit was needed.

Already executed through `index_extract.main([...])` inside the before/after
verification probe (DO NOT rerun as a restart step):
```bash
.venv/bin/python kitchen/index_extract.py HARRISON-22 --reconcile-page 4044 --previous-geography kitchen/logs/before-honeycomb-20261023T201406461287Z/export-geography/geography.json
```

Verified:
- Production extraction-cache validator now accepts PDF 4044.
- Local PDF identity, text and image checks pass.
- SHA256 values of all five original files match before/after.
- Successful Qwen parse key remains valid; assembled entries identity is current.
- Metadata-only pipeline plan passes; 117 tests pass (2.087 s); diff check passes.
- Five new synthetic regression tests cover map changes, exact historical-key
  proof, cache preservation, altered evidence/flags and invalid CLI combinations.

The PDF identity is the project's existing LOCAL stat/path identity, not a new
whole-PDF cryptographic hash. It remains deliberately strict. Moving/copying
the PDF may still require investigation. `pdftotext-v1` is the recipe marker,
not a newly measured claim about the old executable's exact version.

Only extraction identity changed. Context/parser/classification/review approval
identities remain strict. A FUTURE map rebuild may still invalidate downstream
caches under their existing policy; do not promise universal map-independent
cache reuse. Today's saved parse already uses the approved current map, so it
does not need migration. Do not change execution_guard or approval hashes.

Preserved SHA256 values (also in PROGRESS.md):
```text
HARRISON-22-index-4044-source.json 0e9862a898d31fd26daaa645fc84847265ac8eda92b0ae98456b5251c1f79c60
HARRISON-22-index-4044.txt 777019139e9fdc37542ad89e91ec122d578681e69b3ed43b95c07dd1e68f1e32
HARRISON-22-index-4044.json ff5442eeed8b6ab45454f5a0175f1c34dcaf1bd9a56510da59f9d62c496e60d7
HARRISON-22-index-entries.json 35be2c4157334258658c6048e3f3b626de2716878e96b58f0a7d31bd39b12df4
page-4044.png ecde66d1f6f5037c961c38a5607ee2168f8043da4b6a260d2ca943292e56c89f
```

## 5. Exact next step: one classification batch, not a book run

All commands below are from `/home/nir/second-opinion`.

1. Check `git status --short` and recent commits. Recognise the intended local
   changes in section 7; do not discard or overwrite them.
2. Tell Nir briefly: "The first index page is saved. Now Qwen will sort just
   25 terms into the groups. I will time it and stop after that batch. Okay?"
3. WAIT for his okay. Reading this handoff is not reader-job approval.
4. Check that the terminal can enforce a five-minute bound. The ordinary
   stage command is:
   ```bash
   time .venv/bin/python kitchen/index_classify.py HARRISON-22 --limit 1
   ```
   If GNU timeout is available (check `timeout --version` first), use:
   ```bash
   time timeout --signal=INT --kill-after=10s 300s .venv/bin/python kitchen/index_classify.py HARRISON-22 --limit 1
   ```
   Give the enclosing terminal tool at least 330000 ms so it does not kill the
   wrapper early. Keep this foreground. A timeout is a STOP, not permission to
   run it repeatedly or alter reader settings. Preserve the actual exit/error.
5. Report real elapsed seconds, whether model startup was included, saved row
   count, exact term coverage and valid groups. Check STRUCTURE, not medical
   interpretation by the manager. Do not paste all 25 records into chat.
6. On success: show Nir a small structural summary, record commands/time/counts
   in PROGRESS.md, and compute the estimates in section 6. Do not start the
   rest of the book without the separate approval described there.
7. On failure: stop and record the exact command, duration, error and evidence
   paths. If no raw response was captured, say so. The existing
   `index_diagnose.py` is PARSE-specific; do not use it as a classification
   diagnostic or invent a response. Request SMART help when needed (section 9).

`--limit 1` is one NEW batch of up to 25 terms; it is not the whole cached
70-term sample. Existing scripts may retry a validation failure internally,
but the external five-minute trial bound still applies. Do not add retries.

## 6. Time estimate: facts, formulas and unknowns

What is actually measured:
- The successful Harrison first index-page parse: 84.555 seconds.
- 1/230 index pages parsed. 229 remain.
- That sample produces 70 classification terms, not 75 terms after filtering.
- Classification and resolution have NOT yet been timed.

Parsing-only sample estimate:
`229 * 84.555 / 3600 = about 5.38 hours remaining`.
All 230 at that rate would be about 5.40 hours. This is a one-page
extrapolation, not a guarantee and not a whole-pipeline estimate.

After measuring C seconds for ONE 25-term classification batch:
- Rough term estimate: `70 * 230 = 16,100 terms` (sample-based, not a census).
- Rough total classification batches: `ceil(16,100 / 25) = 644`.
- Rough classification hours: `644 * C / 3600` (subtract completed work if
  reporting remaining time; include startup effects honestly).
- Parsing + classification estimate: `about 5.4 + 644*C/3600 hours`.
  Examples ONLY, not measurements: C=30 s gives about 10.8 h; C=60 s gives
  about 16.1 h. Do not present these hypothetical numbers as an actual result.
- Resolution/database/review time is additional and still unmeasured. Harrison
  can still make ambiguous resolution calls as its registry grows; the OLD
  BIBLE's approximate zero-resolution-calls assumption is not a guarantee.

Do not claim the whole workflow is timed after only parsing/classification.
If resolution time cannot yet be estimated, say so and ask for an explicitly
staged scope (for example parse/classify only), rather than silently authorising
the full pipeline. Any new reader trial needs its own explanation and okay.
Existing `--stop-after parse` / `--stop-after classify` options can stage the
pipeline; do not run them without approval of scope and estimated hours.

The duration for all 37 books is UNKNOWN. Index sizes, term counts and later
matching costs differ; do not multiply Harrison by 37 and promise a finish date.
The goal is days, not months; Qwen must never be planned over thousands of
chapter pages. If the proposed measured job is too slow for Nir, stop and ask
SMART for a generic improvement while respecting his choice to keep Qwen.
No unattended, overnight or parallel-book work.

## 7. Local state and saving

Starting committed HEAD was `b6efc254c0808485ddf6a9b865052ad49d846357`, branch main,
matching GitHub when checked. Nir then requested backing up the completed work.
The Git checkpoint containing this handoff includes these five intended files;
verify HEAD/origin/main and remote tracking on restart:
1. `kitchen/index_extract.py` -- focused extraction repair.
2. `kitchen/test_index_pipeline.py` -- five synthetic regression tests.
3. `PROGRESS.md` -- decision, evidence, current pointers and handoff record.
4. `AGENTS.md` -- short next-session pointer only.
5. `HANDOFF-2026-10-25-DEEPSEEK.md` -- this file, including verbatim Opus text.

Local-only caches/proof in `kitchen/logs/` are gitignored. Keep them. Never
force-add them, PDFs, page images, transcripts, reader answers or screenshots.
Never read, print, copy or commit `kitchen/.env`, passwords or tokens.

If Nir asks to back up this checkpoint to GitHub: first inspect git status,
diff and recent commits; show the five intended file names; stage only those;
use a message starting with `3.7`; push and verify remote tracking; report the
commit/link. Do not discard the uncommitted repair to obtain a clean status.
Do not create commits or push merely because this handoff is being read.
Earlier local/uncommitted statements in the ledger describe the pre-save state.

Full test command ALREADY passed after code changes:
```bash
OPENBLAS_NUM_THREADS=2 .venv/bin/python -m unittest discover -s kitchen -p 'test_*.py'
```
117 tests in 2.087 s. Do not rerun it unless new code/failures warrant it.
Software versions checked: Python 3.13.5, git 2.47.3. Nothing installed.

## 8. After Harrison: continue the same work one book at a time

Only after Nir approves the trial and proposed scope/time, use the existing
pipeline/stages and review procedure from Opus's handoff. Keep work visible.
Full pipeline, when explicitly approved:
```bash
.venv/bin/python kitchen/index_pipeline.py HARRISON-22
.venv/bin/python kitchen/review_sample.py HARRISON-22
```
Show a SHORT review summary and the review file path. Only after Nir actually
approves the review, record his exact words using review_sample.py --approve
and in PROGRESS.md (Checkpoint 3.5). A previous globe approval is not this
registry approval. Then STOP and ask which book comes next.

Remaining books follow alphabetical book_id order, starting with ADAMS-12
after Harrison's approved review, unless Nir directs otherwise. Each book
needs its own small measured trial, time approval, execution, review and stop.
Do not switch back to SMART just because one book ended.

25 index ranges are configured; 12 are unset/invalid. An unset range does
not prove there is no index. Locating an index is a SMALL supervised reader
task, not a new TOC/completeness audit. Do not invent ranges. The supplied
--fallback workflow is only for a confirmed unusable index, under BIBLE 3.7.9
and Nir's approval. If finding ranges needs new generic software, ask SMART.

## 9. Exactly when to ask Nir to switch back to SMART

DeepSeek should tell Nir to switch to GPT 6.1 Sol (or his chosen SMART model):

1. EARLY SOFTWARE FAILURE: the same reproducible generic script/reader error
   has failed twice, or proceeding plainly requires new generic programming.
   First stop on the first failure and record evidence; do not blindly rerun
   to reach two failures. A second attempt requires an understood reason and
   Nir's okay. No prompt/model/code/provenance changes by trial and error.
   Bring command, time, full error, evidence paths, current status and what
   changed. Say if the raw answer is unavailable. SMART repairs generic tools;
   DeepSeek then resumes the ordinary operator work.
2. TOO SLOW: the small measured trial projects to a duration Nir rejects.
   Stop; bring timing/term/page counts and actual proposed scope to SMART for
   a faster generic workflow. Do not replace Qwen or weaken checks yourself.
3. NEXT PLANNED SMART REVIEW: after ALL 37 books' registry reviews are approved
   (Checkpoint 3.6), STOP. Ask Nir to switch for the entity-resolution rules
   and Freeze A review. Bring the per-book completion/approval evidence,
   doubtful merges/conflicts, unresolved counts and database verification.
   Do not freeze anything or silently change medical classifications.
4. BEFORE PHASE B: the old read-every-chapter-page plan is CANCELLED. SMART
   must write/review a fast plain-code-first plan, with Qwen only for the small
   measured remainder, show total hours/days, and obtain Nir's approval BEFORE
   any Phase B run. No thousands-of-pages reader job. This is a separate
   requirement even if the Freeze review has passed.

Later phases (altitudes, fact exports, live data) follow their BIBLE gates.
Real exports feed the already-written viewer via Part 7 ADDITION A9; they do
not authorise a viewer rewrite. DeepSeek returns to SMART when those phases
require generic programming/review, not for routine script execution alone.

Suggested short switch message:
"This next step needs GPT 6.1 Sol: <specific reason>. I saved the commands,
results and next step in PROGRESS.md. Please switch models and say continue."

## 10. Hard boundaries

- No edits to BIBLE/. Opus alone had one-time permission. Record decisions in
  PROGRESS.md and ask Nir if a BIBLE requirement seems wrong.
- Protect the approved site/viewer/, both geography folders, geography/Goldberg/
  flower builders and book/chapter identities. Do not regenerate/install maps.
- No model changes, global reader setting changes, secret-file reads, installs,
  sudo, background jobs, no unattended work and no new book without Nir.
- No new TOC work or PDF-completeness reminders. Those subjects are closed.
- Do not delete/re-stamp successful caches or hand-edit hashes/medical entries.
- A changed input or future cache refusal is evidence to investigate, not a
  reason to turn checks off. Do not run the full pipeline as a diagnostic.

## 11. Opus 5.5's complete original handoff -- VERBATIM

Source: `HANDOFF-2026-10-24-DEEPSEEK.md`, written by Claude Opus 5.5.
Everything BETWEEN the four-backtick fences below is copied without changes.
It is historical text, not an instruction to redo completed steps. The
current-state corrections, approvals and safety bounds above must be read
before running any command from it. The source file and BIBLE are not edited.

````markdown
# DeepSeek handoff -- 24 October 2026 (written fresh by Claude Opus 5.5)

This file REPLACES `HANDOFF-2026-10-23-NIGHT-DEEPSEEK.md` (that one is
history now). Everything you need is here. Follow it step by step. Do not
improvise, do not skip, do not "improve" anything.

Your job: run the **Harrison index trial** (book HARRISON-22), with Nir
watching, one small step at a time. Then the full Harrison index, then show
Nir the review. Then stop.

---

## 0. Rules you must obey (read twice)

**RULE ZERO -- NIR'S HARD LIMIT (24 Oct 2026, his words: "i never approved
for qwen to go on thousands of pages per book, in ANY phase, NEVER EVER ...
not months, never months").**
- Qwen is NEVER run over thousands of pages of a book. This job uses Qwen
  only on Harrison's back-of-book INDEX (230 pages of about 4,300) and on
  the index terms, 25 at a time. Nothing else.
- Before the full run you MEASURE the trial, compute the total time in
  HOURS and show it to Nir (step 5b). You start the full run only if Nir
  says okay to that number.
- Anything that would take weeks or months is forbidden. If the estimate
  is too long for Nir, STOP: the answer is a faster plain-code method
  written by SMART, never "let it run".
- Never start "Phase B" / BIBLE Part 4 (reading the chapter pages). It is
  forbidden until SMART writes a new fast plan and Nir approves it.

1. **Do NOT edit anything in `BIBLE/`.** Not one character. Only Claude
   Opus 5.5 was allowed to write there, once. You write your notes only in
   `PROGRESS.md`.
2. **Do NOT touch the map or the viewer.** No changes to `site/viewer/`,
   `site/data/geography/`, `data/export/geography/`, `kitchen/goldberg_*`,
   `kitchen/geography_*`, `kitchen/flower_map.py`, `kitchen/make_demo.py`.
   They are finished and Nir approved them on 24 Oct 2026.
3. **Do NOT reopen closed work**: no table-of-contents checks, no "are the
   PDFs complete books" checks, no re-checking of any book's chapters.
4. **The free local model reads the pages.** The reader is Qwen
   `qwen3.8:27b` on this laptop's Ollama server (already installed and
   running). You (DeepSeek) only run the scripts and check the results. Do
   not read index pages yourself, do not classify terms yourself.
5. **One book only: HARRISON-22.** Nothing runs unattended. No overnight
   jobs, no parallel books, no background loops. Nir watches.
6. **Never print, copy or show `kitchen/.env`** (it holds the database
   password). Never install anything. Never use `sudo`.
7. **Before each step, tell Nir in 1-3 short plain sentences what you will
   do, and wait for his "okay".** He is a beginner. Use emojis in chat
   only, never in files or commit messages.
8. If something fails: **stop**, show Nir the exact error, and do not try
   random fixes. If the same generic software error happens twice, write it
   down (section 7) and tell Nir that SMART (a smarter model) is needed.

All commands run from the project folder:

```bash
cd ~/second-opinion
```

---

## 1. Check the starting point (no changes)

```bash
git status --short
git log --oneline -3
```

Expected: a clean (or nearly clean) status, and the newest commit is from
24 Oct 2026 ("... DeepSeek handoff ..." or later). If there are changed
files you do not understand, STOP and ask Nir.

What already exists (do not redo):
- 37 books, all chapter lists finished. Harrison has 505 chapters.
- The approved map (Goldberg ball) in `data/export/geography/`.
- The index software (`kitchen/index_*.py`, `kitchen/review_sample.py`),
  tested earlier. One Harrison index page (PDF page 4044) was already
  extracted as a pilot; its files are in `kitchen/logs/`.
- The Neo4j database is running but EMPTY (only 3 "Meta" nodes).

---

## 2. Test the reader (Qwen)

Tell Nir: "First I check that the free reader on this computer answers."

```bash
.venv/bin/python kitchen/reader.py
```

Expected output: `{'ok': True}` (the first call can take a minute or two
while the model loads on the graphics card).

If it fails: check that Ollama runs and has the model, then stop and show
Nir:

```bash
curl -s localhost:11434/api/tags
```

(It should list `qwen3.8:27b`.) Do not change any model setting.

---

## 3. Look at the plan (read-only, no reader, no database)

```bash
.venv/bin/python kitchen/index_pipeline.py HARRISON-22 --plan --limit 1
.venv/bin/python kitchen/load_geography.py
```

Expected (checked on 24 Oct 2026):
- `HARRISON-22 extract: index PDF 4044-4273; 230 pages; 505 districts; limit=1; read-only plan`
  (and the same line for parse, classify, resolve)
- `Geometry: 37 books; 5334 territories` and `Dry run; no database access or writes`

---

## 4. Put the map into the database (one transaction)

Tell Nir: "Now I copy the approved map (books, parts, chapters) into the
database. This is needed before the index can be linked to chapters."
Wait for his okay.

```bash
.venv/bin/python kitchen/load_geography.py --apply
```

Expected: 37 books and 5,334 territories (37 continents + 534 provinces +
4,763 districts). Copy the printed counts into your PROGRESS.md note.
If it refuses (for example "frozen" or "differs"), STOP and show Nir.

---

## 5. The bounded trial: ONE index page and ONE batch of terms

Tell Nir: "Now the reader reads ONE index page, and then sorts ONE batch
of 25 terms. Then we look at the result together."

```bash
time .venv/bin/python kitchen/index_parse.py HARRISON-22 --limit 1
time .venv/bin/python kitchen/index_classify.py HARRISON-22 --limit 1
```

Write down the two "real" times that `time` prints (seconds for one page,
seconds for one batch of 25 terms).

`--limit 1` means one NEW page / one NEW batch. Then show Nir, in plain
words, what came out (the newest files about HARRISON-22 in `kitchen/logs/`).
Check only the STRUCTURE, not medicine:
- It really is the back-of-book index (alphabetical terms with page numbers).
- Main entries and their sub-entries are kept apart and in order.
- The page numbers are the book's printed ones, copied exactly.
- A term continued from the previous page stays attached to its parent.
- Each term got exactly one group: symptoms-and-signs,
  diseases-and-conditions, treatments-and-drugs, or not-an-entity.

If Nir is not happy, STOP and write what he said in PROGRESS.md.
Do not hand-edit any JSON to make it look right.

### 5b. The time estimate (MANDATORY before step 6)

Compute and tell Nir, in hours:
- parse time = (seconds for one page) x 229 remaining index pages
- classify time = (seconds for one batch) x (number of index terms / 25).
  The number of terms per page: count the entries in the newest
  `kitchen/logs/HARRISON-22-index-<page>.json`; estimate the total as
  (entries on that page) x 230.
- total = parse time + classify time, in hours (round up).

Say it plainly, for example: "The whole Harrison index would take about
N hours of Qwen time. Is that okay?" If Nir says it is too long, STOP,
write the numbers in PROGRESS.md and tell him SMART can write a faster
plain-code index reader. Do NOT start step 6 without his okay to the
number.

---

## 6. The full Harrison index, then the review (only after Nir says okay to the 5b estimate)

Tell Nir: "The trial looks fine. Now the reader goes through the other 229
index pages of Harrison (about N hours, as measured). You can watch the
progress. It can be stopped and started again without losing work."

```bash
.venv/bin/python kitchen/index_pipeline.py HARRISON-22
```

- Keep it in this visible terminal. Progress is also written to
  `kitchen/logs/HARRISON-22-run.log`.
- If it stops or Nir stops it: run the SAME command again; finished pages
  are not read again.
- To pause between stages: `--stop-after parse` or `--stop-after classify`.

When it has finished:

```bash
.venv/bin/python kitchen/review_sample.py HARRISON-22
```

This writes `kitchen/logs/HARRISON-22-review.md`. Show it to Nir (counts,
sample terms per group, possible wrong merges, conflicts). This is
Checkpoint 3.5.

**Only if Nir approves**, record HIS EXACT WORDS (replace the text in quotes):

```bash
.venv/bin/python kitchen/review_sample.py HARRISON-22 --approve "his exact words here"
```

Then STOP and ask Nir what next. (The next book would be the alphabetical
first remaining book, ADAMS-12, same steps 5-6. Never start it without his
okay.)

---

## 7. Write it down and save to GitHub

Add a short entry at the top of the `## DONE (newest first, each with
evidence)` section of `PROGRESS.md`: date, what you ran (exact commands),
the printed counts, and what Nir said. If something failed, write the exact
command and the full error under `## BLOCKED`.

Then save (show Nir the list of files first):

```bash
git status --short
git add PROGRESS.md
git commit -m "3.7 HARRISON-22 index trial: <one short line>"
git push
```

Only add other files if the scripts created tracked, intended files and
Nir agrees. Never add `kitchen/logs/`, PDFs, page images, reader answers or
`.env` (they are ignored anyway; do not force them).

---

## 8. When to call SMART instead

Stay with DeepSeek for all of this. Call SMART (tell Nir "this needs the
smarter model") only:
- after the same generic software error happened twice (bring the exact
  command, the full error and the log file names), or
- after ALL books have approved reviews (Checkpoint 3.6), for the Freeze A
  review.

---

## 9. If Nir asks about the globe

It is finished and approved. Local view (optional, only if he asks):

```bash
.venv/bin/python kitchen/open_globe.py
```

The live website shows it when Nir double-clicks "Websites ON".
Do not change it. Full documentation: the "CLAUDE OPUS 5.5 ADDITION"
blocks at the top of BIBLE parts 8, 1, 3, 7 and 9.

---

## 10. What Nir pastes to start you

> Please read ~/second-opinion/HANDOFF-2026-10-24-DEEPSEEK.md and follow it
> step by step. Explain each small step briefly before you do it.
````
