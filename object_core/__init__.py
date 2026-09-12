# SPDX-License-Identifier: GPL-3.0-or-later
"""Software-independent object generation and reusable geometry contracts."""

from .models import BodyType, HumanoidSpec, HumanoidProportions, ObjectMesh, MeshPart, Bone, Skeleton
from .proportions import generate_proportions
from .geometry import generate_mesh
from .rigging import generate_skeleton
from .objects import OBJECT_TYPES, get_provider
from .components import AttachmentMode, ComponentKind, ComponentRecord, PhysicsIntent, component_document, validate_component

__all__ = ["BodyType", "HumanoidSpec", "HumanoidProportions", "ObjectMesh",
           "MeshPart", "Bone", "Skeleton", "generate_proportions", "generate_mesh",
           "generate_skeleton", "OBJECT_TYPES", "get_provider", "AttachmentMode",
           "ComponentKind", "ComponentRecord", "PhysicsIntent", "component_document",
           "validate_component"]
