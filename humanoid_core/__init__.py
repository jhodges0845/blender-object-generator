# SPDX-License-Identifier: GPL-3.0-or-later
"""Software-independent humanoid generation."""

from .models import BodyType, HumanoidSpec, HumanoidProportions, HumanoidMesh, MeshPart, Bone, Skeleton
from .proportions import generate_proportions
from .geometry import generate_mesh
from .rigging import generate_skeleton

__all__ = ["BodyType", "HumanoidSpec", "HumanoidProportions", "HumanoidMesh",
           "MeshPart", "Bone", "Skeleton", "generate_proportions", "generate_mesh",
           "generate_skeleton"]
