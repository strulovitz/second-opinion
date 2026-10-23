"""Small artificial PDFs: real extraction, hierarchy, mapping and recovery."""

import contextlib
import copy
import io
import json
import tempfile
import unittest
from pathlib import Path
from types import SimpleNamespace
from unittest.mock import Mock, patch

from pypdf import PdfWriter
from pypdf.generic import DecodedStreamObject, DictionaryObject, NameObject

import page_mapping
import toc_book
import toc_store
import toc_observe
import toc_repair
from toc_evidence import PdfEvidence, bookmark_toc, opener_matches, pdf_identity
from toc_repair import retain_history, summary


def make_pdf(path, texts, outline=()):
    writer = PdfWriter()
    font = DictionaryObject({NameObject("/Type"): NameObject("/Font"),
                             NameObject("/Subtype"): NameObject("/Type1"),
                             NameObject("/BaseFont"): NameObject("/Helvetica")})
    for text in texts:
        page = writer.add_blank_page(width=612, height=792)
        page[NameObject("/Resources")] = DictionaryObject({NameObject("/Font"): DictionaryObject({NameObject("/F1"): font})})
        stream = DecodedStreamObject()
        lines = [line.replace("\\", "\\\\").replace("(", "\\(").replace(")", "\\)") for line in text.splitlines()]
        stream.set_data(("BT /F1 12 Tf 50 740 Td 16 TL " + " ".join(f"({line}) Tj T*" for line in lines) + " ET").encode())
        page[NameObject("/Contents")] = writer._add_object(stream)
    parents = {}
    for name, page, depth in outline:
        parents[depth] = writer.add_outline_item(name, page - 1, parent=parents.get(depth - 1))
    writer.write(path)
    writer.close()


class EvidenceTests(unittest.TestCase):
    def test_heading_requires_full_title_and_exact_number(self):
        self.assertTrue(opener_matches("C\nHAPTER 1\nSurgical Techniques\n1", "1", "Surgical Techniques"))
        self.assertFalse(opener_matches("CHAPTER 10 Surgical Techniques", "1", "Surgical Techniques"))
        self.assertFalse(opener_matches("CHAPTER 1 Diabetes Mellitus: Diagnosis", "1", "Diabetes Mellitus: Complications"))
        self.assertTrue(opener_matches("4.2\nDotted Chapters\nBody", "4.2", "Dotted Chapters"))
        self.assertFalse(opener_matches("42 Dotted Chapters", "4.2", "Dotted Chapters"))
        self.assertFalse(opener_matches("Contents\n1 Surgical Techniques 10", "1", "Surgical Techniques"))
        self.assertFalse(opener_matches("Body refers to chapter 1 Surgical Techniques for details", "1", "Surgical Techniques"))

    def test_nested_outline_excludes_internal_and_technique_lists(self):
        rows = [("PART I Basics", 0, 1), ("SECTION A Foundations", 1, 1),
                ("Chapter 1: Surgical Techniques", 2, 2), ("1.1 Internal detail", 3, 2),
                ("SECTION B Practice", 1, 3), ("2 Practical Work", 2, 3),
                ("List of Techniques", 0, 1), ("3 Not a chapter", 1, 4),
                ("Online-only", 0, None), ("Chapter 4: Not physical", 1, None)]
        toc, proof = bookmark_toc([{"title": t, "depth": d, "image": p} for t, d, p in rows], "Book")
        self.assertEqual([p["name"] for p in toc["provinces"]], ["SECTION A Foundations", "SECTION B Practice"])
        self.assertEqual(toc["provinces"][1]["part_name"], "PART I Basics")
        self.assertEqual([c["number"] for p in toc["provinces"] for c in p["chapters"]], ["1", "2"])
        self.assertEqual(len(proof["excluded"]), 3)

    def test_cache_reuses_selected_pages_and_invalidates_evidence_and_pdf(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            pdf, cache = root / "test.pdf", root / "cache.json"
            make_pdf(pdf, ["CHAPTER 1 Exact Title", "not selected"])
            with PdfEvidence(pdf, cache, "source-one") as session:
                self.assertIn("Exact Title", session.text(1))
                self.assertEqual(len(session.pages), 1)
                session.save_cache()
            with PdfEvidence(pdf, cache, "source-one") as session:
                session.text(1)
                self.assertIsNone(session.reader)
                self.assertEqual(session.hits, 1)
            with PdfEvidence(pdf, cache, "source-two") as session:
                self.assertEqual(session.pages, {})
            make_pdf(pdf, ["Changed"])
            with PdfEvidence(pdf, cache, "source-one") as session:
                self.assertEqual(session.pages, {})


class WorkflowTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)
        self.logs = self.root / "kitchen/logs"
        self.logs.mkdir(parents=True)
        (self.root / "kitchen/books").mkdir()
        self.pdf = self.root / "kitchen/books/test.pdf"
        texts = [f"CHAPTER {i + 1}\nExact Title {i + 1}\nBody\nMore\nText\nFooter\n{i + 10}" for i in range(8)]
        outline = [("PART I Foundations", 1, 0)] + [(f"Chapter {i + 1}: Exact Title {i + 1}", i + 1, 1) for i in range(8)]
        make_pdf(self.pdf, texts, outline)
        self.book = {"book_id": "TEST-1", "title": "Artificial Book", "pdf_file": "test.pdf",
                     "page_count_images": 8, "page_offset": None, "status": "accepted"}
        self.books = self.root / "kitchen/books.json"
        self.books.write_text(json.dumps([self.book, {"book_id": "OTHER", "notes": "preserve"}]))
        self.toc = {"provinces": [{"name": "PART I Foundations", "part_name": "PART I Foundations", "chapters": [
            {"number": str(i + 1), "title": f"Exact Title {i + 1}", "page_start": i + 1, "pdf_page": i + 1}
            for i in range(8)]}]}
        self.path = self.logs / "TEST-1-toc.json"
        self.path.write_text(json.dumps(self.toc))
        (self.logs / "TEST-1-vis-toc.json").write_text(json.dumps(self.toc))
        self.eyes = {"_summary": {"book": "TEST-1"}, "chapters": []}
        image_dir = self.logs / "eyes-render/TEST-1"
        image_dir.mkdir(parents=True)
        for i, ch in enumerate(self.toc["provinces"][0]["chapters"]):
            (image_dir / f"{i + 1:05d}.png").touch()
            self.eyes["chapters"].append(ch | {"province": "PART I Foundations", "status": "ok",
                "opener_confirmed": True, "kind": "printed", "printed": i + 10, "image_file": f"{i + 1:05d}.png"})
        self.eyes_path = self.logs / "TEST-1-eyes.json"

    def cli(self, module, *args):
        out = io.StringIO()
        with patch.object(module, "ROOT", self.root), contextlib.redirect_stdout(out), contextlib.redirect_stderr(out):
            code = module.main(["TEST-1", *args])
        return code, out.getvalue()

    def test_outline_dry_run_apply_and_document_end_keep_units_separate(self):
        before = self.books.read_bytes(), self.path.read_bytes()
        code, text = self.cli(toc_book, "--outline", "--document-end")
        self.assertEqual(code, 0, text)
        self.assertEqual((self.books.read_bytes(), self.path.read_bytes()), before)
        self.assertFalse((self.logs / "TEST-1-toc-proof.json").exists())
        code, text = self.cli(toc_book, "--outline", "--document-end", "--apply")
        self.assertEqual(code, 0, text)
        proof = json.loads((self.logs / "TEST-1-toc-proof.json").read_text())
        self.assertEqual(proof["boundary"]["mode"], "verified-document-end")
        self.assertEqual(proof["last_page"], 8)
        self.assertEqual(self.books.read_bytes(), before[0])
        self.assertEqual(self.cli(toc_book, "--outline", "--document-end", "--apply")[0], 0)
        self.assertEqual(len(list((self.logs / "toc-tool-backups/TEST-1").iterdir())), 1)

    def test_correction_archives_bad_list_eyes_and_folio_cache_together(self):
        wrong = copy.deepcopy(self.toc)
        wrong["provinces"][0]["chapters"].pop()
        self.path.write_text(json.dumps(wrong))
        self.eyes_path.write_text("old accepted observations; preserve in backup")
        folio = self.logs / "TEST-1-folio.txt"
        folio.write_text("old cache")
        code, text = self.cli(toc_book, "--outline", "--apply")
        self.assertEqual(code, 0, text)
        self.assertFalse(self.eyes_path.exists())
        self.assertFalse(folio.exists())
        journal = next((self.logs / "toc-tool-backups/TEST-1").glob("*/transaction.json"))
        data = json.loads(journal.read_text())
        self.assertTrue(any(r["before"] == "old cache" for r in data["files"]))

    def test_arithmetic_only_target_check_preserves_reader_evidence(self):
        self.eyes_path.write_text("keep evidence untouched")
        code, text = self.cli(toc_book, "--apply")
        self.assertEqual(code, 0, text)
        self.assertEqual(self.eyes_path.read_text(), "keep evidence untouched")

    def test_wrong_contents_type_cannot_replace_a_source(self):
        source = self.logs / "checked.json"
        source.write_text(json.dumps(self.toc | {"book_id": "TEST-1", "pdf_identity": pdf_identity(self.pdf),
                                               "kind": "technique-list", "source_pages": [1], "unit": "pdf-page"}))
        before = self.path.read_bytes()
        code, text = self.cli(toc_book, "--source", str(source), "--apply")
        self.assertEqual(code, 1, text)
        self.assertEqual(self.path.read_bytes(), before)

    def test_checked_contents_preserves_sections_and_verifies_printed_folios(self):
        data = copy.deepcopy(self.toc)
        first = data["provinces"][0]
        second = copy.deepcopy(first)
        first["name"], second["name"] = "SECTION A Foundations", "SECTION B Practice"
        first["chapters"], second["chapters"] = first["chapters"][:4], second["chapters"][4:]
        data["provinces"].append(second)
        for i, (_, chapter) in enumerate(page_mapping.flatten(data)):
            chapter["page_start"] = i + 10
        source = self.logs / "checked.json"
        data.update(book_id="TEST-1", pdf_identity=pdf_identity(self.pdf), kind="chapter-contents", source_pages=[1], unit="printed")
        source.write_text(json.dumps(data))
        code, text = self.cli(toc_book, "--source", str(source), "--apply")
        self.assertEqual(code, 0, text)
        saved = json.loads(self.path.read_text())
        self.assertEqual(saved["provinces"][1]["name"], "SECTION B Practice")
        self.assertEqual(saved["provinces"][1]["part_name"], "PART I Foundations")
        saved_bytes = self.path.read_bytes()
        data["provinces"][0]["chapters"][0]["page_start"] = 999
        source.write_text(json.dumps(data))
        self.assertEqual(self.cli(toc_book, "--source", str(source), "--apply")[0], 1)
        self.assertEqual(self.path.read_bytes(), saved_bytes)

    def test_proved_single_page_final_chapter_survives_range_receipt(self):
        make_pdf(self.pdf, ["CHAPTER 1\nExact Title 1"] , [("PART I Foundations", 1, 0), ("Chapter 1: Exact Title 1", 1, 1)])
        self.book["page_count_images"] = 1
        self.books.write_text(json.dumps([self.book]))
        code, text = self.cli(toc_book, "--outline", "--document-end", "--apply")
        self.assertEqual(code, 0, text)
        with patch.multiple(toc_repair, ROOT=self.root, KITCHEN=self.root / "kitchen", LOGS=self.logs):
            report, _, _ = toc_repair.plan(self.book)
        self.assertEqual((report["first_page"], report["last_page"]), (1, 1))
        self.assertEqual(report["boundary"]["mode"], "verified-document-end")

    def test_one_page_reader_observation_is_resumable_and_pdf_identity_bound(self):
        def render(command, **kwargs):
            Path(command[-1] + ".png").write_bytes(b"artificial image; renderer mocked")
        ask = Mock(return_value="KIND: OPENING\nHEADING: CHAPTER 1 Exact Title 1\nFOLIO: 10")
        with patch.object(toc_observe.subprocess, "run", side_effect=render) as rendered, \
                patch.dict("sys.modules", {"reader": SimpleNamespace(ask=ask)}):
            code, text = self.cli(toc_observe, "--number", "1", "--pdf-page", "1")
            self.assertEqual(code, 0, text)
            self.assertEqual(self.cli(toc_observe, "--number", "1", "--pdf-page", "1")[0], 0)
            self.assertEqual(rendered.call_count, 1)
            self.assertEqual(ask.call_count, 1)
        data = json.loads((self.logs / "TEST-1-checked-pairs.json").read_text())
        self.assertEqual(len(data["chapters"]), 1)
        self.assertEqual(data["pdf_identity"], pdf_identity(self.pdf))
        self.assertEqual(data["chapters"][0]["printed"], 10)

    def test_ambiguous_bookmark_target_uses_draft_and_saved_reader_without_reaudit(self):
        make_pdf(self.pdf, ["Encoded heading is unreadable"] + [f"CHAPTER {i}\nExact Title {i}" for i in range(2, 9)],
                 [("PART I Foundations", 1, 0)] + [(f"Chapter {i}: Exact Title {i}", i, 1) for i in range(1, 9)])
        code, text = self.cli(toc_book, "--outline", "--proposal")
        self.assertEqual(code, 1, text)
        draft = self.logs / "TEST-1-toc-proposal.json"
        self.assertTrue(draft.exists())
        def render(command, **kwargs):
            Path(command[-1] + ".png").write_bytes(b"selected-page-image")
        ask = Mock(return_value="KIND: OPENING\nHEADING: CHAPTER 1 Exact Title 1\nFOLIO: 10")
        with patch.object(toc_observe.subprocess, "run", side_effect=render), \
                patch.dict("sys.modules", {"reader": SimpleNamespace(ask=ask)}):
            code, text = self.cli(toc_observe, "--number", "1", "--pdf-page", "1", "--source", str(draft))
            self.assertEqual(code, 0, text)
        observations = self.logs / "TEST-1-checked-pairs.json"
        code, text = self.cli(toc_book, "--outline", "--observations", str(observations), "--apply")
        self.assertEqual(code, 0, text)
        proof = json.loads((self.logs / "TEST-1-toc-proof.json").read_text())
        self.assertEqual(sum(p["method"] == "saved-free-reader" for p in proof["proofs"]), 1)

    def prepare_mapping(self):
        toc = copy.deepcopy(self.toc)
        for i, chapter in enumerate(toc["provinces"][0]["chapters"]):
            chapter["page_start"] = i + 10
        self.path.write_text(json.dumps(toc))
        self.eyes_path.write_text(json.dumps(self.eyes))
        return toc

    def test_uniform_negative_offset_saves_with_backup_and_preserves_other_book(self):
        self.prepare_mapping()
        before = self.books.read_text()
        code, text = self.cli(page_mapping)
        self.assertEqual(code, 0, text)
        self.assertEqual(self.books.read_text(), before)
        code, text = self.cli(page_mapping, "--save")
        self.assertEqual(code, 0, text)
        books = json.loads(self.books.read_text())
        self.assertEqual(books[0]["page_offset"], -9)
        self.assertEqual(books[1], {"book_id": "OTHER", "notes": "preserve"})

    def test_unsampled_offset_difference_proposes_ranges_and_cannot_save(self):
        self.prepare_mapping()
        self.eyes["chapters"][-1]["printed"] = 99
        toc = json.loads(self.path.read_text())
        toc["provinces"][0]["chapters"][-1]["page_start"] = 99
        self.path.write_text(json.dumps(toc))
        self.eyes_path.write_text(json.dumps(self.eyes))
        before = self.books.read_bytes()
        code, text = self.cli(page_mapping, "--report")
        self.assertEqual(code, 2, text)
        report = json.loads((self.logs / "TEST-1-mapping-proposal.json").read_text())
        self.assertIsNone(report["page_offset"])
        self.assertEqual(len(report["proposed_page_offsets"]), 2)
        self.assertEqual(report["proposed_page_offsets"][1]["transition_after_image"], 7)
        self.assertEqual(self.cli(page_mapping, "--save")[0], 1)
        self.assertEqual(self.books.read_bytes(), before)

    def test_pdf_unit_citations_cannot_be_saved_as_printed_zero_offset(self):
        for row in self.eyes["chapters"]:
            row["kind"], row["printed"] = "pdf-page", row["pdf_page"]
        self.eyes_path.write_text(json.dumps(self.eyes))
        before = self.books.read_bytes()
        code, text = self.cli(page_mapping, "--save")
        self.assertEqual(code, 1, text)
        self.assertIn("no accepted printed/PDF pairs", text)
        self.assertEqual(self.books.read_bytes(), before)

    def test_new_four_samples_cannot_hide_an_older_unsampled_disagreement(self):
        self.prepare_mapping()
        extra = {"book_id": "TEST-1", "pdf_identity": pdf_identity(self.pdf),
                 "chapters": [copy.deepcopy(self.eyes["chapters"][i]) for i in (0, 2, 4, 6)]}
        extra_path = self.logs / "TEST-1-checked-pairs.json"
        extra_path.write_text(json.dumps(extra))
        self.eyes["chapters"][-1]["printed"] = 99
        self.eyes_path.write_text(json.dumps(self.eyes))
        toc = json.loads(self.path.read_text())
        toc["provinces"][0]["chapters"][-1]["page_start"] = 99
        self.path.write_text(json.dumps(toc))
        before = self.books.read_bytes()
        code, text = self.cli(page_mapping, "--pairs", str(extra_path), "--report")
        self.assertEqual(code, 2, text)
        report = json.loads((self.logs / "TEST-1-mapping-proposal.json").read_text())
        self.assertEqual(len(report["accepted_pairs"]), 8)
        self.assertIsNone(report["page_offset"])
        self.assertEqual(self.books.read_bytes(), before)

    def test_unaccepted_book_mapping_cannot_promote_status(self):
        self.prepare_mapping()
        self.book["status"] = "candidate"
        self.books.write_text(json.dumps([self.book]))
        before = self.books.read_bytes()
        code, text = self.cli(page_mapping, "--save")
        self.assertEqual(code, 1, text)
        self.assertEqual(self.books.read_bytes(), before)

    def test_bundle_rolls_back_partial_write_and_guards_changed_input(self):
        a, b = self.logs / "a.json", self.logs / "b.json"
        a.write_text("before-a")
        b.write_text("before-b")
        original = toc_store.atomic_write
        def fail_second(path, text):
            if path == b and text == "after-b":
                raise OSError("simulated disk failure")
            original(path, text)
        with patch.object(toc_store, "atomic_write", side_effect=fail_second):
            with self.assertRaisesRegex(OSError, "simulated"):
                toc_store.save_bundle(self.root, self.logs, "TEST-1", "test", toc_store.snapshot([a, b]),
                                      {a: "after-a", b: "after-b"})
        self.assertEqual((a.read_text(), b.read_text()), ("before-a", "before-b"))
        with self.assertRaisesRegex(ValueError, "inputs changed"):
            toc_store.save_bundle(self.root, self.logs, "TEST-1", "test", {a: "stale"}, {a: "new"})

    def test_receipt_retry_retains_history_backup_and_distinct_corrections(self):
        prior = {"state": "applied", "backup": "first-backup", "ends_total": 7, "corrected_chapters": ["ch1"]}
        new = retain_history(prior, {"state": "applied", "saved_files": 0, "corrected_chapters": ["ch1"]})
        self.assertEqual(new["backup"], "first-backup")
        self.assertEqual(new["distinct_corrected_chapters"], 1)
        self.assertEqual(new["legacy_end_assignments"], 7)
        self.assertEqual(new["history"][0], prior)

    def test_summary_distinguishes_document_end_from_estimate(self):
        record = {"state": "applied", "book": "TEST-1", "boundary": {"mode": "verified-document-end", "note": "PDF end"},
                  "image_issues": [], "offset_values": 0}
        out = io.StringIO()
        with contextlib.redirect_stdout(out):
            summary({"books": {"TEST-1": record}}, [])
        self.assertIn("1 document-end proofs (PDF units); 0 estimates/unverified", out.getvalue())


if __name__ == "__main__":
    unittest.main()
