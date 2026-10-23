# Restart handoff -- paused actual 3D viewer implementation, 23 Oct 2026

LATEST SCOPE CORRECTION FROM NIR: build the ACTUAL viewer, not a disposable
preview or a warm-up for another programmer. Read section 13 as well as the
saved checklist in section 12. The initial geography-only code is the
starting point, not the definition of the finished assignment. The current
session is still paused for a save/restart; this correction changes the
next programming assignment, not the truth of what is already working.

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

## 12. EXACT SAVED OPENCODE TODO LIST AND IMPLEMENTATION PROCEDURE

This section explicitly preserves the sidebar checklist Nir asked about.
It is the active implementation assignment after restart. The unfinished
items are PAUSED, not abandoned. The sidebar showed cancelled when Nir
stopped the session; that UI status must not erase the remaining work.
Restore the tasks from this file instead of relying on conversation memory.

### Task 1 -- Check the configured local reader and the BIBLE's 3D viewer requirements

STATUS: COMPLETED for inspection only. No model was loaded. Do not spend
another session repeating the same inventory or rereading the whole BIBLE.

Already established:

1. The installed, configured book reader is qwen3.8:27b, for both text and
   images, on the existing Ollama 0.32.14 server. Its API responded; no
   model was resident in memory at the last check. Installed does not mean
   already loaded. This reader runs on Nir's laptop, not a paid cloud API.
2. The BIBLE routes generic programming to SMART, repetitive execution to
   DeepSeek, and page reading/classification to that local reader.
3. Part 7 sections 2, 4-6 and 8-10 were read for the current work. Required
   technology: locally vendored Three.js and OrbitControls for the globe,
   Canvas 2D for the map, existing JSON/PNG geography and fixed layout.
4. Required interactions: rotate/zoom; click a district through the actual
   raster; show real book/province/chapter names; keep texture and click
   coordinates aligned. Part 7's Harrison alignment check is mandatory.
5. The existing local-reader command is `.venv/bin/python kitchen/reader.py`.
   It can load the installed model on demand through the configured local
   endpoint and should return {'ok': True}. This is an actual existing
   BIBLE command, not an invented launcher. It has not been run in the
   paused 3D session. DeepSeek can run it with Nir watching when index
   processing is due; the geography preview itself does not need Qwen.

Acceptance of Task 1 does NOT mean the reader is warmed up, the index
pipeline has run, or the globe works. It means the requirements and exact
installed components were identified. Recheck only a fact that changed.

### Task 2 -- Build the actual 3D viewer from the approved map

STATUS: PARTIALLY IMPLEMENTED, UNTESTED. Resume this task first.

The sidebar originally said "Build a working 3D geography preview from the
approved map". Nir explicitly corrected that wording and scope: he wants
the actual application. The original title is preserved here as history;
the active assignment is the real viewer, with the full scope in section 13.

The initial code is saved in the seven site/viewer files listed in section
7. The dependencies are already saved under site/assets/three (section 8).
Do not start over, redownload Three.js or regenerate the approved geography.

Implementation sequence:

1. Read the seven SMALL authored viewer files once. Do not print/read the
   60,000-line Three.js core or its bundled module; use VERSION.txt for
   dependency identity. Check git status before edits and preserve user work.
2. Run syntax checks for the five authored JS modules. Proposed command for
   the resumed session, not a command already executed:

       for file in app data geo globe3d map2d; do node --check "site/viewer/$file.js" || break; done

3. Confirm index.html's import map maps 'three' to the LOCAL module and
   OrbitControls resolves it. The local module's relative three.core.js
   import must work. No CDN/network dependency is required at runtime.
4. Check data.js loads only the existing public viewer assets using relative
   URLs. It should build the territory-ID and raster-code lookups, decode
   the 2048x1024 PNG into ImageData and resolve a click to the real district.
   Keep the ID raster lossless; do not smooth/recolour it for hit-testing.
5. Check globe3d.js follows BIBLE 7.8: SphereGeometry(1,96,64), a texture
   material with sRGB colour space, OrbitControls, fixed world coordinates,
   camera movement rather than automatic planet movement, and rendering
   only during interaction/damping/camera animation. Both texture sizes
   already exist. Use the small one on small screens/limited hardware.
6. Verify geo.js's coordinate convention with focused tests: lon=0/lat=0
   points along +x; lon=90 points along -z; north points along +y. The
   equirectangular pixel conversion must agree with the approved raster.
   The sphere hit uses px=uv.x*2048, py=(1-uv.y)*1024 and code=R*256+G.
7. Use Three.js Raycaster against the planet geometry to compare known
   territory centres with their texture UVs. Then run the actual browser
   alignment(home) check. A mirrored globe or misassigned click is a
   failing test, not a cosmetic issue. Do not change approved seating to
   hide a coordinate bug. Use the BIBLE's sign convention and verify it.
8. In app.js, verify dynamic import failures show the honest 2D fallback;
   successful startup must actually select 3D. Clicks/hash routes should
   show the actual hierarchy and stored bounds through textContent, never
   raw book-derived innerHTML. Sidebar search is specialty search at this
   stage, not a fake symptom/disease search.
9. Exercise home/selection marker clearing, malformed/unknown hashes,
   drag versus click, pointer cancellation/release, zoom bounds and camera
   tween/damping. Fix only diagnosed issues. In map2d.js verify letterbox
   coordinates, click mapping and canvas redraw after it becomes visible.
10. Retain the geography-preview label. Entity registries, clinical links,
    entity shells/altitudes and cascades are not implemented by this
    prototype. Do not invent sample medical facts or disguise missing data.

The first visible milestone is real browser evidence of the textured globe
and working interactions. Task 2's full completion also requires the actual
viewer functionality and honest data-state handling described in section 13.
A JS syntax check, a flat image, a 2D fallback or the old 88 Python tests
does not verify the new viewer.

### Task 3 -- Verify/open the globe and give DeepSeek exact reader-start instructions

STATUS: NOT STARTED. Do it after finishing Task 2; do not omit the opening.

A. Serve the actual viewer locally

- An import-map/ES-module app needs HTTP, not file://. Use a temporary
  localhost-only development server rooted at site/, not the repo root.
- A valid standard-library command for the next session is:

      .venv/bin/python -m http.server 8765 --bind 127.0.0.1 --directory /home/nir/second-opinion/site

- This server has NOT been started. Before using that port, check it is
  free or already serves this same app. If another application owns it,
  choose a free port and report the actual URL; do not kill that app.
- If a persistent launcher is useful, create and test kitchen/open_globe.py
  first; it does not exist at this checkpoint. Keep it small: reuse a
  verified existing preview server or start one rooted at site/, wait a
  bounded time for its HTML marker, then open the URL. Record its process
  and log under ignored kitchen/logs. Do not invent an already-working
  launcher in the reply. A direct server command is sufficient if simpler.
- No changes to Apache/Caddy/cloudflared, system services or sudo. Serving
  site/ must not make kitchen/.env or book PDFs available.

B. Verify in a real browser, economically

- Use installed Google Chrome 150 or Firefox 140; a desktop is available.
  Prefer existing tools over installing playwright/selenium or more browsers.
- For automation, Chrome's DevTools Protocol plus Node 26 native fetch and
  WebSocket can avoid new dependencies. Use an isolated temporary profile
  under /tmp/opencode and a free loopback debugging port. Do not touch
  Nir's normal browser profile/settings or close his existing windows.
- Chrome flags such as --headless=new, --remote-debugging-port=9223 and
  --user-data-dir=/tmp/opencode/second-opinion-globe-test are a proposed
  test setup, not an existing running process. Verify the port is free.
  If headless WebGL needs a software graphics backend, diagnose that
  locally; do not silently fall back to a flat map and call it 3D.
- Obtain the page target from Chrome's /json/list, attach to its debugger
  WebSocket, correlate incrementing request IDs and enable Runtime/Page.
  Capture JS exceptions, failed asset requests and startup status.
- Bounded wait for document.body.dataset.state='ready'. Require its mode
  to be '3d' and alignment to be 'passed', and confirm the globe canvas
  has a live WebGL context and visible rendered contents.
- Test rotation and zoom, a real planet click and the correct district
  panel, specialty selection (e.g. Cardiology), home navigation, 2D/3D
  toggling, resize and a narrow phone-size viewport. A drag must not act
  as a chapter click. Data must match the approved input, not hardcoded
  expected placeholder names.
- Capture a real screenshot through Page.captureScreenshot (or another
  installed browser facility) into ignored kitchen/logs. View it with
  the image-reading tool to check actual appearance, not just DOM flags.
- Keep geometry tests focused and add tests for diagnosed bugs. Do not
  rerun the entire Python suite after every CSS/JS change. Broader checks
  are justified only when affected code or a new failure warrants them.

C. Open the verified view for Nir

- The intended URL, if port 8765 is the actual server, is:

      http://127.0.0.1:8765/viewer/#/globe

- Open the actual successful URL with xdg-open, for example:

      xdg-open "http://127.0.0.1:8765/viewer/#/globe"

- Do not merely send another map screenshot or say "you can open it".
  Nir explicitly asked to SEE the 3D view. Request the browser opening
  after verification, leave its preview server alive while he uses it,
  and tell him briefly: drag, scroll/pinch, click a region.
- Clean up only the isolated automation browser/processes you started.
  The user's normal browser and the server needed for his open view stay.

D. Give DeepSeek a concrete reader-start procedure

- Update INDEX-PIPELINE.md's startup section to name Qwen qwen3.8:27b and
  Ollama explicitly and give the existing reader.py test command, not
  vague "start the free model" instructions. Do not require Nir to
  figure out a second AI chat, model choice or download.
- DeepSeek can run `.venv/bin/python kitchen/reader.py` with Nir watching.
  Explain it loads the already-installed local reader if needed and
  tests the configured connection. Expect {'ok': True}; if it fails,
  save the exact error and diagnose it before launching index batches.
- Do not expose .env/passwords/tokens. Do not secretly start a GPU job
  during this save-only session. Do not build a new readiness wrapper
  unless the existing command is genuinely insufficient.
- The next bounded index commands already exist in INDEX-PIPELINE.md:
  index_parse.py HARRISON-22 --limit 1, then index_classify.py HARRISON-22
  --limit 1. Keep medical interpretation with the local reader and the
  long execution with DeepSeek. No completed contents work is reopened.

Task 3 is completed only when the verified globe was actually requested
open in Nir's browser and the DeepSeek document contains explicit, real
reader-start/test commands with the actual installed model name.

### Task 4 -- Record the results and save the changes to GitHub

STATUS: The interrupted-work checkpoint was saved/pushed as 0ed46ec.
This checklist expansion is a documentation-only follow-up. The final
WORKING-globe checkpoint is still pending Tasks 2 and 3.

After that implementation is actually verified: update PROGRESS.md with
exact commands, browser/test evidence, screenshot path, actual working URL,
what is implemented and what remains. Update this handoff's status instead
of starting another contradictory instruction chain. Inspect status/diff,
stage only intended changes, commit/push and confirm the working tree.
No claims that a globe test populated Neo4j or finished the medical viewer.
Keep AGENTS.md a short pointer and leave global memory unexpanded.

### What the next session should say and do

One brief sentence to Nir: "I will build the actual globe application,
test it and open it for you." Resume Task 2 on the SAVED code and apply
the full scope in section 13. Proceed through Task 3 and save Task 4.
Do not substitute a new audit, a giant planning conversation, another
dependency download or another handoff for substantial implementation.
If blocked, state the concrete error plainly.

## 13. Nir's scope correction: ACTUAL APPLICATION, not a minimal preview

After requesting the exact checklist, Nir explicitly objected to the word
"preview" and to the impression that SMART was doing a minimal warm-up
for a future, smarter programmer. He said SMART must do as much substantive
work as it can, rather than requiring him to push out every next feature.

This correction supersedes the narrow geography-only finish line earlier
in this file. It does NOT permit fake clinical data, incorrect completion
claims, reopening completed book work or starting unattended reader jobs.
The paused-save instruction remains in force until he resumes the work.

### What SMART is responsible for on continuation

Build the real reusable viewer defined by BIBLE Part 7, progressing from
the existing globe code into substantial functioning application code.
SMART itself is the programmer for this work. Do not defer its core
programming to an unspecified future smarter model. DeepSeek handles the
long execution/data operations; that division is for cost, not an excuse
for SMART to avoid building the application.

The existing sphere/map code is an initial increment of the SAME product.
It must be tested, corrected and developed, not discarded in favour of
another demo. A working round globe is an early deliverable, not the
automatic stopping point of the next substantial programming session.

### Implement the actual viewer features from the BIBLE

Read Part 7 sections 3-14 and the relevant Part 6 JSON export interfaces,
then implement against those specified interfaces. No whole-BIBLE reread
or invented replacement architecture is needed. The scope includes:

1. The real textured globe: rotation, zoom, stable geography, picking,
   reliable camera/navigation and actual district/book detail panels.
2. Shared real geography/data loading and hash routing, browser Back,
   caching and clear missing/loading/error states.
3. The 2D entity map and 3D entity shells, including actual lit spots,
   frequency-based sizes, unknown-frequency treatment, severity rings,
   fixed-coordinate offsets and links/cascades between entity maps.
4. The symptom/disease/treatment picker, search, entity cards, aliases,
   altitude display, district information, legend and meaningful tooltips.
5. Phone/touch/responsive behaviour and the BIBLE's browser checks, plus
   focused tests of coordinate alignment, picking, routes and data use.
6. The required export/integration code where it is necessary for the
   viewer to consume Neo4j-derived data through the defined formats.

Build as much of this real software as feasible in a substantial SMART
session. Do not declare victory after adding one button, a static image,
or a globe-only minimum and then hand another programming to-do to Nir.
Save sensible working checkpoints as development proceeds. Explain only
meaningful milestones briefly; keep routine implementation out of chat.

### Missing medical data does not mean missing software is acceptable

The approved geography is real and can be displayed now. Registry terms,
relationships and altitudes are produced by later data execution. Their
absence must be represented honestly in the application, but it does not
prevent writing the viewer code described by the BIBLE's data formats.
Use explicitly artificial test fixtures to test those features, isolated
from the actual published project data. Do not add invented medical facts
or invented entities to make the actual application appear populated.

The user-facing product is Second Opinion's actual viewer. Avoid making
"preview" its permanent goal or using that word to reduce the assignment.
Distinguish software functionality from available data plainly. Show Nir
the real working globe, and tell him in one short sentence which data
layers are populated. Never claim live clinical layers have been loaded
when they have not.

After the substantial generic programming, give DeepSeek concrete working
commands for the remaining repetitive execution, as Nir originally asked.
Return to the remaining BIBLE stages with a clear next step. Preserve the
full-project path rather than repeatedly waiting for Nir to identify each
obvious missing piece. Keep global memory unchanged and AGENTS.md short.
