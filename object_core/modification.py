# SPDX-License-Identifier: GPL-3.0-or-later
"""Host-independent inspection and planning contracts for Modify."""

from dataclasses import dataclass
from math import isfinite
from typing import Tuple

from .objects import get_provider


@dataclass(frozen=True)
class AnimationSnapshot:
    """Portable identity for one Asset Assistant-generated animation clip."""

    clip_id: str
    export_name: str


@dataclass(frozen=True)
class AssetSnapshot:
    """Portable facts observed from a generated asset."""

    asset_id: str
    provider_key: str
    provider_label: str
    parameters: Tuple[Tuple[str, object], ...]
    animations: Tuple[AnimationSnapshot, ...] = ()
    has_rig: bool = False
    has_materials: bool = False
    has_animations: bool = False
    owns_geometry: bool = False
    owns_rig: bool = False
    owns_materials: bool = False
    owns_animations: bool = False
    warnings: Tuple[str, ...] = ()

    def parameter_values(self):
        return dict(self.parameters)


@dataclass(frozen=True)
class ModificationRequest:
    """Explicit requested changes; omitted fields mean preserve."""

    parameter_changes: Tuple[Tuple[str, object], ...] = ()
    animation_export_names: Tuple[Tuple[str, str], ...] = ()


@dataclass(frozen=True)
class ModificationPlan:
    """Reviewable plan produced before any host mutation occurs."""

    asset_id: str
    provider_key: str
    requested_parameter_changes: Tuple[Tuple[str, object], ...]
    requested_animation_renames: Tuple[Tuple[str, str], ...]
    rebuild_components: Tuple[str, ...]
    blockers: Tuple[str, ...]

    @property
    def safe_to_apply(self):
        return not self.blockers


def _as_unique_dict(items, label):
    result = {}
    for key, value in items:
        if not isinstance(key, str) or not key.strip():
            raise ValueError(label + " keys must be nonempty strings")
        if key in result:
            raise ValueError("Duplicate " + label + " key: " + key)
        result[key] = value
    return result


def _validate_parameter(parameter, value):
    if parameter.choices:
        if value not in parameter.choices:
            raise ValueError(parameter.label + " is not an allowed choice")
        return value
    if isinstance(value, bool) or not isinstance(value, (int, float)):
        raise TypeError(parameter.label + " must be a number")
    try:
        normalized = float(value)
    except OverflowError:
        raise ValueError(parameter.label + " must be finite") from None
    if not isfinite(normalized):
        raise ValueError(parameter.label + " must be finite")
    if not parameter.minimum <= normalized <= parameter.maximum:
        raise ValueError(parameter.label + " is outside its supported range")
    return normalized


def _conservative_parameter_impact(provider, snapshot):
    """Rebuild only generated components that already exist on this asset."""
    components = ["geometry"]
    if provider.supports_rig and snapshot.has_rig:
        components.append("rig")
    if getattr(provider, "supports_materials", False) and snapshot.has_materials:
        components.append("materials")
    if snapshot.has_animations and any(
        getattr(provider, capability, False)
        for capability in ("supports_idle", "supports_locomotion", "supports_run", "supports_flight")
    ):
        components.append("animations")
    return tuple(components)


def plan_modification(snapshot, request):
    """Validate an explicit request and return a non-mutating modification plan."""
    if not isinstance(snapshot, AssetSnapshot):
        raise TypeError("snapshot must be an AssetSnapshot")
    if not isinstance(request, ModificationRequest):
        raise TypeError("request must be a ModificationRequest")

    provider = get_provider(snapshot.provider_key)
    if snapshot.provider_label != provider.label:
        raise ValueError("Snapshot provider label does not match provider registry")

    current = snapshot.parameter_values()
    changes = _as_unique_dict(request.parameter_changes, "parameter change")
    parameter_by_key = {parameter.key: parameter for parameter in provider.parameters}
    normalized_changes = []
    for key, value in changes.items():
        try:
            parameter = parameter_by_key[key]
        except KeyError:
            raise ValueError("Unsupported parameter for " + provider.label + ": " + key) from None
        if key not in current:
            raise ValueError("Snapshot is missing provider parameter: " + key)
        normalized = _validate_parameter(parameter, value)
        if normalized != current[key]:
            normalized_changes.append((key, normalized))

    animation_names = _as_unique_dict(request.animation_export_names, "animation rename")
    generated_clips = {clip.clip_id: clip for clip in snapshot.animations}
    normalized_renames = []
    for clip_id, export_name in animation_names.items():
        if clip_id not in generated_clips:
            raise ValueError("Unknown generated animation clip: " + clip_id)
        if not isinstance(export_name, str) or not export_name.strip():
            raise ValueError("Animation export name must be a nonempty string")
        cleaned = export_name.strip()
        if cleaned != generated_clips[clip_id].export_name:
            normalized_renames.append((clip_id, cleaned))

    rebuild = _conservative_parameter_impact(provider, snapshot) if normalized_changes else ()
    blockers = []
    ownership = {
        "geometry": snapshot.owns_geometry,
        "rig": snapshot.owns_rig,
        "materials": snapshot.owns_materials,
        "animations": snapshot.owns_animations,
    }
    for component in rebuild:
        if not ownership[component]:
            blockers.append("Cannot safely replace unowned or ambiguous " + component)
    if normalized_renames and not snapshot.owns_animations:
        blockers.append("Cannot safely rename unowned or ambiguous animations")

    return ModificationPlan(
        asset_id=snapshot.asset_id,
        provider_key=provider.key,
        requested_parameter_changes=tuple(normalized_changes),
        requested_animation_renames=tuple(normalized_renames),
        rebuild_components=tuple(rebuild),
        blockers=tuple(blockers),
    )
