# DeepSeek handoff -- repair Campbell from the actual book

## Human's request and scope

Nir approved repairing CAMPBELL-2020 with minimum money. He then stopped
the paid SMART session and requested a detailed explanation for DeepSeek,
without unfinished code. This handoff is the task and evidence, not an
implementation. Repair this ONE book, save the result, report and stop.

Read the repository AGENTS.md, the current PROGRESS.md pointers, and
BIBLE Part 3 sections 4.2-4.6 plus Part 8. BIBLE files are never edited.

## The actual defect

The current saved contents and export agree with each other but disagree
with the book. They contain 82 chapters in 4 purported volume groups.
Chapter 1 is wrongly called "Total Ankle Arthroplasty", starting at 14.
The actual chapter 1 is "Surgical Techniques", printed page 1, PDF page 27.

The previous source was contaminated by the PDF's "List of Techniques".
PDF page 11 explicitly has that heading and lists operations such as
45.1, 45.2, etc. It is not the book's chapter contents. Re-exporting that
source again cannot fix it, even when all range arithmetic passes.

## Reliable source already found -- zero AI calls

The PDF itself contains a detailed bookmark hierarchy: 4,183 entries,
including exactly 90 explicit chapter bookmarks numbered 1 through 90,
under 19 genuine Part headings. Each has an internal PDF destination.
The chapter bookmarks say "Chapter N: Title". Technique/subheading
bookmarks are a different level and must not become chapters.

Examples measured from the PDF's bookmarks:

- Part I: General Principles -- chapter 1 Surgical Techniques, PDF 27;
  chapter 2 Advanced Imaging in Orthopaedics, PDF 170.
- Part II: Reconstructive Procedures of the Hip in Adults -- chapter 3
  Arthroplasty of the Hip, PDF 210; chapter 4 Surface Replacement Hip
  Arthroplasty, PDF 382.
- Chapter 10 Total Ankle Arthroplasty belongs at PDF 599, not chapter 1.
- Chapter 45 Knee Injuries begins at PDF 2460.
- Part XIX: The Foot and Ankle contains the final chapters. Chapter 89
  Fractures and Dislocations of the Foot begins at PDF 4902; chapter 90
  Sports Injuries of the Ankle begins at PDF 4990.

Use the bookmarks' actual titles and parent Parts; do not invent headings
or retain the incorrect four-volume grouping. The existing toc_outline.py
shows how this project reads bookmarks with pypdf; its old chapter-matching
pattern does not recognise this PDF's "Chapter N: Title" form.

## Page units and the last chapter

The PDF has 5,036 pages, matching books.json. Bookmark destinations are
PDF page numbers. Keep that distinct from printed folios. Existing tools
already support PDF-page citations via the pdf-outline source marker.
If you use that convention, say so explicitly; printed-page mapping
remains a separate Step A3 task. Never silently label PDF numbers printed.

PDF page-label metadata is unreliable here: it labels PDF page 27 "2",
but the actual chapter opener prints 1. Some label ranges also produce
pypdf warnings. Do not use those labels as verified printed folios.

The configured index location is absent. The outline places References
for chapter 90 at PDF 5026 and Supplemental References at PDF 5032.
The actual final PDF page, 5036, still carries the running heading
"CHAPTER 90 SPORTS INJURIES OF THE ANKLE" and folio "4536.e5".
Use this evidence when determining where the final chapter ends in the
provided PDF; distinguish document-end proof from printed/index proof.
Do not interpret 4536.e5 as the integer 4536 or mix it with PDF 5036.

## Cost-saving and the observed blocker

Start with one PDF open and its bookmarks. That metadata read was quick.
Check actual chapter-opening headings against bookmark targets, with
automated text matching and a small spread of samples first. The free
Qwen reader is available for genuinely ambiguous pages.

Repeatedly launching pdftotext for each of 90 chapter pages was too slow:
the read-only attempt confirmed only the first 10 before its 180-second
tool timeout. It wrote no book data. Avoid repeating that strategy.

A one-open-PDF pypdf text experiment then failed its strict chapter-1
heading check. This is not evidence that the bookmark is wrong: pdftotext
had already shown the correct chapter-1 heading at PDF 27. Inspect the
text extractor's ordering/spacing on that ONE page and handle it before
expanding verification. Do not repeatedly retry the full book or weaken
verification to accept any page with a number. Cache useful proof where
appropriate, print progress, and keep the human watching.

## Deliverable and checks

Back up the old Campbell vis-toc, export, relevant evidence and receipt
before replacing anything. Repair both the source and export, so a later
export cannot restore the bad 82-chapter list. The old folio mapping was
built against that bad list; do not blindly reuse it as new page proof.

Verify all of the following:
- Exactly 90 distinct chapters, numbered 1-90 in book order.
- The 19 real Parts, correct chapter membership and verbatim titles.
- Valid, increasing PDF destinations; target-heading checks have real
  evidence, with unresolved cases stated honestly.
- Internal chapter ends use the next start minus one, with the approved
  shared-page exception. Province bounds agree with their chapters.
- Final chapter-end evidence and page units are stated explicitly.
- Other books and books.json stay unchanged.

Update only Campbell's entry in TOC-REPAIR-STATUS.json using the project's
receipt conventions and correct file hashes. Preserve the prior receipt
in the backup; do not claim the whole library newly verified. Record the
commands, outputs, counts, units and remaining limitations in PROGRESS.md.
Commit and push the intended code/reports, keeping PDFs, images, full-page
text and local logs gitignored. Then give Nir a short result and stop.

## State at handoff

No Campbell source/export/receipt was changed during the stopped attempt.
No reader calls, rendering or database writes were made. SMART withdrew
its unfinished implementation at Nir's request. The existing scripts
remain at their previous committed versions.

The preceding read-only library review found 39 tests passing, matching
hashes for all 37 receipts, and correct internal range arithmetic. That
does not prove the chapter lists themselves. Campbell's physical-book
mismatch is confirmed; the other rebuilt books' physical review remains
open. Finish Campbell before returning to Step A3 or another book.
