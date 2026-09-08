# SPDX-License-Identifier: GPL-3.0-or-later
"""Portable material intent with no host-application dependencies."""

from dataclasses import dataclass
from math import isfinite
from typing import Tuple


Color = Tuple[float, float, float, float]


@dataclass(frozen=True)
class MaterialSpec:
    """A conservative PBR material that common game exporters can translate."""

    name: str
    part_names: Tuple[str, ...]
    base_color: Color
    metallic: float = 0.0
    roughness: float = 0.65

    def __post_init__(self) -> None:
        if not isinstance(self.name, str) or not self.name.strip():
            raise ValueError("material name must be a nonempty string")
        parts = tuple(self.part_names)
        if not parts or any(not isinstance(name, str) or not name.strip() for name in parts):
            raise ValueError("material part_names must contain nonempty strings")
        if len(set(parts)) != len(parts):
            raise ValueError("material part_names must be unique")
        color = tuple(self.base_color)
        if len(color) != 4:
            raise ValueError("base_color must contain RGBA values")
        values = color + (self.metallic, self.roughness)
        if any(isinstance(value, bool) or not isinstance(value, (int, float)) for value in values):
            raise TypeError("material values must be numbers")
        normalized = tuple(float(value) for value in values)
        if any(not isfinite(value) or value < 0.0 or value > 1.0 for value in normalized):
            raise ValueError("material values must be finite and between 0 and 1")
        object.__setattr__(self, "part_names", parts)
        object.__setattr__(self, "base_color", normalized[:4])
        object.__setattr__(self, "metallic", normalized[4])
        object.__setattr__(self, "roughness", normalized[5])
