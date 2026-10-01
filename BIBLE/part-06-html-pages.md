================================================================================
SECOND OPINION -- THE BIBLE
PART 6 OF 13 -- THE HTML PAGES
File: BIBLE/part-06-html-pages.md
MANAGER FOR THIS PART: SMART (Claude Sonnet 5.5 / GPT 6.1 Sol) writes
                       the three scripts and the CSS once (sections 4-9);
                       [SWITCH TO CHEAP] for running, text generation
                       babysitting, link checks and reviews (sections
                       10-11) and for every later regeneration.
READER FOR THIS PART:  free local model, TEXT mode, prompt P-D1 only
                       (TL;DR and ELI5).
PRECONDITIONS:         Freeze A done. Altitudes exist (provisional is
                       enough; Part 5 section 1.1). Some Phase B pages
                       loaded (the pilot is enough to test; pages for
                       entities with no quotes are generated too, see
                       section 6.5).
================================================================================

0. PURPOSE AND AMENDMENTS
--------------------------------------------------------------------------------
0.1 Purpose
  One static HTML file per entity, site/pages/<slug>.html, built ONLY
  from the entity's export file site/data/entities/<slug>.json, which is
  built ONLY from Neo4j. The page shows: what the books call it, what
  the books connect it to (blue / yellow / grey, sized by frequency),
  where the books discuss it, the verbatim sentences with book and page,
  and two AI-written helpers (TL;DR, ELI5) composed from those sentences
  alone. Plus three A-Z list pages and a link back to the globe.

0.2 BIBLE AMENDMENTS declared in this part
  AMENDMENT 6.1 (moves work from Part 9 to Part 6). The scripts
    kitchen/export_entities.py (writes entities/<slug>.json and
    search.json) and kitchen/build_pages.py are delivered in this part.
    Part 9 delivers the remaining export files (books.json,
    quarantine.json, ledger.json) and the orchestrating export.py that
    calls export_entities.py.
  AMENDMENT 6.2 (viewer URL scheme, binding for Part 7). The viewer
    lives at site/viewer/index.html and is addressed by hash routes:
      #/globe                      the 3-D globe
      #/map/<slug>                 the 2-D map of that entity's shell
      #/map/<slug>/3d              the same shell drawn on the 3-D globe
      #/district/<territory_id>    the globe centred on a territory
    Pages link only to these four forms, always relatively
    ("../viewer/index.html#/map/<slug>").
  AMENDMENT 6.3 (adds to Part 2 section 6.1 C). Entity gets
    text_quote_count (integer: how many quotes the reader saw when it
    wrote tldr/eli5) and text_status ("none" | "written" | "stale").
  Everything else in Parts 1-5 stands.

0.3 Order of work
  Step D0  Export entities and search index              (section 4)   SMART writes, CHEAP runs
  Step D1  TL;DR + ELI5 generation, prompt P-D1          (section 5)   SMART writes, reader works, CHEAP babysits
  Step D2  Page template, CSS, list pages                (sections 6-8) SMART writes
  Step D3  Build, link check                              (section 9)   CHEAP
  Step D4  Review and Checkpoint 6.1                      (section 10)  CHEAP + human
  Step D5  Regeneration rule                              (section 11)  CHEAP, forever

1. FIXED NAMES AND PATHS USED BY PAGES
--------------------------------------------------------------------------------
  site/index.html                      main page (Part 9; has the ONLY disclaimer)
  site/pages/<slug>.html               one per entity
  site/pages/all-symptoms.html         A-Z list, symptoms-and-signs
  site/pages/all-diseases.html         A-Z list, diseases-and-conditions
  site/pages/all-treatments.html       A-Z list, treatments-and-drugs
  site/assets/pages.css                the one stylesheet for all pages
  site/data/entities/<slug>.json       the entity export (also in data/export/)
  site/data/search.json                the elevator list (also in data/export/)
  site/viewer/index.html               the viewer (Part 7)
  From a page in site/pages/, every link is relative:
    ../index.html   ../assets/pages.css   ../viewer/index.html#/map/<slug>
    ../data/entities/<slug>.json   <other-slug>.html   all-diseases.html
  No absolute paths, no domain names, no JavaScript in pages (Law 14:
  nothing to break, nothing to maintain).

2. WORDING TABLE (fixed English phrases; the human may edit the text
   file kitchen/prompts/wording.json, never the code)
--------------------------------------------------------------------------------
  Group labels:
    symptoms-and-signs        "Symptom or sign"
    diseases-and-conditions   "Disease or condition"
    treatments-and-drugs      "Treatment or drug"
  Section titles by relation and direction (direction is from the
  viewpoint of the page's own entity):
    PRESENTS_WITH in  (page = symptom)   "Caused by: diseases and conditions that present with this"   BLUE
    PRESENTS_WITH out (page = disease)   "You may notice: symptoms and signs of this condition"       BLUE
    TREATED_BY out    (page = disease or symptom) "Treated by"                                        BLUE
    TREATED_BY in     (page = treatment) "Used for"                                                   BLUE
    HARMS out         (page = treatment, subtype null) "Can cause: side effects and harms"            YELLOW
    HARMS out         (subtype CONTRAINDICATED_IN) "Must not be given to people who have"             YELLOW
    HARMS in          (page = disease or symptom, subtype null) "Can be caused by a treatment (side effect)"  YELLOW
    HARMS in          (subtype CONTRAINDICATED_IN) "Treatments that must not be given in this condition"    YELLOW
    LEADS_TO out      (page = disease)   "If present, can lead to / raises the risk of"               YELLOW
    LEADS_TO in       (page = disease)   "Can result from"                                            YELLOW
    MISTAKEN_FOR      (either)           "Often mistaken for (differential diagnosis)"                GREY
  F-scale labels:
    F5 "very common"  F4 "common"  F3 "uncommon"  F2 "rare"
    F1 "very rare"    F0 "frequency not stated in the books"
  Severity marker text: "serious" (shown with the red ring style).
  Altitude line templates:
    symptom:   "Altitude {r}. Presents in {n} diseases or conditions, counted in the books read so far. Low altitude means nonspecific; high means specific."
    disease:   "Altitude {r}. Discussed in {n} of the {N} books. Deep means multisystem; shallow means local."
    treatment: "Altitude {r}. Orbit group: {heaviness_group_label} (grouping decided by the reader model for layout only). Class: {class_canonical}."
    heaviness_group_label: lifestyle "lifestyle and diet"; otc "over-the-counter medicines"; prescription "prescription medicines and minor procedures"; biologic-chemo-radiation "biologics, chemotherapy, radiation and hospital procedures"; surgery-transplant "surgery, devices and transplantation"
  AI-written label (shown above TL;DR and ELI5):
    "Written by the reader model ({model}) on {date}, using only the {k} book sentences quoted on this page."
  No-text notice (section 6.5):
    "No page of the books about this entity has been read yet. It appears in the index of: {book list}. The map still shows where."

3. THE ENTITY EXPORT FORMAT (exact; entities/<slug>.json)
--------------------------------------------------------------------------------
  {
   "slug": "...", "group": "...", "canonical_name": "...",
   "aliases": [...], "abbreviations": [...],
   "generic_names": [...], "brand_names": [...], "formulas": [...],
   "drug_class": "...", "class_canonical": "...",
   "heaviness_group": "...", "heaviness_confidence": 0.0,
   "altitude": 1.234567, "rank": 17, "altitude_status": "provisional|frozen|inserted",
   "ordering_value": 212, "tie1": 90, "tie2": 7,
   "books_total": 42,
   "tldr": "...", "eli5": "...", "text_model": "...", "text_date": "...",
   "text_quote_count": 31, "text_status": "none|written|stale",
   "lit_spots": [
     {"district_id":"C01.P02.D020","district_name":"Fever","book_id":"HARRISON-22",
      "book_field":"Internal Medicine (general)","pages":[133,134,135],
      "sources":["index","page"]}
   ],
   "edges": [
     {"relation":"PRESENTS_WITH","direction":"in|out","subtype":null,
      "other_slug":"...","other_name":"...","other_group":"...",
      "f_scale":4,"severity":false,"numeric_pct":null,
      "statements":[
        {"book_id":"HARRISON-22","district_id":"C01.P02.D020","district_name":"Fever",
         "page_number":134,"quote":"...","frequency_phrase":"often","f_scale":4,
         "numeric_pct":null,"severity":false,"severity_phrase":""}
      ]}
   ],
   "quotes_total": 57,
   "export_date": "2026-10-01"
  }
  Aggregation rules (Part 1 section 3.7 d, made exact):
  - One aggregated edge per (relation, direction, subtype, other_slug).
  - f_scale = the MAX over statements; numeric_pct = the max numeric
    value if any statement has one, else null; severity = true if ANY
    statement is severe.
  - MISTAKEN_FOR is stored once in Neo4j (smaller slug -> larger) but
    exported into BOTH entity files with direction "both".
  - statements are sorted by f_scale desc, then book_id, then page.
  - lit_spots: one object per (district, book) with the sorted distinct
    page list; sources lists which of index/page produced them.
  - edges sorted by: colour group (blue, yellow, grey), then f_scale
    desc, then severity true first, then other_name.
  search.json: a list of {"slug","group","canonical_name","aliases",
  "altitude","rank","lit_spot_count","edge_count","has_text"} sorted
  by group then canonical_name. Expected size: a few MB; fine.

4. STEP D0 -- kitchen/export_entities.py (SMART writes; under 200 lines)
--------------------------------------------------------------------------------
4.1 Cypher used (through db.run; three queries per entity, or one batch
    per 500 entities for speed; the writer may batch but must produce
    exactly the format of section 3):
    Entities:
      MATCH (e:Entity) RETURN e { .* } AS e ORDER BY e.slug
    Lit spots of one entity:
      MATCH (e:Entity {slug:$slug})-[l:DISCUSSED_IN]->(d:Territory)
      MATCH (d)-[:CHILD_OF*1..2]->(c:Territory {level:"continent"})
      RETURN d.territory_id AS district_id, d.name AS district_name,
             l.book_id AS book_id, c.name AS book_field,
             collect(DISTINCT l.page_number) AS pages,
             collect(DISTINCT l.source) AS sources
    Edges of one entity (outgoing):
      MATCH (e:Entity {slug:$slug})-[r:PRESENTS_WITH|TREATED_BY|HARMS|LEADS_TO|MISTAKEN_FOR]->(o:Entity)
      MATCH (d:Territory {territory_id: r.district_id})
      RETURN type(r) AS relation, "out" AS direction, r.subtype AS subtype,
             o.slug AS other_slug, o.canonical_name AS other_name, o.group AS other_group,
             r.book_id AS book_id, r.district_id AS district_id, d.name AS district_name,
             r.page_number AS page_number, r.quote AS quote, r.frequency_phrase AS frequency_phrase,
             r.f_scale AS f_scale, r.numeric_pct AS numeric_pct, r.severity AS severity,
             r.severity_phrase AS severity_phrase
    Incoming: the same with the arrow reversed and "in" as direction.
    MISTAKEN_FOR rows get direction "both" in Python.
    books_total: MATCH (b:Book) WHERE b.status IN ["index-done","reading","read"] RETURN count(b)
4.2 Writes site/data/entities/<slug>.json and data/export/entities/
    <slug>.json (identical), then search.json in both places. Idempotent:
    a file is rewritten only if its content (excluding export_date)
    changed; unchanged files keep their old export_date. Prints: entities
    exported, files changed, largest file size. Any single file over
    40 MB: STOP and write QUESTIONS FOR HUMAN (expected never; fever at
    42 books might reach a few MB).
4.3 Run:  python kitchen/export_entities.py
    EVIDENCE: the printed summary; ls site/data/entities | wc -l equals
    the Entity count in Neo4j.

5. STEP D1 -- TL;DR AND ELI5 (reader prompt P-D1; script
   kitchen/write_texts.py)
--------------------------------------------------------------------------------
5.1 Which entities get text: those with quotes_total >= 1 and text_status
    in ("none", "stale"). Entities with quotes_total = 0 get text_status
    "none" and the no-text notice (2). Order: by quotes_total descending
    (the most connected entities first: they are the pages users will
    reach first).
5.2 Input selection per entity (built by the script): canonical_name,
    group label, aliases (up to 8), and up to 40 quotes chosen as
    follows: all distinct quotes from edges sorted by f_scale desc with
    severity true pulled forward, taking at most 3 quotes per other
    entity and at most 15 per book, until 40 or exhausted; if fewer than
    10, add lit-spot quotes (page sentences). Each quote is given with
    "[book_id p.page]" in front. Total input capped at 9,000 characters
    (cut the list, never a quote).
5.3 System message P-D1 (verbatim; the script appends the human's
    additional-rules-P-D1.txt):

    You write two short plain-language texts about one medical entity
    for a general reader, using ONLY the quoted sentences you are given
    from medical textbooks. Output ONLY JSON:
    {"tldr":"<1 or 2 sentences, max 60 words>",
     "eli5":"<2 to 4 short paragraphs, max 220 words, simple words,
             explain like the reader is a smart twelve-year-old>"}
    Strict rules: (1) every fact you write must be supported by one of
    the quotes; do not add anything from your own knowledge, not even
    well-known facts; (2) if the quotes do not cover something (for
    example no treatment is quoted), simply do not mention it; (3) keep
    the frequency words of the quotes ("rarely", "most patients"); do
    not upgrade or downgrade them; (4) if the quotes disagree, say that
    the books differ; (5) no advice, no instructions to the reader, no
    "see a doctor", no disclaimers, no warnings in your own voice; only
    what the books say, in simple words; (6) do not name the books in
    the text; (7) do not use the words "I", "we", "you should".

5.4 User message: {"entity": name, "group": label, "aliases": [...],
    "quotes": ["[HARRISON-22 p.134] ...", ...]}.
    Call: reader.ask(P_D1, user, max_tokens=900). On invalid JSON
    twice: text_status stays as it was, logged. Length check: tldr
    over 90 words or eli5 over 300 words -> re-ask once with "Shorter."
    appended; then accept.
5.5 Write to Neo4j:
      MATCH (e:Entity {slug:$slug})
      SET e.tldr=$tldr, e.eli5=$eli5, e.text_model=$model,
          e.text_date=toString(date()), e.text_quote_count=$k,
          e.text_status="written"
    Then export_entities.py must run again before build (section 9 does
    this automatically).
5.6 Staleness: after each Phase B load, the loader (Part 4 section 10)
    runs:
      MATCH (e:Entity) WHERE e.text_status="written"
      OPTIONAL MATCH (e)-[r:PRESENTS_WITH|TREATED_BY|HARMS|LEADS_TO|MISTAKEN_FOR]-()
      WITH e, count(r) AS q
      WHERE q >= 10 AND q >= 2 * coalesce(e.text_quote_count, 0)
      SET e.text_status = "stale"
    (text is rewritten only when the evidence has at least doubled and
    is at least 10 quotes: cheap, and the first text stays good enough.)
    DEFAULT, human may overturn.
5.7 Run unattended:
      nohup python kitchen/write_texts.py > kitchen/logs/write-texts.log 2>&1 &
    Idempotent (skips "written"). Ledger per run in PROGRESS.md: texts
    written, failed, average seconds.

6. STEP D2 -- THE PAGE TEMPLATE (exact structure and order; the script
   fills it with html.escape on every value)
--------------------------------------------------------------------------------
6.1 <head>: charset utf-8; viewport width=device-width, initial-scale=1;
    <title>{canonical_name} -- Second Opinion</title>;
    <link rel="stylesheet" href="../assets/pages.css">;
    <meta name="description" content="{tldr or first 150 chars of the
    no-text notice}">. No scripts.
6.2 <body> order:
    (1) <nav class="top">: links "Second Opinion" (../index.html),
        "Globe" (../viewer/index.html#/globe), "Symptoms"
        (all-symptoms.html), "Diseases" (all-diseases.html),
        "Treatments" (all-treatments.html).
    (2) <header class="entity {group}">:
        <p class="group">{group label}</p>
        <h1>{canonical_name}</h1>
        <p class="aliases">Also called: {aliases joined by "; "}</p>
          (omitted if no aliases other than the name)
        treatments only: <p class="drugnames">Generic: {...}. Brand:
          {...}. Chemical: {...}.</p> (each part omitted if empty)
        <p class="altitude">{altitude line from section 2}</p>
        <p class="globe-link"><a href="../viewer/index.html#/map/{slug}">Show me on the globe</a>
          -- <a href="../viewer/index.html#/map/{slug}/3d">in 3-D</a></p>
    (3) <section class="tldr"> with <h2>TL;DR</h2>, the AI-written label
        in <p class="ai-label">, then <p>{tldr}</p>. If text_status is
        "none": instead <p class="notice">{no-text notice}</p> and no
        ELI5 section.
    (4) <section class="eli5"> with <h2>Explained simply</h2>, the same
        AI-written label, then the eli5 paragraphs (split on blank
        lines into <p>).
    (5) Relation sections, in this order, each only if it has items:
        blue sections first (PRESENTS_WITH, TREATED_BY in the order of
        section 2), then yellow (HARMS plain, HARMS contraindicated,
        LEADS_TO out, LEADS_TO in), then grey (MISTAKEN_FOR).
        <section class="rel {blue|yellow|grey}">
          <h2>{section title}</h2>
          <ol class="items">
            <li class="f{f_scale} {severe}">
              <a href="{other_slug}.html">{other_name}</a>
              <span class="fbadge">{F label}</span>
              {if numeric_pct: <span class="pct">{numeric_pct}%</span>}
              {if severity: <span class="severe">serious</span>}
              <span class="cites">{n statements}: {book_id} p.{page}; ...
                 (first 3 citations; then "and {k} more")</span>
            </li>
          </ol>
        </section>
        Items sorted as the export sorts them (F desc, severe first,
        name).
    (6) <section class="where"><h2>Where the books discuss this</h2>
        one <h3>{book_field} ({book_id})</h3> per book, then a <ul> of
        "<a href="../viewer/index.html#/district/{district_id}">
        {district_name}</a> -- pages {pages}" (pages compressed to
        ranges: 133-135, 140). Books sorted by number of pages desc.
    (7) <section class="quotes"><h2>Verbatim from the books</h2>
        <ol class="quotes"> one <li> per distinct quote (from edges and
        lit spots), as: <blockquote>{quote}</blockquote>
        <cite>{book_id}, {district_name}, p.{page}</cite>. Sorted by
        book_id then page. CAP: 80 quotes on the page; if more, a final
        <li class="more">{k} more sentences are in the data file:
        <a href="../data/entities/{slug}.json">{slug}.json</a></li>.
    (8) <footer>: "Data file: <a ...>{slug}.json</a>. Altitude status:
        {altitude_status}. Exported {export_date}. Source code and data:
        <a href="https://github.com/strulovitz/second-opinion">GitHub</a>."
        (This is the only absolute URL allowed, and it is a link to the
        project itself.) NO disclaimer here (Law 12).
6.3 Group-dependent sections (so that the manager does not invent
    extra ones): a symptom page can have: PRESENTS_WITH in, TREATED_BY
    out, HARMS in (plain). A disease page can have: PRESENTS_WITH out,
    TREATED_BY out, HARMS in (plain), HARMS in (contraindicated),
    LEADS_TO out, LEADS_TO in, MISTAKEN_FOR. A treatment page can have:
    TREATED_BY in, HARMS out (plain), HARMS out (contraindicated).
    Any edge in the export that does not fit these is still rendered,
    under the title of its relation/direction from section 2, so
    nothing is hidden; the build prints a count of such "unexpected"
    edges for the review.
6.4 Links to entities with no page: never happens; every entity in the
    registry gets a page (6.5). Links to slugs absent from search.json
    (should be impossible) are rendered as plain text and counted by
    the link checker.
6.5 Entities with zero quotes still get a full page: header, altitude
    line, globe link, the no-text notice, "Where the books discuss
    this" from the index lit spots, footer. This is the majority of
    pages until Phase B is far along, and it is honest.

7. site/assets/pages.css (exact content; SMART may add rules, never
   remove these)
--------------------------------------------------------------------------------
    :root { --blue:#1f5fbf; --yellow:#e0a800; --grey:#6b6b6b; --red:#b3261e;
            --bg:#fbfbf8; --ink:#1b1b1b; --muted:#555; }
    * { box-sizing: border-box; }
    body { margin:0; font: 17px/1.55 system-ui, -apple-system, "Segoe UI", Roboto, sans-serif;
           color:var(--ink); background:var(--bg); }
    nav.top { display:flex; flex-wrap:wrap; gap:1em; padding:.7em 1em; background:#222; }
    nav.top a { color:#fff; text-decoration:none; }
    header.entity, section, footer { max-width:56em; margin:0 auto; padding:1em; }
    header.entity .group { color:var(--muted); text-transform:uppercase; letter-spacing:.05em; font-size:.85em; margin:0; }
    header.entity h1 { margin:.1em 0 .3em; font-size:2em; line-height:1.15; }
    header.symptoms-and-signs h1 { color:#1b6b3a; }
    header.diseases-and-conditions h1 { color:#7a2e1d; }
    header.treatments-and-drugs h1 { color:#2e3f7a; }
    .aliases, .drugnames, .altitude { color:var(--muted); margin:.2em 0; }
    .globe-link a { font-weight:600; }
    .ai-label { font-size:.85em; color:var(--muted); font-style:italic; margin:0 0 .4em; }
    .notice { background:#fff4d6; padding:.6em .9em; border-left:4px solid var(--yellow); }
    section.rel { border-left:6px solid var(--grey); padding-left:1em; margin-top:1.2em; }
    section.rel.blue { border-color:var(--blue); }
    section.rel.yellow { border-color:var(--yellow); }
    section.rel h2 { font-size:1.15em; margin:.2em 0 .5em; }
    ol.items { list-style:none; padding:0; margin:0; }
    ol.items li { display:flex; flex-wrap:wrap; align-items:baseline; gap:.5em;
                  padding:.35em 0; border-bottom:1px solid #e6e6e0; }
    ol.items li a { font-weight:600; text-decoration:none; color:var(--ink); }
    ol.items li.f5 a { font-size:1.35em; }  ol.items li.f4 a { font-size:1.2em; }
    ol.items li.f3 a { font-size:1.05em; }  ol.items li.f2 a { font-size:.95em; }
    ol.items li.f1 a { font-size:.85em; }   ol.items li.f0 a { font-size:1.05em; border-bottom:1px dashed var(--grey); }
    .fbadge { font-size:.8em; color:#fff; background:var(--grey); border-radius:1em; padding:.05em .6em; }
    section.blue .fbadge { background:var(--blue); }
    section.yellow .fbadge { background:var(--yellow); color:#222; }
    .pct { font-size:.85em; color:var(--muted); }
    .severe { font-size:.8em; color:var(--red); border:2px solid var(--red); border-radius:1em; padding:0 .5em; font-weight:700; }
    .cites { font-size:.8em; color:var(--muted); flex-basis:100%; }
    section.where h3 { font-size:1em; margin:.8em 0 .2em; }
    ol.quotes blockquote { margin:.3em 0 .1em; padding:.3em .8em; border-left:3px solid #ccc; background:#fff; }
    ol.quotes cite { font-size:.8em; color:var(--muted); }
    footer { font-size:.85em; color:var(--muted); border-top:1px solid #ddd; margin-top:2em; }
    @media (max-width:600px) { body { font-size:16px; } header.entity h1 { font-size:1.6em; } }
  Note: item font size encodes F on the page the same way circle size
  encodes F on the map (Law 10); the dashed underline is F0; the red
  pill is the severity ring.

8. THE THREE A-Z LIST PAGES
--------------------------------------------------------------------------------
  all-<group>.html: same <head> and nav; <h1>{group label}s, A to Z</h1>;
  <p>{count} entities. {count_with_text} have text written; {count_with_edges}
  have connections.</p>; then for each initial letter an <h2>{letter}</h2>
  and a <ul> of <li><a href="{slug}.html">{canonical_name}</a>
  <span class="cites">{edge_count} connections</span></li>, sorted by
  canonical_name (case-insensitive, accents stripped for sorting only).
  Non-letter initials under "#". Expected size: up to a few hundred KB
  for diseases; acceptable.

9. STEP D3 -- kitchen/build_pages.py AND THE LINK CHECKER
--------------------------------------------------------------------------------
9.1 build_pages.py:
    (1) runs export_entities.py (import and call main) so pages never
        lag the database;
    (2) reads kitchen/prompts/wording.json (section 2; the script
        creates it with the default wording if absent);
    (3) renders every entity page and the three lists with Python
        f-strings and html.escape; no template library;
    (4) writes a file only if its content changed (compare bytes);
    (5) prints: pages written, pages unchanged, unexpected edges count,
        pages with no text, total size of site/pages/.
    Expected runtime: under a minute for 10,000 pages.
9.2 kitchen/check_links.py: scans every .html under site/ and for every
    href and src that is relative, checks the target file exists
    (hash fragments stripped; "../viewer/index.html#..." counts as OK if
    the viewer file exists, else counted as "viewer not built yet").
    Prints: links checked, broken links (with file and href), viewer
    links pending. Exit code 1 if any broken link. The build is "done"
    only with zero broken links.
9.3 Local preview (Part 2 section 8.4): cd site && python3 -m
    http.server 8765 ; the human opens http://localhost:8765/pages/
    all-symptoms.html on the laptop and on a phone on the same Wi-Fi
    (http://<laptop-ip>:8765/...).
9.4 Commit: site/pages/ and site/data/ are committed (small files,
    many). After each build: git add -A site data && git commit -m
    "Pages build <date>: <n> pages" && git push. If git complains about
    too many files, that is fine; it is just slow.

10. STEP D4 -- REVIEW AND CHECKPOINT 6.1
--------------------------------------------------------------------------------
10.1 kitchen/review_html.py writes kitchen/logs/html-review.md with:
     (a) the counts of 9.1 and 9.2;
     (b) 5 random slugs per group WITH text and 3 per group WITHOUT text,
         each as a local preview URL;
     (c) 15 random TL;DR texts with their entity names (for the human
         to spot invented facts: every sentence should be traceable to
         the quotes on the page);
     (d) the five largest pages by file size.
10.2 The human opens the sample pages on laptop and phone and answers:
     "ok"; or "wording: <key> = <text>" (edits wording.json; rebuild);
     or "css: <request>" (SMART edits pages.css); or "add rule: <text>"
     for P-D1 (appended to additional-rules-P-D1.txt; affected texts
     set to "stale" only if the human says "rewrite all"); or "text of
     <slug> is wrong" (set text_status "stale" for that slug; rewritten
     on the next write_texts run).
  CHECKPOINT 6.1: human approves the sample. Recorded under DECISIONS BY
  HUMAN. After this, pages are rebuilt routinely (section 11) with no
  further approval unless wording or CSS change.

11. STEP D5 -- REGENERATION RULE (forever)
--------------------------------------------------------------------------------
  After every Phase B book review approval (Part 4 Checkpoints 4.2 and
  beyond), after every altitude run, and after every quarantine replay:
    python kitchen/write_texts.py        (only none/stale; may run long,
                                          nohup; pages can be built
                                          before it finishes)
    python kitchen/build_pages.py
    python kitchen/check_links.py
    git add -A site data && git commit -m "Rebuild <date>" && git push
  The desktop PC pulls and serves. Nothing else is needed. This four-
  line sequence is written into PROGRESS.md as "STANDARD REBUILD" so
  that the CHEAP tier runs it without thinking.

12. SCRIPT LIST FOR THIS PART
--------------------------------------------------------------------------------
  export_entities.py      -> site/data/entities/*.json, search.json (both copies)
  write_texts.py          -> P-D1, Neo4j tldr/eli5
  build_pages.py          -> site/pages/*.html, all-*.html
  check_links.py          -> link report, exit code
  review_html.py          -> html-review.md
  assets/pages.css        -> section 7
  prompts/P-D1.txt, additional-rules-P-D1.txt, wording.json
  Reference implementation of two helpers (used by build_pages.py):

    import html, re, unicodedata
    def esc(x):
        return html.escape("" if x is None else str(x), quote=True)
    def page_ranges(pages):
        pages = sorted(set(int(p) for p in pages)); out = []; i = 0
        while i < len(pages):
            j = i
            while j + 1 < len(pages) and pages[j + 1] == pages[j] + 1:
                j += 1
            out.append(str(pages[i]) if i == j else f"{pages[i]}-{pages[j]}"); i = j + 1
        return ", ".join(out)
    def sort_key(name):
        s = unicodedata.normalize("NFKD", name)
        return "".join(c for c in s if not unicodedata.combining(c)).lower()
    def initial(name):
        k = sort_key(name)[:1]
        return k.upper() if k.isalpha() else "#"
    F_LABEL = {5:"very common",4:"common",3:"uncommon",2:"rare",1:"very rare",0:"frequency not stated in the books"}

13. DEFAULTS IN THIS PART THAT THE HUMAN MAY OVERTURN
--------------------------------------------------------------------------------
  (1) Zero JavaScript on entity pages; one CSS file (section 1).
  (2) Up to 40 quotes fed to P-D1; 60-word TL;DR; 220-word ELI5 (5.2-5.3).
  (3) Staleness = evidence doubled and at least 10 quotes (5.6).
  (4) 80-quote cap on the page, rest via the JSON link (6.2 step 7).
  (5) F encoded as font size on pages (section 7).
  (6) The wording of section 2 (editable in wording.json).
  (7) Edge sort: colour group, F desc, severe first, name (section 3).
  (8) Hash-route URL scheme for the viewer (Amendment 6.2).

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
(environment; repo layout kitchen/ data/ site/ BIBLE/; Neo4j schema:
Book, Territory, Entity(+Symptom/Disease/Treatment), QuarantineTerm,
Meta; DISCUSSED_IN lit spots; edges PRESENTS_WITH, TREATED_BY,
HARMS(subtype CONTRAINDICATED_IN), LEADS_TO, MISTAKEN_FOR with
provenance, frequency_phrase, f_scale 0-5, numeric_pct, severity,
quote_hash; kitchen/db.py, reader.py), Part 3 (Phase A: Fibonacci
sphere + Voronoi EQUAL-area continents with cluster seating; recursive
treemap making district area ~ page count; 2048x1024 equirectangular
district raster district_raster.png (code = R*256+G) + district_raster.npy
+ continents_texture.png 4096x2048 + districts_lookup.json +
geography.json with lat, lon, colour_hex, bbox_px, raster_code per
territory; index pipeline builds entity registry; Freeze A), Part 4
(Phase B reading pipeline: text-first transcription, vision only for
figure/table pages, sliding window, P-B1 extraction, quote
verification, F-scale table, resolution P-B2, quarantine, idempotent
load, ledger), Part 5 (Phase C altitudes: symptoms by specificity low =
nonspecific, diseases by breadth deep = multisystem, treatments by
heaviness sub-bands lifestyle 1.52-1.78, otc 1.82-2.08, prescription
2.12-2.38, biologic-chemo-radiation 2.42-2.68, surgery-transplant
2.72-2.98, then class then name; diseases 0.30-0.98, symptoms
1.02-1.50; guide spheres at 1.00, 1.50, 1.80, 2.10, 2.40, 2.70, 3.00;
Freeze B; insertion rule), Part 6 (HTML pages: export_entities.py
writes site/data/entities/<slug>.json with aggregated edges (one per
relation+direction+subtype+other_slug, f_scale max, severity any,
statements list with book/district/page/quote) and lit_spots per
district+book with page lists, plus search.json {slug, group,
canonical_name, aliases, altitude, rank, lit_spot_count, edge_count,
has_text}; write_texts.py with prompt P-D1 writes TL;DR + ELI5 from
quotes only, staleness when evidence doubles; build_pages.py renders
zero-JS pages with one CSS file pages.css where F is font size, F0
dashed, severity red pill, blue/yellow/grey sections with fixed
wording in wording.json, "Where the books discuss this" linking
#/district/<id>, verbatim quotes capped at 80, footer with JSON link,
no disclaimer on pages; three A-Z list pages; check_links.py;
Checkpoint 6.1; STANDARD REBUILD = write_texts, build_pages,
check_links, commit+push; Amendment 6.2 fixes the viewer hash routes:
site/viewer/index.html#/globe, #/map/<slug>, #/map/<slug>/3d,
#/district/<territory_id>; pages link relatively
../viewer/index.html#/map/<slug>). Viewer (Part 7, next): 3-D globe
with continents_texture on a sphere + faint guide spheres <-> 2-D
equirectangular map using the same texture; lit filled circles at
district lat/lon (ring when several share a district) sized by F, F0
dashed, blue forward / yellow harm / grey differential, severity red
ring; hover/tap shows other entity + frequency phrase + book/page;
click = cascade to that entity's map; altitude elevator = three
searchable lists from search.json; 2-D/3-D toggle; back to globe;
loads only entities/<slug>.json on demand; desktop + mobile (touch);
Chrome/Firefox/Safari/Edge; no build step; vendored JS libraries in
site/assets/; relative links only; hit-testing via district_raster.png
+ districts_lookup.json. Tiers: READER = free local Qwen 3.8 27B Q4_K_M
(Gemma 4 31B substitute); CHEAP = DeepSeek V4.1 Flash runs scripts;
SMART = Claude Sonnet 5.5 or GPT 6.1 Sol writes code; manager says
"HUMAN: please switch to <tier>" and stops. Laws include: books only,
provenance always, Neo4j single source of truth, cheap beats perfect,
never assume installed, when unclear stop and ask, one disclaimer only
(site/index.html bottom), no multi-model editions, books/images/
transcripts never committed.
Next delivery requested: Part 7 (The Viewer).
================================================================================
