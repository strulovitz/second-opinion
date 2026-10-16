# HANDOFF -- Territory names: NUMBER + MEANING together (Nir's FINAL rule, 15 Oct 2026, evening)

READ THIS FIRST after restart, before touching any book.
This SUPERSEDES the earlier "meaning only, drop the numbering" rule
from the same morning. Nir changed his mind after thinking about it.

## STATUS after 15 Oct (late evening) -- READ THIS SECTION FIRST

**Nir added a second order the same evening: a book with NO parts at all
must not be left as one big group.** His words: *"in books that have NO
parts at all, please try to create such 'parts' for them, like, please
group the chapters ... and give them a proper title that will contain all
of them ... please do the work that the author should have done ... try to
imitate the style of other books (where the author DID do a proper job) ...
it's a lot better than 1 big group."*

So a flat book is grouped into written parts, each carrying
`name_source: "written"`.

**DONE on 15 Oct -- six books, all validator-clean, chapter totals
unchanged:**

| Book | before | after | where the names came from |
|---|---|---|---|
| FIRESTEIN-12 | 2 ("Volume 1/2") | 18 parts | the book's own Part banners |
| BOLOGNIA-2024 | 1 ("Volume 1", 161 ch) | 22 sections | the book's own SECTION banners |
| ROCKWOOD-10 | 2 | 4 sections | the book's own banners (word-numbers kept: "Section TWO") |
| ROBBINS-10 | 1 ("ALL") | 6 parts | **WRITTEN by us** |
| THOMPSON-2023 | 1 ("ALL") | 4 parts | **WRITTEN by us** |
| BRENNER-11 | 1 ("ALL") | 18 parts | **WRITTEN by us** |

The written groupings are human decisions stored in
`kitchen/parts/<BOOK>.json` and applied by `kitchen/toc_group_flat.py`.
Full ledger with evidence: `PROGRESS.md`, entry "DONE 2026-10-15 (late
evening)".

**FIVE pipeline bugs were found and fixed in the process** -- read the
ledger entry before touching the pipeline again. The dangerous one:
`toc_reparse.py` EMPTIED BRENNER-11 (its transcript is in a different
format), and only the backup held the 71 chapters. **Always copy a
book's `vis-toc.json` aside before any rebuild.**

**GRAY-2020 IS DONE (16 Oct 2026).** The 8 loose sub-headings were folded
into their printed Sections (Section 4 = ch 33-45, Section 7 = 52-58,
Section 8 = 59-75); the book now has 9 Sections and 79 chapters, validator
22/23 and 2,239 chapters unchanged. NO side file was kept for the folded
headings -- Nir's UNIFORMITY order of 16 Oct: every book is treated the
SAME way, no book gets an extra file the others do not have.

**ONE BOOK STILL TO DO:**

2. **GOODMAN-14** -- 10 provinces, mixed: "Section IV Inflammation,
   Immunomodulation, and Hematopoiesis" has a number, but "General
   Principles" and "Neuropharmacology" do not. Recover the missing
   numbers from the printed contents and finish the truncated title.

Then change the TOC prompts so the remaining 15 books keep BOTH the
numbering and the title when they are read.

## The rule (Nir's words, 15 Oct 2026 evening)

1. **Every territory name = entity type + number + meaning, TOGETHER.**
   - "SECTION V CARDIAC RADIOLOGY" -> name = "Section V - Cardiac Radiology"
   - "UNIT VI Blood Cells, Immunity, and Blood" -> name =
     "Unit VI - Blood Cells, Immunity, and Blood"
   - "PART 4: MAJOR CATEGORIES OF NEUROLOGIC DISEASE, 615" -> name =
     "Part 4 - Major Categories of Neurologic Disease" (the trailing
     615 is a TOC page number; it goes in toc_number, not in the name).
   Never strip the number. Never keep only the meaning. Nir's worry:
   in the future, when we put something into or take something out of
   "the book numbered X", we must be able to FIND it fast -- and a
   bare meaning with no number makes that hard.

2. **When a book prints only "PART 3" with no title:** first LOOK on
   that part's opening page inside the PDF (the page where the part
   starts). If a title is printed there, use it: "Part 3 - <title>".
   If nothing useful is printed: **WRITE a short descriptive name
   yourself** from the chapters inside that part -- a few words that
   hold the meaning of all its chapters, as if the author had named
   it. Then the name becomes "Part 3 - <the name you wrote>".
   Descriptive and short.

3. **Honesty flag:** every name we wrote ourselves (not printed by the
   book) must be marked as such in the JSON, e.g.
   `"name_source": "toc"` for names taken from the printed TOC or the
   part's opening page, vs `"name_source": "written"` for names we
   composed. Never pretend a book printed something it did not.

4. **Do NOT change the database structure.** The BIBLE's schema stays
   as it is -- ONE name field, not two. The combined
   "Type N - Meaning" string goes into that one field. The elegant
   design would have been two separate fields (one for the graphical
   map, one for the book's own name), but changing the schema now
   would only confuse future sessions. (Nir said this himself.)

## Why this is safe right now

- Nothing is loaded into Neo4j yet. Nothing is frozen (no Freeze A).
- Changing province names now costs nothing. After the Freeze it would
  be forbidden.

## What is wrong today (the 22 clean books)

Checked 15 Oct 2026 against kitchen/logs/*-vis-toc.json:

BAD -- province is only a number, no meaning (needs meaning ADDED,
keeping the number):
  GUYTON-2026      "UNIT I" .. "UNIT XV"          (15 provinces)
  BRANT-5          "SECTION I" .. "SECTION XII"
  DELISA-6         "PART I" .. "PART IX"
  DEVITA-12        "PART I" .. "PART IV"
  WILLIAMS-OBSTETRICS-26  "SECTION 1" .. "SECTION 12"
  BRAUNWALD-12     "PART I","PART II","PART III","PART IX","PART X",
                   "PART XI" have no title (others are fine)

BAD -- middle level is a physical volume, not a meaning (add a meaning
after the volume label, or split into real parts if the TOC shows
them):
  CAMPBELL-2020    "VOLUME I" .. "VOLUME IV"
  FIRESTEIN-12     "VOLUME I", "VOLUME II"
  ROCKWOOD-10      "Volume 1", "Volume 2"

BAD -- no middle level at all (create one from the chapters; each new
middle level should be "Part/Section <n> - <meaning>" if a number
exists, or just a short descriptive name if there is none):
  BOLOGNIA-2024, BRENNER-11, ROBBINS-10, THOMPSON-2023  ("ALL")

MESSY -- meaning present but dirty (de-glue, keep the number):
  ADAMS-12         trailing page number glued on:
                   "PART 4: MAJOR CATEGORIES OF NEUROLOGIC DISEASE, 615"
                   -> name = "Part 4 - Major Categories of Neurologic
                      Disease", 615 -> toc_number
  SABISTON-22      same trailing-page-number problem
  GOODMAN-14       title cut off mid-sentence:
                   "Modulation of Pulmonary, Renal, and Cardiovascular"
                   -> re-read the TOC page and get the full title
  GRAY-2020        duplicated levels ("SECTION 4: HEAD AND NECK" AND
                   "Head and neck" as sibling provinces) -- re-check
                   the real structure

GOOD already -- number + meaning together, exactly the target form:
  HARRISON-22, SLEISENGER-11, KRAUSE-16, BENZON-2023, AVERY-2021,
  GRAY-2020 (mostly), ADAMS-12 / SABISTON-22 (after de-gluing),
  and in general any book whose name already reads
  "PART n <Title>" or "SECTION n: <Title>".

The raw TOC text already contains the missing titles for at least:
  GUYTON-2026  kitchen/logs/GUYTON-2026-toc.txt
               e.g. "UNIT VI Blood Cells, Immunity, and Blood"
  BRANT-5      kitchen/logs/BRANT-5-vis-toc.txt
               e.g. "SECTION V CARDIAC RADIOLOGY"
So for many books this is a RE-PARSE of text we already have -- zero
model calls (toc_reparse.py rebuilds from the saved transcript).

## How to fix (after restart, one step at a time)

1. For each BAD/MESSY book: fix the province names to the form
   "Type N - Meaning".
   - If the title exists in the saved TOC text: re-parse
     (toc_reparse.py rebuilds JSON from the transcript, zero model
     calls), or fix the prompt that lost it so future reads keep it.
   - If the title exists only on the part's opening page: open that
     page (pdftotext or the page image) and take it.
   - If nowhere: WRITE the short descriptive name from the chapters,
     set "name_source": "written".
2. Normalize the connector: use " - " between the "Type N" part and
   the meaning ("Section V - Cardiac Radiology"). The exact character
   does not matter much, but pick ONE form and use it everywhere.
3. Apply the SAME rule going forward for the 15 unread books -- the
   toc_vision / toc_headings prompts must ask for BOTH the numbering
   AND the title on every heading line. Check those prompts before the
   next book. The reader must never drop a printed title, and never
   drop a printed number.
4. Prove each fix with the JSON before/after (Law 11).
5. One book at a time. No batches. Ask Nir if unsure.

## Where the names live

- kitchen/logs/<BOOK_ID>-vis-toc.json  (provinces[].name, part_name)
- kitchen/logs/<BOOK_ID>-toc.json      (the validated copy)
- later: geography.json / territories.csv / Neo4j Territory.name
- The BIBLE itself is NEVER edited (standing rule). This decision is
  an AMENDMENT recorded in PROGRESS.md under DECISIONS BY HUMAN.

## The earlier same-morning rule is WITHDRAWN

The version of this file written earlier on 15 Oct said "meaning only,
drop SECTION V / PART n". Nir retracted that. Do not follow it. If you
find any note or memory that still says "strip the numbering", it is
out of date -- this file is the truth.
