================================================================================
SECOND OPINION -- THE BIBLE
PART 2 OF 13 -- ENVIRONMENT AND DATA MODEL
File: BIBLE/part-02-environment-and-data-model.md
MANAGER FOR THIS PART: CHEAP (DeepSeek V4.1 Flash)
================================================================================

0. PURPOSE AND RULES FOR THIS PART
--------------------------------------------------------------------------------
  This part makes the kitchen ready and defines where every piece of data
  lives. After this part is done, the following must be true and PROVEN:
  (a) every needed program and library is installed and recorded with its
  version; (b) the GitHub repository exists with the fixed layout;
  (c) the Neo4j database exists with the fixed schema; (d) a Python helper
  can talk to Neo4j; (e) a placeholder page is visible at
  https://www.strulovitz.org/2nd-opinion/ .
  Rules for the manager in this part:
  - Follow Law 13 (never assume what is installed) and Law 15 (when
    unclear, stop and ask) at every step.
  - Before ANY command that needs sudo, or any download larger than 1 GB,
    write the exact command in chat and wait for the human to say "yes".
  - Every section ends with "EVIDENCE": the exact commands whose output
    you paste into PROGRESS.md. Law 11: no evidence, not done.
  - Do not "improve" the schema, the file names, or the IDs. They are
    fixed. If something cannot work as written, STOP and ask.

1. ENVIRONMENT INVENTORY (do this first, change nothing yet)
--------------------------------------------------------------------------------
  Run every command below. Paste the full output of each into PROGRESS.md
  under the heading "ENVIRONMENT INVENTORY <date>". If a command says
  "command not found", that IS the result; record it. Do not install
  anything during the inventory.

  1.1 Operating system and hardware
    cat /etc/os-release
    uname -a
    nproc
    free -h
    df -h ~
    nvidia-smi
      (expected: an RTX 5090 with about 24 GB; if nvidia-smi is missing,
       record it and continue; the GPU is only needed by the reader's
       server, which the human runs himself)

  1.2 Python
    which python3; python3 --version
    python3 -m pip --version
    python3 -m venv --help > /dev/null && echo "venv OK" || echo "venv MISSING"
    python3 -c "import neo4j; print('neo4j driver', neo4j.__version__)"
    python3 -c "import networkx; print('networkx', networkx.__version__)"
    python3 -c "import matplotlib; print('matplotlib', matplotlib.__version__)"
    python3 -c "import numpy; print('numpy', numpy.__version__)"
    python3 -c "import scipy; print('scipy', scipy.__version__)"
    python3 -c "import PIL; print('pillow', PIL.__version__)"
    python3 -c "import requests; print('requests', requests.__version__)"
      (each may fail with ModuleNotFoundError; record which ones)

  1.3 Neo4j
    which neo4j; neo4j --version
    which cypher-shell; cypher-shell --version
    systemctl status neo4j --no-pager
    java -version
    ls /etc/neo4j/ 2>/dev/null
    ss -ltnp | grep -E '7474|7687'
      (7474 = Neo4j browser, 7687 = Bolt; if nothing listens, Neo4j is
       not running or not installed)

  1.4 Git and GitHub
    git --version
    git config --global user.name; git config --global user.email
    gh --version
    gh auth status
    ssh -T git@github.com 2>&1 | head -n 3

  1.5 Web serving on this computer
    systemctl list-units --type=service --state=running --no-pager | grep -Ei 'nginx|apache|httpd|caddy|lighttpd|cloudflared'
    which nginx apache2 caddy cloudflared
    cloudflared --version
    ls -la ~/.cloudflared/ 2>/dev/null; ls -la /etc/cloudflared/ 2>/dev/null
    cat ~/.cloudflared/config.yml 2>/dev/null; cat /etc/cloudflared/config.yml 2>/dev/null
      (the config shows which local port or folder the tunnel sends
       www.strulovitz.org to; record it; this tells us the web root)
    ls /etc/nginx/sites-enabled/ 2>/dev/null; cat /etc/nginx/sites-enabled/* 2>/dev/null
    ls /etc/apache2/sites-enabled/ 2>/dev/null; cat /etc/apache2/sites-enabled/* 2>/dev/null
    cat /etc/caddy/Caddyfile 2>/dev/null

  1.6 The existing website and its sub-projects
    From the output of 1.5, identify the WEB ROOT folder (the folder
    whose index.html is served at https://www.strulovitz.org/ ). Then:
    ls -la <WEB_ROOT>
    find <WEB_ROOT> -maxdepth 2 -name ".git" -type d
    find <WEB_ROOT> -maxdepth 1 -type l -exec ls -la {} \;
    cd <WEB_ROOT> && git remote -v 2>/dev/null
    Record HOW the existing sub-projects (for example AI Panorama) are
    mounted: (A) a sub-folder inside the main website's own git repo;
    (B) a symlink from the web root to a separate repo clone; (C) a
    nested git clone inside the web root; (D) something else. This
    decides section 8. If you cannot tell, STOP and ask the human.

  1.7 Local model servers (the reader's home)
    ss -ltnp | grep -E '11434|1234|8000|8080'
    curl -s http://localhost:11434/api/tags | head -c 600; echo
      (Ollama; lists downloaded models)
    curl -s http://localhost:1234/v1/models | head -c 600; echo
      (LM Studio's server, if its server is switched on)
    For Unsloth Studio: ask the human which port its OpenAI-compatible
    server listens on, or find it in the Unsloth Studio settings screen.
    Then: curl -s http://localhost:<PORT>/v1/models | head -c 600
    Record which servers answered and which model names they list.
    The reader pipeline (Part 4) will talk ONLY to an OpenAI-compatible
    endpoint (/v1/chat/completions), so any of the three servers can be
    used; the address goes into kitchen/.env (section 6.3). If none of
    the three answers right now, that is fine: record it; the human
    starts the server when Phase A begins.

  EVIDENCE for section 1: the whole PROGRESS.md block "ENVIRONMENT
  INVENTORY <date>" with raw outputs.

2. INSTALL WHAT IS MISSING
--------------------------------------------------------------------------------
  Only install what section 1 showed as missing. Record every install
  command and its result in PROGRESS.md under "INSTALLS <date>".

  2.1 System packages (need sudo: ask first)
    sudo apt update
    sudo apt install -y python3-venv python3-pip git curl
    If gh (GitHub CLI) is missing, install it following the official
    instructions at https://github.com/cli/cli/blob/trunk/docs/install_linux.md
    (Debian/Ubuntu apt repository). Then: gh auth login (the human types
    the browser code).

  2.2 Neo4j (if missing or not running)
    Neo4j Community Edition, installed as a Debian package from Neo4j's
    official apt repository, following the current official page
    https://neo4j.com/docs/operations-manual/current/installation/linux/debian/
    Requirements: a Java version matching the Neo4j version (the official
    page says which; currently Java 21 for Neo4j 5.x / 2025.x). Install
    the Java the page names, then neo4j. Ask before sudo.
    After install:
      sudo systemctl enable neo4j
      sudo systemctl start neo4j
      systemctl status neo4j --no-pager
    Set the password (first-run default user neo4j / password neo4j):
      cypher-shell -u neo4j -p neo4j
      and follow the prompt to set a new password, OR run
      sudo neo4j-admin dbms set-initial-password '<NEW_PASSWORD>'
      before the first start.
    The human chooses the password and tells you. You write it ONLY into
    kitchen/.env (section 6.3), never into any committed file, never
    into PROGRESS.md.
    Memory: the laptop has 64 GB. Optionally set in /etc/neo4j/neo4j.conf
      server.memory.heap.initial_size=4g
      server.memory.heap.max_size=4g
      server.memory.pagecache.size=4g
    then restart. This is optional; skip it if anything is unclear.
    Test: cypher-shell -u neo4j -p '<PASSWORD>' "RETURN 1 AS ok;"
    Expected output: a row with ok = 1.

  2.3 Python virtual environment and libraries (no sudo)
    All Python work uses one virtual environment inside the repository
    (created after section 4 clones the repo), path <REPO>/.venv, which
    is gitignored.
      cd <REPO>
      python3 -m venv .venv
      source .venv/bin/activate
      pip install --upgrade pip
      pip install neo4j networkx matplotlib numpy scipy pillow requests
      pip freeze > kitchen/requirements.txt
    Every script in kitchen/ is run as:
      cd <REPO> && source .venv/bin/activate && python kitchen/<script>.py
    Test:
      python -c "import neo4j, networkx, matplotlib, numpy, scipy, PIL, requests; print('all imports OK')"

  2.4 Not installed in this part
    No Node.js, no npm, no bundler. The viewer (Part 7) is plain HTML +
    JavaScript with its libraries vendored as files inside site/ (copied
    once, committed), so the website has no build step and works from any
    folder. No cloudflared changes: the tunnel already exists and already
    serves the main website; we only add a sub-folder (section 8).

  EVIDENCE for section 2: "INSTALLS <date>" block; the "RETURN 1" output;
  the "all imports OK" output; `pip freeze | wc -l`.

3. REPOSITORY CREATION
--------------------------------------------------------------------------------
  3.1 Create (public):
    gh repo create strulovitz/second-opinion --public --description "Second Opinion: a medical knowledge globe built only from textbooks. Open source." --confirm
    If gh cannot create it, STOP and ask the human to create the empty
    public repo "second-opinion" at https://github.com/strulovitz/ in the
    browser; then continue.
  3.2 Where to clone. The clone location depends on section 1.6:
    - Mount type (A) or (C): clone INSIDE the web root as
      <WEB_ROOT>/2nd-opinion-repo (the serving folder will be its site/
      sub-folder, see section 8).
    - Mount type (B): clone at ~/second-opinion and later symlink.
    - Unknown: clone at ~/second-opinion for now; mounting waits for the
      human's answer.
    git clone git@github.com:strulovitz/second-opinion.git <REPO>
  3.3 License (DEFAULT, human may overturn): file LICENSE containing the
    MIT License for the code, and a second file LICENSE-CONTENT.md stating
    that the generated texts and data in data/ and site/pages/ are released
    under Creative Commons Attribution 4.0 (CC BY 4.0), and that verbatim
    quotations from the textbooks are short excerpts cited for
    identification and verification and remain the copyright of their
    publishers.
  EVIDENCE: `gh repo view strulovitz/second-opinion --json url`, `git -C <REPO> remote -v`.

4. REPOSITORY LAYOUT (fixed)
--------------------------------------------------------------------------------
  Create exactly this tree. Folders that must exist but are empty get a
  file named .gitkeep so git keeps them.

  <REPO>/
    AGENTS.md              read by OpenCode every session (section 5)
    PROGRESS.md            the ledger (section 5)
    README.md              short public description + link to the site
    LICENSE                MIT
    LICENSE-CONTENT.md     CC BY 4.0 note
    .gitignore             section 4.1
    BIBLE/
      part-01-charter-and-world-model.md
      part-02-environment-and-data-model.md
      (parts 03..09 and appendix-A..D arrive later)
    kitchen/               Python scripts; small files only
      .env                 secrets (gitignored)
      .env.example         same keys, dummy values (committed)
      requirements.txt
      db.py                Neo4j helper (section 6.4)
      schema.cypher        the schema (section 6.2), applied once
      books/               PDFs            (gitignored)
      pages/<BOOK_ID>/     page images     (gitignored)
      transcripts/<BOOK_ID>/  full-page text from the reader (gitignored)
      extractions/<BOOK_ID>/  reader JSON per page (gitignored; loaded
                              into Neo4j, which is the source of truth)
      logs/                (gitignored)
    data/                  committed exports FROM Neo4j, small enough
      registry/            Appendix tables as CSV/JSON, frozen at Freeze
      export/              the viewer feed (section 7); regenerated by
                           script; committed
    site/                  the static website served at /2nd-opinion/
      index.html           main page; the ONLY place with the disclaimer
      viewer/              globe + maps (Part 7)
      pages/               one HTML file per entity (Part 6)
      assets/              css, vendored JS libraries, icons
      data/                a copy of data/export/ that the viewer loads
                           (the export script writes both)

  4.1 .gitignore (exact content)
    .venv/
    __pycache__/
    *.pyc
    kitchen/.env
    kitchen/books/
    kitchen/pages/
    kitchen/transcripts/
    kitchen/extractions/
    kitchen/logs/
    *.pdf
    *.png
    *.jpg
    *.jpeg
    *.tif
    *.tiff
    !site/assets/**/*.png
    !site/assets/**/*.jpg
    .DS_Store
    Thumbs.db

  4.2 Sizes. GitHub refuses files over 100 MB and complains over 50 MB.
    Nothing committed may exceed 50 MB. If an export file grows past
    50 MB, it is split per entity (section 7 already does this for the
    viewer feed). Check before each push:
      find <REPO> -path <REPO>/.git -prune -o -type f -size +40M -print
    Must print nothing.

  EVIDENCE: `cd <REPO> && find . -path ./.git -prune -o -print | sort`
  (the full tree), and `cat .gitignore`.

5. AGENTS.md AND PROGRESS.md (initial versions; Part 8 extends them)
--------------------------------------------------------------------------------
  5.1 AGENTS.md: create it now with this content, in this order:
    - Title line: "# Second Opinion -- standing orders for the manager"
    - Part 1 section 2 (the Fifteen Laws), copied verbatim.
    - Part 1 section 6 (the Glossary), copied verbatim.
    - Part 1 section 8 (Manager model routing), copied verbatim.
    - This closing paragraph, verbatim:
      "Before doing any task: open BIBLE/ and read the part that governs
      the current phase; then read PROGRESS.md; then continue from the
      first unfinished step. Never skip a step. Never substitute a
      technology. When unclear, write under QUESTIONS FOR HUMAN in
      PROGRESS.md and stop. Report every completed step with evidence."
  5.2 PROGRESS.md: create it now with these headings, in this order, and
    keep them forever (add entries under them; never delete history):
      # PROGRESS -- Second Opinion
      ## CURRENT PHASE
      ## NEXT STEP
      ## QUESTIONS FOR HUMAN
      ## BLOCKED
      ## LATER, IF MONEY
      ## ENVIRONMENT INVENTORY <date>
      ## INSTALLS <date>
      ## DECISIONS BY HUMAN
      ## DONE (newest first, each with evidence)
    "CURRENT PHASE" and "NEXT STEP" are each one or two lines, rewritten
    whenever they change. Everything else is appended.
  5.3 Record in "DECISIONS BY HUMAN" now: the human confirmed all seven
    defaults of Part 1 section 10, including the Indexes as the source of
    the entity registry, and the names second-opinion / 2nd-opinion.
  EVIDENCE: `wc -l AGENTS.md PROGRESS.md` and `head -n 30 AGENTS.md`.

6. THE DATA MODEL IN NEO4J
--------------------------------------------------------------------------------
  Why a graph database and not HTML files directly (for the human): HTML
  is for eyes. To build the website we must COUNT (how many diseases
  present with tiredness -> its altitude), SORT (heaviness order of
  drugs), DE-DUPLICATE (the same disease under three names), and FOLLOW
  CHAINS (pill -> liver disease -> its symptoms -> their pills). These
  are questions, and a database answers questions; a folder of HTML
  files cannot. HTML is generated LAST, from the answers.

  6.1 Node labels and properties
  (A) (:Book)  one per ingested book; 42 in total
      book_id          string, unique. Rule: the book's eponym or first
                       title word in UPPERCASE, hyphen, edition number.
                       Examples: HARRISON-22, BRAUNWALD-12. Appendix A
                       lists all 42. If a book has no edition number,
                       use the year: e.g. SOMEBOOK-2021.
      title            verbatim full title
      edition          string
      year             integer
      field_name       the field of medicine this book represents
                       (continent name), decided in Part 3
      continent_id     e.g. "C07"
      page_count       integer, number of page images
      page_offset      integer. printed_page = image_number - page_offset
                       for the main body (front matter with roman
                       numerals is below image_number = page_offset + 1).
                       Determined in Part 3.
      index_image_start, index_image_end   integers: the image numbers of
                       the back-of-book index (Part 3)
      image_name_pattern  e.g. "harrison-internal-medicine_Page_{n:04d}.png"
      status           one of: "candidate", "accepted", "rejected-duplicate",
                       "geography-done", "index-done", "reading", "read"

  (B) (:Territory)  continents, provinces, districts
      territory_id     string, unique: "C07", "C07.P02", "C07.P02.D020".
                       Province number Pmm: sequential in book order,
                       starting at P01. A book with no Part/Section level
                       uses the pseudo-province P00 for all its chapters.
                       District number Dkkk: the book's own chapter number
                       if the book numbers chapters; otherwise sequential
                       in book order, starting at D001.
      level            "continent" | "province" | "district"
      name             verbatim from the Table of Contents
      book_id          string
      page_start, page_end   printed page numbers (districts and
                       provinces); for continents: 1 and the last
                       printed page
      page_count       integer
      lat, lon         centre of the territory in degrees (Part 3)
      border_geojson   string: a GeoJSON Polygon of the border in
                       lon/lat degrees (Part 3). Stored as a string.
      area_fraction    float: fraction of the globe's surface
      seat_order       integer 1..42 for continents (the seating), null
                       for others
      Relationships:
        (district)-[:CHILD_OF]->(province)-[:CHILD_OF]->(continent)
        (continent)-[:REPRESENTS]->(book)

  (C) (:Entity)  one per symptom, disease or treatment
      slug             string, unique. See 6.5.
      group            "symptoms-and-signs" | "diseases-and-conditions"
                       | "treatments-and-drugs"
      canonical_name   display name, verbatim form chosen by the rules in
                       Part 3 (a label, not a home)
      aliases          list of strings, all verbatim variants seen
      aliases_text     the same list joined with " | " (for full-text
                       search)
      generic_names, brand_names, formulas   lists of strings, verbatim;
                       treatments only; empty lists otherwise
      created_from     "index" | "toc" | "page" | "manual-wikipedia"
      created_book_id  the book whose index/page first produced it
      frozen           boolean; false until the Freeze, then true
      ordering_value   float; the ordering key value computed in Part 5
                       (specificity count / breadth count / heaviness code)
      heaviness_group  treatments only: "lifestyle" | "otc" |
                       "prescription" | "biologic-chemo-radiation" |
                       "surgery-transplant"; null otherwise
      drug_class       treatments only: verbatim class name from the
                       books' pharmacology chapters, else null
      rank             integer, position inside its band (Part 5)
      altitude         float, the radius r (Part 5); null until then
      tldr             string, one or two sentences, AI-written (Part 6)
      eli5             string, a few paragraphs, AI-written (Part 6)
      text_model, text_date   which reader model wrote tldr/eli5, when
      Every Entity ALSO carries one of the secondary labels :Symptom,
      :Disease, :Treatment matching its group (convenience for queries).

  (D) Lit spots are RELATIONSHIPS, not nodes:
      (e:Entity)-[:DISCUSSED_IN]->(d:Territory {level:"district"})
      One relationship per proving page, with properties:
      book_id, page_number (printed), image_file, quote, reader_model,
      read_date, source ("index" | "page" | "manual-wikipedia").
      For index-derived lit spots (Part 3) the quote is the verbatim
      index line, e.g. "Scurvy, 2612-2613".

  (E) Edges between entities, five relationship types, with identical
      property sets:
      (a:Entity)-[:PRESENTS_WITH]->(b:Entity)   disease -> symptom
      (a:Entity)-[:TREATED_BY]->(b:Entity)      disease|symptom -> treatment
      (a:Entity)-[:HARMS]->(b:Entity)           treatment -> disease|symptom
      (a:Entity)-[:LEADS_TO]->(b:Entity)        disease -> disease
      (a:Entity)-[:MISTAKEN_FOR]->(b:Entity)    disease <-> disease; stored
                                                ONCE, from the
                                                alphabetically smaller slug
                                                to the larger; read as
                                                undirected
      Properties on each:
      district_id, book_id, page_number, image_file, quote,
      frequency_phrase   verbatim words from the sentence, or ""
      f_scale            integer 0..5 (Part 4 gives the mapping table)
      numeric_pct        float or null, if the book gave a number
      severity           boolean (Part 1, 3.7 e)
      severity_phrase    verbatim severity words or ""
      subtype            "CONTRAINDICATED_IN" for that case, else null
                         (HARMS only)
      reader_model, read_date, source
      One relationship per proving sentence. If three pages prove the
      same edge, there are three relationships. Aggregation (highest F
      wins) happens in the export (section 7), never by deleting.

  (F) (:QuarantineTerm)  terms the reader found on pages that match no
      frozen entity (Part 4)
      term, group_guess, book_id, district_id, page_number, image_file,
      quote, reader_model, read_date, resolved (boolean, default false)

  (G) (:Meta {key, value})  a few project-wide facts
      key "skeleton_frozen"  value "false" / "true"
      key "freeze_date"      value ISO date or ""
      key "schema_version"   value "2"

  6.2 schema.cypher (exact content; save as kitchen/schema.cypher, apply
      once with: cypher-shell -u neo4j -p '<PASSWORD>' -f kitchen/schema.cypher )

    CREATE CONSTRAINT book_id_unique IF NOT EXISTS
    FOR (b:Book) REQUIRE b.book_id IS UNIQUE;
    CREATE CONSTRAINT territory_id_unique IF NOT EXISTS
    FOR (t:Territory) REQUIRE t.territory_id IS UNIQUE;
    CREATE CONSTRAINT entity_slug_unique IF NOT EXISTS
    FOR (e:Entity) REQUIRE e.slug IS UNIQUE;
    CREATE CONSTRAINT meta_key_unique IF NOT EXISTS
    FOR (m:Meta) REQUIRE m.key IS UNIQUE;
    CREATE INDEX territory_level_idx IF NOT EXISTS
    FOR (t:Territory) ON (t.level);
    CREATE INDEX territory_book_idx IF NOT EXISTS
    FOR (t:Territory) ON (t.book_id);
    CREATE INDEX entity_group_idx IF NOT EXISTS
    FOR (e:Entity) ON (e.group);
    CREATE INDEX entity_name_idx IF NOT EXISTS
    FOR (e:Entity) ON (e.canonical_name);
    CREATE INDEX quarantine_term_idx IF NOT EXISTS
    FOR (q:QuarantineTerm) ON (q.term);
    CREATE FULLTEXT INDEX entity_fulltext IF NOT EXISTS
    FOR (e:Entity) ON EACH [e.canonical_name, e.aliases_text];
    MERGE (m1:Meta {key:"skeleton_frozen"}) SET m1.value = "false";
    MERGE (m2:Meta {key:"freeze_date"}) SET m2.value = "";
    MERGE (m3:Meta {key:"schema_version"}) SET m3.value = "2";

    Verification (paste the outputs into PROGRESS.md):
      cypher-shell -u neo4j -p '<PASSWORD>' "SHOW CONSTRAINTS;"
      cypher-shell -u neo4j -p '<PASSWORD>' "SHOW INDEXES;"
      cypher-shell -u neo4j -p '<PASSWORD>' "MATCH (m:Meta) RETURN m.key, m.value ORDER BY m.key;"
    Expected: 4 constraints, the indexes above (plus the ones Neo4j
    creates automatically for constraints), and 3 Meta rows.
    If any statement errors with a syntax message, do NOT rewrite it;
    record the exact error and the Neo4j version in QUESTIONS FOR HUMAN
    and stop.

  6.3 kitchen/.env (gitignored) and kitchen/.env.example (committed)
    Keys, one per line, KEY=value, no quotes:
      NEO4J_URI=bolt://localhost:7687
      NEO4J_USER=neo4j
      NEO4J_PASSWORD=<the real password only in .env>
      NEO4J_DATABASE=neo4j
      READER_BASE_URL=http://localhost:11434/v1
        (or http://localhost:1234/v1 for LM Studio, or Unsloth Studio's
         port; whichever server the human runs; must end with /v1)
      READER_MODEL=<the model name exactly as the server lists it>
      READER_VISION_MODEL=<same as READER_MODEL unless the human runs a
                           separate vision model>
      KITCHEN_ROOT=<absolute path of REPO>/kitchen
    .env.example has the same keys with values "CHANGE_ME".

  6.4 kitchen/db.py (exact content)

    # kitchen/db.py -- the only way scripts talk to Neo4j
    import os
    from pathlib import Path
    from neo4j import GraphDatabase

    def _load_env():
        env_path = Path(__file__).resolve().parent / ".env"
        if not env_path.exists():
            raise SystemExit("kitchen/.env is missing; see BIBLE part 2 section 6.3")
        for line in env_path.read_text().splitlines():
            line = line.strip()
            if line and not line.startswith("#") and "=" in line:
                key, value = line.split("=", 1)
                os.environ.setdefault(key.strip(), value.strip())

    _load_env()
    _driver = GraphDatabase.driver(
        os.environ["NEO4J_URI"],
        auth=(os.environ["NEO4J_USER"], os.environ["NEO4J_PASSWORD"]),
    )

    def run(cypher, **params):
        """Run one Cypher statement; return a list of dict rows."""
        db = os.environ.get("NEO4J_DATABASE", "neo4j")
        with _driver.session(database=db) as session:
            return [record.data() for record in session.run(cypher, **params)]

    def env(key, default=None):
        return os.environ.get(key, default)

    if __name__ == "__main__":
        print(run("RETURN 1 AS ok"))

    Test (from REPO with .venv active):
      python kitchen/db.py
    Expected: [{'ok': 1}]

  6.5 Slug rules (the Entity ID and the HTML file name; fixed forever
      after the Freeze)
    slug = group + "-" + slugify(canonical_name)
    slugify, in this exact order:
      1. Convert to Unicode NFKD and drop all non-ASCII marks
         (Sjögren -> Sjogren, Behçet -> Behcet, β -> remove or spell
         "beta" if the book spells it; keep the book's spelling).
      2. Lowercase.
      3. Remove apostrophes: Parkinson's -> parkinsons.
      4. Replace every run of characters that is not a-z or 0-9 with a
         single hyphen.
      5. Strip leading and trailing hyphens.
      6. If longer than 80 characters, cut at 80 and strip trailing
         hyphens.
    Examples:
      diseases-and-conditions-sjogren-disease
      diseases-and-conditions-parkinsons-disease
      symptoms-and-signs-fever
      treatments-and-drugs-paracetamol
      treatments-and-drugs-n-4-hydroxyphenyl-ethanamide   (a formula as
        an alias, never as the canonical name; canonical names are the
        book's common generic name)
    HTML file = site/pages/<slug>.html
    Collision: if two DIFFERENT entities produce the same slug, the
    second gets "-2" appended and the pair is written to QUESTIONS FOR
    HUMAN before the Freeze. After the Freeze no slug ever changes.
    Python reference (put in kitchen/slug.py):

    import re, unicodedata
    def slugify(name: str) -> str:
        s = unicodedata.normalize("NFKD", name)
        s = "".join(c for c in s if not unicodedata.combining(c))
        s = s.encode("ascii", "ignore").decode("ascii").lower()
        s = s.replace("'", "").replace("\u2019", "")
        s = re.sub(r"[^a-z0-9]+", "-", s).strip("-")
        return s[:80].rstrip("-")
    def slug(group: str, name: str) -> str:
        return f"{group}-{slugify(name)}"

  EVIDENCE for section 6: outputs of the three verification queries;
  `python kitchen/db.py`; `python -c "import sys; sys.path.insert(0,'kitchen'); from slug import slug; print(slug('diseases-and-conditions', \"Sjögren's Disease\"))"`
  which must print diseases-and-conditions-sjogrens-disease.

7. THE EXPORT FORMAT (what the viewer and the HTML pages are built from)
--------------------------------------------------------------------------------
  The export is written by one script (kitchen/export.py, given in Part 9)
  that reads Neo4j and writes identical copies to data/export/ and
  site/data/. Files are small JSON, one per entity, so no file approaches
  50 MB and the browser loads only what the user clicks.
  Files:
    geography.json      all territories: territory_id, level, name,
                        book_id, lat, lon, border (polygon), page_start,
                        page_end, area_fraction, parent territory_id,
                        seat_order
    books.json          the 42 books: book_id, title, edition, year,
                        field_name, continent_id, page_count
    search.json         every entity: slug, group, canonical_name,
                        aliases, altitude, rank, lit_spot_count,
                        edge_count (this is the Elevator's list)
    entities/<slug>.json
                        one entity in full: all Entity properties;
                        lit_spots: list of {district_id, book_id,
                        page_number, quote}; edges: list of aggregated
                        edges {relation, other_slug, other_name,
                        district_id, f_scale (highest), severity (any),
                        subtype, statements: [ {book_id, page_number,
                        quote, frequency_phrase, f_scale, numeric_pct} ]}
    quarantine.json     unresolved QuarantineTerm rows (published list)
    ledger.json         the honest numbers of Part 9 (pages read, entities,
                        edges, F0 share, quarantine size, dates)
  Direction note for the viewer: an edge is shown on BOTH entities' maps.
  On disease X's map, a PRESENTS_WITH edge to symptom Y is a blue circle
  labelled Y; on Y's map it is a blue circle labelled X. The export writes
  the edge into both entity files, with the field "direction" = "out" or
  "in" so the HTML page can choose the right phrase ("you may notice" /
  "caused by").

8. MOUNTING site/ AT https://www.strulovitz.org/2nd-opinion/
--------------------------------------------------------------------------------
  8.1 Do NOT change nginx/apache/caddy/cloudflared configuration unless
      the human approves a written proposal. First write in PROGRESS.md
      under "QUESTIONS FOR HUMAN" a short proposal based on section 1.6:
      - Mount type (A) (sub-folder of the main site's repo): propose
        adding a nested clone <WEB_ROOT>/2nd-opinion-repo and a symlink
        <WEB_ROOT>/2nd-opinion -> <WEB_ROOT>/2nd-opinion-repo/site, and
        adding "2nd-opinion-repo/" and "2nd-opinion" to the main site's
        .gitignore so the two repos never nest inside each other's
        history.
      - Mount type (B) (symlink): propose the symlink
        <WEB_ROOT>/2nd-opinion -> ~/second-opinion/site, done the same
        way as the existing symlinks. Check that the web server follows
        symlinks (nginx: it does by default; apache: needs
        "Options FollowSymLinks").
      - Mount type (C) (nested clone): propose the same as (A).
      Wait for "yes".
  8.2 After approval, do it, then create the placeholder site/index.html:
      a page titled "Second Opinion", one paragraph "Under construction.
      A medical knowledge globe built only from textbooks.", a link to
      the GitHub repository, and at the bottom the disclaimer paragraph
      (Law 12), exact text:
      "Second Opinion is not a doctor and is not medical advice. Its
       content was generated by AI models reading medical textbooks and
       may contain mistakes. It is offered for information only, as
       another angle to think about. Always verify with the cited book
       pages and with a qualified professional you trust."
      The human may edit this wording later; it lives in index.html only.
  8.3 Relative links only. Every link, script src and image src inside
      site/ is relative (for example "../assets/viewer.css", never
      "/2nd-opinion/assets/viewer.css" and never "https://..."). Then the
      same folder works at /2nd-opinion/ on the laptop, on the desktop,
      from a local preview, and from any future address.
  8.4 Local preview for testing without the tunnel:
      cd <REPO>/site && python3 -m http.server 8765
      then open http://localhost:8765/ in a browser.
  8.5 The second computer (Desktop PC, Linux Mint 22) only needs: git
      clone of this repo in the equivalent place, the same mount, and
      NO Neo4j, NO Python, NO reader: site/ is fully static. Neo4j lives
      only in the kitchen (the laptop). The desktop serves whatever was
      last pushed.
  EVIDENCE: `ls -la <WEB_ROOT>/2nd-opinion` (showing the symlink or
  folder); `curl -sI https://www.strulovitz.org/2nd-opinion/ | head -n 1`
  (must say 200); the human opens the URL in a phone browser and confirms.

9. FIRST COMMIT AND PUSH
--------------------------------------------------------------------------------
    cd <REPO>
    find . -path ./.git -prune -o -type f -size +40M -print     (must be empty)
    git status                                                   (no .env, no PDFs, no PNGs)
    git add -A
    git commit -m "Part 2: environment, layout, Neo4j schema, placeholder site"
    git push -u origin main
  If the default branch is "master", use that name consistently and
  record it in PROGRESS.md.
  EVIDENCE: `git log --oneline | head -n 3`; `git status` showing a clean
  tree; `gh repo view strulovitz/second-opinion --web` opened by the human.

10. CHECKPOINT 2 -- DEFINITION OF DONE FOR THIS PART
--------------------------------------------------------------------------------
  All ten lines below must be true, each with its evidence in PROGRESS.md
  under DONE:
   1. ENVIRONMENT INVENTORY block exists with raw outputs.
   2. Neo4j running; "RETURN 1 AS ok" returns 1.
   3. .venv exists; "all imports OK" printed; requirements.txt committed.
   4. Repository strulovitz/second-opinion exists, public, cloned.
   5. Layout of section 4 exists exactly; .gitignore exact.
   6. AGENTS.md and PROGRESS.md exist with the required content/headings.
   7. schema.cypher applied; SHOW CONSTRAINTS shows the 4 constraints;
      Meta has 3 rows.
   8. python kitchen/db.py prints [{'ok': 1}]; slug test prints
      diseases-and-conditions-sjogrens-disease.
   9. https://www.strulovitz.org/2nd-opinion/ returns 200 and shows the
      placeholder with the disclaimer at the bottom; confirmed on a phone.
  10. First commit pushed; no file over 40 MB; no secrets committed.
  Then set in PROGRESS.md: CURRENT PHASE = "Phase A (Part 3) not started";
  NEXT STEP = "Wait for BIBLE part 3".
  Any step that fails twice: write it under BLOCKED with the exact error
  and tell the human "HUMAN: please switch the model to SMART and say
  'continue'"; then stop.

================================================================================
HANDOFF CAPSULE (updated; the human pastes this into a NEW conversation
with Fable when asking for the next part)
================================================================================
Project: "Second Opinion", a medical knowledge globe built only from 42
medical textbooks the human owns, vibe-coded, open source, hosted at
https://www.strulovitz.org/2nd-opinion/ from the human's own computers
(laptop = kitchen with Neo4j; desktop serves static only) via Cloudflare
Tunnel, synced through https://github.com/strulovitz/second-opinion.
Fable writes a 13-delivery BIBLE (9 parts + 4 appendix templates) in
plain text, one copy-paste block per delivery, no tables, no
collapsibles, formulas in words plus LaTeX text. Delivered: Part 1
(charter, 15 laws, world model) and Part 2 (environment inventory and
installs, repo layout with kitchen/ data/ site/ BIBLE/, AGENTS.md and
PROGRESS.md headings, Neo4j schema: nodes Book, Territory (levels
continent/province/district, IDs Cnn / Cnn.Pmm / Cnn.Pmm.Dkkk, P00 for
books without parts), Entity (slug = group + slugify(name), secondary
labels Symptom/Disease/Treatment, altitude/rank/ordering_value/
heaviness_group/drug_class, tldr/eli5), QuarantineTerm, Meta; lit spots
as DISCUSSED_IN relationships; edges PRESENTS_WITH, TREATED_BY, HARMS
(subtype CONTRAINDICATED_IN), LEADS_TO, MISTAKEN_FOR (stored once,
smaller slug -> larger) each with provenance + frequency_phrase +
f_scale 0-5 + numeric_pct + severity; one relationship per proving
sentence, aggregation (highest F) only at export; kitchen/db.py helper,
kitchen/.env with NEO4J_* and READER_BASE_URL (OpenAI-compatible /v1)
+ READER_MODEL; export = geography.json, books.json, search.json,
entities/<slug>.json, quarantine.json, ledger.json written to
data/export/ and site/data/; all site links relative; placeholder
index.html with the single disclaimer). All Part 1 defaults confirmed
by the human (indexes as entity-registry source; district area ~ page
count; disease order by breadth; severity ring; highest-F wins; names
second-opinion / 2nd-opinion). World model: WHERE = library geography
from Tables of Contents (42 continents by Fibonacci sphere + spherical
Voronoi, provinces = book parts, districts = chapters); WHICH =
altitude, one shell per entity: diseases 0.30-1.00 by breadth (deep =
multisystem), symptoms 1.00-1.50 by specificity (low = nonspecific),
treatments 1.50-3.00 by heaviness (lifestyle -> OTC -> prescription ->
biologics/chemo/radiation -> surgery) with drug classes adjacent, every
drug its own shell. No single home (Law 8). Rigid layout. Viewer: 3-D
globe <-> 2-D equirectangular maps, lit circles only sized by F, blue
forward / yellow harm / grey differential, desktop + mobile. Tiers:
READER = free local Qwen 3.8 27B Q4_K_M (Gemma 4 31B substitute) does
all per-page/per-term work; CHEAP = DeepSeek V4.1 Flash; SMART = Claude
Sonnet 5.5 or GPT 6.1 Sol; manager says "HUMAN: please switch to <tier>"
and stops. Laws include: everything from the books only, provenance on
every claim, Neo4j single source of truth, cheap beats perfect, never
assume installed, when unclear stop and ask, one disclaimer only, no
multi-model editions, books/images/transcripts never committed.
Next delivery requested: Part 3 (Phase A -- Building the Skeleton:
geography from the 42 TOCs, entity registry from the Indexes,
duplicate-book rule, page_offset detection, Fibonacci/Voronoi
algorithm, review checkpoints, the Freeze).
================================================================================
