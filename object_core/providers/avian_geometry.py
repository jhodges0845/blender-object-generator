# SPDX-License-Identifier: GPL-3.0-or-later
"""Connected Avian surface generation."""

from math import cos, pi, sin, sqrt

from ..models import MeshPart, ObjectMesh


_RING_SIDES = 8


def _normalize(vector):
    length = sqrt(sum(value * value for value in vector))
    if length == 0:
        raise ValueError("ring tangent must have nonzero length")
    return tuple(value / length for value in vector)


def _cross(a, b):
    return (
        a[1] * b[2] - a[2] * b[1],
        a[2] * b[0] - a[0] * b[2],
        a[0] * b[1] - a[1] * b[0],
    )


def _subtract(a, b):
    return tuple(a[i] - b[i] for i in range(3))


def _lerp(a, b, amount):
    return tuple(a[i] + (b[i] - a[i]) * amount for i in range(3))


def _ring(center, width, depth, tangent):
    tangent = _normalize(tangent)
    reference = (0.0, 0.0, 1.0)
    if abs(sum(tangent[i] * reference[i] for i in range(3))) > 0.95:
        reference = (0.0, 1.0, 0.0)
    width_axis = _normalize(_cross(reference, tangent))
    depth_axis = _normalize(_cross(tangent, width_axis))
    return tuple(
        tuple(
            center[axis]
            + width_axis[axis] * width * 0.5 * cos(2 * pi * index / _RING_SIDES)
            + depth_axis[axis] * depth * 0.5 * sin(2 * pi * index / _RING_SIDES)
            for axis in range(3)
        )
        for index in range(_RING_SIDES)
    )


def _append_tube(vertices, faces, centers, widths, depths, *, cap_start=True, cap_end=True):
    rings = []
    for index, center in enumerate(centers):
        if index == 0:
            tangent = _subtract(centers[1], center)
        elif index == len(centers) - 1:
            tangent = _subtract(center, centers[index - 1])
        else:
            tangent = _subtract(centers[index + 1], centers[index - 1])
        start = len(vertices)
        vertices.extend(_ring(center, widths[index], depths[index], tangent))
        rings.append(tuple(range(start, start + _RING_SIDES)))

    if cap_start:
        faces.append(tuple(reversed(rings[0])))
    for level in range(len(rings) - 1):
        first, second = rings[level], rings[level + 1]
        for segment in range(_RING_SIDES):
            nxt = (segment + 1) % _RING_SIDES
            faces.append((first[segment], first[nxt], second[nxt], second[segment]))
    if cap_end:
        faces.append(tuple(rings[-1]))
    return rings


def _append_branch(vertices, faces, root, centers, widths, depths):
    if len(root) != 4:
        raise ValueError("branch root must contain four vertices")
    rings = _append_tube(vertices, faces, centers, widths, depths, cap_start=False, cap_end=True)
    first = rings[0]
    for index in range(4):
        root_start = root[index]
        root_end = root[(index + 1) % 4]
        ring_start = first[(2 * index) % _RING_SIDES]
        ring_mid = first[(2 * index + 1) % _RING_SIDES]
        ring_end = first[(2 * index + 2) % _RING_SIDES]
        faces.append((root_start, root_end, ring_end))
        faces.append((root_start, ring_end, ring_mid, ring_start))


def generate_avian_deformable_mesh(dimensions):
    """Return one connected low-poly Avian surface with integrated wings and tail."""
    length = dimensions["body_length_cm"]
    width = dimensions["body_width_cm"]
    height = dimensions["body_height_cm"]
    wingspan = dimensions["wingspan_cm"]
    tail_length = dimensions["tail_length_cm"]

    body_z = height * 0.52
    rear_y = -length * 0.42
    chest_y = length * 0.30
    neck_y = length * 0.48
    head_y = length * 0.63
    beak_y = length * 0.78
    tail_base_y = -length * 0.48
    tail_mid_y = tail_base_y - tail_length * 0.46
    tail_tip_y = tail_base_y - tail_length

    centers = (
        (0.0, tail_tip_y, body_z + height * 0.02),
        (0.0, tail_mid_y, body_z + height * 0.05),
        (0.0, tail_base_y, body_z),
        (0.0, rear_y, body_z),
        (0.0, 0.0, body_z + height * 0.04),
        (0.0, chest_y, body_z + height * 0.08),
        (0.0, neck_y, body_z + height * 0.22),
        (0.0, head_y, body_z + height * 0.31),
        (0.0, beak_y, body_z + height * 0.26),
    )
    widths = (
        width * 0.10, width * 0.18, width * 0.38, width * 0.82,
        width, width * 0.92, width * 0.48, width * 0.60, width * 0.18,
    )
    depths = (
        height * 0.10, height * 0.16, height * 0.28, height * 0.76,
        height, height * 0.88, height * 0.46, height * 0.56, height * 0.20,
    )

    vertices, faces = [], []
    _append_tube(vertices, faces, centers, widths, depths)

    wing_level = 4
    openings = {}
    for side, segment in (("left", 3), ("right", 7)):
        face_index = 1 + wing_level * _RING_SIDES + segment
        openings[side] = faces[face_index]
    removed = {face for face in openings.values()}
    faces = [face for face in faces if face not in removed]

    half_span = wingspan * 0.5
    root_x = width * 0.36
    root_y = length * 0.08
    root_z = body_z + height * 0.14
    for side, sign in (("left", -1.0), ("right", 1.0)):
        shoulder = (sign * root_x, root_y, root_z)
        elbow = (sign * (root_x + (half_span - root_x) * 0.48), root_y - length * 0.06, root_z - height * 0.08)
        tip = (sign * half_span, root_y - length * 0.16, root_z - height * 0.13)
        centers_wing = (
            shoulder,
            _lerp(shoulder, elbow, 0.22),
            elbow,
            _lerp(elbow, tip, 0.20),
            tip,
        )
        base = max(height * 0.20, 1.0)
        widths_wing = (base * 1.12, base, base * 0.84, base * 0.55, base * 0.18)
        depths_wing = (base * 0.78, base * 0.66, base * 0.54, base * 0.34, base * 0.12)
        _append_branch(vertices, faces, openings[side], centers_wing, widths_wing, depths_wing)

    return ObjectMesh((MeshPart("avian", tuple(vertices), tuple(faces)),))
