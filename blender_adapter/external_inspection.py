# SPDX-License-Identifier: GPL-3.0-or-later
"""Non-destructive inspection for artist-authored objects before adoption."""

from dataclasses import dataclass

from .components import _armature, _require_asset_root


SUPPORTED = "supported"
REDUCED = "reduced_capability"
BLOCKED = "blocked"


@dataclass(frozen=True)
class ExternalObjectInspection:
    status: str
    reasons: tuple
    suggested_behavior: str
    detected_materials: bool
    detected_armature: bool
    detected_vertex_groups: bool

    @property
    def can_adopt(self):
        return self.status != BLOCKED


def _asset_owner(obj):
    current = obj
    while current is not None:
        if current.get("generator") == "object_generator":
            return current
        current = current.parent
    return None


def inspect_external_object(root, obj):
    """Inspect one Blender object without mutating it or claiming ownership.

    The result deliberately describes the *current* adoption capability rather
    than trying to repair or normalize artist-authored data. This lets the UI
    explain whether adoption is fully supported, available with reduced
    capability, or blocked before any ownership transfer occurs.
    """
    _require_asset_root(root)

    if obj is None:
        return ExternalObjectInspection(
            BLOCKED,
            ("No object was supplied for inspection.",),
            "none",
            False,
            False,
            False,
        )
    if getattr(obj, "type", None) != "MESH":
        return ExternalObjectInspection(
            BLOCKED,
            ("Current component adoption requires a Blender mesh object.",),
            "none",
            False,
            False,
            False,
        )

    materials = bool(getattr(getattr(obj, "data", None), "materials", ()))
    vertex_groups = bool(getattr(obj, "vertex_groups", ()))
    armature_modifiers = [modifier for modifier in obj.modifiers if modifier.type == "ARMATURE"]
    owner = _asset_owner(obj)

    if owner is not None and owner != root:
        return ExternalObjectInspection(
            BLOCKED,
            ("Object already belongs to a different Asset Assistant asset.",),
            "none",
            materials,
            bool(armature_modifiers),
            vertex_groups,
        )
    if owner == root and ("part_name" in obj or "body_part" in obj):
        return ExternalObjectInspection(
            BLOCKED,
            ("Generated body geometry cannot be re-adopted as a reusable component.",),
            "none",
            materials,
            bool(armature_modifiers),
            vertex_groups,
        )
    if "asset_assistant_component_id" in obj:
        return ExternalObjectInspection(
            BLOCKED,
            ("Object is already registered as an Asset Assistant component.",),
            "none",
            materials,
            bool(armature_modifiers),
            vertex_groups,
        )
    if len(armature_modifiers) > 1:
        return ExternalObjectInspection(
            BLOCKED,
            ("Multiple armature modifiers are not currently adoptable without artist cleanup.",),
            "none",
            materials,
            True,
            vertex_groups,
        )

    reasons = []
    status = SUPPORTED
    suggested_behavior = "rigid"

    if obj.children:
        status = REDUCED
        reasons.append("Child-object hierarchies are preserved but must be separated before current adoption.")

    if armature_modifiers:
        modifier = armature_modifiers[0]
        target = modifier.object
        try:
            parent_armature = _armature(root)
        except ValueError:
            parent_armature = None

        if target == parent_armature and vertex_groups:
            suggested_behavior = "parent_skinned"
            if not modifier.use_vertex_groups or modifier.use_bone_envelopes:
                status = REDUCED
                reasons.append(
                    "Parent-rig modifier settings are recognizable but need artist cleanup before adoption."
                )
        else:
            suggested_behavior = "external_rig"
            status = REDUCED
            reasons.append(
                "An external rig was detected. Asset Assistant can inspect it, but current adoption will not claim or retarget that rig."
            )
    elif vertex_groups:
        status = REDUCED
        reasons.append(
            "Vertex groups were detected without a usable armature modifier; weights will remain artist-owned until a supported binding is chosen."
        )

    if materials:
        reasons.append("Artist materials detected; adoption will preserve artist material ownership.")

    if not reasons:
        reasons.append("Object matches the currently supported rigid component adoption path.")

    return ExternalObjectInspection(
        status,
        tuple(reasons),
        suggested_behavior,
        materials,
        bool(armature_modifiers),
        vertex_groups,
    )


__all__ = [
    "BLOCKED",
    "REDUCED",
    "SUPPORTED",
    "ExternalObjectInspection",
    "inspect_external_object",
]
