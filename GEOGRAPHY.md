# Geography generator

Implemented from BIBLE Part 3 section 6 and the mobile-texture amendment in
Part 7. It builds the fixed spherical geography used by the eventual viewer.

## Generate a provisional map from the existing library

Run from the repository root:

```bash
OPENBLAS_NUM_THREADS=2 OMP_NUM_THREADS=2 MKL_NUM_THREADS=2 PYTHONDONTWRITEBYTECODE=1 .venv/bin/python kitchen/geography.py --draft --out kitchen/logs/geography-draft
```

The first successful build contains 37 continents, 534 provinces and 4,763
districts. Draft mode uses the existing provisional alphabetical IDs and
book titles as labels when field_name is not filled. It includes candidate
configuration records without changing their statuses. This is a visual
draft, not an approved clinical seating or a published database export.

Open `kitchen/logs/geography-draft/seating-preview.png` for the diagnostic
map. The directory also contains:

- `district_raster.npy`: 2048 x 1024 integer district codes.
- `district_raster.png`: lossless viewer hit-testing, code = R*256 + G.
- `districts_lookup.json`: raster code to territory ID.
- `geography.json`: names, hierarchy, page bounds, centres, areas and colours.
- `continents_texture.png`: labelled 4096 x 2048 globe texture.
- `continents_texture_2k.png`: mobile texture.
- `territories.csv`: staging atlas, with original chapter-number strings.
- `seating-proposal.json`: a separate copy of the configuration with locations.
- `build.json`: counts, mode, SHA-256s and explicit approval/database status.

Existing chapter lists and configuration are read-only inputs. Page bounds
are copied in their existing units; a visual map does not certify printed
citations. Existing empty headings remain zero-area provinces. Noninteger
or repeated chapter numbers get collision-free district IDs while the
original number is preserved in toc_number (Appendix B).

## Clinical seating and normal generation

Completed on 23 Oct 2026 (see Approved result below). The instructions remain
for future regeneration. This was a CHEAP-tier operation followed by the
human's seating/texture checkpoints, not another contents-reading task. Use
existing book metadata to prepare the field names and clinical clusters
specified in BIBLE 3.6.3. Record the existing acceptance decisions correctly;
do not treat a draft rendering as permission to change statuses or declare a
Freeze.

Use a separately prepared configuration file with the accepted records:

```bash
OPENBLAS_NUM_THREADS=2 OMP_NUM_THREADS=2 .venv/bin/python kitchen/geography.py --books kitchen/logs/geography-approved-books.json --out kitchen/logs/geography-clinical-preview
```

Normal mode uses Harrison as the opening-view hub and places related fields
together with the BIBLE's greedy seating algorithm. A complete saved
seat_order/seat_index assignment is preserved exactly. To propose a location
swap before approval, exchange those books' seat_index values in the separate
proposal configuration; regenerate and inspect the preview. Partial or
duplicate saved seats are refused.

Once the relevant checkpoints are satisfied, the same generator can write
`data/export/geography`. It never updates the configuration or loads Neo4j.
The registry CSV is exported from Neo4j at its later BIBLE step, not replaced
by this staging atlas. No service, model endpoint or PDF is used by this tool.

## Approved result -- 23 Oct 2026

Nir approved the specialty seating and the displayed map on 23 Oct 2026
("i think it's ok"). The approval is recorded in PROGRESS.md under
DECISIONS BY HUMAN and in `data/export/geography/build.json`
(`seating_approved` and `approved_by_human` are true).

The canonical `kitchen/books.json` now records the approved grouping for all
37 books: status accepted, field_name, cluster. A pre-change backup is at
`kitchen/logs/books-before-seating-20261023T205918.json`. No chapter title,
page number, TOC source or acceptance evidence was changed.

Approved build command (from the repository root):

```bash
OPENBLAS_NUM_THREADS=2 OMP_NUM_THREADS=2 MKL_NUM_THREADS=2 PYTHONDONTWRITEBYTECODE=1 .venv/bin/python kitchen/geography.py --approved --out data/export/geography
```

Result: 37 continents, 534 provinces, 4,763 districts, district area sum
1.0, no unpainted pixels, no missing lat/lon. The preview output is
byte-identical to the approved clinical preview (SHA-256 e564b3c3...).
One pre-existing empty heading (ADAMS-12, `C10.P02 PART 2: CARDINAL
MANIFESTATIONS OF NEUROLOGIC DISEASE`) remains a zero-area province; no
district was lost.

Viewer files copied to `site/data/geography/`: geography.json,
districts_lookup.json, district_raster.png, continents_texture.png and
continents_texture_2k.png. The public site does not receive the diagnostic
preview or the configuration dump. The `.npy` and `territories.csv` staging
atlas stay in data/export; the frozen registry CSV is still exported from
Neo4j at its later step. Neo4j was not loaded and nothing was frozen.

## Exact model hand-back point

STATUS: reached on 23 Oct 2026. The next task is SMART's index-to-entity
registry software (BIBLE 3.7.4-3.7.7).


DeepSeek stays in charge throughout Step A5:

1. Prepare the clinical grouping/seating proposal from the existing metadata.
2. Generate the preview and show it to Nir. Apply any requested placement or
   appearance adjustments with the existing generator.
3. Record Nir's seating and texture approvals (Checkpoints 3.3 and 3.4),
   generate the approved geography outputs, and commit/push the results and
   evidence. Update PROGRESS.md with the approved configuration/output paths.
4. STOP and tell Nir: "Please switch to GPT 6.1 Sol and say continue.
   The next task is writing the index-to-entity-registry software,
   BIBLE Part 3 sections 7.4-7.7."

Do not switch models between preview adjustments. The next SMART assignment
is reusable programming; after that code is tested, DeepSeek/free reader
handle its repetitive execution. Do not start index extraction before that
machinery is ready. If the reusable generator fails twice, record the exact
commands/errors and return that software blocker to SMART earlier.
The old contents-checking queue remains cancelled.

## Verification

```bash
OPENBLAS_NUM_THREADS=2 OMP_NUM_THREADS=2 TMPDIR=/tmp/opencode PYTHONDONTWRITEBYTECODE=1 .venv/bin/python -m unittest discover -s kitchen -p 'test_*.py'
```

The 67-test suite includes nine geometry tests: spherical coordinates,
equal-area continent cells, stable hub/seating, full pixel coverage,
page-weighted district sizes, snapped district centres, original-number/ID
round trips, empty headings, insufficient resolution, longitude-seam borders,
PNG code decoding and CSV/JSON/manifest agreement. No model or database is
called. These tests verify software, not clinical facts or book contents.
