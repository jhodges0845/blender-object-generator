# SPDX-License-Identifier: GPL-3.0-or-later
"""Host-independent requirements for supported asset destinations."""

from dataclasses import dataclass
from typing import Dict, Tuple

from .models.validation import AssetSnapshot, ValidationIssue
from .validation import validate_asset


@dataclass(frozen=True)
class OutputTarget:
    """Describes what a destination expects without depending on Blender APIs."""

    key: str
    display_name: str
    asset_use: str
    preferred_formats: Tuple[str, ...]
    require_textures: bool = False
    require_rig: bool = False
    require_animation: bool = False
    require_manifold_geometry: bool = False
    supports_rig: bool = True
    supports_animation: bool = True
    notes: Tuple[str, ...] = ()


GODOT = OutputTarget(
    key="GODOT",
    display_name="Godot",
    asset_use="ANIMATED",
    preferred_formats=("GLB", "GLTF"),
    require_rig=True,
    require_animation=True,
    notes=("Review scale, axes, materials, collision, and LODs after import.",),
)

UNITY = OutputTarget(
    key="UNITY",
    display_name="Unity",
    asset_use="ANIMATED",
    preferred_formats=("FBX",),
    require_rig=True,
    require_animation=True,
    notes=("Review humanoid/avatar mapping, scale, materials, collision, and LODs after import.",),
)

UNREAL = OutputTarget(
    key="UNREAL",
    display_name="Unreal Engine",
    asset_use="ANIMATED",
    preferred_formats=("FBX",),
    require_rig=True,
    require_animation=True,
    notes=("Review Skeleton assignment, scale, morph targets, collision, and LODs after import.",),
)

CURA = OutputTarget(
    key="CURA",
    display_name="Cura",
    asset_use="STATIC",
    preferred_formats=("STL",),
    require_manifold_geometry=True,
    supports_rig=False,
    supports_animation=False,
    notes=("Bake the desired pose and validate wall thickness, dimensions, intersections, and slicer readiness.",),
)

# Keep the original public constant and saved key working.
PRINT_3D = CURA

TARGETS: Dict[str, OutputTarget] = {
    target.key: target for target in (GODOT, UNITY, UNREAL, CURA)
}


def get_target(key: str) -> OutputTarget:
    if not isinstance(key, str):
        raise TypeError("target key must be str")
    try:
        return TARGETS["CURA" if key.upper() == "PRINT_3D" else key.upper()]
    except KeyError:
        raise ValueError("unknown output target: " + key)


def validate_for_target(snapshot: AssetSnapshot, target) -> Tuple[ValidationIssue, ...]:
    """Run shared readiness checks and append destination-specific guidance."""

    if isinstance(target, str):
        target = get_target(target)
    if not isinstance(target, OutputTarget):
        raise TypeError("target must be an OutputTarget or target key")

    results = list(validate_asset(
        snapshot,
        asset_use=target.asset_use,
        require_textures=target.require_textures,
    ))

    if target.require_manifold_geometry:
        if not snapshot.mesh_count or snapshot.invalid_meshes:
            results.append(ValidationIssue(
                "target_geometry", "ERROR",
                "Cura output requires closed, valid geometry before export.",
            ))
        else:
            results.append(ValidationIssue(
                "target_geometry", "PASS",
                "Core geometry is closed and valid; wall thickness and slicer checks still remain.",
            ))

    if not target.supports_rig and snapshot.has_rig:
        results.append(ValidationIssue(
            "target_rig", "WARN",
            "This target does not use a runtime rig; bake the desired pose and remove/ignore armature data for export.",
        ))

    if not target.supports_animation and snapshot.has_animation:
        results.append(ValidationIssue(
            "target_animation", "WARN",
            "This target does not use animation clips; export only the baked printable pose.",
        ))

    results.append(ValidationIssue(
        "target_format", "PASS",
        target.display_name + " preferred export format(s): " + ", ".join(target.preferred_formats) + ".",
    ))
    for note in target.notes:
        results.append(ValidationIssue("target_review", "INFO", note))
    return tuple(results)
