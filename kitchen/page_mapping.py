#!/usr/bin/env python3
"""A3: uniform printed/PDF proof or an honest per-range proposal, ONE book.

  python kitchen/page_mapping.py BOOK_ID
  python kitchen/page_mapping.py BOOK_ID --pairs checked-pairs.json --cache
  python kitchen/page_mapping.py BOOK_ID --save

Uniform saves require four spread samples, all available accepted pairs in
agreement and recorded book acceptance. Irregular mappings are proposals for
the human, never automatically installed as page_offsets.
"""

import argparse
import copy
import hashlib
import json
import sys
from pathlib import Path

from page_offset import flatten, key, positive_integer, require
from toc_evidence import (PdfEvidence, corner_folios, fingerprint, opener_matches,
                          pdf_identity, heading_names_chapter)
from toc_reexport import atomic_write
from toc_store import save_bundle, snapshot

ROOT = Path(__file__).resolve().parents[1]


def accepted_pairs(book, toc, evidence, logs):
    """Preserve every accepted pair; PDF-unit citations do not imply folios."""
    require(evidence.get("book_id", evidence.get("_summary", {}).get("book")) == book["book_id"],
            "wrong pair evidence book")
    chapters = flatten(toc)
    by_key = {key(p, c): i for i, (p, c) in enumerate(chapters)}
    require(len(by_key) == len(chapters), "duplicate TOC chapter identities")
    pairs, unresolved, seen = [], [], set()
    for row in evidence["chapters"]:
        identity = key(row["province"], row)
        require(identity in by_key and identity not in seen, "stale/duplicate pair identity; do not reuse bad-list evidence")
        seen.add(identity)
        if row.get("status") != "ok" or row.get("opener_confirmed") is not True:
            unresolved.append({"number": row.get("number"), "reason": "unconfirmed saved opener"})
            continue
        pdf = row.get("pdf_page")
        require(positive_integer(pdf) and pdf <= book["page_count_images"], "invalid PDF pair")
        chapter = chapters[by_key[identity]][1]
        require(chapter.get("pdf_page") in (None, pdf), "TOC PDF target and pair disagree")
        folio = row.get("printed") if row.get("kind") == "printed" else None
        if row.get("kind") == "pdf-page":
            # Use only an actual reader observation of this page, not the
            # PDF-page value intentionally stored in row['printed'].
            observations = row.get("tries", []) + row.get("refine", {}).get("back_walk", [])
            candidates = {r["folio"] for r in observations if r.get("pdf_page") == pdf
                          and positive_integer(r.get("folio")) and r.get("kind") in ("OPENING", "BODY")}
            if len(candidates) == 1:
                folio = candidates.pop()
        if not positive_integer(folio):
            unresolved.append({"number": row.get("number"), "pdf_page": pdf,
                               "reason": "no accepted printed folio (PDF citation/label is not a pair)"})
            continue
        image_root = logs / "eyes-render" / book["book_id"]
        image = (image_root / row.get("image_file", "")).resolve()
        require(image.is_relative_to(image_root.resolve()), "reader image must stay in this book's evidence directory")
        if image.name != f"{pdf:05d}.png":
            image = image_root / f"{pdf:05d}.png"
        require(image.is_file(), f"missing saved observation image {image}")
        if row.get("image_sha256"):
            require(hashlib.sha256(image.read_bytes()).hexdigest() == row["image_sha256"], "saved reader image changed")
        if Path(row.get("image_file", "")).name != image.name:
            require(any(r.get("pdf_page") == pdf and r.get("folio") == folio
                        for r in row.get("refine", {}).get("back_walk", [])), "stale image lacks saved pair proof")
        if row.get("kind") == "printed":
            pdf_unit = chapter.get("_page_source") in ("pdf-outline", "pdf-link", "text-top")
            require(chapter["page_start"] == folio or (pdf_unit and chapter["page_start"] == pdf),
                    "TOC printed folio and pair disagree")
        pairs.append({"province": row["province"], "number": row.get("number"), "title": row["title"],
                      "chapter_index": by_key[identity], "pdf_page": pdf, "printed": folio,
                      "offset": pdf - folio, "image_file": str(image.relative_to(logs)),
                      "reader_heading": row.get("heading"), "reader_raw": row.get("reader_raw"),
                      "printed_observed": row.get("printed_observed", False)})
    pairs.sort(key=lambda r: r["chapter_index"])
    require(all(a["pdf_page"] <= b["pdf_page"] for a, b in zip(pairs, pairs[1:])), "PDF pair sequence decreases")
    return pairs, unresolved


def propose_mapping(chapters, pairs, unresolved):
    require(len(chapters) >= 4, "fewer than four chapters; human decision required")
    sample_indices = [0, len(chapters) // 4, len(chapters) // 2, 3 * len(chapters) // 4]
    by_index = {r["chapter_index"]: r for r in pairs}
    missing = [i for i in sample_indices if i not in by_index]
    values = {r["offset"] for r in pairs}
    segments = []
    for row in pairs:
        if not segments or segments[-1]["offset"] != row["offset"]:
            previous = segments[-1]["last_observed_image"] if segments else None
            segments.append({"from_image": row["pdf_page"], "last_observed_image": row["pdf_page"],
                             "offset": row["offset"], "observed_pairs": 1,
                             "transition_after_image": previous})
        else:
            segments[-1]["last_observed_image"] = row["pdf_page"]
            segments[-1]["observed_pairs"] += 1
    uniform = len(values) == 1 and not missing and not unresolved
    return {"state": "uniform-candidate" if uniform else "human-review",
            "page_offset": next(iter(values)) if uniform else None,
            "samples": [by_index[i] for i in sample_indices if i in by_index],
            "missing_sample_chapters": [chapters[i][1].get("number") for i in missing],
            "accepted_pairs": pairs, "unresolved": unresolved,
            "proposed_page_offsets": segments,
            "warning": "segments cover observations only; exact transitions and unsampled inserts are not proved; human approval required"}


def cross_check(session, samples, current_reader=False):
    results = []
    for row in samples:
        text = session.text(row["pdf_page"])
        saved = (current_reader and row["printed_observed"] and row["reader_raw"]
                 and heading_names_chapter(row["reader_heading"], row["number"], row["title"]))
        require(opener_matches(text, row["number"], row["title"]) or saved,
                f"ch{row['number']}: sample heading ambiguous; use the free reader")
        seen = row["printed"] in corner_folios(text, row["number"]) or bool(saved)
        results.append({"number": row["number"], "pdf_page": row["pdf_page"], "printed": row["printed"],
                        "opener": True, "corner_folio": seen})
    require(any(r["corner_folio"] for r in results), "no sampled folio readable; human/free-reader cross-check needed")
    return results


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("book")
    parser.add_argument("--pairs", type=Path, help="checked reader observations; same rows as eyes evidence")
    parser.add_argument("--cache", action="store_true")
    parser.add_argument("--save", action="store_true")
    parser.add_argument("--report", action="store_true", help="save BOOK_ID-mapping-proposal.json under kitchen/logs")
    args = parser.parse_args(argv)
    try:
        kitchen, logs = ROOT / "kitchen", ROOT / "kitchen/logs"
        books_path = kitchen / "books.json"
        toc_path = logs / f"{args.book}-toc.json"
        evidence_path = args.pairs or logs / f"{args.book}-eyes.json"
        proof_path = logs / f"{args.book}-mapping-proof.json"
        originals = snapshot([books_path, toc_path, evidence_path, proof_path])
        books = json.loads(originals[books_path])
        matches = [b for b in books if b["book_id"] == args.book]
        require(len(matches) == 1, "unknown or duplicate book ID")
        book = matches[0]
        require(originals[evidence_path] is not None, "no saved pairs; prepare checked observations with the free reader")
        toc, evidence = json.loads(originals[toc_path]), json.loads(originals[evidence_path])
        pairs, unresolved = accepted_pairs(book, toc, evidence, logs)
        report = propose_mapping(flatten(toc), pairs, unresolved)
        pdf = kitchen / "books" / book["pdf_file"]
        identity = pdf_identity(pdf)
        require(not evidence.get("pdf_identity") or evidence["pdf_identity"] == identity, "pair evidence PDF changed")
        if args.pairs:
            require(evidence.get("pdf_identity") == identity, "new pair input must name its current PDF identity")
        report.update(book=args.book, pdf_identity=identity, toc_hash=fingerprint(toc),
                      evidence_hash=fingerprint(evidence))
        with PdfEvidence(pdf, logs / f"{args.book}-mapping-cache.json", report["evidence_hash"]) as session:
            if report["state"] == "uniform-candidate":
                report["cross_checks"] = cross_check(session, report["samples"], evidence.get("pdf_identity") == identity)
                report["state"] = "verified-uniform"
            if args.cache:
                session.save_cache()
        print(f"{args.book}: {report['state']}; accepted printed pairs={len(pairs)}; "
              f"page_offset={report['page_offset']}; unresolved={len(unresolved)}")
        for sample in report["samples"]:
            print(f"  ch{sample['number']}: PDF {sample['pdf_page']} -> printed {sample['printed']}; offset {sample['offset']}")
        if report["state"] == "human-review":
            if not pairs:
                print("  no accepted printed/PDF pairs; use the free reader, not PDF labels")
            print(f"  missing spread samples: {report['missing_sample_chapters']}")
            print(f"  proposed observed ranges: {report['proposed_page_offsets']}")
            print("  " + report["warning"])
        if args.report:
            atomic_write(logs / f"{args.book}-mapping-proposal.json", json.dumps(report, indent=2, ensure_ascii=False) + "\n")
        if args.save:
            require(report["state"] == "verified-uniform", "irregular/incomplete mapping is a proposal, not a saveable offset")
            require(book["status"] in ("accepted", "geography-done"), "book acceptance not recorded; ask the human")
            require(not book.get("page_offsets"), "existing per-range decision must not be overwritten")
            require(book.get("page_offset") in (None, report["page_offset"]), "stored offset conflicts; ask the human")
            require(pdf_identity(pdf) == identity, "PDF changed during verification")
            updated = copy.deepcopy(books)
            next(b for b in updated if b["book_id"] == args.book)["page_offset"] = report["page_offset"]
            payload = json.dumps(updated, indent=1, ensure_ascii=False) + "\n"
            if updated == books:
                payload = originals[books_path]
            proof = json.dumps(report, indent=2, ensure_ascii=False) + "\n"
            backup = save_bundle(ROOT, logs, args.book, "uniform-page-mapping", originals,
                                 {books_path: payload, proof_path: proof})
            print(f"Saved verified uniform offset; backup: {backup}" if backup else "Already current; no writes")
        else:
            print("Dry run; books.json unchanged")
        return 0 if report["state"] == "verified-uniform" else 2
    except (ValueError, KeyError, TypeError, OSError) as exc:
        print(f"NOT SAVED: {args.book}: {exc}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    sys.exit(main())
