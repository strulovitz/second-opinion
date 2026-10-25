# Hand-off to SMART (GPT 6.1 Sol): the Harrison index extraction-key mismatch

Written: 25 October 2026, morning.
Author: DeepSeek V4.1 Flash (CHEAP tier), at Nir's request.
For: GPT 6.1 Sol (SMART tier).
Tier rule: this file describes a SOFTWARE defect. Writing or changing code is
SMART work (BIBLE Part 8 section 6.3). DeepSeek must not repair it.

## 1. What Nir asked for, in his words

> "thank you for noticing, i do not want you to fix things, i want you only to do
> simple work, please write a detailed hand-off to our smart model GPT 6.1 Sol,
> about what is the problem (what you said blocked note etc, and then i will
> switch model, and ask GPT to fix it, and then i will come back to you"

So: diagnose and repair the defect below, then hand the book-by-book bookkeeping
back to CHEAP. Nir supervises. Nothing runs unattended.

The user-visible symptom is only one sentence: with the current files, a full
Harrison index run dies on its first index page before the reader is ever called:

```
ValueError: stale extraction for PDF 4044; archive the old index cache, do not mix sources
```

The rest of this file proves exactly where that comes from and what it does and
does not mean. Read all of it before changing anything.

## 2. Starting state (verified this morning, read-only)

Repository: `/home/nir/second-opinion`, GitHub `strulovitz/second-opinion`, branch
`main`. Local HEAD equals `origin/main`.

```
$ git -C ~/second-opinion status --short --branch
## main...origin/main
$ git -C ~/second-opinion rev-parse HEAD origin/main
c65b80d8bd5d0d382c87725f0d09df6689e83f59
c65b80d8bd5d0d382c87725f0d09df6689e83f59
$ git -C ~/second-opinion log --oneline -3
c65b80d 3.7 repair Qwen index parsing and save overnight handoff
a464c7a 3.7 HARRISON-22 index trial blocked on page 1; hand-off to SMART
5c02774 4 8 Nir's hard limit: Qwen never on thousands of pages, measure and show hours first; cancel read-every-page plan
```

Working tree clean. No index job is running. Ollama had no model loaded
(`ollama ps` printed only the header), so no reader work can happen by accident.

Everything in this document was gathered with read-only commands. No extraction,
no Qwen call, no database query, no cache was written or deleted, and no
`index_pipeline.py` / `index_extract.py` / `index_parse.py` run was started.

Existing Harrison index state in `kitchen/logs/` (all ignored by git):

```
-rw------- 1 nir nir  37402 Oct 24 18:16 HARRISON-22-index-4044.json          (successful Qwen parse, 1 page)
-rw------- 1 nir nir    794 Oct 23 21:19 HARRISON-22-index-4044-source.json   (extraction receipt)
-rw------- 1 nir nir   6305 Oct 23 21:19 HARRISON-22-index-4044.txt           (extracted page text)
-rw------- 1 nir nir 197894 Oct 24 18:16 HARRISON-22-index-entries.json       (assembled entries, complete=false)
         no HARRISON-22-classified.jsonl                                       (classification never run)
```

`HARRISON-22-index-entries.json` reports `entries = 75`, `complete = false`,
1 of 230 pages. The three raw diagnostic responses from 24 Oct are still in
`kitchen/logs/HARRISON-22-index-diagnostic-4044-20261024T15*.json`.

## 3. The exact defect

`kitchen/index_extract.py` line 23 computes the cache key of an extracted index
page as:

```python
key = fingerprint([ctx.identity, identity, page, layout, columns, "pdftotext-v1"])
```

and lines 24-27 refuse to continue when the stored key differs:

```python
if meta.exists():
    saved = json.loads(meta.read_text())
    require(saved["key"] == key and target.exists() and fingerprint(target.read_text()) == saved["text_hash"],
            f"stale extraction for PDF {page}; archive the old index cache, do not mix sources")
```

`ctx.identity` is defined in `kitchen/index_common.py` lines 86-87 as:

```python
self.identity = fingerprint({"book": self.book, "geography": self.geography,
                             **({"mode": "chapter-fallback"} if self.fallback else {})})
```

`self.geography` is the whole `data/export/geography/geography.json`: all 5,334
territories with their coordinates, areas, colour, raster code and bounding
boxes. So an extracted *text* page is keyed to the current approved MAP.

Measured consequence (see section 4): every time the approved geography changes,
every already-extracted index page becomes "stale", although the page text,
the PDF, the source image and the receipt hashes are all unchanged. Three
geography installs have happened since the indexes work began (23 Oct seating
export, 23 Oct honeycomb, 24 Oct Goldberg).

## 4. The proof: which input changed, and which did not

The probe below is read-only: it constructs the same `Context` the scripts use
and recomputes the same key. It writes nothing.

```bash
cd ~/second-opinion && .venv/bin/python - <<'PY'
import json, sys
from pathlib import Path
sys.path.insert(0, "kitchen")
from index_common import Context, arguments, fingerprint
from toc_evidence import pdf_identity

a = arguments("probe").parse_args(["HARRISON-22"])
ctx = Context(a)
saved = json.loads(Path("kitchen/logs/HARRISON-22-index-4044-source.json").read_text())
cur_pdf = pdf_identity(ctx.pdf)
print("saved key   :", saved["key"])
print("current key :", fingerprint([ctx.identity, cur_pdf, 4044, False, False, "pdftotext-v1"]))
print("pdf_identity equal:", cur_pdf == saved["pdf_identity"])
txt = Path("kitchen/logs/HARRISON-22-index-4044.txt").read_text()
print("text hash equal   :", fingerprint(txt) == saved["text_hash"])
import hashlib
img = Path(saved["image_file"])
print("image hash equal  :", hashlib.sha256(img.read_bytes()).hexdigest() == saved["image_hash"])
print("ctx.identity      :", ctx.identity)
PY
```

Actual output on 25 Oct 2026:

```
saved key          : f87b7f6f930d91d37599df18ab0abbb035a486d0a885231390edcf07aef80e87
current key        : ded7ce584a533e0072df154adfe77bc6ae232afff84ff80185b9b187c5b814cc
same?              : False
current ctx.identity: a71c67fba1fb6bb1f7956dd57175f7f0fdff27fe5e8e3cca9f67b4f4b21df3df
current pdf_identity equal to saved: True
  (no field of pdf_identity differs)
text file hash == saved text_hash: True
text file chars: 6226
image exists: True
image hash matches saved: True
```

So the PDF, the text and the page image are provably the same evidence as when
the receipt was written. Only the composite key differs.

### 4.1 Where the saved key came from (cause proven, not guessed)

The 23 Oct honeycomb install and the 24 Oct Goldberg install each left a backup
of the geography they replaced. Recomputing the key from those backups:

```bash
cd ~/second-opinion && .venv/bin/python - <<'PY'
import json, sys
from pathlib import Path
sys.path.insert(0, "kitchen")
from index_common import fingerprint
books = json.loads(Path("kitchen/books.json").read_text())
b = [x for x in books if x["book_id"] == "HARRISON-22"][0]
saved = json.loads(Path("kitchen/logs/HARRISON-22-index-4044-source.json").read_text())
for name in ("before-honeycomb-20261023T201406461287Z", "before-honeycomb-20261024T112358007494Z"):
    g = json.loads((Path("kitchen/logs")/name/"export-geography/geography.json").read_text())
    ident = fingerprint({"book": b, "geography": g})
    key = fingerprint([ident, saved["pdf_identity"], 4044, False, False, "pdftotext-v1"])
    print(name, len(g), ident[:12], key[:12], key == saved["key"])
PY
```

Actual output:

```
before-honeycomb-20261023T201406461287Z 5334 974fc08993f9 f87b7f6f930d True
before-honeycomb-20261024T112358007494Z 5334 45983c2ebfa6 db9203f773fb False
```

The saved key is reproduced EXACTLY by the geography that was live before the
23 Oct honeycomb was installed. `books.json` has not changed since commit
`a816e30` (23 Oct 21:01), so the book record is not the variable; the geography
is. Timeline:

```
a816e30  23 Oct 21:01  approved seating exported          <- receipt written at 21:19 against this map
726d5c4  23 Oct 23:42  honeycomb geography committed      <- all extraction receipts became stale
d60a3ed  24 Oct 16:08  Goldberg geography committed       <- stale again (currently live)
c65b80d  24 Oct       Qwen parse repair committed         (no geography change)
```

### 4.2 What the successful parse cache is bound to (important)

`kitchen/index_parse.py` line 31:

```python
key = fingerprint(["index-parse-v2-no-reasoning", source, ctx.identity, PARSE, OCR if needs_ocr else None, model, ...])
```

`source` is the whole extraction-receipt dictionary, so the parse key depends on
both the receipt and the geography. The cached parse and the assembled entries
are nevertheless CURRENT: `HARRISON-22-index-entries.json` has
`input_identity = a71c67fba1fb6bb1f7956dd57175f7f0fdff27fe5e8e3cca9f67b4f4b21df3df`,
which is exactly today's `ctx.identity`. That is consistent: the 24 Oct replay
ran after the Goldberg install, reading the old text file directly after
re-verifying the PDF/text/image hashes.

The practical result is an asymmetry:

- `index_parse.py` would accept page 4044 from cache today (its key matches).
- `index_extract.py` refuses page 4044 first, and `index_pipeline.py` runs
  extract before parse, so the pipeline stops at extraction and never reaches
  the cached parse or any Qwen call.

## 5. Why this matters, and why it is not a data corruption

- Nothing is corrupted. Proven above: PDF identity, text hash, image hash and
  receipt hashes all still match, and the parse cache is current.
- The refusal is the safety check doing its job with an over-broad input list.
  Extraction output depends only on: the PDF bytes, the PDF page number, and
  the flags `--layout` / `--columns` (plus the pdftotext tool version). It does
  NOT depend on latitudes, longitudes, areas, colours, raster codes or bboxes.
- Because geography is approved and rebuilt by the human, a map rebuild will
  keep invalidating extraction receipts for every book, for ever, unless the
  input list is corrected or a deliberate reconciliation path is added.
- There is a second latent fragility of the same kind: `pdf_identity` in
  `kitchen/toc_evidence.py` includes `mtime_ns`, `ctime_ns`, `inode` and
  `device`. Moving, copying or re-downloading an unchanged PDF would also
  invalidate every receipt. It is NOT the cause today (the values match), but
  SMART should decide whether that is intended.
- The same `ctx.identity` is also used to guard review approvals
  (`Context.execution_guard`, `index_common.py` lines 110-125) and the
  `input_identity` written into `index-entries.json`. Any change to how identity
  is computed must be considered there too, or Harrison's later
  Checkpoint 3.5 approval record will not match.

## 6. What breaks today, exactly, and what does not

Breaks:

- `python kitchen/index_pipeline.py HARRISON-22` (and any `--stop-after`
  variant that runs extract) stops on page 4044 with the ValueError in
  section 1.
- Nothing else in the repository is broken. The viewer, geography, Neo4j load,
  TOC work and tests are untouched by this defect.

Does not break (worth keeping that way):

- `python kitchen/index_classify.py HARRISON-22 --limit 1` does not run
  extraction; it classifies from the cached parse. This is the one bounded
  reader trial Nir has not yet approved. It is NOT part of this repair and
  must not be used to test the repair.
- `python kitchen/index_pipeline.py HARRISON-22 --plan --limit 1` is metadata
  only and still works.

## 7. Decisions for SMART (do not start coding before deciding these)

The repair must preserve two things at once: (a) provenance stays honest, and
(b) the single successful Qwen answer (84.555 s, 75 entries, 112 subentries,
278 reference tokens) is not thrown away or silently re-derived.

Options, with the honest trade-offs. This list is not exhaustive; SMART may
propose a better one.

A. Narrow the extraction key. Remove `ctx.identity` (the book+geography hash)
   from the extraction key, keeping PDF identity, page, layout, columns and the
   tool version. Add a cache-version string so old receipts are not silently
   reinterpreted. Then the existing receipt on page 4044 becomes valid again
   by an explicit, documented rule, with no re-extraction, no Qwen call, and no
   cache deletion.
   Cost: touches the meaning of a provenance key; must be argued in
   PROGRESS.md and needs Nir's approval. Must also decide what to do with the
   old receipt's stored `key` field (the `source` dict is itself inside the
   parse key).

B. Re-stamp the receipt after re-verifying every other hash. A one-off, audited
   reconciliation step for page 4044 that re-checks PDF identity, text hash,
   image hash, then rewrites only the `key` field, archiving the previous
   receipt first.
   Cost: it edits a provenance artefact, which the BIBLE's spirit dislikes
   ("do not hand-edit hashes"). It is defensible ONLY as an explicit recorded
   human-approved action with the old file kept. It also changes the `source`
   dict inside the parse key, so the cached parse key must be re-derived and
   checked, not assumed.

C. Treat the old caches as history and re-extract page 4044 with defaults.
   Cheap in wall-clock (pdftotext, no model) but the new receipt changes
   `source`, which changes the parse key, which will invalidate the successful
   Qwen parse and force one new Qwen call (about 85 s measured, plus it may
   differ from the cached answer). Costs evidence, not money.
   If chosen, archive the current page files first and record why.

D. Do nothing to the key; add an explicit `--accept-old-receipt` style flag
   that re-verifies PDF/text/image hashes and proceeds.
   Cost: a second code path that every later book must also navigate; easy to
   misuse; probably worse than A for the long run.

Whatever is chosen must answer these questions explicitly in PROGRESS.md:

1. Which inputs genuinely determine an extracted index page's text?
2. Does the chosen rule keep the existing receipts honest, or does it change
   their meaning? If it changes meaning, say so plainly.
3. What happens on the NEXT approved geography rebuild (there will be one if a
   book is added or removed)? Will the receipt stay valid or must the rule
   cover that too?
4. Does the review-approval guard (`execution_guard`) and the
   `input_identity` written into `index-entries.json` need the same treatment
   so Checkpoint 3.5 can be recorded later?
5. If any Qwen call becomes necessary, what is the measured cost and did Nir
   approve it?

## 8. Hard constraints (from Nir, the BIBLE and the project rules)

- DO NOT edit anything in `BIBLE/`. Only Claude Opus 5.5 had a one-time
  permission. Write findings and Nir's decisions in `PROGRESS.md`.
- Nir's hard limit: the free reader (Qwen `qwen3.8:27b`) is never run over
  thousands of pages in any phase. Every reader job is measured on a tiny trial
  and its total shown to Nir in hours before it starts. Nothing may take months.
- Do not authorize or start a full 230-page index run, another book, a Freeze,
  Phase B, or any overnight/unattended job.
- Do not delete, overwrite or "clean" the successful parse, the assembled
  entries, the extracted text or the receipts. Archive instead of deleting.
- Do not hand-edit hashes or weaken provenance checks to get past an error.
- Do not change the reader model, Ollama settings, `kitchen/.env`, the viewer,
  the geography, `kitchen/books.json`, or Neo4j. Never print `.env`, passwords
  or tokens.
- Change as little code as possible. If a rule change is needed in more than
  one script, keep it in one place (`index_common.py`) and say so.
- Cache and log files under `kitchen/logs/` are gitignored: evidence must be
  pasted into `PROGRESS.md`, not committed as files.

## 9. How to verify the repair (all of it, on page 4044 only)

1. Re-run the probe in section 4 and show that the key comparison now agrees
   under the chosen rule, or that the deliberate re-stamp was applied, with the
   archived previous receipt named.
2. Show that the page's text hash, image hash and PDF identity are unchanged.
3. Show that `HARRISON-22-index-4044.json` (the Qwen parse) is still the SAME
   file content as before the change (compare a copy taken beforehand), or, if
   the rule invalidates it, say so and get Nir's approval for one new call with
   its measured time.
4. Run the metadata-only plan and show it still works:
   `.venv/bin/python kitchen/index_pipeline.py HARRISON-22 --plan --limit 1`
5. Run the existing test suite once after the change:
   `OPENBLAS_NUM_THREADS=2 .venv/bin/python -m unittest discover -s kitchen -p 'test_*.py'`
   (112 tests passed in 1.926 s on 24 Oct; state the new number).
   `git diff --check`.
6. If you add a test for this, make it synthetic (two different geography
   dictionaries, same text) so it proves the rule without touching the real
   caches.
7. Do NOT run `index_extract.py` for a new page, `index_parse.py` for a new
   page, `index_classify.py`, or the pipeline, to prove the fix. They either
   need the reader or do work beyond the defect.

## 10. What to leave behind for the next session

- A DONE entry in `PROGRESS.md` in the project Evidence format
  (COMMANDS / OUTPUT / FILES / COMMIT), naming the decision chosen and the
  quotations of Nir's approval.
- Update `BLOCKED` on the open 24 Oct entry: either resolved, with the exact
  evidence, or still open with the reason.
- Update CURRENT PHASE / NEXT STEP so the next CHEAP session knows the next
  step is still the one untested classification batch (25 terms, timed, with
  Nir's okay) and nothing else.
- Replace the three-line NEXT SESSION pointer in the project `AGENTS.md` with a
  pointer to the new state, without inflating that file.
- Commit only the code/tests/docs changed, with a message starting with the
  BIBLE section (`3.7 ...`). Never commit caches, PDFs, images, `.env`.

## 11. Plain summary for Nir (one paragraph)

The map was rebuilt twice after the first Harrison index page was processed.
The index code ties each extracted page to the exact map that existed when it
was extracted, so the page is now refused as "stale" even though the page
itself, its text, its image and its saved reader answer are all provably
unchanged. Nothing is lost. SMART only has to decide, and record, which inputs
should really lock an extracted index page, then apply the smallest change that
keeps the saved reader answer while making the key honest again. After that the
next step returns to DeepSeek: one timed classification batch of 25 terms, only
with Nir's okay.
