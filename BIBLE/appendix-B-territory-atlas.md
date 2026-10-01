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
