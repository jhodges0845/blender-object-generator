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
    return "Managed Asset"


def _provider_label(target):
    try:
        from .workflow import provider_for
        return provider_for(target).label
    except (ValueError, TypeError, AttributeError, KeyError):
        stored = str(target.get("object_type", "")).strip()
        return stored.replace("_", " ").title() if stored else "Unknown"


def _draw_identity(layout, target):
    identity = layout.box()
    identity.label(text="ASSET IDENTITY", icon="OBJECT_DATA")
    identity.prop(target, "name", text="Name")

    details = identity.column(align=True)
    details.label(text="Type: " + _provider_label(target), icon="OUTLINER_OB_MESH")
    details.label(text="Source: " + _source_label(target), icon="IMPORT")
    details.label(text="Managed by Asset Assistant", icon="CHECKMARK")
    return identity


def install(workflow_ui):
    """Add editable display identity beneath the current asset summary."""
    original = workflow_ui._asset_summary

    def draw_asset_summary(layout, context):
        original(layout, context)
        settings = getattr(context.scene, "humanoid_settings", None)
        target = getattr(settings, "target", None) if settings else None
        if target is not None:
            _draw_identity(layout, target)

    workflow_ui._asset_summary = draw_asset_summary
