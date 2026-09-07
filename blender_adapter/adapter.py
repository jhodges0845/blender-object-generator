# SPDX-License-Identifier: GPL-3.0-or-later
"""Translate core mesh data into Blender data; no body generation rules here."""

from math import isfinite

from .core import ObjectMesh, Skeleton


def _populate_mesh(data, part, coordinate_scale):
    vertices = [tuple(value * coordinate_scale for value in vertex)
                for vertex in part.vertices]
    data.from_pydata(vertices, [], part.faces)
    data.update()


def create_character(mesh: ObjectMesh, *, name="Humanoid", scene=None, skeleton=None):
    """Create a collection, Empty root, editable parts, and an optional rigid rig.

    Returns the root object. Source coordinates are converted from centimeters
    using the scene's meters-per-unit scale. Existing objects, unit settings,
    cursor, and selection are preserved. On failure only resources created by
    this call are removed. A skeleton requires the active scene in Object Mode.
    Requires execution inside Blender.
    """
    if not isinstance(mesh, ObjectMesh):
        raise TypeError("mesh must be ObjectMesh")
    if not isinstance(name, str) or not name.strip():
        raise ValueError("name must be a nonempty string")
    import bpy

    scene = bpy.context.scene if scene is None else scene
    if skeleton is not None:
        if not isinstance(skeleton, Skeleton):
            raise TypeError("skeleton must be Skeleton")
        bindings = {bone.part_name for bone in skeleton.bones if bone.part_name is not None}
        if bindings != {part.name for part in mesh.parts}:
            raise ValueError("skeleton must bind every mesh part exactly once")
        if scene != bpy.context.scene or bpy.context.mode != "OBJECT":
            raise ValueError("rig creation requires the active scene in Object Mode")
    meters_per_unit = scene.unit_settings.scale_length
    if not isfinite(meters_per_unit) or meters_per_unit <= 0:
        raise ValueError("scene unit scale must be positive and finite")
    coordinate_scale = 0.01 / meters_per_unit
    collection = bpy.data.collections.new(name)
    created_objects = []
    created_meshes = []
    try:
        root = bpy.data.objects.new(name, None)
        created_objects.append(root)
        collection.objects.link(root)
        root.empty_display_type = "PLAIN_AXES"
        root.empty_display_size = 10 * coordinate_scale
        root["generator"] = "object_generator"
        root["stage"] = "blockout"
        root["coordinate_scale"] = coordinate_scale
        for part in mesh.parts:
            data = bpy.data.meshes.new(name + "." + part.name)
            created_meshes.append(data)
            _populate_mesh(data, part, coordinate_scale)
            obj = bpy.data.objects.new(name + "." + part.name, data)
            created_objects.append(obj)
            obj.parent = root
            obj["body_part"] = part.name
            obj["part_name"] = part.name
            collection.objects.link(obj)
        scene.collection.children.link(collection)
        if skeleton is not None:
            from .rigging import attach_rig
            attach_rig(root, skeleton, coordinate_scale)
        return root
    except Exception:
        for obj in reversed(created_objects):
            bpy.data.objects.remove(obj, do_unlink=True)
        for data in created_meshes:
            bpy.data.meshes.remove(data)
        bpy.data.collections.remove(collection)
        raise
