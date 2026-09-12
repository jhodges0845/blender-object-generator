# SPDX-License-Identifier: GPL-3.0-or-later
"""Adopt artist-authored Blender mesh objects into the component lifecycle."""

import json

from .components import (
    _COMPONENT_ID_KEY,
    _COMPONENT_RECORD_KEY,
    _COMPONENTS_KEY,
    _attach_component_root,
    _documents,
    _require_asset_root,
    _set_documents,
    component_records,
    inspect_component,
)
from .core import AttachmentMode, ComponentRecord, component_document, validate_component

_PART_NAME_KEY = "component_part_name"


def _asset_owner(obj):
    current = obj
    while current is not None:
        if current.get("generator") == "object_generator":
            return current
        current = current.parent
    return None


def adopt_rigid_component(root, mesh_object, record, *, name=None):
    """Transfer one existing Blender mesh into an owned rigid component.

    Adoption is an explicit ownership transfer: the mesh object and mesh datablock
    are not copied. Once adopted, normal component remove/replace operations may
    delete them. Materials remain artist-owned in this first adoption path so a
    shared material cannot be deleted merely because one component was removed.
    """
    import bpy

    _require_asset_root(root)
    validate_component(record)
    if record.attachment_mode != AttachmentMode.RIGID:
        raise ValueError("imported adoption currently supports rigid components only")
    if record.owns_rig:
        raise ValueError("rigid components must not own rig data")
    if not record.owns_geometry:
        raise ValueError("adopted rigid components must own their geometry")
    if record.owns_materials:
        raise ValueError("imported rigid adoption does not claim material ownership")
    if mesh_object is None or mesh_object.type != "MESH":
        raise ValueError("adoption requires one Blender mesh object")
    owner = _asset_owner(mesh_object)
    if owner is not None:
        raise ValueError("mesh is already part of an Asset Assistant asset")
    if mesh_object.children:
        raise ValueError("adoption currently requires a mesh with no child objects")
    if any(modifier.type == "ARMATURE" for modifier in mesh_object.modifiers):
        raise ValueError("mesh uses an armature modifier; use skinned component adoption instead")
    if mesh_object.get(_COMPONENT_ID_KEY):
        raise ValueError("mesh is already registered as an Asset Assistant component")
    if any(item.component_id == record.component_id for item in component_records(root)):
        raise ValueError("component id is already attached to this asset")

    component_name = name or mesh_object.name or "Imported Component"
    if not isinstance(component_name, str) or not component_name.strip():
        raise ValueError("component name must be a nonempty string")

    collection = root.users_collection[0]
    previous_registry = root.get(_COMPONENTS_KEY)
    previous_parent = mesh_object.parent
    previous_parent_type = mesh_object.parent_type
    previous_parent_bone = mesh_object.parent_bone
    previous_world = mesh_object.matrix_world.copy()
    had_component_id = _COMPONENT_ID_KEY in mesh_object
    previous_component_id = mesh_object.get(_COMPONENT_ID_KEY)
    had_part_name = _PART_NAME_KEY in mesh_object
    previous_part_name = mesh_object.get(_PART_NAME_KEY)
    document = component_document(record)
    component_root = None
    try:
        component_root = bpy.data.objects.new(component_name, None)
        collection.objects.link(component_root)
        _attach_component_root(root, component_root, record)
        component_root.empty_display_type = "PLAIN_AXES"
        component_root[_COMPONENT_ID_KEY] = record.component_id
        component_root[_COMPONENT_RECORD_KEY] = json.dumps(document, sort_keys=True)

        mesh_object.parent = component_root
        mesh_object.parent_type = "OBJECT"
        mesh_object.parent_bone = ""
        mesh_object.matrix_world = previous_world
        mesh_object[_COMPONENT_ID_KEY] = record.component_id
        mesh_object[_PART_NAME_KEY] = mesh_object.name

        documents = _documents(root)
        documents.append(document)
        _set_documents(root, documents)
        inspect_component(root, record.component_id)
        return component_root
    except Exception:
        if previous_registry is None:
            if _COMPONENTS_KEY in root:
                del root[_COMPONENTS_KEY]
        else:
            root[_COMPONENTS_KEY] = previous_registry

        if had_component_id:
            mesh_object[_COMPONENT_ID_KEY] = previous_component_id
        elif _COMPONENT_ID_KEY in mesh_object:
            del mesh_object[_COMPONENT_ID_KEY]
        if had_part_name:
            mesh_object[_PART_NAME_KEY] = previous_part_name
        elif _PART_NAME_KEY in mesh_object:
            del mesh_object[_PART_NAME_KEY]

        mesh_object.parent = previous_parent
        mesh_object.parent_type = previous_parent_type
        mesh_object.parent_bone = previous_parent_bone
        mesh_object.matrix_world = previous_world
        if component_root is not None and component_root.name in bpy.data.objects:
            bpy.data.objects.remove(component_root, do_unlink=True)
        raise


__all__ = ["adopt_rigid_component"]
