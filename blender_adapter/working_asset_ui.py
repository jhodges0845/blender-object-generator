# SPDX-License-Identifier: GPL-3.0-or-later
"""Editable Asset Assistant working-state checkpoint workflow."""

from pathlib import Path

import bpy
from bpy_extras.io_utils import ExportHelper


class ASSET_ASSISTANT_OT_save_editable_checkpoint(bpy.types.Operator, ExportHelper):
    bl_idname = "asset_assistant.save_editable_checkpoint"
    bl_label = "Save Editable Checkpoint"
    bl_description = (
        "Save a complete editable .blend copy without changing the current working file; "
        "engine export remains a separate workflow"
    )
    filename_ext = ".blend"
    filter_glob: bpy.props.StringProperty(default="*.blend", options={"HIDDEN"})

    @classmethod
    def poll(cls, context):
        return context.scene is not None and context.mode == "OBJECT"

    def invoke(self, context, event):
        current = Path(bpy.data.filepath).stem if bpy.data.filepath else "asset-assistant-working-asset"
        self.filepath = current + ".checkpoint.blend"
        return ExportHelper.invoke(self, context, event)

    def execute(self, context):
        path = Path(self.filepath)
        if path.suffix.lower() != ".blend":
            path = path.with_suffix(".blend")
        try:
            result = bpy.ops.wm.save_as_mainfile(filepath=str(path), copy=True)
        except (RuntimeError, OSError, ValueError) as error:
            self.report({"ERROR"}, str(error))
            return {"CANCELLED"}
        if "FINISHED" not in result:
            self.report({"ERROR"}, "Blender did not finish saving the editable checkpoint.")
            return {"CANCELLED"}
        self.report({"INFO"}, "Editable checkpoint saved without changing the current working file.")
        return {"FINISHED"}


class ASSET_ASSISTANT_PT_working_asset(bpy.types.Panel):
    bl_label = "Working Asset"
    bl_idname = "ASSET_ASSISTANT_PT_working_asset"
    bl_space_type = "VIEW_3D"
    bl_region_type = "UI"
    bl_category = "Asset Assistant"
    bl_order = 5
    bl_options = {"DEFAULT_CLOSED"}

    def draw(self, context):
        layout = self.layout
        layout.label(text="Editable working state")
        layout.operator(
            "asset_assistant.save_editable_checkpoint",
            text="Save Editable Checkpoint (.blend)",
            icon="FILE_TICK",
        )
        layout.label(text="Game/print files belong in Export.")


_CLASSES = (
    ASSET_ASSISTANT_OT_save_editable_checkpoint,
    ASSET_ASSISTANT_PT_working_asset,
)


def register():
    for cls in _CLASSES:
        bpy.utils.register_class(cls)


def unregister():
    for cls in reversed(_CLASSES):
        bpy.utils.unregister_class(cls)


__all__ = [
    "ASSET_ASSISTANT_OT_save_editable_checkpoint",
    "ASSET_ASSISTANT_PT_working_asset",
    "register",
    "unregister",
]
