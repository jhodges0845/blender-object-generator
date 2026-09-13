# SPDX-License-Identifier: GPL-3.0-or-later
"""Targeted recovery for stale component registry entries during checkpoint save.

A generated component can be deleted directly in Blender, leaving its persisted
registry document behind on the Asset Assistant root. Checkpoint validation is
correct to reject that inconsistent state, but artists need a safe recovery path.

This module only removes registry entries when the corresponding managed component
root is definitely absent. Ambiguous duplicates are never repaired automatically.
"""

import json

from .workflow import is_generated


_COMPONENTS_KEY = "asset_assistant_components"
_COMPONENT_ID_KEY = "asset_assistant_component_id"
_COMPONENT_RECORD_KEY = "asset_assistant_component_record"


def _descendants(root):
    pending = list(getattr(root, "children", ()))
    while pending:
        child = pending.pop()
        yield child
        pending.extend(getattr(child, "children", ()))


def _documents(root):
    raw = root.get(_COMPONENTS_KEY, "[]")
    if not isinstance(raw, str):
        raise ValueError("component registry is not valid persisted JSON")
    try:
        documents = json.loads(raw)
    except (TypeError, ValueError):
        raise ValueError("component registry is not valid persisted JSON") from None
    if not isinstance(documents, list):
        raise ValueError("component registry must contain a JSON array")
    return documents


def _component_root_matches(root, component_id):
    return [
        obj for obj in _descendants(root)
        if obj.get(_COMPONENT_ID_KEY) == component_id
        and obj.get(_COMPONENT_RECORD_KEY) is not None
    ]


def repair_missing_component_records(root):
    """Remove only registry rows whose managed component root is definitely gone.

    Returns the removed component ids. If more than one managed root claims an id,
    no repair is attempted because choosing between duplicates would be destructive.
    """
    documents = _documents(root)
    kept = []
    removed = []
    for document in documents:
        component_id = str(document.get("component_id", "")).strip() if isinstance(document, dict) else ""
        if not component_id:
            kept.append(document)
            continue
        matches = _component_root_matches(root, component_id)
        if len(matches) > 1:
            raise ValueError("persisted component root is ambiguous: " + component_id)
        if len(matches) == 0:
            removed.append(component_id)
            continue
        kept.append(document)

    if removed:
        root[_COMPONENTS_KEY] = json.dumps(kept, sort_keys=True)
    return tuple(removed)


def repair_scene_missing_component_records(scene):
    repaired = []
    for root in tuple(obj for obj in scene.objects if is_generated(obj)):
        for component_id in repair_missing_component_records(root):
            repaired.append((root, component_id))
    return tuple(repaired)


def install(working_asset_ui):
    """Retry checkpoint save once after safely pruning stale missing registry rows."""
    original = working_asset_ui.save_editable_checkpoint
    if getattr(original, "_asset_assistant_component_repair", False):
        return

    def save_with_component_repair(filepath, save_operator, scene=None):
        try:
            return original(filepath, save_operator, scene)
        except ValueError as error:
            if scene is None or "persisted component root is missing" not in str(error):
                raise
            repaired = repair_scene_missing_component_records(scene)
            if not repaired:
                raise
            result = original(filepath, save_operator, scene)
            ids = ", ".join(component_id for _root, component_id in repaired)
            scene[working_asset_ui._CHECKPOINT_MESSAGE_KEY] = (
                "Checkpoint saved after removing stale component registry entries: " + ids
            )
            return result

    save_with_component_repair._asset_assistant_component_repair = True
    working_asset_ui.save_editable_checkpoint = save_with_component_repair


__all__ = [
    "install",
    "repair_missing_component_records",
    "repair_scene_missing_component_records",
]
