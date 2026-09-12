# SPDX-License-Identifier: GPL-3.0-or-later
"""Blender persistence, attachment, and lifecycle for first-class asset components."""

import json

from .adapter import _populate_mesh
from .core import (
    AttachmentMode,
    ComponentRecord,
    ObjectMesh,
    RigBinding,
    component_document,
    component_from_document,
    validate_component,
)

_COMPONENTS_KEY = "asset_assistant_components"
_COMPONENT_ID_KEY = "asset_assistant_component_id"
_COMPONENT_RECORD_KEY = "asset_assistant_component_record"
_BONE_PREFIX = "bone:"


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


def _set_documents(root, documents):
    root[_COMPONENTS_KEY] = json.dumps(list(documents), sort_keys=True)


def component_records(root):
    """Load and validate all component records persisted on an asset root."""
    _require_asset_root(root)
    records = tuple(component_from_document(document) for document in _documents(root))
    ids = [record.component_id for record in records]
    if len(ids) != len(set(ids)):
        raise ValueError("component registry contains duplicate component ids")
    return records


def _descendants(root):
    pending = list(root.children)
    while pending:
        child = pending.pop()
        yield child
        pending.extend(child.children)


def _component_root(root, component_id):
    matches = [obj for obj in _descendants(root) if obj.get(_COMPONENT_ID_KEY) == component_id]
    matches = [obj for obj in matches if obj.get(_COMPONENT_RECORD_KEY) is not None]
    if len(matches) != 1:
        raise ValueError("persisted component root is missing or ambiguous: " + component_id)
    return matches[0]


def _armature(root):
    armatures = [child for child in root.children if child.type == "ARMATURE"]
    if len(armatures) != 1:
        raise ValueError("bone attachment requires exactly one generated armature")
    return armatures[0]


def _bone_name(target):
    if not target.startswith(_BONE_PREFIX):
        return None
    name = target[len(_BONE_PREFIX):]
    if not name:
        raise ValueError("bone attachment target must include a bone name")
    return name


def _validate_attachment(root, component_root, record):
    if record.attachment_target == "asset_root":
        if component_root.parent != root:
            raise ValueError("component is no longer attached to its owning asset root")
        return

    bone_name = _bone_name(record.attachment_target)
    if bone_name is None:
        raise ValueError("unsupported rigid attachment target: " + record.attachment_target)
    armature = _armature(root)
    if armature.data.bones.get(bone_name) is None:
        raise ValueError("attachment bone does not exist: " + bone_name)
    if component_root.parent != armature:
        raise ValueError("component is no longer attached to the generated armature")
    if component_root.parent_type != "BONE" or component_root.parent_bone != bone_name:
        raise ValueError("component bone attachment no longer matches persisted metadata")


def _validate_owned_rig(component_root, record):
    descendants = tuple(_descendants(component_root))
    owned_rigs = [
        obj for obj in descendants
        if obj.type == "ARMATURE"
        and obj.get(_COMPONENT_ID_KEY) == record.component_id
        and bool(obj.get("asset_assistant_component_rig"))
    ]
    if record.owns_rig:
        if record.rig_binding != RigBinding.OWNED:
            raise ValueError("component declares rig ownership without owned rig binding")
        if len(owned_rigs) != 1:
            raise ValueError("owned-rig component must contain exactly one managed component armature")
        rig = owned_rigs[0]
        mesh_children = [obj for obj in descendants if obj.type == "MESH"]
        for mesh in mesh_children:
            armature_modifiers = [modifier for modifier in mesh.modifiers if modifier.type == "ARMATURE"]
            if not any(modifier.object == rig for modifier in armature_modifiers):
                raise ValueError("owned-rig component mesh is no longer bound to its component armature")
    elif owned_rigs:
        raise ValueError("component contains a managed component armature without declaring rig ownership")


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
    _validate_attachment(root, component_root, record)
    mesh_children = [child for child in component_root.children if child.type == "MESH"]
    if record.owns_geometry and not mesh_children:
        raise ValueError("owned component geometry is missing")
    _validate_owned_rig(component_root, record)
    return record


def _attach_component_root(root, component_root, record):
    if record.attachment_target == "asset_root":
        component_root.parent = root
        return

    bone_name = _bone_name(record.attachment_target)
    if bone_name is None:
        raise ValueError("unsupported rigid attachment target: " + record.attachment_target)
    armature = _armature(root)
    if armature.data.bones.get(bone_name) is None:
        raise ValueError("attachment bone does not exist: " + bone_name)
    component_root.parent = armature
    component_root.parent_type = "BONE"
    component_root.parent_bone = bone_name


def _delete_component_tree(component_root):
    import bpy

    component_id = str(component_root.get(_COMPONENT_ID_KEY) or "").strip()
    objects = list(_descendants(component_root))
    objects.append(component_root)
    meshes = [obj.data for obj in objects if obj.type == "MESH" and obj.data is not None]
    armatures = [
        obj.data for obj in objects
        if obj.type == "ARMATURE" and obj.data is not None
        and obj.get(_COMPONENT_ID_KEY) == component_id
        and bool(obj.get("asset_assistant_component_rig"))
    ]
    actions = [
        action for action in bpy.data.actions
        if component_id
        and action.get(_COMPONENT_ID_KEY) == component_id
        and bool(action.get("asset_assistant_component_animation"))
    ]
    for obj in reversed(objects):
        bpy.data.objects.remove(obj, do_unlink=True)
    for data in meshes:
        if data.users == 0:
            bpy.data.meshes.remove(data)
    for data in armatures:
        if data.users == 0:
            bpy.data.armatures.remove(data)
    for action in actions:
        if action.users == 0:
            bpy.data.actions.remove(action)


def attach_rigid_component(root, mesh, record, *, name="Accessory"):
    """Create and persist one rigid component on the asset root or a named bone."""
    import bpy

    _require_asset_root(root)
    if not isinstance(mesh, ObjectMesh):
        raise TypeError("mesh must be ObjectMesh")
    validate_component(record)
    if record.attachment_mode != AttachmentMode.RIGID:
        raise ValueError("this Blender path only supports rigid components")
    if record.owns_rig:
        raise ValueError("rigid components must not own rig data")
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
    previous_registry = root.get(_COMPONENTS_KEY)
    document = component_document(record)
    try:
        component_root = bpy.data.objects.new(name, None)
        created_objects.append(component_root)
        collection.objects.link(component_root)
        _attach_component_root(root, component_root, record)
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
        _set_documents(root, documents)
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


def remove_component(root, component_id):
    """Remove one validated owned component and its registry entry."""
    record = inspect_component(root, component_id)
    component_root = _component_root(root, component_id)
    documents = [
        document for document in _documents(root)
        if document.get("component_id") != component_id
    ]
    _delete_component_tree(component_root)
    _set_documents(root, documents)
    return record


def replace_rigid_component(root, mesh, record, *, name="Accessory"):
    """Replace a rigid component while preserving its stable component id.

    The old component remains intact until the replacement has been created and
    successfully re-inspected. If replacement creation fails, registry and object
    metadata are restored to the previous component.
    """
    _require_asset_root(root)
    if not isinstance(record, ComponentRecord):
        raise TypeError("component must be a ComponentRecord")
    old_record = inspect_component(root, record.component_id)
    old_root = _component_root(root, record.component_id)
    previous_registry = root.get(_COMPONENTS_KEY)
    old_id = old_root.get(_COMPONENT_ID_KEY)
    old_record_raw = old_root.get(_COMPONENT_RECORD_KEY)
    remaining_documents = [
        document for document in _documents(root)
        if document.get("component_id") != record.component_id
    ]

    _set_documents(root, remaining_documents)
    del old_root[_COMPONENT_ID_KEY]
    del old_root[_COMPONENT_RECORD_KEY]
    try:
        replacement_root = attach_rigid_component(root, mesh, record, name=name)
    except Exception:
        root[_COMPONENTS_KEY] = previous_registry
        old_root[_COMPONENT_ID_KEY] = old_id
        old_root[_COMPONENT_RECORD_KEY] = old_record_raw
        raise

    _delete_component_tree(old_root)
    inspect_component(root, record.component_id)
    return old_record, replacement_root


__all__ = [
    "attach_rigid_component",
    "component_records",
    "inspect_component",
    "remove_component",
    "replace_rigid_component",
]
