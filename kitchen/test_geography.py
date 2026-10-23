"""Geography invariants: coverage, stable seating, area, IDs and hit testing."""

import copy
import csv
import hashlib
import json
import tempfile
import unittest
from pathlib import Path

import numpy as np
from PIL import Image

import geography as geo


class GeographyTests(unittest.TestCase):
    def fixture(self):
        books = [{"book_id": name, "title": name, "field_name": name, "cluster": cluster,
                  "status": "accepted", "page_count_images": 100}
                 for name, cluster in (("HARRISON-22", "general"), ("BETA-1", "lungs"), ("ALPHA-1", "lungs"))]
        contents = {}
        for book in books:
            contents[book["book_id"]] = {"provinces": [
                {"name": "Part I Foundations", "part_name": "Part I Foundations", "chapters": [
                    {"number": "1", "title": "First chapter", "page_start": 1, "page_end": 10},
                    {"number": "2", "title": "Second chapter", "page_start": 11, "page_end": 40}]},
                {"name": "Section A Practice", "part_name": "Part II Practice", "chapters": [
                    {"number": "3", "title": "Third chapter", "page_start": 41, "page_end": 100}]}]}
        return books, contents

    def test_spherical_projection_and_equal_area_cells(self):
        centres = geo.fibonacci_sphere(37)
        np.testing.assert_allclose(np.linalg.norm(centres, axis=1), 1)
        for lat, lon in ((0, 0), (45, -179), (-89, 90)):
            got = geo.vec_to_latlon(geo.latlon_to_vec(lat, lon))
            np.testing.assert_allclose(got, (lat, lon), atol=1e-10)
        points, weights = geo.pixel_grid(360, 180)
        cells = geo.continent_pixels(points, centres)
        areas = np.bincount(cells, weights=weights) / weights.sum()
        self.assertLess(np.max(np.abs(areas - 1 / 37)), 0.002)

    def test_harrison_hub_and_saved_seating_are_stable(self):
        books, _ = self.fixture()
        centres = geo.fibonacci_sphere(3)
        original = copy.deepcopy(books)
        seats = geo.seat_books(books, centres)
        self.assertEqual(seats[0]["book_id"], "HARRISON-22")
        self.assertEqual(seats[0]["seat_index"], int(np.argmax(centres @ geo.latlon_to_vec(0, 0))))
        self.assertEqual(books, original)
        self.assertEqual(geo.seat_books(list(reversed(seats)), centres), seats)
        seats[1]["seat_order"] = seats[0]["seat_order"]
        with self.assertRaisesRegex(ValueError, "invalid saved seat_order"):
            geo.seat_books(seats, centres)

    def test_complete_coverage_area_weights_and_centres_inside_districts(self):
        books, contents = self.fixture()
        result = geo.build(books, contents, 192, 96)
        rows, raster = result["territories"], result["raster"]
        self.assertEqual(len(rows), 18)  # three continents, six provinces, nine districts
        self.assertTrue(np.all(raster > 0))
        districts = [r for r in rows if r["level"] == "district"]
        self.assertEqual(set(np.unique(raster)), {r["raster_code"] for r in districts})
        self.assertAlmostEqual(sum(r["area_fraction"] for r in districts), 1)
        for book in books:
            own = [r for r in districts if r["book_id"] == book["book_id"]]
            total = sum(r["area_fraction"] for r in own)
            for row, expected in zip(own, (0.1, 0.3, 0.6)):
                self.assertAlmostEqual(row["area_fraction"] / total, expected, delta=0.003)
        for row in districts:
            x = int((row["lon"] + 180) / 360 * 192) % 192
            y = min(95, int((90 - row["lat"]) / 180 * 96))
            self.assertEqual(raster[y, x], row["raster_code"])
            self.assertTrue(-90 <= row["lat"] <= 90 and -180 <= row["lon"] <= 180)

    def test_draft_keeps_candidates_and_uses_alphabetical_provisional_ids(self):
        books, contents = self.fixture()
        for book in books:
            book.update(status="candidate", cluster="", field_name="")
        before = copy.deepcopy((books, contents))
        result = geo.build(books, contents, 96, 48, draft=True)
        continents = [r for r in result["territories"] if r["level"] == "continent"]
        self.assertEqual([(r["territory_id"], r["book_id"]) for r in continents],
                         [("C01", "ALPHA-1"), ("C02", "BETA-1"), ("C03", "HARRISON-22")])
        self.assertEqual((books, contents), before)

    def test_dotted_numbers_and_restarts_do_not_collide_or_lose_original_numbers(self):
        books, contents = self.fixture()
        chapters = contents["ALPHA-1"]["provinces"][0]["chapters"]
        chapters[0]["number"], chapters[1]["number"] = "4.2", "42"
        _, rows, _ = geo.make_items(books[2] | {"seat_order": 1}, contents["ALPHA-1"])
        districts = [r for r in rows if r["level"] == "district"]
        self.assertEqual(len({r["territory_id"] for r in districts}), 3)
        self.assertEqual([r["toc_number"] for r in districts], ["4.2", "42", "3"])

    def test_empty_headings_remain_zero_area_without_losing_districts(self):
        books, contents = self.fixture()
        contents["ALPHA-1"]["provinces"].append({"name": "Part III Existing empty heading", "chapters": []})
        result = geo.build(books, contents, 96, 48)
        empty = next(r for r in result["territories"] if r["name"] == "Part III Existing empty heading")
        self.assertEqual(empty["area_fraction"], 0)
        self.assertEqual(empty["page_count"], 0)
        self.assertEqual(len(result["warnings"]), 1)

    def test_insufficient_pixels_fail_instead_of_losing_districts(self):
        books, contents = self.fixture()
        with self.assertRaisesRegex(ValueError, "every district"):
            geo.build(books, contents, 2, 1)

    def test_seam_borders_wrap_longitude_but_not_poles(self):
        pixels = np.array([[1, 1, 2, 2], [1, 1, 2, 2]])
        edges = geo.borders(pixels)
        self.assertTrue(np.all(edges[:, (0, 3)]))
        self.assertFalse(np.any(geo.borders(np.ones((2, 4)))))

    def test_export_roundtrip_matches_viewer_encoding_and_csv(self):
        books, contents = self.fixture()
        result = geo.build(books, contents, 96, 48, draft=True)
        with tempfile.TemporaryDirectory() as temp:
            out = Path(temp)
            manifest = geo.write_outputs(result, out)
            with Image.open(out / "district_raster.png") as image:
                encoded = np.asarray(image, dtype=np.int32)
            np.testing.assert_array_equal(encoded[..., 0] * 256 + encoded[..., 1], result["raster"])
            np.testing.assert_array_equal(np.load(out / "district_raster.npy"), result["raster"])
            lookup = json.loads((out / "districts_lookup.json").read_text())
            with (out / "territories.csv").open() as stream:
                rows = list(csv.DictReader(stream))
            districts = [r for r in rows if r["level"] == "district"]
            self.assertEqual(set(lookup), {r["raster_code"] for r in districts})
            self.assertFalse(manifest["seating_approved"])
            self.assertFalse(manifest["database_loaded"])
            for filename, digest in manifest["files"].items():
                self.assertEqual(hashlib.sha256((out / filename).read_bytes()).hexdigest(), digest)
            with Image.open(out / "continents_texture.png") as image:
                self.assertEqual(image.size, (192, 96))
            with Image.open(out / "continents_texture_2k.png") as image:
                self.assertEqual(image.size, (96, 48))


if __name__ == "__main__":
    unittest.main()
