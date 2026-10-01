================================================================================
SECOND OPINION -- THE BIBLE
APPENDICES C AND D OF 13 -- ENTITY AND ALTITUDE REGISTRY; TREATMENT
HEAVINESS GROUPS AND CLASSES
Files: BIBLE/appendix-C-entity-and-altitude-registry.md
       BIBLE/appendix-D-treatment-heaviness-groups.md
MANAGER FOR THESE APPENDICES: CHEAP (DeepSeek V4.1 Flash). The same
                       script kitchen/build_appendices.py (Appendix A-B
                       delivery, section 0.4) generates both .md files
                       when their CSVs exist. No judgement needed.
READER:                not used.
PRECONDITION:          For a PROVISIONAL generation: Freeze A done and
                       the provisional altitude run of Part 5 section
                       1.1 complete. For the FROZEN generation: Freeze B
                       done (Part 5 section 7.2) and export_registry.py
                       run, so that data/registry/entities.csv,
                       aliases.csv, heaviness.csv, classes.csv exist
                       with altitude columns filled.
================================================================================

0. RULES SPECIFIC TO APPENDICES C AND D
--------------------------------------------------------------------------------
0.1 Two generations, clearly labelled
  The script writes the header line "STATUS: PROVISIONAL (altitudes
  may change until Freeze B)" or "STATUS: FROZEN at Freeze B <date>,
  commit <hash>", reading Meta.altitudes_frozen from Neo4j. The
  provisional appendix is committed so the human can read it early;
  the frozen one replaces it; the git diff between them is the record
  of what Phase B data changed in the ordering.

0.2 What may change after Freeze B (and only this)
  - aliases.csv may GROW (Phase B adds spellings; Part 3 section 11.5);
    appendix C's summary line "aliases: n" updates when the script is
    re-run; no existing alias is ever removed.
  - entities.csv may gain APPENDED rows for entities the human approved
    from quarantine (Part 4 section 13.4), with altitude_status
    "inserted" and a float rank (Part 5 section 8); no existing row's
    slug, group, canonical_name, rank, altitude changes. The script
    checks this (section 1.6) by comparing with the previous CSV
    committed at Freeze B (git show altitude-freeze-B:data/registry/
    entities.csv) and exits 1 on any changed frozen value.
  - lit_spot_count, book_count, ordering_value, tie1 are facts about
    the books read so far and MAY be refreshed in the CSV for display;
    they no longer affect rank or altitude after Freeze B (Part 5
    section 7.3). The script writes both the frozen-at-B value and the
    current value when they differ (columns ordering_value_at_freeze /
    ordering_value_now).
  - classes.csv member_count may refresh for the same reason; class
    membership of existing entities never changes.
  Re-generation cadence: at every publish (the script is called by
  kitchen/publish.sh after export.py; add the line
  "python kitchen/build_appendices.py" to publish.sh right after
  "python kitchen/export.py"; commit "App.C-D publish.sh calls
  build_appendices").

================================================================================
APPENDIX C -- ENTITY AND ALTITUDE REGISTRY
File: BIBLE/appendix-C-entity-and-altitude-registry.md
================================================================================

1.1 Purpose (fixed text, copied into the .md)
  "This appendix records every entity of Second Opinion -- every
  symptom or sign, disease or condition, treatment or drug named in the
  indexes of the accepted books -- with its frozen identifier, group,
  display name, and the altitude of its shell on the globe. One
  entity, one shell, no home. Identifiers, groups and names were frozen
  at Freeze A; altitudes at Freeze B. Aliases may still grow; entities
  approved later from quarantine are appended with status inserted and
  move nothing."

1.2 Source files
  data/registry/entities.csv, aliases.csv   (Part 3 section 11.3,
                                             extended in Part 5 section 7.2)
  data/registry/stats.json                  (index-pipeline counts per
                                             book, summed)
  kitchen/logs/<BOOK_ID>-classified.jsonl, -doubtful-merges.jsonl,
  resolve-cache-global.json                 (the decisions trail)
  Neo4j: (:Entity) with secondary labels :Symptom, :Disease, :Treatment

1.3 Column definitions of entities.csv (fixed text)
  slug                 group + "-" + slugify(canonical_name) (Part 2
                       section 6.5). The HTML file name and the viewer
                       route. Frozen at Freeze A. Slugs ending "-2"
                       were collisions resolved by the human before the
                       Freeze (Part 3 section 11.2).
  group                symptoms-and-signs | diseases-and-conditions |
                       treatments-and-drugs. Frozen.
  canonical_name       Display label, verbatim form from the FIRST book
                       whose index created the entity (Harrison first;
                       Part 3 section 7.1). A label, not a home. Frozen.
  created_from         index | toc (fallback registry, Part 3 section
                       7.9) | manual-wikipedia | quarantine (human-
                       approved insertion after Freeze A).
  created_book_id      The book whose index (or page) first produced it.
  created_date         ISO date.
  alias_count          Number of rows in aliases.csv for this slug
                       (includes the canonical name). May grow.
  abbreviation_count   Length of the abbreviations list (Amendment 4.3).
                       May grow.
  lit_spot_count       Distinct districts where the entity is
                       DISCUSSED_IN (index or page). Refreshable.
  book_count           Distinct books among its lit spots and edges.
                       Refreshable. For diseases this IS the breadth
                       key.
  ordering_value       The band's ordering key value (Part 5 section 3):
                       symptoms = distinct diseases with PRESENTS_WITH;
                       diseases = book_count; treatments = heaviness
                       code 0-4. Column pair ordering_value_at_freeze /
                       ordering_value_now after Freeze B (section 0.2).
  tie1, tie2           Tie-break counts (Part 5 section 3). Same pair
                       treatment as ordering_value.
  rank                 Position inside the band, from 0; integer for
                       frozen entities, float (k + 0.5, k + 0.25 ...)
                       for inserted ones. Frozen at B.
  altitude             Radius r, 6 decimals; unique across all
                       entities. Frozen at B.
  altitude_status      provisional | frozen | inserted.
  altitude_date        ISO date when the altitude was written.
  heaviness_group      Treatments only (also in heaviness.csv); empty
                       otherwise.
  class_canonical      Treatments only; empty otherwise.
  has_text             true if tldr/eli5 were written (text_status
                       "written"); refreshable; display only.
  edge_count           Total edges of any type touching the entity;
                       refreshable; display only.

1.4 Column definitions of aliases.csv (fixed text)
  slug                 The entity.
  alias                A verbatim variant seen in a book: index
                       headword, inverted form, "see" cross-reference
                       source, page spelling, brand or generic name.
                       Case preserved.
  source               index-headword | index-see | page-reader |
                       drug-generic | drug-brand | human.
  book_id              Where it was seen first.
  added_date           ISO date.
  The canonical name itself appears as a row with source
  "index-headword" (or "toc"/"human").

1.5 Summary section (generated)
  (a) Totals: entities per group and overall; aliases total; average
      aliases per entity; entities with created_from = toc, manual-
      wikipedia, quarantine (counts); entities with altitude_status
      inserted (count, listed by name with their two neighbours' names
      from DECISIONS BY HUMAN).
  (b) The altitude profile, per band: r_min, r_max, count, and the
      spacing between neighbouring shells (r_max - r_min) / (n - 1) to
      8 decimals -- the number that shows why shells are picked by
      search, not by eye.
  (c) SYMPTOMS: the 40 lowest shells (most nonspecific) with
      ordering_value and altitude; the 20 highest (most specific) with
      the single disease each presents in, if ordering_value = 1.
  (d) DISEASES: the 40 deepest (highest breadth) with book_count and
      altitude; the count of diseases discussed in exactly one book
      (the thin crust), and 20 random examples of them.
  (e) TREATMENTS: one line per heaviness sub-band with its count and
      r range (details in Appendix D).
  (f) The decisions trail: counts summed from stats.json -- index
      entries parsed, exact merges, reader merges (SAME >= 0.6),
      doubtful merges (listed count; file path), group conflicts
      (count; file path), not-an-entity terms (count); human fixes
      applied at Checkpoints 3.5 and 3.6 (count of DECISIONS BY HUMAN
      lines referencing Part 3 section 9).
  (g) Slug collisions resolved ("-2" slugs): list with the human's
      words, or "none".

1.6 Verification queries and checks (run by the script; outputs pasted)
  MATCH (e:Entity) RETURN e.group, count(*) ORDER BY e.group;
  MATCH (e:Entity) WHERE e.frozen <> true RETURN count(e);         -- must be 0
  MATCH (e:Entity) WHERE e.altitude IS NULL RETURN count(e);       -- must be 0 (after provisional run)
  MATCH (e:Entity) WITH e.altitude AS a, count(*) AS c WHERE c > 1
    RETURN a, c LIMIT 5;                                            -- must be empty
  MATCH (e:Entity) RETURN e.group, min(e.altitude), max(e.altitude)
    ORDER BY e.group;                                               -- inside the band limits of Part 5 section 2
  MATCH (e:Entity:Symptom) WHERE e.altitude <= 1.0 OR e.altitude > 1.5 RETURN count(e);  -- 0
  MATCH (e:Entity:Disease) WHERE e.altitude < 0.3 OR e.altitude >= 1.0 RETURN count(e);  -- 0
  MATCH (e:Entity:Treatment) WHERE e.altitude <= 1.5 OR e.altitude > 3.0 RETURN count(e); -- 0
  MATCH (e:Entity) WHERE NOT (e:Symptom OR e:Disease OR e:Treatment) RETURN count(e);    -- 0
  MATCH (e:Entity) WHERE (e:Symptom AND e.group <> "symptoms-and-signs")
    OR (e:Disease AND e.group <> "diseases-and-conditions")
    OR (e:Treatment AND e.group <> "treatments-and-drugs") RETURN count(e);              -- 0
  MATCH (e:Entity) RETURN e.altitude_status, count(*);
  MATCH (m:Meta) WHERE m.key IN ["skeleton_frozen","freeze_date","altitudes_frozen","freeze_b_date"]
    RETURN m.key, m.value ORDER BY m.key;
  Python checks: (1) every slug in entities.csv has exactly one HTML
  file site/pages/<slug>.html and one site/data/entities/<slug>.json
  (or the build has not run yet: reported, not failed); (2) every slug
  in aliases.csv exists in entities.csv; (3) slug = slugify rule
  applied to canonical_name (recomputed and compared; "-2" allowed);
  (4) after Freeze B: no frozen row differs from the tagged CSV in
  slug, group, canonical_name, rank, altitude (section 0.2). Any
  failure: exit 1, BLOCKED, no fixing.

1.7 How a later reader uses this registry (fixed text)
  "To find an entity: search canonical_name or aliases.csv; the slug
  gives its page (pages/<slug>.html), its data (data/entities/
  <slug>.json) and its map (viewer/index.html#/map/<slug>). The
  altitude is the radius of its shell; the rank is its position in
  its band; neither is a medical statement -- both are counts over the
  books read, explained on the entity's page."
