# SPDX-License-Identifier: GPL-3.0-or-later
"""Translate core mesh data into Blender data; no provider-specific generation rules here."""

from math import isfinite
from uuid import uuid4

from .core import ObjectMesh, Skeleton


_ASSET_ID = "asset_assistant_asset_id"
_ASSET_SOURCE = "asset_assistant_source"


def _populate_mesh(data, part, coordinate_scale):
    vertices = [tuple(value * coordinate_scale for value in vertex)
                for vertex in part.vertices]
    data.from_pydata(vertices, [], part.faces)
    data.update()
    if part.uvs:
        uv_layer = data.uv_layers.new(name="UVMap")
        for polygon, face_uvs in zip(data.polygons, part.uvs):
            if polygon.loop_total != len(face_uvs):
                raise ValueError("core UV corner count does not match Blender polygon")
            for offset, uv in enumerate(face_uvs):
                uv_layer.data[polygon.loop_start + offset].uv = uv


def create_asset(mesh: ObjectMesh, *, name="Asset", scene=None, skeleton=None,
                 skin_weights=None, materials=()):
    """Create an editable asset with optional rigging and portable materials."""
    if not isinstance(mesh, ObjectMesh):
        raise TypeError("mesh must be ObjectMesh")
    if not isinstance(name, str) or not name.strip():
        raise ValueError("name must be a nonempty string")
    if skin_weights is not None and skeleton is None:
        raise ValueError("skin_weights require a skeleton")
    materials = tuple(materials)
    import bpy

    scene = bpy.context.scene if scene is None else scene
    if skeleton is not None:
        if not isinstance(skeleton, Skeleton):
            raise TypeError("skeleton must be Skeleton")
        if skin_weights is None:
            bindings = {bone.part_name for bone in skeleton.bones if bone.part_name is not None}
            if bindings != {part.name for part in mesh.parts}:
                raise ValueError("skeleton must bind every mesh part exactly once")
        else:
            weight_parts = {weights.part_name for weights in skin_weights}
            if weight_parts != {part.name for part in mesh.parts}:
                raise ValueError("skin_weights must cover every mesh part exactly once")
        if scene != bpy.context.scene or bpy.context.mode != "OBJECT":
            raise ValueError("rig creation requires the active scene in Object Mode")
    meters_per_unit = scene.unit_settings.scale_length
    if not isfinite(meters_per_unit) or meters_per_unit <= 0:
        raise ValueError("scene unit scale must be positive and finite")
    coordinate_scale = 0.01 / meters_per_unit
    collection = bpy.data.collections.new(name)
    created_objects = []
    created_meshes = []
    created_materials = []
    try:
        root = bpy.data.objects.new(name, None)
        created_objects.append(root)
        collection.objects.link(root)
        root.empty_display_type = "PLAIN_AXES"
        root.empty_display_size = 10 * coordinate_scale
        root["generator"] = "object_generator"
        root["stage"] = "blockout"
        root["coordinate_scale"] = coordinate_scale
        root[_ASSET_ID] = uuid4().hex
        root[_ASSET_SOURCE] = "GENERATED"
        for part in mesh.parts:
            data = bpy.data.meshes.new(name + "." + part.name)
            created_meshes.append(data)
            _populate_mesh(data, part, coordinate_scale)
            obj = bpy.data.objects.new(name + "." + part.name, data)
            created_objects.append(obj)
            obj.parent = root
            obj["part_name"] = part.name
            obj["body_part"] = part.name
            collection.objects.link(obj)
        scene.collection.children.link(collection)
        if materials:
            from .materials import apply_generated_materials
            created_materials.extend(apply_generated_materials(root, materials))
        if skeleton is not None:
            if skin_weights is None:
                from .rigging import attach_rig
                attach_rig(root, skeleton, coordinate_scale)
            else:
                from .rigging import attach_deforming_rig
                attach_deforming_rig(root, skeleton, skin_weights, coordinate_scale)
        return root
    except Exception:
        for obj in reversed(created_objects):
            bpy.data.objects.remove(obj, do_unlink=True)
        for data in created_meshes:
            bpy.data.meshes.remove(data)
        for material in created_materials:
            if material.users == 0:
                bpy.data.materials.remove(material)
        bpy.data.collections.remove(collection)
        raise


create_character = create_asset
