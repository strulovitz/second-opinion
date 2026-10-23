# Restart handoff -- paused 3D geography preview, 23 Oct 2026

## 1. Read this first: Nir stopped the session

Nir requested a restart because the session/context was getting expensive.
His current instruction is SAVE THE WHOLE SITUATION in a detailed text file,
put a SHORT reference in the project AGENTS.md, and stop. Do not expand
global memory. Do not continue coding, load a model or start a job during
this save-only step. The pending globe work is NOT tested or complete.

Communication correction: talk normally and briefly. Explain one practical
step in simple language before a substantial action. Do not send long
bullet lists, rapid-fire updates, internal deliberation, self-debugging
monologues or repeated file reads. Nir is a beginner, not a speed reader.
He wants the project built and visible, not endless handoffs/checking.
Use friendly emojis only in chat, never in project files or memory.

He asked why he had to ask about 3D to get visible progress. Own the poor
communication and lack of a clear overall build path; do not blame him or
claim that unfinished software works. A short explanation of the next
deliverable is better than another essay or asking him to plan the project.

## 2. What Nir asked immediately before stopping

He asked what "the free model" means, wanted BIBLE instructions that he or
DeepSeek can actually execute, and asked whether the 3D globe works and
whether he can see it. SMART responded:

- The laptop reader does page/term work without a paid API bill.
- GPT writes reusable software; DeepSeek operates the long workflows.
- The rotatable globe was NOT built; the earlier image was a flat map.
- SMART began a 3D geography preview using the approved map.

The next user message STOPPED development and requested this handoff.
Finish saving, then wait for the new session/user's continuation.

## 3. Repository and last completed checkpoints

Repository: /home/nir/second-opinion, github.com/strulovitz/second-opinion,
branch main. Stable HEAD before this paused work: 0140ecf.

- c73e74e: geography generator and initial alphabetical map.
- 406106a: explicit A5-to-SMART hand-back instructions.
- a816e30: DeepSeek saved Nir's approved clinical seating/geography.
- 41fbd27: SMART delivered the A6 index-to-Neo4j software.
- 0140ecf: INDEX-PIPELINE.md execution handoff.

Current project stage: Part 3 Phase A. Geography approved; A6 software
written, actual registry execution still pending. The new 3D preview is an
early visible geography-only part of Part 7, requested by Nir; it does not
mean the full medical viewer or later phases are complete.

Read governing BIBLE sections economically: Part 7 sections 2, 4-6, 8-10
for the viewer; Part 3 section 7 for the index workflow. Do not reread all
fourteen BIBLE files. The BIBLE is never edited.

## 4. Completed data and the closed lane

The approved geography contains 37 continents, 534 provinces and 4,763
chapter districts. Input/output paths:

- kitchen/books.json -- canonical book metadata.
- data/export/geography/ -- approved generated geography/raster/textures.
- site/data/geography/ -- the five public viewer JSON/PNG assets.
- GEOGRAPHY.md -- geography implementation and approved result.

All completed contents work stays closed. Do not reopen/recheck the ten
books because the assistants previously assured Nir they were OK. Do not
attribute that assurance to an independent certification/decision by Nir.
The old KRAUSE/MIDDLETON/SABISTON checking queue is cancelled. Existing book
lists are program inputs, not a new audit assignment. No list, page range,
seat, approved map or book status was changed during this 3D session.

## 5. A6 software already delivered -- do not rebuild it

INDEX-PIPELINE.md contains the current DeepSeek operating commands. Code:
index_extract.py, index_parse.py, index_classify.py, index_resolve.py,
index_pipeline.py, index_fallback.py, review_sample.py, load_geography.py,
and their index_common/pages/prompts/registry helpers, under kitchen/.

Last completed Python suite: 88 tests passed (21 new index tests plus the
67 inherited tests). Production Neo4j LOAD and entity/proving-page queries
were accepted using EXPLAIN, with no data writes. Synthetic DB/reader test
doubles were clearly labelled, not substitutes for the registry.

One real index page was extracted as the programmer proof: Harrison PDF
4044. Its text/source-image receipt are in gitignored kitchen/logs. The
configured Harrison index is PDF 4044-4273, 230 pages. No real reader parse,
classification batch or entity ingestion has run yet.

Neo4j was checked during A6 and contains three Meta nodes and no Book,
Territory or Entity data. No Freeze. The approved geography loader must run
before index_resolve can MATCH districts. That routine execution belongs
to DeepSeek, following the approved map checkpoints and INDEX-PIPELINE.md.

Metadata inspection found 25 syntactically usable index ranges and 12
unset/invalid ranges. This is not proof of absent indexes or bad books.
DeepSeek handles index-location work with the local reader and uses the
explicit BIBLE 3.7.9 fallback only for a genuinely unusable index. No new
contents audit. Harrison registry review precedes later books alphabetically;
DeepSeek stays the operator between books, with Nir's supervision/reviews.

## 6. The laptop reader: exact facts and practical explanation

Last checked this session:

- Server: existing Ollama, version 0.32.14, HTTP API responsive.
- Installed model: qwen3.8:27b.
- Configured text model: qwen3.8:27b.
- Configured vision model: qwen3.8:27b.
- Already-loaded model list: empty.
- No model pull, model load, inference or service change was performed.

Say to Nir: "Qwen is the program on your laptop that reads the books.
DeepSeek can run it for you." Do not say only "start the free model" and
leave him to work out which application, name or command is meant.

The BIBLE's existing real reader test is executable from the repo root:

    .venv/bin/python kitchen/reader.py

This uses the existing configured local Qwen through reader.py and can load
it on demand, then should return {'ok': True}. DeepSeek can perform this
with Nir watching before the bounded index trial. No new model download is
needed. GPU startup may take time; do not silently start it during this
paused save-only session. The small paid management cost of DeepSeek is
separate from the no-paid-API local page-reading work.

The earlier idea of adding reader_ready.py was NOT implemented. No such
command/flag exists yet. Prefer the existing BIBLE helper if sufficient.
No reading/printing .env or secret values: only use the existing helpers.

## 7. Paused new 3D files -- preserve them, do not call them finished

Before this save there were no tracked changes; these new files were
untracked. They are checkpointed with this handoff, explicitly unfinished:

- kitchen/vendor_three.py: reproducible pinned dependency downloader.
- site/viewer/index.html: geography-preview page, import map, controls,
  specialty search, info panel, globe/map canvases.
- site/viewer/viewer.css: responsive dark layout and controls.
- site/viewer/geo.js: pure coordinate/pixel helpers.
- site/viewer/data.js: loads existing geography/lookup/raster and texture.
- site/viewer/globe3d.js: Three.js sphere, OrbitControls, zoom, raycast
  district picking, marker, optional guide spheres and on-demand rendering.
- site/viewer/map2d.js: flat map using the same raster selection.
- site/viewer/app.js: startup, specialty list, simple hash routing, details,
  dynamic 3D import and a 2D fallback/error message.

The viewer uses existing approved geography, not invented entities. Page
bounds are labelled "Stored page range" because their printed/PDF unit
work is separate. It has no entity search, clinical relations, altitude
assignment, lit spots or cascades yet. The sidebar explains the preview.
Do not claim that staging geography is a completed Neo4j medical export.

No browser test, screenshot, live 3D display, JS test or 3D smoke test was
run before Nir stopped the work. The 88 Python tests predate these files;
they do NOT verify the new globe. No preview HTTP server was started and
no browser was opened for this viewer. open_globe.py, a local server
launcher, browser tests and the suggested reader_ready.py do not exist.

## 8. Vendored dependencies already downloaded -- do not redownload

GitHub latest Three.js release was checked: r186, published 24 Sep 2026.
Ran kitchen/vendor_three.py once, successfully. site/assets/three/ has:

- three.module.js -- 662,772 bytes.
- three.core.js -- 1,458,113 bytes, required by modern three.module.js.
- OrbitControls.js -- 40,755 bytes.
- LICENSE -- 1,081 bytes, MIT.
- VERSION.txt -- pinned npm 0.186.0, source URLs, SHA-256 hashes.

These are unmodified upstream files from pinned unpkg URLs. No runtime CDN
is intended. Modern Three.js needs its extra core module, despite the older
BIBLE's two-JS-file example. Do not rerun the downloader over these files:
it deliberately refuses replacement of existing vendor assets.

## 9. Environment for continuing the browser work economically

Checked versions: Node v26.7.0; Google Chrome 150.0.7871.181;
Firefox 140.13.0esr. Desktop DISPLAY/Wayland environment is present.
Google Chrome is /usr/bin/google-chrome; Firefox is /usr/bin/firefox.

No installed playwright, puppeteer, selenium-webdriver, Python playwright,
Python selenium or geckodriver was found. Avoid installing a large browser
stack. Node 26 has native fetch/WebSocket, so Chrome DevTools Protocol with
a temporary isolated test profile is a possible dependency-free check.
Do not change Nir's normal browser profile or persistent browser settings.

An ES-module viewer should be served over local HTTP, not simply opened as
a file URL. A bounded localhost-only development server serving site/ would
be enough. It must not expose kitchen/ or .env, replace a website, modify
Apache/Caddy/cloudflared, require sudo or become a new hosting service.
This server/launcher is proposed work, NOT already installed/running.

## 10. Next practical step after Nir resumes

Briefly explain: finish and open the existing 3D geography preview. Review
the new small viewer files, do focused coordinate/hit-test checks, then use
a real browser to verify WebGL rendering, drag/zoom, district picking,
specialty navigation, 2D toggle and responsive layout. The BIBLE requires
the Harrison marker/texture alignment self-check; a function exists but has
not yet been executed in the browser. Save a real screenshot as evidence.

Likely review points, not diagnosed bugs: home navigation/marker clearing,
invalid hashes, drag-versus-click handling, hidden-canvas resizing, pointer
release outside the canvas, WebGL fallback messaging, camera tween/control
interaction and texture-coordinate orientation. Do not assert any are fixed
or broken without checking. Preserve the approved raster/seat/data files.

Open the working view for Nir only after verifying it. Report simply what
works and that medical relationship layers are still a later step. Do not
let an early geography preview substitute for the remaining BIBLE work:
index registry and its reviews/Freeze A; reading/relations; altitudes;
entity pages/full viewer; publishing. SMART builds reusable code, DeepSeek
operates the long runs and the local reader does page/term interpretation.

## 11. Save checkpoint discipline

This checkpoint preserves partial work, not a feature-completion claim.
Use a checkpoint commit message. Check status/diff; stage only the new
viewer/vendor files, this handoff, the short AGENTS.md pointer and ledger
update. No PDF/image/private log/env file belongs in this commit. Third-party
JS/license files and their hashes are intentional public dependencies.
Do not update global memory or copy this long handoff into AGENTS.md.
