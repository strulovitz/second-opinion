# One chapter, one honeycomb tile -- Amendment 3.5

> **SUPERSEDED ON 24 OCT 2026 (Claude Opus 5.5, approved by Nir).** The map is now the
> Goldberg ball (Amendment 3.6) and the viewer has the Sand table / Atlas looks, the flower
> 2-D map, the future layers and DEMO mode. The exact, binding description is in the
> "CLAUDE OPUS 5.5 ADDITION" blocks at the top of BIBLE parts 1, 3 and 7. Where this file
> disagrees with those blocks, the blocks win. This file is kept as history.


OVERNIGHT RESTART: read HANDOFF-2026-10-23-NIGHT-DEEPSEEK.md first. Nir
approved the displayed globe on 23 Oct: "it looks great, yes i am very happy
with it!!!" Approval is recorded in the canonical manifest and PROGRESS.md.
He stopped for sleep; the next execution belongs to DeepSeek when he returns.
At his further request, the completed implementation/map/handoff were
successfully pushed tonight as 726d5c4. DeepSeek need not repeat that save.

## Nir's decision, 23 October 2026

Nir explicitly requested one polygon per chapter, not several small tiles
per chapter. Whole neighboring tiles fit like a honeycomb or jigsaw, including
at book boundaries. Hexagons and pentagons are accepted; clipped border tiles
are not. Stepped book outlines are accepted. Tile areas should be as similar
as practical across the whole globe. Chapter length must not determine area.

This overrides the old equal-continent/page-weighted-rectangle rules; the
BIBLE remains unchanged. All territory IDs, chapter names/numbers, hierarchy,
page bounds, units, raster codes, colours and seat_order are preserved.
The old clinical locations are assignment anchors. Book areas now follow
chapter counts, so the old exact book outlines cannot be preserved.

## What is built

The actual viewer now displays the new honeycomb geography:

http://127.0.0.1:8765/viewer/?layout=honeycomb#/globe

- Exactly 4,763 whole chapter polygons: 4,751 hexagons and 12 pentagons.
- Every shared edge has exactly two owners; no border tile is clipped.
- Every book is connected (37/37). Every nonempty province is connected
  (533/533); the pre-existing empty ADAMS heading remains empty, giving the
  original 534 provinces overall.
- True spherical area variation: coefficient of variation 1.4047% across
  all tiles. Smallest tile is 72.2074% of the mean; largest is 110.3430%.
  "Similar-sized" is an approximation, not a claim of exactly equal areas.
- All 2,097,152 picking pixels are assigned to exactly one polygon, with
  zero boundary ties. Every chapter has pixels and an interior picking centre.
- Vertex/edge topology is in matching data/export/geography/honeycomb.json
  and site/data/geography/honeycomb.json, using shared vertex indices and
  reciprocal district neighbor IDs. Existing JSON/PNG viewer interfaces stay.
- Selecting a chapter shows whether its tile is a hexagon or pentagon.

## Mathematical/software method

kitchen/honeycomb_mesh.py builds a closed triangular mesh with exactly the
required vertex count. A concave sequence of integer latitude-ring counts
transports six units of curvature through each hemisphere. The northern
construction is mirrored and stitched at the equator. Taking the geometric
dual gives one convex spherical polygon per mesh vertex: exactly twelve
five-sided cells, with all others six-sided. Shared polygon corners come
from the same normalized face-centre vertices; borders are great-circle arcs.

The actual 4,763-tile mesh has 9,522 shared polygon vertices and 14,283
edges. Convexity, edge ownership, the Euler counts and the 4*pi spherical-area
sum are checked. This is not a flat hex texture painted over rectangles.

kitchen/honeycomb_partition.py uses capacity-constrained transportation
linear programming to give each book/province exactly its chapter count.
Connected boundary exchanges and bounded geographic centroid reassignment
handle islands. Connectivity is checked before any output. This assigns
ownership to the fixed mesh; it is not a force-directed viewer/layout.

kitchen/geography_honeycomb.py reads the existing geography as the identity
and hierarchy input. It never reopens PDFs or chapter lists. Old parent
coordinates are retained as layout_anchor_lat/lon so rebuilding from the
installed map uses the same original targets. District rasterization tests
the actual spherical polygon half-spaces, not approximate hex stamps.

## Safe build and installation

From the repository root:

```bash
OPENBLAS_NUM_THREADS=2 OMP_NUM_THREADS=2 MKL_NUM_THREADS=2 .venv/bin/python kitchen/geography_honeycomb.py
```

This writes a candidate to ignored kitchen/logs/honeycomb-candidate/. It
refuses direct build output to either live geography directory. Source
identities are copied verbatim; chapter page counts are not layout weights.

Initial installation was performed with:

```bash
.venv/bin/python kitchen/geography_honeycomb.py --install
```

Installation verifies candidate hashes and source identity/bounds, requires
an unfrozen schema and no existing Neo4j territories, and backs up both old
geography directories before replacing the viewer assets. The actual backup:

`kitchen/logs/before-honeycomb-20261023T201406461287Z/`

It contains export-geography/ and site-geography/ for the rectangular map.
No Neo4j data were changed. A later migration after database loading needs
an explicit coordinate update, not this empty-database installer.

Do not rerun --install on the old candidate after installation: its source
hash intentionally refers to the pre-install map. For a future rebuild,
generate a fresh candidate from the current geography first. The saved
layout anchors preserve reproducibility. The old geography.py rectangle
command refuses to overwrite a directory marked chapter-honeycomb.

Nir approved the resulting displayed map (Checkpoint 3.4) on 23 Oct before
going to sleep: "it looks great, yes i am very happy with it!!!" The canonical
data/export/geography/build.json now has geometry_review_pending=false,
seating_approved=true and approved_by_human=true, with the approval quote.
This does not approve an entity registry or either Freeze. The loader's
pending-review guard remains in the software for a future replacement map.

## Verification performed

Installed dependency versions checked before use: NumPy 2.5.3, SciPy 1.18.1,
NetworkX 3.7, Pillow 12.3.0 and Matplotlib 3.11.2. No dependency installation.

```bash
OPENBLAS_NUM_THREADS=2 OMP_NUM_THREADS=2 TMPDIR=/tmp/opencode .venv/bin/python -m unittest discover -s kitchen -p 'test_*.py'
```

101 Python tests pass, including seven new honeycomb tests covering actual
4,763-cell topology/area/shared edges, polygon raster coverage, integral
capacities, retained identity/page metadata, empty headings and reproducible
rebuilding from the installed coordinates. Artificial chapter fixtures do
not constitute new book reading or medical data.

```bash
VIEWER_EXPECT_HONEYCOMB=1 VIEWER_EVIDENCE_PREFIX=honeycomb- node kitchen/test_viewer_browser.mjs
```

All ten browser integration checks pass on the real new geometry. The
browser also checks the actual 4,751/12 tile counts, WebGL, Harrison alignment,
district picking, drag/navigation, two views, synthetic entity shells and
cascades, touch/mobile, missing-data handling and no-WebGL fallback.

Visually inspected evidence, all ignored local files:

- kitchen/logs/honeycomb-candidate/seating-preview.png
- kitchen/logs/honeycomb-viewer-real-globe.png
- kitchen/logs/honeycomb-viewer-harrison-alignment.png
- kitchen/logs/honeycomb-viewer-phone-globe.png
- kitchen/logs/honeycomb-viewer-browser-results.json (the ten check names)

The new globe was requested open with xdg-open successfully. The local
viewer server remains running. The geometry loader dry run reports 37 books
and 5,334 territories. The updated loader query, which carries tile_sides
and layout anchors into Neo4j, was accepted with EXPLAIN (no writes). Actual
read-only count still returns `[{'labels': ['Meta'], 'count': 3}]`.

The updated link check reports 44 checked assets/links, zero broken and 21
explicitly pending medical exports (search.json plus 20 district samples).
The shared honeycomb topology is now checked too. git diff --check passes.

## Next inexpensive work -- DeepSeek handoff

The visual review is complete and recorded; do not ask Nir to repeat it.
He paused for sleep. Follow HANDOFF-2026-10-23-NIGHT-DEEPSEEK.md on his next
authorised continuation. A later appearance adjustment belongs to SMART;
completed contents/book-completeness checking is not the next assignment.

The routine GitHub save was completed tonight at Nir's explicit request
(726d5c4, pushed). Its scope includes HONEYCOMB.md, GEOGRAPHY.md,
kitchen/geography.py, kitchen/geography_honeycomb.py, kitchen/honeycomb_mesh.py,
kitchen/honeycomb_partition.py, kitchen/test_honeycomb.py,
kitchen/load_geography.py, data/export/geography/ and site/data/geography/.
The updated wording and browser/link-check tools are also intentional.
Inspect status/diffs first; do not stage ignored backups, previews, receipts,
logs, PDFs or credentials. These viewer/honeycomb changes are already committed.

With this map approved, INDEX-PIPELINE.md remains the next routine
workflow: Qwen reader startup, bounded Harrison trial, approved geography
load and supervised index/registry execution, one book and human review at
a time. The existing IDs/page bounds still match those tools. Stay with
DeepSeek for long execution. Return to SMART for the later Freeze/rules/
software work or a generic software failure after two attempts.
