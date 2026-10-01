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
