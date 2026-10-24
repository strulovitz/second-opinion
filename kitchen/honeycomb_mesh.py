"""Closed spherical honeycomb: an exact tile count, twelve pentagons, no cuts.

The dual of a latitude-ring triangular mesh gives one polygon per vertex.
Concave integer ring populations transport six units of curvature through
each hemisphere. No springs, force-directed layout or clinical data are used.
"""

from itertools import combinations, combinations_with_replacement
import math

import numpy as np


def require(condition, message):
    if not condition:
        raise ValueError(message)


def ring_plan(count):
    """Find six paired slope changes; 2 + sum(t*(R-t)) is the tile count."""
    require(type(count) is int and count >= 32, "honeycomb requires at least 32 tiles")
    estimate = round(math.sqrt(count) * 0.96)
    best = None
    for rings in range(max(6, estimate - 3), estimate + 4):
        half = rings // 2
        amplitude = (count - 2) * math.pi / (2 * rings)
        slope = amplitude * math.pi / rings
        preferred = [max(1, rings / math.pi * math.acos(min(1, (5.5 - i) / slope))) for i in range(6)]
        triples = list(combinations_with_replacement(range(1, half + 1), 3))
        sums = {}
        for triple in triples:
            value = sum(t * (rings - t) for t in triple)
            cost = sum((t - preferred[i]) ** 2 for i, t in enumerate(triple))
            sums.setdefault(value, []).append((cost, triple))
        for values in sums.values():
            values.sort()
        for last in triples:
            wanted = count - 2 - sum(t * (rings - t) for t in last)
            for first_cost, first in sums.get(wanted, []):
                if first[-1] > last[0]:
                    continue
                times = first + last
                cost = first_cost + sum((t - preferred[i + 3]) ** 2 for i, t in enumerate(last))
                cost += (rings - estimate) ** 2 * 2
                candidate = (cost, rings, times)
                if best is None or candidate < best:
                    best = candidate
                break
    require(best is not None, f"no exact honeycomb ring plan for {count} tiles")
    _, rings, times = best
    changes = sorted([*times, *(rings - t for t in times)])
    populations = [6 * r - sum(max(0, r - t) for t in changes) for r in range(1, rings)]
    require(sum(populations) + 2 == count and min(populations) >= 6, "invalid ring populations")
    require(populations[0] == populations[-1] == 6, "polar rings must have six vertices")
    return populations, {"intervals": rings, "slope_changes": changes}


def spread_score(indices, angles):
    if len(indices) < 2:
        return 0.0
    selected = np.sort(angles[list(indices)] % (2 * np.pi))
    gaps = np.diff(np.r_[selected, selected[0] + 2 * np.pi])
    return float(np.var(gaps))


def grow_faces(old, new, splits):
    faces, j = [], 0
    for i, vertex in enumerate(old):
        faces.append((vertex, new[j % len(new)], new[(j + 1) % len(new)]))
        j += 1
        if i in splits:
            faces.append((vertex, new[j % len(new)], new[(j + 1) % len(new)]))
            j += 1
        faces.append((vertex, old[(i + 1) % len(old)], new[j % len(new)]))
    require(j == len(new), "ring band did not close")
    return faces


def triangular_mesh(count):
    populations, plan = ring_plan(count)
    points, faces, old, angles, down = [[0., 0., 1.]], [], None, None, None
    consumed = 1
    for size in populations[:plan['intervals'] // 2]:
        ids = list(range(len(points), len(points) + size))
        z = 1 - 2 * (consumed + size / 2) / count
        if old is None:
            angles = np.arange(size) * 2 * np.pi / size
            faces.extend((0, ids[i], ids[(i + 1) % size]) for i in range(size))
            next_down = np.ones(size, dtype=int)
        else:
            delta = size - len(old)
            allowed = np.flatnonzero(down == 1).tolist()
            require(delta <= len(allowed), "non-concave northern ring")
            splits = min(combinations(allowed, delta), key=lambda s: (spread_score(s, angles), s)) if delta else ()
            splits = set(splits)
            faces.extend(grow_faces(old, ids, splits))
            targets, next_down = [], np.full(size, 2, dtype=int)
            step = 2 * np.pi / len(old)
            for i in range(len(old)):
                targets.append(angles[0] + (i - 0.5) * step)
                if i in splits:
                    next_down[len(targets)] = 1
                    targets.append(angles[i])
            phase = float(np.mean(np.asarray(targets) - np.arange(size) * 2 * np.pi / size))
            angles = phase + np.arange(size) * 2 * np.pi / size
        radius = math.sqrt(1 - z * z)
        points.extend(np.column_stack((radius * np.cos(angles), radius * np.sin(angles), np.full(size, z))))
        consumed += size
        old, down = ids, next_down
    # Mirror the northern triangulation. Sharing its equatorial ring (even R)
    # or stitching two rings (odd R) avoids accumulating seam defects.
    northern_count, northern_faces = len(points), list(faces)
    mapping = {}
    if plan['intervals'] % 2 == 0:
        defects = set(np.flatnonzero(down == 1).tolist())
        shift = next(k for k in range(len(old)) if not defects.intersection({(i + k) % len(old) for i in defects}))
        angle = shift * 2 * np.pi / len(old)
        mapping.update({v: old[(i + shift) % len(old)] for i, v in enumerate(old)})
    else:
        angle = -np.pi / len(old)
    for i in range(northern_count):
        if i in mapping:
            continue
        x, y, z = points[i]
        mapping[i] = len(points)
        points.append([x * math.cos(angle) - y * math.sin(angle), x * math.sin(angle) + y * math.cos(angle), -z])
    faces.extend(tuple(mapping[v] for v in face[::-1]) for face in northern_faces)
    if plan['intervals'] % 2:
        faces.extend(grow_faces(old, [mapping[v] for v in old], set()))
    points, faces = np.asarray(points), np.asarray(faces, dtype=int)
    orientation = np.einsum('ij,ij->i', np.cross(points[faces[:, 1]] - points[faces[:, 0]], points[faces[:, 2]] - points[faces[:, 0]]), points[faces[:, 0]])
    faces[orientation < 0] = faces[orientation < 0, ::-1]
    require(len(points) == count and len(faces) == 2 * count - 4, "mesh Euler count differs")
    return points, faces, plan


def dual_mesh(count):
    points, faces, plan = triangular_mesh(count)
    return dual_from(points, faces, plan)


def dual_from(points, faces, plan=None):
    """Dual polygons of a closed outward triangulation (shared by the Goldberg mesh)."""
    vertices = points[faces].sum(axis=1)
    vertices /= np.linalg.norm(vertices, axis=1)[:, None]
    incident, adjacent = [[] for _ in points], [set() for _ in points]
    edge_faces = {}
    for index, face in enumerate(faces):
        for i, v in enumerate(face):
            incident[v].append(index)
            other = int(face[(i + 1) % 3])
            adjacent[v].add(other); adjacent[other].add(int(v))
            edge_faces.setdefault(tuple(sorted((int(v), other))), []).append(index)
    require(all(len(value) == 2 for value in edge_faces.values()), "mesh has an open or duplicated edge")
    polygons, areas, normals = [], [], []
    for index, ids in enumerate(incident):
        centre = points[index]
        up = np.array([0., 0., 1.]) if abs(centre[2]) < 0.9 else np.array([1., 0., 0.])
        east = np.cross(up, centre); east /= np.linalg.norm(east)
        north = np.cross(centre, east)
        corners = vertices[ids]
        order = np.argsort(np.arctan2(corners @ north, corners @ east))
        ids = np.asarray(ids)[order]; corners = vertices[ids]
        after = np.roll(corners, -1, axis=0)
        planes = np.cross(corners, after)
        planes /= np.linalg.norm(planes, axis=1)[:, None]
        require(np.min(planes @ centre) > 0 and np.min(planes @ corners.T) >= -1e-10, f"non-convex honeycomb tile {index}")
        determinant = np.abs(np.einsum('ij,j->i', np.cross(corners, after), centre))
        denominator = 1 + corners @ centre + after @ centre + np.einsum('ij,ij->i', corners, after)
        areas.append(float(np.sum(2 * np.arctan2(determinant, denominator))))
        polygons.append(ids.tolist()); normals.append(planes)
    degrees = np.array([len(p) for p in polygons])
    require(np.count_nonzero(degrees == 5) == 12 and np.all(np.isin(degrees, (5, 6))), "mesh must contain exactly twelve pentagons and otherwise hexagons")
    require(abs(sum(areas) - 4 * np.pi) < 1e-8, "spherical polygon areas do not cover the globe exactly")
    return {"points": points, "vertices": vertices, "polygons": polygons, "normals": normals,
            "adjacent": adjacent, "areas": np.asarray(areas), "plan": plan,
            "faces": faces, "edges": edge_faces}


if __name__ == '__main__':
    import argparse
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--tiles', type=int, default=4763)
    args = parser.parse_args()
    mesh = dual_mesh(args.tiles)
    areas = mesh['areas'] / (4 * np.pi / args.tiles)
    print({"tiles": args.tiles, "pentagons": 12, "hexagons": args.tiles - 12,
           "area_min_over_mean": float(areas.min()), "area_max_over_mean": float(areas.max()),
           "area_cv": float(areas.std()), "plan": mesh['plan']})
