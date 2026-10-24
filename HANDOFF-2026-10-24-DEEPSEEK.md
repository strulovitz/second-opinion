# DeepSeek handoff -- 24 October 2026 (written fresh by Claude Opus 5.5)

This file REPLACES `HANDOFF-2026-10-23-NIGHT-DEEPSEEK.md` (that one is
history now). Everything you need is here. Follow it step by step. Do not
improvise, do not skip, do not "improve" anything.

Your job: run the **Harrison index trial** (book HARRISON-22), with Nir
watching, one small step at a time. Then the full Harrison index, then show
Nir the review. Then stop.

---

## 0. Rules you must obey (read twice)

**RULE ZERO -- NIR'S HARD LIMIT (24 Oct 2026, his words: "i never approved
for qwen to go on thousands of pages per book, in ANY phase, NEVER EVER ...
not months, never months").**
- Qwen is NEVER run over thousands of pages of a book. This job uses Qwen
  only on Harrison's back-of-book INDEX (230 pages of about 4,300) and on
  the index terms, 25 at a time. Nothing else.
- Before the full run you MEASURE the trial, compute the total time in
  HOURS and show it to Nir (step 5b). You start the full run only if Nir
  says okay to that number.
- Anything that would take weeks or months is forbidden. If the estimate
  is too long for Nir, STOP: the answer is a faster plain-code method
  written by SMART, never "let it run".
- Never start "Phase B" / BIBLE Part 4 (reading the chapter pages). It is
  forbidden until SMART writes a new fast plan and Nir approves it.

1. **Do NOT edit anything in `BIBLE/`.** Not one character. Only Claude
   Opus 5.5 was allowed to write there, once. You write your notes only in
   `PROGRESS.md`.
2. **Do NOT touch the map or the viewer.** No changes to `site/viewer/`,
   `site/data/geography/`, `data/export/geography/`, `kitchen/goldberg_*`,
   `kitchen/geography_*`, `kitchen/flower_map.py`, `kitchen/make_demo.py`.
   They are finished and Nir approved them on 24 Oct 2026.
3. **Do NOT reopen closed work**: no table-of-contents checks, no "are the
   PDFs complete books" checks, no re-checking of any book's chapters.
4. **The free local model reads the pages.** The reader is Qwen
   `qwen3.8:27b` on this laptop's Ollama server (already installed and
   running). You (DeepSeek) only run the scripts and check the results. Do
   not read index pages yourself, do not classify terms yourself.
5. **One book only: HARRISON-22.** Nothing runs unattended. No overnight
   jobs, no parallel books, no background loops. Nir watches.
6. **Never print, copy or show `kitchen/.env`** (it holds the database
   password). Never install anything. Never use `sudo`.
7. **Before each step, tell Nir in 1-3 short plain sentences what you will
   do, and wait for his "okay".** He is a beginner. Use emojis in chat
   only, never in files or commit messages.
8. If something fails: **stop**, show Nir the exact error, and do not try
   random fixes. If the same generic software error happens twice, write it
   down (section 7) and tell Nir that SMART (a smarter model) is needed.

All commands run from the project folder:

```bash
cd ~/second-opinion
```

---

## 1. Check the starting point (no changes)

```bash
git status --short
git log --oneline -3
```

Expected: a clean (or nearly clean) status, and the newest commit is from
24 Oct 2026 ("... DeepSeek handoff ..." or later). If there are changed
files you do not understand, STOP and ask Nir.

What already exists (do not redo):
- 37 books, all chapter lists finished. Harrison has 505 chapters.
- The approved map (Goldberg ball) in `data/export/geography/`.
- The index software (`kitchen/index_*.py`, `kitchen/review_sample.py`),
  tested earlier. One Harrison index page (PDF page 4044) was already
  extracted as a pilot; its files are in `kitchen/logs/`.
- The Neo4j database is running but EMPTY (only 3 "Meta" nodes).

---

## 2. Test the reader (Qwen)

Tell Nir: "First I check that the free reader on this computer answers."

```bash
.venv/bin/python kitchen/reader.py
```

Expected output: `{'ok': True}` (the first call can take a minute or two
while the model loads on the graphics card).

If it fails: check that Ollama runs and has the model, then stop and show
Nir:

```bash
curl -s localhost:11434/api/tags
```

(It should list `qwen3.8:27b`.) Do not change any model setting.

---

## 3. Look at the plan (read-only, no reader, no database)

```bash
.venv/bin/python kitchen/index_pipeline.py HARRISON-22 --plan --limit 1
.venv/bin/python kitchen/load_geography.py
```

Expected (checked on 24 Oct 2026):
- `HARRISON-22 extract: index PDF 4044-4273; 230 pages; 505 districts; limit=1; read-only plan`
  (and the same line for parse, classify, resolve)
- `Geometry: 37 books; 5334 territories` and `Dry run; no database access or writes`

---

## 4. Put the map into the database (one transaction)

Tell Nir: "Now I copy the approved map (books, parts, chapters) into the
database. This is needed before the index can be linked to chapters."
Wait for his okay.

```bash
.venv/bin/python kitchen/load_geography.py --apply
```

Expected: 37 books and 5,334 territories (37 continents + 534 provinces +
4,763 districts). Copy the printed counts into your PROGRESS.md note.
If it refuses (for example "frozen" or "differs"), STOP and show Nir.

---

## 5. The bounded trial: ONE index page and ONE batch of terms

Tell Nir: "Now the reader reads ONE index page, and then sorts ONE batch
of 25 terms. Then we look at the result together."

```bash
time .venv/bin/python kitchen/index_parse.py HARRISON-22 --limit 1
time .venv/bin/python kitchen/index_classify.py HARRISON-22 --limit 1
```

Write down the two "real" times that `time` prints (seconds for one page,
seconds for one batch of 25 terms).

`--limit 1` means one NEW page / one NEW batch. Then show Nir, in plain
words, what came out (the newest files about HARRISON-22 in `kitchen/logs/`).
Check only the STRUCTURE, not medicine:
- It really is the back-of-book index (alphabetical terms with page numbers).
- Main entries and their sub-entries are kept apart and in order.
- The page numbers are the book's printed ones, copied exactly.
- A term continued from the previous page stays attached to its parent.
- Each term got exactly one group: symptoms-and-signs,
  diseases-and-conditions, treatments-and-drugs, or not-an-entity.

If Nir is not happy, STOP and write what he said in PROGRESS.md.
Do not hand-edit any JSON to make it look right.

### 5b. The time estimate (MANDATORY before step 6)

Compute and tell Nir, in hours:
- parse time = (seconds for one page) x 229 remaining index pages
- classify time = (seconds for one batch) x (number of index terms / 25).
  The number of terms per page: count the entries in the newest
  `kitchen/logs/HARRISON-22-index-<page>.json`; estimate the total as
  (entries on that page) x 230.
- total = parse time + classify time, in hours (round up).

Say it plainly, for example: "The whole Harrison index would take about
N hours of Qwen time. Is that okay?" If Nir says it is too long, STOP,
write the numbers in PROGRESS.md and tell him SMART can write a faster
plain-code index reader. Do NOT start step 6 without his okay to the
number.

---

## 6. The full Harrison index, then the review (only after Nir says okay to the 5b estimate)

Tell Nir: "The trial looks fine. Now the reader goes through the other 229
index pages of Harrison (about N hours, as measured). You can watch the
progress. It can be stopped and started again without losing work."

```bash
.venv/bin/python kitchen/index_pipeline.py HARRISON-22
```

- Keep it in this visible terminal. Progress is also written to
  `kitchen/logs/HARRISON-22-run.log`.
- If it stops or Nir stops it: run the SAME command again; finished pages
  are not read again.
- To pause between stages: `--stop-after parse` or `--stop-after classify`.

When it has finished:

```bash
.venv/bin/python kitchen/review_sample.py HARRISON-22
```

This writes `kitchen/logs/HARRISON-22-review.md`. Show it to Nir (counts,
sample terms per group, possible wrong merges, conflicts). This is
Checkpoint 3.5.

**Only if Nir approves**, record HIS EXACT WORDS (replace the text in quotes):

```bash
.venv/bin/python kitchen/review_sample.py HARRISON-22 --approve "his exact words here"
```

Then STOP and ask Nir what next. (The next book would be the alphabetical
first remaining book, ADAMS-12, same steps 5-6. Never start it without his
okay.)

---

## 7. Write it down and save to GitHub

Add a short entry at the top of the `## DONE (newest first, each with
evidence)` section of `PROGRESS.md`: date, what you ran (exact commands),
the printed counts, and what Nir said. If something failed, write the exact
command and the full error under `## BLOCKED`.

Then save (show Nir the list of files first):

```bash
git status --short
git add PROGRESS.md
git commit -m "3.7 HARRISON-22 index trial: <one short line>"
git push
```

Only add other files if the scripts created tracked, intended files and
Nir agrees. Never add `kitchen/logs/`, PDFs, page images, reader answers or
`.env` (they are ignored anyway; do not force them).

---

## 8. When to call SMART instead

Stay with DeepSeek for all of this. Call SMART (tell Nir "this needs the
smarter model") only:
- after the same generic software error happened twice (bring the exact
  command, the full error and the log file names), or
- after ALL books have approved reviews (Checkpoint 3.6), for the Freeze A
  review.

---

## 9. If Nir asks about the globe

It is finished and approved. Local view (optional, only if he asks):

```bash
.venv/bin/python kitchen/open_globe.py
```

The live website shows it when Nir double-clicks "Websites ON".
Do not change it. Full documentation: the "CLAUDE OPUS 5.5 ADDITION"
blocks at the top of BIBLE parts 8, 1, 3, 7 and 9.

---

## 10. What Nir pastes to start you

> Please read ~/second-opinion/HANDOFF-2026-10-24-DEEPSEEK.md and follow it
> step by step. Explain each small step briefly before you do it.
