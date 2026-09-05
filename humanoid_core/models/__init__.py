"""Shared, software-independent character data contracts."""

from .spec import BodyType, HumanoidSpec
from .proportions import HumanoidProportions
from .mesh import HumanoidMesh, MeshPart

__all__ = ["BodyType", "HumanoidSpec", "HumanoidProportions", "HumanoidMesh", "MeshPart"]
