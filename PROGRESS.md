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

**SUPERSEDED 2026-10-15 (evening).** Read `HANDOFF-meaningful-names.md` FIRST.

Nir stopped the one-book-at-a-time reading on 15 Oct: the province
(middle) level of many books stores only a number ("PART I",
"SECTION 3", "UNIT VII") with no meaning. He first decided MEANING
only, then (same evening) changed his final rule: keep BOTH the
number AND the meaning together ("Section V - Cardiac Radiology"),
never meaning alone, because in the future we must be able to find
"the book numbered X" fast. The database structure stays unchanged —
one name field holds the combined string.

BEFORE reading any of the remaining 15 books, the names of the already
read books must be fixed and the TOC prompts must be changed to keep
BOTH the numbering and the title. Steps are in
HANDOFF-meaningful-names.md. One book at a time.

After that, the remaining 15 books (ONE AT A TIME, never a batch):
GREEN-HAND-2021, HAZZARD-2022, IRWIN-RIPPE-2023, KAPLAN-11, MANDELL-9,
MIDDLETON-2019, MILLER-10, MURRAY-7, NELSON-2024, OXFORD-6, ROSEN-2022,
STAHL-2024, WILLIAMS-ENDO-2024, WILLIAMS-HEMATOLOGY-2021, YOUMANS-4.

```bash
cd ~/second-opinion && source .venv/bin/activate
python kitchen/build_book.py <BOOK_ID>     # one whole book, unattended
```

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

## DONE (newest first, each with evidence)

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
