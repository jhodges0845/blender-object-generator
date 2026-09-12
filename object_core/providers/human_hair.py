# SPDX-License-Identifier: GPL-3.0-or-later
"""Human-specific fitting and low-cost parent-rig weighting for hair components."""

from ..models import BoneWeight, MeshPart, ObjectMesh, Skeleton, SkinWeights


def _bone(skeleton, name):
    return next((bone for bone in skeleton.bones if bone.name == name), None)


def fit_parent_skinned_hair(mesh, skeleton):
    """Fit a local hair shell around a Human head and return low-cost skin weights.

    The cap follows the head. Long rear vertices gradually transfer through neck
    to torso so head/neck animation produces visible secondary deformation
    without runtime simulation or an extra component rig.
    """
    if not isinstance(mesh, ObjectMesh):
        raise TypeError("mesh must be ObjectMesh")
    if not isinstance(skeleton, Skeleton):
        raise TypeError("skeleton must be Skeleton")
    head = _bone(skeleton, "head")
    neck = _bone(skeleton, "neck")
    torso = _bone(skeleton, "torso")
    if head is None or neck is None or torso is None:
        raise ValueError("parent-skinned Human hair requires head, neck, and torso bones")

    center_x = (head.head[0] + head.tail[0]) / 2.0
    center_y = (head.head[1] + head.tail[1]) / 2.0
    head_length = head.tail[2] - head.head[2]
    rim_z = head.head[2] + head_length * 0.45

    fitted_parts = []
    all_weights = []
    for part in mesh.parts:
        local_min_z = min(vertex[2] for vertex in part.vertices)
        back_length = max(0.0, -local_min_z)
        fitted_vertices = []
        part_weights = []
        for vertex in part.vertices:
            local_z = vertex[2]
            fitted_vertices.append((
                vertex[0] + center_x,
                vertex[1] + center_y,
                vertex[2] + rim_z,
            ))
            if local_z >= 0.0 or back_length <= 0.0:
                influences = (BoneWeight("head", 1.0),)
            else:
                t = min(1.0, max(0.0, -local_z / back_length))
                if t <= 0.5:
                    neck_amount = t * 2.0 * 0.65
                    influences = (
                        BoneWeight("head", 1.0 - neck_amount),
                        BoneWeight("neck", neck_amount),
                    )
                else:
                    lower = (t - 0.5) * 2.0
                    torso_amount = lower * 0.65
                    neck_amount = 1.0 - torso_amount
                    influences = (
                        BoneWeight("neck", neck_amount),
                        BoneWeight("torso", torso_amount),
                    )
            part_weights.append(influences)
        fitted_parts.append(MeshPart(part.name, tuple(fitted_vertices), part.faces, part.uvs))
        all_weights.append(SkinWeights(part.name, tuple(part_weights)))

    return ObjectMesh(tuple(fitted_parts)), tuple(all_weights)


__all__ = ["fit_parent_skinned_hair"]
