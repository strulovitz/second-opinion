================================================================================
SECOND OPINION -- THE BIBLE
PART 0 OF 13 -- THE SPEED CHARTER (overrides every other part where they
                 disagree)
File: BIBLE/part-00-speed-charter.md
Written: 3 November 2026 by Claude Fable, at Nir's explicit request and with
         his explicit permission to rewrite the BIBLE. Decisions D1-D4 below
         were each put to Nir separately with pros and cons; he answered yes
         to all four.
================================================================================

0. HOW TO READ THIS PART
  Read this part FIRST, before AGENTS.md routing and before any other part.
  Where an older part says something slower, more careful or more
  model-heavy than this part, THIS PART WINS. The older parts remain for
  their data formats, identities and the viewer; their process rules are
  replaced here. Nothing already built (geography, Goldberg globe, viewer,
  TOC data, export format) is thrown away.

1. THE GOAL, RESTATED (D4, approved)
  The skeleton is NOT the product. The product is an INGESTION system:
  Nir hands over material every few days (copy-paste, a file in a folder,
  or an upload): articles, studies, price lists, foreign treatments such as
  Cuba's CIMAvax-EGF for lung cancer. A model reads each item ONCE, extracts
  its core knowledge, and files it into the database attached to the right
  entities (disease, drug, side effect), keeping the source. A visitor who
  opens an entity sees the Western textbook pages AND Nir's added sources,
  side by side. There are NO live internet lookups. Truth, selection and
  responsibility for what is shown are Nir's, not the system's.
  The skeleton exists only to give that product (a) a list of medical
  things, (b) where the textbooks discuss each one, (c) the searchable text
  of those pages. Everything else is presentation.

2. THE TIME LAW (D1, approved)
  Every book: under one day of laptop time. The whole skeleton: under one
  month, target two weeks. Speed beats accuracy in every section. An
  estimated 5-10 percent of wrong merges or wrong groups is accepted; they
  are visible (every claim carries its page and snippet) and fixable later.
  Never plan anything that takes months. Measure a trial, state the hours,
  then run.

3. THE MODEL TIERS (new understanding, 3 Nov 2026)
  Three tiers, used in this order of preference for TEXT jobs:
  T-A  CHEAP CLOUD through OpenRouter (DeepSeek Flash, GLM Flash and the
       like). Batched, parallel (10-20 requests at once), a few dollars for
       the whole library. This is the main worker for repairs, batch
       classification, batch same-or-new decisions and ingestion reading.
  T-B  LOCAL SMALL (4B-8B through Ollama). The free fallback when cloud
       quota runs out. Same prompts, same JSON, slower.
  T-C  LOCAL BIG (Qwen 27B). Pictures only (a scanned page with no text
       layer that OCR fails on). Never used as a typist again.
  The pipeline talks to a MODEL SLOT, never to a named model. One client
  (kitchen/worker.py) holds an ordered list of providers and fails over
  automatically. No "marriage" to any model. Smart paid models (Claude,
  GPT) write code and plans; they do not run loops.

4. THE FIFTEEN TRICKS (all mandatory unless a trial proves one wrong)
  T1  Text first, model last. pdftotext and the PDF's own hidden links for
      every page. A model is called only for a page that FAILS a
      deterministic check. Scans without a text layer: tesseract OCR.
  T2  Indexes are parsed by code (regex + validator: every page number in
      the source text must be captured). Rejected pages go to T-A in a
      batch as repair only.
  T3  Within one book, never ask a model whether two headwords are the same.
      The book's own "see" lines are its synonyms. Zero resolution calls
      per book.
  T4  Late binding. Store every book's headwords as TERMS first. Merge terms
      into shared ENTITIES once, over all books, in a single global pass.
  T5  Embeddings before questions. A local embedding model turns all terms
      into vectors in minutes. Near-identical vectors in the same group are
      merged by code. Only the uncertain band goes to T-A, 50 per call.
  T6  Small model for text, big model for pictures (section 3).
  T7  Classification by neighbours: a seed set classified by T-A in batches
      of 100; the rest by nearest labelled neighbour in embedding space.
  T8  Index every page instead of reading every page: pdftotext of all
      books into SQLite FTS5. "Where is X discussed" is a search, answered
      in milliseconds, with the verbatim snippet as proof. Phase B's
      "read every page" is dead.
  T9  Frequency and altitude from counts (index references + full-text
      hits). SQL, seconds.
  T10 Bulk loads: one UNWIND per book into Neo4j, not one transaction per
      entry.
  T11 Deterministic steps run for ALL books in one batch (D3, approved),
      reported by summary. Supervision exists only for measured trials of
      model steps and for review samples.
  T12 Models kept warm and parallel (keep_alive, OLLAMA_NUM_PARALLEL, cloud
      concurrency).
  T13 Review by sample: 20 random terms per book with page and snippet;
      merge decisions of the uncertain band once per library. Nir approves
      books in groups.
  T14 Proof is the snippet: page number plus verbatim pdftotext lines. Page
      images are rendered on demand for the viewer, not stored as evidence
      per claim. (Law 2 kept in spirit.)
  T15 Reuse everything already built.

5. THE NEW PIPELINE
  Stage 1, all books, one script: pdftotext every page -> pages table and
    FTS index; locate the index range (books.json has 25; the rest by
    searching for the index heading); parse by code; validate; store TERMS
    with page references and "see" links. T-A repairs rejected pages.
  Stage 2, library-wide: embed all terms; seed classification by T-A;
    neighbour classification for the rest; code merges near-identical
    terms; T-A batches the uncertain band; bulk-write ENTITIES, aliases and
    lit spots to Neo4j.
  Stage 3: export; replace the demo data on the live globe with real data;
    search box over the FTS database; one page per entity listing every
    book, page and snippet.
  Stage 4, the product: the ingestion system of section 1. Inputs are a
    folder (kitchen/inbox/) and pasted text. Each item becomes a SOURCE node
    with its extracted claims linked to entities. Shown on entity pages as
    "Second opinion".

6. THE VIEWER (3D kept, 2D redesigned)
  The 3D sand-table globe by Claude Opus 5.5 is approved as-is and is not
  touched. The 2D "flower" map is retired: Nir judged his own request
  ("blobs not touching, to hide the stretched poles") a mistake. The 2D
  view becomes ONE generic projection routine driven by code, the same for
  any point the user clicks: an azimuthal equal-area view centred on the
  clicked point (no pole stretching, every region drawn by the same
  function), with a whole-globe equal-area projection as the overview.
  Pretty is welcome; generic and correct comes first.

7. WHAT HAPPENS TO EXISTING WORK
  Harrison's 4,350 resolved entries and 2,517 entities become TERMS like
  everything else and are re-merged in the global pass. Geography, globe,
  TOC data and export format: unchanged. The per-entry resolver
  (index_resolve.py) and the model-based index parser (index_parse.py) are
  retired, kept in git history.

8. REPORTING
  After each stage: what ran, measured time, counts, what failed. Failures
  are reported plainly, never hidden or dressed up. Emojis never appear in
  files, commits or reports; only in chat replies to Nir.

9. DECISIONS RECORD
  D1 Speed Charter as Part 0, overriding older parts: YES (3 Nov 2026).
  D2 Download free local models through Ollama as needed: YES.
  D3 Code-only steps run for all books in one batch, no page supervision,
     full machine all day: YES.
  D4 Product = ingestion system fed manually by Nir; no live lookups; truth
     is Nir's responsibility: YES.
  Also: cheap cloud models become the main text tier (section 3); 2D map
  redesigned, 3D kept (section 6).
================================================================================

================================================================================
10. STAGE 4 DESIGN -- THE INGESTION SYSTEM (written 3 Nov 2026 by Claude
    Fable for Claude Opus 5.5 to implement; the thinking is done, follow it)
================================================================================
10.1 Purpose. Nir drops material into the system; a cheap model reads each
     item ONCE and files its core claims onto the entities; the entity card
     shows them under the heading "Second opinion". No live lookups. Nir is
     responsible for truth and selection; the card says so in one line.

10.2 Inputs. Folder kitchen/inbox/ (gitignored). Accepted: .pdf, .txt, .md,
     .html, .url (one URL per line is NOT fetched automatically; Nir saves
     the page himself). Pasted text: Nir saves it as inbox/paste-<topic>.txt.
     Each file is identified by sha256; a file already ingested is skipped.
     Optional sidecar inbox/<name>.meta.json: {"title","origin","year","url"}.

10.3 Text. pdftotext (reading order) for PDF; html stripped with the
     standard library; others read as UTF-8. Chunk at about 12,000 characters
     on paragraph boundaries. Items over 30 chunks: ingest the first 30 and
     record "truncated". No vision model; a PDF with no text layer is
     reported, not OCR'd, unless Nir asks.

10.4 The worker (kitchen/worker.py, model-agnostic, Part 0 section 3).
     ask(system, user, schema=None, max_tokens=2000) -> dict.
     Providers in order from kitchen/.env (never printed):
       OPENROUTER_API_KEY, OPENROUTER_MODELS="model-a,model-b,..." (cheap
       Flash-class models; the implementer lists
       https://openrouter.ai/api/v1/models, filters by price under about
       0.5 dollars per million output tokens, shows Nir three candidates,
       Nir picks the order), then local Ollama qwen3:8b as last resort.
     Rules: temperature 0, JSON response_format where supported, strict
     schema check, one retry with the validation error appended, failover
     to the next provider on 429/5xx/timeout/invalid JSON twice. Thread pool
     of 8 for independent chunks. Every call logs provider, model, tokens
     in/out and the price from the response "usage" to
     kitchen/logs/worker-cost.jsonl; ingest.py prints the running total.

10.5 Reading prompt (one call per chunk). System: "You extract medical
     claims from a document for a second-opinion library. Output ONLY JSON:
     {"title":str,"origin":str (country or institution if stated else
     null),"year":int|null,"kind":"study|review|news|official|price-list|
     other","summary":str (max 60 words),"claims":[{"text":str (max 35
     words, one claim),"type":"treatment|side-effect|price|availability|
     mechanism|epidemiology|diagnosis|other","entities":[str...] (diseases,
     drugs, symptoms named in the claim, canonical English names),
     "quote":str (verbatim from the text, max 30 words),"strength":
     "trial|observational|review|case|opinion|official"}]}. Report only what
     the text says; do not add outside knowledge; at most 25 claims per
     chunk." User: the chunk, prefixed with "Document: <file name>".
     Chunks of one item are merged: title/origin/year from the first chunk
     that has them, claims concatenated, duplicate claim texts dropped.

10.6 Linking claims to entities (code first, model never):
     for each entity name in a claim: norm() key (speed_entities.norm) ->
     exact entity; else bge-m3 embedding nearest entity name with cosine
     >= 0.88 (any group); else create a new Entity with created_from=
     "source", group by nearest labelled neighbour (speed_entities logic),
     flagged needs_review=true. Keep the embedding matrix of all entity
     names cached in kitchen/logs/entity-embeddings.npy (rebuilt when
     speed_entities.py runs).

10.7 Storage. SQLite library.sqlite tables sources(id sha, file, title,
     origin, year, kind, summary, added, truncated) and claims(id, source_id,
     text, type, quote, strength, entity_slugs JSON). Neo4j, bulk UNWIND:
     (:Source {id,title,origin,year,kind,summary,file}) and
     (:Claim {id,text,type,quote,strength})-[:FROM]->(:Source),
     (:Claim)-[:ABOUT]->(:Entity). Ingest is idempotent per source id.

10.8 Export and viewer (simplest thing that works). speed_export.py adds
     to each entity JSON "second_opinion": [{"source":{title,origin,year,
     kind,file},"claims":[{text,type,quote,strength}]}] and writes
     site/data/sources.json (list of all sources with claim counts).
     ui.js entityCard: after the lights paragraph, if second_opinion is
     non-empty, an h3 "Second opinion" with one bullet per claim: the claim
     text, then small text "<type> - <strength> - <origin> <year>", then the
     quote in italics; a one-line notice: "Added by the site owner from
     sources outside the Western textbooks; judge for yourself." On the
     globe, an entity with second-opinion claims gets a gold ring on its
     search result ("N second opinions") -- nothing more in 3D for now.

10.9 Command. kitchen/ingest.py [--all | files...] [--dry-run]. Prints per
     file: chunks, claims, linked entities, new entities, cost. Dry run
     shows the extracted JSON without writing. Then run speed_export.py.

10.10 Budget. Expect roughly 10-20k tokens per article chunk pair; at Flash
     prices a 20-page article costs cents. If a run exceeds 2 dollars,
     stop and tell Nir.

11. SMALL TRIAGE ITEMS (do each in under 15 minutes or drop it)
11.1 Page offsets for the 10 books without one: first try
     kitchen/logs/<BOOK>-eyes.json / -vis-links.json from the TOC lane (they
     record the PDF image where each chapter opener was found; offset =
     image - page_start, take the mode). If absent, loosen page_offsets()
     thresholds (votes >= 2). If still nothing, record "no offset" and move on.
11.2 Junk names in speed_entities.py: also drop names containing curly
     quotes, names ending in a single stray letter after a comma (OCR
     tails like ", Z" or ", l"), and names whose key is a single stopword.
11.3 Stale tests (flower map, resolver) are deleted or skipped, not fixed.

================================================================================
12. THE PURPOSE OF THE PROJECT AND HOW IT IS SHOWN (it was always this; the
    manager, Claude Opus 5.5, misunderstood it on 4 Nov 2026 and wrote it
    here at Nir's order). THIS SECTION WINS OVER EVERY OTHER PART, OVER
    LAW 1, OVER PART 1 SECTION 3.6, OVER PART 7 ADDITION A11, OVER SECTION
    10 OF THIS PART, AND OVER EVERY HANDOFF OR PROMPT FILE. What Nir
    says is binding, not a recommendation.
================================================================================
12.1 The purpose. Second Opinion shows knowledge the establishment hides:
     cascading side effects, better cures that are not approved, and the
     same chemical sold elsewhere at a fraction of the price. The core
     message, and the non-trivial part: a treatment that people believe is
     GOOD causes something BAD. The arrow from the good thing to the bad
     thing is what the visitor must see.

12.2 The books are the establishment's view and only the SKELETON: the
     list of medical things (35,845 entities), each thing's own altitude,
     and the chapters where the books discuss it (2.4 M mentions). NO
     connections are taken from the books. NEXT-SESSION-PROMPT step C is
     CANCELLED. The wrong attempt of 4 Nov morning (kitchen/speed_edges.py,
     kitchen/worker.py, SQLite tables edge_candidates and edge_results) was
     DELETED at Nir's order. Do not rebuild it.

12.3 GOLDEN FACTS ARE ENTERED BY HAND. Nir hands the manager an article
     (Chinese research, an Indian market price, a Cuban clinic report,
     anything he chooses); about 20 articles in total, not thousands. The
     MANAGER (the chat model in OpenCode) reads the article itself, picks
     its golden facts, and writes each fact by hand as one record in the
     committed file data/golden/facts.json. There is NO automatic article
     reader, NO OpenRouter key in the system, NO upload page on the
     website, and NOTHING from the internet, ever. Section 10 of this part
     (automatic ingestion) is CANCELLED.
     One fact record:
       id            "G001", "G002", ...
       relation      HARMS (treatment -> the bad thing it causes; subtype
                     CONTRAINDICATED_IN allowed), LEADS_TO (disease ->
                     disease), PRESENTS_WITH (disease -> symptom),
                     TREATED_BY (disease or symptom -> treatment),
                     MISTAKEN_FOR (disease <-> disease), or SAME_CHEMICAL
                     (treatment <-> treatment: the same active chemical
                     under another name or from another country)
       from, to      entity slugs from the registry
       quote         the article's own sentence, verbatim
       frequency_phrase, severity_phrase   the article's own words or ""
       price, availability, approval       free text for treatments (for
                     example "approved in Cuba 2011, not FDA approved"),
                     or ""
       source        {title, origin (country or institution), year, file
                     or url as Nir gave it, kind (study, review, news,
                     price list, official), strength (trial,
                     observational, review, case, opinion, official)}
       entered_by, entered_date
     A thing missing from the registry is added by hand in the same file
     (section "new_entities": name, group, aliases) and gets its altitude
     by the insertion rule of Part 5 section 8; nothing else moves.
     A script (kitchen/golden_load.py) loads the file into Neo4j: the
     connections as the relationship types above with source "article"
     and the source fields; F-scale and severity from the Part 4 tables.
     The export writes them into the entity files. From here everything is
     AUTOMATIC DISPLAY ONLY: the website never analyzes anything.

12.4 Words. Say "connection" or "path", never "links" or "edges" to Nir:
     he hears "links" as automatic internet scraping. Nir switches the chat
     model in OpenCode himself; the manager never compares models or shows
     price tables.

12.5 HOW CONNECTIONS ARE SHOWN (automatic, from the database only)
  (a) A PATH IS AN ARROW. Every connection is drawn as a smooth curved line
      (a spline) WITH AN ARROWHEAD from A to B, so the direction is
      obvious. This REPLACES Part 1 section 3.6 "no lines" and Part 7 A11
      "lines forbidden". The chapter lights (where the books discuss a
      thing) stay, as faint dots under the paths.
  (b) TWO DIRECTIONS, TWO COLOURS (Nir, 4 Nov 2026). The colour and the
      arrow direction belong to the WALK the visitor starts, not to the
      stored fact:
      BLUE walk = the normal medical knowledge, starting from a SYMPTOM:
        symptom -> disease (that presents with it) -> treatment (for that
        disease). All arrows blue.
      YELLOW walk = the opposite direction, the hidden harm, starting from
        a TREATMENT: treatment -> disease it CAUSES (a different disease:
        the headache pill -> liver damage) -> that disease's symptoms
        (jaundice, tiredness). All arrows yellow.
      So one stored fact (liver damage presents with jaundice) is drawn
      blue in a blue walk and yellow in a yellow walk. Grey = MISTAKEN_FOR
      and green = SAME_CHEMICAL (two arrowheads) are shown with any walk.
      Thickness = frequency (F-scale; thicker = more common); dashed =
      frequency not stated; a red glow = the source's severity words
      (fatal, life-threatening ...). Each arrow carries the other thing's
      name at its end. Hover or tap an arrow: the verbatim sentence, the
      source title, country, year and evidence strength.
  (c) 2D. The clicked thing glows; the arrows of its walk go out to
      labelled nodes; the next step of the chain is drawn fainter, so the
      whole chain (headache pill -> liver damage -> jaundice, tiredness) is
      visible at once. ONLY TWO INPUTS EXIST: a symptom (starts a blue
      walk) and a treatment (starts a yellow walk). A disease is never an
      input; it is only the middle of a walk (Nir: "there is no such
      thing"). The end of one walk is the input of the other: clicking the
      symptom at the end of a yellow walk starts its blue walk; clicking
      the treatment at the end of a blue walk starts its yellow walk. A
      node sits on the chapter tile where the books discuss that thing
      most (its drawing anchor only; Law 8 still holds for the lights).
  (d) 3D. NOTHING MOVES; this is not a flight. The camera stays where the
      visitor put it. The same arrows are simply DRAWN in 3D between the
      heights: a curve from the point on A's shell (A's altitude, above
      A's anchor tile) to the point on B's shell, crossing the layers in
      between, with the arrowhead at B. Example: from a drug's shell among
      the satellites, an arrow is drawn down into the glass planet to
      liver damage's depth, and from there an arrow up into the
      atmosphere to jaundice. The visitor turns and zooms the globe by
      hand, as now.
  (e) ONLY RELEVANT LAYERS. There are thousands of symptom altitudes and
      thousands of treatment altitudes. Never draw them all. Draw ONLY the
      shells of the clicked thing and of the things on its paths, each as
      a thin translucent shell or ring with its name; every other shell
      is hidden. The decoration (clouds, satellites, bands) stays faint so
      the visitor still sees where the atmosphere and the orbits are.
  (f) Cards and pages: each connection as text with its arrow
      ("Drug X -> causes -> liver damage"), the sentence and the source.
      A treatment's card lists "Same chemical, other names and countries"
      with prices, and "Approval" (where approved, where not).

12.6 Unchanged: the geography, the globe and its looks, the altitude rule
     (one altitude per thing, shared by every chapter that discusses it),
     search, and the book lists and pages.

12.7 Behaviour. Answer short and simple. Do NOTHING until Nir explicitly
     says to do it and approves it.
================================================================================

================================================================================
13. THE WORLD MODEL, CORRECTED BY NIR (4 Nov 2026 evening; written by the
    manager, Claude Opus 5.5, at Nir's explicit order "please correct the
    BIBLE"). THIS SECTION WINS OVER SECTION 12.5(d), OVER PART 1 SECTIONS
    3.3-3.4, OVER PART 5, OVER PART 7 A6/A6b, AND OVER EVERY HANDOFF OR
    PROMPT FILE.
================================================================================
13.1 What Fable got wrong. Fable put "diseases and conditions" in one group
     and drew them as onion layers INSIDE the planet, deep = "discussed in
     many books". Nir never meant that. Nir meant: under the diseases there
     are DEEPER things, the CONDITIONS that CAUSE the diseases. Example:
     lack of vitamin C (a cause) -> scurvy (a disease) -> bleeding gums (a
     symptom). The onion of 22,000 disease layers inside a glass planet is
     CANCELLED; nobody can see it.

13.2 The four places, from the inside out:
     UNDERGROUND (inside the planet): the CAUSES, the conditions under the
       diseases (lack of vitamin C, leaky gut, ...).
     SURFACE: the DISEASES ARE THE HEXAGONS. A hexagon is a chapter; most
       chapters are about a disease. A disease lights up EVERY hexagon
       (chapter) whose chapter discusses it. Nothing is merged: every
       chapter stays its own hexagon.
     AIR (atmosphere): the SYMPTOMS, drawn as cartoon CLOUDS above the
       hexagons.
     ORBITS: the TREATMENTS, drawn as cartoon SATELLITES above the air.
     Example walk: lack of vitamin C (underground) -> scurvy (hexagon) ->
     bleeding gums (cloud). Arrows (section 12.5 a-b) go between these
     places: from a satellite down to a hexagon, from a hexagon up to a
     cloud, from an underground cause up to a hexagon.

13.3 Heights are ROUGH. The visitor cannot see thousands of levels and does
     not care. Heights only put a thing in the right place (underground,
     surface, air, orbit) and roughly lower or higher inside it. They are
     computed by a simple code rule in seconds; NO AI model, NO measured
     trial, NO question to Nir about the exact order. The detailed ordering
     rules of Part 1 3.4 and Part 5 are not important and must not cost
     time or money.

13.4 Only what is clicked is shown (section 12.5 e stands): never all
     things at once. After a click, only the thing and the few things on
     its walk are marked at their rough height: a lit hexagon for a
     disease, a cartoon cloud for a symptom, a cartoon satellite for a
     treatment, a marked spot under the surface for a cause. Hovering or
     tapping the mark shows its information. There is NO glass planet for
     diseases any more (they are on the surface).

13.5 Decided by Nir (4 Nov 2026 evening):
     (a) CAUSE OR DISEASE: like cause and effect. The cause happens FIRST
         (lack of vitamin C); AFTERWARDS the problem in the body happens
         (scurvy). In practice: when a fact says "X causes disease Y", X is
         the cause and is drawn underground; Y is the disease, a hexagon.
     (b) ONE ORDER FOR EVERYTHING: COMMON VERSUS RARE. The further a thing
         is from the centre of the Earth, the more rare ("exotic") it is.
         This holds for causes (common deep, rare near the surface),
         symptoms (common low in the air, rare high) and treatments
         (common low orbit, rare high orbit). Diseases stay on the ground,
         the hexagons; common versus rare is used for them only where it
         is relevant. This REPLACES "heaviness" (Part 1 3.4, Part 5 4-5),
         "specificity" and "breadth" as ordering keys.
     (c) The rough code rule (13.3) for "common": the number of chapters
         and books that mention the thing (more mentions = more common).
     (d) POISONS AND HARMFUL EXPOSURES ARE CAUSES (Nir): GM food (GM
         potatoes, Bt toxin, glyphosate) is like a poison, like asbestos
         that causes cancer. It is NOT a disease; it causes many diseases
         (allergies, cancer ...). Drawn underground as a cause.

13.6 Lesson for the manager. When the BIBLE and Nir disagree, Nir is right;
     say plainly that the BIBLE (or the manager) was wrong, without
     defending it, and help him do it right.
================================================================================
