# NEXT SESSION PROMPT -- Second Opinion (written 4 Nov 2026 afternoon by Claude Opus 5.5 for itself)

## RESTART 4 Nov 2026 evening (READ THIS BLOCK FIRST, after the whole BIBLE)

BIBLE Part 0 section 13 (Nir corrected the world model) wins over everything below.
State: all pushed (fdbaaec), tree clean. Nothing of the build is started.
Nir's orders for this session: read the WHOLE BIBLE yourself; then BUILD, cheaply,
exactly as he planned; much code, little documentation (no long notes, no clerk work);
Nir is the eyes (never look at screenshots); grunt work -> give a short handoff to the
cheap model Nir switches to, then he switches back. Tell Nir in max 4 short lines
that you are ready, then wait for "go".

THE BUILD (replaces section 4 below where they differ):
1. Rough heights by code, seconds, no model. "Common" = number of chapters+books
   that mention the thing; the further from the Earth's centre, the more rare.
   Symptoms: air 1.02-1.50 (common low). Treatments: orbit 1.52-2.98 (common low).
   Diseases: ON the hexagons (surface; anchor = chapter discussing it most; lit =
   every chapter discussing it). Causes: underground (common deep, rare near the
   surface); a thing is a cause when a fact says "X causes disease Y" (X = cause).
2. data/golden/facts.json + kitchen/golden_load.py (Part 0 12.3; validate quotes
   verbatim against data/golden/sources/; F-scale/severity from Part 4 8.3/8.4;
   idempotent; SAME_CHEMICAL type).
3. Export site/data/golden.json + edges in entity files (kitchen/speed_export.py).
4. Viewer: site/viewer/paths.js; curved arrows with arrowheads in 2D and 3D; blue
   walk from a symptom, yellow walk from a treatment; disease = lit hexagon, symptom =
   cartoon cloud, treatment = cartoon satellite, cause = mark underground; hover/tap
   shows sentence + source; only the things on the walk are shown; NO glass planet
   for diseases. Keep each JS file under 400 lines; run kitchen/stamp_viewer.py.
5. Test with DEMO mode, text output only. 6. Enter the facts of section 6 (one short
   line each to Nir for approval), load, export, push.
Open for Nir: S003 "GM potatoes" is food, not one of the groups -- ask where it goes.

This file REPLACES NEXT-SESSION-PROMPT-2026-11-04.md and HANDOFF-2026-11-04-MORNING.md
(both deleted: they were wrong). READ THE WHOLE BIBLE FIRST (section 1), then this file.

## 0. What went wrong on 4 Nov morning (never repeat)

- The manager followed its own old plan file instead of Nir, built an automatic
  "connections from the books" pipeline with an OpenRouter model, compared model
  prices, and read the BIBLE through sub-agent summaries. All wrong. Deleted.
- Nir's words are COMMANDS, not suggestions. When two of his orders seem to clash
  (for example "read everything" and "save money"), ask ONE short question; never
  decide for him.
- Delete wrong work. Never mark it "not used".

## 1. Session start (do exactly this, nothing more)

1. FIRST read THE WHOLE BIBLE, YOURSELF, EVERY WORD, every file in BIBLE/
   (part-00 to part-09 and all appendix files). No sub-agent, no summaries, no
   skipping "to save money". Nir's order (4 Nov): saving by not reading is what
   made the manager dumb. Understanding the whole project comes first.
2. ONLY THEN read this file to the end (the small details and the current state).
3. Tell Nir in at most 6 short lines (with emojis, plain words) what the project
   is and what the next step is, so he sees you understand. Then wait for his
   "go". The next step is to BUILD THE WHOLE SYSTEM (section 4); the first five
   sources are already here (section 6). Do not ask him for an article.

## 2. The project in Nir's words (BIBLE Part 0 section 12)

- PURPOSE: show what the establishment hides: cascading side effects, better cures
  that are not approved (Cuba's CIMAvax-EGF for lung cancer), the same chemical
  sold elsewhere far cheaper. The core message: a "good" medicine causes something
  BAD. The arrow from the good thing to the bad thing is what visitors must see.
- THE BOOKS (37) = the establishment's view = ONLY the skeleton: 35,845 entities
  (symptoms 3,028, diseases 22,039, treatments 10,778), the chapters where each is
  discussed (2.4 M mentions), the globe geography. NO connections from the books.
- GOLDEN FACTS BY HAND: Nir gives an article (about 20 in total). The MANAGER reads
  it itself and writes each golden fact by hand into data/golden/facts.json
  (format: Part 0 section 12.3). No automatic reader, no API key, no upload page,
  nothing from the internet, ever. Then the website only DISPLAYS, automatically.
- WORDS: "connection" or "path", never "links" or "edges" to Nir. Never compare
  models, never show price tables.
- PATHS ARE CURVED ARROWS with arrowheads (2D and 3D). Lines are now REQUIRED
  (this overrides Part 1 section 3.6 and Part 7 A11).
- TWO WALKS, ONLY TWO INPUTS:
    BLUE walk, input = a SYMPTOM:      symptom -> disease -> treatment
    YELLOW walk, input = a TREATMENT:  treatment -> disease it CAUSES -> that
                                        disease's symptoms
  A disease is never an input (Nir: "there is no such thing"); it is only the
  middle. The end of one walk is the input of the other (yellow ends at a symptom
  -> click starts its blue walk; blue ends at a treatment -> click starts its
  yellow walk). The colour belongs to the walk, not to the stored fact.
- Thickness = frequency (F-scale, Part 4 section 8.3 table); dashed = frequency not
  stated; red glow = severity words (Part 4 section 8.4 list). Hover an arrow:
  verbatim sentence, source title, country, year, evidence strength.
- 3D: NOTHING MOVES, no flying, no camera animation. Arrows are DRAWN between the
  heights: from A's shell (A's altitude, above A's anchor tile) to B's shell,
  crossing the layers. Visitor turns the globe by hand.
- ONLY RELEVANT LAYERS: draw only the shells of the things on the current walk;
  hide all others; decoration (clouds, satellites, bands) stays faint.
- Treatment card: "Same chemical, other names and countries" with prices;
  "Approval" (where approved, where not).

## 3. Facts about the system you must know (checked 4 Nov afternoon)

- Neo4j: 35,845 Entity nodes; ZERO connections of any type; ZERO entities have an
  ALTITUDE (property does not exist). The 3D shells and 3D arrows NEED altitudes.
  This is the first real gap. Part 5 (provisional run, section 1.1) defines them:
  symptoms by number of districts (index proxy), diseases by number of books,
  treatments by heaviness group (P-C1, needs a model over 10,778 treatments) then
  class. ASK NIR how to do the treatment heaviness (options to state plainly:
  a measured trial with the local free model, or a code rule from drug-class words,
  or only the treatments that appear in golden facts get exact sub-band slots).
  Never run a model over thousands of items without a measured trial and Nir's
  okay (Part 8 D2b).
- Export: kitchen/speed_export.py (45 s) writes site/data/entities/<slug>.json,
  search.json, districts/. It hard-codes "edges": [] (line 43) and altitude None.
- Rebuild of entities: kitchen/speed_entities.py (6 min). Not needed for this work.
- Viewer: site/viewer/ (app.js 245, map2d.js 201, layers.js 164, globe3d.js 226,
  geo.js 126, ui.js 123, data.js 87 lines; each must stay under 400). layers.js
  already draws one entity shell at entity.altitude with lights (showShell);
  map2d.js is the 2D map (azimuthal equal-area, Part 0 section 6). After any
  viewer change run kitchen/stamp_viewer.py (cache busting).
- Tests (Part 7 A10): node --test kitchen/test_viewer.mjs;
  node kitchen/test_viewer_browser.mjs (writes screenshots: DO NOT open them;
  read only the pass/fail text; Nir is the eyes).
- Live site = ~/second-opinion/site through the symlink; it is live the moment it
  is pushed and pulled (Part 9 ADDITION E2-E3).
- Five calibre books still lack index links (HAZZARD-2022, IRWIN-RIPPE-2023,
  KAPLAN-11, ROCKWOOD-10, WILLIAMS-OBSTETRICS-26). Only if Nir brings an EPUB:
  unzip -p f.epub '*.xhtml' | grep -c 'id="page' (markers present?), then
  .venv/bin/python kitchen/epub_folios.py BOOK f.epub ; speed_entities.py ;
  speed_export.py ; copy EPUB to kitchen/books/<BOOK>-print-markers.epub.
  Do not raise this topic yourself.

## 4. The build, in order (one step at a time; Nir says "go" for each)

BUILD THE WHOLE SYSTEM FIRST (Nir, 4 Nov: "you are supposed to build the whole
system, the whole visual things"), then fill it with the golden facts of section 6.

Step 1. Altitudes for all 35,845 entities (Part 5, provisional run). Symptoms and
  diseases by code. Treatments: ask Nir the question of section 3 first.
Step 2. data/golden/facts.json (format Part 0 section 12.3) and
  kitchen/golden_load.py: validate (slugs exist or are in "new_entities",
  relation legal for the groups, quote non-empty and found verbatim in the saved
  source file), F-scale and severity from the Part 4 tables, load into Neo4j with
  source "article" (replace all source "article" relationships on each run, so it
  is idempotent). New relationship type SAME_CHEMICAL. Print counts (Law 11).
Step 3. Export: extend speed_export.py to write site/data/golden.json (every
  golden connection: from/to slug, names, groups, altitudes, anchor tile = the
  district where the books discuss the thing most, relation, quote, source, F,
  severity) and fill "edges" in the entity files.
Step 4. Viewer. New module site/viewer/paths.js: compute the walk from
  golden.json (blue from a symptom, yellow from a treatment, 2-3 steps), draw
  curved arrows in map2d.js (canvas Bezier + arrowhead) and in 3D (THREE curve +
  tube + cone arrowhead between shells), show only the shells on the walk, card
  text with arrows, sources, same chemical with prices, approval. Inputs are
  symptoms and treatments; ASK Nir before removing the Diseases tab.
Step 5. Test the display with the EXISTING DEMO mode (kitchen/make_demo.py,
  site/data/demo/; invented entities clearly labelled "DEMO", never in Neo4j,
  never in site/data/entities/). Text test output only; Nir looks with his eyes.
Step 6. Enter the real golden facts of section 6 (show Nir each fact as a short
  line first; he approves), golden_load.py, export, stamp_viewer.py, commit
  (show Nir the file list), push. Nir checks the live site.
Step 7. Forever after: Nir brings new articles (people will send him more). Each
  time: save the text verbatim as data/golden/sources/S0NN-<topic>.md, read it,
  show Nir the facts, he approves, add to facts.json, load, export, push.

## 5. Cost rules (Nir, repeated many times)

- No screenshots, ever. Nir is the eyes.
- Reading articles and entering golden facts = the manager (this is the precious
  part; do it carefully). Long dumb runs, babysitting, git chores = tell Nir
  "please switch to DeepSeek 4.1 Flash and say continue", give exact commands, a
  stop rule and what to report.
- One-shot code, no exploratory loops. Saving NEVER means skipping the BIBLE.
- Short chat replies with emojis; no emojis in files or commits.
- Honest: say what is missing. Do NOTHING until Nir explicitly says so.

## 6. The first five sources (given by Nir on 4 Nov 2026) and their golden facts

Saved verbatim in data/golden/sources/ (quotes must be copied from these files):
  S001-cimavax-ai-overview.md, S002-revlimid-ai-overview.md,
  S003-pusztai-ai-overview.md, S004-headache-pills-liver-ai-overview.md,
  S005-madhoney-chapter-04-pharma.md (Nir's own book Mad Honey, chapter 4).
NIR'S RULES FOR SOURCES: the "what science says today" parts are the
establishment's lies and are NOT entered. Each fact keeps plain facts about its
source (who, where, year, kind of study), never the establishment's verdict.
Nir's chapter itself states the project's purpose: "The only thing the industry
hid was the connection between the links. A hierarchical hive draws the arrows."

Facts drafted with Nir in chat (Nir saw each list; enter them in Step 6):
S001 CIMAvax: CIMAvax TREATS lung cancer (stage 4 / advanced non-small cell);
  approval "developed by Cuba's Center of Molecular Immunology; not FDA
  approved"; availability "US embargo bans import; patients travel through
  third countries"; mechanism: targets EGF, manages the cancer as chronic
  without chemo toxicity; US trials at Roswell Park, Buffalo NY.
S002 Revlimid: lenalidomide TREATS blood cancer; SAME_CHEMICAL Revlimid
  (brand) = generic lenalidomide made in India; price US brand $900-1,000 per
  pill, India generic $0.30-3.00 per pill; why: patents and market
  exclusivity, not chemistry; FDA approves generic lenalidomide and many Indian
  plants; availability: some Americans order via Canadian pharmacies routed to
  Indian makers.
S003 Pusztai: GM potatoes (snowdrop GNA lectin) HARMS -> thickened stomach and
  intestinal lining, stunted growth, suppressed immune system (rats, Pusztai,
  Rowett Institute, Scotland, 1998; partly published in The Lancet 1999; rats
  fed normal potatoes plus the same lectin were not affected); leaky gut
  (increased intestinal permeability) LEADS_TO inflammation and
  hypersensitivity / food allergy; celiac disease, severe stress, poor diet,
  microbiome imbalance LEADS_TO leaky gut; source card: Pusztai suspended, data
  confiscated, banned from speaking. OPEN QUESTION for Nir: GM potatoes / GM
  food is food, not one of the three groups; ask which group.
S004 Headache pills: acetaminophen (paracetamol, Tylenol) TREATS headache;
  acetaminophen HARMS acute liver injury / liver failure (severity "failure";
  in excess, with alcohol, long-term; NAPQI); note: alcohol makes lower doses
  harmful; note: acetaminophen is in more than 600 other medicines (hidden
  double dose); NSAIDs (ibuprofen, naproxen, aspirin) HARMS liver damage
  (heavy, chronic, daily use), stomach, kidneys; liver injury PRESENTS_WITH
  nausea or vomiting, right upper abdominal pain, jaundice, extreme fatigue,
  confusion. (A full yellow walk: pill -> liver injury -> its symptoms.)
S005 Mad Honey chapter 4 (Angles 2, 5, 6 carry the medical facts):
  - PRESCRIPTION CASCADE (6B, the showcase walk): statin -> new-onset type 2
    diabetes -> metformin -> gastrointestinal distress -> PPI -> vitamin B12
    deficiency, dementia workup, hip fracture -> opioids -> addiction.
  - acetaminophen HARMS acute liver failure ("nearly fifty percent of all
    reported cases" in the US; about 500 deaths a year); N-acetylcysteine
    TREATS acetaminophen poisoning ("the only effective antidote").
  - statins HARMS muscle pain and weakness (9-20%), loss of muscle mass and
    grip strength, memory loss and confusion, new-onset type 2 diabetes.
  - PPIs (Nexium, Prilosec, Prevacid) HARMS dementia (22-44% increased risk),
    vitamin B12 deficiency, hip/spine fractures, chronic kidney disease, acute
    kidney injury, hypomagnesemia, iron deficiency, C. difficile infection;
    B12 deficiency PRESENTS_WITH confusion, fatigue, memory problems.
  - SSRIs HARMS post-SSRI sexual dysfunction (PSSD: genital numbness, loss of
    libido, absent orgasm, erectile dysfunction, emotional blunting; 0.46% of
    males, 2023 study; can last 20+ years); approval note: label warnings EMA
    2019, Health Canada 2021, Australia TGA 2024, UK MHRA code; FDA none
    (2018 petition, Public Citizen lawsuit May 2024).
  - metformin HARMS gastrointestinal distress; OxyContin HARMS addiction
    (Purdue's "less than one percent" sales script).
  - Bt toxin and glyphosate in GM crops LEADS_TO leaky gut LEADS_TO food
    allergies: label exactly as Nir wrote it, "a hypothesis; I have not proven
    it".
  - high-dose intravenous vitamin C TREATS cancer (with chemotherapy; Pauling
    and Cameron 1970s; retried in oncology centers 2025); vitamin C TREATS
    common cold (Pauling 1970); omega-3 fish oil TREATS chronic inflammation,
    cardiovascular and cognitive health; exercise (45 minutes 3 times a week)
    and cognitive behavioral therapy TREATS mild to moderate depression
    (comparable to SSRIs).
  - CIMAvax extra: approved in Cuba 2011, Argentina, Colombia, Peru, Paraguay;
    indicated after first-line chemotherapy for advanced NSCLC; Roswell Park
    trials also with nivolumab. Vaxira: second Cuban therapeutic cancer
    vaccine, not FDA approved.
  - SAME_CHEMICAL Ozempic = semaglutide; India generics after the Indian patent
    expired 20 March 2026: Semanat (Natco), Semasize (Alkem), Noveltreat and
    Sematrinity (Sun Pharma), Obeda (Dr. Reddy's), $14-20 a month vs about
    $1,000 a month for US Ozempic; China generics (Huadong, CSPC) expected
    $15-30 a month.
  - zanubrutinib (Brukinsa, BeiGene) TREATS relapsed mantle cell lymphoma
    (alternative to ibrutinib / Imbruvica).
