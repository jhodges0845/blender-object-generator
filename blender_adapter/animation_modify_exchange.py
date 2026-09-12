# SPDX-License-Identifier: GPL-3.0-or-later
"""Expose first-class Blender animation records through portable Modify inspection."""

from .animation import clip_export_name, generated_actions
from .animation_lifecycle import managed_actions
from .animation_records import inspect_animation_record
from .core import AnimationSnapshot


def _snapshot_from_record(action, record):
    # Preserve the existing Modify clip key for generated Actions so rename/apply
    # requests remain backward compatible. First-class identity is carried
    # separately in animation_id.
    legacy_clip_id = str(action.get("asset_assistant_clip") or "").strip()
    clip_id = legacy_clip_id or record.animation_id
    return AnimationSnapshot(
        clip_id=clip_id,
        export_name=record.export_name,
        animation_id=record.animation_id,
        display_name=record.display_name,
        source=record.source.value,
        rig_signature=record.rig_signature,
        frame_start=float(record.frame_start),
        frame_end=float(record.frame_end),
        fps=float(record.fps),
        looping=record.looping,
        root_motion=record.root_motion.value,
        owns_curves=record.owns_curves,
        source_reference=record.source_reference,
        provider_key=record.provider_key,
        capability=record.capability,
    )


def animation_state(root, warnings):
    """Return managed animation metadata, retaining legacy generated clip compatibility."""
    try:
        managed = tuple(managed_actions(root))
    except ValueError as error:
        warnings.append("First-class animation inspection failed: " + str(error))
        managed = ()

    clips = []
    seen_clip_ids = set()
    seen_animation_ids = set()
    owns_all = True
    for action in managed:
        try:
            record = inspect_animation_record(root, action)
        except ValueError as error:
            warnings.append(action.name + ": " + str(error))
            owns_all = False
            continue
        snapshot = _snapshot_from_record(action, record)
        if snapshot.clip_id in seen_clip_ids:
            warnings.append("Duplicate managed animation clip identity: " + snapshot.clip_id)
            owns_all = False
            continue
        if record.animation_id in seen_animation_ids:
            warnings.append("Duplicate managed animation identity: " + record.animation_id)
            owns_all = False
            continue
        seen_clip_ids.add(snapshot.clip_id)
        seen_animation_ids.add(record.animation_id)
        clips.append(snapshot)
        owns_all = owns_all and record.owns_curves

    # Keep older generated Actions visible until every saved asset has first-class records.
    for action in generated_actions(root):
        if any(candidate == action for candidate in managed):
            continue
        clip_id = str(action.get("asset_assistant_clip") or action.name)
        if clip_id in seen_clip_ids:
            warnings.append("Duplicate generated animation clip identity: " + clip_id)
            owns_all = False
            continue
        seen_clip_ids.add(clip_id)
        clips.append(AnimationSnapshot(clip_id, clip_export_name(action)))

    if not clips:
        return (), False, False
    return tuple(sorted(clips, key=lambda clip: clip.clip_id)), True, owns_all


def install(modification):
    """Install first-class animation inspection into Blender Modify without changing core ownership rules."""
    if getattr(modification._animation_state, "_asset_assistant_first_class", False):
        return
    animation_state._asset_assistant_first_class = True
    modification._animation_state = animation_state


__all__ = ["animation_state", "install"]
