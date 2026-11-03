# HANDOFF 2026-11-04 MORNING -- Claude Opus 5.5 restart point

Read first: BIBLE/part-00-speed-charter.md (rules; sections 10-11 = next
work), then this file. Older handoff HANDOFF-2026-11-03-EVENING.md is still
valid for everything not changed below.

## Done on 3 Nov late (all pushed: aba3103, 761f312)

- speed_entities.py: single page offset replaced by a per-chapter page map
  (chapter titles found in FTS, longest chain of openers) plus a per-page
  folio map for index references. All 37/37 books now have full-text links.
  The old offset was wrong for CAMPBELL, MANDELL, STAHL, WILLIAMS-ENDO,
  NELSON (fixed). Check in 15 s: speed_entities.py --offsets-only.
- kitchen/epub_folios.py BOOK file.epub: printed-page map from the print
  page markers inside a publisher EPUB -> kitchen/logs/<BOOK>-folios.json,
  used automatically by speed_entities. BRANT-5 done (EPUB kept as
  kitchen/books/BRANT-5-print-markers.epub; index spots 0 -> 4,241).
- Totals: 35,845 entities, 2,376,084 lit spots. Nir checked "inguinal
  hernia" on the globe: many columns, Sabiston included.

## Next (Nir's plan, one book at a time, he finds the files)

1. Five calibre books (EPUB converted to PDF, no printed folios) have no
   index links: HAZZARD-2022, IRWIN-RIPPE-2023, KAPLAN-11, ROCKWOOD-10,
   WILLIAMS-OBSTETRICS-26. Nir will download, per book, an EPUB / older
   print-replica PDF / equivalent textbook. For an EPUB: check for markers
   (unzip -p f.epub '*.xhtml' | grep -c 'id="page'), then
     .venv/bin/python kitchen/epub_folios.py BOOK f.epub
     .venv/bin/python kitchen/speed_entities.py   (6 min)
     .venv/bin/python kitchen/speed_export.py     (45 s)
   then copy the EPUB to kitchen/books/<BOOK>-print-markers.epub, add a
   PROGRESS.md line, commit, push. A new PDF or a replacement textbook
   needs speed_text.py / speed_index.py / books.json / TOC work; ask Nir.
   A calibre PDF (pdfinfo Creator "calibre") is NOT better; say so.
2. Then Part 0 section 10: ingestion system (worker.py, ingest.py). Ask Nir
   first: inputs (PDF folder, pasted text, both) and the OpenRouter model
   order (candidates measured 3 Nov: deepseek/deepseek-v4-flash 0.18,
   qwen/qwen3.7-flash 0.13, z-ai/glm-5.3-flash 0.08 dollars per M output).
   kitchen/.env has NO OPENROUTER_API_KEY yet; Nir must add it himself;
   never read or print it.
3. Section 11.2 junk names, 11.3 stale tests.

## Cost rules (Nir, repeated)

Save money: no screenshots (Nir is the eyes), one-shot fixes, short
replies, delegate long runs/grunt work to DeepSeek 4.1 Flash (Nir switches
models). Do not do unnecessary things.
