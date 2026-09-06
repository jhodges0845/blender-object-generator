# SPDX-License-Identifier: GPL-3.0-or-later
"""Shared, software-independent character data contracts."""

from .spec import BodyType, HumanoidSpec
from .proportions import HumanoidProportions
from .mesh import HumanoidMesh, MeshPart
from .skeleton import Bone, Skeleton

__all__ = ["BodyType", "HumanoidSpec", "HumanoidProportions", "HumanoidMesh", "MeshPart", "Bone", "Skeleton"]
