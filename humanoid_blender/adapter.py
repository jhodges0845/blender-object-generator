"""Translate core mesh data into Blender data; no body generation rules here."""

from math import isfinite

from .core import HumanoidMesh


def _populate_mesh(data, part, coordinate_scale):
    vertices = [tuple(value * coordinate_scale for value in vertex)
                for vertex in part.vertices]
    data.from_pydata(vertices, [], part.faces)
    data.update()


def create_character(mesh: HumanoidMesh, *, name="Humanoid", scene=None):
    """Create a collection, an Empty root, and one editable object per part.

    Returns the root object. Source coordinates are converted from centimeters
    using the scene's meters-per-unit scale. Existing objects, unit settings,
    cursor, and selection are preserved. On failure only resources created by
    this call are removed. Requires execution inside Blender.
    """
    if not isinstance(mesh, HumanoidMesh):
        raise TypeError("mesh must be HumanoidMesh")
    if not isinstance(name, str) or not name.strip():
        raise ValueError("name must be a nonempty string")
    import bpy

    scene = bpy.context.scene if scene is None else scene
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
        root["generator"] = "humanoid_blockout"
        root["stage"] = "blockout"
        for part in mesh.parts:
            data = bpy.data.meshes.new(name + "." + part.name)
            created_meshes.append(data)
            _populate_mesh(data, part, coordinate_scale)
            obj = bpy.data.objects.new(name + "." + part.name, data)
            created_objects.append(obj)
            obj.parent = root
            obj["body_part"] = part.name
            collection.objects.link(obj)
        scene.collection.children.link(collection)
        return root
    except Exception:
        for obj in reversed(created_objects):
            bpy.data.objects.remove(obj, do_unlink=True)
        for data in created_meshes:
            bpy.data.meshes.remove(data)
        bpy.data.collections.remove(collection)
        raise
