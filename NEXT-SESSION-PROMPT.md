# NEXT SESSION PROMPT -- Second Opinion, finish the product (written 3 Nov 2026 night by Claude Opus 5.5 for itself)

Whoever opens a session on Second Opinion: read THIS file first, act on it,
and tick its steps in PROGRESS.md. It does not replace BIBLE Part 0 (the
rules) or BIBLE Part 2 section (E) (the edge schema); it orders the work so
the product gets finished. If something here conflicts with the BIBLE, ask
Nir with one short question.

## 0. The goal in Nir's words (this is the product, not an extra)

A public site where Nir adds an article now and then, and the system
shows the hidden things right away:
- BLUE paths: symptom -> disease (PRESENTS_WITH), disease/symptom -> treatment
  (TREATED_BY). Example: headache -> migraine -> drug X.
- YELLOW paths: treatment -> harm (HARMS), disease -> complication
  (LEADS_TO), then that disease -> its symptoms. Example: Nir adds a paper
  that drug X damages the liver -> drug X (yellow) -> liver injury ->
  jaundice, fatigue...
- Visible on the 2D view of the chosen entity; clicking the drug shows its
  yellow side; clicking any linked entity follows the path (cascade).
- Side effects are first-class (Law 9), never hidden.
- Cheaper equivalents: the same active drug under other names or from other
  countries at a lower price (brand/generic aliases from the books; prices
  from articles and price lists Nir adds).
- Treatments not approved by the FDA, with the evidence Nir brings (for
  example Cuba's CIMAvax-EGF for lung cancer): shown with their origin,
  year and evidence strength, clearly labelled "added by the site owner".
The system is NOT complete until a visitor can see all of this for real
entities. Say that honestly whenever asked. Never call missing core work a
"small cleanup".

## 1. What exists (3 Nov night, all pushed)

- 37 books, 135,325 pages, text + FTS in kitchen/logs/library.sqlite.
- 35,845 entities (3 groups), 2,376,084 lit spots (DISCUSSED_IN) in Neo4j.
- Per-chapter page map + folio map (speed_entities.py), EPUB folio tool
  (epub_folios.py). Rebuild: speed_entities.py (6 min), speed_export.py (45 s).
- The viewer ALREADY handles edges: site/viewer/geo.js spotsFor() colours
  them (RELATION_COLOUR), ui.js lists them on the card. The format it expects
  is in kitchen/make_demo.py lines 74-80: per entity "edges": [{relation,
  direction "out"|"in"|"both", subtype, other_slug, other_name, other_group,
  f_scale, severity, numeric_pct, statements:[{district_id, book_id, page,
  quote, f_scale, severity, ...}]}]. speed_export.py writes "edges": [] now.
- ZERO edges exist. This is the missing core.
- kitchen/.env has no OPENROUTER_API_KEY. Nir adds it himself; never read,
  print or log it.

## 2. The work, in order

### Step A (first message of the session, one question at a time)
A1. Ask Nir: "Paths first, or the 5 calibre books first?" (HAZZARD,
    IRWIN-RIPPE, KAPLAN, ROCKWOOD, WILLIAMS-OBSTETRICS lack only index
    links; procedure in HANDOFF-2026-11-04-MORNING.md). Recommend paths first;
    a book file can be handled in 5 minutes whenever he brings one.
A2. Ask Nir to put OPENROUTER_API_KEY=... in kitchen/.env himself, and to
    pick the model order (show: deepseek/deepseek-v4-flash 0.18,
    qwen/qwen3.7-flash 0.13, z-ai/glm-5.3-flash 0.08 dollars per million
    output tokens; recommend DeepSeek first). Re-list prices with the
    curl filter used on 3 Nov if a day has passed.

### Step B: kitchen/worker.py (Part 0 section 10.4, exactly)
ask(system, user, schema=None, max_tokens=2000) -> dict; providers from
.env in order, Ollama qwen3:8b last; temperature 0; JSON mode; schema check
+ one retry; failover on 429/5xx/timeout/2x invalid JSON; ThreadPool(8-16);
every call appended to kitchen/logs/worker-cost.jsonl with tokens and the
price from "usage"; a running-total helper; a hard stop at a dollar cap
passed by the caller. Test with one tiny call; show Nir the cost line.

### Step C: book edges (the blue/yellow paths from the 37 books)
C1. kitchen/speed_edges.py --candidates: code only, no model.
    - Mention finder: entity names and aliases -> a token-n-gram dictionary
      on norm()-style keys (max 6 words; skip names under 4 letters and
      single stopwords). Check first whether pyahocorasick is installed
      (Law 13); a dict lookup over n-grams is enough without it.
    - Split every page into sentences; keep sentences with >= 2 entities of
      a pair type that the schema allows: disease-symptom (PRESENTS_WITH),
      disease|symptom-treatment (TREATED_BY or HARMS), disease-disease
      (LEADS_TO / MISTAKEN_FOR).
    - Keep only sentences with a cue word (present, manifest, symptom, sign,
      treat, therapy, managed, drug of choice, respond, adverse, toxicity,
      side effect, induced, caus*, complicat*, lead to, result in,
      associated, risk, contraindicat*, mistaken, mimic, differential...).
    - Cap: at most 3 sentences per (pair, book), best = most cue words,
      shortest. Store in table edge_candidates(id, book_id, page, sentence,
      a_slug, b_slug, pair_kind).
    - Print counts per book and the total. Target well under 1 M sentences.
C2. Estimate before any model run: tokens per batch of 40 sentences, total
    calls, dollars at the chosen model's price, hours at 8-16 parallel.
    Tell Nir in one line; start only with his "okay". Expected order of
    magnitude: 10-20 dollars and a few hours for the whole library; if the
    estimate is above 25 dollars, tighten the cue filter or the cap first.
C3. Trial: one book (HARRISON-22), 500 sentences. Show Nir 20 random typed
    edges (sentence + result) as plain text in chat, no screenshots. Fix
    the prompt once if needed.
C4. Typing prompt (one call per 40 sentences), output ONLY JSON:
    [{"id":int,"relation":"PRESENTS_WITH|TREATED_BY|HARMS|LEADS_TO|
    MISTAKEN_FOR|NONE","from":"a|b","frequency_phrase":str (verbatim or
    ""),"severity_phrase":str (verbatim or ""),"contraindicated":bool}].
    Rules in the prompt: use only the sentence; NONE when the sentence does
    not state that relation; never invent frequency. Code maps
    frequency_phrase to f_scale with the Part 4 F-word table (F5..F1; none =
    F0) and severity from severity_phrase. Code checks the direction is
    legal for the groups (Part 2 E) and drops illegal ones.
C5. Full run: DELEGATE to DeepSeek 4.1 Flash in OpenCode (Nir switches the
    model). Give it the exact command, the dollar cap, and "stop and report
    counts, cost and failures, then hand back". Resumable: results in table
    edge_results keyed by candidate id; reruns skip done ids.
C6. Load: one UNWIND per relation type into Neo4j with the Part 2 E
    property set (district_id via speed_entities' page map, book_id,
    page_number printed, quote = the sentence, frequency_phrase, f_scale,
    severity, severity_phrase, subtype CONTRAINDICATED_IN, reader_model,
    read_date, source "text-model"). One relationship per sentence.
C7. Export: speed_export.py fills "edges" in the make_demo format, both
    directions (out on the source entity, in on the target), aggregated per
    other entity (highest f_scale wins, all statements kept). Also an
    "edges_here" count per district file. Then kitchen/stamp_viewer.py,
    commit (not the data files), push.
C8. Nir checks the live site with his eyes: "migraine", a common drug, and
    "inguinal hernia". Ask him then (one question) whether the 2D view should
    also draw LINES from entity to entity (a path), or whether the coloured
    district spots + cascade links are enough. Build only what he says.

### Step D: the article reader (Part 0 section 10, plus edges)
Implement section 10 exactly (inbox/, sha256 skip, sidecar meta, chunking,
claims, linking by norm + bge-m3 0.88, SQLite + Neo4j Source/Claim, card
"Second opinion", gold ring in search, ingest.py --dry-run, 2 dollar stop),
with three additions Nir needs:
D1. The reading prompt also returns typed edges in the C4 format
    (relation, from-name, to-name, frequency_phrase, severity_phrase,
    quote). They are loaded like C6 with source "article", source_id and
    the Source's origin/year/strength, so a paper "drug X damages the liver"
    creates a yellow HARMS edge drug X -> liver injury that shows on the map
    next to the textbook edges, labelled as from the article.
D2. Price and availability claims (type price|availability) attach to the
    treatment entity and its aliases; the card groups them as "Prices and
    where available" so cheaper equivalents are visible.
D3. Regulatory status: claim field "approval" (e.g. "not FDA approved;
    approved in Cuba 2008") shown on the card next to the treatment.
Test with one article Nir chooses (dry run first, then real), show the
cost line.

### Step E (only when A-D work): Part 0 section 11 items, quick or dropped.

## 3. Cost and behaviour rules (Nir, repeated many times)

- Target per session: about 15 dollars of manager tokens. Code and cheap
  models do the work; the manager writes code and reads summaries.
- No screenshots; Nir is the eyes. Show results as short text.
- One-shot fixes; no exploratory loops; read only the files needed.
- Long runs and babysitting go to DeepSeek 4.1 Flash: say "HUMAN: please
  switch to DeepSeek 4.1 Flash and say continue", give exact commands, a
  stop rule and what to report.
- Every model run: trial first, hours and dollars stated, Nir's okay.
- Short chat replies with emojis; no emojis in files or commits.
- Honest: say what is missing; never dress a gap up as a cleanup.
