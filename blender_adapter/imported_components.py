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


def _belongs_to_asset(obj, root):
    current = obj
    while current is not None:
        if current == root:
            return True
        current = current.parent
    return False


def adopt_rigid_component(root, mesh_object, record, *, name=None):
    """Transfer one existing Blender mesh into an owned rigid component.

    Adoption is explicit ownership transfer: the mesh is not copied. Once adopted,
    the normal component remove/replace lifecycle may delete or replace it.
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
    if mesh_object is None or mesh_object.type != "MESH":
        raise ValueError("adoption requires one Blender mesh object")
    if mesh_object == root or _belongs_to_asset(mesh_object, root):
        raise ValueError("mesh is already part of the owning Asset Assistant asset")
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
        mesh_object["component_part_name"] = mesh_object.name

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
        if _COMPONENT_ID_KEY in mesh_object:
            del mesh_object[_COMPONENT_ID_KEY]
        if "component_part_name" in mesh_object:
            del mesh_object["component_part_name"]
        mesh_object.parent = previous_parent
        mesh_object.parent_type = previous_parent_type
        mesh_object.parent_bone = previous_parent_bone
        mesh_object.matrix_world = previous_world
        if component_root is not None and component_root.name in bpy.data.objects:
            bpy.data.objects.remove(component_root, do_unlink=True)
        raise


__all__ = ["adopt_rigid_component"]
