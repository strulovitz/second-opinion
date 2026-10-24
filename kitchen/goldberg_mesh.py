#!/usr/bin/env python3
"""Amendment 3.6: the Goldberg honeycomb (one regular-looking hexagon per chapter).

A Goldberg polyhedron GP(m, n) is a flat triangular lattice laid on each of the
20 faces of an icosahedron. Its cells are 12 pentagons (at the 12 icosahedron
corners) and 10*T - 10 hexagons, T = m*m + m*n + n*n. GP(16, 9) gives
T = 481 and 4,812 cells: the smallest Goldberg ball with room for 4,763
chapters. The 12 pentagons become non-chapter "poles" and each of the 37 books
gets one non-chapter "name tile" (4,763 + 12 + 37 = 4,812; Nir, 24 Oct 2026).

Steps: (1) lattice points of every face, mapped to the sphere through the flat
face (gnomonic); (2) a few Lloyd steps on the spherical Voronoi diagram, which
evens out tile AREAS while keeping the near-perfect hexagon SHAPES; (3) the
dual of the convex hull gives one convex spherical polygon per lattice point.
Every cell keeps its face number and integer lattice coordinates so the 2-D
"orange peel" map (goldberg_net.py) can draw it as a perfect flat hexagon.
"""

import numpy as np
from scipy.spatial import ConvexHull, SphericalVoronoi

from honeycomb_mesh import dual_from, require

PHI = (1 + 5 ** 0.5) / 2
ICO_VERTICES = np.array([[-1, PHI, 0], [1, PHI, 0], [-1, -PHI, 0], [1, -PHI, 0], [0, -1, PHI], [0, 1, PHI],
                         [0, -1, -PHI], [0, 1, -PHI], [PHI, 0, -1], [PHI, 0, 1], [-PHI, 0, -1], [-PHI, 0, 1]], float)
ICO_VERTICES /= np.linalg.norm(ICO_VERTICES, axis=1)[:, None]
# Counter-clockwise seen from outside; the lattice chirality depends on it.
ICO_FACES = [[0, 11, 5], [0, 5, 1], [0, 1, 7], [0, 7, 10], [0, 10, 11], [1, 5, 9], [5, 11, 4], [11, 10, 2],
             [10, 7, 6], [7, 1, 8], [3, 9, 4], [3, 4, 2], [3, 2, 6], [3, 6, 8], [3, 8, 9], [4, 9, 5],
             [2, 4, 11], [6, 2, 10], [8, 6, 7], [9, 8, 1]]
SQRT3 = 3 ** 0.5


def axial_to_xy(axial):
    """Axial lattice (i, j) -> plane, basis e1 = (1, 0), e2 = (1/2, sqrt(3)/2)."""
    axial = np.asarray(axial, float)
    return np.stack([axial[..., 0] + axial[..., 1] / 2, axial[..., 1] * SQRT3 / 2], axis=-1)


def face_corners(m, n):
    """Integer axial corners of one face: 0, (m, n) and (m, n) turned by 60 degrees."""
    return np.array([[0, 0], [m, n], [-n, m + n]])


def lattice_points(m, n):
    corners = axial_to_xy(face_corners(m, n))
    inverse = np.linalg.inv(np.array([corners[1], corners[2]]).T)
    found = []
    for i in range(-n - 1, m + 2):
        for j in range(0, m + n + 2):
            b = inverse @ axial_to_xy([i, j])
            if min(1 - b.sum(), b[0], b[1]) > 1e-9:
                found.append((i, j, 1 - b.sum(), b[0], b[1]))
    require(len(found) == (m * m + m * n + n * n - 1) // 2, "wrong number of interior lattice points")
    return found


def spherical_centroids(points):
    voronoi = SphericalVoronoi(points)
    voronoi.sort_vertices_of_regions()
    result = np.empty_like(points)
    for k, region in enumerate(voronoi.regions):
        corners, g = voronoi.vertices[region], points[k]
        after = np.roll(corners, -1, axis=0)
        weights = np.linalg.norm(np.cross(corners - g, after - g), axis=1)
        total = (weights[:, None] * (g + corners + after)).sum(axis=0)
        result[k] = total / np.linalg.norm(total)
    return result


def goldberg_mesh(m=16, n=9, lloyd=40):
    """The closed Goldberg mesh, in the dict format of honeycomb_mesh.dual_mesh."""
    rows = lattice_points(m, n)
    points, face_of, lattice = [*ICO_VERTICES], [-1] * 12, [(0, 0)] * 12
    for f, (a, b, c) in enumerate(ICO_FACES):
        for i, j, wa, wb, wc in rows:
            p = wa * ICO_VERTICES[a] + wb * ICO_VERTICES[b] + wc * ICO_VERTICES[c]
            points.append(p / np.linalg.norm(p)); face_of.append(f); lattice.append((i, j))
    points = np.array(points)
    require(len(points) == 10 * (m * m + m * n + n * n) + 2, "Goldberg cell count is wrong")
    for _ in range(lloyd):
        points = spherical_centroids(points)
    faces = ConvexHull(points).simplices
    normal = np.cross(points[faces[:, 1]] - points[faces[:, 0]], points[faces[:, 2]] - points[faces[:, 0]])
    flip = np.einsum('ij,ij->i', normal, points[faces].mean(axis=1)) < 0
    faces[flip] = faces[flip][:, [0, 2, 1]]
    mesh = dual_from(points, faces, plan={'goldberg': [m, n], 'lloyd_steps': lloyd})
    pentagons = [i for i, p in enumerate(mesh['polygons']) if len(p) == 5]
    require(pentagons == list(range(12)), "Lloyd steps moved a pentagon away from an icosahedron corner")
    mesh.update(face_of=np.array(face_of), lattice=np.array(lattice), pentagons=pentagons, m=m, n=n,
                ico_vertices=ICO_VERTICES, ico_faces=np.array(ICO_FACES))
    check_lattice(mesh)
    return mesh


def check_lattice(mesh):
    """Inside one face, sphere neighbours must be lattice neighbours (no flipped diagonal)."""
    unit = {(1, 0), (0, 1), (-1, 1), (-1, 0), (0, -1), (1, -1)}
    for a, neighbours in enumerate(mesh['adjacent']):
        for b in neighbours:
            if mesh['face_of'][a] == mesh['face_of'][b] >= 0:
                d = tuple(int(x) for x in mesh['lattice'][b] - mesh['lattice'][a])
                require(d in unit, f"cells {a} and {b} are neighbours on the sphere but not in the lattice")


def regularity(mesh):
    """Hexagon shape and size statistics, measured in each tile's tangent plane."""
    ratios, errors = [], []
    for index, ids in enumerate(mesh['polygons']):
        if len(ids) != 6:
            continue
        c = mesh['points'][index]
        east = np.cross([0., 0., 1.] if abs(c[2]) < 0.9 else [1., 0., 0.], c); east /= np.linalg.norm(east)
        north = np.cross(c, east)
        q = np.stack([mesh['vertices'][ids] @ east, mesh['vertices'][ids] @ north], axis=1)
        sides = np.linalg.norm(np.roll(q, -1, axis=0) - q, axis=1)
        a, b = np.roll(q, 1, axis=0) - q, np.roll(q, -1, axis=0) - q
        angles = np.degrees(np.arccos(np.clip(np.einsum('ij,ij->i', a, b) / np.linalg.norm(a, axis=1) / np.linalg.norm(b, axis=1), -1, 1)))
        ratios.append(sides.min() / sides.max()); errors.append(np.abs(angles - 120).max())
    ratios, errors = np.array(ratios), np.array(errors)
    hexagons = np.array([len(p) == 6 for p in mesh['polygons']])
    area = mesh['areas'][hexagons] / mesh['areas'][hexagons].mean()
    return {'hexagons': int(hexagons.sum()), 'pentagons': int((~hexagons).sum()),
            'side_ratio_median': float(np.median(ratios)), 'side_ratio_worst': float(ratios.min()),
            'corner_error_deg_median': float(np.median(errors)), 'corner_error_deg_p95': float(np.percentile(errors, 95)),
            'corner_error_deg_worst': float(errors.max()), 'hexagon_area_min_over_mean': float(area.min()),
            'hexagon_area_max_over_mean': float(area.max()), 'hexagon_area_cv': float(area.std())}


if __name__ == '__main__':
    import argparse
    import json
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--lloyd', type=int, default=40)
    args = parser.parse_args()
    print(json.dumps(regularity(goldberg_mesh(lloyd=args.lloyd)), indent=1))
