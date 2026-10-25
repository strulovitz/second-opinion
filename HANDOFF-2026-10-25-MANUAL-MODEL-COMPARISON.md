# Hand-off: Nir manually switches to the free model, which does this trial itself

Written by GPT 6.1 Sol, 25 October 2026, following Nir's explicit correction.
Repository: `/home/nir/second-opinion`.

## 1. The arrangement -- read this before doing anything

NIR switches the model HIMSELF in this OpenCode conversation, from GPT 6.1
Sol to free DeepSeek V4.1 Flash or another free model HE chooses. He then
gives the selected model this handoff. That selected model is YOU.

YOU perform the small reading task yourself, using the text and instructions
below. Do NOT call a cloud API, launch another OpenCode session/model, call
Ollama/Qwen, inspect credentials, or ask GPT to run a comparison for you.
If GPT 6.1 Sol is still selected, stop and let Nir switch models himself.

GPT previously misunderstood this arrangement and made two direct API requests.
They returned HTTP 429 and no answers. Those are NOT the comparison Nir asked
to conduct. They do not show whether your manually selected model can do the
task, and do not prevent this trial through the existing OpenCode conversation.

This is an explicit, narrow human exception to the older rule that DeepSeek
only supervises while Qwen reads: for THIS ONE trial, the selected FREE cloud
model itself parses the saved index page. The project BIBLE is not edited.

Do not modify scripts, configuration, the globe, the database or production
caches. No full-book work. Do not resume the older classification instructions.
One existing page, one answer, validation, report, then return to GPT with Nir.

## 2. What you must do

Qwen previously turned ONE Harrison index page (PDF 4044) into structured
JSON: main entries, subentries, See targets and original page references.
You will do that SAME task on the SAME text with the SAME original system
instruction. This is index parsing, not the later symptom/disease/drug
classification stage. No classification trial is requested here.

Use your own interpretation of the source. Do not open Qwen's answer, copy
it, or tune your output to its counts before saving your own first answer.
The preparation command prints only the original instructions and page text,
not Qwen's response. The comparison command reads Qwen's answer afterward.

The general chat context and model settings in OpenCode differ from the
original direct Qwen API call. This is a practical same-task comparison,
not a claim that all underlying API/sampling settings are identical.

## 3. Preparation: print the actual original task, without its answer

Check normal Git status first. The scripts and Qwen repair are already saved;
do not redo the repair, extraction, database load or automated test suite.
Use `/home/nir/second-opinion` as the terminal working directory.

Tell Nir in ONE short sentence that you will parse the one saved page yourself.
His manual switch and instruction to follow this handoff authorise this trial;
do not ask him repeatedly to approve the same one-page task.

Run this metadata/preparation command. It makes no model/API/database calls.
It records the start and hashes, and prints the exact original task messages:

```bash
.venv/bin/python -c '
import sys, json, time, hashlib
from pathlib import Path
sys.path.insert(0, "kitchen")
from index_common import Context, arguments, fingerprint, require, save
from index_extract import cached_source
from index_prompts import PARSE
from toc_evidence import pdf_identity
ctx = Context(arguments("manual comparison preparation").parse_args(["HARRISON-22"]))
source = cached_source(ctx, 4044, pdf_identity(ctx.pdf))
diagnostic = ctx.path("index-diagnostic-4044-20261024T151351817100Z.json")
original = json.loads(diagnostic.read_text())
require(original["prompt_hash"] == fingerprint(PARSE), "original prompt has changed")
body = original["requests"][0]["body"]
require(body["messages"][1]["content"] == ctx.path("index-4044.txt").read_text(), "source text has changed")
start = ctx.path("manual-cloud-4044-start.json")
answer = ctx.path("manual-cloud-4044-answer.json")
require(not start.exists() and not answer.exists(), "a manual trial already exists; preserve it and report")
paths = [ctx.path(s) for s in ("index-4044-source.json", "index-4044.txt", "index-4044.json", "index-entries.json", "index-4044-source-check.json")]
paths += [ctx.image(4044), diagnostic]
paths += sorted(Path("kitchen").glob("*.py"))
hashes = {str(p): hashlib.sha256(p.read_bytes()).hexdigest() for p in paths}
save(start, {"started_unix": time.time(), "input_identity": ctx.identity, "source": source, "hashes_before": hashes})
print("SYSTEM INSTRUCTION:\n" + body["messages"][0]["content"])
print("\nINDEX PAGE TEXT:\n" + body["messages"][1]["content"])
'
```

If this stops on an evidence check or an existing trial, report and STOP.
Do not erase a previous trial to start over. No network fallback is needed.

## 4. Do the task yourself and save your FIRST answer

Read the printed system instruction and page text. Perform that parsing task
yourself. Keep the required schema, literal source wording and all references.
Save your FIRST complete JSON answer, without Markdown fences or commentary, to:

`kitchen/logs/HARRISON-22-manual-cloud-4044-answer.json`

Use the normal file-editing tool (apply_patch); this creates only an ignored
answer file, not a Python script. Do not overwrite the normal index-4044.json.
Do not change code, run another model, look at Qwen's answer first, add a new
prompt, or hand-fix your answer after seeing validation errors. Preserve the
first answer even if it fails. A later experiment needs Nir's agreement.

Do not fill the chat with the full JSON. Nir cannot scroll/read long screens.
This is one foreground attempt; Nir can interrupt it in OpenCode. Do not
claim that a terminal timeout hard-limits your own model response generation.

## 5. Validate and compare using the EXISTING code

After saving your answer, run this command. It calls no model and edits no
scripts. It reads Qwen's saved answer only NOW, checks your answer against the
real source with the production validators, compares reference coverage, and
saves a separate local result. It does not promote your answer into production.

```bash
.venv/bin/python -c '
import sys, json, time, hashlib
from pathlib import Path
from collections import Counter
sys.path.insert(0, "kitchen")
from index_common import Context, arguments, require, save
from index_extract import cached_source
from index_pages import ground_entries, assemble, citation_unit
from toc_evidence import pdf_identity
ctx = Context(arguments("manual comparison validation").parse_args(["HARRISON-22"]))
start = json.loads(ctx.path("manual-cloud-4044-start.json").read_text())
require(ctx.identity == start["input_identity"], "book/map inputs changed; stop")
result_path = ctx.path("manual-cloud-4044-comparison.json")
require(not result_path.exists(), "comparison already exists; preserve it and report")
before = start["hashes_before"]
after = {p: hashlib.sha256(Path(p).read_bytes()).hexdigest() for p in before}
require(before == after, "source, Qwen evidence or scripts changed; stop")
cached_source(ctx, 4044, pdf_identity(ctx.pdf))
result = {"mode": "Nir manually selected the cloud model in OpenCode", "elapsed_wall_seconds_including_tools": round(time.time() - start["started_unix"], 3), "scripts_and_original_evidence_unchanged": True}
try:
    answer = json.loads(ctx.path("manual-cloud-4044-answer.json").read_text())
    text = ctx.path("index-4044.txt").read_text()
    grounded = ground_entries(answer, text, 4044, str(ctx.image(4044)))
    require(grounded or len(text.strip()) < 30, "reader returned no entries from a nonempty page")
    entries, counts = assemble([grounded], ctx, citation_unit(ctx))
    original = json.loads(ctx.path("index-diagnostic-4044-20261024T151351817100Z.json").read_text())["answer"]
    def refs(a):
        return Counter(p for e in a["entries"] for p in e["pages"] + [p for s in e["subentries"] for p in s["pages"]])
    ours, qwen = refs(answer), refs(original)
    result.update({"production_grounding_and_assembly_pass": True, "entries": len(grounded), "subentries": sum(len(e["subentries"]) for e in answer["entries"]), "reference_tokens": sum(ours.values()), "qwen_reference_tokens": sum(qwen.values()), "missing_reference_tokens_vs_verified_baseline": sum((qwen - ours).values()), "extra_reference_tokens_vs_verified_baseline": sum((ours - qwen).values()), "assembly_counts": counts})
except (ValueError, KeyError, TypeError) as exc:
    result.update({"production_grounding_and_assembly_pass": False, "error": str(exc), "error_type": type(exc).__name__})
save(result_path, result)
print(json.dumps(result, indent=2))
print("Local comparison file:", result_path)
'
```

If it fails, keep the answer/error and STOP. Do not change validators or silently
produce another answer. Passing structure and reference checks is useful but
does not establish medical accuracy or all-book reliability.

The original successful Qwen parse took 84.555 seconds in its direct reader
request. Your recorded wall time includes OpenCode/tool overhead and is not a
strictly comparable API-inference benchmark. Report that distinction honestly.
Neither classification nor the full book has been tested by this experiment.

## 6. Report and hand control back to Nir

Record a short entry in PROGRESS.md: which model Nir selected (exact UI label
if known; otherwise say unknown), first-answer path, validation pass/failure,
reference counts, elapsed wall time and its timing limitation, and unchanged
scripts/evidence. Keep page text and raw answers out of GitHub.

Reply briefly to Nir with the result and local comparison file path. Then say:
"Please switch back to GPT 6.1 Sol and ask it to read the manual comparison
result. We can then decide together which reader to use."

STOP. Do not choose the winner yourself, permanently switch the reader, start
classification, read another page/book, or begin the long process.

GPT next reads these local files, not a new model/API request:
- `kitchen/logs/HARRISON-22-manual-cloud-4044-start.json`
- `kitchen/logs/HARRISON-22-manual-cloud-4044-answer.json`
- `kitchen/logs/HARRISON-22-manual-cloud-4044-comparison.json`

The larger project handoff, Opus verbatim text and repair history remain in
`HANDOFF-2026-10-25-DEEPSEEK.md`. Its earlier next-step instructions are paused
for THIS manual-model comparison. The approved globe and BIBLE remain untouched.
