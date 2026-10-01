================================================================================
SECOND OPINION -- THE BIBLE
PART 4 OF 13 -- PHASE B: THE READING PIPELINE
File: BIBLE/part-04-phase-b-reading-pipeline.md
MANAGER FOR THIS PART: SMART (Claude Sonnet 5.5 / GPT 6.1 Sol) writes
                       the scripts and runs the pilot (sections 5-9, 11);
                       [SWITCH TO CHEAP] for the long runs, loading,
                       ledger and reviews (sections 10, 12, 13).
READER FOR THIS PART:  free local model (Qwen 3.8 27B Q4_K_M, Gemma 4
                       31B substitute), TEXT mode for extraction, VISION
                       mode for figure/table pages.
PRECONDITION:          Freeze A done (Part 3 section 11). Entities are
                       frozen: Phase B never creates an Entity. Unknown
                       terms go to Quarantine.
================================================================================

0. PURPOSE, INPUTS, OUTPUTS, AMENDMENTS
--------------------------------------------------------------------------------
0.1 Purpose
  Read every page of every accepted book and pour its CONTENT into the
  frozen skeleton: edges (PRESENTS_WITH, TREATED_BY, HARMS, LEADS_TO,
  MISTAKEN_FOR) with verbatim quotes, frequency phrases and F-scale;
  page-derived lit spots; drug names (generic, brand, formula); and
  quarantine terms. Nothing moves. Nothing is created except
  relationships, QuarantineTerm nodes and new aliases.

0.2 Inputs
  - kitchen/books.json (status "index-done" for every accepted book),
    page_offset known, image_name_pattern known.
  - Page images in kitchen/pages/<BOOK_ID>/ (Part 3 section 2.3).
  - The frozen Entity registry in Neo4j.
  - A running reader server (address in kitchen/.env).

0.3 Outputs
  - kitchen/transcripts/<BOOK_ID>/p<printed_page>.txt  (gitignored)
  - kitchen/extractions/<BOOK_ID>/p<printed_page>.json (gitignored)
  - kitchen/logs/<BOOK_ID>-pages.jsonl   per-page ledger (committed;
    small)
  - kitchen/logs/<BOOK_ID>-resolve-cache.json  term -> slug decisions
    (committed; this is the project's growing synonym memory)
  - Neo4j: edges, DISCUSSED_IN (source "page"), aliases, generic/brand/
    formula lists, QuarantineTerm nodes.

0.4 BIBLE AMENDMENTS declared in this part
  AMENDMENT 4.1 (text-first transcription). For a book with
    text_layer = true, the verbatim page text comes from pdftotext.
    The vision reader is called only (a) for pages that contain
    embedded images (detected with pdfimages -list) or whose text shows
    table structure (section 5.3), to describe figures and re-transcribe
    tables; (b) for every page of a book with text_layer = false (full
    vision OCR, prompt P-B0). Reason: pdftotext is exact and instant;
    Q4 vision OCR is slow and less accurate. Switch in kitchen/.env:
    VISION_MODE = "figures" (default) | "all" | "off".
  AMENDMENT 4.2 (adds to Part 2 section 6.1 E): every edge relationship
    gets the property quote_hash (string, SHA-1 of the normalised quote
    plus relation plus the two slugs). It makes loading idempotent.
    DISCUSSED_IN with source "page" gets the same.
  AMENDMENT 4.3 (adds to Part 2 section 6.1 C): Entity gets the list
    property abbreviations (verbatim abbreviations the books define,
    e.g. "MI"), kept separate from aliases so that short tokens never
    cause exact-match merges.
  Everything else in Parts 1-3 stands.

0.5 Order of work in this part
  Step B0  Tools check; .env additions                 (section 1)   SMART
  Step B1  Page plan per book: which printed pages are
           read, in which order                         (section 2)   SMART
  Step B2  Transcription (text layer, figure pass, OCR) (sections 3-5) SMART writes
  Step B3  Windowing and the extraction prompt P-B1    (sections 6-7) SMART writes
  Step B4  Provenance check, F-scale, severity          (section 8)   SMART writes
  Step B5  Resolution against the frozen registry,
           quarantine                                   (section 9)   SMART writes
  Step B6  Loading into Neo4j                           (section 10)  SMART writes
  Step B7  Pilot: 24 pages, human review                (section 11)  SMART runs
  Step B8  Full runs, book by book                      (section 12)  CHEAP runs
  Step B9  Reviews and ledger                           (section 13)  CHEAP + human

1. TOOLS AND SETTINGS (Law 13)
--------------------------------------------------------------------------------
  Check: which pdfimages (poppler-utils, installed in Part 3). Python:
  nothing new. kitchen/.env additions (and the same keys with CHANGE_ME
  in .env.example):
    VISION_MODE=figures
    READER_CONTEXT_TOKENS=16384
    WINDOW_PREV_CHARS=1500
    WINDOW_NEXT_CHARS=1500
    MAX_PAGE_CHARS=14000
      (a page longer than this, which happens with dense tables, is cut
       into two halves at a blank line, each half processed as its own
       window; the second half keeps the page number with suffix "b")
    LOAD_EVERY_PAGES=25
  Server settings the human sets once in the server's screen: context
  length 16384 (or more), thinking OFF (or keep READER_NO_THINK_TAG),
  temperature 0, GPU offload as high as the 24 GB allows. Record the
  settings in PROGRESS.md.

2. STEP B1 -- THE PAGE PLAN
--------------------------------------------------------------------------------
2.1 Which pages are read. For each book, exactly the printed pages that
    belong to a district (chapter): from the first district's page_start
    to the last district's page_end. Never the front matter, never the
    index, never appendices without a chapter number. Image number of
    printed page p is p + page_offset (Part 3 section 4.6; per-province
    offsets if books.json has "page_offsets").
2.2 Reading order (DEFAULT, human may overturn). Books: HARRISON-22
    first, then the rest alphabetically by book_id. Inside Harrison:
    first Part 2 "Cardinal Manifestations and Presentation of Diseases"
    (printed pages about 93-482: the symptom chapters, which are the
    gates into the system and give the earliest useful website), then
    Part 3 Pharmacology, then all remaining parts in page order. For
    every other book: page order. The plan is written once per book to
    kitchen/logs/<BOOK_ID>-plan.json as an ordered list of
    {"page": p, "district_id": ..., "image": image_number}. The human
    can reorder by editing this file before the run starts.
2.3 Per-page ledger kitchen/logs/<BOOK_ID>-pages.jsonl: one line per
    page, appended at each stage change:
    {"page":134,"district_id":"C01.P02.D020","stage":"transcribed"|
     "extracted"|"resolved"|"loaded"|"failed","seconds":42.1,
     "edges":7,"terms":19,"quarantine":2,"error":"", "time":"<ISO>"}
    A page with stage "loaded" is skipped on re-run. A page with
    "failed" is retried once on the next run, then left for the human.

3. STEP B2a -- TRANSCRIPTION FROM THE TEXT LAYER (text_layer = true)
--------------------------------------------------------------------------------
3.1 Command, per page (image number N):
      pdftotext -f N -l N -layout "<pdf>" kitchen/transcripts/<BOOK_ID>/p<p>.txt
    Then normalise with a script: join hyphenated line breaks
    ("hyper-\ntension" -> "hypertension" only when the joined word is
    lowercase-continued; keep "Non-\nHodgkin" as "Non-Hodgkin"),
    collapse 3+ spaces inside a line to 2 spaces (preserves table
    columns), collapse 3+ blank lines to 2, remove form-feed characters,
    strip the running header/footer lines (the first and last line if
    they consist of the page number and/or the Part/Chapter title).
3.2 Reference lists. Harrison chapters end with "FURTHER READING";
    other books end chapters with "REFERENCES" or "Suggested Reading".
    Everything from such a heading to the end of the chapter is cut
    from the transcript (kept in a side file p<p>.refs.txt, never read).
    Heading detection: a line equal (case-insensitive, stripped) to one
    of: FURTHER READING, REFERENCES, SUGGESTED READING, SUGGESTED
    READINGS, BIBLIOGRAPHY, ADDITIONAL READING, SELECTED REFERENCES.
3.3 The transcript header (first lines of every transcript file, added
    by the script, so that a human opening the file knows where it is):
      === BOOK: HARRISON-22 | DISTRICT: C01.P02.D020 "Fever" |
          PRINTED PAGE: 134 | IMAGE: harrison-internal-medicine_Page_0180.png ===

4. STEP B2b -- FULL VISION OCR (text_layer = false, or VISION_MODE=all)
--------------------------------------------------------------------------------
4.1 Prompt P-B0 (one page image -> text). System message:

    You transcribe one page of a medical textbook. Output PLAIN TEXT,
    not JSON. Rules: (1) transcribe all text VERBATIM, word for word,
    in reading order (left column before right column); (2) reproduce
    tables row by row, cells separated by " | ", with the table title
    first; (3) for every figure, photograph, diagram or chart, write a
    paragraph beginning with "[FIGURE] " that gives the figure's
    caption verbatim and then describes accurately in words what the
    image shows (structures, arrows, labels, colours, what is abnormal);
    (4) do not summarise, do not skip, do not add commentary; (5) if a
    sentence is cut by the page edge, transcribe the fragment as is.

    User message: "Transcribe this page." with the page image attached.
    Call: reader.ask(P_B0, "Transcribe this page.", images=[path],
    expect_json=False, max_tokens=8000).
4.2 The result is saved as the transcript, with the header of 3.3, and
    then the normalisation of 3.1 and the reference cut of 3.2 apply.
4.3 Image resolution: 150 dpi images (Part 3) are about 1240 x 1750
    pixels; this is enough for body text. If the reader misreads
    footnotes or table text, the human may re-render that book at
    200 dpi (pdftoppm -r 200); no other remedy.

5. STEP B2c -- THE FIGURE/TABLE PASS (VISION_MODE=figures)
--------------------------------------------------------------------------------
5.1 Detection, per page:
    (a) images:  pdfimages -list -f N -l N "<pdf>" | tail -n +3 | wc -l
        greater than 0 -> the page has embedded images. (Ignore images
        smaller than 60 x 60 pixels: decorative rules and icons; the
        -list output has width and height columns.)
    (b) tables:  the normalised transcript has at least 4 consecutive
        lines each containing 2 or more runs of 2+ spaces (column gaps),
        OR contains a line starting with "TABLE " followed by a number.
    If (a) or (b): the page gets a figure pass.
5.2 Prompt P-B0f (figure/table pass). System message:

    You are given one page image of a medical textbook AND the machine
    text of the same page. The machine text is correct for running
    prose. Your job is ONLY: (1) for every figure, photograph, diagram
    or chart on the page, write a paragraph beginning "[FIGURE] " with
    the caption verbatim and an accurate description in words of what
    the image shows; (2) for every table on the page, write "[TABLE] "
    followed by the table title verbatim and then the table row by row,
    cells separated by " | ", exactly as printed; (3) output nothing
    else: no prose from the page, no commentary. If the page has no
    figures and no tables, output exactly "[NONE]".

    User message: the normalised transcript text, with the page image
    attached. The output (if not "[NONE]") is appended to the transcript
    under a line "=== FIGURES AND TABLES (described by reader) ===".
    Table text from the figure pass is quotable (section 8.2 treats a
    table row as a sentence).

6. STEP B3a -- THE SLIDING WINDOW (solves "the idea starts on page k
   and ends on page k+1")
--------------------------------------------------------------------------------
6.1 A WINDOW for printed page p consists of three labelled blocks:
      <<<PREVIOUS PAGE p-1, LAST PART (context only)>>>
      the last WINDOW_PREV_CHARS characters of transcript p-1, cut at a
      sentence boundary (the first ". " after the cut point), or empty
      if p is the first page of its district.
      <<<THIS PAGE p (extract from here)>>>
      the whole transcript of p, including the figure/table block.
      <<<NEXT PAGE p+1, FIRST PART (context only)>>>
      the first WINDOW_NEXT_CHARS characters of transcript p+1, cut at a
      sentence boundary, or empty if p is the last page of its district.
    Windows never cross a district boundary: a chapter is a closed unit.
6.2 Rules given to the reader (inside P-B1): extract every relation
    whose proving sentence lies wholly or mainly in THIS PAGE; a
    sentence that BEGINS at the end of the previous block and ENDS in
    this page belongs to this page; a sentence that begins in this page
    and ends in the next block also belongs to this page (quote the
    whole sentence across the boundary). A sentence lying entirely in a
    context block is NOT extracted here (it was or will be extracted
    from its own page). The provenance page_number of an edge is p.
6.3 Dedup across neighbouring windows: an edge whose quote_hash already
    exists (same relation, same two slugs, same normalised quote) is
    not stored twice. Because the window rule above is strict, this
    only catches boundary sentences.
6.4 Transcription must therefore run at least one page AHEAD of
    extraction. The pipeline transcribes the whole district first (fast
    for text-layer books), then extracts page by page.

7. STEP B3b -- THE EXTRACTION PROMPT P-B1
--------------------------------------------------------------------------------
7.1 System message (verbatim; the script appends the human's
    "Additional rules" list from section 13 at the end):

    You read one page of a medical textbook and extract structured
    facts. Output ONLY JSON matching this schema:
    {
     "subjects": ["<the 1 to 6 main diseases, symptoms or treatments
                  this page is about, verbatim as named on the page>"],
     "edges": [
      {"relation": "PRESENTS_WITH" | "TREATED_BY" | "HARMS" |
                   "LEADS_TO" | "MISTAKEN_FOR",
       "from": "<term verbatim>", "to": "<term verbatim>",
       "from_group": "<symptoms-and-signs | diseases-and-conditions |
                      treatments-and-drugs>",
       "to_group": "<same choices>",
       "quote": "<the proving sentence(s), VERBATIM, copied character
                 for character from THIS PAGE; may include the words
                 from the context blocks only when the sentence crosses
                 the page boundary>",
       "frequency_phrase": "<the exact words in the quote that say how
                 often, e.g. 'in most patients', 'rarely', '30%'; or
                 empty string>",
       "numeric_pct": <number or null; a percentage stated in the quote,
                 e.g. 30 for '30%'; a range '10-20%' gives its upper
                 value 20; '1 in 1000' gives 0.1>,
       "severity_phrase": "<exact words in the quote expressing danger,
                 e.g. 'fatal', 'life-threatening', 'boxed warning';
                 or empty string>",
       "subtype": "CONTRAINDICATED_IN" | null
      }
     ],
     "drugs": [
      {"name": "<drug term verbatim as used in edges>",
       "generic_names": ["<verbatim>"], "brand_names": ["<verbatim>"],
       "formulas": ["<verbatim chemical name or formula>"],
       "drug_class": "<verbatim class words on the page, or empty>"}
     ],
     "abbreviations": [{"short": "<MI>", "long": "<myocardial
                        infarction>"}]
    }
    Relation meanings and directions (strict):
    PRESENTS_WITH: from = a disease/condition, to = a symptom or sign
      that it causes or that patients with it show.
    TREATED_BY: from = a disease, condition OR symptom, to = a drug,
      procedure, diet or other treatment used for it (including
      prevention and prophylaxis).
    HARMS: from = a treatment, to = a disease/condition or symptom that
      the treatment causes (adverse effect, side effect, toxicity,
      complication of a procedure). Use subtype CONTRAINDICATED_IN when
      the sentence says the treatment must not be given to people who
      HAVE the condition (to = that condition).
    LEADS_TO: from = a disease/condition, to = another disease/condition
      that it causes, progresses to, or whose risk it raises
      (complication, sequela, risk factor stated as a condition).
    MISTAKEN_FOR: two diseases/conditions named as differential
      diagnoses of each other, or one said to mimic or be confused with
      the other. Order does not matter.
    Group rules: symptoms-and-signs = what a patient feels or an
    examiner observes or measures, not chronic; diseases-and-conditions
    = named diseases, syndromes, infections, injuries, poisonings,
    deficiencies, chronic states, abnormalities defined by measurement;
    treatments-and-drugs = drugs, vaccines, procedures, surgery,
    radiation, dialysis, transplantation, diet or lifestyle named as
    treatment. When a symptom and disease reading are both possible
    with no clue, choose symptoms-and-signs. A chronic state is a
    disease. A term is written exactly as the page writes it (keep
    spelling, hyphens, capitalisation).
    Extraction rules: (1) one edge per proving sentence per pair; if a
    sentence lists five symptoms of one disease, output five edges with
    the same quote; (2) a table row is a sentence: for a table of drugs
    and adverse effects, each cell pair is an edge with the row text as
    quote, prefixed by the table title; (3) quote only what is printed;
    never paraphrase inside "quote"; never merge two sentences unless
    the second is needed to name the subject (e.g. "It causes ..." ->
    include the previous sentence that names "It"); (4) do not extract
    from the context blocks except for a sentence crossing the page
    boundary; (5) do not extract anatomy, physiology, mechanisms,
    history, epidemiology without a relation, or references; (6) if the
    page has no extractable relation, output {"subjects":[...],
    "edges":[],"drugs":[],"abbreviations":[]}; (7) numbers: copy the
    percentage in the quote into numeric_pct only when the quote states
    it for this exact relation.

7.2 User message (built by the script):
      BOOK FIELD: <field_name>   BOOK: <title>
      CHAPTER: <district name>   PROVINCE: <province name / part_name>
      PRINTED PAGE: <p>
      <<<PREVIOUS PAGE ... >>> ... <<<THIS PAGE ... >>> ... <<<NEXT PAGE ... >>> ...
    Call: reader.ask(P_B1 + additional_rules, user, max_tokens=6000).
    If the reader returns invalid JSON twice, the page is marked
    "failed" with the error and the run continues.
7.3 Token budget at 16k context: system prompt about 1,300 tokens; a
    dense page with figure block about 2,500; two context blocks about
    900; output up to 6,000. Fits with margin. If the server reports a
    context overflow, the script halves MAX_PAGE_CHARS for that page
    and retries once.

8. STEP B4 -- PROVENANCE CHECK, F-SCALE, SEVERITY (pure script, no AI)
--------------------------------------------------------------------------------
8.1 Why a script here: Law 2 says every claim carries a verbatim quote
    from a page. The script only verifies that the quote the reader
    wrote is really on that page. It judges nothing about medicine.
8.2 Quote verification, in order:
    (a) Normalise both the quote and the window text: lowercase; replace
        every run of whitespace with one space; replace curly quotes and
        dashes with straight ones; remove soft hyphens.
    (b) If the normalised quote is a substring of the normalised window
        (this page plus both context blocks): PASS, status "exact".
    (c) Else compute the best partial match with
        rapidfuzz.fuzz.partial_ratio(quote, window). If >= 92: PASS,
        status "fuzzy" (tolerates a dropped comma or an OCR slip). The
        stored quote becomes the matching window substring (the book's
        text wins over the reader's copy): use
        rapidfuzz.fuzz.partial_ratio_alignment to get the span.
    (d) Else FAIL: the edge is NOT stored. It is written to
        kitchen/logs/<BOOK_ID>-unverified.jsonl with the reader's quote
        and the page, and counted in the ledger as "unverified". This
        is a provenance rule, not a medical judgement: a sentence that
        is not on the page cannot be cited.
    Table rows: the figure-pass table text is part of the window, so
    quotes from tables verify normally.
8.3 F-scale mapping (the full table; applied to frequency_phrase after
    lowercasing; the FIRST matching rule in this order wins; if
    numeric_pct is not null the NUMERIC rule wins over words):
    NUMERIC: pct > 50 -> F5; 10 < pct <= 50 -> F4; 1 < pct <= 10 -> F3;
             0.1 < pct <= 1 -> F2; pct <= 0.1 -> F1.
    F5 words: "most patients", "the majority", "majority of", "nearly
       all", "almost all", "virtually all", "all patients", "usually",
       "typically", "characteristic", "the hallmark", "hallmark",
       "invariably", "universal", "cardinal", "classic", "classically",
       "predominant", "common presentation", "most common", "the most
       frequent", "in most".
    F4 words: "common", "commonly", "frequent", "frequently", "often",
       "many patients", "a substantial", "a significant proportion",
       "a large proportion", "not uncommon", "regularly", "well
       recognized", "well-recognized", "prominent".
    F3 words: "occasionally", "sometimes", "in some patients", "some
       patients", "a minority", "less common", "less commonly", "less
       frequent", "may occur", "can occur", "has been reported in some",
       "uncommon", "uncommonly", "infrequently" (note: "infrequently" is
       F3 here but "infrequent" alone is F2; the longer word is matched
       first).
    F2 words: "rare", "rarely", "infrequent", "unusual", "seldom", "few
       patients", "a small number", "a small proportion", "on rare
       occasions", "in rare cases".
    F1 words: "very rare", "very rarely", "extremely rare", "exceedingly
       rare", "exceptional", "exceptionally", "case reports", "isolated
       reports", "anecdotal", "has been described" (only when no other
       rule matched).
    F0: frequency_phrase empty, or no rule matched. The unmatched
    phrase is kept verbatim and counted in the ledger as
    "frequency-phrase-unmapped" so the human can add rules.
    Negations: if the frequency_phrase contains "not" or "no" directly
    before a frequency word ("not common", "not rare"), the mapped
    level is replaced: not common -> F3, not rare -> F4, not unusual ->
    F4, not infrequent -> F4. Otherwise F0 and ledger-counted.
8.4 Severity (boolean) is true when severity_phrase is non-empty OR the
    quote (lowercased) contains any of: "fatal", "fatality", "death",
    "life-threatening", "life threatening", "lethal", "boxed warning",
    "black box", "medical emergency", "requires immediate",
    "requires urgent", "potentially fatal", "mortality", "irreversible",
    "permanent". severity_phrase stores the matched words if the reader
    left it empty. Severity is recorded for every relation type but
    only drawn (red ring) on yellow edges (Part 1 section 3.7 e).
8.5 Direction sanity (script): an edge whose from_group/to_group do not
    fit its relation (e.g. PRESENTS_WITH from a treatment) is not
    rejected; the script tries the single legal reinterpretation:
    PRESENTS_WITH with from = symptom and to = disease -> swap; HARMS
    with from = disease and to = treatment -> swap; TREATED_BY with from
    = treatment -> swap. If still illegal, the edge goes to
    unverified.jsonl with reason "direction". Resolution (section 9)
    then uses the registry's TRUE groups, which override the reader's
    group guesses; a mismatch after resolution is handled in 9.5.

9. STEP B5 -- RESOLUTION AGAINST THE FROZEN REGISTRY, AND QUARANTINE
--------------------------------------------------------------------------------
9.1 Every term string that appears in "subjects", "edges" (from, to) or
    "drugs" must be mapped to a frozen Entity slug, or to QUARANTINE.
    The mapping is cached per book in
    kitchen/logs/<BOOK_ID>-resolve-cache.json:
      {"<normalised term>": {"slug": "...", "how": "exact|alias|abbrev|
       reader|quarantine", "confidence": 0.9, "date": "..."}}
    and a global cache kitchen/logs/resolve-cache-global.json is
    consulted first (decisions made in earlier books are reused: the
    same synonym does not cost a second reader call). normalised term =
    lowercase, whitespace collapsed, trailing "s" NOT stripped (plural
    handling is left to the reader).
9.2 Resolution order for a term T with reader group guess G:
    (a) EXACT NAME: slugify(T) equals the name part of an existing slug
        -> that entity (any group; the registry's group wins).
    (b) ALIAS: normalised T equals a normalised alias of an entity ->
        that entity.
    (c) ABBREVIATION: T is all-caps, length 2-6, and equals an entry in
        some entity's abbreviations list (Amendment 4.3) -> that entity;
        if T matches abbreviations of two or more entities, go to (d)
        with those as candidates. The page's own "abbreviations" output
        is applied FIRST: if the page defines "MI = myocardial
        infarction", then T = "MI" is replaced by the long form before
        step (a). Page-defined abbreviations are added to the resolved
        entity's abbreviations list.
    (d) CANDIDATES: full-text query (Part 3 section 7.6 b) plus
        rapidfuzz top 5 within group G, union, max 8. If no candidate
        has token_set_ratio >= 60 and no full-text score >= 1.0:
        QUARANTINE (how = "quarantine", reason "no-candidates").
    (e) READER, prompt P-B2 (same as P-A4c with one more option).
        System message:

        You decide whether a medical term found on a textbook page is
        the SAME entity as one of the candidate entities in a frozen
        registry, or NONE of them. Same entity means the same disease,
        symptom or treatment under another spelling, word order,
        synonym, eponym, plural, abbreviation or brand name. Different
        means a distinct concept even if related (a disease vs its
        subtype, complication or location variant; a drug vs its class;
        a symptom vs the disease named after it). Output ONLY JSON:
        {"decision":"SAME"|"NONE","candidate_slug":"<slug or null>",
         "confidence":<0.0-1.0>,"reason":"<max 15 words>"}

        User message: {"term": T, "group_guess": G, "sentence": <the
        quote or the first sentence mentioning T on the page>,
        "chapter": <district name>, "book_field": <field_name>,
        "candidates": [{"slug", "canonical_name", "aliases" (up to 8),
        "group"}]}
        SAME with confidence >= 0.6 -> resolved (how = "reader"). If
        confidence >= 0.8 and T has 4+ characters and T is not already
        an alias: add T to the entity's aliases (Freeze A allows alias
        growth). SAME with confidence < 0.6, or NONE -> QUARANTINE
        (reason "reader-none" or "reader-low").
9.3 Quarantine node (Cypher):
      MERGE (q:QuarantineTerm {term:$term, book_id:$book_id,
                               district_id:$did})
      ON CREATE SET q.group_guess=$g, q.page_number=$page,
        q.image_file=$image, q.quote=$quote, q.reader_model=$model,
        q.read_date=date(), q.resolved=false, q.count=1, q.reason=$reason
      ON MATCH SET q.count = q.count + 1
    An edge with a quarantined endpoint is NOT stored as an edge; it is
    written to kitchen/logs/<BOOK_ID>-quarantined-edges.jsonl in full
    (both terms, relation, quote, page) so nothing is lost. The
    published quarantine list (Part 9) shows the terms and their
    counts. After the human reviews quarantine (section 13.4) and maps
    a term to a slug or asks for a new entity (which is a formal
    amendment of the registry, allowed only by the human, recorded
    under DECISIONS BY HUMAN), the quarantined-edges file is replayed
    through the loader. This is how "unknown" never means "dropped".
9.4 Terms that are not entities (the reader sometimes names an organism
    or an organ in "from"): they will not match the registry and will go
    to quarantine with their count; the human sees "Staphylococcus
    aureus, 212 occurrences" and either maps it to the infection
    entity or marks it "not-an-entity" (q.resolved = true,
    q.resolution = "not-an-entity"), after which the term is cached and
    never asked again.
9.5 Group check after resolution. The registry's groups are the truth.
    Legal pairs: PRESENTS_WITH disease->symptom; TREATED_BY
    disease|symptom->treatment; HARMS treatment->disease|symptom;
    LEADS_TO disease->disease; MISTAKEN_FOR disease<->disease. If the
    resolved pair is illegal, apply the swaps of 8.5 once; if still
    illegal, write to unverified.jsonl with reason "group-after-
    resolution" and count it. (Example that will happen: PRESENTS_WITH
    from "hypertension" (disease) to "headache" (symptom) is legal;
    LEADS_TO from "hypertension" to "headache" is not -> it becomes
    PRESENTS_WITH automatically by this rule: LEADS_TO disease->symptom
    is converted to PRESENTS_WITH; TREATED_BY disease->disease is
    written to unverified with reason, never guessed.)

10. STEP B6 -- LOADING INTO NEO4J (script kitchen/load_extractions.py;
    idempotent; runs every LOAD_EVERY_PAGES pages and at the end)
--------------------------------------------------------------------------------
10.1 quote_hash = sha1(relation + "|" + from_slug + "|" + to_slug + "|"
     + normalised quote). For MISTAKEN_FOR, from/to are ordered by slug
     (smaller first) before hashing and storing (Part 2 section 6.1 E).
10.2 Edge (one statement per relation type; relation names are literal
     in Cypher, so the script has five copies of this with the type
     substituted):
       MATCH (a:Entity {slug:$from}), (b:Entity {slug:$to})
       MERGE (a)-[r:PRESENTS_WITH {quote_hash:$h}]->(b)
       ON CREATE SET r.district_id=$did, r.book_id=$book, r.page_number=$page,
         r.image_file=$image, r.quote=$quote, r.frequency_phrase=$fp,
         r.f_scale=$f, r.numeric_pct=$pct, r.severity=$sev,
         r.severity_phrase=$sp, r.subtype=$subtype, r.reader_model=$model,
         r.read_date=date(), r.source="page", r.verify_status=$vs
       RETURN r.quote_hash
10.3 Page lit spots: for every resolved term in "subjects" and every
     resolved endpoint of a stored edge:
       MATCH (e:Entity {slug:$slug}), (d:Territory {territory_id:$did})
       MERGE (e)-[r:DISCUSSED_IN {book_id:$book, page_number:$page, source:"page"}]->(d)
       ON CREATE SET r.quote=$quote, r.image_file=$image,
         r.reader_model=$model, r.read_date=date()
     quote = the sentence mentioning the term (for subjects: the first
     sentence on the page containing it; for edge endpoints: the edge's
     quote).
10.4 Drug details:
       MATCH (e:Entity {slug:$slug})
       SET e.generic_names = [x IN e.generic_names + $generic WHERE x IS NOT NULL],
           e.brand_names = e.brand_names + [x IN $brand WHERE NOT x IN e.brand_names],
           e.formulas = e.formulas + [x IN $formulas WHERE NOT x IN e.formulas],
           e.drug_class = coalesce(e.drug_class, $drug_class)
     (apply the same "only if not already present" pattern to
     generic_names; the first form shown is simplified; the script
     must deduplicate all three lists). drug_class keeps the FIRST
     verbatim class seen; all other class words seen are appended to a
     list property drug_class_mentions for Part 5 to use.
10.5 Abbreviations: MATCH (e:Entity {slug:$slug}) WHERE NOT $short IN
     e.abbreviations SET e.abbreviations = e.abbreviations + $short
     (initialise the list to [] where null).
10.6 After loading a page: ledger line stage "loaded". Verification
     query after each batch, output appended to <BOOK_ID>-run.log:
       MATCH ()-[r]->() WHERE r.book_id=$book AND r.source="page"
       RETURN type(r), count(*) ORDER BY type(r);

11. STEP B7 -- THE PILOT (SMART runs; human reviews)
--------------------------------------------------------------------------------
11.1 Pilot pages (Harrison, 24 printed pages): 133-136 (Ch. 20 Fever),
     2133-2138 (Ch. 288 Hypertension, first six pages), 3205-3212
     (Ch. 416 Diabetes management: drugs and TREATED_BY), 416-421
     (Ch. 63 Cutaneous Drug Reactions: HARMS). Run transcription,
     figure pass, extraction, verification, resolution, loading for
     exactly these pages: python kitchen/read_pipeline.py HARRISON-22
     --pages 133-136,2133-2138,3205-3212,416-421
11.2 kitchen/review_pages.py HARRISON-22 writes
     kitchen/logs/HARRISON-22-pilot-review.md with: per page the
     counts (edges stored, unverified, quarantined, seconds); 30 random
     stored edges shown as "FROM -> relation -> TO | F<n> '<frequency
     phrase>' | severity | quote | page"; all unverified quotes with
     the reader's text next to the nearest window text; the quarantine
     terms with counts; the resolution decisions made by the reader
     with their reasons.
11.3 The human reads it and answers: "ok", or "add rule: <text>" (goes
     into the Additional rules of P-B1 or P-B2), or "map <term> ->
     <slug>" (goes into the global resolve cache), or "not-an-entity:
     <term>". SMART applies, re-runs the pilot pages (delete their
     ledger lines first), and repeats until the human says ok.
  CHECKPOINT 4.1: pilot approved. Record the average seconds per page
  for text-only pages and for figure-pass pages in PROGRESS.md: this is
  the only timing yardstick, used to estimate the full runs.

12. STEP B8 -- THE FULL RUNS  [SWITCH TO CHEAP]
--------------------------------------------------------------------------------
12.1 Start a book:
       nohup python kitchen/read_pipeline.py HARRISON-22 > kitchen/logs/HARRISON-22-read.log 2>&1 &
     Write in PROGRESS.md: "Phase B HARRISON-22 running since <time>;
     estimated <pages x seconds>". Stop the chat. The human checks
     progress with: tail -n 3 kitchen/logs/HARRISON-22-read.log and
     wc -l kitchen/logs/HARRISON-22-pages.jsonl
12.2 The runner: transcribes a whole district, then extracts and
     resolves its pages in plan order, loads every LOAD_EVERY_PAGES
     pages, writes the ledger, continues. Resumable at any time
     (skips "loaded" pages). On reader-server failure (connection
     refused) it waits 60 seconds and retries forever (the human may
     have restarted the server). On 20 consecutive page failures it
     stops and writes BLOCKED.
12.3 Every 500 loaded pages, and at the end of each book, the runner
     runs review_pages.py and git-commits the small logs (pages.jsonl,
     resolve caches, run log, review md); never the transcripts or
     extractions.
12.4 Running on the Desktop PC at night (optional): copy kitchen/
     books/<pdf>, kitchen/pages/<BOOK_ID>/ and the repo to the desktop;
     set .env there to the desktop's reader server; run
     read_pipeline.py with --no-load (extractions written to JSON
     only); copy kitchen/extractions/<BOOK_ID>/ back to the laptop and
     run load_extractions.py <BOOK_ID>. Neo4j stays only on the laptop.
     The ledger file is merged by the loader (it rewrites "loaded"
     lines). Not required; written here so the manager does not invent
     a different scheme.
12.5 Next book only after the human says "ok" to the previous book's
     review (section 13).

13. STEP B9 -- REVIEWS, ADDITIONAL RULES, QUARANTINE, LEDGER
--------------------------------------------------------------------------------
13.1 Review file per book (review_pages.py, same as pilot but with 60
     random edges, 20 per colour group blue/yellow/grey).
13.2 Additional rules. The human's corrections become numbered rules
     appended to kitchen/prompts/additional-rules-P-B1.txt and
     additional-rules-P-B2.txt (committed). They apply to all later
     pages; earlier pages are re-read only if the human says so (each
     re-read costs time, not money).
13.3 Frequency phrases unmapped: kitchen/logs/unmapped-frequency.jsonl
     is summarised (phrase, count) in the review; the human may add a
     phrase to one F-level in kitchen/prompts/fscale-extra.json
     ({"F3": ["in a subset of patients"], ...}); the loader re-maps
     F0 edges with that phrase on the next run (UPDATE of r.f_scale,
     logged).
13.4 Quarantine review: review file lists the top 50 quarantine terms
     by count. The human answers per term: "map -> <slug>",
     "not-an-entity", or "new entity: <group> <name>" (rare; a registry
     amendment, logged under DECISIONS BY HUMAN; the new entity gets
     frozen = true, altitude assigned by Part 5's rule at the next
     altitude run). Then: python kitchen/replay_quarantine.py <BOOK_ID>
     re-runs the quarantined-edges file through verification and
     loading.
13.5 Ledger numbers per book, written by the loader to
     data/registry/phase-b-ledger.json (committed) and shown in Part 9:
     pages planned, pages loaded, pages failed, figure-pass pages,
     edges stored by type, edges unverified, edges quarantined, F0
     share (percentage of stored edges with f_scale 0), severity edges,
     quarantine terms open/resolved, aliases added, seconds total.
     Honest numbers; never rounded up.
  CHECKPOINT 4.2: Harrison fully loaded and its review approved.
  CHECKPOINT 4.3: all accepted books loaded and reviewed.

14. SCRIPT LIST FOR THIS PART (SMART writes; all under kitchen/)
--------------------------------------------------------------------------------
  page_plan.py        <BOOK_ID>               -> <BOOK_ID>-plan.json
  transcribe.py       <BOOK_ID> --district D  -> transcripts (3, 4, 5)
  windows.py          (library)               -> build_window(book, p)
  extract.py          <BOOK_ID> --page p      -> extractions/p<p>.json (7)
  verify.py           (library)               -> verify_quote, f_scale,
                                                 severity, direction (8)
  resolve.py          (library + CLI)         -> resolve_term(T, G, ctx) (9)
  load_extractions.py <BOOK_ID> [--pages]     -> Neo4j (10)
  read_pipeline.py    <BOOK_ID> [--pages a-b,c-d] [--no-load]  -> runs all
  review_pages.py     <BOOK_ID> [--pilot]     -> review md (11, 13)
  replay_quarantine.py <BOOK_ID>              -> (13.4)
  prompts/P-B0.txt, P-B0f.txt, P-B1.txt, P-B2.txt  the prompts of this
                      part, verbatim, read by the scripts (never
                      hard-coded inside Python, so the human can read
                      and edit them)
  prompts/additional-rules-P-B1.txt, additional-rules-P-B2.txt,
  fscale-extra.json
  Each script under 250 lines, prints a one-line summary, appends to
  <BOOK_ID>-run.log. SMART tests each on one page before the pilot.
  Reference implementation of the two most delicate functions:

    # kitchen/verify.py (core of 8.2)
    import re, hashlib
    from rapidfuzz import fuzz
    def norm(s):
        s = s.lower().replace("\u00ad", "")
        s = re.sub(r"[\u2018\u2019]", "'", s); s = re.sub(r"[\u201c\u201d]", '"', s)
        s = re.sub(r"[\u2013\u2014]", "-", s)
        return re.sub(r"\s+", " ", s).strip()
    def verify_quote(quote, window):
        q, w = norm(quote), norm(window)
        if not q:
            return None, "empty"
        if q in w:
            return quote.strip(), "exact"
        al = fuzz.partial_ratio_alignment(q, w)
        if al and al.score >= 92:
            return w[al.dest_start:al.dest_end], "fuzzy"
        return None, "fail"
    def quote_hash(relation, a, b, quote):
        if relation == "MISTAKEN_FOR" and b < a:
            a, b = b, a
        return hashlib.sha1(f"{relation}|{a}|{b}|{norm(quote)}".encode()).hexdigest()

    # kitchen/windows.py (core of 6.1)
    def tail_at_sentence(text, n):
        cut = text[-n:] if len(text) > n else text
        i = cut.find(". ")
        return cut[i + 2:] if 0 <= i < len(cut) - 2 else cut
    def head_at_sentence(text, n):
        cut = text[:n] if len(text) > n else text
        i = cut.rfind(". ")
        return cut[:i + 1] if i > 0 else cut
    def build_window(prev_text, this_text, next_text, p, n_prev, n_next):
        parts = []
        if prev_text:
            parts.append(f"<<<PREVIOUS PAGE {p-1}, LAST PART (context only)>>>\n{tail_at_sentence(prev_text, n_prev)}")
        parts.append(f"<<<THIS PAGE {p} (extract from here)>>>\n{this_text}")
        if next_text:
            parts.append(f"<<<NEXT PAGE {p+1}, FIRST PART (context only)>>>\n{head_at_sentence(next_text, n_next)}")
        return "\n\n".join(parts)

15. DEFAULTS IN THIS PART THAT THE HUMAN MAY OVERTURN
--------------------------------------------------------------------------------
  (1) Text-first transcription; vision only for figure/table pages
      (Amendment 4.1; VISION_MODE in .env).
  (2) Window context 1,500 characters each side (6.1).
  (3) Reading order: Harrison Part 2 first, then Pharmacology, then the
      rest; other books in page order (2.2).
  (4) Quote verification threshold partial_ratio >= 92 (8.2 c).
  (5) The F-scale word lists and negation rules (8.3); extendable via
      fscale-extra.json.
  (6) Severity word list (8.4).
  (7) Resolution: SAME needs confidence >= 0.6; alias added at >= 0.8
      and 4+ characters (9.2 e).
  (8) LEADS_TO disease->symptom is auto-converted to PRESENTS_WITH; all
      other illegal pairs go to unverified (9.5).
  (9) Reference lists cut from transcripts (3.2).
  (10) Pilot pages (11.1).

================================================================================
HANDOFF CAPSULE (updated; paste into a NEW conversation with Fable when
asking for the next part)
================================================================================
Project: "Second Opinion", a medical knowledge globe built only from N
(up to 42) medical textbooks the human owns, vibe-coded, open source,
hosted at https://www.strulovitz.org/2nd-opinion/ from the human's own
computers via Cloudflare Tunnel, synced through
https://github.com/strulovitz/second-opinion (laptop = kitchen with
Neo4j; desktop serves static site/ only). Fable writes a 13-delivery
BIBLE (9 parts + 4 appendix templates) in plain text, one copy-paste
block per delivery, no tables, no collapsibles, formulas in words plus
LaTeX. Delivered: Part 1 (charter, 15 laws, world model), Part 2
(environment, repo layout kitchen/ data/ site/ BIBLE/, AGENTS.md +
PROGRESS.md, Neo4j schema: Book, Territory, Entity(+Symptom/Disease/
Treatment), QuarantineTerm, Meta; DISCUSSED_IN lit spots; edges
PRESENTS_WITH, TREATED_BY, HARMS(subtype CONTRAINDICATED_IN), LEADS_TO,
MISTAKEN_FOR(stored once, smaller slug first) with provenance,
frequency_phrase, f_scale 0-5, numeric_pct, severity, quote_hash; one
relationship per proving sentence; kitchen/db.py, reader.py
ask(system,user,images); export = geography.json, books.json,
search.json, entities/<slug>.json, quarantine.json, ledger.json), Part 3
(Phase A: books.json; TOC -> provinces/districts; page_offset; N-point
Fibonacci sphere + nearest-centre Voronoi EQUAL-area continents, greedy
cluster seating, recursive treemap split making district area ~ page
count, 2048x1024 equirectangular district raster + continents_texture
+ districts_lookup.json; index pipeline P-A4a/P-A4b/P-A4c builds the
entity registry with lit spots from index page refs; Harrison first;
Freeze A = geography + entity slugs/groups/names frozen, aliases may
grow, registries in data/registry/*.csv = Appendices A-C), Part 4
(Phase B: text-first transcription via pdftotext -layout, reference
lists cut, vision pass P-B0f only for pages with images/tables, full
OCR P-B0 for books without text layer; sliding window = prev-page tail
1500 chars + this page + next-page head 1500 chars, never across a
chapter; extraction prompt P-B1 -> subjects, edges with verbatim quote
+ frequency_phrase + numeric_pct + severity_phrase + subtype, drugs
(generic/brand/formula/class), abbreviations; script-only provenance
check: quote must be substring or partial_ratio >= 92 of the window,
else unverified.jsonl; full F-scale word table + numeric rule +
negations; severity word list; direction swaps; resolution against
frozen registry: exact -> alias -> abbreviation -> candidates
(fulltext + rapidfuzz) -> reader P-B2 SAME/NONE >= 0.6, alias added at
>= 0.8; unknown -> QuarantineTerm with count, quarantined edges kept in
a replay file; idempotent loading by quote_hash; per-page ledger
pages.jsonl; resolve caches per book + global; pilot of 24 Harrison
pages reviewed by human; nohup full runs book by book, resumable;
reviews with additional-rules files; phase-b-ledger.json honest
numbers; checkpoints 4.1-4.3). World model: WHERE = library geography;
WHICH = altitude, one shell per entity: diseases r 0.30-1.00 by breadth
(deep = multisystem), symptoms 1.00-1.50 by specificity (low =
nonspecific), treatments 1.50-3.00 by heaviness (lifestyle -> OTC ->
prescription -> biologics/chemo/radiation -> surgery) with drug classes
adjacent, every drug its own shell. No single home (Law 8). Rigid
layout. Viewer: 3-D globe <-> 2-D equirectangular map, lit filled
circles at district centres sized by F (F0 dashed), blue forward /
yellow harm / grey differential, severity red ring, desktop + mobile,
no build step, vendored JS. Tiers: READER = free local Qwen 3.8 27B
Q4_K_M (Gemma 4 31B substitute) does all per-page/per-term work; CHEAP
= DeepSeek V4.1 Flash runs scripts; SMART = Claude Sonnet 5.5 or GPT
6.1 Sol writes scripts; manager says "HUMAN: please switch to <tier>"
and stops. Laws include: books only, provenance always, Neo4j single
source of truth, cheap beats perfect, never assume installed, when
unclear stop and ask, one disclaimer only (index.html bottom), no
multi-model editions, books/images/transcripts never committed.
Next delivery requested: Part 5 (Phase C -- Altitude assignment:
computing specificity for symptoms from PRESENTS_WITH edges plus index
proxies, breadth for diseases from distinct books, heaviness group and
drug class for treatments from the books' pharmacology chapters via a
reader prompt, ordering and tie-breaks, the radius formula per band,
Freeze B, Appendix C altitude columns and Appendix D heaviness groups,
re-run rule when the human adds quarantine entities).
================================================================================
