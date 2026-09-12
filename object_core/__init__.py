# SPDX-License-Identifier: GPL-3.0-or-later
"""Software-independent object generation and reusable geometry contracts."""

from .models import BodyType, HumanoidSpec, HumanoidProportions, ObjectMesh, MeshPart, Bone, Skeleton
from .proportions import generate_proportions
from .geometry import generate_mesh
from .rigging import generate_skeleton
from .objects import OBJECT_TYPES, get_provider
from .components import (
    AttachmentMode,
    ComponentKind,
    ComponentRecord,
    PhysicsIntent,
    RigBinding,
    component_document,
    component_from_document,
    validate_component,
)
from .animations import (
    AnimationRecord,
    AnimationSource,
    RootMotionIntent,
    animation_document,
    animation_from_document,
    validate_animation,
)

__all__ = ["BodyType", "HumanoidSpec", "HumanoidProportions", "ObjectMesh",
           "MeshPart", "Bone", "Skeleton", "generate_proportions", "generate_mesh",
           "generate_skeleton", "OBJECT_TYPES", "get_provider", "AttachmentMode",
           "ComponentKind", "ComponentRecord", "PhysicsIntent", "RigBinding",
           "component_document", "component_from_document", "validate_component",
           "AnimationRecord", "AnimationSource", "RootMotionIntent",
           "animation_document", "animation_from_document", "validate_animation"]
