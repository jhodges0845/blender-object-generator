# SPDX-License-Identifier: GPL-3.0-or-later
"""Dog-specific connected quadruped surface generation."""

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
    """Replace one torso quad with an eight-sided deformable limb chain."""
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


def generate_dog_deformable_mesh(dimensions):
    """Return one connected quadruped mesh shaped by validated Dog dimensions."""
    length = dimensions["body_length_cm"]
    shoulder = dimensions["shoulder_height_cm"]
    width = dimensions["body_width_cm"]
    head_length = dimensions["head_length_cm"]
    tail_length = dimensions["tail_length_cm"]

    torso_height = shoulder * 0.42
    back_z = shoulder - torso_height * 0.30
    belly_z = shoulder - torso_height * 0.72
    body_z = (back_z + belly_z) * 0.5
    fore_y = length * 0.32
    hind_y = -length * 0.32
    leg_height = shoulder - torso_height * 0.45
    side_x = width * 0.34
    knee_z = leg_height * 0.48

    tail_tip = (0.0, -length * 0.5 - tail_length, back_z + torso_height * 0.36)
    tail_mid = (0.0, -length * 0.5 - tail_length * 0.48, back_z + torso_height * 0.22)
    tail_base = (0.0, -length * 0.5, back_z)
    rear = (0.0, -length * 0.42, body_z)
    hind = (0.0, hind_y, body_z)
    mid = (0.0, 0.0, body_z)
    fore = (0.0, fore_y, body_z + torso_height * 0.06)
    chest = (0.0, length * 0.43, body_z + torso_height * 0.16)
    neck = (0.0, length * 0.52, shoulder + torso_height * 0.05)
    head = (0.0, length * 0.5 + head_length * 0.34, shoulder + torso_height * 0.13)
    muzzle = (0.0, length * 0.5 + head_length * 0.82, shoulder + torso_height * 0.06)

    centers = (tail_tip, tail_mid, tail_base, rear, hind, mid, fore, chest, neck, head, muzzle)
    widths = (
        width * 0.08, width * 0.12, width * 0.18,
        width * 0.82, width * 0.96, width, width,
        width * 0.90, width * 0.58, width * 0.72, width * 0.48,
    )
    depths = (
        width * 0.08, width * 0.12, width * 0.18,
        torso_height * 0.82, torso_height, torso_height, torso_height * 1.04,
        torso_height * 0.94, torso_height * 0.62, torso_height * 0.72, torso_height * 0.42,
    )

    vertices, faces = [], []
    rings = _append_tube(vertices, faces, centers, widths, depths)

    # One lateral torso quad per limb becomes the shared seam into that limb.
    openings = {}
    # Body tube side faces start after the initial cap. Each level contributes 8 quads.
    # Segment 3 sits on negative X (left), segment 7 on positive X (right).
    level_by_pair = {"hind": 3, "fore": 5}
    for region, level in level_by_pair.items():
        for side, segment in (("left", 3), ("right", 7)):
            index = 1 + level * _RING_SIDES + segment
            openings[(region, side)] = faces[index]
    removed = {face for face in openings.values()}
    faces = [face for face in faces if face not in removed]

    for side, x in (("left", -side_x), ("right", side_x)):
        for region, y, top_z in (
            ("fore", fore_y, shoulder),
            ("hind", hind_y, shoulder * 0.86),
        ):
            upper = (x, y, top_z)
            knee = (x, y, knee_z)
            ankle = (x, y, max(width * 0.12, 1.5))
            paw = (x, y + width * 0.10, max(width * 0.07, 1.0))
            centers_leg = (
                upper,
                _lerp(upper, knee, 0.18),
                knee,
                _lerp(knee, ankle, 0.18),
                ankle,
                paw,
            )
            base = max(width * 0.18, 2.0)
            widths_leg = (base * 1.12, base, base * 0.88, base * 0.78, base * 0.70, base * 0.94)
            depths_leg = (base * 1.12, base, base * 0.88, base * 0.78, base * 0.70, base * 0.58)
            _append_branch(vertices, faces, openings[(region, side)], centers_leg, widths_leg, depths_leg)

    return ObjectMesh((MeshPart("dog", tuple(vertices), tuple(faces)),))
