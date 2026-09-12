# SPDX-License-Identifier: GPL-3.0-or-later
"""Artist-facing registration of imported Blender objects as reusable components."""

import uuid

import bpy

from .components import _armature
from .core import AttachmentMode, ComponentKind, ComponentRecord, RigBinding
from .imported_components import adopt_rigid_component


def _target(context):
    scene = context.scene if context else None
    settings = getattr(scene, "humanoid_settings", None) if scene else None
    root = settings.target if settings else None
    if root is None or root.get("generator") != "object_generator":
        return None
    return root


def _attachment_items(self, context):
    items = [("asset_root", "Asset Root", "Move with the complete Asset Assistant asset")]
    root = _target(context)
    if root is None:
        return items
    try:
        armature = _armature(root)
    except ValueError:
        return items
    for bone in armature.data.bones:
        value = "bone:" + bone.name
        items.append((value, bone.name, "Attach rigidly to bone " + bone.name))
    return items


class ASSET_ASSISTANT_OT_adopt_rigid_component(bpy.types.Operator):
    bl_idname = "asset_assistant.adopt_rigid_component"
    bl_label = "Register Selected Component"
    bl_description = (
        "Transfer ownership of the selected standalone mesh to the current Asset Assistant asset"
    )
    bl_options = {"REGISTER", "UNDO"}

    component_id: bpy.props.StringProperty(name="Component ID")
    component_name: bpy.props.StringProperty(name="Name")
    component_kind: bpy.props.EnumProperty(
        name="Kind",
        items=(
            (ComponentKind.HAIR.value, "Hair", "Reusable hair component"),
            (ComponentKind.CLOTHING.value, "Clothing", "Reusable clothing component"),
            (ComponentKind.ACCESSORY.value, "Accessory", "Reusable rigid accessory component"),
        ),
        default=ComponentKind.ACCESSORY.value,
    )
    attachment_target: bpy.props.EnumProperty(
        name="Attach To",
        items=_attachment_items,
    )

    @classmethod
    def poll(cls, context):
        return (
            context.scene is not None
            and context.mode == "OBJECT"
            and _target(context) is not None
            and context.active_object is not None
            and context.active_object.type == "MESH"
        )

    def invoke(self, context, event):
        mesh_object = context.active_object
        self.component_id = "component-" + uuid.uuid4().hex
        self.component_name = mesh_object.name
        self.attachment_target = "asset_root"
        return context.window_manager.invoke_props_dialog(self, width=420)

    def draw(self, context):
        layout = self.layout
        layout.prop(self, "component_name")
        layout.prop(self, "component_kind")
        layout.prop(self, "attachment_target")
        layout.prop(self, "component_id")
        box = layout.box()
        box.label(text="Ownership transfer")
        box.label(text="The selected mesh becomes managed component geometry.")
        box.label(text="Materials remain artist-owned and are not claimed.")

    def execute(self, context):
        root = _target(context)
        mesh_object = context.active_object
        try:
            record = ComponentRecord(
                component_id=self.component_id.strip(),
                kind=ComponentKind(self.component_kind),
                provider_key="artist_authored",
                attachment_target=self.attachment_target,
                attachment_mode=AttachmentMode.RIGID,
                owns_geometry=True,
                owns_materials=False,
                owns_rig=False,
                rig_binding=RigBinding.NONE,
            )
            component_root = adopt_rigid_component(
                root,
                mesh_object,
                record,
                name=self.component_name,
            )
        except (TypeError, ValueError, RuntimeError, AttributeError) as error:
            self.report({"ERROR"}, str(error))
            return {"CANCELLED"}

        for obj in context.selected_objects:
            obj.select_set(False)
        component_root.select_set(True)
        context.view_layer.objects.active = component_root
        self.report({"INFO"}, "Selected mesh registered as reusable Asset Assistant component.")
        return {"FINISHED"}


_CLASSES = (ASSET_ASSISTANT_OT_adopt_rigid_component,)


def register():
    for cls in _CLASSES:
        bpy.utils.register_class(cls)


def unregister():
    for cls in reversed(_CLASSES):
        bpy.utils.unregister_class(cls)


__all__ = [
    "ASSET_ASSISTANT_OT_adopt_rigid_component",
    "register",
    "unregister",
]
