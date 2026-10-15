# HANDOFF -- Meaningful territory names (Nir's decision, 15 Oct 2026)

READ THIS FIRST after restart, before touching any book.

## The decision (Nir's words, 15 Oct 2026)

1. **Meaning over numbers, at EVERY level.** If a heading prints
   "chapter 1 bla bla bla", keep "bla bla bla". If it prints
   "SECTION V CARDIAC RADIOLOGY", keep "Cardiac Radiology" and DROP the
   "SECTION V" part. Same rule for Parts, Units, Sections, Volumes,
   chapters, and any other heading level. The NUMBER is not the name.
2. **When a book prints only "PART 3" with no title:** first LOOK on
   that part's opening page inside the PDF (the page where the part
   starts). Nir suspects usually nothing useful will be there, but try
   anyway. If no title found: **WRITE a short descriptive name yourself**
   from the chapters inside that part — a few words that hold the
   meaning of all its chapters, as if the author had named it.
   Descriptive and short.
3. **Honesty flag:** every name we wrote ourselves (not printed by the
   book) must be marked as such in the JSON, e.g.
   `"name_source": "toc"` for verbatim-from-TOC names vs
   `"name_source": "written"` for names we composed. Never pretend a
   book printed something it did not.

## Why this is safe right now

- Nothing is loaded into Neo4j yet. Nothing is frozen (no Freeze A).
- Changing province names now costs nothing. After the Freeze it would
  be forbidden.

## What is wrong today (the 22 clean books)

Checked 15 Oct 2026 against kitchen/logs/*-vis-toc.json:

BAD -- province is only a number, no meaning:
  GUYTON-2026      "UNIT I" .. "UNIT XV"          (15 provinces, no meaning)
  BRANT-5          "SECTION I" .. "SECTION XII"
  DELISA-6         "PART I" .. "PART IX"
  DEVITA-12        "PART I" .. "PART IV"
  WILLIAMS-OBSTETRICS-26  "SECTION 1" .. "SECTION 12"
  BRAUNWALD-12     "PART I","PART II","PART III","PART IX","PART X",
                   "PART XI" have no title (others are fine)

BAD -- middle level is a physical volume, not a meaning:
  CAMPBELL-2020    "VOLUME I" .. "VOLUME IV"
  FIRESTEIN-12     "VOLUME I", "VOLUME II"
  ROCKWOOD-10      "Volume 1", "Volume 2"

BAD -- no middle level at all:
  BOLOGNIA-2024, BRENNER-11, ROBBINS-10, THOMPSON-2023  ("ALL")

MESSY -- meaning present but dirty:
  ADAMS-12         trailing page number glued on:
                   "PART 4: MAJOR CATEGORIES OF NEUROLOGIC DISEASE, 615"
                   -> keep "Major Categories of Neurologic Disease",
                      put 615 in toc_number, not in the name
  SABISTON-22      same trailing-page-number problem
  GOODMAN-14       title cut off mid-sentence:
                   "Modulation of Pulmonary, Renal, and Cardiovascular"
                   -> re-read the TOC page and get the full title
  GRAY-2020        duplicated levels ("SECTION 4: HEAD AND NECK" AND
                   "Head and neck" as sibling provinces) -- re-check
                   the real structure

GOOD already (meaning is there; just strip the "PART n" prefix if Nir
wants only the meaning -- see open question below):
  HARRISON-22, SLEISENGER-11, KRAUSE-16, BENZON-2023, AVERY-2021,
  GRAY-2020 (mostly), ADAMS-12 / SABISTON-22 (after de-gluing)

The raw TOC text already contains the missing titles for at least:
  GUYTON-2026  kitchen/logs/GUYTON-2026-toc.txt
               e.g. "UNIT VI Blood Cells, Immunity, and Blood"
  BRANT-5      kitchen/logs/BRANT-5-vis-toc.txt
               e.g. "SECTION V CARDIAC RADIOLOGY"
So for many books this is a RE-PARSE of text we already have -- zero
model calls (toc_reparse.py rebuilds from the saved transcript).

## How to fix (after restart, one step at a time)

1. For each BAD/MESSY book: fix the province names.
   - If the title exists in the saved TOC text: re-parse
     (toc_reparse.py rebuilds JSON from the transcript, zero model
     calls), or fix the prompt that lost it so future reads keep it.
   - If the title exists only on the part's opening page: open that
     page (pdftotext or the page image) and take it.
   - If nowhere: WRITE the short descriptive name from the chapters,
     set "name_source": "written".
2. Strip number prefixes from names everywhere ("PART 2 Cardinal
   Manifestations..." -> name = "Cardinal Manifestations..."; the
   number itself, if useful, belongs in a toc_number field, not in the
   name).
3. Apply the SAME rule going forward for the 15 unread books -- the
   toc_vision / toc_headings prompts must ask for MEANING only, not
   the numbering. Check those prompts before the next book.
4. Prove each fix with the JSON before/after (Law 11).
5. One book at a time. No batches. Ask Nir if unsure.

## Where the names live

- kitchen/logs/<BOOK_ID>-vis-toc.json  (provinces[].name, part_name)
- kitchen/logs/<BOOK_ID>-toc.json      (the validated copy)
- later: geography.json / territories.csv / Neo4j Territory.name
- The BIBLE itself is NEVER edited (standing rule). This decision is
  an AMENDMENT recorded in PROGRESS.md under DECISIONS BY HUMAN.

## Open question for Nir (ask BEFORE renaming the GOOD books)

The GOOD books currently store "PART 2 Cardinal Manifestations and
Presentation of Diseases". Should the name become only
"Cardinal Manifestations and Presentation of Diseases" (meaning only),
or is the current form acceptable when the book itself printed the
title? Nir said "meaning, not the number" -- likely meaning-only, but
CONFIRM before mass-renaming.
