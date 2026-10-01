================================================================================
SECOND OPINION -- THE BIBLE
PART 7 OF 13 -- THE VIEWER (3-D GLOBE AND 2-D MAPS)
File: BIBLE/part-07-viewer.md
MANAGER FOR THIS PART: SMART (Claude Sonnet 5.5 / GPT 6.1 Sol) writes
                       all viewer code and the two export additions
                       (sections 3-12); [SWITCH TO CHEAP] for vendoring
                       the library files, running exports, and the
                       browser test checklist (sections 2, 13, 14).
READER:                not used in this part.
PRECONDITIONS:         Part 3 geography files exist in site/data/
                       geography/; Part 6 export (search.json,
                       entities/<slug>.json) exists; altitudes exist
                       (provisional is enough).
================================================================================

0. PURPOSE AND AMENDMENTS
--------------------------------------------------------------------------------
0.1 Purpose
  One static web application, site/viewer/index.html, that shows:
  (a) the GLOBE VIEW: a rotatable 3-D globe textured with the frozen
      geography (continents_texture.png), faint guide spheres for the
      altitude bands, click on any place to learn which district it is
      and what is discussed there;
  (b) the MAP VIEW: for one entity (one shell), the 2-D equirectangular
      map with the same texture, lit filled circles at every district
      where the books connect that entity to something (blue forward,
      yellow harm, grey differential), sized by F, F0 dashed, severity
      red ring; hover or tap shows the other entity, the frequency
      words and the book page; click opens that other entity's map
      (the CASCADE);
  (c) the same shell drawn in 3-D on the globe (toggle);
  (d) the ELEVATOR: search and three lists to pick any shell.
  Nothing moves, bends or re-arranges (Law 5). The viewer draws data;
  it never computes medicine.

0.2 BIBLE AMENDMENTS declared in this part
  AMENDMENT 7.1 (the one JavaScript library). The viewer uses Three.js
    (pinned version, vendored as site/assets/three/three.module.js and
    site/assets/three/OrbitControls.js) for the 3-D globe only. The 2-D
    map is drawn with the browser's own Canvas 2D API, no library.
    ES modules with an import map; no bundler, no npm in the repo.
  AMENDMENT 7.2 (per-district export files). New export
    site/data/districts/<territory_id>.json (also in data/export/),
    written by kitchen/export_districts.py (section 3), listing the
    entities discussed in that district. Needed for "what is here?"
    when the user clicks a place.
  AMENDMENT 7.3 (phone texture). Part 3's geography.py output is
    extended by one line: a 2048x1024 copy continents_texture_2k.png.
    The viewer loads the 2k texture when the device's maximum WebGL
    texture size is below 4096 or the screen is narrower than 900 CSS
    pixels.
  AMENDMENT 7.4 (wording shared with pages). build_pages.py (Part 6)
    also copies kitchen/prompts/wording.json to site/data/wording.json;
    the viewer reads its labels from there, so pages and viewer never
    disagree on words.
  Everything else in Parts 1-6 stands.

0.3 Order of work
  Step E0  Vendor Three.js; export additions                 (sections 2-3)  CHEAP vendors, SMART writes export
  Step E1  Files, routes, data loading, shared geometry       (sections 4-6)  SMART
  Step E2  Map view (2-D canvas)                               (section 7)     SMART
  Step E3  Globe view and shell-in-3-D (Three.js)              (section 8)     SMART
  Step E4  Panel, elevator, tooltip, legend, mobile layout     (sections 9-11) SMART
  Step E5  Errors and honesty                                  (section 12)    SMART
  Step E6  Browser and phone test checklist; Checkpoint 7.1    (sections 13-14) CHEAP + human

1. FIXED NAMES AND PATHS
--------------------------------------------------------------------------------
  site/viewer/index.html        the application shell (HTML)
  site/viewer/viewer.css        the one stylesheet
  site/viewer/app.js            router, state, panel, elevator, tooltip
  site/viewer/data.js           loading and caching of JSON and images
  site/viewer/geo.js            projections, sunflower offsets, F sizes
  site/viewer/map2d.js          the 2-D canvas map
  site/viewer/globe3d.js        the Three.js globe and shell-in-3-D
  site/assets/three/three.module.js
  site/assets/three/OrbitControls.js
  site/assets/three/VERSION.txt   the pinned version string and the
                                  download URLs used
  Data read by the viewer (all relative to site/viewer/):
    ../data/geography/geography.json
    ../data/geography/districts_lookup.json
    ../data/geography/district_raster.png      (hit-testing; code = R*256 + G)
    ../data/geography/continents_texture.png   (4096x2048)
    ../data/geography/continents_texture_2k.png (2048x1024)
    ../data/search.json
    ../data/wording.json
    ../data/entities/<slug>.json               on demand
    ../data/districts/<territory_id>.json      on demand
  Links out of the viewer: ../index.html, ../pages/<slug>.html,
  ../pages/all-*.html. All relative (Part 2 section 8.3).

2. STEP E0a -- VENDORING THREE.JS (CHEAP; Law 13)
--------------------------------------------------------------------------------
2.1 Check first: ls site/assets/three/ ; if the two files exist and
    VERSION.txt names a version, skip to 2.4.
2.2 Choose the newest release of Three.js at https://github.com/mrdoob/three.js/releases
    (versions look like r1NN). Record the version. Download exactly two
    files with curl into site/assets/three/:
      https://unpkg.com/three@0.<NN>.0/build/three.module.js
      https://unpkg.com/three@0.<NN>.0/examples/jsm/controls/OrbitControls.js
    (the npm version "0.<NN>.0" corresponds to release "r<NN>"; e.g.
    r170 = 0.170.0). If unpkg is unreachable, use
    https://cdn.jsdelivr.net/npm/three@0.<NN>.0/... with the same paths.
    Do NOT download the whole repository. Do NOT use a CDN at run time:
    the site must work from the local folder with no internet.
2.3 Write VERSION.txt: the version, the two URLs, the date, and the
    SHA-256 of each file (sha256sum). Check: head -c 300 of each file
    shows JavaScript, not an HTML error page. three.module.js is about
    1.2 MB; OrbitControls.js about 30 KB.
2.4 Three.js is MIT licensed; copy its LICENSE into
    site/assets/three/LICENSE (from https://unpkg.com/three@0.<NN>.0/LICENSE).
  EVIDENCE: ls -la site/assets/three/ ; cat VERSION.txt.

3. STEP E0b -- EXPORT ADDITIONS (SMART writes; CHEAP runs)
--------------------------------------------------------------------------------
3.1 kitchen/export_districts.py (under 120 lines). For every district:
      MATCH (d:Territory {level:"district", territory_id:$did})
      OPTIONAL MATCH (d)-[:CHILD_OF]->(p:Territory)-[:CHILD_OF]->(c:Territory)
      OPTIONAL MATCH (e:Entity)-[l:DISCUSSED_IN]->(d)
      WITH d, p, c, e, count(l) AS mentions, collect(DISTINCT l.page_number) AS pages
      OPTIONAL MATCH (e)-[r:PRESENTS_WITH|TREATED_BY|HARMS|LEADS_TO|MISTAKEN_FOR]-()
        WHERE r.district_id = d.territory_id
      RETURN d.territory_id AS territory_id, d.name AS name, d.part_name AS part_name,
             d.book_id AS book_id, d.page_start AS page_start, d.page_end AS page_end,
             d.lat AS lat, d.lon AS lon, p.territory_id AS province_id, p.name AS province_name,
             c.territory_id AS continent_id, c.name AS continent_name,
             collect({slug:e.slug, canonical_name:e.canonical_name, group:e.group,
                      mentions:mentions, pages:pages, edges_here:count(r)}) AS entities
    (one query per district, or batched; the writer may restructure
    for speed but must produce this content). Entities sorted by
    edges_here desc, then mentions desc, then name; entity objects with
    slug null (district with no mentions) are dropped. Output file:
      {"territory_id","name","part_name","book_id","page_start","page_end",
       "lat","lon","province_id","province_name","continent_id",
       "continent_name","entities":[...],"export_date"}
    Written to site/data/districts/ and data/export/districts/, only
    when content changed. Typical size: a few KB to 200 KB.
3.2 Texture 2k: add to the end of geography.py main(), before print:
      Image.open(OUT / "continents_texture.png").resize((2048, 1024), Image.LANCZOS).save(OUT / "continents_texture_2k.png")
    then re-run geography.py (deterministic: identical raster) and copy
    the new file to site/data/geography/.
3.3 build_pages.py: add one line copying kitchen/prompts/wording.json to
    site/data/wording.json (Amendment 7.4).
  EVIDENCE: ls site/data/districts | wc -l equals the district count;
  ls -la site/data/geography/continents_texture_2k.png; ls site/data/wording.json.

4. STEP E1a -- index.html (exact structure; SMART fills attributes)
--------------------------------------------------------------------------------
  <!doctype html><html lang="en"><head>
    <meta charset="utf-8">
    <meta name="viewport" content="width=device-width, initial-scale=1, maximum-scale=1">
    <title>Second Opinion -- Globe</title>
    <link rel="stylesheet" href="viewer.css">
    <script type="importmap">
      {"imports": {"three": "../assets/three/three.module.js"}}
    </script>
  </head><body>
    <nav class="top">
      <a href="../index.html">Second Opinion</a>
      <a href="#/globe" id="nav-globe">Globe</a>
      <a href="../pages/all-symptoms.html">Symptoms</a>
      <a href="../pages/all-diseases.html">Diseases</a>
      <a href="../pages/all-treatments.html">Treatments</a>
      <button id="btn-panel" class="mobile-only" aria-label="Open panel">Menu</button>
    </nav>
    <main>
      <div id="stage">
        <canvas id="globe"></canvas>
        <canvas id="map"></canvas>
        <div id="tooltip" hidden></div>
        <div id="legend"></div>
        <div id="controls">
          <button id="btn-back">Back to globe</button>
          <button id="btn-toggle">3-D</button>
          <button id="btn-zoom-in">+</button>
          <button id="btn-zoom-out">-</button>
          <button id="btn-fit">Fit</button>
        </div>
        <div id="status" hidden></div>
      </div>
      <aside id="panel">
        <section id="elevator">
          <input id="search" type="search" placeholder="Search a symptom, disease or treatment" autocomplete="off">
          <div class="tabs">
            <button data-group="symptoms-and-signs" class="on">Symptoms</button>
            <button data-group="diseases-and-conditions">Diseases</button>
            <button data-group="treatments-and-drugs">Treatments</button>
          </div>
          <ol id="results"></ol>
        </section>
        <section id="info"></section>
      </aside>
    </main>
    <script type="module" src="app.js"></script>
  </body></html>
  Import-map support: Chrome 89+, Firefox 108+, Safari 16.4+, Edge
  89+. If a browser lacks it, app.js is still loaded as a module; the
  3-D part fails to import and section 12 shows the honest message
  while the 2-D map keeps working (map2d.js does not import three).
  Therefore app.js must import globe3d.js DYNAMICALLY
  (await import("./globe3d.js")) inside a try/catch, not statically.

5. STEP E1b -- ROUTES AND STATE (app.js)
--------------------------------------------------------------------------------
5.1 Hash routes (Amendment 6.2, binding):
      #/globe                      globe view, no shell selected
      #/map/<slug>                 2-D map of the shell <slug>
      #/map/<slug>/3d              the shell drawn on the 3-D globe
      #/district/<territory_id>    globe view centred on that territory,
                                   its info in the panel
    Empty or unknown hash -> #/globe (replaceState, no history entry).
    Every navigation is done by setting location.hash (so the browser
    Back button works for free). The router listens to "hashchange"
    and to the initial load.
5.2 State object (single, in app.js):
      { route: "globe"|"map"|"map3d"|"district",
        slug: string|null, entity: object|null,
        territoryId: string|null, hover: object|null,
        group: "symptoms-and-signs" (current elevator tab),
        query: "" }
5.3 On route change:
    globe:    show #globe canvas, hide #map; globe3d.showGlobe();
              panel info = the globe intro (section 9.1);
              #btn-toggle label "2-D" disabled; #btn-back hidden.
    map:      load entity (data.entity(slug)); show #map; map2d.render(
              entity); panel info = entity card (9.2); #btn-toggle "3-D";
              #btn-back visible.
    map3d:    load entity; show #globe; globe3d.showShell(entity);
              panel = entity card; #btn-toggle "2-D".
    district: load district (data.district(id)); show #globe;
              globe3d.lookAt(lat, lon); panel = district card (9.3).
    Loading indicator: #status "Loading <file>..." while awaiting;
    hidden on success; on failure section 12 applies.

6. STEP E1c -- DATA (data.js) AND SHARED GEOMETRY (geo.js)
--------------------------------------------------------------------------------
6.1 data.js: async functions with in-memory caches (a Map per kind):
      geography()   -> parsed geography.json plus two derived Maps:
                       byId (territory_id -> object) and
                       codeToId (from districts_lookup.json)
      search()      -> search.json array (loaded once; a few MB)
      wording()     -> wording.json
      entity(slug)  -> entities/<slug>.json
      district(id)  -> districts/<id>.json
      raster()      -> an ImageData of district_raster.png drawn on an
                       offscreen canvas 2048x1024 (loaded once)
      texture()     -> HTMLImageElement of the 4k or 2k texture
                       (choice rule in Amendment 7.3), loaded once
    Every fetch uses relative URLs exactly as section 1 lists. A 404 or
    network error rejects with an Error whose message is the URL.
6.2 geo.js constants and functions (exact; both views use these so the
    2-D and 3-D positions agree):
      export const W = 2048, H = 1024;                 // raster size
      export const COLOUR = { blue:"#1f5fbf", yellow:"#e0a800", grey:"#6b6b6b",
                              red:"#b3261e", lit:"#ffffff" };
      export const RELATION_COLOUR = { PRESENTS_WITH:"blue", TREATED_BY:"blue",
                              HARMS:"yellow", LEADS_TO:"yellow", MISTAKEN_FOR:"grey" };
      export function lonLatToPixel(lon, lat) {        // equirectangular
        return [ (lon + 180) / 360 * W, (90 - lat) / 180 * H ];
      }
      export function pixelToLonLat(px, py) {
        return [ px / W * 360 - 180, 90 - py / H * 180 ];
      }
      export function radiusPx(f) {                     // circle size by F
        const F = (f === 0) ? 3 : f;                    // F0 drawn at F3 size, dashed
        return 3 + 2.2 * F;                             // F1 5.2px ... F5 14px
      }
      export function sunflower(i, n, base) {           // offsets when several
        if (n <= 1) return [0, 0];                      // circles share a district
        const a = i * 2.39996323;                       // golden angle in radians
        const r = base * 1.3 * Math.sqrt(i + 1);
        return [ r * Math.cos(a), r * Math.sin(a) ];
      }
      export function districtCode(imageData, px, py) { // hit-test helper
        const x = Math.max(0, Math.min(W - 1, Math.floor(px)));
        const y = Math.max(0, Math.min(H - 1, Math.floor(py)));
        const k = (y * W + x) * 4;
        return imageData.data[k] * 256 + imageData.data[k + 1];
      }
    In LaTeX, the projection is $x = \frac{lon + 180}{360}\,W$,
    $y = \frac{90 - lat}{180}\,H$, identical to Part 3 section 6.2.
6.3 Spots to draw for an entity (shared by both views; function
    spotsFor(entity, geography) in geo.js):
    For each aggregated edge in entity.edges and for each DISTINCT
    district_id among its statements: one SPOT with
      { district_id, lon, lat (from geography.byId), colour =
        RELATION_COLOUR[relation], f = max f_scale over that district's
        statements, severity = any severity among them, dashed = (f ==
        0), relation, direction, subtype, other_slug, other_name,
        other_group, statement = the statement with the highest
        f_scale in that district (for the tooltip), count = number of
        statements in that district }
    Then for each lit_spot (district, book) that has NO spot from edges:
    one LIT SPOT { district_id, lon, lat, lit: true, pages, book_id }
    drawn as a small hollow white dot (radius 3 px, 1.5 px stroke):
    "discussed here, no relation extracted yet". Spots are grouped by
    district_id; inside a district they are ordered blue, yellow, grey,
    then f desc; the i-th of n gets the sunflower offset with base =
    the largest radiusPx in that district. Severity-ringed spots are
    drawn last so the ring is never covered.

7. STEP E2 -- THE 2-D MAP (map2d.js)
--------------------------------------------------------------------------------
7.1 Canvas: #map fills #stage (CSS), its drawing buffer is sized to
    stage size times devicePixelRatio (crisp on phones). A view
    transform {scale, tx, ty} maps raster pixel coordinates (0..W,
    0..H) to canvas pixels. "Fit" sets scale so the whole 2:1 image
    fits the stage, centred. Zoom limits: fit-scale .. fit-scale * 16.
7.2 Rendering, in order, every frame that needs it (no animation loop;
    redraw on input):
    (1) clear; (2) draw the texture image with the view transform
    (imageSmoothingEnabled = true); (3) for each spot, compute the
    screen position of its district centre + sunflower offset (offsets
    in SCREEN pixels, so they do not shrink when zooming out), then:
      lit dot: strokeStyle white, lineWidth 1.5, arc r=3;
      edge spot: fillStyle COLOUR[colour], globalAlpha 0.92, arc
        r=radiusPx(f); if dashed: setLineDash([4,3]), strokeStyle =
        same colour darkened, lineWidth 2, fill with globalAlpha 0.35
        instead of 0.92; if severity: setLineDash([]), strokeStyle
        COLOUR.red, lineWidth 3, stroke a ring at r+2;
    (4) if a spot is hovered: draw a white ring r+4 around it;
    (5) nothing else: no lines, no beams, no labels on the map itself
    (labels live in the tooltip and the panel; the texture already
    carries the continent names).
7.3 Input (Pointer Events so mouse and touch share code):
    - pointerdown + move: pan (tx, ty += delta) when one pointer; pinch
      zoom when two pointers (scale by ratio of distances, around the
      midpoint); wheel: zoom by factor 1.15 per notch around the cursor;
      #btn-zoom-in/out: factor 1.5 around the stage centre; #btn-fit.
    - A "click" is a pointerup within 6 px and 400 ms of its pointerdown
      with no second pointer.
    - Hit-test order on click or mouse-move: the nearest spot whose
      screen distance to the pointer is <= its radius + 6 px wins (lit
      dots: 8 px). If none: the district under the pointer via the
      raster (pixel -> districtCode -> codeToId).
    - mouse-move over a spot: tooltip (section 10) follows the pointer;
      cursor pointer. Over a district only: tooltip shows the district
      name and its book; no cursor change.
    - click on an edge spot: desktop -> navigate to #/map/<other_slug>
      (the cascade). Touch -> first tap shows the tooltip with an
      "Open" button; a second tap on the same spot, or on the button,
      navigates; a tap elsewhere closes the tooltip.
    - click on a lit dot: panel shows that district's card (data
      .district) and the entity's pages there; no navigation.
    - click on empty territory: panel shows the district card.
7.4 Performance: fever at 42 books may have a few thousand spots. Draw
    once per input event; no per-frame redraw. If spots > 4000, the
    sunflower base is reduced by 30% and lit dots are hidden until the
    scale exceeds 2 x fit-scale (declared in the legend: "zoom in to see
    all mentions").

8. STEP E3 -- THE GLOBE AND THE SHELL IN 3-D (globe3d.js)
--------------------------------------------------------------------------------
8.1 Scene: WebGLRenderer on #globe (antialias true, alpha false,
    setPixelRatio min(devicePixelRatio, 2)); PerspectiveCamera fov 40;
    OrbitControls (enableDamping true, dampingFactor 0.08, minDistance
    1.3, maxDistance 12, enablePan false); ambient light 1.0 (the
    texture carries its own colours; no shading tricks). Initial camera
    at distance 4.6 looking at the origin from lat 15, lon 0 (so the
    Harrison hub at lat 0 lon 0 faces the user; Part 3 section 6.3 b).
    Background colour #0b0f1a.
8.2 Planet: SphereGeometry(1, 96, 64) with MeshBasicMaterial({ map:
    texture, transparent: true, opacity: 1 }). texture.colorSpace =
    SRGBColorSpace; anisotropy = renderer.capabilities
    .getMaxAnisotropy(). Guide spheres: for each radius in [1.50, 1.80,
    2.10, 2.40, 2.70, 3.00] a SphereGeometry(r, 48, 32) with
    MeshBasicMaterial({ wireframe: true, transparent: true, opacity:
    0.07, color: 0xffffff }); and 1.00 is the planet surface itself.
    (Faint; they show the bands without hiding the planet.)
8.3 Lat/lon to 3-D position (Three.js is y-up; this formula matches
    the way SphereGeometry wraps an equirectangular texture, with
    u = 0 at lon -180 on the -x side):
      export function lonLatToVec3(lon, lat, r) {
        const la = lat * Math.PI / 180, lo = lon * Math.PI / 180;
        return new THREE.Vector3( r * Math.cos(la) * Math.cos(lo),
                                  r * Math.sin(la),
                                 -r * Math.cos(la) * Math.sin(lo) );
      }
    In LaTeX: $x = r\cos(lat)\cos(lon)$, $y = r\sin(lat)$,
    $z = -r\cos(lat)\sin(lon)$.
    SELF-CHECK (mandatory, section 14 item 6): after loading, place a
    temporary marker with lonLatToVec3 at the Harrison continent's
    lat/lon from geography.json; it must sit on the Harrison label in
    the texture. If it is mirrored east-west, set z = +r cos(lat)
    sin(lon) instead and record the change in PROGRESS.md. Do not
    guess; look.
8.4 Hit-testing on the globe: Raycaster from the pointer; intersect the
    planet mesh only; take intersection.uv; raster pixel px = uv.x * W,
    py = (1 - uv.y) * H (Three.js flipY is true by default);
    districtCode -> codeToId -> territory. This uses the texture
    mapping itself, so it is correct even if 8.3 needed the sign flip.
    Click (pointerup within 6 px / 400 ms) on the planet -> navigate to
    #/district/<territory_id>. Hover on desktop: tooltip with the
    district name and book (throttled to one raycast per animation
    frame).
8.5 lookAt(lat, lon): rotate the camera (not the globe) so the point
    faces the user: set camera position = lonLatToVec3(lon, lat,
    currentDistance) blended over 600 ms (ease in-out), controls
    .update(). The planet never rotates by itself (Law 5: the user
    moves the camera; the world stays put).
8.6 showShell(entity): remove previous shell objects; then
    - shell sphere: SphereGeometry(entity.altitude, 64, 48) with
      MeshBasicMaterial({ transparent: true, opacity: 0.10, color:
      group tint: symptoms 0x2fae6a, diseases 0xc0533a, treatments
      0x4a6bd6, side: THREE.DoubleSide, depthWrite: false });
    - planet opacity: 0.35 if entity.altitude < 1 (a disease shell is
      inside the planet; the planet becomes glass so the shell shows),
      else 1.0; restore to 1.0 in showGlobe();
    - one Sprite per spot (section 6.3) at lonLatToVec3(lon, lat,
      entity.altitude) plus a tiny tangential offset for the sunflower
      (offset vector = sunflower offset in pixels / 400, applied along
      the local east and north directions), SpriteMaterial with a
      generated CanvasTexture: 12 textures cached (3 colours x
      severity yes/no x dashed yes/no), each a 64x64 canvas drawn with
      the same rules as 7.2; sizeAttenuation: false so that the sprite
      size encodes F regardless of zoom: sprite.scale.set(s, s, 1) with
      s = radiusPx(f) * 2 / stageHeightPx * 1.6 (SMART tunes the 1.6 so
      F5 on the globe looks the same as F5 on the map at fit scale);
      depthTest true so spots behind the planet are hidden (the glass
      planet at 0.35 still occludes partially: accepted);
    - lit dots as small white sprites (same mechanism, radius 3);
    - sprite.userData = the spot; raycast against sprites first (before
      the planet) for hover and click; click on a spot cascades to
      #/map/<other_slug>/3d (staying in 3-D), touch rules as in 7.3;
    - camera: lookAt the entity's spot with the highest f (or the first
      lit spot), distance = max(current, entity.altitude + 1.8).
8.7 showGlobe(): remove shell objects, planet opacity 1, keep camera.
8.8 Render loop: requestAnimationFrame only while controls are damping
    or a camera blend is running or the pointer is down; otherwise
    render once per change. (Battery on phones.)
8.9 Resize: on window resize set renderer size and camera aspect; the
    2-D map re-fits only if it was at fit scale.

9. STEP E4a -- THE PANEL (#info; app.js)
--------------------------------------------------------------------------------
9.1 Globe intro (route globe): title "The globe"; one paragraph from
    wording.json key "globe_intro" (default: "Every continent is one
    textbook. Every chapter is a district. Click a place to see what is
    discussed there, or search a symptom, disease or treatment to open
    its map."); the band legend (lines: "0.30-1.00 diseases and
    conditions (deep = multisystem)", "1.00-1.50 symptoms and signs
    (low = nonspecific)", "1.50-3.00 treatments (lifestyle, over-the-
    counter, prescription, biologics/chemo/radiation, surgery)"); the
    counts from search.json (entities per group) and the ledger date
    if ../data/ledger.json exists (Part 9) else nothing.
9.2 Entity card (routes map, map3d): group label; h2 canonical_name;
    aliases (up to 6, "and k more"); the altitude line (same templates
    as Part 6 section 2, from wording.json; the viewer formats {r} to 3
    decimals); a line "Showing {spots} lights in {districts} districts
    from {books} books; {blue} blue, {yellow} yellow, {grey} grey";
    links: "Read the page" -> ../pages/<slug>.html; "Open in 3-D" /
    "Open in 2-D" (route toggle); "Back to globe". Then a compact list
    of the entity's aggregated edges grouped under the same section
    titles as the HTML page (wording.json), each item: other_name
    (link to #/map/<other_slug> or /3d when in 3-D), F label, severity
    pill, "{n} sentences". This list is the keyboard- and screen-reader-
    friendly twin of the circles. Hovering an item highlights its spots
    on the map (white rings); clicking an item navigates.
9.3 District card (route district, and on clicks in 7.3/8.4): breadcrumb
    "{continent_name} > {province_name or part_name} > {name}"; book_id
    and printed pages page_start-page_end; a line "{k} entities
    discussed here"; three lists (symptoms, diseases, treatments)
    from districts/<id>.json, each entity as a link to #/map/<slug>
    with "{edges_here} connections, {mentions} mentions"; capped at 60
    per list with "and k more in the data file" linking the JSON. A
    "Show on globe" button -> #/district/<id>.
9.4 All panel text uses textContent or escaped HTML; never innerHTML
    with raw data (names come from books; they can contain < and &).

10. STEP E4b -- THE TOOLTIP (#tooltip)
--------------------------------------------------------------------------------
  Position: near the pointer (offset 14 px, flipped to stay inside the
  stage). Content for an edge spot, in this order:
    line 1: other_name (bold), group label small
    line 2: the relation phrase from wording.json for (relation,
            direction, subtype), e.g. "Caused by" / "Can cause"
    line 3: F label; if numeric_pct: "{pct}%"; if severity: "serious"
            red pill; if dashed: "frequency not stated in the books"
    line 4: the frequency_phrase verbatim in quotes, if any
    line 5: "{book_id}, {district_name}, p.{page}" of the top statement;
            if count > 1: "and {count-1} more sentences"
    line 6 (touch only): an "Open" button
  For a lit dot: entity name, "discussed in {district_name}
  ({book_id}), pages {ranges}". For a district: "{name} -- {book_id}
  pages {start}-{end}". Tooltip never exceeds 320 px wide; text wraps.

11. STEP E4c -- THE ELEVATOR, THE LEGEND, MOBILE LAYOUT
--------------------------------------------------------------------------------
11.1 Elevator: on input in #search (debounced 120 ms) and on tab click,
     filter search.json rows of the current group where canonical_name
     or any alias contains the query (case-insensitive, accents
     stripped on both sides). Empty query: show the whole group sorted
     by rank (altitude ascending: nonspecific symptoms first, deep
     diseases first, lifestyle treatments first). Render at most 300
     rows ("type to narrow" line when more); each row: name, altitude
     to 3 decimals, "{edge_count}" with a small bar whose width is
     proportional to log(1 + edge_count), and a muted "no text yet" if
     has_text is false. Click -> #/map/<slug> (or /3d if currently in
     3-D). Pressing Enter opens the first row. The search box also
     matches the query against district names in geography.json and
     shows up to 10 district hits under a "Places" heading -> #/district/<id>.
11.2 Legend (#legend, bottom-left of the stage, always visible, from
     wording.json): three colour swatches (blue "forward: presents
     with / treated by", yellow "harm: side effect / leads to", grey
     "often mistaken for"); five filled circles F1..F5 with the F
     labels; a dashed circle "frequency not stated"; a red-ringed
     circle "serious"; a hollow white dot "discussed here (no relation
     extracted yet)". Collapsible on phones (a small "Legend" button).
11.3 viewer.css (SMART writes; rules that must exist):
     - html, body { height:100% } ; main { display:grid; grid-template-
       columns: 1fr 360px; height: calc(100% - 48px) } ; #stage
       { position:relative; overflow:hidden; background:#0b0f1a } ;
       canvas { position:absolute; inset:0; width:100%; height:100% ;
       touch-action:none } ; #panel { overflow:auto; background:#fbfbf8;
       padding:1em; font: 15px/1.45 system-ui, sans-serif }.
     - @media (max-width: 900px): main { grid-template-columns: 1fr }
       ; #panel becomes a bottom sheet: position:fixed; left:0;
       right:0; bottom:0; max-height:55%; transform:translateY(100%)
       by default; class "open" -> translateY(0); #btn-panel toggles
       it; .mobile-only visible only here.
     - #controls { position:absolute; top:.6em; right:.6em; display:
       flex; gap:.4em } buttons at least 40x40 px (thumb size).
     - #tooltip { position:absolute; pointer-events:none (except its
       Open button on touch: pointer-events:auto); background:
       rgba(20,20,20,.92); color:#fff; padding:.5em .7em; border-
       radius:6px; max-width:320px; font-size:14px }.
     - The same colour variables as pages.css (Part 6 section 7).
     - prefers-reduced-motion: camera blends become instant.

12. STEP E5 -- ERRORS AND HONESTY (Law 11 on the user's side)
--------------------------------------------------------------------------------
  Nothing fails silently. #status (top-centre of the stage) shows:
  - while loading: "Loading <short file name>..."
  - if a data file is missing (404): "This part of the data has not
    been built yet: <file>. The rest of the viewer still works." and
    the view falls back (map with texture only; globe with no shell).
  - if WebGL or the import map is unavailable: "3-D view is not
    available in this browser; showing the 2-D map." and #btn-toggle
    is disabled; routes /3d redirect to the 2-D map; #/globe shows the
    2-D map of nothing (texture only) with the elevator.
  - if an entity has zero spots: the map shows the texture and the
    panel says "No relation from the books has been read for this
    entity yet; it appears in the index of {k} chapters (white dots)."
  The browser console additionally logs every error with the URL.

13. SCRIPT AND FILE LIST FOR THIS PART
--------------------------------------------------------------------------------
  site/viewer/index.html, viewer.css, app.js, data.js, geo.js, map2d.js,
  globe3d.js                      (SMART; each JS file under 400 lines;
                                   geo.js exactly as section 6.2 plus
                                   spotsFor of 6.3)
  site/assets/three/three.module.js, OrbitControls.js, LICENSE, VERSION.txt
                                  (CHEAP vendors; section 2)
  kitchen/export_districts.py     (SMART; section 3.1)
  one-line additions to kitchen/geography.py and kitchen/build_pages.py
                                  (section 3.2, 3.3)
  kitchen/check_links.py          extend: also check that every
                                  ../data/... URL in the viewer JS
                                  exists as a file (static list of the
                                  nine names in section 1 plus a sample
                                  of 20 random entities/<slug>.json and
                                  20 random districts/<id>.json).
  Local test: cd site && python3 -m http.server 8765 then open
  http://localhost:8765/viewer/index.html#/globe (file:// does NOT
  work for ES modules and fetch; always use the local server or the
  tunnel).

14. STEP E6 -- BROWSER AND PHONE TEST CHECKLIST (CHEAP prepares, HUMAN
    performs; results pasted in PROGRESS.md; Checkpoint 7.1)
--------------------------------------------------------------------------------
  Browsers: Chrome (desktop), Firefox (desktop), Edge (desktop), and on
  the human's phone: Chrome on Android and/or Safari on iPhone
  (whichever the human has; record which). For each browser, each line
  must be "pass":
   1. #/globe loads; the globe shows coloured continents with readable
      names; drag rotates; wheel (or pinch) zooms; nothing moves by
      itself.
   2. Clicking (tapping) on the Harrison continent opens a district
      card whose breadcrumb starts with the Harrison field name.
   3. Elevator: type "fever"; the first result is the fever symptom;
      Enter opens #/map/symptoms-and-signs-fever; the 2-D map shows the
      same continents as the globe with circles on them (or white dots
      only, if Phase B has not reached those chapters: that is fine and
      the panel says so).
   4. Hover (desktop) a circle: tooltip shows another entity's name, an
      F label, a book and page. Tap (phone): tooltip with "Open"; second
      tap opens the other entity's map. The browser Back button returns
      to the fever map.
   5. The "3-D" button opens #/map/symptoms-and-signs-fever/3d: the
      fever shell is a faint sphere just above the surface with spots
      on it; "2-D" returns; "Back to globe" returns to #/globe.
   6. SELF-CHECK of 8.3: open #/district/<Harrison continent's first
      district id>; the camera centres on the Harrison label (not on
      its mirror image on the other side of the globe). If mirrored,
      SMART applies the sign flip of 8.3 and this item is re-tested.
   7. Open a disease map in 3-D (e.g. diseases-and-conditions-
      hypertension/3d): the planet turns to glass and the shell is
      visible inside it, with spots.
   8. Open ../pages/<any slug>.html and click "Show me on the globe":
      the viewer opens on that entity's map.
   9. On the phone: the panel opens and closes with the Menu button;
      buttons are tappable with a thumb; pinch-zoom on the 2-D map
      works; the page never scrolls sideways.
  10. Load with the network disabled after one full visit is NOT
      required (no offline promise).
  11. The URL https://www.strulovitz.org/2nd-opinion/viewer/index.html#/globe
      works through the tunnel exactly like the local server.
  Any "fail" is written under BLOCKED with the browser name and what
  happened, and SMART fixes it. CHECKPOINT 7.1: all lines pass in all
  tested browsers; the human says "ok". Recorded under DECISIONS BY
  HUMAN.

15. DEFAULTS IN THIS PART THAT THE HUMAN MAY OVERTURN
--------------------------------------------------------------------------------
  (1) Three.js + Canvas 2D, vendored, ES modules with import map
      (Amendment 7.1).
  (2) Circle radius 3 + 2.2 F pixels; F0 at F3 size, dashed (6.2).
  (3) Sunflower arrangement for several circles in one district (6.2).
  (4) Lit-only mentions drawn as hollow white dots (6.3).
  (5) Glass planet (opacity 0.35) when a disease shell is shown in 3-D;
      shell sphere opacity 0.10; guide spheres opacity 0.07 (8.2, 8.6).
  (6) Camera moves, globe never rotates by itself (8.5).
  (7) Panel 360 px on desktop; bottom sheet under 900 px (11.3).
  (8) Elevator shows at most 300 rows; districts in search under
      "Places" (11.1).
  (9) Initial camera distance 4.6 from lat 15, lon 0 (8.1).

================================================================================
HANDOFF CAPSULE (updated; paste into a NEW conversation with Fable when
asking for the next part)
================================================================================
Project: "Second Opinion", a medical knowledge globe built only from N
(up to 42) medical textbooks the human owns, vibe-coded, open source,
hosted at https://www.strulovitz.org/2nd-opinion/ from the human's own
computers via Cloudflare Tunnel, synced through
https://github.com/strulovitz/second-opinion (laptop = kitchen with
Neo4j; desktop serves static site/ only). Fable writes a 13-delivery
BIBLE (9 parts + 4 appendix templates) in plain text, one copy-paste
block per delivery, no tables, no collapsibles, formulas in words plus
LaTeX. Delivered: Part 1 (charter, 15 laws, world model: WHERE =
library geography, WHICH = altitude, one shell per entity, no single
home, rigid layout, five edge types PRESENTS_WITH/TREATED_BY blue,
HARMS(subtype CONTRAINDICATED_IN)/LEADS_TO yellow, MISTAKEN_FOR grey,
F-scale 0-5, severity ring), Part 2 (environment, repo layout
kitchen/ data/ site/ BIBLE/, AGENTS.md + PROGRESS.md headings: CURRENT
PHASE, NEXT STEP, QUESTIONS FOR HUMAN, BLOCKED, LATER IF MONEY,
ENVIRONMENT INVENTORY, INSTALLS, DECISIONS BY HUMAN, DONE; Neo4j
schema; kitchen/db.py, .env; tiers), Part 3 (Phase A: geography.py
Fibonacci+Voronoi equal-area continents, treemap districts ~ page
count, raster 2048x1024, textures; index pipeline P-A4a/b/c; Freeze A),
Part 4 (Phase B reading pipeline P-B0/P-B0f/P-B1/P-B2, verification,
quarantine, ledger), Part 5 (Phase C altitudes, Freeze B, insertion
rule), Part 6 (export_entities.py, write_texts.py P-D1, build_pages.py
zero-JS pages + pages.css, check_links.py, wording.json, STANDARD
REBUILD, viewer hash routes #/globe, #/map/<slug>, #/map/<slug>/3d,
#/district/<id>), Part 7 (viewer: site/viewer/index.html + viewer.css
+ app.js + data.js + geo.js + map2d.js + globe3d.js; Three.js pinned
and vendored in site/assets/three/ with import map, dynamic import so
2-D works without WebGL; 2-D = Canvas 2D equirectangular with texture,
spots per (edge, district) coloured by relation, radius 3+2.2F px, F0
dashed at F3 size, severity red ring, sunflower offsets, hollow white
dots for index-only mentions, pan/pinch/wheel, hit-test spots then
district raster (code R*256+G); 3-D = textured sphere r=1, guide
wireframe spheres at 1.50..3.00, lonLatToVec3 y-up with mandatory
self-check, raycast uv -> raster for districts, showShell = translucent
sphere at altitude + sprites sizeAttenuation false, glass planet 0.35
for disease shells, camera moves never globe; panel: globe intro,
entity card with edges list, district card from new
site/data/districts/<id>.json (Amendment 7.2, export_districts.py);
tooltip rules; elevator from search.json max 300 rows + Places;
legend; mobile bottom sheet under 900 px; honest #status messages;
continents_texture_2k.png for phones (Amendment 7.3); wording.json
copied to site/data/ (Amendment 7.4); 11-item browser/phone checklist;
Checkpoint 7.1). Tiers: READER = free local Qwen 3.8 27B Q4_K_M
(Gemma 4 31B substitute) does all per-page/per-term work; CHEAP =
DeepSeek V4.1 Flash runs scripts, vendors, tests; SMART = Claude
Sonnet 5.5 or GPT 6.1 Sol writes code; manager says "HUMAN: please
switch to <tier>" and stops. Laws include: books only, provenance
always, Neo4j single source of truth, cheap beats perfect, never
assume installed, when unclear stop and ask, one disclaimer only
(site/index.html bottom), no multi-model editions, books/images/
transcripts never committed, report with evidence.
Next delivery requested: Part 8 (Manager Operating Protocol: the full
text of AGENTS.md; the full PROGRESS.md template; the session start
ritual; the batch procedure; the evidence rules with examples of
acceptable and unacceptable reports; the model-switch procedure; the
"stuck" procedure; the git discipline; the forbidden list; how the
human audits a session in five minutes).
================================================================================
