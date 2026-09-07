# SPDX-License-Identifier: GPL-3.0-or-later
"""Immutable Blender-independent skinning data."""

from dataclasses import dataclass
from math import isfinite
from typing import Tuple


@dataclass(frozen=True)
class BoneWeight:
    """One normalized bone influence for a mesh vertex."""
    bone_name: str
    weight: float

    def __post_init__(self):
        if not isinstance(self.bone_name, str) or not self.bone_name.strip():
            raise ValueError("bone_name must be a nonempty string")
        if isinstance(self.weight, bool) or not isinstance(self.weight, (int, float)):
            raise TypeError("weight must be numeric")
        weight = float(self.weight)
        if not isfinite(weight) or weight <= 0.0 or weight > 1.0:
            raise ValueError("weight must be finite and in (0, 1]")
        object.__setattr__(self, "weight", weight)


@dataclass(frozen=True)
class SkinWeights:
    """Per-vertex influences for exactly one mesh part."""
    part_name: str
    vertices: Tuple[Tuple[BoneWeight, ...], ...]

    def __post_init__(self):
        if not isinstance(self.part_name, str) or not self.part_name.strip():
            raise ValueError("part_name must be a nonempty string")
        vertices = tuple(tuple(influences) for influences in self.vertices)
        if not vertices:
            raise ValueError("vertices must not be empty")
        for influences in vertices:
            if not influences:
                raise ValueError("every vertex must have at least one influence")
            if any(not isinstance(influence, BoneWeight) for influence in influences):
                raise TypeError("vertex influences must contain BoneWeight instances")
            names = [influence.bone_name for influence in influences]
            if len(names) != len(set(names)):
                raise ValueError("a bone may influence a vertex only once")
            if abs(sum(influence.weight for influence in influences) - 1.0) > 1e-6:
                raise ValueError("vertex weights must sum to 1")
        object.__setattr__(self, "vertices", vertices)
