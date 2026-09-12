# SPDX-License-Identifier: GPL-3.0-or-later
"""Small UI enhancement for editing an Asset Assistant asset's display name."""


def install(workflow_ui):
    """Add a Blender-native asset-name field below the current asset summary."""
    original = workflow_ui._asset_summary

    def draw_asset_summary(layout, context):
        original(layout, context)
        settings = getattr(context.scene, "humanoid_settings", None)
        target = getattr(settings, "target", None) if settings else None
        if target is None:
            return
        identity = layout.box()
        identity.label(text="ASSET IDENTITY", icon="OBJECT_DATA")
        identity.prop(target, "name", text="Name")
        identity.label(text="Rename the generated or imported asset here.")

    workflow_ui._asset_summary = draw_asset_summary
