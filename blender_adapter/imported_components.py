# SPDX-License-Identifier: GPL-3.0-or-later
"""Adopt artist-authored Blender mesh objects into the component lifecycle."""

import json

from .components import (
    _COMPONENT_ID_KEY,
    _COMPONENT_RECORD_KEY,
    _COMPONENTS_KEY,
    _armature,
    _attach_component_root,
    _documents,
    _require_asset_root,
    _set_documents,
    component_records,
    inspect_component,
)
from .core import (
    AttachmentMode,
    ComponentRecord,
    RigBinding,
    component_document,
    validate_component,
)
from .skinned_components import _MODIFIER_NAME, _SKIN_KEY, inspect_skinned_component

_PART_NAME_KEY = "component_part_name"


def _asset_owner(obj):
    current = obj
    while current is not None:
        if current.get("generator") == "object_generator":
            return current
        current = current.parent
    return None


def _validate_import_candidate(root, mesh_object, record, *, allow_target_hierarchy=False):
    _require_asset_root(root)
    validate_component(record)
    if not record.owns_geometry:
        raise ValueError("adopted components must own their geometry")
    if record.owns_materials:
        raise ValueError("imported adoption does not claim material ownership")
    if mesh_object is None or mesh_object.type != "MESH":
        raise ValueError("adoption requires one Blender mesh object")
    owner = _asset_owner(mesh_object)
    if owner is not None:
        if owner != root:
            raise ValueError("mesh belongs to a different Asset Assistant asset")
        if not allow_target_hierarchy:
            raise ValueError("mesh is already part of an Asset Assistant asset")
        if "part_name" in mesh_object or "body_part" in mesh_object:
            raise ValueError("generated body geometry cannot be adopted as a component")
    if mesh_object.children:
        raise ValueError("adoption currently requires a mesh with no child objects")
    if _COMPONENT_ID_KEY in mesh_object:
        raise ValueError("mesh is already registered as an Asset Assistant component")
    if any(item.component_id == record.component_id for item in component_records(root)):
        raise ValueError("component id is already attached to this asset")


def _restore_object_metadata(mesh_object, state):
    had_component_id, previous_component_id, had_part_name, previous_part_name = state
    if had_component_id:
        mesh_object[_COMPONENT_ID_KEY] = previous_component_id
    elif _COMPONENT_ID_KEY in mesh_object:
        del mesh_object[_COMPONENT_ID_KEY]
    if had_part_name:
        mesh_object[_PART_NAME_KEY] = previous_part_name
    elif _PART_NAME_KEY in mesh_object:
        del mesh_object[_PART_NAME_KEY]


def _object_metadata_state(mesh_object):
    return (
        _COMPONENT_ID_KEY in mesh_object,
        mesh_object.get(_COMPONENT_ID_KEY),
        _PART_NAME_KEY in mesh_object,
        mesh_object.get(_PART_NAME_KEY),
    )


def adopt_rigid_component(root, mesh_object, record, *, name=None):
    """Transfer one existing Blender mesh into an owned rigid component.

    Adoption is an explicit ownership transfer: the mesh object and mesh datablock
    are not copied. Once adopted, normal component remove/replace operations may
    delete them. Materials remain artist-owned in this first adoption path so a
    shared material cannot be deleted merely because one component was removed.
    """
    import bpy

    _validate_import_candidate(root, mesh_object, record)
    if record.attachment_mode != AttachmentMode.RIGID:
        raise ValueError("rigid adoption requires a rigid component record")
    if record.owns_rig:
        raise ValueError("rigid components must not own rig data")
    if any(modifier.type == "ARMATURE" for modifier in mesh_object.modifiers):
        raise ValueError("mesh uses an armature modifier; use skinned component adoption instead")

    component_name = name or mesh_object.name or "Imported Component"
    if not isinstance(component_name, str) or not component_name.strip():
        raise ValueError("component name must be a nonempty string")

    collection = root.users_collection[0]
    previous_registry = root.get(_COMPONENTS_KEY)
    previous_parent = mesh_object.parent
    previous_parent_type = mesh_object.parent_type
    previous_parent_bone = mesh_object.parent_bone
    previous_world = mesh_object.matrix_world.copy()
    metadata_state = _object_metadata_state(mesh_object)
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

        _restore_object_metadata(mesh_object, metadata_state)
        mesh_object.parent = previous_parent
        mesh_object.parent_type = previous_parent_type
        mesh_object.parent_bone = previous_parent_bone
        mesh_object.matrix_world = previous_world
        if component_root is not None and component_root.name in bpy.data.objects:
            bpy.data.objects.remove(component_root, do_unlink=True)
        raise


def _imported_skin_document(mesh_object, armature):
    bone_names = {bone.name for bone in armature.data.bones}
    vertices = []
    for vertex in mesh_object.data.vertices:
        influences = []
        for assignment in vertex.groups:
            group = mesh_object.vertex_groups[assignment.group]
            weight = float(assignment.weight)
            if weight <= 0.0:
                continue
            if group.name not in bone_names:
                raise ValueError(
                    "skinned mesh vertex groups must map only to bones in the parent Asset Assistant rig"
                )
            influences.append([group.name, weight])
        if not influences:
            raise ValueError("skinned mesh must weight every vertex to the parent Asset Assistant rig")
        vertices.append(sorted(influences, key=lambda item: item[0]))
    return {mesh_object.name: vertices}


def adopt_skinned_component(root, mesh_object, record, *, name=None):
    """Adopt one artist-authored weighted mesh into the parent-rig component lifecycle.

    Existing vertex groups and a valid parent-rig armature modifier are preserved.
    If the mesh has no armature modifier, adoption adds the Asset Assistant parent
    rig modifier after validating all existing vertex-group weights. An existing
    armature modifier is never silently retargeted or reconfigured.
    """
    import bpy

    _validate_import_candidate(root, mesh_object, record, allow_target_hierarchy=True)
    if record.attachment_mode != AttachmentMode.SKINNED:
        raise ValueError("skinned adoption requires a skinned component record")
    if record.rig_binding != RigBinding.PARENT:
        raise ValueError("imported skinned adoption currently requires parent rig binding")
    if record.owns_rig:
        raise ValueError("parent-rig skinned components must not own rig data")
    if record.attachment_target != "body":
        raise ValueError("parent-rig skinned components currently require attachment_target 'body'")

    armature = _armature(root)
    skin_document = _imported_skin_document(mesh_object, armature)
    armature_modifiers = [modifier for modifier in mesh_object.modifiers if modifier.type == "ARMATURE"]
    if len(armature_modifiers) > 1:
        raise ValueError("skinned adoption requires zero or one armature modifier")
    existing_modifier = armature_modifiers[0] if armature_modifiers else None
    if existing_modifier is not None:
        if existing_modifier.object != armature:
            raise ValueError("existing armature modifier must already target the owning Asset Assistant rig")
        if not existing_modifier.use_vertex_groups or existing_modifier.use_bone_envelopes:
            raise ValueError(
                "existing armature modifier must already use vertex groups without bone envelopes"
            )

    component_name = name or mesh_object.name or "Imported Skinned Component"
    if not isinstance(component_name, str) or not component_name.strip():
        raise ValueError("component name must be a nonempty string")

    collection = root.users_collection[0]
    previous_registry = root.get(_COMPONENTS_KEY)
    previous_parent = mesh_object.parent
    previous_parent_type = mesh_object.parent_type
    previous_parent_bone = mesh_object.parent_bone
    previous_world = mesh_object.matrix_world.copy()
    metadata_state = _object_metadata_state(mesh_object)
    created_modifier = None
    document = component_document(record)
    component_root = None
    try:
        component_root = bpy.data.objects.new(component_name, None)
        collection.objects.link(component_root)
        component_root.parent = root
        component_root.empty_display_type = "PLAIN_AXES"
        component_root[_COMPONENT_ID_KEY] = record.component_id
        component_root[_COMPONENT_RECORD_KEY] = json.dumps(document, sort_keys=True)
        component_root[_SKIN_KEY] = json.dumps(skin_document, sort_keys=True)

        mesh_object.parent = component_root
        mesh_object.parent_type = "OBJECT"
        mesh_object.parent_bone = ""
        mesh_object.matrix_world = previous_world
        mesh_object[_COMPONENT_ID_KEY] = record.component_id
        mesh_object[_PART_NAME_KEY] = mesh_object.name

        if existing_modifier is None:
            created_modifier = mesh_object.modifiers.new(name=_MODIFIER_NAME, type="ARMATURE")
            created_modifier.object = armature
            created_modifier.use_vertex_groups = True
            created_modifier.use_bone_envelopes = False

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

        if created_modifier is not None:
            try:
                mesh_object.modifiers.remove(created_modifier)
            except (ReferenceError, RuntimeError):
                pass

        _restore_object_metadata(mesh_object, metadata_state)
        mesh_object.parent = previous_parent
        mesh_object.parent_type = previous_parent_type
        mesh_object.parent_bone = previous_parent_bone
        mesh_object.matrix_world = previous_world
        if component_root is not None and component_root.name in bpy.data.objects:
            bpy.data.objects.remove(component_root, do_unlink=True)
        raise


__all__ = ["adopt_rigid_component", "adopt_skinned_component"]
