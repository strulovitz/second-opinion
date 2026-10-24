# Actual viewer software and DeepSeek handoff -- 23 October 2026

> **SUPERSEDED ON 24 OCT 2026 (Claude Opus 5.5, approved by Nir).** The map is now the
> Goldberg ball (Amendment 3.6) and the viewer has the Sand table / Atlas looks, the flower
> 2-D map, the future layers and DEMO mode. The exact, binding description is in the
> "CLAUDE OPUS 5.5 ADDITION" blocks at the top of BIBLE parts 1, 3 and 7. Where this file
> disagrees with those blocks, the blocks win. This file is kept as history.


LATEST GEOGRAPHY: Nir requested and authorised one near-equal-size chapter
tile, mostly hexagons with pentagons. That implementation is now built/tested/
opened and Nir has approved its appearance. Read the current overnight
handoff, HANDOFF-2026-10-23-NIGHT-DEEPSEEK.md, before execution; HONEYCOMB.md
has the geometry detail. The viewer work and commands below still apply;
the old equal-continent/rectangle layout does not.
GITHUB SAVE COMPLETED at Nir's explicit bedtime request: implementation and
approved map/handoff pushed as 726d5c4. The routine-save section below is
historical staging guidance; next session begins with the supervised trial.

## Working view

The saved globe code has been developed into the actual reusable viewer.
Open it with:

```bash
.venv/bin/python kitchen/open_globe.py
```

Actual URL: http://127.0.0.1:8765/viewer/#/globe

The launcher serves only site/ on loopback, reuses the same verified server,
and asks the desktop browser to open the view. Server PID/root/URL are in
ignored kitchen/logs/globe-server.json; output is in globe-server.log. An
occupied port serving another application is refused; use --port to choose
another. The current server was left running for Nir. xdg-open successfully
requested the real URL in the desktop browser during this session.

## Software delivered versus data available

Real public data: 37 books, 534 provinces and 4,763 districts, with the new
honeycomb textures and lossless picking raster. The later Amendment 3.5
changed the geometry, not chapter identity, hierarchy or source page bounds.

Implemented BIBLE Part 7 functionality:

- Vendored Three.js textured globe, drag/pinch/wheel, zoom controls, fit,
  correct UV/raster picking, Harrison-centred home, selection marker,
  optional altitude guides, camera animation and reduced-motion support.
- Shared geometry, cached relative asset/data loading, four hash routes,
  browser Back, cancellation of stale route/panel results and explicit
  missing-data/WebGL fallback states.
- Canvas 2D entity maps with pan, wheel/pinch, raster picking, lit dots,
  deterministic sunflower offsets, district-specific F sizes/dashes,
  harm/forward/differential colours, red severity and white hover rings.
- 3D entity shells/sprites, glass planet for inner disease shells,
  raycast/cascade on actual sprites, provenance tooltips and touch first-tap
  inspection/second-tap navigation. Rendering stops when idle.
- Three-group elevator, accent-insensitive name/alias search, Enter,
  altitude/rank/count rows, place search, specialty navigation, entity and
  district cards, keyboard-accessible relationship links, shared wording,
  legend and phone bottom sheet. Narrow-screen globe framing is corrected.
- Neo4j-only entity/search and district exporters, mirrored idempotent
  output, preserved quote/image provenance, wording copy and link checker.

The application itself has NO invented sample entities. search.json, real
entity/district exports, registry altitudes and clinical relationships are
not populated. Neo4j still holds only three Meta nodes. Missing registry
data is stated in the actual interface. The 3D entity mode requires a real
exported altitude; none is fabricated from rank, order or medical knowledge.
Part 6 entity HTML pages, Phase B reading pipeline, Phase C altitude software
and Part 9 final publishing remain later work. This viewer checkpoint does
not claim those parts, either Freeze or human Checkpoint 7.1 complete.

## Programmer evidence

Checked installed versions: Node v26.7.0, Python 3.13.5, Google Chrome
150.0.7871.181, Neo4j Python driver 6.4.0 and Neo4j Kernel 2026.09.0.
No new dependency installation. Vendored Three.js r186 was reused unchanged.

Commands from the repository root:

```bash
node --test kitchen/test_viewer.mjs
.venv/bin/python -m unittest discover -s kitchen -p test_viewer_export.py -v
.venv/bin/python kitchen/open_globe.py --no-open
node kitchen/test_viewer_browser.mjs
.venv/bin/python kitchen/check_links.py --allow-pending
```

Results: 4 focused JS tests, 6 Python export tests and 10 browser integration
checks passed. Browser checks exercise real globe/district picking, UV
alignment, drag versus click, specialty/route navigation, artificial entity
search, actual 2D/3D spot tooltips and cascades, Back, inner shell, phone
layout, two-tap touch interaction, missing exports and unavailable WebGL.
No uncaught browser exception or uncancelled failed network request.
The original 88 Python tests were not rerun or relabelled as globe proof.

Browser automation uses installed Chrome and Node's native WebSocket/CDP,
with an isolated disposable profile in /tmp/opencode. Artificial entity
responses are injected into that test browser's fetch only. They are not
medical claims and were never written into site/data/ or Neo4j. That browser
and its profile are removed on test completion; Nir's normal browser stays.

Evidence under ignored kitchen/logs/:

- viewer-browser-results.json -- ten named passing checks.
- viewer-real-globe.png -- real data, no synthetic entities.
- viewer-harrison-alignment.png -- marker at the real Harrison label.
- viewer-synthetic-map.png, viewer-synthetic-shell.png,
  viewer-synthetic-glass.png -- explicitly artificial integration fixtures.
- viewer-phone-globe.png, viewer-phone.png -- 390x844 viewport evidence.

Screenshots were opened and visually inspected. A phone-size viewport is
not a test on Nir's physical phone. Remaining browser/phone/tunnel and human
acceptance checks belong to BIBLE 7.14, with real data when available.

All six exporter queries were accepted with EXPLAIN on the real Neo4j
server (no writes); query constants are in export_entities.py and
export_districts.py. Unknown-property/type notifications are expected on
the empty data graph. The actual read-only count query:

```cypher
MATCH (n) RETURN labels(n) AS labels, count(*) AS count
```

returned `[{'labels': ['Meta'], 'count': 3}]`.

Original viewer checkpoint link check: 43 links/assets, 0 broken, 21 explicitly pending medical
exports (search index and 20 sampled district files). --allow-pending is
only the Phase A programming check. A final exported build must pass the
default strict command, without this flag.
After the honeycomb change the count is 44, including its shared topology;
broken/pending counts are unchanged. See HONEYCOMB.md for the newest evidence.

## DeepSeek: exact next task and when to switch back

This is now routine execution. Read the newest PROGRESS.md and
INDEX-PIPELINE.md. The GitHub save below is complete; run the bounded
Harrison trial with Nir watching next session.
Qwen qwen3.8:27b via Ollama reads pages; DeepSeek operates the scripts.

First commands, after briefly explaining the trial to Nir:

```bash
.venv/bin/python kitchen/reader.py
.venv/bin/python kitchen/index_pipeline.py HARRISON-22 --plan --limit 1
.venv/bin/python kitchen/load_geography.py
.venv/bin/python kitchen/index_parse.py HARRISON-22 --limit 1
.venv/bin/python kitchen/index_classify.py HARRISON-22 --limit 1
```

The reader test should return {'ok': True}. Review the one page/batch with
Nir before the full run. Follow INDEX-PIPELINE.md for loading the approved
geography into Neo4j, the full Harrison workflow and Checkpoint 3.5. After
each book, stop for Nir's review/choice. Remain on DeepSeek across books.
The completed contents work stays closed. This assignment is the index to
entity registry, not book completeness checking or a contents audit.

Return to SMART for the Freeze A software/rules review after the registry
workflow and required reviews are complete, or earlier for a reproducible
generic code failure that DeepSeek has failed to resolve twice. Bring exact
command, error and local evidence paths; do not pay SMART to babysit pages.
SMART still owns future reusable reading/altitude/page/publishing software.

The new export integration is ready for execution when the BIBLE's data
preconditions are met; it is not an instruction to skip those phases:

```bash
.venv/bin/python kitchen/export_viewer.py
.venv/bin/python kitchen/check_links.py
```

export_viewer reads Neo4j through db.run, exports entity/search and district
JSON into data/export/ and site/data/, then copies the shared wording. It
never loads a model, computes altitudes or changes Neo4j. Empty entity or
territory graphs are refused rather than erasing an existing real export.
To copy UI wording alone without a database connection:

```bash
.venv/bin/python kitchen/export_viewer.py --wording-only
```

When Part 6 build_pages.py is implemented, it must use this same wording
file and invoke the existing entity exporter rather than replace its format.

### Routine GitHub save -- completed at Nir's bedtime request

SMART finished programming and verification, then handed off the routine
save. Nir subsequently explicitly asked for GitHub backup immediately before
sleep. Commit 726d5c4 includes the intended implementation/map/handoff and
was successfully pushed. Starting HEAD was 42af00d. The staging list below
is retained as historical scope, not an unfinished task for DeepSeek.

Inspect git status, git diff and git log --oneline -10 first, including the
new files. Stage only the implementation/docs/UI wording named below. PDFs,
source-page text/images, .env, screenshots, server receipts and reader logs
remain ignored. Do not rerun book checks, download dependencies or repeat
already-passing browser tests just to make a commit. If code changes, run
the relevant focused check again.

Intended staging list:

```bash
git add AGENTS.md PROGRESS.md HANDOFF-2026-10-23-3D-RESTART.md INDEX-PIPELINE.md VIEWER.md site/index.html site/viewer site/data/wording.json data/export/wording.json kitchen/prompts/wording.json kitchen/viewer_export.py kitchen/export_entities.py kitchen/export_districts.py kitchen/export_viewer.py kitchen/open_globe.py kitchen/check_links.py kitchen/browser_cdp.mjs kitchen/test_viewer.mjs kitchen/test_viewer_browser.mjs kitchen/test_viewer_export.py
git diff --cached --check
git diff --cached --stat
```

The actual implementation commit message was `7.3-12 build the viewer and
approved chapter honeycomb`. Its successful push is recorded in PROGRESS.md
and the overnight handoff. For later changes, never stage the whole
repository blindly or silently discard user changes.
