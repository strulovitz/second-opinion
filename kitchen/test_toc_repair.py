"""Regression checks for generic repair, legacy sources and resumable queues."""

import contextlib
import copy
import io
import json
import tempfile
import unittest
from pathlib import Path
from types import SimpleNamespace
from unittest.mock import patch

import toc_repair
import test_toc_reexport as fixture_cases
from toc_repair_source import accepted_source, final_boundary, flat_identity


class GenericRepairTests(unittest.TestCase):
    def setUp(self):
        self.fixture = fixture_cases.ReexportTests()
        self.fixture.setUp()
        self.addCleanup(self.fixture.doCleanups)
        f = self.fixture
        self.book, self.source, self.eyes = f.book, f.source, f.eyes
        self.old = f.toc(45)
        # Use a repository-like layout for receipts and relative backups.
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)
        self.kitchen = self.root / "kitchen"
        self.logs = self.kitchen / "logs"
        self.logs.mkdir(parents=True)
        self.status = self.root / "TOC-REPAIR-STATUS.json"

    def choose(self):
        return accepted_source(self.book, self.source, self.old, self.eyes, self.fixture.images)

    def legacy(self):
        source = copy.deepcopy(self.source)
        for pi, province in enumerate(source["provinces"]):
            for ci, chapter in enumerate(province["chapters"]):
                chapter["page_start"] = pi * 20 + ci * 10 + 1
        return source

    def prepare(self, eyes=True):
        documents = {"vis-toc": self.source if eyes else self.legacy(),
                     "toc": self.old if eyes else {"provinces": []}}
        if eyes:
            documents["eyes"] = self.eyes
        for suffix, data in documents.items():
            (self.logs / f"TEST-1-{suffix}.json").write_text(json.dumps(data))
        (self.kitchen / "books.json").write_text(json.dumps([self.book]))

    def run_cli(self, *args):
        out = io.StringIO()
        with patch.multiple(toc_repair, ROOT=self.root, KITCHEN=self.kitchen,
                            LOGS=self.logs, STATUS=self.status), \
                patch("toc_repair_source.subprocess.run", side_effect=AssertionError("unexpected PDF access")), \
                contextlib.redirect_stdout(out):
            code = toc_repair.main(list(args))
        return code, out.getvalue()

    def test_variable_offsets_do_not_block_ranges_or_change_pdf_pairs(self):
        self.eyes["chapters"][-1]["pdf_page"] += 2
        self.old["provinces"][-1]["chapters"][-1]["pdf_page"] += 2
        toc, updated, mapping, _, issues = self.choose()
        self.assertEqual(mapping["offset_values"], 2)
        self.assertIsNone(mapping["uniform_offset"])
        self.assertEqual(flat_identity(toc), flat_identity(self.old))
        self.assertEqual(updated["chapters"][-1]["pdf_page"], 38)
        self.assertTrue(issues)  # Missing picture is reported, not invented.

    def test_legacy_source_restores_empty_export_without_fake_eyes(self):
        toc, updated, mapping, images, issues = accepted_source(
            self.book, self.legacy(), {"provinces": []}, None, self.fixture.images)
        self.assertIsNone(updated)
        self.assertEqual(mapping["source"], "accepted-vis-toc")
        self.assertEqual(len(flat_identity(toc)), 4)
        self.assertEqual(toc["provinces"][0]["name_source"], "written")
        self.assertNotIn("pdf_page", toc["provinces"][0]["chapters"][0])
        self.assertEqual((images, issues), ([], []))

    def test_matching_export_keeps_its_own_provinces_and_titles(self):
        old = copy.deepcopy(self.old)
        split = copy.deepcopy(old["provinces"][1])
        del split["chapters"][1:]
        removed = copy.deepcopy(old["provinces"][1])
        removed["chapters"] = removed["chapters"][1:]
        old["provinces"] = old["provinces"][:1] + [split, removed]
        old["provinces"][0]["chapters"][0]["title"] = "Title 1 (book wording)"
        toc, _, mapping, _, _ = accepted_source(
            self.book, self.legacy(), old, None, self.fixture.images)
        self.assertEqual([p["name"] for p in toc["provinces"]],
                         ["Part 1", "Part 2", "Part 2"])
        self.assertEqual(toc["provinces"][0]["chapters"][0]["title"],
                         "Title 1 (book wording)")
        self.assertEqual([c["page_end"] for p in toc["provinces"] for c in p["chapters"]],
                         [10, 20, 30, 41])
        self.assertTrue(mapping["structure_preserved"])

    def test_different_chapter_list_is_blocked_for_review(self):
        old = copy.deepcopy(self.old)
        old["provinces"][1]["chapters"].pop()
        with self.assertRaisesRegex(ValueError, "needs SMART review"):
            accepted_source(self.book, self.legacy(), old, None, self.fixture.images)

    def test_rebuild_flag_replaces_a_different_list_only_on_request(self):
        old = copy.deepcopy(self.old)
        old["provinces"][1]["chapters"].pop()
        toc, _, mapping, _, _ = accepted_source(
            self.book, self.legacy(), old, None, self.fixture.images, rebuild=True)
        self.assertEqual(len(flat_identity(toc)), 4)
        self.assertFalse(mapping["structure_preserved"])

    def test_rebuild_is_refused_for_the_automatic_queue(self):
        self.prepare(eyes=False)
        with self.assertRaisesRegex(ValueError, "explicit BOOK_ID"):
            self.run_cli("--next", "--rebuild", "--apply")

    def test_apply_writes_nothing_when_ends_are_already_correct(self):
        self.prepare(eyes=False)
        toc, _, _, _, _ = accepted_source(
            self.book, self.legacy(), {"provinces": []}, None, self.fixture.images)
        path = self.logs / "TEST-1-toc.json"
        path.write_text(json.dumps(toc, indent=1))
        before = path.read_bytes()
        self.assertEqual(self.run_cli("--next", "--apply")[0], 0)
        receipt = json.loads(self.status.read_text())["books"]["TEST-1"]
        self.assertEqual(receipt["saved_files"], 0)
        self.assertNotIn("backup", receipt)
        self.assertEqual(path.read_bytes(), before)

    def test_legacy_pdf_outline_units_are_kept_as_pdf_pages(self):
        source = self.legacy()
        for province in source["provinces"]:
            for chapter in province["chapters"]:
                chapter["_page_source"] = "pdf-outline"
        toc, _, mapping, _, _ = accepted_source(
            self.book, source, {"provinces": []}, None, self.fixture.images)
        self.assertEqual(mapping["unit"], "pdf-page")
        self.assertEqual(toc["provinces"][-1]["chapters"][-1]["pdf_page"], 31)

    def test_bad_eyes_do_not_silently_fall_back_to_an_older_source(self):
        self.eyes["chapters"][0]["opener_confirmed"] = False
        with self.assertRaisesRegex(ValueError, "unconfirmed"):
            self.choose()

    def test_mixed_units_and_reordered_accepted_starts_are_blocked(self):
        self.eyes["chapters"][0]["kind"] = "pdf-page"
        with self.assertRaisesRegex(ValueError, "mixed/unknown"):
            self.choose()
        self.eyes["chapters"][0]["kind"] = "printed"
        self.old["provinces"][0]["chapters"][0]["page_start"] += 1
        with self.assertRaisesRegex(ValueError, "disagrees"):
            self.choose()

    def test_irregular_offsets_can_use_two_actual_adjacent_tail_folios(self):
        mapping = {"unit": "printed", "uniform_offset": None}
        pages = {51: "Index\nEntries, 1, 2\n", 50: "45\nBody\n", 49: "44\nBody\n"}
        def extract(command, **kwargs):
            return SimpleNamespace(stdout=pages[int(command[command.index("-f") + 1])])
        with patch("toc_repair_source.subprocess.run", side_effect=extract) as calls:
            end, result = final_boundary(self.book, self.old, self.old, mapping, Path("unused.pdf"), True)
        self.assertEqual((end, result["mode"]), (45, "verified-tail-folios"))
        self.assertEqual(calls.call_count, 3)

    def test_unconfirmed_index_is_a_reported_fallback_not_a_book_failure(self):
        with patch("toc_repair_source.subprocess.run", return_value=SimpleNamespace(stdout="Not an index\n")):
            end, result = final_boundary(self.book, self.old, self.old,
                                         {"unit": "printed", "uniform_offset": None}, Path("unused.pdf"), True)
        self.assertIsNone(end)
        self.assertEqual(result["mode"], "median-fallback")
        self.assertIn("not confirmed", result["note"])

    def test_existing_index_derived_end_is_preserved_without_claiming_recheck(self):
        end, result = final_boundary(self.book, self.old, self.old,
                                     {"unit": "printed", "uniform_offset": 5}, Path("unused.pdf"))
        self.assertEqual((end, result["mode"]), (45, "saved-index-boundary"))
        self.assertIn("not rechecked", result["note"])

    def test_audit_opens_no_pdfs_and_writes_no_status_or_output(self):
        self.prepare(eyes=False)
        before = {p: p.read_bytes() for p in self.logs.iterdir()}
        code, out = self.run_cli("--audit")
        self.assertEqual(code, 0)
        self.assertIn("1/1 books repairable", out)
        self.assertEqual({p: p.read_bytes() for p in before}, before)
        self.assertFalse(self.status.exists())

    def test_apply_backs_up_legacy_export_and_resume_does_not_repeat_book(self):
        self.prepare(eyes=False)
        old_bytes = (self.logs / "TEST-1-toc.json").read_bytes()
        books_bytes = (self.kitchen / "books.json").read_bytes()
        self.assertEqual(self.run_cli("--next", "--apply")[0], 0)
        receipt = json.loads(self.status.read_text())["books"]["TEST-1"]
        self.assertEqual(receipt["state"], "applied")
        backup = self.root / receipt["backup"]
        self.assertEqual((backup / "TEST-1-toc.json").read_bytes(), old_bytes)
        self.assertEqual((self.kitchen / "books.json").read_bytes(), books_bytes)
        self.assertEqual(receipt["previous_chapters"], 0)
        self.assertEqual(receipt["chapters"], 4)
        self.assertIn("Queue finished", self.run_cli("--next", "--apply")[1])

    def test_bad_book_is_recorded_and_skipped_until_explicit_retry(self):
        self.prepare(eyes=False)
        (self.logs / "TEST-1-vis-toc.json").write_text('{"provinces":[]}')
        before = (self.logs / "TEST-1-toc.json").read_bytes()
        self.assertEqual(self.run_cli("--next", "--apply")[0], 1)
        self.assertEqual(json.loads(self.status.read_text())["books"]["TEST-1"]["state"], "blocked")
        self.assertEqual((self.logs / "TEST-1-toc.json").read_bytes(), before)
        self.assertIn("Queue finished", self.run_cli("--next", "--apply")[1])

    def test_summary_collects_exceptions_and_added_evidence_invalidates_a_receipt(self):
        self.prepare(eyes=False)
        self.assertEqual(self.run_cli("--next", "--apply")[0], 0)
        code, text = self.run_cli("--summary")
        self.assertEqual(code, 0)
        self.assertIn("1 applied; 0 blocked; 0 pending/stale", text)
        self.assertIn("FINAL TEST-1:", text)
        (self.logs / "TEST-1-eyes.json").write_text(json.dumps(self.eyes))
        self.assertIn("1 pending/stale", self.run_cli("--summary")[1])


if __name__ == "__main__":
    unittest.main()
