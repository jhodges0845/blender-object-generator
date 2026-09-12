# SPDX-License-Identifier: GPL-3.0-or-later
"""Small host-independent component primitives used by the production workflow.

These are deliberately generic starting assets, not a game-specific catalog.
Coordinates are centimeters, matching the rest of ``object_core``.
"""

from math import cos, pi, sin

from .models import MeshPart, ObjectMesh


def ring_mesh(major_radius=3.0, minor_radius=0.45, major_segments=24, minor_segments=8):
    """Return a lightweight torus suitable as a ring/bracelet accessory starting point."""
    if not isinstance(major_segments, int) or major_segments < 8:
        raise ValueError("major_segments must be an integer of at least 8")
    if not isinstance(minor_segments, int) or minor_segments < 3:
        raise ValueError("minor_segments must be an integer of at least 3")
    if major_radius <= 0 or minor_radius <= 0 or minor_radius >= major_radius:
        raise ValueError("ring radii must be positive and minor_radius must be smaller than major_radius")

    vertices = []
    faces = []
    for major_index in range(major_segments):
        major_angle = 2.0 * pi * major_index / major_segments
        c_major, s_major = cos(major_angle), sin(major_angle)
        for minor_index in range(minor_segments):
            minor_angle = 2.0 * pi * minor_index / minor_segments
            radial = major_radius + minor_radius * cos(minor_angle)
            vertices.append((
                radial * c_major,
                radial * s_major,
                minor_radius * sin(minor_angle),
            ))

    for major_index in range(major_segments):
        next_major = (major_index + 1) % major_segments
        for minor_index in range(minor_segments):
            next_minor = (minor_index + 1) % minor_segments
            a = major_index * minor_segments + minor_index
            b = next_major * minor_segments + minor_index
            c = next_major * minor_segments + next_minor
            d = major_index * minor_segments + next_minor
            faces.append((a, b, c, d))

    return ObjectMesh((MeshPart("Ring", tuple(vertices), tuple(faces)),))


__all__ = ["ring_mesh"]
