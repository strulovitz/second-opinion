"""Capacity-constrained geographic assignment of fixed honeycomb tiles.

Transportation linear programming assigns exactly the requested number of
tiles. It changes ownership labels, never the mesh or any book contents.
"""

import numpy as np
from scipy.optimize import linprog
from scipy.sparse import coo_matrix

from honeycomb_mesh import require


def components(nodes, adjacent):
    unseen, result = set(map(int, nodes)), []
    while unseen:
        seed = min(unseen)
        unseen.remove(seed)
        found, queue = {seed}, [seed]
        while queue:
            for neighbor in adjacent[queue.pop()] & unseen:
                unseen.remove(neighbor); found.add(neighbor); queue.append(neighbor)
        result.append(found)
    return sorted(result, key=lambda c: (-len(c), min(c)))


def transport(points, anchors, capacities):
    n, k = len(points), len(anchors)
    require(sum(capacities) == n and min(capacities) > 0, "tile capacities do not match the input")
    if k == 1:
        return np.zeros(n, dtype=int)
    cost = 1 - points @ anchors.T
    columns = np.arange(n * k)
    rows = np.r_[np.repeat(np.arange(n), k), n + np.tile(np.arange(k), n)]
    matrix = coo_matrix((np.ones(n * k * 2), (rows, np.tile(columns, 2))), shape=(n + k, n * k)).tocsc()
    solution = linprog(cost.ravel(), A_eq=matrix, b_eq=np.r_[np.ones(n), capacities], bounds=(0, 1), method='highs', options={'time_limit': 90})
    require(solution.success, f"capacity assignment failed: {solution.message}")
    values = solution.x.reshape(n, k)
    require(np.max(np.minimum(np.abs(values), np.abs(values - 1))) < 1e-6, "transport solution is fractional")
    labels = np.argmax(values, axis=1)
    require(np.array_equal(np.bincount(labels, minlength=k), capacities), "transport lost a chapter tile")
    return labels


def repair(labels, nodes, adjacent, costs):
    """Exchange boundary tiles without changing capacities or splitting regions."""
    labels = labels.copy()
    local = {int(node): i for i, node in enumerate(nodes)}
    k = int(labels.max()) + 1

    def groups():
        return [components(nodes[labels == i], adjacent) for i in range(k)]

    def debt(parts):
        return sum(sum(len(c) for c in group[1:]) for group in parts)

    parts = groups()
    for _ in range(len(nodes) * 2):
        if debt(parts) == 0:
            return labels
        options = []
        for owner, group in enumerate(parts):
            if len(group) == 1:
                continue
            main = group[0]
            boundary = {}
            for v in main:
                for w in adjacent[v]:
                    if w in local and labels[local[w]] != owner:
                        boundary.setdefault(int(labels[local[w]]), set()).add(w)
            for island in group[1:]:
                for v in sorted(island):
                    for neighbor in adjacent[v]:
                        if neighbor not in local:
                            continue
                        other = int(labels[local[neighbor]])
                        if other == owner or other not in boundary:
                            continue
                        for w in sorted(boundary[other]):
                            delta = costs[local[v], other] + costs[local[w], owner] - costs[local[v], owner] - costs[local[w], other]
                            options.append((float(delta), owner, other, v, w))
        applied = False
        for _, owner, other, v, w in sorted(options):
            candidate = labels.copy()
            candidate[local[v]], candidate[local[w]] = other, owner
            owner_parts = components(nodes[candidate == owner], adjacent)
            other_parts = components(nodes[candidate == other], adjacent)
            new_parts = list(parts); new_parts[owner] = owner_parts; new_parts[other] = other_parts
            if debt(new_parts) < debt(parts):
                labels, parts, applied = candidate, new_parts, True
                break
        if not applied:
            return None
    return None


def assign(mesh, nodes, anchors, capacities, iterations=4):
    nodes, anchors = np.asarray(nodes, dtype=int), np.asarray(anchors, dtype=float)
    points = mesh['points'][nodes]
    require(len(components(nodes, mesh['adjacent'])) == 1, "parent tile region is disconnected")
    for attempt in range(iterations):
        labels = transport(points, anchors, capacities)
        fixed = repair(labels, nodes, mesh['adjacent'], 1 - points @ anchors.T)
        if fixed is not None:
            require(np.array_equal(np.bincount(fixed, minlength=len(capacities)), capacities), "repair changed tile counts")
            return fixed
        # A deterministic geographic centroid update is a new assignment target,
        # not a force-directed motion of the fixed mesh or viewer positions.
        for i in range(len(anchors)):
            centre = points[labels == i].mean(axis=0)
            anchors[i] = centre / np.linalg.norm(centre)
    counts = [len(components(nodes[labels == i], mesh['adjacent'])) for i in range(len(capacities))]
    raise ValueError(f"could not create connected capacity regions after {iterations} assignments: {counts}")
