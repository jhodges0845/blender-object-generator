# SPDX-License-Identifier: GPL-3.0-or-later
"""Generic self-rigged accessory proof with independent rig and animation ownership."""

import json
import uuid

import bpy

from .components import _documents, _set_documents, inspect_component
from .core import (
    AttachmentMode,
    ComponentBehavior,
    ComponentKind,
    ComponentRecord,
    RigBinding,
    component_document,
)


def _target(context):
    settings = getattr(context.scene, "humanoid_settings", None) if context.scene else None
    root = settings.target if settings else None
    return root if root is not None and root.get("generator") == "object_generator" else None


def _cube_geometry(center, size):
    cx, cy, cz = center
    sx, sy, sz = (value / 2.0 for value in size)
    verts = [
        (cx - sx, cy - sy, cz - sz), (cx + sx, cy - sy, cz - sz),
        (cx + sx, cy + sy, cz - sz), (cx - sx, cy + sy, cz - sz),
        (cx - sx, cy - sy, cz + sz), (cx + sx, cy - sy, cz + sz),
        (cx + sx, cy + sy, cz + sz), (cx - sx, cy + sy, cz + sz),
    ]
    faces = [
        (0, 1, 2, 3), (4, 7, 6, 5), (0, 4, 5, 1),
        (1, 5, 6, 2), (2, 6, 7, 3), (4, 0, 3, 7),
    ]
    return verts, faces


def create_self_rigged_gauntlet(root, *, name="Mechanical Gauntlet"):
    """Create a generic two-segment accessory with an independently owned armature/action."""
    if root is None or root.get("generator") != "object_generator":
        raise ValueError("choose an Asset Assistant base asset first")
    coordinate_scale = root.get("coordinate_scale")
    if not isinstance(coordinate_scale, (int, float)) or coordinate_scale <= 0:
        raise ValueError("asset root has an invalid coordinate scale")

    component_id = "generated-" + uuid.uuid4().hex
    record = ComponentRecord(
        component_id=component_id,
        kind=ComponentKind.ACCESSORY,
        provider_key="primitive.mechanical_gauntlet",
        attachment_target="asset_root",
        attachment_mode=AttachmentMode.SKINNED,
        parameters=(("segments", 2),),
        owns_geometry=True,
        owns_materials=False,
        owns_rig=True,
        rig_binding=RigBinding.OWNED,
        behavior=ComponentBehavior.SELF_RIGGED,
    )
    document = component_document(record)
    collection = root.users_collection[0]
    created_objects = []
    created_meshes = []
    created_armatures = []
    created_actions = []
    previous_registry = root.get("asset_assistant_components")

    try:
        component_root = bpy.data.objects.new(name, None)
        created_objects.append(component_root)
        collection.objects.link(component_root)
        component_root.parent = root
        component_root.empty_display_type = "PLAIN_AXES"
        component_root["asset_assistant_component_id"] = component_id
        component_root["asset_assistant_component_record"] = json.dumps(document, sort_keys=True)

        armature_data = bpy.data.armatures.new(name + ".RigData")
        created_armatures.append(armature_data)
        rig = bpy.data.objects.new(name + ".Rig", armature_data)
        created_objects.append(rig)
        collection.objects.link(rig)
        rig.parent = component_root
        rig["asset_assistant_component_id"] = component_id
        rig["asset_assistant_component_rig"] = True

        previous_active = bpy.context.view_layer.objects.active
        previous_selected = tuple(bpy.context.selected_objects)
        for obj in previous_selected:
            obj.select_set(False)
        rig.select_set(True)
        bpy.context.view_layer.objects.active = rig
        bpy.ops.object.mode_set(mode="EDIT")
        base = armature_data.edit_bones.new("gauntlet_base")
        base.head = (0.0, 0.0, 0.0)
        base.tail = (0.0, 0.0, 0.12)
        plate = armature_data.edit_bones.new("gauntlet_plate")
        plate.parent = base
        plate.use_connect = True
        plate.head = base.tail
        plate.tail = (0.0, 0.0, 0.24)
        bpy.ops.object.mode_set(mode="OBJECT")

        base_verts, base_faces = _cube_geometry((0.0, 0.0, 6.0), (8.0, 5.0, 10.0))
        plate_verts, plate_faces = _cube_geometry((0.0, 0.0, 16.0), (9.0, 5.5, 10.0))
        offset = len(base_verts)
        verts_cm = base_verts + plate_verts
        faces = base_faces + [tuple(index + offset for index in face) for face in plate_faces]
        verts = [(x * coordinate_scale, y * coordinate_scale, z * coordinate_scale) for x, y, z in verts_cm]
        mesh_data = bpy.data.meshes.new(name + ".Mesh")
        created_meshes.append(mesh_data)
        mesh_data.from_pydata(verts, (), faces)
        mesh_data.update()
        mesh_obj = bpy.data.objects.new(name + ".Mesh", mesh_data)
        created_objects.append(mesh_obj)
        collection.objects.link(mesh_obj)
        mesh_obj.parent = component_root
        mesh_obj["asset_assistant_component_id"] = component_id
        mesh_obj["component_part_name"] = "Gauntlet"

        group_base = mesh_obj.vertex_groups.new(name="gauntlet_base")
        group_base.add(list(range(0, 8)), 1.0, "REPLACE")
        group_plate = mesh_obj.vertex_groups.new(name="gauntlet_plate")
        group_plate.add(list(range(8, 16)), 1.0, "REPLACE")
        modifier = mesh_obj.modifiers.new(name="Asset Assistant Component Rig", type="ARMATURE")
        modifier.object = rig

        action = bpy.data.actions.new(name + ".Flex")
        created_actions.append(action)
        action["asset_assistant_component_id"] = component_id
        action["asset_assistant_component_animation"] = True
        action["asset_assistant_component_animation_name"] = "Flex"
        rig.animation_data_create().action = action
        pose_bone = rig.pose.bones.get("gauntlet_plate")
        pose_bone.rotation_mode = "XYZ"
        pose_bone.rotation_euler[0] = 0.0
        pose_bone.keyframe_insert(data_path="rotation_euler", frame=1)
        pose_bone.rotation_euler[0] = 0.45
        pose_bone.keyframe_insert(data_path="rotation_euler", frame=12)
        pose_bone.rotation_euler[0] = 0.0
        pose_bone.keyframe_insert(data_path="rotation_euler", frame=24)

        docs = _documents(root)
        docs.append(document)
        _set_documents(root, docs)
        inspect_component(root, component_id)

        for obj in bpy.context.selected_objects:
            obj.select_set(False)
        component_root.select_set(True)
        bpy.context.view_layer.objects.active = component_root
        return component_root, record
    except Exception:
        if bpy.context.mode != "OBJECT":
            bpy.ops.object.mode_set(mode="OBJECT")
        if previous_registry is None:
            if "asset_assistant_components" in root:
                del root["asset_assistant_components"]
        else:
            root["asset_assistant_components"] = previous_registry
        for action in created_actions:
            if action.name in bpy.data.actions:
                bpy.data.actions.remove(action)
        for obj in reversed(created_objects):
            if obj.name in bpy.data.objects:
                bpy.data.objects.remove(obj, do_unlink=True)
        for data in created_meshes:
            if data.users == 0:
                bpy.data.meshes.remove(data)
        for data in created_armatures:
            if data.users == 0:
                bpy.data.armatures.remove(data)
        raise


class ASSET_ASSISTANT_OT_generate_self_rigged_accessory(bpy.types.Operator):
    bl_idname = "asset_assistant.generate_self_rigged_accessory"
    bl_label = "Generate Self-Rigged Accessory"
    bl_description = "Create a generic mechanical accessory with its own independent rig and Flex animation"
    bl_options = {"REGISTER", "UNDO"}

    component_name: bpy.props.StringProperty(name="Name", default="Mechanical Gauntlet")

    @classmethod
    def poll(cls, context):
        return context.scene is not None and context.mode == "OBJECT" and _target(context) is not None

    def execute(self, context):
        try:
            _component_root, record = create_self_rigged_gauntlet(
                _target(context), name=self.component_name.strip() or "Mechanical Gauntlet"
            )
        except (TypeError, ValueError, RuntimeError, AttributeError) as error:
            self.report({"ERROR"}, str(error))
            return {"CANCELLED"}
        context.scene.humanoid_settings.validation_results.clear()
        self.report({"INFO"}, "Generated self-rigged accessory: " + record.component_id)
        return {"FINISHED"}


_CLASSES = (ASSET_ASSISTANT_OT_generate_self_rigged_accessory,)


def register():
    for cls in _CLASSES:
        bpy.utils.register_class(cls)


def unregister():
    for cls in reversed(_CLASSES):
        bpy.utils.unregister_class(cls)


__all__ = ["create_self_rigged_gauntlet", "ASSET_ASSISTANT_OT_generate_self_rigged_accessory", "register", "unregister"]
