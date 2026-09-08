# SPDX-License-Identifier: GPL-3.0-or-later
"""Portable material and image-texture intent with no host dependencies."""

from dataclasses import dataclass
from math import isfinite
from typing import Optional, Tuple


Color = Tuple[float, float, float, float]


@dataclass(frozen=True)
class ImageTextureSpec:
    """Small generated RGBA image data that host adapters can materialize."""

    name: str
    width: int
    height: int
    pixels: Tuple[float, ...]

    def __post_init__(self) -> None:
        if not isinstance(self.name, str) or not self.name.strip():
            raise ValueError("texture name must be a nonempty string")
        for label, value in (("width", self.width), ("height", self.height)):
            if isinstance(value, bool) or not isinstance(value, int):
                raise TypeError(label + " must be an integer")
            if value <= 0:
                raise ValueError(label + " must be positive")
        pixels = tuple(self.pixels)
        if len(pixels) != self.width * self.height * 4:
            raise ValueError("texture pixels must contain width * height * 4 RGBA values")
        if any(isinstance(value, bool) or not isinstance(value, (int, float)) for value in pixels):
            raise TypeError("texture pixels must be numbers")
        normalized = tuple(float(value) for value in pixels)
        if any(not isfinite(value) or value < 0.0 or value > 1.0 for value in normalized):
            raise ValueError("texture pixels must be finite and between 0 and 1")
        object.__setattr__(self, "pixels", normalized)


@dataclass(frozen=True)
class MaterialSpec:
    """A conservative PBR material that common game exporters can translate."""

    name: str
    part_names: Tuple[str, ...]
    base_color: Color
    metallic: float = 0.0
    roughness: float = 0.65
    base_color_texture: Optional[ImageTextureSpec] = None

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
        if self.base_color_texture is not None and not isinstance(self.base_color_texture, ImageTextureSpec):
            raise TypeError("base_color_texture must be ImageTextureSpec or None")
        object.__setattr__(self, "part_names", parts)
        object.__setattr__(self, "base_color", normalized[:4])
        object.__setattr__(self, "metallic", normalized[4])
        object.__setattr__(self, "roughness", normalized[5])
