"""Honeycomb geometry/ownership invariants; artificial chapter metadata only."""

import contextlib
import copy
import io
import unittest
from collections import Counter

import numpy as np

import geography as geo
from geography_honeycomb import build, rasterize
from honeycomb_mesh import dual_mesh
from honeycomb_partition import components, transport


class ClosedHoneycombTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.mesh = dual_mesh(4763)

    def test_exact_chapter_count_and_only_hexagons_pentagons(self):
        self.assertEqual(Counter(map(len, self.mesh['polygons'])), {6: 4751, 5: 12})
        self.assertEqual(len(self.mesh['vertices']), 2 * 4763 - 4)
        self.assertEqual(len(self.mesh['edges']), 3 * 4763 - 6)
        self.assertTrue(all(len(faces) == 2 for faces in self.mesh['edges'].values()))

    def test_neighbors_share_one_identical_whole_edge(self):
        polygons = self.mesh['polygons']
        for i, neighbors in enumerate(self.mesh['adjacent']):
            self.assertEqual(len(neighbors), len(polygons[i]))
            for other in neighbors:
                self.assertIn(i, self.mesh['adjacent'][other])
                self.assertEqual(len(set(polygons[i]) & set(polygons[other])), 2)

    def test_real_spherical_areas_are_nearly_equal_and_cover_sphere(self):
        areas = self.mesh['areas']
        self.assertAlmostEqual(float(areas.sum()), 4 * np.pi, places=9)
        self.assertLess(float(areas.std() / areas.mean()), 0.02)
        self.assertGreater(float(areas.min() / areas.mean()), 0.70)
        self.assertLess(float(areas.max() / areas.mean()), 1.12)

    def test_small_mesh_and_polygon_raster_have_no_missing_or_cut_tiles(self):
        mesh = dual_mesh(83)
        raster, points, weights, ties = rasterize(mesh, 256, 128)
        self.assertEqual(set(np.unique(raster)), set(range(83)))
        self.assertEqual(ties, 0)
        self.assertEqual(Counter(map(len, mesh['polygons'])), {6: 71, 5: 12})
        for i, p in enumerate(mesh['points']):
            lat, lon = geo.vec_to_latlon(p)
            x = min(255, int((lon + 180) / 360 * 256))
            y = min(127, int((90 - lat) / 180 * 128))
            self.assertEqual(raster[y * 256 + x], i)

    def test_capacity_assignment_is_integral_and_exact(self):
        points = self.mesh['points'][:50]
        labels = transport(points, points[[0, 20, 40]], [7, 18, 25])
        np.testing.assert_array_equal(np.bincount(labels), [7, 18, 25])


class ChapterOwnershipTests(unittest.TestCase):
    def fixture(self):
        rows, code = [], 0
        for i, counts in enumerate(([40, 12, 1, 0], [10, 20]), 1):
            cid, bid = f'C{i:02d}', f'SYNTHETIC-{i}'
            lon = -65 if i == 1 else 95
            rows.append(geo.territory(cid, 'continent', bid, bid, None, 1, 10000, lat=10, lon=lon, seat_order=i, colour_hex='#aa5555'))
            for j, count in enumerate(counts, 1):
                pid = f'{cid}.P{j:02d}'
                rows.append(geo.territory(pid, 'province', f'Synthetic part {j}', bid, cid, 1 if count else None, 10000 if count else None,
                                          lat=10 + j * 5, lon=lon + j * 4, area_fraction=0, colour_hex='#aa5555'))
                for k in range(count):
                    code += 1
                    rows.append(geo.territory(f'{pid}.D{k + 1:03d}', 'district', f'Synthetic chapter {k + 1}', bid, pid,
                                              1, 10000 if k == 0 else 1, lat=10, lon=lon, colour_hex='#aa5555', raster_code=code, toc_number=k + 1))
        return rows

    def test_identity_hierarchy_page_units_and_ids_survive_equal_tile_rebuild(self):
        source = self.fixture()
        before = copy.deepcopy(source)
        with contextlib.redirect_stdout(io.StringIO()):
            result, topology = build(source, 256, 128)
        self.assertEqual(source, before)
        stable = ['territory_id', 'name', 'book_id', 'parent', 'page_start', 'page_end', 'page_count', 'raster_code', 'toc_number']
        self.assertEqual([{k: r[k] for k in stable} for r in before], [{k: r[k] for k in stable} for r in result['territories']])
        self.assertEqual(len(topology['tiles']), 83)
        self.assertEqual(topology['statistics']['connected_books'], 2)
        self.assertEqual(topology['statistics']['connected_nonempty_provinces'], 5)
        self.assertEqual(len(result['warnings']), 1)
        self.assertTrue(np.all(result['raster'] > 0))

    def test_rebuild_from_installed_coordinates_uses_saved_anchors_deterministically(self):
        with contextlib.redirect_stdout(io.StringIO()):
            first, topology = build(self.fixture(), 256, 128)
            second, repeated = build(first['territories'], 256, 128)
        np.testing.assert_array_equal(first['raster'], second['raster'])
        self.assertEqual(first['territories'], second['territories'])
        self.assertEqual(topology, repeated)


if __name__ == '__main__':
    unittest.main()
