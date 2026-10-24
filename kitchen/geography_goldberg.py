#!/usr/bin/env python3
"""Amendment 3.6: build the Goldberg honeycomb geography (candidate first).

4,812 Goldberg cells = 4,763 chapter hexagons + 37 book name tiles + 12
pentagon poles. Identity, hierarchy, titles, page bounds, raster codes,
colours and seat order are copied verbatim from the installed geography;
only coordinates, tile ownership and areas change. The old layout anchors
keep every book near its approved place. No PDF, Neo4j or model is touched
while building; --install backs up both live map folders first.
"""

import argparse
import copy
import hashlib
import json
import shutil
from collections import deque
from pathlib import Path

import numpy as np

import geography as geo
from geography_honeycomb import centre_of, install, rasterize
from goldberg_mesh import goldberg_mesh, regularity
import flower_map
from honeycomb_mesh import require
from honeycomb_partition import assign, components

ROOT = Path(__file__).resolve().parents[1]
LAYOUT = 'goldberg-honeycomb'


def name_tile(nodes, mesh):
    """The deepest tile of a book: farthest (in steps) from the book's border."""
    inside = set(map(int, nodes))
    depth, queue = {}, deque()
    for v in inside:
        if any(w not in inside for w in mesh['adjacent'][v]):
            depth[v] = 0; queue.append(v)
    while queue:
        v = queue.popleft()
        for w in mesh['adjacent'][v]:
            if w in inside and w not in depth:
                depth[w] = depth[v] + 1; queue.append(w)
    direction = mesh['points'][list(inside)].mean(axis=0)
    ranked = sorted(inside, key=lambda v: (-depth.get(v, 0), -float(mesh['points'][v] @ direction), v))
    for v in ranked:
        rest = np.array(sorted(inside - {v}))
        if len(components(rest, mesh['adjacent'])) == 1:
            return v
    raise ValueError('no name tile keeps the book connected')


def build(source, lloyd=40, width=geo.W, height=geo.H):
    rows = copy.deepcopy(source)
    by_id = {r['territory_id']: r for r in rows}
    districts = [r for r in rows if r['level'] == 'district']
    books = [r for r in rows if r['level'] == 'continent']
    require(len(by_id) == len(rows) and all(r['parent'] is None or r['parent'] in by_id for r in rows), 'invalid source hierarchy')
    for row in rows:
        if row['level'] != 'district':
            row.setdefault('layout_anchor_lat', row['lat'])
            row.setdefault('layout_anchor_lon', row['lon'])
    mesh = goldberg_mesh(lloyd=lloyd)
    cells = len(mesh['points'])
    require(cells == len(districts) + len(books) + 12, f'{cells} Goldberg cells do not equal chapters + books + 12 poles')
    print(f'Goldberg GP(16,9): {cells} cells for {len(districts)} chapters, {len(books)} name tiles, 12 poles', flush=True)
    usable = np.array([i for i in range(cells) if i not in mesh['pentagons']])
    capacities = [sum(d['book_id'] == b['book_id'] for d in districts) + 1 for b in books]
    anchors = np.array([geo.latlon_to_vec(b['layout_anchor_lat'], b['layout_anchor_lon']) for b in books])
    book_labels = assign(mesh, usable, anchors, capacities)
    owner = [None] * cells          # ('district', row) | ('name', book row) | ('pole', None)
    for p in mesh['pentagons']:
        owner[p] = ('pole', None)
    cell_book = np.full(cells, -1)
    for i, book in enumerate(books):
        nodes = usable[book_labels == i]
        cell_book[nodes] = i
        capital = name_tile(nodes, mesh)
        owner[capital] = ('name', book)
        book['name_tile_lat'], book['name_tile_lon'] = geo.vec_to_latlon(mesh['points'][capital])
        book['lat'], book['lon'] = book['name_tile_lat'], book['name_tile_lon']
        nodes = nodes[nodes != capital]
        provinces = [r for r in rows if r['level'] == 'province' and r['parent'] == book['territory_id']]
        active = [p for p in provinces if any(d['parent'] == p['territory_id'] for d in districts)]
        counts = [sum(d['parent'] == p['territory_id'] for d in districts) for p in active]
        targets = np.array([geo.latlon_to_vec(p['layout_anchor_lat'], p['layout_anchor_lon']) for p in active])
        labels = assign(mesh, nodes, targets, counts)
        for j, province in enumerate(active):
            tiles = nodes[labels == j]
            x, y = geo.local_xy(mesh['points'][tiles], mesh['points'][centre_of(tiles, mesh)])
            order = np.lexsort((x, -np.round(y / 0.044)))   # rows about one tile high, read west to east
            children = [d for d in districts if d['parent'] == province['territory_id']]
            for tile, district in zip(tiles[order], children):
                owner[int(tile)] = ('district', district)
                district['tile_sides'] = 6
                district['lat'], district['lon'] = geo.vec_to_latlon(mesh['points'][tile])
            province['lat'], province['lon'] = geo.vec_to_latlon(mesh['points'][centre_of(tiles, mesh)])
        for province in provinces:
            if province not in active:
                province['lat'], province['lon'] = book['lat'], book['lon']
        print(f"Assigned {book['book_id']}: {len(nodes)} chapter hexagons + 1 name tile; {len(active)} connected provinces", flush=True)
    require(all(owner), 'unassigned Goldberg cell')
    require(sum(o[0] == 'district' for o in owner) == len(districts), 'a chapter has no tile')
    print('Rasterising the spherical polygons', flush=True)
    cell_raster, pixels, weights, ties = rasterize(mesh, width, height)
    codes = np.array([o[1]['raster_code'] if o[0] == 'district' else 0 for o in owner], dtype=np.int32)
    raster = codes[cell_raster]
    pixel_order = np.argsort(cell_raster, kind='stable')
    offsets = np.r_[0, np.cumsum(np.bincount(cell_raster, minlength=cells))]
    for cell, (kind, row) in enumerate(owner):
        if kind != 'district':
            continue
        own = pixel_order[offsets[cell]:offsets[cell + 1]]
        row['area_fraction'] = float(mesh['areas'][cell] / (4 * np.pi))
        row['bbox_px'] = [int((own % width).min()), int((own // width).min()), int((own % width).max()), int((own // width).max())]
        x = min(width - 1, int((row['lon'] + 180) / 360 * width)); y = min(height - 1, int((90 - row['lat']) / 180 * height))
        if raster[y * width + x] != row['raster_code']:
            best = own[np.argmax(pixels[own] @ mesh['points'][cell])]
            row['lat'], row['lon'] = geo.vec_to_latlon(pixels[best])
    for parent in (r for r in rows if r['level'] != 'district'):
        children = [d for d in districts if (d['parent'] == parent['territory_id'] if parent['level'] == 'province' else d['book_id'] == parent['book_id'])]
        parent['area_fraction'] = sum(d['area_fraction'] for d in children)
    book_ids = [b['book_id'] for b in books]
    stats = regularity(mesh) | {
        'cells': cells, 'chapter_tiles': len(districts), 'name_tiles': len(books), 'poles': 12,
        'goldberg': [mesh['m'], mesh['n']], 'lloyd_steps': lloyd, 'raster_boundary_ties': ties,
        'connected_books': sum(len(components(np.flatnonzero(cell_book == i), mesh['adjacent'])) == 1 for i in range(len(books))),
        'amendment': '3.6'}
    tiles = []
    for cell, (kind, row) in enumerate(owner):
        tile = {'kind': kind, 'territory_id': row['territory_id'] if row else None,
                'book_id': row['book_id'] if row else None, 'vertices': mesh['polygons'][cell],
                'centre_xyz': mesh['points'][cell].round(9).tolist(),
                'neighbors': sorted(int(w) for w in mesh['adjacent'][cell])}
        tiles.append(tile)
    topology = {'format': 'goldberg-honeycomb-2', 'note': 'Amendment 3.6. kind: district | name | pole. '
                'vertices are indices into vertices_xyz (counter-clockwise seen from outside); '
                'neighbors are tile indices; centre_xyz is the tile centre on the unit sphere.',
                'vertices_xyz': mesh['vertices'].round(12).tolist(), 'tiles': tiles, 'books': book_ids, 'statistics': stats}
    result = {'territories': rows, 'raster': raster.reshape(height, width),
              'continents': cell_book[cell_raster].reshape(height, width), 'seating': [],
              'warnings': [f"{r['territory_id']}: existing empty heading retained with zero area" for r in rows if r['level'] == 'province' and r['area_fraction'] == 0],
              'draft': False, 'width': width, 'height': height}
    return result, topology, mesh


def write_flowers(territories, topology, folder):
    """One flower 2-D map per book (the book you look at sits in the middle)."""
    folder.mkdir(parents=True, exist_ok=True)
    order = [r['territory_id'] for r in territories if r['level'] == 'district']
    for book in topology['books']:
        layout = flower_map.flower_map(territories, topology, book)
        compact = {'format': 'flower-map-1', 'view_book': book,
                   'note': 'xy[i] is the hexagon centre of the i-th district of geography.json (file order), in tile spacings, y up.',
                   'xy': [layout['districts'][d] for d in order], 'books': layout['books'], 'flowers': layout['flowers'],
                   'width': round(layout['width'], 3), 'height': round(layout['height'], 3)}
        (folder / f'{book}.json').write_text(json.dumps(compact, separators=(',', ':')) + '\n')
        if book == 'HARRISON-22':
            flower_map.preview(territories, layout, folder.parent / 'flowers-preview.png', title='Looking at: Internal Medicine (general)')
    print(f"Wrote {len(topology['books'])} flower maps", flush=True)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--source', type=Path, default=ROOT / 'data/export/geography/geography.json')
    parser.add_argument('--out', type=Path, default=ROOT / 'kitchen/logs/goldberg-candidate')
    parser.add_argument('--lloyd', type=int, default=40)
    parser.add_argument('--install', action='store_true', help='install an already-built candidate (backs up the old map first)')
    args = parser.parse_args()
    try:
        if args.install:
            from db import run
            install(args.out, args.source, run, layout=LAYOUT)
            for target in (ROOT / 'data/export/geography/flowers', ROOT / 'site/data/geography/flowers'):
                shutil.copytree(args.out / 'flowers', target, dirs_exist_ok=True)
            print('Installed the 37 flower maps')
            return
        require(args.out.resolve() not in ((ROOT / 'data/export/geography').resolve(), (ROOT / 'site/data/geography').resolve()),
                'build into a candidate directory first; use --install for a backed-up installation')
        result, topology, mesh = build(json.loads(args.source.read_text()), lloyd=args.lloyd)
        seating = args.source.parent / 'seating-proposal.json'
        if seating.exists():
            result['seating'] = json.loads(seating.read_text())
        manifest = geo.write_outputs(result, args.out)
        raw = json.dumps(topology, separators=(',', ':')) + '\n'
        (args.out / 'honeycomb.json').write_text(raw)
        manifest.update(layout=LAYOUT, amendment='3.6', geometry_review_pending=True, seating_approved=False,
                        approved_by_human=False, honeycomb=topology['statistics'],
                        source_sha256=hashlib.sha256(args.source.read_bytes()).hexdigest())
        manifest['files']['honeycomb.json'] = hashlib.sha256(raw.encode()).hexdigest()
        (args.out / 'build.json').write_text(json.dumps(manifest, indent=2) + '\n')
        write_flowers(result['territories'], topology, args.out / 'flowers')
        print(json.dumps(topology['statistics'], indent=1))
        print(f'Candidate: {args.out}; no source book or database changed')
    except (ValueError, KeyError, OSError) as error:
        parser.exit(1, f'NOT BUILT: {error}\n')


if __name__ == '__main__':
    main()
