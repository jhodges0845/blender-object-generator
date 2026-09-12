# SPDX-License-Identifier: GPL-3.0-or-later
"""High-impact Blender-native presentation for the Asset Assistant Create workspace.

This module intentionally owns presentation only. It reuses the existing provider
parameters and operators so generation, Modify, Rig, ownership, and export behavior
remain unchanged.
"""

_ASSET_TILES = (
    ("human_experimental", "USER"),
    ("quadruped", "ARMATURE_DATA"),
    ("avian", "OUTLINER_OB_MESH"),
    ("box", "CUBE"),
)

_CREATE_MODES = (
    ("GENERATE", "Generate", "ADD"),
    ("MODIFY", "Modify", "MODIFIER"),
    ("RIG", "Rig", "ARMATURE_DATA"),
)


def _draw_create_mode_nav(layout, settings):
    """Keep Generate / Modify / Rig obvious without competing with primary nav."""
    row = layout.row(align=True)
    row.scale_y = 1.35
    for key, label, icon in _CREATE_MODES:
        row.prop_enum(
            settings,
            "asset_assistant_create_view",
            key,
            text=label,
            icon=icon,
        )


def _draw_asset_tiles(layout, settings, ui):
    """Draw the provider choice as four large visual tiles instead of form controls."""
    card = layout.box()
    card.label(text="CHOOSE A STARTING POINT", icon="OBJECT_DATA")
    card.label(text="Pick the asset family you want to create")

    tiles = card.row(align=True)
    for key, icon in _ASSET_TILES:
        provider = ui.get_provider(key)
        tile = tiles.column(align=True)
        icon_button = tile.row(align=True)
        icon_button.scale_y = 1.75
        icon_button.prop_enum(
            settings,
            "object_type",
            key,
            text="",
            icon=icon,
        )
        label_button = tile.row(align=True)
        label_button.scale_y = 1.15
        label_button.prop_enum(
            settings,
            "object_type",
            key,
            text=provider.label,
        )
    return card


def _draw_generate(panel, context, ui, working_asset_ui):
    settings = context.scene.humanoid_settings
    layout = panel.layout

    hero = layout.box()
    title = hero.row(align=True)
    title.scale_y = 1.2
    title.label(text="CREATE CHARACTER", icon="USER")
    hero.label(text="Start with a production-ready editable asset")

    _draw_asset_tiles(layout, settings, ui)
    provider = ui.get_provider(settings.object_type)
    fields = tuple(provider.parameters)

    setup = layout.box()
    setup.label(text="QUICK SETUP", icon="PREFERENCES")
    setup.label(text=provider.label + " proportions")
    for field in fields[:3]:
        setup.prop(settings, ui._field_name(provider, field))

    if len(fields) > 3:
        advanced = layout.box()
        advanced.prop(
            settings,
            "asset_assistant_create_advanced",
            text="Advanced Options",
            toggle=True,
            icon="DOWNARROW_HLT" if settings.asset_assistant_create_advanced else "RIGHTARROW",
        )
        if settings.asset_assistant_create_advanced:
            for field in fields[3:]:
                advanced.prop(settings, ui._field_name(provider, field))

    primary = layout.box()
    primary.label(text="READY TO BUILD", icon="CHECKMARK")
    action = primary.row()
    action.scale_y = 1.75
    action.operator(
        "humanoid.generate_blockout",
        text="Generate " + provider.label,
        icon="ADD",
    )
    primary.label(text="Creates an editable Asset Assistant model")

    if working_asset_ui is not None:
        layout.separator(factor=0.6)
        resume = layout.box()
        resume.label(text="CONTINUE EXISTING", icon="FILE_FOLDER")
        row = resume.row()
        row.scale_y = 1.1
        row.operator(
            "asset_assistant.open_editable_checkpoint",
            text="Open Editable Checkpoint",
            icon="FILE_FOLDER",
        )


def _draw_create(panel, context, ui, modify_ui, working_asset_ui):
    """Replacement Create renderer with a first-impression visual hierarchy."""
    settings = context.scene.humanoid_settings
    layout = panel.layout

    _draw_create_mode_nav(layout, settings)
    layout.separator(factor=0.7)

    if settings.asset_assistant_create_view == "GENERATE":
        _draw_generate(panel, context, ui, working_asset_ui)
        return

    if settings.asset_assistant_create_view == "MODIFY":
        workspace = _WORKFLOW_UI
        workspace._section_header(
            layout,
            "MODIFY ASSET",
            "Load, tune, preview, then apply",
            "MODIFIER",
        )
        workspace._draw_artist_modify(panel, context, ui, modify_ui)
        return

    workspace = _WORKFLOW_UI
    workspace._section_header(
        layout,
        "RIG & POSE",
        "Prepare the current asset for animation",
        "ARMATURE_DATA",
    )
    ui._WorkflowPanel.draw(workspace._stage_proxy(panel, "RIGGING"), context)


_WORKFLOW_UI = None


def install(workflow_ui, ui):
    """Install the Create renderer before Blender registers the settings class."""
    global _WORKFLOW_UI
    _WORKFLOW_UI = workflow_ui

    annotations = ui.HUMANOID_PG_settings.__annotations__
    if "asset_assistant_create_advanced" not in annotations:
        annotations["asset_assistant_create_advanced"] = ui.BoolProperty(
            name="Advanced Options",
            default=False,
        )

    workflow_ui._draw_create = _draw_create
