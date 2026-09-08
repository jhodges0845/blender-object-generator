# SPDX-License-Identifier: GPL-3.0-or-later
"""Shared, software-independent character data contracts."""

from .spec import BodyType, HumanoidSpec
from .proportions import HumanoidProportions
from .mesh import ObjectMesh, MeshPart
from .skeleton import Bone, Skeleton
from .skinning import BoneWeight, SkinWeights
from .material import ImageTextureSpec, MaterialSpec

__all__ = [
    "BodyType", "HumanoidSpec", "HumanoidProportions", "ObjectMesh", "MeshPart",
    "Bone", "Skeleton", "BoneWeight", "SkinWeights", "ImageTextureSpec", "MaterialSpec",
]
