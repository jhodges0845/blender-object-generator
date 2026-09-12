# SPDX-License-Identifier: GPL-3.0-or-later
"""Present Asset Assistant as one ordered, polished Blender sidebar workflow."""

_CATEGORY = "Asset Assistant"


def _asset_summary(layout, context):
    """Render a compact, read-only working-asset summary without changing workflow state."""
    settings = getattr(context.scene, "humanoid_settings", None)
    target = getattr(settings, "target", None) if settings else None
    box = layout.box()
    row = box.row(align=True)
    row.label(text="Current Asset", icon="OBJECT_DATA")
    if target is None:
        box.label(text="No asset selected", icon="INFO")
        box.label(text="Create an asset or choose an existing generated asset.")
        return

    box.label(text=target.name, icon="OUTLINER_OB_GROUP_INSTANCE")
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
    status.label(text=str(animation_count) + " Animations", icon="ACTION")
    box.label(text=str(component_count) + " Mesh Components", icon="OUTLINER_OB_MESH")


def _decorate_panel(panel_type, stage_label, stage_icon):
    """Add consistent product identity and context while preserving the existing panel draw."""
    original_draw = panel_type.draw
    if getattr(original_draw, "_asset_assistant_polished_shell", False):
        return

    def draw_with_shell(panel, context):
        layout = panel.layout
        title = layout.row(align=True)
        title.scale_y = 1.15
        title.label(text="Asset Assistant", icon="TOOL_SETTINGS")
        subtitle = layout.row()
        subtitle.label(text=stage_label, icon=stage_icon)
        _asset_summary(layout, context)
        layout.separator()
        original_draw(panel, context)

    draw_with_shell._asset_assistant_polished_shell = True
    if getattr(original_draw, "_asset_assistant_confidence_header", False):
        draw_with_shell._asset_assistant_confidence_header = True
    panel_type.draw = draw_with_shell


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


def _wrap_confidence_panel(panel_type, heading, detail, icon):
    """Add confidence-oriented context before existing validation/export controls."""
    original_draw = panel_type.draw
    if getattr(original_draw, "_asset_assistant_confidence_header", False):
        return

    def draw_with_confidence(panel, context):
        layout = panel.layout
        box = layout.box()
        box.label(text=heading, icon=icon)
        box.label(text=detail)
        target = getattr(context.scene.humanoid_settings, "target", None)
        if target is None:
            box.label(text="Choose an asset before continuing.", icon="INFO")
        else:
            box.label(text="Current target: " + target.name, icon="OBJECT_DATA")
        layout.separator()
        original_draw(panel, context)

    draw_with_confidence._asset_assistant_confidence_header = True
    panel_type.draw = draw_with_confidence


def prepare(ui, modify_ui, animation_names_ui, working_asset_ui=None,
            component_adoption_ui=None, hair_component_ui=None, clothing_component_ui=None,
            animation_adoption_ui=None, self_rigged_accessory=None):
    panels = (
        (ui.HUMANOID_PT_panel, "Create", 0),
        (modify_ui.ASSET_ASSISTANT_PT_modify, "Modify", 1),
        (ui.HUMANOID_PT_rigging, "Rig", 2),
        (ui.HUMANOID_PT_animations, "Animate", 3),
        (ui.HUMANOID_PT_validation, "Validate", 4),
        (ui.HUMANOID_PT_export, "Export", 5),
    )
    for panel, label, order in panels:
        panel.bl_label = label
        panel.bl_category = _CATEGORY
        panel.bl_order = order
        options = set(getattr(panel, "bl_options", set()))
        if order == 0:
            options.discard("DEFAULT_CLOSED")
        else:
            options.add("DEFAULT_CLOSED")
        panel.bl_options = options

    animation_names_ui.ASSET_ASSISTANT_PT_animation_names.bl_category = _CATEGORY

    if animation_adoption_ui is not None:
        original_animation_draw = ui.HUMANOID_PT_animations.draw
        if not getattr(original_animation_draw, "_asset_assistant_external_actions", False):
            def draw_animation_with_external_actions(panel, context):
                original_animation_draw(panel, context)
                layout = panel.layout
                layout.separator()
                box = layout.box()
                target = getattr(context.scene.humanoid_settings, "target", None)
                _draw_animation_adoption(box, target)
            draw_animation_with_external_actions._asset_assistant_external_actions = True
            ui.HUMANOID_PT_animations.draw = draw_animation_with_external_actions

    if component_adoption_ui is not None:
        original_generate_draw = ui.HUMANOID_PT_panel.draw
        if not getattr(original_generate_draw, "_asset_assistant_components", False):
            def draw_generate_with_components(panel, context):
                original_generate_draw(panel, context)
                layout = panel.layout
                layout.separator()
                box = layout.box()
                box.label(text="Components", icon="OUTLINER_COLLECTION")
                box.label(text="Build the asset in separate editable pieces.")
                target = getattr(context.scene.humanoid_settings, "target", None)
                _draw_component_actions(
                    box, target, hair_component_ui, clothing_component_ui, self_rigged_accessory)

            draw_generate_with_components._asset_assistant_components = True
            ui.HUMANOID_PT_panel.draw = draw_generate_with_components

    if working_asset_ui is not None:
        original_generate_draw = ui.HUMANOID_PT_panel.draw
        if not getattr(original_generate_draw, "_asset_assistant_checkpoint_open", False):
            def draw_generate_with_open(panel, context):
                original_generate_draw(panel, context)
                layout = panel.layout
                layout.separator()
                box = layout.box()
                box.label(text="Continue Existing Work", icon="FILE_FOLDER")
                box.label(text="Resume an Asset Assistant working file without rebuilding it.")
                action = box.row()
                action.scale_y = 1.15
                action.operator("asset_assistant.open_editable_checkpoint", text="Open Editable Checkpoint (.blend)", icon="FILE_FOLDER")
                status = context.scene.get("asset_assistant_working_state_status")
                message = context.scene.get("asset_assistant_working_state_message")
                if status and message:
                    box.label(text=message, icon="CHECKMARK" if status == "READY" else "ERROR")
            draw_generate_with_open._asset_assistant_checkpoint_open = True
            ui.HUMANOID_PT_panel.draw = draw_generate_with_open

        original_export_draw = ui.HUMANOID_PT_export.draw
        if not getattr(original_export_draw, "_asset_assistant_checkpoint_action", False):
            def draw_export_with_checkpoint(panel, context):
                original_export_draw(panel, context)
                layout = panel.layout
                layout.separator()
                box = layout.box()
                box.label(text="Editable working state")
                box.operator("asset_assistant.save_editable_checkpoint", text="Validate + Save Editable Checkpoint (.blend)", icon="FILE_TICK")
                box.label(text="Validates ownership/continuity before saving.")
            draw_export_with_checkpoint._asset_assistant_checkpoint_action = True
            ui.HUMANOID_PT_export.draw = draw_export_with_checkpoint

    _wrap_confidence_panel(
        ui.HUMANOID_PT_validation,
        "Readiness Check",
        "Review target requirements and resolve issues before export.",
        "CHECKMARK",
    )
    _wrap_confidence_panel(
        ui.HUMANOID_PT_export,
        "Export Confidence",
        "Export stays locked until the current target passes its readiness checks.",
        "EXPORT",
    )

    # Apply the visual shell last so it wraps all existing workflow extensions rather than
    # replacing them. This is intentionally presentation-only: every operator and property
    # remains owned by its existing adapter module.
    shell_panels = (
        (ui.HUMANOID_PT_panel, "Create an asset", "OUTLINER_OB_MESH"),
        (modify_ui.ASSET_ASSISTANT_PT_modify, "Refine the current asset", "MODIFIER"),
        (ui.HUMANOID_PT_rigging, "Prepare for posing", "ARMATURE_DATA"),
        (ui.HUMANOID_PT_animations, "Build and preview motion", "ACTION"),
        (ui.HUMANOID_PT_validation, "Check game readiness", "CHECKMARK"),
        (ui.HUMANOID_PT_export, "Send to your target", "EXPORT"),
    )
    for panel, label, icon in shell_panels:
        _decorate_panel(panel, label, icon)
