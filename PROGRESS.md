# PROGRESS -- Second Opinion

## CURRENT PHASE
Part 3 (Phase A -- Building the Skeleton) -- IN PROGRESS. Tier deviation recorded: BIBLE part 3 asks for [SWITCH TO SMART] on the writing steps, but the human has nobody to switch models with, so Space Bunny (the manager) executes every step itself, including the SMART ones.

DONE in part 3 so far: Step A0 (book intake), Step A1 (duplicate detection AND the human's decision -- the 5 redundant PDFs were deleted, leaving **37 books**), and the locator for Step A2 (TOC and Index page ranges).

**AMENDMENT 3.3 (declared by the manager, confirmed by the human on 2026-10-10):
THE LIBRARY IS 37 BOOKS, NOT 42.** The BIBLE was written before the PDFs
arrived and says "42" throughout. The BIBLE files are NEVER edited (that is a
standing project rule), so the correct number is declared here as an
amendment, exactly as BIBLE part 3 itself amends parts 1 and 2 (AMENDMENT 3.1
and 3.2). Wherever a later part says "42 books", read "the books", and use
the count in kitchen/books.json, which is the single source of truth: it
holds exactly 37 records, 130,457 pages.

Why 37, item by item, with the human's agreement:
  42 files -> 39 after removing 3 byte-identical duplicate pairs
  (sha256-proven: Goodman & Gilman, Brenner & Rector's Kidney,
  Bailey & Love) -> 37 after LAW 6 removed one book per same-field pair
  (Bailey & Love lost to Sabiston; Marino's ICU Book lost to Irwin & Rippe).
  The five deleted files, their sizes and their SHA-256 hashes are recorded
  forever in data/registry/removed-books.json. Nothing was silently dropped.
## NEXT STEP

**2026-10-22: BRAUNWALD-12 and BOLOGNIA-2024 were only half-books; both are now
COMPLETE (2,549 and 3,233 pages) and both TOCs are verified 102/102 and
161/161 by the eyes. AVERY-2021 (61/61), BENZON-2023 (86/86), BRANT-5 (83/83),
BRENNER-11 (71/71), DELISA-6 (62/62), DEVITA-12 (107/107), FIRESTEIN-12
(125/125), GRAY-2020 (79/79), GREEN-HAND-2021 (60/60), GUYTON-2026 (85/85),
HAZZARD-2022 (108/108, one TOC finding: ch7 outline says 284, the real
opener is 286), IRWIN-RIPPE-2023 (215/215) and KAPLAN-11 (60/60) are now
also done -- see the newest DONE entries. 9 books remain for the eyes. The
human still checks the OTHER PDFs himself for completeness.

One book at a time (the human's rule, 2026-10-22): after each book, stop and
report, so an interruption never leaves a long batch half-explained.**

**NEWEST HAND-OFF (read this first): `HANDOFF-2026-10-22-night.md`** -- the
full state at the end of 22 Oct: next book MILLER-10, the 9 books left, the
tool fixes and the TOC findings.

**READ FIRST: `HANDOFF-2026-10-19-evening.md`** (written at end of session
19 Oct, evening -- it WITHDRAWS the morning's "10 trusted books" claim and
describes the rewritten tool). Then `HANDOFF-2026-10-19-page-offset.md`
(morning), then `HANDOFF-2026-10-18-evening.md`.
Older: `HANDOFF-2026-10-16-evening.md`.

**SUPERSEDED 2026-10-16 (late).** The TOC prompts now tell the reader to
copy each heading EXACTLY as the book prints it (number kept if printed,
title kept if printed, nothing invented) -- done 2026-10-16 in
`kitchen/toc_vision.py` and `kitchen/toc_headings.py`.

**WILLIAMS-HEMATOLOGY-2021 is now read and CLEAN (DONE 2026-10-18 (f)).
Validator: 36/36 clean, 4,323 chapters -- every attempted book is clean.**
1 book remains: YOUMANS-4 (the last one). Ask Nir first, per the
one-book rule.
*** SUPERSEDED 2026-10-19: YOUMANS-4 was read that morning (432 chapters, 49
provinces, validator clean) and the library is 37/37 clean, 4,755 chapters.
The reading of the books is FINISHED. The unfinished step is now
`page_offset` / printed folio -- see `HANDOFF-2026-10-19-evening.md`. ***

**TWO PIPELINE FIXES landed with OXFORD-6 (2026-10-18), in
`kitchen/toc_vision.py` -- both protect every future book:**
1. `_rollback()` in `read_pages`: a thin page re-read at 220 dpi now
   also trims chapters that were appended to a province opened on an
   EARLIER page (before, only the province list was truncated, so the
   same chapters could be appended 2-3 times).
2. `parse()`: a bare "SECTION 8" plus a separate title field is joined
   into one name (Nir's number+meaning rule).
Also: when the model keeps printing a section banner BEFORE the trailing
chapters of the previous section (measured twice on OXFORD-6 page 9),
a recorded one-off regroups by the book's own rule "chapter N.M belongs
to SECTION N" -- see `kitchen/logs/OXFORD-6-regroup.py`.

**UNIFORMITY RULE (Nir, 2026-10-16): every book is treated the SAME way.**
No book gets an extra file, field or special case that the others do not
have. This is why GRAY-2020 got NO side file for its folded headings --
they stay only in the backup and in the book's own printed contents.

```bash
cd ~/second-opinion && source .venv/bin/activate
python kitchen/toc_validate.py --vis          # must stay 36/36, 4323
python kitchen/toc_fix_names.py <BOOK_ID>     # dry run first
python kitchen/toc_fix_names.py <BOOK_ID> --apply
```
Before ANY rebuild of a book, copy its `vis-toc.json` to a safe place:
`toc_reparse.py` has been proven capable of emptying a book.

Nothing is loaded into Neo4j until the validator is happy, which is
deliberate. `page_offset` (BIBLE part 3 section 4.6) is still NOT started
and every citation depends on it.

## QUESTIONS FOR HUMAN

### TO BE ASKED ONE AT A TIME, IN PLAIN WORDS, ON 2026-10-11

Nir's instruction: explain each one simply, one by one, and let HIM decide.
Do not offer a menu of unexplained options, and do not drop any book on our
own initiative -- every book here was hard to get.

1. **STAHL-2024** (The Prescriber's Guide, Children and Adolescents). Our
   tool expected a list of chapters on pages 66-67 and those pages were
   actually the drug entry for *aripiprazole*. We simply did not FIND a
   contents page; that is not proof that none exists. The book is organised
   one monograph per drug, so its structure is different from a normal
   textbook. NIR will open the book. QUESTION: is there a contents page, and
   roughly which page?
2. **ROSEN-2022** (Rosen's Emergency Medicine). The vision model said
   "image 3 is the contents"; image 3 is the COPYRIGHT page (publisher,
   ISBN, VOLUME 1). The model was wrong, and the reader then correctly
   refused to invent chapters from it. QUESTION: which page really shows the
   list of contents?
3. The other thirteen open books (BRADDOM-6, BRANT-5, GREEN-HAND-2021,
   HAZZARD-2022, IRWIN-RIPPE-2023, KAPLAN-11, MILLER-10,
   WILLIAMS-HEMATOLOGY-2021, BRAUNWALD-12, MANDELL-9, MURRAY-7,
   NELSON-2024, YOUMANS-4): where is the contents page?
4. If a book genuinely has no contents page, the choice is between using its
   structure differently (drug classes for Stahl, for example) or setting it
   aside. **Nir decides. Nothing is set aside without him.**

### Resolved earlier

### Q1 (2026-10-10) -- ANSWERED: the human said YES. The symlink below was created; see DONE 2026-10-10 (site mounted and live).


**Finding from the inventory (Part 2 section 1.6).** The web root of
www.strulovitz.org is `~/strulovitz-website/exports/`, served by Caddy
(`site-caddy.service`) on 127.0.0.1:8081, reached through the Cloudflare
Tunnel (`site-tunnel.service`). Apache is NOT involved and stays untouched.
The `exports/` folder already uses a symlink for its versioning
(`current -> v2026-10-10-a`), so a symlink is an established pattern here.
`exports/` is gitignored build output of the strulovitz-website repository.

**Proposal (recommended): one symlink, nothing else.**

```
ln -s ~/second-opinion/site ~/strulovitz-website/exports/2nd-opinion
```

Why this is enough and is the least invasive option:
- Caddy follows symlinks by default; the Caddyfile needs NO change.
- The Cloudflare Tunnel needs NO change.
- No sudo, no service restart, no risk to Apache or to the three existing
  sites (:8081 strulovitz, :8082 learnime, :8083 peak together).
- Because `exports/` is gitignored, the symlink never enters the
  strulovitz-website git history, so the two repositories never nest.
- Removal is one `rm` if the human ever wants it gone.

**Alternative if the human prefers an explicit Caddy rule** (requires editing
`~/strulovitz-website/hosting/Caddyfile`, which IS a committed file, and
reloading site-caddy):

```
handle /2nd-opinion/* {
    root * /home/nir/second-opinion
    rewrite * /site{uri}
    file_server
}
```

**Awaiting the human's yes. Nothing has been changed on the web server.**

## BLOCKED
- (nothing)

## AMENDMENTS DECLARED BY THE MANAGER
- AMENDMENT 3.1 (from BIBLE part 3): continents have equal area; page-count
  proportionality applies to provinces and districts inside each continent.
- AMENDMENT 3.2 (from BIBLE part 3): Territory.border_geojson is null for all
  territories; borders are raster pixels, with raster_code, colour_hex and
  bbox_px instead.
- AMENDMENT 3.3 (NEW, 2026-10-10): the library is **37 books, not 42**. See
  CURRENT PHASE for the full item-by-item reason. The BIBLE text is not
  edited.

## LATER, IF MONEY
- (nothing yet)

## ENVIRONMENT INVENTORY 2026-10-10

Raw output of the Part 2 section 1 inventory, run on the laptop BEFORE any install.

```
### 1.1 OS / HARDWARE
PRETTY_NAME="Debian GNU/Linux 13 (trixie)"
NAME="Debian GNU/Linux"
VERSION_ID="13"
Linux deb-server 6.12.94+deb13-amd64 #1 SMP PREEMPT_DYNAMIC Debian 6.12.94-1 (2026-06-20) x86_64 GNU/Linux
nproc: 24
               total        used        free      shared  buff/cache   available
Mem:            62Gi       5.3Gi        38Gi       734Mi        19Gi        56Gi
Swap:           61Gi          0B        61Gi
Filesystem      Size  Used Avail Use% Mounted on
/dev/sda4       1.8T  1.2T  463G  73% /
name, memory.total [MiB]
NVIDIA GeForce RTX 5090 Laptop GPU, 24463 MiB

### 1.2 PYTHON
/usr/bin/python3
Python 3.13.5
pip 25.1.1 from /usr/lib/python3/dist-packages/pip (python 3.13)
venv OK
neo4j MISSING
networkx 3.6.1
matplotlib MISSING
numpy 2.3.5
scipy MISSING
PIL 12.0.0
requests 2.32.3

### 1.3 NEO4J
openjdk version "21.0.12.1" 2026-08-18
/etc/neo4j
LISTEN 0      50     [::ffff:127.0.0.1]:7474             *:*   
LISTEN 0      4096   [::ffff:127.0.0.1]:7687             *:*   

### 1.4 GIT / GITHUB
git version 2.47.3
strulovitz
nir.strulovitz@gmail.com
gh version 2.97.0 (2026-07-31)
github.com
  ✓ Logged in to github.com account strulovitz (keyring)
  - Active account: true
  - Git operations protocol: https

### 1.5 WEB SERVING
  apache2.service               loaded active running The Apache HTTP Server
/home/nir/.local/bin/caddy
/usr/bin/cloudflared
caddyfile: ~/strulovitz-website/hosting/Caddyfile

### 1.6 WEB ROOT
total 968
drwxrwxr-x  5 nir nir   4096 Oct 10 15:26 .
drwxrwxr-x 17 nir nir   4096 Sep 28 20:09 ..
-rw-rw-r--  1 nir nir  18218 Oct 10 15:26 about.html
-rw-rw-r--  1 nir nir  18237 Oct 10 15:26 about-page-flux-2-max.html
-rw-rw-r--  1 nir nir  18469 Oct 10 15:26 about-page-gemini-3-pro-image.html
-rw-rw-r--  1 nir nir  18266 Oct 10 15:26 about-page-gpt-image-2.html
-rw-rw-r--  1 nir nir  18527 Oct 10 15:26 about-page-grok-imagine-image-2.html
origin	https://github.com/strulovitz/strulovitz-website.git (fetch)
origin	https://github.com/strulovitz/strulovitz-website.git (push)

### 1.7 LOCAL MODEL SERVERS
LISTEN 0      4096            127.0.0.1:11434      0.0.0.0:*   
qwen3.8:27b 17.7 GB
```

## INSTALLS 2026-10-10

```
$ sudo apt install -y openjdk-21-jre-headless
  openjdk version "21.0.12.1" 2026-08-18
  OpenJDK Runtime Environment (build 21.0.12.1+1-1-deb13u1-Debian)
  OpenJDK 64-Bit Server VM (build 21.0.12.1+1-1-deb13u1-Debian, mixed mode, sharing)

$ (added Neo4j official apt repo, per neo4j.com/docs/operations-manual/current/installation/linux/debian/)
$ sudo apt-get install -y neo4j=1:2026.09.0
  2026.09.0
  Cypher-Shell 2026.09.0

$ sudo neo4j-admin dbms set-initial-password <PASSWORD>   # password chosen by the human, never recorded here
$ sudo systemctl enable neo4j && sudo systemctl start neo4j
$ systemctl is-active neo4j
  active
$ cypher-shell -u neo4j -p <PASSWORD> "RETURN 1 AS ok;"
  ok
  1

$ cd ~/second-opinion && python3 -m venv .venv
$ .venv/bin/pip install neo4j networkx matplotlib numpy scipy pillow requests
  all imports OK
$ .venv/bin/pip freeze > kitchen/requirements.txt   # 20 packages
```

## DECISIONS BY HUMAN

- 2026-10-10: The human confirmed all seven Part 1 section 10 defaults, including "the Indexes are the source of the entity registry", and the names second-opinion (repo) / 2nd-opinion (URL).
- 2026-10-10: The human chose the Neo4j password himself and authorised its use. It is written ONLY into kitchen/.env (gitignored). It appears in no committed file and not in this ledger.
- 2026-10-10: The 42 PDFs were MOVED from ~/Downloads/books to ~/second-opinion/kitchen/books/ (no copies; the folder was emptied).
- 2026-10-10: Tier decision in force until end of October 2026: free models only for repetitive work; the MANAGER tier stays with Space Bunny.
- 2026-10-10: Three file pairs are byte-identical in size and are almost certainly duplicate books (Goodman & Gilman, Brenner & Rector, Bailey & Love). NOTHING was deleted. Part 3 applies the duplicate-book rule and the human makes the final choice.
- 2026-10-15: **MEANINGFUL TERRITORY NAMES (amendment to the province rule).** Nir's words: "i am interested in the meaning i am not interested in the number." Every heading level (Part/Section/Unit/Volume/chapter) keeps ONLY its meaningful title, never the numbering ("SECTION V CARDIAC RADIOLOGY" -> "Cardiac Radiology"). When a book prints "PART 3" with no title: first look on the part's opening page; if nothing, the manager WRITES a short descriptive name from the chapters inside, marked "name_source": "written". Full plan in HANDOFF-meaningful-names.md. This supersedes the immediate "read the next 15 books" step until the 22 already-read books are fixed and the TOC prompts are changed. **Same day, evening: SUPERSEDED by the entry below.**
- 2026-10-15 (evening): **TERRITORY NAMES = NUMBER + MEANING TOGETHER (Nir's final rule, supersedes the entry above).** Nir's words: "i want to do BOTH the entity (entity is 'part' or 'chapter' etc) and the entity's number, AND the entity's meaning (if it does not have a written meaning in the book (title) then you write a short and descriptive meaning/title by yourself)... it is NOT elegant, the elegant solution would have been to design the database better and to make 2 separate fields... but i do not want to change the structure of the database which is in the BIBLE." So: "SECTION V CARDIAC RADIOLOGY" -> name = "Section V - Cardiac Radiology" (number kept, meaning added). Books that print "PART 3" with no title: look on the part's opening page; if nothing, WRITE a short descriptive name, marked "name_source": "written". ONE name field in the existing schema holds the combined string — the database structure is NOT changed. The GOOD books already reading "PART 2 Cardinal Manifestations..." are in the target form: do not strip their numbers. The TOC prompts must ask for BOTH the numbering and the title. Full plan in HANDOFF-meaningful-names.md.
- 2026-10-15 (late evening): **FOR A BOOK WITH NO PARTS AT ALL, WRITE THE PARTS THE AUTHOR LEFT OUT.** Nir's words: "in books that have NO parts at a ll, please try to create such 'parts' for them, like, please group the chapters (assuming like that there are more than a handful of chapters), like the first few chapters, and give them a proper title that will contain all of them, and then the next few chapters and group them with another title, and so on please. please do the work that the author should have done. as much as you can, similar to other books. like try to imitate the style of other books (where the author DID do a proper job) please. it's a lot better than 1 big group." So a flat book is NOT left as one province called "ALL". The chapters are grouped and each group is given a written title covering every chapter in it, in the same style as the books that printed theirs. Every such province carries `name_source: "written"` so the database can always tell a printed part from a part we wrote (Law 2). The grouping itself is a HUMAN decision and lives in `kitchen/parts/<BOOK>.json`; the script only applies it.

## DONE (newest first, each with evidence)

### DONE 2026-10-22 -- KAPLAN-11 read by the eyes: 60/60, 0 unresolved, 0 disagreements

16,525 PDF pages (the largest PDF in the library), 2 volumes, 60 chapters.
No printed folio the reader can see, so all 60 are "pdf-page": the number is
the PDF page. Clean on the first pass -- no tool change needed; the divider
rule added for IRWIN-RIPPE-2023 also covers this book.

    .venv/bin/python kitchen/eyes_folio.py KAPLAN-11 --all --scan 6
      60/60 chapters read by the eyes; 0 unresolved
      0 disagree with the book's own contents
    kitchen/logs/KAPLAN-11-toc.json  2 provinces (Volume I 26, Volume II 34), 60 chapters

### DONE 2026-10-22 -- IRWIN-RIPPE-2023 read by the eyes: 215/215, 0 unresolved, 0 disagreements

7,992 PDF pages, 20 provinces, 215 chapters. The pages print no folio the
reader can see, so all 215 are "pdf-page" (the number is the PDF page). The
first pass placed 213 and made one plain mistake:

- ch167 and ch184: the link points at a divider page that says only
  "Chapter 167" / "Chapter 184" -- the title is on the NEXT page -- so the
  opener test (which wants title words) rejected the linked page;
- ch185: it was accepted on pdf 95, a front-matter list that mentions
  "Chapter 185" and the title inside a paragraph (KIND=OTHER). It was the
  image-field fallback, and it beat the real linked page.

Fixed in `kitchen/eyes_folio.py` with one helper, `pdf_page_matches()`, used
by BOTH the pointer and the scan loops: accept a page if the reader calls it
OPENING with a matching heading, OR if its heading starts with "Chapter N"
(a divider). A contents listing is KIND=OTHER and is no longer accepted.

    .venv/bin/python kitchen/eyes_folio.py IRWIN-RIPPE-2023 --all --scan 6
      213/215; unresolved ch167 (divider page) and ch184 (divider page);
      ch185 wrongly placed on pdf 95
    .venv/bin/python kitchen/eyes_folio.py IRWIN-RIPPE-2023 --only 167,184,185 --scan 6 --proof
      215/215 chapters read by the eyes; 0 unresolved
      0 disagree with the book's own contents
    kitchen/logs/IRWIN-RIPPE-2023-toc.json  20 provinces, 215 chapters

### DONE 2026-10-22 -- HAZZARD-2022 read by the eyes: 108/108, 0 unresolved, 1 TOC finding

3,952 PDF pages, 23 provinces, 108 chapters. This book prints no folios on
the pages the reader can see and its outline links are the only page numbers,
so all 108 are "pdf-page": the printed number IS the PDF page. Clean except
chapter 7: the outline points at pdf 284, which is the Part II divider page
(its list of chapters mentions chapter 7), while the real opener is pdf 286.
The scan found 286, but two bugs in the tool then put 284 back:

1. the scan branch did not accept a `pdf-page` match (only the pointer loop
   did), so 286 was found and rejected; and
2. after accepting it, `refine_opener` + the floor rule moved it to the
   contents number 284 -- but for a link/outline book the PDF page is the
   truth, and the outline is what is wrong.

Both fixed in `kitchen/eyes_folio.py`: the scan branch now accepts a
`pdf-page` match, and refine/reconcile/floor are skipped for `pdf-page`
chapters (their job is printed-folio repair). Re-run: 108/108, and chapter 7
is recorded as a real disagreement with the book's own contents (284 vs 286).

    .venv/bin/python kitchen/eyes_folio.py HAZZARD-2022 --all --scan 6
      107/108; unresolved ch7 (outline points at the Part II page)
    .venv/bin/python kitchen/eyes_folio.py HAZZARD-2022 --only 7 --from 285 --scan 10 --proof
      108/108 chapters read by the eyes; 0 unresolved
      1 disagree with the book's own contents: ch7 contents=284 page=286
    kitchen/logs/HAZZARD-2022-toc.json  23 provinces, 108 chapters

### DONE 2026-10-22 -- GUYTON-2026 read by the eyes: 85/85, 0 unresolved, 0 disagreements

1,070 PDF pages, 15 provinces, 85 chapters. The first pass placed 84; chapter
1 (printed page 3) was missed because its long title matched pages in the
front matter, and the automatic scan walked through the preface/contents
instead of reaching pdf page 20. Re-run with `--from 15`: the opener is
pdf 20 -> printed 3. This is the case `--from` was added for; the reader still
had to see the heading and the folio.

    .venv/bin/python kitchen/eyes_folio.py GUYTON-2026 --all --scan 6
      84/85; unresolved ch1
    .venv/bin/python kitchen/eyes_folio.py GUYTON-2026 --only 1 --from 15 --scan 10 --proof
      85/85 chapters read by the eyes; 0 unresolved
      0 disagree with the book's own contents
    kitchen/logs/GUYTON-2026-toc.json  15 provinces, 85 chapters

### DONE 2026-10-22 -- GREEN-HAND-2021 read by the eyes: 60/60, 0 unresolved, 0 disagreements

2,535 PDF pages, 8 provinces, 60 chapters. Clean on the first pass; no tool
change.

    .venv/bin/python kitchen/eyes_folio.py GREEN-HAND-2021 --all --scan 6
      60/60 chapters read by the eyes; 0 unresolved
      0 disagree with the book's own contents
    kitchen/logs/GREEN-HAND-2021-toc.json  8 provinces, 60 chapters

### DONE 2026-10-22 -- GRAY-2020 read by the eyes: 79/79, 0 unresolved, 0 disagreements

2,602 PDF pages, 9 provinces, 79 chapters. Clean on the first pass: every
chapter's opener printed exactly the folio the contents gives. No tool change.

    .venv/bin/python kitchen/eyes_folio.py GRAY-2020 --all --scan 6
      79/79 chapters read by the eyes; 0 unresolved
      0 disagree with the book's own contents
    kitchen/logs/GRAY-2020-toc.json  9 provinces, 79 chapters

### DONE 2026-10-22 -- FIRESTEIN-12 read by the eyes: 125/125, 0 unresolved, 0 disagreements

2,875 PDF pages, 18 provinces, 125 chapters. The first pass placed 124; the
one miss exposed a TRUNCATED text cache, not a bad TOC:

    kitchen/logs/FIRESTEIN-12-folio.txt had only 2,750 of 2,875 pages
    (created 21 Oct), so the last chapters were invisible to the pointer
    search. Chapter 130 was really at pdf 2764 -> printed 2229.

Fix in `kitchen/eyes_folio.py`: the folio cache is now checked against
`page_count_images`; if it is shorter than the PDF, it is rebuilt instead of
trusted. This is the same class of bug as the stale half-book caches fixed
earlier, and it is silent, so the check matters. A quick audit of every
existing `*-folio.txt` found no other truncated cache.

    .venv/bin/python kitchen/eyes_folio.py FIRESTEIN-12 --all --scan 6
      124/125; unresolved ch130
    .venv/bin/python kitchen/eyes_folio.py FIRESTEIN-12 --only 130 --scan 10 --proof
      cache rebuilt (2,750 -> 2,875 pages); 125/125; 0 unresolved
      0 disagree with the book's own contents
    kitchen/logs/FIRESTEIN-12-toc.json  18 provinces, 125 chapters

### DONE 2026-10-22 -- DEVITA-12 read by the eyes: 107/107, 0 unresolved, 0 disagreements

2,427 PDF pages, 4 provinces, 107 chapters. Clean on the first pass: every
chapter's opener printed exactly the folio the contents gives, so no tool
change and no second pass were needed.

    .venv/bin/python kitchen/eyes_folio.py DEVITA-12 --all --scan 6
      107/107 chapters read by the eyes; 0 unresolved
      0 disagree with the book's own contents
    kitchen/logs/DEVITA-12-toc.json  4 provinces, 107 chapters

### DONE 2026-10-22 -- DELISA-6 read by the eyes: 62/62, 0 unresolved, 0 disagreements

3,742 PDF pages, 9 provinces, 62 chapters. DELISA-6 is the third of the four
"no printed folio" books (with BRANT-5, ROCKWOOD-10,
WILLIAMS-OBSTETRICS-26); its contents is link-sourced, so the PDF link plus
the heading on the page is the proof and the PDF page number is stored
(`page_offset` 0 by construction). The new `pdf-page` branch handled it with
no special work: every chapter's opener printed the heading that its link
claimed.

    .venv/bin/python kitchen/eyes_folio.py DELISA-6 --all --scan 6
      62/62 chapters read by the eyes; 0 unresolved
      0 disagree with the book's own contents
    kitchen/logs/DELISA-6-toc.json  9 provinces, 62 chapters

### DONE 2026-10-22 -- BRENNER-11 read by the eyes: 71/71, 0 unresolved, 0 disagreements

3,529 PDF pages, 18 provinces, 71 chapters. The first pass placed 69. The two
misses exposed a TOC bug, not a page we could not find:

    vis-toc.txt had TWO entries for chapter 31 and TWO for chapter 56
      31  Primary Glomerular Disease          1007   <- the real chapter
      31  PRIMARY GLOMERULAR DISEASE          1091   <- duplicate, an e-page
      56  Endocrine Aspects of CKD            1901   <- the real chapter
      56  ENDOCRINE ASPECTS OF CKD            1915.e7 <- duplicate, an e-page

The TOC stage had kept the uppercase duplicates, whose "page" was the
e-page number (1091.e21 / 1915.e7) and therefore pointed at the wrong place.
The real openers, measured by the eyes, are pdf 1333 -> printed 1007 and
pdf 2521 -> printed 1901. The two entries in `BRENNER-11-vis-toc.json` were
corrected to the title-case titles and the real pages, then the eyes placed
them.

Two tool changes in `kitchen/eyes_folio.py`:
1. **The floor rule now keeps the SMALLER number in both directions.** It was
   written for the page showing a LATER number; when a bad TOC points LATER
   than the page (these two chapters), it used to restore the bad number.
   Now `kept = min(page, contents)` -- exactly the human's rule.
2. New `--from PAGE` starts the forward scan at a given PDF page, for the
   rare case where the pointer is far off. It does not decide anything: the
   reader still has to see the heading and the folio.

Evidence:

    .venv/bin/python kitchen/eyes_folio.py BRENNER-11 --all --scan 6
      69/71; unresolved ch31, ch56
    .venv/bin/python kitchen/eyes_folio.py BRENNER-11 --only 31,56 --scan 8 --proof
      71/71 chapters read by the eyes; 0 unresolved
      0 disagree with the book's own contents
    kitchen/logs/BRENNER-11-toc.json  18 provinces, 71 chapters

### DONE 2026-10-22 -- BRANT-5 read by the eyes: 83/83, 0 unresolved, 0 disagreements

4,324 PDF pages, 12 provinces, 83 chapters. BRANT-5 is one of the four books
whose pages print NO folio (with DELISA-6, ROCKWOOD-10 and
WILLIAMS-OBSTETRICS-26); its own contents gives hidden PDF links and the
project's rule for these books is: the page number is the PDF image number
(the number the human sees in the reader), so `page_offset` is 0 by
construction.

The first pass failed every chapter because the tool still demanded a printed
folio. Fix in `kitchen/eyes_folio.py`: when the contents is link-sourced
(`kind == "pdf-page"`) and the page prints no folio, the PDF link PLUS the
chapter heading on the page are the proof, and the number stored is the PDF
page. Recorded as `printed_from = "pdf-page (no printed folio; PDF page
used)"` so nobody mistakes it for a measured printed folio.

Evidence:

    .venv/bin/python kitchen/eyes_folio.py BRANT-5 --all --scan 6
      83/83 chapters read by the eyes; 0 unresolved
      0 disagree with the book's own contents
    kitchen/logs/BRANT-5-toc.json  12 provinces, 83 chapters

### DONE 2026-10-22 -- BENZON-2023 read by the eyes: 86/86, 0 unresolved, 0 disagreements

1,503 PDF pages, 8 provinces, 86 chapters. The first pass placed 84; two
chapters were missed and then placed on the second pass:

    ch76 Pain Management in the Emergency Department
         pdf 1327 -> printed 1034
    ch82 Pain Management at the End of Life and Home Care ...
         pdf 1386 -> printed 1076

Why they were missed: with `--only`, `after` stayed 0, so the pointer search
only looked at the first 400 pages (it found page 2 instead of page 1327).
Two small fixes in `kitchen/eyes_folio.py`:
1. `--only` now seeds `after` from the nearest earlier chapter that an
   earlier run placed, so the pointer is searched in the right part of the
   book.
2. `--only` now rewrites `<BOOK>-toc.json` from the MERGED records; before,
   only `--all` wrote it, so the two repaired chapters were silently absent
   from the TOC (it had 84 of 86).

Evidence:

    .venv/bin/python kitchen/eyes_folio.py BENZON-2023 --all --scan 6
      84/86; unresolved ch76, ch82
    .venv/bin/python kitchen/eyes_folio.py BENZON-2023 --only 76,82 --scan 30 --proof
      86/86 chapters read by the eyes; 0 unresolved
      0 disagree with the book's own contents
    kitchen/logs/BENZON-2023-toc.json  8 provinces, 86 chapters

### DONE 2026-10-22 -- AVERY-2021 read by the eyes: 61/61, 0 unresolved, 0 disagreements

The first of the 22 remaining books, in list order. The book is the South
Asian Edition (no edition number stated), 1,019 PDF pages, 4 provinces.

    .venv/bin/python kitchen/eyes_folio.py AVERY-2021 --all --scan 6
      61 chapters; kind: 61 printed-folio
      -> printed page 1 is PDF page 23 (page_offset 22)
      61/61 chapters read by the eyes; 0 unresolved
      0 disagree with the book's own contents
    kitchen/logs/AVERY-2021-toc.json  4 provinces, 61 chapters

Every chapter's opener printed exactly the folio the contents gives, so this
book needed no tool change. Note for the next run: the script needs the
project venv (`.venv/bin/python`); plain `python3` cannot import `neo4j`.

### DONE 2026-10-22 -- THE TWO HALF-BOOKS MADE WHOLE; both verified 100%

The human downloaded the missing parts. Both are real, complete PDFs and are
now the library's files; the old half-files and the two separate Bolognia
volumes were DELETED afterwards (the human asked for no souvenirs), and the
stray duplicate copy in ~/Downloads was deleted too.

    BRAUNWALD-12   new complete PDF: 2,549 pages, Parts I-XI, full index
                   (the old file was Parts I-V only, 1,227 pages)
    BOLOGNIA-2024  vol 2 (Sections 15-22, 1,191 pages) glued to vol 1
                   (Sections 1-14, 2,042 pages) = 3,233 pages; the printed
                   page numbers are continuous (vol 1 ends at printed 1692,
                   vol 2 starts at printed 1693)

Commands and evidence:

    pdfinfo  -> BRAUNWALD-12 2549 pages; BOLOGNIA-2024 combined 3233 pages
    python kitchen/eyes_folio.py BRAUNWALD-12 --all --scan 6
      102/102 chapters; 0 unresolved; 0 disagree with the contents
    python kitchen/eyes_folio.py BOLOGNIA-2024 --all --scan 6
      (then --only for the 10 chapters the first pass missed)
      161/161 chapters; 0 unresolved; 0 disagree with the contents
    kitchen/logs/BRAUNWALD-12-toc.json   11 provinces, 102 chapters
    kitchen/logs/BOLOGNIA-2024-toc.json  22 provinces, 161 chapters

`kitchen/books.json`: `pdf_file` and `page_count_images` updated for both
(the only tracked file whose DATA changed). Stale `<BOOK>-folio.txt` caches
removed so the text layer is re-read from the new PDFs. The vis-toc.json
files are unchanged: their chapter lists already covered all 102/161
chapters; only the physical pages had been missing.

Tool fixes in `kitchen/eyes_folio.py` (all measured on these two books):
1. An online-supplement page ("786.e1") is NOT printed page 786; it is an
   EXTRA page between 786 and 787. It was read as 786, which put Braunwald
   chapters 41, 64, 74 on the wrong page. `folio_of` now ignores such lines,
   and when the page before folio+1 is such a page the tool skips back over
   ALL of them to the last PRINTED page.
2. Bolognia prints its folio at the BOTTOM and the CHAPTER number at the
   top; reading the top first returned the chapter number. `folio_of` now
   checks the bottom lines first. This fixed chapters 7, 14, 27, 36, 50,
   62, 72, 90, 150.
3. The page that prints EXACTLY the folio the contents gives is now tried
   FIRST (the handoff's strongest-proof rule), then the page before
   folio+1. This fixed chapter 0.
4. An unresolved chapter was appended to the records twice (the summary
   said 105/105 instead of 102/102). Fixed.

Still to do (22 books, one at a time, the human watching):
AVERY-2021, BENZON-2023, BRANT-5, BRENNER-11, DELISA-6, DEVITA-12,
FIRESTEIN-12, GRAY-2020, GREEN-HAND-2021, GUYTON-2026, HAZZARD-2022,
IRWIN-RIPPE-2023, KAPLAN-11, MILLER-10, NELSON-2024, OXFORD-6, ROCKWOOD-10,
SLEISENGER-11, STAHL-2024, WILLIAMS-ENDO-2024, WILLIAMS-HEMATOLOGY-2021,
WILLIAMS-OBSTETRICS-26.

The human still checks the OTHER PDFs himself for completeness (a scan can
be missing pages in the middle); the two known half-books are now whole.

Invariants untouched: the 4,755 chapters, every geography file, Neo4j (still
empty), the BIBLE. The old half-files were DELETED (no souvenirs); the
library now holds only the 37 books in use, all referenced by
`kitchen/books.json`.

### DONE 2026-10-21 (n) -- FINAL STATE OF THE TOC WORK (do not redo these)

    Book            chapters   read by the eyes   not placed   BIBLE toc.json
    HARRISON-22         505            503             2        written
    ROBBINS-10           29             29             0        written
    THOMPSON-2023        20             20             0        written

* HARRISON-22: the two chapters not placed are ch 46 (its page is NOT in
  our PDF -- the book jumps from printed 292 to 293; checked by hand) and
  ch 417 (needs one more look).
* THOMPSON-2023 was re-run in full on 2026-10-21 evening because a small
  test run had overwritten its evidence file; the tool now MERGES with an
  existing file instead of overwriting it, so this cannot happen again.
* The result files live in `kitchen/logs/` (gitignored by the project): the
  working file `<BOOK>-eyes.json` (every chapter with its picture, the
  number, the proof) and the BIBLE's own `<BOOK>-toc.json` (provinces with
  page ranges, chapters with page_start and page_end). They are on this
  laptop; they are rebuildable with one command, but there is no need to
  rebuild them.
* STILL TO DO (24 books, one at a time, the human watching):
  AVERY-2021, BENZON-2023, BOLOGNIA-2024, BRANT-5, BRAUNWALD-12,
  BRENNER-11, DELISA-6, DEVITA-12, FIRESTEIN-12, GRAY-2020,
  GREEN-HAND-2021, GUYTON-2026, HAZZARD-2022, IRWIN-RIPPE-2023, KAPLAN-11,
  MILLER-10, NELSON-2024, OXFORD-6, ROCKWOOD-10, SLEISENGER-11, STAHL-2024,
  WILLIAMS-ENDO-2024, WILLIAMS-HEMATOLOGY-2021, WILLIAMS-OBSTETRICS-26.
* THE FIRST THING to raise with the human next time: he is to check by
  hand whether our PDFs are the COMPLETE books. BOLOGNIA-2024 and
  BRAUNWALD-12 are only volume 1 of a 2-volume set.

### DONE 2026-10-21 (m) -- THE TOC CHECKED AGAINST THE REAL PAGES, BY THE EYES

**READ `HANDOFF-2026-10-21-evening.md` FIRST. This entry only points at it.**

What the human decided today (and what overrules older notes):
* the 10 books he had already accepted stay as they are and are not tested
  again: YOUMANS-4, MANDELL-9, ROSEN-2022, MURRAY-7, MIDDLETON-2019,
  KRAUSE-16, SABISTON-22, CAMPBELL-2020, GOODMAN-14, ADAMS-12;
* Mimo v2.6's rewrite of `kitchen/page_folio.py` is ARCHIVED and not used
  (`kitchen/logs/mimo-2026-10-21/`); the file in git is the 19 Oct morning
  version written by `space-bunny-free`;
* the manager's lane is the Table of Contents. The globe, the entity
  registry, the viewer and the reading pipeline are for PAID models;
* nothing runs unattended -- one book at a time, the human watching;
* when the book's contents and the page disagree, the SMALLER number is
  kept (the floor rule) and the difference is recorded as a finding.

What was built: `kitchen/eyes_folio.py` (one script). For every chapter it
finds the page where the chapter BEGINS and the page number the book PRINTS
for that page, by showing the page to the free local reader (Qwen 3.8 27B)
as a PICTURE and keeping that picture on disk. The text layer only points
at which page to show. It also writes the BIBLE's own file
`kitchen/logs/<BOOK>-toc.json` (part 3 section 4.4): provinces with page
ranges, chapters with page_start and page_end.

The rules that settle a disagreement (all measured today, all in the
handoff file):
  * a page that prints EXACTLY the folio the contents gives IS that
    chapter's first page, whatever the reader calls the heading;
  * the corner number can be the chapter number, not a folio;
  * the reader can misread a digit, so the neighbouring pages are the check;
  * a page that prints no number is PROVED by the pages before and after
    (L and L+2 -> this page prints L+1; L and L+1 -> this page is an
    unnumbered plate and carries no number). In HARRISON-22: 813 pages of
    the first kind, 1 of the second;
  * a Table-of-Contents line that is only a number is NOT a folio;
  * accents and a trailing "s" are stripped when matching a title.

Results: THOMPSON-2023 20/20, ROBBINS-10 29/29 (every folio equal to the
book's own contents), HARRISON-22 finished and re-checked.

Two findings for the human: HARRISON-22 chapter 46 has NO page in our PDF
(the book jumps from printed 292 to 293), and BOLOGNIA-2024 / BRAUNWALD-12
may be volume 1 of a 2-volume set (not verified).

Invariants untouched: books.json (page_offset still null for all 37), every
geography file, the 4,755 chapters, Neo4j (still empty), the BIBLE.

### DONE 2026-10-21 (l) -- THE TOOL FIXED: the reader REPORTS, the script DECIDES

The first version of `kitchen/eyes_folio.py` asked the reader "is this the
chapter's first page? YES/NO". On HARRISON-22 that gave a false YES on an
index page (the index lists the chapter title), and the wrong page then
poisoned every chapter after it: 72 ok, 433 unresolved, and some of the
"ok" ones pointed at the index. The reader now reports what it SEES and the
script decides:

    KIND:    OPENING | BODY | INDEX | OTHER
    HEADING: the heading printed at the top of the page, verbatim
    FOLIO:   the page number printed in a corner, or NONE

A page is the chapter's opener when KIND is OPENING and the heading carries
the chapter number or the chapter's title. An INDEX page can no longer be
mistaken for an opener.

The pointer (which page to show) was rebuilt from the books' own structure:
    1. the folio evidence: the opener is the page before the one that prints
       folio+1, or the page that prints the folio itself;
    2. pages whose head carries a chapter marker and the number
       ("c h a p t e r" / "19"), which is the opener in some books;
    3. pages whose running head carries the chapter title;
    4. if all of that fails, the pages after the previous chapter are read
       one by one (--scan N) until the reader finds the opener.
Two more lessons, both measured today:
  * a Table-of-Contents line that is only a number ("45") is NOT a folio;
    only the first three and last three lines of a page are trusted for the
    folio, so the front matter can no longer hijack the pointer;
  * a title with no significant word ("Introduction") is matched by the
    reader's KIND=OPENING alone.

RESULT, both books clean with the fixed tool:
    python kitchen/eyes_folio.py THOMPSON-2023 --all --scan 6
      20/20 chapters read by the eyes, 0 unresolved, and every folio equals
      the folio the book's own contents prints. 4 provinces.
    python kitchen/eyes_folio.py ROBBINS-10 --all --scan 6
      29/29 chapters read by the eyes, 0 unresolved, every folio equal to the
      contents' folio. 6 provinces.
The tool also writes the BIBLE's own file `kitchen/logs/<BOOK>-toc.json`
(part 3 section 4.4): provinces with their page ranges, chapters with
page_start = the printed page the page shows and page_end = the next
chapter's printed page minus one. That is the one thing the Table of
Contents data still lacked.

HARRISON-22 (505 chapters) is running with the fixed tool.

### DONE 2026-10-21 (k) -- ROBBINS-10 read by the eyes: 29/29, 0 unresolved

    python kitchen/eyes_folio.py ROBBINS-10 --all
    29/29 chapters read by the eyes, 0 unresolved. Every folio was read off
    the page picture itself ("printed-on-the-page", not derived from a
    neighbour). Every one of the 29 folios EQUALS the folio the book's own
    contents prints -- two independent sources, no disagreement.
    The manager's own eyes on PDF page 82: the corner prints 71 and the page
    is the opener of chapter 3 "Inflammation and Repair" -- matches.
    detail: kitchen/logs/ROBBINS-10-eyes.json
    pictures: kitchen/logs/eyes-render/ROBBINS-10/

### DONE 2026-10-21 (j) -- THE EYES METHOD: a new tool, the first book finished (THOMPSON-2023)

**The human's decision on 2026-10-21:** the 10 books reported OK on 2026-10-19
morning stay as they are (not tested again, not touched). For the other 27
books the human asked for a NEW method, his way, not the continuation of the
rewrite that `mimo-v2.6-flash-free` made on 2026-10-19 evening and 2026-10-21
morning. Evidence for who wrote what is in the OpenCode session database:
`page_folio.py` was created 19 Oct 14:24 by `space-bunny-free`; Mimo v2.6
rewrote it 19 Oct 15:38-16:19 (commit 1efc2a9), wrote `folio_sample.py`
19 Oct 16:20, and added +188 uncommitted lines on 2026-10-21 11:43-13:09.

**What was done:**
1. `kitchen/page_folio.py` restored to the 19 Oct MORNING version (written by
   `space-bunny-free`, the one that measured the human's 10 books). Mimo's
   rewrite is archived, not used: `kitchen/logs/mimo-2026-10-21/`
   (page_folio.py.mimo, folio_sample.py.mimo and his 12 result files).
   Commit ffba5be.
2. New tool `kitchen/eyes_folio.py`. The printed page of a chapter is read by
   the FREE local reader (Qwen 3.8 27B, TIER FREE) from a PICTURE of the
   page: two questions, "does this page begin the chapter?" and "what number
   is printed in the corner?". The PDF text layer is used ONLY to point at
   which page to show; the stored value always comes from the picture, and
   the picture is kept on disk under `kitchen/logs/eyes-render/<BOOK>/`.
   Nothing is invented: a page with no printed number is recorded as such,
   a chapter whose page is not found is recorded as unresolved and reported.
3. The pointer (text layer) was rebuilt from the books' own structure, not
   from Mimo's clustering: a chapter opener is found from the folio the
   book's contents prints (the first page printing folio+1 is the page AFTER
   the opener) or, for books whose TOC stores a PDF page, from that page.
   Chapters are walked in book order so a pointer must be later than the
   previous chapter's page.

**THOMPSON-2023 -- the first book done with the new method:**
    python kitchen/eyes_folio.py THOMPSON-2023 --all
    20/20 chapters read by the eyes, 0 unresolved.
    Every printed folio equals the folio the book's own contents prints
    (1, 5, 23, 45, 61, 79, 109, 135, 149, 175, 203, 231, 251, 293, 321,
    347, 373, 391, 411, 425).
    detail: kitchen/logs/THOMPSON-2023-eyes.json
    pictures: kitchen/logs/eyes-render/THOMPSON-2023/
    The manager's own eyes on PDF page 28 (the page after chapter 2's
    opener): the corner prints 6, so chapter 2's first page is printed
    page 5 -- the tool and the eye agree.

**Invariants untouched:** books.json (page_offset still null for all 37),
every geography file, the 4,755 chapters, Neo4j (still empty).

### DONE 2026-10-19 (i) -- THE BUG BEHIND (h) FOUND AND FIXED; HARRISON-22 FINISHED AND CHECKED

**READ `HANDOFF-2026-10-19-evening.md` FIRST. This entry only points at it.**

What (h) got wrong, and what replaced it:

1. **`page_start` holds two different numbers.** `toc_vision`/`toc_openers`
   stored the number the CONTENTS PRINTS (22 books -> it IS the printed page);
   `toc_outline` stored the PDF bookmark destination (15 books -> it IS the
   PDF page). `page_folio.py` read every entry as a PDF page, so for the
   contents-read books the answer was off by the whole front matter.
   Proof by rendered images: Harrison-22 pdf 2044 is the opener of ch. 266,
   contents say 2001, corner prints 2001, `page_start` 2001, PDF page 2044.
   Mandell-9 pdf 1835 is the opener of ch. 107, `page_start` 1835, corner
   prints 1452. Nelson-2024 pdf 2430, corner prints 2415.
   **The "10 books / 1,485 chapters verified" claim of (h) is WITHDRAWN.**
2. **Off-by-one:** `folio_at()` returned the NEXT page's folio when the
   chapter's own page printed nothing (Mandell 107 -> 1453; the page prints
   1452). Fixed: a later page with gap g means `folio = start - g`.
3. **The two tools are rewritten** -- `kitchen/page_folio.py` (decides the
   meaning of `page_start` per entry from its own evidence, returns BOTH the
   PDF page and the printed page, refuses to answer when it cannot prove one)
   and `kitchen/folio_sample.py` (renders a random sample to PNG and lets the
   free local READER confirm: is this the chapter's first page, what does the
   corner print -- Law 14).

EVIDENCE for the book that is finished:

    python kitchen/page_folio.py HARRISON-22
    -> HARRISON-22  OK  both=505/505 kind=printed offset=43 conflicts=0
    offset is CONSTANT: 2,542 pages vote for 43, and 43 wins in every
    500-page block of the book (offset_mode_share = 1.0).
    python kitchen/folio_sample.py HARRISON-22 --n 12
    -> 12/12 sampled chapters agree with Qwen on BOTH questions (opener +
       corner folio); 0 disagree.  kitchen/logs/HARRISON-22-folio-sample.json
    manager's own eye check: pdf 357 -> corner prints 314, page is the opener
    of chapter 50 "Unintentional Weight Loss" (matches).
    One book oddity is real, not a bug: the book's own contents puts chapters
    45 and 46 both on printed page 291 (recorded as check = "shared-page").

INVARIANTS (nothing else touched): `toc_validate.py --vis` 37/37 clean,
4,755 chapters; `kitchen/books.json` unchanged (`page_offset` still null for
all 37 books); no geography file written; nothing loaded into Neo4j; BIBLE/ not
edited.

NEXT: `page_folio.py --all` (free), then `folio_sample.py <BOOK> --n 12` ONE
BOOK AT A TIME with a report after each, exactly as Nir asked.

### DONE 2026-10-19 (h) -- page_offset: 10 of 37 books measured, BIBLE's one-offset-per-book PROVED FALSE

**READ `HANDOFF-2026-10-19-page-offset.md` FIRST. It is the full account of
this step and this handoff entry only points at it.**

Step A3 (page_offset, BIBLE part 3 section 4.6) was attempted on all 37 books
with the new `kitchen/page_folio.py`. Zero model calls.

THE FINDING THAT MATTERS: **one page_offset per book does not exist.** Rendered
page images and read them: SABISTON-22 prints 876 on pdf 1429 and 1367 on pdf
1982 (the gap drifts by 62 unnumbered pages in between), and it restarts its
numbering inside each Section (pdf 300 prints 13, pdf 500 prints 178). A
single offset would put hundreds of chapters on a page they are not printed
on, which is a false citation (Law 2). The method therefore decides each
chapter's folio LOCALLY, over a forward window, with the pages voting.

RESULTS: 10 books at 100 percent and TRUSTED (1,485 chapters):
YOUMANS-4 432/432, MANDELL-9 210/210, ROSEN-2022 208/208, MURRAY-7 142/142,
MIDDLETON-2019 99/99, KRAUSE-16 93/93, SABISTON-22 92/92, CAMPBELL-2020 82/82,
GOODMAN-14 78/78, ADAMS-12 49/49. Written to kitchen/logs/<BOOK>-folio.json.

The other 27 books are PARTIAL and their printed pages are NOT trusted and
MUST NOT be used. DELISA-6's failure is understood and proved: that book
prints no page numbers at all, on chapter openers or on ordinary pages
(pdf 51, 52, 60 and 203 checked in the text layer and in the rendered image).

TWO BUGS FOUND BY LOOKING AT REAL PAGES, both already fixed in the code, do
not relearn: (1) Elsevier's "721.e89" folio -- e89 is a marker, not a page,
and because it advances while the page stays put it produces a perfectly
constant WRONG offset (measured 1160 across six pages) that beats a naive
vote; (2) section numbers that look exactly like folios.

THE INDEPENDENT CHECK IS STILL MISSING. Only 4 pages were verified by eye,
across 2 books. That proves the method and caught two bugs; it does not prove
the 1,485 answers.

EVIDENCE: `python kitchen/toc_validate.py --vis` -> 37/37 clean, 4755 chapters
(unchanged; this step wrote nothing into the geography). The handoff file has
the per-book table, the causes, and the ordered next steps.

### DONE 2026-10-19 (g) -- YOUMANS-4 read: 432 chapters, 49 provinces, validator CLEAN. THE LIBRARY IS 37/37.

YOUMANS-4 = Youmans Neurological Surgery, a MULTI-VOLUME set, and the only
image-only book in the library (pdftotext returns 0 characters), so it was read
with the vision path: `toc_vision.py` 778 s + `toc_headings.py` 787 s, model
`qwen3.8:27b` via Ollama (READER_VISION_MODEL in kitchen/.env).

    python kitchen/build_book.py YOUMANS-4
    RESULT YOUMANS-4 ok chapters=432 provinces=49 without_page=0
    python kitchen/toc_validate.py --vis
    37/37 clean, 4755 chapters total

The human ordered the book done FROM SCRATCH: the 11:22 output of an earlier
run was rejected and DELETED (not backed up), together with its rendered page
images. The library count is unchanged by that (kitchen/logs/ is gitignored).

**TWO NEW BUGS FOUND AND FIXED -- both only visible in a multi-volume book.**

1. THE SAME PART READ TWICE. A volume prints its own "PART 1, PART 2 ..." so
   the same name+page arrives from two different contents pages. The 19 Oct
   read produced 52 provinces and 444 chapters, of which 8 chapter rows were
   the same chapter written twice. `toc_dedupe.py` removed none of them
   because they sat in different provinces.
2. A PART THAT IS ONLY A SLICE OF THE PART BEFORE IT. The truncated read
   invented a second "PART 3" at page 2325 whose four chapters (298-301) all
   already belonged to PART 2, while the real PART 3 stood at page 2465. This
   is what the validator was warning about ("1 page_start decreases, first:
   p2361 -> p2249"); the page numbers were never wrong.

FIX: new `kitchen/toc_merge_dup_provinces.py`, wired into `build_book.py` as
step 4c -- it MUST run after `toc_apply_headings.py`, because that step
rebuilds the provinces and would throw the merge away. It merges provinces
sharing name+page_start, and drops a province whose every chapter is already
held (same number, same page) by a larger part when another province already
uses its name. Result 52 -> 49 provinces, 444 -> 432 chapters, validator clean.
PROVENANCE LAW 11 KEPT: no JSON was typed by hand, the script reads and writes
the reader's own recorded words; 432 chapters = 428 numbered + the 4 the book
itself prints with letters (94A 94B 157A 157B), numbered 35..464, pages
275..3804.

**THE WHOLE LIBRARY IS NOW READ: 37/37 books clean, 4,755 chapters.** The next
BIBLE phase is page_offset (BIBLE part 3 section 4.6), still NOT STARTED, and
every citation depends on it.

### DONE 2026-10-18 (f) -- WILLIAMS-HEMATOLOGY-2021 read: 140 chapters, 13 provinces, validator CLEAN

Williams Hematology, 10th ed (2021, McGraw-Hill, 5,052 pages). EIGHTH
contents-less book: the 10 Oct locator's toc_images was null, and no
printed Contents exists in this libgen PDF (pdf 39-81 = Abbreviations).
The book's own Contents turns out to be a scraped AccessMedicine web TOC
printed on pdf 82-83: it gives all 13 Parts and all 140 chapter titles
but NO page numbers.

Chapter PAGES from the PDF bookmark outline: 149 flat bookmarks --
front matter, then Chapter 1@84, Chapter 2@97, then libgen's misnamed
"ownload (N).pdf" targets for the rest (target pages still correct);
140/140 chapter targets present, 0 broken
(`/tmp/opencode/wchem-targets.json`). Titles merged from the web TOC
and the opener text (`wchem-parts.json`, `wchem-final-titles.json`).
ZERO model calls. Recorded builder:
`kitchen/logs/WILLIAMS-HEMATOLOGY-2021-build.py`.

Verification:
- All 140 opener pages verified by pdftotext: the last four significant
  words of each chapter's title are present on its outline-target page
  (0 mismatches).
- 14 titles eye-verified from 110-dpi renders where pdftotext glued the
  author onto the title or cut a wrapped line: ch 27, 50, 61, 69, 75,
  77, 80, 82, 94, 102, 112, 115, 123, 125 (ch125's opener prints
  letter-spaced "V O N Willebrand Disease" with the author glued on;
  ch129's author "X. Long Zheng" was glued to the title and stripped).
- ch139 "Preservation and Clinical use of Platelets" (lowercase "use")
  is what the book's own Contents prints -- kept verbatim.

Part banners do NOT print on the chapter openers (these are
AccessMedicine chapter pages), so Part boundaries come from the book's
own Contents listing. Province name = "Part N - Title" (number + meaning
together, Nir's 15 Oct rule).

MEASURED result -- 140 chapters (1..140 complete, pages ascending,
no gaps/dupes), 13 provinces:

    Part I   - Clinical Evaluation of the Patient        3 ch   84-132
    Part II  - The Organization of the Lymphohematopoie  2 ch  153-223
    Part III - Epochal Hematology                        3 ch  243-302
    Part IV  - Molecular and Cellular Hematology        13 ch  331-681
    Part V   - Therapeutic Principles                   11 ch  691-978
    Part VI  - The Erythrocyte                          28 ch 1015-1969
    Part VII - Neutrophils, Eosinophils, Basophils...    6 ch 1987-2173
    Part VIII - Monocytes and Macrophages                6 ch 2209-2344
    Part IX  - Lymphocytes and Plasma Cells              9 ch 2371-2614
    Part X   - Malignant Myeloid Diseases                7 ch 2633-3021
    Part XI  - Malignant Lymphoid Diseases              21 ch 3145-3775
    Part XII - Hemostasis and Thrombosis                26 ch 3795-4818
    Part XIII - Transfusion Medicine                     5 ch 4875-4999

NOTE (page_offset, still NOT started): page_start stores PDF pages;
that is what BIBLE 3 section 4.6 will fix later. Nothing depends on it
yet.

Evidence:

    RESULT WILLIAMS-HEMATOLOGY-2021 ok chapters=140 provinces=13 without_page=0
    - 140 of 140 chapters get their page from the PDF's OWN bookmark
      outline (the contents prints none and carries no link for them)
    Full library: 36/36 clean, 4,323 chapters total.

### DONE 2026-10-18 (e) -- WILLIAMS-ENDO-2024 read: 48 chapters, 11 provinces, validator CLEAN

Williams Textbook of Endocrinology, 14th ed (2024, Elsevier, 2,319
pages). SEVENTH contents-less book: pdftotext found NO Contents heading
and no dotted-leader pages anywhere in the front matter or first 60
pages. The 10 Oct locator's toc_images [26,37] was wrong -- pdf 26 is
chapter 2's opener, not a contents page (found today by looking at the
text and the page itself, the standard lesson).

Built from the PDF bookmark outline: 2,944 entries, 0 broken
(`/tmp/opencode/wendo-outline.json`), ZERO model calls. Structure:
9 printed Sections, chapters numbered 1-48 continuously. Chapters
19-26 sit one bookmark level deeper because Section VI prints three
sub-banners; the banners were eye-verified:
    pdf 982  = "SECTION VI Endocrinology and the Lifespan" TOGETHER
                with "SECTION VI A Maternal-Fetal" (chapter 19)
    pdf 1063 = "SECTION VI B Childhood" (chapter 21)
    pdf 1442 = "SECTION VI C Adulthood" (chapter 25)
So Section VI is split into VI A / VI B / VI C provinces exactly as
the book prints them -> 11 provinces, not 9.

Every one of the 48 chapter openers was verified by pdftotext (the
outline target page carries the chapter number + title at the top).
Eye spot-checks across the whole book (9 pages):
    pdf 13  = SECTION I banner + chapter 1 Principles of Endocrinology
    pdf 120 = SECTION II banner + chapter 5 Neuroendocrinology
    pdf 413 = SECTION III banner + chapter 9 Thyroid Pathophysiology
    pdf 597 = SECTION IV banner + chapter 13 The Adrenal Cortex
    pdf 982 = SECTION VI + VI A banners + chapter 19 Endocrine Changes
              in Pregnancy
    pdf 1063/1442 = VI B / VI C banners + chapters 21/25
    pdf 1493 = SECTION VII banner + chapter 27 Mineral Metabolism
    pdf 1777 = chapter 35 Type 1 Diabetes Mellitus
    pdf 2153 = SECTION IX banner + chapter 42 Endocrine Neoplasia
    pdf 2310 = chapter 48 Endocrine Disorders of Critical Illness

MEASURED result -- 48 chapters (1..48 complete, no gaps/dupes),
11 provinces:

    Section I   - Hormones and Hormone Action          4 ch   13-85
    Section II  - Hypothalamus and Pituitary           4 ch  120-376
    Section III - Thyroid                              4 ch  413-542
    Section IV  - Adrenal Cortex and Endocrine Htn     2 ch  597-673
    Section V   - Sexual Development and Function      4 ch  712-936
    Section VI A - Maternal-Fetal                      2 ch  982-1005
    Section VI B - Childhood                           4 ch 1063-1425
    Section VI C - Adulthood                           2 ch 1442-1461
    Section VII - Mineral Metabolism                   5 ch 1493-1658
    Section VIII - Disorders of Carb. and Fat Metab.  10 ch 1681-2093
    Section IX  - Polyendocrine and Neoplastic Dis.    7 ch 2153-2310

NOTE (page_offset, still NOT started): page_start stores PDF pages.
The printed folio drifts badly in this book because every chapter's
references carry e-pages ("12.e1" style): printed 1 = pdf 13, but
chapter 2 already prints folio 13 at pdf 26, and by chapter 46 the
gap is ~500 pages. That is exactly what BIBLE 3 section 4.6
(page_offset) will fix later; nothing depends on it yet.

Evidence:

    RESULT WILLIAMS-ENDO-2024 ok chapters=48 provinces=11 without_page=0
    - 48 of 48 chapters get their page from the PDF's OWN bookmark
      outline (the contents prints none and carries no link for them)

### DONE 2026-10-18 (d) -- STAHL-2024 read: 61 chapters, 61 provinces, validator CLEAN

The Prescriber's Guide: Children and Adolescents (Stahl's Essential
Psychopharmacology), 2nd ed (2024, Cambridge University Press, 605
pages). Earlier attempts "could not find a contents page" -- MEASURED
today: the book DOES print its Contents (pdf pages 6-7); the text layer
carries it cleanly, so the whole book was parsed with ZERO model calls
and ZERO image renders for the build itself.

What the Contents prints: Introduction (vii), List of Icons (xix), 59
numbered drug monographs in alphabetical order (printed pages 1-560),
Appendix (561), three indexes (573/577/581), Abbreviations (583).
Included as chapters: Introduction + the 59 drugs + Appendix = 61.
Skipped (not chapters): List of Icons (icon legend), the three indexes
(already recorded in books.json as index_images 598-603), Abbreviations
(back-matter list).

Offsets verified by eye: body pdf = printed + 21 (printed 1 = pdf 22,
folio "1" at the page foot); roman front matter pdf = roman + 1 (xix =
pdf 20). Every one of the 59 drug openers was matched to its Contents
entry via pdftotext heads (59/59), and 5 openers were then rendered and
checked by eye: pdf 8 = Introduction; pdf 22 = ALPRAZOLAM; pdf 294 =
GABAPENTIN; pdf 576 = ZOLPIDEM; pdf 582 = Appendix.

PROVINCE DECISION (recorded, reversible -- nothing is in Neo4j yet):
one province per monograph ("DRUG 1 - alprazolam" ... "DRUG 59 -
zolpidem") plus Introduction and Appendix = 61 provinces. Reasons:
(1) the book IS "one monograph per drug" -- its own structure;
(2) its Index by Drug Class puts nearly every drug in TWO OR MORE
classes (diazepam = anticonvulsant + anxiolytic; clomipramine =
antidepressant + anxiolytic + neuropathic pain; aripiprazole =
antipsychotic + mood stabilizer), so class-based provinces cannot be
contiguous in the alphabetical book order the validator requires;
(3) Nir's 15 Oct rule forbids leaving the 59 chapters as one big
group, and an invented alphabetical block ("A-C drugs") would carry
no meaning. Each monograph is a self-contained unit with its own
printed page range -- the closest honest imitation of what the authors
printed.

Pipeline change (benefits every future text-layer book):
`toc_validate.py` now accepts _page_source "text-contents" (printed
contents read from the PDF text layer) with the same book-evidence
standing as pdf-outline / text-top / pdf-link. Printed folios are kept
per chapter in _printed_folio (Law 2), including "vii" and 561.

Evidence:

    RESULT STAHL-2024 ok chapters=61 provinces=61 without_page=0
    - 61 of 61 chapters get their page from the printed contents read
      in the PDF's TEXT LAYER

### DONE 2026-10-18 (c) -- ROSEN-2022 read: 208 chapters, 25 provinces, validator CLEAN

Rosen's Emergency Medicine, 10th ed (2022, 2-volume set in one PDF,
3,050 pages). SIXTH contents-less book: no printed CONTENTS page
anywhere (pdftotext scan of the front matter, the volume boundary and
the back matter found none). Geography built with ZERO model calls from
three recorded sources:

1. The PDF's own bookmark outline: 192 numbered chapters (1-192, no
   gaps) + 16 e-chapters (e1-e16), 0 broken targets
   (`/tmp/opencode/rosen-banners.json`, chapter list).
2. The 24 SECTION banners, found by a pdftotext scan of every chapter
   opener ("KEY CONCEPTS" + banner text) -- each banner prints only on
   the FIRST chapter of its section, and section numbering restarts
   within each Part.
3. The 5 PART names, read from the running headers via a full-book
   pdftotext scan (PART I Fundamental Clinical Concepts, II Trauma,
   III Emergency Medicine by System, IV Environment and Toxicology,
   V Special Populations) plus the unnumbered part header "The
   Practice of Emergency Medicine" over e1-e16.

Two eye-verified corrections to the outline targets:

1. 57 numbered-chapter targets pointed ONE PAGE LATE (the outline
   links to the first content page, not the opener). The opener was
   recovered by the "KEY CONCEPTS" signature (present only on true
   openers); all 57 fixes are target-1 except none the other way.
2. E-chapter openers are the outline targets THEMSELVES (their
   openers carry an OUTLINE box, and KEY CONCEPTS starts on the next
   page) except e5, whose opener is 2912 (eye-verified with e3, e4,
   e10).

One book-design quirk, recorded not corrected: the banner
"SECTION FIVE Gastrointestinal System" physically prints on chapter
77's opener (pdf 1264), but chapters 75-76 (Esophagus/Stomach/
Duodenum, Liver) are GI content whose openers carry no banner. The
province therefore starts at chapter 75 (pdf 1216); the banner's real
page is recorded in `ROSEN-2022-vis-outline.json`.

MEASURED result -- 208 chapters (192 numbered + 16 e), 25 provinces,
every numbered chapter present exactly once:

    PART I   SECTION ONE   Resuscitation and Analgesia          7 ch    21-110
    PART I   SECTION TWO   Signs, Symptoms, and Presentations  24 ch   122-337
    PART II  SECTION ONE   General Concepts and System Injuries 9 ch   350-521
    PART II  SECTION TWO   Orthopedic Injuries                 9 ch   532-732
    PART II  SECTION THREE Soft Tissue Injuries                6 ch   763-842
    PART III SECTION ONE   Head and Neck                       3 ch   857-912
    PART III SECTION TWO   Pulmonary System                    5 ch   927-982
    PART III SECTION THREE Cardiac System                      6 ch   993-1128
    PART III SECTION FOUR  Vascular System                     5 ch  1139-1193
    PART III SECTION FIVE  Gastrointestinal System             8 ch  1216-1342
    PART III SECTION SIX   Genitourinary and Gynecologic Sys   4 ch  1355-1414
    PART III SECTION SEVEN Neurology                           9 ch  1424-1539
    PART III SECTION EIGHT Behavioral Disorders                6 ch  1552-1585
    PART III SECTION NINE  Immunologic and Inflammatory        6 ch  1597-1669
    PART III SECTION TEN   Hematology and Oncology             5 ch  1696-1752
    PART III SECTION ELEVEN Metabolism and Endocrinology       5 ch  1773-1832
    PART III SECTION TWELVE Infectious Diseases               10 ch  1854-2024
    PART IV  SECTION ONE   Environment                         7 ch  2034-2117
    PART IV  SECTION TWO   Toxicology                         20 ch  2127-2327
    PART V   SECTION ONE   The Pediatric Patient              18 ch  2337-2602
    PART V   SECTION TWO   The Pregnant Patient                5 ch  2619-2696
    PART V   SECTION THREE The Geriatric Patient               4 ch  2707-2733
    PART V   SECTION FOUR  Special Clinical Circumstances      4 ch  2743-2781
    PART V   SECTION FIVE  Underserved Populations             7 ch  2795-2858
    (unnumbered) The Practice of Emergency Medicine           16 ch  2869-3043

Spot-checked by eye (8 openers across the whole book): pdf 21 = 1
Airway + SECTION ONE banner; pdf 763 = 50 Wound Management Principles
+ SECTION THREE; pdf 1216 = 75 Esophagus, Stomach, and Duodenum (no
banner, as decided); pdf 1597 = 102 Arthritis + SECTION NINE
"Immunologic and Inflammatory" (kept exactly as the banner prints --
the first draft had wrongly added the word "Disorders"); pdf 2337 =
155 Care of the Pediatric Patient; pdf 2795 = 186 Multiculturalism,
Diversity, and Care Delivery; pdf 2869 = e1 Global Emergency
Medicine; pdf 3043 = e16 Tactical Emergency Medical Support and
Urban Search and Rescue. Builder: `kitchen/logs/ROSEN-2022-build.py`
(recorded, re-runnable).

Evidence:

    RESULT ROSEN-2022 ok chapters=208 provinces=25 without_page=0
    Full library: 33/33 clean, 4,074 chapters total
    -- EVERY attempted book is clean; 4 books remain unread.

### DONE 2026-10-18 (b) -- OXFORD-6 read: 127 chapters, 22 Sections, validator CLEAN

Oxford Textbook of Palliative Medicine, 6th ed (2021, 1,409 pages). This
book DOES print its contents (images 8-13), read with the model's eyes
in one pass (`toc_vision.py OXFORD-6 --start 1 --windows 3`). Chapters
are numbered N.M (section.chapter) and every section title sits on its
own line below a bare "SECTION N" banner.

Three defects were found by eye-checking the transcript against the
printed pages, and all three were fixed:

1. TRIPLICATED CHAPTERS (pipeline bug, fixed for every book). Page 13
   is thin (7 chapters), so it was re-read at 220 dpi; the rollback in
   `read_pages` truncated the province LIST but page 13 had appended its
   chapters to the SECTION 22 province opened on page 12 -- so the same
   7 chapters were appended 3 times (22.3-22.9 x3 in the first JSON).
   `toc_vision.py` now has `_rollback()`, which also trims chapters
   added to pre-existing provinces. Reparse from the saved transcript
   (zero model calls) removed the duplicates.

2. CHAPTERS UNDER THE WRONG BANNER. On printed pages 9 and 10 the model
   printed the SECTION 5 / SECTION 8 banner BEFORE the trailing 4.5-4.13
   and 7.15-7.18 chapters that the page puts ABOVE the banner. Re-reading
   both pages at 220 dpi fixed page 10 (7.15-7.18 now precede the
   SECTION 8 banner, and "Cardiorespiratory" is spelled correctly -- the
   150 dpi read had dropped an 'o'); page 9 kept the same order at both
   resolutions, so a recorded one-off (`kitchen/logs/OXFORD-6-regroup.py`)
   moved the 9 chapters by the BOOK'S OWN rule: chapter N.M belongs to
   SECTION N. Every move is in `OXFORD-6-vis-regroup.json`.

3. MISSING 16.2 AND 16.3. The 150 dpi read of page 12 skipped the top of
   the page entirely; the 220 dpi re-read recovered "16.2 Care of
   children with advanced illness 1035" and "16.3 Palliative medicine
   and care of the elderly 1046". The newer answers for pages 9, 10 and
   12 replaced their blocks in the transcript; `toc_reparse.py` then
   rebuilt the JSON from the corrected words on disk.

Also fixed in `toc_vision.py` `parse()`: a bare "SECTION 8" plus a
separate title field is now joined ("SECTION 8 - Gastrointestinal
symptoms and disorders" would have been the old form; the 220 dpi reads
then supplied the full names inline, which the parser keeps as-is).

MEASURED result -- 127 chapters, every section's numbers complete 1..N,
every page from the printed contents, pages ascending within each
section:

    SECTION 1  The worldwide status of palliative care       4 ch      3-26
    SECTION 2  The challenge of palliative medicine          6 ch     35-93
    SECTION 3  Service delivery issues in palliative care    5 ch    103-143
    SECTION 4  Healthcare professionals in palliative care  13 ch    159-255
    SECTION 5  Communication and palliative medicine         3 ch    267-286
    SECTION 6  Family and caregiver issues                   2 ch    295-303
    SECTION 7  Pain                                         18 ch    313-506
    SECTION 8  Gastrointestinal symptoms and disorders       6 ch    525-579
    SECTION 9  Cardiorespiratory symptoms and disorders      2 ch    589-604
    SECTION 10 Skin and oral symptoms and disorders          4 ch    613-656
    SECTION 11 Genitourinary symptoms and disorders          2 ch    673-677
    SECTION 12 Constitutional symptoms and related disorders 5 ch    685-727
    SECTION 13 Psychiatric and psychological symptoms...     5 ch    739-773
    SECTION 14 Palliative care in cancer                    13 ch    787-937
    SECTION 15 Issues in populations with non-cancer ill...  8 ch    949-1020
    SECTION 16 Issues of the very young and the very old     3 ch  1029-1046
    SECTION 17 Spiritual issues in palliative medicine        2 ch  1063-1072
    SECTION 18 The terminal phase                            3 ch  1083-1104
    SECTION 19 Ethical issues                                8 ch  1121-1180
    SECTION 20 Assessment tools and informatics              3 ch  1191-1216
    SECTION 21 Teaching and training in palliative medicine   3 ch  1233-1252
    SECTION 22 Research in palliative medicine                9 ch  1261-1335

Spot-checked by eye (PDF page = printed folio + 23; page_start stores
the PRINTED folio, Law 2): printed 3 = 1.1 International progress;
printed 13 = 1.2 Essential medicines; printed 198 = 4.5 The role of the
chaplain; printed 1035 = 16.2 (the page's own footnote says "Chapter
16.2"); printed 1335 = 22.9 Clinical audit, quality improvement, and
safety. The book's body starts on printed page 3 -- low numbers are
real, not locator noise.

Evidence:

    RESULT OXFORD-6 ok chapters=127 provinces=22 without_page=0
    Full library: 32/32 clean, 3,866 chapters total
    -- EVERY attempted book is clean; 5 books remain unread.

### DONE 2026-10-18 (a) -- NELSON-2024 read: 519 chapters, 33 Parts, validator CLEAN

Nelson Textbook of Pediatrics, 22nd ed (2-volume set in one PDF, 4,534
pages). FIFTH book with no printed table of contents -- verified by eye:
cover -> In Memory -> contributors (pp. 5-42) -> Preface (p. 43) ->
Chapter 1 starts on p. 44. The old October attempt had left 4 stray
chapters in `NELSON-2024-toc.json` (backed up to
`kitchen/logs/backup-2026-10-18/`); its locator range 117-155 was also
wrong (those pages are chapter text, checked by eye).

The PDF bookmark outline is complete and clean: 1,122 entries, ZERO
broken targets -- the easiest contents-less book so far. Hierarchy:

    depth 0   front matter (In Memory, Front Matter, Dedication,
              Contributors, Preface) + Volume-2-Cover + 33 Parts
    depth 1   519 chapters ("Chapter N -- Title")
    depth 2+  519 subsection/duplicate banners (kept out)

A one-off builder (recorded in `NELSON-2024-vis-outline.json`) took the
33 Parts as provinces and the 519 chapters as districts with
`_page_source = pdf-outline`. Part names were whitespace-normalized
("Part I -The Field" -> "Part I - The Field"); the "_compressed" suffix
on Part XXIX was removed -- a PDF-production artifact, verified by eye:
image 4065 prints "The Skin / PART XXIX".

Chapter numbers are NOT contiguous (1-770 with 251 gaps -- the 22nd
edition moved many chapters online). Verified by eye, not assumed:

- image 135 prints "Chapter 14 Injury Control" (outline: 9 -> 14 -> 16)
- image 158 prints "Chapter 17 Abused and Neglected Children"

Three more random spot-checks, all exact matches:

- image 1505 prints "Chapter 199 Systemic Lupus Erythematosus" (Part XIV)
- image 2232 prints "PART XVI The Digestive System / Chapter 351 Normal
  Digestive Tract Phenomena" (first chapter of Volume 2)
- image 4453 prints "PART XXXII Environmental Health / Chapter 757
  Overview of Environmental Health and Children"

MEASURED result -- chapters 1-770 (519 present, gaps are the book's
own numbering), every page from the book:

    Part I    - The Field of Pediatrics                      12 ch    44-158
    Part II   - Growth, Development, and Behavior             8 ch   180-228
    Part III  - Behavioral and Psychiatric Disorders          8 ch   261-331
    Part IV   - Learning and Developmental Disorders          5 ch   346-393
    Part V    - Nutrition                                     8 ch   435-530
    Part VI   - Fluid and Electrolyte Disorders               2 ch   532-580
    Part VII  - Emergency Medicine, Critical Care, Anesthesia 12 ch  581-723
    Part VIII - Human Genetics                                6 ch   772-842
    Part IX   - Metabolic Disorders                           8 ch   849-1026
    Part X    - The Fetus and the Neonatal Infant            24 ch  1038-1165
    Part XI   - Adolescent Medicine                          12 ch  1171-1253
    Part XII  - Immunology                                   17 ch  1265-1378
    Part XIII - Allergic Disorders                            7 ch  1380-1457
    Part XIV  - Rheumatic Diseases of Childhood              12 ch  1476-1577
    Part XV   - Infectious Diseases                          87 ch  1586-2228
    Part XVI  - The Digestive System                         53 ch  2232-2527
    Part XVII - The Respiratory System                       35 ch  2530-2736
    Part XVIII- The Cardiovascular System                    21 ch  2751-2933
    Part XIX  - Diseases of the Blood                        37 ch  2944-3101
    Part XX   - Cancer and Benign Tumors                     12 ch  3105-3188
    Part XXI  - Nephrology                                   11 ch  3215-3275
    Part XXII - Urologic Disorders in Infants and Children    6 ch  3295-3337
    Part XXIII- Gynecologic Problems of Childhood             4 ch  3352-3392
    Part XXIV - The Endocrine System                         24 ch  3394-3553
    Part XXV  - The Nervous System                           12 ch  3588-3820
    Part XXVI - Neuromuscular Disorders                       8 ch  3829-3946
    Part XXVII- Disorders of the Eye                         11 ch  3947-4016
    Part XXVIII- The Ear                                      6 ch  4021-4061
    Part XXIX - The Skin                                     17 ch  4065-4212
    Part XXX  - Bone and Joint Disorders                     19 ch  4235-4425
    Part XXXI - Rehabilitation Medicine                       6 ch  4428-4446
    Part XXXII- Environmental Health                          7 ch  4453-4505
    Part XXXIII- Laboratory Medicine (digital format only)     2 ch  4517-4522

Evidence:

    RESULT NELSON-2024 ok chapters=519 provinces=33 without_page=0
    - all 519 chapters get their page from the PDF's OWN bookmark outline
    Full library: 31/31 clean, 3,739 chapters total
    -- EVERY attempted book is clean; 6 books remain unread.

### DONE 2026-10-16 (j) -- MURRAY-7 read: 142 chapters, 3 Parts, validator CLEAN

Murray & Nadel's Textbook of Respiratory Medicine, 7th ed (2-volume set
in one PDF, 3,317 pages). FOURTH book with no printed table of contents
(cover -> dedication -> contributors -> preface -> chapter 1). Worse:
its PDF bookmark outline is only PARTIALLY usable -- 97 chapters have
valid bookmark targets, but 45 have BROKEN targets (`image: None`), and
their subsection bookmarks are broken too.

Recovered the 45 with ZERO model calls, from the book's own printed
pages, via the pdftotext layer:

1. The chapter opener prints the number and an ALL-CAPS TITLE at the top
   of its first page (verified by eye on chapter 3, image 75). Body
   running headers print only "PART N - <part name>", never chapter
   titles, so a title found near the top of a page IS the opener.
2. A first version ("title equals a whole line") found only 16/45; a
   second ("title inside the first 8 lines") found 45/45 but grabbed
   cross-references (e.g. "Influenza" inside chapter 46's text). The
   final rule walks the outline's OWN chapter order with a cursor: each
   missing chapter's start = first page after the previous chapter's
   start whose top mentions its title. Five KNOWN chapters were used as
   sanity anchors (3->75, 11->252, 46->980, 60->1374, 100->2324 -- all
   matched), and three recovered pages were opened by eye:
   - image  63 prints "2 LUNG GROWTH AND DEVELOPMENT" (chapter 2)
   - image 1082 prints "46a COVID-19"
   - image 1104 prints "47 INFLUENZA"
     (the book really prints COVID before influenza; outline order kept)
3. The 3 Parts come from each chapter's OWN running header (every one
   of the 142 chapters matched exactly one): Part 1 Scientific
   Principles (17 ch), Part 2 Diagnosis and Evaluation (18 ch),
   Part 3 Clinical Respiratory Medicine (107 ch).

`toc_validate.py` now also accepts the new honest page source
`text-top` (title printed at the top of the chapter's own first page),
and prints its count. MEASURED result:

    RESULT MURRAY-7 ok chapters=142 provinces=3 without_page=0
    - 97 of 142 chapters get their page from the PDF's OWN bookmark outline
    - 45 of 142 chapters get their page from the title printed at the TOP
      of the chapter's own first page
    Full library: 30/30 clean, 3,220 chapters total
    -- EVERY attempted book is now clean; 7 books remain unread.

### DONE 2026-10-16 (i) -- MILLER-10 read: 87 chapters, 8 Sections, validator CLEAN

Miller's Anesthesia, 10th ed (2-volume set in one PDF, 13,485 pages --
the biggest book in the library). The printed Table of Contents exists
(images 6-65) but carries NO page numbers -- it is a hyperlinked
navigation list of Section / chapter / subsection titles. The PDF
bookmark outline (932 entries) is clean and hierarchical:

    depth 0   front matter, Volume 1, Volume 2, Index
    depth 1   8 Sections (I-VIII)
    depth 2   87 chapters ("N. Title")
    depth 3   824 subsections (kept out of the geography)

A one-off builder took the 8 Sections as provinces and the 87 chapters
as districts with `_page_source = pdf-outline`. Chapter numbers 1-87
complete, none missing.

Spot-checked by opening two pages with my own eyes:
- image 681 prints "8: Consciousness, Memory, and Anesthesia" -- the
  first chapter of Section II -- matches the outline exactly
- image 12301 prints "83: Burn Management" -- the first chapter of
  Section VIII -- matches the outline exactly

MEASURED result -- chapters 1-87 complete, every page from the book:

    Section I.   INTRODUCTION                          7 ch   122-598
    Section II.  Anesthetic Physiology                19 ch   681-3651
    Section III. Anesthesia Management                20 ch  3697-6706
    Section IV.  Adult Subspecialty Management        25 ch  6823-10379
    Section V.   Pediatric Anesthesia                  4 ch 10540-11217
    Section VI.  Postoperative Care                    3 ch 11553-11809
    Section VII. Critical Care Medicine                4 ch 11870-12181
    Section VIII Ancillary Responsibilities/Problems   5 ch 12301-12659

Evidence:

    RESULT MILLER-10 ok chapters=87 provinces=8 without_page=0
    - all 87 chapters get their page from the PDF's OWN bookmark outline
    Full library: 29/29 clean, 3,078 chapters total
    -- EVERY attempted book is now clean; 8 books remain unread.

### DONE 2026-10-16 (h) -- MIDDLETON-2019 read: 99 chapters, 8 Sections, validator CLEAN (library now 28/28 clean)

Middleton's Allergy: Principles and Practice, 9th ed (2-volume set in
one PDF, 1,886 pages). THIRD book with NO printed table of contents --
the PDF runs cover -> copyright -> foreword -> preface -> contributors ->
straight into chapter 1 (image 18). The old October attempt had left 7
pages of "KIND=OTHER" in the transcript and a WARN with 0 chapters.

The PDF bookmark outline is complete (4,286 entries) and was used as the
book's own structure, exactly like MANDELL-9. Its hierarchy is messy
(chapters sit at depth 0 AND depth 1, front matter mixed in), so a
one-off builder took every outline entry at depth 0-1 matching "N Title"
(chapter) or "A-H Title" (section), deduplicated chapter numbers keeping
the first occurrence, and wrote `kitchen/logs/MIDDLETON-2019-vis-toc.json`
with `_page_source = pdf-outline` for all 99 chapters.

Spot-checked by opening two pages with my own eyes:
- image 678 prints SECTION E "Respiratory Tract", chapter 39 "The Nose
  and Control of Nasal Airflow" -- matches the outline exactly
- image 1487 prints SECTION H "Therapeutics", chapter 84 "Allergen
  Control for Prevention and Management of Allergic Diseases" -- matches

MEASURED result -- chapters 1-99 complete, every page from the book:

    A Basic Sciences Underlying Allergy and Immunology   25 ch  18-416
    B Aerobiology and Allergens                           6 ch  428-546
    C The Skin                                            6 ch  556-643
    D The Eye                                             1 ch  658-658
    E Respiratory Tract                                  25 ch  678-1127
    F Gastrointestinal Tract                              2 ch 1142-1153
    G Systemic Disease                                   18 ch 1165-1466
    H Therapeutics                                       16 ch 1487-1723

Evidence:

    RESULT MIDDLETON-2019 ok chapters=99 provinces=8 without_page=0
    - 99 of 99 chapters get their page from the PDF's OWN bookmark outline
    Full library: 28/28 clean, 2,991 chapters total
    -- EVERY attempted book is now clean; 9 books remain unread.

### DONE 2026-10-16 (g) -- MANDELL-9 read: 210 chapters, 4 Parts, validator CLEAN (no contents page in the PDF)

Mandell, Douglas & Bennett's Principles and Practice of Infectious
Diseases, 9th ed (2019). This is the SECOND book (after SLEISENGER-11)
with NO printed table of contents anywhere in the PDF. The library copy
(libgen scan, 4,895 pages) runs cover -> contributors -> preface ->
straight into Part 1, chapter 1: there is no contents page to find, and
no chapter hyperlinks to click. The locator (`toc_vision.py` locate,
images 1-120) honestly reported "no contents page found", as did the
wider scan.

The book's own PDF bookmark outline, however, is complete and exact:
11,527 entries, with Part banners at depth 0, section letters at depth 1
("A Microbial Pathogenesis", "A Fever", ...), and every chapter at depth
2 with its true first image. That is evidence from the book itself (Law
2), exactly like a hyperlink -- not a guess.

New one-off (recorded, then deleted; MANDELL-9's geography is written
from the outline into `kitchen/logs/MANDELL-9-vis-toc.json`):
depth-0 banners matching "I"/"II"/... become the 4 Parts, depth-2
chapter entries "N Title" become the chapters with `_page_source =
pdf-outline` and the outline's own image as `page_start`. 210 chapters,
numbers present as printed, every page from the book.

Spot-checked by opening two pages: chapter 55 (image 990) really opens
Part II "Major Clinical Syndromes" / Section A "Fever" / chapter 55
"Temperature Regulation and the Pathogenesis of Fever" -- matches the
outline exactly.

`toc_validate.py` now accepts a book whose every chapter page comes from
`pdf-outline` even when there is no raw TOC text to verify against
(the printed contents does not exist in this PDF); before this, such a
book was WARN for the missing TOC text. The evidence line is printed:

    RESULT MANDELL-9 ok chapters=210 provinces=4 without_page=0
    - all 210 chapters get their page from the PDF's OWN bookmark outline
    (this book has no printed contents to verify against)

MEASURED result -- numbers as printed, every page from the book:

    I   Basic Principles in the Diagnosis and Management   53 ch  29-989
    II  Major Clinical Syndromes                          76 ch 990-2266
    III Infectious Diseases and Their Etiologic Agents    59 ch 2267-4516
    IV  Special Problems                                  22 ch 4517-4895

Full library: 27/28 clean, 2,892 chapters. Only MIDDLETON-2019 remains
unread (as before).

### DONE 2026-10-16 (f) -- KAPLAN-11 read: 60 chapters, both Volumes, validator CLEAN

Kaplan & Sadock's Comprehensive Textbook of Psychiatry, 11th ed (16,525
pages). This book's contents prints NO page numbers and is a three-level
list: VOLUME -> integer chapter -> dotted sub-entries (1.1, 33.13a ...).
The reader transcribed all three levels as chapters (414 entries, only 50
plain integers 1-60 present) and printed 10 of the chapters themselves as
heading lines instead of chapter lines, because their sub-entries follow
them. Repaired with ZERO model calls beyond the original read and one
`toc_fill_gaps.py` call:

1. NEW `toc_split_subsections.py` -- moves the 376 dotted sub-entries to
   `kitchen/logs/KAPLAN-11-vis-subsections.json` (recorded with their
   parent chapter, never dropped), and re-reads the 10 heading lines the
   reader printed as "P  3  Contributions of the Psychological Sciences"
   as the chapters they are -- number AND title are the model's own
   recorded words, nothing invented. Result: 60 chapters, numbers 1-60
   complete.
2. `toc_links.py` -- 49 chapters got their true first page from the
   contents pages' own clickable hyperlinks (`_page_source = pdf-link`).
3. `toc_outline.py` -- the PDF bookmark outline filled the remaining 11
   pages (`_page_source = pdf-outline`), and corrected ONE title where the
   reader had answered with a sub-entry's title: chapter 11 is
   "Substance-Related Disorders" (PDF outline AND the contents heading
   both say so), not "Anabolic-Androgenic Steroid-Related Disorders"
   (= sub-entry 11.11). The change is recorded in
   `KAPLAN-11-vis-outline.json` under `title_corrections`.
4. `toc_outline.py --regroup` -- rebuilt the provinces from the outline's
   two printed banners, IN THE BOOK'S OWN ORDER. The book prints nothing
   between VOLUME and chapter, so the geography keeps exactly the 2
   printed volumes -- the same depth decision made for CAMPBELL-2020.

MEASURED result -- numbers 1-60 complete, every page from the book:

    VOLUME I    26 chapters   1-26
    VOLUME II   34 chapters   27-60

Evidence:

    RESULT KAPLAN-11 ok chapters=60 provinces=2 without_page=0
    - 49 of 60 chapters get their page from the book's OWN PDF chapter link
    - 11 of 60 chapters get their page from the PDF's OWN bookmark outline
    Full library: 26/27 clean, 2682 chapters total
    (only MIDDLETON-2019 still unread, as before)

### DONE 2026-10-16 (e) -- IRWIN-RIPPE-2023 read: 215 chapters, 20 Sections, validator CLEAN

Irwin & Rippe's Intensive Care Medicine, 13th ed -- the biggest book yet
(7,992 pages). The contents was found and read (images 75-98, 24 pages,
KIND=CHAPTERS, NOPAGES: this book prints NO page numbers in the contents),
but the automated heading pass afterwards produced a broken geography: 250
chapters for 189 unique numbers, chapters 1-26 missing entirely, and
"Section 3" holding 94 chapters that belonged to Sections 7-10.

Rebuilt from the saved transcript and the PDF itself, zero model calls:

1. `toc_reparse.py` -- the transcript holds chapters 1-215 complete,
   nothing was ever lost from it (the transcript is safe; the JSON was
   the broken part).
2. `toc_links.py` -- the contents pages carry clickable hyperlinks:
   237 matched, 215 chapters got their true first page from the book
   itself (`_page_source = pdf-link`), zero conflicts.
3. NEW `toc_outline.py --regroup` -- the PDF outline's 23 banner entries
   rebuilt the provinces IN THE BOOK'S OWN ORDER, and this book prints
   the Section titles in the outline, so every province now carries its
   full title (the rebuilt JSON previously said bare "Section 2" etc.).

MEASURED result -- numbers 1-215 complete, every page from the book,
validator ok:

    Section 1  Procedures, Techniques and Ultrasonography   26 ch  1-26
    Section 2  Minimally Invasive Monitoring                 5 ch 27-31
    Section 3  Palliative Care and Ethical Issues            4 ch 32-35
    Section 4  Shock, Trauma and Sepsis Management          10 ch 36-45
    Section 5  Surgical Problems in the ICU                  9 ch 46-54
    Section 6  Transplantation                              10 ch 55-64
    Section 7  Rheumatologic, Immunologic, Dermatologic      5 ch 65-69
    Section 8  Infectious Disease Problems                  17 ch 70-86
    Section 9  Hematologic and Oncologic Problems            9 ch 87-95
    Section 10 Pharmacology, Overdoses and Poisonings       30 ch 96-125
    Section 11 Critical Care Consequences of Weapons         4 ch 126-129
    Section 12 ICU Design, Organization, Operation           6 ch 130-135
    Section 13 Endocrine Problems                            8 ch 136-143
    Section 14 Neurologic Problems                          13 ch 144-156
    Section 15 Psychiatric Issues                            6 ch 157-162
    Section 16 Pulmonary Problems                           23 ch 163-185
    Section 17 Cardiovascular Problems and Coronary Care    12 ch 186-197
    Section 18 Renal Problems                                6 ch 198-203
    Section 19 Gastrointestinal Disease Problems             9 ch 204-212
    Section 20 Metabolism and Nutrition                      3 ch 213-215

**EVIDENCE** (2026-10-16, `cd ~/second-opinion && source .venv/bin/activate`):

```
$ python kitchen/toc_validate.py IRWIN-RIPPE-2023 --vis
       - 215 of 215 chapters get their page from the book's OWN PDF chapter link
RESULT IRWIN-RIPPE-2023 ok chapters=215 provinces=20 without_page=0

$ python kitchen/toc_validate.py --vis
25/26 clean, 2622 chapters total
```

Chapter totals rose 2,407 -> 2,622 exactly by IRWIN's 215 chapters.
The 26th book (MIDDLETON-2019) still has 0 chapters -- never read.
Backup of the broken JSON kept as IRWIN-RIPPE-2023-vis-toc.before-rebuild.json.

### DONE 2026-10-16 (d) -- HAZZARD-2022 read: 108 chapters, 23 provinces, validator CLEAN; two pipeline bugs caught and fixed

Hazzard's Geriatric Medicine and Gerontology, 8th ed. The contents pages
(images 6-12, 69) print chapter numbers, titles and authors but NO page
numbers anywhere -- checked by eye on the page image, not only by the
model. The reader honestly answered NOPAGES on 4 of the 8 pages, but on
the other 4 it copied the CHAPTER number into the page column (chapter 88
-> "page 88"). Those 19 invented pages then triggered two bugs:

1. `toc_strip_online_only.py` treated the book as "has pages" and
   DELETED the 109 honest page-less chapters from the transcript, and its
   second run overwrote the evidence file with count=0. FIXED (general):
   a page carried on a NOPAGES page, or equal to its own chapter number,
   is cleared (recorded in <BOOK_ID>-online-only.json under
   "cleared_invented_pages"), never trusted; page-less chapters are
   stripped only when they are a small minority (<= 1/3); a page with
   `_page_source = pdf-link` is evidence and is never cleared.
2. Pages for this book cannot come from the contents at all. They came
   from the PDF ITSELF, two general zero-cost tools:
   - `toc_links.py` (already existed): 92 clickable hyperlinks, 64
     chapters matched;
   - NEW `kitchen/toc_outline.py`: the PDF's bookmark outline holds 140
     entries -- every Part, Section and CHAPTER with its true first
     page. 64 more chapters filled (`_page_source = pdf-outline`), and
     with `--regroup` the 24 outline banners rebuild the provinces in
     the book's own order (the contents reading had duplicated Section
     names across Parts). `toc_validate.py` learned that an outline page
     is book evidence, same as a link page.
3. Chapters 31-32 were skipped by the reader; `toc_fill_gaps.py` asked
     for that gap by name and the model returned both.

MEASURED result -- numbers 1-108 complete, every page from the book
itself, validator ok:

    Part I   Principles of Gerontology                    6 ch   1-6
    Part II  Principles of Geriatrics                     1 ch   7-7
    SECTION A-G (under Part II)                         31 ch   8-38
    Part III Geriatric Conditions                        3 ch  39-41
    SECTION A-C (under Part III)                        25 ch  42-66
    Part IV  Principles of Palliative Medicine and Ethics 6 ch  67-72
    SECTION A-I (under Part IV)                         36 ch  73-108

**EVIDENCE** (2026-10-16, `cd ~/second-opinion && source .venv/bin/activate`):

```
$ python kitchen/toc_validate.py HAZZARD-2022 --vis
       - 64 of 108 chapters get their page from the book's OWN PDF chapter link
       - 44 of 108 chapters get their page from the PDF's OWN bookmark outline
RESULT HAZZARD-2022 ok chapters=108 provinces=23 without_page=0

$ python kitchen/toc_validate.py --vis
24/25 clean, 2407 chapters total
```

Chapter totals rose 2,299 -> 2,407 exactly by HAZZARD's 108 chapters.
The 25th book (MIDDLETON-2019) still has 0 chapters -- never read.

### DONE 2026-10-16 (c) -- GREEN-HAND-2021 read end to end: 60 chapters, 8 Parts, validator CLEAN

Green's Operative Hand Surgery (2 volumes, 2,535 images). The contents
finder scanned the first 120 images in 6-page sheets and honestly
reported no contents page, so the book was read by the OPENER method
(toc_openers.py): the whole book shown to the model as contact sheets,
every page that opens a chapter named by the model, then each such page
read alone at 150 dpi. 64 openers found, 60 chapters kept.

MEASURED result -- numbers 1-60, complete, missing=[], every page printed
by the book (validator: without_page=0):

    PART I    Basic Principles                        1 ch   1-1
    PART II   Hand                                   10 ch   2-11
    PART III  Wrist                                   6 ch  12-17
    PART IV   Elbow and Forearm                      10 ch  18-27
    PART V    Nerves                                  7 ch  28-34
    PART VI   Pediatric Hand                          7 ch  35-41
    PART VII  Bone and Soft Tissue Reconstructions    7 ch  42-48
    PART VIII Other Disorders of the Upper Extremity 12 ch  49-60

Three general tool improvements came out of this book (no book-specific
code anywhere):

1. `toc_vision.py` and `toc_headings.py` prompts now say: copy every
   heading EXACTLY as the book prints it -- number kept if printed, title
   kept if printed, never invent a number, never drop a printed one.
2. `toc_openers_build.py` found the 5 chapters the sheet scan had walked
   past (24, 42, 48, 56, 57) by asking the model page by page inside each
   gap ("does this page open chapter N?"), and recovered a 60th chapter
   ("Vascular Disorders of the Hand") that the first scan had refused.
3. `toc_group_parts.py` learned to read the RUNNING HEADER of the
   ordinary page AFTER an opening page: this book prints no part banner
   and not even a header on its chapter-opening pages -- I looked at the
   page image myself and confirmed it -- so the part name was only
   obtainable from the header of the pages inside the chapter (e.g.
   "1664 PART VII Bone and Soft Tissue Reconstructions"). 28 of 54
   bannerless openers recovered this way. Also fixed: an answer of
   "PART=-" was being stored as a part named "=-".

Nir was watching live throughout (watchdog heartbeat every 60s in
kitchen/logs/GREEN-HAND-2021-watchdog.log).

**EVIDENCE** (2026-10-16, `cd ~/second-opinion && source .venv/bin/activate`):

```
$ python kitchen/toc_validate.py GREEN-HAND-2021 --vis
RESULT GREEN-HAND-2021 ok chapters=60 provinces=8 without_page=0

$ python kitchen/toc_validate.py --vis
23/24 clean, 2299 chapters total
```

Backups: kitchen/logs/backup-16oct-green/. The 24th book (MIDDLETON-2019)
still has 0 chapters -- never read. Chapter totals rose 2,239 -> 2,299
exactly by GREEN-HAND's 60 chapters; nothing else changed.

### DONE 2026-10-16 (b) -- GOODMAN-14 named from the printed contents; both queued books now done

GOODMAN-14 came out of the reader with three provinces carrying no number
("General Principles", "Neuropharmacology", "Modulation of Pulmonary,
Renal, and Cardiovascular") and six carrying a number without the
" - " connector. The book was verified page by page before any change:

- PDF page 8 of the contents (seen as an IMAGE by the manager, not only
  as text) prints the banners on their own line: "Section I" /
  "General Principles" 1, "Section II" / "Neuropharmacology" 171,
  "Section III" / "Modulation of Pulmonary, Renal, and Cardiovascular" 555.
- The Section III title looks cut off, but it is NOT: the book prints the
  exact same words on the contents AND on Section III's own opening page
  (printed page 555, raw text line 72508: "Modulation of Pulmonary,
  Renal, / and Cardiovascular / III / Section"). Nothing was invented; the
  title is kept verbatim as printed (Law 3).
- Section IV's title was also checked in the contents (page viii):
  "Inflammation, Immunomodulation, and Hematopoiesis" -- complete as we
  had it; only the connector was missing.

`kitchen/toc_fix_names.py` gained ONE general rule (no book-specific
code): when a province's title is EXACTLY a title the printed contents
puts beside a numbered banner on its own line, the number is recovered
from that banner and recorded as `toc_page` if the book prints a page
beside the heading. A province whose title is never printed beside a
number ("Appendices") stays reported and unnumbered -- KRAUSE-16's
"APPENDICES" is treated by the same rule (Nir's uniformity order).

Target form reached for all 10 provinces:

```
Section I   - General Principles                    (9 ch,  contents page 1)
Section II  - Neuropharmacology                    (19 ch,  contents page 171)
Section III - Modulation of Pulmonary, Renal, and Cardiovascular (9 ch, contents page 555)
Section IV  - Inflammation, Immunomodulation, and Hematopoiesis  (8 ch, contents page 747)
Section V   - Endocrine Pharmacology                (7 ch,  contents page 921)
Section VI  - Gastrointestinal Pharmacology         (3 ch,  contents page 1071)
Section VII - Chemotherapy of Infectious Diseases  (13 ch,  contents page 1125)
Section VIII- Pharmacotherapy of Neoplastic Disease (5 ch,  contents page 1335)
Section IX  - Special Systems Pharmacology          (3 ch,  contents page 1451)
Appendices                                        (2 ch,  no number printed)
```

**EVIDENCE** (2026-10-16, `cd ~/second-opinion && source .venv/bin/activate`):

```
$ python kitchen/toc_fix_names.py --all          # dry run over ALL books
  (dry run -- 0 name(s) would change and 6 contents page(s) recorded)
--- total provinces renamed: 0
--- structure still to fix -> GOODMAN-14: ['Appendices']
--- structure still to fix -> KRAUSE-16: ['APPENDICES']

$ python kitchen/toc_fix_names.py GOODMAN-14 --apply
  WRITTEN: 0 name(s) changed, 6 contents page(s) recorded
  (the 9 names were written by the earlier run of the same session)

$ python kitchen/toc_validate.py --vis
RESULT GOODMAN-14 ok chapters=78 provinces=10 without_page=0
22/23 clean, 2239 chapters total
```

Chapters unchanged (78 before and after). Only Goodman and KRAUSE have an
unnumbered province at all, and both are Appendices, which the books
number never -- reported, not guessed.


### DONE 2026-10-16 (a) -- GRAY-2020 folded to 9 clean Sections; no side files, one rule for all books

GRAY-2020 printed SECTION banners ("SECTION 4: HEAD AND NECK") with smaller
unnumbered headings ("Head and neck", "Upper aerodigestive tract", "Special
senses") inside them. The reader had kept both as sibling provinces, so the
book came out as 17 provinces, 8 of them fragments of a Section that already
existed.

The fold rule is the book's own layout, never a guess: an unnumbered
province joins the numbered province printed ABOVE it, in chapter-number
order. MEASURED result -- every group is contiguous, which is the proof the
fold is right:

| folded heading | into | chapters |
|---|---|---|
| Head and neck, Upper aerodigestive tract, Special senses | Section 4 - HEAD AND NECK | 33-45 |
| Lungs and respiratory diaphragm, Heart and mediastinum | Section 7 - THORAX | 52-58 |
| Gastrointestinal tract, Abdominal viscera, Urogenital system | Section 8 - ABDOMEN AND PELVIS | 59-75 |

**Nir's UNIFORMITY order (2026-10-16): every book is treated the SAME way,
as similar as possible -- no book gets an extra file the others do not
have.** A side file for Gray's folded headings was therefore NOT kept; it
was deleted, and the tool that would have written it was changed so no book
ever gets one. The folded names remain in the 16 Oct backup and in the
book's own printed contents, both of which we hold.

Also measured for Nir: GRAY-2020's 79 chapters are typical (median across
the 22 read books = 83; range 20 THOMPSON to 505 HARRISON).

Tool: `kitchen/toc_fold_subsections.py` (dry run by default, --apply to
write, refuses to write if the chapter count would change, reports
"nothing to do" when re-run).

**EVIDENCE** (2026-10-16, `cd ~/second-opinion && source .venv/bin/activate`):

```
$ python kitchen/toc_fold_subsections.py GRAY-2020 --apply
  fold  'Head and neck' (3 ch)               -> 'Section 4 - HEAD AND NECK'
  fold  'Upper aerodigestive tract' (5 ch)   -> 'Section 4 - HEAD AND NECK'
  fold  'Special senses' (4 ch)              -> 'Section 4 - HEAD AND NECK'
  fold  'Lungs and respiratory diaphragm' (2 ch) -> 'Section 7 - THORAX'
  fold  'Heart and mediastinum' (3 ch)       -> 'Section 7 - THORAX'
  fold  'Gastrointestinal tract' (3 ch)      -> 'Section 8 - ABDOMEN AND PELVIS'
  fold  'Abdominal viscera' (5 ch)           -> 'Section 8 - ABDOMEN AND PELVIS'
  fold  'Urogenital system' (5 ch)           -> 'Section 8 - ABDOMEN AND PELVIS'
  chapters 79 -> 79 (unchanged), provinces 17 -> 9

$ python kitchen/toc_fold_subsections.py GRAY-2020     # re-run: safe
GRAY-2020: no loose sub-headings -- nothing to do

$ python kitchen/toc_validate.py --vis
RESULT GRAY-2020 ok chapters=79 provinces=9 without_page=0
22/23 clean, 2239 chapters total
```

Chapter total unchanged from 14-15 Oct (2,239); no chapter lost or
invented. Backup taken BEFORE the change:
`kitchen/logs/backup-16oct-before-fold/GRAY-2020-vis-toc.json`.
The 23rd book (MIDDLETON-2019) still has 0 chapters -- never read.

### DONE 2026-10-15 (late evening) -- SIX MORE BOOKS GIVEN REAL PARTS; PIPELINE BUGS FIXED

Six of the 22 read books had a province level that was useless, and five
pipeline bugs were found by running the honest validator. **Nothing was
guessed; every number below comes from a script run.**

**THE SIX BOOKS:**

| Book | before | after |
|---|---|---|
| FIRESTEIN-12 | 2 provinces ("Volume 1/2", no meaning) | **18 parts**, each "Part n - Title" |
| BOLOGNIA-2024 | 1 province ("Volume 1", 161 chapters in one blob) | **22 sections**, "Section 5 - Vesiculobullous Diseases" |
| ROCKWOOD-10 | 2 provinces | **4 sections**, word-numbers kept as printed ("Section TWO - UPPER EXTREMITY") |
| ROBBINS-10 | 1 province ("ALL") | **6 written parts** |
| THOMPSON-2023 | 1 province ("ALL") | **4 written parts** |
| BRENNER-11 | 1 province ("ALL") | **18 written parts** |

For ROBBINS-10, THOMPSON-2023 and BRENNER-11 the author printed no Part
banner at all, so the parts were WRITTEN by us per the human's order of
15 Oct (late evening). They are stored in `kitchen/parts/<BOOK>.json`,
applied by `kitchen/toc_group_flat.py`, and every province carries
`name_source: "written"`.

**THE FIVE BUGS, each measured, each fixed:**

1. `toc_apply_headings.py` picked VOLUME whenever any volume banner
   existed, even though "VOLUME I" is bare and the titled "SECTION n"
   banners below it are the real geography (BOLOGNIA, ROCKWOOD, FIRESTEIN).
   It now falls to the next kind that carries titles, and keeps the
   transcript's own numbered, titled provinces when the banner read was
   incomplete. Also `first` was tested with `if f`, so a chapter numbered
   0 read as None.
2. `toc_dedupe.py` flattened EVERY book into one province called "ALL",
   destroying the 18 Part provinces reparse had just built from the
   reader's own words. It now keeps the provinces.
3. `toc_reparse.py` recorded image->province by INDEX while parsing and
   empty provinces were dropped afterwards, so the indices went stale and
   reassign filed chapters into the wrong Part (99 of FIRESTEIN's 125
   chapters). The map is now derived from the data itself.
4. `toc_dedupe.py`'s reassign then over-corrected: one contents page
   carries several Parts, so "page -> one province" is false. The stray
   test now uses the last province's longest consecutive run of chapter
   numbers and files by nearest chapter number, then nearest page.
   A stray already sitting where its page belongs is left alone --
   appending to the list being iterated never ended and BOLOGNIA's
   dedupe spun forever (fixed after it hung for 600 s).
5. **`toc_reparse.py` could DELETE a whole book.** BRENNER-11's saved
   transcript is a field list of PART/NUM/TITLE/PAGE, not the reader's
   P/C lines, so re-parsing wrote an EMPTY document and wiped all 71
   chapters. Only the 15 Oct backup happened to hold them. The parser now
   checks for P/C lines first and leaves the existing document untouched
   when there are none. **This is why every rebuild must be run against
   the backup directory.**
6. `toc_fix_names.py` did not recognise word-numerals; "SECTION ONE:
   GENERAL PRINCIPLES" was reported NOT NUMBERED. ONE..TWENTY and the
   tens are now accepted, and the word is kept exactly as printed.

**EVIDENCE** (all run 2026-10-15, `cd ~/second-opinion && source
.venv/bin/activate`):

```
$ python kitchen/toc_validate.py --vis
22/23 clean, 2239 chapters total

$ python kitchen/toc_validate.py FIRESTEIN-12 BOLOGNIA-2024 ROCKWOOD-10 \
      ROBBINS-10 THOMPSON-2023 BRENNER-11 --vis
RESULT FIRESTEIN-12    ok chapters=125 provinces=18
RESULT BOLOGNIA-2024   ok chapters=161 provinces=22
RESULT ROCKWOOD-10     ok chapters= 69 provinces= 4
RESULT ROBBINS-10      ok chapters= 29 provinces= 6
RESULT THOMPSON-2023   ok chapters= 20 provinces= 4
RESULT BRENNER-11      ok chapters= 71 provinces=18

230 provinces across the 22 read books
```

Chapter totals are unchanged from 14 Oct (2,239), so no chapter was lost
or invented by any of this. The 23rd book (MIDDLETON-2019) still has 0
chapters -- never read.

Commits: `6dc4a47`, `89dbb1a`, (guard), `8aa8999` -- all pushed.

### DONE 2026-10-14 (b) -- KRAUSE-16 FIXED, GRAY-2020 CLEANED, ALL 22 BOOKS VERIFIED

**Nir found the bug by looking at the actual PDF himself.** He opened
GRAY-2020 and saw a perfect contents on pages 8-11. He asked why we had
reported "154 chapters, pages went backwards" when the book clearly prints
a clean list. He was right to be angry: the model HAD read pages 8-11
correctly (all 81 chapters in the transcript), but the pipeline that ran
afterward mangled it.

**What was actually wrong, found by reading the logs not guessing:**

1. **GRAY-2020** -- the build log showed 154 chapters with pages going
   backwards. The cause was in `toc_apply_headings.py`: the book prints
   "SECTION 1" on image 27 AND "SECTION 1 CELLS, TISSUES AND SYSTEMS" on
   images 28 and 29 (the same section repeated across pages), and the
   heading-application step created duplicate provinces. The final
   `vis-toc.json` on disk (rebuilt later on 14 Oct) was already correct --
   81 chapters, pages in order. The 154-chapter mess was a stale build
   artifact.

2. **GRAY-2020 supplementary chapters removed.** Chapters 80 and 81
   ("The anatomy of the peripheral nervous system" and "The anatomy of the
   vascular and lymphatic systems") print NO page number in the contents --
   checked by eye on the rendered image (`kitchen/pages/GRAY-2020/vis/read-11/p-0011.png`).
   Nir looked at the book himself, saw the small "S" icon next to them,
   concluded they are supplementary, and ordered them removed. Done.
   GRAY-2020 is now **17 provinces / 79 chapters, all with pages, validator ok**.

3. **KRAUSE-16 was still broken and is now fixed.** The model had read it
   perfectly (5 pages, 93 entries in the transcript), but two things went
   wrong in post-processing:
   * The APPENDICES restart their own numbering at 1, colliding with
     chapters 1-45. The dedup step saw "chapter 1 appears twice" and
     deleted the appendices. Fixed by renumbering appendices A1-A48.
   * **A bug in `toc_vision.py`'s FRONT_WORDS regex**: `\bindex\b` matched
     the word "Index" inside "Body Mass Index Table" and "Glycemic Index
     and Glycemic Load of Selected Foods" and threw both away. The regex
     now only treats "Index" as front matter when it is the WHOLE title or
     starts it ("Index", "Index of Terms"). KRAUSE-16 is now
     **7 provinces / 93 chapters (45 chapters + 48 appendices), validator ok**.

4. **All 22 read books re-verified with an automated scan.** Every
   `vis-toc.json` was checked for: duplicate chapter numbers, pages going
   backwards, missing page numbers, duplicate province names. Only
   KRAUSE-16 failed (fixed above). Result: **22 of 23 books clean,
   2,239 chapters total.** The 23rd (MIDDLETON-2019) has 0 chapters --
   never read.

**EVIDENCE:**

```
$ python kitchen/toc_validate.py --vis
  KRAUSE-16                  ok  prov=  7 chap=  93 pages 2-1211
  GRAY-2020                  ok  prov= 17 chap=  79 pages 4-1447
  ...
  22/23 clean, 2239 chapters total
```

**THE 15 BOOKS NOT YET READ:**
GREEN-HAND-2021, HAZZARD-2022, IRWIN-RIPPE-2023, KAPLAN-11, MANDELL-9,
MIDDLETON-2019, MILLER-10, MURRAY-7, NELSON-2024, OXFORD-6, ROSEN-2022,
STAHL-2024, WILLIAMS-ENDO-2024, WILLIAMS-HEMATOLOGY-2021, YOUMANS-4.

**Nir's standing orders (14 Oct):**
* One book at a time. Never launch a batch queue again unless he asks.
* When a book is finished, say so clearly with evidence.
* When something is wrong, look at the ACTUAL logs and images, not guesses.

### 2026-10-13, 12:00 -- BRANT-5 RECOVERED (83 chapters), TWO FALSE "CLEAN" VERDICTS KILLED, QUEUE OF 23 BOOKS LAUNCHED

**1. BRANT-5 was never a broken book -- our parser threw it away.**
Yesterday's handoff left BRANT-5 as "17 provinces and 0 chapters". The
transcript on disk held **84 chapter lines, all correct**. I opened the
rendered page myself (`kitchen/pages/BRANT-5/vis/read-36/p-0036.png`) and
confirmed what the reader had said: BRANT-5 prints a real contents with
**NO page numbers anywhere** ("9 Spine Imaging", "SECTION III / CHEST",
"10 Methods of Examination..."). Two faults followed from that:

  * `toc_vision.parse()` demanded a page number and threw away every entry
    without one. It now keeps the entry with `page_start = null`. A page that
    is not printed is never invented (Law 2); an entry that IS printed is
    never dropped either. The read prompt no longer contradicts itself (it
    said "leave that entry out" while the NOPAGES rule said keep it).
  * **The build still said `validator: CLEAN` with 0 chapters.** The verdict
    searched the word " clean" inside the validator's own output and found it
    in the summary line `0/1 clean`. `toc_validate.py` now prints one
    machine-readable `RESULT <BOOK_ID> ok|warn ...` line per book,
    `build_book.py` reads that line, and **0 chapters is a FAILED build**.
    `build_queue.py` also records the chapter count in the ledger, because
    "clean=True" alone cannot tell an empty book from a full one.

  BRANT-5 is now **12 sections / 83 chapters**, and the section sizes match the
  book's own banner layout exactly (I:1, II:8, III:8, IV:6, V:7, VI:12, VII:7,
  VIII:3, IX:5, X:10, XI:6, XII:10 = 83). Its 83 chapters print **no page**,
  which the validator reports as a warning and not as an invented number. The
  pages will come from the book itself in Part 4. The book's own chapter
  numbers include letters (32A, 36B, 71A, 72D), which is why "missing numbers"
  32/36/37/71/72 are not missing chapters.

**2. Two more faults found while rebuilding it, both general:**
  * `toc_apply_headings.py` died with `int("32A")`. Chapter numbers with a
    letter suffix are now read as their digits.
  * SECTION XII prints no chapter under its banner (its chapters are on the
    next contents page), so the model answered NONE. Deriving the number from
    the remaining chapter list gave **66 and swallowed six paediatric
    chapters**. The reader's own transcript says the banner is followed by
    **71A**, so the transcript is now authoritative for that question and the
    guess is not used.
  * The provinces were being thrown away at the end of a `--no-gaps` build
    (the last reparse starts again from the transcript, which is flat), so
    the headings step now always runs LAST.

**3. FIRESTEIN-12's one warning was a hallucination, and it is now caught by a
general rule.** The validator reported `p574 -> p452 at 'Cytokines and
Chemokines'`. The gap repair had answered "**28** Occupational Therapy,
Physical Therapy, and Rehabilitation **574**" -- the exact title and page the
contents already prints for **chapter 38**. Two chapters cannot start on the
same printed page with the same title, so `toc_reparse.py` now refuses any
entry that repeats another entry's (title, page) under a different number and
writes it to `<BOOK_ID>-vis-copytitles.json`. Related: an entry the reader
gives with an **empty** page field is now recorded in
`<BOOK_ID>-online-only.json` and kept out of the geography when the book
prints pages elsewhere (it was quietly entering the map as an unplaceable
chapter). Result: **FIRESTEIN-12 = 2 volumes / 125 chapters / pages 1-2229 /
validator ok**, with 5 chapters (2, 6, 28, 78, 79) **reported as still
missing, not invented**.

**4. `build_book.py` threw option values away.** It kept only the `--word`
arguments, so `--windows 40` reached `toc_vision.py` as `--windows` and the
book was read with the default 20 windows -- the documented next step for
BRADDOM-6 and BRENNER-11 could not actually be taken. Values are passed
through now, in `build_book.py` and in `build_queue.py` (which also takes
`--windows` and `--start`). `build_book.py --no-read` rebuilds a book from
the transcription already on disk for **zero model calls**, which is how
BRANT-5 was recovered. A book with no contents page found now stops with one
clear line instead of six FileNotFoundErrors.

**5. A queue of the remaining 23 books is running unattended**
(`kitchen/logs/queue3.log`, ledger `kitchen/logs/build_queue_verdicts.json`):
the six books the validator flagged on 11 Oct (ROCKWOOD-10,
WILLIAMS-OBSTETRICS-26, WILLIAMS-ENDO-2024, MIDDLETON-2019, KRAUSE-16,
THOMPSON-2023), GRAY-2020 (interrupted by the shutdown), the 14 books never
attempted, and last the two hard ones BRADDOM-6 and BRENNER-11.

STATE: **15 books read with the model's eyes** (13 fully clean, BRANT-5 clean
but with no printed pages), 1701+ chapters.

### 2026-10-12, 17:30 -- END OF SESSION. See HANDOFF-2026-10-12-evening.md

Eight more books were read with the model's eyes and pass the validator, so
the library now has **14 books read and verified** (HARRISON-22 505,
BOLOGNIA-2024 161, DEVITA-12 107, SLEISENGER-11 132, BRAUNWALD-12 102,
SABISTON-22 92, BENZON-2023 86, GUYTON-2026 85, CAMPBELL-2020 82,
AVERY-2021 61, ADAMS-12 49, ROBBINS-10 29, plus the four re-verified).

**BRAUNWALD-12 was on the hard list** -- its contents prints no text layer at
all -- and the vision path read it with no difficulty: 11 sections, 102
chapters, validator clean.

**THE FAULT THE HUMAN FOUND (this is the important one).** SABISTON-22
prints its real contents on images 35-38 and then a **VIDEO CONTENTS** list
in the same two-column layout, with the same section numbers I to XI and the
same chapter numbers. Nir opened the pages and saw it. The reader had turned
"Video 110.1 Pleural Effusion" into a chapter with a page number printed
nowhere in the book -- precisely the invented-page fault BIBLE part 3
section 4.4 exists to catch. **The reader now declares `KIND=CHAPTERS` or
`KIND=OTHER` before transcribing anything, and an OTHER page is refused and
reported, never used.** The same guard was added to `toc_reparse.py` (which
otherwise brought the video chapters back) and to `toc_headings.py` (which
had rebuilt the book with 187 chapters instead of 92 by reading banners off
the refused pages).

**AND THE FAULT THAT GUARD CAUSED, found only by looking with my own eyes.**
BRANT-5 prints a contents with **no page numbers anywhere**, and six of its
eight contents pages were refused with `KIND=OTHER`. Refusing a real contents
page loses the whole book. A refused page is now shown to the model a second
time -- "is this the chapter list, even if it prints no page numbers?" -- and
only a second refusal is honoured.

**THREE MORE FAULTS, ALL FIXED:**
  * The gap repair invented a page for an "(online only)" chapter, producing
    chapter 50 with page_start 50 -- the chapter number copied into the page
    column. `toc_strip_online_only.py` now removes such entries from the
    geography and records them in `kitchen/logs/<BOOK_ID>-online-only.json`,
    so they are never silently lost. They get their page in Part 4.
  * A two-column contents read right-column-first filed chapters 68-72 of
    SABISTON-22 (printed pages 819-906, belonging to SECTION V which starts
    at page 721) under SECTION IX which starts at page 1579.
    `toc_fix_misfiled.py` moves such a trailing run to the section whose own
    printed banner page claims it.
  * Re-running `toc_apply_headings.py` on an already-built JSON double-counts
    (187 chapters for a 92-chapter book). `build_book.py` always runs the
    full chain in order.

**THE HUMAN'S ORDER, NOW BUILT INTO THE TOOLS:** "do not stop and ask in the
middle of a book ... this burns our whole day on you waiting". So
`kitchen/build_book.py` takes one book from PDF to a verified verdict in a
single command, and `kitchen/build_queue.py` runs book after book
unattended, reporting a verdict per book. Measured cost: **4 to 15 minutes a
book, 8 books in about 50 minutes.** The human still wants progress reports
while it runs, and gets them.

**ONE BOOK WAS INTERRUPTED BY THE LAPTOP BEING CLOSED (12 Oct, Nir's
note).** A second queue was running: BRANT-5, BRADDOM-6, BRENNER-11,
DEVITA-12, FIRESTEIN-12, GRAY-2020. **FIRESTEIN-12 finished before the
shutdown and is clean** (566s) -- validate it and count it in, do not rebuild
it. **GRAY-2020 did not finish**: it was stopped inside `toc_vision.py`
before any JSON was written, so there is no half-written file to clean up
and it must simply be built again with `python kitchen/build_book.py
GRAY-2020`. STANDING RULE: a detached job killed by a shutdown leaves no
verdict, so a book with no `>>>` line in the queue log and no entry in
kitchen/logs/build_queue_verdicts.json was NOT finished -- re-run it.
Re-running is always safe because toc_reparse.py rebuilds from the
transcript before every apply.

**VERIFIED CLEAN, NO ACTION NEEDED:** all six books finished before today
were re-validated after the script changes and are unchanged; a scan of every
recorded page of the four earlier books for "video / podcast / online only /
index / contributors" found no contamination (the three Campbell hits are
real chapter titles, "Video-Assisted Thoracic Surgery"); the invented-page
signature (page_start == chapter number) was checked on every book and the
only hits are chapter 1 on page 1, which is true. GUYTON-2026's lost heading
file was regenerated and it is back to 15 units / 85 chapters.

**STILL OPEN, IN ORDER (section 7 of the handoff has the detail):**
  1. **BRANT-5** -- the guard fix stopped the refusals, but the model now
     returns only section banners and zero chapters. The read prompt still
     says to leave out an entry whose page number cannot be seen, and this
     book's contents prints none. Fix in this order: add a `NOPAGES` marker
     to the prompt, then a prompt asking for `C<TAB>number<TAB>title` with no
     page field at all, then `toc_openers.py`. Never invent a page.
  2. **BRADDOM-6 and BRENNER-11** -- no contents located in the first 120
     images. Try `--windows 40`, then `toc_openers.py`. Do not ask Nir to
     open these by hand yet; the openers path is untried on both.
  3. The books the validator flagged on 11 Oct, still unread with the model's
     eyes, including the two with invented page numbers (ROCKWOOD-10,
     WILLIAMS-OBSTETRICS-26), plus every book never attempted.
  4. `page_offset` detection (BIBLE part 3 section 4.6) -- not started, and
     every citation depends on it. Then seating, the raster, the registry,
     load and verify, and the Freeze.

### 2026-10-11, 21:30 -- END OF SESSION. See HANDOFF-2026-10-11-evening.md

Four books read with the model's eyes and passing the validator today:
GUYTON-2026 (15 units / 85 chapters), CAMPBELL-2020 (4 volumes / 82
districts, at the level the human chose), HARRISON-22 (20 Parts / 505
chapters), SLEISENGER-11 (9 Parts / 132 chapters, a book that has NO table
of contents and was read from its chapter-opening pages).

**The figure "22 books, 2,859 chapters" recorded on 2026-10-10 is
WITHDRAWN.** Writing the validation script the BIBLE asks for showed that
whole stretches of contents had never been read, and that two books carried
page numbers printed nowhere in the book. Nothing has been loaded into
Neo4j, so no damage has reached the database. Details and evidence in
section (a) below and in the handoff file.

### 2026-10-11 (f) -- BOOK 4 OF 37: SLEISENGER-11, WHICH HAS NO CONTENTS AT ALL

**THE FINDING.** SLEISENGER-11 (*Sleisenger and Fordtran's
Gastrointestinal and Liver Disease*, 11th ed, 2,725 images) has **no table
of contents**. I looked at its front matter myself, page by page:
images 1-2 title, 3-4 copyright, 5-14 **Contributors**, 15 Foreword,
16 The Editors, 17 Preface, 18 Acknowledgments, 19-20 Abbreviation List,
and image 21 opens the book with "PART I Biology of the Gastrointestinal
Tract / 1 Cellular Growth and Neoplasia". 24 contact sheets covering
images 1-144 were shown to the model and it reported no contents page
anywhere in them. Last night's text-layer locator had "found" images 21-33
and produced 22 chapters ending at printed page 22 of a 2,224-page book,
which is why it looked plausible and was wrong.

**THE ANSWER, USING THE MODEL AS MUCH AS POSSIBLE.** Every chapter opens
on its own page printing a LARGE chapter number, the chapter title, the
author and a "Chapter Outline" box, and the printed page. So
kitchen/toc_openers.py shows the model the WHOLE BOOK as 6-page contact
sheets (455 sheets) and asks which pages open a chapter; the model decides,
and no regex votes. It named 146 opening pages. Each is then read on its
own at 150 dpi. **Total cost about 75 minutes of free model time.**

```
  scanned up to image 2124 (354 sheets) -> 117 chapter openers so far
  DONE SLEISENGER-11: parts=9 chapters=146
$ python kitchen/toc_openers_build.py SLEISENGER-11
    still missing 3 chapter(s): [5, 50, 80]
    chapter 5 found at image 72: Nutritional Principles and Assessment of the
    chapter 50 found at image 846: Gastric Neuromuscular Function and Neuromusc
    chapter 80 found at image 1501: Hepatitis C
  SLEISENGER-11: parts=13 chapters=146 numbers 1-132 missing=0
$ python kitchen/toc_dedupe.py SLEISENGER-11 --vis && python kitchen/toc_group_parts.py SLEISENGER-11
$ python kitchen/toc_validate.py SLEISENGER-11 --vis
  SLEISENGER-11   ok  prov=  9 chap= 132 pages 1-2221      1/1 clean
```
**132 chapters, numbered 1 to 132 with no gap, printed pages 1 to 2221, in
9 Parts, validator clean.** Compare with last night's 22 chapters.

**WHAT WENT WRONG AND WAS FIXED, IN ORDER:**
  * *37 of the 146 opening pages returned nothing at 150 dpi.* Reading
    them again at 240 dpi recovered chapters 60, 65, 75, 79, 82, 88, 95,
    105, 106, 109, 115 and others.
  * *31 chapter numbers were still missing.* A chapter's opening page is
    always between the opening pages of the chapters around it, so for
    each missing number the model was asked page by page "does this page
    open chapter N?" That found chapters 5, 50 and 80.
  * *The model was reading running headers as chapter numbers.* An
    ordinary page carries a thin header like "6PART I Biology of the
    Gastrointestinal Tract", which it first reported as "chapter 6". Both
    prompts now say in so many words that a thin running header is not a
    chapter number. I checked one of these pages with my own eyes: image
    846 is chapter 50's ordinary opening page and carries no part banner
    at all -- the model was right to say so.
  * *Asking again for a banner that is not printed made things worse.* A
    pass that re-asked 123 pages produced 20 provinces named "PART" or
    "-". The part banner is printed only on a part's FIRST chapter, so
    "no banner" is the correct answer for the rest and those chapters
    inherit the part above. That pass was reverted.
  * *The banner arrives split across tab fields* -- "PART<TAB>VI<TAB>Stomach
    and Duodenum", "PART VIII<TAB>Biliary Tract", "PART=<TAB>IX<TAB>Liver",
    "PART PART III<TAB>Symptoms..." -- so the whole rest of the line is
    taken and the keyword is normalised. That is what recovered PART VI,
    PART VIII and PART IX.
  * *PART II and PART VII do not exist in this edition.* Chapter 10 has
    no banner and chapter 11 opens PART III; chapter 61 has none and
    chapter 62 opens PART VIII. The part numbers simply skip, and the
    nine parts recorded are the nine the book prints.

### 2026-10-11 (e) -- BOOK 3 OF 37: HARRISON-22, and the pipeline that got it right
### 2026-10-11 (e) -- BOOK 3 OF 37: HARRISON-22, and the pipeline that got it right

```
$ python kitchen/toc_vision.py HARRISON-22 --start 1 --windows 12
  the model named 12 contents page(s): [7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 17, 18]
  DONE HARRISON-22: provinces=78 chapters=522
$ python kitchen/toc_reparse.py HARRISON-22 && python kitchen/toc_dedupe.py HARRISON-22 --vis
$ python kitchen/toc_apply_headings.py HARRISON-22
  heading kinds seen {'PART': 20, 'SECTION': 57} -> top level is PART
  provinces=20 chapters=505 chapters not under any province=0
$ python kitchen/toc_validate.py HARRISON-22 --vis
  HARRISON-22   ok  prov= 20 chap= 505 pages 1-4002      1/1 clean
```
**Chapters 1 to 505, no gap, no duplicate, printed pages strictly
increasing from 1 to 4002, in 20 Parts.** The model located the contents at
images 7-18 by itself -- exactly the range the BIBLE records as
known-correct, found independently. The old text-based reading of this same
book gave 435 chapters.

**FOUR FAULTS FOUND AND FIXED ON THE WAY, ALL CAUGHT BY CHECKING:**
  1. *11 chapters captured twice* (495-505, identical in number, title and
     page) where the contents ran over a page boundary. Removed by rule,
     counted: kitchen/toc_dedupe.py.
  2. *Chapters 142-146 missing* between image 9 and image 10. The automatic
     high-resolution retry had not fired because image 10 returned 42
     lines, which is not "thin". kitchen/toc_fill_gaps.py now asks the
     model for a numbered gap directly. When asked about BOTH neighbouring
     pages it answered image 9 confidently and WRONGLY ("142 Approach to
     the Patient with an Infectious Disease, 957"); checked with my own
     eyes on the rendered page, 142 is "Encephalitis, 1111" at the top of
     image 10. The rule is now: a gap belongs to the page holding the first
     chapter after it, because the contents runs forwards.
  3. *Section banners misread.* While transcribing fifty chapter entries the
     model got the grey banner beside them wrong -- the first province came
     out "SECTION 5" where the page prints "SECTION 1". Asking for the
     banners ALONE, one page per call, with nothing else on the page to
     distract it, returned all 77 headings correctly
     (kitchen/toc_headings.py, two passes: the exact text, then the first
     chapter under each).
  4. *The model had swapped the numbers of chapters 270 and 271* -- the
     titles and their pages were right, but Amyloidosis (p2020) was
     numbered 271 and Cardiac Transplantation (p2028) was numbered 270.
     The validator's page-order check exposed it, a targeted re-read at 240
     dpi confirmed the swap, and the corrected entries replaced the
     originals with the change recorded in
     kitchen/logs/HARRISON-22-vis-conflicts.json. Nothing was edited by
     hand at any point.

**A MISTAKE I MADE AND CORRECTED:** toc_dedupe.py was first run WITHOUT
`--vis`, so it processed last night's text-based file instead of the new
vision one. Its chapter set was verified identical to this morning's backup
(435 chapters, same set) and the file was put back; the only difference is
that nine empty provinces were dropped, which is what the script does by
design. No content was lost, and the mistake is recorded rather than hidden.

### 2026-10-11 (d) -- CAMPBELL-2020 FINISHED, at the level the human chose
### 2026-10-11 (d) -- CAMPBELL-2020 FINISHED, at the level the human chose

**THE HUMAN'S DECISION (2026-10-11):** the geography must stay comparable
with every other book. Campbell's contents is three levels deep
(VOLUME / chapter block / 1,686 individual techniques) and the extra fine
resolution does not belong in the geography -- the techniques will live
inside the chapters later, where they belong. **Chapter block = district.**

Result: **4 volumes, 82 districts, printed pages 14 to 4545, validator
clean**, and all 1,736 techniques kept in
kitchen/logs/CAMPBELL-2020-vis-detail.json (82 lists, one per district)
for the reading phase. Nothing was thrown away.

**A SERIOUS PARSER BUG FOUND AND FIXED (this one nearly cost the book).**
The model prints the page number as its own field on some books
("C<TAB>33<TAB>Red Blood Cells...<TAB>447") and inside the title field on
others. CAMPBELL-2020 used the second form, and the parser required four
fields -- so **1,300 of the book's 1,686 entries were being thrown away
silently.** Found by counting chapter numbers after a re-read and seeing a
gap. Fixed in one place; the fix costs no model call because the raw
transcription is kept on disk and kitchen/toc_reparse.py regenerates the
JSON from the model's own words.

**TWO MORE RULES, BOTH EARNED BY MEASUREMENT:**
  * *A contents page thinner than 20 lines is read again at 220 dpi and the
    answer with more lines wins.* A "fewer than 5 lines" test had let a
    page through that returned 8 lines while its neighbours returned 111.
  * *Pages outside the longest unbroken run of contents pages are not
    contents.* The locator swept in images 27-28, which are the body's
    "CHAPTER 1 SURGICAL TECHNIQUES" opener; without the rule they would
    have become "chapters" on printed pages 1 to 7 inside a volume running
    from page 3300. They are reported in
    kitchen/logs/CAMPBELL-2020-vis-suspect.json, never silently dropped.
  * Districts are sorted by printed page inside their volume, because the
    model sometimes reads a two-column page right-column-first; the
    validator had flagged 4 chapters as "going backwards" purely because of
    that reading order.

### 2026-10-11 (c) -- BOOK 2 OF 37: CAMPBELL-2020, read with the model's eyes
### 2026-10-11 (c) -- BOOK 2 OF 37: CAMPBELL-2020, read with the model's eyes

```
$ python kitchen/toc_vision.py CAMPBELL-2020 --start 1 --windows 12
  the model named 20 contents page(s): [2,3,4,...,20, 27]
  DONE CAMPBELL-2020: provinces=52 chapters=1686 0 pages empty
  THIN PAGES (ask the human, do not guess): [(27, 1)]
```

**WHAT THIS BOOK ACTUALLY IS.** CAMPBELL-2020 is *Campbell's Operative
Orthopaedics*, 14th ed. -- a four-volume surgical atlas, NOT a medicine
textbook. Its front matter (images 2-20) is a **"List of Techniques"**:
4 VOLUME banners, about 82 chapter blocks, and 1,686 individual surgical
techniques, each with its printed page. Image 21 is the title page and
image 27 is the opening of "CHAPTER 1 SURGICAL TECHNIQUES", so the front
matter is exactly images 2-20.

**THE PROMPT FIX THAT MATTERED.** The first run stopped early on dense
pages: images 9 and 15 returned 5 and 1 lines and chapters 2, 14 and 20
went missing. The read prompt now opens with "WORK THROUGH THE WHOLE PAGE.
It is printed in columns. Read column by column, top to bottom, left
column first, and do not stop early." Result: image 9 went from 5 lines to
107, image 15 from 1 to 107, and the entry count rose 1,205 -> 1,686. A
second automatic guard was added: a page that yields fewer than 5 lines is
read again at 220 dpi, and the better answer wins.

**WHAT THE MODEL GOT RIGHT, CHECKED WITH MY OWN EYES ON THE IMAGES**
(rendered pages are kept in kitchen/pages/CAMPBELL-2020/vis/):
  * image 4 prints "15.1 Syme Amputation, 713" and the model recorded 15.x.
  * image 4 jumps from 13.14 straight to the bold heading "Amputations of
    the Foot" 15.1. **The book's own list skips chapter 14.** The model
    did not invent a chapter 14 -- it reported the gap honestly.
  * image 6 is the "VOLUME II" banner, first entry 29.1, exactly as read.
  * the List of Techniques skips the numbers 2, 14, 20, 25, 26, 27, 28 and
    49 between 1 and 90. This is a property of the printed book; it is
    recorded, not "repaired".

**TWO WARNINGS, BOTH REAL, NEITHER HIDDEN:**
  * p3970 -> p3968 at "Toe-Phalanx Transplantation": one page was read in
    column order that differs from the printed reading order.
  * p4526 -> p1 at "SURGICAL TECHNIQUES": the locator included image 27,
    which is the body's Chapter 1 opener, not a contents page. It is kept
    in the record and flagged rather than silently deleted.

### 2026-10-11 (b) -- THE HUMAN'S ORDER
### 2026-10-11 (b) -- THE HUMAN'S ORDER: READ THE CONTENTS WITH THE MODEL'S EYES, ONE BOOK AT A TIME

The human's instruction, recorded verbatim in substance: do NOT minimise the
model's part in this critical stage -- use the vision model AS MUCH AS
possible, not as little; go book by book; do not launch the 28-book job;
then repeat the whole thing with a second model (he will install Gemma 4
31B) and compare the two brains.

So expand_toc.py's text-layer rule is demoted to a cheap cross-check, and
kitchen/toc_vision.py now does the real work with qwen3.8:27b:

  STAGE 1 LOCATE -- 6 rendered pages per labelled contact sheet, the model is
    asked which page numbers are the contents; it is walked forward window
    by window and keeps looking for two empty windows in a row, so a second
    volume's contents block is found too. The model decides; no regex votes.
  STAGE 2 READ -- each page it named is rendered at 150 dpi and sent to the
    model ALONE, as an image, reasoning off, one page per call.

**MEASURED (the old 55 dpi thumbnails were the reason the model had said
NONE):** at 55 dpi with 20 pages per sheet the model answered NONE on
GUYTON-2026 image 14, which IS a contents page -- the thumbnails were too
small to read. At 100 dpi with 6 pages per sheet it reads them correctly and
one such call costs only about 2 seconds, because the answer is two short
lines: the cost is the image tokens, not the generation.

**BOOK 1 OF 37 -- GUYTON-2026 -- DONE AND VERIFIED.**

```
$ python kitchen/toc_vision.py GUYTON-2026 --start 1 --windows 10
    window    1-  6 -> NONE
    window    7- 12 -> [10, 11, 12]
    window   13- 18 -> [13, 14, 15, 16, 17, 18]
    window   19- 24 -> NONE
    window   25- 30 -> NONE
  the model named 9 contents page(s): [10, 11, 12, 13, 14, 15, 16, 17, 18]
  DONE GUYTON-2026: provinces=15 chapters=85 0 pages empty

$ python kitchen/toc_validate.py GUYTON-2026 --vis
  GUYTON-2026   ok  prov= 15 chap=  85 pages 3-1113
  1/1 clean, 85 chapters total
```

And checked directly, because "clean" is not a certificate:
```
chapters 85 numbered 85
numbering 1..85 complete & unique: True
page_start decreases: []
first 1 page 3   last 85 page 1101
```
85 chapters numbered 1 to 85 with no gap and no duplicate, printed pages
strictly increasing from 3 to 1101, in 15 units. **Before today this book
had 11 chapters starting at page 447** -- units I to V were simply missing.
The model found them; the text-layer rule never would have.

**THREE PARSER FAULTS THE VALIDATOR AND THE REPARSE CAUGHT** (all in the
model's own saved words, kitchen/logs/GUYTON-2026-vis-toc.txt -- the JSON is
never typed by hand, it is always regenerated from the recorded text by
kitchen/toc_reparse.py, which costs no model call at all):
  1. The model first answered 203 entries because it listed the small
     sub-headings under each chapter ("Iron Metabolism", "Determinants of
     GFR"). The prompt now says in bold what counts as a chapter; 203 -> 85,
     which is the book's real chapter count.
  2. A heading line printed as a bare "P<TAB>UNIT III" has only two fields
     and was being dropped, which moved a whole unit's chapters into the
     unit before it. 15 provinces -> 16 after the fix, correct.
  3. A contents page that STARTS in the middle of a unit (before its banner)
     created a second province with the same name, so "UNIT V" appeared
     twice, 16 chapters apart. Fixed: such chapters now join the unit above.

**COST PER BOOK, measured:** 9 contents pages took 5 locate calls of about 2
seconds plus 9 read calls of 6 to 11 seconds = about 2 minutes per book for
this one. Books with 20 to 30 contents pages will take proportionally longer.
Nothing has been loaded into Neo4j.

### 2026-10-11 (a) -- VALIDATION WRITTEN, AND IT FOUND REAL DAMAGE
### 2026-10-11 (a) -- VALIDATION WRITTEN, AND IT FOUND REAL DAMAGE

kitchen/toc_validate.py (BIBLE part 3 section 4.4) now exists and runs.
It fills in chapter page_end and province page_start/page_end, and it
checks three things: page_start never decreases; every page_start is
really printed next to its own title in the raw TOC text; the titles are
found in the raw TOC text at all.

```
$ python kitchen/toc_validate.py
validating 31 books
  ADAMS-12  WARN ... BRAUNWALD-12 WARN ... HARRISON-22 ok prov=66 chap=435 pages 1-3922 ...
15/31 clean, 2866 chapters total
```

The "clean" label is NOT a certificate of completeness, and the evidence
below is why. **The 22 books / 2,859 chapters figure recorded on
2026-10-10 is unsafe and must not be used as a baseline.**

**Damage 1 -- the located page ranges were too small, so whole stretches of
contents were never read.** GUYTON-2026 was given the range [14, 14]: ONE
page. Its contents run images 14-22, so units I to V were never read and
the book came out as 11 chapters beginning at printed page 447. The same
happened elsewhere. Measured by comparing the first chapter's page with
the highest page number printed anywhere in the raw TOC text:

```
book                       chaps  1stpage lastpage  max_pg_in_toc_text
CAMPBELL-2020                862     2222     4526                4526
GRAY-2020                     56      386     1430                2020
MIDDLETON-2019                22        3       59                2971
ROCKWOOD-10                   24       46       69                   69
SLEISENGER-11                 22        1       22                2843
THOMPSON-2023                116        1      576                 631
WILLIAMS-ENDO-2024            19       13       43                8292
```

GUYTON-2020's loss was confirmed by eye, not by statistics: its JSON begins
at UNIT VI, and the raw TOC text on image 14 shows UNIT VI and UNIT VII
side by side in two columns.

**Damage 2 -- two books have page numbers that are printed NOWHERE in the
book.** The reader was asked for the printed page of each chapter, but
ROCKWOOD-10 and WILLIAMS-OBSTETRICS-26 have contents pages whose page
numbers are not in the text layer at all, so the model filled the column
with the chapter number. The validator caught it because the extracted
number does not appear next to the title in the raw text:

```
ROCKWOOD-10            24 chapters, page_start == chapter_number in 24 of 24 (100%)
WILLIAMS-OBSTETRICS-26 25 chapters, page_start == chapter_number in 25 of 25 (100%)
```
and in the validator's own words:
```
ROCKWOOD-10  WARN  only 1/12 sampled page numbers are really printed next to their title
WILLIAMS-OBSTETRICS-26 WARN only 0/12 sampled page numbers are really printed next to their title
```
An invented page number breaks Law 2 (provenance) and every citation that
would hang on it. These two books must be read by VISION from the rendered
page images, not from the text layer.

**Damage 3 -- a wrong chapter count is not detectable from the count
alone.** The BIBLE's check "chapter count must match the number of TOC
lines ending in a number" is useless as written: on these multi-column
pages the number sits mid-line, and a run over the raw text returned a
near-constant -45% for every book, which is a property of the REGEX, not
of the books. That check was replaced by the "is the number really printed
next to that title" check above, which is honest and which caught a real
fault.

**FIX APPLIED -- kitchen/expand_toc.py.** A contents page can be told from
an ordinary page by the TEXT LAYER alone: it holds many
"words ... number" fragments, an ordinary page does not. So the range can
be widened with no model calls at all. The script walks forward from the
first page scoring >= 8 fragments, allows 2 weak pages, and also picks up a
second contents block within 26 pages (that is how CAMPBELL-2020 and
GRAY-2020 keep their SECOND VOLUME's contents, which the old range threw
away). The old range is preserved under "toc_images_found" and the blocks
under "toc_blocks" in books.json; nothing is lost.

```
$ python kitchen/expand_toc.py
widening the TOC range of 28 books (window +60 pages, threshold 8) ...
  ADAMS-12   [6, 7] -> [6, 17]  blocks=[[6, 7], [15, 17]] peak=63
  AVERY-2021 [20, 21] -> [20, 55] blocks=[[20, 50], [55, 55]] peak=138
  ...
  HARRISON-22 [7, 17] -> [7, 18] blocks=[[7, 18]] peak=88
  ...
28 ranges widened, books.json written
```
HARRISON-22 landing on 7-18 is the cross-check that the rule is right: that
is the known-correct range the vision locator reproduced earlier.

**WHAT THIS COSTS TO RE-READ.** One reader call per contents page takes
about 48 seconds on this laptop (measured: GUYTON-2026 image 14, 47.7 s,
model on the RTX 5090, 20 GB of 24 GB in use). Counting only the pages
that actually hold entries, the widened ranges hold **678 pages, about 9
hours** of free background reading -- or about 2.5 hours if only the books
the validator flags are re-read. The human decides whether his laptop may
do that. Not started yet.

**MEASURED, NOT GUESSED -- why detection is not done with cheaper tricks.**
Three text-layer ideas were tried and rejected on measurement:
  * "a contents line ends with a page number": 0 hits on GUYTON-2026's own
    contents page, because two columns share every physical line.
  * "a page number is preceded by a wide gap (3+ spaces)": 0-7 hits per
    page, no separation from body pages.
  * "lower the threshold and let the range run": THRESHOLD 4 / 3 weak pages
    gave GUYTON-2026 [14, 73] and SABISTON-22 [35, 95] -- 60 pages of
    ordinary body text. Rejected as Law 1 risk (invented entries).

### 2026-10-10 -- VISION locator + page-at-a-time extraction: 22 of 37 books now have a geography

Three findings, in order.

**1. The model can SEE a Table of Contents; regex cannot.** kitchen/vis_locate.py
renders the front matter at 55 dpi, pastes 20 pages onto one labelled contact
sheet and asks the multimodal model which page numbers are the contents. It
reproduced HARRISON-22's known-correct range 7-18 EXACTLY, and it found a
contents page for BRAUNWALD-12 that no text rule had located. Vision pass 1
located 10 of 16 books; a deeper pass over images 71-210 located 3 more
(BRENNER-11 135-208, MURRAY-7 203, NELSON-2024 117-124).

**2. One giant prompt per book cannot work with this model.** qwen3.8:27b
spends hidden-reasoning tokens before answering; with max_tokens=3000 it
consumed the entire budget reasoning and returned an EMPTY string. Giving it
16,000 tokens worked, but it dropped whole sections (SABISTON-22 lost SECTION I
entirely). Disabling reasoning fixes the empty answer but degrades judgement.

**3. The resolution: one Table-of-Contents PAGE at a time, reasoning off, as
pure transcription.** Small input, small output, nothing to truncate, and a
failure costs one page instead of a whole book. This is AMENDMENT 3.4, and it
is dramatically better than every earlier attempt:

```
BEFORE (whole-book prompt)      AFTER (page at a time)
CAMPBELL-2020   415 chapters ->  862 chapters
DEVITA-12        64 chapters ->  269 chapters
BOLOGNIA-2024   161 chapters ->  194 chapters
SABISTON-22      93 chapters ->  124 chapters
THOMPSON-2023    64 chapters ->  116 chapters
HARRISON-22     494 chapters ->  435 chapters   (needs validation, see below)
```

Result: **22 of 37 books have a usable Table of Contents, 2,859 chapters in
total.** 15 books remain:

```
no TOC located at all (9): BRADDOM-6, BRANT-5, GREEN-HAND-2021, HAZZARD-2022,
    IRWIN-RIPPE-2023, KAPLAN-11, MILLER-10, STAHL-2024, WILLIAMS-HEMATOLOGY-2021
located but yielded <5 chapters (6): BRAUNWALD-12, MANDELL-9, MURRAY-7,
    NELSON-2024, ROSEN-2022, YOUMANS-4
```

Of these, YOUMANS-4 (images 21-52) and part of BRAUNWALD-12 have IMAGE-ONLY
contents: pdftotext returns 0 characters there, so they must be read with the
vision reader, not the text reader. ROSEN-2024's vision answer pointed at
image 3, which turns out to be the copyright page -- a wrong answer that the
page-at-a-time reader correctly refused to invent anything from.
STAHL-2024 appears genuinely to have no contents page at all: it is a drug
guide organised one monograph per drug, which is a different structure and is
recorded as such rather than faked.

### 2026-10-10 -- Step A2 reader run: 17 of 31 books converted, 14 still open

### 2026-10-10 -- Step A2 reader run: 17 of 31 books converted, 14 still open

```
$ python kitchen/toc_to_json.py     (run detached, polled from the log)
31 TOCs attempted
OK: 17 books, 1,898 chapters extracted
NEEDS WORK: 14 books
```

Highlights: HARRISON-22 79 provinces / 494 chapters; CAMPBELL-2020 415
chapters; BOLOGNIA-2024 161; FIRESTEIN-12 119; OXFORD-6 120; SABISTON-22 93.

**The 14 failures are a LOCATION problem, not a reading problem.** The first
TOC locator scored pages by "a title-like string followed by a number", which
also matches NUMBERED REFERENCE LISTS. Proof, the first lines of the pages it
chose:

```
BRENNER-11   [64,79]  "143. Moore MW, Klein RD, Far..."      <- references
NELSON-2024  [5,21]   "Contributors Mark J. Abzug, MD..."    <- contributors
ROCKWOOD-10  [67,71]  "Reference 2007;43:95-103..."           <- references
WILLIAMS-ENDO-2024 [56,59] "References 24. Vassart G..."      <- references
STAHL-2024   [66,67]  "ARIPIPRAZOLE (Continued) ..."          <- a drug monograph
BRAUNWALD-12 [40,49]  "11 The Future"                         <- body text
YOUMANS-4    [9,9]    "DEDICATION The 8th edition..."         <- dedication
```

Three further attempts were made and their exact outcomes recorded, because
they cost hours and must not be repeated:

1. kitchen/toc_parse.py (pure regex, no AI): found 406 chapters in
   HARRISON-22 but **zero** in SABISTON-22, GUYTON-2026 and NELSON-2024.
   Real TOCs wrap titles over two lines, interleave two columns, print author
   names under each chapter, and in GUYTON print the page number on its OWN
   line with U+00B7 and \x08 markers. Regex cannot do this. The script is kept
   as a cross-check for the clean dot-leader books only.
2. kitchen/relocate_toc.py (regex, excluding reference/contributor pages):
   still landed on body pages and reference lists (MANDELL-9 [132,132] body,
   ROCKWOOD-10 [103,109] references, WILLIAMS-ENDO [114,118] references).
3. kitchen/locate_with_reader.py (the READER judges page snippets): reliable
   format, but the model answered FIRST=0 LAST=0 CONF=low for NELSON-2024,
   i.e. it could not find a contents page among the first 200 images either.

**Reader lesson, DEVIATION 2 to the BIBLE's verbatim kitchen/reader.py:** this
model always spends hidden-reasoning tokens before answering. Ollama's
`"think": false` is IGNORED on /v1/chat/completions, so a small max_tokens is
consumed entirely by reasoning and the answer comes back as an EMPTY string
with finish_reason="length". Measured: max_tokens=400 gave
reasoning=1546 chars and content="". The working switch is
`reasoning_effort="none"` (reasoning=0, answer returned) -- but reasoning
improves quality, so the default is now to allow reasoning and budget enough
max_tokens for reasoning PLUS the answer. reader.py also sets
`options.num_ctx` because Ollama otherwise truncates to 4,096 tokens, which
would have silently thrown away most of a Table of Contents.

### 2026-10-10 -- Step A2: 31 Tables of Contents extracted as text

### 2026-10-10 -- 5 PDFs deleted, library is now 37 books / 130,457 pages

```
$ ls kitchen/books/*.pdf | wc -l
37
$ du -sh kitchen/books
12G
```

Each file was hashed BEFORE deletion and the record committed to
data/registry/removed-books.json. The three duplicate pairs shared their
survivor's sha256 exactly. Two of the deletions (Bailey & Love's Short
Practice of Surgery, Marino's The ICU Book) were NOT duplicates: they were
unique books dropped under Law 6, one book per field, and that is stated
plainly in the record.

books.json was rewritten to hold exactly the 37 surviving books, all with
status "candidate".

Vision check for the two image-only contents (BRAUNWALD-12 images 21-29,
YOUMANS-4 images 17-52). The BIBLE (part 3, section 4.1) says: if the text
layer is missing, render the pages and give THEM to the reader in vision
mode. No download and no outside service is needed, because the model
already on this laptop is multimodal:

```
$ curl -s http://localhost:11434/api/show -d '{"name":"qwen3.8:27b"}'
capabilities: ['completion', 'vision', 'tools', 'thinking']
```

So the vision fallback of section 4.1 is available today for free and
offline, exactly as the BIBLE intends. (tesseract OCR is NOT installed and is
not needed.)

### 2026-10-10 -- Step A1: the three duplicate books proven, and the human's decision is REQUIRED

Full SHA-256 of the three suspicious pairs (files of identical size):

```
--- 2 files, 301593085 bytes   -> 1 distinct sha256 = EXACT DUPLICATES
    941104c95e2c1ac9...  Brenner and Rector's The Kidney ... Anna's Archiv-1.pdf
    941104c95e2c1ac9...  Brenner and Rector's The Kidney ... Anna's Archiv.pdf
--- 2 files, 165077460 bytes  -> 1 distinct sha256 = EXACT DUPLICATES
    116c92f513b269a3...  Goodman and Gilman ... libgen.li-1.pdf
    116c92f513b269a3...  Goodman and Gilman ... libgen.li.pdf
--- 2 files, 370089102 bytes  -> 1 distinct sha256 = EXACT DUPLICATES
    ccd621560f181a93...  Bailey and Love's Short Practice of Surgery ... -1.pdf
    ccd621560f181a93...  Bailey and Love's Short Practice of Surgery (plain)
```

So the library is **39 unique books, not 42**. NOTHING was deleted from disk:
the losing copy of each pair stays in kitchen/books/ and carries
status "rejected-duplicate" in books.json so it is never read again.

**DECISION TAKEN (the human, 2026-10-10):** the 3 byte-identical copies were
DELETED from disk so the library can never be confused, and the same-field
choices were approved as proposed: SABISTON-22 kept over BAILEY-2023,
IRWIN-RIPPE-2023 kept over MARINO-2025, and BOTH ADAMS-12 and YOUMANS-4 kept
because neurology (medicine) and neurosurgery (surgery) are different fields.
All five files are recorded with SHA-256 in data/registry/removed-books.json.
### 2026-10-10 -- Step A0: book intake of all 42 PDFs

kitchen/intake.py (pdfinfo + pdffonts + a probe page at 40% depth), run over
every PDF, six at a time:

```
$ python kitchen/intake.py
scanning 42 PDFs ...
wrote kitchen/logs/intake.json
readable probe page: 37/42
```

- ALL 42 have a real text layer (pdffonts found fonts on pages 1-5).
- 5 probes returned under 500 characters: BRANT-5 (401), HAZZARD-2022 (64),
  GOODMAN-14 (87, both copies), ROCKWOOD-10 (152). These are image-heavy
  pages such as full-page radiographs, NOT missing text.
- Total pages across the 39 unique books: **133,100**.
- No file was converted, renamed, split, compressed or modified.

kitchen/books.json now holds one record per book with book_id, pdf_file,
title, edition, year, page_count_images, text_layer, image_dir,
image_name_pattern, toc_images, index_images, page_offset, field_name,
cluster, status and notes.

Two coding lessons recorded so they are not repeated (Law 11):
1. Calling `pdftotext` once PER PAGE re-parses the whole PDF each time and
   took hours on the 1.7 GB books. ONE call per range plus splitting the
   output on the form-feed character does the same job in 1.0 second for 301
   pages. kitchen/find_toc.py now does this.
2. A Table of Contents line must NEVER be matched by "ends with a page
   number". TOC pages are printed in multiple columns, so a physical line
   interleaves entries and the number sits in the middle. The first pattern
   scored ZERO on every real TOC page. The working pattern counts
   title-ish-string-followed-by-number anywhere in the line; with it, TOC
   detection went from 18/39 to 33/39.

### 2026-10-10 -- Part 2 closed; Part 3 opened

### 2026-10-10 -- First commit pushed, and the site is LIVE (Part 2 sections 8 and 9)

The human approved the symlink proposal. Nothing in Caddy, in the Cloudflare
Tunnel or in Apache was modified.

```
$ ln -s ~/second-opinion/site ~/strulovitz-website/exports/2nd-opinion
$ ls -la ~/strulovitz-website/exports/2nd-opinion
2nd-opinion -> /home/nir/second-opinion/site

$ curl -s -o /dev/null -w "%{http_code}" http://127.0.0.1:8081/2nd-opinion/
200
$ curl -s -o /dev/null -w "%{http_code}" https://www.strulovitz.org/2nd-opinion/
200
$ curl -s https://www.strulovitz.org/2nd-opinion/ | grep <title>
<title>Second Opinion - under construction</title>
```

The disclaimer of Law 12 is present once, at the bottom of index.html only.

Commit and push (Part 2 section 9):

```
$ git log --oneline | head -1
9658b85 Part 2: environment, layout, Neo4j schema, placeholder site
$ git status --short      # clean tree
```

Exactly 18 files were sent, the largest PROGRESS.md at 11,282 bytes. No file
over 40 MB. Verified before the push: `kitchen/.env` (the password),
`kitchen/books/` (the 13 GB of PDFs), `kitchen/pages/`, `kitchen/transcripts/`,
`kitchen/extractions/` and `.venv/` are all ignored, so none of them left the
laptop.


### 2026-10-10 -- Neo4j schema applied and helpers proven (Part 2 section 6)

kitchen/schema.cypher was extracted straight out of BIBLE/part-02-environment-and-data-model.md (lines 445-467), so it is word-for-word the schema the BIBLE fixed. Applied once with `cypher-shell -f`. No statement errored.

```
$ SHOW CONSTRAINTS YIELD name, labelsOrTypes, properties
"book_id_unique",       ["Book"],      ["book_id"]
"entity_slug_unique",   ["Entity"],    ["slug"]
"meta_key_unique",      ["Meta"],      ["key"]
"territory_id_unique",  ["Territory"], ["territory_id"]

$ MATCH (m:Meta) RETURN m.key, m.value ORDER BY m.key
"freeze_date", ""
"schema_version", "2"
"skeleton_frozen", "false"

$ SHOW INDEXES YIELD name, type, labelsOrTypes   ->  12 rows
  the 4 constraint indexes, the 5 named range indexes (territory_level_idx,
  territory_book_idx, entity_group_idx, entity_name_idx,
  quarantine_term_idx), entity_fulltext (FULLTEXT) and 2 automatic LOOKUP
  indexes. Exactly what the BIBLE expects.

$ python kitchen/db.py
[{'ok': 1}]

$ python -c "from slug import slug; print(slug('diseases-and-conditions', 'Sjögren's Disease'))"
diseases-and-conditions-sjogrens-disease
```

Both tests printed exactly the values the BIBLE predicted.

Secret safety proof -- kitchen/.env holds the real password and can never be committed:

```
$ git check-ignore -v kitchen/.env
.gitignore:4:kitchen/.env	kitchen/.env
$ git add -An --dry-run      # kitchen/.env is NOT in the list
```

```
$ cd ~/second-opinion && mkdir -p kitchen/pages kitchen/transcripts kitchen/extractions kitchen/logs data/registry data/export site/viewer site/pages site/assets site/data
$ git add -An --dry-run      # exactly what git would commit
  add '.gitignore'
  add 'AGENTS.md'
  add 'PROGRESS.md'
  add 'data/export/.gitkeep'
  add 'data/registry/.gitkeep'
  add 'kitchen/requirements.txt'
  add 'site/assets/.gitkeep'
  add 'site/data/.gitkeep'
  add 'site/pages/.gitkeep'
  add 'site/viewer/.gitkeep'

```

Proof the 13 GB of books and the password can never reach GitHub:

```
$ git check-ignore -v kitchen/books/ .venv/
.gitignore:5:kitchen/books/	kitchen/books/
.gitignore:1:.venv/	.venv/
```


The fixed tree of BIBLE part 2 section 4 was created. Here is exactly what git would commit, and what it refuses to commit:

### 2026-10-10 -- Repository layout and .gitignore (Part 2 section 4)

```
$ cd ~/second-opinion && mkdir -p kitchen/pages kitchen/transcripts kitchen/extractions kitchen/logs data/registry data/export site/viewer site/pages site/assets site/data
$ git add -An --dry-run      # exactly what git would commit
  add '.gitignore'
  add 'AGENTS.md'
  add 'PROGRESS.md'
  add 'data/export/.gitkeep'
  add 'data/registry/.gitkeep'
  add 'kitchen/requirements.txt'
  add 'site/assets/.gitkeep'
  add 'site/data/.gitkeep'
  add 'site/pages/.gitkeep'
  add 'site/viewer/.gitkeep'

```

Proof the 13 GB of books and the password can never reach GitHub:

```
$ git check-ignore -v kitchen/books/ .venv/
.gitignore:5:kitchen/books/	kitchen/books/
.gitignore:1:.venv/	.venv/
```

### 2026-10-10 -- AGENTS.md (Part 2 section 5.1)

The Fifteen Laws, the Glossary and the Manager model routing were copied straight out of BIBLE/part-01-charter-and-world-model.md with sed (lines 93-183, 429-471, 512-539), so they are word-for-word identical to the BIBLE, followed by the required closing paragraph.

```
$ wc -l AGENTS.md
  172 AGENTS.md
```

### 2026-10-10 -- Books received (the blocker from 2026-10-10 is resolved)

```
$ ls ~/second-opinion/kitchen/books | wc -l
  42
$ du -sh ~/second-opinion/kitchen/books
  13G
```

### 2026-10-10 -- Environment inventory (Part 2 section 1)

See the ENVIRONMENT INVENTORY 2026-10-10 block above. Key findings: Java, Neo4j and the Python neo4j/matplotlib/scipy libraries were MISSING; git, gh, Python 3.13, networkx, numpy, PIL, requests were present; the free READER model qwen3.8:27b (17.7 GB) was ALREADY downloaded in Ollama on 127.0.0.1:11434; the web root is ~/strulovitz-website/exports served by Caddy on port 8081 through the Cloudflare Tunnel.

### 2026-10-10 -- Neo4j installed and running (Part 2 section 2.2)

See the INSTALLS 2026-10-10 block above: `RETURN 1 AS ok` returned 1, and the database listens on 127.0.0.1:7474 and 127.0.0.1:7687 only, so it is NOT reachable from the internet.

### 2026-10-10 -- Python virtual environment (Part 2 section 2.3)

`.venv` created inside the repo; `all imports OK`; kitchen/requirements.txt written with 20 pinned packages.

### 2026-10-10 -- Environment inventory (Part 2 section 1) and the blocker

The 42 textbooks were NOT on this laptop. The human copied them from the Windows PC and they now sit in kitchen/books/ (gitignored).

## DONE 2026-10-14 (a) -- DELISA-6 read, and the "no printed pages" problem SOLVED

**The human's idea (14 Oct):** the contents pages that print no page number
still carry HIDDEN PDF LINKS, one per chapter line, and clicking one jumps to
the chapter. He was right. This is now a tool.

```
$ python kitchen/toc_links.py DELISA-6
DELISA-6: 74 links on images [9, 10, 11, 12, 13]
  matched to chapters: 62
  unmatched (front matter, part pages, index): 12
$ python kitchen/toc_validate.py DELISA-6 --vis
  DELISA-6                   ok  prov=  9 chap=  62 pages 51-3565
RESULT DELISA-6 ok chapters=62 provinces=9 without_page=0
```

**HOW A PAGE IS PROVED (Law 2).** For every link, the TARGET PAGE IS OPENED and
the chapter number is read from the page itself ("CHAPTER 1", or Rockwood's bare
"1" over the title). A page is never taken from the link's position on the
contents page, and never invented. Each chapter stores `_page_source =
"pdf-link"` plus `_link_head`, the page's own first lines.

**GUARDS, both learned the hard way:**
* An INDEX page also prints "7" then "68" then a title. It is refused unless the
  chapter's own title words appear on that page (`title_agrees`). This caught
  ROCKWOOD-10 image 3452 pretending to be a chapter opener.
* Two links claiming one chapter keep the EARLIER page and the disagreement is
  written to `conflicts` in `<BOOK_ID>-vis-links.json`. (BRANT-5 lists every
  chapter twice; both links point to the same page.)

**WHAT THE PAGE NUMBER IS.** These four scans print NO folio on the page
(checked by eye on DELISA-6 images 51 and 52: nothing in header or footer, and
no folio in the text layer). So the page number recorded is the PDF IMAGE
NUMBER -- which is the number Nir sees in his PDF reader, and it is the page
the chapter actually begins on. `page_offset` for these books is therefore 0 by
construction, NOT measured; BIBLE part 3 section 4.6 is still NOT started for
the other 33 books.

**THE FOUR BOOKS THAT PRINTED NO PAGES -- ALL FOUR NOW CLEAN:**

| book | provinces | chapters | pages | validator |
|---|---|---|---|---|
| DELISA-6 | 9 | 62 | 51-3565 | ok |
| BRANT-5 | 12 | 83 | 45-4100 | ok (was "warn, no pages") |
| ROCKWOOD-10 | 2 | 69 | 22-3613 | ok (was "invented pages") |
| WILLIAMS-OBSTETRICS-26 | 12 | 68 | 28-3184 | ok (was "invented pages") |

`toc_validate.py` no longer judges a link-sourced page against the contents
TEXT (it is not printed there) and says so on every run.

`toc_folio.py` was written to MEASURE the printed folio with the reader; it
answered NONE on all 7 samples, which is correct -- these scans print no folio.
It is kept, unused, for books that do print one.

INSTALL: `pypdf 6.20.1` added to the venv (Law 13; small, no sudo).
