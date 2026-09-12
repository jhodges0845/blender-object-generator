# SPDX-License-Identifier: GPL-3.0-or-later
"""Artist-facing generation and adoption of reusable Blender components."""

import uuid

import bpy

from object_core.component_primitives import ring_mesh

from .components import _armature, attach_rigid_component
from .core import AttachmentMode, ComponentBehavior, ComponentKind, ComponentRecord, RigBinding
from .imported_components import adopt_rigid_component, adopt_skinned_component


def _target(context):
    scene = context.scene if context else None
    settings = getattr(scene, "humanoid_settings", None) if scene else None
    root = settings.target if settings else None
    if root is None or root.get("generator") != "object_generator":
        return None
    return root


def _selected_meshes(context):
    return [obj for obj in context.selected_objects if obj.type == "MESH"]


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


def _behavior_items(include_skinned=True):
    items = [
        (ComponentBehavior.STATIC.value, "Static", "No independent deformation or simulation"),
        (ComponentBehavior.RIGID.value, "Rigid", "Follow the asset root or one bone without deforming"),
    ]
    if include_skinned:
        items.append((
            ComponentBehavior.PARENT_SKINNED.value,
            "Skinned to Parent Rig",
            "Use existing vertex weights with the Asset Assistant armature",
        ))
    return tuple(items)


def _mode_for_behavior(value):
    behavior = ComponentBehavior(value)
    if behavior == ComponentBehavior.PARENT_SKINNED:
        return behavior, AttachmentMode.SKINNED, RigBinding.PARENT
    if behavior in (ComponentBehavior.STATIC, ComponentBehavior.RIGID):
        return behavior, AttachmentMode.RIGID, RigBinding.NONE
    raise ValueError("This component behavior is not executable in the current Blender workflow yet.")


def _select_only(context, obj):
    for selected in context.selected_objects:
        selected.select_set(False)
    obj.select_set(True)
    context.view_layer.objects.active = obj


class ASSET_ASSISTANT_OT_generate_ring_component(bpy.types.Operator):
    bl_idname = "asset_assistant.generate_ring_component"
    bl_label = "Generate Ring / Bracelet"
    bl_description = "Create a separate lightweight accessory asset and attach it to the active Asset Assistant base"
    bl_options = {"REGISTER", "UNDO"}

    component_name: bpy.props.StringProperty(name="Name", default="Ring Accessory")
    behavior: bpy.props.EnumProperty(name="Behavior", items=_behavior_items(False), default=ComponentBehavior.RIGID.value)
    attachment_target: bpy.props.EnumProperty(name="Attach To", items=_attachment_items)
    major_radius_cm: bpy.props.FloatProperty(name="Radius (cm)", default=3.0, min=0.3, max=30.0)
    thickness_cm: bpy.props.FloatProperty(name="Thickness (cm)", default=0.45, min=0.05, max=5.0)

    @classmethod
    def poll(cls, context):
        return context.scene is not None and context.mode == "OBJECT" and _target(context) is not None

    def invoke(self, context, event):
        self.attachment_target = "asset_root"
        return context.window_manager.invoke_props_dialog(self, width=440)

    def draw(self, context):
        layout = self.layout
        layout.prop(self, "component_name")
        layout.prop(self, "behavior")
        layout.prop(self, "attachment_target")
        layout.prop(self, "major_radius_cm")
        layout.prop(self, "thickness_cm")
        box = layout.box()
        box.label(text="Generated as a separate accessory asset.")
        box.label(text="Move/rotate/scale it after generation to fit the character.")

    def execute(self, context):
        root = _target(context)
        try:
            behavior, mode, rig_binding = _mode_for_behavior(self.behavior)
            if mode != AttachmentMode.RIGID:
                raise ValueError("Generated ring/bracelet currently supports Static or Rigid behavior.")
            record = ComponentRecord(
                component_id="generated-" + uuid.uuid4().hex,
                kind=ComponentKind.ACCESSORY,
                provider_key="primitive.ring",
                attachment_target=self.attachment_target,
                attachment_mode=mode,
                owns_geometry=True,
                owns_materials=False,
                owns_rig=False,
                rig_binding=rig_binding,
                behavior=behavior,
            )
            mesh = ring_mesh(self.major_radius_cm, self.thickness_cm)
            component_root = attach_rigid_component(root, mesh, record, name=self.component_name.strip() or "Ring Accessory")
        except (TypeError, ValueError, RuntimeError, AttributeError) as error:
            self.report({"ERROR"}, str(error))
            return {"CANCELLED"}
        _select_only(context, component_root)
        self.report({"INFO"}, "Generated separate accessory: " + record.component_id)
        return {"FINISHED"}


class ASSET_ASSISTANT_OT_adopt_selected_component(bpy.types.Operator):
    bl_idname = "asset_assistant.adopt_selected_component"
    bl_label = "Adopt Selected Component"
    bl_description = "Register one selected external mesh as an Asset Assistant component without copying it"
    bl_options = {"REGISTER", "UNDO"}

    component_id: bpy.props.StringProperty(name="Component ID")
    component_name: bpy.props.StringProperty(name="Name")
    kind: bpy.props.EnumProperty(
        name="Kind",
        items=(
            (ComponentKind.HAIR.value, "Hair", "Reusable hair component"),
            (ComponentKind.CLOTHING.value, "Clothing", "Reusable clothing component"),
            (ComponentKind.ACCESSORY.value, "Accessory", "Reusable accessory component"),
        ),
        default=ComponentKind.ACCESSORY.value,
    )
    behavior: bpy.props.EnumProperty(
        name="Behavior",
        items=_behavior_items(True),
        default=ComponentBehavior.RIGID.value,
    )
    attachment_target: bpy.props.EnumProperty(name="Attach To", items=_attachment_items)

    @classmethod
    def poll(cls, context):
        return (
            context.scene is not None
            and context.mode == "OBJECT"
            and _target(context) is not None
            and len(_selected_meshes(context)) == 1
        )

    def invoke(self, context, event):
        mesh_object = _selected_meshes(context)[0]
        self.component_id = "imported-" + uuid.uuid4().hex
        self.component_name = mesh_object.name
        self.behavior = (
            ComponentBehavior.PARENT_SKINNED.value
            if any(modifier.type == "ARMATURE" for modifier in mesh_object.modifiers)
            else ComponentBehavior.RIGID.value
        )
        self.attachment_target = "asset_root"
        return context.window_manager.invoke_props_dialog(self, width=440)

    def draw(self, context):
        layout = self.layout
        layout.prop(self, "component_name")
        layout.prop(self, "kind")
        layout.prop(self, "behavior")
        if self.behavior != ComponentBehavior.PARENT_SKINNED.value:
            layout.prop(self, "attachment_target")
        else:
            box = layout.box()
            box.label(text="Binds to the active asset's generated armature.")
            box.label(text="Existing vertex-group weights must use matching bone names.")
        layout.prop(self, "component_id")
        box = layout.box()
        box.label(text="Ownership transfer")
        box.label(text="The selected mesh becomes managed component geometry.")
        box.label(text="Removing the component may delete that mesh.")
        box.label(text="Materials remain artist-owned and are not claimed.")

    def execute(self, context):
        root = _target(context)
        meshes = _selected_meshes(context)
        if len(meshes) != 1:
            self.report({"ERROR"}, "Select exactly one external mesh to adopt.")
            return {"CANCELLED"}
        mesh_object = meshes[0]
        try:
            behavior, mode, rig_binding = _mode_for_behavior(self.behavior)
            record = ComponentRecord(
                component_id=self.component_id.strip(),
                kind=ComponentKind(self.kind),
                provider_key="artist_authored",
                attachment_target=("body" if mode == AttachmentMode.SKINNED else self.attachment_target),
                attachment_mode=mode,
                owns_geometry=True,
                owns_materials=False,
                owns_rig=False,
                rig_binding=rig_binding,
                behavior=behavior,
            )
            if mode == AttachmentMode.SKINNED:
                component_root = adopt_skinned_component(root, mesh_object, record, name=self.component_name)
            else:
                component_root = adopt_rigid_component(root, mesh_object, record, name=self.component_name)
        except (TypeError, ValueError, RuntimeError, AttributeError) as error:
            self.report({"ERROR"}, str(error))
            return {"CANCELLED"}

        _select_only(context, component_root)
        self.report({"INFO"}, "Adopted component: " + record.component_id)
        return {"FINISHED"}


_CLASSES = (
    ASSET_ASSISTANT_OT_generate_ring_component,
    ASSET_ASSISTANT_OT_adopt_selected_component,
)


def register():
    for cls in _CLASSES:
        bpy.utils.register_class(cls)


def unregister():
    for cls in reversed(_CLASSES):
        bpy.utils.unregister_class(cls)


__all__ = [
    "ASSET_ASSISTANT_OT_generate_ring_component",
    "ASSET_ASSISTANT_OT_adopt_selected_component",
    "register",
    "unregister",
]
