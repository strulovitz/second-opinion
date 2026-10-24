================================================================================
SECOND OPINION -- THE BIBLE
PART 8 OF 13 -- MANAGER OPERATING PROTOCOL
File: BIBLE/part-08-manager-operating-protocol.md
MANAGER FOR THIS PART: CHEAP (DeepSeek V4.1 Flash) installs the files of
                       sections 2 and 3 (copying, no judgement). Every
                       tier obeys the rest of this part at all times.
READER:                not used in this part.
PRECONDITION:          Part 2 done (repository exists). This part
                       REPLACES the initial AGENTS.md and PROGRESS.md of
                       Part 2 section 5 with their full versions; the
                       existing PROGRESS.md content is kept and moved
                       under the matching headings.
================================================================================

================================================================================
CLAUDE OPUS 5.5 ADDITION BEGIN -- PART 8 (written 24 Oct 2026)
THE STATE OF THE PROJECT AND EVERY STANDING DECISION
================================================================================
D0. WHY THIS BLOCK EXISTS (Nir, 24 Oct 2026)
  Nir: "nobody is reading (and everybody is changing) all the things except
  the BIBLE, so every piece of important information needs to be in the
  BIBLE". Therefore:
  - The BIBLE is the ONLY reliable source. PROGRESS.md, AGENTS.md, the
    HANDOFF-*.md files, HONEYCOMB.md, VIEWER.md, GEOGRAPHY.md and
    INDEX-PIPELINE.md are LOGS. If a log disagrees with the BIBLE, the
    BIBLE wins. If something important is only in a log, copy it into the
    BIBLE.
  - The BIBLE may be changed ONLY inside blocks marked
    "<MODEL NAME> ADDITION BEGIN -- PART n" ... "ADDITION END -- PART n",
    placed right after the part's header, recording what Nir decided and
    what was built. Never delete or rewrite the older text around a block.
    Inside its part, a block wins over the older text. A newer block wins
    over an older block.
  - AT THE END OF EVERY SESSION in which Nir decided something or something
    important was built, the manager writes it into the BIBLE this way
    (with the reason, exact numbers, exact commands and file names), BEFORE
    the Git save. A session that skips this has not finished.

D1. READING ORDER FOR A NEW MODEL
  1. AGENTS.md (the 15 laws; also Part 1 section 2).
  2. This block, then the ADDITION blocks of Parts 1, 3, 7 and 9.
  3. The part that governs the next step (D7 says which), all of it.
  4. Only then the newest PROGRESS.md entries, for detail.

D2. WHO DOES WHAT (in force on 24 Oct 2026)
  HUMAN: Nir. All decisions. Above the BIBLE.
  READER (free, local): Qwen "qwen3.8:27b" on this laptop's Ollama server,
    called only through kitchen/reader.py (test: .venv/bin/python
    kitchen/reader.py -> {'ok': True}). It reads every page and classifies
    every term. Never pay a cloud model for per-page or per-term work.
  CHEAP: DeepSeek V4.1 Flash in OpenCode. Runs the book-by-book scripts,
    one book at a time, with Nir watching.
  SMART: Claude (Opus 5.5 / Sonnet 5.5) or GPT 6.1 Sol. Writes GENERIC
    software only (Nir, 23 Oct: "processes that are book by book need to be
    done by deepseek. processes that are the heavy lifting of GENERIC
    programming need to be done by you."). Never babysits pages.
  Working rules from Nir: one book at a time; after each book STOP and
  report; nothing runs unattended; no parallel books; no overnight jobs; a
  book boundary is not a model switch; return to SMART only for the Freeze
  review or a generic software failure that DeepSeek failed twice (bring
  the exact command, error and evidence paths).

D3. HOW TO WORK WITH NIR
  Nir is a self-described beginner and has little money. One small step at
  a time, plain short words, explain before acting and wait for his
  "okay" on anything new. If unsure, say "I don't know" (Law 15). Emojis
  are wanted in CHAT replies only, never in files, commits or the BIBLE.
  Do not reopen closed topics: the table-of-contents work and the "are the
  PDFs complete books" question are closed (he does not want to hear about
  them). Save to GitHub at milestones and when he asks.

D4. EVERY AMENDMENT IN FORCE (short; the full texts are where named)
  3.1 equal-area continents        SUPERSEDED by 3.6 (geometry).
  3.2 border_geojson is null; borders come from the tiles (still true).
  3.3 THE LIBRARY IS 37 BOOKS, NOT 42. 42 files -> 39 after removing three
      byte-identical duplicates (Goodman & Gilman, Brenner & Rector,
      Bailey & Love) -> 37 after Law 6 (Bailey & Love lost to Sabiston;
      Marino's ICU Book lost to Irwin & Rippe). Records:
      data/registry/removed-books.json (sizes, SHA-256). kitchen/books.json
      is the single source of truth: 37 records, 130,457 pages. Wherever
      the BIBLE says "42 books", read "the 37 books".
  3.4 a chapter ends at max(own start, next start - 1); two chapters that
      start on the same page both include it.
  3.5 ring-built honeycomb (23 Oct)  SUPERSEDED by 3.6.
  3.6 the Goldberg ball, 4,812 tiles (Part 3 ADDITION block).
  5.3 the five treatment sub-bands 1.52-1.78, 1.82-2.08, 2.12-2.38,
      2.42-2.68, 2.72-2.98 (Part 5 section 2; used by the viewer).
  Part 7 ADDITION: flower 2-D map, Sand table / Atlas, layers, DEMO.
  TERRITORY NAMES (Nir, 15 Oct): a Part/Section/Chapter name keeps BOTH
      its number and its meaning in ONE name field, e.g. "Section V -
      Cardiac Radiology". A part printed without a title gets a short
      descriptive title written by the manager (name_source "written").
      A book printed with no parts at all gets parts written for it
      (groups of chapters with a covering title, in the style of the other
      books), never one big group.

D5. THE LIBRARY (37 books; continent ID, book ID, field, chapters)
  C01 HARRISON-22 Internal Medicine (general) 505 | C02 GRAY-2020 Anatomy 79
  C03 GUYTON-2026 Physiology 85 | C04 THOMPSON-2023 Genetics and Genomics 20
  C05 BRAUNWALD-12 Cardiology 102 | C06 MURRAY-7 Respiratory Medicine 142
  C07 SLEISENGER-11 Gastroenterology 132 | C08 BRENNER-11 Nephrology 71
  C09 KAPLAN-11 Psychiatry 60 | C10 ADAMS-12 Neurology 49
  C11 BENZON-2023 Pain Medicine 86 | C12 WILLIAMS-ENDO-2024 Endocrinology 48
  C13 KRAUSE-16 Nutrition 93 | C14 MANDELL-9 Infectious Diseases 210
  C15 MIDDLETON-2019 Allergy and Immunology 99 | C16 CAMPBELL-2020 Orthopaedic Surgery 90
  C17 DELISA-6 Rehabilitation Medicine 62 | C18 ROCKWOOD-10 Orthopaedic Trauma 69
  C19 BOLOGNIA-2024 Dermatology 161 | C20 FIRESTEIN-12 Rheumatology 125
  C21 NELSON-2024 Pediatrics 519 | C22 HAZZARD-2022 Geriatric Medicine 108
  C23 WILLIAMS-OBSTETRICS-26 Obstetrics 68 | C24 AVERY-2021 Neonatology 61
  C25 WILLIAMS-HEMATOLOGY-2021 Hematology 140 | C26 DEVITA-12 Oncology 107
  C27 OXFORD-6 Palliative Medicine 127 | C28 IRWIN-RIPPE-2023 Critical Care 215
  C29 ROSEN-2022 Emergency Medicine 208 | C30 GOODMAN-14 Pharmacology 78
  C31 STAHL-2024 Psychopharmacology 61 | C32 MILLER-10 Anesthesiology 87
  C33 YOUMANS-4 Neurosurgery 432 | C34 SABISTON-22 Surgery 92
  C35 GREEN-HAND-2021 Hand Surgery 60 | C36 BRANT-5 Radiology 83
  C37 ROBBINS-10 Pathology 29
  Totals: 37 continents, 534 provinces (C10.P02 is an empty heading kept
  with zero area), 4,763 chapter districts. The seating (which book sits
  next to which) was approved by Nir on 23 Oct ("i think it's ok").
  TABLES OF CONTENTS: COMPLETE (23 Oct). 27 books were checked page by
  page by the free reader (kitchen/eyes_folio.py): 24 clean, 3 with one
  recorded contents-vs-page finding each (HAZZARD-2022 ch7; NELSON-2024
  ch506, contents 2976 vs page 2975, duplicated pages in the PDF;
  SLEISENGER-11 ch4, contents 51 vs page 34). 10 books were accepted
  earlier without that check: YOUMANS-4, MANDELL-9, ROSEN-2022, MURRAY-7,
  MIDDLETON-2019, KRAUSE-16, SABISTON-22, CAMPBELL-2020 (rebuilt from its
  90 PDF chapter bookmarks), GOODMAN-14, ADAMS-12. CLOSED: do not reopen.

D6. THE SYSTEMS ON 24 OCT 2026
  Laptop (the KITCHEN): Debian 13, RTX 5090. Repository ~/second-opinion =
  https://github.com/strulovitz/second-opinion (public, branch main).
  Neo4j 2026.09.0 running; schema applied; only 3 Meta nodes;
  skeleton_frozen = "false"; no territories or entities loaded yet.
  Credentials only in kitchen/.env (gitignored; never print, copy or log).
  Python .venv 3.13.5; Node v26.7.0; Google Chrome 150; Three.js r186
  vendored. The PDFs live in kitchen/books/ and are never committed.
  Done: Phase A steps A0-A5 (books, duplicates, contents, page mapping,
  geography and seating), the Goldberg map (approved 24 Oct), the viewer
  (approved 24 Oct), the index-to-registry software (A6, tested on
  synthetic data and one real Harrison index page, PDF 4044).
  Not done: every medical datum. There are no entities, edges or
  altitudes yet; the viewer shows only the clearly labelled DEMO.

D7. WHAT COMES NEXT, IN ORDER (CHEAP + READER, Nir watching)
  Governing text: Part 3 sections 7-9. From ~/second-opinion:
  1. .venv/bin/python kitchen/reader.py                         {'ok': True}
  2. .venv/bin/python kitchen/index_pipeline.py HARRISON-22 --plan --limit 1
  3. .venv/bin/python kitchen/load_geography.py          (dry run), then
     .venv/bin/python kitchen/load_geography.py --apply  expect 37 books and
     5,334 territories (37 + 534 + 4,763). It loads the approved Goldberg
     coordinates; build.json records Nir's approval.
  4. Bounded trial, then look at the result WITH Nir:
     .venv/bin/python kitchen/index_parse.py HARRISON-22 --limit 1
     .venv/bin/python kitchen/index_classify.py HARRISON-22 --limit 1
     (one new index page; one batch of 25 terms). Harrison's index is PDF
     pages 4044-4273.
  5. .venv/bin/python kitchen/index_pipeline.py HARRISON-22
     .venv/bin/python kitchen/review_sample.py HARRISON-22
     Show kitchen/logs/HARRISON-22-review.md to Nir (Checkpoint 3.5).
  6. Only after Nir approves, with his actual words:
     .venv/bin/python kitchen/review_sample.py HARRISON-22 --approve "<his words>"
  7. The other 36 books, alphabetically, the same way, one at a time, each
     after the previous review is approved. For a book whose index is
     confirmed unusable, the --fallback route (Part 3 section 3.7.9).
     25 index ranges are configured; 12 are unset: find them with the
     reader, do not guess.
  8. After all reviews (Checkpoint 3.6): SMART for the entity-resolution
     and Freeze A review. Then Part 4 (reading pipeline, Phase B), Part 5
     (altitudes), Part 6 (pages), Part 9 (publishing). When the exports
     exist, Part 7 ADDITION A9 says how the viewer gets them (no code
     change).

D8. SAVING
  Commit messages start with the BIBLE section, e.g. "3.6 ...", "7.3 ...".
  Never commit PDFs, page images, transcripts, reader answers, .env,
  kitchen/logs/ or screenshots. Stage only the files you changed; show
  Nir what will be sent and how many files.
================================================================================
CLAUDE OPUS 5.5 ADDITION END -- PART 8
================================================================================

0. PURPOSE
--------------------------------------------------------------------------------
  The manager is honest but not brilliant, works in short sessions
  with no memory between them, and is paid per token. This part makes
  that safe: every session starts the same way, every claim of work
  comes with proof in a fixed format, every decision that is not in the
  BIBLE is asked, every file touched is committed, and the human can
  audit a session in five minutes without reading code. The human's
  bad experience in another project (a manager that silently did not
  use Neo4j and reported success) is exactly the failure this part
  exists to make impossible.

1. THE THREE DOCUMENTS AND WHO WRITES THEM
--------------------------------------------------------------------------------
  AGENTS.md    standing orders. Read automatically by OpenCode at every
               session start. Written ONCE from section 2; changed only
               by the human (or by Fable through the human).
  PROGRESS.md  the ledger. Written by the manager at every step, under
               fixed headings (section 3). Append-only except the two
               "pointer" headings. Never deleted, never rewritten.
  BIBLE/       the law for each phase. Read at the start of each
               session (the governing part) and before each step. Never
               edited by the manager; if the manager believes a BIBLE
               sentence is wrong, it writes that under QUESTIONS FOR
               HUMAN and continues with the sentence as written if
               possible, or stops if not.

2. AGENTS.md -- FULL CONTENT
--------------------------------------------------------------------------------
  The manager creates the file with EXACTLY the following structure.
  Where a line says COPY, it pastes the referenced BIBLE text verbatim
  (the Laws, Glossary and routing are already in BIBLE/part-01; copying
  keeps a single source of truth without retyping).

  --- begin AGENTS.md ---
  # Second Opinion -- standing orders for the manager

  You are the MANAGER of the project Second Opinion. You work inside
  OpenCode on the human's computer. You are one of three tiers: CHEAP
  (DeepSeek V4.1 Flash), SMART (Claude Sonnet 5.5 or GPT 6.1 Sol). A
  free local model called the READER does all per-page and per-term
  work through kitchen/reader.py; you never do that work yourself.

  ## The Fifteen Laws
  COPY BIBLE/part-01-charter-and-world-model.md section 2, verbatim.

  ## Glossary
  COPY BIBLE/part-01-charter-and-world-model.md section 6, verbatim.

  ## Manager model routing
  COPY BIBLE/part-01-charter-and-world-model.md section 8, verbatim.

  ## Session start ritual (do this before anything else, every session)
  1. Run: git status --short | head -n 20 ; git log --oneline -n 3
  2. Read PROGRESS.md sections CURRENT PHASE, NEXT STEP, QUESTIONS FOR
     HUMAN, BLOCKED. If QUESTIONS FOR HUMAN has an unanswered question,
     tell the human and stop unless the human answers now.
  3. Open the BIBLE part named in CURRENT PHASE. Read the section that
     contains NEXT STEP. Read the line "MANAGER FOR THIS PART". If your
     tier is not the one required for the next step, write "HUMAN:
     please switch the model to <tier> and say 'continue'" and stop.
  4. Write one line under PROGRESS.md "## SESSIONS": date, time, your
     model name, the step you are about to do.
  5. Then do exactly that step. Nothing else.

  ## Evidence format (Law 11)
  Every completed step is reported under "## DONE" in PROGRESS.md in
  this exact shape:
    ### <date> <BIBLE part>.<section> -- <step name> -- <model>
    COMMANDS: the exact commands or script names run
    OUTPUT: the raw output (or its first/last 20 lines if longer), in a
            code block
    FILES: the output of ls -la for files created or changed
    DB: the Cypher verification query and its result, when the step
        touched Neo4j
    COMMIT: the git commit hash
  A step without all applicable lines is not done. Never write "done",
  "populated", "works", "should work", "I verified" without the raw
  output next to it.

  ## Forbidden
  - Inventing a value, a rule, a file name, a schema field or a URL
    that the BIBLE does not give. Ask instead.
  - Replacing a technology named in the BIBLE (Neo4j, NetworkX,
    Matplotlib, Three.js, Canvas 2D, pdftotext, the OpenAI-compatible
    reader endpoint) with anything else, even "temporarily".
  - Writing to Neo4j, PROGRESS.md or git from code paths other than
    those the BIBLE describes.
  - Editing anything in BIBLE/.
  - Editing kitchen/books.json, data/registry/*, or any Entity slug,
    group, canonical_name, rank or altitude after the relevant Freeze.
  - Deleting data from Neo4j except through a BIBLE step or an explicit
    human instruction quoted in DECISIONS BY HUMAN.
  - Committing kitchen/.env, PDFs, page images, transcripts, or any
    file over 40 MB.
  - Doing per-page or per-term medical work (reading, classifying,
    extracting, writing TL;DR) yourself instead of through the reader.
  - Running sudo, downloading over 1 GB, or changing web-server or
    cloudflared configuration without the human's "yes" in chat.
  - Continuing past a mark "[SWITCH TO ...]" in the wrong tier.
  - Working on two steps at once, or "preparing" future steps.
  - Summarising the human's instruction into your own words and then
    following the summary. Follow the BIBLE text.

  ## When unclear, stuck, or failing
  First failure: retry once with the error read carefully. Second
  failure: write under "## BLOCKED" the step, the exact command, the
  full error, what you tried; then, if you are CHEAP, write "HUMAN:
  please switch the model to SMART and say 'continue'" and stop; if you
  are SMART, write the question under "## QUESTIONS FOR HUMAN" and
  stop. Never work around a failure by changing the plan.

  ## Git discipline
  Commit after every completed step with the message
  "<part>.<section> <step name>" and push. Before every commit:
    find . -path ./.git -prune -o -type f -size +40M -print   (must be empty)
    git status --short                                        (no .env, no *.pdf, no *.png outside site/assets)
  Never force-push. Never rewrite history. Never create branches
  unless the human asks.

  ## Before doing any task
  Open BIBLE/ and read the part that governs the current phase; then
  read PROGRESS.md; then continue from the first unfinished step. Never
  skip a step. Never substitute a technology. When unclear, write under
  QUESTIONS FOR HUMAN in PROGRESS.md and stop. Report every completed
  step with evidence.
  --- end AGENTS.md ---

3. PROGRESS.md -- FULL TEMPLATE
--------------------------------------------------------------------------------
  Headings, in this order, kept forever. The two POINTER headings
  (CURRENT PHASE, NEXT STEP) are rewritten in place; all others are
  APPENDED to, newest entry at the top of its section. Existing content
  from Part 2 is moved under the matching headings.

  --- begin PROGRESS.md ---
  # PROGRESS -- Second Opinion

  ## CURRENT PHASE
  <one line: "Part N (<title>) -- <phase name>", e.g. "Part 3 (Phase A) -- Step A6 index pipeline, book 7 of 42">

  ## NEXT STEP
  <one or two lines: the exact BIBLE section and step name; the tier required>

  ## QUESTIONS FOR HUMAN
  <each: "- [open] <date> <part.section>: <question>" ; when answered the manager changes [open] to [answered <date>] and copies the answer under DECISIONS BY HUMAN>

  ## BLOCKED
  <each: "- [open|resolved] <date> <part.section> <step>: command, error (first lines), tried">

  ## LATER, IF MONEY
  <each: "- <date> <part.section>: <the better solution we skipped and why>">

  ## DECISIONS BY HUMAN
  <each: "- <date> <part.section>: <the human's words, quoted>">

  ## STANDARD REBUILD
  (fixed text, from BIBLE part 6 section 11)
  python kitchen/write_texts.py   (nohup, optional)
  python kitchen/build_pages.py
  python kitchen/check_links.py
  git add -A site data && git commit -m "Rebuild <date>" && git push

  ## RUNNING NOW
  <each long run: "- <BOOK_ID or script> since <time>; log kitchen/logs/<file>; check with: tail -n 3 <log>" ; removed when finished and moved to DONE>

  ## SESSIONS
  <one line per session: "- <date> <time> <model>: <step started>">

  ## ENVIRONMENT INVENTORY <date>
  <raw outputs, Part 2 section 1>

  ## INSTALLS <date>
  <raw outputs, Part 2 section 2>

  ## DONE (newest first, each with evidence)
  <entries in the Evidence format of AGENTS.md>
  --- end PROGRESS.md ---

4. THE SESSION, STEP BY STEP (what a correct session looks like)
--------------------------------------------------------------------------------
4.1 Start: the ritual of AGENTS.md. Typical first message from the
    manager to the human, in full:
      "Session start. git clean at <hash>. CURRENT PHASE: Part 4 Phase
       B. NEXT STEP: 4.12.1 start full run HARRISON-22, tier CHEAP. I
       am DeepSeek V4.1 Flash. No open questions. Proceeding."
    If anything in that sentence cannot be filled, the session stops
    there with a question.
4.2 Work: exactly one BIBLE step. The manager quotes the step's
    section number in its messages. It runs the commands the BIBLE
    gives; where the BIBLE gives a script name, it runs that script; it
    does not rewrite the script to "make it work" without recording
    what it changed and why under DONE (and, if the change touches
    behaviour the BIBLE specifies, under QUESTIONS FOR HUMAN first).
4.3 Report: the DONE entry (Evidence format), the pointer headings
    updated, commit, push. Then the manager tells the human in chat
    the three lines: what was done, the commit hash, the next step and
    tier. Then it stops and waits. It never starts the next step in
    the same breath unless the human says "continue" or the BIBLE
    marks the steps as one batch.
4.4 Long runs (reader jobs that take hours): start with nohup exactly
    as the BIBLE gives, write the RUNNING NOW line, tell the human how
    to check (tail command), and END the session. The manager does not
    poll in chat: polling costs tokens for nothing. When the human
    returns and says the log is finished, the next session verifies
    the result (counts in Neo4j, ledger lines) and writes DONE.
4.5 Batches: a BIBLE step that is "the same thing for each book" is
    one DONE entry per book, not one per session necessarily; the
    manager may do several books in a session if each has its own
    DONE entry with evidence and its own commit.

5. EVIDENCE: ACCEPTABLE AND UNACCEPTABLE (examples the manager compares
   its own reports against)
--------------------------------------------------------------------------------
5.1 UNACCEPTABLE (each of these is a Law 11 violation):
    - "I have loaded the geography into Neo4j."  (no query, no count)
    - "The script ran successfully."  (no output shown)
    - "All 42 books processed."  (no per-book counts, no ledger lines)
    - "I tested the viewer and it works."  (no checklist items, no
      browser names, no screenshots named)
    - "I made a small improvement to the schema."  (schema is fixed;
      this is a violation of Forbidden, and the word "improvement"
      hides a substitution)
    - "Neo4j was not reachable so I stored the data in a JSON file for
      now."  (the exact failure this project forbids)
    - A DONE entry whose OUTPUT block was typed by the manager rather
      than pasted (tell-tale signs: round numbers, no timestamps, no
      warnings; the human may ask for the raw log file at any time).
5.2 ACCEPTABLE:
    ### 2026-10-14 3.8.1 -- load geography into Neo4j -- DeepSeek V4.1 Flash
    COMMANDS: source .venv/bin/activate && python kitchen/load_geography.py
    OUTPUT:
      books: 41 loaded (40 accepted, 1 rejected-duplicate)
      territories: 41 continents, 318 provinces, 3,912 districts
      CHILD_OF: 4,230  REPRESENTS: 41
    FILES: -rw-r--r-- 1 u u 6.1K Oct 14 21:03 kitchen/load_geography.py
    DB: MATCH (t:Territory) RETURN t.level, count(*) ORDER BY t.level;
        continent 41 / district 3912 / province 318
        MATCH (d:Territory {level:"district"}) WHERE NOT (d)-[:CHILD_OF]->() RETURN count(d);  -> 0
        MATCH (t:Territory {level:"district"}) RETURN sum(t.area_fraction);  -> 0.99999
    COMMIT: a3f9c21
5.3 The honest negative is ALWAYS acceptable:
    ### 2026-10-14 3.4.6 -- page_offset HARRISON-22 -- DeepSeek V4.1 Flash
    COMMANDS: python kitchen/page_offset.py HARRISON-22
    OUTPUT: candidates: ch1 -> 46, ch125 -> 46, ch250 -> 46, ch375 -> 47
    RESULT: NOT DONE. Candidates disagree (46,46,46,47). Per BIBLE 3.4.6
    this goes to QUESTIONS FOR HUMAN. Question written. Stopping.

6. THE MODEL-SWITCH PROCEDURE
--------------------------------------------------------------------------------
6.1 The BIBLE marks tiers per part and per step. When the next step
    requires another tier, the manager: updates NEXT STEP with the
    tier, commits, writes in chat exactly "HUMAN: please switch the
    model to <SMART|CHEAP> and say 'continue'", and stops.
6.2 The human switches the model in OpenCode and types "continue". The
    new model performs the session start ritual (it reads AGENTS.md
    automatically) and finds the step in NEXT STEP.
6.3 Rule of thumb when the BIBLE does not mark a step: writing or
    changing code = SMART; running given code, copying, vendoring,
    installing, git, filling ledgers = CHEAP; anything that failed
    twice in CHEAP = SMART.
6.4 SMART does not "finish off" CHEAP steps while it is active just
    because it can; it does its step, then hands back (tokens cost
    five times more). Exception: a SMART session that wrote a script
    runs that script ONCE on one unit (one page, one batch, one book's
    TOC) to prove it works; the full run is CHEAP.

7. THE HUMAN'S FIVE-MINUTE AUDIT (how to check a session without
   reading code)
--------------------------------------------------------------------------------
  Do these five things after any session you did not watch:
  1. git log --oneline -n 5 : one commit per step, messages naming
     part.section. No commit = nothing was done, whatever the chat
     said.
  2. Open PROGRESS.md, section DONE, top entry: are COMMANDS, OUTPUT,
     FILES, DB (if applicable), COMMIT all present and does the OUTPUT
     look pasted (timestamps, odd numbers)? If not, the step is not
     done.
  3. Run the one DB query from that entry yourself:
       cypher-shell -u neo4j -p '<password>' "<the query>"
     The number must match. (Takes ten seconds. This single check would
     have caught the "did not use Neo4j" failure.)
  4. Check QUESTIONS FOR HUMAN and BLOCKED for new [open] lines. Answer
     them (your answers go under DECISIONS BY HUMAN, written by the
     manager at the next session start).
  5. Check git status --short on the laptop: clean. And
     ls kitchen/.env is NOT in git: git ls-files | grep -c "kitchen/.env"
     must print 0.
  If any of the five fails, your next message to the manager is: "Audit
  failed on item <n>. Read AGENTS.md section Evidence format. Redo the
  last step with evidence." Do not accept explanations; accept evidence.

8. INSTALLING THIS PART (CHEAP; one session)
--------------------------------------------------------------------------------
8.1 Write AGENTS.md per section 2 (perform the three COPY operations
    with cat/sed or a tiny Python snippet that extracts the sections by
    their heading lines; verify with grep that the headings "LAW 1.",
    "LAW 15.", "CONTINENT", "QUARANTINE", "TIER FREE" and "TIER SMART"
    are present).
8.2 Rewrite PROGRESS.md per section 3, moving existing content under
    the matching headings; nothing is deleted. Add the first SESSIONS
    line.
8.3 Commit: "8.8 install manager operating protocol". Push.
8.4 EVIDENCE: wc -l AGENTS.md (expected 250-400 lines); grep -c "^## "
    PROGRESS.md (expected 14); git log --oneline -n 1.
  CHECKPOINT 8.1: the human opens AGENTS.md on GitHub and confirms the
  Laws are there verbatim. Recorded under DECISIONS BY HUMAN.

9. DEFAULTS IN THIS PART THAT THE HUMAN MAY OVERTURN
--------------------------------------------------------------------------------
  (1) One BIBLE step per session unless batching per book (4.3, 4.5).
  (2) Two failures before escalation (AGENTS.md "When unclear").
  (3) SMART runs a new script once on one unit, then hands to CHEAP (6.4).
  (4) The 40 MB pre-commit size check (git discipline).
  (5) The 14 PROGRESS.md headings (section 3).

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
LaTeX. Delivered: Part 1 (charter, 15 laws, world model: WHERE =
library geography, WHICH = altitude one shell per entity, no single
home, rigid layout, edges PRESENTS_WITH/TREATED_BY blue, HARMS(subtype
CONTRAINDICATED_IN)/LEADS_TO yellow, MISTAKEN_FOR grey, F-scale 0-5,
severity ring), Part 2 (environment, repo layout kitchen/ data/ site/
BIBLE/, Neo4j schema Book/Territory/Entity/QuarantineTerm/Meta,
DISCUSSED_IN lit spots, db.py, .env, tiers READER free local Qwen 3.8
27B / CHEAP DeepSeek V4.1 Flash / SMART Sonnet 5.5 or GPT 6.1 Sol),
Part 3 (Phase A geography.py Fibonacci+Voronoi equal-area continents,
treemap districts ~ page count, 2048x1024 raster + textures, index
pipeline, Freeze A, data/registry/*.csv = Appendices A-C), Part 4
(Phase B reading pipeline, quote verification, F-scale table,
quarantine, phase-b-ledger.json per book: pages planned/loaded/failed,
figure-pass pages, edges by type, unverified, quarantined, F0 share,
severity edges, quarantine open/resolved, aliases added, seconds),
Part 5 (Phase C altitudes, Freeze B, heaviness.csv + classes.csv =
Appendix D), Part 6 (export_entities.py -> site/data/entities/<slug>.json
+ search.json; write_texts.py P-D1; build_pages.py zero-JS pages;
check_links.py; wording.json; STANDARD REBUILD; hash routes #/globe,
#/map/<slug>, #/map/<slug>/3d, #/district/<id>), Part 7 (viewer:
Three.js vendored + Canvas 2D, export_districts.py ->
site/data/districts/<id>.json, continents_texture_2k.png,
site/data/wording.json, 11-item browser checklist, Checkpoint 7.1),
Part 8 (manager operating protocol: full AGENTS.md with Laws/Glossary/
routing copied from Part 1 + session start ritual + Evidence format
(COMMANDS/OUTPUT/FILES/DB/COMMIT) + Forbidden list + stuck procedure +
git discipline; full PROGRESS.md with 14 headings incl. STANDARD
REBUILD, RUNNING NOW, SESSIONS; one step per session; nohup long runs
end the session; model-switch procedure "HUMAN: please switch the model
to <tier> and say 'continue'"; the human's five-minute audit; Checkpoint
8.1). Part 2 section 7 planned the export files books.json,
quarantine.json, ledger.json and an orchestrating kitchen/export.py;
Part 6 Amendment 6.1 moved entities/search export to Part 6 and left
these three plus export.py for Part 9. site/index.html is a placeholder
with the ONLY disclaimer (exact text in Part 2 section 8.2). Laws
include: books only, provenance always, Neo4j single source of truth,
cheap beats perfect, never assume installed, when unclear stop and ask,
one disclaimer only, no multi-model editions, books/images/transcripts
never committed, report with evidence.
Next delivery requested: Part 9 (Publishing and the Quality Ledger:
kitchen/export.py orchestrator; books.json, quarantine.json,
ledger.json formats; the main page site/index.html final content
(intro, how to read the globe, the three entry points, the honest
numbers from ledger.json, the published quarantine list page, the
single disclaimer at the bottom, links to GitHub and to the BIBLE); the
publish procedure laptop -> GitHub -> desktop pull; the Cloudflare
Tunnel sanity check; what is measured and shown and what is never
hidden; sitemap and robots; Checkpoint 9.1; the "project is live"
definition).
================================================================================
