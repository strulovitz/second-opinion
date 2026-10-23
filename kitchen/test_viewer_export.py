"""Artificial export fixtures, never written into the project's real site/."""

import copy
import json
import tempfile
import unittest
from datetime import date
from pathlib import Path

import export_districts
import export_entities
from viewer_export import write_json


class ViewerExportTests(unittest.TestCase):
    def statement(self, district, f, severe=False):
        return {"book_id": "SYNTHETIC", "district_id": district, "page_number": 7,
                "quote": "Artificial test sentence.", "image_file": "synthetic.png",
                "f_scale": f, "severity": severe, "read_date": date(2026, 1, 1)}

    def row(self, district, f, severe=False):
        return {"relation": "HARMS", "direction": "in", "subtype": None,
                "other_slug": "synthetic-b", "other_name": "Synthetic B", "other_group": "treatments-and-drugs",
                "district_name": district, "statement": self.statement(district, f, severe)}

    def test_aggregation_retains_district_statements_and_provenance(self):
        edges = export_entities.aggregate([self.row("D1", 0), self.row("D2", 5, True)])
        self.assertEqual(len(edges), 1)
        self.assertEqual(edges[0]["f_scale"], 5)
        self.assertTrue(edges[0]["severity"])
        self.assertEqual([s["district_id"] for s in edges[0]["statements"]], ["D2", "D1"])
        self.assertEqual(edges[0]["statements"][1]["f_scale"], 0)
        self.assertEqual(edges[0]["statements"][0]["image_file"], "synthetic.png")

    def test_missing_provenance_is_not_published(self):
        row = self.row("D1", 2)
        del row["statement"]["image_file"]
        with self.assertRaisesRegex(ValueError, "provenance"):
            export_entities.aggregate([row])

    def test_dates_mirrors_and_unchanged_export_are_idempotent(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            payload = {"evidence_date": date(2026, 1, 1), "name": "Synthetic < & >"}
            self.assertEqual(write_json("test.json", payload, root)[0], 2)
            first = (root / "site/data/test.json").read_bytes()
            self.assertEqual(write_json("test.json", payload, root)[0], 0)
            self.assertEqual(first, (root / "data/export/test.json").read_bytes())
            self.assertEqual(json.loads(first)["evidence_date"], "2026-01-01")

    def test_entities_and_search_use_database_rows_without_invented_altitude(self):
        def run(query, **params):
            if query == export_entities.ENTITIES:
                return [{"e": {"slug": "synthetic-a", "group": "symptoms-and-signs", "canonical_name": "Synthetic A"}}]
            if query == export_entities.BOOKS:
                return [{"n": 1}]
            if query == export_entities.LIT:
                return [{"district_id": "D1", "district_name": "Synthetic district", "book_id": "SYNTHETIC", "book_field": "Synthetic field",
                         "pages": [8, 7, 7], "sources": ["index"], "mentions": [self.statement("D1", 0) | {"source": "index"}]}]
            if query == export_entities.EDGES:
                return [self.row("D1", 0)]
            self.fail(query)
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            self.assertEqual(export_entities.export(run, root)["entities"], 1)
            self.assertEqual(export_entities.export(run, root)["files_changed_both_copies"], 0)
            entity = json.loads((root / "site/data/entities/synthetic-a.json").read_text())
            self.assertIsNone(entity["altitude"])
            self.assertEqual(entity["lit_spots"][0]["pages"], [7, 8])
            self.assertFalse(json.loads((root / "site/data/search.json").read_text())[0]["has_text"])

    def test_districts_keep_empty_places_and_rank_mentions(self):
        districts = [{"territory_id": "D1", "name": "Synthetic district"}, {"territory_id": "D2", "name": "Empty synthetic district"}]
        def run(query, **params):
            if query == export_districts.DISTRICTS:
                return [{"district": copy.deepcopy(d)} for d in districts]
            return [{"territory_id": "D1", "slug": "synthetic-a", "canonical_name": "A", "group": "symptoms-and-signs", "mentions": 3, "pages": [2, 1], "edges_here": 0},
                    {"territory_id": "D1", "slug": "synthetic-b", "canonical_name": "B", "group": "diseases-and-conditions", "mentions": 1, "pages": [1], "edges_here": 2}]
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            self.assertEqual(export_districts.export(run, root)["districts"], 2)
            self.assertEqual(export_districts.export(run, root)["files_changed_both_copies"], 0)
            self.assertEqual(json.loads((root / "site/data/districts/D1.json").read_text())["entities"][0]["slug"], "synthetic-b")
            self.assertEqual(json.loads((root / "site/data/districts/D2.json").read_text())["entities"], [])

    def test_empty_database_does_not_erase_existing_exports(self):
        for exporter in (export_entities.export, export_districts.export):
            with self.assertRaises(ValueError):
                exporter(lambda query: [])


if __name__ == "__main__":
    unittest.main()
