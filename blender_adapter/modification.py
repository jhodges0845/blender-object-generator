# SPDX-License-Identifier: GPL-3.0-or-later
"""Inspect Blender data and safely apply approved Modify operations."""

import json
from math import isclose

from .animation import clip_export_name, generated_actions
from .core import (
    AnimationSnapshot,
    ModificationPlan,
    ModifyAssetSnapshot,
    SemanticOperation,
    canonical_provider_key,
    get_provider,
)
from .workflow import is_generated


_ASSET_ID = "asset_assistant_asset_id"
_RIG_ID = "asset_assistant_rig_id"
_EXPORT_NAME = "asset_assistant_export_name"
_GENERATED_CLIP = "asset_assistant_clip"
_GENERATED_RIG = "asset_assistant_rig"
_GENERATED_MATERIAL = "asset_assistant_generated_material"
_SEMANTIC_PATCH = "asset_assistant_semantic_operations"


def _identity_matrix(matrix):
    return all(isclose(matrix[r][c], float(r == c), abs_tol=1e-6)
               for r in range(4) for c in range(4))


def _saved_parameters(root, provider, warnings):
    values = []
    for field in provider.parameters:
        if field.key not in root:
            warnings.append("Missing saved generation parameter: " + field.label)
            continue
        values.append((field.key, root[field.key]))
    return tuple(values)


def _plain_value(value):
    if isinstance(value, tuple):
        if value and all(isinstance(item, tuple) and len(item) == 2 and isinstance(item[0], str) for item in value):
            return {key: _plain_value(item) for key, item in value}
        return [_plain_value(item) for item in value]
    return value


def _semantic_document(operation):
    return {
        "operation": operation.operation,
        "target": operation.target,
        "arguments": {key: _plain_value(value) for key, value in operation.arguments},
    }


def _semantic_operations(root, warnings):
    payload = root.get(_SEMANTIC_PATCH)
    if not payload:
        return ()
    if not isinstance(payload, str):
        warnings.append("Stored semantic patch metadata is invalid.")
        return ()
    try:
        document = json.loads(payload)
    except (TypeError, ValueError):
        warnings.append("Stored semantic patch metadata is not valid JSON.")
        return ()
    if not isinstance(document, list):
        warnings.append("Stored semantic patch metadata must be a list.")
        return ()
    operations = []
    for item in document:
        if not isinstance(item, dict):
            warnings.append("Stored semantic patch contains an invalid operation.")
            return ()
        operation = item.get("operation")
        target = item.get("target")
        arguments = item.get("arguments", {})
        if not isinstance(operation, str) or not isinstance(target, str) or not isinstance(arguments, dict):
            warnings.append("Stored semantic patch contains invalid fields.")
            return ()
        operations.append(SemanticOperation(operation, target, tuple(arguments.items())))
    return tuple(operations)


def _expected_mesh(provider, values, semantic_operations):
    mesh = provider.mesh(dict(values))
    if semantic_operations:
        semantic_mesh = getattr(provider, "semantic_mesh", None)
        if not callable(semantic_mesh):
            raise ValueError("Provider cannot reproduce stored semantic geometry.")
        mesh = semantic_mesh(mesh, dict(values), semantic_operations)
    return mesh


def _geometry_owned(root, provider, values, semantic_operations, warnings):
    meshes = [obj for obj in root.children if obj.type == "MESH"]
    if not meshes:
        warnings.append("Generated geometry is missing.")
        return False
    if len(values) != len(provider.parameters):
        warnings.append("Geometry ownership cannot be verified without all generation parameters.")
        return False
    if any(not _identity_matrix(obj.matrix_basis) for obj in meshes):
        warnings.append("One or more generated mesh transforms were edited.")
        return False
    try:
        expected = _expected_mesh(provider, values, semantic_operations)
    except (KeyError, TypeError, ValueError):
        warnings.append("Current generation parameters and semantic patch cannot reproduce provider geometry.")
        return False
    actual = {obj.get("part_name", obj.get("body_part")): obj for obj in meshes}
    expected_parts = {part.name: part for part in expected.parts}
    if len(actual) != len(meshes) or set(actual) != set(expected_parts):
        warnings.append("Generated mesh parts no longer match the provider definition.")
        return False
    scale = root.get("coordinate_scale")
    if not isinstance(scale, (int, float)) or scale <= 0:
        warnings.append("Generated coordinate scale is missing or invalid.")
        return False
    for name, part in expected_parts.items():
        obj = actual[name]
        if len(obj.data.vertices) != len(part.vertices) or len(obj.data.polygons) != len(part.faces):
            warnings.append(name + ": mesh topology differs from generated geometry.")
            return False
        for vertex, expected_vertex in zip(obj.data.vertices, part.vertices):
            if any(not isclose(vertex.co[index], expected_vertex[index] * scale, abs_tol=1e-6)
                   for index in range(3)):
                warnings.append(name + ": mesh vertices were edited after generation.")
                return False
        for polygon, expected_face in zip(obj.data.polygons, part.faces):
            if tuple(polygon.vertices) != tuple(expected_face):
                warnings.append(name + ": mesh faces were edited after generation.")
                return False
    return True


def _rig_state(root, warnings):
    rigs = [obj for obj in root.children if obj.type == "ARMATURE"]
    if not rigs:
        return False, False
    if len(rigs) != 1:
        warnings.append("Multiple armatures make generated rig ownership ambiguous.")
        return True, False
    rig = rigs[0]
    owned = bool(rig.get(_RIG_ID))
    if not owned:
        warnings.append("The attached rig is not marked as Asset Assistant-generated.")
    data = rig.animation_data
    generated = set(generated_actions(root))
    if data and (data.nla_tracks or data.drivers):
        warnings.append("The rig has NLA tracks or drivers that Modify must preserve.")
        owned = False
    if data and data.action and data.action not in generated:
        warnings.append("The rig has an artist-owned active action that Modify must preserve.")
        owned = False
    if any(bone.constraints for bone in rig.pose.bones):
        warnings.append("The rig has pose constraints that Modify must preserve.")
        owned = False
    return True, owned


def _material_state(root, provider, values, warnings):
    meshes = [obj for obj in root.children if obj.type == "MESH"]
    materials = {slot.material for obj in meshes for slot in obj.material_slots if slot.material is not None}
    if not materials:
        return False, False
    if not getattr(provider, "supports_materials", False) or len(values) != len(provider.parameters):
        warnings.append("Material ownership cannot be verified for this provider state.")
        return True, False
    try:
        expected_names = {spec.name for spec in provider.materials(dict(values))}
    except (KeyError, TypeError, ValueError):
        warnings.append("Provider materials cannot be reproduced from saved parameters.")
        return True, False
    actual_names = {material.name for material in materials}
    marked_generated = all(bool(material.get(_GENERATED_MATERIAL)) for material in materials)
    owned = marked_generated or actual_names == expected_names
    if not owned:
        warnings.append("Material assignments differ from the generated provider materials.")
    return True, owned


def _animation_state(root, warnings):
    actions = generated_actions(root)
    if not actions:
        return (), False, False
    clips = []
    seen = set()
    for action in actions:
        clip_id = str(action.get(_GENERATED_CLIP) or action.name)
        if clip_id in seen:
            warnings.append("Duplicate generated animation clip identity: " + clip_id)
            return (), True, False
        seen.add(clip_id)
        clips.append(AnimationSnapshot(clip_id, clip_export_name(action)))
    return tuple(sorted(clips, key=lambda clip: clip.clip_id)), True, True


def inspect_generated_asset(root):
    """Return a portable snapshot without mutating the Blender scene."""
    if not is_generated(root):
        raise ValueError("Choose a generated Asset Assistant asset first.")
    warnings = []
    stored_key = root.get("object_type", "humanoid")
    canonical_key = canonical_provider_key(stored_key)
    provider = get_provider(canonical_key)
    if stored_key != canonical_key:
        warnings.append("Legacy provider key " + str(stored_key) + " resolves to " + canonical_key + ".")

    values = _saved_parameters(root, provider, warnings)
    semantic_operations = _semantic_operations(root, warnings)
    owns_geometry = _geometry_owned(root, provider, values, semantic_operations, warnings)
    has_rig, owns_rig = _rig_state(root, warnings)
    has_materials, owns_materials = _material_state(root, provider, values, warnings)
    animations, has_animations, owns_animations = _animation_state(root, warnings)

    asset_id = root.get(_ASSET_ID)
    if not asset_id:
        asset_id = "legacy:" + root.name
        warnings.append("This legacy asset has no stable Asset Assistant asset id; regenerate before destructive Modify operations.")

    return ModifyAssetSnapshot(
        asset_id=str(asset_id),
        provider_key=provider.key,
        provider_label=provider.label,
        parameters=values,
        animations=animations,
        semantic_operations=semantic_operations,
        has_rig=has_rig,
        has_materials=has_materials,
        has_animations=has_animations,
        owns_geometry=owns_geometry,
        owns_rig=owns_rig,
        owns_materials=owns_materials,
        owns_animations=owns_animations,
        warnings=tuple(warnings),
    )


def _check_plan_matches(root, plan):
    if not isinstance(plan, ModificationPlan):
        raise TypeError("plan must be a ModificationPlan")
    if plan.blockers:
        raise ValueError("Modification plan has blockers: " + "; ".join(plan.blockers))
    snapshot = inspect_generated_asset(root)
    if snapshot.asset_id != plan.asset_id:
        raise ValueError("Modification plan no longer matches the selected asset.")
    if snapshot.provider_key != plan.provider_key:
        raise ValueError("Modification plan provider no longer matches the selected asset.")
    return snapshot


def apply_metadata_modification(root, plan):
    """Apply an approved metadata-only plan transactionally."""
    snapshot = _check_plan_matches(root, plan)
    if plan.rebuild_components or plan.requested_parameter_changes or plan.requested_semantic_operations:
        raise ValueError("This apply path only supports metadata-only modifications.")
    if plan.requested_animation_renames and not snapshot.owns_animations:
        raise ValueError("Generated animation ownership is ambiguous; nothing was changed.")

    actions = {str(action.get(_GENERATED_CLIP) or action.name): action
               for action in generated_actions(root)}
    requested = dict(plan.requested_animation_renames)
    missing = [clip_id for clip_id in requested if clip_id not in actions]
    if missing:
        raise ValueError("Modification plan references missing generated animation: " + missing[0])

    final_names = {clip_id: requested.get(clip_id, clip_export_name(action)).strip()
                   for clip_id, action in actions.items()}
    if any(not name for name in final_names.values()):
        raise ValueError("Animation export name cannot be empty.")
    if len(set(final_names.values())) != len(final_names):
        raise ValueError("Animation export names must remain unique; nothing was changed.")

    previous = {clip_id: action.get(_EXPORT_NAME) for clip_id, action in actions.items()
                if clip_id in requested}
    try:
        for clip_id, export_name in requested.items():
            actions[clip_id][_EXPORT_NAME] = export_name
    except Exception:
        for clip_id, old_value in previous.items():
            action = actions[clip_id]
            if old_value is None:
                if _EXPORT_NAME in action:
                    del action[_EXPORT_NAME]
            else:
                action[_EXPORT_NAME] = old_value
        raise
    return inspect_generated_asset(root)


def _staged_asset(root, provider, values, snapshot):
    """Build replacement generated components before touching the live asset."""
    import bpy
    from .adapter import create_character

    if bpy.context.scene.objects.get(root.name) != root or bpy.context.mode != "OBJECT":
        raise ValueError("Modify regeneration requires the asset in the active scene and Object Mode.")
    mesh = provider.mesh(values)
    if snapshot.semantic_operations:
        semantic_mesh = getattr(provider, "semantic_mesh", None)
        if not callable(semantic_mesh):
            raise ValueError("Provider cannot reapply the stored semantic patch.")
        mesh = semantic_mesh(mesh, values, snapshot.semantic_operations)
    materials = provider.materials(values) if snapshot.has_materials else ()
    skeleton = None
    weights = None
    if snapshot.has_rig:
        skeleton = provider.skeleton(values)
        if provider.uses_skin_weights:
            weights = provider.skin_weights(mesh, values)
    staged = create_character(
        mesh,
        name=root.name + ".ModifyStaging",
        scene=bpy.context.scene,
        skeleton=skeleton,
        skin_weights=weights,
        materials=materials,
    )
    staged["object_type"] = provider.key
    for key, value in values.items():
        staged[key] = value
    return staged


def _remove_staged_root(staged, *, remove_children=True):
    import bpy

    collections = tuple(staged.users_collection)
    if remove_children:
        for child in tuple(staged.children):
            bpy.data.objects.remove(child, do_unlink=True)
    bpy.data.objects.remove(staged, do_unlink=True)
    for collection in collections:
        if collection.users == 0:
            bpy.data.collections.remove(collection)


def apply_parameter_modification(root, plan):
    """Stage and swap provider-owned generated components for parameter changes."""
    import bpy

    snapshot = _check_plan_matches(root, plan)
    if not plan.requested_parameter_changes:
        raise ValueError("This apply path requires at least one provider parameter change.")
    if plan.requested_semantic_operations:
        raise ValueError("Apply semantic operations separately from parameter regeneration.")
    if not plan.rebuild_components or "geometry" not in plan.rebuild_components:
        raise ValueError("Parameter modification plan must rebuild generated geometry.")
    if plan.requested_animation_renames:
        raise ValueError("Apply animation renames separately before parameter regeneration.")

    ownership = {
        "geometry": snapshot.owns_geometry,
        "rig": snapshot.owns_rig,
        "materials": snapshot.owns_materials,
        "animations": snapshot.owns_animations,
    }
    for component in plan.rebuild_components:
        if not ownership.get(component, False):
            raise ValueError("Generated " + component + " ownership is ambiguous; nothing was changed.")

    provider = get_provider(snapshot.provider_key)
    values = snapshot.parameter_values()
    values.update(dict(plan.requested_parameter_changes))
    staged = _staged_asset(root, provider, values, snapshot)

    old_meshes = [obj for obj in root.children if obj.type == "MESH"]
    old_rigs = [obj for obj in root.children if obj.type == "ARMATURE"]
    staged_meshes = [obj for obj in staged.children if obj.type == "MESH"]
    staged_rigs = [obj for obj in staged.children if obj.type == "ARMATURE"]
    old_rig = old_rigs[0] if old_rigs else None
    new_rig = staged_rigs[0] if staged_rigs else None
    actions = tuple(generated_actions(root))

    if snapshot.has_rig and (len(old_rigs) != 1 or len(staged_rigs) != 1):
        _remove_staged_root(staged)
        raise ValueError("Rig staging did not produce exactly one generated armature.")
    if snapshot.has_animations:
        if not snapshot.has_rig or old_rig is None or new_rig is None:
            _remove_staged_root(staged)
            raise ValueError("Generated animations require a staged rig for safe regeneration.")
        if {bone.name for bone in old_rig.data.bones} != {bone.name for bone in new_rig.data.bones}:
            _remove_staged_root(staged)
            raise ValueError("Provider bone identities changed; generated animations cannot be preserved safely.")

    original_collection = root.users_collection[0] if root.users_collection else None
    if original_collection is None:
        _remove_staged_root(staged)
        raise ValueError("Generated asset is not linked to a collection.")

    old_children = tuple(old_meshes + old_rigs)
    old_names = {obj: obj.name for obj in old_children}
    parameter_before = {key: root.get(key) for key, _ in plan.requested_parameter_changes}
    action_metadata = {action: (action.get(_RIG_ID), action.get(_GENERATED_RIG)) for action in actions}
    old_active = old_rig.animation_data.action if old_rig and old_rig.animation_data else None

    try:
        for obj in old_children:
            obj.name = obj.name + ".ModifyBackup"
            obj.parent = staged

        for obj in tuple(staged_meshes + staged_rigs):
            if original_collection not in obj.users_collection:
                original_collection.objects.link(obj)
            obj.parent = root

        old_mesh_by_part = {obj.get("part_name", obj.get("body_part")): obj for obj in old_meshes}
        for obj in staged_meshes:
            part = obj.get("part_name", obj.get("body_part"))
            if part in old_mesh_by_part:
                obj.name = old_names[old_mesh_by_part[part]]
        if old_rig is not None and new_rig is not None:
            new_rig.name = old_names[old_rig]

        for key, value in plan.requested_parameter_changes:
            root[key] = value

        if actions:
            new_rig_id = new_rig.get(_RIG_ID)
            if not new_rig_id:
                raise ValueError("Staged rig is missing its generated ownership id.")
            for action in actions:
                action[_RIG_ID] = new_rig_id
                action[_GENERATED_RIG] = new_rig.name
            data = new_rig.animation_data_create()
            if old_active in actions:
                data.action = old_active
                if hasattr(old_active, "slots") and len(old_active.slots):
                    data.action_slot = old_active.slots[0]

        result = inspect_generated_asset(root)
        if not result.owns_geometry:
            raise RuntimeError("Replacement geometry failed post-apply ownership validation.")
        if snapshot.has_rig and not result.owns_rig:
            raise RuntimeError("Replacement rig failed post-apply ownership validation.")
        if snapshot.has_materials and not result.owns_materials:
            raise RuntimeError("Replacement materials failed post-apply ownership validation.")
        if snapshot.has_animations and not result.owns_animations:
            raise RuntimeError("Generated animations failed post-apply ownership validation.")
    except Exception:
        for obj in tuple(staged_meshes + staged_rigs):
            try:
                bpy.data.objects.remove(obj, do_unlink=True)
            except ReferenceError:
                pass
        for obj in old_children:
            try:
                obj.parent = root
                obj.name = old_names[obj]
                if original_collection not in obj.users_collection:
                    original_collection.objects.link(obj)
            except ReferenceError:
                pass
        for key, old_value in parameter_before.items():
            if old_value is None:
                if key in root:
                    del root[key]
            else:
                root[key] = old_value
        for action, (old_rig_id, old_rig_name) in action_metadata.items():
            if old_rig_id is None:
                if _RIG_ID in action:
                    del action[_RIG_ID]
            else:
                action[_RIG_ID] = old_rig_id
            if old_rig_name is None:
                if _GENERATED_RIG in action:
                    del action[_GENERATED_RIG]
            else:
                action[_GENERATED_RIG] = old_rig_name
        _remove_staged_root(staged, remove_children=False)
        raise

    for obj in old_children:
        bpy.data.objects.remove(obj, do_unlink=True)
    _remove_staged_root(staged, remove_children=False)
    return result


def apply_semantic_modification(root, plan):
    """Apply semantic geometry as a persistent procedural patch with unchanged topology."""
    snapshot = _check_plan_matches(root, plan)
    if not plan.requested_semantic_operations:
        raise ValueError("This apply path requires semantic operations.")
    if plan.requested_parameter_changes or plan.requested_animation_renames:
        raise ValueError("Apply semantic operations separately from other Modify changes.")
    if plan.rebuild_components != ("geometry",):
        raise ValueError("Semantic mesh apply currently supports geometry-only patches.")
    if not snapshot.owns_geometry:
        raise ValueError("Generated geometry ownership is ambiguous; nothing was changed.")

    provider = get_provider(snapshot.provider_key)
    semantic_mesh = getattr(provider, "semantic_mesh", None)
    if not callable(semantic_mesh):
        raise ValueError("Provider does not implement semantic geometry apply.")
    values = snapshot.parameter_values()
    combined = snapshot.semantic_operations + plan.requested_semantic_operations
    mesh = semantic_mesh(provider.mesh(values), values, combined)
    expected_parts = {part.name: part for part in mesh.parts}
    actual = {obj.get("part_name", obj.get("body_part")): obj for obj in root.children if obj.type == "MESH"}
    if set(actual) != set(expected_parts):
        raise ValueError("Semantic patch changed generated mesh part identities.")
    scale = root.get("coordinate_scale")
    if not isinstance(scale, (int, float)) or scale <= 0:
        raise ValueError("Generated coordinate scale is missing or invalid.")

    before_vertices = {}
    for name, part in expected_parts.items():
        obj = actual[name]
        if len(obj.data.vertices) != len(part.vertices) or len(obj.data.polygons) != len(part.faces):
            raise ValueError("Semantic patch must preserve generated mesh topology.")
        if any(tuple(polygon.vertices) != tuple(face) for polygon, face in zip(obj.data.polygons, part.faces)):
            raise ValueError("Semantic patch must preserve generated mesh topology.")
        before_vertices[obj] = tuple(tuple(vertex.co) for vertex in obj.data.vertices)

    previous_patch = root.get(_SEMANTIC_PATCH)
    payload = json.dumps([_semantic_document(operation) for operation in combined], sort_keys=True)
    try:
        for name, part in expected_parts.items():
            obj = actual[name]
            for vertex, coordinate in zip(obj.data.vertices, part.vertices):
                vertex.co = tuple(value * scale for value in coordinate)
            obj.data.update()
        root[_SEMANTIC_PATCH] = payload
        result = inspect_generated_asset(root)
        if not result.owns_geometry:
            raise RuntimeError("Semantic patch failed post-apply ownership validation.")
    except Exception:
        for obj, coordinates in before_vertices.items():
            for vertex, coordinate in zip(obj.data.vertices, coordinates):
                vertex.co = coordinate
            obj.data.update()
        if previous_patch is None:
            if _SEMANTIC_PATCH in root:
                del root[_SEMANTIC_PATCH]
        else:
            root[_SEMANTIC_PATCH] = previous_patch
        raise
    return result
