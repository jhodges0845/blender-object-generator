# SPDX-License-Identifier: GPL-3.0-or-later
"""Artist-facing asset identity without coupling display names to provider identity."""


def _source_label(target):
    source = str(target.get("asset_assistant_source", "")).strip().upper()
    labels = {
        "GENERATED": "Generated",
        "IMPORTED": "Imported",
        "ADOPTED": "Imported / Adopted",
    }
    if source in labels:
        return labels[source]
    # Existing Asset Assistant files predate explicit provenance metadata.
    if target.get("generator") in ("humanoid_blockout", "object_generator"):
        return "Generated"
    return "External / Unclassified"


def _provider_label(target):
    try:
        from .workflow import provider_for
        return provider_for(target).label
    except (ValueError, TypeError, AttributeError, KeyError):
        stored = str(target.get("object_type", "")).strip()
        return stored.replace("_", " ").title() if stored else "Unknown"


def _component_label(count):
    return str(count) + (" Component" if count == 1 else " Components")


def _draw_summary(layout, context):
    settings = getattr(context.scene, "humanoid_settings", None)
    target = getattr(settings, "target", None) if settings else None
    card = layout.box()
    title = card.row(align=True)
    title.label(text="CURRENT ASSET", icon="OBJECT_DATA")
    if target is None:
        card.label(text="Nothing selected yet")
        return None

    title.label(text=target.name)
    children = tuple(target.children)
    has_rig = any(obj.type == "ARMATURE" for obj in children)
    component_count = sum(obj.type == "MESH" for obj in children)
    animation_count = 0
    for obj in children:
        if obj.type != "ARMATURE" or not obj.animation_data:
            continue
        if obj.animation_data.action is not None:
            animation_count += 1
        animation_count += len(obj.animation_data.nla_tracks)

    status = card.row(align=True)
    status.label(text="Rigged" if has_rig else "No Rig", icon="ARMATURE_DATA")
    status.label(text=str(animation_count) + (" Clip" if animation_count == 1 else " Clips"), icon="ACTION")
    status.label(text=_component_label(component_count), icon="CUBE")
    return target


def _draw_identity(layout, target):
    identity = layout.box()
    identity.label(text="ASSET IDENTITY", icon="OBJECT_DATA")
    identity.prop(target, "name", text="Name")

    details = identity.column(align=True)
    details.label(text="Type: " + _provider_label(target), icon="OUTLINER_OB_MESH")
    details.label(text="Source: " + _source_label(target), icon="IMPORT")
    return identity


def install(workflow_ui):
    """Replace the stock summary with a clearer artist-facing identity card."""
    def draw_asset_summary(layout, context):
        target = _draw_summary(layout, context)
        if target is not None:
            _draw_identity(layout, target)

    workflow_ui._asset_summary = draw_asset_summary
