# SPDX-License-Identifier: GPL-3.0-or-later
"""Persist and inspect first-class animation records on Blender Actions."""

import json
from hashlib import sha256
from uuid import uuid4

from .core import (
    AnimationRecord,
    AnimationSource,
    RootMotionIntent,
    animation_document,
    animation_from_document,
)

_ANIMATION_RECORD_KEY = "asset_assistant_animation_record"
_ANIMATION_ID_KEY = "asset_assistant_animation_id"


def rig_signature(rig):
    """Return a deterministic compatibility signature for one Blender armature."""
    if rig is None or rig.type != "ARMATURE":
        raise ValueError("animation records require one Blender armature")
    rows = []
    for bone in sorted(rig.data.bones, key=lambda item: item.name):
        rows.append((
            bone.name,
            bone.parent.name if bone.parent else None,
            bool(bone.use_deform),
        ))
    payload = json.dumps(rows, separators=(",", ":"), ensure_ascii=True)
    return "sha256:" + sha256(payload.encode("utf-8")).hexdigest()


def persist_generated_animation(
    root,
    action,
    *,
    display_name,
    export_name,
    frame_start,
    frame_end,
    fps,
    provider_key,
    capability,
):
    """Attach one generated portable animation record to an existing Action."""
    rigs = [child for child in root.children if child.type == "ARMATURE"]
    if len(rigs) != 1:
        raise ValueError("animation persistence requires exactly one Asset Assistant rig")
    animation_id = action.get(_ANIMATION_ID_KEY) or ("animation-" + uuid4().hex)
    record = AnimationRecord(
        animation_id=animation_id,
        display_name=display_name,
        export_name=export_name,
        source=AnimationSource.GENERATED,
        rig_signature=rig_signature(rigs[0]),
        frame_start=frame_start,
        frame_end=frame_end,
        fps=fps,
        looping=True,
        root_motion=RootMotionIntent.IN_PLACE,
        owns_curves=True,
        source_reference=provider_key + ":" + capability,
        provider_key=provider_key,
        capability=capability,
    )
    action[_ANIMATION_ID_KEY] = record.animation_id
    action[_ANIMATION_RECORD_KEY] = json.dumps(animation_document(record), sort_keys=True)
    return record


def animation_record(action):
    """Parse one persisted portable animation record from an Action."""
    raw = action.get(_ANIMATION_RECORD_KEY)
    if not isinstance(raw, str):
        raise ValueError("Action is missing Asset Assistant animation record metadata")
    try:
        document = json.loads(raw)
    except (TypeError, ValueError):
        raise ValueError("Action animation record metadata is invalid JSON") from None
    record = animation_from_document(document)
    if action.get(_ANIMATION_ID_KEY) != record.animation_id:
        raise ValueError("Action animation id no longer matches its persisted record")
    return record


def inspect_animation_record(root, action):
    """Validate persisted identity, rig compatibility, and generated ownership."""
    record = animation_record(action)
    rigs = [child for child in root.children if child.type == "ARMATURE"]
    if len(rigs) != 1:
        raise ValueError("animation inspection requires exactly one Asset Assistant rig")
    if record.rig_signature != rig_signature(rigs[0]):
        raise ValueError("animation rig signature no longer matches the current Asset Assistant rig")
    if record.source == AnimationSource.GENERATED and not action.get("asset_assistant_generated"):
        raise ValueError("generated animation record is attached to an Action without generated ownership")
    export_name = str(action.get("asset_assistant_export_name") or "").strip()
    if export_name and export_name != record.export_name:
        raise ValueError("Action export name no longer matches its persisted animation record")
    return record


def update_animation_export_name(action, export_name):
    """Update the portable record when the existing export-name workflow changes."""
    record = animation_record(action)
    updated = AnimationRecord(
        animation_id=record.animation_id,
        display_name=record.display_name,
        export_name=export_name,
        source=record.source,
        rig_signature=record.rig_signature,
        frame_start=record.frame_start,
        frame_end=record.frame_end,
        fps=record.fps,
        looping=record.looping,
        root_motion=record.root_motion,
        owns_curves=record.owns_curves,
        source_reference=record.source_reference,
        provider_key=record.provider_key,
        capability=record.capability,
    )
    action[_ANIMATION_RECORD_KEY] = json.dumps(animation_document(updated), sort_keys=True)
    return updated


__all__ = [
    "animation_record",
    "inspect_animation_record",
    "persist_generated_animation",
    "rig_signature",
    "update_animation_export_name",
]
