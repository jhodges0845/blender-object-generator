# SPDX-License-Identifier: GPL-3.0-or-later
"""Host-independent Dog/quadruped provider foundation."""

from math import isfinite

from ..models import MeshPart, ObjectMesh
from .base import Parameter


DOG_PARAMETERS = (
    Parameter("body_length_cm", "Body Length (cm)", 70, 25, 140),
    Parameter("shoulder_height_cm", "Shoulder Height (cm)", 55, 15, 100),
    Parameter("body_width_cm", "Body Width (cm)", 24, 8, 55),
    Parameter("head_length_cm", "Head Length (cm)", 24, 8, 45),
    Parameter("tail_length_cm", "Tail Length (cm)", 35, 5, 80),
)


def _box(name, center, size):
    cx, cy, cz = center
    sx, sy, sz = size
    x0, x1 = cx - sx / 2, cx + sx / 2
    y0, y1 = cy - sy / 2, cy + sy / 2
    z0, z1 = cz - sz / 2, cz + sz / 2
    vertices = (
        (x0, y0, z0), (x1, y0, z0), (x1, y1, z0), (x0, y1, z0),
        (x0, y0, z1), (x1, y0, z1), (x1, y1, z1), (x0, y1, z1),
    )
    faces = (
        (3, 2, 1, 0), (4, 5, 6, 7), (0, 1, 5, 4),
        (1, 2, 6, 5), (2, 3, 7, 6), (3, 0, 4, 7),
    )
    return MeshPart(name, vertices, faces)


class DogProvider:
    """Editable quadruped blockout used to prove non-Human provider boundaries."""

    key, label = "dog", "Dog"
    supports_rig = supports_idle = supports_locomotion = False
    uses_skin_weights = supports_materials = False
    parameters = DOG_PARAMETERS

    def mesh(self, values):
        dimensions = {}
        for field in self.parameters:
            value = values[field.key]
            if isinstance(value, bool) or not isinstance(value, (int, float)):
                raise TypeError(field.label + " must be a number")
            if not isfinite(value) or not field.minimum <= value <= field.maximum:
                raise ValueError(field.label + " is outside its supported range")
            dimensions[field.key] = float(value)

        length = dimensions["body_length_cm"]
        shoulder = dimensions["shoulder_height_cm"]
        width = dimensions["body_width_cm"]
        head_length = dimensions["head_length_cm"]
        tail_length = dimensions["tail_length_cm"]

        torso_height = shoulder * 0.42
        torso_z = shoulder - torso_height * 0.48
        head_z = shoulder + torso_height * 0.12
        head_y = length * 0.5 + head_length * 0.28
        muzzle_y = head_y + head_length * 0.42
        leg_height = shoulder - torso_height * 0.45
        leg_width = max(width * 0.18, 2.0)
        fore_y = length * 0.32
        hind_y = -length * 0.32

        parts = [
            _box("dog_torso", (0, 0, torso_z), (width, length, torso_height)),
            _box("dog_head", (0, head_y, head_z),
                 (width * 0.78, head_length * 0.72, torso_height * 0.72)),
            _box("dog_muzzle", (0, muzzle_y, head_z - torso_height * 0.08),
                 (width * 0.56, head_length * 0.46, torso_height * 0.42)),
        ]

        for side, x in (("left", -width * 0.34), ("right", width * 0.34)):
            parts.append(_box("dog_foreleg_" + side, (x, fore_y, leg_height / 2),
                              (leg_width, leg_width, leg_height)))
            parts.append(_box("dog_hindleg_" + side, (x, hind_y, leg_height / 2),
                              (leg_width, leg_width, leg_height)))

        tail_segment = max(tail_length / 3, 2.0)
        tail_width = max(width * 0.14, 1.5)
        tail_base_y = -length * 0.5 - tail_segment * 0.35
        for index in range(3):
            parts.append(_box(
                "dog_tail_%d" % (index + 1),
                (0, tail_base_y - index * tail_segment * 0.75,
                 torso_z + torso_height * (0.2 + index * 0.16)),
                (tail_width, tail_segment, tail_width),
            ))

        return ObjectMesh(tuple(parts))
