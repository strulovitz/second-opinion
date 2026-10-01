================================================================================
SECOND OPINION -- THE BIBLE
PART 1 OF 13 -- CHARTER AND WORLD MODEL
File: BIBLE/part-01-charter-and-world-model.md
================================================================================

0. HOW TO READ THIS DOCUMENT
--------------------------------------------------------------------------------

0.1 Who reads it
  - The HUMAN: the project owner. Makes all final decisions.
  - The ARCHITECT: Fable (Claude Fable 5.1), who writes the BIBLE parts.
  - The MANAGER: the AI model working inside OpenCode on the human's
    computer. One of: Claude Sonnet 5.5, GPT 6.1 Sol, DeepSeek V4.1 Flash.
    The BIBLE tells which one to use for which work (see section 8).
  - The READER: a free local vision-language model (Qwen 3.8 27B Q4_K_M
    first choice; Gemma 4 31B as substitute) running on the human's laptop
    through Unsloth Studio, LM Studio, or Ollama. It reads page images and
    classifies terms. It costs no money. It is slow. That is fine.

0.2 Writing style of this BIBLE
  The MANAGER is assumed to be honest but not brilliant. Therefore nothing
  important is left to the manager's judgement that can instead be written
  down as a rule. Where judgement is unavoidable, the BIBLE says exactly
  what information to look at and exactly what to write down about the
  decision.

0.3 THE MOST IMPORTANT INSTRUCTION TO THE MANAGER
  If any sentence in this BIBLE is unclear to you, or two sentences seem
  to contradict, or a step needs information you do not have: STOP. Write
  in PROGRESS.md under the heading "QUESTIONS FOR HUMAN" exactly what is
  unclear, and tell the human in chat. Do NOT guess. Do NOT fill the gap
  with your own invention. Do NOT substitute a different approach. An
  honest "I do not understand step 4.3" is a success. A silent guess is
  the worst possible failure in this project.

0.4 Where the BIBLE lives
  In the GitHub repository (section 7), folder BIBLE/, one Markdown file
  per part. The manager re-reads the governing part at the start of every
  session (the mechanism is in section 9 and in Part 8).

1. MAP OF THE WHOLE BIBLE
--------------------------------------------------------------------------------
  Part 1  Charter and World Model (this file). Written by Fable.
  Part 2  Environment and Data Model. Opening section: inventory of what
          is already installed on the laptop (Debian 13) and installation
          of what is missing. Then: Neo4j schema, stable IDs and slugs,
          repository layout, how the website folder is mounted under the
          main website. Written by Fable.
  Part 3  Phase A -- Building the Skeleton: geography from the 42 Tables
          of Contents, entity registry from the back-of-book Indexes, the
          one-book-per-field rule, the review checkpoints, the Freeze.
          Algorithm by Fable; execution by the manager + reader; results
          go into Appendices A, B, C.
  Part 4  Phase B -- The Reading Pipeline: the reader reads page images,
          the sliding window across page boundaries, the extraction
          prompt, entity resolution by AI with context (not by script),
          the F-scale mapping table. Written by Fable.
  Part 5  Phase C -- Altitude assignment: specificity (symptoms), breadth
          (diseases), heaviness + class (treatments), final radii.
          Algorithm by Fable; execution by manager; results into
          Appendices C and D.
  Part 6  The HTML pages: TL;DR, ELI5, caused-by / treated-by / harms /
          often-mistaken-for sections, verbatim quotes with book and page,
          relative links, back-to-globe links. Written by Fable.
  Part 7  The Viewer: 3-D globe <-> 2-D maps (Google-Earth style), the
          altitude elevator, lit circles sized by frequency, blue/yellow,
          URL scheme, works on desktop and smartphone browsers.
          Written by Fable.
  Part 8  Manager Operating Protocol: AGENTS.md, PROGRESS.md, the
          evidence rules, batch procedure, model-switch procedure, what to
          do when stuck. Written by Fable.
  Part 9  Publishing and the Quality Ledger: static export, the main page
          with the single disclaimer, serving from the local git clone via
          Cloudflare Tunnel, honest published numbers. Written by Fable.
  Appendix A  Field Registry (the 42 books -> 42 continents). Template by
              Fable, filled by manager.
  Appendix B  Territory Atlas (every province and district with page
              ranges and coordinates). Template by Fable, filled by
              manager.
  Appendix C  Entity and Altitude Registry (every entity, its group, its
              aliases, its altitude). Template by Fable, filled by
              manager + reader.
  Appendix D  Treatment Heaviness Groups and Classes. Template by Fable,
              filled by manager.
  Total: 13 deliveries from Fable (9 parts + 4 appendix templates).
  The appendices are FROZEN after the Freeze (Part 3) and never change.

2. THE CHARTER -- FIFTEEN LAWS
--------------------------------------------------------------------------------
  These are copied verbatim into AGENTS.md. They never change.

  LAW 1. EVERYTHING COMES FROM THE 42 BOOKS. No open datasets, no FDA or
  EMA or WHO lists, no Wikipedia, no drug databases, no "general
  knowledge" of any AI model. If a fact is not on a page of one of the
  books, it is not in Second Opinion. Sole exception: the HUMAN may paste
  a Wikipedia passage manually for a term the reader could not
  understand; it is stored with source = "manual-wikipedia" so it is
  visibly different.

  LAW 2. EVERY CLAIM CARRIES PROVENANCE. Every lit spot, every edge, every
  quote stores: book ID, district ID (chapter), printed page number, image
  file name, and the verbatim sentence(s) it came from. A fact without
  provenance is deleted, not displayed.

  LAW 3. VERBATIM FIRST, PARAPHRASE SECOND. The books' own words (names,
  synonyms, chemical names, formulas, frequency words such as "rarely" or
  "in 30% of patients") are stored exactly. Simplified ELI5 text is
  additional and is always labelled as AI-written.

  LAW 4. NEO4J IS THE SINGLE SOURCE OF TRUTH. NetworkX is used for
  computations (counting, ranking, ordering). Matplotlib is used for
  diagnostic pictures and 2-D map previews. The website is a static export
  FROM Neo4j. The manager may never substitute "a JSON file" or "an
  in-memory graph" for the Neo4j database and call the job done.

  LAW 5. THE LAYOUT IS RIGID. No force-directed layout anywhere. Nothing
  moves, bends, or re-arranges when the user clicks. Geography comes from
  the Tables of Contents; altitude comes from the registries; both are
  frozen at the Freeze. Highlights are temporary overlays only.

  LAW 6. ONE BOOK PER FIELD. Two books on the same subject are never both
  ingested. The duplicate-detection procedure is in Part 3; the human
  makes the final choice of which book to keep.

  LAW 7. THREE GROUPS, NOTHING ELSE. Every entity is exactly one of:
  symptoms-and-signs, diseases-and-conditions, treatments-and-drugs.
  Chronic -> disease. Test findings and measured abnormalities (for
  example a blood-pressure reading) -> disease. Doubtful things stay as
  symptoms (symptoms are the gates into the system). Splitting one term
  into two entities (pain / chronic pain) is a rare, explicitly recorded
  exception.

  LAW 8. NO SINGLE HOME. A disease, a symptom, or a treatment is never
  assigned to one "canonical" chapter or field. It owns ONE ALTITUDE and
  lights up in EVERY territory where the books discuss it.

  LAW 9. FORWARD IS BLUE, HARM IS YELLOW. Symptom -> disease and
  disease -> treatment are blue. Treatment -> harm and disease ->
  complication are yellow. Side effects are first-class citizens, never
  hidden, never summarised away.

  LAW 10. FREQUENCY DECIDES SIZE. Every edge carries the book's frequency
  wording mapped to the F-scale (section 3.7). Common things are drawn
  big, rare things small, unknown things dashed. The manager and the
  reader never invent a frequency the book did not state.

  LAW 11. REPORT WITH EVIDENCE OR NOT AT ALL. "Done" must come with proof:
  the Cypher query and its output, the ls of the files, the row counts.
  "I have populated the database" with nothing attached is a violation.
  Write "I could not do X because Y" in PROGRESS.md rather than quietly
  doing something else. Substituting a technology, skipping a step, or
  faking a result is the one unforgivable act in this project.

  LAW 12. ONE DISCLAIMER, ONCE. The main page of the project carries, at
  its bottom, one fixed notice: not a doctor, not medical advice,
  AI-generated from textbooks, may contain mistakes, offered as another
  angle. This notice appears NOWHERE ELSE. No per-page disclaimers, no
  red-flag routing, no hallucination checker, no filtering of what the
  books say.

  LAW 13. NEVER ASSUME WHAT IS INSTALLED. Before using any software
  (Neo4j, Python, NetworkX, Matplotlib, the Python Neo4j driver, Node,
  any JavaScript library, the local model server, cloudflared, git), the
  manager checks whether it is installed and which version, records the
  result in PROGRESS.md, and installs what is missing (asking the human
  before anything that needs sudo or a download larger than 1 GB).
  Part 2 opens with the exact inventory procedure.

  LAW 14. CHEAP BEATS PERFECT. The human pays per token for the manager.
  Therefore: (a) all per-page and per-term work (reading pages,
  classifying index terms, extracting edges) is done by the free local
  READER, never by the paid manager; (b) the manager writes scripts and
  reviews samples, it does not do grunt work by hand; (c) when a choice
  exists between a high-quality solution needing hours of manager time and
  a simpler solution needing minutes, take the simpler one and write the
  high-quality one down in PROGRESS.md under "LATER, IF MONEY"; (d) the
  cheapest manager tier that can do a step is used for that step
  (section 8).

  LAW 15. WHEN UNCLEAR, STOP AND ASK. Restates section 0.3 because it is
  the law most often broken: never invent, never guess, never substitute.
  Write the question in PROGRESS.md under "QUESTIONS FOR HUMAN" and stop.

3. THE WORLD MODEL
--------------------------------------------------------------------------------
  Every later part refers to these definitions by name.

3.1 Two coordinates: WHERE and WHICH
  Every piece of medical knowledge in Second Opinion has two coordinates.
  - WHERE: a point on the surface of the globe (latitude, longitude).
    WHERE answers: in which part of the library of 42 books is this
    written?
  - WHICH: an altitude, meaning a radius measured from the centre. WHICH
    answers: which entity is this? Every disease, every symptom, every
    treatment is one shell at its own unique radius.
  So the globe is a library with altitude. The angular geography is the
  library's own structure (books -> parts -> chapters). The radial
  dimension is the list of entities. A LIT SPOT is where a shell (an
  entity) and a territory (a library location) meet: "this entity is
  discussed here."
  Consequence: every 2-D map, at every altitude, shows the same
  continents. The user learns the geography once and every map they
  open (the Tiredness map, the Ozempic map, the Lupus map) is drawn on
  the same familiar coastline. Only the lights change.

3.2 Geography (WHERE): continents, provinces, districts
  Geography is built once, from the 42 Tables of Contents only, and
  frozen.
  - Level 0, CONTINENT: one book = one field of medicine.
    Example: Harrison's = "Internal Medicine (general)".
  - Level 1, PROVINCE: the book's Part or Section, if the book has this
    level. Example: Harrison Part 2 "Cardinal Manifestations", Section 2
    "Alterations in Body Temperature".
  - Level 2, DISTRICT: the book's chapter. The smallest territory.
    Example: Harrison Chapter 20 "Fever".
  Rules:
  (a) The 42 continent centres are placed by a Fibonacci sphere (42 points
      spread evenly over the sphere). Each continent's border is its
      spherical Voronoi cell: every point on the sphere belongs to the
      nearest continent centre. Continents never overlap, never leave
      gaps, and together cover the whole globe.
  (b) Provinces subdivide a continent; districts subdivide a province (or
      the continent directly if the book has no Part/Section level). The
      subdivision algorithm (nested Voronoi inside a cell) is in Part 3.
  (c) DEFAULT (human may overturn): territory AREA IS PROPORTIONAL TO PAGE
      COUNT. A 60-page chapter gets a district about fifteen times larger
      than a 4-page chapter. The map then honestly shows how much the
      literature itself devotes to each subject.
  (d) Headings inside a chapter are NOT territories. The district is the
      finest WHERE. A lit spot is placed at the centre of its district;
      when several lit spots fall in one district on the same map they are
      arranged in a small ring around the centre (Part 7).
  (e) Fibonacci placement is random with respect to meaning. Part 3 has an
      optional step where the manager proposes a seating order so related
      fields (cardiology / vascular / pulmonology) are neighbours, and the
      human approves it. Once approved: frozen.
  Every territory gets a stable ID:
    C07            continent number 7
    C07.P02        province 2 of continent 7
    C07.P02.D020   district (chapter) 20 inside that province
  Human-readable names are copied verbatim from the Table of Contents.

3.3 Altitude (WHICH): three bands, one shell per entity
  Radius is normalised so that the surface of the globe is r = 1.
  - PLANET BODY, 0.30 <= r <= 1.00: diseases-and-conditions. One shell per
    disease. Multisystem diseases deep near the core; narrow
    single-chapter conditions near the crust.
  - ATMOSPHERE, 1.00 < r <= 1.50: symptoms-and-signs. One shell per
    symptom. Nonspecific symptoms low (troposphere); pathognomonic
    symptoms high.
  - ORBITS, 1.50 < r <= 3.00: treatments-and-drugs. One shell per
    treatment. Lifestyle and diet in the lowest orbit; surgery and
    transplantation in the outermost orbit.
  The centre r = 0 is the HEALTHY BODY: a conceptual point, not an entity.
  Every continent is a wedge from the centre out to r = 3: Cardiology is a
  wedge that passes through all disease shells, all symptom shells, and
  all orbits.
  Rigidity: a shell's radius is assigned once (Part 5) and then frozen.
  Reading more pages adds lit spots and edges to a shell; it never moves
  the shell.
  Spacing inside a band: entities are ranked by the band's ordering key
  (3.4), and radii are spaced evenly between the band's minimum and
  maximum. In words: the k-th entity of n (k counted from 0) gets radius
  r_min plus (r_max minus r_min) times k divided by (n minus 1).
  In LaTeX: $r_k = r_{\min} + (r_{\max} - r_{\min}) \cdot \frac{k}{n-1}$,
  for $k = 0, \dots, n-1$.
  With perhaps 10,000 diseases in a band of width 0.70, neighbouring
  shells are about 0.00007 apart, invisible to the eye. That is fine: the
  user never scrolls shells by eye; the user picks a shell by searching
  or clicking (the "altitude elevator", Part 7). The radius exists so the
  globe view can draw shells in a meaningful order and so that similar
  entities are physically adjacent.

3.4 Ordering inside each band
  - SYMPTOMS: ordered by SPECIFICITY = number of distinct diseases that
    present with the symptom. Many diseases -> nonspecific -> LOW
    altitude. Few diseases -> pathognomonic -> HIGH altitude.
    Status: DECIDED BY HUMAN.
  - TREATMENTS: ordered by HEAVINESS, in this order from lowest orbit to
    highest: lifestyle/diet -> over-the-counter -> prescription ->
    biologics / chemotherapy / radiation -> surgery and transplantation.
    Inside a heaviness group, drugs of the same class are adjacent;
    inside a class, alphabetical. Class membership comes from the books'
    own pharmacology chapters (Part 5). Each individual drug has its own
    shell. Status: DECIDED BY HUMAN.
  - DISEASES: DEFAULT (human may overturn): ordered by BREADTH = number of
    distinct continents (books) that discuss the disease. Lupus, systemic
    sclerosis, advanced diabetes, vasculitis, which touch many fields,
    sit deep near the core. A condition discussed in one chapter of one
    book sits just under the crust. Ties broken alphabetically.
  The breadth rule mirrors the specificity rule: the deepest diseases and
  the lowest symptoms are both "the ones that touch everything". The
  user's intuition "deep = systemic, shallow = local" matches the planet.

3.5 Lit spots
  A LIT SPOT = (entity, district) + provenance. Meaning: this entity is
  discussed in this chapter. One entity has as many lit spots as there
  are chapters, across all 42 books, that discuss it. Lupus will have lit
  spots in rheumatology, nephrology, cardiology, dermatology, neurology,
  pulmonology: one altitude, many lights. This is Law 8 made geometric.

3.6 Edges (relations) and their colours
  An EDGE connects two entities (two shells) and is anchored to the
  district whose page contains the sentence that proves it. There are
  exactly five relation types:
  (1) PRESENTS_WITH. disease -> symptom. BLUE. On the symptom's HTML
      page: "caused by ...". On the disease's page: "you may notice ...".
      Example: scurvy -> bleeding gums.
  (2) TREATED_BY. disease -> treatment, or symptom -> treatment. BLUE.
      Shown as "treated by ..." / "used for ...".
      Example: fever -> paracetamol.
  (3) HARMS. treatment -> disease or symptom (side effect, adverse
      effect). Subtype CONTRAINDICATED_IN for "do not give to people who
      have ...". YELLOW. Shown as "can cause ..." / "must not be given
      in ...". Example: prednisone -> osteoporosis.
  (4) LEADS_TO. disease -> disease (complication, progression, risk
      factor). YELLOW. Shown as "if untreated, can lead to ..." /
      "raises the risk of ...".
      Example: vitamin C deficiency -> iron-deficiency anaemia.
  (5) MISTAKEN_FOR. disease <-> disease (differential diagnosis),
      undirected. GREY. Shown as "often mistaken for ...".
      Example: pericarditis <-> myocardial infarction.
  The FORWARD CHAIN (symptom -> disease -> treatment) is a walk along
  blue edges. The HARM CASCADE (headache pill -> liver disease -> what
  liver disease feels like -> the pill for that) is a walk along yellow,
  then blue, then yellow edges; the viewer lets the user follow it map
  by map (Part 7).
  On a map an edge is drawn as a FILLED CIRCLE at the anchoring district,
  coloured by relation type, labelled with the other entity's name. No
  lines, no beams, nothing crossing the planet. Like a satellite
  night-photo of city lights.

3.7 Frequency -> circle size: the F-scale
  Every edge stores the book's verbatim frequency phrase and its mapping
  to one of six levels (full wording table in Part 4):
  - F5 very common: "most patients", "the majority", "characteristic",
    "usually", "the hallmark". Numeric: above 50%.
  - F4 common: "common", "frequent", "often", "many patients".
    Numeric: 10% to 50%.
  - F3 uncommon: "occasionally", "sometimes", "in some patients",
    "a minority". Numeric: 1% to 10%.
  - F2 rare: "rare", "rarely", "infrequent", "unusual".
    Numeric: 0.1% to 1%.
  - F1 very rare: "very rare", "exceptional", "case reports",
    "isolated reports". Numeric: below 0.1%.
  - F0 not stated: the book asserts the relation but gives no frequency.
  Rules:
  (a) Circle radius grows linearly with F: F5 largest, F1 smallest.
  (b) F0 is drawn at F3 size with a DASHED outline: an honest "the book
      did not say how common".
  (c) If the book gives a number, the number wins over the words and is
      shown on hover, verbatim.
  (d) If several books state the same edge with different frequencies,
      every statement is kept (Law 2); the circle uses the HIGHEST F and
      the hover shows all statements with citations. Disagreement between
      books is itself information. DEFAULT, human may overturn.
  (e) DEFAULT (human may overturn): SEVERITY RING. A yellow edge whose
      sentence contains the book's severity words ("fatal",
      "life-threatening", "boxed warning", "requires immediate ...")
      gets a thick dark-red outline regardless of size. Example: for
      Ozempic the digestive-symptoms circle is big and plain; the
      pancreatitis and thyroid-tumour circles are small (rare) but ringed
      in red. Size says how often; the ring says how bad.

3.8 Provenance: the anatomy of a citation
  Every lit spot and every edge stores these fields:
    book_id        e.g. HARRISON-22
    district_id    e.g. C07.P02.D020   (this is also the WHERE)
    page_number    e.g. 134            (printed page, as the book numbers it)
    image_file     e.g. harrison-internal-medicine_Page_0180.png
    quote          verbatim sentence(s) as transcribed by the reader
    reader_model   which local model read this page, e.g. "Qwen3.8-27B-Q4_K_M"
    read_date      ISO date
  Because every claim is a sentence on a page of a book the human owns,
  anyone can check Second Opinion against the book itself.

4. THE USER'S JOURNEY (short; Part 7 has the details)
--------------------------------------------------------------------------------
  (1) GLOBE VIEW. A rotatable, draggable 3-D globe showing the 42
      continents (coloured, labelled), with the three altitude bands
      visible as faint translucent shells. A search box and the altitude
      ELEVATOR (three searchable lists: symptoms, diseases, treatments).
  (2) CHOOSE AN ENTITY (search "tiredness", or click a continent and pick
      from its districts). The globe fades to the 2-D MAP of that shell:
      equirectangular projection, the same coastlines as always, with
      that entity's lights: filled circles at every district where a book
      links it to something, blue and yellow, sized by F.
  (3) HOVER a circle (tap on phone): the other entity's name, the
      frequency phrase, the book and page. CLICK a circle: jump to that
      entity's map (the cascade). CLICK the entity's title: open its HTML
      page. Every HTML page has a "show me on the globe" link back to its
      map.
  (4) "Back to globe" button at all times; 2-D / 3-D toggle at all times.
  (5) Must work the same way in current Chrome, Firefox, Safari and Edge,
      on desktop and on smartphones (touch). Part 7 chooses the library
      and gives the manager a browser test checklist.

5. THE SKELETON HAS TWO SOURCES, BOTH IN THE BOOKS
--------------------------------------------------------------------------------
  Geography comes from the Tables of Contents. But a shell list (every
  disease, symptom, treatment, with a frozen altitude) must exist BEFORE
  any page is read, so that reading never moves anything.
  The books already contain this list: the BACK-OF-BOOK INDEX. Harrison's
  index alone runs over a hundred pages; every entry is a term followed by
  the pages where it appears, which is an entity with its lit spots and
  provenance already attached, in the book's own words. Therefore:
  - Tables of Contents -> geography (continents, provinces, districts,
    page ranges).
  - Indexes -> the entity registry. The READER (free, local) classifies
    each index term into one of the three groups or "not an entity",
    following Part 3's rules, term by term with the surrounding index
    context. The manager only writes the script that feeds terms to the
    reader and reviews random samples. The indexes also give the ordering
    proxies: a symptom's specificity is proxied by how many distinct
    disease districts its index pages fall into; a disease's breadth is
    literally how many books' indexes contain it.
  - Page reading (Phase B) -> edges, quotes, frequencies, ELI5: all the
    content, poured into a skeleton that already exists and never moves.
  Status: DEFAULT, the human has not yet explicitly confirmed. Part 3 is
  built on it. If a book has no usable index, Part 3 has a fallback: that
  book's registry is derived from its chapter titles and the first page
  of each chapter.

6. GLOSSARY: THE CANONICAL VOCABULARY
--------------------------------------------------------------------------------
  Every prompt, file, Cypher label and conversation uses these words and
  no synonyms.
  CONTINENT      one book = one field; a spherical Voronoi cell around a
                 Fibonacci-sphere point; ID Cnn.
  PROVINCE       a Part/Section of a book; ID Cnn.Pmm.
  DISTRICT       a chapter; the finest territory; ID Cnn.Pmm.Dkkk.
  TERRITORY      any of the above three.
  GEOGRAPHY      the frozen set of all territories with borders.
  ENTITY         one symptom, disease or treatment; exactly one group;
                 one shell.
  GROUP          symptoms-and-signs / diseases-and-conditions /
                 treatments-and-drugs.
  SHELL          the sphere at an entity's radius; one per entity.
  BAND           planet body (diseases) / atmosphere (symptoms) /
                 orbits (treatments).
  ALTITUDE       an entity's radius r; assigned once in Phase C.
  ORDERING KEY   specificity (symptoms), breadth (diseases),
                 heaviness + class (treatments).
  LIT SPOT       (entity, district) + provenance: "discussed here".
  EDGE           a typed relation between two entities, anchored to a
                 district, with F-scale and provenance.
  RELATION TYPES PRESENTS_WITH, TREATED_BY (blue); HARMS, LEADS_TO
                 (yellow); MISTAKEN_FOR (grey).
  F-SCALE        F0 to F5 frequency ordinal; F0 = not stated.
  SEVERITY RING  red outline on a yellow edge carrying the book's
                 severity wording.
  PROVENANCE     book, district, page, image file, verbatim quote,
                 reader model, date.
  REGISTRY       the frozen list of entities + altitudes (Appendix C).
  SKELETON       geography + registry; frozen at the Freeze.
  FREEZE         the ceremony in Part 3 after which the skeleton never
                 changes.
  KITCHEN        the human's laptop: where all reading, computing and
                 export happen.
  MANAGER        the paid AI model in OpenCode executing the BIBLE.
  READER         the free local vision-language model reading pages and
                 classifying terms.
  GLOBE VIEW / MAP VIEW   the 3-D and 2-D displays; the user toggles.
  ELEVATOR       the UI for picking a shell by search or list.
  CASCADE        the user following edges from one map to the next.
  CANONICAL NAME the entity's display name; a label, not a home; all
                 aliases kept verbatim.
  QUARANTINE     the list of terms found in pages but absent from the
                 frozen registry; published as "not yet in Second
                 Opinion", never silently dropped (Law 11).

7. REPOSITORY, HOSTING AND NAMES (decided by Fable, overturnable by human)
--------------------------------------------------------------------------------
  7.1 GitHub repository: https://github.com/strulovitz/second-opinion
      The manager creates it (public) in Part 2. Short, descriptive,
      matches the project name.
  7.2 Public URL: https://www.strulovitz.org/2nd-opinion/
      The abbreviation "2nd-opinion" is short, readable and unambiguous.
  7.3 Hosting model: NO external host. The websites are served from the
      human's own computers (Desktop PC and Laptop PC, one at a time)
      through a Cloudflare Tunnel. GitHub is both backup and the sync
      method between the two computers: each computer pulls the repo and
      serves from its local clone.
  7.4 The manager must NOT assume how the main website is served. In
      Part 2 the manager inspects the existing setup (which web server,
      which folder is the web root, how the existing sub-projects such as
      AI Panorama are mounted: symlink, nested clone, or copy) and
      mounts the folder site/ of this repo at /2nd-opinion/ IN THE SAME
      WAY the existing sub-projects are mounted. Any change to the
      serving configuration is first proposed in PROGRESS.md and
      approved by the human.
  7.5 What is committed and what is not. The books are copyrighted and
      the repo is public. Therefore book PDFs, page images and full-page
      transcripts are NEVER committed (they live only in the kitchen and
      are listed in .gitignore). Committed: the BIBLE, scripts, the Neo4j
      export, entities, edges, short verbatim proving sentences with
      citations, the HTML pages, the viewer, PROGRESS.md.
  7.6 Repository layout (summary; full layout in Part 2):
      AGENTS.md          read automatically by OpenCode every session
      PROGRESS.md        the manager's ledger: done / doing / blocked /
                         QUESTIONS FOR HUMAN / LATER, IF MONEY
      BIBLE/             parts 01..09 and appendices A..D
      kitchen/           scripts (Python); nothing large
      data/              exports from Neo4j (JSON), registries
      site/              the static website: index.html, viewer, pages/
      .gitignore         books/, pages/, transcripts/ and all large files

8. MANAGER MODEL ROUTING (Law 14 in practice)
--------------------------------------------------------------------------------
  Three tiers:
  TIER FREE  = local READER (Qwen 3.8 27B Q4_K_M via Unsloth Studio /
               LM Studio / Ollama; Gemma 4 31B as substitute).
  TIER CHEAP = DeepSeek V4.1 Flash in OpenCode.
  TIER SMART = Claude Sonnet 5.5 or GPT 6.1 Sol in OpenCode (either;
               the human picks by price and mood; they are
               interchangeable for this BIBLE).
  Assignment:
  - TIER FREE does: reading every page image; transcribing; classifying
    every index term; extracting every edge and frequency phrase;
    writing every ELI5 paragraph. Never pay a cloud model for per-page
    or per-term work.
  - TIER CHEAP does: the installation inventory and installs (Part 2);
    running Cypher that the BIBLE gives verbatim; parsing Tables of
    Contents into territory lists; running and babysitting batch scripts
    that call the reader; git add/commit/push; the static export;
    filling PROGRESS.md; filling appendix tables from script output.
  - TIER SMART does: writing the geography code (Fibonacci sphere,
    spherical Voronoi, nested subdivision); writing the viewer (Part 7);
    writing and tuning the reader prompts (Part 4); the entity-resolution
    rules review and the Freeze review (Part 3); any step that TIER CHEAP
    has failed twice.
  Procedure: each BIBLE part begins with a line
    "MANAGER FOR THIS PART: <tier>"
  and each step that needs a different tier is marked
    "[SWITCH TO SMART]" or "[SWITCH TO CHEAP]".
  When the manager reaches such a mark, it writes to the human in chat:
    "HUMAN: please switch the model to <tier> and say 'continue'."
  and then STOPS. It does not attempt the step in the wrong tier.

9. NEVER-FORGET MECHANISM
--------------------------------------------------------------------------------
  OpenCode reads AGENTS.md at the start of every session. AGENTS.md
  contains: (a) the Fifteen Laws of section 2, verbatim; (b) the Glossary
  of section 6, verbatim; (c) the routing rule of section 8; (d) this
  sentence: "Before doing any task, open BIBLE/ and read the part that
  governs the current phase, then read PROGRESS.md, then continue from
  the first unfinished step." The manager therefore never depends on
  remembering a chat prompt. Part 8 gives AGENTS.md and PROGRESS.md in
  full.

10. DEFAULTS IN THIS PART THAT THE HUMAN MAY OVERTURN BEFORE THE FREEZE
--------------------------------------------------------------------------------
  (1) District area proportional to page count (3.2 c).
  (2) Disease ordering by breadth, deep = multisystem (3.4).
  (3) Severity ring on yellow edges (3.7 e).
  (4) Highest-F wins for circle size when books disagree (3.7 d).
  (5) Indexes as the source of the entity registry and the ordering
      proxies (section 5). Please confirm explicitly; Part 3 depends
      on it.
  (6) Lit spots at district centres with a small ring when several share
      a district (3.2 d).
  (7) Repository name "second-opinion" and URL path "/2nd-opinion/"
      (section 7).
  Everything else in this part is either the human's explicit decision
  or a direct consequence of one.

================================================================================
HANDOFF CAPSULE (for the human to paste into a NEW conversation with
Fable when asking for the next part; it protects against Fable's own
limited context window)
================================================================================
Project: "Second Opinion", a medical knowledge globe built only from 42
medical textbooks the human owns, vibe-coded, open source, hosted at
https://www.strulovitz.org/2nd-opinion/ from the human's own computers
via Cloudflare Tunnel, synced through https://github.com/strulovitz/
second-opinion. Fable writes a 13-delivery BIBLE (9 parts + 4 appendix
templates) in plain text, one copy-paste block per delivery, no tables,
no collapsibles, formulas in words plus LaTeX text. Delivered so far:
Part 1. World model: a globe; WHERE = library geography from Tables of
Contents (42 continents by Fibonacci sphere + spherical Voronoi;
provinces = book parts; districts = chapters; area ~ page count);
WHICH = altitude, one shell per entity; diseases 0.30-1.00 ordered by
breadth (deep = multisystem), symptoms 1.00-1.50 ordered by specificity
(low = nonspecific), treatments 1.50-3.00 ordered by heaviness
(lifestyle -> OTC -> prescription -> biologics/chemo/radiation ->
surgery) with drug classes adjacent, every drug its own shell. No single
home for anything (Law 8). Rigid layout, no force-directed graph. Five
edge types: PRESENTS_WITH, TREATED_BY (blue); HARMS incl.
CONTRAINDICATED_IN, LEADS_TO (yellow); MISTAKEN_FOR (grey). F-scale
F0-F5 from the book's frequency words; circle size linear in F; F0
dashed; severity ring red. Viewer: 3-D globe <-> 2-D equirectangular
maps, Google-Earth style, lit circles only, no lines; must work on
desktop and mobile browsers. Entity registry comes from back-of-book
indexes (default awaiting confirmation). Neo4j is the single source of
truth, NetworkX for computation, Matplotlib for previews, static export
to site/. Tiers: READER = free local Qwen 3.8 27B Q4_K_M (Gemma 4 31B
substitute) via Unsloth Studio/LM Studio/Ollama does all per-page and
per-term work; CHEAP = DeepSeek V4.1 Flash; SMART = Claude Sonnet 5.5 or
GPT 6.1 Sol; manager says "HUMAN: please switch to <tier>" and stops.
Laws: 15, including cheap beats perfect, never assume installed (Part 2
opens with inventory + installs), when unclear stop and ask, one
disclaimer only at the bottom of the main page, no multi-model editions,
books/images/transcripts never committed (copyright). Next delivery
requested: Part 2 (Environment and Data Model).
================================================================================
