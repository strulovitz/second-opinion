"""Regression checks for false offsets and writes based on incomplete evidence."""

import contextlib
import copy
import io
import json
import tempfile
import unittest
from pathlib import Path
from types import SimpleNamespace
from unittest.mock import patch

import page_offset


class OffsetEvidenceTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)
        self.book = {"book_id": "TEST-1", "page_count_images": 100,
                     "page_offset": None, "status": "accepted", "pdf_file": "test.pdf"}
        self.chapters = [{"number": str(i + 1), "title": f"Chapter title {i + 1}",
                          "page_start": 1 + 10 * i, "pdf_page": 6 + 10 * i,
                          "page_end": 10 + 10 * i} for i in range(8)]
        self.toc = {"provinces": [{"name": "Part 1", "chapters": self.chapters}]}
        self.eyes = {"_summary": {"book": "TEST-1"}, "chapters": []}
        for ch in self.chapters:
            image = f"{ch['pdf_page']:05d}.png"
            (self.root / image).touch()
            self.eyes["chapters"].append({
                "province": "Part 1", "number": ch["number"], "title": ch["title"],
                "status": "ok", "opener_confirmed": True, "kind": "printed",
                "pdf_page": ch["pdf_page"], "printed": ch["page_start"], "image_file": image})

    def verify(self):
        return page_offset.verify_pairs(self.book, self.toc, self.eyes, self.root)

    def test_four_agree_but_unsampled_chapter_disagrees(self):
        # The BIBLE samples 0,2,4,6; the old majority vote missed this outlier.
        self.chapters[7]["pdf_page"] += 1
        self.eyes["chapters"][7]["pdf_page"] += 1
        self.eyes["chapters"][7]["image_file"] = "00077.png"
        (self.root / "00077.png").touch()
        with self.assertRaisesRegex(ValueError, "no single offset"):
            self.verify()

    def test_missing_or_duplicate_evidence_is_not_coverage(self):
        self.eyes["chapters"][-1] = copy.deepcopy(self.eyes["chapters"][0])
        with self.assertRaisesRegex(ValueError, "duplicate eye records"):
            self.verify()

    def test_mixed_pdf_and_printed_units_are_rejected(self):
        self.eyes["chapters"][2]["kind"] = "pdf-page"
        with self.assertRaisesRegex(ValueError, "mixed or unknown page units"):
            self.verify()

    def test_stale_image_needs_explicit_refinement_evidence(self):
        rec = self.eyes["chapters"][0]
        rec["image_file"] = "00007.png"
        with self.assertRaisesRegex(ValueError, "image does not prove"):
            self.verify()
        rec["refine"] = {"back_walk": [{"pdf_page": 6, "folio": 1}]}
        self.assertEqual(len(self.verify()[3]), 1)

    def test_bad_chapter_ranges_are_visible(self):
        self.chapters[1]["page_start"] = 1  # two openers on the same printed page
        self.chapters[0]["page_end"] = 0
        self.assertIn("gives 1", page_offset.range_warnings(
            self.book, page_offset.flatten(self.toc), 5)[0])

    def test_layout_restores_reordered_pdf_heading(self):
        def extract(command, **kwargs):
            page = int(command[command.index("-f") + 1])
            ch = self.chapters[(page - 6) // 10]
            heading = ch["title"] if "-layout" in command else "reordered words"
            return SimpleNamespace(stdout=f"{ch['page_start']}\n{heading}\nBody text")

        with patch.object(page_offset.subprocess, "run", side_effect=extract) as run:
            samples = page_offset.cross_check(
                self.root / "test.pdf", page_offset.flatten(self.toc), "printed")
        self.assertEqual(len(samples), 4)
        self.assertEqual(run.call_count, 8)
        self.assertIn("corner folio not readable", samples[0])

    def test_failed_cross_check_cannot_save_any_record(self):
        logs = self.root / "logs"
        logs.mkdir()
        books_file = self.root / "books.json"
        original = json.dumps([self.book, {"book_id": "OTHER-1", "notes": "keep"}])
        books_file.write_text(original)
        (logs / "TEST-1-toc.json").write_text(json.dumps(self.toc))
        (logs / "TEST-1-eyes.json").write_text(json.dumps(self.eyes))
        pdf_dir = self.root / "books"
        pdf_dir.mkdir()
        (pdf_dir / "test.pdf").touch()
        with patch.multiple(page_offset, KITCHEN=self.root, BOOKS=books_file, LOGS=logs), \
                patch.object(page_offset, "verify_pairs", return_value=self.verify()), \
                patch.object(page_offset, "cross_check", side_effect=ValueError("wrong PDF")), \
                contextlib.redirect_stderr(io.StringIO()):
            self.assertEqual(page_offset.main(["TEST-1", "--save"]), 1)
        self.assertEqual(books_file.read_text(), original)


if __name__ == "__main__":
    unittest.main()
