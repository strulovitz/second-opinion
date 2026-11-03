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
