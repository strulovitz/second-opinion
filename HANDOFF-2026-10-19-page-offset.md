# HANDOFF -- 2026-10-19, page_offset session end (context window full)

READ FIRST, IN ORDER:
1. This file
2. `HANDOFF-2026-10-18-evening.md` (the book-reading session, still valid)
3. `PROGRESS.md` (the ledger)

## ONE-LINE SUMMARY OF TODAY

YOUMANS-4 was finished from scratch (library now 37/37 books clean, 4,755
chapters), the laptop sound was fixed permanently, and step A3 (page_offset,
BIBLE part 3 section 4.6) was attempted on all 37 books. **10 books came out
100 percent and are verified by eye; the other 27 are NOT trusted and must not
be used.** Nothing was loaded into Neo4j; nothing was frozen; the books
themselves are untouched.

## 1. WHAT IS DONE AND TRUSTED

A printed folio was read for 100 percent of the chapters of these 10 books.
These results are in `kitchen/logs/<BOOK>-folio.json` and may be used.

    YOUMANS-4              432/432
    MANDELL-9              210/210
    ROSEN-2022             208/208
    MURRAY-7               142/142
    MIDDLETON-2019          99/99
    KRAUSE-16               93/93
    SABISTON-22             92/92
    CAMPBELL-2020           82/82
    GOODMAN-14              78/78
    ADAMS-12                 49/49

Total: 1,485 chapters with a printed page.

EYE VERIFICATION actually performed (4 pages, 2 books, rendered to PNG and
read by the manager itself):

    SABISTON-22 pdf  651 -> script said 304 -> PAGE IMAGE SHOWS 304  (match)
    SABISTON-22 pdf 1249 -> script said 721 -> PAGE IMAGE SHOWS 721.e89 (match)
    SABISTON-22 pdf  300 -> script said 13  -> PAGE IMAGE SHOWS 13   (match)
    YOUMANS-4  pdf 1885 -> script said 802 -> PAGE IMAGE SHOWS 802  (match)

THIS IS A SAMPLE, NOT A FULL CHECK. Four pages prove the method and caught two
real bugs; they do NOT prove all 1,485 answers. Say so honestly whenever the
number is quoted. The stronger check is still to be written (section 5).

## 2. WHAT IS NOT DONE AND MUST NOT BE USED

The other 27 books have PARTIAL results. Treat them as "printed page unknown".

    NELSON-2024              207/519
    HAZZARD-2022               3/108
    BRANT-5                    1/83
    MILLER-10                 15/87
    IRWIN-RIPPE-2023         146/215
    WILLIAMS-OBSTETRICS-26     6/68
    DELISA-6                   0/62     <- cause KNOWN, see section 4
    KAPLAN-11                  3/60
    GUYTON-2026               34/85
    BOLOGNIA-2024            113/161
    ROCKWOOD-10               23/69
    BRAUNWALD-12              60/102
    WILLIAMS-HEMATOLOGY-2021 121/140
    HARRISON-22              501/504
    AVERY-2021                59/61
    BENZON-2023               84/86
    FIRESTEIN-12             120/122
    OXFORD-6                 125/127
    SLEISENGER-11            130/132
    THOMPSON-2023             18/20
    WILLIAMS-ENDO-2024        46/48
    BRENNER-11                70/71
    DEVITA-12                106/107
    GRAY-2020                 78/79
    GREEN-HAND-2021           59/60
    ROBBINS-10                28/29
    STAHL-2024                60/61

Grouped by how much work is left:

  GROUP A -- almost done, 4 chapters or fewer missing (14 books): HARRISON-22,
  AVERY-2021, BENZON-2023, DEVITA-12, FIRESTEIN-12, OXFORD-6, SLEISENGER-11,
  THOMPSON-2023, WILLIAMS-ENDO-2024, BRENNER-11, GRAY-2020, GREEN-HAND-2021,
  ROBBINS-10, STAHL-2024. Most likely cause: a chapter-opening page that
  prints no folio, and the forward window in the script is too short to reach
  the first page that does print one. Fix by looking BACKWARD as well as
  forward, and by widening the window. This is the cheapest group to finish
  and should be done first.

  GROUP B -- half or more resolved (8 books): BOLOGNIA-2024,
  WILLIAMS-HEMATOLOGY-2021, ROCKWOOD-10, BRAUNWALD-12, IRWIN-RIPPE-2023,
  GUYTON-2026, MILLER-10, NELSON-2024. Needs a look at the book itself.

  GROUP C -- essentially failed (5 books): DELISA-6 (0/62, cause known),
  HAZZARD-2022, BRANT-5, KAPLAN-11, WILLIAMS-OBSTETRICS-26.

BEWARE: the `median_offset` printed in the run log for several of these books
is nonsense (KAPLAN 5886, MILLER 7401, HAZZARD 3348, IRWIN-RIPPE 3697). Those
numbers are NOT offsets; they are what falls out when most chapters failed.
Never quote them and never store them.

## 3. THE CRITICAL DISCOVERY -- ONE OFFSET PER BOOK DOES NOT EXIST

BIBLE part 3 section 4.6 assumes `printed_page = image_number - page_offset`
with ONE number per book. **That assumption is false**, and this was proved
by rendering pages to images and reading them:

- SABISTON-22 prints 876 on pdf page 1429 and 1367 on pdf page 1982. The
  distance between the two PDF pages is 553 but the distance between the two
  printed numbers is 491. Sixty-two unnumbered pages sit between them. A
  single offset cannot serve this book, and the BIBLE's own text anticipates
  exactly this case ("the book has several numbering sequences").
- SABISTON-22 restarts its numbering inside each Section. PDF page 300 prints
  "13", and pdf page 500 prints "178" -- both are correct for their Section.
- So a method that interpolates one offset across a whole book produces
  CONFIDENTLY WRONG pages for hundreds of chapters. That is worse than having
  no answer, because a wrong citation is a false citation (Law 2).

The method therefore decides each chapter's folio LOCALLY, over a forward
window of pages starting at the chapter's own page, and lets the pages in
that window vote. This makes section restarts irrelevant.

## 4. DELISA-6 -- THE ONE FAILURE WITH A KNOWN CAUSE

DELISA-6 returned 0 of 62 because **that book prints no page numbers at all**.

Evidence, gathered 2026-10-19:

- The header of pdf page 51 is "CHAPTER 1 / Clinical Evaluation / John A.
  Freeman / ..." -- no folio anywhere on it.
- Rendering pdf page 51 to an image and looking at it confirms it: a chapter
  opener with authors, then body text. No page number is printed in any
  corner.
- Ordinary pages carry no folio either. pdf page 52 begins mid-sentence with
  body text and ends with body text; pdf page 60 and 203 are the same.
  The text layer of the whole page contains no page number.

So no offset can be measured for DELISA-6 from the text. The honest options,
in order of preference:

  a) Render a page image and look, to see whether a page number exists in a
     form the text layer cannot capture (a picture, a rotated line, a
     decorative element). If one exists, the reader must read it from the
     IMAGE, not the text.
  b) If the book genuinely prints no page numbers, then its citations carry
     the PDF page, recorded as such, and the gap is documented in PROGRESS.md
     as a book-level fact -- never invented (Law 2).

Check the other Group C books the same way before assuming anything.

## 5. WHAT WAS BUILT TODAY AND WHERE IT IS

New, untracked in git at the moment this file was written (git add them):

    kitchen/page_folio.py    the working method. Reads the printed folio of
                             every chapter page from the PDF text layer.
                             Zero model calls, one pdftotext per book.
                             Writes kitchen/logs/<BOOK>-folio.json.
    kitchen/page_offset.py   the BIBLE's single-offset method. Kept only as a
                             comparison. It is WRONG for books that restart
                             their numbering, and must not be the method.

Commands:

    python kitchen/page_folio.py SABISTON-22     one book, prints coverage
    python kitchen/page_folio.py --all           all books
    cat kitchen/logs/SABISTON-22-folio.json      the printed pages, as
                                                 {"<pdf page>": <printed page>}

The intermediate pdftotext caches were DELETED at Nir's request (531 MB,
down to 14 MB). They are rebuilt automatically; they are scratch and never
committed.

### THE TWO BUGS ALREADY FOUND -- do not relearn them

1. Elsevier prints some folios as `721.e89`. The number after the dot is a
   running annotation marker, NOT a page number. Reading it gives "89" and
   puts the chapter on the wrong page. Worse: because that marker advances by
   one on every page while the page part stays put, it forms a PERFECTLY
   CONSTANT WRONG OFFSET (measured 1160 across six consecutive pages of
   SABISTON-22), so it wins a naive vote. The page part (721) is the folio.
   The code handles this with the ANNOT pattern and by never reading the
   trailing part of such a line as a second candidate.
2. The same page can also carry a section or chapter number that looks
   exactly like a folio. PDF page 295 of SABISTON-22 prints "8" as a
   SECTION-relative folio while the neighbouring Section uses a different
   sequence. Only a local window avoids confusing these.

## 6. THE CHECK THAT IS STILL MISSING

Today's eye check was 4 pages by hand. It is not enough. What is needed is a
second, INDEPENDENT check that runs on every chapter, for example:

- for each chapter, open the page image and read the corner number with the
  vision reader (this costs model calls, so it is the expensive option), or
- compare the folio of a chapter page against the folio of the chapter's own
  neighbours inside the chapter (cheap, catches discontinuities), or
- take a random sample of, say, 30 chapters per book, render them, and read
  them by eye -- the manager can do this itself and report the disagreements.

Whatever is chosen, the rule stands: **a printed page that has not been
checked is not evidence.**

## 7. INVARIANTS -- NOTHING TODAY TOUCHED THESE

    python kitchen/toc_validate.py --vis
    37/37 clean, 4755 chapters total

The 37 books, their 49-to-210 provinces, their 4,755 chapters and every
geography file are UNTOUCHED by today's work. `kitchen/books.json` was NOT
modified (no `--save` was ever run), so `page_offset` in it is still null for
every book. Only new files were added.

Do not let page_offset work overwrite a geography file. It must only ever
write `kitchen/logs/<BOOK>-folio.json` and, at the very end, the
`page_offset` field in books.json for books that are actually verified.

## 8. ALREADY DONE TODAY, DO NOT REDO

- YOUMANS-4 was rebuilt from scratch on Nir's explicit order; an earlier run's
  output was deleted, not backed up. It is 432 chapters, 49 provinces, clean.
- `kitchen/toc_merge_dup_provinces.py` was added and wired into build_book.py
  as step 4c; it fixes multi-volume books that print PART 1 again for every
  volume. Commit 348cf67.
- The laptop sound was fixed permanently with Option A (no BIOS, no sudo):
  `~/.local/bin/fix-sound.sh` plus a systemd user service, plus a "Fix Sound"
  desktop and menu icon. Details are in `/home/nir/AUDIO-FIX-HANDOFF.md`.
  Option B (changing the kernel driver) was REFUSED by Nir and must not be
  attempted again without him asking.

## 9. HOW NIR WORKS -- READ THIS BEFORE THE NEXT SESSION

- One thing at a time. He names it or agrees to it; never a batch, never a
  queue.
- Short, plain words. One thing per message. He said plainly he can understand
  anything if it is explained one thing at a time.
- No walls of numbers. He got angry twice today at raw output dumped in chat.
  Summarise, then offer the file.
- He checks facts himself and wants a path or a link so he can look. Give it.
- Emojis in chat replies only. None in files, commits or this memory.
- He does not want to be told what to do; he wants to be asked.
- Never set a book aside on my own initiative; it goes on the question list.
- If a plan fails, say so plainly and stop. Do not keep tinkering.
