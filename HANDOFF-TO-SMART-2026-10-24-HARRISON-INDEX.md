# Hand-off to SMART (GPT 6.1 Sol) -- HARRISON-22 index trial blocked on page 1 (2026-10-24)

From: DeepSeek (executor)
To: GPT 6.1 Sol (SMART, project manager), at Nir's request
Read first: `AGENTS.md`, `HANDOFF-2026-10-24-DEEPSEEK.md` (Opus's step-by-step
instructions), `INDEX-PIPELINE.md`, and the `## BLOCKED` plus recent
`## DONE` entries in `PROGRESS.md`.

## Bottom line

The Harrison index trial stopped on the **first** index page (PDF 4044).
The free reader answered, but its answer failed the source-grounding check
twice: `subentry absent from its source block`. I then warmed
`qwen3.8:27b` (confirmed loaded in VRAM) and ran the same page again: the
same error, and 7m08s again. One page therefore costs about 7 minutes, which
projects to roughly **27 hours** for Harrison's 230 index pages -- over
Nir's hard limit even if the check had passed.

Per Opus's rule 8 (same generic software error twice -> SMART), I stopped.
I changed no code, no BIBLE file, no map/viewer file, and no model setting.

## What Nir wants

Continue the Second Opinion project, **one book at a time**, with Nir
watching. The current book is HARRISON-22 (505 chapters, index PDF pages
4044-4273, 230 pages). The immediate task is the back-of-book index: parse
its pages, classify the terms, link them to chapters, review, then Nir
approves. Do not start another book without his okay.

Nir's hard limit, in his own words (recorded in PROGRESS.md / memory):
"i never approved for qwen to go on thousands of pages per book, in ANY
phase, NEVER EVER ... not months, never months". Measure a trial, compute
the hours, show him the number, and only start the full run after he agrees.

## What was done in this session, in order

All commands were run from `/home/nir/second-opinion` with the project venv.
Starting point was clean: HEAD `5c02774` ("Nir's hard limit ...");

```bash
git status --short     # empty
git log --oneline -3   # 5c02774, fb951fc, 25349b2
```

1. Reader test (step 2 of Opus's hand-off):

   ```bash
   .venv/bin/python kitchen/reader.py
   # {'ok': True}
   ```

2. Read-only plan (step 3):

   ```bash
   .venv/bin/python kitchen/index_pipeline.py HARRISON-22 --plan --limit 1
   .venv/bin/python kitchen/load_geography.py
   ```

   Output was exactly as expected:

   ```text
   HARRISON-22 extract: index PDF 4044-4273; 230 pages; 505 districts; limit=1; read-only plan
   HARRISON-22 parse: index PDF 4044-4273; 230 pages; 505 districts; limit=1; read-only plan
   HARRISON-22 classify: index PDF 4044-4273; 230 pages; 505 districts; limit=1; read-only plan
   HARRISON-22 resolve: index PDF 4044-4273; 230 pages; 505 districts; limit=1; read-only plan
   HARRISON-22: pipeline stopped after resolve; no unattended process started
   Geometry: 37 books; 5334 territories
   Dry run; no database access or writes
   ```

3. Map loaded into Neo4j with Nir's explicit okay (step 4):

   ```bash
   .venv/bin/python kitchen/load_geography.py --apply
   # [{'books': 37, 'territories': 5334, 'child_links': 5297, 'book_links': 37}]
   # [{'level': 'continent', 'count': 37}, {'level': 'district', 'count': 4763},
   #  {'level': 'province', 'count': 534}]
   ```

   Neo4j now holds the approved map (37 continents + 534 provinces + 4,763
   districts = 5,334 territories). The load printed three harmless
   "property key does not exist" notices from its pre-check query; they are
   warnings, not errors. No git files changed by this step.

4. Bounded trial (step 5), first attempt:

   ```bash
   time .venv/bin/python kitchen/index_parse.py HARRISON-22 --limit 1
   # INDEX STOPPED: ValueError: reader failed validation twice:
   # The previous answer failed validation: subentry absent from its source block. Fix it using only the source.
   # real 7m2.840s

   time .venv/bin/python kitchen/index_classify.py HARRISON-22 --limit 1
   # INDEX STOPPED: FileNotFoundError: .../kitchen/logs/HARRISON-22-index-entries.json
   # real 0m0.277s
   ```

   The classify error is a consequence of the parse failure: `index_parse.py`
   never reached `assemble()`/`save()`, so `index-entries.json` was not
   written. Classification was therefore never timed.

5. Warm-up check, because Nir reasonably asked whether the 7 minutes was
   just Qwen waking up:

   ```bash
   time .venv/bin/python kitchen/reader.py       # real 0m5.806s
   curl -s localhost:11434/api/ps
   # [('qwen3.8:27b', 17399734598)]   <- 17.4 GB already in VRAM
   time .venv/bin/python kitchen/index_parse.py HARRISON-22 --limit 1
   # same ValueError, same wording
   # real 7m8.312s
   ```

   So the cost is generation, not model loading. The model was still loaded
   in VRAM after the second run.

## The failure, precisely

- Page: PDF 4044, the first page of Harrison's back-of-book index.
- Cached page text already existed from the 23 Oct pilot:
  `kitchen/logs/HARRISON-22-index-4044.txt` (6,226 chars, 210 lines) and
  `HARRISON-22-index-4044-source.json`. The text layer is clean and
  readable; no OCR was needed (`needs_ocr` is false).
- The page starts with a long italic-ish explanatory preamble ("Page
  numbers in bold indicate ..."), then the section letter `A`, then entries
  such as `AA amyloidosis, 899`, `AAG (autoimmune autonomic
  ganglionopathy), 3550`, `Abacavir`, `Abatacept`, etc.
- Each parse run makes up to **two** reader answers. Both failed validation
  (`kitchen/index_common.py:128-137`). Two runs = four rejected answers.
- No raw reader answer was saved, and no parsed page JSON was written to
  `kitchen/logs/` (the pilot files there are only the page text and its
  source/hash record). So the exact offending sub-entry is not recorded.
- `kitchen/logs/HARRISON-22-run.log` only has the 23 Oct extraction line:
  `2026-10-23T21:19:44 HARRISON-22 extract: new_pages=1; cached_pages=0; expected_pages=230`.
- Zero-byte lock files `kitchen/logs/HARRISON-22-index.lock` and
  `kitchen/logs/index-registry.lock` exist; I left them untouched.

## Likely cause (hypothesis; NOT proven)

`ground_entries()` (`kitchen/index_pages.py:35-69`) walks the reader's
entries in order. For each non-CONTINUED entry it finds the headword
literally in the page text starting from the previous match, then defines
that entry's source block as the text up to the next headword. Every
sub-entry and page reference must then appear literally inside that block
(`kitchen/index_pages.py:58`).

Page 4044 is unusual: it has the preamble and a standalone section letter
`A` before the first real headword. If the reader emits `A` as an entry (or
emits an entry whose headword first appears inside the preamble, e.g. the
`A` of "(Atlases)"), the cursor is placed there, the block boundaries shift,
and later sub-entries no longer fall inside their parent's block. That would
produce exactly this error, deterministically, no matter how many times the
reader is asked. A second possibility is simple non-literal normalisation
by the reader (dropped punctuation/parentheses) in a sub-entry text.

Do not treat this hypothesis as fact. The cheapest way to confirm it is to
capture the raw answer on validation failure (or run one direct
`reader.ask` call with the PARSE prompt on the cached text and save the
JSON). One such call costs about 3.5 minutes.

## Why I did not fix it myself

- Opus's rule 8: after the same generic error twice, stop and hand to SMART.
- Opus's step 2: do not change any model setting.
- The 27-hour projection is over Nir's hard limit; the answer cannot be
  "let Qwen grind". A faster method (likely a plain-code parser over the
  clean text layer, with the reader used only for ambiguous pages) needs a
  SMART decision.

## Recommended next steps (SMART's call)

1. Diagnose cheaply: save the raw failing answer, or make one direct reader
   call on the cached page text. Confirm whether the trigger is the section
   letter/preamble or literal-normalisation.
2. Decide the method. The index text layer is clean; consider a deterministic
   parser (indentation, headword lines, sub-entry lines, page-reference
   regex) and reserve Qwen for pages the plain parser cannot ground. This
   respects Nir's limit far better than 3.5 minutes per reader answer.
   If a Qwen path is kept, consider the existing `READER_NO_REASONING`
   switch (`kitchen/reader.py`) and measure whether it changes quality and
   time; do not change it silently.
3. Measure on 2-3 typical index pages, not only page 4044 (the first page
   has the preamble and may be harder than average). Compute total hours and
   show Nir before any full run. Get his explicit okay.
4. Run Harrison only, watched, one book. Then `review_sample.py HARRISON-22`
   and show Nir the review (Checkpoint 3.5). Record his exact approval words.
5. After Harrison is approved, the next book would be ADAMS-12. Do not start
   it unasked.

## Environment and evidence

- Repo: `/home/nir/second-opinion` (github.com/strulovitz/second-opinion).
- Python: `.venv/bin/python` in the repo.
- Reader: Ollama at `localhost:11434`, model `qwen3.8:27b` only. `reader.py`
  goes through the OpenAI-compatible `/chat/completions` endpoint; hidden
  reasoning is allowed by default. Do not print `kitchen/.env`.
- Index software: `kitchen/index_parse.py`, `index_pages.py`,
  `index_common.py` (`ask_checked`), `index_classify.py`,
  `index_pipeline.py`, `review_sample.py`; docs in `INDEX-PIPELINE.md`.
- Book data: `kitchen/logs/HARRISON-22-eyes.json` (505 chapters),
  `HARRISON-22-toc.json`, `HARRISON-22-index-4044.txt` / `-source.json`.
- Database: Neo4j is running and now contains the approved map. Counts as
  above. Do not re-run the load unless you first check its idempotence.
- Git at hand-off time: clean tree at `5c02774`, plus this hand-off file and
  one BLOCKED note in `PROGRESS.md` in the commit that adds them. Nothing
  under `kitchen/logs/`, no PDF, no page image and no `.env` is tracked.

## Do not

- Do not edit `BIBLE/`. Only Claude Opus 5.5 had a one-time permission.
- Do not touch `site/viewer/`, `site/data/geography/`,
  `data/export/geography/`, `kitchen/goldberg_*`, `kitchen/geography_*`,
  `kitchen/flower_map.py`, `kitchen/make_demo.py`.
- Do not reopen TOC checks, PDF-completeness checks or any book's chapters.
- No sudo, no installs, no unattended or overnight runs, no parallel books.
- Never print, copy or commit `kitchen/.env`.

## Nir's own words today

> "i do not understand what are you saying, that it takes a lot of time to
> warm up for the Qwen model? why don't you wake him up, wait, and then try
> and get a normal result please?"

We did exactly that: warm-up 5.8 s, model confirmed in VRAM, same page
re-run -> same error, same 7m08s.

## Copy-paste start for SMART

> Please read ~/second-opinion/HANDOFF-TO-SMART-2026-10-24-HARRISON-INDEX.md
> first, then AGENTS.md, PROGRESS.md (## BLOCKED and recent ## DONE) and
> INDEX-PIPELINE.md. The Harrison index trial is blocked on page 1. Diagnose
> it cheaply first, propose the fastest correct method, and show Nir the
> hours before any full run. One book only, with Nir watching.
