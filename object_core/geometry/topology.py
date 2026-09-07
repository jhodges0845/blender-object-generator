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


def connected_surface_count(part: MeshPart) -> int:
    """Return the number of face-connected surface islands in a mesh part."""
    if not isinstance(part, MeshPart):
        raise TypeError("part must be a MeshPart")
    edge_faces = {}
    for face_index, face in enumerate(part.faces):
        for index, start in enumerate(face):
            end = face[(index + 1) % len(face)]
            edge = (start, end) if start < end else (end, start)
            edge_faces.setdefault(edge, []).append(face_index)
    neighbors = [set() for _ in part.faces]
    for face_indices in edge_faces.values():
        for face_index in face_indices:
            neighbors[face_index].update(other for other in face_indices if other != face_index)
    unseen = set(range(len(part.faces)))
    components = 0
    while unseen:
        components += 1
        stack = [unseen.pop()]
        while stack:
            current = stack.pop()
            adjacent = neighbors[current] & unseen
            unseen.difference_update(adjacent)
            stack.extend(adjacent)
    return components


def is_closed_manifold(part: MeshPart) -> bool:
    """Whether the part is one closed surface with two faces per edge."""
    counts = edge_use_counts(part)
    return (
        bool(counts)
        and all(count == 2 for count in counts.values())
        and connected_surface_count(part) == 1
    )
