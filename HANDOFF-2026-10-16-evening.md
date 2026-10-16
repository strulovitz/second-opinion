# HANDOFF -- evening of 16 Oct 2026 (end of session)

Read this file FIRST when resuming the Second Opinion project. It
supersedes every earlier handoff for the book-reading phase. Nir ended
the session tonight ("good night") after MURRAY-7 was finished.

## Where we are (MEASURED, evidence in PROGRESS.md)

- Validator: 30/30 books clean, 3,220 chapters. Every attempted book
  is clean. Command:
      cd ~/second-opinion && source .venv/bin/activate
      python kitchen/toc_validate.py --vis
- 37 books in the library. 30 read+clean. 7 NOT yet read, in this
  order (Nir approves each book; ONE AT A TIME, never a batch):
      NELSON-2024, OXFORD-6, ROSEN-2022, STAHL-2024,
      WILLIAMS-ENDO-2024, WILLIAMS-HEMATOLOGY-2021, YOUMANS-4
- NEXT BOOK: NELSON-2024. Ask nothing mid-book; take it through like
  tonight's books; commit+push after (Nir approves each time and has
  said "yes please do" / "continue with the next book" every time).

## What was done today (16 Oct, entries (c)-(j) in PROGRESS.md)

Books read+clean today: GREEN-HAND-2021, HAZZARD-2022, IRWIN-RIPPE-2023,
KAPLAN-11, MANDELL-9, MIDDLETON-2019, MILLER-10, MURRAY-7
(8 books in one day). Commits: 2572c1e, 785e051, efbd17c, 56746a8,
a062428, a8dcc3f, 798fac4, b07fafb (all pushed).

## THE METHOD that worked for the 5 "no contents" Elsevier PDFs

MANDELL-9, MIDDLETON-2019, MILLER-10, MURRAY-7 (and KAPLAN-11 partly)
have NO usable printed table of contents in the PDF. In this order:

1. Look with your OWN EYES first (render 6-10 front pages with
   toc_vision.render, open the PNGs). Confirm whether a real contents
   exists. Do not launch a blind build before looking.
2. Read the PDF bookmark outline with pypdf (`walk` pattern used
   today; scripts were one-offs in /tmp/opencode -- they vanish, but
   the full recipe is in PROGRESS entry (j)). Chapters = titles like
   "N Title" or "N. Title" or "N - Title". Sections/Parts = banners.
3. If some bookmark targets are BROKEN (image None): recover the page
   from the chapter's OWN printed title at the TOP of its first page
   in the pdftotext layer ("text-top"). Walk the outline's chapter
   order with a cursor; first top-hit after the previous chapter's
   start wins. Sanity-check on 3-5 KNOWN chapters first, then open
   2-3 recovered pages with your own eyes. (Recipe in PROGRESS (j).)
4. Provinces: prefer the book's own structure -- printed Sections if
   the outline has them; else the "PART N - name" running header on
   each chapter's first pages (that is how MURRAY-7 got its 3 Parts).
5. Write kitchen/logs/<BOOK>-vis-toc.json directly (one-off builder,
   recorded in vis-outline.json), then:
      python kitchen/toc_validate.py <BOOK> --vis
   must print RESULT <BOOK> ok. Then full --vis must stay "N/N clean".
6. Validator now accepts three honest page sources when no contents
   text exists: pdf-link, pdf-outline, text-top (see toc_validate.py).

## Rules that still stand (do not relearn)

- ONE book at a time. NEVER a batch/queue unless Nir asks.
- Nothing invented: pages/titles/numbers only from the book (printed
  page, PDF hyperlink, PDF outline, or the page's own printed title).
- Nothing dropped silently: sub-entries go to a recorded side JSON.
- Backup vis-toc.json before ANY rebuild (toc_reparse has emptied a
  book once).
- Emojis in chat replies only; NEVER in files/commits/memory.
- Commit+push after each book, with Nir's approval.
- Long jobs: setsid nohup ... + disown, or they die with the tool call.
- Watchdog: /tmp/opencode/watchdog2.sh <BOOK_ID> (heartbeat every 60s
  in kitchen/logs/<BOOK>-watchdog.log). Kill with an ANCHORED pattern:
  pgrep -f "^/bin/bash /tmp/opencode/watchdog2.sh <ID>" -- plain
  pkill -f kills the agent's own shell.
- Launch builds with .venv/bin/python (plain "python" is not on PATH
  outside the venv; this failed once today on MANDELL-9).

## After the 7 books are done

- page_offset (BIBLE part 3 section 4.6) is still NOT started and
  every citation depends on it. Then seating, raster, registry,
  load/verify, and the FREEZE. Nothing is in Neo4j yet (deliberate).
- Gemma 4 31B comparison (re-read all books with the second brain)
  is planned for later, when Nir installs it.
