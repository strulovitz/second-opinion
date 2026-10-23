#!/usr/bin/env python3
"""Amendment 3.5: one whole, near-equal-area hexagon/pentagon per chapter.

Read the saved geography as identity/hierarchy input. Build a candidate under
ignored logs first; no source list, PDF, Neo4j or model is modified or loaded.
"""

import argparse
import copy
import hashlib
import json
import shutil
from datetime import datetime, timezone
from pathlib import Path

import numpy as np
from scipy.spatial import cKDTree

import geography as geo
from honeycomb_mesh import dual_mesh, require
from honeycomb_partition import assign

ROOT = Path(__file__).resolve().parents[1]


def rasterize(mesh, width, height):
    points, weights = geo.pixel_grid(width, height)
    tree = cKDTree(mesh['points'])
    planes = np.zeros((len(mesh['points']), 6, 3))
    for i, normals in enumerate(mesh['normals']):
        planes[i, :len(normals)] = normals
    raster = np.empty(len(points), dtype=np.int32)
    ambiguities = 0
    for start in range(0, len(points), 32768):
        batch = points[start:start + 32768]
        near = tree.query(batch, k=8, workers=2)[1]
        inside = np.all(np.einsum('bi,bkji->bkj', batch, planes[near]) >= -1e-12, axis=2)
        require(np.all(inside.any(axis=1)), "polygon raster has an uncovered pixel")
        ambiguities += int(np.count_nonzero(inside.sum(axis=1) > 1))
        raster[start:start + len(batch)] = near[np.arange(len(batch)), np.argmax(inside, axis=1)]
    require(len(np.unique(raster)) == len(mesh['points']), "raster resolution lost a chapter tile")
    return raster, points, weights, ambiguities


def centre_of(nodes, mesh):
    direction = mesh['points'][nodes].mean(axis=0)
    return int(nodes[np.argmax(mesh['points'][nodes] @ direction)])


def build(source, width=geo.W, height=geo.H):
    rows = copy.deepcopy(source)
    by_id = {r['territory_id']: r for r in rows}
    districts = [r for r in rows if r['level'] == 'district']
    books = [r for r in rows if r['level'] == 'continent']
    for row in rows:
        if row['level'] != 'district':
            row.setdefault('layout_anchor_lat', row['lat'])
            row.setdefault('layout_anchor_lon', row['lon'])
    require(len(by_id) == len(rows) and all(r['parent'] is None or r['parent'] in by_id for r in rows), "invalid source hierarchy")
    require(len(districts) <= 65535, "district codes exceed R*256+G")
    print(f"Building the closed {len(districts)}-tile honeycomb", flush=True)
    mesh = dual_mesh(len(districts))
    capacities = [sum(r['book_id'] == b['book_id'] for r in districts) for b in books]
    anchors = np.array([geo.latlon_to_vec(b['layout_anchor_lat'], b['layout_anchor_lon']) for b in books])
    book_labels = assign(mesh, np.arange(len(districts)), anchors, capacities)
    tile_rows = [None] * len(districts)
    for i, book in enumerate(books):
        nodes = np.flatnonzero(book_labels == i)
        provinces = [r for r in rows if r['level'] == 'province' and r['parent'] == book['territory_id']]
        active = [p for p in provinces if any(d['parent'] == p['territory_id'] for d in districts)]
        counts = [sum(d['parent'] == p['territory_id'] for d in districts) for p in active]
        targets = np.array([geo.latlon_to_vec(p['layout_anchor_lat'], p['layout_anchor_lon']) for p in active])
        labels = assign(mesh, nodes, targets, counts)
        for j, province in enumerate(active):
            tiles = nodes[labels == j]
            centre = mesh['points'][centre_of(tiles, mesh)]
            x, y = geo.local_xy(mesh['points'][tiles], centre)
            # Fixed north/south rows with east/west order give a
            # readable deterministic chapter sweep within each province.
            order = np.lexsort((x, -np.round(y / 0.04)))
            children = [d for d in districts if d['parent'] == province['territory_id']]
            for tile, district in zip(tiles[order], children):
                tile_rows[int(tile)] = district
                district['tile_sides'] = len(mesh['polygons'][tile])
                district['lat'], district['lon'] = geo.vec_to_latlon(mesh['points'][tile])
        for parent in [book, *provinces]:
            members = nodes if parent['level'] == 'continent' else np.array([n for n in nodes if tile_rows[int(n)] and tile_rows[int(n)]['parent'] == parent['territory_id']], dtype=int)
            if len(members):
                parent['lat'], parent['lon'] = geo.vec_to_latlon(mesh['points'][centre_of(members, mesh)])
            else:
                parent['lat'], parent['lon'] = book['lat'], book['lon']
        print(f"Assigned {book['book_id']}: {len(nodes)} whole tiles; {len(active)} connected provinces", flush=True)
    require(all(tile_rows), "unassigned honeycomb chapter")
    print("Rasterising shared polygon borders", flush=True)
    tile_raster, pixels, weights, ambiguities = rasterize(mesh, width, height)
    codes = np.array([r['raster_code'] for r in tile_rows], dtype=np.int32)
    raster = codes[tile_raster]
    sums = np.bincount(tile_raster, weights=weights, minlength=len(districts)) / weights.sum()
    # Sort pixel IDs once, rather than scanning the entire raster per chapter.
    pixel_order = np.argsort(tile_raster, kind='stable')
    offsets = np.r_[0, np.cumsum(np.bincount(tile_raster, minlength=len(districts))) ]
    for tile, district in enumerate(tile_rows):
        own = pixel_order[offsets[tile]:offsets[tile + 1]]
        district['area_fraction'] = float(sums[tile])
        district['bbox_px'] = [int((own % width).min()), int((own // width).min()), int((own % width).max()), int((own // width).max())]
        x = min(width - 1, int((district['lon'] + 180) / 360 * width))
        y = min(height - 1, int((90 - district['lat']) / 180 * height))
        if raster[y * width + x] != district['raster_code']:
            best = own[np.argmax(pixels[own] @ mesh['points'][tile])]
            district['lat'], district['lon'] = geo.vec_to_latlon(pixels[best])
    for parent in (r for r in rows if r['level'] != 'district'):
        children = [d for d in districts if (d['parent'] == parent['territory_id'] if parent['level'] == 'province' else d['book_id'] == parent['book_id'])]
        parent['area_fraction'] = sum(d['area_fraction'] for d in children)
    relative = mesh['areas'] / (4 * np.pi / len(districts))
    stats = {'tiles': len(districts), 'hexagons': len(districts) - 12, 'pentagons': 12,
             'spherical_area_cv': float(relative.std()), 'area_min_over_mean': float(relative.min()),
             'area_max_over_mean': float(relative.max()), 'raster_boundary_ties': ambiguities,
             'connected_books': len(books), 'connected_nonempty_provinces': sum(r['level'] == 'province' and r['area_fraction'] > 0 for r in rows),
             'whole_shared_edges': True, 'one_tile_per_chapter': True, 'amendment': '3.5'}
    topology = {'vertices_xyz': mesh['vertices'].round(12).tolist(), 'tiles': [
        {'territory_id': row['territory_id'], 'vertices': mesh['polygons'][i],
         'neighbors': [tile_rows[n]['territory_id'] for n in sorted(mesh['adjacent'][i])],
         'area_fraction': float(mesh['areas'][i] / (4 * np.pi))} for i, row in enumerate(tile_rows)], 'statistics': stats}
    warnings = [f"{r['territory_id']}: existing empty heading retained with zero area" for r in rows if r['level'] == 'province' and r['area_fraction'] == 0]
    result = {'territories': rows, 'raster': raster.reshape(height, width),
              'continents': book_labels[tile_raster].reshape(height, width), 'seating': [],
              'warnings': warnings, 'draft': False, 'width': width, 'height': height}
    return result, topology


def install(candidate, source, run, root=ROOT):
    """Back up both old maps before installing the tested, unfrozen candidate."""
    candidate = Path(candidate)
    manifest = json.loads((candidate / 'build.json').read_text())
    require(manifest.get('layout') == 'chapter-honeycomb', 'not a honeycomb candidate')
    for name, digest in manifest['files'].items():
        require(hashlib.sha256((candidate / name).read_bytes()).hexdigest() == digest, f'candidate hash changed: {name}')
    require(hashlib.sha256(source.read_bytes()).hexdigest() == manifest['source_sha256'], 'source geography changed while building')
    old, new = json.loads(source.read_text()), json.loads((candidate / 'geography.json').read_text())
    keys = ('territory_id', 'level', 'name', 'book_id', 'parent', 'page_start', 'page_end', 'page_count', 'part_name', 'raster_code', 'seat_order', 'toc_number', 'colour_hex')
    require([{k: r.get(k) for k in keys} for r in old] == [{k: r.get(k) for k in keys} for r in new], 'candidate changed a source identity, hierarchy, title or page bound')
    freeze = run("MATCH (m:Meta {key:'skeleton_frozen'}) RETURN m.value AS value")
    require(freeze == [{'value': 'false'}], 'missing or frozen skeleton; stop for human decision')
    require(run('MATCH (t:Territory) RETURN count(t) AS n') == [{'n': 0}], 'Neo4j already has territories; stop before changing the shared geography')
    backup = root / 'kitchen/logs' / ('before-honeycomb-' + datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%S%fZ'))
    backup.mkdir()
    export, public = root / 'data/export/geography', root / 'site/data/geography'
    shutil.copytree(export, backup / 'export-geography')
    shutil.copytree(public, backup / 'site-geography')
    try:
        for path in candidate.iterdir():
            if path.is_file():
                shutil.copy2(path, export / path.name)
        for name in ('geography.json', 'districts_lookup.json', 'district_raster.png', 'continents_texture.png', 'continents_texture_2k.png', 'honeycomb.json'):
            shutil.copy2(candidate / name, public / name)
    except Exception:
        shutil.copytree(backup / 'export-geography', export, dirs_exist_ok=True)
        shutil.copytree(backup / 'site-geography', public, dirs_exist_ok=True)
        raise
    print(f'Installed the tested honeycomb candidate. Old map backup: {backup}')
    print('Visual approval pending; Neo4j unchanged and not frozen.')
    return backup


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--source', type=Path, default=ROOT / 'data/export/geography/geography.json')
    parser.add_argument('--out', type=Path, default=ROOT / 'kitchen/logs/honeycomb-candidate')
    parser.add_argument('--install', action='store_true', help='install an already-built candidate after identity/hash/freeze checks and an old-map backup')
    args = parser.parse_args()
    try:
        if args.install:
            from db import run
            install(args.out, args.source, run)
            return
        require(args.out.resolve() not in ((ROOT / 'data/export/geography').resolve(), (ROOT / 'site/data/geography').resolve()),
                'build into a candidate directory first; use --install for a backed-up installation')
        source = json.loads(args.source.read_text())
        result, topology = build(source)
        seating = args.source.parent / 'seating-proposal.json'
        if seating.exists():
            result['seating'] = json.loads(seating.read_text())
        manifest = geo.write_outputs(result, args.out)
        raw = json.dumps(topology, separators=(',', ':')) + '\n'
        (args.out / 'honeycomb.json').write_text(raw)
        manifest.update(layout='chapter-honeycomb', amendment='3.5', geometry_review_pending=True,
                        honeycomb=topology['statistics'], source_sha256=hashlib.sha256(args.source.read_bytes()).hexdigest())
        manifest['files']['honeycomb.json'] = hashlib.sha256(raw.encode()).hexdigest()
        (args.out / 'build.json').write_text(json.dumps(manifest, indent=2) + '\n')
        print(json.dumps(topology['statistics'], indent=2))
        print(f"Candidate: {args.out}; no source book or database changed")
    except (ValueError, KeyError, OSError) as error:
        parser.exit(1, f"NOT BUILT: {error}\n")


if __name__ == '__main__':
    main()
