# SPDX-License-Identifier: GPL-3.0-or-later
"""Blender persistence and root attachment for first-class asset components."""

import json

from .adapter import _populate_mesh
from .core import (
    AttachmentMode,
    ComponentRecord,
    ObjectMesh,
    component_document,
    component_from_document,
    validate_component,
)

_COMPONENTS_KEY = "asset_assistant_components"
_COMPONENT_ID_KEY = "asset_assistant_component_id"
_COMPONENT_RECORD_KEY = "asset_assistant_component_record"


def _require_asset_root(root):
    if root is None or root.get("generator") != "object_generator":
        raise ValueError("components require an Asset Assistant generated asset root")
    if not root.get("asset_assistant_asset_id"):
        raise ValueError("generated asset is missing its stable asset id")


def _documents(root):
    raw = root.get(_COMPONENTS_KEY, "[]")
    if not isinstance(raw, str):
        raise ValueError("component registry is not valid persisted JSON")
    try:
        documents = json.loads(raw)
    except (TypeError, ValueError):
        raise ValueError("component registry is not valid persisted JSON") from None
    if not isinstance(documents, list):
        raise ValueError("component registry must contain a JSON array")
    return documents


def component_records(root):
    """Load and validate all component records persisted on an asset root."""
    _require_asset_root(root)
    records = tuple(component_from_document(document) for document in _documents(root))
    ids = [record.component_id for record in records]
    if len(ids) != len(set(ids)):
        raise ValueError("component registry contains duplicate component ids")
    return records


def _component_root(root, component_id):
    matches = [child for child in root.children if child.get(_COMPONENT_ID_KEY) == component_id]
    if len(matches) != 1:
        raise ValueError("persisted component root is missing or ambiguous: " + component_id)
    return matches[0]


def inspect_component(root, component_id):
    """Return the validated record only when Blender hierarchy and metadata still agree."""
    record = next((item for item in component_records(root) if item.component_id == component_id), None)
    if record is None:
        raise ValueError("component id is not registered on this asset: " + component_id)
    component_root = _component_root(root, component_id)
    raw = component_root.get(_COMPONENT_RECORD_KEY)
    if not isinstance(raw, str):
        raise ValueError("component root is missing persisted component metadata")
    try:
        object_record = component_from_document(json.loads(raw))
    except (TypeError, ValueError):
        raise ValueError("component root metadata is invalid") from None
    if object_record != record:
        raise ValueError("component root metadata no longer matches the asset registry")
    if component_root.parent != root:
        raise ValueError("component is no longer attached to its owning asset root")
    mesh_children = [child for child in component_root.children if child.type == "MESH"]
    if record.owns_geometry and not mesh_children:
        raise ValueError("owned component geometry is missing")
    return record


def attach_rigid_component(root, mesh, record, *, name="Accessory"):
    """Create and persist one rigid component attached to the generated asset root.

    This first executable slice intentionally supports only ``asset_root``
    attachment. Bone attachment, skinned components, replacement, and removal are
    separate milestones because each adds a new preservation boundary.
    """
    import bpy

    _require_asset_root(root)
    if not isinstance(mesh, ObjectMesh):
        raise TypeError("mesh must be ObjectMesh")
    validate_component(record)
    if record.attachment_mode != AttachmentMode.RIGID:
        raise ValueError("this Blender path only supports rigid components")
    if record.attachment_target != "asset_root":
        raise ValueError("this Blender path only supports attachment_target 'asset_root'")
    if record.owns_rig:
        raise ValueError("rigid root-attached components must not own rig data")
    if not record.owns_geometry:
        raise ValueError("generated rigid components must own their geometry")
    if any(item.component_id == record.component_id for item in component_records(root)):
        raise ValueError("component id is already attached to this asset")
    if not isinstance(name, str) or not name.strip():
        raise ValueError("component name must be a nonempty string")

    coordinate_scale = root.get("coordinate_scale")
    if not isinstance(coordinate_scale, (int, float)) or coordinate_scale <= 0:
        raise ValueError("asset root has an invalid coordinate scale")
    collection = root.users_collection[0]
    created_objects = []
    created_meshes = []
    component_root = None
    previous_registry = root.get(_COMPONENTS_KEY)
    document = component_document(record)
    try:
        component_root = bpy.data.objects.new(name, None)
        created_objects.append(component_root)
        collection.objects.link(component_root)
        component_root.parent = root
        component_root.empty_display_type = "PLAIN_AXES"
        component_root[_COMPONENT_ID_KEY] = record.component_id
        component_root[_COMPONENT_RECORD_KEY] = json.dumps(document, sort_keys=True)

        for part in mesh.parts:
            data = bpy.data.meshes.new(name + "." + part.name)
            created_meshes.append(data)
            _populate_mesh(data, part, coordinate_scale)
            obj = bpy.data.objects.new(name + "." + part.name, data)
            created_objects.append(obj)
            collection.objects.link(obj)
            obj.parent = component_root
            obj["component_part_name"] = part.name
            obj[_COMPONENT_ID_KEY] = record.component_id

        documents = _documents(root)
        documents.append(document)
        root[_COMPONENTS_KEY] = json.dumps(documents, sort_keys=True)
        inspect_component(root, record.component_id)
        return component_root
    except Exception:
        if previous_registry is None:
            if _COMPONENTS_KEY in root:
                del root[_COMPONENTS_KEY]
        else:
            root[_COMPONENTS_KEY] = previous_registry
        for obj in reversed(created_objects):
            bpy.data.objects.remove(obj, do_unlink=True)
        for data in created_meshes:
            if data.users == 0:
                bpy.data.meshes.remove(data)
        raise


__all__ = ["attach_rigid_component", "component_records", "inspect_component"]
