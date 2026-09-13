# SPDX-License-Identifier: GPL-3.0-or-later
"""Normalized logical structure for generated and imported Asset Assistant assets.

Blender importers are allowed to create different raw object hierarchies. Downstream
Asset Assistant workflows should ask this module for an asset boundary, base meshes,
base rigs, and animation-bearing objects instead of assuming direct children of one
particular importer root.
"""

import bpy


_IMPORT_GROUP_KEY = "asset_assistant_import_group"
_IMPORT_ROOT_KEY = "asset_assistant_import_root"
_COMPONENT_ID_KEY = "asset_assistant_component_id"
_COMPONENT_RIG_KEY = "asset_assistant_component_rig"


def _metadata(obj, key, default=None):
    """Read Blender custom properties without requiring a real bpy object.

    Host-side contract tests intentionally use lightweight namespaces. Treat objects
    without Blender's ``get`` API as unmarked scene objects so normalized traversal
    keeps the same recursive fallback behavior outside Blender.
    """
    if obj is None:
        return default
    getter = getattr(obj, "get", None)
    return getter(key, default) if callable(getter) else default


def _import_group(obj):
    return str(_metadata(obj, _IMPORT_GROUP_KEY, ""))


def _hierarchy_root(obj):
    root = obj
    while root is not None and getattr(root, "parent", None) is not None:
        root = root.parent
    return root


def _walk_hierarchy(root):
    if root is None:
        return
    yield root
    for child in tuple(getattr(root, "children", ())):
        yield from _walk_hierarchy(child)


def _is_component_member(obj):
    """Return whether an object belongs to a first-class component, not the base asset."""
    return bool(_metadata(obj, _COMPONENT_ID_KEY)) or bool(_metadata(obj, _COMPONENT_RIG_KEY, False))


def asset_boundary(selected, objects=None):
    """Return ``(logical_root, members)`` for one asset candidate.

    Imported files use the non-owning import-group metadata established at import
    time, so sibling meshes/rigs remain in one logical asset even when Blender's
    importer did not parent them under the same Empty. Ordinary/generated assets
    fall back to their complete parent hierarchy.
    """
    if selected is None:
        return None, ()

    group = _import_group(selected)
    universe = tuple(objects) if objects is not None else tuple(bpy.data.objects)
    if group:
        members = tuple(obj for obj in universe if _import_group(obj) == group)
        if members:
            root = next(
                (obj for obj in members if bool(_metadata(obj, _IMPORT_ROOT_KEY, False))),
                None,
            )
            if root is None:
                roots = tuple(
                    obj for obj in members if getattr(obj, "parent", None) not in members
                )
                root = roots[0] if roots else selected
            return root, members

    root = _hierarchy_root(selected)
    return root, tuple(_walk_hierarchy(root))


def asset_members(root, objects=None):
    """Return every Blender object in the logical asset boundary, including components."""
    _logical_root, members = asset_boundary(root, objects=objects)
    return members


def base_asset_members(root, objects=None):
    """Return base-asset objects while keeping first-class components in a separate scope."""
    return tuple(
        obj for obj in asset_members(root, objects=objects)
        if not _is_component_member(obj)
    )


def asset_meshes(root, objects=None):
    return tuple(
        obj for obj in base_asset_members(root, objects=objects)
        if getattr(obj, "type", None) == "MESH"
    )


def asset_rigs(root, objects=None):
    """Return unique base armatures, including modifier-referenced imported rigs.

    Component-owned armatures intentionally stay out of the base-rig set. A generated
    asset may legally contain a self-rigged component, and that must not make base
    animation validation look like the character suddenly has multiple rigs.
    """
    members = base_asset_members(root, objects=objects)
    rigs = {
        id(obj): obj
        for obj in members
        if getattr(obj, "type", None) == "ARMATURE" and not _is_component_member(obj)
    }
    for mesh in (obj for obj in members if getattr(obj, "type", None) == "MESH"):
        for modifier in tuple(getattr(mesh, "modifiers", ())):
            if getattr(modifier, "type", None) != "ARMATURE":
                continue
            rig = getattr(modifier, "object", None)
            if rig is not None and not _is_component_member(rig):
                rigs[id(rig)] = rig
    return tuple(rigs.values())


def animation_count_for_object(obj):
    """Count unique animation Actions referenced by one Blender object.

    Blender's GLB importer can expose the same clip both as the active Action and as
    an NLA strip. Counting the active slot plus NLA tracks therefore over-reports
    clips after a round trip. Asset Assistant cares about distinct editable clips,
    so deduplicate by Action identity across both locations.
    """
    animation_data = getattr(obj, "animation_data", None)
    if animation_data is None:
        return 0
    actions = {}
    active = getattr(animation_data, "action", None)
    if active is not None:
        actions[id(active)] = active
    for track in tuple(getattr(animation_data, "nla_tracks", ())):
        for strip in tuple(getattr(track, "strips", ())):
            action = getattr(strip, "action", None)
            if action is not None:
                actions[id(action)] = action
    return len(actions)


def asset_animation_count(root, objects=None):
    members = base_asset_members(root, objects=objects)
    count = sum(animation_count_for_object(obj) for obj in members)
    for rig in asset_rigs(root, objects=objects):
        if rig not in members:
            count += animation_count_for_object(rig)
    return count


def logical_asset(root, objects=None):
    """Return one normalized base-asset view consumed by UI/workflow code.

    ``objects`` retains the complete boundary for ownership/traversal work, while
    ``meshes``, ``rigs``, and ``animation_count`` describe the base asset only.
    First-class components remain a separate concern and cannot create false
    multi-rig or extra-animation results for the character itself.
    """
    logical_root, members = asset_boundary(root, objects=objects)
    base_members = tuple(obj for obj in members if not _is_component_member(obj))
    meshes = tuple(obj for obj in base_members if getattr(obj, "type", None) == "MESH")
    rigs = asset_rigs(logical_root, objects=objects) if logical_root is not None else ()
    return {
        "root": logical_root,
        "objects": members,
        "base_objects": base_members,
        "meshes": meshes,
        "rigs": rigs,
        "animation_count": asset_animation_count(logical_root, objects=objects) if logical_root is not None else 0,
    }


__all__ = [
    "animation_count_for_object",
    "asset_animation_count",
    "asset_boundary",
    "asset_members",
    "asset_meshes",
    "asset_rigs",
    "base_asset_members",
    "logical_asset",
]
