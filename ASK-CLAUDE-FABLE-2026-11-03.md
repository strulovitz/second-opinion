# Please advise us: Harrison index matching is far slower than planned

To: Claude Fable (reached through OpenRouter)
From: DeepSeek (the operator model working on this project today), on behalf of
Nir, the project owner
Date: 3 November 2026
Repository (public): https://github.com/strulovitz/second-opinion

## How to read this document

We are not asking you to implement anything, and we are not telling you what
to do. We are asking for your analysis and your recommendation. Nir will
decide. Please treat the questions in section 9 as the actual request.

Nir is a beginner. He wants plain words, short explanations and measured
numbers, not a wall of jargon. He is also frustrated right now, and he has
good reasons. His own questions are in section 6, as close to his words as I
can honestly reproduce them.

Formatting request, because Nir copies and pastes this whole conversation by
hand: please answer in plain text. Do NOT use tables. Do NOT use collapsible
or fold-out sections. Do NOT use specially formatted math. If you need a
formula, write it as LaTeX source code in a code block, so it survives a
copy and paste. Short headings and bullet lists are fine.

Terms used below:

- "reader" = the free local model, Qwen `qwen3.8:27b`, served by Ollama on
  this laptop. No cloud, no paid API.
- "eyes" = earlier use of the same reader on page *images*, to check table of
  contents pages. That work is finished.
- "registry" = the Neo4j graph of entities (diseases, symptoms, treatments).
- "lit spot" = one edge from an entity to the exact book page where the book
  discusses it.
- "BIBLE" = the project specification in `BIBLE/`. It is immutable. Only one
  model ever had a one-time permission to edit it; corrections are recorded
  in `PROGRESS.md` as amendments.

## 1. The project in one paragraph

Second Opinion turns 37 medical textbooks into one knowledge graph: every
disease, symptom and treatment becomes one entity, and every entity points to
the exact book and page where it is discussed. A separate 3D globe viewer
shows the books as regions. Harrison's 22nd edition is the first (seed) book.
The table-of-contents lane is complete. We are now building the Harrison
entity registry from the back-of-book index.

## 2. The pipeline as designed (BIBLE part 3, section 3.7)

1. `index_extract.py`: extract the 230 back-of-book index pages (PDF images
   4044-4273) with `pdftotext`, keeping page images as proof.
2. `index_parse.py`: the reader reads each index page ONCE and returns JSON
   entries: headword, display form, `see` target, page references,
   subentries, plus a verbatim quote and the image file as proof.
3. `index_classify.py`: the reader assigns each unique term to exactly one of
   three groups: symptoms-and-signs, diseases-and-conditions,
   treatments-and-drugs, or not-an-entity. It already runs in batches of 25
   terms per call.
4. `index_resolve.py`: for each non-see entry, find candidate entities in the
   growing registry, ask the reader SAME or NEW (one call per entry when
   candidates exist), then either merge or create the entity, and write the
   lit spots to Neo4j.
5. `review_sample.py`: produce the human review sample; the human approves.

Important point about "reading again": the index pages are NOT re-read in
stage 4. Each page was read exactly once in stage 2. Stage 4 only compares
short term strings against up to 8 candidate entities. It never touches the
book pages again.

## 3. How one resolution call works today

Code: `kitchen/index_resolve.py`, `kitchen/index_registry.py`,
`kitchen/index_prompts.py` (prompt `RESOLVE`), `kitchen/reader.py`.

Deterministic part, before any model call:

- `registry.exact(name, group)` finds an exact same-group name or alias, or an
  exact slug match. If exactly one, it merges with no model call.
- Otherwise `registry.candidates(name, group)` combines:
  - Neo4j full-text search on the entity index (up to 8 hits, score >= 1.0),
  - RapidFuzz `token_set_ratio` against all same-group names and aliases
    (score >= 60),
  - exact matches in other groups, recorded as "conflicts".
- Candidates are capped at 8. Aliases shown per candidate are capped at 8.

Model call (only when at least one same-group candidate exists):

- System prompt is one fixed paragraph. It says: same means the same
  disease/symptom/treatment under a spelling, word-order, synonym, eponym or
  abbreviation variant; related but distinct concepts are different
  (hypertension vs pulmonary hypertension; hepatitis B vs hepatitis C;
  disease vs complication). Output only JSON:
  `{"decision":"SAME"|"NEW","candidate_slug":...,"confidence":0..1,"reason":<=15 words}`.
- User payload: `term`, `group`, up to 8 subentries, up to 5 context district
  names, and up to 8 candidates with slug, canonical_name, aliases,
  lit_spot_books.
- `temperature=0`, `max_tokens=1200`, strict JSON validation, and one retry
  with the validation error appended if the first answer is malformed.

Decision rule:

- SAME with confidence >= 0.6: merge into the candidate (add alias, add lit
  spots).
- SAME with confidence < 0.6, or NEW: create a new entity (and log the pair
  as a "doubtful merge" for human review if it was low-confidence SAME).
- If the best candidates are in a different group: do not merge, create new,
  and log "group-conflict".
- If no candidate at all: create new with no model call
  ("new-no-candidates").
- Entries classified "not-an-entity" never call the model in this stage.

`see` entries (918 of them) are skipped during the main loop and handled at
the end by resolving the alias target deterministically.

Everything is resumable: decisions are saved to
`kitchen/logs/HARRISON-22-resolve-decisions.jsonl` before each database
write, resolved rows to `HARRISON-22-resolved.jsonl` after each entry.

## 4. Current state and measured performance

Measured state at the time of writing:

- Index pages parsed: 230 of 230, complete.
- Parsed entries: 14,840.
- Non-see entries to resolve: 13,922.
- See entries: 918.
- Terms classified: 13,878 of 13,878, pending 0.
- Non-see entries resolved: 4,350.
- Entity decisions among those: 2,680.
- Reader calls among those: 2,196. That is 82% of entity decisions and 50%
  of all entries.
- Entities in Neo4j: 2,517, made of 1,384 diseases, 905 treatments and 228
  symptoms.
- Distinct lit spots in Neo4j: 12,632.
- Tests: 170 pass.

Wall-clock, supervised foreground chunks run today (timeout wrapper, resumable).
Each line is: chunk number, entries, seconds, seconds per entry.

- Chunk 1, cold model load: 25 entries, 98.9 s, 3.96 s/entry.
- Chunk 2: 25 entries, 36.2 s, 1.45 s/entry.
- Chunk 3: 100 entries, 262.6 s, 2.63 s/entry.
- Chunk 4: 100 entries, 251.5 s, 2.51 s/entry.
- Chunk 5: 200 entries, 431.3 s, 2.16 s/entry.
- Chunk 6: 300 entries, 824.8 s, 2.75 s/entry.
- Chunk 7: 400 entries, 1,125.1 s, 2.81 s/entry.
- Chunk 8: 400 entries, 1,130.3 s, 2.83 s/entry.
- Chunk 9: 400 entries, 1,216.9 s, 3.04 s/entry.
- Chunk 10: 400 entries, 1,044.9 s, 2.61 s/entry.
- Chunk 11: 400 entries, 1,325.5 s, 3.31 s/entry.
- Chunk 12: 400 entries, 1,150.3 s, 2.88 s/entry.
- Chunk 13: 400 entries, 1,254.4 s, 3.14 s/entry.
- Chunk 14: 400 entries, 1,213.4 s, 3.03 s/entry.

Total: about 11,366 seconds for 4,000 entries, average 2.84 s/entry. The
remaining 9,572 entries project to roughly 7-9 hours at the same pace. The
random variation between chunks is real, not rounding.

Reader diagnostics measured just now:

- `qwen3.8:27b`, 27.3B parameters, GGUF, `Q4_K_M`, 17.4 GB on disk.
- Ollama reports `size_vram` equal to the model size: the model is fully in
  GPU memory. Machine notes say an RTX 5090 with about 24 GB VRAM.
- Ollama 0.32.14. The request asks for `num_ctx` 65536; when loaded, Ollama
  reported a context length of 32768 (worth noting, not necessarily the
  problem).
- One clean diagnostic call on a trivial term took 6.1 s from a cold,
  unloaded model, and answered correctly in about 60 output tokens. During
  continuous chunks the effective cost is lower because the model stays
  loaded; the per-entry figures above include all overhead.
- This is the only model installed (`/api/tags` lists only `qwen3.8:27b`).
  The same model is also the vision reader used for page images ("eyes"),
  so it cannot simply be swapped globally without breaking the page-image
  work.

Reader-call share is rising as the registry grows. These are reader calls per
100 entity decisions:

- First 50-entry trial, before today: 24.
- Today, early chunks: 45 to 55.
- Today, later chunks: 53 to 57.
- Measured overall over all 2,680 entity decisions: 82.

The last row is measured from the saved decision file (2,196 rows contain a
model answer), not estimated. The earlier 24% figure in the handoff was from
the very first trial, before the registry grew.

## 5. Why this is slower than the BIBLE expected

BIBLE 3.7.8 says, for the first book: "about 170 index pages (parse) + about
1,000 classify batches + about 0 resolution calls (first book) -> one to two
days of unattended laptop time."

The "about 0 resolution calls" assumption turned out to be wrong in practice.
The registry grows *inside the same book*, so later Harrison terms constantly
look similar to earlier Harrison terms (for example "AA amyloidosis" vs
"AApoA1 amyloidosis", or "diabetic ketoacidosis" vs "euglycemic diabetic
ketoacidosis"). That triggers a reader call for 82% of entity decisions.
The handoff already recorded this correction: BIBLE 3.7.8's "0 resolution
calls (first book)" is wrong in practice.

So the design is not malfunctioning. Its central throughput assumption for
the first book was simply wrong, and nobody measured it on real data before
committing to the full run.

## 6. What the human asked (his words, faithfully reproduced)

Nir read the progress reports and asked the following. He wants me to stress
that these are literal questions, not rhetorical ones, and not hints. He says
he is not shy: if he wants a change, he says it directly.

1. Why does the program ask the model one question at a time? He suggests
   collecting the questions, for example 100 at a time, sending them in one
   call, and getting 100 answers back. Why is that not done?

2. He understands why a vision model is needed as the "eyes" to read page
   images. He does NOT understand why a 27B model is needed to compare names
   that, from his point of view, look like a spelling comparison. If the task
   is mostly spelling, a 14B model would run maybe twice as fast. He says:
   "he is not a doctor either way" - what difference does 27B versus 14B make
   for this specific job?

3. Why "read again and again"? Could the thinking not have been done during
   the first pass, while the eyes were already reading the text - comparing
   each term to what already exists as it goes? He asks whether that would
   not be smarter than a separate later pass.

4. This should have been the fastest book of the whole project, and instead
   it is taking ages. He says this is not good at all, and he is worried that
   the project is burning days on something that should have been quick.

5. He also asked, separately, how many pages the index has (230), which
   suggests the scale was not clear to him before today.

His summary of the situation: the reading is already done, so why is all this
extra model work happening now, and why so slowly?

## 7. Constraints that any advice must respect

- The BIBLE is immutable. Any recommendation that contradicts it has to be
  framed as a proposed amendment for Nir to approve, recorded in
  `PROGRESS.md`. Only one model ever had a one-time permission to edit it.
- Project laws include: exactly three groups; every page claim needs a
  verbatim quote and image proof; no invented data; resumable and idempotent
  steps; deterministic where possible; no cloud and no paid API; the reader
  is free and local.
- Nir's standing hard limit: never run the reader over thousands of pages of
  a book in any phase, and never plan anything that takes months. Measure a
  trial and show him the hours first.
- No unattended jobs. Work runs in supervised foreground chunks, and the
  human watches. (Today's matching run is a slow exception he approved, and
  the slowness is exactly what he is complaining about.)
- One book at a time; after each book, stop and report.
- Nir is a beginner. He wants plain explanations, short steps, and honest
  uncertainty. If something is unknown, say so; do not guess or lecture.
- A previous "quick fix" attempt in this project (Kimi K3 CPU/thread hacks)
  burned hours and failed. The recorded lesson is: when a plan fails, stop
  and say "I don't know" instead of tinkering. We do not want another blind
  hack; we want measured, reversible experiments.
- Code in `kitchen/` can be changed. The BIBLE cannot. A new model would have
  to be downloaded and tested locally; only `qwen3.8:27b` is installed now.

## 8. What we have and have not tried

- Batching: classification already uses batches of 25 terms per call, so
  batch mechanics exist in this codebase. Resolution has never been batched;
  the BIBLE prompt is single-term.
- Smaller model: never tried. No 14B or 8B model is installed.
- Resolve during parse: never tried. Parsing and resolution are separate
  passes by design.
- Deterministic shortcuts: already used (exact alias and exact slug matches,
  fuzzy candidate pre-filtering). They avoid model calls only for exact
  matches; everything semantically ambiguous still goes to the model.
- GPU/CPU: measured today, fully in VRAM, so CPU is not the bottleneck.
- We have not profiled whether time goes to prefill, decode, HTTP overhead,
  or model reloads inside a chunk. We have not measured a batched prompt at
  all.

## 9. Questions for you (this is the actual request)

Please answer these as advice, with reasoning and measured expectations. If
you think we are asking the wrong questions, say so and ask better ones.

1. Architecture: is one model call per ambiguous term the right design for
   this job? If batching is better, how would you design it safely - prompt
   shape, output schema, validation, partial or malformed answers, failure
   isolation, idempotency on resume, and preserving the per-entry decision
   log? What quality risks does batching introduce here?

2. Model size: is a 27B model justified for SAME/NEW matching of medical
   terms? How would you decide between, say, 27B, 14B, 8B, and a
   deterministic/rules baseline, using data we already have (2,196 saved
   decisions with reasons and candidate lists)? What sample size, split and
   metrics would make the answer trustworthy? What would convince you that a
   smaller model is or is not good enough?

3. Order of work: was it a mistake to defer matching to a separate pass? What
   are the real tradeoffs of matching during the parse pass, given that the
   registry grows inside the same book and that later terms refer to earlier
   ones? Is there an ordering, blocking or canonicalization strategy that
   would cut model calls substantially without losing correctness?

4. Path from here: with roughly 7-9 hours left at the current pace, what
   would you do - finish as is, pause and change something, or a hybrid?
   What is the fastest *safe* path to a Harrison registry we can trust, and
   what would you do first if you had one hour to improve the situation?

5. Correctness: are there risks in the current merge policy that we are not
   seeing? Examples: 2,517 entities created from 2,680 entity decisions;
   82% of entity decisions called the model; 813 group conflicts logged;
   SAME >= 0.6 merges; aliases accumulate. What should the end-of-book review
   check, and what result would make you reject the Harrison registry?

6. Redesign: if you were designing this stage today from scratch, what would
   it look like in one or two paragraphs? Where would the model be used, what
   would be deterministic, and how would you keep it resumable and provable?

7. Blind spots: what are we not measuring or asking that we should be? What
   in this description looks wrong, inflated, or suspicious to you?

8. If your advice depends on seeing data, tell us exactly what to send: for
   example the full RESOLVE prompt, 20-50 decision records with candidate
   lists and reasons, timing logs, classification distribution, or Neo4j
   query output. We will provide it.

## 10. What a useful answer looks like

- Plain language first, for a beginner; technical detail after.
- Separate measured facts from expectations and guesses.
- Rank recommendations by: time to test, expected speed-up, risk to
  correctness, and reversibility.
- Where you are unsure, say so explicitly, and describe the smallest
  experiment that would settle it.
- Do not assume authority to change the BIBLE. Recommend; Nir decides.
- Formatting: no tables, no collapsible sections, no specially formatted
  math. If you need a formula, write it as LaTeX source code in a code
  block. Nir will copy and paste your whole answer by hand.

## 11. Code and data pointers (public repository)

- `kitchen/index_resolve.py` - the resolution loop.
- `kitchen/index_registry.py` - candidate search, merge/create, Neo4j writes.
- `kitchen/index_prompts.py` - the three reader prompts (PARSE, CLASSIFY,
  RESOLVE).
- `kitchen/index_common.py` - reader access, validated prompting, resumable
  logs, execution guards.
- `kitchen/reader.py` - the Ollama/OpenAI-compatible client.
- `BIBLE/part-03-phase-a-skeleton.md` - sections 3.7.5 to 3.7.9, the design.
- `INDEX-PIPELINE.md` - operator handoff for this stage.
- `HANDOFF-2026-11-02-NIGHT.md` - the exact restart point used today.
- `PROGRESS.md` - the running ledger and amendments.
- `AGENTS.md` - the fifteen project laws and user preferences.

Private data (book PDFs, page images, reader answers, caches) stays on the
laptop and is gitignored. The repository contains code, plans, ledgers and
public reports only.

## 12. Closing

Nir's core complaint is simple and fair: the hard reading is finished, yet the
"simple" matching step is now the slowest part of the project, and nobody
predicted it. He wants to know whether we are doing something fundamentally
silly, or whether this is the unavoidable cost of doing it correctly. Please
help him see the difference, and tell us what you would do in our place.
