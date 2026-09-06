# SPDX-License-Identifier: GPL-3.0-or-later
"""Operations on an existing generated character."""

from .core import BodyType, HumanoidSpec, generate_proportions, generate_skeleton


def find_character(obj):
    while obj is not None:
        if obj.get("generator") == "humanoid_blockout":
            return obj
        obj = obj.parent
    return None


def add_basic_rig(root, context):
    from .rigging import attach_rig
    if root is None or root.get("generator") != "humanoid_blockout":
        raise ValueError("Choose a generated character first.")
    if context.mode != "OBJECT" or context.scene.objects.get(root.name) != root:
        raise ValueError("Rigging requires the character in the active scene and Object Mode.")
    if any(obj.type == "ARMATURE" for obj in root.children):
        raise ValueError("This character already has a rig; its existing rig was preserved.")
    for obj in root.children:
        if obj.type == "MESH" and any(abs(obj.matrix_basis[r][c] - float(r == c)) > 1e-6
                                      for r in range(4) for c in range(4)):
            raise ValueError("Part transforms were edited. Restore their original transforms before automatic rigging.")
    try:
        spec = HumanoidSpec(root["height_cm"], root["weight_kg"], BodyType(root["body_type"]))
    except (KeyError, TypeError, ValueError):
        raise ValueError("Generation measurements are missing. Generate a new character first.") from None
    scale = root.get("coordinate_scale", 0.01 / context.scene.unit_settings.scale_length)
    return attach_rig(root, generate_skeleton(generate_proportions(spec)), scale)
