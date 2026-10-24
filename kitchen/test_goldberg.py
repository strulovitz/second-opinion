"""Amendment 3.6 (Opus 5.5): checks of the installed Goldberg geography and flower maps.

These read the INSTALLED files in site/data/geography/ (no rebuild, no Neo4j), so
any later model that changes the map must keep all of them green.
"""

import json
import unittest
from collections import deque
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parents[1]
GEO = ROOT / 'site/data/geography'


class InstalledGoldberg(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.rows = json.loads((GEO / 'geography.json').read_text())
        cls.topology = json.loads((GEO / 'honeycomb.json').read_text())
        cls.tiles = cls.topology['tiles']
        cls.books = [r['book_id'] for r in cls.rows if r['level'] == 'continent']
        cls.districts = [r for r in cls.rows if r['level'] == 'district']

    def test_counts_and_kinds(self):
        self.assertEqual(self.topology['format'], 'goldberg-honeycomb-2')
        kinds = [t['kind'] for t in self.tiles]
        self.assertEqual(len(self.tiles), 4812)
        self.assertEqual(kinds.count('district'), len(self.districts))
        self.assertEqual(kinds.count('name'), len(self.books))
        self.assertEqual(kinds.count('pole'), 12)
        for t in self.tiles:
            self.assertEqual(len(t['vertices']), 5 if t['kind'] == 'pole' else 6, 'every chapter and name tile is a hexagon')

    def test_every_chapter_exactly_once(self):
        ids = [t['territory_id'] for t in self.tiles if t['kind'] == 'district']
        self.assertEqual(sorted(ids), sorted(d['territory_id'] for d in self.districts))
        names = [t['book_id'] for t in self.tiles if t['kind'] == 'name']
        self.assertEqual(sorted(names), sorted(self.books))

    def test_books_connected_on_the_ball(self):
        for book in self.books:
            own = {i for i, t in enumerate(self.tiles) if t['book_id'] == book}
            seen, queue = {min(own)}, deque([min(own)])
            while queue:
                for n in self.tiles[queue.popleft()]['neighbors']:
                    if n in own and n not in seen:
                        seen.add(n); queue.append(n)
            self.assertEqual(seen, own, f'{book} is split on the globe')

    def test_hexagons_are_regular(self):
        stats = self.topology['statistics']
        self.assertGreater(stats['side_ratio_median'], 0.93)
        self.assertLess(stats['corner_error_deg_median'], 4.0)
        self.assertLess(stats['corner_error_deg_worst'], 10.0)
        self.assertGreater(stats['hexagon_area_min_over_mean'], 0.74)


class InstalledFlowers(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.rows = json.loads((GEO / 'geography.json').read_text())
        cls.books = [r['book_id'] for r in cls.rows if r['level'] == 'continent']
        cls.district_book = [r['book_id'] for r in cls.rows if r['level'] == 'district']

    def test_each_flower_map(self):
        from scipy.spatial import cKDTree
        for view in self.books:
            layout = json.loads((GEO / 'flowers' / f'{view}.json').read_text())
            xy = np.array(layout['xy'])
            self.assertEqual(len(xy), len(self.district_book))
            tree = cKDTree(xy)
            self.assertGreater(tree.query(xy, k=2)[0][:, 1].min(), 0.99, f'{view}: two hexagons overlap')
            flower_of = {}
            for k, f in enumerate(layout['flowers']):
                for b in [f['pollen'], *f['petals']]:
                    self.assertNotIn(b, flower_of, f'{view}: {b} in two flowers'); flower_of[b] = k
            self.assertEqual(set(flower_of), set(self.books))
            pairs = tree.query_pairs(1.01)
            adjacent = {}
            for a, b in pairs:
                adjacent.setdefault(a, set()).add(b); adjacent.setdefault(b, set()).add(a)
                fa, fb = flower_of[self.district_book[a]], flower_of[self.district_book[b]]
                self.assertEqual(fa, fb, f'{view}: two flowers touch')
            for book in self.books:          # every book is ONE blob in the 2-D map (Nir: never split)
                own = {i for i, b in enumerate(self.district_book) if b == book}
                seen, queue = {min(own)}, deque([min(own)])
                while queue:
                    for n in adjacent.get(queue.popleft(), ()):
                        if n in own and n not in seen:
                            seen.add(n); queue.append(n)
                self.assertEqual(seen, own, f'{view}: {book} is split in the flower map')


if __name__ == '__main__':
    unittest.main()
