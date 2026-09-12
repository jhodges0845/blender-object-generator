# SPDX-License-Identifier: GPL-3.0-or-later
"""Blender execution and lifecycle for skinned components bound to an owning asset rig."""

import json

from .adapter import _populate_mesh
from .components import (
    _COMPONENT_ID_KEY,
    _COMPONENT_RECORD_KEY,
    _COMPONENTS_KEY,
    _armature,
    _component_root,
    _delete_component_tree,
    _documents,
    _require_asset_root,
    _set_documents,
    component_records,
)
from .core import (
    AttachmentMode,
    ComponentRecord,
    ObjectMesh,
    RigBinding,
    component_document,
    validate_component,
)

_SKIN_KEY = "asset_assistant_component_skin_weights"
_MODIFIER_NAME = "Asset Assistant Component Rig"


def _weights_document(skin_weights):
    return {
        item.part_name: [
            [[influence.bone_name, influence.weight] for influence in vertex]
            for vertex in item.vertices
        ]
        for item in skin_weights
    }


def _validate_weights(mesh, skin_weights, armature):
    skin_weights = tuple(skin_weights)
    parts = {part.name: part for part in mesh.parts}
    weights = {item.part_name: item for item in skin_weights}
    if len(weights) != len(skin_weights) or set(parts) != set(weights):
        raise ValueError("skinned component weights must match every mesh part exactly once")
    bone_names = {bone.name for bone in armature.data.bones}
    for part_name, item in weights.items():
        if len(item.vertices) != len(parts[part_name].vertices):
            raise ValueError("skinned component weights must cover every mesh vertex exactly once")
        for influences in item.vertices:
            for influence in influences:
                if influence.bone_name not in bone_names:
                    raise ValueError("skinned component weights reference a bone not present in the parent rig")
    return weights


def _actual_vertex_weights(obj, vertex_index):
    values = []
    vertex = obj.data.vertices[vertex_index]
    for assignment in vertex.groups:
        group = obj.vertex_groups[assignment.group]
        values.append([group.name, assignment.weight])
    return sorted(values, key=lambda item: item[0])


def _validate_skin_state(root, component_root, record):
    if record.attachment_mode != AttachmentMode.SKINNED or record.rig_binding != RigBinding.PARENT:
        return
    if component_root.parent != root:
        raise ValueError("skinned component is no longer attached to its owning asset root")
    armature = _armature(root)
    raw = component_root.get(_SKIN_KEY)
    if not isinstance(raw, str):
        raise ValueError("skinned component is missing persisted weight metadata")
    try:
        expected = json.loads(raw)
    except (TypeError, ValueError):
        raise ValueError("skinned component weight metadata is invalid") from None
    mesh_children = [child for child in component_root.children if child.type == "MESH"]
    by_part = {child.get("component_part_name"): child for child in mesh_children}
    if set(by_part) != set(expected):
        raise ValueError("skinned component mesh parts no longer match persisted weight metadata")
    for part_name, vertices in expected.items():
        obj = by_part[part_name]
        modifiers = [modifier for modifier in obj.modifiers if modifier.type == "ARMATURE"]
        if len(modifiers) != 1 or modifiers[0].object != armature:
            raise ValueError("skinned component armature modifier no longer targets the parent rig")
        if len(vertices) != len(obj.data.vertices):
            raise ValueError("skinned component vertex count no longer matches persisted weights")
        for index, expected_vertex in enumerate(vertices):
            expected_vertex = sorted([[name, float(weight)] for name, weight in expected_vertex], key=lambda item: item[0])
            actual_vertex = _actual_vertex_weights(obj, index)
            if len(actual_vertex) != len(expected_vertex):
                raise ValueError("skinned component vertex weights no longer match persisted weights")
            for actual, wanted in zip(actual_vertex, expected_vertex):
                if actual[0] != wanted[0] or abs(actual[1] - wanted[1]) > 1e-6:
                    raise ValueError("skinned component vertex weights no longer match persisted weights")


def inspect_skinned_component(root, component_id):
    """Validate persistence, ownership, parent-rig modifier, and exact generated weights."""
    record = next((item for item in component_records(root) if item.component_id == component_id), None)
    if record is None:
        raise ValueError("component id is not registered on this asset: " + component_id)
    component_root = _component_root(root, component_id)
    raw = component_root.get(_COMPONENT_RECORD_KEY)
    if not isinstance(raw, str):
        raise ValueError("component root is missing persisted component metadata")
    from .core import component_from_document
    try:
        object_record = component_from_document(json.loads(raw))
    except (TypeError, ValueError):
        raise ValueError("component root metadata is invalid") from None
    if object_record != record:
        raise ValueError("component root metadata no longer matches the asset registry")
    if record.attachment_mode != AttachmentMode.SKINNED:
        raise ValueError("component is not skinned")
    if record.rig_binding != RigBinding.PARENT:
        raise ValueError("this Blender path only inspects parent-rig skinned components")
    if record.owns_rig:
        raise ValueError("parent-rig skinned components must not own rig data")
    _validate_skin_state(root, component_root, record)
    return record


def attach_skinned_component(root, mesh, skin_weights, record, *, name="Skinned Component"):
    """Create a generated skinned component that deforms with the owning asset rig."""
    import bpy

    _require_asset_root(root)
    if not isinstance(mesh, ObjectMesh):
        raise TypeError("mesh must be ObjectMesh")
    validate_component(record)
    if record.attachment_mode != AttachmentMode.SKINNED:
        raise ValueError("this Blender path only supports skinned components")
    if record.rig_binding != RigBinding.PARENT:
        raise ValueError("this Blender path only supports parent rig binding")
    if record.owns_rig:
        raise ValueError("parent-rig skinned components must not own rig data")
    if not record.owns_geometry:
        raise ValueError("generated skinned components must own their geometry")
    if record.attachment_target != "body":
        raise ValueError("parent-rig skinned components currently require attachment_target 'body'")
    if any(item.component_id == record.component_id for item in component_records(root)):
        raise ValueError("component id is already attached to this asset")
    if not isinstance(name, str) or not name.strip():
        raise ValueError("component name must be a nonempty string")

    armature = _armature(root)
    skin_weights = tuple(skin_weights)
    weights_by_part = _validate_weights(mesh, skin_weights, armature)
    coordinate_scale = root.get("coordinate_scale")
    if not isinstance(coordinate_scale, (int, float)) or coordinate_scale <= 0:
        raise ValueError("asset root has an invalid coordinate scale")

    collection = root.users_collection[0]
    created_objects = []
    created_meshes = []
    previous_registry = root.get(_COMPONENTS_KEY)
    document = component_document(record)
    skin_document = _weights_document(skin_weights)
    try:
        component_root = bpy.data.objects.new(name, None)
        created_objects.append(component_root)
        collection.objects.link(component_root)
        component_root.parent = root
        component_root.empty_display_type = "PLAIN_AXES"
        component_root[_COMPONENT_ID_KEY] = record.component_id
        component_root[_COMPONENT_RECORD_KEY] = json.dumps(document, sort_keys=True)
        component_root[_SKIN_KEY] = json.dumps(skin_document, sort_keys=True)

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

            item = weights_by_part[part.name]
            groups = {}
            bone_names = sorted({influence.bone_name for vertex in item.vertices for influence in vertex})
            for bone_name in bone_names:
                groups[bone_name] = obj.vertex_groups.new(name=bone_name)
            for vertex_index, influences in enumerate(item.vertices):
                for influence in influences:
                    groups[influence.bone_name].add([vertex_index], influence.weight, "REPLACE")
            modifier = obj.modifiers.new(name=_MODIFIER_NAME, type="ARMATURE")
            modifier.object = armature
            modifier.use_vertex_groups = True
            modifier.use_bone_envelopes = False

        documents = _documents(root)
        documents.append(document)
        _set_documents(root, documents)
        inspect_skinned_component(root, record.component_id)
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


def remove_skinned_component(root, component_id):
    """Remove one validated parent-rig skinned component without touching the parent rig."""
    record = inspect_skinned_component(root, component_id)
    component_root = _component_root(root, component_id)
    documents = [
        document for document in _documents(root)
        if document.get("component_id") != component_id
    ]
    _delete_component_tree(component_root)
    _set_documents(root, documents)
    return record


def replace_skinned_component(root, mesh, skin_weights, record, *, name="Skinned Component"):
    """Replace a parent-rig skinned component while preserving stable identity.

    The previous weighted tree remains intact until the replacement has been
    created and fully re-inspected. Failed replacement creation restores the
    original registry and component-root metadata.
    """
    _require_asset_root(root)
    if not isinstance(record, ComponentRecord):
        raise TypeError("component must be a ComponentRecord")
    old_record = inspect_skinned_component(root, record.component_id)
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
        replacement_root = attach_skinned_component(
            root,
            mesh,
            skin_weights,
            record,
            name=name,
        )
    except Exception:
        root[_COMPONENTS_KEY] = previous_registry
        old_root[_COMPONENT_ID_KEY] = old_id
        old_root[_COMPONENT_RECORD_KEY] = old_record_raw
        raise

    _delete_component_tree(old_root)
    inspect_skinned_component(root, record.component_id)
    return old_record, replacement_root


__all__ = [
    "attach_skinned_component",
    "inspect_skinned_component",
    "remove_skinned_component",
    "replace_skinned_component",
]
