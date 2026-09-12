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


def hair_shell_mesh(width_cm=18.0, depth_cm=20.0, cap_height_cm=12.0, back_length_cm=18.0,
                    radial_segments=16, cap_segments=5):
    """Return a lightweight hair-cap shell with an optional simple back section.

    The shell is intentionally inexpensive and unrigged. It is a starting asset
    for Static/Rigid use and can later be replaced or adopted into richer motion
    behavior without changing the component workflow.
    """
    dimensions = (width_cm, depth_cm, cap_height_cm)
    if any(value <= 0 for value in dimensions) or back_length_cm < 0:
        raise ValueError("hair dimensions must be positive and back length cannot be negative")
    if not isinstance(radial_segments, int) or radial_segments < 8:
        raise ValueError("radial_segments must be an integer of at least 8")
    if not isinstance(cap_segments, int) or cap_segments < 2:
        raise ValueError("cap_segments must be an integer of at least 2")

    radius_x = width_cm / 2.0
    radius_y = depth_cm / 2.0
    vertices = [(0.0, 0.0, cap_height_cm)]
    faces = []

    # Concentric elliptical rings from crown to scalp rim.
    for ring_index in range(1, cap_segments + 1):
        polar = (pi / 2.0) * ring_index / cap_segments
        ring_z = cap_height_cm * cos(polar)
        scale = sin(polar)
        for segment in range(radial_segments):
            angle = 2.0 * pi * segment / radial_segments
            vertices.append((
                radius_x * scale * cos(angle),
                radius_y * scale * sin(angle),
                ring_z,
            ))

    first_ring = 1
    for segment in range(radial_segments):
        next_segment = (segment + 1) % radial_segments
        faces.append((0, first_ring + segment, first_ring + next_segment))

    for ring_index in range(cap_segments - 1):
        current = 1 + ring_index * radial_segments
        following = current + radial_segments
        for segment in range(radial_segments):
            next_segment = (segment + 1) % radial_segments
            faces.append((
                current + segment,
                following + segment,
                following + next_segment,
                current + next_segment,
            ))

    # Cheap long-hair fallback: a back curtain connected to the rear quarter of
    # the scalp rim. +Y is forward, so the rear rim is centered on -Y.
    if back_length_cm > 0:
        rim_start = 1 + (cap_segments - 1) * radial_segments
        back_indices = [
            segment for segment in range(radial_segments)
            if sin(2.0 * pi * segment / radial_segments) <= -0.5
        ]
        lower = {}
        for segment in back_indices:
            upper = vertices[rim_start + segment]
            lower[segment] = len(vertices)
            vertices.append((upper[0], upper[1], -back_length_cm))
        for segment, next_segment in zip(back_indices, back_indices[1:]):
            faces.append((
                rim_start + segment,
                lower[segment],
                lower[next_segment],
                rim_start + next_segment,
            ))

    return ObjectMesh((MeshPart("Hair", tuple(vertices), tuple(faces)),))


__all__ = ["hair_shell_mesh", "ring_mesh"]
