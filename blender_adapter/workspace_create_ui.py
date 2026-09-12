# SPDX-License-Identifier: GPL-3.0-or-later
"""High-impact Blender-native presentation for the Asset Assistant Create workspace.

This module owns presentation only. Existing provider parameters and operators are
reused so generation, Modify, Rig, animation, and export behavior remain unchanged.
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

_WORKFLOW_UI = None
_ORIGINAL_ASSET_SUMMARY = None
_ASSET_INSPECTION_UI = None


def _draw_create_mode_nav(layout, settings):
    """Keep Generate / Modify / Rig available without overpowering the main flow."""
    row = layout.row(align=True)
    row.scale_y = 1.2
    for key, label, icon in _CREATE_MODES:
        row.prop_enum(
            settings,
            "asset_assistant_create_view",
            key,
            text=label,
            icon=icon,
        )


def _draw_asset_tiles(layout, settings, ui):
    """Draw each provider as one cohesive tall button with icon and label together."""
    tiles = layout.row(align=True)
    tiles.scale_y = 2.25
    for key, icon in _ASSET_TILES:
        provider = ui.get_provider(key)
        tiles.prop_enum(
            settings,
            "object_type",
            key,
            text=provider.label,
            icon=icon,
        )


def _draw_start_options(layout, context, working_asset_ui):
    """Show artist-owned and saved-asset paths before generation."""
    if working_asset_ui is None and _ASSET_INSPECTION_UI is None:
        return
    start = layout.box()
    start.label(text="START WITH", icon="FILE_FOLDER")
    start.label(text="Continue existing work, inspect a selected asset, or build new")
    row = start.row(align=True)
    row.scale_y = 1.45
    if working_asset_ui is not None:
        row.operator(
            "asset_assistant.open_editable_checkpoint",
            text="Open Existing Asset",
            icon="FILE_FOLDER",
        )
    if _ASSET_INSPECTION_UI is not None:
        row.operator(
            "asset_assistant.inspect_selected_asset",
            text="Inspect Selected",
            icon="VIEWZOOM",
        )
        _ASSET_INSPECTION_UI.draw_inspection_report(start, context.scene)


def _draw_generate(panel, context, ui, working_asset_ui):
    settings = context.scene.humanoid_settings
    layout = panel.layout
    provider = ui.get_provider(settings.object_type)
    fields = tuple(provider.parameters)

    _draw_start_options(layout, context, working_asset_ui)
    if working_asset_ui is not None or _ASSET_INSPECTION_UI is not None:
        layout.separator(factor=0.6)

    # One dominant card instead of a stack of equally weighted boxes.
    create = layout.box()
    hero = create.row(align=True)
    hero.scale_y = 1.35
    hero.label(text="CREATE NEW ASSET", icon="USER")
    create.label(text="Choose a starting point, tune the essentials, then build")
    create.separator(factor=0.5)

    _draw_asset_tiles(create, settings, ui)
    create.separator(factor=0.7)

    setup_title = create.row(align=True)
    setup_title.label(text="QUICK SETUP", icon="PREFERENCES")
    setup_title.label(text=provider.label)
    for field in fields[:3]:
        create.prop(settings, ui._field_name(provider, field))

    if len(fields) > 3:
        advanced = create.column(align=True)
        advanced.separator(factor=0.35)
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

    create.separator(factor=0.75)
    action = create.row()
    action.scale_y = 2.0
    replacing = getattr(settings, "target", None) is not None
    action.operator(
        "asset_assistant.generate_replace_current",
        text=("Replace Current with " if replacing else "Generate ") + provider.label,
        icon="FILE_REFRESH" if replacing else "ADD",
    )
    create.label(
        text="Replaces the current asset after a successful build"
        if replacing else "Creates a new editable Asset Assistant model"
    )


def _draw_create(panel, context, ui, modify_ui, working_asset_ui):
    """Replacement Create renderer with a first-impression visual hierarchy."""
    settings = context.scene.humanoid_settings
    layout = panel.layout

    _draw_create_mode_nav(layout, settings)
    layout.separator(factor=0.8)

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


def _draw_contextual_asset_summary(layout, context):
    """Do not spend prime empty-state space on a card that only says nothing exists."""
    settings = getattr(context.scene, "humanoid_settings", None)
    target = getattr(settings, "target", None) if settings else None
    is_empty_create = (
        settings is not None
        and target is None
        and getattr(settings, "asset_assistant_workspace", None) == "CREATE"
        and getattr(settings, "asset_assistant_create_view", None) == "GENERATE"
    )
    if is_empty_create:
        return
    _ORIGINAL_ASSET_SUMMARY(layout, context)


def install(workflow_ui, ui, asset_inspection_ui=None):
    """Install the Create renderer before Blender registers the settings class."""
    global _WORKFLOW_UI, _ORIGINAL_ASSET_SUMMARY, _ASSET_INSPECTION_UI
    _WORKFLOW_UI = workflow_ui
    _ASSET_INSPECTION_UI = asset_inspection_ui

    annotations = ui.HUMANOID_PG_settings.__annotations__
    if "asset_assistant_create_advanced" not in annotations:
        annotations["asset_assistant_create_advanced"] = ui.BoolProperty(
            name="Advanced Options",
            default=False,
        )

    if _ORIGINAL_ASSET_SUMMARY is None:
        _ORIGINAL_ASSET_SUMMARY = workflow_ui._asset_summary
    workflow_ui._asset_summary = _draw_contextual_asset_summary
    workflow_ui._draw_create = _draw_create
