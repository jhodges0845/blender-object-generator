# SPDX-License-Identifier: GPL-3.0-or-later
"""Present Asset Assistant as one compact Blender sidebar workspace."""

_CATEGORY = "Asset Assistant"


def _asset_summary(layout, context):
    """Render one compact, read-only working-asset summary."""
    settings = getattr(context.scene, "humanoid_settings", None)
    target = getattr(settings, "target", None) if settings else None
    box = layout.box()
    row = box.row(align=True)
    row.label(text="Current Asset", icon="OBJECT_DATA")
    if target is None:
        row.label(text="None", icon="INFO")
        box.label(text="Create an asset or choose one in a workspace below.")
        return

    row.label(text=target.name)
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

    status = box.row(align=True)
    status.label(text="Rigged" if has_rig else "No Rig", icon="ARMATURE_DATA")
    status.label(text=str(animation_count) + " Clips", icon="ACTION")
    status.label(text=str(component_count) + " Parts", icon="OUTLINER_OB_MESH")


def _draw_component_actions(box, target, hair_component_ui, clothing_component_ui, self_rigged_accessory):
    """Group existing component operators by artist intent without changing their behavior."""
    generated = box.box()
    generated.label(text="Add Generated Component", icon="ADD")
    if target is None:
        generated.label(text="Choose or create a base asset first.", icon="INFO")

    if hair_component_ui is not None:
        row = generated.row()
        row.enabled = target is not None
        row.operator("asset_assistant.generate_hair_shell", text="Hair", icon="OUTLINER_OB_MESH")
    if clothing_component_ui is not None:
        row = generated.row()
        row.enabled = target is not None and clothing_component_ui._supports_shirt(target)
        row.operator("asset_assistant.generate_basic_shirt", text="Shirt", icon="MOD_CLOTH")
    row = generated.row()
    row.enabled = target is not None
    row.operator("asset_assistant.generate_ring_component", text="Ring / Bracelet", icon="MESH_TORUS")
    if self_rigged_accessory is not None:
        row = generated.row()
        row.enabled = target is not None
        row.operator("asset_assistant.generate_self_rigged_accessory", text="Self-Rigged Accessory", icon="ARMATURE_DATA")

    imported = box.box()
    imported.label(text="Bring Your Own Component", icon="IMPORT")
    row = imported.row()
    row.enabled = target is not None
    row.operator("asset_assistant.adopt_selected_component", text="Adopt Selected Mesh", icon="IMPORT")
    imported.label(text="Choose attachment and behavior in the adoption dialog.")
    imported.label(text="Adopted mesh geometry becomes Asset Assistant-managed.")
    imported.label(text="Existing materials remain artist-owned.")


def _draw_animation_adoption(box, target):
    """Present artist-owned animation adoption as a separate, explicit workflow."""
    box.label(text="Bring Your Own Animation", icon="IMPORT")
    box.label(text="Register an existing Blender action for game-engine export.")
    row = box.row()
    row.enabled = target is not None and sum(obj.type == "ARMATURE" for obj in target.children) == 1
    row.scale_y = 1.1
    row.operator("asset_assistant.adopt_animation_action", text="Adopt Existing Action", icon="ACTION")
    box.label(text="Keeps the artist's curves, NLA, and drivers under artist ownership.")
    box.label(text="Asset Assistant adds identity and export metadata only.")


def _stage_proxy(panel, stage):
    """Let the established stage renderer draw inside the single workspace panel."""
    proxy = type("AssetAssistantStageProxy", (), {})()
    proxy.layout = panel.layout
    proxy.stage = stage
    return proxy


def _draw_create(panel, context, ui, modify_ui, working_asset_ui):
    settings = context.scene.humanoid_settings
    panel.layout.prop(settings, "asset_assistant_create_view", expand=True)
    panel.layout.separator()

    if settings.asset_assistant_create_view == "GENERATE":
        ui._WorkflowPanel.draw(_stage_proxy(panel, "MODEL"), context)
        if working_asset_ui is not None:
            box = panel.layout.box()
            box.label(text="Continue Existing Work", icon="FILE_FOLDER")
            row = box.row()
            row.scale_y = 1.1
            row.operator("asset_assistant.open_editable_checkpoint", text="Open Editable Checkpoint (.blend)", icon="FILE_FOLDER")
        return

    if settings.asset_assistant_create_view == "MODIFY":
        modify_ui.ASSET_ASSISTANT_PT_modify.draw(panel, context)
        return

    ui._WorkflowPanel.draw(_stage_proxy(panel, "RIGGING"), context)


def _draw_animate(panel, context, ui, animation_names_ui, animation_adoption_ui):
    ui._WorkflowPanel.draw(_stage_proxy(panel, "ANIMATION"), context)
    target = getattr(context.scene.humanoid_settings, "target", None)

    if target is not None:
        panel.layout.separator()
        clip_box = panel.layout.box()
        animation_names_ui.ASSET_ASSISTANT_PT_animation_names.draw(type("ClipLibraryProxy", (), {"layout": clip_box})(), context)

    if animation_adoption_ui is not None:
        panel.layout.separator()
        _draw_animation_adoption(panel.layout.box(), target)


def _draw_components(panel, context, component_adoption_ui, hair_component_ui, clothing_component_ui,
                     self_rigged_accessory):
    layout = panel.layout
    settings = context.scene.humanoid_settings
    layout.prop(settings, "target")
    target = getattr(settings, "target", None)
    box = layout.box()
    box.label(text="Asset Components", icon="OUTLINER_COLLECTION")
    box.label(text="Build hair, clothing and accessories as separate editable pieces.")
    _draw_component_actions(box, target, hair_component_ui, clothing_component_ui, self_rigged_accessory)


def _draw_export(panel, context, ui, working_asset_ui):
    layout = panel.layout
    settings = context.scene.humanoid_settings
    layout.prop(settings, "target")
    target = getattr(settings, "target", None)
    if target is None:
        layout.label(text="Create or choose an asset first.", icon="INFO")
        return

    setup = layout.box()
    setup.label(text="Export Target", icon="EXPORT")
    setup.prop(settings, "output_target")
    if settings.output_target == "CURA":
        setup.label(text="STL: current pose, millimetres, one solid.")
    else:
        setup.prop(settings, "asset_use")
        setup.prop(settings, "require_textures")

    validation = layout.box()
    validation.label(text="Readiness", icon="CHECKMARK")
    if settings.output_target != "CURA":
        validation.operator("humanoid.prepare_materials", text="Add Missing Materials", icon="MATERIAL")
    action = validation.row()
    action.scale_y = 1.15
    action.operator("humanoid.validate_character", text="Run Validation", icon="CHECKMARK")

    snapshot = settings.validation_results
    if snapshot:
        errors = sum(row.status == "ERROR" for row in snapshot)
        warnings = sum(row.status == "WARN" for row in snapshot)
        passes = sum(row.status == "PASS" for row in snapshot)
        validation.label(text=f"{errors} errors  •  {warnings} warnings  •  {passes} passed",
                         icon="CHECKMARK" if errors == 0 else "ERROR")
        width = max(24, int(context.region.width / 7) - 6)
        ui._draw_validation_results(validation, snapshot, width)
    else:
        validation.label(text="Run validation to create a readiness snapshot.", icon="INFO")

    readiness_rows = snapshot if settings.output_target == "CURA" else ui._export_issues(context)
    ready = ui.is_ready(readiness_rows)
    confidence = layout.box()
    confidence.label(text="Ready to export." if ready else "Needs attention before export.",
                     icon="CHECKMARK" if ready else "ERROR")
    export_row = confidence.row()
    export_row.scale_y = 1.3
    export_row.enabled = ready
    export_row.operator("humanoid.export_asset", text="Export Asset", icon="EXPORT")
    if settings.last_export:
        confidence.label(text="Saved: " + settings.last_export, icon="CHECKMARK")

    if working_asset_ui is not None:
        checkpoint = layout.box()
        checkpoint.label(text="Editable Working State", icon="FILE_BLEND")
        checkpoint.operator("asset_assistant.save_editable_checkpoint",
                            text="Validate + Save Editable Checkpoint (.blend)", icon="FILE_TICK")


def _draw_workspace(panel, context, ui, modify_ui, animation_names_ui, working_asset_ui,
                    component_adoption_ui, hair_component_ui, clothing_component_ui,
                    animation_adoption_ui, self_rigged_accessory):
    layout = panel.layout
    settings = context.scene.humanoid_settings

    title = layout.row(align=True)
    title.scale_y = 1.2
    title.label(text="Asset Assistant", icon="TOOL_SETTINGS")
    layout.label(text="Create. Animate. Prepare. Export.")

    nav = layout.row(align=True)
    nav.scale_y = 1.2
    nav.prop(settings, "asset_assistant_workspace", expand=True)
    _asset_summary(layout, context)
    layout.separator()

    if settings.asset_assistant_workspace == "CREATE":
        _draw_create(panel, context, ui, modify_ui, working_asset_ui)
    elif settings.asset_assistant_workspace == "ANIMATE":
        _draw_animate(panel, context, ui, animation_names_ui, animation_adoption_ui)
    elif settings.asset_assistant_workspace == "COMPONENTS":
        _draw_components(panel, context, component_adoption_ui, hair_component_ui,
                         clothing_component_ui, self_rigged_accessory)
    else:
        _draw_export(panel, context, ui, working_asset_ui)


def _hide_legacy_panel(panel_type):
    """Keep legacy panel classes registered for compatibility but out of the sidebar."""
    def poll(_cls, _context):
        return False
    panel_type.poll = classmethod(poll)


def prepare(ui, modify_ui, animation_names_ui, working_asset_ui=None,
            component_adoption_ui=None, hair_component_ui=None, clothing_component_ui=None,
            animation_adoption_ui=None, self_rigged_accessory=None):
    # Navigation state lives on the existing settings group so saved files and operator
    # contracts stay intact. These properties are presentation-only.
    annotations = ui.HUMANOID_PG_settings.__annotations__
    if "asset_assistant_workspace" not in annotations:
        annotations["asset_assistant_workspace"] = ui.EnumProperty(
            name="Workspace",
            default="CREATE",
            items=[
                ("CREATE", "Create", "Create, modify or rig an asset"),
                ("ANIMATE", "Animate", "Create, preview and manage animation clips"),
                ("COMPONENTS", "Components", "Manage hair, clothing and accessories"),
                ("EXPORT", "Export", "Validate and export for a target application"),
            ],
        )
    if "asset_assistant_create_view" not in annotations:
        annotations["asset_assistant_create_view"] = ui.EnumProperty(
            name="Create View",
            default="GENERATE",
            items=[
                ("GENERATE", "Generate", "Create a new base asset"),
                ("MODIFY", "Modify", "Safely modify the current asset"),
                ("RIG", "Rig", "Rig or pose the current asset"),
            ],
        )

    # The Create panel becomes the one visible Asset Assistant workspace.
    ui.HUMANOID_PT_panel.bl_label = "Asset Assistant"
    ui.HUMANOID_PT_panel.bl_category = _CATEGORY
    ui.HUMANOID_PT_panel.bl_order = 0
    ui.HUMANOID_PT_panel.bl_options = set(getattr(ui.HUMANOID_PT_panel, "bl_options", set())) - {"DEFAULT_CLOSED"}

    def draw_workspace(panel, context):
        _draw_workspace(
            panel, context, ui, modify_ui, animation_names_ui, working_asset_ui,
            component_adoption_ui, hair_component_ui, clothing_component_ui,
            animation_adoption_ui, self_rigged_accessory,
        )

    draw_workspace._asset_assistant_workspace = True
    ui.HUMANOID_PT_panel.draw = draw_workspace

    legacy_panels = (
        modify_ui.ASSET_ASSISTANT_PT_modify,
        ui.HUMANOID_PT_rigging,
        ui.HUMANOID_PT_animations,
        ui.HUMANOID_PT_validation,
        ui.HUMANOID_PT_export,
        animation_names_ui.ASSET_ASSISTANT_PT_animation_names,
    )
    for order, panel in enumerate(legacy_panels, start=1):
        panel.bl_category = _CATEGORY
        panel.bl_order = order
        _hide_legacy_panel(panel)
