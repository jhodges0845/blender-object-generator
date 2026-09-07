# SPDX-License-Identifier: GPL-3.0-or-later
"""Translate independent skeleton and skinning data into Blender rigs."""


def _populate_bones(data, skeleton, scale, *, deform_unbound=False):
    for source in skeleton.bones:
        bone = data.edit_bones.new(source.name)
        bone.head = tuple(v * scale for v in source.head)
        bone.tail = tuple(v * scale for v in source.tail)
        bone.use_deform = deform_unbound or source.part_name is not None
        if source.parent:
            bone.parent = data.edit_bones[source.parent]
            bone.use_connect = (bone.head - bone.parent.tail).length < 1e-8


def _assign_weights(group, vertices):
    group.add(list(range(len(vertices))), 1.0, "REPLACE")


def _rig_context(root, scale):
    import bpy
    from math import isfinite
    if bpy.context.mode != "OBJECT":
        raise ValueError("Rigging requires Object Mode.")
    if not isfinite(scale) or scale <= 0:
        raise ValueError("Rig scale must be positive and finite.")
    if any(obj.type == "ARMATURE" for obj in root.children):
        raise ValueError("Character already has a rig.")


def attach_rig(root, skeleton, scale):
    """Attach the legacy rigid rig transactionally."""
    import bpy
    _rig_context(root, scale)
    mesh_objects = [obj for obj in root.children if obj.type == "MESH"]
    parts = {obj.get("part_name", obj.get("body_part")): obj for obj in mesh_objects}
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


def attach_deforming_rig(root, skeleton, skin_weights, scale):
    """Attach one weighted armature to mesh objects transactionally."""
    import bpy
    _rig_context(root, scale)
    mesh_objects = [obj for obj in root.children if obj.type == "MESH"]
    parts = {obj.get("part_name", obj.get("body_part")): obj for obj in mesh_objects}
    weights_by_part = {weights.part_name: weights for weights in skin_weights}
    if len(parts) != len(mesh_objects) or set(parts) != set(weights_by_part):
        raise ValueError("Skin weights must match every mesh part exactly once.")
    bone_names = {bone.name for bone in skeleton.bones}
    for weights in weights_by_part.values():
        if any(influence.bone_name not in bone_names for vertex in weights.vertices for influence in vertex):
            raise ValueError("Skin weights reference a bone not present in the skeleton.")
        if len(weights.vertices) != len(parts[weights.part_name].data.vertices):
            raise ValueError("Skin weights must cover every mesh vertex exactly once.")
    if any(obj.vertex_groups for obj in mesh_objects):
        raise ValueError("Existing vertex groups found; deforming rig will not overwrite them.")

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
        _populate_bones(data, skeleton, scale, deform_unbound=True)
        bpy.ops.object.mode_set(mode="OBJECT")

        for part_name, weights in weights_by_part.items():
            obj = parts[part_name]
            groups = {}
            for bone_name in sorted({influence.bone_name for vertex in weights.vertices for influence in vertex}):
                group = obj.vertex_groups.new(name=bone_name)
                groups[bone_name] = group
                created_groups.append((obj, group))
            for vertex_index, influences in enumerate(weights.vertices):
                for influence in influences:
                    groups[influence.bone_name].add([vertex_index], influence.weight, "REPLACE")
            modifier = obj.modifiers.new(name="Deforming Human Rig", type="ARMATURE")
            created_modifiers.append((obj, modifier))
            modifier.object = armature
            modifier.use_vertex_groups = True
            modifier.use_bone_envelopes = False
        root["stage"] = "deforming_rig"
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
