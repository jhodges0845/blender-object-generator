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


def attach_rig(root, skeleton, scale):
    """Attach to newly created meshes; caller owns mesh cleanup on failure."""
    import bpy
    previous_active = bpy.context.view_layer.objects.active
    previous_selection = tuple(bpy.context.selected_objects)
    data = bpy.data.armatures.new(root.name + ".Rig")
    armature = None
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
        parts = {obj["body_part"]: obj for obj in root.children if obj.type == "MESH"}
        for bone in skeleton.bones:
            if bone.part_name is None:
                continue
            obj = parts[bone.part_name]
            group = obj.vertex_groups.new(name=bone.name)
            group.add(list(range(len(obj.data.vertices))), 1.0, "REPLACE")
            modifier = obj.modifiers.new(name="Rigid Blockout Rig", type="ARMATURE")
            modifier.object = armature
            modifier.use_vertex_groups = True
            modifier.use_bone_envelopes = False
        root["stage"] = "rigid_rig"
        return armature
    except Exception:
        if bpy.context.mode != "OBJECT":
            bpy.ops.object.mode_set(mode="OBJECT")
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
