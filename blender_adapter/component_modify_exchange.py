# SPDX-License-Identifier: GPL-3.0-or-later
"""Bridge validated Blender component state into portable Modify snapshots."""

from dataclasses import replace

from .components import component_records, inspect_component
from .core import AttachmentMode
from .skinned_components import inspect_skinned_component


def enrich_snapshot(root, snapshot):
    """Return snapshot with every persisted component revalidated in Blender."""
    records = component_records(root)
    validated = []
    for record in records:
        if record.attachment_mode == AttachmentMode.SKINNED:
            validated.append(inspect_skinned_component(root, record.component_id))
        else:
            validated.append(inspect_component(root, record.component_id))
    return replace(snapshot, components=tuple(validated))


def install(modify_ui):
    """Install component-aware inspection into the artist-facing Modify workflow."""
    original = modify_ui.inspect_generated_asset
    if getattr(original, "_asset_assistant_component_enriched", False):
        return

    def component_aware_inspection(root):
        return enrich_snapshot(root, original(root))

    component_aware_inspection._asset_assistant_component_enriched = True
    modify_ui.inspect_generated_asset = component_aware_inspection


__all__ = ["enrich_snapshot", "install"]
