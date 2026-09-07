# SPDX-License-Identifier: GPL-3.0-or-later
"""Small Blender-independent topology checks used by geometry generators.

These helpers intentionally inspect topology only. They do not try to repair a
mesh or infer artist intent; geometry producers remain responsible for creating
valid surfaces.
"""

from collections import Counter

from ..models.mesh import MeshPart


def edge_use_counts(part: MeshPart):
    """Return undirected edge -> face-use count for one mesh part."""
    if not isinstance(part, MeshPart):
        raise TypeError("part must be a MeshPart")
    counts = Counter()
    for face in part.faces:
        for index, start in enumerate(face):
            end = face[(index + 1) % len(face)]
            edge = (start, end) if start < end else (end, start)
            counts[edge] += 1
    return dict(counts)


def boundary_edges(part: MeshPart):
    """Return edges used by exactly one face."""
    return tuple(sorted(edge for edge, count in edge_use_counts(part).items() if count == 1))


def nonmanifold_edges(part: MeshPart):
    """Return edges whose face-use count is not exactly two."""
    return tuple(
        sorted((edge, count) for edge, count in edge_use_counts(part).items() if count != 2)
    )


def is_closed_manifold(part: MeshPart) -> bool:
    """Whether every undirected edge is shared by exactly two faces."""
    counts = edge_use_counts(part)
    return bool(counts) and all(count == 2 for count in counts.values())
