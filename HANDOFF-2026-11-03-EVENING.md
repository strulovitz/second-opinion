# HANDOFF 2026-11-03 EVENING -- Claude Fable to Claude Opus 5.5 (restart point)

Dear Opus: Nir switches to you for cost reasons. The design thinking for the
next stage is finished and written down in BIBLE/part-00-speed-charter.md
section 10 (ingestion system) and section 11 (small triage). Implement it
as written; do not redesign. Where it says "ask Nir", ask him with a short
plain-language question and pros/cons, one question at a time. He uses
lots of emojis in chat and likes them back; none in files. He cannot
scroll in OpenCode: keep replies short.

Read in this order, nothing else unless needed:
1. BIBLE/part-00-speed-charter.md (the rules; overrides every older part)
2. this file
3. newest block of PROGRESS.md only if a number is needed

## State (all pushed, all working on the live site)

- Library: 37 books, 135,325 pages in kitchen/logs/library.sqlite (pages,
  pages_layout, pages_fts, terms). Rebuild: speed_text.py --all (6 min),
  speed_index.py --all (2 s), speed_entities.py (5-6 min, loads Neo4j),
  speed_export.py (35 s, writes site/data/entities, districts, search.json).
  After any viewer change: kitchen/stamp_viewer.py (cache busting), commit, push.
- Numbers: 35,845 entities; 1,821,171 lit spots (115,787 index, rest
  full-text); 16 books have an index in the PDF, 21 do not; page offsets by
  code for 27/37 books; 10 books without offset have no full-text links
  (BENZON, BOLOGNIA, FIRESTEIN, GRAY, GUYTON, MURRAY, ROSEN, SABISTON,
  THOMPSON, YOUMANS).
- Viewer (Nir approved "not perfect, good enough"): lit chapters rise as
  neon book-coloured columns in 3D (layers.js buildColumns); columns persist
  when a chapter is opened; per-chapter cards list entities; 2D map is a
  generic click-centred Lambert azimuthal equal-area projection (map2d.js);
  search results rank exact/most-discussed first, hide empty names, always
  open in 3D; Enter jumps to the tab that has the word.
- Old pipeline (index_parse/classify/resolve) retired; old tests for the
  flower map and the resolver are stale and were not run.
- Cloud model spend so far: 0 dollars. All stages are code + local models
  (bge-m3 embeddings, qwen3:8b installed but unused).

## Nir's orders for the next session

- TURBO mode: field triage. Visual work is done; anything else visual gets
  the simplest thing that works, not perfect.
- Concentrate on SPEED of the whole future workflow and on COST. Spend as
  few tokens as possible: no exploratory screenshots, one-shot fixes, ask
  Nir instead of experimenting. Delegate grunt work (long runs, waiting,
  repetitive edits) to DeepSeek in OpenCode and let him hand back.
- Session cost so far was about 46 dollars; Nir considers 15 the right size.

## Next steps (in order)

1. Stage 4, the product: ingestion system. Nir hands over articles (PDF in
   kitchen/inbox/ or pasted text). A cheap cloud model (OpenRouter, via a
   small model-agnostic kitchen/worker.py with Ollama fallback) extracts the
   core claims once and files them as SOURCE nodes linked to entities; the
   entity card shows them as "Second opinion". Ask Nir first: PDF folder,
   pasted text, or both (he has not answered yet).
2. Page offsets for the 10 missing books (try the chapter-title FTS vote
   with looser thresholds; if it fails, say so and move on).
3. Junk names cleanup only if cheap (subentry fragments, quoted names).
4. Synonym merge (heart attack = myocardial infarction) is deliberately NOT
   done; only if Nir asks, via embedding band + batched cheap model.

## Do not

- Do not re-run or revive index_resolve.py / index_parse.py.
- Do not touch the 3D sand table beyond the columns.
- Do not commit site/data/entities, districts, search.json or library.sqlite
  (gitignored by design; the site is served from this laptop).
