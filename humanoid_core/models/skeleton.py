"""Immutable skeleton and rigid part bindings, independent of Blender."""

from dataclasses import dataclass
from math import isfinite
from typing import Optional, Tuple

from .mesh import Vertex


@dataclass(frozen=True)
class Bone:
    """Head/tail in world-space rest coordinates (cm); parent names another bone.

    A bound part follows this bone with full weight in the initial rigid rig.
    Unbound bones serve as hierarchy controls. Roll is chosen by the adapter.
    """
    name: str
    head: Vertex
    tail: Vertex
    parent: Optional[str] = None
    part_name: Optional[str] = None

    def __post_init__(self):
        for field in ("name", "parent", "part_name"):
            value = getattr(self, field)
            if value is None and field != "name":
                continue
            if not isinstance(value, str) or not value.strip():
                raise ValueError(field + " must be a nonempty string")
        for field in ("head", "tail"):
            point = tuple(getattr(self, field))
            if len(point) != 3:
                raise ValueError(field + " must have three coordinates")
            if any(isinstance(v, bool) or not isinstance(v, (int, float)) for v in point):
                raise TypeError(field + " must contain numbers")
            try:
                point = tuple(float(v) for v in point)
            except OverflowError:
                raise ValueError(field + " must be finite") from None
            if not all(isfinite(v) for v in point):
                raise ValueError(field + " must be finite")
            object.__setattr__(self, field, point)
        if self.head == self.tail:
            raise ValueError("bone must have nonzero length")


@dataclass(frozen=True)
class Skeleton:
    """A tree in parent-before-child order with at most one binding per part."""
    bones: Tuple[Bone, ...]

    def __post_init__(self):
        bones = tuple(self.bones)
        if not bones:
            raise ValueError("bones must not be empty")
        names, parts = set(), set()
        roots = 0
        for bone in bones:
            if not isinstance(bone, Bone):
                raise TypeError("bones must contain Bone instances")
            if bone.name in names:
                raise ValueError("bone names must be unique")
            if bone.parent is None:
                roots += 1
            elif bone.parent not in names:
                raise ValueError("parent must precede its child")
            names.add(bone.name)
            if bone.part_name is not None:
                if bone.part_name in parts:
                    raise ValueError("part bindings must be unique")
                parts.add(bone.part_name)
        if roots != 1:
            raise ValueError("skeleton must have exactly one root")
        object.__setattr__(self, "bones", bones)
