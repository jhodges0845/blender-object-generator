# SPDX-License-Identifier: GPL-3.0-or-later
"""Artist-facing registration of imported Blender meshes as components."""

import uuid

import bpy

from .core import AttachmentMode, ComponentKind, ComponentRecord
from .imported_components import adopt_rigid_component


_KIND_ITEMS = (
    ("ACCESSORY", "Accessory", "Rigid reusable prop or attachment"),
    ("HAIR", "Hair", "Artist-authored hair asset"),
    ("CLOTHING", "Clothing", "Artist-authored clothing asset"),
)


class ASSET_ASSISTANT_OT_adopt_selected_component(bpy.types.Operator):
    bl_idname = "asset_assistant.adopt_selected_component"
    bl_label = "Adopt Selected Component"
    bl_description = (
        "Register one selected external mesh as an owned Asset Assistant component; "
        "the mesh is not copied"
    )

    component_id: bpy.props.StringProperty(name="Component ID")
    kind: bpy.props.EnumProperty(name="Kind", items=_KIND_ITEMS, default="ACCESSORY")
    attachment_target: bpy.props.StringProperty(
        name="Attachment Target",
        default="asset_root",
        description="Use asset_root or bone:<bone-name>",
    )

    @classmethod
    def poll(cls, context):
        settings = getattr(context.scene, "humanoid_settings", None)
        return (
            context.mode == "OBJECT"
            and settings is not None
            and settings.target is not None
            and any(obj.type == "MESH" for obj in context.selected_objects)
        )

    def invoke(self, context, event):
        if not self.component_id:
            self.component_id = "imported-" + uuid.uuid4().hex[:12]
        return context.window_manager.invoke_props_dialog(self)

    def execute(self, context):
        root = context.scene.humanoid_settings.target
        meshes = [obj for obj in context.selected_objects if obj.type == "MESH"]
        if len(meshes) != 1:
            self.report({"ERROR"}, "Select exactly one external mesh to adopt.")
            return {"CANCELLED"}
        kind = ComponentKind[self.kind]
        record = ComponentRecord(
            component_id=self.component_id.strip(),
            kind=kind,
            provider_key="imported.blender",
            attachment_target=self.attachment_target.strip(),
            attachment_mode=AttachmentMode.RIGID,
            owns_geometry=True,
            owns_materials=False,
            owns_rig=False,
        )
        try:
            component_root = adopt_rigid_component(root, meshes[0], record, name=meshes[0].name)
        except (TypeError, ValueError, RuntimeError) as error:
            self.report({"ERROR"}, str(error))
            return {"CANCELLED"}
        context.view_layer.objects.active = component_root
        component_root.select_set(True)
        self.report({"INFO"}, "Adopted component: " + record.component_id)
        return {"FINISHED"}


_CLASSES = (ASSET_ASSISTANT_OT_adopt_selected_component,)


def register():
    for cls in _CLASSES:
        bpy.utils.register_class(cls)


def unregister():
    for cls in reversed(_CLASSES):
        bpy.utils.unregister_class(cls)


__all__ = ["ASSET_ASSISTANT_OT_adopt_selected_component", "register", "unregister"]
