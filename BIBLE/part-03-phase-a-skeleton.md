================================================================================
SECOND OPINION -- THE BIBLE
PART 3 OF 13 -- PHASE A: BUILDING THE SKELETON
File: BIBLE/part-03-phase-a-skeleton.md
MANAGER FOR THIS PART: CHEAP (DeepSeek V4.1 Flash) for running steps;
                       [SWITCH TO SMART] marks the steps where scripts
                       are WRITTEN (sections 5, 6, 8).
READER FOR THIS PART:  free local model (Qwen 3.8 27B Q4_K_M), TEXT mode
                       only; vision is not needed in Phase A except the
                       rare fallback in 7.9.
================================================================================

0. PURPOSE, INPUTS, OUTPUTS, AMENDMENTS
--------------------------------------------------------------------------------
0.1 Purpose
  Turn the 42 books into the frozen SKELETON:
  (a) GEOGRAPHY: 42 continents, their provinces and districts, each with
      page ranges and a position on the globe, painted into a raster;
  (b) ENTITY REGISTRY: every symptom, disease and treatment named in the
      42 back-of-book indexes, each with its group, its aliases, and its
      index-derived lit spots (DISCUSSED_IN) with provenance.
  Altitudes are NOT assigned here (Part 5). Pages are NOT read here
  (Part 4).

0.2 Inputs (provided by the human)
  - The 42 PDF files, copied into kitchen/books/ (gitignored).
  - A started local reader server (Ollama, LM Studio or Unsloth Studio)
    with an OpenAI-compatible endpoint, address in kitchen/.env.
  - The human's answers at the six checkpoints (section 10).

0.3 Outputs
  - kitchen/books.json: one record per book (section 2.4).
  - Neo4j: Book, Territory, Entity nodes; CHILD_OF, REPRESENTS,
    DISCUSSED_IN relationships.
  - data/registry/books.csv, territories.csv, entities.csv,
    aliases.csv (Appendices A, B, C are generated from these).
  - data/export/geography/ : district_raster.png, district_raster.npy
    (kitchen only, gitignored if over 40 MB), continents_texture.png,
    districts_lookup.json, geography.json.
  - The Freeze A git tag (section 11).

0.4 BIBLE AMENDMENTS declared in this part (Law 14, cheap beats perfect)
  AMENDMENT 3.1 (changes Part 1 section 3.2 c): continents have EQUAL
    area (the 42 Voronoi cells of a Fibonacci sphere are nearly equal).
    Page-count proportionality applies to provinces and districts INSIDE
    each continent, exactly. Reason: weighted Voronoi on a sphere is
    hard; equal continents are visually fine. Written to "LATER, IF
    MONEY".
  AMENDMENT 3.2 (changes Part 2 section 6.1 B): Territory.border_geojson
    is set to null for all territories. Borders are not polygons; they
    are pixels. New Territory properties: raster_code (integer, the
    district's code in the raster; null for continents and provinces),
    colour_hex (string), bbox_px (list of four integers x0,y0,x1,y1 in
    the 2048 x 1024 raster). The viewer (Part 7) uses the raster
    textures and districts_lookup.json for hit-testing.
  Everything else in Parts 1 and 2 stands.

0.5 Order of work in this part
  Step A0  Book intake and text-layer check         (sections 2)   CHEAP
  Step A1  One-book-per-field: duplicate detection  (section 3)    CHEAP + human
  Step A2  Tables of Contents -> territories        (section 4)    CHEAP + reader
  Step A3  page_offset detection                    (section 4.6)  CHEAP
  Step A4  Scripts: reader helper, geography        (sections 5,6) SMART
  Step A5  Seating, raster, textures                (section 6)    CHEAP runs + human
  Step A6  Indexes -> entity registry               (section 7)    SMART writes, CHEAP runs, reader works
  Step A7  Load, verify, review samples             (sections 8,9) CHEAP + human
  Step A8  Freeze A                                 (section 11)   CHEAP + human

1. HELPER TOOLS NEEDED IN THIS PART (Law 13: check, then install)
--------------------------------------------------------------------------------
  Check:
    which pdftotext pdftoppm pdfinfo pdffonts; pdftotext -v
  These come from the Debian package poppler-utils. If missing:
    sudo apt install -y poppler-utils         (ask the human first)
  Python (inside .venv, no sudo): already installed in Part 2. Add:
    pip install pyyaml rapidfuzz
    pip freeze > kitchen/requirements.txt
  rapidfuzz is used ONLY to pick candidate matches for the reader to
  judge (section 7.6); it never decides anything by itself.
  EVIDENCE: versions of pdftotext, pdftoppm; "import rapidfuzz" OK.

2. STEP A0 -- BOOK INTAKE
--------------------------------------------------------------------------------
2.1 For each PDF in kitchen/books/, run and record:
    pdfinfo "<file>"                      (Pages, Title, Page size)
    pdffonts -f 1 -l 5 "<file>" | head    (if it lists fonts, there is a
                                           text layer)
    pdftotext -f <N> -l <N> "<file>" - | wc -c
       with N = a page about 40% into the book; more than 500 characters
       means the text layer is usable on that page.
2.2 book_id: apply the rule of Part 2 section 6.1 A (eponym or first
    title word, UPPERCASE, hyphen, edition; or year if no edition).
    Example: "Harrison's Principles of Internal Medicine, 22nd edition"
    -> HARRISON-22. Write the proposed 42 ids in PROGRESS.md; the human
    may rename any before they are used.
2.3 Page images for Phase B (can run in the background now; not needed
    for Phase A). Harrison already exists as images named
    harrison-internal-medicine_Page_0001.png etc. For the others:
      mkdir -p kitchen/pages/<BOOK_ID>
      pdftoppm -r 150 -png "kitchen/books/<file>.pdf" kitchen/pages/<BOOK_ID>/page
    which produces page-0001.png, page-0002.png ... (pdftoppm pads to the
    number of digits of the page count). Record the resulting pattern in
    books.json as image_name_pattern, e.g. "page-{n:04d}.png".
    Disk: about 0.3 MB per page; 42 books x 2000 pages x 0.3 MB is about
    25 GB. Check df -h first. If space is short, convert later, book by
    book, when Phase B reaches it.
2.4 kitchen/books.json (committed; the single per-book configuration).
    One object per book with these keys:
      book_id            "HARRISON-22"
      pdf_file           "harrison-internal-medicine.pdf"
      title              verbatim
      edition            "22"
      year               2025
      page_count_images  4273
      text_layer         true | false
      image_dir          "kitchen/pages/HARRISON-22"
      image_name_pattern "harrison-internal-medicine_Page_{n:04d}.png"
      toc_images         [5, 17]        image numbers of the TOC pages
      index_images       [4101, 4273]   image numbers of the index pages
      page_offset        null           filled in 4.6
      field_name         ""             filled in 3.3
      cluster            ""             filled in 6.3
      status             "candidate"
      notes              ""
    Keep this file sorted by book_id. Every later script reads it.
2.5 Finding toc_images and index_images:
    TOC: pdftotext -f 1 -l 40 "<pdf>" - and look for the page(s) where
    lines end with page numbers and the word "Contents" appears. Index:
    pdftotext of the LAST 300 images; the index starts at the first page
    whose text begins with "Index" (or "INDEX") followed by lines of the
    form "Term, 123, 456". Record both ranges. If uncertain, open the
    PDF at that page and look; if still uncertain, ask the human.
  EVIDENCE: kitchen/books.json with 42 records; the pdfinfo outputs in
  PROGRESS.md; df -h.

3. STEP A1 -- ONE BOOK PER FIELD (Law 6)
--------------------------------------------------------------------------------
3.1 For each book extract the TOC text (section 4.1) and write a
    one-line field description: the book's own subject words from its
    title and its Part/Section headings, e.g. "cardiovascular medicine",
    "clinical dermatology", "obstetrics", "pharmacology".
3.2 Duplicate detection (script, deterministic): two books are
    CANDIDATE DUPLICATES if (a) their field descriptions share a key
    word (cardio-, derm-, neuro-, gastro-, nephro-, endocrin-, hemat-,
    onco-, infect-, pediatr-, obstet-, gynec-, psychiat-, pulmon-,
    rheumat-, ophthalm-, otolaryng-, urol-, orthop-, anesth-, emergenc-,
    pharmac-, nutrit-, surg-, radiol-, patholog-, immun-, geriatr-),
    OR (b) more than 30% of the chapter titles of the smaller book have
    a near-identical title (rapidfuzz token_set_ratio >= 85) in the
    larger book. The general textbook (Harrison) is EXEMPT: it is the
    hub and overlaps with everything by design.
3.3 For each candidate pair write to QUESTIONS FOR HUMAN a comparison
    with exactly these facts for each book: title, edition, year, page
    count, number of chapters, text layer yes/no, index yes/no, and
    the overlap percentage from (b). Add one line "Suggestion: keep X
    because <the newer edition / the larger index / the better text
    layer>". The HUMAN decides. Losers get status
    "rejected-duplicate" and are never touched again. Winners get
    status "accepted" and a field_name written in books.json (short,
    Title Case, e.g. "Cardiology"; this becomes the continent name).
    If after this step fewer than 42 books remain, the project has
    fewer continents; everything below works with any number N.
  CHECKPOINT 3.1: the human has decided every pair; books.json has N
  accepted books with field names. EVIDENCE: the list in PROGRESS.md
  under DECISIONS BY HUMAN.

4. STEP A2 -- TABLES OF CONTENTS -> TERRITORIES
--------------------------------------------------------------------------------
4.1 Extract the TOC text:
      pdftotext -f <toc_start> -l <toc_end> -layout "<pdf>" kitchen/logs/<BOOK_ID>-toc.txt
    If text_layer is false: render the TOC images and give them to the
    reader in vision mode with the prompt in 4.3 (same prompt, image
    attached instead of text). This is the only vision use in Phase A.
4.2 Province rule (fixed):
    - The DISTRICT is the chapter: the smallest numbered unit that has
      its own starting page in the TOC.
    - The PROVINCE is the innermost heading level directly above the
      chapters. In Harrison, Part 2 has Sections, so the provinces of
      Part 2 are its Sections and each province stores part_name =
      "PART 2 Cardinal Manifestations and Presentation of Diseases".
      Part 1 of Harrison has no Sections, so Part 1 itself is the
      province (part_name = same as name).
    - A book with no heading level above chapters has ONE pseudo-province
      per book, territory_id Cnn.P00, name = the book title.
    - Online-only content, videos, atlases, supplements that have no
      printed pages in the PDF (Harrison's V1.., S1.., A1..) are NOT
      territories. Record them in books.json notes.
    - Front matter (preface, contributors) and back matter (index,
      appendices without chapter numbers) are NOT territories.
4.3 Reader prompt P-A2 (TOC text -> JSON). System message:

    You convert a medical textbook's Table of Contents into JSON. Output
    ONLY JSON, no commentary. Schema:
    {"provinces":[{"name":"<verbatim heading>","part_name":"<verbatim
    heading of the level above, or same as name>","chapters":[{"number":
    "<chapter number as printed, or null>","title":"<verbatim title>",
    "page_start":<integer printed page>}]}]}
    Rules: keep titles VERBATIM including punctuation; join titles that
    wrap over two lines; ignore author names; ignore roman-numeral pages
    (preface, contributors); ignore entries without a page number
    (online-only chapters, videos, atlases); if the book has no
    headings above chapters, output one province named "ALL" with all
    chapters; page_start must be an integer.

    User message: the full TOC text. If the TOC text is longer than
    about 20,000 characters, split it at a Part/Section boundary and
    send two or more messages, then concatenate the "provinces" lists.
4.4 Validation (script kitchen/toc_validate.py; CHEAP writes this; it
    is a 40-line script):
    - page_start strictly increasing across the whole book (allow equal
      for a chapter that starts on the same page as the previous one
      ends; never decreasing). Report every violation.
    - chapter count equals the count of lines in the TOC text that end
      with a number (within 5%); otherwise report.
    - page_end of chapter k = page_start of chapter k+1 minus 1; for the
      last chapter: the printed page before the first index page
      (compute from 4.6) or, if unknown, page_start + median chapter
      length.
    - Province page_start/page_end = min/max of its chapters.
    - If validation fails, do NOT hand-edit the JSON. Re-run the reader
      on the failing portion with the error message appended to the
      user message ("The previous attempt had this problem: ... Fix
      it."). After two failures: QUESTIONS FOR HUMAN with the raw TOC
      text attached.
    Save the validated result as kitchen/logs/<BOOK_ID>-toc.json.
4.5 Territory IDs: continent Cnn with nn = seat_order (section 6.3;
    use the provisional alphabetical order of book_id until seating is
    approved, then renumber ONCE before anything is loaded into Neo4j).
    Province Pmm: sequential in book order from P01 (P00 only for the
    pseudo-province). District Dkkk: the printed chapter number if the
    book numbers chapters; else sequential from D001 within the book.
4.6 Step A3: page_offset. printed_page = image_number - page_offset.
    Method: take four chapters spread through the book (the 1st, and
    those at 25%, 50%, 75%). For each, search the PDF text for the
    chapter title near its expected image: 
      for N in range(page_start + 0, page_start + 60):
        pdftotext -f N -l N "<pdf>" - | grep -i -F "<first 25 characters of the title>"
    The first image N where the title appears as a heading gives
    offset_candidate = N - page_start. All four candidates must agree;
    then page_offset = that value. If they disagree, the book has
    several numbering sequences (common when parts restart at page 1):
    write QUESTIONS FOR HUMAN with the four values; the human may
    decide to keep the most common value and accept small errors
    (cheap) or to record a per-province offset in books.json
    ("page_offsets": [{"from_image":..,"offset":..}]).
    Cross-check: pdftotext -f N -l N for one of those images should show
    the printed page number in its header or footer.
4.7 For each accepted book: write toc.json; set status
    "geography-done" in books.json.
  CHECKPOINT 3.2: for every book the human receives a 5-line summary
  (book_id, number of provinces, number of districts, first and last
  printed page, page_offset) and the list of any validation warnings.
  The human says "ok" or names books to redo. EVIDENCE: the summaries
  in PROGRESS.md; `ls kitchen/logs/*-toc.json | wc -l` equals N.

5. STEP A4 -- SCRIPT: THE READER HELPER  [SWITCH TO SMART]
--------------------------------------------------------------------------------
5.1 kitchen/reader.py (exact content; this is the ONLY way scripts call
    the local model)

    # kitchen/reader.py -- talk to the free local model (OpenAI-compatible)
    import json, re, time, base64, sys
    from pathlib import Path
    sys.path.insert(0, str(Path(__file__).resolve().parent))
    from db import env
    import requests

    def _strip_think(text):
        return re.sub(r"<think>.*?</think>", "", text, flags=re.S).strip()

    def _extract_json(text):
        start = min([i for i in (text.find("{"), text.find("[")) if i >= 0], default=-1)
        if start < 0:
            raise ValueError("no JSON found")
        end = max(text.rfind("}"), text.rfind("]"))
        return text[start:end + 1]

    def ask(system, user, images=None, max_tokens=6000, temperature=0.0,
            expect_json=True, retries=3, timeout=3600):
        url = env("READER_BASE_URL").rstrip("/") + "/chat/completions"
        no_think = env("READER_NO_THINK_TAG", "")
        if no_think:
            system = system + "\n" + no_think
        content = [{"type": "text", "text": user}]
        for path in (images or []):
            b64 = base64.b64encode(Path(path).read_bytes()).decode()
            content.append({"type": "image_url",
                            "image_url": {"url": "data:image/png;base64," + b64}})
        body = {
            "model": env("READER_VISION_MODEL") if images else env("READER_MODEL"),
            "messages": [{"role": "system", "content": system},
                         {"role": "user", "content": content if images else user}],
            "temperature": temperature,
            "max_tokens": max_tokens,
        }
        last_error = None
        for attempt in range(retries):
            try:
                r = requests.post(url, json=body, timeout=timeout)
                r.raise_for_status()
                text = _strip_think(r.json()["choices"][0]["message"]["content"])
                if not expect_json:
                    return text
                return json.loads(_extract_json(text))
            except Exception as e:
                last_error = e
                time.sleep(3)
        raise RuntimeError(f"reader failed after {retries} attempts: {last_error}")

    if __name__ == "__main__":
        print(ask("Answer in JSON.", 'Return {"ok": true}'))

5.2 kitchen/.env additions:
      READER_NO_THINK_TAG=/no_think
        (Qwen models skip chain-of-thought when the system prompt ends
         with /no_think; for Gemma leave it empty. The human may also
         switch thinking off in the server's settings screen.)
      READER_CONTEXT_TOKENS=16384
        (the human sets the server's context length to 16k; Phase A
         prompts are sized to fit in 16k with margin.)
    Test: python kitchen/reader.py  ->  {'ok': True}
    Record the seconds it took in PROGRESS.md (this is the per-call
    cost yardstick; no other benchmarking is done).

6. STEP A4/A5 -- SCRIPT: GEOGRAPHY  [SMART writes, CHEAP runs]
--------------------------------------------------------------------------------
6.1 The Fibonacci sphere. For N centres, point i (i = 0..N-1) has
    polar angle phi_i = arccos(1 - 2(i+0.5)/N) and azimuth
    theta_i = pi (1 + sqrt(5)) (i+0.5).
    In LaTeX: $\phi_i = \arccos\!\left(1 - \frac{2(i+0.5)}{N}\right)$,
    $\theta_i = \pi\,(1+\sqrt{5})\,(i+0.5)$, and the unit vector is
    $(\sin\phi_i\cos\theta_i,\ \sin\phi_i\sin\theta_i,\ \cos\phi_i)$.
    A continent = all points of the sphere whose nearest centre (largest
    dot product) is that continent's centre. This IS the spherical
    Voronoi cell; no library is needed.
6.2 Coordinates. Latitude lat in degrees, -90 (south) to +90 (north);
    longitude lon in degrees, -180 to +180. Unit vector from lat/lon:
    $x = \cos(lat)\cos(lon)$, $y = \cos(lat)\sin(lon)$, $z = \sin(lat)$.
    The raster is equirectangular, W = 2048 by H = 1024 pixels; pixel
    column c has lon = (c + 0.5)/W * 360 - 180; pixel row r has
    lat = 90 - (r + 0.5)/H * 180. Row 0 is the north pole edge. The
    area weight of a pixel is cos(lat).
6.3 Seating (which book sits at which centre). Cheap procedure:
    (a) CHEAP assigns each accepted book a cluster word in books.json,
        from this fixed list: "general", "heart-vessels", "lungs",
        "gut-liver", "kidney-urology", "brain-nerves-mind",
        "hormones-metabolism-nutrition", "infection-immunity",
        "skin-bone-joint-muscle", "women-children-aging",
        "cancer-blood", "emergency-toxins-environment", "drugs",
        "senses" (eye, ear, nose, throat), "surgery-anesthesia",
        "imaging-laboratory". Harrison = "general".
    (b) The script seats books greedily: order books by cluster in the
        order listed above, and inside a cluster by page count
        descending. The first book (Harrison) takes the centre nearest
        to lat 0, lon 0 (so the opening globe view faces the hub).
        Each next book takes the unassigned centre nearest to the mean
        vector of the already-seated books of its cluster; if none of
        its cluster is seated yet, nearest to the last seated book.
        seat_order = 1..N in seating sequence; Cnn uses seat_order.
    (c) The script draws kitchen/logs/seating-preview.png (Matplotlib,
        equirectangular, each pixel coloured by continent, continent
        names at centres) and the human approves or asks for swaps
        ("swap Cardiology and Dermatology"). Swaps are applied by
        exchanging seat numbers in books.json and re-running.
  CHECKPOINT 3.3: seating approved. After approval seat_order and Cnn
  never change.
6.4 Subdivision inside a continent (the treemap-on-a-cell algorithm).
    Local coordinates: for a continent with centre unit vector c, build
    east = normalise(cross((0,0,1), c)) (if c is within 1 degree of a
    pole, use (1,0,0) instead of (0,0,1)), north = cross(c, east). For
    a pixel unit vector p: angular distance $\theta = \arccos(p\cdot c)$,
    azimuth $a = \operatorname{atan2}(p\cdot north,\ p\cdot east)$, local
    $x = \theta\cos a$, $y = \theta\sin a$.
    Recursive binary split on the set of pixels of a region:
    - If the region's item list has one item and that item has children
      (a province with districts), recurse into the children on the
      same pixels. If it has one item and no children, paint all pixels
      with that district's code. Stop.
    - Else split the ordered item list into a first part and a second
      part at the position where the cumulative page count is closest
      to half the total (never an empty part). Let frac = pages of the
      first part / total pages.
    - Choose the split axis: x if the pixels' x-range >= y-range, else
      y. Sort the region's pixels by that axis; take cumulative pixel
      weights (cos lat); cut at the first index where the cumulative
      weight reaches frac of the total. First part gets the pixels
      before the cut, second part the rest. Recurse on both.
    Consequence: consecutive chapters are adjacent; each district's area
    is proportional to its page count to within one pixel row.
6.5 kitchen/geography.py (exact content; writes the raster, the
    textures, geography.json, and the territory CSV)

    # kitchen/geography.py -- Phase A geography: seating, raster, textures
    import json, math, colorsys, sys
    from pathlib import Path
    import numpy as np
    from PIL import Image, ImageDraw, ImageFont
    ROOT = Path(__file__).resolve().parents[1]
    LOGS = ROOT / "kitchen" / "logs"
    OUT = ROOT / "data" / "export" / "geography"
    W, H = 2048, 1024
    CLUSTER_ORDER = ["general","heart-vessels","lungs","gut-liver","kidney-urology",
        "brain-nerves-mind","hormones-metabolism-nutrition","infection-immunity",
        "skin-bone-joint-muscle","women-children-aging","cancer-blood",
        "emergency-toxins-environment","drugs","senses","surgery-anesthesia",
        "imaging-laboratory"]

    def fibonacci_sphere(n):
        i = np.arange(n) + 0.5
        phi = np.arccos(1 - 2 * i / n)
        theta = np.pi * (1 + 5 ** 0.5) * i
        return np.stack([np.sin(phi) * np.cos(theta), np.sin(phi) * np.sin(theta), np.cos(phi)], 1)

    def latlon_to_vec(lat, lon):
        la, lo = np.radians(lat), np.radians(lon)
        return np.array([np.cos(la) * np.cos(lo), np.cos(la) * np.sin(lo), np.sin(la)])

    def vec_to_latlon(v):
        v = v / np.linalg.norm(v)
        return float(np.degrees(np.arcsin(v[2]))), float(np.degrees(np.arctan2(v[1], v[0])))

    def pixel_grid():
        lon = (np.arange(W) + 0.5) / W * 360 - 180
        lat = 90 - (np.arange(H) + 0.5) / H * 180
        LON, LAT = np.meshgrid(np.radians(lon), np.radians(lat))
        P = np.stack([np.cos(LAT) * np.cos(LON), np.cos(LAT) * np.sin(LON), np.sin(LAT)], -1)
        return P.reshape(-1, 3), np.cos(LAT).reshape(-1)

    def seat_books(books, centres):
        books = [b for b in books if b["status"] in ("accepted", "geography-done")]
        books.sort(key=lambda b: (CLUSTER_ORDER.index(b["cluster"]), -b["page_count_images"]))
        if "seat_order" in books[0] and all("seat_order" in b for b in books):
            return books  # seating already approved: keep it
        free = list(range(len(centres)))
        seated = []
        for k, b in enumerate(books):
            if k == 0:
                target = latlon_to_vec(0, 0)
            else:
                same = [centres[s["seat_index"]] for s in seated if s["cluster"] == b["cluster"]]
                target = np.mean(same, 0) if same else centres[seated[-1]["seat_index"]]
            best = max(free, key=lambda j: float(centres[j] @ target))
            free.remove(best)
            b["seat_index"] = best
            b["seat_order"] = k + 1
            seated.append(b)
        return books

    def local_xy(P, c):
        up = np.array([0, 0, 1.0]) if abs(c[2]) < math.cos(math.radians(1)) else np.array([1.0, 0, 0])
        east = np.cross(up, c); east /= np.linalg.norm(east)
        north = np.cross(c, east)
        d = np.clip(P @ c, -1, 1)
        theta = np.arccos(d)
        a = np.arctan2(P @ north, P @ east)
        return theta * np.cos(a), theta * np.sin(a)

    def split_items(items):
        total = sum(it["pages"] for it in items)
        best, best_diff, acc = 1, None, 0
        for k in range(1, len(items)):
            acc += items[k - 1]["pages"]
            diff = abs(acc - total / 2)
            if best_diff is None or diff < best_diff:
                best, best_diff = k, diff
        first = items[:best]
        frac = sum(it["pages"] for it in first) / total
        return first, items[best:], frac

    def partition(idx, items, x, y, w, out):
        if len(items) == 1:
            if items[0].get("children"):
                partition(idx, items[0]["children"], x, y, w, out)
            else:
                out[idx] = items[0]["code"]
            return
        first, second, frac = split_items(items)
        xs, ys = x[idx], y[idx]
        axis = xs if (xs.max() - xs.min()) >= (ys.max() - ys.min()) else ys
        order = np.argsort(axis, kind="stable")
        cw = np.cumsum(w[idx][order])
        cut = int(np.searchsorted(cw, frac * cw[-1]))
        cut = min(max(cut, 1), len(idx) - 1)
        partition(idx[order[:cut]], first, x, y, w, out)
        partition(idx[order[cut:]], second, x, y, w, out)

    def main():
        books = json.loads((ROOT / "kitchen" / "books.json").read_text())
        n = len([b for b in books if b["status"] in ("accepted", "geography-done")])
        centres = fibonacci_sphere(n)
        seated = seat_books(books, centres)
        (ROOT / "kitchen" / "books.json").write_text(json.dumps(books, indent=2, ensure_ascii=False))
        P, wts = pixel_grid()
        cont = np.argmax(P @ centres.T, axis=1)          # seat_index per pixel
        raster = np.zeros(P.shape[0], dtype=np.int32)
        territories, code = [], 1
        for b in seated:
            cid = f"C{b['seat_order']:02d}"
            toc = json.loads((LOGS / f"{b['book_id']}-toc.json").read_text())
            items = []
            for pi, prov in enumerate(toc["provinces"]):
                pid = f"{cid}.P{pi + 1:02d}" if prov["name"] != "ALL" else f"{cid}.P00"
                kids = []
                for di, ch in enumerate(prov["chapters"]):
                    num = ch["number"] if ch.get("number") not in (None, "") else str(di + 1)
                    did = f"{pid}.D{int(''.join(ch for ch in str(num) if ch.isdigit()) or di + 1):03d}"
                    kids.append({"id": did, "name": ch["title"], "pages": max(1, ch["page_end"] - ch["page_start"] + 1),
                                 "page_start": ch["page_start"], "page_end": ch["page_end"], "code": code,
                                 "parent": pid, "level": "district"})
                    code += 1
                items.append({"id": pid, "name": prov["name"], "part_name": prov.get("part_name", prov["name"]),
                              "pages": sum(k["pages"] for k in kids), "children": kids, "parent": cid,
                              "level": "province", "page_start": min(k["page_start"] for k in kids),
                              "page_end": max(k["page_end"] for k in kids)})
            idx = np.nonzero(cont == b["seat_index"])[0]
            x, y = local_xy(P[idx], centres[b["seat_index"]])
            xx = np.zeros(P.shape[0]); yy = np.zeros(P.shape[0]); xx[idx] = x; yy[idx] = y
            partition(idx, items, xx, yy, wts, raster)
            lat, lon = vec_to_latlon(centres[b["seat_index"]])
            territories.append({"territory_id": cid, "level": "continent", "name": b["field_name"], "book_id": b["book_id"],
                                "parent": None, "lat": lat, "lon": lon, "seat_order": b["seat_order"],
                                "page_start": min(i["page_start"] for i in items), "page_end": max(i["page_end"] for i in items),
                                "area_fraction": float(wts[idx].sum() / wts.sum()), "raster_code": None})
            for prov in items:
                territories.append({k: prov[k] for k in ("level", "name", "part_name", "parent", "page_start", "page_end")}
                                   | {"territory_id": prov["id"], "book_id": b["book_id"], "raster_code": None, "seat_order": None})
                for d in prov["children"]:
                    territories.append({k: d[k] for k in ("level", "name", "parent", "page_start", "page_end")}
                                       | {"territory_id": d["id"], "book_id": b["book_id"], "raster_code": d["code"], "seat_order": None})
        # centres, areas, bboxes for districts and provinces
        total_w = wts.sum()
        by_code = {t["raster_code"]: t for t in territories if t["raster_code"]}
        rows = np.arange(P.shape[0]) // W; cols = np.arange(P.shape[0]) % W
        for c_, t in by_code.items():
            idx = np.nonzero(raster == c_)[0]
            v = (P[idx] * wts[idx, None]).sum(0)
            lat, lon = vec_to_latlon(v)
            # snap to the nearest pixel that belongs to the district
            best = idx[np.argmax(P[idx] @ latlon_to_vec(lat, lon))]
            t["lat"], t["lon"] = vec_to_latlon(P[best])
            t["area_fraction"] = float(wts[idx].sum() / total_w)
            t["bbox_px"] = [int(cols[idx].min()), int(rows[idx].min()), int(cols[idx].max()), int(rows[idx].max())]
        for t in territories:
            if t["level"] == "province":
                kids = [k for k in territories if k["level"] == "district" and k["parent"] == t["territory_id"]]
                v = sum(latlon_to_vec(k["lat"], k["lon"]) * k["area_fraction"] for k in kids)
                t["lat"], t["lon"] = vec_to_latlon(v)
                t["area_fraction"] = float(sum(k["area_fraction"] for k in kids))
        # colours: one hue per continent, lightness varies by province
        hues = {t["territory_id"]: i / n for i, t in enumerate([t for t in territories if t["level"] == "continent"])}
        prov_index = {}
        for t in territories:
            if t["level"] == "province":
                prov_index.setdefault(t["parent"], []).append(t["territory_id"])
        for t in territories:
            if t["level"] == "continent":
                r, g, b_ = colorsys.hls_to_rgb(hues[t["territory_id"]], 0.55, 0.55)
            elif t["level"] == "province":
                k = prov_index[t["parent"]].index(t["territory_id"]); m = len(prov_index[t["parent"]])
                r, g, b_ = colorsys.hls_to_rgb(hues[t["parent"]], 0.45 + 0.25 * (k / max(1, m - 1)), 0.55)
            else:
                parent = next(p for p in territories if p["territory_id"] == t["parent"])
                k = prov_index[parent["parent"]].index(parent["territory_id"]); m = len(prov_index[parent["parent"]])
                r, g, b_ = colorsys.hls_to_rgb(hues[parent["parent"]], 0.45 + 0.25 * (k / max(1, m - 1)), 0.55)
            t["colour_hex"] = "#%02x%02x%02x" % (int(r * 255), int(g * 255), int(b_ * 255))
        # write outputs
        OUT.mkdir(parents=True, exist_ok=True)
        img = raster.reshape(H, W)
        np.save(OUT / "district_raster.npy", img)
        rgb = np.zeros((H, W, 3), dtype=np.uint8)
        rgb[..., 0] = (img // 256).astype(np.uint8); rgb[..., 1] = (img % 256).astype(np.uint8)
        Image.fromarray(rgb).save(OUT / "district_raster.png")
        tex = np.zeros((H, W, 3), dtype=np.uint8)
        palette = {t["raster_code"]: tuple(int(t["colour_hex"][i:i + 2], 16) for i in (1, 3, 5)) for t in territories if t["raster_code"]}
        lut = np.zeros((code + 1, 3), dtype=np.uint8)
        for c_, col in palette.items():
            lut[c_] = col
        tex = lut[img]
        edge = np.zeros((H, W), dtype=bool)
        edge[:, 1:] |= img[:, 1:] != img[:, :-1]; edge[1:, :] |= img[1:, :] != img[:-1, :]
        tex[edge] = (40, 40, 40)
        cont_px = cont.reshape(H, W)
        cedge = np.zeros((H, W), dtype=bool)
        cedge[:, 1:] |= cont_px[:, 1:] != cont_px[:, :-1]; cedge[1:, :] |= cont_px[1:, :] != cont_px[:-1, :]
        tex[cedge] = (0, 0, 0)
        im = Image.fromarray(tex).resize((W * 2, H * 2), Image.NEAREST)
        draw = ImageDraw.Draw(im)
        try:
            font = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", 28)
        except Exception:
            font = ImageFont.load_default()
        for t in territories:
            if t["level"] == "continent":
                px = (t["lon"] + 180) / 360 * W * 2; py = (90 - t["lat"]) / 180 * H * 2
                draw.text((px, py), t["name"], fill=(255, 255, 255), font=font, anchor="mm", stroke_width=2, stroke_fill=(0, 0, 0))
        im.save(OUT / "continents_texture.png")
        (OUT / "geography.json").write_text(json.dumps(territories, indent=1, ensure_ascii=False))
        (OUT / "districts_lookup.json").write_text(json.dumps(
            {str(t["raster_code"]): t["territory_id"] for t in territories if t["raster_code"]}))
        (LOGS / "seating-preview.png").write_bytes((OUT / "continents_texture.png").read_bytes())
        print("territories:", len(territories), "districts:", len(by_code), "raster codes up to", code - 1)

    if __name__ == "__main__":
        main()

6.6 Before running: kitchen/logs/<BOOK_ID>-toc.json must contain
    page_end for every chapter (toc_validate.py adds it, 4.4). Run:
      python kitchen/geography.py
    Expected: it prints the counts; data/export/geography/ has five
    files; kitchen/logs/seating-preview.png exists. Look at the preview
    (the human opens it). Then copy the folder for the site:
      mkdir -p site/data/geography && cp data/export/geography/*.png data/export/geography/*.json site/data/geography/
    Check sizes: district_raster.npy is about 8 MB (commit it: fine);
    continents_texture.png at 4096 x 2048 is a few MB. Nothing over 40 MB.
  CHECKPOINT 3.4: the human approves the texture (continents readable,
  districts visible). Possible requests: different hues (edit the
  lightness numbers), font size. Re-run until approved.
  EVIDENCE: the printed counts; `ls -la data/export/geography/`;
  a Cypher count after section 8.

7. STEP A6 -- INDEXES -> ENTITY REGISTRY  [SMART writes 7.4-7.7 scripts;
   CHEAP runs; the READER does all per-term work]
--------------------------------------------------------------------------------
7.1 Order of books: HARRISON-22 first (the hub seeds the registry with
    its names), then all other accepted books in alphabetical order of
    book_id. The FIRST book that creates an entity fixes its
    canonical_name; later books add aliases and lit spots only.
7.2 Extract index text, page by page (printed index pages carry their
    own numbers like I-1; we work by image number):
      for N in index_images range:
        pdftotext -f N -l N "<pdf>" kitchen/logs/<BOOK_ID>-index-<N>.txt
    Default: no -layout flag (reading order follows the columns). If
    the human's sample review (7.10) shows that sub-entries are being
    promoted to main entries, re-extract with -layout and column crops:
      pdftotext -layout -f N -l N -x 0 -y 0 -W <half page width in
      points> -H <page height> ... for the left column, then -x <half>
      for the right column (page size from pdfinfo), and concatenate.
    This is tuned once per book, not per page.
7.3 Reader prompt P-A4a (one index page -> entries). System message:

    You parse one page of a medical textbook's back-of-book INDEX into
    JSON. Output ONLY JSON. Schema:
    {"entries":[{"headword":"<main term exactly as printed, including
    inverted comma form>","display":"<the same term in natural word
    order, e.g. 'Anemia, hemolytic' -> 'hemolytic anemia'; if not
    inverted, same as headword>","see":"<target term if the line is a
    'See X' cross-reference, else null>","pages":["<every page
    reference of the headword itself>"],"subentries":[{"text":"<the
    sub-entry words>","pages":["..."]}]}]}
    Rules: a MAIN entry starts at the left margin and usually begins
    with a capital letter; SUB-entries are indented or begin with a
    lowercase word or with 'in', 'with', 'for', 'and', 'of', 'due to'.
    Keep page references exactly as printed (e.g. "1234", "1234-1236",
    "1234t", "1234f", "e12"). Do not invent entries. If the page begins
    in the middle of a main entry, output that first partial entry with
    headword "CONTINUED".

    User message: the page text. Result saved as
    kitchen/logs/<BOOK_ID>-index-<N>.json. Post-processing (script):
    merge a "CONTINUED" first entry into the last entry of the previous
    page; convert page refs: strip trailing letters (t, f, b), drop refs
    starting with a letter (online-only), expand "a-b" ranges into the
    printed pages a..b (cap a range at 30 pages; if longer, keep a and b
    only). Then each ref becomes (printed_page -> district_id) through
    the book's territory page ranges (a page outside every district,
    e.g. an appendix, is dropped and counted).
7.4 Reader prompt P-A4b (classify a batch of main entries). The script
    sends 25 entries per call, each with: display form; up to 6
    sub-entry texts; the names of up to 5 districts where its pages
    fall (this is the CONTEXT that makes the classification sane).
    System message:

    You classify medical index terms into exactly one group. Output
    ONLY JSON: {"results":[{"display":"<as given>","group":"<one of
    symptoms-and-signs | diseases-and-conditions | treatments-and-drugs
    | not-an-entity>","confidence":<0.0-1.0>,"reason":"<max 12
    words>"}]}
    Definitions:
    symptoms-and-signs: what a patient feels or notices (pain, nausea,
    tiredness) OR what an examiner or test can observe or measure
    (rash, fever, murmur, high reading). Specific or nonspecific, but
    NOT chronic. Includes abnormal findings described as a state of the
    patient (jaundice, edema, cough, hemoptysis).
    diseases-and-conditions: any named disease, syndrome, infection
    named as a disease (e.g. "Staphylococcal infections",
    "Tuberculosis"), injury, poisoning, deficiency, chronic state
    (chronic pain, hypertension, obesity, pregnancy, menopause), and any
    abnormality defined by a measurement (hyperkalemia, anemia).
    treatments-and-drugs: any drug (generic or brand), vaccine,
    substance given to treat or prevent, procedure meant to treat or
    prevent (surgery, dialysis, transplantation, radiation therapy,
    physiotherapy), diet or lifestyle intervention when named as a
    treatment.
    not-an-entity: people's names; anatomy and physiology (liver,
    nephron, cardiac output); organisms named as organisms
    (Staphylococcus aureus, as opposed to an infection); genes,
    proteins, receptors, lab methods; diagnostic tests and imaging as
    methods (electrocardiography, MRI); statistics, ethics, history,
    health policy, economics; abbreviations with no meaning alone.
    Tie-break rules, apply in order: (1) between symptom and disease
    with no clue, choose symptoms-and-signs; (2) a term that is both a
    drug and a poison (alcohol, lead) is treatments-and-drugs only if
    the context districts are pharmacology or therapy, else
    diseases-and-conditions (the poisoning); (3) an organism term whose
    sub-entries are about infection, treatment or diagnosis is
    diseases-and-conditions; (4) between an entity and not-an-entity
    with no clue, choose the entity group you lean to and set
    confidence below 0.5.

    User message: the 25 entries as a JSON list. The script writes the
    results into kitchen/logs/<BOOK_ID>-classified.jsonl (one line per
    term) and never re-asks a term already classified for this book.
7.5 Cross-references: an entry with "see": X is not an entity; its
    headword is added to X's aliases when X exists (after the whole
    book is parsed), else written to the book's unresolved-see list and
    retried after the next book. "See also" is ignored.
7.6 Entity resolution across books (the "fuzzy logic" the human asked
    for, done by AI with context, never by a script alone). For each
    classified term with group != not-an-entity, in order:
    (a) EXACT: slugify(display) equals an existing slug's name part, or
        display (lowercased) equals an existing alias (lowercased), in
        the same group -> MERGE automatically: add display to aliases
        if new; add lit spots. No reader call. Log "exact".
    (b) Otherwise CANDIDATES: run the Neo4j full-text query
          CALL db.index.fulltext.queryNodes("entity_fulltext", $q)
          YIELD node, score RETURN node.slug, node.canonical_name,
          node.aliases, node.group, score LIMIT 8
        with $q = the display words joined by " OR " (strip punctuation,
        append "~" to each word of 5+ letters for fuzziness), and add
        rapidfuzz.process.extract(display, all_names_in_group,
        scorer=token_set_ratio, limit=5). Union, keep at most 8
        candidates with the same group. If there are no candidates with
        token_set_ratio >= 60 and no full-text hits with score >= 1.0:
        CREATE a new entity. Log "new-no-candidates".
    (c) Otherwise ask the reader, prompt P-A4c. System message:

        You decide whether a medical index term from book B is the SAME
        entity as one of the candidate entities already registered
        from other books, or a NEW entity. Same entity means the same
        disease, symptom or treatment under a different spelling, word
        order, synonym, eponym or abbreviation (e.g. "myocardial
        infarction" = "heart attack" = "MI"; "paracetamol" =
        "acetaminophen"). Different entity means a distinct concept
        even if related (e.g. "hypertension" vs "pulmonary
        hypertension"; "hepatitis B" vs "hepatitis C"; a disease vs its
        complication). Output ONLY JSON: {"decision":"SAME"|"NEW",
        "candidate_slug":"<slug if SAME else null>","confidence":
        <0.0-1.0>,"reason":"<max 15 words>"}

        User message: {"term": display, "group": group, "subentries":
        [...up to 8], "context_districts": [...up to 5 district names
        with their book field], "candidates": [{"slug":..,
        "canonical_name":.., "aliases":[..up to 8], "lit_spot_books":
        [..]} ...]}
        SAME with confidence >= 0.6 -> merge (add alias, lit spots).
        SAME with confidence < 0.6 or NEW -> create new entity, and if
        SAME-but-low-confidence also write the pair to
        kitchen/logs/<BOOK_ID>-doubtful-merges.jsonl for the human's
        sample review. Log every decision with the full reason.
    Group conflict: if the best candidate has a different group than
    the new term's classification, do NOT merge; create new, and log
    "group-conflict". Part 7 of the human review looks at these.
7.7 Creating an entity (Cypher executed by the script through db.run):

      MERGE (e:Entity {slug: $slug})
      ON CREATE SET e.group = $group, e.canonical_name = $name,
        e.aliases = [$name], e.aliases_text = $name,
        e.generic_names = [], e.brand_names = [], e.formulas = [],
        e.created_from = "index", e.created_book_id = $book_id,
        e.frozen = false
      WITH e
      CALL apoc.create.addLabels(e, [$label]) YIELD node
      RETURN node.slug

    If APOC is not installed (SHOW PROCEDURES YIELD name WHERE name
    STARTS WITH "apoc" returns nothing), use instead three fixed
    statements, one per group, e.g. for symptoms:
      MERGE (e:Entity {slug:$slug}) ON CREATE SET ... SET e:Symptom
    (the label after SET is literal: Symptom, Disease, Treatment).
    Adding an alias:
      MATCH (e:Entity {slug:$slug}) WHERE NOT $alias IN e.aliases
      SET e.aliases = e.aliases + $alias,
          e.aliases_text = e.aliases_text + " | " + $alias
    Adding a lit spot (one per printed page reference):
      MATCH (e:Entity {slug:$slug}), (d:Territory {territory_id:$did})
      MERGE (e)-[r:DISCUSSED_IN {book_id:$book_id, page_number:$page,
                                 source:"index"}]->(d)
      ON CREATE SET r.quote = $quote, r.image_file = $image_file,
        r.reader_model = $model, r.read_date = date()
    quote = the verbatim index line (headword + sub-entry text if the
    page came from a sub-entry + the page reference); image_file = the
    index page image where the line was read.
7.8 Throughput and resumability. Everything is per page / per batch and
    idempotent: the scripts skip pages whose .json exists and terms
    already in classified.jsonl, so the human can stop the laptop any
    time and re-run. Expected free-model time for Harrison: about 170
    index pages (parse) + about 1,000 classify batches + about 0
    resolution calls (first book) -> one to two days of unattended
    laptop time. Later books: fewer entries, plus resolution calls.
    The manager does NOT wait in chat while this runs: it starts the
    script with nohup, writes "running since <time>" in PROGRESS.md, and
    the human restarts the manager when the log says done.
      nohup python kitchen/index_pipeline.py HARRISON-22 > kitchen/logs/HARRISON-22-run.log 2>&1 &
7.9 Fallback for a book with no usable index: the registry for that
    book is derived from its chapter titles (each title is sent to
    P-A4b as a term with the chapter itself as context; most become
    diseases) and from the first printed page of each chapter (pdftotext
    of that page; prompt P-A4b applied to the capitalised noun phrases
    the reader extracts with a one-line pre-prompt: "List the medical
    terms in this page as a JSON list of strings, verbatim."). This
    yields a thin registry for that book; Phase B quarantine will show
    what it missed.
7.10 Script list for this section (SMART writes; all under kitchen/):
     index_extract.py  <BOOK_ID>   -> runs pdftotext for index pages
     index_parse.py    <BOOK_ID>   -> P-A4a per page, post-processing,
                                      writes <BOOK_ID>-index-entries.json
     index_classify.py <BOOK_ID>   -> P-A4b in batches of 25
     index_resolve.py  <BOOK_ID>   -> 7.5-7.7, writes to Neo4j
     index_pipeline.py <BOOK_ID>   -> runs the four in order, resumable
     Each script prints a one-line summary and appends it to
     kitchen/logs/<BOOK_ID>-run.log. Each is under 200 lines. SMART
     writes them to follow this part literally and tests each on ONE
     index page / ONE batch before CHEAP launches the full run.

8. STEP A7 -- LOADING GEOGRAPHY INTO NEO4J (CHEAP; Cypher given)
--------------------------------------------------------------------------------
8.1 kitchen/load_geography.py (short script): reads kitchen/books.json
    and data/export/geography/geography.json and runs:

      UNWIND $books AS b
      MERGE (k:Book {book_id: b.book_id})
      SET k.title = b.title, k.edition = b.edition, k.year = b.year,
          k.field_name = b.field_name, k.page_count = b.page_count_images,
          k.page_offset = b.page_offset, k.image_name_pattern = b.image_name_pattern,
          k.index_image_start = b.index_images[0], k.index_image_end = b.index_images[1],
          k.continent_id = "C" + right("0" + toString(b.seat_order), 2),
          k.status = "geography-done"

      UNWIND $territories AS t
      MERGE (x:Territory {territory_id: t.territory_id})
      SET x.level = t.level, x.name = t.name, x.part_name = t.part_name,
          x.book_id = t.book_id, x.page_start = t.page_start, x.page_end = t.page_end,
          x.page_count = t.page_end - t.page_start + 1,
          x.lat = t.lat, x.lon = t.lon, x.area_fraction = t.area_fraction,
          x.seat_order = t.seat_order, x.raster_code = t.raster_code,
          x.colour_hex = t.colour_hex, x.bbox_px = t.bbox_px, x.border_geojson = null

      UNWIND $territories AS t
      WITH t WHERE t.parent IS NOT NULL
      MATCH (c:Territory {territory_id: t.territory_id}), (p:Territory {territory_id: t.parent})
      MERGE (c)-[:CHILD_OF]->(p)

      MATCH (c:Territory {level:"continent"}), (b:Book {book_id: c.book_id})
      MERGE (c)-[:REPRESENTS]->(b)

    (Only books with status accepted/geography-done are loaded;
    rejected duplicates get a Book node with status
    "rejected-duplicate" and no territories, so the record of the
    decision stays in the database.)
8.2 Verification queries (paste outputs into PROGRESS.md):
      MATCH (b:Book) RETURN b.status, count(*) ORDER BY b.status;
      MATCH (t:Territory) RETURN t.level, count(*) ORDER BY t.level;
      MATCH (d:Territory {level:"district"}) WHERE NOT (d)-[:CHILD_OF]->() RETURN count(d);   -- must be 0
      MATCH (t:Territory {level:"district"}) RETURN sum(t.area_fraction);   -- about 1.0
      MATCH (t:Territory {level:"continent"}) RETURN t.territory_id, t.name, t.seat_order ORDER BY t.seat_order;

9. REVIEW SAMPLES FOR THE HUMAN (after each book's index run)
--------------------------------------------------------------------------------
  The script kitchen/review_sample.py <BOOK_ID> writes
  kitchen/logs/<BOOK_ID>-review.md containing:
  (a) counts: entries parsed, pages referenced, references dropped
      (outside any district), terms per group, not-an-entity count,
      exact merges, reader merges, new entities, group conflicts,
      doubtful merges;
  (b) 20 random terms per group with their aliases and the names of
      their top 3 districts by lit-spot count;
  (c) 20 random not-an-entity terms (to catch symptoms wrongly
      excluded);
  (d) all group-conflict pairs and up to 30 doubtful merges.
  The human reads it (five minutes) and answers in one of three ways:
  "ok"; "redo classification with this extra rule: <text>" (the rule is
  appended to P-A4b's system message under "Additional rules from the
  human", and ONLY the affected book is re-classified; previously
  processed books are re-run only if the human says so); or
  "fix these: <list of slug -> group or merge/split>" (applied by
  Cypher, logged under DECISIONS BY HUMAN).
  CHECKPOINT 3.5: Harrison's review approved before any other book's
  index run starts (its names seed everything).
  CHECKPOINT 3.6: all N books reviewed and approved.

10. CHECKPOINT SUMMARY
--------------------------------------------------------------------------------
  3.1 duplicates decided, field names set            (section 3)
  3.2 TOC summaries approved per book                (section 4)
  3.3 seating approved                               (section 6.3)
  3.4 texture approved                               (section 6.6)
  3.5 Harrison registry review approved              (section 9)
  3.6 all books' registry reviews approved           (section 9)
  Each is recorded in PROGRESS.md under DECISIONS BY HUMAN with the
  date and the human's words.

11. STEP A8 -- FREEZE A
--------------------------------------------------------------------------------
11.1 Preconditions: all six checkpoints recorded; the verification
     queries of 8.2 pass; no QUESTIONS FOR HUMAN open.
11.2 Final slug collision check:
       MATCH (e:Entity) WITH e.slug AS s, count(*) AS c WHERE c > 1 RETURN s, c;
     must return nothing (the constraint guarantees it, but check).
     Entities with slugs ending in "-2" are listed for the human; the
     human renames or merges; then proceed.
11.3 Export the registries to data/registry/ (script
     kitchen/export_registry.py; CSV, UTF-8, header row):
       books.csv        book_id, title, edition, year, field_name,
                        continent_id, page_count, page_offset, status
       territories.csv  territory_id, level, name, part_name, book_id,
                        parent, page_start, page_end, lat, lon,
                        area_fraction, seat_order, raster_code, colour_hex
       entities.csv     slug, group, canonical_name, created_book_id,
                        lit_spot_count, book_count, altitude (empty
                        until Part 5), rank (empty)
       aliases.csv      slug, alias
       stats.json       the counts of 9(a) summed over all books, plus
                        the date
     These files ARE Appendices A, B and C (the appendix .md files
     delivered later are short descriptions pointing to these CSVs).
11.4 Freeze:
       MATCH (e:Entity) SET e.frozen = true;
       MATCH (m:Meta {key:"skeleton_frozen"}) SET m.value = "true";
       MATCH (m:Meta {key:"freeze_date"}) SET m.value = toString(date());
       MATCH (b:Book) WHERE b.status = "geography-done" SET b.status = "index-done";
     Commit everything and tag:
       git add -A && git commit -m "Freeze A: geography + entity registry"
       git tag -a skeleton-freeze-A -m "Skeleton frozen (geography + entities)"
       git push && git push --tags
11.5 After Freeze A, the following NEVER change: territory IDs, names,
     page ranges, lat/lon, the raster; entity slugs, groups, canonical
     names. Aliases MAY still grow (Phase B adds spellings). Lit spots
     and edges grow forever. Altitudes are assigned in Part 5 and
     frozen there (Freeze B).
11.6 Set PROGRESS.md: CURRENT PHASE = "Skeleton frozen (A). Waiting for
     BIBLE part 4 and part 5."; NEXT STEP = "Part 5 altitude assignment
     can run now (needs only the registry); Part 4 page reading starts
     when the human says so."

12. DEFAULTS IN THIS PART THAT THE HUMAN MAY OVERTURN
--------------------------------------------------------------------------------
  (1) Equal-area continents (Amendment 3.1).
  (2) Raster instead of polygons (Amendment 3.2).
  (3) The 16 cluster words and the greedy seating (6.3).
  (4) Harrison first, then alphabetical; first book fixes canonical
      names (7.1).
  (5) Merge threshold: SAME needs confidence >= 0.6 (7.6 c).
  (6) Range cap of 30 pages when expanding "a-b" index references (7.3).
  (7) Index sub-entries are lit spots of the main term, never entities
      of their own (7.3). A sub-entry that is clearly its own disease
      ("Hepatitis, B" under "Hepatitis") will appear as its own main
      entry elsewhere in a good index; if not, Phase B quarantine
      catches it.

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
LaTeX. Delivered: Part 1 (charter, 15 laws, world model), Part 2
(environment, repo layout kitchen/ data/ site/ BIBLE/, AGENTS.md +
PROGRESS.md, Neo4j schema: Book, Territory, Entity(+Symptom/Disease/
Treatment labels), QuarantineTerm, Meta; DISCUSSED_IN lit spots; edges
PRESENTS_WITH, TREATED_BY, HARMS(subtype CONTRAINDICATED_IN), LEADS_TO,
MISTAKEN_FOR with provenance + frequency_phrase + f_scale 0-5 +
numeric_pct + severity; one relationship per proving sentence;
kitchen/db.py; .env with NEO4J_* and READER_BASE_URL (/v1) +
READER_MODEL + READER_NO_THINK_TAG; export = geography.json, books.json,
search.json, entities/<slug>.json, quarantine.json, ledger.json), Part 3
(Phase A: books.json per-book config; pdftotext for TOC and index text;
one-book-per-field decided by human; TOC -> provinces/districts via
reader prompt P-A2 + validation; page_offset detection; kitchen/
reader.py helper ask(system,user,images); geography.py: N-point
Fibonacci sphere, nearest-centre Voronoi continents of EQUAL area
(Amendment 3.1), greedy cluster seating with human approval, recursive
binary treemap split inside each continent making province/district
areas exactly proportional to page count, output a 2048x1024
equirectangular district raster (Amendment 3.2: rasters instead of
polygons; Territory gets raster_code, colour_hex, bbox_px,
border_geojson=null) + continents_texture.png + districts_lookup.json +
geography.json; index pipeline: P-A4a parse index pages, P-A4b classify
25 terms per call with district-name context into 3 groups or
not-an-entity with tie-break rules, P-A4c entity resolution SAME/NEW by
reader with fulltext + rapidfuzz candidates, exact matches merged by
script, SAME needs confidence >= 0.6, group conflicts never merged;
Harrison first then alphabetical, first book fixes canonical_name; lit
spots from index page refs with quote = verbatim index line; review
samples per book; six checkpoints; Freeze A = geography + entity list +
slugs frozen, tag skeleton-freeze-A, registries exported to
data/registry/*.csv which serve as Appendices A, B, C; altitudes left
for Part 5 = Freeze B). World model: WHERE = library geography; WHICH =
altitude, one shell per entity: diseases r 0.30-1.00 by breadth (deep =
multisystem), symptoms 1.00-1.50 by specificity (low = nonspecific),
treatments 1.50-3.00 by heaviness (lifestyle -> OTC -> prescription ->
biologics/chemo/radiation -> surgery) with drug classes adjacent, every
drug its own shell. No single home (Law 8). Rigid layout. Viewer: 3-D
globe (texture on sphere) <-> 2-D equirectangular map, lit filled
circles at district centres sized by F, blue forward / yellow harm /
grey differential, severity red ring, F0 dashed, desktop + mobile, no
build step, vendored JS. Tiers: READER = free local Qwen 3.8 27B Q4_K_M
(Gemma 4 31B substitute) does all per-page/per-term work; CHEAP =
DeepSeek V4.1 Flash runs scripts; SMART = Claude Sonnet 5.5 or GPT 6.1
Sol writes scripts; manager says "HUMAN: please switch to <tier>" and
stops. Laws include: books only, provenance always, Neo4j single source
of truth, cheap beats perfect, never assume installed, when unclear stop
and ask, one disclaimer only (index.html bottom), no multi-model
editions, books/images/transcripts never committed.
Next delivery requested: Part 4 (Phase B -- the Reading Pipeline: page
images -> reader transcription + extraction with a sliding window across
page boundaries, the extraction prompt producing edges with verbatim
quotes and frequency phrases, the full F-scale wording table, entity
resolution of page terms against the frozen registry with context,
quarantine, generic/brand/formula capture for drugs, resumable batch
runner, per-book progress ledger).
================================================================================
