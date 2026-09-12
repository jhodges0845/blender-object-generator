# SPDX-License-Identifier: GPL-3.0-or-later
"""Temporary visual lab for experimenting with Asset Assistant navigation widgets.

This panel is intentionally isolated from the production workspace navigation so
we can compare Blender-native approaches in the real sidebar before promoting
one into the main UI.
"""

import bpy
from bpy.props import StringProperty


_WORKSPACES = (
    ("CREATE", "Create", "USER"),
    ("ANIMATE", "Animate", "ACTION"),
    ("COMPONENTS", "Components", "CUBE"),
    ("EXPORT", "Export", "EXPORT"),
)


class ASSET_ASSISTANT_OT_widget_lab_workspace(bpy.types.Operator):
    """Switch workspace from an experimental navigation control."""

    bl_idname = "asset_assistant.widget_lab_workspace"
    bl_label = "Widget Lab Workspace"
    bl_options = {"INTERNAL"}

    workspace: StringProperty()

    def execute(self, context):
        context.scene.humanoid_settings.asset_assistant_workspace = self.workspace
        return {"FINISHED"}


def _workspace_button(layout, key, label, icon, scale_y=1.0):
    row = layout.row(align=True)
    row.scale_y = scale_y
    op = row.operator(
        ASSET_ASSISTANT_OT_widget_lab_workspace.bl_idname,
        text=label,
        icon=icon,
        depress=False,
    )
    op.workspace = key
    return row


class ASSET_ASSISTANT_PT_nav_widget_lab(bpy.types.Panel):
    """Disposable sidebar playground for navigation experiments."""

    bl_label = "Navigation Widget Lab"
    bl_idname = "ASSET_ASSISTANT_PT_nav_widget_lab"
    bl_space_type = "VIEW_3D"
    bl_region_type = "UI"
    bl_category = "Asset Assistant"
    bl_order = 99
    bl_options = {"DEFAULT_CLOSED"}

    def draw(self, context):
        layout = self.layout
        settings = context.scene.humanoid_settings

        intro = layout.box()
        intro.label(text="EXPERIMENTAL ONLY", icon="EXPERIMENTAL")
        intro.label(text="Nothing here changes the production navigation.")
        intro.label(text="Use this panel to compare widget ideas in Blender.")

        native = layout.box()
        native.label(text="A  •  Native one-piece buttons")
        native.label(text="Current safe behavior: one hit target, icon beside text.")
        row = native.row(align=True)
        row.scale_y = 1.65
        for key, label, icon in _WORKSPACES:
            row.prop_enum(
                settings,
                "asset_assistant_workspace",
                key,
                text=label,
                icon=icon,
            )

        cards = layout.box()
        cards.label(text="B  •  Large single-button cards")
        cards.label(text="Still one hit target; tests size and visual weight.")
        for first, second in ((_WORKSPACES[0], _WORKSPACES[1]), (_WORKSPACES[2], _WORKSPACES[3])):
            row = cards.row(align=True)
            row.scale_y = 2.4
            for key, label, icon in (first, second):
                op = row.operator(
                    ASSET_ASSISTANT_OT_widget_lab_workspace.bl_idname,
                    text=label,
                    icon=icon,
                    depress=settings.asset_assistant_workspace == key,
                )
                op.workspace = key

        stacked = layout.box()
        stacked.label(text="C  •  Stacked-card visual prototype")
        stacked.label(text="Icon and text are separate controls, but both do the same action.")
        stacked.label(text="This is here only to judge the desired vertical composition.")
        row = stacked.row(align=True)
        for key, label, icon in _WORKSPACES:
            card = row.column(align=True)
            icon_row = card.row(align=True)
            icon_row.scale_y = 2.0
            icon_op = icon_row.operator(
                ASSET_ASSISTANT_OT_widget_lab_workspace.bl_idname,
                text="",
                icon=icon,
                depress=settings.asset_assistant_workspace == key,
            )
            icon_op.workspace = key
            text_op = card.operator(
                ASSET_ASSISTANT_OT_widget_lab_workspace.bl_idname,
                text=label,
                depress=settings.asset_assistant_workspace == key,
            )
            text_op.workspace = key

        probe = layout.box()
        probe.label(text="D  •  Multiline-label probe")
        probe.label(text="Tests whether this Blender build honors line breaks in button text.")
        row = probe.row(align=True)
        row.scale_y = 2.4
        for key, label, icon in _WORKSPACES:
            op = row.operator(
                ASSET_ASSISTANT_OT_widget_lab_workspace.bl_idname,
                text=label + "\n" + label.upper(),
                icon=icon,
                depress=settings.asset_assistant_workspace == key,
            )
            op.workspace = key


_CLASSES = (
    ASSET_ASSISTANT_OT_widget_lab_workspace,
    ASSET_ASSISTANT_PT_nav_widget_lab,
)


def register():
    for cls in _CLASSES:
        bpy.utils.register_class(cls)


def unregister():
    for cls in reversed(_CLASSES):
        bpy.utils.unregister_class(cls)
