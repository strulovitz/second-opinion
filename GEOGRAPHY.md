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

This is the next routine CHEAP-tier operation, followed by the human's
seating/texture checkpoints, not another contents-reading task. Use existing
book metadata to prepare the field names and clinical clusters specified in
BIBLE 3.6.3. Record the existing acceptance decisions correctly; do not treat
a draft rendering as permission to change statuses or declare a Freeze.

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
