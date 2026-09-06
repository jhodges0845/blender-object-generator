# SPDX-License-Identifier: GPL-3.0-or-later
"""Internal capped ring lofts used by the blockout generator."""

from math import cos, sin, pi, hypot

from ..models.mesh import MeshPart


RING_SIDES = 8


def _loft(name, rings):
    """Join equally sized rings ordered along their positive normal."""
    vertices = tuple(vertex for ring in rings for vertex in ring)
    faces = [tuple(reversed(range(RING_SIDES)))]
    for level in range(len(rings) - 1):
        lower = level * RING_SIDES
        upper = lower + RING_SIDES
        for index in range(RING_SIDES):
            next_index = (index + 1) % RING_SIDES
            faces.append((lower + index, lower + next_index,
                          upper + next_index, upper + index))
    faces.append(tuple(range(len(vertices) - RING_SIDES, len(vertices))))
    return MeshPart(name, vertices, tuple(faces))


def vertical_loft(name, sections, center_x=0.0, center_y=0.0):
    """Sections are (z, full width, full depth), from bottom to top."""
    rings = [tuple((center_x + width * 0.5 * cos(2 * pi * i / RING_SIDES),
                    center_y + depth * 0.5 * sin(2 * pi * i / RING_SIDES), z)
                   for i in range(RING_SIDES))
             for z, width, depth in sections]
    return _loft(name, rings)


def limb(name, start, end, start_width, end_width, depth_ratio=1.0):
    """Capped tapered limb along an axis in the XZ plane."""
    dx, dz = end[0] - start[0], end[2] - start[2]
    length = hypot(dx, dz)
    # u cross v follows the limb axis, preserving outward winding on both sides.
    ux, uz = dz / length, -dx / length
    rings = []
    for center, width in ((start, start_width), (end, end_width)):
        ring = []
        for i in range(RING_SIDES):
            angle = 2 * pi * i / RING_SIDES
            across = width * 0.5 * cos(angle)
            forward = width * depth_ratio * 0.5 * sin(angle)
            ring.append((center[0] + ux * across,
                         center[1] + forward, center[2] + uz * across))
        rings.append(tuple(ring))
    return _loft(name, rings)
