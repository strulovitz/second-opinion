"""Synthetic index evidence and fake-DB failure tests, never a book audit."""

import contextlib
import copy
import hashlib
import io
import json
import tempfile
import unittest
from pathlib import Path
from types import SimpleNamespace
from unittest.mock import Mock, patch

from PIL import Image

import index_classify
import index_common
import index_extract
import index_fallback
import index_parse
import index_resolve
from index_common import Context, fingerprint, save, validate_classification
from index_pages import assemble, expand_reference, ground_entries, map_page
from index_registry import CATALOG, Registry, validate_resolution
from test_toc_tools import make_pdf
from toc_evidence import pdf_identity


class FakeDatabase:
    """Test double only. Production uses the existing Neo4j db.run helper."""
    def __init__(self, districts):
        self.entities, self.spots = {}, set()
        self.districts, self.frozen = districts, False
        self.writes = 0
        self.fulltext = []

    def run(self, query, **p):
        if "RETURN m.value AS value" in query:
            return [{"value": "true" if self.frozen else "false"}]
        if "RETURN d.territory_id AS id" in query:
            return [{"id": d["territory_id"]} for d in self.districts]
        if query == CATALOG:
            return copy.deepcopy(list(self.entities.values()))
        if "RETURN e.slug AS slug, d.territory_id AS did" in query:
            return [{"slug": slug, "did": did, "page": page, "source": source} for slug, did, page, source in self.spots]
        if "queryNodes" in query:
            return self.fulltext
        if "MERGE (e:Entity" in query:
            if self.frozen:
                return []
            self.writes += 1
            e = self.entities.setdefault(p["slug"], {"slug": p["slug"], "canonical_name": p["name"],
                "group": p["group"], "aliases": [], "lit_spot_books": []})
            e["aliases"] = list(dict.fromkeys(e["aliases"] + p["aliases"]))
            e["lit_spot_books"] = list(dict.fromkeys(e["lit_spot_books"] + [p["bid"]]))
            self.spots.update((p["slug"], s["did"], s["page"], s["source"]) for s in p["spots"])
            self.last_query = query
            return [{"slug": p["slug"], "spots": len(p["spots"])}]
        if "SET e.aliases=CASE" in query:
            self.entities[p["slug"]]["aliases"].append(p["alias"])
            return [{"slug": p["slug"]}]
        if "SET b.status='index-done'" in query:
            return [{"book_id": p["bid"]}]
        raise AssertionError(query)


class ReferenceTests(unittest.TestCase):
    def test_numeric_refs_suffixes_abbreviations_and_range_cap(self):
        self.assertEqual(expand_reference("1234t"), ([1234], None))
        self.assertEqual(expand_reference("1234–36"), ([1234, 1235, 1236], None))
        self.assertEqual(expand_reference("1-30"), (list(range(1, 31)), None))
        self.assertEqual(expand_reference("1-31"), ([1, 31], None))
        self.assertEqual(expand_reference("e12"), ([], "online-only"))
        self.assertEqual(expand_reference("4536.e5"), ([], "non-integer-or-malformed"))
        with self.assertRaises(ValueError):
            expand_reference("900-800")

    def test_reader_cannot_invent_headwords_subentries_or_refs(self):
        row = {"headword": "Alpha", "display": "Alpha", "see": None, "pages": ["12"], "subentries": []}
        self.assertEqual(ground_entries({"entries": [row]}, "Alpha, 12\n", 3, "3.png")[0]["quote"], "Alpha, 12")
        for bad in (row | {"headword": "Invented"}, row | {"pages": ["99"]},
                    row | {"subentries": [{"text": "Invented", "pages": []}]}):
            with self.assertRaises(ValueError):
                ground_entries({"entries": [bad]}, "Alpha, 12\n", 3, "3.png")

    def test_invalid_classifier_and_resolution_answers_cannot_enter_registry(self):
        terms = [{"display": "Alpha"}]
        for result in ({"results": []}, {"results": [{"display": "Alpha", "group": "made-up", "confidence": 1, "reason": "x"}]}):
            with self.assertRaises(ValueError):
                validate_classification(result, terms)
        with self.assertRaisesRegex(ValueError, "invented candidate"):
            validate_resolution({"decision": "SAME", "candidate_slug": "not-real", "confidence": 1, "reason": "same"}, [])


class PipelineTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)
        self.logs = self.root / "kitchen/logs"
        self.logs.mkdir(parents=True)
        (self.root / "kitchen/books").mkdir()
        self.pdf = self.root / "kitchen/books/test.pdf"
        make_pdf(self.pdf, ["Body", "Body", "Alpha, 2\nBeta, 12", "Other, 13"])
        self.images = self.root / "images"
        self.images.mkdir()
        for page in (3, 4):
            Image.new("RGB", (20, 20), "white").save(self.images / f"page-{page:04d}.png")
        self.book = {"book_id": "HARRISON-22", "title": "Synthetic Book", "pdf_file": "test.pdf",
                     "status": "accepted", "index_images": [3, 4], "page_count_images": 100,
                     "image_dir": str(self.images), "image_name_pattern": "page-{n:04d}.png", "page_offset": None}
        self.books = self.root / "books.json"
        self.books.write_text(json.dumps([self.book]))
        self.geography = self.root / "geography.json"
        self.districts = [{"territory_id": f"C01.P01.D00{i}", "book_id": "HARRISON-22", "name": f"District {i}",
                           "level": "district", "page_start": (i - 1) * 10 + 1, "page_end": i * 10} for i in (1, 2)]
        self.geography.write_text(json.dumps(self.districts))
        self.patch = patch.object(index_common, "ROOT", self.root)
        self.patch.start()
        self.addCleanup(self.patch.stop)
        self.args = SimpleNamespace(book="HARRISON-22", books=self.books, geography=self.geography, logs=self.logs,
                                    limit=0, plan=False)
        self.ctx = Context(self.args)
        save(self.ctx.path("vis-toc.json"), {"provinces": [{"chapters": [{"page_start": 1}]}]})
        self.reader = Mock()
        self.db = FakeDatabase(self.districts)

    def quiet(self):
        return contextlib.redirect_stdout(io.StringIO())

    def source(self, page, text):
        self.ctx.path(f"index-{page}.txt").write_text(text)
        save(self.ctx.path(f"index-{page}-source.json"), {"key": "fixture", "text_hash": fingerprint(text),
            "pdf_identity": pdf_identity(self.pdf), "image_hash": hashlib.sha256(self.ctx.image(page).read_bytes()).hexdigest()})

    def parsed(self):
        text = "Alpha, 2\n  detail, 12\nBeta, 12\n"
        rows = [{"headword": "Alpha", "display": "Alpha", "pages": ["2"], "see": None,
                 "subentries": [{"text": "detail", "pages": ["12"]}]},
                {"headword": "Beta", "display": "Beta", "pages": ["12"], "see": None, "subentries": []}]
        grounded = ground_entries({"entries": rows}, text, 3, str(self.ctx.image(3)))
        entries, counts = assemble([grounded], self.ctx, "printed")
        parsed = {"input_identity": self.ctx.identity, "entries": entries, "reference_counts": counts,
                  "complete": True, "pages_parsed": 2}
        save(self.ctx.path("index-entries.json"), parsed)
        self.reader.side_effect = lambda prompt, payload, **kw: {"results": [
            {"display": r["display"], "group": "diseases-and-conditions", "confidence": 1.0, "reason": "synthetic fixture"}
            for r in json.loads(payload)]}
        with self.quiet():
            index_classify.classify(self.ctx, self.reader, "fixture-reader")
        self.reader.reset_mock()
        return parsed

    def test_extraction_resumes_without_reopening_completed_pages(self):
        def text(command, **kwargs):
            page = int(command[command.index("-f") + 1])
            return SimpleNamespace(stdout=f"Term, {page}\n")
        with patch.object(index_extract.subprocess, "run", side_effect=text) as calls, self.quiet():
            index_extract.extract(self.ctx)
            self.assertEqual(calls.call_count, 2)
            index_extract.extract(self.ctx)
            self.assertEqual(calls.call_count, 2)
        self.assertTrue(self.ctx.path("index-4-source.json").exists())

    def test_continuation_keeps_the_actual_proving_page_and_raw_line(self):
        first = ground_entries({"entries": [{"headword": "Alpha", "display": "Alpha", "see": None,
                    "pages": ["2"], "subentries": []}]}, "Alpha, 2", 3, "3.png")
        second = ground_entries({"entries": [{"headword": "CONTINUED", "display": "CONTINUED", "see": None,
                    "pages": [], "subentries": [{"text": "detail", "pages": ["12"]}]}]}, "detail, 12", 4, "4.png")
        entries, counts = assemble([first, second], self.ctx, "printed")
        self.assertEqual(len(entries), 1)
        ref = entries[0]["references"][-1]
        self.assertEqual((ref["printed_page"], ref["image_file"], ref["quote"]), (12, "4.png", "detail, 12"))
        self.assertEqual(ref["district_ids"], ["C01.P01.D002"])
        self.assertEqual(counts["mapping-unresolved"], 0)
        with self.assertRaisesRegex(ValueError, "orphan"):
            assemble([second], self.ctx, "printed")

    def test_unknown_pdf_to_printed_mapping_is_not_a_zero_offset(self):
        ids, issue = map_page(12, self.ctx, "pdf-page")
        self.assertEqual((ids, issue), ([], "mapping-unresolved"))
        self.book["page_offset"] = 2
        self.books.write_text(json.dumps([self.book]))
        ids, issue = map_page(9, Context(self.args), "pdf-page")
        self.assertEqual(ids, ["C01.P01.D002"])

    def test_parse_retries_semantic_error_once_then_reuses_page_cache(self):
        # Ensure the normal text parser is exercised, not OCR.
        text = "Alpha, 2\n" + "Index source footer information\n"
        self.source(3, text)
        self.args.limit = 1
        row = {"headword": "Alpha", "display": "Alpha", "see": None, "pages": ["2"], "subentries": []}
        self.reader.side_effect = [{"entries": [row | {"pages": ["99"]}]}, {"entries": [row]}]
        with self.quiet():
            result = index_parse.parse(self.ctx, self.reader, "fixture-reader", "fixture-vision")
        self.assertEqual(self.reader.call_count, 2)
        self.assertFalse(result["complete"])
        self.reader.reset_mock()
        with self.quiet():
            index_parse.parse(self.ctx, self.reader, "fixture-reader", "fixture-vision")
        self.reader.assert_not_called()

    def test_classification_batches_25_and_skips_unchanged_terms(self):
        parsed = self.parsed()
        for i in range(26):
            parsed["entries"].append(parsed["entries"][0] | {"display": f"Term {i}"})
        save(self.ctx.path("index-entries.json"), parsed)
        with self.quiet():
            index_classify.classify(self.ctx, self.reader, "fixture-reader")
        self.assertEqual([len(json.loads(call.args[1])) for call in self.reader.call_args_list], [25, 1])
        self.reader.reset_mock()
        with self.quiet():
            index_classify.classify(self.ctx, self.reader, "fixture-reader")
        self.reader.assert_not_called()

    def test_resolution_recovers_after_db_commit_before_local_receipt(self):
        self.parsed()
        actual_save = index_resolve.save_rows
        def crash(path, records):
            if path.name.endswith("resolved.jsonl"):
                raise OSError("simulated power loss after database commit")
            return actual_save(path, records)
        with patch.object(index_resolve, "save_rows", side_effect=crash), self.quiet():
            with self.assertRaisesRegex(OSError, "power loss"):
                index_resolve.resolve(self.ctx, Registry(self.db.run), self.reader, "fixture-reader")
        self.assertEqual(len(self.db.entities), 1)
        with self.quiet():
            index_resolve.resolve(self.ctx, Registry(self.db.run), self.reader, "fixture-reader")
        self.assertEqual(len(self.db.entities), 2)
        self.assertEqual(len(self.db.spots), 3)
        self.reader.assert_not_called()  # No candidates in this artificial catalog.
        before = self.db.writes
        with self.quiet():
            index_resolve.resolve(self.ctx, Registry(self.db.run), self.reader, "fixture-reader")
        self.assertEqual(self.db.writes, before)

    def test_old_receipt_does_not_claim_success_after_database_was_cleared(self):
        self.parsed()
        with self.quiet():
            index_resolve.resolve(self.ctx, Registry(self.db.run), self.reader, "fixture-reader")
        self.db.entities.clear()
        self.db.spots.clear()
        with self.quiet():
            index_resolve.resolve(self.ctx, Registry(self.db.run), self.reader, "fixture-reader")
        self.assertEqual(len(self.db.entities), 2)
        self.assertEqual(len(self.db.spots), 3)

    def test_missing_districts_and_frozen_registry_prevent_all_writes(self):
        self.parsed()
        for districts, frozen in (([], False), (self.districts, True)):
            database = FakeDatabase(districts)
            database.frozen = frozen
            with self.quiet(), self.assertRaises(ValueError):
                index_resolve.resolve(self.ctx, Registry(database.run), self.reader, "fixture-reader")
            self.assertEqual(database.writes, 0)
        self.reader.assert_not_called()

    def test_candidate_similarity_does_not_merge_without_reader(self):
        registry = Registry(self.db.run)
        registry.entities = {"diseases-and-conditions-alpha-variant": {"slug": "diseases-and-conditions-alpha-variant",
            "group": "diseases-and-conditions", "canonical_name": "Alpha variant", "aliases": [], "lit_spot_books": []}}
        ask = Mock(return_value={"decision": "NEW", "candidate_slug": None, "confidence": 0.9, "reason": "distinct fixture"})
        entry = {"display": "Alpha", "subentries": [], "context_districts": []}
        decision = index_resolve.decide(entry, {"group": "diseases-and-conditions"}, registry, ask)
        self.assertEqual(decision["how"], "new-reader")
        self.assertEqual(decision["slug"], "diseases-and-conditions-alpha")
        ask.assert_called_once()

    def test_low_confidence_same_creates_new_and_records_the_doubt(self):
        registry = Registry(self.db.run)
        candidate = {"slug": "diseases-and-conditions-alpha-variant", "group": "diseases-and-conditions",
                     "canonical_name": "Alpha variant", "aliases": [], "lit_spot_books": []}
        registry.entities[candidate["slug"]] = candidate
        ask = Mock(return_value={"decision": "SAME", "candidate_slug": candidate["slug"], "confidence": 0.4, "reason": "uncertain fixture"})
        decision = index_resolve.decide({"display": "Alpha", "subentries": []}, {"group": "diseases-and-conditions"}, registry, ask)
        self.assertTrue(decision["doubtful"])
        self.assertNotEqual(decision["slug"], candidate["slug"])

    def test_see_alias_keeps_its_source_and_retries_when_target_exists(self):
        registry = Registry(self.db.run)
        entity = {"slug": "diseases-and-conditions-alpha", "group": "diseases-and-conditions",
                  "canonical_name": "Alpha", "aliases": ["Alpha"], "lit_spot_books": []}
        self.db.entities[entity["slug"]] = entity
        registry.entities = self.db.entities
        entries = [{"headword": "Variant", "see": "Alpha", "sources": [{"quote": "Variant. See Alpha", "image_file": "3.png"}]}]
        self.assertEqual(index_resolve.retry_see(self.ctx, registry, entries), 0)
        self.assertIn("Variant", entity["aliases"])
        evidence = index_common.rows(self.ctx.path("see-aliases.jsonl"))
        self.assertEqual(evidence[0]["sources"][0]["quote"], "Variant. See Alpha")

    def test_shared_printed_page_keeps_both_districts(self):
        self.ctx.districts[0]["page_end"] = 11
        ids, issue = map_page(11, self.ctx, "printed")
        self.assertIsNone(issue)
        self.assertEqual(ids, ["C01.P01.D001", "C01.P01.D002"])

    def test_pdf_change_prevents_reusing_old_extraction_as_new_provenance(self):
        self.source(3, "Alpha, 2\nIndex source footer information\n")
        make_pdf(self.pdf, ["Changed source"] * 4)
        with self.quiet(), self.assertRaisesRegex(ValueError, "changed PDF"):
            index_parse.parse(self.ctx, self.reader, "fixture-reader", "fixture-vision")
        self.reader.assert_not_called()

    def test_group_conflict_creates_a_distinct_entity(self):
        registry = Registry(self.db.run)
        registry.entities["symptoms-and-signs-alpha"] = {"slug": "symptoms-and-signs-alpha", "canonical_name": "Alpha",
            "group": "symptoms-and-signs", "aliases": ["Alpha"], "lit_spot_books": []}
        ask = Mock()
        decision = index_resolve.decide({"display": "Alpha", "subentries": []}, {"group": "diseases-and-conditions"}, registry, ask)
        self.assertEqual(decision["how"], "group-conflict")
        self.assertEqual(decision["slug"], "diseases-and-conditions-alpha")
        ask.assert_not_called()

    def test_unmapped_references_stop_before_any_registry_writes(self):
        parsed = self.parsed()
        parsed["reference_counts"]["mapping-unresolved"] = 1
        save(self.ctx.path("index-entries.json"), parsed)
        with self.quiet(), self.assertRaisesRegex(ValueError, "mapping is unresolved"):
            index_resolve.resolve(self.ctx, Registry(self.db.run), self.reader, "fixture-reader")
        self.assertEqual(self.db.writes, 0)
        parsed["reference_counts"]["mapping-unresolved"] = 0
        parsed["complete"] = False
        save(self.ctx.path("index-entries.json"), parsed)
        with self.quiet(), self.assertRaisesRegex(ValueError, "complete the source parsing"):
            index_resolve.resolve(self.ctx, Registry(self.db.run), self.reader, "fixture-reader")
        self.assertEqual(self.db.writes, 0)

    def test_complete_synthetic_pipeline_and_second_run_are_resumable(self):
        from index_prompts import PARSE, CLASSIFY
        def extract(command, **kwargs):
            page = int(command[command.index("-f") + 1])
            term, ref = ("Alpha", "2") if page == 3 else ("Beta", "12")
            return SimpleNamespace(stdout=f"{term}, {ref}\nIndex source footer information\n")
        def reader(prompt, payload, **kwargs):
            if prompt == PARSE:
                term, ref = ("Alpha", "2") if payload.startswith("Alpha") else ("Beta", "12")
                return {"entries": [{"headword": term, "display": term, "see": None, "pages": [ref], "subentries": []}]}
            if prompt == CLASSIFY:
                return {"results": [{"display": r["display"], "group": "diseases-and-conditions",
                                     "confidence": 1.0, "reason": "synthetic fixture"} for r in json.loads(payload)]}
            raise AssertionError("unexpected entity-resolution reader call")
        ask = Mock(side_effect=reader)
        with patch.object(index_extract.subprocess, "run", side_effect=extract), self.quiet():
            for _ in range(2):
                index_extract.extract(self.ctx)
                parsed = index_parse.parse(self.ctx, ask, "fixture-reader", "fixture-vision")
                index_classify.classify(self.ctx, ask, "fixture-reader")
                index_resolve.resolve(self.ctx, Registry(self.db.run), ask, "fixture-reader")
        self.assertTrue(parsed["complete"])
        self.assertEqual(ask.call_count, 3)
        self.assertEqual(self.db.writes, 2)
        self.assertEqual(len(self.db.spots), 2)
        self.assertTrue(json.loads(self.ctx.path("index-status.json").read_text())["complete"])

    def fallback_fixture(self, pdf_units=False):
        make_pdf(self.pdf, ["Alpha Title\nAlpha term\nSource explanation footer\n1",
                            "Beta Title\nBeta term\nSource explanation footer\n11"])
        self.book["index_images"] = None
        self.books.write_text(json.dumps([self.book]))
        self.args.fallback = True
        self.ctx = Context(self.args)
        for page in (1, 2):
            Image.new("RGB", (20, 20), "white").save(self.ctx.image(page))
        chapters = [{"number": str(i + 1), "title": title, "page_start": i * 10 + 1, "pdf_page": i + 1}
                    for i, title in enumerate(("Alpha Title", "Beta Title"))]
        save(self.ctx.path("toc.json"), {"provinces": [{"name": "Part I", "chapters": chapters}]})
        if pdf_units:
            for chapter in chapters:
                chapter["_page_source"] = "pdf-outline"
                chapter["page_start"] = chapter["pdf_page"]
        save(self.ctx.path("vis-toc.json"), {"provinces": [{"name": "Part I", "chapters": chapters}]})

    def test_explicit_no_index_fallback_uses_existing_openers_and_keeps_page_provenance(self):
        self.fallback_fixture()
        def read(prompt, text, **kwargs):
            return {"terms": ["Alpha term" if text.startswith("Alpha") else "Beta term"], "printed_page": None, "text": ""}
        ask = Mock(side_effect=read)
        with self.quiet():
            result = index_fallback.fallback(self.ctx, ask, "fixture-reader", "fixture-vision")
            again = index_fallback.fallback(self.ctx, ask, "fixture-reader", "fixture-vision")
        self.assertTrue(result["complete"])
        self.assertEqual(len(result["entries"]), 4)
        self.assertEqual(ask.call_count, 2)
        self.assertEqual(result, again)
        self.assertTrue(all(r["source"] == "page" for e in result["entries"] for r in e["references"]))
        self.assertEqual(result["reference_counts"]["mapping-unresolved"], 0)

    def test_fallback_keeps_unreadable_printed_folios_unknown(self):
        self.fallback_fixture(pdf_units=True)
        ask = Mock(side_effect=lambda prompt, text, **kwargs: {
            "terms": ["Alpha term" if text.startswith("Alpha") else "Beta term"], "printed_page": None, "text": ""})
        with self.quiet():
            result = index_fallback.fallback(self.ctx, ask, "fixture-reader", "fixture-vision")
        self.assertGreater(result["reference_counts"]["mapping-unresolved"], 0)
        self.assertTrue(all(r["printed_page"] is None for e in result["entries"] for r in e["references"]))


if __name__ == "__main__":
    unittest.main()
