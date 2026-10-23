#!/usr/bin/env python3
"""Verify/correct ONE chapter list with PDF bookmarks or reader-checked contents.

  python kitchen/toc_book.py BOOK_ID                       # current target check
  python kitchen/toc_book.py BOOK_ID --outline             # proposed bookmark list
  python kitchen/toc_book.py BOOK_ID --source checked.json # proposed contents list
  python kitchen/toc_book.py BOOK_ID --outline --apply     # backup source/export

Dry runs change nothing. --cache explicitly saves selected-page text for reuse.
Saved contents input format and limitations are in DEEPSEEK-TOC-RUNBOOK.md.
"""

import argparse
import copy
import hashlib
import json
import sys
from pathlib import Path

from page_offset import flatten, key, positive_integer, require
from toc_evidence import (PdfEvidence, bookmark_toc, fingerprint, pdf_identity,
                          verify_targets, heading_names_chapter, corner_folios)
from toc_outline import walk
from toc_ranges import fill_ranges
from toc_repair import digest
from toc_repair_source import final_boundary
from toc_store import save_bundle, snapshot

ROOT = Path(__file__).resolve().parents[1]


def document(text):
    return json.loads(text) if text else {"provinces": []}


def list_identity(toc):
    return [(p, c.get("number"), c.get("title"), c.get("page_start"), c.get("pdf_page"))
            for p, c in flatten(toc)]


def keep_flat_groups(toc, previous):
    """Existing human-authored grouping survives a flat bookmark list."""
    if all(p["name"] != "ALL" for p in toc["provinces"]):
        return toc
    have = [(str(c.get("number")), c["title"]) for _, c in flatten(previous)]
    want = [(str(c.get("number")), c["title"]) for _, c in flatten(toc)]
    require(have == want and all(p["name"] != "ALL" for p in previous["provinces"]),
            "flat chapter list needs the human's grouping; supply grouped checked contents")
    chapters = iter(c for _, c in flatten(toc))
    result = copy.deepcopy(previous)
    for province in result["provinces"]:
        province["chapters"] = [next(chapters) for _ in province["chapters"]]
    return result


def checked_source(data, book, identity):
    require(data.get("book_id") == book["book_id"], "wrong source book")
    require(data.get("pdf_identity") == identity, "checked contents belong to another PDF identity")
    require(data.get("kind") in ("chapter-contents", "saved-reader"),
            "not chapter contents (techniques/internal outlines/online lists are not accepted)")
    require(data.get("source_pages") and all(positive_integer(p) and p <= book["page_count_images"]
                                           for p in data["source_pages"]), "missing physical contents pages")
    require(data.get("unit") in ("printed", "pdf-page"), "explicit citation unit required")
    toc = {"provinces": copy.deepcopy(data["provinces"])}
    for _, ch in flatten(toc):
        require(positive_integer(ch.get("pdf_page")), "contents chapter needs a PDF target")
        require(data["unit"] != "pdf-page" or ch["page_start"] == ch["pdf_page"], "mixed citation units")
        ch["_page_source"] = "pdf-outline" if data["unit"] == "pdf-page" else "verified-contents"
    return toc, {"kind": data["kind"], "source_pages": data["source_pages"],
                 "source_hash": fingerprint(data), "unresolved": []}, data["unit"]


def reader_proofs(data, unresolved, logs):
    """Use explicit saved reader observations only for ambiguous text pages."""
    accepted, remaining = [], []
    observations = data.get("opener_evidence", []) if data else []
    for row in unresolved:
        matches = [r for r in observations if all(r.get(k) == row[k]
                   for k in ("province", "number", "title", "pdf_page"))]
        if len(matches) != 1:
            remaining.append(row)
            continue
        proof = matches[0]
        image = (logs / proof.get("image_file", "")).resolve()
        require(image.is_relative_to(logs.resolve()) and image.is_file(), "missing/local reader image required")
        require(proof.get("opener_confirmed") is True and proof.get("kind") == "OPENING"
                and proof.get("reader_raw") and proof.get("heading"), "reader observation does not confirm opener")
        require(image.name == f"{row['pdf_page']:05d}.png", "reader image does not name the selected PDF page")
        require(image.parent.name == fingerprint(data["pdf_identity"])[:16]
                and proof.get("image_sha256") == hashlib.sha256(image.read_bytes()).hexdigest(),
                "reader image must be bound to the current PDF; use toc_observe.py")
        require(heading_names_chapter(proof["heading"], row["number"], row["title"]),
                "reader heading does not name this chapter in full")
        accepted.append(row | {"method": "saved-free-reader", "observation": proof})
    return accepted, remaining


def verify_source_folios(session, toc, supplied, logs):
    for province, chapter in flatten(toc):
        if chapter["page_start"] in corner_folios(session.text(chapter["pdf_page"]), chapter.get("number")):
            continue
        row = {"province": province, "number": chapter.get("number"), "title": chapter["title"],
               "pdf_page": chapter["pdf_page"]}
        proofs, missing = reader_proofs(supplied, [row], logs)
        require(not missing and proofs[0]["observation"].get("printed_observed") is True
                and proofs[0]["observation"].get("printed") == chapter["page_start"],
                f"ch{chapter.get('number')}: printed folio is not proved; use PDF units or a saved reader observation")


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("book")
    source = parser.add_mutually_exclusive_group()
    source.add_argument("--outline", action="store_true")
    source.add_argument("--source", type=Path)
    parser.add_argument("--proposal", action="store_true", help="save BOOK_ID-toc-proposal.json for selected free-reader checks")
    parser.add_argument("--observations", type=Path, help="checked-pairs file from toc_observe.py for ambiguous targets")
    parser.add_argument("--apply", action="store_true")
    parser.add_argument("--cache", action="store_true", help="explicitly save selected-page text (even in dry run)")
    parser.add_argument("--check-index", action="store_true")
    parser.add_argument("--document-end", action="store_true", help="check the final PDF page still names the last chapter (PDF-unit only)")
    args = parser.parse_args(argv)
    try:
        kitchen, logs = ROOT / "kitchen", ROOT / "kitchen/logs"
        books_path, status_path = kitchen / "books.json", ROOT / "TOC-REPAIR-STATUS.json"
        paths = {s: logs / f"{args.book}-{s}.json" for s in ("vis-toc", "toc", "eyes", "toc-proof")}
        cache = logs / f"{args.book}-target-cache.json"
        legacy_cache = logs / f"{args.book}-folio.txt"
        originals = snapshot([books_path, status_path, *paths.values(), legacy_cache])
        books = json.loads(originals[books_path])
        matches = [b for b in books if b["book_id"] == args.book]
        require(len(matches) == 1, "unknown or duplicate book ID")
        book = matches[0]
        old = document(originals[paths["toc"]])
        previous = document(originals[paths["vis-toc"]])
        require(args.outline or args.source or originals[paths["vis-toc"]] is not None,
                "accepted contents missing; choose an explicit outline/checked source")
        pdf = kitchen / "books" / book["pdf_file"]
        supplied_text = args.source.read_text() if args.source else None
        supplied = json.loads(supplied_text) if supplied_text else None
        observations_text = args.observations.read_text() if args.observations else None
        observations = json.loads(observations_text) if observations_text else None
        with PdfEvidence(pdf, cache, evidence={"book": book, "source": supplied or previous,
                                             "mode": "outline" if args.outline else "existing"}) as session:
            require(len(session.open().pages) == book["page_count_images"], "configured PDF length differs")
            if args.outline:
                toc, provenance = bookmark_toc(walk(session.open(), session.open().outline), book["title"])
                unit = "pdf-page"
            elif supplied:
                toc, provenance, unit = checked_source(supplied, book, session.identity)
            else:
                toc = copy.deepcopy(old)
                provenance = {"kind": "existing-export", "unresolved": [],
                              "note": "target checks do not establish chapter-list completeness"}
                unit = "pdf-page" if all(c.get("pdf_page") == c.get("page_start")
                                         for _, c in flatten(toc)) else "printed"
            require(flatten(toc), "empty chapter list")
            require(not provenance["unresolved"], f"unresolved bookmark destinations: {provenance['unresolved']}")
            if args.proposal:
                proposal = toc | {"book_id": args.book, "pdf_identity": session.identity,
                                  "kind": provenance["kind"], "unit": unit, "provenance": provenance}
                from toc_reexport import atomic_write
                atomic_write(logs / f"{args.book}-toc-proposal.json", json.dumps(proposal, indent=2, ensure_ascii=False) + "\n")
            toc = keep_flat_groups(toc, previous)
            keys = [key(p, c) for p, c in flatten(toc)]
            require(len(set(keys)) == len(keys), "duplicate chapter identities")
            proofs, unresolved = verify_targets(session, toc, print)
            reader_data = supplied or {"pdf_identity": session.identity}
            if observations:
                require(observations["pdf_identity"] == session.identity, "saved observations belong to a different PDF")
                reader_data = reader_data | {"opener_evidence": observations["opener_evidence"]}
            accepted, unresolved = reader_proofs(reader_data, unresolved, logs)
            proofs.extend(accepted)
            print(f"{args.book}: {len(toc['provinces'])} provinces; {len(keys)} chapters; unit={unit}; "
                  f"targets={len(proofs)} confirmed/{len(unresolved)} ambiguous; source={provenance['kind']}")
            for row in unresolved:
                print(f"  ch{row['number']} PDF {row['pdf_page']}: {row['reason']}")
            print(f"Selected-page extraction: {session.extracted} new; {session.hits} cached; model calls=0")
            if args.cache:
                session.save_cache()
            require(not unresolved, "ambiguous targets remain; use saved free-reader observations, then retry")
            if supplied and unit == "printed":
                verify_source_folios(session, toc, reader_data, logs)
            mapping = {"unit": unit, "uniform_offset": 0 if unit == "pdf-page" else book.get("page_offset")}
            end, boundary = final_boundary(book, toc, old, mapping, pdf, args.check_index)
            if args.document_end:
                from page_offset import folded
                import re
                require(unit == "pdf-page", "document-end proof is PDF-unit only; printed extrapolation is an estimate")
                last = flatten(toc)[-1][1]
                tail = " ".join(session.text(book["page_count_images"]).splitlines()[:12])
                require(folded(last["title"]) in folded(tail) and re.search(
                    rf"\b(?:chapter\s+)?{re.escape(str(last['number']))}(?![\w.])", tail, re.I),
                    "document end does not clearly name the final chapter; keep the median estimate")
                end = book["page_count_images"]
                boundary = {"mode": "verified-document-end", "note": f"final PDF page {end} names the last chapter; not a printed/index proof"}
            # Reuse only a proof bound to the exact current export/source/PDF.
            prior_proof = document(originals[paths["toc-proof"]])
            if not args.outline and not supplied and end is None and prior_proof.get("pdf_identity") == session.identity:
                if prior_proof.get("export_hash") == digest(originals[paths["toc"]] or ""):
                    end, boundary = prior_proof.get("last_page"), prior_proof["boundary"]
            fill_ranges(toc, end, book["page_count_images"] if unit == "pdf-page" else None)
            list_changed = list_identity(previous) != list_identity(toc)
            changed = list_identity(old) != list_identity(toc)
            # Existing checks/range fixes never discard accepted reader evidence.
            retire = [paths["eyes"], legacy_cache] if (changed or list_changed) and (args.outline or supplied) else []
            if list_changed and (args.outline or supplied):
                retire.append(legacy_cache)
            source_toc = toc if args.outline or supplied else previous
            source_payload = json.dumps(source_toc, indent=1, ensure_ascii=False)
            export_payload = json.dumps(toc, indent=1, ensure_ascii=False)
            # Preserve exact bytes when the documents already agree.
            if document(originals[paths["vis-toc"]]) == source_toc:
                source_payload = originals[paths["vis-toc"]]
            if document(originals[paths["toc"]]) == toc:
                export_payload = originals[paths["toc"]]
            report = {"book": args.book, "unit": unit, "provenance": provenance,
                      "pdf_identity": session.identity, "proofs": proofs,
                      "source_hash": digest(source_payload), "export_hash": digest(export_payload),
                      "boundary": boundary, "last_page": flatten(toc)[-1][1]["page_end"],
                      "limitation": "PDF targets do not prove printed folios or completeness of the PDF; bookmarks may omit chapters"}
            payloads = {paths["toc"]: export_payload,
                        paths["toc-proof"]: json.dumps(report, indent=2, ensure_ascii=False) + "\n"}
            if args.outline or supplied:
                payloads[paths["vis-toc"]] = source_payload
            print(f"Final boundary: {boundary['mode']}; {boundary['note']}; list changed={changed}")
            print(f"Before/after: {len(flatten(old))}/{len(keys)} chapters; "
                  f"{len(old['provinces'])}/{len(toc['provinces'])} provinces; "
                  f"pages ({unit}) {flatten(toc)[0][1]['page_start']}-{flatten(toc)[-1][1]['page_end']}; "
                  f"configured printed offset={book.get('page_offset')}")
            if not args.apply:
                print("Dry run; source/export/configuration/receipts unchanged")
                return 0
            require(pdf_identity(pdf) == session.identity, "PDF changed during verification")
            require(not args.source or args.source.read_text() == supplied_text, "checked source changed")
            require(not args.observations or args.observations.read_text() == observations_text, "saved observations changed")
            # Invalidate only this book's old arithmetic receipt; keep its history.
            status = json.loads(originals[status_path]) if originals[status_path] else {"books": {}}
            prior = status["books"].get(args.book)
            if prior and (changed or payloads[paths["toc"]] != originals[paths["toc"]]):
                record = copy.deepcopy(prior)
                record["state"] = "needs-range-receipt"
                record["previous_receipt"] = prior
                status["books"][args.book] = record
                payloads[status_path] = json.dumps(status, indent=2, ensure_ascii=False) + "\n"
            backup = save_bundle(ROOT, logs, args.book, "chapter-list/target-check", originals, payloads, retire)
            print(f"Saved; backup: {backup}" if backup else "Already current; no writes")
            print("Book acceptance/page_offset unchanged; run the one-book range dry run next")
            return 0
    except (ValueError, KeyError, TypeError, OSError) as exc:
        print(f"NOT APPLIED: {args.book}: {exc}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    sys.exit(main())
