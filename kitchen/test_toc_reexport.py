"""Regression checks for cross-province ranges and evidence-only re-export."""

import contextlib
import io
import json
import tempfile
import unittest
from pathlib import Path
from types import SimpleNamespace
from unittest.mock import patch

import eyes_folio
import toc_reexport


class ReexportTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)
        self.logs = self.root / "logs"
        self.logs.mkdir()
        self.images = self.logs / "eyes-render" / "TEST-1"
        self.images.mkdir(parents=True)
        self.book = {"book_id": "TEST-1", "page_count_images": 100,
                     "index_images": [51, 100], "page_offset": 5,
                     "pdf_file": "test.pdf", "status": "accepted"}
        self.source = {"provinces": []}
        self.rows = []
        for pi in range(2):
            province = {"name": f"Part {pi + 1}", "name_source": "written", "chapters": []}
            self.source["provinces"].append(province)
            for j in range(2):
                number = str(pi * 2 + j + 1)
                start = (pi * 2 + j) * 10 + 1
                chapter = {"number": number, "title": f"Title {number}"}
                province["chapters"].append(chapter)
                row = chapter | {"province": province["name"], "status": "ok",
                                 "opener_confirmed": True, "kind": "printed",
                                 "pdf_page": start + 5, "printed": start,
                                 "image_file": f"{start + 5:05d}.png"}
                self.rows.append(row)
                (self.images / row["image_file"]).touch()
        self.eyes = {"_summary": {"book": "TEST-1", "unresolved": 0}, "chapters": self.rows}

    def toc(self, end=None):
        return eyes_folio.toc_from_evidence(self.source, self.rows, end, require_complete=True)

    def test_ranges_cross_province_boundary_and_preserve_name_provenance(self):
        toc = self.toc(45)
        first, last = toc["provinces"]
        self.assertEqual(first["chapters"][-1]["page_end"], 20)
        self.assertEqual((first["page_start"], first["page_end"]), (1, 20))
        self.assertEqual((last["page_start"], last["page_end"]), (21, 45))
        self.assertEqual(first["name_source"], "written")

    def test_shared_page_has_no_negative_range_even_across_provinces(self):
        self.rows[2]["printed"] = 11
        toc = self.toc(45)
        self.assertEqual(toc["provinces"][0]["chapters"][-1]["page_end"], 11)
        self.assertEqual(toc["provinces"][1]["chapters"][0]["page_start"], 11)

    def test_unknown_index_uses_book_wide_positive_median(self):
        # Positive gaps are 10 and 20; the equal start must not bias the median.
        self.rows[2]["printed"] = 11
        self.assertEqual(self.toc()["provinces"][-1]["page_end"], 46)

    def test_decreasing_starts_are_rejected_without_sorting(self):
        self.rows[2]["printed"] = 2
        with self.assertRaisesRegex(ValueError, "decreases"):
            self.toc(45)

    def test_incomplete_or_duplicate_saved_evidence_is_rejected(self):
        with self.assertRaisesRegex(ValueError, "missing saved eyes"):
            eyes_folio.toc_from_evidence(self.source, self.rows[:-1], require_complete=True)
        with self.assertRaisesRegex(ValueError, "duplicate eye records"):
            eyes_folio.toc_from_evidence(self.source, self.rows + [self.rows[0]])

    def test_chapter_numbers_restarting_in_a_new_province_do_not_collide(self):
        self.source["provinces"][1]["chapters"][0]["number"] = "1"
        self.rows[2]["number"] = "1"
        self.assertEqual(self.toc(45)["provinces"][1]["chapters"][0]["page_start"], 21)

    def test_index_cannot_end_before_last_chapter(self):
        with self.assertRaisesRegex(ValueError, "precedes"):
            self.toc(30)

    def test_stale_picture_requires_saved_matching_page_and_folio(self):
        row = self.rows[0]
        row.update(image_file="00007.png", heading="original", reader_raw="original raw")
        row["refine"] = {"back_walk": [{"pdf_page": 6, "folio": 2,
                                        "kind": "OPENING", "heading": "Title 1"}]}
        with self.assertRaisesRegex(ValueError, "no saved refinement proof"):
            toc_reexport.repair_images(self.eyes, self.images)
        row["refine"]["back_walk"][0]["folio"] = 1
        changes = toc_reexport.repair_images(self.eyes, self.images)
        self.assertEqual(changes, ["ch1: 00007.png -> 00006.png"])
        self.assertIsNone(row["reader_raw"])  # Do not invent a missing historical raw answer.
        self.assertEqual(row["refine"]["initial_observation"]["reader_raw"], "original raw")
        self.assertEqual(toc_reexport.repair_images(self.eyes, self.images), [])

    def test_future_refinement_keeps_the_selected_raw_answer_and_image(self):
        answers = [("OPENING", "Title 1", 1, "selected raw", "00006.png"),
                   ("BODY", "previous chapter", 0, "previous raw", "00005.png")]
        with patch.object(eyes_folio, "ask_page", side_effect=answers):
            page, folio, proof = eyes_folio.refine_opener(
                Path("unused.pdf"), "TEST-1", {"number": "1", "title": "Title 1"}, 7, 2, 1)
        self.assertEqual((page, folio), (6, 1))
        self.assertEqual(proof["back_walk"][0]["image_file"], "00006.png")
        self.assertEqual(proof["back_walk"][0]["raw"], "selected raw")

    def extract(self, command, **kwargs):
        page = int(command[command.index("-f") + 1])
        return SimpleNamespace(stdout="Index\nEntries, 1, 2\n" if page == 51 else "Body\n")

    def test_index_boundary_converts_the_same_way_as_the_chapter_unit(self):
        with patch.object(toc_reexport.subprocess, "run", side_effect=self.extract):
            self.assertEqual(toc_reexport.index_end(self.book, Path("unused.pdf"), 5)[0], 45)
            self.assertEqual(toc_reexport.index_end(self.book, Path("unused.pdf"), 0)[0], 50)
        with patch.object(toc_reexport.subprocess, "run", return_value=SimpleNamespace(stdout="Index\n")):
            with self.assertRaisesRegex(ValueError, "already index"):
                toc_reexport.index_end(self.book, Path("unused.pdf"), 5)

    def prepare_files(self):
        for name, data in (("eyes", self.eyes), ("toc", self.toc(31)), ("vis-toc", self.source)):
            (self.logs / f"TEST-1-{name}.json").write_text(json.dumps(data))
        (self.root / "books.json").write_text(json.dumps([self.book]))

    def run_cli(self, *args):
        with patch.multiple(toc_reexport, KITCHEN=self.root, LOGS=self.logs), \
                patch.object(toc_reexport.subprocess, "run", side_effect=self.extract), \
                contextlib.redirect_stdout(io.StringIO()), contextlib.redirect_stderr(io.StringIO()):
            return toc_reexport.main(["TEST-1", *args])

    def test_dry_run_writes_nothing_apply_backs_up_and_second_apply_is_noop(self):
        self.prepare_files()
        originals = {p: p.read_bytes() for p in self.logs.glob("*.json")}
        books = (self.root / "books.json").read_bytes()
        self.assertEqual(self.run_cli(), 0)
        self.assertEqual({p: p.read_bytes() for p in originals}, originals)
        self.assertFalse((self.logs / "toc-reexport-backups").exists())
        self.assertEqual(self.run_cli("--apply"), 0)
        backups = list((self.logs / "toc-reexport-backups/TEST-1").iterdir())
        self.assertEqual(len(backups), 1)
        self.assertEqual((backups[0] / "TEST-1-toc.json").read_bytes(), originals[self.logs / "TEST-1-toc.json"])
        self.assertEqual((self.root / "books.json").read_bytes(), books)
        self.assertEqual(self.run_cli("--apply"), 0)
        self.assertEqual(len(list((self.logs / "toc-reexport-backups/TEST-1").iterdir())), 1)

    def test_failed_verification_cannot_write_or_create_backups(self):
        self.rows[-1]["status"] = "opener-not-found"
        # Write inputs directly because the pure exporter rejects this too.
        (self.logs / "TEST-1-eyes.json").write_text(json.dumps(self.eyes))
        (self.logs / "TEST-1-vis-toc.json").write_text(json.dumps(self.source))
        (self.logs / "TEST-1-toc.json").write_text("{}")
        (self.root / "books.json").write_text(json.dumps([self.book]))
        self.assertEqual(self.run_cli("--apply"), 1)
        self.assertEqual((self.logs / "TEST-1-toc.json").read_text(), "{}")
        self.assertFalse((self.logs / "toc-reexport-backups").exists())


if __name__ == "__main__":
    unittest.main()
