# SPDX-License-Identifier: GPL-3.0-or-later
"""Operations on an existing generated asset."""

from .core import get_provider


def is_generated(obj):
    return obj is not None and obj.get('generator') in ('humanoid_blockout', 'object_generator')


def provider_for(root):
    if not is_generated(root):
        raise ValueError('Choose a generated asset first.')
    return get_provider(root.get('object_type', 'humanoid'))


def find_character(obj):
    while obj is not None:
        if is_generated(obj):
            return obj
        obj = obj.parent
    return None


def _saved_values(provider, root):
    try:
        return {field.key: root[field.key] for field in provider.parameters}
    except KeyError:
        raise ValueError("Generation parameters are missing. Generate a new asset first.") from None


def add_basic_rig(root, context):
    from .rigging import attach_rig, attach_deforming_rig
    provider = provider_for(root)
    if not provider.supports_rig:
        raise ValueError(provider.label + ' is a static object and does not support rigging.')
    if context.mode != "OBJECT" or context.scene.objects.get(root.name) != root:
        raise ValueError("Rigging requires the asset in the active scene and Object Mode.")
    if any(obj.type == "ARMATURE" for obj in root.children):
        raise ValueError("This asset already has a rig; its existing rig was preserved.")
    for obj in root.children:
        if obj.type == "MESH" and any(abs(obj.matrix_basis[r][c] - float(r == c)) > 1e-6
                                      for r in range(4) for c in range(4)):
            raise ValueError("Part transforms were edited. Restore their original transforms before automatic rigging.")
    values = _saved_values(provider, root)
    try:
        skeleton = provider.skeleton(values)
    except (KeyError, TypeError, ValueError):
        raise ValueError("Generation parameters are missing. Generate a new asset first.") from None
    scale = root.get("coordinate_scale", 0.01 / context.scene.unit_settings.scale_length)
    if provider.uses_skin_weights:
        mesh_objects = [obj for obj in root.children if obj.type == 'MESH']
        mesh = provider.mesh(values)
        if len(mesh_objects) != len(mesh.parts):
            raise ValueError("Generated mesh no longer matches the selected provider.")
        weights = provider.skin_weights(mesh, values)
        return attach_deforming_rig(root, skeleton, weights, scale)
    return attach_rig(root, skeleton, scale)
