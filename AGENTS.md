# Second Opinion -- standing orders for the manager

WHERE THE CURRENT STATE LIVES: read `HANDOFF-TO-SMART-AFTER-CAMPBELL-2026-10-23.md`
first, then `PROGRESS.md`. Campbell is repaired (90 chapters, 19 Parts,
PDF-page unit); the handoff lists the remaining rebuilt-book checks and
Step A3. Earlier completion claims are not physical-book proof.

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

Before doing any task: open BIBLE/ and read the part that governs
the current phase; then read PROGRESS.md; then continue from the
first unfinished step. Never skip a step. Never substitute a
technology. When unclear, write under QUESTIONS FOR HUMAN in
PROGRESS.md and stop. Report every completed step with evidence.
