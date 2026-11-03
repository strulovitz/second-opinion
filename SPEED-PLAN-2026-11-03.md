# SPEED PLAN -- the skeleton in two weeks, not months

Author: Claude Fable, 3 November 2026, at Nir's request.
Status: PROPOSAL. Becomes BIBLE Part 0 (overriding all other parts) the moment
Nir says "go". Nothing below has been run yet.

## 0. The goal, restated so the plan serves it

The skeleton is NOT the product. The product is the added-value phase: asking
"what do the Western textbooks say about X, and what did someone in China,
India or elsewhere publish that the West buried or ignores?" and getting a
cited answer. For that, the skeleton needs only three things:

1. A list of medical things (diseases, symptoms, drugs/treatments).
2. For each thing, where the textbooks talk about it (book, chapter, page).
3. The actual text of those pages, searchable, so an AI can read the Western
   position quickly and compare it with outside sources.

Everything else (3D globe, altitude bands, circle sizes) is presentation. It
stays, because it is already built and it is what people will share. But it
must never again cost a day of model time.

Hard budget: every book must take under one day of laptop time, and the whole
skeleton under one month. Target below: about two weeks.

## 1. Why the current design is slow (the honest diagnosis)

- It uses a 27B language model as a typist. Parsing an index page with the
  model took about 80 seconds per page; pdftotext gives the same text in
  under a second. 230 Harrison index pages took days of supervised sessions.
- It asks the model one question at a time, ~5 seconds each, 82% of the time,
  and 93% of the answers were "NEW" (useless). Most of those questions
  compared Harrison names to other Harrison names, which the BIBLE never
  asked for; the index's own "see" lines already give within-book synonyms.
- Phase B planned to have the model READ every page of every book (tens of
  thousands of pages). That is months. It was already cancelled, but nothing
  replaced it, so "where is X discussed" would have stayed thin.
- Every step waits for a human "okay" before the next page or batch. Good for
  trust, deadly for a one-month deadline when steps are deterministic anyway.

Nir's three tricks were right: batch the questions, use a small model for text
jobs, and do the thinking in ONE pass instead of returning to the same data
again and again. They are all adopted below, and extended.

## 2. The tricks, all of them

T1. Text first, model last. pdftotext (and the PDF's hidden links) for every
    page of every book. The model is only called for a page that FAILS a
    deterministic check, never as the default reader. Scans without a text
    layer get tesseract OCR (seconds per page), not a vision model.

T2. Parse indexes with code, not a model. Back-of-book indexes are regular:
    headword, optional "see X", page numbers, indented subentries. One regex
    parser plus a validator (every page number in the text must be captured).
    Pages the parser rejects go to a small model in a batch, as repair only.

T3. Within one book, NEVER ask the model whether two headwords are the same.
    Index headwords of one book are distinct by construction; "see" lines
    carry the synonyms. Zero resolution calls per book. (This alone turns the
    remaining Harrison work from 8-10 hours into about 1-2 hours even in the
    old code.)

T4. Late binding across books. Do not merge entities book by book while the
    registry grows. Store every book's headwords as TERMS first (fast, bulk).
    Merge terms into shared entities ONCE, at the end, over all books, in a
    single global pass. One pass instead of 37 growing passes.

T5. Embeddings instead of questions. A local embedding model (for example
    bge-m3 or nomic-embed through Ollama, ~1 GB) turns all ~100,000 terms
    into vectors in minutes on this GPU. Terms whose vectors are nearly
    identical AND share a group are merged by code. Only the uncertain middle
    band (perhaps 5-10% of terms) is shown to a small language model, in
    batches of 50 per call. Expected: a few hundred calls total for the whole
    library, not tens of thousands.

T6. Small model for text, big model only for pictures. Qwen 27B stays as the
    optional vision fallback. Text jobs (batch repair, batch SAME/NEW,
    classification) use a 4B-8B model. Two to four times faster per token,
    and leaves VRAM for the embedding model to stay loaded alongside it.

T7. Classification by neighbours. Classify a few hundred terms with the model
    once (batched, 100 per call). Classify the rest by nearest labelled
    neighbour in embedding space. Zero further model calls. Accuracy maybe
    90-95 percent; acceptable for a proof of concept and fixable later.

T8. Replace "read every page" with "index every page". pdftotext of all 37
    books into a full-text search database (SQLite FTS5; a single file, no
    server). ~100,000 pages in under an hour on this machine. "Where is X
    discussed" becomes a search query answered in milliseconds, with the
    verbatim snippet as proof. Later, if wanted, page-level embeddings for
    semantic search: a few GPU-hours, run overnight, optional.

T9. Frequency and "altitude" from counts, not from reading. Number of index
    references plus number of full-text hits per term. Pure SQL, seconds.

T10. Bulk loads, not row-by-row transactions. Neo4j gets each book's terms and
     page links in one UNWIND statement per book (seconds), not one
     transaction per entry with a proof check each time.

T11. Run deterministic steps for ALL books in one go. Supervision stays for
     model steps and for review samples; pdftotext, parsing, loading and
     exporting run as one batch script with a summary at the end.

T12. Keep the model warm and parallel. Ollama keep_alive set for the session,
     OLLAMA_NUM_PARALLEL so batched requests overlap, no cold reloads between
     chunks.

T13. Review by sample, not by page. Per book: 20 random terms with their page
     and snippet, shown once. Per library: the merge decisions in the
     uncertain band, shown once. Nir approves books in groups, not pages.

T14. Proof is the snippet. Law 2 is kept in spirit: every page claim carries
     the page number and the verbatim text snippet from pdftotext. Page
     images are rendered on demand for the viewer, not stored as evidence
     for every claim.

T15. Reuse what exists. The geography (37 books, 5,334 territories), the
     Goldberg globe, the viewer, the export format and the Harrison index
     text already extracted are all kept. Only the slow middle is replaced.

## 3. The new pipeline, start to finish

Stage 1 (all books, one script, about one day including fixing parser edge
cases): pdftotext every page -> pages table + FTS index; find the index
range per book (books.json already has 25; the rest by searching for the
index heading); parse the index with code; validate; store TERMS with page
references and "see" links. Model used only for rejected pages, batched.

Stage 2 (library-wide, about one day): embed all terms; classify seed set
with the small model; classify the rest by neighbours; merge near-identical
terms by code; batch the uncertain band through the small model; write
ENTITIES with aliases and lit spots to Neo4j in bulk.

Stage 3 (about two days): export; replace the demo data on the live globe
with real data; search box over the FTS database; one page per entity
listing every book/page with its snippet.

Stage 4 (the actual product; starts in week three): the "second opinion"
assistant. Given a disease or drug, it pulls the Western textbook passages
from the FTS database and compares them with outside sources. Free sources
with APIs: PubMed/Europe PMC, ClinicalTrials.gov, WHO essential medicines,
Indian price lists (NPPA), openFDA adverse events. Chinese literature: I do
not know a free, reliable English-accessible API for CNKI/Wanfang; this
needs its own investigation and I will not pretend otherwise.

## 4. Time, honestly

Measured today: pdftotext of one Harrison page is well under a second; the
embedding and small-model numbers are expectations, not measurements. First
thing after "go": a one-hour timed trial of stages 1-2 on Harrison alone, so
the real per-book number is known before the plan is promised.

Expected: stage 1 for all 37 books in 1-2 days, stage 2 in 1 day, stage 3 in
2 days, parser surprises and review in the remaining days of week two.
Skeleton: about two weeks. Worst case I can see: four weeks, which is still
inside Nir's maximum.

## 5. What we lose, and why it is acceptable

- Some wrong merges and wrong groups (estimate 5-10%). Visible, fixable, and
  irrelevant to the goal of finding buried treatments.
- No model "understanding" of every page. Replaced by search, which is what
  the added-value phase needs anyway.
- Fewer human approvals. Replaced by samples and by the fact that every claim
  still carries its page and snippet, so any error can be checked by eye.

## 6. What happens to the work already done

- Harrison's 4,350 resolved entries and 2,517 entities are not wasted: they
  become terms like everything else and are re-merged in the global pass.
- Geography, globe, viewer, TOC data: unchanged.
- The old per-entry resolver and the model-based index parser are retired,
  kept in git history.

## 7. The decisions Nir owns

D1. Approve this plan as BIBLE Part 0, overriding earlier parts where they
    conflict (speed over perfection, text before model, late binding, sample
    review). Yes/no.
D2. Allow installing one embedding model and one 4B-8B text model through
    Ollama (a few GB download). Yes/no.
D3. Allow deterministic steps to run for all books in one batch, supervised
    by summary rather than page by page. Yes/no.
D4. Confirm the product definition in section 0 and stage 4, or correct it in
    one sentence.
