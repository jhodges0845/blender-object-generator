# SPDX-License-Identifier: GPL-3.0-or-later
"""Inspect Blender data into the host-independent Modify snapshot contract."""

from math import isclose

from .animation import clip_export_name, generated_actions
from .core import AnimationSnapshot, ModifyAssetSnapshot, canonical_provider_key, get_provider
from .workflow import is_generated


_ASSET_ID = "asset_assistant_asset_id"
_RIG_ID = "asset_assistant_rig_id"


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


def _geometry_owned(root, provider, values, warnings):
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
        expected = provider.mesh(dict(values))
    except (KeyError, TypeError, ValueError):
        warnings.append("Current generation parameters cannot reproduce the provider geometry.")
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
    if data and (data.nla_tracks or data.drivers):
        warnings.append("The rig has NLA tracks or drivers that Modify must preserve.")
    if any(bone.constraints for bone in rig.pose.bones):
        warnings.append("The rig has pose constraints that Modify must preserve.")
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
    owned = actual_names == expected_names
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
        clip_id = str(action.get("asset_assistant_clip") or action.name)
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
    owns_geometry = _geometry_owned(root, provider, values, warnings)
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
        has_rig=has_rig,
        has_materials=has_materials,
        has_animations=has_animations,
        owns_geometry=owns_geometry,
        owns_rig=owns_rig,
        owns_materials=owns_materials,
        owns_animations=owns_animations,
        warnings=tuple(warnings),
    )
