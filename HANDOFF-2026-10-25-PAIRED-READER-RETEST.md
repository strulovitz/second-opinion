# New handoff: Nir switches to DeepSeek for the paired reader retest

HISTORICAL: this comparison was completed; Nir subsequently selected local
Qwen and closed the cloud-reader comparison. Do not execute the trial again.
Latest instruction: [budget pause and November restart handoff](HANDOFF-2026-10-26-PAUSED-UNTIL-NOVEMBER.md).
Wait for Nir to return and explicitly continue; this file is preserved evidence.

Written by GPT 6.1 Sol, 25 October 2026. Repository: /home/nir/second-opinion.
This replaces the earlier manual-comparison handoff for the NEW trial only.
Keep every earlier answer, timing, comparison and cache unchanged.

## 1. The human switches models, not GPT

Nir explicitly corrected GPT again: GPT must WRITE THIS HANDOFF, then stop.
NIR switches to free DeepSeek himself inside this OpenCode conversation and
gives DeepSeek this file. GPT must not invoke DeepSeek through an API,
opencode run, a child session, a subagent or any other automatic model switch.

If you are GPT, stop here. If Nir has selected DeepSeek and told you to follow
this handoff, YOU are the cloud reader for the new trial. Do the parsing
yourself in this conversation. Do not delegate it or copy a saved answer.

Nir has requested the retest. That authorises ONE fresh DeepSeek parse and ONE
fresh local Qwen parse of saved Harrison index PDF 4044, in the foreground,
with Nir watching. No further pages, retries or full-book job. Do not ask him
to approve these same two one-page attempts again.

## 2. What we are measuring

Nir wants to know which usable workflow saves HIS time. Every necessary step
counts: reasoning, generation, tool calls, answer saving, validation, assembly
and saving the checked result. Do not excuse DeepSeek's tool/reasoning time.

For BOTH readers use the SAME boundary:

    prepared page released to reader -> first answer checked and saved

Use the frozen local harness below. Both branches call the identical finish()
function, the production ground_entries()/assemble() validators, and the same
comparison against the existing verified reference. Both clocks stop AFTER
the checked output has been saved. Qwen's clock includes its model loading
if needed; no warm-up or cached answer is used. Necessary DeepSeek tool work
stays on its clock. One-time handoff/setup/preflight and final chat/ledger
reporting are outside BOTH clocks.

The old 84.555 s versus 267.945 s are NOT the new test results. GPT previously
confirmed a 3x practical advantage without equivalent timing boundaries;
that was unsupported. Do not repeat it as an established whole-job result.

This is a practical local-workflow versus OpenCode-workflow comparison, not
identical cloud/local hardware or settings. The cloud conversation has extra
instructions/history, and both models' old answers have already been discussed.
This is not a blind accuracy experiment or evidence about every book.

## 3. Read and prepare BEFORE starting the stopwatch

Do all required standing-order reading now. Finish reading THIS ENTIRE handoff
before starting the timer. Do not spend timed minutes rereading the handoff,
looking for commands, debating fairness or narrating the test.

Working directory for every command: /home/nir/second-opinion.

The isolated harness already exists locally:

    kitchen/logs/reader-retest-20261025.py

Frozen harness SHA-256 (the check command prints it):

    8354fcd78780128e645910d711a3ea00391495b6a4c4b513d100d1357faa659a

It is ignored by Git and is NOT a production-script edit. Do not change it.
It uses existing source/prompt/settings and rejects changed originals. It
never writes production caches or calls the database. The only generation
request it can make is Qwen through the configured LOOPBACK local endpoint.
No cloud API, provider credential, child model or new OpenCode session is used.
Do not read or display .env or credentials.

Read-only check (no generation, no stopwatch or trial output):

```bash
.venv/bin/python kitchen/logs/reader-retest-20261025.py check
```

Expected: read-only preflight passed. If it fails or says a retest already
exists, preserve everything and STOP; do not erase artifacts or adjust hashes.
The harness was syntax-checked and its read-only preflight passed during GPT's
handoff preparation. Offline fixtures also verified baseline acceptance,
wrong-reference-assignment detection and preservation of existing results,
without calling a model or creating the real trial directory. Neither new
reader attempt has been run by GPT.

Tell Nir only: "I will time both readers through checking and saving, counting
all necessary work." Keep chat brief. Qwen's previous one-page time was about
85 seconds; the single local request has a 300-second timeout, one attempt.
There is no enforceable generation timeout on your own OpenCode turn; do not
claim there is one. Nir can interrupt either task. Do not run anything longer.

## 4. First attempt: DeepSeek itself

Start the stopwatch and receive the exact original instruction and page text:

```bash
.venv/bin/python kitchen/logs/reader-retest-20261025.py start-deepseek
```

The clock is now running continuously, including ALL your reasoning and
necessary tools. Parse the displayed source yourself. Use the original JSON
schema, compact JSON, literal headwords/subentries and every printed reference.
Do not open ANY old answer, diagnostic response or comparison while generating.
Do not run Qwen first. You must produce a fresh answer, not reuse one from
memory as a substitute for checking the displayed source.

Using apply_patch, create ONLY this first-answer file:

    kitchen/logs/HARRISON-22-reader-retest-20261025/deepseek-answer.json

Immediately run the next command. Do not check status, give a report, ask a
question or read more files between answer saving and this command:

```bash
.venv/bin/python kitchen/logs/reader-retest-20261025.py finish-deepseek
```

This checks and saves the result, THEN stops DeepSeek's clock. Validation
failure is recorded as failure, with its elapsed time. Never edit the answer
after seeing the result; never edit a validator or secretly retry.

If Nir interrupts or a tool/permission failure prevents timely completion,
preserve the artifacts and report the interruption; do not rank that timing
as an uninterrupted reader result or reset the stopwatch yourself.

## 5. Second attempt: Qwen on Nir's computer

Only after DeepSeek's first result is saved:

```bash
.venv/bin/python kitchen/logs/reader-retest-20261025.py qwen
```

Use a foreground terminal timeout of 330000 milliseconds. This makes ONE
fresh request to qwen3.8:27b through the existing local reader, with the exact
original request body/settings. It rejects a non-local endpoint or changed
request. It then saves Qwen's first answer, checks it through the SAME finish()
function, saves the checked output and stops Qwen's clock. Local request time
is included, not substituted for total workflow time. No model warm-up,
production-cache hit, extra pages, retry loop or source edit is allowed.

Even if DeepSeek's answer failed normal output validation, the one Qwen attempt
can still be measured. If an integrity/identity check failed, STOP instead.
An unsuccessful/timeout answer does not win just because it returned quickly.

## 6. Summary and a DIRECT answer

```bash
.venv/bin/python kitchen/logs/reader-retest-20261025.py summary
```

The harness compares references WITH their headword/subentry assignments,
not just global counts. It checks literal headwords, See targets and subentry
labels, and reports display-label differences separately. Both answers must
pass and retain the baseline assignments before it declares a timing winner.
Inspect any display-label differences for meaning before calling quality tied.
Do not equate matching counts alone with matching answers.

Evidence lives only under:

    kitchen/logs/HARRISON-22-reader-retest-20261025/

Important files: deepseek-answer.json, deepseek-checked.json,
deepseek-result.json, qwen-answer.json, qwen-checked.json, qwen-result.json,
qwen-local-response.json and summary.json. Raw book text/answers never go to
GitHub. Existing scripts/caches/evidence must still match their original hashes.

Record a short PROGRESS.md entry with the model Nir selected, both NEW total
times, validation/assignment results, interruptions if any and the evidence
path. Update CURRENT PHASE/NEXT STEP so this trial supersedes the old timings.
Do not change BIBLE/, globe/viewer/geography, reader settings, database or
production caches. No commit/push unless Nir asks.

Give Nir a SHORT, direct result, with chat emojis only:

    [Reader] was faster in this complete one-page test: X seconds versus Y,
    about Z times faster. [Both passed / explain the failure].

If there is a failure or meaningful quality difference, say that directly
instead of announcing a speed winner for equally usable answers.

The summary also gives 230-index-page PARSING-ONLY hour projections under the
explicit assumption that every page takes this long. Give these as estimates,
not a measured whole-book duration. Classification/resolution are not included.
Do not turn one page into a general model ranking. Do not call necessary
DeepSeek overhead unfair or dismiss Nir's real waiting time.

Then ask Nir to switch back to GPT 6.1 Sol and have it read the NEW summary.
STOP. Nir chooses the reader together with GPT; do not switch production,
start classification or read another page/book.
