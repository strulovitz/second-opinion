# Second Opinion -- paused 2 November 2026 at Nir's request

Repository: `/home/nir/second-opinion`
GitHub: https://github.com/strulovitz/second-opinion

## 1. Why this file exists

Nir asked to save the exact place and pause the project for a moment. The
classification job was stopped cleanly with SIGINT. Both the `timeout`
wrapper and the Python process were confirmed gone afterwards. This was a
human pause, not a validation failure.

## 2. Exact saved position (verified after stopping)

| Item | Saved state |
| --- | --- |
| Parse | `parsed_pages=230/230`, `complete=True`, `entries=14,840` |
| Classification | `saved_current=3,700 / 13,878` terms |
| Pending classification | `10,178` terms |
| Reference counts | online-only=2280, non-integer-or-malformed=75, outside-districts=0, mapping-unresolved=0 |
| Next action | classify the first pending term after the saved 3,700 |

This continuation added 1,500 new classified terms in three completed
500-term chunks: 19.1, 17.1 and 17.5 minutes (about 2.2 s/term). A fourth
chunk was interrupted by the pause request before completing and saved
nothing; do not count it.

Remaining classification projects to roughly 5.9-6.1 hours at the measured
pace. This is an extrapolation, not a guarantee.

## 3. Resume check and command (only after Nir says continue)

```bash
cd /home/nir/second-opinion
.venv/bin/python kitchen/logs/HARRISON-22-pause-progress-20261026.py
```

Expected: `pages=230/230 left=0 entries=14840 complete=True`,
`saved_current=3700 pending_prefix=10178`.

Then, in supervised foreground chunks:

```bash
time timeout --signal=INT --kill-after=10s 1700s .venv/bin/python -u kitchen/index_classify.py HARRISON-22 --limit 20
```

`--limit 20` means 20 batches of up to 25 terms = 500 terms. Each batch is
saved to `kitchen/logs/HARRISON-22-classified.jsonl` as it completes, so an
interruption loses only the in-flight batch.

## 4. What NOT to do

- Do not start matching, database resolution, registry approval, another
  book or Phase B.
- Do not run the unrestricted pipeline.
- Do not edit the BIBLE.
- Do not re-run warm-ups, cloud-reader comparisons or the old classification
  trial as a restart ritual.
- Local PDFs, page images, model answers and caches are gitignored and stay
  on this machine. GitHub is not a backup of that private reading progress.

## 5. Where the data lives

```text
kitchen/logs/HARRISON-22-index-entries.json
kitchen/logs/HARRISON-22-classified.jsonl
kitchen/logs/HARRISON-22-run.log
kitchen/logs/HARRISON-22-pause-progress-20261026.py
```

Keep these files intact. Do not delete or reconstruct them by hand.
