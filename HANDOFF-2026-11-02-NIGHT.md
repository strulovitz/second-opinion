# Second Opinion -- night handoff, 2 November 2026

Repository: `/home/nir/second-opinion`
GitHub: https://github.com/strulovitz/second-opinion

Nir said: do this tomorrow, save all progress, push, and write the handoff.
This file is the exact restart point. Read it with the newest PROGRESS.md
block and `AGENTS.md` before doing anything.

## 1. State at the stop

| Item | Value |
| --- | --- |
| Parse | `parsed_pages=230/230`, `complete=True`, `entries=14,840` |
| Classification | `13,878 / 13,878` terms, `pending=0` |
| Matching / resolution | **50 / 13,922** non-see entries resolved |
| Neo4j entities | **28** (diseases=16, treatments=9, symptoms=3) |
| Neo4j lit spots | **109** `DISCUSSED_IN` relationships |
| Tests | **170 pass** |
| Running process | none (checked) |
| Git | clean before this handoff commit |

The 50 trial entries are real data, not a dry run. Nothing was rolled back.
The book status is still `geography-done`; `finish_book` only runs when all
non-see entries are resolved.

Trial outcome counts for the 50 entries:

```text
new-no-candidates=12
new-reader=11
not-an-entity=21
group-conflict=5
reader-merge=1
```

## 2. Measured pace (important)

Two 25-entry trials were run with local Qwen already loaded:

```text
first 25:  29.9 s, 4 reader calls
next 25:   42.7 s, 8 reader calls
```

Derived:

- about **0.7 s per entry** fixed cost (decision, Neo4j, logs)
- about **3.2 s per reader call**
- about **24%** of entries needed a reader call

Projection for the remaining 13,872 entries: **roughly 5-8 hours, most likely
about 6-7 hours**. This is measured from 50 entries, not a guarantee.

**Correction to BIBLE 3.7.8:** it says "about 0 resolution calls (first
book)". That is wrong in practice. The registry grows inside the same book,
so similar terms (for example `AA amyloidosis` vs `AApoA1 amyloidosis`)
trigger Qwen SAME/NEW calls. Do not repeat the earlier 20-60 minute estimate.

## 3. Exact resume command

Run in supervised foreground chunks. `--limit` counts NEW entries, not
batches. The script skips the 50 already-resolved entries and continues at
the 51st non-see entry.

```bash
cd /home/nir/second-opinion
time timeout --signal=INT --kill-after=10s 1700s .venv/bin/python -u kitchen/index_resolve.py HARRISON-22 --limit 25
```

The job is idempotent and resumable. It saves `resolved.jsonl` after every
entry and `resolve-decisions.jsonl` before each database write.

## 4. Verify before resuming

```bash
cd /home/nir/second-opinion
.venv/bin/python kitchen/logs/HARRISON-22-pause-progress-20261026.py
.venv/bin/python - <<'PY'
import json
rows=[json.loads(l) for l in open('kitchen/logs/HARRISON-22-resolved.jsonl') if l.strip()]
print("resolved", len(rows), "lit_spots", sum(r.get('lit_spots',0) for r in rows))
PY
```

Expected: parse 230/230, classification 13,878 saved / 0 pending, 50 resolved
rows, 109 lit spots. Check Neo4j too:

```bash
cd /home/nir/second-opinion
timeout 30 .venv/bin/python - <<'PY'
import sys; sys.path.insert(0,'kitchen')
from db import run
print(run("MATCH (e:Entity) RETURN count(e) AS n"))
print(run("MATCH ()-[r:DISCUSSED_IN]->() RETURN count(r) AS n"))
PY
```

Expected: 28 entities, 109 lit spots. If local data differs, inspect and
explain; do not overwrite it from this document.

## 5. What NOT to do

- Do not rerun the classification; it is complete.
- Do not rerun the two matching trials as a warm-up; they are saved.
- Do not start registry review, Neo4j approval, another book or Phase B.
- Do not run the unrestricted pipeline.
- Do not edit the BIBLE.
- Do not hand-edit resolved entries to make a pass.
- Keep local Qwen; Nir chooses the operator model himself.

## 6. Where the data lives (local, gitignored)

```text
kitchen/logs/HARRISON-22-index-entries.json
kitchen/logs/HARRISON-22-classified.jsonl
kitchen/logs/HARRISON-22-resolved.jsonl
kitchen/logs/HARRISON-22-resolve-decisions.jsonl
kitchen/logs/HARRISON-22-run.log
kitchen/logs/HARRISON-22-pause-progress-20261026.py
```

Neo4j holds the 28 entities and 109 lit spots. PDFs, images, model answers
and caches stay on this machine; GitHub is not a backup of that private data.

## 7. How to report tomorrow

After each chunk, show: entries resolved, entries left, wall time, reader
calls, and the updated hours projection. Stop after matching and report.
