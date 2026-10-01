================================================================================
SECOND OPINION -- THE BIBLE
APPENDICES A AND B OF 13 -- FIELD REGISTRY AND TERRITORY ATLAS
Files: BIBLE/appendix-A-field-registry.md
       BIBLE/appendix-B-territory-atlas.md
MANAGER FOR THESE APPENDICES: CHEAP (DeepSeek V4.1 Flash). One short
                       script (section 0.4) generates both .md files
                       from data/registry/*.csv. No judgement needed.
READER:                not used.
PRECONDITION:          Freeze A done (Part 3 section 11); the files
                       data/registry/books.csv and territories.csv
                       exist.
================================================================================

0. COMMON RULES FOR ALL FOUR APPENDICES
--------------------------------------------------------------------------------
0.1 What an appendix is
  Parts 1-9 are the LAW (written by Fable, never edited by the manager).
  Appendices A-D are the RECORD: the frozen skeleton of this particular
  project, as it actually came out of the 42 books. Their content is
  not written by hand. The truth lives in Neo4j; the CSVs in
  data/registry/ are the export of that truth at the Freeze; the
  appendix .md files are human-readable summaries GENERATED from the
  CSVs. Three copies, one source, zero hand edits.

0.2 Freeze rule
  Appendices A and B are generated once at Freeze A and then never
  regenerated, except: (a) if the human overturns a Freeze A decision
  before Freeze B (recorded under DECISIONS BY HUMAN), in which case
  export_registry.py and the appendix script run again and the git
  diff of the .md files IS the record of what changed; (b) Appendix A
  gains reading-progress columns that are allowed to update (section
  1.4). Appendices C and D are generated at Freeze B (next delivery).

0.3 Each appendix .md has the same five sections
  1. Purpose (two sentences, fixed text below).
  2. Source files (the CSV paths and the Neo4j labels).
  3. Column definitions (fixed text below).
  4. Summary (generated numbers and lists).
  5. Verification (the Cypher queries and their outputs at generation
     time, pasted by the script).
  The .md header line: "Generated <ISO date-time> from commit <short
  hash> by kitchen/build_appendices.py. Do not edit by hand."

0.4 kitchen/build_appendices.py  [CHEAP may write this; under 150 lines;
    if it fails twice, SWITCH TO SMART]
  - reads data/registry/books.csv, territories.csv (and, after Freeze
    B, entities.csv, aliases.csv, heaviness.csv, classes.csv);
  - runs the verification queries of sections 1.5 and 2.5 through
    db.run and pastes the results;
  - writes BIBLE/appendix-A-field-registry.md and
    BIBLE/appendix-B-territory-atlas.md (and C, D when their CSVs
    exist) with the five sections of 0.3;
  - prints one line per appendix: file name, bytes, number of rows
    summarised.
  This is the ONE exception to "the manager never writes in BIBLE/":
  the script writes the four appendix files, and only those. AGENTS.md
  Forbidden list is amended by appending: "(exception: kitchen/
  build_appendices.py writes BIBLE/appendix-*.md)". The manager adds
  this sentence to AGENTS.md verbatim and commits "App.0.4 amend
  AGENTS.md appendix exception".

================================================================================
APPENDIX A -- FIELD REGISTRY (the books, and the continents they became)
File: BIBLE/appendix-A-field-registry.md
================================================================================

1.1 Purpose (fixed text, copied into the .md)
  "This appendix records which textbooks were accepted into Second
  Opinion, which were rejected as duplicates of another book on the
  same field, and which continent of the globe each accepted book
  became. One book, one field, one continent. Frozen at Freeze A."

1.2 Source files
  data/registry/books.csv       (written by kitchen/export_registry.py,
                                 Part 3 section 11.3)
  kitchen/books.json            (the per-book configuration, Part 3
                                 section 2.4; the CSV is derived from it
                                 plus Neo4j)
  Neo4j: (:Book), (:Territory {level:"continent"})-[:REPRESENTS]->(:Book)

1.3 Column definitions of books.csv (fixed text; the script copies it)
  book_id        Stable identifier: eponym or first title word in
                 UPPERCASE, hyphen, edition number (or year). Example
                 HARRISON-22. Never changes.
  title          Full title, verbatim from the title page.
  edition        Edition string as printed ("22", "12th", "2021").
  year           Publication year, integer.
  field_name     The field of medicine the book represents; this is the
                 continent's display name. Short, Title Case, chosen by
                 the human at Checkpoint 3.1 (Part 3 section 3.3).
  continent_id   "Cnn" where nn = seat_order (Part 3 section 6.3).
                 Empty for rejected books.
  seat_order     1..N; the order in which the book was seated on the
                 Fibonacci sphere. 1 is always the general textbook
                 (Harrison), seated facing lat 0, lon 0.
  cluster        One of the 16 cluster words of Part 3 section 6.3 (a),
                 used only for seating neighbours; not shown to users.
  lat, lon       Centre of the continent in degrees (the Fibonacci
                 point), 4 decimals.
  area_fraction  Fraction of the globe's surface covered by the
                 continent, 5 decimals. All continents are nearly
                 equal (Amendment 3.1); the sum over accepted books is
                 1.00000 within rounding.
  page_count     Number of page images of the PDF.
  page_offset    printed_page = image_number - page_offset (Part 3
                 section 4.6). If the book has per-province offsets, the
                 most common value, and the note column says "multiple".
  text_layer     true / false (Part 3 section 2.1).
  toc_images     "a-b": image numbers of the Table of Contents.
  index_images   "a-b": image numbers of the back-of-book index; empty
                 if the book has no usable index (Part 3 section 7.9
                 fallback used).
  provinces      Number of provinces (P00 counts as one).
  districts      Number of districts (chapters).
  status         At Freeze A: "index-done" or "rejected-duplicate".
                 Later: "reading", "read" (section 1.4).
  duplicate_of   For rejected books: the book_id of the winner. Empty
                 otherwise.
  decision_date  ISO date of the human's decision at Checkpoint 3.1.
  notes          Free text from books.json notes (online-only chapters,
                 numbering oddities), verbatim.

1.4 Columns that may change after Freeze A (and only these)
  status, and three progress columns added by the Part 9 ledger when
  present: pages_planned, pages_loaded, edges_stored. The script fills
  them from data/export/books.json if it exists; otherwise leaves them
  empty. Everything else in the row is frozen.

1.5 Summary section (generated)
  (a) "N accepted books; M rejected as duplicates; total continents N."
  (b) The seating list, one line per accepted book, in seat_order:
      "C01  Internal Medicine (general)  HARRISON-22  lat 0.0, lon 0.0
       cluster general  4,273 pages  500 districts"
  (c) The cluster map: one line per cluster word with the field names
      seated in it, so the human can see the neighbourhoods.
  (d) The rejected list: "BOOK-X rejected in favour of BOOK-Y on
      <date>: <the human's words from DECISIONS BY HUMAN, quoted>".
  (e) Books without a usable index (fallback registry): list, or
      "none".

1.6 Verification queries (run by the script; outputs pasted)
  MATCH (b:Book) RETURN b.status, count(*) ORDER BY b.status;
  MATCH (c:Territory {level:"continent"})-[:REPRESENTS]->(b:Book)
    RETURN count(c) AS continents, count(DISTINCT b) AS books;
    -- the two numbers must be equal and equal to N
  MATCH (c:Territory {level:"continent"}) RETURN sum(c.area_fraction);
    -- about 1.0
  MATCH (b:Book) WHERE b.status <> "rejected-duplicate"
    AND NOT (:Territory {level:"continent"})-[:REPRESENTS]->(b)
    RETURN b.book_id;
    -- must return nothing
  Consistency check in Python: every book_id in books.csv exists in
  kitchen/books.json and vice versa; field_name values are unique among
  accepted books (Law 6). Any mismatch: the script exits 1 and writes
  BLOCKED; it does not "fix" either file.
================================================================================
APPENDIX B -- TERRITORY ATLAS (every province and district, with its
place on the globe)
File: BIBLE/appendix-B-territory-atlas.md
================================================================================

2.1 Purpose (fixed text)
  "This appendix records the frozen geography: every continent,
  province and district of the globe, its verbatim name from the
  book's Table of Contents, its printed page range, its centre in
  latitude and longitude, and its code in the district raster. The
  geography never changes after Freeze A; every light on every map is
  placed by this atlas."

2.2 Source files
  data/registry/territories.csv   (Part 3 section 11.3)
  data/export/geography/geography.json, districts_lookup.json,
  district_raster.png / .npy, continents_texture.png (Part 3 section 6.5)
  kitchen/logs/<BOOK_ID>-toc.json   (the validated TOC per book)
  Neo4j: (:Territory) with CHILD_OF relationships

2.3 Column definitions of territories.csv (fixed text)
  territory_id   "Cnn" | "Cnn.Pmm" | "Cnn.Pmm.Dkkk" (Part 2 section
                 6.1 B). P00 = the pseudo-province of a book with no
                 Part/Section level. Dkkk = the book's printed chapter
                 number when it has one, else sequential.
  level          continent | province | district.
  name           Verbatim from the Table of Contents (the chapter title
                 for districts; the Section/Part heading for provinces;
                 the field_name for continents).
  part_name      Provinces only: the heading of the level above the
                 province when the book has two levels (e.g. "PART 2
                 Cardinal Manifestations and Presentation of Diseases"
                 above "SECTION 2 Alterations in Body Temperature").
                 Equal to name when there is one level. Empty for
                 continents and districts.
  book_id        The book this territory belongs to.
  parent         territory_id of the parent (province for a district,
                 continent for a province); empty for continents.
  page_start     First printed page of the territory.
  page_end       Last printed page (next territory's start minus one;
                 for the last chapter, the page before the index, or
                 start + median chapter length if unknown; Part 3
                 section 4.4).
  page_count     page_end - page_start + 1; the weight that set the
                 territory's area (Part 3 section 6.4).
  lat, lon       Centre in degrees, 4 decimals. For districts: the
                 area-weighted centre snapped to a pixel inside the
                 district. For provinces: area-weighted mean of their
                 districts. For continents: the Fibonacci point.
  area_fraction  Fraction of the globe's surface, 6 decimals. Within a
                 continent, district areas are proportional to
                 page_count within one pixel row.
  seat_order     Continents only; empty otherwise.
  raster_code    Districts only: the integer code in
                 district_raster.png (pixel value R*256 + G) and in
                 districts_lookup.json. Unique across the whole globe.
                 Empty for provinces and continents.
  colour_hex     The fill colour of the territory in
                 continents_texture.png (one hue per continent,
                 lightness by province; Part 3 section 6.5).
  bbox_px        Districts only: "x0,y0,x1,y1" in the 2048x1024 raster.
  toc_number     Districts only: the chapter number string exactly as
                 printed in the TOC (may differ from Dkkk when the book
                 uses letters or restarts numbering); provinces: the
                 Part/Section number string; empty if none.

2.4 Summary section (generated)
  (a) Totals: continents, provinces, districts; smallest and largest
      district by area_fraction with name and book; median district
      page_count.
  (b) Per continent, in seat_order, a block:
      "C01 Internal Medicine (general) -- HARRISON-22 -- 20 provinces,
       505 districts, pages 1-4000"
      followed by one line per province:
      "  C01.P02  SECTION 1 Pain  (PART 2 Cardinal Manifestations ...)
         pages 93-132  6 districts"
      Districts are NOT listed in the .md (that would be ~4,000 lines);
      they are in the CSV. Exception: the five largest districts of
      each continent are listed, as the landmarks a user will notice.
  (c) Books whose page numbering was irregular (per-province offsets
      or validation warnings accepted by the human at Checkpoint 3.2),
      with the human's words.
  (d) The link to the texture preview committed at Freeze A:
      data/export/geography/continents_texture.png, and the seating
      approval (Checkpoint 3.3) with date.

2.5 Verification queries (run by the script; outputs pasted)
  MATCH (t:Territory) RETURN t.level, count(*) ORDER BY t.level;
  MATCH (d:Territory {level:"district"}) WHERE NOT (d)-[:CHILD_OF]->(:Territory {level:"province"})
    RETURN count(d);                                        -- must be 0
  MATCH (p:Territory {level:"province"}) WHERE NOT (p)-[:CHILD_OF]->(:Territory {level:"continent"})
    RETURN count(p);                                        -- must be 0
  MATCH (d:Territory {level:"district"}) RETURN sum(d.area_fraction);   -- about 1.0
  MATCH (d:Territory {level:"district"}) WITH d.raster_code AS c, count(*) AS n WHERE n > 1
    RETURN c, n LIMIT 5;                                    -- must be empty
  MATCH (d:Territory {level:"district"}) WHERE d.raster_code IS NULL OR d.lat IS NULL
    RETURN count(d);                                        -- must be 0
  MATCH (d:Territory {level:"district"})-[:CHILD_OF]->(p:Territory)
    WHERE d.page_start < p.page_start OR d.page_end > p.page_end
    RETURN count(d);                                        -- must be 0
  Consistency checks in Python: the set of raster_code values in the
  CSV equals the set of keys in districts_lookup.json equals the set of
  distinct non-zero values in district_raster.npy; the number of
  districts per book in the CSV equals the chapter count in that book's
  toc.json. Any mismatch: exit 1, BLOCKED, no fixing.

2.6 How a later reader of the project uses this atlas (fixed text)
  "To find where a page of a book lands on the globe: look up the
  book_id and the printed page; the district whose page range contains
  it is the WHERE; its lat and lon are the centre where the lights of
  that chapter are drawn; its raster_code is the value painted at that
  place in district_raster.png. To find what a place on the globe is:
  read the raster pixel, look up the code. Nothing else is needed, and
  nothing in this file changes."

================================================================================
INSTALLATION (CHEAP; one session)
================================================================================
  1. Write kitchen/build_appendices.py (section 0.4). Run it.
  2. Append the exception sentence to AGENTS.md Forbidden list (0.4).
  3. Open the two .md files; confirm the five sections and that the
     verification outputs show the expected values (zeros where "must
     be 0", about 1.0 where stated).
  4. Commit "App.A-B generate appendices A and B" and push.
  EVIDENCE: the script's two summary lines; head -n 12 of each .md;
  the verification outputs; commit hash.
  CHECKPOINT A-B.1: the human opens appendix A on GitHub and sees the
  seating list matching the approved seating preview. Recorded under
  DECISIONS BY HUMAN.

================================================================================
HANDOFF CAPSULE (updated; paste into a NEW conversation with Fable when
asking for the final delivery)
================================================================================
Project: "Second Opinion", a medical knowledge globe built only from N
(up to 42) medical textbooks the human owns, vibe-coded, open source,
hosted at https://www.strulovitz.org/2nd-opinion/ from the human's own
computers via Cloudflare Tunnel, synced through
https://github.com/strulovitz/second-opinion. Fable writes a
13-delivery BIBLE (9 parts + 4 appendix templates) in plain text, one
copy-paste block per delivery, no tables, no collapsibles. Delivered:
Parts 1-9 (charter and world model; environment and Neo4j schema;
Phase A skeleton with Freeze A; Phase B reading pipeline; Phase C
altitudes with Freeze B; HTML pages; viewer; manager protocol;
publishing and ledger) and Appendices A (Field Registry: books.csv
columns book_id, title, edition, year, field_name, continent_id,
seat_order, cluster, lat, lon, area_fraction, page_count, page_offset,
text_layer, toc_images, index_images, provinces, districts, status,
duplicate_of, decision_date, notes; progress columns may update) and B
(Territory Atlas: territories.csv columns territory_id, level, name,
part_name, book_id, parent, page_start, page_end, page_count, lat,
lon, area_fraction, seat_order, raster_code, colour_hex, bbox_px,
toc_number). Common appendix rules: appendices are the RECORD, not
the law; generated by kitchen/build_appendices.py from
data/registry/*.csv with five sections (purpose, source files, column
definitions, generated summary, verification queries with pasted
outputs); header "Generated <date> from commit <hash>. Do not edit by
hand."; the script is the one exception allowing writes into
BIBLE/appendix-*.md (AGENTS.md amended). Entity schema (Part 2 + later
amendments): slug, group, canonical_name, aliases, aliases_text,
abbreviations, generic_names, brand_names, formulas, drug_class,
drug_class_mentions, class_verbatim, class_canonical,
heaviness_group, heaviness_confidence, created_from, created_book_id,
frozen, ordering_value, tie1, tie2, rank, altitude, altitude_status
(provisional/frozen/inserted), altitude_date, tldr, eli5, text_model,
text_date, text_quote_count, text_status. Part 5: symptoms ordered by
specificity (distinct diseases with PRESENTS_WITH; ties districts,
books, name; rank 0 = most = lowest r, band 1.02-1.50), diseases by
breadth (distinct books across lit spots and edges; ties districts,
name; rank 0 = deepest r = 0.30, band 0.30-0.98), treatments by
heaviness sub-band (lifestyle 1.52-1.78, otc 1.82-2.08, prescription
2.12-2.38, biologic-chemo-radiation 2.42-2.68, surgery-transplant
2.72-2.98) then class_canonical alphabetical ("(unclassified)" last)
then name; r_k = r_min + (r_max - r_min) k/(n-1); insertion rule =
midpoint between neighbours, rank + 0.5; Freeze B exports
data/registry/entities.csv (slug, group, canonical_name,
created_book_id, lit_spot_count, book_count, altitude, rank,
ordering_value, tie1), aliases.csv (slug, alias), heaviness.csv (slug,
canonical_name, heaviness_group, heaviness_confidence, class_verbatim,
class_canonical), classes.csv (heaviness_group, class_canonical,
member_count, members_verbatim_forms); tag altitude-freeze-B.
Next delivery requested: Appendices C (Entity and Altitude Registry)
and D (Treatment Heaviness Groups and Classes), in the same five-
section template style, with column definitions, generated summary
contents, verification queries, the freeze rule (generated at Freeze
B; aliases may still grow; inserted entities appended with status
"inserted"), and the final installation step and Checkpoint. This is
the 13th and last delivery.
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
