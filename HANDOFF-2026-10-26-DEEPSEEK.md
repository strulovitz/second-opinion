# DeepSeek restart handoff -- Harrison parser repaired, 26 October 2026

PAUSED LATER ON 26 OCTOBER: Nir requested a budget stop until next month.
Read [the November pause/restart handoff](HANDOFF-2026-10-26-PAUSED-UNTIL-NOVEMBER.md)
FIRST. Actual saved state: 54/230 accepted, next PDF 4098 with 89/91 pieces
cached (next 90). The commands and counts below are historical; do not resume
until Nir explicitly returns and asks. The new handoff documents subsequent
normalization changes, verification, local caches and remaining-time estimates.

From GPT 6.1 Sol, at Nir's request. Repository: /home/nir/second-opinion.

## LATEST -- second repair completed, 26 October afternoon: resume at 4053

This block supersedes the older counts, JSON-only recipe and timing claims
below. Read the newest PROGRESS.md DONE entry for the repair experiments.

- Nir manually returned to GPT to fix the 4052 stop. It is now repaired:
  **9/230 pages accepted, PDF 4044-4052; 221 remain; next new page 4053**.
  Assembly is 593 entries. Current prefix has 534 classification terms;
  25 saved classifications remain current/unchanged, 509 prefix terms pending.
  Whole-book term total is still unknown. No classification during this fix.
- The original eight accepted page caches and all 230 extraction text/image/
  receipt sets are unchanged. Offline verification checked 836 protected files,
  all nine page keys/groundings, the assembly and all 51 saved fragments of
  4052; zero reader/database calls during verification. **137 tests pass**.
- The old 301-reference count for 4052 was WRONG. The source has a printed
  range split as `3479–` / `3480`. The old checker rejected its legitimate
  joined reference and missed the references before the incomplete range.
  Source counting/literal matching now handle ASCII, en and em dash wraps
  without changing quotes. **All 303 source reference tokens are retained**.
- Valid JSON could also have stray top-level entry fields: data outside the
  entries list was ignored. New answers use the complete strict JSON schema
  and an explicit shape validator; reference completeness is still mandatory.
- Whole-page schema-only, sampling and reasoning experiments did NOT solve
  the early stop. Broad 24-line chunks also lost entries after a large entry
  or a See alias. The final fallback reads **one physical main-entry block**
  per request, splitting long entries at complete reference runs (24-line
  target). Exactly one entry/CONTINUED is required for each fragment. It
  checks indentation, literal source text and every reference, joins genuine
  continuations, then revalidates the ENTIRE page and rebuilds full-page quotes.
  4052 used 51 fragments -> 49 main entries; no hand-edited medical entries.
- Ordinary new pages still try the full page first (at most two attempts).
  Failed completed answers trigger the fallback. Transport failures with no
  completion stop. Fragment plans/results/responses are cache-bound; a resume
  reuses accepted fragments and skips failed whole-page work. Do NOT delete
  caches or manually change the fragment recipe. The v4 page key binds the
  source, ordering, model, schema, controls and fragment version. Revalidated
  v2/v3 page caches are reused under their ORIGINAL keys, without re-stamping.
- New parse requests alone use temperature=.7, top_p=.8, presence_penalty=1.5,
  reasoning off, strict schema and a 300 s HTTP timeout. The base PARSE prompt
  is unchanged; fragment instructions are separately cache-bound. No global
  reader/model/environment changes; classification keeps its original controls.
- Each completed page now checkpoints the assembly immediately; a later
  failure cannot leave it reporting an older successful prefix. Partial-page
  resumes no longer print a fresh-page ETA from only their remaining work.

### Restart and timing

NIR SWITCHES BACK TO DEEPSEEK HIMSELF. GPT ends after this handoff.
Explain 9/230, 221 remaining, and the changed timing uncertainty, then run
the NEXT **one new page**, supervised, under the already approved scope:

```bash
time timeout --signal=INT --kill-after=10s 900s .venv/bin/python -u kitchen/index_parse.py HARRISON-22 --limit 1
```

Use tool workdir=/home/nir/second-opinion, timeout at least 930000 ms. No
warm-up, extraction, diagnostics or repeat of 4052. Then continue the same
foreground stages below. Use one-page chunks if fallbacks make five-page
chunks exceed 15 minutes; keep reporting counts, wall elapsed and stage ETAs.
After all pages parse, continue the existing classification stage; stop there.

The final 4052 recipe needed **172.013 s across two commands** (108.000 +
64.013), including failed whole-page work and a continuation-feedback repair.
The last command's 64.013 s and printed 3.91 h ETA represented a PARTIAL
RESUME, not a new full-page timing sample. Do not extrapolate them. The old
~15-hour forecast is historical: frequency of fallback and the new normal-page
pace are not measured yet. Report actual time for 4053 and subsequent fresh
pages, update the projection, and tell Nir if materially different. Classification
still uses the old single-batch timing (51.220 s/25 terms) until newly measured.

Evidence (gitignored, under kitchen/logs/):
`HARRISON-22-index-4052-repair-before-20261026.json`,
`HARRISON-22-index-4052-repair-verification-20261026.json`,
`HARRISON-22-index-4052.json`, `...-4052-fragments.json`, 51 numeric fragment
caches and their raw responses/rejections. Earlier failed fragment recipes are
preserved as `...-trial-v1/v2/v3.json`, not accepted caches. No commit/push.

## Earlier morning handoff -- historical details follow

## 1. The current instruction and model switch

NIR SWITCHES MODELS HIMSELF in this OpenCode conversation. GPT repairs the
generic software and stops after this handoff. GPT must not launch DeepSeek,
call a cloud reader, switch models or start the long book job for him.
DeepSeek operates the scripts; local qwen3.8:27b is still the actual reader.

Read AGENTS.md, the governing BIBLE additions/Part 3 sections 7-9, and the
newest PROGRESS.md pointers. This handoff supersedes the next-step/status
sections in HANDOFF-2026-10-25-DEEPSEEK.md and INDEX-PIPELINE.md. The original
Opus appendix in the older handoff remains historical; do not redo its steps.

On 26 October Nir explicitly requested the previously estimated ~14.5-hour
Harrison job, continuously, with visible progress. That approved scope is
**HARRISON-22 parsing and classification only**, equivalent to the pipeline's
--stop-after classify. The earlier pending-approval entries are historical.
After the failure he asked GPT to investigate/fix it and write this handoff,
then he would manually switch back to DeepSeek to continue.

The repair is finished and checked on the two affected pages. No long job is
running now. On Nir's return to DeepSeek with "continue", explain the current
counts/time briefly, then resume that approved scope. Do not ask for a new
approval after every page/chunk. Still stop on a genuine error, a human stop,
the end of classification or a proposed new scope.

## 2. Actual saved position -- do not repeat the successful trials

- Extracted source text/image receipts: **230/230 index pages**, PDF 4044-4273.
- Accepted parse caches: **3/230**, PDF 4044, 4045 and 4046. **227 remain**;
  the next new reader page is **4047**.
- Assembly: 196 main entries, 974 expanded numeric reference records;
  online-only=35, non-integer-or-malformed=1, outside-districts=0,
  mapping-unresolved=0. Incomplete; not a completed book/registry review.
- The three pages contain 905 original reference tokens (278 + 313 + 314).
  Each page passes the new missing/duplicate-reference check.
- Their current classification inputs: **180 terms**. **25** previously
  classified terms still have current keys and valid records, unchanged
  byte-for-byte. **155 current-prefix terms** are pending. Neither 180 nor
  155 is a whole-book term count.
- Classification should wait until all 230 pages are parsed, so page
  continuations have their final context. The existing 25 records are reused.

PDF 4044 and its original source/reader evidence remain unchanged. The
apparently successful old PDF 4045 cache was actually incomplete: 73 main
entries, zero subentries, only 121 of 313 source reference tokens. It was
preserved, not deleted or edited, as:
`kitchen/logs/HARRISON-22-index-4045-incomplete-20261026.json`.
Its bytes match the before-repair hash. It is NOT an accepted parse cache.
The current numeric-name 4045.json is Qwen's complete repaired answer.

## 3. What failed and what SMART fixed

1. **Unfinished JSON.** The original failed response was not saved. One
   bounded reproduction stopped before closing the JSON despite
   finish_reason=stop and only 4,747/12,000 completion tokens. Do not claim
   the original missing-comma location proves the same exact character defect.
2. **Wrong PDF column order.** Page 4046's default pdftotext output had the
   middle and right columns before the left column. This made an internal
   column continuation look like a continuation from the previous page.
   JSON-only mode fixed syntax but still produced a duplicate headword and
   failed source grounding. It was not accepted.
3. **Incomplete output could pass.** The old checker tested whether returned
   words/references existed, but did not require all source references. That
   is why 4045's 192 missing tokens had been overlooked.

The generic changes:
- kitchen/index_order.py derives physical left-to-right column order from
  selected-page pdftotext -bbox-layout geometry. It preserves original text,
  image and source receipts; derived bbox/ordered evidence is separate. It
  compares word inventories, allowing only the known line-end discretionary
  hyphen difference, and refuses ambiguous geometry or changed evidence.
- New index parsing uses request-local response_format={"type":"json_object"}
  and its existing reasoning-off setting. No model, prompt, .env or global
  reader setting changed. Classification/matching keep their reader settings.
- New parse caches have a v3 key bound to the ordered-input receipt. Old v2
  caches are accepted only under their exact original source/input/model/
  prompt key and revalidated. No hash re-stamping or blanket cache deletion.
- ground_entries() now checks literal reference-list tails for missing/extra
  tokens, in addition to its existing source checks. It is a conservative
  structural check, not proof that every medical interpretation is correct.
- Every new parse completion is saved locally BEFORE JSON content decoding,
  including malformed/truncated content: index-<page>-response-<UTC>.json.
  Semantic failures also retain index-<page>-rejected-<UTC>.json. Transport
  failures without a completion may still have no raw answer; report honestly.
- Parse/classify output now includes saved/expected counts, elapsed time for
  the current command, and a clearly labelled STAGE-only remaining estimate.

Do not edit the returned entries manually. Qwen did the actual parsing. GPT
replayed its two exact successful diagnostic completions through the real
production parser with HTTP intercepted and exact request-body checks; no
second Qwen call was needed to save those accepted production caches.

## 4. Resume visibly in foreground chunks

Use the terminal tool's workdir=/home/nir/second-opinion. Keep the work
foreground. The earlier setsid/nohup launch and /tmp/opencode/sp_progress.py
are NOT the restart method: that monitor had a wrong PID initially, and its
"TOTAL LEFT" omitted classification. Its displayed 19-hour estimate was not
a measured whole-job result. Do not reuse it or overwrite the failure log.

Record the actual resume clock once (`date -Is`) in PROGRESS.md. Keep the
same start clock across chunks; distinguish wall time (including pauses)
from summed timed-command execution. Check `timeout --version` once if using
the wrapper below; GNU timeout 9.7 was available in the original trial.

Run one foreground chunk at a time, report briefly, and immediately continue
the next chunk under Nir's existing approval. This gives real chat updates
roughly every 5-10 minutes instead of one silent 15-hour tool call. There is
no detached job, background polling loop or work after the chat is abandoned.
Give the enclosing terminal tool **at least 930000 ms**, so the 900-second
wrapper can signal/exit before the tool kills it.

### Parsing -- repeat until parsed_pages=230 and complete=True

```bash
time timeout --signal=INT --kill-after=10s 900s .venv/bin/python kitchen/index_parse.py HARRISON-22 --limit 5
```

--limit 5 means up to five NEW pages. Saved pages are checked/reused without
reader calls. At the current two-page sample speed a normal chunk is about
7-8 minutes; complicated pages/retries can be slower. Source extraction has
already finished; no extraction rerun, warm-up, reader smoke test or new
diagnostic is needed just to restart.

### Classification -- only AFTER the full parse succeeds

```bash
time timeout --signal=INT --kill-after=10s 900s .venv/bin/python kitchen/index_classify.py HARRISON-22 --limit 5
```

Here --limit 5 is five NEW batches of up to 25 terms, not five terms. At the
old measured 51.220 seconds/batch, a normal chunk is about four minutes.
Continue chunks until all current whole-book terms have current records.
Do not start resolve, registry review/approval, another book or Phase B.

These are the existing stages of the approved --stop-after classify scope.
Do not run the unrestricted pipeline, which would continue into Neo4j
resolution. The staged/chunked commands do not change the medical workflow.

### What to show Nir after every chunk

Keep chat short, with emojis in CHAT ONLY:
- phase; pages saved out of 230; pages left;
- classified current terms/expected terms (mark full-book totals UNKNOWN
  until parsing completes); terms/batches left once that total is known;
- wall time since resume and actual timed-command duration;
- approximate parsing time left AND classification time left, plus their
  sum. Never call a parsing-only number the total remaining time.

Use the scripts' raw counts and the command's real time. Update parse pace
as (chunk real seconds / new pages), and classification pace as (chunk real
seconds / new batches). Do not treat cached-page checking as new reader work.
If a command fails/times out, report saved progress and the error, not an ETA.

## 5. Time estimate -- sample, not a promise

The repaired successful calls took 97.163 s (4045) and 85.791 s (4046), with
startup not measured separately. Their mean is 91.477 s/page. This implies:
- 227 remaining pages * 91.477 / 3600 = **5.77 h parsing**.
- Keeping the OLD one-page assumption of 16,100 whole-book terms and the
  measured 51.220 s per 25-term batch: 643 batches remain, **9.15 h**.
- Combined: **about 14.92 h**, roughly 15 h, under those sample assumptions.

The new three-page sample averages 60 classification terms/page rather than
the original 70; do not silently promote either extrapolation to a census.
The exact total arrives after parsing. Recompute remaining batches as
ceil((current whole-book terms minus valid saved current terms) / 25), and
use newly measured chunk times. Reader retries and human pauses are extra.
Nir already approved the roughly 14.5-hour staged job; explain this modest
updated estimate when resuming. Ask him if materially slower evidence or a
new scope needs a new decision, not after each ordinary chunk.

Matching/database/review remain UNMEASURED and require the next separate
small timing step and Nir's scope/time approval after classification ends.

## 6. Verification and evidence already saved -- do not rerun as a ritual

127 automated tests passed in 1.961 s:
`OPENBLAS_NUM_THREADS=2 .venv/bin/python -m unittest discover -s kitchen -p 'test_*.py'`.
git diff --check passed. No installs or database calls during this repair.
Versions: Python 3.13.5, git 2.47.3, pdftotext 25.03.0, pypdf 6.20.1,
Ollama 0.32.14. GitHub main was read-only checked and matched local committed
HEAD bd95a18; the current repair and preceding documentation edits are local.

Local, gitignored evidence (never force-add to GitHub):
- HARRISON-22-index-diagnostic-4046-20261026T070115246150Z.json -- reproduced
  incomplete JSON, 95.101 s, no JSON constraint.
- HARRISON-22-index-diagnostic-4046-20261026T070422295809Z.json -- JSON-only,
  83.203 s, duplicate headword/source grounding failure; not accepted.
- HARRISON-22-index-diagnostic-4046-20261026T071119631227Z.json -- final
  ordered/JSON trial, 85.791 s, 35 entries, 161 subentries, all 314 refs.
- HARRISON-22-index-diagnostic-4045-20261026T071254980982Z.json -- final
  ordered/JSON trial, 97.163 s, 86 entries, 122 subentries, all 313 refs.
- HARRISON-22-repair-20261026-before.json -- before hashes for 967 files.
- HARRISON-22-repair-replay-20261026.json -- diagnostic/cache hashes and
  exact production replay receipt, zero network calls during replay.
- HARRISON-22-repair-verification-20261026.json -- offline verification of
  all 230 unchanged extraction receipts/text/images, three accepted parse
  keys/groundings/assembly, and the 25 unchanged current classifications.

All paths above are under kitchen/logs/. Exactly FOUR live diagnostic model
requests occurred; the first column-inventory check stopped before a model
call. No reader warm-up, new classification, resolution or long job by GPT.

## 7. Boundaries and errors

Preserve the BIBLE, approved globe/viewer/geography, book identities and
closed TOCs. No global model changes, installs, sudo, secret-file reads,
unattended jobs or parallel books. On failure stop and bring the exact
command, time, error and local response/rejection evidence to Nir/SMART;
do not blindly retry, weaken checks, reorder medical entries by hand or
delete successful caches. Nir may request GPT review at any time.

At the end of classification, record the exact counts/time and STOP for the
small measured matching step. At the later end of approved Harrison registry
work, show the review and obtain Nir's actual approval before another book.
The old model-switch gates in handoff section 9 still describe later phases.

No commit/push was requested for this repair. If Nir asks for a GitHub save,
inspect status/diff/recent history, preserve the preceding local documentation,
show intended filenames and stage only the intended public code/tests/docs.
Never add kitchen/logs/, PDFs, page images, responses, transcripts or .env.
