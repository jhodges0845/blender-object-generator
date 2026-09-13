# SPDX-License-Identifier: GPL-3.0-or-later
"""Operations on existing Asset Assistant assets."""

from .core import canonical_provider_key, get_provider


_EXTERNAL_ASSET_KEY = "asset_assistant_external_asset"


def is_generated(obj):
    return obj is not None and obj.get('generator') in ('humanoid_blockout', 'object_generator')


def is_external_asset(obj):
    return obj is not None and bool(obj.get(_EXTERNAL_ASSET_KEY, False))


def is_managed_asset(obj):
    """Return whether the root is an explicit Asset Assistant workflow target.

    External assets only become managed after the artist explicitly adopts them.
    This does not make them generated-provider assets and does not transfer ownership
    of their geometry, rigs, materials, weights, or animation curves.
    """
    return is_generated(obj) or is_external_asset(obj)


def _migrate_provider_metadata(root, stored_key, canonical_key):
    """Upgrade persisted provider/part identifiers without changing artist data."""
    if canonical_key == stored_key:
        return
    root['object_type'] = canonical_key
    for obj in root.children:
        if obj.type != 'MESH':
            continue
        if obj.get('part_name') == stored_key:
            obj['part_name'] = canonical_key
        if obj.get('body_part') == stored_key:
            obj['body_part'] = canonical_key


def provider_for(root):
    if not is_generated(root):
        raise ValueError('This imported asset is not tied to a generated provider.')
    stored_key = root.get('object_type', 'humanoid')
    canonical_key = canonical_provider_key(stored_key)
    _migrate_provider_metadata(root, stored_key, canonical_key)
    return get_provider(canonical_key)


def find_character(obj):
    while obj is not None:
        if is_managed_asset(obj):
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
