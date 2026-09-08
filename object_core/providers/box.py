# SPDX-License-Identifier: GPL-3.0-or-later
"""Static Box provider implementation."""

from math import isfinite

from ..models import MeshPart, ObjectMesh
from .base import Parameter


class BoxProvider:
    key, label = "box", "Box"
    supports_rig = supports_idle = uses_skin_weights = False
    parameters = tuple(
        Parameter(key, label, 100, 1, 1000)
        for key, label in (
            ("width_cm", "Width (cm)"),
            ("depth_cm", "Depth (cm)"),
            ("height_cm", "Height (cm)"),
        )
    )

    def mesh(self, values):
        dimensions = []
        for field in self.parameters:
            value = values[field.key]
            if isinstance(value, bool) or not isinstance(value, (int, float)):
                raise TypeError(field.label + " must be a number")
            if not isfinite(value) or not field.minimum <= value <= field.maximum:
                raise ValueError(field.label + " is outside its supported range")
            dimensions.append(value)

        width, depth, height = dimensions
        vertices = (
            (-width / 2, -depth / 2, 0),
            (width / 2, -depth / 2, 0),
            (width / 2, depth / 2, 0),
            (-width / 2, depth / 2, 0),
            (-width / 2, -depth / 2, height),
            (width / 2, -depth / 2, height),
            (width / 2, depth / 2, height),
            (-width / 2, depth / 2, height),
        )
        faces = (
            (3, 2, 1, 0),
            (4, 5, 6, 7),
            (0, 1, 5, 4),
            (1, 2, 6, 5),
            (2, 3, 7, 6),
            (3, 0, 4, 7),
        )
        return ObjectMesh((MeshPart("box", vertices, faces),))
