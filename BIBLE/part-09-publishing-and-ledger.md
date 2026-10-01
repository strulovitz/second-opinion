================================================================================
SECOND OPINION -- THE BIBLE
PART 9 OF 13 -- PUBLISHING AND THE QUALITY LEDGER
File: BIBLE/part-09-publishing-and-ledger.md
MANAGER FOR THIS PART: SMART (Claude Sonnet 5.5 / GPT 6.1 Sol) writes
                       the four short scripts of section 10 (one
                       session); [SWITCH TO CHEAP] for everything else:
                       running exports, building, publishing, pulling
                       on the desktop, tunnel checks, the live checklist.
READER:                not used in this part.
PRECONDITIONS:         Parts 2-8 installed. At least: Freeze A done,
                       provisional altitudes (Part 5 section 1.1),
                       pages built (Part 6), viewer passing Checkpoint
                       7.1. Phase B may be anywhere (even just the
                       pilot): the site publishes honestly whatever
                       exists.
================================================================================

0. PURPOSE AND AMENDMENTS
--------------------------------------------------------------------------------
0.1 Purpose
  (a) One orchestrating export (kitchen/export.py) that writes every
      file the website reads, from Neo4j, in one command.
  (b) The QUALITY LEDGER: the honest numbers of the project (what was
      read, what was found, what is missing), computed from Neo4j and
      the Phase B ledgers, published as ledger.json and shown on the
      main page. Never rounded up, never hidden.
  (c) The final main page site/index.html, the published quarantine
      page, sitemap and robots.
  (d) The publish procedure: laptop -> GitHub -> desktop -> Cloudflare
      Tunnel, with a check that what the world sees is what was built.
  (e) The definition of "live".

0.2 BIBLE AMENDMENTS declared in this part
  AMENDMENT 9.1 (build stamp). export.py writes site/data/build.json:
    {"commit": "<git short hash at export time, or 'uncommitted'>",
     "export_date": "<ISO date-time>", "ledger_date": "<same>"}.
    The tunnel check (section 7) compares the served build.json with
    the local one. The commit field is filled AFTER the publish commit
    by publish.sh (section 6), which amends nothing: it writes the file,
    commits it as the last commit of the publish, so the hash recorded
    is the hash of the previous commit plus one; the check compares
    export_date, which is enough.
  AMENDMENT 9.2 (main-page text file). All visitor-facing prose of
    index.html lives in kitchen/prompts/index-text.json (committed),
    editable by the human; build_index.py renders it. The disclaimer
    text (Part 2 section 8.2) is the key "disclaimer" in that file and
    is rendered ONLY at the bottom of index.html (Law 12).
  AMENDMENT 9.3 (published quarantine page). site/pages/quarantine.html,
    zero-JS, lists open quarantine terms with counts and the books they
    came from. Linked from index.html under "What is not here yet".
  AMENDMENT 9.4 (sponsorship key). index-text.json has a key
    "sponsor_note", default empty string. If non-empty, build_index.py
    renders it in a clearly separated box titled exactly "Sponsored /
    paid content" above the footer. Nothing else on the site may carry
    paid content. This keeps the human's promise: paid things are
    marked, the data never is.
  Everything else in Parts 1-8 stands.

0.3 Order of work
  Step F0  Scripts: export.py, ledger.py, build_index.py, publish.sh   (section 10)  SMART
  Step F1  First full export + ledger                                   (sections 1-3) CHEAP
  Step F2  index.html, quarantine.html, sitemap, robots                (sections 4-5) CHEAP runs
  Step F3  Publish; desktop pull; tunnel check                          (sections 6-7) CHEAP + human
  Step F4  Live checklist; Checkpoint 9.1                               (section 8)    CHEAP + human
  Step F5  Routine: the publish cadence                                 (section 9)    CHEAP, forever

1. kitchen/export.py -- THE ORCHESTRATOR
--------------------------------------------------------------------------------
1.1 Runs, in this order, importing each module's main():
      export_entities.main()     (Part 6 section 4)   -> entities/, search.json
      export_districts.main()    (Part 7 section 3.1) -> districts/
      export_books()             (section 2.1)        -> books.json
      export_quarantine()        (section 2.2)        -> quarantine.json
      ledger.main()              (section 3)          -> ledger.json
      copy geography files if data/export/geography/ is newer than
        site/data/geography/   (Part 3 section 6.6)
      copy kitchen/prompts/wording.json -> site/data/wording.json
      write build.json           (Amendment 9.1)
    Every file is written to BOTH data/export/ and site/data/ (Part 2
    section 7), only when content changed (excluding date fields).
1.2 Prints one summary line per sub-export (count, files changed) and a
    final line "export complete <date-time>". Exit code 1 if any
    sub-export raised; then the partial files already written stay (they
    are valid) and the error goes to BLOCKED.
1.3 Run time: entities export dominates (one JSON per entity); for
    10,000 entities under two minutes on the laptop. If slower than ten
    minutes, SMART batches the Cypher (500 entities per query); nothing
    else changes.

2. books.json AND quarantine.json (exact formats)
--------------------------------------------------------------------------------
2.1 books.json: a list, one object per Book node of ANY status (rejected
    duplicates included: the decision is public):
    {"book_id","title","edition","year","field_name","continent_id",
     "page_count","status","pages_planned","pages_loaded",
     "pages_failed","edges_stored","index_entities_created",
     "lit_spots_index","lit_spots_page"}
    Cypher for the counts (per book; batched or per row):
      MATCH (b:Book {book_id:$id})
      OPTIONAL MATCH (:Entity)-[l:DISCUSSED_IN {book_id:$id}]->()
      WITH b, sum(CASE WHEN l.source="index" THEN 1 ELSE 0 END) AS li,
              sum(CASE WHEN l.source="page" THEN 1 ELSE 0 END) AS lp
      OPTIONAL MATCH (:Entity)-[r:PRESENTS_WITH|TREATED_BY|HARMS|LEADS_TO|MISTAKEN_FOR {book_id:$id}]->()
      WITH b, li, lp, count(r) AS edges
      OPTIONAL MATCH (e:Entity {created_book_id:$id})
      RETURN b.book_id AS book_id, li AS lit_spots_index, lp AS lit_spots_page,
             edges AS edges_stored, count(e) AS index_entities_created
    pages_planned/loaded/failed come from kitchen/logs/<BOOK_ID>-pages.jsonl
    (count of lines whose latest stage is "loaded"/"failed"; planned
    from <BOOK_ID>-plan.json); 0 if the files do not exist yet.
    Sorted by continent_id, rejected books last.
2.2 quarantine.json: {"export_date", "open_count", "resolved_count",
    "terms": [ {"term","group_guess","count_total","books":[book_id...],
    "first_seen_district":"<district name>","example_quote":"<the
    quote of the most-counted node, cut to 240 chars>"} ... ]}
    Cypher:
      MATCH (q:QuarantineTerm {resolved:false})
      WITH q.term AS term, collect(q) AS qs
      WITH term, qs, reduce(s=0, x IN qs | s + x.count) AS total
      ORDER BY total DESC
      RETURN term, qs[0].group_guess AS group_guess, total AS count_total,
             [x IN qs | x.book_id] AS books, qs[0].district_id AS first_district,
             qs[0].quote AS example_quote
    (district name resolved via geography; books deduplicated in
    Python.) Capped at 2,000 terms in the file; the total count is still
    reported. Terms with count_total = 1 are included (honesty) but the
    quarantine PAGE shows only count >= 2 plus a line "and N terms seen
    once".

3. ledger.json -- THE QUALITY LEDGER (exact content; kitchen/ledger.py)
--------------------------------------------------------------------------------
3.1 Fields:
    "ledger_date"              ISO date-time
    "commit"                   git short hash or "uncommitted"
    "skeleton_frozen"          true/false (Meta)      "freeze_a_date"
    "altitudes_frozen"         true/false (Meta)      "freeze_b_date"
    "altitude_status_counts"   {"provisional":n,"frozen":n,"inserted":n,"null":n}
    "books"                    {"total":n,"accepted":n,"rejected_duplicate":n,
                                "reading":n,"read":n}
    "pages"                    {"planned":n,"loaded":n,"failed":n,
                                "figure_pass":n,"percent_loaded":x.x}
                                (percent = loaded / planned * 100, ONE
                                 decimal, truncated not rounded)
    "territories"              {"continents":n,"provinces":n,"districts":n}
    "entities"                 {"symptoms":n,"diseases":n,"treatments":n,
                                "total":n,"with_text":n,"with_edges":n,
                                "with_only_index_mentions":n}
    "edges"                    {"PRESENTS_WITH":n,"TREATED_BY":n,"HARMS":n,
                                "HARMS_contraindicated":n,"LEADS_TO":n,
                                "MISTAKEN_FOR":n,"total":n,
                                "blue":n,"yellow":n,"grey":n}
    "frequency"                {"F5":n,...,"F0":n,"F0_percent":x.x,
                                "with_numeric_pct":n}
    "severity_edges"           n
    "verification"             {"exact":n,"fuzzy":n,"unverified":n,
                                "unverified_percent":x.x}
                                (from r.verify_status and the
                                 unverified.jsonl files)
    "quarantine"               {"open_terms":n,"resolved_terms":n,
                                "quarantined_edges_waiting":n}
    "lit_spots"                {"index":n,"page":n}
    "reader_models"            list of distinct r.reader_model values
                               with the count of edges each produced
    "reader_seconds_total"     sum of "seconds" over pages.jsonl lines
                               with stage loaded (honest wall-clock)
    "human_decisions"          count of lines under DECISIONS BY HUMAN
                               in PROGRESS.md
    "additional_rules"         {"P-B1":n,"P-B2":n,"P-C1":n,"P-D1":n}
                               line counts of the rules files
3.2 Cypher for the main counts (the writer may merge queries):
      MATCH (e:Entity) RETURN e.group, count(*);
      MATCH (e:Entity) WHERE e.text_status="written" RETURN count(e);
      MATCH (e:Entity) WHERE (e)-[:PRESENTS_WITH|TREATED_BY|HARMS|LEADS_TO|MISTAKEN_FOR]-() RETURN count(e);
      MATCH ()-[r:PRESENTS_WITH|TREATED_BY|HARMS|LEADS_TO|MISTAKEN_FOR]->() RETURN type(r), r.subtype, count(*);
      MATCH ()-[r:PRESENTS_WITH|TREATED_BY|HARMS|LEADS_TO|MISTAKEN_FOR]->() RETURN r.f_scale, count(*);
      MATCH ()-[r:PRESENTS_WITH|TREATED_BY|HARMS|LEADS_TO|MISTAKEN_FOR]->() WHERE r.severity RETURN count(*);
      MATCH ()-[r:PRESENTS_WITH|TREATED_BY|HARMS|LEADS_TO|MISTAKEN_FOR]->() RETURN r.verify_status, count(*);
      MATCH ()-[r:PRESENTS_WITH|TREATED_BY|HARMS|LEADS_TO|MISTAKEN_FOR]->() RETURN r.reader_model, count(*);
      MATCH ()-[l:DISCUSSED_IN]->() RETURN l.source, count(*);
      MATCH (q:QuarantineTerm) RETURN q.resolved, count(DISTINCT q.term);
      MATCH (e:Entity) RETURN coalesce(e.altitude_status,"null"), count(*);
      MATCH (m:Meta) RETURN m.key, m.value;
3.3 Rules: every number is what the queries return. No estimate, no
    projection ("expected when complete"), no rounding up. Percentages
    truncated to one decimal. If a source file is missing, the field is
    null and the main page shows "not yet measured" for it. ledger.json
    is committed every publish, so the GitHub history is itself a
    public log of how the numbers grew.

4. site/index.html -- FINAL CONTENT (rendered by kitchen/build_index.py
   from index-text.json + ledger.json + books.json)
--------------------------------------------------------------------------------
4.1 Head: same as pages (Part 6 section 6.1) with
    <link rel="stylesheet" href="assets/pages.css"> and one extra small
    stylesheet block for the hero and the numbers grid (SMART adds
    rules to pages.css under a comment "/* index */"; no new file).
    <title>Second Opinion -- a medical knowledge globe built only from
    textbooks</title>. No scripts.
4.2 Body, in order (keys refer to index-text.json; defaults given in
    4.3; the human may edit any text):
    (1) <nav class="top">: "Second Opinion", "Globe"
        (viewer/index.html#/globe), "Symptoms", "Diseases",
        "Treatments" (pages/all-*.html), "Numbers" (#numbers), "GitHub"
        (https://github.com/strulovitz/second-opinion).
    (2) <header class="hero">: <h1>{title}</h1> <p class="tag">{tagline}</p>
        <p class="cta"><a class="button" href="viewer/index.html#/globe">
        Open the globe</a></p>
    (3) <section id="what"><h2>{what_heading}</h2> {what_paragraphs}
        (list of paragraphs).
    (4) <section id="how"><h2>{how_heading}</h2> {how_paragraphs}
        followed by the fixed legend list (same text as the viewer
        legend, from wording.json keys).
    (5) <section id="start"><h2>{start_heading}</h2> three big links:
        "Start from a symptom" -> pages/all-symptoms.html; "Start from a
        disease" -> pages/all-diseases.html; "Start from a treatment or
        drug" -> pages/all-treatments.html; and a fourth: "Start from a
        book" -> a list of the accepted books (field_name, title,
        edition) each linking to viewer/index.html#/district/<first
        district id of that continent>.
    (6) <section id="numbers"><h2>{numbers_heading}</h2>
        <p class="ai-label">Measured from the database on {ledger_date};
        commit {commit}.</p>
        A definition-list grid, exactly these lines, values from
        ledger.json (null -> "not yet measured"):
          Books accepted / rejected as duplicates
          Pages planned / read so far ({percent_loaded}%)
          Chapters (districts) on the globe
          Symptoms and signs / Diseases and conditions / Treatments and drugs
          Entities with a written TL;DR / with at least one connection /
            with only index mentions so far
          Connections, total; blue (forward) / yellow (harm) / grey (differential)
          Of which "must not be given in" (contraindications)
          Connections marked serious by the books' wording
          Connections with a stated frequency / without ({F0_percent}%)
          Sentences the reader quoted that could NOT be found on the page
            and were therefore discarded ({unverified_percent}%)
          Terms found on pages that are not in the registry (quarantine):
            open / resolved
          Skeleton frozen: {yes/no, date}. Altitudes: {counts by status}
          Reader model(s) used, with connection counts
          Reader time spent, in hours (seconds / 3600, one decimal)
          Human decisions recorded
        Then <p>{numbers_note}</p> (default explains F0 and quarantine
        in one sentence each) and a link "Full ledger (JSON)" ->
        data/ledger.json and "Per-book numbers (JSON)" -> data/books.json.
    (7) <section id="missing"><h2>{missing_heading}</h2> {missing_paragraph}
        with links: pages/quarantine.html; data/quarantine.json; and
        the sentence "Pages not yet read: {planned - loaded} of
        {planned}."
    (8) <section id="made"><h2>{made_heading}</h2> {made_paragraphs}
        with links: GitHub repository; the BIBLE folder
        (https://github.com/strulovitz/second-opinion/tree/main/BIBLE);
        the registries folder (.../tree/main/data/registry).
    (9) If sponsor_note non-empty: <aside class="sponsored"><h2>Sponsored /
        paid content</h2><p>{sponsor_note}</p></aside> (Amendment 9.4).
    (10) <footer><p class="disclaimer">{disclaimer}</p>
         <p>Build {commit}, {export_date}.</p></footer>
         The ONLY disclaimer on the whole site (Law 12).
4.3 Default index-text.json (build_index.py creates it if absent; the
    human edits freely; keep the keys):
    title:           "Second Opinion"
    tagline:         "A medical knowledge globe built only from textbooks. Every light on it is a sentence in a book, with the page number."
    what_heading:    "What this is"
    what_paragraphs: [
      "Second Opinion is a map of what medical textbooks say: which symptoms the books connect to which diseases, which treatments the books connect to which diseases, and, with the same weight, which harms and side effects the books connect to which treatments.",
      "Nothing here comes from the internet, from a database, from a regulator, or from an AI model's memory. Everything was read from the pages of the books listed below by a local AI model running on one laptop, and every connection keeps the sentence it came from, with the book and page, so you can check it yourself.",
      "Forward connections (symptom to disease to treatment) are blue. Harm connections (treatment to side effect, disease to complication) are yellow, drawn with the same size rules, never smaller, never hidden."
    ]
    how_heading:     "How to read the globe"
    how_paragraphs:  [
      "Every continent is one textbook, one field of medicine. Every chapter is a district. The map never changes shape: you learn the geography once.",
      "Every symptom, disease and treatment is a shell at its own altitude. Diseases are inside the planet (deep means it touches many fields); symptoms are the atmosphere (low means nonspecific, high means specific); treatments are orbits (lifestyle lowest, surgery highest).",
      "Open a shell and you see lights on the familiar map: a light where a book connects that entity to another. Bigger means the book says it is more common. Dashed means the book did not say how common. A red ring means the book used words like fatal or life-threatening. Click a light to follow the chain."
    ]
    start_heading:   "Start somewhere"
    numbers_heading: "The numbers, honestly"
    numbers_note:    "Connections without a stated frequency are shown dashed, never guessed. Quarantine terms are words found on pages that did not match the frozen registry; they are listed, not dropped."
    missing_heading: "What is not here yet"
    missing_paragraph: "This is a work in progress read by an imperfect model. Pages not yet read are not here. Terms the model could not match are in quarantine. The AI-written summaries use only the quoted sentences and are labelled as AI-written on every page."
    made_heading:    "How it was made"
    made_paragraphs: [
      "The project is open source. The design document (the BIBLE), every script, the frozen registries and the exported data are in the repository. The books themselves are not: they are copyrighted; only short quoted sentences with citations are published.",
      "The reading was done by a free, local, open-weight model on the author's own computer; no cloud model touched a page."
    ]
    sponsor_note:    ""
    disclaimer:      the exact text of Part 2 section 8.2.

5. quarantine.html, sitemap.xml, robots.txt (built by build_index.py)
--------------------------------------------------------------------------------
5.1 site/pages/quarantine.html: nav as pages; <h1>Quarantine: terms not
    yet in Second Opinion</h1>; <p>{open_count} open terms, {resolved}
    resolved. Listed: terms seen at least twice.</p>; a table-free list
    <ol> of <li><strong>{term}</strong> -- guessed group {group_guess}
    -- seen {count_total} times in {books} -- first in "{district}" --
    <q>{example_quote}</q></li>; then "and {N} terms seen once (in the
    data file)" linking ../data/quarantine.json. Footer like pages (no
    disclaimer).
5.2 site/sitemap.xml: standard sitemap with <loc> entries built from a
    base URL read from index-text.json key "base_url" (default
    "https://www.strulovitz.org/2nd-opinion/"), for: index.html, the
    three A-Z pages, quarantine.html, viewer/index.html, and every
    pages/<slug>.html. If over 45,000 URLs, split into sitemap-1.xml
    ... with a sitemap index; not expected.
5.3 site/robots.txt:
      User-agent: *
      Allow: /
      Sitemap: https://www.strulovitz.org/2nd-opinion/sitemap.xml
    (Note: robots.txt is only honoured at a domain root; the main
    website's own robots.txt governs. This file is still written so the
    sitemap URL is discoverable, and the human may add the Sitemap line
    to the main website's robots.txt.)

6. PUBLISH PROCEDURE -- kitchen/publish.sh (CHEAP runs; human watches
   the first time)
--------------------------------------------------------------------------------
6.1 Content (exact; bash; stops on first error):
      #!/usr/bin/env bash
      set -euo pipefail
      cd "$(dirname "$0")/.."
      source .venv/bin/activate
      python kitchen/export.py
      python kitchen/build_pages.py
      python kitchen/build_index.py
      python kitchen/check_links.py
      big=$(find . -path ./.git -prune -o -type f -size +40M -print)
      if [ -n "$big" ]; then echo "FILES OVER 40MB:"; echo "$big"; exit 1; fi
      if git ls-files --error-unmatch kitchen/.env >/dev/null 2>&1; then echo ".env is tracked!"; exit 1; fi
      git add -A site data kitchen/logs/*.jsonl kitchen/logs/*-run.log kitchen/logs/*.md kitchen/prompts PROGRESS.md 2>/dev/null || true
      git commit -m "Publish $(date -Iseconds)" || echo "nothing to commit"
      git push
      python - <<'EOF'
      import json, subprocess, datetime, pathlib
      h = subprocess.check_output(["git","rev-parse","--short","HEAD"]).decode().strip()
      for p in ("site/data/build.json","data/export/build.json"):
          d = json.loads(pathlib.Path(p).read_text()); d["commit"] = h
          pathlib.Path(p).write_text(json.dumps(d, indent=1))
      EOF
      git add site/data/build.json data/export/build.json
      git commit -m "Build stamp $(git rev-parse --short HEAD)" || true
      git push
      echo "PUBLISHED $(date -Iseconds) $(git rev-parse --short HEAD)"
    chmod +x kitchen/publish.sh. (Note: the pages.jsonl/run.log/md
    patterns commit only the small logs the BIBLE allows; transcripts
    and extractions are gitignored anyway.)
6.2 On the serving computer (whichever currently runs the tunnel):
      cd <REPO> && git pull --ff-only
    If the serving computer is the laptop itself, the pull is a no-op.
    If it is the desktop: the human runs the pull (or a cron line, DEFAULT
    off: "*/30 * * * * cd <REPO> && git pull --ff-only >> /tmp/2nd-opinion-pull.log 2>&1";
    the human decides whether to enable it, recorded under DECISIONS BY
    HUMAN).
6.3 Nothing else is needed: site/ is static; the mount of Part 2
    section 8 serves whatever is in the clone.

7. THE TUNNEL CHECK (CHEAP; after every publish)
--------------------------------------------------------------------------------
7.1 Commands:
      curl -sI https://www.strulovitz.org/2nd-opinion/ | head -n 1              (expect 200)
      curl -s  https://www.strulovitz.org/2nd-opinion/data/build.json          (print)
      cat site/data/build.json                                                  (compare export_date)
      curl -sI https://www.strulovitz.org/2nd-opinion/viewer/index.html | head -n 1
      curl -sI https://www.strulovitz.org/2nd-opinion/pages/all-symptoms.html | head -n 1
      curl -s  https://www.strulovitz.org/2nd-opinion/ | grep -c "disclaimer"  (expect 1)
      curl -s  https://www.strulovitz.org/2nd-opinion/pages/all-symptoms.html | grep -c "disclaimer"  (expect 0)
    If the served export_date is older than the local one: the serving
    computer has not pulled. Tell the human which computer must pull.
    If 404 on /data/build.json but 200 on /: the web server does not
    serve .json or the mount points at an old copy; QUESTIONS FOR HUMAN
    with the outputs (Part 2 section 8.1 forbids changing server config
    without approval).
7.2 Cache: Cloudflare may cache static files for minutes. If build.json
    lags by less than one hour after a confirmed pull, wait; do not
    "fix" anything. The human may purge the Cloudflare cache in the
    Cloudflare dashboard if impatient.
7.3 EVIDENCE: the seven outputs pasted under DONE.

8. THE LIVE CHECKLIST (Checkpoint 9.1 -- "the project is live")
--------------------------------------------------------------------------------
  All lines true, with evidence under DONE, then the human says "live"
  and it is recorded under DECISIONS BY HUMAN:
   1. https://www.strulovitz.org/2nd-opinion/ returns 200 and shows the
      final index.html with the numbers block populated from ledger.json
      (not "not yet measured" everywhere) and exactly one disclaimer, at
      the bottom.
   2. The globe opens from the hero button on desktop and on the human's
      phone; Checkpoint 7.1 items 1-5 pass through the tunnel.
   3. At least one entity map through the tunnel shows at least one
      blue and one yellow light (i.e. the pilot or more of Phase B is
      loaded), and hovering shows a book and page number.
   4. Clicking that light's "Read the page" opens the entity's HTML
      page; its "Show me on the globe" returns to the viewer.
   5. The three A-Z pages open; the quarantine page opens; data/
      ledger.json, data/books.json and data/quarantine.json download.
   6. sitemap.xml returns 200 and lists more than 1,000 URLs.
   7. git ls-files | grep -c -E "\.pdf$|kitchen/pages/|kitchen/transcripts/|kitchen/.env" prints 0.
   8. The GitHub repository front page shows README.md with the live
      URL, the one-paragraph description from index-text.json
      "what_paragraphs"[0], the licence note, and a link to BIBLE/.
      (README.md is rewritten by build_index.py from those sources;
      it is the only README content.)
   9. PROGRESS.md CURRENT PHASE reads "LIVE since <date>; Phase B
      continuing: <k> of <N> books read"; NEXT STEP names the next book
      or the next BIBLE step.
  10. The five-minute audit of Part 8 section 7 passes.
  Being live does NOT mean finished. Phase B continues for months; each
  publish updates the numbers. The site is honest about this at every
  stage (section 4.2 items 6 and 7).

9. THE ROUTINE (CHEAP, forever; written into PROGRESS.md under
   STANDARD REBUILD, replacing Part 6's four lines)
--------------------------------------------------------------------------------
  STANDARD REBUILD AND PUBLISH:
    1. (if texts are stale) nohup python kitchen/write_texts.py > kitchen/logs/write-texts.log 2>&1 &
    2. bash kitchen/publish.sh
    3. on the serving computer: cd <REPO> && git pull --ff-only
    4. the tunnel check of section 7
    5. DONE entry with the publish.sh last line and the seven outputs
  Cadence (DEFAULT, human may change): after every Phase B book review
  approval; after every quarantine replay; after Freeze B; and at least
  once a week while any long run is active, so the public numbers never
  lag reality by more than a week.

10. SCRIPT LIST FOR THIS PART  [SMART writes; one session]
--------------------------------------------------------------------------------
  kitchen/export.py          section 1 (under 120 lines; imports the others)
  kitchen/ledger.py          section 3 (under 200 lines)
  kitchen/build_index.py     sections 4, 5, and README.md (under 250
                             lines; f-strings + html.escape, no
                             template library; creates index-text.json
                             with the defaults of 4.3 if absent)
  kitchen/publish.sh         section 6.1 exactly
  kitchen/prompts/index-text.json   created on first run; committed
  pages.css additions under "/* index */": .hero { text-align:center;
    padding:3em 1em 2em } .hero h1 { font-size:2.6em; margin:.2em 0 }
    .tag { font-size:1.2em; color:var(--muted); max-width:40em;
    margin:0 auto } .button { display:inline-block; margin-top:1em;
    padding:.7em 1.4em; background:var(--blue); color:#fff;
    border-radius:.4em; text-decoration:none; font-weight:700 }
    #start .big { display:grid; grid-template-columns:repeat(auto-fit,
    minmax(14em,1fr)); gap:1em } #start .big a { display:block;
    padding:1.2em; background:#fff; border:1px solid #ddd;
    border-radius:.5em; text-decoration:none; color:var(--ink);
    font-weight:600 } dl.numbers { display:grid; grid-template-columns:
    1fr auto; gap:.3em 1.5em } dl.numbers dt { color:var(--muted) }
    dl.numbers dd { margin:0; font-variant-numeric:tabular-nums;
    text-align:right } aside.sponsored { max-width:56em; margin:2em
    auto; padding:1em; border:3px dashed var(--yellow); background:
    #fffbe8 } .disclaimer { font-size:.95em; color:var(--ink);
    border-top:3px solid var(--yellow); padding-top:1em }
  SMART runs export.py once, build_index.py once, and opens the local
  preview (python3 -m http.server 8765 in site/) to confirm index.html
  renders, then hands to CHEAP for publish.sh.

11. DEFAULTS IN THIS PART THAT THE HUMAN MAY OVERTURN
--------------------------------------------------------------------------------
  (1) The default wording of index-text.json (4.3); edit the file.
  (2) Quarantine page shows count >= 2 only (5.1).
  (3) Publish cadence (section 9).
  (4) Desktop auto-pull cron OFF by default (6.2).
  (5) Percentages truncated, not rounded (3.3).
  (6) README.md generated from index-text.json (8.8).
  (7) Sponsorship box only on index.html, only if sponsor_note is set
      (Amendment 9.4).

================================================================================
HANDOFF CAPSULE (updated; paste into a NEW conversation with Fable when
asking for the next delivery)
================================================================================
Project: "Second Opinion", a medical knowledge globe built only from N
(up to 42) medical textbooks the human owns, vibe-coded, open source,
hosted at https://www.strulovitz.org/2nd-opinion/ from the human's own
computers via Cloudflare Tunnel, synced through
https://github.com/strulovitz/second-opinion (laptop = kitchen with
Neo4j; desktop serves static site/ only, pulls from GitHub). Fable
writes a 13-delivery BIBLE (9 parts + 4 appendix templates) in plain
text, one copy-paste block per delivery, no tables, no collapsibles.
ALL NINE PARTS DELIVERED: Part 1 charter (15 laws, world model: WHERE =
library geography from TOCs, WHICH = altitude one shell per entity;
diseases 0.30-0.98 by breadth, symptoms 1.02-1.50 by specificity,
treatments 1.52-2.98 in five heaviness sub-bands then class then name;
no single home; rigid; edges PRESENTS_WITH/TREATED_BY blue, HARMS
(subtype CONTRAINDICATED_IN)/LEADS_TO yellow, MISTAKEN_FOR grey;
F-scale 0-5; severity ring), Part 2 environment + Neo4j schema (Book:
book_id,title,edition,year,field_name,continent_id,page_count,
page_offset,index_image_start/end,image_name_pattern,status;
Territory: territory_id Cnn/Cnn.Pmm/Cnn.Pmm.Dkkk, level, name,
part_name, book_id, page_start/end, page_count, lat, lon,
area_fraction, seat_order, raster_code, colour_hex, bbox_px; Entity:
slug, group, canonical_name, aliases, aliases_text, abbreviations,
generic_names, brand_names, formulas, drug_class, drug_class_mentions,
class_verbatim, class_canonical, heaviness_group,
heaviness_confidence, created_from, created_book_id, frozen,
ordering_value, tie1, tie2, rank, altitude, altitude_status,
altitude_date, tldr, eli5, text_model, text_date, text_quote_count,
text_status; DISCUSSED_IN lit spots with book_id, page_number,
image_file, quote, reader_model, read_date, source; edges with
district_id, book_id, page_number, image_file, quote,
frequency_phrase, f_scale, numeric_pct, severity, severity_phrase,
subtype, reader_model, read_date, source, verify_status, quote_hash;
QuarantineTerm; Meta), Part 3 Phase A (books.json; geography.py;
index pipeline; Freeze A; data/registry/books.csv, territories.csv,
entities.csv, aliases.csv, stats.json), Part 4 Phase B (reading
pipeline; phase-b-ledger.json), Part 5 Phase C (altitudes; Freeze B;
data/registry/heaviness.csv, classes.csv; entities.csv gains altitude,
rank, ordering_value, tie1), Part 6 HTML pages, Part 7 viewer, Part 8
manager protocol (AGENTS.md, PROGRESS.md 14 headings, evidence format,
five-minute audit), Part 9 publishing (export.py orchestrator;
books.json, quarantine.json, ledger.json formats; build.json stamp;
index-text.json drives index.html with numbers block, quarantine page,
sitemap, robots, README; publish.sh; tunnel check; live checklist
Checkpoint 9.1; sponsor_note box; the ONLY disclaimer at the bottom of
index.html). Part 3 section 11.3 said the appendix .md files are short
descriptions pointing to the CSVs in data/registry/, with filling
instructions: Appendix A Field Registry (books -> continents),
Appendix B Territory Atlas, Appendix C Entity and Altitude Registry,
Appendix D Treatment Heaviness Groups and Classes. Tiers: READER =
free local Qwen 3.8 27B Q4_K_M (Gemma 4 31B substitute); CHEAP =
DeepSeek V4.1 Flash; SMART = Claude Sonnet 5.5 or GPT 6.1 Sol.
Next delivery requested: the appendix templates. Proposed: one answer
with Appendices A and B, one answer with Appendices C and D (each a
short plain-text template: purpose, the CSV it points to, column
definitions, how the manager fills the .md summary from the CSV, the
freeze rule, and a verification query per appendix).
================================================================================
