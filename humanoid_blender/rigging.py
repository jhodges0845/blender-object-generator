# SPDX-License-Identifier: GPL-3.0-or-later
"""Internal rigid-rig translation for newly created blockout objects."""


def _populate_bones(data, skeleton, scale):
    for source in skeleton.bones:
        bone = data.edit_bones.new(source.name)
        bone.head = tuple(v * scale for v in source.head)
        bone.tail = tuple(v * scale for v in source.tail)
        bone.use_deform = source.part_name is not None
        if source.parent:
            bone.parent = data.edit_bones[source.parent]
            bone.use_connect = (bone.head - bone.parent.tail).length < 1e-8


def _assign_weights(group, vertices):
    group.add(list(range(len(vertices))), 1.0, "REPLACE")


def attach_rig(root, skeleton, scale):
    """Attach a rigid rig transactionally, preserving existing meshes on failure."""
    import bpy
    from math import isfinite
    if bpy.context.mode != "OBJECT":
        raise ValueError("Rigging requires Object Mode.")
    if not isfinite(scale) or scale <= 0:
        raise ValueError("Rig scale must be positive and finite.")
    if any(obj.type == "ARMATURE" for obj in root.children):
        raise ValueError("Character already has a rig.")
    mesh_objects = [obj for obj in root.children if obj.type == "MESH"]
    parts = {obj.get("body_part"): obj for obj in mesh_objects}
    bindings = {bone.part_name for bone in skeleton.bones if bone.part_name is not None}
    if len(parts) != len(mesh_objects) or set(parts) != bindings:
        raise ValueError("Character parts no longer match the generated skeleton.")
    for bone in skeleton.bones:
        if bone.part_name is not None and parts[bone.part_name].vertex_groups.get(bone.name):
            raise ValueError("Existing bone weights found; automatic rigging will not overwrite them.")
    previous_active = bpy.context.view_layer.objects.active
    previous_selection = tuple(bpy.context.selected_objects)
    data = bpy.data.armatures.new(root.name + ".Rig")
    armature = None
    created_groups, created_modifiers = [], []
    try:
        armature = bpy.data.objects.new(root.name + ".Rig", data)
        root.users_collection[0].objects.link(armature)
        armature.parent = root
        armature.show_in_front = True
        for obj in previous_selection:
            obj.select_set(False)
        armature.select_set(True)
        bpy.context.view_layer.objects.active = armature
        bpy.ops.object.mode_set(mode="EDIT")
        _populate_bones(data, skeleton, scale)
        bpy.ops.object.mode_set(mode="OBJECT")
        for bone in skeleton.bones:
            if bone.part_name is None:
                continue
            obj = parts[bone.part_name]
            group = obj.vertex_groups.new(name=bone.name)
            created_groups.append((obj, group))
            _assign_weights(group, obj.data.vertices)
            modifier = obj.modifiers.new(name="Rigid Blockout Rig", type="ARMATURE")
            created_modifiers.append((obj, modifier))
            modifier.object = armature
            modifier.use_vertex_groups = True
            modifier.use_bone_envelopes = False
        root["stage"] = "rigid_rig"
        return armature
    except Exception:
        if bpy.context.mode != "OBJECT":
            bpy.ops.object.mode_set(mode="OBJECT")
        for obj, modifier in reversed(created_modifiers):
            obj.modifiers.remove(modifier)
        for obj, group in reversed(created_groups):
            obj.vertex_groups.remove(group)
        if armature is not None:
            bpy.data.objects.remove(armature, do_unlink=True)
        bpy.data.armatures.remove(data)
        raise
    finally:
        for obj in bpy.context.selected_objects:
            obj.select_set(False)
        for obj in previous_selection:
            obj.select_set(True)
        bpy.context.view_layer.objects.active = previous_active
