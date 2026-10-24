#!/usr/bin/env python3
"""Nir's "flower" 2-D map (24 Oct 2026), computed for one viewing direction.

Every book is ONE rounded blob of chapter hexagons, never split. Books are
grouped into "flowers": a centre book (the pollen) with some of its globe
neighbours (the petals) touching it around its rim, in the directions they
have on the globe. Flowers do not touch each other. A book with no room for
petals is a lonely pollen. Another viewing direction gives another grouping.

Method, all deterministic:
 1. Azimuthal equidistant projection of the book centres around the viewing
    direction (the map spreads to all sides of the point you look at).
 2. Books in order of distance from that point; an unassigned book becomes a
    pollen and takes unassigned neighbours as petals while their angular
    widths 2*asin(r / (R + r)) still fit around its rim (R, r = blob radii).
 3. Each flower is drawn on its own hexagon lattice: the pollen is the disk of
    its n nearest cells; every petal is a disk tangent to the pollen, filled
    by a capacity-limited nearest-centre assignment (round, never overlapping).
 4. Flowers start at their projected places and are pushed apart until there
    is at least GAP between any two, then pulled inward while they stay clear.
 5. Inside a blob the chapters run clockwise in book order, so every Part
    (province) is one pie slice.
"""

import json
from pathlib import Path

import numpy as np
from scipy.spatial import cKDTree

SQRT3 = 3 ** 0.5
CELL_AREA = SQRT3 / 2      # hexagon area for unit centre spacing
GAP = 3.5                  # empty space between flowers, in tile spacings


def blob_radius(n):
    return float(np.sqrt(n * CELL_AREA / np.pi))


def lattice(radius):
    k = int(radius / 0.85) + 2
    i, j = np.meshgrid(np.arange(-k, k + 1), np.arange(-k, k + 1))
    xy = np.stack([i.ravel() + j.ravel() / 2, j.ravel() * SQRT3 / 2], axis=1)
    return xy[np.hypot(*xy.T) <= radius]


def book_graph(topology):
    tiles = topology['tiles']
    shared = {}
    for tile in tiles:
        for other in tile['neighbors']:
            a, b = tile['book_id'], tiles[other]['book_id']
            if a and b and a != b:
                shared[(a, b)] = shared.get((a, b), 0) + 1
    return shared


def project(directions, view):
    view = view / np.linalg.norm(view)
    up = np.array([0., 1., 0.]) if abs(view[1]) < 0.95 else np.array([1., 0., 0.])
    east = np.cross(up, view); east /= np.linalg.norm(east)
    north = np.cross(view, east)
    theta = np.arccos(np.clip(directions @ view, -1, 1))
    bearing = np.arctan2(directions @ north, directions @ east)
    return np.stack([theta * np.cos(bearing), theta * np.sin(bearing)], axis=1), theta


def spread_angles(angles, widths, rounds=400):
    """Move petal directions apart on the circle until neighbours do not overlap."""
    order = np.argsort(angles)
    a, w = np.array(angles)[order], np.array(widths)[order]
    for _ in range(rounds):
        moved = False
        for i in range(len(a)):
            j = (i + 1) % len(a)
            if len(a) == 1:
                break
            gap = (a[j] - a[i]) % (2 * np.pi)
            need = (w[i] + w[j]) / 2
            if gap < need - 1e-9:
                push = (need - gap) / 2
                a[i] -= push; a[j] += push; moved = True
        if not moved:
            break
    out = np.empty_like(a); out[order] = a
    return out


def make_flowers(books, counts, positions, theta, shared):
    order = sorted(range(len(books)), key=lambda i: (theta[i], books[i]))
    index = {b: i for i, b in enumerate(books)}
    taken, flowers = set(), []
    for p in order:
        if p in taken:
            continue
        taken.add(p)
        R = blob_radius(counts[p]) + 0.5
        neighbours = sorted({index[b] for (a, b) in shared if a == books[p]} - taken,
                            key=lambda q: (-shared[(books[p], books[q])], books[q]))
        petals, used = [], 0.0
        for q in neighbours:
            r = blob_radius(counts[q]) + 0.5
            width = 2 * np.arcsin((r - 0.2) / (R + r - 0.5)) + 0.6 / (R + r - 0.5)
            if used + width <= 2 * np.pi:
                petals.append(q); used += width; taken.add(q)
        flowers.append({'pollen': p, 'petals': petals})
    return flowers


def draw_flower(flower, counts, positions):
    p = flower['pollen']
    R = blob_radius(counts[p])
    radii = {q: blob_radius(counts[q]) for q in flower['petals']}
    angles, widths = [], []
    for q in flower['petals']:
        d = positions[q] - positions[p]
        angles.append(np.arctan2(d[1], d[0]))
        widths.append(2 * np.arcsin((radii[q] + 0.3) / (R + radii[q])) + 0.6 / (R + radii[q]))
    angles = spread_angles(angles, widths) if angles else []
    extent = R + 2 * max(radii.values(), default=0) + 4
    grid = lattice(extent)
    owner = np.full(len(grid), -1)
    near = np.argsort(np.hypot(*grid.T) + 1e-6 * np.arctan2(grid[:, 1], grid[:, 0]), kind='stable')
    owner[near[:counts[p]]] = p
    centres = {}
    for q, a in zip(flower['petals'], angles):
        centres[q] = (R + radii[q] - 0.1) * np.array([np.cos(a), np.sin(a)])   # tangent: the petal touches the pollen
    pairs = []
    for q, c in centres.items():
        d = np.hypot(*(grid - c).T) / max(radii[q], 0.6)
        for k in np.flatnonzero(d < 2.2):
            pairs.append((d[k], q, int(k)))
    left = {q: counts[q] for q in centres}
    for _, q, k in sorted(pairs):
        if owner[k] == -1 and left[q] > 0:
            owner[k] = q; left[q] -= 1
    if any(left.values()):
        raise ValueError(f'flower of book {p} could not fit its petals')
    keep = owner >= 0
    return grid[keep], owner[keep]


def min_distance(a, b):
    return float(cKDTree(a).query(b, k=1)[0].min())


def place(flowers, cells, targets):
    offsets = [t.copy() for t in targets]
    n = len(flowers)
    def clear(i, j):
        return min_distance(cells[i] + offsets[i], cells[j] + offsets[j]) >= GAP
    for _ in range(300):
        moved = False
        for i in range(n):
            for j in range(i + 1, n):
                a, b = cells[i] + offsets[i], cells[j] + offsets[j]
                d = min_distance(a, b)
                if d < GAP:
                    v = offsets[j] - offsets[i]
                    v = v / (np.linalg.norm(v) or 1)
                    step = (GAP - d) / 2 + 0.3
                    offsets[i] -= v * step; offsets[j] += v * step; moved = True
        if not moved:
            break
    # Pull every flower towards the middle while it stays clear of the others.
    for _ in range(60):
        moved = False
        for i in sorted(range(n), key=lambda k: np.linalg.norm(offsets[k])):
            r = np.linalg.norm(offsets[i])
            if r < 1:
                continue
            old = offsets[i].copy()
            offsets[i] = old * max(0, 1 - 1.0 / r)
            if all(clear(i, j) for j in range(n) if j != i):
                moved = True
            else:
                offsets[i] = old
        if not moved:
            break
    return offsets


def flower_map(territories, topology, view_book):
    books = [r['book_id'] for r in territories if r['level'] == 'continent']
    tiles = topology['tiles']
    counts = [sum(t['kind'] == 'district' and t['book_id'] == b for t in tiles) for b in books]
    direction = np.array([next(t['centre_xyz'] for t in tiles if t['kind'] == 'name' and t['book_id'] == b) for b in books])
    view = direction[books.index(view_book)]
    projected, theta = project(direction, view)
    shared = book_graph(topology)
    flowers = make_flowers(books, counts, projected, theta, shared)
    total = sum(counts) * CELL_AREA
    scale = np.sqrt(total / np.pi) * 1.25 / np.pi
    positions = projected * scale
    drawn = [draw_flower(f, counts, positions) for f in flowers]
    targets = [positions[f['pollen']] for f in flowers]
    offsets = place(flowers, [c for c, _ in drawn], targets)
    by_book = {}
    for (cells, owner), offset in zip(drawn, offsets):
        for b in set(owner.tolist()):
            by_book[books[b]] = cells[owner == b] + offset
    districts = [r for r in territories if r['level'] == 'district']
    placed = {}
    for book, cells in by_book.items():
        centre = cells.mean(axis=0)
        angle = (np.pi / 2 - np.arctan2(*(cells - centre).T[::-1])) % (2 * np.pi)   # clockwise from north
        radius = np.hypot(*(cells - centre).T)
        order = np.lexsort((radius, np.round(angle, 6)))
        rows = [d for d in districts if d['book_id'] == book]
        for row, k in zip(rows, order):
            placed[row['territory_id']] = cells[k]
    xy = np.array(list(placed.values()))
    low = xy.min(axis=0) - 2
    return {'view_book': view_book,
            'districts': {k: [round(float(v[0] - low[0]), 4), round(float(v[1] - low[1]), 4)] for k, v in placed.items()},
            'books': {b: [round(float(c[0] - low[0]), 4), round(float(c[1] - low[1]), 4)] for b, c in ((b, by_book[b].mean(axis=0)) for b in books)},
            'flowers': [{'pollen': books[f['pollen']], 'petals': [books[q] for q in f['petals']]} for f in flowers],
            'width': float(xy[:, 0].max() - low[0] + 2), 'height': float(xy[:, 1].max() - low[1] + 2)}


def preview(territories, layout, path, scale=7.0, title=None):
    import matplotlib
    matplotlib.use('Agg')
    import matplotlib.pyplot as plt
    from matplotlib.collections import LineCollection, PolyCollection
    by_id = {r['territory_id']: r for r in territories}
    names = {r['book_id']: r['name'] for r in territories if r['level'] == 'continent'}
    hexagon = np.array([[np.cos(a), np.sin(a)] for a in np.radians(np.arange(6) * 60 + 30)]) / SQRT3
    polys, colours, lines = [], [], []
    keys = list(layout['districts'])
    tree = cKDTree(np.array([layout['districts'][k] for k in keys]))
    def book_at(xy):
        d, i = tree.query(xy)
        return by_id[keys[i]]['book_id'] if d < 0.1 else None
    for key, xy in layout['districts'].items():
        c = np.array(xy); book = by_id[key]['book_id']
        polys.append(c + hexagon); colours.append(by_id[key]['colour_hex'])
        for a in np.radians(np.arange(6) * 60):
            d = np.array([np.cos(a), np.sin(a)])
            if book_at(c + d) != book:
                mid, perp = c + d / 2, np.array([-d[1], d[0]]) / (2 * SQRT3)
                lines.append([mid - perp, mid + perp])
    w, h = layout['width'], layout['height']
    fig = plt.figure(figsize=(w / scale, h / scale), dpi=110)
    axis = fig.add_axes([0, 0, 1, 1]); fig.patch.set_facecolor('#0b1020'); axis.set_facecolor('#0b1020')
    axis.add_collection(PolyCollection(polys, facecolors=colours, edgecolors='#00000040', linewidths=0.25))
    axis.add_collection(LineCollection(lines, colors='#fbf7ea', linewidths=1.5, capstyle='round'))
    for book, xy in layout['books'].items():
        axis.text(*xy, names[book], ha='center', va='center', fontsize=6.5, color='white', weight='bold',
                  bbox={'facecolor': '#000000a0', 'edgecolor': 'none', 'pad': 1.2})
    if title:
        axis.text(1.5, h - 2, title, color='#cfd6e6', fontsize=9, va='top')
    axis.set_xlim(0, w); axis.set_ylim(0, h); axis.set_aspect('equal'); axis.axis('off')
    fig.savefig(path, facecolor=fig.get_facecolor()); plt.close(fig)


if __name__ == '__main__':
    import argparse
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--geography', type=Path, required=True, help='folder with geography.json and honeycomb.json')
    parser.add_argument('--view', default='HARRISON-22', help='book_id at the centre of the view')
    parser.add_argument('--out', type=Path, required=True)
    args = parser.parse_args()
    rows = json.loads((args.geography / 'geography.json').read_text())
    topo = json.loads((args.geography / 'honeycomb.json').read_text())
    result = flower_map(rows, topo, args.view)
    name = next(r['name'] for r in rows if r['level'] == 'continent' and r['book_id'] == args.view)
    preview(rows, result, args.out, title=f'Looking at: {name}')
    print(json.dumps({'flowers': len(result['flowers']), 'lonely': sum(not f['petals'] for f in result['flowers']),
                      'size': [round(result['width']), round(result['height'])]}))
