# SPDX-License-Identifier: GPL-3.0-or-later
"""Present Asset Assistant as one ordered Blender sidebar workflow."""

_CATEGORY = "Asset Assistant"


def prepare(ui, modify_ui, animation_names_ui, working_asset_ui=None,
            component_adoption_ui=None, hair_component_ui=None, clothing_component_ui=None,
            animation_adoption_ui=None, self_rigged_accessory=None):
    panels = (
        (ui.HUMANOID_PT_panel, "Generate", 0),
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
                box.label(text="Existing / imported animations")
                row = box.row()
                target = getattr(context.scene.humanoid_settings, "target", None)
                row.enabled = target is not None and sum(obj.type == "ARMATURE" for obj in target.children) == 1
                row.operator("asset_assistant.adopt_animation_action", text="Adopt Existing Action", icon="ACTION")
                box.label(text="Registers identity/export metadata without claiming artist curves.")
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
                box.label(text="Reusable components")
                target = getattr(context.scene.humanoid_settings, "target", None)
                if target is None:
                    box.label(text="Choose or generate a base asset first.")
                if hair_component_ui is not None:
                    row = box.row(); row.enabled = target is not None
                    row.operator("asset_assistant.generate_hair_shell", text="Generate Hair Shell", icon="OUTLINER_OB_MESH")
                if clothing_component_ui is not None:
                    row = box.row(); row.enabled = target is not None and clothing_component_ui._supports_shirt(target)
                    row.operator("asset_assistant.generate_basic_shirt", text="Generate Basic Shirt", icon="MOD_CLOTH")
                row = box.row(); row.enabled = target is not None
                row.operator("asset_assistant.generate_ring_component", text="Generate Ring / Bracelet", icon="MESH_TORUS")
                if self_rigged_accessory is not None:
                    row = box.row(); row.enabled = target is not None
                    row.operator("asset_assistant.generate_self_rigged_accessory", text="Generate Self-Rigged Accessory", icon="ARMATURE_DATA")
                row = box.row(); row.enabled = target is not None
                row.operator("asset_assistant.adopt_selected_component", text="Adopt Selected External Mesh", icon="IMPORT")
                box.label(text="Pick behavior and attachment in the dialog.")
                box.label(text="Hair, clothing and accessories stay separate from the body.")

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
                box.label(text="Continue existing work")
                box.operator("asset_assistant.open_editable_checkpoint", text="Open Editable Checkpoint (.blend)", icon="FILE_FOLDER")
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
