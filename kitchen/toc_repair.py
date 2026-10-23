#!/usr/bin/env python3
"""Generic saved-TOC range repair. No AI, rendering, DB or global offset needed.

  python kitchen/toc_repair.py --audit                  # all books, metadata only
  python kitchen/toc_repair.py BOOK_ID --check-index    # one-book dry run
  python kitchen/toc_repair.py --next --check-index --apply
  python kitchen/toc_repair.py --summary                # consolidated review

--next resumes the queue; failed books are recorded and skipped on the next
invocation. Each invocation applies at most ONE book. Keep the SAME cheap
manager throughout; collect exceptions for one review after the queue.
"""

import argparse
import copy
import hashlib
import json
import sys
from datetime import datetime
from pathlib import Path

from page_offset import flatten, positive_integer, require
from toc_ranges import fill_ranges
from toc_reexport import atomic_write
from toc_repair_source import accepted_source, final_boundary, flat_identity

ROOT = Path(__file__).resolve().parents[1]
KITCHEN = ROOT / "kitchen"
LOGS = KITCHEN / "logs"
STATUS = ROOT / "TOC-REPAIR-STATUS.json"


def digest(text):
    return hashlib.sha256(text.encode()).hexdigest()


def plan(book, check_index=False):
    bid = book["book_id"]
    paths = {s: LOGS / f"{bid}-{s}.json" for s in ("vis-toc", "toc", "eyes")}
    originals = {p: p.read_text() for p in paths.values() if p.is_file()}
    require(paths["vis-toc"] in originals, "accepted vis-toc missing")
    source = json.loads(originals[paths["vis-toc"]])
    old = json.loads(originals.get(paths["toc"], '{"provinces":[]}'))
    eyes = json.loads(originals[paths["eyes"]]) if paths["eyes"] in originals else None
    toc, updated, mapping, images, issues = accepted_source(
        book, source, old, eyes, LOGS / "eyes-render" / bid)
    identity = flat_identity(toc)
    end, boundary = final_boundary(book, toc, old, mapping,
                                   KITCHEN / "books" / book["pdf_file"], check_index)
    if end is None and mapping.get("structure_preserved"):
        # Minimal-change rule: an unproved tail does not justify rewriting
        # the accepted export's own final number.
        last = flatten(toc)[-1][1]
        have = flatten(old)[-1][1].get("page_end")
        if positive_integer(have) and have >= last["page_start"]:
            end, boundary = have, {"mode": "kept-existing",
                                   "note": "kept the accepted export's final end; index boundary not verified"}
    fill_ranges(toc, end)
    require(flat_identity(toc) == identity, "range calculation changed chapter starts/identity")
    expected = copy.deepcopy(toc)
    fill_ranges(expected, flatten(toc)[-1][1]["page_end"])
    require(expected == toc, "range verification failed")
    before = {(p, str(c.get("number")), c.get("title")): c for p, c in flatten(old)}
    changed = sum(before.get((p, str(c.get("number")), c.get("title")), {}).get("page_end")
                  != c["page_end"] for p, c in flatten(toc))
    payloads = {paths["toc"]: json.dumps(toc, indent=1, ensure_ascii=False)}
    if updated is not None and updated != eyes:
        payloads[paths["eyes"]] = json.dumps(updated, indent=1)
    report = {"book": bid, "state": "ready", "source": mapping["source"],
              "provinces": len(toc["provinces"]), "chapters": len(identity),
              "previous_chapters": len(flatten(old)), "unit": mapping["unit"],
              "first_page": flatten(toc)[0][1]["page_start"],
              "last_page": flatten(toc)[-1][1]["page_end"],
              "changed_ends": changed, "image_changes": images, "image_issues": issues,
              "structure": "preserved" if mapping.get("structure_preserved") else "rebuilt",
              "offset_values": mapping["offset_values"], "boundary": boundary,
              "starts_preserved_from": mapping["source"], "config_hash": digest(json.dumps(book, sort_keys=True))}
    return report, originals, payloads


def current(record, book):
    if not record or record.get("state") == "blocked":
        return bool(record and record.get("state") == "blocked")
    if record.get("config_hash") != digest(json.dumps(book, sort_keys=True)):
        return False
    if any((ROOT / p).exists() for p in record.get("absent", [])):
        return False
    files = record.get("files", {})
    return bool(files) and all((ROOT / p).is_file() and digest((ROOT / p).read_text()) == h
                               for p, h in files.items())


def same_document(before, after):
    try:
        return json.loads(before) == json.loads(after)
    except (TypeError, json.JSONDecodeError):
        return False


def apply_plan(book, report, originals, payloads):
    require(all(p.read_text() == text for p, text in originals.items()), "inputs changed during verification")
    changed = {p: text for p, text in payloads.items()
               if p not in originals or not same_document(originals[p], text)}
    report = copy.deepcopy(report)
    if changed:
        backup = LOGS / "toc-repair-backups" / book["book_id"] / datetime.now().strftime("%Y%m%dT%H%M%S%f")
        backup.mkdir(parents=True)
        for path, text in originals.items():
            (backup / path.name).write_text(text)
        (backup / "books.json").write_text((KITCHEN / "books.json").read_text())
        report["backup"] = str(backup.relative_to(ROOT))
        report["created_files"] = [str(p.relative_to(ROOT)) for p in changed if p not in originals]
        for path, text in changed.items():
            atomic_write(path, text)
    report["state"] = "applied"
    report["files"] = {str(p.relative_to(ROOT)): digest(p.read_text()) for p in originals.keys() | payloads.keys()}
    report["absent"] = [str((LOGS / f"{book['book_id']}-{suffix}.json").relative_to(ROOT))
                        for suffix in ("eyes",) if not (LOGS / f"{book['book_id']}-{suffix}.json").exists()]
    report["saved_files"] = len(changed)
    report["time"] = datetime.now().isoformat(timespec="seconds")
    return report


def show(report):
    if report["state"] == "blocked":
        print(f"{report['book']}: BLOCKED: {report['error']}")
        return
    print(f"{report['book']}: {report['state']}; {report['chapters']} chapters; "
          f"{report['changed_ends']} ends; {report['unit']}; {report['source']}; "
          f"final={report['boundary']['mode']}; images={len(report['image_changes'])} repaired/"
          f"{len(report['image_issues'])} issues")
    if report.get("backup"):
        print(f"  backup: {report['backup']}")
    if report["boundary"]["mode"] == "median-fallback":
        print(f"  final boundary provisional: {report['boundary']['note']}")
    for issue in report["image_issues"]:
        print(f"  {issue}")


def summary(status, books):
    records = status["books"]
    applied = [r for r in records.values() if r["state"] == "applied"]
    blocked = [r for r in records.values() if r["state"] == "blocked"]
    pending = [b["book_id"] for b in books if not current(records.get(b["book_id"]), b)]
    verified = {"verified-index", "verified-tail-folios", "saved-index-boundary"}
    provisional = [r for r in applied if r["boundary"]["mode"] not in verified]
    print(f"Queue: {len(applied)} applied; {len(blocked)} blocked; {len(pending)} pending/stale")
    print(f"Final boundaries: {len(applied) - len(provisional)} index/tail proved; {len(provisional)} provisional (existing or median)")
    print(f"Image issues: {sum(len(r['image_issues']) for r in applied)}; "
          f"variable-offset books preserved: {sum(r['offset_values'] > 1 for r in applied)}")
    for r in blocked:
        print(f"BLOCKED {r['book']}: {r['error']}")
    for r in applied:
        for issue in r["image_issues"]:
            print(f"IMAGE {r['book']}: {issue}")
    for r in provisional:
        print(f"FINAL {r['book']}: {r['boundary']['note']}")
    if pending:
        print("Pending: " + ", ".join(pending))


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    targets = parser.add_mutually_exclusive_group(required=True)
    targets.add_argument("book", nargs="?")
    targets.add_argument("--audit", action="store_true", help="read-only readiness check; never opens PDFs")
    targets.add_argument("--next", action="store_true", help="next book not recorded as completed/blocked")
    targets.add_argument("--summary", action="store_true", help="one consolidated status and exceptions list")
    parser.add_argument("--apply", action="store_true")
    parser.add_argument("--check-index", action="store_true", help="optional bounded tail-page checks for one book")
    args = parser.parse_args(argv)
    require(not args.audit or not (args.apply or args.check_index), "--audit is metadata-only and read-only")
    require(not args.summary or not (args.apply or args.check_index), "--summary is read-only")
    books_text = (KITCHEN / "books.json").read_text()
    books = sorted(json.loads(books_text), key=lambda b: b["book_id"])
    status = json.loads(STATUS.read_text()) if STATUS.exists() else {"purpose": "range-repair run receipts, not a database export", "books": {}}
    if args.summary:
        summary(status, books)
        return 0
    if args.audit:
        targets = books
    elif args.next:
        targets = [b for b in books if not current(status["books"].get(b["book_id"]), b)][:1]
    else:
        targets = [b for b in books if b["book_id"] == args.book]
        require(len(targets) == 1, "unknown book ID")
    if not targets:
        print("Queue finished: return the ONE consolidated status file for SMART review")
        return 0
    passed = blocked = 0
    for book in targets:
        try:
            report, originals, payloads = plan(book, args.check_index)
            if args.apply:
                require((KITCHEN / "books.json").read_text() == books_text, "books.json changed during verification")
                report = apply_plan(book, report, originals, payloads)
            passed += 1
        except (ValueError, KeyError, TypeError, OSError) as exc:
            report = {"book": book["book_id"], "state": "blocked", "error": str(exc)}
            blocked += 1
        show(report)
        if args.apply:
            status["books"][book["book_id"]] = report
            atomic_write(STATUS, json.dumps(status, indent=2, ensure_ascii=False) + "\n")
    if args.audit:
        print(f"Read-only readiness: {passed}/{len(targets)} books repairable; {blocked} blocked; no PDFs/models/writes")
    elif not args.apply:
        print("Dry run; no files written")
    return 1 if blocked else 0


if __name__ == "__main__":
    sys.exit(main())
