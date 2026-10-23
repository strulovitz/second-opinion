"""Shared local state and input identity for the BIBLE 3.7 scripts."""

import argparse
import fcntl
import hashlib
import json
import re
from contextlib import contextmanager
from datetime import datetime
from pathlib import Path

from toc_reexport import atomic_write

ROOT = Path(__file__).resolve().parents[1]
GROUPS = ("symptoms-and-signs", "diseases-and-conditions", "treatments-and-drugs")


def require(condition, message):
    if not condition:
        raise ValueError(message)


def fingerprint(value):
    return hashlib.sha256(json.dumps(value, sort_keys=True, ensure_ascii=False).encode()).hexdigest()


def save(path, value):
    path.parent.mkdir(parents=True, exist_ok=True)
    atomic_write(path, json.dumps(value, indent=1, ensure_ascii=False) + "\n")


def rows(path):
    if not path.exists():
        return []
    return [json.loads(line) for line in path.read_text().splitlines() if line.strip()]


def save_rows(path, records):
    atomic_write(path, "".join(json.dumps(r, ensure_ascii=False) + "\n" for r in records))


@contextmanager
def lock(path):
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("a") as stream:
        try:
            fcntl.flock(stream, fcntl.LOCK_EX | fcntl.LOCK_NB)
        except BlockingIOError:
            raise ValueError("another index operation holds the lock; wait for it to finish") from None
        try:
            yield
        finally:
            fcntl.flock(stream, fcntl.LOCK_UN)


def arguments(description):
    parser = argparse.ArgumentParser(description=description)
    parser.add_argument("book")
    parser.add_argument("--books", type=Path, default=ROOT / "kitchen/books.json")
    parser.add_argument("--logs", type=Path, default=ROOT / "kitchen/logs")
    parser.add_argument("--geography", type=Path, default=ROOT / "data/export/geography/geography.json")
    parser.add_argument("--limit", type=int, default=0, help="maximum NEW units this invocation; 0 = the whole book")
    parser.add_argument("--plan", action="store_true", help="metadata only, no PDF/model/database calls or writes")
    parser.add_argument("--fallback", action="store_true", help="BIBLE 3.7.9: confirmed unusable index; existing titles/opener pages instead")
    return parser


class Context:
    def __init__(self, args):
        self.args, self.root, self.logs = args, ROOT, args.logs
        self.books = json.loads(args.books.read_text())
        matches = [b for b in self.books if b["book_id"] == args.book]
        require(len(matches) == 1, "unknown/duplicate book ID")
        self.book, self.bid = matches[0], args.book
        require(self.book.get("status") in ("accepted", "geography-done", "index-done"), "book not accepted")
        index = self.book.get("index_images")
        self.fallback = getattr(args, "fallback", False)
        valid_index = isinstance(index, list) and len(index) == 2 and all(type(n) is int for n in index) and 0 < index[0] <= index[1] <= self.book["page_count_images"]
        require(valid_index or self.fallback, "no usable index range; locate the real index first, or use --fallback only after confirming BIBLE 3.7.9 applies")
        require(args.limit >= 0, "limit cannot be negative")
        self.pages = list(range(index[0], index[1] + 1)) if valid_index else []
        self.pdf = ROOT / "kitchen/books" / self.book["pdf_file"]
        self.geography = json.loads(args.geography.read_text())
        self.districts = [t for t in self.geography if t["book_id"] == self.bid and t["level"] == "district"]
        require(self.districts, "book has no geography districts")
        self.identity = fingerprint({"book": self.book, "geography": self.geography,
                                     **({"mode": "chapter-fallback"} if self.fallback else {})})

    def path(self, suffix):
        return self.logs / f"{self.bid}-{suffix}"

    def image(self, page):
        directory = Path(self.book["image_dir"])
        directory = directory if directory.is_absolute() else ROOT / directory
        return directory / self.book["image_name_pattern"].format(n=page)

    def summary(self, stage, **values):
        text = f"{self.bid} {stage}: " + "; ".join(f"{k}={v}" for k, v in values.items())
        print(text, flush=True)
        with self.path("run.log").open("a") as stream:
            stream.write(datetime.now().isoformat(timespec="seconds") + " " + text + "\n")

    def plan(self, stage):
        if self.fallback:
            print(f"{self.bid} {stage}: explicit chapter/opener fallback; {len(self.districts)} districts; read-only plan")
            return
        print(f"{self.bid} {stage}: index PDF {self.pages[0]}-{self.pages[-1]}; "
              f"{len(self.pages)} pages; {len(self.districts)} districts; limit={self.args.limit}; read-only plan")

    def execution_guard(self):
        if self.bid == "HARRISON-22":
            return
        accepted = [b for b in self.books if b["status"] in ("accepted", "geography-done", "index-done")]
        order = sorted(accepted, key=lambda b: (b["book_id"] != "HARRISON-22", b["book_id"]))
        for previous in order[:next(i for i, b in enumerate(order) if b["book_id"] == self.bid)]:
            bid = previous["book_id"]
            approval, status_path = self.logs / f"{bid}-index-review-approved.json", self.logs / f"{bid}-index-status.json"
            require(approval.exists() and status_path.exists(), f"{bid} registry review must be approved before {self.bid}")
            decision, status = json.loads(approval.read_text()), json.loads(status_path.read_text())
            expected = {"book": previous, "geography": self.geography,
                        **({"mode": "chapter-fallback"} if status.get("mode") == "chapter-fallback" else {})}
            require(status["complete"] and status["input_identity"] == fingerprint(expected)
                    and decision["status_hash"] == fingerprint(status), f"{bid} review approval is stale")
            review = self.logs / f"{bid}-review.md"
            require(review.exists() and decision["review_hash"] == fingerprint(review.read_text()), f"{bid} review text changed after approval")


def ask_checked(ask, prompt, payload, validator, **kwargs):
    error = ""
    for _ in range(2):
        try:
            result = ask(prompt, (payload if isinstance(payload, str) else json.dumps(payload, ensure_ascii=False)) + error,
                         retries=1, **kwargs)
            return validator(result)
        except (ValueError, KeyError, TypeError, RuntimeError) as exc:
            error = "\nThe previous answer failed validation: " + str(exc) + ". Fix it using only the source."
    raise ValueError("reader failed validation twice: " + error)


def reader_access():
    from reader import ask
    from db import env
    return ask, env("READER_MODEL"), env("READER_VISION_MODEL")


def classification_terms(entries, districts):
    names = {d["territory_id"]: d["name"] for d in districts}
    terms = {}
    for entry in entries:
        if entry.get("see"):
            continue
        term = terms.setdefault(entry["display"], {"display": entry["display"], "subentries": [], "context_districts": []})
        for sub in entry["subentries"]:
            if sub["text"] not in term["subentries"]:
                term["subentries"].append(sub["text"])
        for ref in entry["references"]:
            for did in ref["district_ids"]:
                if names[did] not in term["context_districts"]:
                    term["context_districts"].append(names[did])
    return [t | {"subentries": t["subentries"][:6], "context_districts": t["context_districts"][:5]} for t in terms.values()]


def validate_classification(result, terms):
    result = result["results"]
    require(len(result) == len(terms) and {r["display"] for r in result} == {t["display"] for t in terms}, "missing, duplicate or invented classification terms")
    for row in result:
        require(row["group"] in GROUPS + ("not-an-entity",), "invalid group")
        require(type(row["confidence"]) in (int, float) and 0 <= row["confidence"] <= 1, "invalid confidence")
        require(isinstance(row["reason"], str) and len(row["reason"].split()) <= 12, "invalid classification reason")
    return result


def cli(main):
    import sys
    try:
        return main()
    except KeyboardInterrupt:
        print("Stopped; completed index units remain saved", file=sys.stderr)
        return 130
    except Exception as exc:
        print(f"INDEX STOPPED: {type(exc).__name__}: {exc}", file=sys.stderr)
        return 1
    finally:
        database = sys.modules.get("db")
        if database is not None:
            database._driver.close()
