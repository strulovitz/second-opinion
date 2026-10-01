================================================================================
APPENDIX D -- TREATMENT HEAVINESS GROUPS AND CLASSES
File: BIBLE/appendix-D-treatment-heaviness-groups.md
================================================================================

2.1 Purpose (fixed text)
  "This appendix records how the treatments and drugs were arranged
  into orbits: the five heaviness groups from lifestyle to surgery,
  the sub-band of radius each group occupies, the drug and procedure
  classes inside each group, and which treatment belongs to which
  class. The grouping was decided by the reader model for layout
  only (Part 5 Amendment 5.1) and reviewed by the human; it is not a
  statement about how any medicine is regulated or sold in any
  country. Frozen at Freeze B."

2.2 Source files
  data/registry/heaviness.csv, classes.csv   (Part 5 section 7.2)
  kitchen/logs/heaviness.jsonl, classes.jsonl (the reader's raw
                                              answers with reasons)
  kitchen/prompts/P-C1.txt, P-C2.txt, additional-rules-P-C1.txt
  Neo4j: (:Entity:Treatment) properties heaviness_group,
         heaviness_confidence, class_verbatim, class_canonical

2.3 Column definitions of heaviness.csv (fixed text)
  slug                  The treatment entity.
  canonical_name        Display label.
  heaviness_group       lifestyle | otc | prescription |
                        biologic-chemo-radiation | surgery-transplant.
                        Frozen at B.
  heaviness_confidence  The reader's confidence 0.0-1.0 from P-C1;
                        items below 0.5 were shown to the human at
                        Checkpoint 5.1/5.2.
  decided_by            reader | human (the human overrode the reader
                        at review; the words are under DECISIONS BY
                        HUMAN).
  class_verbatim        The class words the reader chose verbatim from
                        the books' mentions (P-C1 class_label), or
                        empty.
  class_canonical       The normalised class after P-C2, or
                        "(unclassified)". Frozen at B.
  class_mentions        All verbatim class words seen on pages for this
                        treatment (drug_class_mentions), joined by
                        " | "; refreshable; evidence for the human.
  sub_band_min, sub_band_max   The radius limits of the group (Part 5
                        section 2).
  rank, altitude        As in entities.csv.
  reason                The reader's 12-word reason from P-C1,
                        verbatim.

2.4 Column definitions of classes.csv (fixed text)
  heaviness_group       The group the class sits in. The same class
                        name may appear in two groups if the reader
                        split its members (e.g. "corticosteroids" with
                        a topical OTC member and a prescription
                        member); this is allowed and listed in the
                        summary.
  class_canonical       The normalised class label (P-C2 canonical).
  member_count          Number of treatments with this class in this
                        group. Refreshable.
  members_verbatim_forms   The distinct class_verbatim strings united
                        into this class, joined by " | " -- the
                        evidence that the normalisation was sane.
  r_first, r_last       Altitude of the first and last member (the
                        class occupies this thin band of orbits).
  class_order           Position of the class inside its group
                        (alphabetical; "(unclassified)" last; Part 5
                        section 5.4).

2.5 Summary section (generated)
  (a) Per heaviness group, in orbit order: count of treatments, r range
      actually occupied, number of classes, the five largest classes
      with member counts, count of members with confidence < 0.5 and
      how many of those the human changed.
  (b) The class ladder: for each group, the ordered list of all
      classes with member counts (this list is the "table of contents"
      of the orbits; expect a few hundred lines in total; acceptable).
  (c) Classes present in more than one heaviness group (listed).
  (d) The "(unclassified)" count per group and 20 random examples
      (likely procedures and lifestyle measures; the human may add
      rules later -- "LATER, IF MONEY").
  (e) Human overrides at Checkpoint 5.1/5.2: count and the list of
      slugs moved between groups, with the human's words.
  (f) The exact text of additional-rules-P-C1.txt at generation time.

2.6 Verification queries and checks (run by the script; outputs pasted)
  MATCH (t:Entity:Treatment) RETURN t.heaviness_group, count(*), min(t.altitude), max(t.altitude)
    ORDER BY min(t.altitude);
    -- five rows in the order lifestyle, otc, prescription,
    -- biologic-chemo-radiation, surgery-transplant; each min/max
    -- inside its sub-band of Part 5 section 2
  MATCH (t:Entity:Treatment) WHERE t.heaviness_group IS NULL
    OR NOT t.heaviness_group IN ["lifestyle","otc","prescription","biologic-chemo-radiation","surgery-transplant"]
    RETURN count(t);                                                -- 0
  MATCH (t:Entity:Treatment) WHERE t.class_canonical IS NULL OR t.class_canonical = "" RETURN count(t);  -- 0
  MATCH (t:Entity:Treatment) WHERE t.heaviness_confidence < 0.5 RETURN count(t);
  MATCH (t:Entity:Treatment) RETURN t.heaviness_group, count(DISTINCT t.class_canonical) ORDER BY t.heaviness_group;
  Ordering check (Cypher):
  MATCH (t:Entity:Treatment) WITH t ORDER BY t.altitude
    WITH collect(t) AS ts
    UNWIND range(0, size(ts) - 2) AS i
    WITH ts[i] AS a, ts[i + 1] AS b
    WHERE a.heaviness_group = b.heaviness_group AND a.class_canonical <> "(unclassified)"
      AND b.class_canonical <> "(unclassified)"
      AND toLower(a.class_canonical) > toLower(b.class_canonical)
    RETURN count(*);                                                -- 0 (classes alphabetical inside a group)
  Python checks: (1) every slug in heaviness.csv is a treatment in
  entities.csv and vice versa; (2) for every class in classes.csv,
  member_count equals the number of heaviness.csv rows with that
  (group, class); (3) r_first <= r_last and no two classes in the same
  group have overlapping [r_first, r_last] ranges (adjacency, Part 1
  section 3.4); (4) after Freeze B, no frozen heaviness_group or
  class_canonical differs from the tagged CSV. Any failure: exit 1,
  BLOCKED, no fixing.

2.7 How a later reader uses this appendix (fixed text)
  "To find a drug's neighbours in orbit: find its class in classes.csv;
  the members of that class occupy adjacent shells; the classes above
  and below in class_order are the nearest other classes. To see why a
  treatment is in its group: read its reason and confidence in
  heaviness.csv, and the quotes on its page. The grouping orders a
  picture; it does not tell anyone what to take."

================================================================================
INSTALLATION (CHEAP; one session after the provisional altitude run,
and again after Freeze B)
================================================================================
  1. Extend kitchen/build_appendices.py (or confirm it already handles
     C and D) per sections 1 and 2; add the publish.sh line (0.2).
  2. Run: python kitchen/build_appendices.py
  3. Open the two .md files; confirm STATUS line, five sections,
     verification outputs with zeros where "must be 0".
  4. Commit "App.C-D generate appendices C and D (<provisional|frozen>)"
     and push.
  EVIDENCE: the script's summary lines; head -n 12 of each .md; the
  verification outputs; commit hash.
  CHECKPOINT C-D.1 (provisional): the human reads summary (c) and (d)
  of Appendix C -- the lowest symptoms and the deepest diseases -- and
  says whether the picture is sane ("fever, pain, fatigue low; lupus,
  diabetes, hypertension deep" is the expectation, not a rule).
  CHECKPOINT C-D.2 (frozen): after Freeze B, the human confirms on
  GitHub that the STATUS line reads FROZEN and the tag altitude-
  freeze-B exists. Recorded under DECISIONS BY HUMAN.

================================================================================
THE BIBLE IS COMPLETE -- CLOSING NOTE FOR THE MANAGER AND THE HUMAN
================================================================================
  Files in BIBLE/ (13 deliveries):
    part-01-charter-and-world-model.md
    part-02-environment-and-data-model.md
    part-03-phase-a-skeleton.md
    part-04-phase-b-reading-pipeline.md
    part-05-phase-c-altitudes.md
    part-06-html-pages.md
    part-07-viewer.md
    part-08-manager-operating-protocol.md
    part-09-publishing-and-ledger.md
    appendix-A-field-registry.md            (generated)
    appendix-B-territory-atlas.md           (generated)
    appendix-C-entity-and-altitude-registry.md   (generated)
    appendix-D-treatment-heaviness-groups.md     (generated)
  The appendix TEMPLATE texts (these two deliveries and the A-B one)
  are saved as BIBLE/appendix-templates.md so the generating script's
  fixed texts have a source.

  Order of work from here (the manager copies this into PROGRESS.md
  NEXT STEP chain; one step per session, Part 8 section 4):
    1. Part 2 (environment, repo, schema, placeholder site)      CHEAP
    2. Part 8 (install AGENTS.md and PROGRESS.md in full)        CHEAP
    3. Part 3 Phase A, steps A0-A3 (books, duplicates, TOCs)     CHEAP + human
    4. Part 3 steps A4-A5 (reader helper, geography scripts)     SMART writes, CHEAP runs
    5. Part 3 steps A6-A8 (index pipeline, reviews, Freeze A)    SMART writes, CHEAP runs, reader works
    6. Appendices A and B (generate)                             CHEAP
    7. Part 5 provisional altitudes; Appendices C and D (prov.)  SMART writes once, CHEAP runs
    8. Part 6 pages (export, texts, build)                       SMART writes, CHEAP runs
    9. Part 7 viewer; Checkpoint 7.1                             SMART writes, CHEAP tests
   10. Part 9 publish; Checkpoint 9.1 "live"                     SMART writes once, CHEAP publishes
   11. Part 4 Phase B pilot, then full runs book by book         SMART pilot, CHEAP runs
   12. Part 5 Freeze B after Checkpoint 4.2; Appendices C, D (frozen)  CHEAP
   13. Routine: publish after every book review, forever         CHEAP
  Steps 8-10 happen BEFORE most of Phase B on purpose: the site goes
  live early with white dots and honest numbers, and fills with blue
  and yellow lights as the reader works, month by month.

  To the human: when the manager stalls, paste the governing part's
  section number and the words "read it again and do exactly that".
  When the manager claims success, run the five-minute audit (Part 8
  section 7). When something in the BIBLE itself proves wrong, come
  back to Fable with the Handoff Capsule and the exact section; an
  amendment is a numbered line, like the ones inside Parts 3-9, never
  a silent edit.

================================================================================
FINAL HANDOFF CAPSULE (paste into a NEW conversation with Fable for any
future amendment or question)
================================================================================
Project: "Second Opinion", a medical knowledge globe built only from N
(up to 42) medical textbooks the human owns, vibe-coded, open source,
hosted at https://www.strulovitz.org/2nd-opinion/ from the human's own
computers via Cloudflare Tunnel, synced through
https://github.com/strulovitz/second-opinion (laptop = kitchen with
Neo4j; desktop serves static site/ only). The BIBLE is COMPLETE: 13
deliveries in BIBLE/ (Parts 1-9 by Fable; Appendices A-D generated by
kitchen/build_appendices.py from data/registry/*.csv). World model:
WHERE = library geography (42 equal-area continents by Fibonacci
sphere + Voronoi, provinces = book parts, districts = chapters with
area ~ page count, 2048x1024 raster, frozen at Freeze A); WHICH =
altitude, one shell per entity, no single home: diseases 0.30-0.98 by
breadth (deep = multisystem), symptoms 1.02-1.50 by specificity (low
= nonspecific), treatments in five heaviness sub-bands 1.52-2.98
(lifestyle, otc, prescription, biologic-chemo-radiation, surgery-
transplant) then class then name; frozen at Freeze B (default after
Harrison is read); later entities inserted at midpoints, nothing
moves. Edges PRESENTS_WITH/TREATED_BY blue, HARMS(subtype
CONTRAINDICATED_IN)/LEADS_TO yellow, MISTAKEN_FOR grey; one
relationship per proving verbatim sentence with book/district/page/
image/quote/frequency_phrase/f_scale 0-5/numeric_pct/severity/
quote_hash; aggregation (max F) only at export. Pipeline: Phase A
(TOCs -> geography; indexes -> entity registry via reader prompts
P-A2, P-A4a/b/c), Phase B (text-first transcription, vision for
figure pages, sliding window, P-B1 extraction, script-only quote
verification, P-B2 resolution, quarantine with replay), Phase C
(altitudes via Cypher keys + P-C1/P-C2 for treatments), pages
(export_entities.py, P-D1 TL;DR/ELI5 from quotes only, zero-JS pages,
pages.css F = font size), viewer (Three.js vendored + Canvas 2D, hash
routes #/globe, #/map/<slug>, #/map/<slug>/3d, #/district/<id>),
protocol (AGENTS.md with 15 Laws, evidence format COMMANDS/OUTPUT/
FILES/DB/COMMIT, forbidden list, one step per session, model-switch
"HUMAN: please switch the model to <tier> and say 'continue'", five-
minute audit), publishing (export.py, ledger.json honest numbers,
index-text.json -> index.html with the ONLY disclaimer at the bottom,
quarantine page, sitemap, publish.sh, tunnel check, live checklist).
Tiers: READER = free local Qwen 3.8 27B Q4_K_M (Gemma 4 31B
substitute) via OpenAI-compatible endpoint; CHEAP = DeepSeek V4.1
Flash; SMART = Claude Sonnet 5.5 or GPT 6.1 Sol. Laws include: books
only, provenance always, Neo4j single source of truth, rigid layout,
cheap beats perfect, never assume installed, when unclear stop and
ask, one disclaimer only, no multi-model editions, books/images/
transcripts never committed, report with evidence. Amendments so far:
3.1 equal-area continents, 3.2 raster not polygons, 4.1 text-first
transcription, 4.2 quote_hash, 4.3 abbreviations, 5.1 reader knowledge
for heaviness layout key only, 5.2 tie/class fields, 5.3 treatment
sub-bands, 6.1 entity export in Part 6, 6.2 viewer hash routes, 6.3
text_quote_count/text_status, 7.1 Three.js + Canvas 2D, 7.2 district
export, 7.3 2k texture, 7.4 shared wording.json, 9.1 build.json, 9.2
index-text.json, 9.3 quarantine page, 9.4 sponsor_note box. Any
future change to the BIBLE is a numbered amendment stating which
section it changes and why.
================================================================================
