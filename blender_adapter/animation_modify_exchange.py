# SPDX-License-Identifier: GPL-3.0-or-later
"""Expose first-class Blender animation records through portable Modify inspection."""

from .animation import clip_export_name, generated_actions
from .animation_lifecycle import managed_actions
from .animation_records import (
    animation_record,
    has_animation_record,
    inspect_animation_record,
    persist_animation_record,
    update_animation_export_name,
)
from .core import AnimationSnapshot

_EXPORT_NAME = "asset_assistant_export_name"


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


def _metadata_apply_with_records(modification, root, plan):
    """Apply metadata-only Modify while keeping persisted animation records synchronized."""
    snapshot = modification._check_plan_matches(root, plan)
    if plan.rebuild_components or plan.requested_parameter_changes or plan.requested_semantic_operations:
        raise ValueError("This apply path only supports metadata-only modifications.")
    if plan.requested_animation_renames and not snapshot.owns_animations:
        raise ValueError("Generated animation ownership is ambiguous; nothing was changed.")

    actions = {str(action.get("asset_assistant_clip") or action.name): action
               for action in generated_actions(root)}
    requested = dict(plan.requested_animation_renames)
    missing = [clip_id for clip_id in requested if clip_id not in actions]
    if missing:
        raise ValueError("Modification plan references missing generated animation: " + missing[0])

    final_names = {clip_id: requested.get(clip_id, clip_export_name(action)).strip()
                   for clip_id, action in actions.items()}
    if any(not name for name in final_names.values()):
        raise ValueError("Animation export name cannot be empty.")
    if len(set(final_names.values())) != len(final_names):
        raise ValueError("Animation export names must remain unique; nothing was changed.")

    previous = {}
    try:
        for clip_id, export_name in requested.items():
            action = actions[clip_id]
            previous[clip_id] = (
                action.get(_EXPORT_NAME),
                animation_record(action) if has_animation_record(action) else None,
            )
            if has_animation_record(action):
                update_animation_export_name(action, export_name)
            action[_EXPORT_NAME] = export_name
    except Exception:
        for clip_id, (old_export, old_record) in previous.items():
            action = actions[clip_id]
            if old_record is not None:
                persist_animation_record(action, old_record)
            if old_export is None:
                if _EXPORT_NAME in action:
                    del action[_EXPORT_NAME]
            else:
                action[_EXPORT_NAME] = old_export
        raise
    return modification.inspect_generated_asset(root)


def install(modification, modify_ui=None):
    """Install first-class inspection and record-aware metadata Modify behavior."""
    if not getattr(modification._animation_state, "_asset_assistant_first_class", False):
        animation_state._asset_assistant_first_class = True
        modification._animation_state = animation_state

    def record_aware_metadata_apply(root, plan):
        return _metadata_apply_with_records(modification, root, plan)

    record_aware_metadata_apply._asset_assistant_animation_records = True
    modification.apply_metadata_modification = record_aware_metadata_apply
    if modify_ui is not None:
        modify_ui.apply_metadata_modification = record_aware_metadata_apply


__all__ = ["animation_state", "install"]
