================================================================================
SECOND OPINION -- THE BIBLE
PART 5 OF 13 -- PHASE C: ALTITUDE ASSIGNMENT
File: BIBLE/part-05-phase-c-altitudes.md
MANAGER FOR THIS PART: CHEAP (DeepSeek V4.1 Flash) runs everything;
                       [SWITCH TO SMART] only for writing the five short
                       scripts of section 9 (one session) and for any
                       step that fails twice.
READER FOR THIS PART:  free local model, TEXT mode, for prompts P-C1 and
                       P-C2 only (treatments).
PRECONDITIONS:         Provisional run: Freeze A done (Part 3 sec. 11).
                       Final run (Freeze B): Checkpoint 4.2 done
                       (Harrison fully read) -- DEFAULT -- or
                       Checkpoint 4.3 if the human prefers.
================================================================================

0. PURPOSE AND AMENDMENTS
--------------------------------------------------------------------------------
0.1 Purpose
  Give every frozen Entity its rank inside its band and its radius r
  (the ALTITUDE), using the ordering keys the human decided in Part 1
  section 3.4: specificity for symptoms, breadth for diseases, heaviness
  + drug class for treatments. Then freeze the radii (Freeze B). After
  Freeze B a shell never moves; entities added later by the human
  (quarantine amendments) are INSERTED between existing shells without
  moving any (section 8).

0.2 What an altitude is, and is not (for the human and for Part 7)
  An altitude is a LAYOUT key, not a medical claim. "Tiredness sits low
  because it presents in 212 diseases in these books" is a statement
  about the books in Second Opinion, and the viewer shows it exactly
  like that: "presents in 212 diseases (counted in the books read so
  far)". It is never shown as "tiredness is nonspecific" as a bare
  medical statement.

0.3 BIBLE AMENDMENTS declared in this part
  AMENDMENT 5.1 (scope of Law 1 for layout keys only). The heaviness
    group of a treatment (lifestyle / otc / prescription / biologic-
    chemo-radiation / surgery-transplant) is decided by the reader from
    the book contexts; where the books do not say whether a drug is
    sold without prescription, the reader may use its own knowledge of
    the drug's usual status. This is permitted ONLY for this layout
    key, never for any displayed fact. The website labels the orbit
    grouping as "grouping decided by the reader model for layout" and
    never states "this drug is over-the-counter in your country".
  AMENDMENT 5.2 (adds to Part 2 section 6.1 C). Entity gets:
    tie1 (integer), tie2 (integer): tie-break counts (section 3);
    class_canonical (string, treatments only): the normalised class
    label (section 5); heaviness_confidence (float); altitude_status
    ("provisional" | "frozen" | "inserted"); altitude_date.
  AMENDMENT 5.3 (treatment sub-bands). The orbits band 1.50-3.00 is
    split into five equal sub-bands, one per heaviness group, so the
    groups are visibly separated on the globe (section 6.2).
  Everything else in Parts 1-4 stands.

0.4 Order of work
  Step C0  Keys for symptoms and diseases (Cypher)        (section 3)   CHEAP
  Step C1  Heaviness group per treatment, prompt P-C1      (section 4)   CHEAP runs, reader works
  Step C2  Class normalisation, prompt P-C2                (section 5)   CHEAP runs, reader works
  Step C3  Ranks and radii; write to Neo4j                 (section 6)   CHEAP
  Step C4  Review and Freeze B                             (section 7)   CHEAP + human
  Step C5  Insertion rule for later entities               (section 8)   CHEAP, whenever needed
  Scripts written once by SMART                            (section 9)

1. TWO MODES: PROVISIONAL AND FINAL
--------------------------------------------------------------------------------
1.1 PROVISIONAL (run immediately after Freeze A). Uses only the index
    lit spots (DISCUSSED_IN with source "index") that exist for all N
    books. Symptoms are ordered by their index proxy (distinct districts
    whose index pages mention them); diseases by breadth (distinct
    books); treatments by heaviness + class (P-C1 and P-C2 run now;
    their results are kept for the final run). Purpose: the viewer
    (Part 7) and the HTML pages (Part 6) can be built and tested on a
    complete globe while Phase B reads pages. altitude_status =
    "provisional". The site may be published in this state with the
    ledger (Part 9) saying so.
1.2 FINAL (Freeze B). DEFAULT: after Checkpoint 4.2 (Harrison fully
    read and reviewed). Human may instead choose Checkpoint 4.3 (all
    books read). Keys are recomputed with page data included
    (PRESENTS_WITH edges now exist). Treatments keep their P-C1/P-C2
    results unless the human changed them. Then Freeze B (section 7).
    After Freeze B, this part is never re-run in full; only section 8
    (insertion) runs.
1.3 Everything below describes the FINAL run; the provisional run is
    the same with the flag --provisional, which changes only the
    symptom key (3.1 note) and the altitude_status value.

2. BAND LIMITS (exact numbers used by the scripts)
--------------------------------------------------------------------------------
  Diseases   (planet body):  r_min = 0.30, r_max = 0.98
  Symptoms   (atmosphere):   r_min = 1.02, r_max = 1.50
  Treatments (orbits):       1.50-3.00 split into five sub-bands:
     lifestyle                 1.52 - 1.78
     otc                       1.82 - 2.08
     prescription              2.12 - 2.38
     biologic-chemo-radiation  2.42 - 2.68
     surgery-transplant        2.72 - 2.98
  (small gaps so that the surface r = 1.00 and the sub-band borders
   are never occupied by a shell; Part 7 draws thin guide spheres at
   1.00, 1.50, 1.80, 2.10, 2.40, 2.70, 3.00.)

3. STEP C0 -- KEYS FOR SYMPTOMS AND DISEASES (Cypher, run via db.run)
--------------------------------------------------------------------------------
3.1 Symptoms: specificity. ordering_value = number of DISTINCT Disease
    entities having a PRESENTS_WITH edge to the symptom (any book).
    tie1 = distinct districts where the symptom is DISCUSSED_IN (index
    or page). tie2 = distinct books. Rank 0 = LARGEST ordering_value
    (most diseases -> most nonspecific -> lowest altitude). Ties: larger
    tie1 first, then larger tie2, then canonical_name alphabetical.
    Note for --provisional: no PRESENTS_WITH edges exist yet, so
    ordering_value is set equal to tie1 (the index proxy) and tie1 to
    tie2.
      MATCH (s:Entity:Symptom)
      OPTIONAL MATCH (d:Entity:Disease)-[:PRESENTS_WITH]->(s)
      WITH s, count(DISTINCT d) AS diseases
      OPTIONAL MATCH (s)-[l:DISCUSSED_IN]->(t:Territory)
      WITH s, diseases, count(DISTINCT t) AS districts,
           count(DISTINCT l.book_id) AS books
      SET s.ordering_value = diseases, s.tie1 = districts, s.tie2 = books
      RETURN count(s) AS symptoms_keyed;
3.2 Diseases: breadth. ordering_value = number of DISTINCT book_ids
    across the disease's DISCUSSED_IN relationships AND its edges of
    any type. tie1 = distinct districts. Rank 0 = LARGEST breadth
    (deepest, r = 0.30). Ties: larger tie1 first, then alphabetical.
      MATCH (d:Entity:Disease)
      OPTIONAL MATCH (d)-[l:DISCUSSED_IN]->(t:Territory)
      WITH d, collect(DISTINCT l.book_id) AS lb, count(DISTINCT t) AS districts
      OPTIONAL MATCH (d)-[r:PRESENTS_WITH|TREATED_BY|HARMS|LEADS_TO|MISTAKEN_FOR]-(:Entity)
      WITH d, lb, districts, collect(DISTINCT r.book_id) AS eb
      WITH d, districts, [x IN lb + eb WHERE x IS NOT NULL] AS allb
      UNWIND (CASE WHEN size(allb) = 0 THEN [null] ELSE allb END) AS b
      WITH d, districts, count(DISTINCT b) AS books
      SET d.ordering_value = books, d.tie1 = districts, d.tie2 = 0
      RETURN count(d) AS diseases_keyed;
3.3 Verification (paste to PROGRESS.md):
      MATCH (s:Entity:Symptom) RETURN s.canonical_name, s.ordering_value, s.tie1
        ORDER BY s.ordering_value DESC, s.tie1 DESC LIMIT 15;
      MATCH (d:Entity:Disease) RETURN d.canonical_name, d.ordering_value, d.tie1
        ORDER BY d.ordering_value DESC, d.tie1 DESC LIMIT 15;
    Sanity expectation (not a rule): fever, pain, fatigue, dyspnea,
    nausea near the top of the symptom list; diabetes mellitus,
    hypertension, systemic lupus erythematosus, heart failure near the
    top of the disease list. If the lists look absurd (e.g. a rare
    eponym at the top), STOP and write QUESTIONS FOR HUMAN with the
    lists; do not "correct" the data.

4. STEP C1 -- HEAVINESS GROUP PER TREATMENT (reader prompt P-C1)
--------------------------------------------------------------------------------
4.1 Input per treatment (built by the script from Neo4j): canonical_name;
    aliases (up to 8); generic_names, brand_names (up to 5 each);
    drug_class and drug_class_mentions (verbatim, up to 6); names of up
    to 5 districts (with their book field) where it is DISCUSSED_IN; up
    to 3 verbatim quotes from its TREATED_BY or HARMS edges (if any).
    Batches of 15 treatments per call.
4.2 System message P-C1 (verbatim):

    You assign each medical treatment to exactly one HEAVINESS group,
    used only to order items in a visual layout. Output ONLY JSON:
    {"results":[{"slug":"<as given>","heaviness_group":"<lifestyle |
    otc | prescription | biologic-chemo-radiation | surgery-transplant>",
    "class_label":"<the drug or procedure class, chosen VERBATIM from
    the class mentions given, preferring the most complete form; if no
    class mention is given, a short class name the context supports;
    or empty string>","confidence":<0.0-1.0>,"reason":"<max 12 words>"}]}
    Group definitions (choose the FIRST that fits, top to bottom):
    surgery-transplant: any operation, resection, amputation, organ
      or tissue transplantation, implantation of a device (pacemaker,
      defibrillator, stent, joint prosthesis), percutaneous or
      catheter intervention, ablation, endoscopic therapeutic
      procedure.
    biologic-chemo-radiation: monoclonal antibodies and other
      biologics, cytotoxic chemotherapy, targeted cancer drugs,
      immunotherapy, cell and gene therapy, radiation therapy,
      radioactive isotopes, blood and blood-product transfusion,
      plasma exchange, intravenous immunoglobulin, dialysis,
      mechanical ventilation, extracorporeal support, other major
      procedures performed in hospital that are not operations.
    prescription: every other drug, vaccine, or medical gas that is
      normally given only on a clinician's order (antibiotics,
      antihypertensives, insulin, anticoagulants, antidepressants,
      oxygen, hormone therapy, inhalers), and minor clinic procedures
      (injections, wound care by clinicians, splinting).
    otc: medicines and products normally sold without a prescription
      in most countries (paracetamol/acetaminophen, ibuprofen, aspirin,
      antacids, oral antihistamines, oral rehydration solution,
      vitamins and mineral supplements, laxatives, antidiarrheals,
      topical antifungals and antiseptics, nicotine replacement,
      sunscreen, artificial tears). If the text says
      "over-the-counter" or "nonprescription", use this group.
    lifestyle: diet and nutrition changes, exercise, weight loss,
      smoking cessation (as behaviour), alcohol reduction, sleep
      hygiene, physiotherapy and rehabilitation exercises,
      psychotherapy and counselling, hydration, rest, avoidance of a
      trigger, positioning, compression stockings and similar
      self-applied measures.
    Rules: a drug class name (e.g. "ACE inhibitors") takes the group
    of its typical members. A drug available both OTC and by
    prescription goes to otc. If you cannot tell, choose prescription
    and set confidence below 0.5. Never leave heaviness_group empty.

4.3 User message: the batch as a JSON list of the inputs of 4.1. The
    script writes results into kitchen/logs/heaviness.jsonl (one line
    per slug; idempotent: slugs already present are skipped) and sets
    on the entity: heaviness_group, heaviness_confidence, and
    class_verbatim = class_label. Ledger: count per group; count with
    confidence < 0.5 (these go to the human review, section 7.1).

5. STEP C2 -- CLASS NORMALISATION (reader prompt P-C2)
--------------------------------------------------------------------------------
5.1 Why: the same class appears in many spellings ("ACE inhibitors",
    "angiotensin-converting enzyme inhibitors", "ACEIs"). Shells of the
    same class must be adjacent, so the spellings must be united under
    one class_canonical. This is done per heaviness group.
5.2 Script step first (no AI): collect all distinct class_verbatim
    strings in the group; unite strings equal after lowercasing,
    removing punctuation and the plural "s"; this gives clusters with
    one representative each (the longest form). Clusters whose strings
    all have fewer than 3 characters are kept as is.
5.3 Reader prompt P-C2, batches of up to 40 representatives. System
    message (verbatim):

    You are given a list of drug or procedure class names as written
    in medical textbooks. Group together names that denote the SAME
    class (synonyms, abbreviations, spelling variants). Do NOT group a
    class with its parent or child class (e.g. "beta blockers" and
    "antihypertensives" are different; "statins" and "lipid-lowering
    drugs" are different). Output ONLY JSON: {"groups":[{"canonical":
    "<choose the most complete form from the members, verbatim>",
    "members":["<every input string in this group, verbatim>"]}]}.
    Every input string must appear in exactly one group. A string with
    no synonym forms a group of one.

    The script checks the output covers every input exactly once; if
    not, re-asks once with the error appended; after a second failure
    the batch is kept ungrouped (each string its own class) and
    logged. Results -> kitchen/logs/classes.jsonl and on each entity:
    class_canonical. Treatments with empty class_verbatim get
    class_canonical = "(unclassified)".
5.4 Class ORDER inside a heaviness group: alphabetical by
    class_canonical, "(unclassified)" last. Inside a class:
    alphabetical by canonical_name. DEFAULT, human may overturn (for
    example to order classes by number of members).

6. STEP C3 -- RANKS AND RADII
--------------------------------------------------------------------------------
6.1 Ranking (Python sort, script assign_altitudes.py):
    Symptoms:   sort by (-ordering_value, -tie1, -tie2, canonical_name)
    Diseases:   sort by (-ordering_value, -tie1, canonical_name)
    Treatments: sort by (heaviness_order, class_canonical with
                "(unclassified)" forced last, canonical_name)
                where heaviness_order = lifestyle 0, otc 1,
                prescription 2, biologic-chemo-radiation 3,
                surgery-transplant 4.
    rank = position in the sorted list, counted from 0, separately per
    band (and, for treatments, the position is still global across the
    whole band; the sub-band formula below uses the position inside
    the sub-band).
6.2 Radius. For a band or sub-band with limits r_min, r_max holding n
    entities, the entity at position k (from 0) gets
      r_k = r_min + (r_max - r_min) * k / (n - 1)      if n >= 2
      r_k = (r_min + r_max) / 2                         if n = 1
    In LaTeX: $r_k = r_{\min} + (r_{\max}-r_{\min})\,\frac{k}{n-1}$ for
    $n \ge 2$, and $r_k = \tfrac{1}{2}(r_{\min}+r_{\max})$ for $n = 1$.
    A sub-band with n = 0 is simply empty.
6.3 Write to Neo4j (one UNWIND per band):
      UNWIND $rows AS row
      MATCH (e:Entity {slug: row.slug})
      SET e.rank = row.rank, e.altitude = row.altitude,
          e.altitude_status = $status, e.altitude_date = toString(date())
    with $status = "provisional" or "frozen".
6.4 Verification:
      MATCH (e:Entity) WHERE e.altitude IS NULL RETURN e.group, count(*);   -- must be empty
      MATCH (e:Entity) RETURN e.group, min(e.altitude), max(e.altitude), count(*) ORDER BY e.group;
      MATCH (e:Entity:Treatment) RETURN e.heaviness_group, min(e.altitude), max(e.altitude), count(*) ORDER BY min(e.altitude);
      MATCH (e:Entity) WITH e.altitude AS a, count(*) AS c WHERE c > 1 RETURN a, c LIMIT 5;   -- must be empty (altitudes unique)

7. STEP C4 -- REVIEW AND FREEZE B
--------------------------------------------------------------------------------
7.1 kitchen/review_altitudes.py writes kitchen/logs/altitude-review.md:
    (a) the 25 lowest and 25 highest symptoms with ordering_value, tie1;
    (b) the 25 deepest and 25 shallowest diseases with breadth, tie1;
    (c) per heaviness group: its count, 15 random members with
        class_canonical, and ALL members with heaviness_confidence
        < 0.5 (capped at 60 per group; the rest in a side file);
    (d) the 30 largest classes by member count, with their member
        counts, and 20 random classes of size 1 (to catch
        normalisation misses);
    (e) the counts of 6.4.
    The human answers: "ok"; or "move <slug> to <group>"; or "class
    <slug> = <class_canonical>"; or "merge classes <A> into <B>"; or
    "add rule: <text>" (appended to kitchen/prompts/additional-rules-
    P-C1.txt; only low-confidence items are re-asked, by default).
    Fixes are applied by Cypher, logged under DECISIONS BY HUMAN, and
    assign_altitudes.py is re-run (cheap: seconds). Repeat until "ok".
  CHECKPOINT 5.1 (provisional run): review approved; site may show
  provisional altitudes.
  CHECKPOINT 5.2 (final run): review approved after Phase B data.
7.2 Freeze B (after Checkpoint 5.2):
      MATCH (e:Entity) SET e.altitude_status = "frozen";
      MERGE (m:Meta {key:"altitudes_frozen"}) SET m.value = "true";
      MERGE (m2:Meta {key:"freeze_b_date"}) SET m2.value = toString(date());
    Export registries (export_registry.py, extended):
      data/registry/entities.csv   now with altitude, rank,
                                   ordering_value, tie1 filled
      data/registry/heaviness.csv  slug, canonical_name,
                                   heaviness_group, heaviness_confidence,
                                   class_verbatim, class_canonical
      data/registry/classes.csv    heaviness_group, class_canonical,
                                   member_count, members_verbatim_forms
    These are Appendix C (altitude columns) and Appendix D.
      git add -A && git commit -m "Freeze B: altitudes frozen"
      git tag -a altitude-freeze-B -m "Altitudes frozen"
      git push && git push --tags
7.3 After Freeze B: rank, altitude, heaviness_group, class_canonical of
    existing entities NEVER change. ordering_value and tie counts may
    be recomputed and displayed (they are facts about the books read)
    but they no longer affect position.

8. STEP C5 -- INSERTION RULE FOR ENTITIES ADDED AFTER FREEZE B
--------------------------------------------------------------------------------
8.1 When the human approves a new entity from quarantine (Part 4
    section 13.4), the script insert_altitude.py <slug> runs:
    (a) compute the entity's key as in section 3 (or P-C1/P-C2 for a
        treatment, single-item batch);
    (b) build the band's sorted list of FROZEN entities plus the new
        one, using the same sort as 6.1; find the new entity's
        neighbours below (slug_lo) and above (slug_hi) in the sort;
    (c) altitude = (altitude of slug_lo + altitude of slug_hi) / 2;
        if the new entity sorts first, altitude = r_min_of_band +
        (first frozen altitude - r_min_of_band) / 2; if last,
        symmetric with r_max;
    (d) rank = rank of slug_lo + 0.5 (a float; export sorts by rank);
        if several insertions land between the same neighbours, the
        altitude is halved again between the latest neighbours, so
        uniqueness holds;
    (e) altitude_status = "inserted"; logged under DECISIONS BY HUMAN
        with the two neighbours' names.
    No existing shell moves. Law 5 holds.

9. SCRIPT LIST FOR THIS PART  [SWITCH TO SMART for writing; CHEAP runs]
--------------------------------------------------------------------------------
  altitude_keys.py       [--provisional]   -> runs 3.1, 3.2, prints 3.3
  heaviness_classify.py                    -> P-C1 batches, heaviness.jsonl
  class_normalise.py                       -> 5.2 + P-C2, classes.jsonl
  assign_altitudes.py    [--provisional]   -> 6.1-6.4
  review_altitudes.py                      -> altitude-review.md
  insert_altitude.py     <slug>            -> section 8
  phase_c.py             [--provisional]   -> runs the first five in order
  prompts/P-C1.txt, P-C2.txt, additional-rules-P-C1.txt
  Each under 150 lines. Reference implementation of 6.2:

    # part of kitchen/assign_altitudes.py
    def radii(n, r_min, r_max):
        if n == 0:
            return []
        if n == 1:
            return [(r_min + r_max) / 2]
        return [r_min + (r_max - r_min) * k / (n - 1) for k in range(n)]
    SUBBANDS = {"lifestyle": (1.52, 1.78), "otc": (1.82, 2.08),
                "prescription": (2.12, 2.38),
                "biologic-chemo-radiation": (2.42, 2.68),
                "surgery-transplant": (2.72, 2.98)}
    HEAVINESS_ORDER = list(SUBBANDS)
    def treatment_rows(treatments):
        rows, rank = [], 0
        for g in HEAVINESS_ORDER:
            members = [t for t in treatments if t["heaviness_group"] == g]
            members.sort(key=lambda t: (t["class_canonical"] == "(unclassified)",
                                        t["class_canonical"].lower(), t["canonical_name"].lower()))
            for t, r in zip(members, radii(len(members), *SUBBANDS[g])):
                rows.append({"slug": t["slug"], "rank": rank, "altitude": r}); rank += 1
        return rows

10. DEFAULTS IN THIS PART THAT THE HUMAN MAY OVERTURN
--------------------------------------------------------------------------------
  (1) Freeze B after Checkpoint 4.2 (Harrison read), not after 4.3.
  (2) Band limits and the five equal treatment sub-bands (section 2).
  (3) Tie-break order for symptoms and diseases (section 3).
  (4) The heaviness group definitions, including dialysis and
      transfusion in biologic-chemo-radiation and percutaneous
      interventions in surgery-transplant (4.2).
  (5) Drugs available both OTC and by prescription -> otc (4.2).
  (6) Classes ordered alphabetically inside a heaviness group (5.4).
  (7) Insertion at the midpoint between neighbours (section 8).

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
(environment, repo layout kitchen/ data/ site/ BIBLE/, AGENTS.md +
PROGRESS.md, Neo4j schema: Book, Territory, Entity(+Symptom/Disease/
Treatment), QuarantineTerm, Meta; DISCUSSED_IN lit spots; edges
PRESENTS_WITH, TREATED_BY, HARMS(subtype CONTRAINDICATED_IN), LEADS_TO,
MISTAKEN_FOR with provenance, frequency_phrase, f_scale 0-5,
numeric_pct, severity, quote_hash; kitchen/db.py, reader.py; export =
geography.json, books.json, search.json, entities/<slug>.json,
quarantine.json, ledger.json written to data/export/ and site/data/),
Part 3 (Phase A: books.json; TOC -> provinces/districts; Fibonacci
sphere + Voronoi EQUAL-area continents with cluster seating; recursive
treemap split making district area ~ page count; 2048x1024
equirectangular district raster + continents_texture.png +
districts_lookup.json; Territory has raster_code, colour_hex, bbox_px,
lat, lon; index pipeline builds the entity registry with index lit
spots; Freeze A = geography + slugs/groups/names frozen, aliases may
grow), Part 4 (Phase B: text-first transcription, vision pass only for
figure/table pages, sliding window across pages inside a chapter,
extraction prompt P-B1, script-only quote verification, F-scale word
table, severity list, resolution against the frozen registry with
reader prompt P-B2, QuarantineTerm + replay file, idempotent loading,
pilot + full runs + reviews, phase-b-ledger.json), Part 5 (Phase C:
provisional altitudes right after Freeze A from index lit spots; final
Freeze B by default after Checkpoint 4.2; symptoms ordered by
specificity = distinct diseases with PRESENTS_WITH (ties: districts,
books, name), rank 0 = most diseases = lowest r; diseases by breadth =
distinct books across lit spots and edges (ties: districts, name), rank
0 = deepest r = 0.30; treatments by heaviness group from reader prompt
P-C1 (Amendment 5.1 allows reader knowledge for this layout key only)
then class_canonical from P-C2 normalisation then name; band limits
diseases 0.30-0.98, symptoms 1.02-1.50, treatment sub-bands lifestyle
1.52-1.78, otc 1.82-2.08, prescription 2.12-2.38, biologic-chemo-
radiation 2.42-2.68, surgery-transplant 2.72-2.98; radius r_k = r_min +
(r_max - r_min) k/(n-1); altitudes unique; Entity has rank, altitude,
altitude_status provisional/frozen/inserted, heaviness_group,
heaviness_confidence, class_verbatim, class_canonical, tie1, tie2;
insertion rule for post-freeze entities = midpoint between neighbours,
nothing moves; Appendix C altitude columns and Appendix D =
data/registry/heaviness.csv + classes.csv; tag altitude-freeze-B).
Viewer (Part 7, not yet written): 3-D globe with texture + faint guide
spheres at 1.00, 1.50, 1.80, 2.10, 2.40, 2.70, 3.00 <-> 2-D
equirectangular map, lit filled circles at district centres (ring when
several share a district) sized by F (F0 dashed), blue forward / yellow
harm / grey differential, severity red ring, hover shows other entity +
frequency phrase + book/page, click = cascade to that entity's map,
altitude elevator (three searchable lists), 2-D/3-D toggle, back to
globe, desktop + mobile, no build step, vendored JS, relative links.
Tiers: READER = free local Qwen 3.8 27B Q4_K_M (Gemma 4 31B substitute)
does all per-page/per-term work; CHEAP = DeepSeek V4.1 Flash runs
scripts; SMART = Claude Sonnet 5.5 or GPT 6.1 Sol writes scripts;
manager says "HUMAN: please switch to <tier>" and stops. Laws include:
books only, provenance always, Neo4j single source of truth, cheap
beats perfect, never assume installed, when unclear stop and ask, one
disclaimer only (site/index.html bottom), no multi-model editions,
books/images/transcripts never committed.
Next delivery requested: Part 6 (The HTML pages: one static page per
entity generated from entities/<slug>.json: title, aliases, group and
altitude line, TL;DR and ELI5 written by the free reader from the
entity's own verbatim quotes only (prompt P-D1), sections "you may
notice / caused by", "treated by / used for", "can cause / must not be
given in", "if untreated can lead to", "often mistaken for", each a
list of linked entities sorted by F with the frequency phrase, severity
marker and book+page citation, verbatim quotes block, "show me on the
globe" deep link, relative links only, mobile-friendly single CSS file,
generation script and idempotent regeneration, review sample).
================================================================================
